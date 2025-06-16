from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from ..core.logging import get_logger

logger = get_logger(__name__)


class ScanRequest(BaseModel):
    prompt: str = Field(..., description="The prompt text to be evaluated for compliance", min_length=1)
    documents: Optional[List[str]] = Field(default=[], description="List of documents to be analyzed")

    @classmethod
    @field_validator("prompt")
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            logger.error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty or contain only whitespace")
        logger.debug(f"Validated prompt of length {len(v)}")
        return v


class ParsedSection(BaseModel):
    reasoning: Optional[List[str]] = Field(default=None, description="List of reasoning points from the evaluation")
    summarization: Optional[str] = Field(default=None, description="Overall summary of the evaluation")
    recommendations: Optional[List[str]] = Field(default=None, description="List of recommendations for improvement")
    insights: Optional[List[str]] = Field(default=None, description="List of key insights from the evaluation")
    grade: Optional[str] = Field(default=None, description="Numerical grade in string format (e.g., '0.95/1')")
    critical_compliance_concern: Optional[str] = Field(default=None, description="Major compliance issues identified")
    required_mitigation: Optional[str] = Field(default=None, description="Required actions to address compliance concerns")
    rephrase_prompt: Optional[str] = Field(default=None, description="Suggested alternative prompt wording")

    @classmethod
    @field_validator("grade")
    def validate_grade(cls, v: str) -> str:
        try:
            score, denominator = v.split("/")
            score = float(score)
            if not 0 <= score <= 1:
                raise ValueError("Score must be between 0 and 1")
            if denominator != "1":
                raise ValueError("Denominator must be 1")
        except (ValueError, IndexError) as e:
            logger.error(f"Invalid grade format: {v}")
            raise ValueError("Grade must be in format 'X.XX/1' where X.XX is between 0 and 1") from e
        return v


class ComplianceResult(BaseModel):
    name: str = Field(..., description="Name of the compliance check", min_length=1)
    description: str = Field(..., description="Description of what the check evaluates", min_length=1)
    raw_output: str = Field(..., description="Raw text output from the evaluation")
    parsed: ParsedSection = Field(..., description="Structured parsed sections from the evaluation")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Pass/fail threshold between 0 and 1")
    passed: bool = Field(..., description="Whether the evaluation passed the threshold")

    @classmethod
    @field_validator("score", "threshold")
    def validate_score_and_threshold(cls, v: float, info) -> float:
        if not 0 <= v <= 1:
            logger.error(f"Invalid {info.field_name} value: {v}")
            raise ValueError(f"{info.field_name} must be between 0 and 1")
        logger.debug(f"Validated {info.field_name}: {v}")
        return v


class ScanResponse(BaseModel):
    detailed: Dict[str, ComplianceResult] = Field(..., description="Detailed results for each compliance check")
    rephrased_prompt: Optional[str] = Field(default=None, description="Suggested alternative prompt wording")

    model_config: ClassVar[Dict[str, Any]] = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "detailed": {
                    "privacy_check": {
                        "name": "Privacy Compliance",
                        "description": "Checks for privacy-related issues",
                        "raw_output": "...",
                        "parsed": {
                            "reasoning": ["Point 1", "Point 2"],
                            "grade": "0.95/1"
                        },
                        "threshold": 0.8,
                        "passed": True
                    }
                },
                "rephrased_prompt": "Alternative wording suggestion..."
            }
        }
    }
