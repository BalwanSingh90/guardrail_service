# src/app/models/azure_config.py

"""
Azure Configuration Module

This module defines the configuration model for Azure services, specifically handling
the connection settings required for Azure API interactions. It uses Pydantic for
validation and type checking of configuration parameters.
"""


from pydantic import AnyUrl, model_validator
from pydantic_settings import BaseModel

from ..core.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)


class AzureConfig(BaseModel):
    """
    Configuration model for Azure service connections.

    This class validates and stores the essential configuration parameters needed
    to connect to Azure services, particularly for API interactions.

    Attributes:
        endpoint (AnyUrl): The base URL endpoint for the Azure service
        api_key (str): The authentication key for Azure API access
        deployment (str): The deployment name/identifier
        api_version (str): The version of the Azure API to use
    """

    endpoint: AnyUrl  # Base URL for Azure service endpoint
    api_key: str  # Authentication key for API access
    deployment: str  # Deployment identifier
    api_version: str  # API version to use

    @model_validator(mode="before")
    @classmethod
    def add_slash_to_endpoint(cls, data: dict) -> dict:
        if "endpoint" in data and not str(data["endpoint"]).endswith("/"):
            data["endpoint"] = str(data["endpoint"]) + "/"
        return data

    class Config:
        """Pydantic model configuration."""

        # Allow extra fields to be present in the input data
        extra = "allow"
        # Enable validation of assignment
        validate_assignment = True
