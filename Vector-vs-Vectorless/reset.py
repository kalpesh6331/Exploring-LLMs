"""
reset.py — clear the benchmark results so the dashboard starts from nothing.

benchmark.py never overwrites: each execution writes the next free
results-run<n>.json. That is deliberate — one run tells you nothing. But it
also means a rehearsal leaves run 4, 5, 6 lying around, and the dashboard
then shows six dials instead of three.

This puts it back:

    python reset.py            archive the run files AND empty the table
    python reset.py --files    archive the run files only
    python reset.py --db       empty the table only
    python reset.py --restore  put the newest archive back

Nothing is deleted. The run files are moved into runs-archive/<timestamp>/,
so a rehearsal can always be undone with --restore.
"""

import glob, os, shutil, sys
from datetime import datetime

import psycopg2

DSN = os.environ.get("BENCH_DSN", "postgresql://bench:bench@localhost:5433/bench")
ARCHIVE = "runs-archive"

flags = set(sys.argv[1:])
unknown = flags - {"--files", "--db", "--restore"}
if unknown:
    sys.exit(f"unknown option: {' '.join(sorted(unknown))}\n{__doc__}")

do_files = "--files" in flags or not flags & {"--files", "--db", "--restore"}
do_db    = "--db"    in flags or not flags & {"--files", "--db", "--restore"}

# --- restore: newest archive folder wins ----------------------------------
if "--restore" in flags:
    snaps = sorted(glob.glob(f"{ARCHIVE}/*"))
    if not snaps:
        sys.exit("nothing to restore — runs-archive/ is empty")
    for f in sorted(glob.glob(f"{snaps[-1]}/results-run*.json")):
        shutil.copy(f, ".")
        print(f"restored {os.path.basename(f)}")
    print(f"\nfrom {snaps[-1]} — now run: python export_metrics.py")
    sys.exit()

# --- move the run files out of the way ------------------------------------
if do_files:
    runs = sorted(glob.glob("results-run*.json"))
    if runs:
        snap = os.path.join(ARCHIVE, datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(snap, exist_ok=True)
        for f in runs:
            shutil.move(f, os.path.join(snap, f))
        print(f"archived {len(runs)} run file(s) -> {snap}/")
    else:
        print("no results-run*.json to archive")

# --- empty the table, but keep it ------------------------------------------
# TRUNCATE rather than DROP: the panels then say "No data" instead of going
# red with a missing-relation error, which looks a lot better on camera.
if do_db:
    conn = psycopg2.connect(DSN)
    with conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.results')")
        if cur.fetchone()[0] is None:
            print("table 'results' does not exist yet — nothing to clear")
        else:
            cur.execute("TRUNCATE results")
            print("emptied Postgres table 'results'")
    conn.close()

print("\nGrafana needs no reset — the dashboard is provisioned from "
      "grafana/dashboards/benchmark.json and reads Postgres live. Refresh the "
      "browser.")
