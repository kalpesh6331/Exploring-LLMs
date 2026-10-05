"""
export_metrics.py — load the benchmark results into Postgres for Grafana.

results-run*.json is nested by engine; Grafana wants rows. This flattens them:
one row per (run, engine, question) = 72 rows across three runs.

The runs are stamped an hour apart so Grafana's time-series panels can show
"the same question, across three runs" on an x-axis. They aren't real times —
they're just a way to order the runs.
"""

import glob, json, os, re, sys
from datetime import datetime, timedelta

import psycopg2

DSN = os.environ.get("BENCH_DSN", "postgresql://bench:bench@localhost:5433/bench")
BASE = datetime(2026, 9, 21, 9, 0, 0)          # run 1; each later run is +1h

DDL = """
DROP TABLE IF EXISTS results;
CREATE TABLE results (
    run         int,
    run_at      timestamp,
    engine      text,
    question_id text,
    regime      text,
    question    text,
    hit         boolean,
    correct     boolean,
    passed      boolean,        -- hit AND correct: the single pass/fail per question
    seconds     numeric,
    tokens_in   int,
    tokens_out  int,
    tokens      int,
    calls       int,
    cost_usd    numeric,
    sources     text
);
"""

IN_RATE, OUT_RATE = 3/1e6, 15/1e6              # Sonnet pricing, $/token

def by_run(files):
    """Sort by run NUMBER, not by filename — run10 must not land before run2."""
    return sorted(files, key=lambda f: int(re.search(r"run(\d+)", f).group(1)))

# By default load every run. Two ways to narrow it:
#     python export_metrics.py results-run1.json     these files only
#     python export_metrics.py --last 3              the three newest runs only
#
# --last is the one to reach for after a rehearsal: it keeps the dashboard at
# three dials per engine no matter how many run files have piled up. Use
# reset.py instead if you want the run numbering to start from 1 again.
args = sys.argv[1:]
if args[:1] == ["--last"]:
    FILES = by_run(glob.glob("results-run*.json"))[-int(args[1]):]
else:
    FILES = by_run(args) if args else by_run(glob.glob("results-run*.json"))

rows = []
for path in FILES:
    run = int(re.search(r"run(\d+)", path).group(1))
    data = json.load(open(path))
    for engine, records in data.items():
        for r in records:
            rows.append((
                run, BASE + timedelta(hours=run - 1), engine,
                r["id"], r["regime"], r["question"],
                r["hit"], r["correct"], r["hit"] and r["correct"],
                round(r["seconds"], 2),
                r["tokens_in"], r["tokens_out"], r["tokens_in"] + r["tokens_out"],
                r["calls"],
                round(r["tokens_in"] * IN_RATE + r["tokens_out"] * OUT_RATE, 6),
                ", ".join(r["sources"]),
            ))

conn = psycopg2.connect(DSN)
with conn, conn.cursor() as cur:
    cur.execute(DDL)
    cur.executemany(
        "INSERT INTO results VALUES (" + ",".join(["%s"] * 16) + ")", rows)
conn.close()

runs = sorted({r[0] for r in rows})
print(f"Loaded {len(rows)} rows — runs {runs}, "
      f"{len({r[2] for r in rows})} engines, {len({r[3] for r in rows})} questions")
