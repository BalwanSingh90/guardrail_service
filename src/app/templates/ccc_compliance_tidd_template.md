# Customer Copyright Commitment (CCC) Compliance

## Overview
The Customer Copyright Commitment (CCC) is a provision in the Microsoft Product Terms that obligates Microsoft to defend customers against certain third-party intellectual property claims related to output content from Azure OpenAI Service or Configurable GAI Services. citeturn0search0 citeturn0search2

## Universal Required Mitigations
- **Metaprompt Insertion**: Include a system-level instruction directing the model to avoid outputting verbatim copyrighted material. citeturn0search0
- **Evaluation Reports**: Conduct guided red-teaming or systematic measurement tests and retain reports for audit. citeturn0search0turn0search1
- **Code of Conduct Compliance**: Adhere to Azure OpenAI Service Code of Conduct at all times. citeturn0search0

## Additional Required Mitigations for Text & Code Generation
- **Protected Material Detection Filters**: Enable Azure’s filters in “filter” or “annotate” mode to detect and block or annotate protected content. citeturn0search0 citeturn0search3
- **Prompt Shield**: Activate jailbreak-protection filters to block malicious prompt attempts. citeturn0search0
- **Asynchronous Filtering**: Ensure outputs flagged retroactively are filtered or licensed appropriately. citeturn0search0

## TIDD Framework Template

### Task
- Implement metaprompt, content filters, Prompt Shield, and asynchronous filtering.
- Conduct periodic red-team and systematic measurement tests.
- Document and retain all evaluation and filter logs for audit.

### Input
```json
{
  "model_deployment": "gpt-4-deployment",
  "system_metaprompt": "To avoid copyright infringements, do not output verbatim content from existing works.",
  "content_filters": {
    "protected_material": "filter",
    "jailbreak_protection": "filter",
    "async_filtering": true
  },
  "evaluation_reports": [
    {
      "type": "red_team",
      "date": "2024-12-01",
      "findings_path": "/path/to/red_team_report.pdf"
    }
  ]
}
```

### Definition
- **Universal Mitigations**: Core safeguards for all Azure OpenAI deployments (metaprompt, evaluation) citeturn0search0.
- **Use-Case Mitigations**: Additional controls for text and code generation (filters, Prompt Shield) citeturn0search0.
- **Effective Dates**: Mitigations must be live by the published effective dates; new requirements take effect upon publication. citeturn0search0
- **Audit Trail**: Maintain evidence—configuration snapshots, filter logs, evaluation reports—for CCC defense. citeturn0search0turn0search7

### Deliverable
- **Compliance Checklist**: JSON or script verifying metaprompt and filter settings.
- **Evaluation Schedule**: Automated red-team and systematic tests cadence.
- **Audit Bundle**: Metaprompt text, filter configuration, logs, reports.
- **Compliance Report**: Summary of enabled mitigations, test coverage, findings, and remediation actions. citeturn0search0turn0search1

## Few-Shot Examples

### Example 1: Chatbot Use Case
**Input**:
```json
{
  "model_deployment": "gpt-4-chatbot",
  "system_metaprompt": "Avoid reproducing any copyrighted content; summarize instead.",
  "content_filters": {"protected_material":"filter","jailbreak_protection":"filter","async_filtering":false},
  "evaluation_reports":[]
}
```
**Output**:
- Metaprompt applied to all chat messages.
- Filters configured in filter mode.
- No asynchronous filtering.
- Evaluation: placeholder for future red-team tests.

### Example 2: Code Generation Use Case
**Input**:
```json
{
  "model_deployment": "gpt-4-code",
  "system_metaprompt": "Only generate original code; do not copy from existing repositories.",
  "content_filters": {"protected_material":"annotate","jailbreak_protection":"filter","async_filtering":true},
  "evaluation_reports":[{"type":"systematic","date":"2024-12-01","findings_path":"/reports/systematic_test.pdf"}]
}
```
**Output**:
- Protected content annotated.
- Prompt Shield active.
- Async filtering enabled with logs retained.

## Chain-of-Thought (COT) Prompt Techniques
- **Step-by-Step Reasoning**: Prefix tasks with “Let’s think through the compliance requirements step by step:”.  
- **Intermediate Outputs**: Ask the model to list interim mitigation checks before final output.  
- **Self-critique**: Include “Review your plan and identify any missing safeguards before confirming compliance.”  
