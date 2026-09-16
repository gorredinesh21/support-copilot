# Azure OpenAI rate limiting
## Errors
- 429: requests per minute or tokens per minute exceeded.
- `content_filter` result: policy block, not a rate limit.
## Knobs
Per-deployment quota (TPM/RPM) set at creation; can be raised via a support request with the use case.
## Client pattern
Exponential backoff with jitter, honor `retry-after` header; batch prompts where possible; route low-priority traffic to a smaller model deployment.
## Monitoring
Emit a custom metric on each 429 with deployment name; alert at >1% of calls for 10 minutes.