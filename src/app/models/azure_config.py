# src/app/models/azure_config.py

"""
Azure Configuration Module

This module defines the configuration model for Azure services, specifically handling
the connection settings required for Azure API interactions. It uses Pydantic for
validation and type checking of configuration parameters.
"""


from pydantic import AnyUrl
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

    @validator("endpoint", pre=True, always=True)
    def ensure_trailing_slash(self, v: AnyUrl) -> str:
        """
        Validates and ensures the endpoint URL has a trailing slash.

        Args:
            v (AnyUrl): The endpoint URL to validate

        Returns:
            str: The endpoint URL with a trailing slash

        Note:
            This validator runs before other validations (pre=True) and always
            ensures the URL ends with a trailing slash for consistency.
        """
        text = str(v)
        if not text.endswith("/"):
            logger.debug(f"Adding trailing slash to endpoint URL: {text}")
            return text + "/"
        logger.debug(f"Endpoint URL already has trailing slash: {text}")
        return text

    class Config:
        """Pydantic model configuration."""

        # Allow extra fields to be present in the input data
        extra = "allow"
        # Enable validation of assignment
        validate_assignment = True
