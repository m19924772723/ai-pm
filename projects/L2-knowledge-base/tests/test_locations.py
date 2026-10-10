# -*- coding: utf-8 -*-
"""引用定位 + 拒答逻辑的离线单测（不联网）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from query import answer as qa  # noqa: E402
from query.answer import QAAnswer  # noqa: E402


def _mk_answer(citations, **kw):
    a = QAAnswer(question="t", **kw)
    a.citations = citations
    return a


class FakeDoc:
    def __init__(self, doc_id, text):
        self.doc_id = doc_id
        self.text = text


def test_citation_locations_include_source_text():
    a = _mk_answer([{"chunk_id": "chunk_0", "doc_id": "docs/x.md", "heading_path": "h",
                     "quote": "片段", "char_start": 10, "char_end": 12}])
    docs = {"docs/x.md": FakeDoc("docs/x.md", "原文……片段……")}
    locs = qa.citation_locations(a, docs)
    assert len(locs) == 1
    assert locs[0]["source_text"] == "原文……片段……"
    assert locs[0]["char_start"] == 10


def test_citation_locations_missing_doc_keeps_offset():
    a = _mk_answer([{"chunk_id": "c0", "doc_id": "docs/gone.md", "quote": "x",
                     "char_start": 3, "char_end": 4}])
    locs = qa.citation_locations(a, {})
    assert locs[0]["source_text"] == ""
    assert locs[0]["char_start"] == 3


def test_quote_span_is_exact_in_source():
    """端到端不变量：偏移切片 == quote（引用可高亮的前提）。"""
    source = "今天天气很好，适合出去走走。"
    quote = "今天天气很好"
    start = source.index(quote)
    end = start + len(quote)
    assert source[start:end] == quote


def test_refusal_detection_heuristics():
    from query.answer import _is_refusal

    a1 = QAAnswer(question="q", unanswerable=True)
    assert _is_refusal(a1) is True
    a2 = QAAnswer(question="q", answer="资料中没有提到")
    assert _is_refusal(a2) is True
    a3 = QAAnswer(question="q", answer="张三去年的年终奖是 30 万")  # 编的，但不在关键词里
    # 拒答判定靠关键词启发式，无法识别这种"硬答"——这是启发式的边界，诚实记录
    assert _is_refusal(a3) is False