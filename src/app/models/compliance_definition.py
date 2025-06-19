from typing import Any, ClassVar, Dict

from pydantic import BaseModel, Field, field_validator

from ..core.logging import get_logger

logger = get_logger(__name__)


class ComplianceDefinition(BaseModel):
    """
    Model representing a compliance definition for document analysis.

    Attributes:
        id (str): Unique identifier for the compliance definition
        name (str): Human-readable name of the compliance rule
        description (str): Detailed description of the compliance requirement
        threshold (float): Pass/fail threshold between 0.0 and 1.0
        prompt (str): Template string for analysis with {user_input} and {documents} placeholders
    """

    id: str = Field(
        ...,
        description="Unique compliance ID",
        min_length=1,
        pattern="^[a-zA-Z0-9_-]+$",
    )

    name: str = Field(
        ...,
        description="Human-readable name",
        min_length=1,
        max_length=100
    )

    description: str = Field(
        ...,
        description="Detailed description",
        min_length=10,
        max_length=1000
    )

    threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Pass threshold between 0.0 and 1.0"
    )

    prompt: str = Field(
        ...,
        description="Prompt template with {user_input} and {documents} placeholders",
        min_length=20
    )

    @classmethod
    @field_validator("prompt")
    def validate_prompt_template(cls, v: str) -> str:
        required_placeholders = {"{user_input}", "{documents}"}
        missing = [p for p in required_placeholders if p not in v]
        if missing:
            logger.error(f"Prompt template missing required placeholders: {missing}")
            raise ValueError(f"Prompt template must contain placeholders: {', '.join(required_placeholders)}")
        logger.debug(f"Prompt template validated successfully: {v[:50]}...")
        return v

    @classmethod
    @field_validator("threshold")
    def validate_threshold(cls, v: float) -> float:
        logger.debug(f"Setting compliance threshold to {v:.2f}")
        return v

    model_config: ClassVar[Dict[str, Any]] = {
        "json_schema_extra": {
            "example": {
                "id": "compliance_001",
                "name": "Document Privacy Check",
                "description": "Ensures documents don't contain sensitive personal information",
                "threshold": 0.95,
                "prompt": "Analyze the following documents for privacy compliance: {documents}. User input: {user_input}"
            }
        }
    }
