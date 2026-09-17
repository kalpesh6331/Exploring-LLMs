"""
index.py — Build the searchable index for our knowledge base.

This is STEP 1 (INDEX) from the architecture diagram:
  knowledge base (.md)  ->  split into chunks  ->  embed (LOCAL)  ->  Qdrant

Run this once (and re-run whenever the docs change).
"""

import os
import glob

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# --- Config ---------------------------------------------------------------
KB_DIR = "knowledge-base"          # folder of .md docs to index
COLLECTION = "knowledge_base"      # name of the Qdrant collection
MODEL_NAME = "all-MiniLM-L6-v2"    # local embedding model (384 dims)
QDRANT_URL = "http://localhost:6333"

# --- 1. Load the embedding model (runs locally, nothing leaves the box) ---
print(f"Loading embedding model: {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)
VECTOR_SIZE = model.get_embedding_dimension()  # 384 for MiniLM

# --- 2. Read the docs and split them into chunks --------------------------
# We split each doc on its markdown headings (##). Each chunk keeps a
# reference to the file it came from so we can cite it later.
def chunk_markdown(text, source):
    chunks = []
    current_heading = ""
    buffer = []

    def flush():
        body = "\n".join(buffer).strip()
        if body:
            chunks.append({
                "source": source,
                "heading": current_heading,
                "text": (current_heading + "\n" + body).strip(),
            })

    for line in text.splitlines():
        if line.startswith("## "):        # start of a new section
            flush()
            current_heading = line.lstrip("# ").strip()
            buffer = []
        else:
            buffer.append(line)
    flush()
    return chunks


all_chunks = []
for path in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
    with open(path) as f:
        text = f.read()
    source = os.path.basename(path)
    all_chunks.extend(chunk_markdown(text, source))

print(f"Read {len(all_chunks)} chunks from {KB_DIR}/")

# --- 3. Embed every chunk (turn text into vectors) ------------------------
texts = [c["text"] for c in all_chunks]
vectors = model.encode(texts, show_progress_bar=True)

# --- 4. Create the collection and upsert the vectors into Qdrant ----------
client = QdrantClient(url=QDRANT_URL)

# Start clean: drop the collection if it already exists, then create it.
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)

points = [
    PointStruct(
        id=i,
        vector=vectors[i].tolist(),
        payload=all_chunks[i],   # store text + source so we can read it back
    )
    for i in range(len(all_chunks))
]
client.upsert(collection_name=COLLECTION, points=points)

print(f"Indexed {len(points)} chunks into Qdrant collection '{COLLECTION}'.")
print("Done. You can now ask questions with:  python ask.py")
