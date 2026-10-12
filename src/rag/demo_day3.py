"""Day 3 综合演示：多模态 + RAG + 仿真 一体化"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from multimodal import analyze as vl_analyze
from query import answer as rag_answer
from simulate import simulate as circuit_sim

def demo_with_image(image_path: str, question: str = ""):
    """演示流程：上传电路图 → 识别 → 提问 → 仿真。"""
    print("=" * 70)
    print(f"[STEP1] 多模态识别电路图: {image_path}")
    print("=" * 70)
    desc = vl_analyze(image_path, question)
    print(desc)

    print("\n" + "=" * 70)
    print("[STEP 2] 自动仿真关键参数")
    print("=" * 70)
    sim_input = question or "请基于这个电路推导核心公式，并给出典型参数计算"
    sim_out = circuit_sim(sim_input)
    print(sim_out)

    print("\n" + "=" * 70)
    print("[STEP 3] 原理深入问答")
    print("=" * 70)
    follow_up = question or "这个电路的工作原理是什么？"
    ans = rag_answer(follow_up)
    print(ans)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_day3.py <image_path> [question]")
        print('Example: python demo_day3.py circuit.png "LM358 同相放大的增益是多少"')
        sys.exit(1)
    img = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else ""
    demo_with_image(img, q)