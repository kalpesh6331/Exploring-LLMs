# Vector vs Vectorless — the benchmark

The companion code for **Episode 8 — "Vector vs Vectorless"** of the **DevOps & Data Simplified — AI** series (playlist: **Exploring LLMs**).

This is **Part 4 of a 4-part RAG arc**, and its closure. Episode 6 built RAG with a vector database. Episode 7 built it again with no database at all. This episode runs both over **the same 60 documents** and **the same 12 questions with known-correct answers**, and scores them.

It is really an episode about **evals** — how you measure a system whose output changes every time you run it. Retrieval is just the worked example.

- **`build_tree.py`** — builds `tree.json`, the table of contents the vectorless engine navigates. No model, no network call.
- **`index_vector.py`** — re-indexes the same 60 docs into Qdrant with a local embedding model, so both engines search an identical corpus. 252 chunks.
- **`benchmark.py`** — runs all 12 questions through both engines, scores each answer against the ground truth, and records tokens and wall-clock.
- **`report.py`** — turns the `results-run*.json` files into terminal tables.
- **`export_metrics.py`** — loads those same results into Postgres, where the Grafana dashboard reads them.

---

## What's inside
| Path | What it is |
|------|------------|
| `build_tree.py` | Build the vectorless engine's table of contents |
| `index_vector.py` | Re-index the corpus into Qdrant (252 chunks, `all-MiniLM-L6-v2`) |
| `benchmark.py` | Both engines + the scoring function |
| `report.py` | Results tables: headline, per-regime, failures |
| `questions.json` | **The ground truth** — 12 questions, each with its known-correct source document |
| `knowledge-base/` | The same fake **"ShopFast"** corpus from Episode 7 — 60 docs, 8 folders |
| `export_metrics.py` | Flattens the run files into Postgres rows |
| `reset.py` | Archives the run files and empties the table — start clean |
| `docker-compose.yml` | Postgres + Grafana, no volumes, nothing to click |
| `grafana/` | The data source and the dashboard, provisioned as code |
| `FINDINGS.md` | What my three runs said, including the bits that surprised me |

The `results-run*.json` files are **not** in the repo — they're my numbers, not yours. Run the benchmark and you'll generate your own; `FINDINGS.md` and the table at the bottom of this README are there so you can compare.

---

