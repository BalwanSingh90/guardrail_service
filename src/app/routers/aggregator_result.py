# src/app/routers/aggregation_router.py
"""
Aggregates the individual compliance-check failures into a single
human-friendly summary, recommendations map, and (if needed) a re-phrased
prompt that should pass all compliances on re-scan.
"""
from __future__ import annotations

import json
import re
import uuid
from json import JSONDecodeError
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field, model_validator

from src.app.core.config import Settings
from src.app.core.logging import get_logger
from src.app.models.request_logger import RequestLogger
from src.app.services.compliance_service import load_compliances

# ──────────────────────────── setup ──────────────────────────────────
logger = get_logger(__name__)
settings = Settings()
router = APIRouter(prefix="/aggregate", tags=["aggregation"])

AGG_TEMPLATE = settings.get_template_path("aggregator").read_text("utf-8")
logger.info("Aggregator template loaded")

# One global AzureChatOpenAI client - re-used for every request
_llm_client = AzureChatOpenAI(
    api_key=settings.azure_api_key,
    azure_endpoint=str(settings.azure_endpoint),
    api_version=settings.azure_api_version,
    deployment_name=settings.azure_deployment,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens,
    frequency_penalty=settings.llm_frequency_penalty,
    presence_penalty=settings.llm_presence_penalty,
    timeout=60,  # seconds
    # force JSON output (Azure supports the OpenAI 1106 JSON mode)
    model_kwargs={"response_format": {"type": "json_object"}},
)
_AGG_CHAIN = LLMChain(
    llm=_llm_client,
    prompt=PromptTemplate(
        template=AGG_TEMPLATE,
        input_variables=["failed_json", "original_prompt"],
    ),
)
logger.info("Aggregator LLMChain initialised")


# ────────────────────────── Pydantic I/O ────────────────────────────
class AggregationRequest(BaseModel):
    failed_json: dict[str, Any]
    original_prompt: str


class AggregationResponse(BaseModel):
    aggregated_summary: str = Field(..., description="Plain-text roll-up")
    recommendations: dict[str, Any] = Field(
        ..., description="Mapping cid → list[str] of concrete fixes"
    )
    rephrased_prompt: str = Field(..., description="Prompt expected to pass")

    # Ensure a non-empty prompt so callers never get `null`
    @model_validator(mode="before")
    @classmethod    
    def _non_empty(self, v: str) -> str:
        return v.strip() or "<NO-PROMPT-RETURNED>"


# ───────────────────────── helper utils ─────────────────────────────
_JSON_RE = re.compile(r"\{[\s\S]*\}", re.DOTALL)


def _first_json_block(text: str) -> str:
    """Return the *first* {...} block - raises if none found."""
    m = _JSON_RE.search(text)
    if not m:
        raise JSONDecodeError("No JSON object found", text, 0)
    return m.group(0)


# ──────────────────────────── endpoint ──────────────────────────────
@router.post("/results", response_model=AggregationResponse)
async def aggregate_compliance(
    req: AggregationRequest,
    request: Request,
    use_case_id: str | None = Query(None),
) -> AggregationResponse:
    # ── request bookkeeping ─────────────────────────────────────────
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    log = RequestLogger(req_id)
    log.log_stage("aggregation_request_received", req.dict())

    use_case = use_case_id or settings.default_use_case
    comp_path = settings.get_compliance_file(use_case)
    compliances = load_compliances(comp_path)
    valid_ids = {c.id for c in compliances}

    unknown = [cid for cid in req.failed_json if cid not in valid_ids]
    if unknown:
        raise HTTPException(400, detail=f"Unknown compliance IDs: {unknown}")

    # Enrich failures with descriptions / threshold for the LLM
    enriched = {
        cid: {
            **req.failed_json[cid],
            "description": next(c.description for c in compliances if c.id == cid),
            "threshold": next(c.threshold for c in compliances if c.id == cid),
            "name": next(c.name for c in compliances if c.id == cid),
        }
        for cid in req.failed_json
    }
    failed_json_str = json.dumps(enriched, indent=2)
    log.log_stage("enriched_failed_json", enriched)

    # ── LLM call ────────────────────────────────────────────────────
    try:
        raw_output: str = await _AGG_CHAIN.arun(
            failed_json=failed_json_str,
            original_prompt=req.original_prompt,
        )
        log.log_stage("llm_raw_output", raw_output)
    except Exception as exc:
        logger.exception("Aggregation LLM call failed")
        raise HTTPException(502, "Failed to aggregate compliance feedback") from exc

    # ── JSON parse ─────────────────────────────────────────────────
    try:
        payload = json.loads(_first_json_block(raw_output))
    except ValueError as exc:
        raise HTTPException(400, detail="Invalid input") from exc

    # Expected keys - tolerate different capitalisation
    agg_summary = (
        payload.get("aggregated_summary")
        or payload.get("Aggregated Summary")
        or payload.get("summary")
        or ""
    )
    recs = payload.get("recommendations") or payload.get("Recommendations") or {}
    rephrase = (
        payload.get("rephrased_prompt")
        or payload.get("Rephrase Prompt")
        or req.original_prompt
    )

    log.log_stage(
        "parsed_aggregation_result",
        {
            "aggregated_summary": agg_summary,
            "recommendations": recs,
            "rephrased_prompt": rephrase,
        },
    )

    return AggregationResponse(
        aggregated_summary=agg_summary.strip(),
        recommendations=recs,
        rephrased_prompt=rephrase.strip(),
    )
