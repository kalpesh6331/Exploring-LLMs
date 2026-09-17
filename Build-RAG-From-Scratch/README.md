# Build RAG From Scratch

The companion code for **Episode 6 — "Build RAG From Scratch"** of the **DevOps & Data Simplified — AI** series (playlist: **Exploring LLMs**).

This is **Part 2 of a 3-part RAG arc**. Episode 5 covered the concepts; here we build the real thing — a self-hosted **Qdrant** vector database, your own docs indexed with a **local** embedding model, and grounded, **cited** answers from Claude. Two small files:

- **`index.py`** — reads the `knowledge-base/` docs, splits them into chunks, embeds each chunk **locally** (`all-MiniLM-L6-v2`), and loads them into Qdrant. Run once.
- **`ask.py`** — embeds your question, searches Qdrant for the closest chunks, builds a grounded prompt, asks Claude, and prints the answer **with citations** plus which chunks it retrieved and their scores.

> Nothing about your docs leaves the machine except the final question and its matched chunks (the one call to Claude).

---

## What's inside
| Path | What it is |
|------|------------|
| `index.py` | Build the searchable index (docs → chunks → local embeddings → Qdrant) |
| `ask.py` | Answer a question (embed → search → grounded prompt → Claude → cited answer) |
| `knowledge-base/` | A fake **"ShopFast"** platform's docs — dummy data you swap for your own |
| `requirements.txt` | `sentence-transformers`, `qdrant-client`, `requests` |

---

## Prerequisites
- **Python 3.9+**
- **Docker** (to run Qdrant locally)
- An **Anthropic API key** for the final answer step — from [console.anthropic.com](https://console.anthropic.com) (separate from a Claude.ai subscription; set up billing first). You'll set it as `CLAUDE_KEY`.
- First run downloads a small local embedding model (`all-MiniLM-L6-v2`, ~90 MB); after that everything runs on your machine.

---

## Setup

**1. Start Qdrant (the vector database) in Docker:**
```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
Dashboard (optional, nice to watch): http://localhost:6333/dashboard

**2. Create a virtual environment and install the libraries:**
```bash
cd Build-RAG-From-Scratch
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Set your API key (off-screen, never commit it):**
```bash
export CLAUDE_KEY="sk-ant-..."
```

---

## Run

**Index the docs — once:**
```bash
python index.py
```
```
Read 23 chunks from knowledge-base/
Indexed 23 chunks into Qdrant collection 'knowledge_base'.
```
(Refresh the Qdrant dashboard and you'll see the `knowledge_base` collection fill up.)

**Ask questions:**
```bash
python ask.py "how do I restart the payments service?"
```
You get the answer with the source cited (e.g. `[payments-service.md]`), plus a `=== RETRIEVED FROM ===` list showing which chunks it pulled and their similarity scores.

Try a few:
- `python ask.py "how do I roll back a bad deploy?"`
- `python ask.py "who do I page if checkout is down?"`
- `python ask.py "how do I take a postgres backup?"`
- Ask about something **not** in the docs (e.g. Kafka) → it tells you it doesn't know, instead of making something up.

---

## How it works (two phases)

```
INDEX (once):        docs → chunk → embed (local) → Qdrant
ANSWER (per query):  question → embed (local) → search Qdrant → build a grounded prompt → Claude → cited answer
```
Everything except the final Claude call runs locally.

---

## Troubleshooting

**`numpy.core.multiarray failed to import`** / *"A module compiled using NumPy 1.x…"*
Your Python environment (often Anaconda's **base**) has a mismatched numpy / scipy / scikit-learn set. It's not a numpy-2 problem. Use a clean virtual environment (Setup step 2) — it installs a consistent set.

**"You are sending unauthenticated requests to the HF Hub…" / a `Loading weights` bar**
Harmless. Once the model is cached you can silence it:
```bash
export HF_HUB_OFFLINE=1
export HF_HUB_DISABLE_PROGRESS_BARS=1
```

**`ConnectionError` to `localhost:6333`**
Qdrant isn't running — `docker start qdrant` (or re-run the `docker run` above).

---

## Notes
- The `knowledge-base/` here is **fake ShopFast** data. Never index a real customer knowledge base for a public demo.
- Models used: embedder `all-MiniLM-L6-v2` (384-dim), chat `claude-sonnet-5` (in `ask.py`).
- **Next episode (Part 3):** we hand this pipeline to an AI agent as a tool it can call on its own.

▶️ Watch the series: **Exploring LLMs** — *(add your video/playlist link here)*
