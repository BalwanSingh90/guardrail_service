import json
import os

import requests

INPUT_FILE = os.path.join("evaluation", "inputs", "test_cases.json")
OUTPUT_DIR = os.path.join("evaluation", "outputs", "raw_responses")
API_ENDPOINT = "http://localhost:8000/evaluate"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE) as f:
    test_cases = json.load(f)

for case in test_cases:
    case_id = case["id"]
    payload = {"user_input": case["user_input"], "context": case.get("context", "")}
    response = requests.post(API_ENDPOINT, json=payload)
    response.raise_for_status()
    result = response.json()
    out_path = os.path.join(OUTPUT_DIR, f"{case_id}.json")
    with open(out_path, "w") as out_f:
        json.dump(
            {"id": case_id, "input": payload, "response": result}, out_f, indent=2
        )
    print(f"Saved raw response for {case_id} to {out_path}")
