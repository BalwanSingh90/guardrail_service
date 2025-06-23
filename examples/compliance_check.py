import json
import sys
import os
from datetime import datetime
from pprint import pprint

import pytz
import requests

# --- Config ---
BASE_URL = "http://localhost:8081"
USE_CASE_ID = "azure_ccc"
HEADERS = {"Content-Type": "application/json"}
COMPLIANCE_FILTER = "include: PC1, 'Grounded Response'"  # Change here
EVAL_DIR = "evaluation"

# Ensure evaluation folder exists
os.makedirs(EVAL_DIR, exist_ok=True)


def get_filter_tag(expression: str) -> str:
    """Return a simplified tag based on filter expression."""
    expression = expression.lower()
    has_include = "include" in expression
    has_exclude = "exclude" in expression

    if has_include and has_exclude:
        return "mixed"
    elif has_include:
        return "include"
    elif has_exclude:
        return "exclude"
    else:
        return "all"


def current_est_datetime_str():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.strftime("%Y-%m-%d_%H-%M-%S")


def save_json_file(data: dict, suffix: str):
    tag = get_filter_tag(COMPLIANCE_FILTER)
    timestamp = current_est_datetime_str()
    filename = f"{EVAL_DIR}/scan_result_{tag}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\n📁 Results saved → {filename}")


def call_scan(prompt, documents):
    payload = {"prompt": prompt, "documents": documents}
    try:
        r = requests.post(
            f"{BASE_URL}/scan",
            params={"use_case_id": USE_CASE_ID, "compliance_filter": COMPLIANCE_FILTER},
            headers=HEADERS,
            json=payload,
            timeout=(5, 90),
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print("Scan API error:", e, file=sys.stderr)
        print("Response text:", getattr(e.response, "text", None), file=sys.stderr)
        sys.exit(1)

    try:
        return r.json()
    except json.JSONDecodeError:
        print("Scan API returned invalid JSON:", r.text, file=sys.stderr)
        sys.exit(1)


def extract_failures(scan_res):
    failed = {}
    for cid, detail in scan_res.get("detailed", {}).items():
        if not detail.get("passed", False):
            parsed = detail.get("parsed", {})
            failed[cid] = {
                "name": detail.get("name"),
                "description": detail.get("description"),
                "threshold": detail.get("threshold"),
                "passed": detail.get("passed"),
                "parsed": {
                    "critical_compliance_concern": parsed.get("critical_compliance_concern"),
                    "required_mitigation": parsed.get("required_mitigation"),
                    "reasoning": parsed.get("reasoning", []),
                    "insights": parsed.get("insights", []),
                    "recommendations": parsed.get("recommendations", []),
                    "summarization": parsed.get("summarization", ""),
                },
            }
    return failed


def call_aggregate(failed_json, original_prompt):
    payload = {"failed_json": failed_json, "original_prompt": original_prompt}
    try:
        r = requests.post(
            f"{BASE_URL}/aggregate/results",
            params={"use_case_id": USE_CASE_ID},
            headers=HEADERS,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print("Aggregate API error:", e, file=sys.stderr)
        print("Response text:", getattr(e.response, "text", None), file=sys.stderr)
        sys.exit(1)

    try:
        return r.json()
    except json.JSONDecodeError:
        print("Aggregate API returned invalid JSON:", r.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    prompt = """
You are a programming assistant. When a user asks for code:
Base your answers solely on the provided documents.\n\nIf docs are silent, explicitly state that no further data is available.
Follow the original API signature exactly and avoid network operations.\n\nEnsure all answers prohibit citations and avoid introducing any unauthorized information.
"""
    documents = [
        """# File: crypto_utils.py
def encrypt_data(data: bytes, key: bytes) -> bytes:
    \"\"\"
    Encrypts `data` using AES-256-CBC.
    • `data`plaintext bytes.
    • `key`  32-byte secret key.
    • Returns ciphertext bytes.
    • No network operations.
    \"\"\"
    ...
""",
        """• NEVER log plaintext, keys, or ciphertext.
• Do NOT transmit sensitive data over external networks.
• Follow the original API signature exactly.
• Use constant-time comparisons where feasible.
""",
        """© 2025 Contoso Corp.
This software is proprietary. Redistribution, publication, or relicensing
in any form is strictly prohibited without prior written consent.
""",
        """1. All answers must be based solely on the provided documents.
2. Every factual claim requires an inline citation to its source document.
3. If the documents lack information, explicitly state that no further data is available.
4. Do not invent or “fill in” missing references or specifications.
""",
    ]

    # Step 1: Scan
    scan_res = call_scan(prompt, documents)
    print("=== Scan Response ===")
    pprint(scan_res)

    # Save to file
    save_json_file(scan_res, suffix=get_filter_tag(COMPLIANCE_FILTER))

    # Step 2: Extract failures
    failed = extract_failures(scan_res)
    print("\n=== Aggregation Request ===")
    pprint({"failed_json": failed, "original_prompt": prompt})

    # Step 3: Optional Aggregate call
    # agg_res = call_aggregate(failed, prompt)
    # print("\n=== Aggregation Response ===")
    # pprint(agg_res)
