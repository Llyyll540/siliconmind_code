"""知识图谱可视化：输出 HTML(pyvis 交互式）。"""
import json
from pathlib import Path

KG_JSON = Path("kg/electronics_kg.json")
OUT_HTML = Path("assets/kg.html")
OUT_HTML.parent.mkdir(exist_ok=True)

def main():
    if not KG_JSON.exists():
        print(f"[ERROR] {KG_JSON} 不存在，先跑 kg_build.py")
        return

    data = json.loads(KG_JSON.read_text(encoding="utf-8"))
    nodes = data["nodes"]
    edges = data["edges"]
    print(f"[load] {len(nodes)} nodes, {len(edges)} edges")

    # 用 pyvis 生成交互图
    try:
        from pyvis.network import Network
        net = Network(height="750px", width="100%", directed=True, notebook=False)
        # 不同节点类型用不同颜色
        for n in nodes:
            label = n["label"]
            color = "#97c2fc"  # 默认蓝
            if any(k in label for k in ["NE555", "LM358", "LM358", "MOSFET", "三极管", "二极管", "运放"]):
                color = "#ff7f50"  # 元件-橙
            elif any(k in label for k in ["PWM", "放大", "反馈", "调制", "整流", "滤波", "稳压"]):
                color = "#90ee90"  # 原理-绿
            elif any(k in label for k in ["应用", "电路", "调光", "信号", "电源", "驱动"]):
                color = "#dda0dd"  # 应用-紫
            net.add_node(label, label=label, color=color, title=label)

        for e in edges:
            net.add_edge(e["source"], e["target"], title=e["relation"], label=e["relation"])

        net.write_html(str(OUT_HTML), notebook=False)
        print(f"[done] {OUT_HTML}")
        print(f"  在浏览器打开 {OUT_HTML} 看交互图")
    except ImportError:
        print("[WARN] pyvis 没装，跑 pip install pyvis")
        # fallback: matplotlib
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n["label"])
        for e in edges:
            G.add_edge(e["source"], e["target"])
        plt.figure(figsize=(20, 15))
        nx.draw(G, with_labels=True, node_size=300, font_size=8, arrows=True)
        plt.savefig(str(OUT_HTML).replace(".html", ".png"), dpi=100)
        print(f"[done] PNG: {OUT_HTML}".replace(".html", ".png"))

if __name__ == "__main__":
    main()