## Prerequisites
- **Python 3.9+**
- **Docker** (for Qdrant)
- An **Anthropic API key** as `CLAUDE_KEY` — from [console.anthropic.com](https://console.anthropic.com)
- **Docker Compose**, only if you want the Grafana dashboard (step 3b)

---

## The scripts

Three of them are the pipeline. Two are **alternative ways to look at the same
results** — pick one, you don't need both. The last one is housekeeping.

| Script | Produces | Needs |
|---|---|---|
| `build_tree.py` | `tree.json` — the **vectorless** index | nothing |
| `index_vector.py` | a Qdrant collection — the **vector** index | Qdrant |
| `benchmark.py` | `results-run1.json`, `results-run2.json`, … | both indexes, `CLAUDE_KEY` |
| `report.py` | tables in your terminal | nothing |
| `export_metrics.py` | loads the results into Postgres for Grafana | Postgres |
| `reset.py` | archives the run files and empties the table | Postgres |

---

## Setup

```bash
# Qdrant — the vector engine's database
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant

cd Vector-vs-Vectorless
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export CLAUDE_KEY=sk-ant-...    # Windows: set CLAUDE_KEY=sk-ant-...
```

---

## Run, in order

### 1. Build both indexes

Both must exist before the benchmark runs — it queries each engine in turn.
The order *between* these two doesn't matter; they're independent.

```bash
python build_tree.py        # vectorless index — 60 docs, ~0.2s, zero API calls
python index_vector.py      # vector index — 252 chunks into Qdrant
```

### 2. Run the benchmark

The only step that costs money — roughly **$0.27** for all 12 questions across
both engines.

```bash
python benchmark.py         # -> results-run1.json
```

**Run it more than once.** Each execution writes its own `results-run<N>.json`
rather than overwriting, and both viewers below aggregate across every run they
find. This is not a throwaway instruction — a single run nearly had me publishing
the wrong conclusion. See `FINDINGS.md`.

```bash
python benchmark.py         # -> results-run2.json
python benchmark.py         # -> results-run3.json
```

To start clean, run `python reset.py` first — it moves the existing run files
into `runs-archive/<timestamp>/` and empties the Postgres table, so the next
benchmark is run 1 again. `python reset.py --restore` puts the newest archive
back.

### 3. Look at the results — pick one

**3a. In the terminal**

```bash
python report.py            # headline, per-regime, and every failure
```

**3b. Or on a dashboard** — this is what the episode uses

```bash
docker compose up -d        # Postgres + Grafana, both provisioned as code
python export_metrics.py    # results-run*.json -> rows in Postgres
open http://localhost:3000  # the dashboard is already there, no login
```

Nothing to click: the data source and the dashboard are provisioned from
`grafana/`, so `docker compose up -d` gives you the finished thing.

#### What's on it

Seven panels, in four rows:

| Row | Panel | What it answers |
|---|---|---|
| **Headline** | Retrieval hit-rate (%) | How often every expected document came back |
| | Answer correctness (%) | How often the answer contained everything it had to |
| | Avg latency per question | How long a question takes, end to end |
| | Cost per 12-question run | What one full pass costs, at Sonnet pricing |
| **Gauges** | Vector — correct per run | One dial per run, out of 12 |
| | Vectorless — correct per run | The same, for the other engine |
| **Where they differ** | Answer correctness by question type | Accuracy split across the six regimes |
| | Tokens burned per run | Why the cost gap exists |
| **Detail** | Latency per question | Which questions are slow, and for which engine |
| | Every failure, and what came back instead | Every miss, with the run, the regime and the sources retrieved |

The one to look at first is the **gauge row**. Vector reads the same number every
run: its retrieval is embed + cosine + top-k, so the same question gives the same
chunks forever. Vectorless does not — its retrieval step *is* a model call, and
the retriever itself can change its mind. The failures table at the bottom names
the question that flips.

That one dial is why you run an eval more than once.

### Keeping the dashboard at three runs per engine

`benchmark.py` never overwrites — each execution writes the next free
`results-run<n>.json`, and a bare `export_metrics.py` loads all of them. After a
few rehearsals you'll have six dials per engine instead of three. Two ways back:

```bash
python export_metrics.py --last 3   # load only the three newest run files
python reset.py                     # archive every run file + empty the table
python reset.py --restore           # put the newest archive back, then re-export
```

`--last 3` keeps the real run numbers, so the dials may read "run 2, 3, 4".
`reset.py` is the one to use if you want the numbering to start from 1 again.

**Grafana itself never needs resetting.** The dashboard is provisioned from
`grafana/dashboards/benchmark.json` and queries Postgres live — refreshing the
browser is the whole recovery. There's no Postgres volume either, so
`docker compose down && docker compose up -d` is a guaranteed clean slate.

> Re-run `export_metrics.py` after any new benchmark run to refresh the dashboard.

---

## What the scoring actually does

Two things are scored **separately**, on purpose:

- **Retrieval hit** — did *every* expected source document come back? For a multi-hop question that means both of them. All-or-nothing.
- **Answer correct** — does the final answer contain every required string? Crude, but it cannot flatter itself; there is no model grading another model.

A system can retrieve perfectly and answer badly, or retrieve garbage and still bluff a correct answer. If you only score the final answer you cannot tell those apart — and they need completely different fixes.

The `not_in_docs` question inverts the test: retrieving **nothing** is the win, and we look for a refusal.

---

## My results (3 runs — see `FINDINGS.md`)

| | retrieval | answers | avg latency | tokens/12q | cost/12q |
|---|---|---|---|---|---|
| **vector** | **10/11** | 11/12 | **3.2s** | **10,913** | **$0.058** |
| **vectorless** | 9/11 | 11/12 | 5.2s | 57,715 | $0.212 |

**Neither wins.** They tie on answers. Vector is more accurate on retrieval in the typical run, and it is 1.6× faster, uses 5.3× fewer tokens and costs 3.6× less. What vectorless buys you is traceability and the ability to return nothing at all — not accuracy.

**Vector produced byte-identical results all three runs. Vectorless did not.** Its retrieval step *is* a model call, so the retriever itself is non-deterministic. That is an architectural cost worth knowing about.

⚠️ **My first run showed vectorless at 12/12 and I nearly reported it as a win.** It was its best run of three. With 12 questions one flip moves the headline by 8%. Run your eval more than once, or you are reporting luck.

---

## Notes

- **The knowledge base is entirely synthetic.** "ShopFast" is not a real company. Don't point a demo at your real customer documentation.
- `tree.json` and the `results-run*.json` files are **generated** — run the scripts to create them.
- The corpus and `questions.json` are identical to Episode 7's on purpose. Both engines must search the same documents and be graded on the same questions, or the comparison means nothing.
- Uses the Anthropic API directly with `requests` — no SDK, so every part of the call is visible.
