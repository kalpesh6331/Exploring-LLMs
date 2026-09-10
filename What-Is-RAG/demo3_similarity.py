from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
anchor = "How do I restart the payments service?"

for text in [
    "How do I bounce the payments pods?",   # same meaning, different words
    "restart the checkout deployment",      # related
    "How do I take a Postgres backup?",     # unrelated
    "What's the weather in Mumbai today?",  # totally unrelated
]:
    score = util.cos_sim(model.encode(anchor), model.encode(text)).item()
    print(f"{score:.3f}   {text}")
