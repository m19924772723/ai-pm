# -*- coding: utf-8 -*-
"""问答链路自测：真问题 × 4（含 1 个资料里没有的 → 应拒答）。

用法：python -m scripts.qa_demo
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query import answer  # noqa: E402


def main() -> int:
    questions = [
        "跨端点故障转移是做什么的？为什么需要它？",
        "L1 的幻觉率是多少？",
        "分块为什么要保留字符偏移？",
        "我今天中午应该吃什么？",   # 资料里没有 → 应拒答
    ]
    for q in questions:
        print(f"\n{'=' * 60}\n问题：{q}")
        a = answer.answer(q)
        print(f"provider={a.provider} fallback={a.fallback_from or '无'} "
              f"chunks={a.chunks_used} 耗时={a.elapsed_s}s")
        if a.unanswerable:
            print(f"→ 拒答：{a.warnings}")
            continue
        print(f"答案：{a.answer[:300]}")
        for c in a.citations:
            print(f"  引用[{c['chunk_id']}] {c['doc_id']} 偏移[{c['char_start']}:{c['char_end']}] "
                  f"quote={c['quote'][:40]!r}")
        if a.quote_issues:
            print(f"quote_issues: {a.quote_issues}")
        if a.warnings:
            print(f"warnings: {a.warnings}")
        json.dump(a.to_dict(), open(f"logs/qa_{q[:12]}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())