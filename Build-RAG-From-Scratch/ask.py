"""
ask.py — Answer a question using the indexed knowledge base.

This is STEP 2 (ANSWER) from the architecture diagram:
  question -> embed (LOCAL) -> Qdrant search -> build prompt -> Claude -> answer

Usage:
  python ask.py "how do I restart the payments service?"
"""

import os
import sys

import requests
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# --- Config ---------------------------------------------------------------
COLLECTION = "knowledge_base"
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_URL = "http://localhost:6333"
TOP_K = 4                                  # how many chunks to retrieve
CLAUDE_MODEL = "claude-sonnet-5"
API_URL = "https://api.anthropic.com/v1/messages"

# --- 1. Get the question --------------------------------------------------
question = " ".join(sys.argv[1:]).strip()
if not question:
    print('Usage: python ask.py "your question here"')
    sys.exit(1)

# --- 2. Embed the question (same local model we indexed with) -------------
model = SentenceTransformer(MODEL_NAME)
query_vector = model.encode(question).tolist()

# --- 3. Search Qdrant for the most similar chunks -------------------------
client = QdrantClient(url=QDRANT_URL)
hits = client.query_points(
    collection_name=COLLECTION,
    query=query_vector,
    limit=TOP_K,
).points

# --- 4. Build the prompt: stuff the retrieved chunks in as context --------
context_blocks = []
for h in hits:
    src = h.payload["source"]
    text = h.payload["text"]
    context_blocks.append(f"[{src}]\n{text}")
context = "\n\n---\n\n".join(context_blocks)

prompt = f"""You are an on-call assistant. Answer the question using ONLY the
knowledge-base excerpts below. If the answer isn't in them, say so. Cite the
source file (e.g. [payments-service.md]) for any command or fact you give.

Knowledge-base excerpts:
{context}

Question: {question}
"""

# --- 5. Ask Claude (pure API call, no SDK) --------------------------------
resp = requests.post(
    API_URL,
    headers={
        "x-api-key": os.environ["CLAUDE_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    json={
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    },
)
resp.raise_for_status()
answer = resp.json()["content"][0]["text"]

# --- 6. Show the answer and where it came from ----------------------------
print("\n=== ANSWER ===\n")
print(answer)
print("\n=== RETRIEVED FROM ===")
for h in hits:
    print(f"  - {h.payload['source']}  ({h.payload['heading']})  score={h.score:.3f}")
