from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

facts = [
    "To restart the payments service: kubectl rollout restart deploy/payments -n prod.",
    "To roll back a deploy: kubectl rollout undo deploy/<service> -n prod.",
    "Postgres backups use pg_dump.",
    "Page the Payments on-call when checkout is down.",
]
fact_vectors = model.encode(facts)

question = "how do I bounce the payments pods?"
scores = util.cos_sim(model.encode(question), fact_vectors)[0]

best = max(range(len(facts)), key=lambda i: scores[i])
print(facts[best])
