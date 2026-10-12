"""20 道种子题自动评测。
输出:eval/day2_report.json
终端打印：命中率、平均时延、引用率。"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from query import answer

SEED = Path("data/seed/seed_questions.jsonl")
OUT = Path("eval/day2_report.json")
OUT.parent.mkdir(exist_ok=True)


def check_hit(question: dict, ans: str) -> bool:
    """命中判定：答案里出现 answer_hint 的关键词。"""
    hint = question.get("answer_hint", "").strip()
    if not hint:
        # 没 hint 的题默认算"通过"（开放题）
        return len(ans) > 30 and "[ERROR" not in ans and "[NO_HIT" not in ans
    # 拆 hint 关键词（空格分隔）
    keywords = [k for k in hint.replace("，", " ").replace("、", " ").split() if len(k) >= 2]
    return any(k in ans for k in keywords)


def has_citation(ans: str) -> bool:
    """粗略判断是否带页码引用。"""
    return ("p." in ans) or ("页" in ans) or ("《" in ans and "》" in ans)


def main():
    if not SEED.exists():
        print(f"[ERROR] 找不到 {SEED}")
        sys.exit(1)

    questions = [json.loads(l) for l in SEED.open(encoding="utf-8")]
    print(f"[eval] {len(questions)} questions")

    results = []
    t0_all = time.time()
    for i, q in enumerate(questions, 1):
        t0 = time.time()
        ans = answer(q["question"])
        latency = time.time() - t0
        hit = check_hit(q, ans)
        cite = has_citation(ans)
        results.append({
            "id": q.get("id", f"Q{i}"),
            "component": q.get("component", "?"),
            "question": q["question"],
            "answer": ans,
            "hit_hint": hit,
            "has_citation": cite,
            "latency_sec": round(latency, 2),
        })
        flag = ("✓" if hit else "✗")
        cite_flag = "📖" if cite else "  "
        print(f"  [{i:2d}] {flag}{cite_flag} {latency:5.1f}s  {q['component']:<8} {q['question'][:25]}...")

    total_time = time.time() - t0_all
    n = len(results)
    hit_n = sum(r["hit_hint"] for r in results)
    cite_n = sum(r["has_citation"] for r in results)
    avg_lat = sum(r["latency_sec"] for r in results) / n

    report = {
        "total": n,
        "hit": hit_n,
        "hit_rate": round(hit_n / n, 4),
        "cite_rate": round(cite_n / n, 4),
        "avg_latency_sec": round(avg_lat, 2),
        "total_time_sec": round(total_time, 1),
        "results": results,
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"[REPORT] 命中 {hit_n}/{n}  = {hit_n/n:.0%}")
    print(f"[REPORT] 引用率 {cite_n}/{n} = {cite_n/n:.0%}")
    print(f"[REPORT] 平均时延 {avg_lat:.1f} 秒/题")
    print(f"[REPORT] 总耗时 {total_time:.1f} 秒")
    print(f"[FILE]   {OUT}")


if __name__ == "__main__":
    main()