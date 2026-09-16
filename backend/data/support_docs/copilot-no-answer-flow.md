# No-answer flow
## Behavior
When retrieval confidence is low or the model returns the no-answer sentence, the copilot:
1. Shows "I could not find this in the support docs." with zero citations.
2. Surfaces a one-click "Ask an engineer" button that opens a pre-filled ticket.
3. Emits telemetry: `success=true`, `customDimensions.cited=false`, top_doc=null.
## Why it matters
The no-answer path is a feature, not a failure: it prevents hallucinated answers and feeds the KB gap list (weekly review of no-answer questions by the KB owner).