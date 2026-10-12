"""基础 RAG v0.1:检索 + Qwen 回答 + 引用页码。
使用:python src/rag/query.py "你的问题"
"""
import sys
import os
from pathlib import Path
# 让脚本可直接运行
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.utils import embedding_functions
from  openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
if not API_KEY:
    print("[ERROR] .env 里没有 DASHSCOPE_API_KEY")
    sys.exit(1)

DB_DIR = "data/vectorstore"
COLL = "siliconmind_v1"
TOPK = 3
MODEL = "qwen-plus"  # 也可换 qwen-turbo / qwen-ma教学的方式回答学生
client = OpenAI(
    api_key=API_KEY,
    base_url="https://maas.qianwenaiapi.com/compatible-mode/v1",
)
PROMPT = """你是硅智 SiliconMind 的资深模拟电子技术老师。

【强制要求】末尾必须包含【参考】段落，格式严格为:《书名》 第X章 p.XXX。

【回答结构】
1. **原理**:物理/电学原理 + 关键公式
2. **关键参数**:典型值、计算例子
3. **常见误区**:学生最容易错的地方
4. **【参考】**:《书名》 第X章 p.XXX
5. **延伸思考**:给 1 个进阶问题

【参考教材片段】
{context}

【学生问题】
{question}

【你的回答】(末尾【参考】不可省略):
"""
def get_collection():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5",
        device="cpu",
    )
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(
        name=COLL,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def retrieve(question: str, topk: int = TOPK):
    coll = get_collection()
    res = coll.query(query_texts=[question], n_results=topk)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return docs, metas


def answer(question: str) -> str:
    docs, metas = retrieve(question)
    if not docs:
        return "[NO_HIT] 知识库里没找到相关内容"

    context = "\n\n---\n\n".join(
        f"《{m['book']}》 {m['chapter']} p.{m['page']}\n{d}"
        for d, m in zip(docs, metas)
    )

    try:
        # 改用 OpenAI SDK 的调用方式
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": PROMPT.format(context=context, question=question)}
            ],
            max_tokens=1500,
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[EXCEPTION] {type(e).__name__}: {e}"
    
    
def interactive():
    """交互模式:连续提问。"""
    print("=" * 60)
    print("硅智 SiliconMind v0.1  |  输入 'q' 退出")
    print("=" * 60)
    while True:
        q = input("\n[Q] ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            break
        if not q:
            continue
        print("\n[A]", answer(q))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print("Q:", q)
        print("A:", answer(q))
    else:
        interactive()