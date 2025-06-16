# src/app/services/parser.py

import re
from typing import Any, Dict

from src.app.models.evaluation_patterns import OUTPUT_PATTERNS


def parse_evaluation(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}

    for key, pattern in OUTPUT_PATTERNS.items():
        match = re.search(pattern, text)
        content = match.group(1).strip() if (match and match.group(1)) else ""

        if key in ["reasoning", "recommendations", "insights"]:
            items = re.findall(r"\d+\.\s*(.+)", content)
            result[key] = items or ([content] if content else [])

        elif key == "grade":
            # Match variations: with/without backticks, with/without space
            grade_match = re.search(r"Score:\s*`?([0-9]+\.[0-9]{2})\s*/?\s*1`?", text)
            result[key] = grade_match.group(1) if grade_match else "0.00"

        else:
            result[key] = content

    return result
