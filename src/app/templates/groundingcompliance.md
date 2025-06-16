Grounding Compliance Template
Task
Build a Retrieval-Augmented Generation (RAG) workflow using Azure AI Search as the retriever and Azure OpenAI for response generation 
Microsoft Learn
Microsoft Learn
.

Instruct the model via system messages to base answers only on retrieved documents.

Define fallback behavior when no relevant documents are found.

Input
jsonc
Copy
Edit
{
  "retriever": {
    "type": "AzureAI-Search",
    "index_name": "my-document-index"
  },
  "messages": [
    { "role": "system", "content": "Only use facts from the retrieved documents below." },
    { "role": "user",   "content": "User’s question requiring factual grounding." }
  ]
}
Definition
Retriever Integration: Azure AI Search supplies context via vector or keyword queries 
Microsoft Learn
.

System Messages: Enforce strict reliance on retrieved sources, avoiding external or assumed information 
Microsoft Learn
.

Fallback Logic: If the retriever returns no results, respond with a “not found in source documents” message 
Microsoft Learn
.

Deliverable
A pipeline or orchestrator that:

Queries Azure AI Search for relevant docs.

Constructs system + user messages with retrieved content.

Calls the Azure OpenAI chat API and returns grounded answers.

Handles no-result cases per policy.

