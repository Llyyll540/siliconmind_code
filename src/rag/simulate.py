"""自动仿真 v0.2:用 OpenAI 兼容模式调 Qwen(支持 sk-ws- key)。"""
import os, sys, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
BASE_URL = "https://maas.qianwenaiapi.com/compatible-mode/v1"
MODEL = "qwen-plus"

# 验证
client = OpenAI(api_key=API_KEY,base_url=BASE_URL)

PROMPT = """你是电路仿真专家。给定用户关于元件/电路的问题，生成可执行的 Python SymPy 代码。

要求：
1. 第一行 import sympy as sp 和 import numpy as np
2. 定义所有变量为 sympy.Symbol
3. 用 sympy 推导公式
4. 用 sp.lambdify 转为可调用函数
5. 涉及波形时 print 关键结果

用户问题：{question}

你的 Python 代码（只写代码，不要其他说明）：
"""

def gen_code(question: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(question=question)}],
        temperature=0.2,
    )
    code = resp.choices[0].message.content
    return code.replace("```python", "").replace("```", "").strip()

def run_code(code: str) -> str:
    out = io.StringIO()
    old = sys.stdout
    sys.stdout = out
    try:
        exec(code, {"__name__": "__main__"})
    except Exception as e:
        sys.stdout = old
        return f"[EXEC ERROR] {type(e).__name__}: {e}"
    sys.stdout = old
    return out.getvalue() or "[empty]"

def simulate(question: str) -> str:
    code = gen_code(question)
    return f"[CODE]\n{code}\n[OUTPUT]\n{run_code(code)}"

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "NE555 单稳态脉宽 T = 1.1*R*C, R=10kΩ, C=10nF, 推导并计算 T"
    print(f"[Q] {q}\n")
    print(simulate(q))









































