"""
benchmark.py — Score Ep 6's vector RAG against Ep 7's vectorless engine,
over the SAME 60-document corpus and the SAME 12 ground-truth questions.

Both engines use the prompts from their own episode, verbatim. The only thing
added here is instrumentation: token counts and wall-clock, which the demo
scripts don't collect.

The knowledge base and questions.json are identical to Episode 7's — the whole
point is that both engines search the same corpus and are graded on the same
questions.
"""

import os, re, sys, json, time
import requests

KB_DIR = "knowledge-base"          # the same 60 docs both engines search
TREE_FILE = "tree.json"            # built by build_tree.py
QUESTIONS = "questions.json"       # the ground truth, written before any answer was seen
COLLECTION = "knowledge_base_60"
EMBED_MODEL = "all-MiniLM-L6-v2"
QDRANT_URL = "http://localhost:6333"
CLAUDE_MODEL = "claude-sonnet-5"
API_URL = "https://api.anthropic.com/v1/messages"
TOP_K = 4

# --- one Claude call, instrumented ----------------------------------------
def claude(prompt, max_tokens=1024):
    r = requests.post(API_URL, headers={
        "x-api-key": os.environ["CLAUDE_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, json={"model": CLAUDE_MODEL, "max_tokens": max_tokens,
             "messages": [{"role": "user", "content": prompt}]})
    r.raise_for_status()
    d = r.json()
    u = d["usage"]
    # The first content block is not always text (it can be a thinking block),
    # so take the first block that actually is one.
    text = next((b["text"] for b in d["content"] if b.get("type") == "text"), "")
    return text, u["input_tokens"], u["output_tokens"]

# =========================== ENGINE A: VECTOR ==============================
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

_embed = SentenceTransformer(EMBED_MODEL)
_qdrant = QdrantClient(url=QDRANT_URL)

def ask_vector(question):
    t0 = time.time()
    qv = _embed.encode(question).tolist()
    hits = _qdrant.query_points(collection_name=COLLECTION, query=qv, limit=TOP_K).points
    sources = [h.payload["source"] for h in hits]
    context = "\n\n".join(f"[{h.payload['source']}]\n{h.payload['text']}" for h in hits)
    prompt = f"""You are an on-call assistant. Answer the question using ONLY the
knowledge-base excerpts below. If the answer isn't in them, say so. Cite the
source file (e.g. [payments-service.md]) for any command or fact you give.

Knowledge-base excerpts:
{context}

Question: {question}
"""
    answer, tin, tout = claude(prompt)
    return dict(answer=answer, sources=sources, calls=1,
                tokens_in=tin, tokens_out=tout, seconds=time.time() - t0,
                scores=[round(h.score, 3) for h in hits])

# ======================= ENGINE B: VECTORLESS ==============================
_tree = json.load(open(TREE_FILE))
_toc = "\n".join(
    f"{d['path']} | {d['title']} | {d['summary']}"
    + (f" | sections: {', '.join(d['sections'])}" if d["sections"] else "")
    for d in _tree)

def _read_sections(path, wanted):
    text = open(os.path.join(KB_DIR, path)).read()
    if not wanted:
        return text
    blocks = []
    for name in wanted:
        m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
        if m:
            blocks.append(f"## {name}\n{m.group(1).strip()}")
    return "\n\n".join(blocks) if blocks else text

def ask_vectorless(question):
    t0 = time.time()
    nav_prompt = f"""You are navigating an engineering knowledge base. Below is its
table of contents: one line per document, as "path | title | summary | sections".

{_toc}

Question: {question}

Pick ONLY the documents that actually answer the question. Prefer naming the
exact sections. If nothing here answers it, return an empty list — do not guess.

Reply with JSON only:
{{"reasoning": "one sentence on why you chose these",
  "docs": [{{"path": "...", "sections": ["..."]}}]}}
"""
    raw, tin1, tout1 = claude(nav_prompt)
    nav = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
    sources = [d["path"] for d in nav["docs"]]
    context = "\n\n".join(
        f"--- {d['path']} ---\n{_read_sections(d['path'], d.get('sections', []))}"
        for d in nav["docs"])
    answer_prompt = f"""You are an on-call assistant. Answer the question using ONLY the
knowledge-base excerpts below. If the answer isn't in them, say so. Cite the
source file and section (e.g. [databases/postgres.md - Connection limits]).

Knowledge-base excerpts:
{context if context else "(nothing was retrieved)"}

Question: {question}
"""
    answer, tin2, tout2 = claude(answer_prompt)
    return dict(answer=answer, sources=sources, calls=2,
                tokens_in=tin1 + tin2, tokens_out=tout1 + tout2,
                seconds=time.time() - t0, reasoning=nav["reasoning"])

# ============================== SCORING ====================================
DECLINE = ["don't have", "do not have", "not in the knowledge", "no information",
           "isn't in", "is not in", "not covered", "no relevant", "nothing in",
           "doesn't contain", "does not contain", "unable to"]

def score(q, res):
    exp_src = q["expected_sources"]
    exp_txt = q["expected_answer_contains"]
    ans = res["answer"].lower()
    if not exp_src:                                   # not_in_docs guardrail
        hit = len(res["sources"]) == 0                # did it retrieve nothing?
        correct = any(p in ans for p in DECLINE)      # did it decline?
    else:
        hit = all(s in res["sources"] for s in exp_src)
        correct = all(t.lower() in ans for t in exp_txt)
    return hit, correct

def main():
    qs = json.load(open(QUESTIONS))["questions"]
    out = {"vector": [], "vectorless": []}
    for q in qs:
        for name, fn in (("vector", ask_vector), ("vectorless", ask_vectorless)):
            r = fn(q["question"])
            hit, correct = score(q, r)
            r.update(id=q["id"], regime=q["regime"], question=q["question"],
                     expected_sources=q["expected_sources"], hit=hit, correct=correct)
            out[name].append(r)
            print(f"  {q['id']} {name:<6} hit={'Y' if hit else 'n'} correct={'Y' if correct else 'n'} "
                  f"{r['seconds']:.1f}s {r['tokens_in']+r['tokens_out']:>6}tok")
    # Each execution is its own run file, so the dashboard gains a column every
    # time you re-run. That is the whole point — one run tells you nothing.
    n = 1
    while os.path.exists(f"results-run{n}.json"):
        n += 1
    json.dump(out, open(f"results-run{n}.json", "w"), indent=2)
    print(f"\nwrote results-run{n}.json  (run {n})")

if __name__ == "__main__":
    main()
