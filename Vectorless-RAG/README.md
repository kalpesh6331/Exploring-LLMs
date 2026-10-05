# Vectorless RAG

The companion code for **Episode 7 — "Vectorless RAG"** of the **DevOps & Data Simplified — AI** series (playlist: **Exploring LLMs**).

This is **Part 3 of a 4-part RAG arc**. Episode 5 covered the concepts, Episode 6 built the real thing with a vector database and a local embedding model. Here we throw *all* of that away and retrieve a completely different way — by **navigating** the documents instead of measuring similarity.

**No embedding model. No vector database. No Docker.** One dependency: `requests`. And the index builds in about two tenths of a second.

The idea it rests on: your docs already carry a hand-written index — folder names, filenames, titles, headings. Episode 6 threw that away and rebuilt an index statistically. This time we just read the one that's already there.

- **`build_tree.py`** — walks `knowledge-base/` and lifts four fields out of every markdown file (path, title, the doc's own opening sentence, and every `##` heading) into `tree.json`. **No model, no network call.** Run once, re-run whenever the docs change.
- **`ask_tree.py`** — two calls to Claude: **NAVIGATE** (here's the table of contents, which docs and sections answer this?) then **ANSWER** (here's the text of exactly those sections). Prints the answer, the navigator's reasoning, and what it cost.

---

## What's inside
| Path | What it is |
|------|------------|
| `build_tree.py` | Build the table of contents (markdown → `tree.json`), no model involved |
| `ask_tree.py` | Answer a question (navigate → read the sections → grounded, cited answer) |
| `knowledge-base/` | A fake **"ShopFast"** platform's docs — 60 files across 8 folders, dummy data you swap for your own |
| `requirements.txt` | `requests` — that's the whole list |

`tree.json` is **generated**, not committed. Run `build_tree.py` to create it.

---

## Prerequisites
- **Python 3.9+**
- An **Anthropic API key** — from [console.anthropic.com](https://console.anthropic.com) (separate from a Claude.ai subscription; set up billing first). You'll set it as `CLAUDE_KEY`.

No Docker. No local model download. Nothing to install beyond one Python package.

---

## Setup

**1. Create a virtual environment and install the one library:**
```bash
cd Vectorless-RAG
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Set your API key** (never commit this):
```bash
export CLAUDE_KEY=sk-ant-...    # Windows: set CLAUDE_KEY=sk-ant-...
```

---

## Run

**1. Build the tree** — this is the whole indexing step:
```bash
python build_tree.py
```
```
Parsed 60 docs from knowledge-base/ into tree.json
Sections found: 192
Done. You can now ask questions with:  python ask_tree.py
```
That takes about **0.2 seconds** and makes **zero API calls**. Open `tree.json` and have a look — every field in it was typed by whoever wrote the docs.

**2. Ask it something:**
```bash
python ask_tree.py "How do I restart the payments service?"
python ask_tree.py "What does error code ERR-5012 mean?"
python ask_tree.py "What is the maximum Postgres connection limit in staging?"
```

Each run prints the navigator's reasoning, the documents and sections it chose, the grounded answer with citations, and a receipts line:

```
Navigator: Error codes live in the reference section.
  -> reference/error-codes.md

======================================================================
ERR-5012 means payment gateway timeout ... [reference/error-codes.md]
======================================================================
2 Claude calls | 1 docs read | 4.7s
```

**3. Try to break it** — ask about something that isn't in the docs:
```bash
python ask_tree.py "How do I configure the Kafka message queue?"
```
It should retrieve **zero** documents and say it doesn't know. A similarity search always hands back its top *k* results whether they're relevant or not; a navigator is allowed to return nothing.

---

## How it works

**Index (once, local, free):** walk every `.md` file → pull out `path`, `title`, the first real sentence, and every `##` heading → write `tree.json`. Nothing is generated or summarised; it's all lifted verbatim.

**Answer (per question, two model calls):**
1. **NAVIGATE** — the whole knowledge base as a table of contents (~2,700 tokens for 60 docs) plus your question. Claude picks the documents and, where it can, the exact sections.
2. **READ** — plain text handling, no model. A `##` heading owns everything until the next `##`, so sub-sections come along with it. If no sections were named, the whole file is used.
3. **ANSWER** — those sections plus your question, with the instruction to answer only from them and cite the file *and* section.

---

## The honest trade-offs

- **You didn't remove the cost, you moved it.** Episode 6 paid once, upfront, in infrastructure. This pays on every question, in inference — two model calls instead of one, and the table of contents rides along in every prompt.
- **It needs structure.** `infrastructure/dns.md` in this corpus is flat prose with no headings; its tree entry is a title and a sentence, and there's nothing to drill into. The tree is only as good as the writing underneath it.
- **It doesn't scale for free.** 60 docs ≈ 2,700 tokens of table of contents. 10,000 docs would be around half a million — at which point you'd navigate the top-level folders first, then drill into one branch.
- **The whole corpus is ~16,500 tokens.** At this size you could skip retrieval entirely and put everything in one prompt. At five documents you need none of this; at ten thousand you need all of it.

---

## Troubleshooting

**`KeyError: 'CLAUDE_KEY'`** — the key isn't exported in the shell you're running from. Re-run the `export` line.

**`FileNotFoundError: tree.json`** — run `python build_tree.py` first.

**The navigator picks a different document than you expected** — that's expected. The navigation step is a model call, so it isn't deterministic. Run it again and it may choose differently.

---

## Notes

- **The `knowledge-base/` is entirely fake.** "ShopFast" isn't a real company and none of this is real infrastructure. **Don't point a demo at your real customer documentation** — swap in your own docs deliberately, once you know what leaves the machine.
- **What leaves your machine:** nothing during indexing. Per question, the table of contents and the text of the selected sections go to Claude. That's it.
- Uses the Anthropic API directly with `requests` — no SDK, so every part of the call is visible.
