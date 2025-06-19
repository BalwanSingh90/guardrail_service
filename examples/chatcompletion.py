"""compliance_agent.py LangGraph compliance evaluator (sync OpenAI call)
Run:
    python compliance_agent.py "<your prompt>"
Requires:
    langgraph>=0.4.8
    openai>=1.13.3
    Env vars AZURE_OPENAI_ENDPOINT / API_KEY / API_VERSION / DEPLOYMENT
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, List, TypedDict

import openai
from langgraph.graph import END, START, StateGraph


# ───────────────── Settings ─────────────────
class _Cfg(TypedDict):
    azure_endpoint: str
    azure_key: str
    azure_version: str
    deployment: str
    temperature: float
    top_p: float
    max_tokens: int

cfg: _Cfg = {
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    "azure_key": os.getenv("AZURE_OPENAI_KEY", ""),
    "azure_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
    "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800,
}

openai_client = openai.AzureOpenAI(
    api_key=cfg["azure_key"],
    azure_endpoint=cfg["azure_endpoint"],
    api_version=cfg["azure_version"],
)

# ──────────────── TypedDict state ───────────
class InputState(TypedDict):
    user_input: str
    documents: list[str]

class RenderedState(InputState):
    rendered_prompt: str

class CalledState(RenderedState):
    raw_output: str

class OutputState(TypedDict):
    graph_output: Any

# ─────────────── Template helpers ───────────
TEMPLATE = """## Task
You are an AI compliance evaluator. Review the user input against a specific compliance requirement using the provided sample documents.
Your goal is to identify **violations**, explain **why** they failed, suggest **how to fix them**, and rephrase the prompt only if the compliance score is below the threshold.

## Inputs

### User Input
{user_input}

### Sample Documents
{document_context}

### Compliance Prompt
{compliance_prompt}

### COMPLIANCE NAME
{compliance_name}

### COMPLIANCE DESCRIPTION
{compliance_description}

### Threshold
{threshold}

## Instructions
- Focus only on the **assigned compliance category** for this evaluation.
- Use **only** the provided documents or chat history as your evidence base.
- If facts are missing, assume no information and **do not extrapolate**.
- Follow the output format **exactly**. Do **not** output anything else.

**Compliant-by-default rule**  
If the user input:
1. Explicitly directs the assistant to rely solely on the provided documentation **and**  
2. Explicitly forbids unauthorized actions (modifications, network operations, licensing changes, etc.),  

then the prompt is **fully compliant**. In that case set **severity = 0.00**, Grade = 1.00, Result = Passed.

- Do **NOT** fail prompts that conservatively instruct the model to *avoid* undocumented or unauthorized actions when that aligns with the sample documents.
- Rephrase the prompt only when **severity > 0**.
- The rephrased prompt should modify **only** the parts necessary to pass compliance and **must not** copy text from the sample documents.

### Severity scale
| Level  | Value | When to use |
|--------|-------|-------------|
| Safe   | 0.00  | Prompt meets all compliance requirements. |
| Low    | 0.33  | Minor ambiguity; could use clarification. |
| Medium | 0.66  | Omits or contradicts a key requirement.   |
| High   | 1.00  | Explicitly requests disallowed actions.   |

Grade = **1 – severity** (round to two decimals).  
If Grade ≥ Threshold → **Passed**, else → **Failed**.

If severity = High **and** Grade < Threshold, refuse with Grade `0.00/1` and provide a brief refusal rationale.

## Output Format

### Problem
<Short summary of what’s non-compliant — or “No compliance issue detected.”>

### Why It Failed
<Explanation of the violation — or “Prompt meets all compliance requirements.”>

### What To Fix
<Brief actionable fix — or “No fixes necessary.”>

### Prompt Rephrase
<Only if failed: rewrite the input so that it fully complies>

### Compliance ID and Name
`{{id}}` – {{name}}

### Grade
Score: `x.xx/1`  
Threshold: `{threshold}`  
Result: Passed / Failed
"""


def docs_block(docs: List[str]) -> str:
    if not docs:
        return "No documents provided"
    return "\n---\n".join(docs)

# ───────────────────── Nodes ─────────────────

def render_node(state: InputState) -> RenderedState:
    vars = {
    "user_input": "Provide a one-sentence summary of `encrypt_data`.",
    "document_context": "```python\ndef encrypt_data(...): ...\n```",
    "compliance_prompt": "Generate your answer only using the provided docs.",
    "compliance_name": "Grounded Response",
    "compliance_description": (
        "- Ensure answers are strictly based on provided source documents\n"
        "- No extrapolation beyond those documents"
    ),
    "threshold": 0.99,
}

    # 2.  Render the template
    rendered_prompt = TEMPLATE.format(**vars)
    return {
        **state,
        "rendered_prompt": rendered_prompt
    }


def call_node(state: RenderedState) -> CalledState:
    """Synchronous OpenAI call so graph.invoke works."""
    resp = openai_client.chat.completions.create(
        model=cfg["deployment"],
        messages=[
            {"role": "system", "content": "You are an AI assistant that helps people"},
            {"role": "user", "content": state["rendered_prompt"]},
        ],
        temperature=cfg["temperature"],
        top_p=cfg["top_p"],
        max_tokens=cfg["max_tokens"],
    )
    return {**state, "raw_output": resp.choices[0].message.content.strip()}


def parse_node(state: CalledState) -> OutputState:
    text = state["raw_output"]
    print(text)
    def grab(h):
        m = re.search(rf"###\s*{h}[^\n]*\n(.*?)(?=\n###|$)", text, re.S)
        return (m.group(1).strip() if m else "")
    return {"graph_output": {
        "problem": grab("Problem"),
        "why_it_failed": grab("Why It Failed"),
        "what_to_fix": grab("What To Fix"),
        "grade": grab("Grade"),
    }}

# ─────────────── Build the graph ────────────
builder = StateGraph(OutputState, input=InputState, output=OutputState)

builder.add_node("render", render_node)
builder.add_node("call", call_node)
builder.add_node("parse", parse_node)

builder.add_edge(START, "render")
builder.add_edge("render", "call")
builder.add_edge("call", "parse")
builder.add_edge("parse", END)

graph = builder.compile()

# ─────────────── CLI entry point ────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compliance_agent.py \"<prompt>\"")
        sys.exit(1)

    result = graph.invoke({
        "user_input": sys.argv[1],
        "documents": [],
    })
    json.dump(result, sys.stdout, indent=2)
    print()
