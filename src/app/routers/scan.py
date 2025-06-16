"""
Scan Router Module

This module implements the FastAPI router for compliance scanning endpoints.
It handles the processing of compliance scan requests, including document analysis,
LLM-based evaluation, and result aggregation. The module manages parallel processing
of multiple compliance checks and provides detailed logging of the entire process.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Query, Request
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

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
logger = get_logger(__name__)
settings = Settings()

# Initialization on startup
logger.info("Initializing scan router components...")

# Preload evaluation templates
templates: Dict[str, str] = {}
for key in ("compliance_eval", "compliance_eval_with_docs"):
    path = settings.get_template_path(key)
    templates[key] = path.read_text(encoding="utf-8")
EVAL_TEMPLATE = templates["compliance_eval"]
EVAL_TEMPLATE_DOCUMENTS = templates["compliance_eval_with_docs"]

# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
    api_key=settings.azure_api_key,
    azure_endpoint=str(settings.azure_endpoint),
    api_version=settings.azure_api_version,
    deployment_name=settings.azure_deployment,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens,
)
logger.info("AzureChatOpenAI client initialized")


def _init_compliance_definitions(use_case: str):
    """
    Load compliance definitions from YAML based on the use case.

    Sets settings.compliances_file to point to the correct rules file, then calls load_compliances().
    """
    file_path = settings.get_compliance_file(use_case)
    return load_compliances(file_path)

def build_filled_template(
    template: str,
    comp: Any,
    req: ScanRequest,
    docs_text: str,
    task_header: str
) -> str:
    """
    Replace placeholders in the evaluation template, including injecting the task header.
    """
    user_input = req.prompt.strip() or "[EMPTY PROMPT PROVIDED]"
    filled = (
        template
        .replace("{task}", task_header)
        .replace("{compliance_description}", comp.description)
        .replace("{threshold}", str(comp.threshold))
        .replace("{user_input}", user_input)
    )
    if "{document_context}" in template:
        filled = filled.replace("{document_context}", docs_text or "No documents provided")
    return filled


@router.post("/", response_model=ScanResponse)
async def scan_compliance(
    req: ScanRequest,
    request: Request,
    use_case_id: Optional[str] = Query(
        None,
        description="Use case identifier for compliance evaluation"
    )
) -> ScanResponse:
    """
    Endpoint to scan input against compliance definitions for a given use case.
    If use_case_id is not provided, defaults to the value in .env (DEFAULT_USE_CASE).
    """
    effective_use_case = use_case_id or settings.default_use_case
    request_id = str(uuid.uuid4())
    req_logger = RequestLogger(request_id)
    logger.info(f"Processing request {request_id} for use case {effective_use_case}")

    # Load compliance definitions
    try:
        compliances = _init_compliance_definitions(effective_use_case)
        logger.info(f"Loaded {len(compliances)} compliance definitions")
    except ValueError as exc:
        logger.error(f"Invalid use case: {effective_use_case}")
        raise HTTPException(status_code=400, detail=str(exc))

    # Prepare the task header
    task_header = settings.get_task_template(effective_use_case)

    # Validate documents
    if req.documents and len(req.documents) > settings.max_documents:
        raise HTTPException(
            status_code=400,
            detail=f"Too many documents; max allowed: {settings.max_documents}"
        )

    req_logger.log_stage("request_received", {
        "prompt": req.prompt,
        "documents": req.documents,
        "use_case": effective_use_case,
        "client": request.client.host if request.client else "unknown"
    })

    # Combine documents
    docs_text = ""
    if req.documents and req.documents[0]:
        docs_text = "\n---\n".join(req.documents)

    async def eval_one(comp) -> Tuple[str, str]:
        # Select template
        base_tpl = EVAL_TEMPLATE_DOCUMENTS if docs_text else EVAL_TEMPLATE
        # Fill in all placeholders, including the dynamic task header
        filled = build_filled_template(base_tpl, comp, req, docs_text, task_header)

        vars = ["user_input"] + (["documents"] if docs_text else [])
        prompt_obj = PromptTemplate(input_variables=vars, template=filled)
        params = {"user_input": req.prompt.strip()}
        if docs_text:
            params["documents"] = docs_text

        raw = await asyncio.wait_for(
            LLMChain(llm=llm, prompt=prompt_obj).arun(**params),
            timeout=settings.llm_timeout
        )
        return raw, comp.id

    # Run checks
    tasks = [eval_one(c) for c in compliances]
    logger.info(f"Launching {len(tasks)} compliance checks")
    raw_results = await asyncio.gather(*tasks)

    # Process results
    detailed: Dict[str, ComplianceResult] = {}
    failed_ids: List[str] = []
    for raw_text, comp_id in raw_results:
        comp = next(c for c in compliances if c.id == comp_id)
        parsed = parse_evaluation(raw_text)
        score = float(parsed.get("grade", "0.00/1").split("/")[0])
        passed = score >= comp.threshold

        section = ParsedSection(
            reasoning=parsed.get("reasoning"),
            summarization=parsed.get("summarization"),
            recommendations=parsed.get("recommendations"),
            insights=parsed.get("insights"),
            grade=parsed.get("grade"),
            critical_compliance_concern=parsed.get("critical_compliance_concern"),
            required_mitigation=parsed.get("required_mitigation"),
            rephrase_prompt=parsed.get("rephrase_prompt"),
        )

        result = ComplianceResult(
            name=comp.name,
            description=comp.description,
            raw_output=raw_text,
            parsed=section,
            threshold=comp.threshold,
            passed=passed
        )
        detailed[comp_id] = result
        if not passed:
            failed_ids.append(comp_id)
            logger.warning(f"Compliance failed: {comp.id}")
        req_logger.log_stage(f"result_{comp_id}", result.dict())

    rephrase = req.prompt if not failed_ids else None
    req_logger.log_stage("final", {"failed_ids": failed_ids})
    logger.info(f"Completed request {request_id}")

    return ScanResponse(detailed=detailed, rephrased_prompt=rephrase)
