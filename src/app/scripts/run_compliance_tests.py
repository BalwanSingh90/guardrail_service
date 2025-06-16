#!/usr/bin/env python3
"""
src/app/scripts/run_compliance_tests.py

Read test cases from a CSV in assets/data/, call the /scan endpoint,
and save each response (along with input) into src/output/ using filenames
that include index, category, complexity, and expected grade.

Configuration is loaded from environment variables (with sensible defaults).
"""

import json
import os
from pathlib import Path

import pandas as pd
import requests

# ------------------------------------------------------------------------------
# CONFIGURATION (from environment or defaults)
# ------------------------------------------------------------------------------
# Path to the CSV of test cases (defaults to our restructured location)
INPUT_CSV = os.getenv(
    "TEST_CSV",
    str(Path.cwd() / "assets" / "data" / "Compliance_Test_Cases__SDLC___Networking_.csv")
)

# Base output directory (we will place individual JSONs under src/output/)
OUTPUT_ROOT = Path(os.getenv("OUTPUT_DIR", str(Path.cwd() / "src" / "output")))

# Full API URL for compliance evaluation (defaults to our /scan endpoint)
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/scan")


# ------------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------------
def ensure_dir(path: Path):
    """Ensure a directory exists."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def load_test_cases(csv_path: Path) -> pd.DataFrame:
    """
    Load the CSV of test cases into a pandas DataFrame.
    Expect columns: "API Input" (a JSON string), "Category", "Complexity", "Expected Grade".
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Test CSV not found: {csv_path}")
    return pd.read_csv(csv_path, dtype=str)


def save_result(data: dict, output_dir: Path, filename: str):
    """Write a JSON file to output_dir/filename."""
    ensure_dir(output_dir)
    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved result to: {file_path}")


# ------------------------------------------------------------------------------
# MAIN SCRIPT
# ------------------------------------------------------------------------------
def main():
    csv_path = Path(INPUT_CSV)
    df = load_test_cases(csv_path)

    print(f"Loaded {len(df)} test cases from {csv_path}")

    for idx, row in df.iterrows():
        # Parse the API input (JSON string)
        try:
            payload = json.loads(row["API Input"])
        except Exception as e:
            print(f"[!] Skipping row {idx}: invalid JSON in 'API Input' → {e}")
            continue

        # Call the compliance API
        try:
            resp = requests.post(API_ENDPOINT, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            print(f"[!] Failed HTTP for row {idx}: {e}")
            continue

        # Construct a safe filename
        category = row.get("Category", "").replace(" ", "_")
        complexity = row.get("Complexity", "").replace(" ", "_")
        grade = row.get("Expected Grade", "").replace("/", "-")

        filename = f"{idx:03d}_{category}_{complexity}_{grade}.json"

        # Save both input and response under OUTPUT_ROOT
        # (we can group by category if desired, but here we save all in one folder)
        save_result({"input": payload, "response": result}, OUTPUT_ROOT, filename)

    print("All requests completed.")


if __name__ == "__main__":
    main()
