"""
index_vector.py — Re-index Ep 6's vector RAG over the NEW 60-document corpus.

Same pipeline as Ep 6: split on markdown headings, embed locally with
all-MiniLM-L6-v2, upsert into Qdrant. Two deliberate differences, both forced
by the bigger corpus — and both stated on camera:

  1. The glob is RECURSIVE. Ep 6's corpus was flat; this one has 8 sub-folders.
  2. `source` is the path RELATIVE to the knowledge base ("services/foo.md"),
     not just the filename, so it can be matched against the ground truth.

Nothing else changed. Same chunker, same model, same distance metric.
"""

import os
import glob

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# --- Config ---------------------------------------------------------------
KB_DIR = "knowledge-base"          # the same 60 docs Episode 7 used
COLLECTION = "knowledge_base_60"
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_URL = "http://localhost:6333"

print(f"Loading embedding model: {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)
# How many numbers one embedding has (384 for MiniLM). Asking the model for
# this is version-sensitive -- the method got renamed -- so just measure one.
VECTOR_SIZE = len(model.encode("dimension probe"))

# --- Chunk on markdown headings (identical to Ep 6) -----------------------
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
        if line.startswith("## "):
            flush()
            current_heading = line.lstrip("# ").strip()
            buffer = []
        else:
            buffer.append(line)
    flush()
    return chunks

all_chunks = []
for path in sorted(glob.glob(os.path.join(KB_DIR, "**", "*.md"), recursive=True)):
    with open(path) as f:
        text = f.read()
    source = os.path.relpath(path, KB_DIR)
    all_chunks.extend(chunk_markdown(text, source))

print(f"Read {len(all_chunks)} chunks from {len(set(c['source'] for c in all_chunks))} docs")

texts = [c["text"] for c in all_chunks]
vectors = model.encode(texts, show_progress_bar=True)

client = QdrantClient(url=QDRANT_URL)
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)
client.upsert(
    collection_name=COLLECTION,
    points=[PointStruct(id=i, vector=vectors[i].tolist(), payload=all_chunks[i])
            for i in range(len(all_chunks))],
)
print(f"Indexed {len(all_chunks)} chunks into '{COLLECTION}'.")
