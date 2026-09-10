# What is RAG? — demo code

The tiny, standalone demos from **Episode 5 — "What is RAG?"** of the **DevOps & Data Simplified — AI** series (playlist: **Exploring LLMs**).

This is **Part 1 of a 3-part RAG arc**, and it's the *concept* episode. These scripts exist to make the ideas behind RAG — **embeddings**, **similarity**, and **retrieval** — tangible, one at a time. There is **no vector database and no Claude answer here on purpose** — that's the real build in Episode 6. Think of these as "RAG, shown in pieces."

> **The one idea:** RAG doesn't train the model. It *looks up* the paragraphs that matter and hands them to the model at question time. These demos show *how* that lookup works.

---

## What's inside

| File | Demo | What it shows | You should see |
|------|------|---------------|----------------|
| `demo1_no_rag.sh` | 1 | A plain LLM answering a company-specific question with **no** RAG | A confident, **wrong** answer — it has never seen your docs |
| `demo2_embedding.py` | 2 | Turning text into an **embedding** (a list of numbers) | `384` and the first 8 numbers |
| `demo3_similarity.py` | 3 | **Similarity = meaning**: one anchor scored against four sentences | `0.526 / 0.488 / 0.140 / -0.019` |
| `demo4_toy_rag.py` | 4 | **Retrieval** in ~10 lines, no database | the `kubectl rollout restart deploy/payments` fact |

All the text here (a made-up "ShopFast" platform) is **fake, dummy data** — never build a RAG demo on real customer docs.

---

## Prerequisites

- **Python 3.9+**
- For the Python demos: **`sentence-transformers`** (installed below). On first run it downloads a small local embedding model, **`all-MiniLM-L6-v2`** (~90 MB). After that it runs **entirely on your machine** — nothing leaves.
- For `demo1_no_rag.sh` only: **`curl`** + **`jq`**, and an **Anthropic API key** (from [console.anthropic.com](https://console.anthropic.com) — separate from a Claude.ai subscription; set up billing first).

---

## Setup

```bash
cd What-Is-RAG        # this folder, whatever you named it

# (recommended) a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> First install pulls in PyTorch (a few hundred MB), one time. Add `.venv/` to your `.gitignore`.

---

## Run the demos

### Demo 2 — what's an embedding?
```bash
python demo2_embedding.py
```
```
384
[-0.019 -0.028 -0.022 -0.060 -0.075  0.029  0.013 -0.084]
```
A sentence became **384 numbers**. That's the embedding — coordinates for *meaning*.

### Demo 3 — similarity = meaning
```bash
python demo3_similarity.py
```
```
0.526   How do I bounce the payments pods?
0.488   restart the checkout deployment
0.140   How do I take a Postgres backup?
-0.019   What's the weather in Mumbai today?
```
"Bounce the payments pods" shares **zero keywords** with "restart the payments service" — and it still scores highest, because it *means* the same thing. Postgres and the weather fall off a cliff. That number (cosine similarity) is the engine RAG is built on.

### Demo 4 — toy RAG in ten lines
```bash
python demo4_toy_rag.py
```
```
To restart the payments service: kubectl rollout restart deploy/payments -n prod.
```
Four "facts," a question that matches **none of them by keyword**, and it still retrieves the right one — by meaning. That's **retrieval**, the *R* in RAG. No database, no Claude.

### Demo 1 — the problem (a plain LLM, no RAG)
```bash
export CLAUDE_KEY="sk-ant-..."   # never hard-code or show this on camera
chmod +x demo1_no_rag.sh
./demo1_no_rag.sh
```
The model will answer **confidently and wrongly** — it has no idea how *your* platform restarts payments. That gap is exactly what RAG closes.

*(The exact numbers in Demos 2–3 can drift by a hair across library/model versions — the **ordering** is the point.)*

---

## Troubleshooting

**`numpy.core.multiarray failed to import`** or *"A module compiled using NumPy 1.x cannot be run in NumPy 2.x"*

This is **not** a "numpy 2 is unsupported" problem — the demos run fine on numpy 2. It means your Python environment (usually **Anaconda's base**) has a **mismatched set** of packages: a newer numpy sitting next to an older `scipy` / `scikit-learn` that were compiled against numpy 1.x. `sentence-transformers` imports scikit-learn → scipy, and those old compiled modules can't load under numpy 2.

**Fix — use a clean virtual environment** (as in Setup above), which installs a consistent set:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Then run the demos with **that** environment's `python`. Avoid running these in your Anaconda base env.

*(If you must use an existing env, `pip install -U scipy scikit-learn` pulls numpy-2-compatible builds — but a venv is cleaner and won't disturb your other projects.)*

**"You are sending unauthenticated requests to the HF Hub…" (and a `Loading weights` bar)**

Harmless. On first load the embedding model is fetched from Hugging Face; without a token you're just on the anonymous (slower / lower-limit) tier, which is fine for one small model. To silence it once the model is cached:
```bash
export HF_HUB_OFFLINE=1                 # use the local cache, skip the Hub check
export HF_HUB_DISABLE_PROGRESS_BARS=1   # optional: drop the loading bar
```
Or authenticate for faster downloads: create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → `export HF_TOKEN=hf_...`.

---

## What's next

**Episode 6 — "Build RAG from scratch"** turns these pieces into the real thing: a self-hosted **Qdrant** vector database, your whole knowledge-base indexed, and **Claude** writing a grounded answer **with citations** — plus a guardrail for "I don't know."

▶️ Watch the series: **Exploring LLMs** — *(add your video/playlist link here)*
