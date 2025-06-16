# src/app/models/evaluation_patterns.py

"""
Evaluation Patterns Module

This module defines regular expression patterns used for parsing and extracting structured
information from evaluation outputs. These patterns are used to parse different sections
of the evaluation response, such as reasoning, summarization, recommendations, etc.

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
    # Extracts the reasoning section, capturing all content until the next section or end
    "reasoning": re.compile(
        r"###\s*Reasoning\s*:?[\r\n]+([\s\S]*?)(?=###\s*Summarization\s*:|$)",
        re.MULTILINE
    ),

    # Extracts the summarization section, capturing the main points and conclusions
    "summarization": re.compile(
        r"###\s*Summarization\s*:?[\r\n]+([\s\S]*?)(?=###\s*Recommendations\s*:|$)",
        re.MULTILINE
    ),

    # Extracts the recommendations section, capturing suggested actions or improvements
    "recommendations": re.compile(
        r"###\s*Recommendations\s*:?[\r\n]+([\s\S]*?)(?=###\s*Insights\s*:|$)",
        re.MULTILINE
    ),

    # Extracts the insights section, capturing key observations and analysis
    "insights": re.compile(
        r"###\s*Insights\s*:?[\r\n]+([\s\S]*?)(?=###\s*Grade\s*:|$)",
        re.MULTILINE
    ),

    # Extracts the grade section, capturing the numerical score (0-1)
    # Handles both plain numbers and numbers in backticks
    "grade": re.compile(
        r"###\s*Grade\s*:?[\r\n]*`?([0-9]*\.?[0-9]+/1)`?(?=###\s*Critical Compliance Concern\s*:|$)",
        re.MULTILINE
    ),

    # Extracts critical compliance concerns, capturing major issues identified
    "critical_compliance_concern": re.compile(
        r"###\s*Critical Compliance Concern\s*:?[\r\n]+([\s\S]*?)(?=###\s*Required Mitigation\s*:|$)",
        re.MULTILINE
    ),

    # Extracts required mitigation steps, capturing necessary actions to address concerns
    "required_mitigation": re.compile(
        r"###\s*Required Mitigation\s*:?[\r\n]+([\s\S]*?)(?=###\s*Rephrase Prompt\s*:|$)",
        re.MULTILINE
    ),

    # Extracts the rephrased prompt, capturing the suggested alternative wording
    "rephrase_prompt": re.compile(
        r"###\s*Rephrase Prompt\s*:?[\r\n]+([\s\S]*?)$",
        re.MULTILINE
    )
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
            test_input = f"### {pattern_name.title()}:\nTest content\n### Next Section:"
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
