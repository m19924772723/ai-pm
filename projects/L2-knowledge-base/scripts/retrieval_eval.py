# -*- coding: utf-8 -*-
"""检索评测：稠密 vs 混合（BM25）对比，用 Recall@5 / MRR 说话。

gold = 10 条真实提问，每条标注预期命中的文档（第一批为草案，人工复核后转正式）。
用法：python -m scripts.retrieval_eval [--hybrid|--dense]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index import retriever  # noqa: E402

# (问题, [预期命中的 doc_id 前缀])
GOLD: list[tuple[str, list[str]]] = [
    ("跨端点故障转移是做什么的", ["log/2026-10-06.md"]),
    ("为什么要做跨端点故障转移", ["log/2026-10-06.md"]),
    ("L1 的幻觉率是多少", ["docs/L1-1项目说明.md", "docs/L1评测方法.md"]),
    ("评测集是怎么构建的", ["docs/L1评测方法.md"]),
    ("分块策略为什么要保留字符偏移", ["docs/L2-1项目预研.md"]),
    ("向量数据库用 Chroma 还是 FAISS", ["docs/L2-1项目预研.md"]),
    ("部署方案是什么", ["docs/L1部署上线方案.md"]),
    ("简历里的经历怎么写法", ["docs/简历骨架.md"]),
    ("Day 5 完成了什么", ["log/2026-09-27.md"]),
    ("面试怎么练习", ["docs/面试准备参考文档.md"]),
]


def hit_at_k(doc_ids: list[str], gold_prefixes: list[str]) -> bool:
    return any(d.startswith(g) for d in doc_ids for g in gold_prefixes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hybrid", action="store_true", default=True, help="混合检索（默认）")
    ap.add_argument("--dense", action="store_true", help="只用稠密向量（对照）")
    args = ap.parse_args()
    dense_only = args.dense

    rows = []
    t0 = time.time()
    for q, gold in GOLD:
        hits = retriever.search_all(q, k=5, dense=not dense_only, lexical=not dense_only)
        docs = [h.doc_id for h in hits]
        hit5 = hit_at_k(docs, gold)
        pos = next((i for i, d in enumerate(docs) if any(d.startswith(g) for g in gold)), None)
        mrr = 1.0 / (pos + 1) if pos is not None else 0.0
        rows.append({"q": q, "gold": gold, "top": docs[:5], "recall@5": hit5, "mrr": mrr})
        print(f"[{'✓' if hit5 else '✗'}] {q}")
        for d in docs[:3]:
            print(f"      {d}")
    dt = time.time() - t0

    recall = sum(r["recall@5"] for r in rows) / len(rows)
    mrr = sum(r["mrr"] for r in rows) / len(rows)
    print(f"\n=== {'稠密' if dense_only else '混合'} 检索 · 10 问 ===")
    print(f"Recall@5 = {recall:.0%}（{int(recall*len(rows))}/{len(rows)}）｜MRR = {mrr:.3f}｜耗时 {dt:.1f}s")
    mode = "dense_only" if dense_only else "hybrid"
    json.dump({"mode": mode, "recall@5": round(recall, 4), "mrr": round(mrr, 4),
               "rows": rows, "elapsed_s": round(dt, 1)},
              open(f"logs/retrieval_eval_{mode}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())