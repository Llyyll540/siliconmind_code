"""模电教材 PDF 清洗 v1.0。
输入:data/raw/textbooks/*.pdf
输出:data/processed/textbooks.jsonl
每行 JSON:{book, chapter, page, text}
"""
import json
import re
from pathlib import Path

import fitz  # PyMuPDF

RAW_DIR = Path("data/raw/textbooks")
OUT = Path("data/processed/textbooks.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

# 页脚/页眉黑名单
FOOTER = re.compile(r"\s*[—–\-]\s*\d+\s*[—–\-]\s*")
NOISE = re.compile(r"^(目录|习题|参考文献|附录|Contents|References)\s*$")


def clean_text(text: str) -> str:
    """去页眉页脚、空行、章节标号。"""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if NOISE.match(s):
            continue
        s = FOOTER.sub("", s)
        lines.append(s)
    return "\n".join(lines)


def detect_chapter(text: str, prev: str) -> str:
    """简单章节识别：抓到 '第X章 YYY' 就更新当前章节。"""
    m = re.search(r"^第[一二三四五六七八九十百千]+章\s+([^\n]{1,30})", text, re.M)
    return m.group(0).strip() if m else prev


def main():
    pdfs = list(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"[ERROR] 没有 PDF 文件，请把教材放到 {RAW_DIR}")
        return

    total_pages = 0
    with OUT.open("w", encoding="utf-8") as f:
        for pdf in pdfs:
            print(f"[clean] {pdf.name}")
            doc = fitz.open(pdf)
            chapter = "前言"
            for page_idx, page in enumerate(doc, start=1):
                text = clean_text(page.get_text())
                if not text:
                    continue
                chapter = detect_chapter(text, chapter)
                record = {
                    "book": pdf.stem,
                    "chapter": chapter,
                    "page": page_idx,
                    "text": text,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_pages += 1
            doc.close()
    print(f"[done] {total_pages} pages -> {OUT}")


if __name__ == "__main__":
    main()