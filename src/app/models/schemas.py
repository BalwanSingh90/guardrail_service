from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from ..core.logging import get_logger

logger = get_logger(__name__)


class ScanRequest(BaseModel):
    prompt: str = Field(
        ..., description="The prompt text to be evaluated for compliance", min_length=1
    )
    documents: Optional[List[str]] = Field(
        default=[], description="List of documents to be analyzed"
    )

    @classmethod
    @field_validator("prompt")
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            logger.error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty or contain only whitespace")
        logger.debug(f"Validated prompt of length {len(v)}")
        return v


class ParsedSection(BaseModel):
    problem: Optional[str] = Field(default=None, description="What went wrong")
    why_it_failed: Optional[str] = Field(
        default=None, description="Explanation for failure"
    )
    explain: Optional[str] = Field(
        default=None, description="Actionable correction advice"
    )
    rephrase_prompt: Optional[str] = Field(
        default=None, description="Revised compliant prompt"
    )
    compliance_id_and_name: Optional[str] = Field(
        default=None, description="Compliance ID and name"
    )
    grade: Optional[str] = Field(default=None, description="Score in 'X.XX/1' format")

    @classmethod
    @field_validator("grade")
    def validate_grade(cls, v: str) -> str:
        try:
            score, denominator = v.split("/")
            score = float(score)
            if not 0 <= score <= 1:
                raise ValueError("Score must be between 0 and 1")
            if denominator.strip() != "1":
                raise ValueError("Denominator must be 1")
        except Exception as e:
            logger.error(f"Invalid grade format: {v}")
            raise ValueError("Grade must be in format 'X.XX/1'") from e
        return v


class ComplianceResult(BaseModel):
    name: str = Field(..., description="Compliance name")
    description: str = Field(..., description="What this compliance checks for")
    parsed: ParsedSection = Field(..., description="Parsed structured output")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Required minimum score")
    passed: bool = Field(..., description="True if grade ≥ threshold")

    @classmethod
    @field_validator("threshold")
    def validate_threshold(cls, v: float, info) -> float:
        if not 0 <= v <= 1:
            logger.error(f"Invalid {info.field_name} value: {v}")
            raise ValueError(f"{info.field_name} must be between 0 and 1")
        logger.debug(f"Validated {info.field_name}: {v}")
        return v


class ScanResponse(BaseModel):
    detailed: Dict[str, ComplianceResult] = Field(
        ..., description="Result per compliance check"
    )
    rephrased_prompt: Optional[str] = Field(
        default=None, description="Fallback prompt if original fails"
    )
    failures_summary: Optional[List[str]] = Field(
        default=None, description="Formatted summary (optional)"
    )

    model_config: ClassVar[Dict[str, Any]] = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "detailed": {
                    "PC1": {
                        "name": "Grounded Response",
                        "description": "Ensure answers are based on source documents only.",
                        "parsed": {
                            "problem": "The response included assumptions not grounded in documents.",
                            "why_it_failed": "No direct quote from source documents was used.",
                            "explain": "Only refer to approved documents explicitly.",
                            "rephrase_prompt": "How do I act according to documented escalation steps?",
                            "compliance_id_and_name": "PC1 – Grounded Response",
                            "grade": "0.72/1",
                        },
                        "threshold": 0.9,
                        "passed": False,
                    }
                },
                "rephrased_prompt": "Alternative wording suggestion...",
                "failures_summary": None,
            }
        },
    }
