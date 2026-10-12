# -*- coding: utf-8 -*-
"""问答评测（L2 W3）：引用准确率 + 拒答正确率，30 条正式评测集。

评测集 = scripts/build_qa_evalset.py 生成 tests/qa_eval_set.json（20 有答案 + 10 无答案）。
改样本改 build_qa_evalset.py 重跑，脚本只负责跑评测不内嵌样本（可复现纪律）。

用法：python -m scripts.qa_eval [--out logs/qa_eval_w3.json]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query import answer as qa  # noqa: E402


def _is_refusal(a: qa.QAAnswer) -> bool:
    return qa._is_refusal(a)


def _answer_with_retry(q: str, attempts: int = 3) -> qa.QAAnswer:
    """评测调用：引用为空**或调用抛异常（瞬态网络/全端点失败）**时重试。

    教训（Day 20）：全端点瞬态失败会抛 QAError 中断评测，前两条已跑的数字白费。
    引用为空 + 调用异常都重试；持续失败（如 siyu 订阅失效那种确定性错误）才放弃。
    """
    last = None
    for _ in range(attempts):
        try:
            a = qa.answer(q)
            if a.citations or a.unanswerable:
                return a
            last = a
        except qa.QAError as e:
            last = None
            print(f"    (重试: {str(e)[:80]})")
            time.sleep(3)
    return last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="logs/qa_eval_w3.json", help="结果 json 路径")
    args = ap.parse_args()

    data = json.loads(Path("tests/qa_eval_set.json").read_text(encoding="utf-8"))
    answerable = data["answerable"]
    unanswerable = data["unanswerable"]

    t0 = time.time()
    rows, correct = [], 0
    for item in answerable:
        a = _answer_with_retry(item["q"])
        gold = item["gold"]
        cited_docs = {c.get("doc_id", "") for c in a.citations}
        ok = bool(cited_docs) and any(any(d.startswith(g) for g in gold) for d in cited_docs)
        correct += ok
        rows.append({"q": item["q"], "type": item.get("type", ""), "gold": gold,
                     "cited": sorted(cited_docs), "ok": ok, "unanswerable": a.unanswerable})
        print(f"[{'✓' if ok else '✗'}] ({item.get('type','')}) {item['q']} → 引用 {sorted(cited_docs)[:3]}")
    acc = correct / len(answerable)

    rows_r, ref_correct = [], 0
    for q in unanswerable:
        a = _answer_with_retry(q)
        ok = _is_refusal(a)
        ref_correct += ok
        rows_r.append({"q": q, "refused": ok, "unanswerable": a.unanswerable,
                       "answer_head": (a.answer or "")[:40]})
        print(f"[{'✓' if ok else '✗'}] {q} → 拒答={ok}")
    ref_acc = ref_correct / len(unanswerable)

    dt = time.time() - t0
    print(f"\n=== L2 W3 问答评测（{len(answerable)}+{len(unanswerable)} 条）===")
    print(f"引用准确率 = {acc:.0%}（{correct}/{len(answerable)}）")
    print(f"拒答正确率 = {ref_acc:.0%}（{ref_correct}/{len(unanswerable)}）")
    print(f"耗时 {dt:.1f}s")
    json.dump({"citation_accuracy": round(acc, 4), "refusal_accuracy": round(ref_acc, 4),
               "rows": rows, "refusal_rows": rows_r, "elapsed_s": round(dt, 1),
               "gold_status": data.get("gold_status", "")},
              open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已写 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())