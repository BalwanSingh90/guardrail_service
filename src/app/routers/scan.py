"""
scan_router.py – FastAPI router for /scan
Optimised to minimise Assistants latency & network calls

Changes vs previous revision
----------------------------
✓ Each compliance component now triggers ONE Assistants call (run-stream)
  we pass the user prompt inside `additional_messages` instead of adding a
    separate message first.
✓ Total calls per /scan request: 1 (thread) + N (compliances).

Requires
--------
openai>=1.13.3 (Azure extension), fastapi, pydantic v1, etc.
project-local: src.app.core.*, src.app.models.*, src.app.services.*
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from openai import AzureOpenAI

from src.app.core.config import Settings
from src.app.core.logging import get_logger
from src.app.models.request_logger import RequestLogger
from src.app.models.schemas import (
    ComplianceResult,
    ParsedSection,
    ScanRequest,
    ScanResponse,
)
from src.app.services.compliance_service import load_compliances
from src.app.services.parser import parse_evaluation

router = APIRouter(prefix="/scan", tags=["scan"])
settings = Settings()
logger = get_logger(__name__)

client = AzureOpenAI(
    api_key=settings.azure_api_key,
    azure_endpoint=str(settings.azure_endpoint),
    api_version="2024-05-01-preview",  # Assistants preview
)
DEPLOYMENT = settings.azure_deployment


@lru_cache(maxsize=1)
def get_assistant_id() -> str:
    assistant = client.beta.assistants.create(
        model=DEPLOYMENT,
        instructions=(
            "You are an AI compliance evaluator. "
            "Follow the instructions carefully and reply only in the requested format."
        ),
        tools=[],
        temperature=settings.llm_temperature,
        top_p=1,
    )
    logger.info("Assistants: using assistant %s", assistant.id)
    return assistant.id


templates: Dict[str, str] = {
    k: settings.get_template_path(k).read_text("utf-8")
    for k in ("compliance_eval", "compliance_eval_with_docs")
}
EVAL_TEMPLATE = templates["compliance_eval"]
EVAL_TEMPLATE_DOCS = templates["compliance_eval_with_docs"]

os.makedirs(settings.log_dir, exist_ok=True)


def _bullets(text: str) -> str:
    parts = re.split(r"[\.\n]+", text)
    return "\n".join(f"- {p.strip()}" for p in parts if p.strip())


def _docs_block(docs: List[str]) -> str:
    if not docs:
        return "No documents provided"
    return "\n\n".join(f"```text\n{d.strip()}\n```" for d in docs)


def build_prompt(template: str, comp: Any, req: ScanRequest, header: str) -> str:
    vars = {
        "task": header,
        "user_input": req.prompt.strip() or "[EMPTY PROMPT PROVIDED]",
        "document_context": _docs_block(req.documents),
        "compliance_prompt": comp.prompt,
        "compliance_name": comp.name,
        "compliance_description": _bullets(comp.description),
        "threshold": comp.threshold,
    }
    return template.format(**vars)


def _blocks_to_text(blocks) -> str:
    """Flatten TextDeltaBlock[] → str (works with old & new SDK)."""
    out: list[str] = []
    for blk in blocks:
        if getattr(blk, "text", None) is not None:
            val = getattr(blk.text, "value", "")
            if isinstance(val, str):
                out.append(val)
            continue
        val = getattr(blk, "value", None)
        if isinstance(val, str):
            out.append(val)
    return "".join(out)


def _assistant_stream(prompt: str, thread_id: str) -> str:
    assistant_id = get_assistant_id()

    # SINGLE API call per component: create run & stream, injecting the prompt
    with client.beta.threads.runs.create_and_stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_messages=[{"role": "user", "content": prompt}],
    ) as mgr:

        iterator = (
            mgr.events()
            if hasattr(mgr, "events")
            else mgr.iter_events() if hasattr(mgr, "iter_events") else mgr
        )

        chunks: list[str] = []
        for ev in iterator:
            if ev.event != "thread.message.delta":
                continue
            content = getattr(ev.data.delta, "content", None)
            if not content:
                continue
            if isinstance(content, list):
                chunks.append(_blocks_to_text(content))
            elif isinstance(content, str):
                chunks.append(content)

        return "".join(chunks).strip()


async def run_assistant(prompt: str, thread_id: str) -> str:
    return await asyncio.to_thread(_assistant_stream, prompt, thread_id)


@router.post("/", response_model=ScanResponse)
async def scan_compliance(
    req: ScanRequest,
    request: Request,
    use_case_id: Optional[str] = Query(None),
) -> ScanResponse:
    use_case = use_case_id or settings.default_use_case
    req_id = str(uuid.uuid4())
    RequestLogger(req_id)
    logger.info("[%s] /scan – use-case: %s", req_id, use_case)

    try:
        compliances = load_compliances(settings.get_compliance_file(use_case))
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))

    if req.documents and len(req.documents) > settings.max_documents:
        raise HTTPException(
            400, detail=f"Too many documents (max {settings.max_documents})"
        )

    header = settings.get_task_template(use_case)

    thread = client.beta.threads.create()  # one thread reused per request

    detailed: Dict[str, ComplianceResult] = {}
    failures: List[str] = []
    log_blob: Dict[str, Any] = {
        "request_id": req_id,
        "use_case_id": use_case,
        "input_prompt": req.prompt,
        "documents": req.documents,
        "results": [],
    }

    for comp in compliances:  # sequential to respect rate-limits
        template = EVAL_TEMPLATE_DOCS if req.documents else EVAL_TEMPLATE
        filled = build_prompt(template, comp, req, header)

        raw_reply = await run_assistant(filled, thread.id)

        parsed = parse_evaluation(raw_reply)
        ratio = float(parsed.get("grade", {}).get("score_ratio") or 0.0)
        passed = ratio >= comp.threshold

        section = ParsedSection(
            problem=parsed.get("problem"),
            why_it_failed=parsed.get("why_it_failed"),
            explain=parsed.get("what_to_fix"),
            rephrase_prompt=parsed.get("rephrase_prompt"),
            compliance_id_and_name=parsed.get("compliance_id_and_name"),
            grade=str(ratio),
        )
        detailed[comp.id] = ComplianceResult(
            name=comp.name,
            description=comp.description,
            parsed=section,
            threshold=comp.threshold,
            passed=passed,
        )

        log_blob["results"].append(
            {
                "compliance_id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "threshold": comp.threshold,
                "grade": ratio,
                "passed": passed,
                "filled_prompt": filled,
                "raw_llm_output": raw_reply,
                "parsed": section.dict(),
            }
        )

        if not passed:
            failures.append(comp.id)

    path = os.path.join(settings.log_dir, f"{req_id}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log_blob, fh, indent=2)
    logger.info("[%s] log saved → %s", req_id, path)

    return ScanResponse(
        detailed=detailed, rephrased_prompt=None if failures else req.prompt
    )
