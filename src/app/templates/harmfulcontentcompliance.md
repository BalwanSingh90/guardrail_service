## Harmful Content Compliance Template ##
## Task
Enforce Azure’s multi-class content filter on both prompts and completions to detect violence, hate, sexual content, and self-harm 
Microsoft Learn
Microsoft Learn
.

Apply configurable severity thresholds (safe, low, medium, high) and optional jailbreak/code classifiers 
Microsoft Learn
Medium
.

Embed recommended safety system messages to mitigate harmful outputs at the prompt level 
Microsoft Learn
.

Input
jsonc
Copy
Edit
{
  "model_deployment": "gpt-4o",
  "messages": [
    { "role": "system", "content": "[Safety system messages]" },
    { "role": "user",   "content": "User’s input text to check" }
  ],
  "filter_policy": {
    "severity_threshold": "medium",
    "jailbreak_protection": true,
    "public_code_detection": true
  }
}
Definition
Multi-class Filtering: Classification models detect four harmful categories at four severity levels 
Microsoft Learn
.

Jailbreak & Code Checks: Optional classifiers guard against prompt red-teaming and illicit code retrieval 
Microsoft Learn
.

Safety Messages: System messages steer the LLM away from generating harmful content 
Microsoft Learn
.

Deliverable
A wrapper function or chain that:

Sends system + user messages through the content filter API.

Blocks or safely completes flagged content.

Logs category scores and severity levels.

Surfaces human-review workflows for medium-severity cases.

