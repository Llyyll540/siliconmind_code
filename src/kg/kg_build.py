"""知识图谱构建:用 LLM 从教材中提取 元件-关系-应用 三元组。
输入:data/processed/chunks.jsonl
输出:kg/electronics_kg.json + NetworkX 图
"""
import json
import re,os
from pathlib import Path

import networkx as nx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
CHUNKS = Path("data/processed/chunks.jsonl")
KG_JSON = Path("kg/electronics_kg.json")
KG_JSON.parent.mkdir(exist_ok=True)

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY", ""),
    base_url="https://maas.qianwenaiapi.com/compatible-mode/v1",
)

PROMPT = """你是电子信息工程知识图谱专家。从给定教材片段中，提取"实体-关系-实体"三元组。

【要求】
1. 实体类型只能是三种:元件(如:NE555, LM358, 三极管)、原理(如:PWM调制, 负反馈, 比较器)、应用(如:LED调光, 信号放大, 振荡电路)
2. 关系类型限 8 种:USES(用)、IMPLEMENTS(实现)、IS_A(属于)、APPLIES_TO(应用于)、DEPENDS_ON(依赖)、AMPLIFIES(放大)、GENERATES(生成)、REGULATES(调节)
3. 每行 1 个三元组，格式:实体1 | 关系 | 实体2
5. 不输出注释。

【教材片段】
{text}

【三元组】
"""

def extract_triples(text: str) -> list[tuple[str, str, str]]:
    """调 LLM 提取三元组。"""
    try:
        resp = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": PROMPT.format(text=text[:1500])}],
            temperature=0.1,
        )
        out = resp.choices[0].message.content
    except Exception as e:
        return []

    triples = []
    for line in out.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            triples.append((parts[0], parts[1], parts[2]))
    return triples

def build_kg(max_chunks: int = 50):
    """从教材片段构建知识图谱。"""
    G = nx.DiGraph()
    chunks = []
    with CHUNKS.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_chunks:
                break
            chunks.append(json.loads(line))

    print(f"[kg] processing {len(chunks)} chunks ...")
    seen_texts = set()
    triple_count = 0
    for i, ck in enumerate(chunks):
        # 用前 100 字去重
        sig = ck["text"][:100]
        if sig in seen_texts:
            continue
        seen_texts.add(sig)

        triples = extract_triples(ck["text"])
        for h, r, t in triples:
            if len(h) > 30 or len(t) > 30:
                continue
            G.add_edge(h, t, relation=r)
            triple_count += 1 
            if (i+1) % 10 == 0:
              print(f"  [{i+1}/{len(chunks)}] triples={triple_count}, nodes={G.number_of_nodes()}")

    # 保存
    data = {
        "nodes": [{"id": N, "label": N} for N in G.nodes()],
        "edges": [{"source": u, "target": v, "relation": d["relation"]} for u, v, d in G.edges(data=True)],
    }
    KG_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges -> {KG_JSON}")
    return G

if __name__ == "__main__":
    G = build_kg(max_chunks=50)  # 默认 50 块，~5-10 分钟