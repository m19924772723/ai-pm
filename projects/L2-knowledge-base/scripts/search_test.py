# -*- coding: utf-8 -*-
"""检索自测：混合检索（稠密+BM25）Top-K 与引用偏移（W1 的验收动作）。

用法：python -m scripts.search_test "分块策略为什么要保留字符偏移"
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index.retriever import search_all


def main() -> int:
    q = " ".join(sys.argv[1:]) or "分块策略为什么要保留字符偏移"
    hits = search_all(q, k=5)
    print(f"问题：{q}\n")
    for i, h in enumerate(hits, 1):
        head = h.text.replace("\n", " ")[:80]
        print(f"[{i}] {h.doc_id}｜{h.heading_path}")
        print(f"     偏移 [{h.char_start}:{h.char_end}]｜{head}…")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
