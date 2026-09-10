#!/usr/bin/env bash
# Demo 1 (cold open) — a plain LLM answering a company-specific question with NO RAG.
# It will be confident and wrong, because it has never seen our knowledge-base.
# Needs CLAUDE_KEY set in your environment (never show it on camera).

curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-5",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "How do I restart the payments service on our platform?"}]
  }' | jq -r '.content[0].text'
