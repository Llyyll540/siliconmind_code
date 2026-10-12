"""硅智向量索引 v0.3:用 bge-small-zh-v1.5。"""
import json, sys, os
from pathlib import Path
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import chromadb
from chromadb.utils import embedding_functions

CHUNKS = Path("data/processed/chunks.jsonl")
DB_DIR = Path("data/vectorstore")
COLL = "siliconmind_v1"
BATCH = 256
EMBED_MODEL = "BAAI/bge-small-zh-v1.5"

def main():
    if not CHUNKS.exists():
        print(f"[ERROR] 找不到 {CHUNKS}"); sys.exit(1)
    print(f"[init] 加载 {EMBED_MODEL} ...")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL, device="cpu")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    coll = client.get_or_create_collection(
        COLL, embedding_function=ef,
        metadata={"hnsw:space": "cosine"})
    docs, metas, ids = [], [], []
    with CHUNKS.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            docs.append(r["text"])
            metas.append({"book": r.get("book","?"), "chapter": r.get("chapter","?"), "page": int(r.get("page",0))})
            ids.append(f"c{i}")
    print(f"[indexing] {len(docs)} chunks ...")
    for i in range(0, len(docs), BATCH):
        j = min(i+BATCH, len(docs))
        coll.add(documents=docs[i:j], metadatas=metas[i:j], ids=ids[i:j])
        print(f"  [{j}/{len(docs)}]")
    print(f"[done] saved -> {DB_DIR}/{COLL}")

if __name__ == "__main__":
    main()


















































