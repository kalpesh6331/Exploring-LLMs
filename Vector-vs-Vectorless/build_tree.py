"""
build_tree.py — Build the table of contents for our knowledge base.

This is the INDEX step, like Ep 6's index.py — except there is no embedding
model, no vector database, and no API call. Markdown already carries a
hand-written index: folder names, titles, and headings. We just read it out.

Run this once (and re-run whenever the docs change).
"""

import os
import glob
import json

# --- Config ---------------------------------------------------------------
KB_DIR = "knowledge-base"     # folder of .md docs to index
TREE_FILE = "tree.json"       # where we write the table of contents

# --- 1. Pull the structure out of one markdown file -----------------------
# Four fields, and we invent none of them. Every one was already typed by
# whoever wrote the doc:
#   path     -> where it sits in the folder tree
#   title    -> the "# " line
#   summary  -> the first real sentence of the doc
#   sections -> every "## " heading, in order
def parse_doc(path):
    with open(path) as f:
        lines = f.read().splitlines()

    title = ""
    summary = ""
    sections = []
    in_code = False

    for line in lines:
        line = line.strip()
        if line.startswith("```"):
            in_code = not in_code         # never read inside a code block
        elif in_code:
            continue
        elif line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.append(line[3:].strip())
        elif title and not summary and not sections and line and line[0] not in ">|-*":
            summary = line          # opening prose = the doc's own intro, if it has one

    return {
        "path": os.path.relpath(path, KB_DIR),
        "title": title or os.path.basename(path),
        "summary": summary[:200],
        "sections": sections,
    }

# --- 2. Walk the knowledge base and parse every doc -----------------------
paths = sorted(glob.glob(os.path.join(KB_DIR, "**", "*.md"), recursive=True))
tree = [parse_doc(p) for p in paths]

# --- 3. Write the tree out ------------------------------------------------
with open(TREE_FILE, "w") as f:
    json.dump(tree, f, indent=2)

print(f"Parsed {len(tree)} docs from {KB_DIR}/ into {TREE_FILE}")
print(f"Sections found: {sum(len(d['sections']) for d in tree)}")
print("Done. You can now ask questions with:  python ask_tree.py")
