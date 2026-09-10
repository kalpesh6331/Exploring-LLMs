from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
v = model.encode("restart the payments service")
print(len(v))     # 384
print(v[:8])      # the first 8 of 384 numbers
