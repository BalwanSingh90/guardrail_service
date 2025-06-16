# Compliance Evaluation Template

## Task
Evaluate user input for compliance with content safety and ethical guidelines using a Chain-of-Thought approach. The evaluation should consider:
- Content safety and harm prevention
- Ethical AI usage
- Data privacy and security
- Transparency and accountability

## Input Format
```json
{
    "user_input": "Text to be evaluated for compliance",
    "context": "Optional additional context about the use case"
}
```

## Definition
The evaluation should follow a structured Chain-of-Thought process:

1. **Initial Analysis**
   - Identify key components and intended use
   - Map to relevant compliance categories
   - Note potential risk areas

2. **Compliance Categories**
   - Content Safety (violence, hate, sexual content, self-harm)
   - Ethical Usage (bias, fairness, transparency)
   - Privacy & Security (data handling, user protection)
   - Accountability (monitoring, oversight, human review)

3. **Severity Levels**
   - Safe: No concerns, fully compliant
   - Low: Minor concerns, easily addressable
   - Medium: Significant concerns, requires mitigation
   - High: Critical concerns, immediate action needed

## Examples

### Example 1: Safe Content
**Input**: "Our AI assistant helps users find recipes based on available ingredients."

**Chain of Thought**:
1. Purpose: Recipe recommendation
2. Risk Assessment:
   - No harmful content generation
   - Clear, beneficial use case
   - No privacy concerns
3. Compliance Check:
   - Content Safety: Safe (food-related content)
   - Ethical Usage: Safe (helpful, non-manipulative)
   - Privacy: Safe (ingredient data only)
   - Accountability: Safe (clear purpose)

**Evaluation**:
### Summarization:
The input describes a benign use case for recipe recommendations. The system's purpose is clear, helpful, and poses no significant compliance risks.

### Recommendations:
1. Implement ingredient data validation
2. Add nutritional information disclaimers
3. Include user preference options

### Insights:
1. Recipe recommendation systems typically fall under safe use cases
2. Focus on data accuracy and user preferences
3. Consider dietary restrictions and allergies

### Grade: 9/10

### Example 2: Medium Risk Content
**Input**: "Our AI assistant will generate songs lyrics when users request them."

**Chain of Thought**:
1. Purpose: Creative content generation
2. Risk Assessment:
   - Potential for harmful content
   - Copyright concerns
   - Age-appropriate content
3. Compliance Check:
   - Content Safety: Medium (needs filtering)
   - Ethical Usage: Medium (copyright issues)
   - Privacy: Safe (minimal data)
   - Accountability: Medium (needs oversight)

**Evaluation**:
### Summarization:
The input involves AI-generated lyrics, requiring careful content filtering and copyright management. While creative, it needs robust safeguards.

### Recommendations:
1. Implement content filtering for harmful themes
2. Add copyright detection and attribution
3. Include age-appropriate content controls
4. Establish human review for flagged content

### Insights:
1. Creative AI systems need stronger content controls
2. Copyright management is crucial for lyrics
3. Age-appropriate filtering is essential

### Grade: 6/10

## Deliverable
The evaluation should provide:

1. **Structured Output**
   - Summarization of compliance status
   - Specific recommendations for improvement
   - Key insights and patterns
   - Overall compliance grade (1-10)

2. **Required Sections**
   ```markdown
   ### Summarization:
   [Clear, concise summary of compliance status]

   ### Recommendations:
   1. [First actionable recommendation]
   2. [Second actionable recommendation]
   ...

   ### Insights:
   1. [First key observation]
   2. [Second key observation]
   ...

   ### Grade:
   [Numerical score from 1-10]
   ```

3. **Evaluation Criteria**
   - Content Safety: 40% weight
   - Ethical Usage: 30% weight
   - Privacy & Security: 20% weight
   - Accountability: 10% weight

## USER INPUT
[User input will be inserted here] 