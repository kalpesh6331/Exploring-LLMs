"""report.py — turn the benchmark results into the tables we put on screen.

Reads EVERY results-run*.json and aggregates across them, because a single run
tells you almost nothing — see the stability section of FINDINGS.md.
"""
import glob, json, collections

FILES = sorted(glob.glob("results-run*.json"))
if not FILES:
    raise SystemExit("No results-run*.json found — run `python benchmark.py` first.")

R = collections.defaultdict(list)
for f in FILES:
    for engine, rows in json.load(open(f)).items():
        R[engine].extend(rows)
print(f"aggregating {len(FILES)} run(s): {', '.join(FILES)}\n")
IN_COST, OUT_COST = 3/1e6, 15/1e6          # $/token, Sonnet

def agg(rows):
    scored = [r for r in rows if r["expected_sources"]]   # hit-rate excludes guardrail
    return dict(
        hit=sum(r["hit"] for r in scored), hit_n=len(scored),
        correct=sum(r["correct"] for r in rows), n=len(rows),
        secs=sum(r["seconds"] for r in rows) / len(rows),
        # tokens and cost are reported PER RUN, so the figures stay comparable
        # however many times you have run the benchmark
        tin=sum(r["tokens_in"] for r in rows) / len(FILES),
        tout=sum(r["tokens_out"] for r in rows) / len(FILES),
        calls=sum(r["calls"] for r in rows))

print("=" * 74)
print(f"{'':<12}{'retrieval':>12}{'answer':>10}{'avg time':>11}{'tokens/run':>12}{'cost/run':>11}")
print("=" * 74)
for name in ("vector", "vectorless"):
    a = agg(R[name])
    cost = a["tin"] * IN_COST + a["tout"] * OUT_COST
    print(f"{name:<12}{a['hit']}/{a['hit_n']:<10}{a['correct']}/{a['n']:<8}"
          f"{a['secs']:>9.1f}s{round(a['tin']+a['tout']):>12,}{'  $'+format(cost,'.4f'):>11}")
print("=" * 74)

print("\nPER REGIME (retrieval hit / answer correct)")
print("-" * 74)
regimes = {}
for name in ("vector", "vectorless"):
    for r in R[name]:
        regimes.setdefault(r["regime"], {}).setdefault(name, []).append(r)
for reg, d in regimes.items():
    row = f"  {reg:<22}"
    for name in ("vector", "vectorless"):
        rows = d[name]
        sc = [x for x in rows if x["expected_sources"]]
        h = f"{sum(x['hit'] for x in sc)}/{len(sc)}" if sc else "n/a"
        c = f"{sum(x['correct'] for x in rows)}/{len(rows)}"
        row += f"{name}: {h:>5} {c:>5}   "
    print(row)

print("\nFAILURES")
print("-" * 74)
for name in ("vector", "vectorless"):
    for r in R[name]:
        if not r["hit"] or not r["correct"]:
            print(f"  [{name}] {r['id']} ({r['regime']}) hit={r['hit']} correct={r['correct']}")
            print(f"     Q: {r['question']}")
            print(f"     expected: {r['expected_sources']}")
            print(f"     got:      {r['sources']}")
