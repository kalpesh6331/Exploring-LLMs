"""
ask_tree.py — Answer a question by NAVIGATING the tree, not by comparing vectors.

Two calls to Claude:
  1. NAVIGATE — here is the table of contents, which docs and sections hold
                the answer?  (it is allowed to say "none of them")
  2. ANSWER   — here is the text of exactly those sections, answer from it.

No embedding model. No vector database. One dependency: requests.
"""

import os
import re
import sys
import json
import time

import requests

# --- Config ---------------------------------------------------------------
KB_DIR = "knowledge-base"
TREE_FILE = "tree.json"
CLAUDE_MODEL = "claude-sonnet-5"
API_URL = "https://api.anthropic.com/v1/messages"

calls = 0                                  # count them, so we can be honest

# --- A small helper: one call to Claude -----------------------------------
def ask_claude(prompt, max_tokens=1024):
    global calls
    calls += 1
    resp = requests.post(
        API_URL,
        headers={
            "x-api-key": os.environ["CLAUDE_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={"model": CLAUDE_MODEL, "max_tokens": max_tokens,
              "messages": [{"role": "user", "content": prompt}]},
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

# --- 1. Get the question --------------------------------------------------
question = " ".join(sys.argv[1:]) or input("Question: ")
start = time.time()

# --- 2. Load the tree and render it as plain text -------------------------
# This is the whole knowledge base as a table of contents — about 2,700
# tokens for 60 docs. It goes into the prompt in one piece.
with open(TREE_FILE) as f:
    tree = json.load(f)

toc = "\n".join(
    f"{d['path']} | {d['title']} | {d['summary']}"
    + (f" | sections: {', '.join(d['sections'])}" if d["sections"] else "")
    for d in tree
)

# --- 3. NAVIGATE: which docs and sections hold the answer? ----------------
nav_prompt = f"""You are navigating an engineering knowledge base. Below is its
table of contents: one line per document, as "path | title | summary | sections".

{toc}

Question: {question}

Pick ONLY the documents that actually answer the question. Prefer naming the
exact sections. If nothing here answers it, return an empty list — do not guess.

Reply with JSON only:
{{"reasoning": "one sentence on why you chose these",
  "docs": [{{"path": "...", "sections": ["..."]}}]}}
"""

nav_raw = ask_claude(nav_prompt)
nav = json.loads(re.search(r"\{.*\}", nav_raw, re.S).group(0))

print(f"\nNavigator: {nav['reasoning']}")
for d in nav["docs"]:
    print(f"  -> {d['path']}" + (f"  §{', §'.join(d['sections'])}" if d.get("sections") else ""))

# --- 4. Read the text of exactly those sections ---------------------------
# A "## " heading owns everything until the next "## ", so sub-sections
# underneath it come along for the ride.
def read_sections(path, wanted):
    with open(os.path.join(KB_DIR, path)) as f:
        text = f.read()
    if not wanted:
        return text                        # no sections named: take the whole doc

    blocks = []
    for name in wanted:
        pattern = rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)"
        match = re.search(pattern, text, re.S | re.M)
        if match:
            blocks.append(f"## {name}\n{match.group(1).strip()}")
    return "\n\n".join(blocks) if blocks else text

context = "\n\n".join(
    f"--- {d['path']} ---\n{read_sections(d['path'], d.get('sections', []))}"
    for d in nav["docs"]
)

# --- 5. ANSWER: ground the answer in what we just read --------------------
answer_prompt = f"""You are an on-call assistant. Answer the question using ONLY the
knowledge-base excerpts below. If the answer isn't in them, say so. Cite the
source file and section (e.g. [databases/postgres.md - Connection limits]).

Knowledge-base excerpts:
{context if context else "(nothing was retrieved)"}

Question: {question}
"""

answer = ask_claude(answer_prompt)

# --- 6. Show the answer, and what it cost ---------------------------------
print("\n" + "=" * 70)
print(answer.strip())
print("=" * 70)
print(f"{calls} Claude calls | {len(nav['docs'])} docs read | {time.time() - start:.1f}s")
