# -*- coding: utf-8 -*-
"""引用定位端到端：答案引用 → 磁盘文件 → 原文片段（可高亮）。

用法：python -m scripts.citation_locate "L1 的幻觉率是多少"
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.loader import load_docs  # noqa: E402
from query import answer as qa  # noqa: E402
from query.docpath import resolve_doc_path  # noqa: E402


def main() -> int:
    q = " ".join(sys.argv[1:]) or "L1 的幻觉率是多少"
    a = qa.answer(q)
    docs = {d.doc_id: d for d in load_docs()}
    print(f"问题：{q}\n")
    if a.unanswerable:
        print("→ 拒答")
        return 0
    print(f"答案：{a.answer[:200]}\n")
    for c in a.citations:
        doc = docs.get(c.get("doc_id", ""))
        src_text = doc.text if doc else ""
        start, end = c.get("char_start", 0), c.get("char_end", 0)
        slice_ = src_text[start:end] if src_text else ""
        p = resolve_doc_path(c.get("doc_id", ""), c.get("doc_id", ""))
        # quote 是该块的一段（不是整块）；校验"quote 必须落在偏移切片内"
        quote = c.get("quote", "")
        ok = bool(slice_) and quote in slice_
        print(f"[{'✓' if ok else '✗'}] {c.get('doc_id')} 偏移[{start}:{end}]")
        print(f"      文件: {p}")
        print(f"      片段: {slice_[:60]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())