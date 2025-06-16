## Aggregator Template

## Task
You are given:
- A JSON object `failed_json` containing detailed results of compliance checks that did not pass  
- The original user prompt `original_prompt`

Your **inputs** (do not edit these):
{{  
  "failed_json": {failed_json},  
  "original_prompt": "{original_prompt}"  
}}

### Your Goals
1. Summarize the key compliance failures.  
2. Provide two actionable recommendations for each failed category.  
3. Rewrite the exact text of `original_prompt` into a single, new prompt that would satisfy all compliance requirements.

## Instructions

### 1. Analysis  
- Parse `failed_json`.  
- For each key (e.g. `"PC1"`), note its `name`, `critical_compliance_concern`, and why it failed.

### 2. Summarization  
Write one paragraph listing each failed ID with its name and main issue.

### 3. Recommendations  
Under each compliance ID, produce exactly two numbered items:



### 4. Rephrase Prompt  
Transform the **exact text** of `original_prompt` so that:
- It mitigates all identified issues
- Preserves the user’s original intent
- Would pass all compliance checks

## Output Format
Produce **only** this JSON object (no Markdown fences, no extra keys):

{{  
  "Aggregated Summary": "<your one-paragraph summary>",  
  "Recommendations": {{  
    "<CategoryID>": [  
      "1. <Cat name>: <first recommendation>",  
      "2. <Cat name>: <second recommendation>"  
    ],  
    "…": ["…"]  
  }},  
  "Rephrase Prompt": "<new compliant prompt>"  
}}
