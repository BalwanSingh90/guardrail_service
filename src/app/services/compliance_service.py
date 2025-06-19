# src/app/services/compliance_service.py

"""
Compliance Service Module

This module handles the loading and management of compliance definitions from YAML files.
It provides functionality to load compliance definitions, validate their structure,
and convert them into ComplianceDefinition models for use in the application.

The module uses centralized configuration from Settings and implements proper error
handling and logging for all operations.
"""

from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.app.core.config import Settings
from src.app.core.logging import get_logger
from src.app.models.compliance_definition import ComplianceDefinition

# Initialize logger
logger = get_logger(__name__)

# Initialize settings
settings = Settings()


def validate_compliance_data(data: Dict[str, Any]) -> bool:
    """Validate the structure and content of compliance data."""
    is_valid = True
    # Check if data is a dictionary
    if not isinstance(data, dict):
        logger.error("Compliance data must be a dictionary")
        is_valid = False
    # Check for required 'compliances' key
    elif "compliances" not in data:
        logger.error("Missing 'compliances' key in data")
        is_valid = False
    # Validate compliances list
    else:
        items = data.get("compliances", [])
        if not isinstance(items, list):
            logger.error("'compliances' must be a list")
            is_valid = False
        else:
            # Validate each compliance item
            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    logger.error(f"Compliance item at index {idx} must be a dictionary")
                    is_valid = False
                    break
                # Check required fields
                required_fields = ["id", "name", "description", "threshold"]
                missing_fields = [
                    field for field in required_fields if field not in item
                ]
                if missing_fields:
                    logger.error(
                        f"Compliance item at index {idx} missing required fields: {missing_fields}"
                    )
                    is_valid = False
                    break
                # Validate threshold
                if not isinstance(item.get("threshold"), (int, float)):
                    logger.error(
                        f"Compliance item at index {idx} threshold must be a number"
                    )
                    is_valid = False
                    break
    return is_valid


def load_compliances(file_path) -> List[ComplianceDefinition]:
    """
    Load and validate compliance definitions from the configured YAML file.

    This function:
    1. Reads the compliance definitions from the configured YAML file
    2. Validates the structure and content of the data
    3. Converts valid definitions into ComplianceDefinition models
    4. Handles errors gracefully with proper logging

    Returns:
        List[ComplianceDefinition]: List of validated compliance definitions

    Raises:
        FileNotFoundError: If the compliance file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
        ValueError: If the compliance data is invalid
    """
    try:
        # Get the compliance file path from settings
        path = Path(file_path)
        logger.info(f"Loading compliance definitions from: {path}")

        # Check if file exists
        if not path.exists():
            error_msg = f"Compliance file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Read and parse YAML file
        try:
            raw = path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            logger.debug("Successfully parsed YAML file")
        except yaml.YAMLError as e:
            error_msg = f"Failed to parse YAML file: {e!s}"
            logger.error(error_msg)
            raise yaml.YAMLError(error_msg) from e

        # Validate compliance data
        if not validate_compliance_data(data):
            error_msg = "Invalid compliance data structure"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Convert to ComplianceDefinition models
        items = data.get("compliances", [])
        compliances = []

        for item in items:
            try:
                compliance = ComplianceDefinition(**item)
                compliances.append(compliance)
                logger.debug(f"Loaded compliance definition: {compliance.id}")
            except Exception as e:
                logger.error(f"Failed to create ComplianceDefinition from item: {e!s}")
                raise ValueError(f"Invalid compliance definition: {e!s}") from e

        logger.info(f"Successfully loaded {len(compliances)} compliance definitions")
        return compliances

    except Exception as e:
        if isinstance(e, (FileNotFoundError, yaml.YAMLError, ValueError)):
            raise
        error_msg = f"Unexpected error loading compliance definitions: {e!s}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def get_compliance_by_id(compliance_id: str) -> ComplianceDefinition:
    """
    Get a specific compliance definition by its ID.

    Args:
        compliance_id: The unique identifier of the compliance definition

    Returns:
        ComplianceDefinition: The matching compliance definition

    Raises:
        ValueError: If no compliance definition is found with the given ID
    """
    compliances = load_compliances()
    for compliance in compliances:
        if compliance.id == compliance_id:
            return compliance

    error_msg = f"No compliance definition found with ID: {compliance_id}"
    logger.error(error_msg)
    raise ValueError(error_msg)
