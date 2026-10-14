# -*- coding: utf-8 -*-
"""W4 前后对比：rerank on/off 的检索指标（用同一份 20 条有答案评测集）。"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index import retriever  # noqa: E402


def eval_set(rerank: bool) -> dict:
    data = json.loads(Path("tests/qa_eval_set.json").read_text(encoding="utf-8"))
    answerable = data["answerable"]
    rows, t0 = [], time.time()
    for item in answerable:
        q, gold = item["q"], item["gold"]
        hits = retriever.search_all(q, k=5, rerank=rerank)
        docs = [h.doc_id for h in hits]
        rec = any(any(d.startswith(g) for g in gold) for d in docs)
        ctx = sum(1 for d in docs if any(d.startswith(g) for g in gold)) / 5.0
        rows.append({"q": q, "top": docs[:5], "recall": rec, "context": ctx})
    n = len(answerable)
    return {"rerank": rerank, "rows": rows,
            "recall": sum(r["recall"] for r in rows) / n,
            "context": sum(r["context"] for r in rows) / n,
            "elapsed_s": round(time.time() - t0, 1)}


def main() -> int:
    off = eval_set(rerank=False)
    on = eval_set(rerank=True)
    print(f"\n=== W4 前后对比（20 条有答案，rerank 池={__import__('config').RERANK_POOL}）===")
    print(f"{'':14s} rerank OFF     rerank ON")
    print(f"{'召回率':12s} {off['recall']:6.0%}        {on['recall']:6.0%}")
    print(f"{'上下文相关性':8s} {off['context']:6.0%}        {on['context']:6.0%}")
    print(f"耗时 OFF={off['elapsed_s']}s ON={on['elapsed_s']}s")
    json.dump({"off": off, "on": on},
              open("logs/rerank_compare_w4.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())