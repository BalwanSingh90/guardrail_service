# src/app/core/config.py

"""
Configuration Module

This module defines the application's configuration settings using Pydantic's BaseSettings.
All configuration values can be overridden using environment variables or a .env file.
"""

from pathlib import Path
from typing import Dict, Optional, Union

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden using environment variables or a .env file.
    Default values are provided where appropriate.
    """
    # Default use case, read from .env COMPLIANCE_MAP
    default_use_case: str = Field(
        "generic",
        alias="COMPLIANCE_MAP",
        env="COMPLIANCE_MAP",
        description="Default compliance use case identifier"
    )

    # Static map of compliance files and task templates
    compliance_map: Dict[str, Dict[str, str]] = {
        "generic": {
            "file": "compliances.yaml",
            "task_template": (
                "Evaluate the following input against all compliance categories defined in the system prompt."
            )
        },
        "azure_ccc": {
            "file": "azure_ccc_compliances.yaml",
            "task_template": (
                "Your job is to analyze this system prompt against the CCC guidelines and other compliance rules, flag any violations, and—if it fails—suggest a compliant rephrasing. \n"
                "Use the **Compliance Rule Description** below to drive your analysis:"  
            )
        }
    }

    # Azure OpenAI Configuration
    azure_endpoint: AnyUrl = Field(..., alias="AZURE_OPENAI_ENDPOINT", env="AZURE_OPENAI_ENDPOINT")
    azure_api_key: str = Field(..., alias="AZURE_OPENAI_KEY", env="AZURE_OPENAI_KEY")
    azure_deployment: str = Field("gpt-4", alias="AZURE_OPENAI_DEPLOYMENT", env="AZURE_OPENAI_DEPLOYMENT")
    azure_api_version: str = Field("2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION", env="AZURE_OPENAI_API_VERSION")

    # LLM Configuration
    llm_temperature: float = Field(0.7, alias="LLM_TEMPERATURE", env="LLM_TEMPERATURE", ge=0.0, le=1.0)
    llm_max_tokens: Optional[int] = Field(None, alias="LLM_MAX_TOKENS", env="LLM_MAX_TOKENS", gt=0)
    llm_timeout: int = Field(60, alias="LLM_TIMEOUT", env="LLM_TIMEOUT", gt=0)

    # Template Configuration
    template_dir: str = Field("src/app/templates", alias="TEMPLATE_DIR", env="TEMPLATE_DIR")
    template_names: Dict[str, str] = Field(
        {
            "compliance_eval": "compliance_eval.md",
            "compliance_eval_with_docs": "compliance_eval_with_documents.md",
            "aggregator": "aggregator.md"
        },
        alias="TEMPLATE_NAMES",
        env="TEMPLATE_NAMES"
    )

    # File Paths
    compliances_file: str = Field("compliances.yaml", alias="COMPLIANCES_FILE", env="COMPLIANCES_FILE")
    log_dir: str = Field("src/logs", alias="LOG_DIR", env="LOG_DIR")

    # Application Settings
    request_timeout: int = Field(300, alias="REQUEST_TIMEOUT", env="REQUEST_TIMEOUT", gt=0)
    max_documents: int = Field(10, alias="MAX_DOCUMENTS", env="MAX_DOCUMENTS", gt=0)
    max_document_size: int = Field(1024 * 1024, alias="MAX_DOCUMENT_SIZE", env="MAX_DOCUMENT_SIZE", gt=0)

    # Evaluation Settings
    evaluation_dir: str = Field("evaluation", alias="EVALUATION_DIR", env="EVALUATION_DIR")
    evaluation_inputs_dir: str = Field("inputs", alias="EVALUATION_INPUTS_DIR", env="EVALUATION_INPUTS_DIR")
    evaluation_outputs_dir: str = Field("outputs", alias="EVALUATION_OUTPUTS_DIR", env="EVALUATION_OUTPUTS_DIR")
    evaluation_metrics_dir: str = Field("metrics", alias="EVALUATION_METRICS_DIR", env="EVALUATION_METRICS_DIR")
    evaluation_test_cases_file: str = Field("test_cases.json", alias="EVALUATION_TEST_CASES_FILE", env="EVALUATION_TEST_CASES_FILE")
    evaluation_raw_responses_dir: str = Field("raw_responses", alias="EVALUATION_RAW_RESPONSES_DIR", env="EVALUATION_RAW_RESPONSES_DIR")
    evaluation_evaluated_dir: str = Field("evaluated", alias="EVALUATION_EVALUATED_DIR", env="EVALUATION_EVALUATED_DIR")
    evaluation_metrics_file: str = Field("summary_metrics.json", alias="EVALUATION_METRICS_FILE", env="EVALUATION_METRICS_FILE")
    evaluation_grade_tolerance: float = Field(1e-6, alias="EVALUATION_GRADE_TOLERANCE", env="EVALUATION_GRADE_TOLERANCE", ge=0.0)

    @field_validator("template_dir")
    @classmethod
    def validate_template_dir(cls, v: str) -> str:
        path = Path(v)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid template directory: {v}")
        return v

    @field_validator("log_dir")
    @classmethod
    def validate_log_dir(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("evaluation_dir")
    @classmethod
    def validate_evaluation_dir(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    def get_template_path(self, template_name: str) -> Path:
        if template_name not in self.template_names:
            raise ValueError(f"Unknown template: {template_name}")
        return Path(self.template_dir) / self.template_names[template_name]

    def get_compliance_file(self, use_case: str) -> str:
        mapping = self.compliance_map.get(use_case)
        if not mapping:
            raise ValueError(f"Unknown use case: {use_case}")
        # Compliance YAMLs are in rules/ folder
        return str(Path("rules") / mapping["file"])

    def get_task_template(self, use_case: str) -> str:
        mapping = self.compliance_map.get(use_case)
        if not mapping or "task_template" not in mapping:
            raise ValueError(f"Missing task template for use case: {use_case}")
        return mapping["task_template"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
