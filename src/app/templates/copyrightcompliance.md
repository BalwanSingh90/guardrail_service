Copyright Compliance Template
Task
Implement the Customer Copyright Commitment (CCC) required mitigations to maintain IP indemnity 
Microsoft Learn
.

Embed a system metaprompt instructing “do not output verbatim copyrighted material” 
Microsoft Learn
.

Enforce protected-material detection filters in filter or annotate mode 
Microsoft Learn
.

Retain results of guided red-teaming and systematic measurement tests for audits 
Microsoft Learn
.

Input
jsonc
Copy
Edit
{
  "system_metaprompt": "To avoid copyright infringement, summarize instead of reproducing content verbatim.",
  "filter_settings": {
    "protected_material": "filter",
    "jailbreak_protection": "filter"
  },
  "evaluation_reports": [
    { "type": "red_team", "date": "2025-01-15", "path": "/reports/red_team_20250115.pdf" }
  ]
}
Definition
Metaprompt Insertion: System-level instruction to avoid verbatim reproduction 
Microsoft Learn
.

Protected-Material Filters: Azure filters block or annotate copyrighted content 
Microsoft Learn
.

Audit Reports: Documentation of red-team and systematic tests evidences compliance 
Microsoft Learn
.

CCC Indemnity: Microsoft defends customers if these mitigations are in place 
The Official Microsoft Blog
Techstrong.ai
.

Deliverable
A deployment script or chain that:

Configures system metaprompt and filter settings on the Azure OpenAI endpoint.

Runs and archives red-team/systematic tests.

Generates an audit bundle (prompts, filter logs, test reports).

Produces a compliance summary report for legal review.

