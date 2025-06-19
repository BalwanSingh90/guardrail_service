#!/usr/bin/env python3

import subprocess
import sys

def run_guardrail_linter():
    print("Running ruff linting on src/...")

    result = subprocess.run(["ruff", "check", "src"], capture_output=True, text=True)

    if result.returncode != 0:
        print("Guardrail Linter Failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

    print("Guardrail Linter Passed.")
    return 0

if __name__ == "__main__":
    run_guardrail_linter()
