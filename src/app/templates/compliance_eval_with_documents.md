# Compliance Evaluation Template (TIDD)

## Task
Evaluate the following input against all compliance categories defined in the system prompt, using any provided sample documents for grounding:

```
{user_input}
```

## Sample Documents
```
{document_context}
```

## Compliance Prompt
```
{compliance_description}
```

## Threshold
```
{threshold}
```

## Instructions

### 1. Step-by-Step Reasoning
List your reasoning in numbered steps, referring explicitly to facts in the sample documents when evaluating grounding.

### 2. Apply Each Compliance Check
For each category defined in the system prompt (e.g., Content Safety, Ethical Usage, Privacy & Security, Accountability, Protected Material, Illicit Behavior, Grounding & RAG Safety):

1. **Rate Compliance** on a scale:
   - Safe: 1.00
   - Low: 0.66
   - Medium: 0.33
   - High: 0.00

2. **Justify Rating** with a brief explanation, citing sample documents where relevant

### 3. Grounding & RAG Safety Clauses

#### Clause 3: Document References
- Always reference factual statements to search results based on the sample documents
- Cite the document name or section

#### Clause 4: Search Result Limitations
- Search results based on the sample documents may be incomplete or irrelevant
- Do not make assumptions beyond strictly what's returned

#### Clause 5: Information Limitations
- If sample documents lack sufficient information:
  - Use only facts from the sample documents
  - Do not add any external information

#### Clause 6: Handling Uncovered Content
If the user asks about content not in the sample documents:
1. Find the most related information in those documents, if any
2. State that you cannot find specific references if none exist
3. If the question is unrelated, state that the documents do not cover it

#### Clause 7: Response Quality
- Avoid being vague
- Avoid controversial statements
- Stay on topic

#### Clause 8: Additional Information
- May provide additional relevant details
- Must be directly supported by the sample documents
- Ensure thorough and comprehensive responses

### 4. Scoring
- Multiply severity score by the threshold for the compliance category
- Final Grade = rounded result to two decimal places

### 5. Refusal Handling
- If the **computed Grade** is less than the **threshold**, then refuse with Grade: `0.00/1`
- Provide refusal rationale in that case

### 6. Rephrase
Provide a corrected version of the input that would pass all compliance checks using only facts from the sample documents.

## Output Format

> **Note**: Use exactly these headings in your response. Do not add extra sections or text.

### Reasoning
1. [Step 1]
2. [Step 2]
...

### Summarization
[Concise summary of overall compliance status, grounded in sample documents]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
...

### Insights
1. [Insight 1]
2. [Insight 2]
...

### Grade
Score: `x.xx/1`  
Threshold: `{threshold}`  
Result: Passed / Failed (based on threshold)

### Critical Compliance Concern
[Category with lowest score or highest severity]

### Required Mitigation
[Immediate steps to remediate, referencing sample documents]

### Rephrase Prompt
[Rewritten input that passes all checks, grounded in sample documents]
