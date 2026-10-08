# -*- coding: utf-8 -*-
"""检索器离线单测：分词、BM25、RRF 融合（不联网、不调 embedding）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from index.retriever import BM25, lexical_tokens, rrf_fuse  # noqa: E402


def test_lexical_tokens_chinese_bigrams():
    # 连续汉字串按滑动二元组切："跨端点故障转移" → 6 个二元组
    assert lexical_tokens("跨端点故障转移") == ["跨端", "端点", "点故", "故障", "障转", "转移"]


def test_lexical_tokens_ascii_lowercased():
    assert lexical_tokens("Streamlit App") == ["streamlit", "app"]


def test_ascii_wireframe_produces_no_tokens():
    """ASCII 线框图（─│┌└┐┘）一个 token 都不应产生 → 天然免疫图块污染。"""
    fig = "│   ┌──────────────┐  │\n└────┴────┘"
    assert lexical_tokens(fig) == []


def test_bm25_ranks_exact_match_first():
    docs = ["跨端点故障转移在 10 月 6 日落地", "今天是晴天适合散步", "L1 评测要写指标口径"]
    bm = BM25.build(docs)
    scores = bm.score_all("跨端点故障转移")
    assert scores[0] > scores[1] and scores[0] > scores[2]


def test_bm25_term_frequency_counts():
    docs = ["故障 故障 故障", "故障 意外"]
    bm = BM25.build(docs)
    scores = bm.score_all("故障")
    assert scores[0] > scores[1]


def test_rrf_fuses_two_rankings():
    a = [0, 1, 2, 3]
    b = [3, 2, 1, 0]
    fused = rrf_fuse([a, b])
    assert fused[0] in (0, 3)  # 两个排名里都靠前的先出
    assert set(fused) == set(a)


def test_rrf_item_in_both_ranks_first():
    # 两个排序都把 2 放第一 → 融合后 2 必须第一
    a = [2, 0, 1]
    b = [2, 1, 0]
    assert rrf_fuse([a, b])[0] == 2


def test_rrf_tie_is_stable():
    # 完全对称的排名会平票（RRF 数学上等价）——断言不崩、只出两者之一
    a = [0, 1, 2]
    b = [1, 0, 2]
    assert rrf_fuse([a, b])[0] in (0, 1)


def test_bm25_empty_query_zero():
    bm = BM25.build(["任意文本"])
    assert bm.score_all("") == [0.0]