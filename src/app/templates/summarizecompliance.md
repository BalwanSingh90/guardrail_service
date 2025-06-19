Summarization Compliance Template
Task
Generate a concise summary strictly grounded in the source document, with no added or inferred information
Medium
Microsoft for Developers
.

Prohibit speculation about author intent, sentiment, or backgrounds
Medium
.

Preserve dates/times exactly as in the source
Microsoft Learn
.

Input
jsonc
Copy
Edit
{
  "document": "Full text of the source document here",
  "system_instructions": [
    "All information in each summary sentence must be explicitly mentioned in the document.",
    "Do not assume or change dates and times.",
    "Focus only on the main points (neither exhaustive nor overly brief)."
  ]
}
Definition
Grounded Summary: Every sentence must mirror exact facts from the document, without inference
Microsoft for Developers
.

No Speculation: Avoid assumptions about sentiment, purpose, or personal details
Medium
.

Date Preservation: Dates and times remain unchanged from the source
Microsoft Learn
.

Conciseness: Summaries must be coherent, focused, and of moderate length
Microsoft for Developers
.

Deliverable
A summarization component that:

Injects system instructions and source text into the chat prompt.

Calls Azure OpenAI’s summarization endpoint.

Returns a final grounded, coherent summary.

Logs compliance metrics (e.g., length, date fidelity).
