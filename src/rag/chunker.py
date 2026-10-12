"""切片策略 v1:按章节优先 + 段落聚合 + 长度控制。
输入:data/processed/textbooks.jsonl
输出:data/processed/chunks.jsonl
"""
import json
from pathlib import Path

IN = Path("data/processed/textbooks.jsonl")
OUT = Path("data/processed/chunks.jsonl")
MIN_LEN, MAX_LEN, OVERLAP = 200, 800, 80


def chunk_record(rec: dict) -> list[dict]:
    """把一页切成若干块。"""
    paras = [p for p in rec["text"].split("\n") if p.strip()]
    chunks, buf = [], ""

    def flush():
        nonlocal buf
        if len(buf) >= MIN_LEN:
            chunks.append({**rec, "text": buf})
        buf = ""

    for p in paras:
        # 单段过长 -> 硬切
        if len(p) > MAX_LEN:
            flush()
            for i in range(0, len(p), MAX_LEN - OVERLAP):
                chunk_text = p[i:i + MAX_LEN]
                chunks.append({**rec, "text": chunk_text})
            continue
        # 累积
        new_buf = (buf + "\n" + p).strip() if buf else p
        if len(new_buf) > MAX_LEN:
            flush()
            buf = (buf[-OVERLAP:] + "\n" + p).strip() if buf and OVERLAP else p
        else:
            buf = new_buf
    flush()
    return chunks


def main():
    if not IN.exists():
        print(f"[ERROR] 找不到 {IN}, 先跑 clean_pdf.py")
        return

    total = 0
    with IN.open(encoding="utf-8") as fi, OUT.open("w", encoding="utf-8") as fo:
        for line in fi:
            rec = json.loads(line)
            for ck in chunk_record(rec):
                fo.write(json.dumps(ck, ensure_ascii=False) + "\n")
                total += 1
    print(f"[done] {total} chunks -> {OUT}")


if __name__ == "__main__":
    main()