# Guardrail Service

> Status : active development / beta

Guardrail Service is a FastAPI‑based micro‑service that performs LLM prompt compliance scanning and prompt remediation.
It integrates with Azure OpenAI Assistants, evaluates prompts against configurable “policy” rules, and—when necessary—automatically rewrites them so they pass every compliance check.

## Features

| Module                                  | Purpose                                                                                  |
| --------------------------------------- | ---------------------------------------------------------------------------------------- |
| `src/app/routers/scan_router.py`        | Runs scan – streams the Assistant, produces a per‑policy breakdown (PC1‑PC8)         |
| `src/app/routers/aggregation_router.py` | Runs aggregate – summarises all failed compliances and returns a single fixed prompt |
| `src/app/services/`                    | Helpers for compliance templates, parsing, logging                                       |
| `src/logs/`                             | JSON audit logs for every request (auto‑rotated)                                         |

 Zero‑cold‑start Assistants via a singleton instance & in‑thread streaming.
 Config‑driven compliances (`.yaml` per use‑case) with live reload.
 Fully async; low‑latency thanks to `create_and_stream`.
 First‑class developer ergonomics: ruff, isort, pre‑commit, GitHub Actions CI.

## Architecture snapshot

FastAPI ▶ /scan        ──►  Azure OpenAI Assistant (stream)
        │                 ◄── parsed deltas ← PC1…PC8
        ├─ /aggregate  ──►  Azure OpenAI Chat → Aggregator LLM
        │
        └─ /healthz    ──►  200 OK


## Getting Started

### 1. Clone & install

```bash
git clone git@github.com:BalwanSingh90/guardrail_service.git
cd guardrail_service
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

### ENVIRONMENT VARIABLES ###
AZURE_OPENAI_API_KEY=…
AZURE_OPENAI_ENDPOINT=…
AZURE_OPENAI_DEPLOYMENT=…
AZURE_OPENAI_API_VERSION=2024-05-01-preview
LLM_TEMPERATURE=0.2
LOG_DIR=src/logs
DEFAULT_USE_CASE=azure_ccc


### 3. Run locally

```bash
uvicorn src.app.main:app --reload --port 8081
```

### 4. Call the API

```bash
curl -X POST http://localhost:8081/scan \
     -H "Content-Type: application/json" \
     -d '{"prompt": "…", "documents": ["…"]}'
```
## Code Quality

| Tool      | Command          | Notes                        |
| --------- | ---------------- | ---------------------------- |
| ruff  | `ruff check src` | Linting (PEP8, flake8, etc.) |
| isort | `isort src`      | Import sorting               |
| black | `black src`      | (optional) code formatting   |

A convenience script is provided:

```bash
make fmt   # runs isort then black
make lint  # runs ruff
```

Pre‑commit hooks are set up; just

```bash
pre-commit install
```
## Branch & Git workflow

 `master` – deployable, protected.  (Was renamed from `main`; old `master` deleted.)
 Feature work → short‑lived branches `feature/<slug>`
 PRs require passing CI & at least one review.

Rename recipe (for reference)

```bash
git branch -m master main
git push -u origin main
# On GitHub: Settings → Branches → Default → main
```

---

## Contributing

Pull requests welcome!  Please:

1. Open an issue or draft PR first.
2. Follow the style‑guide (`ruff --fix`, `isort`).
3. Add/adjust unit tests in `tests/`.

## License

© 2025 Contoso Corp.  All rights reserved.  Redistribution prohibited without written consent.
