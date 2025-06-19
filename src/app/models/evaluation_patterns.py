# src/app/models/evaluation_patterns.py

"""
Evaluation Patterns Module

This module defines regular expression patterns used for parsing and extracting structured
information from evaluation outputs. These patterns are used to parse different sections
of the evaluation response, such as problem description, failure reason, fix suggestions, etc.

The patterns are designed to extract content between specific markdown headers (###) and
handle various formatting cases. Each pattern is carefully crafted to capture the content
while being resilient to minor formatting variations.
"""

import re
from typing import Dict, Pattern

from ..core.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Dictionary of compiled regex patterns for extracting different sections from evaluation output
OUTPUT_PATTERNS: Dict[str, Pattern] = {
    # Extracts the problem section
    "problem": re.compile(
        r"###\s*Problem\s*:?[\r\n]+([\s\S]*?)(?=###\s*Why It Failed\s*:|$)",
        re.MULTILINE,
    ),
    # Extracts the why it failed section
    "why_it_failed": re.compile(
        r"###\s*Why It Failed\s*:?[\r\n]+([\s\S]*?)(?=###\s*What To Fix\s*:|$)",
        re.MULTILINE,
    ),
    # Extracts what to fix section
    "what_to_fix": re.compile(
        r"###\s*What To Fix\s*:?[\r\n]+([\s\S]*?)(?=###\s*Prompt Rephrase\s*:|$)",
        re.MULTILINE,
    ),
    # Extracts prompt rephrase suggestion
    "rephrase_prompt": re.compile(
        r"###\s*Prompt Rephrase\s*:?[\r\n]+([\s\S]*?)(?=###\s*Compliance ID and Name\s*:|$)",
        re.MULTILINE,
    ),
    # Extracts compliance ID and name
    "compliance_id_and_name": re.compile(
        r"###\s*Compliance ID and Name\s*:?[\r\n]+([\s\S]*?)$", re.MULTILINE
    ),
    # Extracts the grade (optional but supported)
    "grade": re.compile(
        r"###\s*Grade\s*:?[\r\n]*`?([0-9]*\.?[0-9]+/1)`?", re.MULTILINE
    ),
}


def validate_patterns() -> None:
    """
    Validates all patterns to ensure they are properly compiled and functional.
    Logs any issues found during validation.
    """
    logger.debug("Validating evaluation patterns...")

    for pattern_name, pattern in OUTPUT_PATTERNS.items():
        try:
            # Test pattern with a minimal valid input
            test_input = f"### {pattern_name.replace('_', ' ').title()}:\nTest content\n### Next Section:"
            if not pattern.search(test_input):
                logger.warning(f"Pattern '{pattern_name}' failed to match test input")
            else:
                logger.debug(f"Pattern '{pattern_name}' validated successfully")
        except Exception as e:
            logger.error(f"Error validating pattern '{pattern_name}': {e!s}")
            raise


# Validate patterns when module is imported
try:
    validate_patterns()
    logger.info("All evaluation patterns validated successfully")
except Exception as e:
    logger.error(f"Failed to validate evaluation patterns: {e!s}")
    raise
