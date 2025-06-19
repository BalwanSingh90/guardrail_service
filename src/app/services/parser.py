import re
from typing import Any, Dict

SECTION_HEADERS = [
    ("problem",                 r"###\s*Problem"),
    ("why_it_failed",           r"###\s*Why\s+It\s+Failed"),
    ("what_to_fix",             r"###\s*What\s+To\s+Fix"),
    ("rephrase_prompt",         r"###\s*Prompt\s+Rephrase"),
    ("compliance_id_and_name",  r"###\s*Compliance\s+ID\s+and\s+Name"),
    ("grade_raw",               r"###\s*Grade"),
]


def _extract_block(text: str, start_pat: str, next_pat: str | None) -> str:
    """
    Grab everything between `start_pat` and `next_pat` (or EOF) and return trimmed text.
    """
    pattern = rf"{start_pat}\s*\n(.*?)(?=\n{next_pat}\s*\n|\Z)" if next_pat else rf"{start_pat}\s*\n(.*)\Z"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_evaluation(text: str) -> Dict[str, Any]:
    """
    Parse a compliance-evaluation response into a structured dictionary.

    Returns keys:
        problem, why_it_failed, what_to_fix, rephrase_prompt,
        compliance_id_and_name, grade  (dict with score, threshold, result, score_ratio)
    """
    out: Dict[str, Any] = {}

    # ── 1. Extract each block ──────────────────────────────────────────
    for idx, (key, hdr_pat) in enumerate(SECTION_HEADERS):
        next_pat = SECTION_HEADERS[idx + 1][1] if idx + 1 < len(SECTION_HEADERS) else None
        block = _extract_block(text, hdr_pat, next_pat)
        out[key] = block

    # Rename the raw grade block and parse its fields
    grade_block = out.pop("grade_raw", "")

    # ── 2. Parse the “Grade” block (score / threshold / result) ────────
    # Example lines:
    #   Score: `0.66/1`
    #   Threshold: `0.97`
    #   Result: Failed
    score, denom = 0.0, 1.0
    if m := re.search(r"Score:\s*`?(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)`?", grade_block):
        score, denom = map(float, m.groups())
    threshold = float(m.group(1)) if (m := re.search(r"Threshold:\s*`?(\d+(?:\.\d+)?)`?", grade_block)) else None
    result    = (m.group(1) if (m := re.search(r"Result:\s*(Passed|Failed)", grade_block, re.I)) else None)

    out["grade"] = {
        "score_raw": score,
        "denominator": denom,
        "score_ratio": score / denom if denom else None,
        "threshold": threshold,
        "result": result,
    }

    return out
