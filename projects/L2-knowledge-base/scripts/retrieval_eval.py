# -*- coding: utf-8 -*-
"""检索评测（L2 W3 升级版）：召回率 + MRR + 上下文相关性。

- 评测集 = scripts/build_qa_evalset.py 生成的 tests/qa_eval_set.json（20 条有答案 + 10 无答案）
- 指标：
  * **召回率（Recall@5）**：gold 来源文档是否出现在检索 top-5（≥90% 目标）
  * **MRR**：gold 文档在 top-5 的平均倒数排名
  * **上下文相关性**：top-5 里与 gold 来源文档相关的块数 ÷ 5（≥60% 目标）
    相关块 = doc_id 命中任一 gold 前缀
- 无答案题不参与检索评测（它们本来就该检不到）

用法：python -m scripts.retrieval_eval
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index import retriever  # noqa: E402
from query import rewrite  # noqa: E402


def main() -> int:
    data = json.loads(Path("tests/qa_eval_set.json").read_text(encoding="utf-8"))
    answerable = data["answerable"]

    rows = []
    t0 = time.time()
    for item in answerable:
        q = item["q"]
        gold = item["gold"]
        # Day 25：查询改写（读缓存，离线、可复现；缓存缺该题 = 降级原查询不调网）
        rws = rewrite.rewrite(q, cache_only=True)
        alt = rws[1:] if len(rws) > 1 else None
        lex_floor = int(__import__("os").environ.get("L2_LEX_FLOOR", "0"))
        hits = retriever.search_all(q, k=5, alt_queries=alt, lex_floor=lex_floor)
        docs = [h.doc_id for h in hits]

        # Recall@5：gold 文档是否在 top-5
        rec = any(any(d.startswith(g) for g in gold) for d in docs)
        # MRR：第一个 gold 文档的排名倒数
        mrr_pos = next((i for i, d in enumerate(docs) if any(d.startswith(g) for g in gold)), None)
        mrr = 1.0 / (mrr_pos + 1) if mrr_pos is not None else 0.0
        # 上下文相关性：top-5 里 gold 相关块占比
        ctx = sum(1 for d in docs if any(d.startswith(g) for g in gold)) / 5.0

        rows.append({"q": q, "type": item.get("type", ""), "gold": gold,
                     "top": docs[:5], "recall": rec, "mrr": mrr, "context": ctx})
        print(f"[{'✓' if rec else '✗'}] ({item.get('type','')}) {q}")
        for d in docs[:3]:
            print(f"      {d}")
    dt = time.time() - t0

    n = len(answerable)
    recall = sum(r["recall"] for r in rows) / n
    mrr = sum(r["mrr"] for r in rows) / n
    context = sum(r["context"] for r in rows) / n
    print(f"\n=== L2 W3 检索评测（{n} 条有答案）===")
    print(f"召回率 Recall@5 = {recall:.0%}（{int(recall*n)}/{n}）｜目标 ≥90%")
    print(f"MRR = {mrr:.3f}")
    print(f"上下文相关性 = {context:.0%}｜目标 ≥60%")
    print(f"耗时 {dt:.1f}s")
    json.dump({"recall@5": round(recall, 4), "mrr": round(mrr, 4),
               "context_relevance": round(context, 4),
               "rows": rows, "elapsed_s": round(dt, 1),
               "gold_status": data.get("gold_status", "")},
              open("logs/retrieval_eval_w4.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("已写 logs/retrieval_eval_w4.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())