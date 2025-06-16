# src/app/routers/aggregation_router.py

import json
import uuid
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from src.app.core.config import Settings
from src.app.core.logging import get_logger
from src.app.models.request_logger import RequestLogger
from src.app.services.compliance_service import load_compliances
from src.app.services.parser import parse_evaluation

logger = get_logger(__name__)
settings = Settings()
router = APIRouter(prefix="/aggregate", tags=["aggregation"])

# Preload aggregator template
template_path = settings.get_template_path("aggregator")
AGG_TEMPLATE = template_path.read_text(encoding="utf-8")
logger.info("Aggregator template loaded from %s", template_path)

# Initialize LLM client
llm = AzureChatOpenAI(
    api_key=settings.azure_api_key,
    azure_endpoint=str(settings.azure_endpoint),
    api_version=settings.azure_api_version,
    deployment_name=settings.azure_deployment,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens,
)
logger.info("AzureChatOpenAI client initialized for aggregation")


class AggregationRequest(BaseModel):
    failed_json: Dict[str, Any]
    original_prompt: str


class AggregationResponse(BaseModel):
    aggregated_summary: str
    recommendations: Dict[str, Any]
    rephrased_prompt: Optional[str]


@router.post("/results", response_model=AggregationResponse)
async def aggregate_compliance(
    req: AggregationRequest,
    request: Request,
    use_case_id: Optional[str] = Query(
        None, description="Use case identifier for compliance aggregation"
    )
) -> AggregationResponse:
    # Determine use case
    effective_use_case = use_case_id or settings.default_use_case
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    req_logger = RequestLogger(req_id)
    logger.info("Aggregation request %s for use case %s", req_id, effective_use_case)

    # Load compliance definitions per use case
    try:
        # override the settings file then call loader
        file_path = settings.get_compliance_file(effective_use_case)
        compliances = load_compliances(file_path)
    except ValueError as e:
        logger.error("Invalid use case: %s", effective_use_case)
        raise HTTPException(status_code=400, detail=str(e))

    failed = req.failed_json

    # Validate IDs
    valid_ids = {c.id for c in compliances}
    unknown = [cid for cid in failed if cid not in valid_ids]
    if unknown:
        logger.error("Unknown compliance IDs: %s", unknown)
        raise HTTPException(400, f"Unknown compliance IDs: {unknown}")

    # Enrich with description & threshold
    enriched: Dict[str, Any] = {}
    for comp in compliances:
        if comp.id in failed:
            entry = failed[comp.id]
            enriched[comp.id] = {
                **entry,
                "description": comp.description,
                "threshold": comp.threshold,
                "name":comp.name
            }
    failed_json_str = json.dumps(enriched, indent=2)

    req_logger.log_stage("aggregation_request_received", {
        "failed_ids": list(enriched.keys()),
        "original_prompt": req.original_prompt
    })

    # Prepare prompt
    prompt = PromptTemplate(
        input_variables=["failed_json", "original_prompt"],
        template=AGG_TEMPLATE
    )
    
    try:
        filled = prompt.format(
            failed_json=failed_json_str,
            original_prompt=req.original_prompt
        )
        req_logger.log_stage("filled_aggregator_template", {"filled": filled})
    except Exception as e:
        logger.error("Error formatting aggregator template: %s", e, exc_info=True)
        raise HTTPException(500, "Template formatting failed")

    # Call LLM
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        raw_output = await chain.arun(
            failed_json=failed_json_str,
            original_prompt=req.original_prompt
        )
        req_logger.log_stage("llm_raw_output", {"raw": raw_output})
    except Exception as e:
        logger.error("Aggregation LLM call failed: %s", e, exc_info=True)
        raise HTTPException(502, "Failed to generate aggregated output")

    # Debug log
    logger.warning("AGGREGATOR RAW OUTPUT:\n%s", raw_output)

    # Parse JSON
    try:
        result = json.loads(raw_output)
    except JSONDecodeError:
        logger.error("Aggregation LLM returned invalid JSON: %r", raw_output)
        raise HTTPException(
            status_code=502,
            detail="Aggregation service returned invalid JSON. Please check the aggregator template or LLM output."
        )
    except Exception as e:
        logger.error("Unexpected error parsing aggregation result: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unexpected error parsing aggregation result."
        )

    # Extract aggregated summary
    if "Aggregated Summary" not in result:
        logger.error("Missing 'Aggregated Summary' in output: %s", result)
        raise HTTPException(
            status_code=502,
            detail="Aggregation result JSON is missing 'Aggregated Summary'"
        )
    aggregated_summary = result["Aggregated Summary"]

    # Rebuild recommendations map with original failure IDs
    raw_recs = result.get("Recommendations", {})
    recommendations: Dict[str, Any] = {}
    for cid in req.failed_json.keys():
        recommendations[cid] = raw_recs.get(cid, [])

    # Ensure rephrase relates to original prompt
    rephrased_prompt = result.get("Rephrase Prompt") or req.original_prompt

    req_logger.log_stage("parsed_aggregation_result", {
        "Aggregated Summary": aggregated_summary,
        "Recommendations": recommendations,
        "Rephrase Prompt": rephrased_prompt
    })

    return AggregationResponse(
        aggregated_summary=aggregated_summary,
        recommendations=recommendations,
        rephrased_prompt=rephrased_prompt
    )
