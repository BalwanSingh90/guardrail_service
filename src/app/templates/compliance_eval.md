# Compliance Evaluation Template (TIDD)

## Task
{task}

**Compliance Rule Description**: {compliance_description}  
**Threshold**: {threshold}

**Input:**: {user_input}

## Instructions

### 1. Step-by-Step Reasoning
List your reasoning in numbered steps before applying the specific compliance check.

### 2. Apply Compliance Check
Based on the rule provided in the system prompt (e.g., Content Safety, Privacy & Security, etc.):

1. **Rate Severity** on a numeric scale:
   - Safe: 0.00  
   - Low: 0.33  
   - Medium: 0.66  
   - High: 1.00

2. **Justify Rating** with a brief explanation

3. **Compute Score (Grade)**:
   - Grade = 1.00 - severity
   - Round to two decimal places

4. **Determine Pass/Fail**:
   - If Grade ≥ Threshold → Result: Passed
   - Else → Result: Failed

5. **Refusal Handling**:
   - If severity = High and Grade < Threshold, refuse with Grade: `0.00/1`
   - Provide refusal rationale

### 3. Rephrase Input
Provide a corrected version of the input that would pass this compliance check.

---

## Output Format

> **Note**: Use exactly these headings in your response. Do not add extra sections or text.

### Reasoning
1. [Step 1]  
2. [Step 2]  
...

### Summarization
[Brief summary of compliance status for this rule]

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
[If refusing: name the problematic element]

### Required Mitigation
[Immediate actions to remedy]

### Rephrase Prompt
[Rewritten input that passes this compliance]
