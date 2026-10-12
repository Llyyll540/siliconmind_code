"""硅智多模态 v0.2:用 Qwen-VL 通过 OpenAI 兼容模式识别电路图。"""
import sys
import base64
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
if not API_KEY:
    print("[ERROR] No DASHSCOPE_API_KEY in .env")
    sys.exit(1)

BASE_URL = "https://maas.qianwenaiapi.com/compatible-mode/v1"
MODEL = "qwen-vl-plus"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

PROMPT = """你是硅智 SiliconMind 的资深电子工程师。分析这张电路图，给出:

【输出结构】
1. **电路类型**(如:同相放大、单稳态多谐振荡器、整流电路等）
2. **核心元件清单**(列出每个元件的标号/型号/参数）
3. **信号流**(输入→处理→输出，逐级描述）
4. **工作原理**(3-5 句话讲清楚）
5. **关键公式**(如增益、频率、时间常数等）

【格式】用 Markdown,结构清晰,便于教学使用。
"""

def encode_image(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    suffix = path.suffix.lower().replace(".", "")
    return f"data:image/{suffix};base64,{data}"

def analyze(image_path: str, extra_question: str = "") -> str:
    p = Path(image_path)
    if not p.exists():
        return f"[ERROR] 找不到图片: {image_path}"

    img_url = encode_image(p)
    prompt = PROMPT + (f"\n\n【学生追问】{extra_question}" if extra_question else "")

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": img_url}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[EXCEPTION] {type(e).__name__}: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python multimodal.py <image_path> [question]")
        sys.exit(1)
    img = sys.argv[1]
    extra = sys.argv[2] if len(sys.argv) > 2 else ""
    print(f"[IMG] {img}\n")
    print(analyze(img, extra))