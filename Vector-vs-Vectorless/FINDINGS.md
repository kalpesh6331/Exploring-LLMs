# Ep 8 — benchmark results (3 independent runs, real API, 2026-09-21)

60 documents · 12 ground-truth questions · Sonnet 5 · Qdrant + all-MiniLM-L6-v2 (252 chunks, top-k=4)

> ⚠️ **Run it 3× before trusting any number.** The first run showed vectorless at 12/12 answers. That was its *best* run of three, not its typical one.

## Stability — the finding that reframes everything

| | run 1 | run 2 | run 3 | verdict |
|---|---|---|---|---|
| **vector** retrieval | 10/11 | 10/11 | 10/11 | **perfectly stable** |
| **vector** answers | 11/12 | 11/12 | 11/12 | **perfectly stable** |
| **vectorless** retrieval | 10/11 | 9/11 | 9/11 | **flaky (q04)** |
| **vectorless** answers | 12/12 | 11/12 | 11/12 | **flaky (q04)** |

**Vector produced byte-identical results all three times.** Its retrieval is pure maths — embed, cosine, top-k — so the only model call sees identical context every run.

**Vectorless did not.** Its navigation step *is* a model call, so the retriever itself is stochastic. **That non-determinism is an architectural cost nobody mentions:** you traded a deterministic retriever for one that can pick a different door on a given day.

## Headline (modal result — 2 of 3 runs)

| | retrieval | answers | avg latency | tokens/12q | cost/12q |
|---|---|---|---|---|---|
| **vector** (Ep 6) | **10/11** | 11/12 | **3.2s** | **10,913** | **$0.0579** |
| **vectorless** (Ep 7) | 9/11 | 11/12 | 5.2s | 57,715 | $0.2118 |

Latency and cost were stable to within 0.2s and a fraction of a cent across all three runs.

**On the modal run they tie on answers, and vector edges retrieval** — while being 1.6× faster, using 5.3× fewer tokens, and costing 3.6× less.

## The four findings that matter

**1. My Ep 7 hypothesis was WRONG.** I expected exact identifiers (`ERR-5012`, `--skip-smoke`, port `8443`) to be vector's weak spot. **Vector went 3/3, all three runs.** Ep 7 hedged correctly on camera, so nothing frozen is contradicted — but the prediction failed and Ep 8 should say so first.

**2. q04 vectorless — "the signpost problem". THE finding of the episode.**
`incidents/incident-response.md` contains a section titled **"Who to page"** whose entire body is *"See `incidents/on-call-rotation.md`."*
Asked *"who do I page?"*, the navigator matched that **section title**, opened it, found a cross-reference rather than an answer — and **did not follow it**. It answered anyway, wrongly.
- Run 1 it chose `on-call-rotation.md` correctly. Runs 2 and 3 it took the signpost.
- Vector never had this problem: it embeds **content**, and a section whose only content is a pointer has nothing to match.
- **The symmetry:** vector matches on content and is blind to structure; vectorless matches on labels and is seduced by a good-looking label. Naming this is worth more than the scoreboard.
- **The fix worth stating:** a navigator should follow cross-references, or the tree should inline them. We don't, and it costs us.

**3. q04 vector — the top-k duplication failure.** Stable across all 3 runs. Four slots came back as **two documents, each twice** (`deployments.md` ×2, `deploy-freeze.md` ×2, scores 0.571→0.508). A two-document question cannot be answered when top-k is consumed by duplicates. It failed *honestly*: *"I can answer part of this question but not all of it."*
**Both engines fail q04, for completely opposite reasons.** That single question is the whole episode in miniature.

**4. q08 — the guardrail came from the PROMPT, not the retriever.** Stable across all 3 runs. Vector retrieved four irrelevant chunks (0.29–0.32) and **still declined correctly**. Tree declined because it retrieved nothing. Both pass, via different mechanisms. Your safety came from *"if the answer isn't in them, say so"* — not from retrieval quality.

## Recording risk

**q04 vectorless is the only unstable cell.** On camera it may go either way. Options: run it live and treat whichever happens as the teaching moment (the signpost problem is interesting *either* way), or pre-record. Everything else reproduced exactly, three times.

## The honest conclusion

**Neither wins.** They tie on answers; vector is more accurate on retrieval in the modal run, deterministic, 1.6× faster and 3.6× cheaper. The vectorless advantage is traceability and the ability to return nothing — not accuracy. At 60 documents, the numbers do not justify vectorless on cost alone.
