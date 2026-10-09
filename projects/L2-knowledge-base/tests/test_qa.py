# -*- coding: utf-8 -*-
"""问答链路离线单测：引用校验、JSON 解析、拒答把关（不联网）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from query import answer as qa  # noqa: E402


def test_quote_exact_substring():
    assert qa._find_quote("分块策略要保留字符偏移", "c0", "分块策略要保留") == (True, "")


def test_quote_allows_whitespace_diff_only():
    ok, msg = qa._find_quote("学院要求在 10 月 8 日前提交", "c0", "10月8日前")
    assert ok
    assert "空白" in msg


def test_quote_rejects_rewrite():
    ok, _ = qa._find_quote("分块策略要保留字符偏移", "c0", "分块策略需要保留偏移")
    assert not ok


def test_quote_rejects_cross_sentence_merge():
    # 跨块拼接：quote 由两个块的句子拼成，在任一单块里都不是连续子串 → 必须失败
    ok, msg = qa.verify_quotes(
        {"chunk_0": "故障转移会在主端点失败时自动切换。", "chunk_1": "第二个块的内容。"},
        {"chunk_id": "chunk_0", "quote": "故障转移会在主端点失败时自动切换。第二个块的内容。"})
    assert not ok
    assert "未在块" in msg


def test_quote_rejects_unknown_chunk():
    ok, msg = qa.verify_quotes({"c0": "文本"}, {"chunk_id": "c9", "quote": "文本"})
    assert not ok
    assert "不在本次检索结果中" in msg


def test_citation_id_accepts_both_forms():
    texts = {"chunk_0": "甲", "chunk_1": "乙"}
    ok, idx = qa.check_citation_found("1", texts)
    assert ok and idx == 0          # 用户可见编号（从 1 起）
    ok, idx = qa.check_citation_found("chunk_1", texts)
    assert ok and idx == 1          # 内部名
    ok, _ = qa.check_citation_found("2", texts)
    assert ok                       # 2 → idx 1
    ok, _ = qa.check_citation_found("9", texts)
    assert not ok                   # 越界
    ok, _ = qa.check_citation_found("abc", texts)
    assert not ok                   # 乱填


def test_verify_quotes_with_user_facing_id():
    texts = {"chunk_0": "故障转移会在主端点失败时自动切换。"}
    ok, msg = qa.verify_quotes(texts, {"chunk_id": "1", "quote": "故障转移会在主端点失败时自动切换"})
    assert ok
    assert "空白" in msg or msg == ""


def test_extract_json_plain_and_fenced():
    assert qa.extract_json('{"answer": "x"}') == {"answer": "x"}
    assert qa.extract_json('```json\n{"answer": "x"}\n```') == {"answer": "x"}


def test_extract_json_rejects_non_object():
    try:
        qa.extract_json("答案是 42")
        assert False, "应当失败"
    except qa.QAError:
        pass


def test_relevant_gate_requires_lexical_hit():
    # 全 0 BM25 分 → 拒答开关
    assert not qa._relevant_ok(hits=["x"], bm25_top_score=0.0)
    assert qa._relevant_ok(hits=["x"], bm25_top_score=1.0)


def test_prompt_contains_block_numbers():
    p = qa.prompt.build_user_prompt("问题", [{"id": "c0", "text": "甲"}, {"id": "c1", "text": "乙"}])
    assert "[1]" in p and "[2]" in p
    assert "JSON" in qa.prompt.SYSTEM_PROMPT