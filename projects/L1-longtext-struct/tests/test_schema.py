# -*- coding: utf-8 -*-
"""不依赖网络的单元测试：JSON 提取、Schema 校验、证据回溯、Markdown 渲染。

运行：.venv/Scripts/python.exe -m pytest tests -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import StructResult, structure, to_markdown  # noqa: E402
from utils import schema as S  # noqa: E402


# ---------- extract_json ----------

def test_extract_plain_json():
    assert S.extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_from_code_fence():
    txt = '```json\n{"a": 1}\n```'
    assert S.extract_json(txt) == {"a": 1}


def test_extract_json_with_preamble():
    txt = '好的，结果如下：\n{"title": "x", "n": 2}\n以上。'
    assert S.extract_json(txt) == {"title": "x", "n": 2}


def test_extract_json_nested_braces_and_strings():
    txt = '{"a": {"b": "}"} , "c": 3}'
    assert S.extract_json(txt) == {"a": {"b": "}"}, "c": 3}


def test_extract_json_rejects_array():
    with pytest.raises(S.ParseError):
        S.extract_json('[1, 2]')


def test_extract_json_rejects_truncated():
    with pytest.raises(S.ParseError):
        S.extract_json('{"a": 1, "b": {')


def test_extract_json_rejects_empty():
    with pytest.raises(S.ParseError):
        S.extract_json('   ')


# ---------- validate ----------

GOOD_SUMMARY = {
    "title": "T",
    "one_sentence_summary": "一句话",
    "key_points": [{"point": "p", "evidence": "e"}],
    "tags": ["a"],
    "todos": [],
    "uncertainties": [],
}


def test_validate_summary_ok():
    ok, errors = S.validate(GOOD_SUMMARY, "summary")
    assert ok, errors


def test_validate_summary_missing_field():
    bad = {k: v for k, v in GOOD_SUMMARY.items() if k != "tags"}
    ok, errors = S.validate(bad, "summary")
    assert not ok and errors


def test_validate_todos_bad_priority():
    bad = {"title": "t", "not_todos": [],
           "todos": [{"action": "a", "owner": "o", "deadline": "d",
                      "deliverable": "x", "priority": "urgent", "evidence": "e"}]}
    ok, errors = S.validate(bad, "todos")
    assert not ok and any("priority" in e for e in errors)


def test_validate_archive_bad_source_type():
    bad = {"title": "t", "source_type": "blog", "topic": "x", "summary": "s",
           "claims": [], "facts": [], "keywords": [], "follow_up_questions": []}
    ok, errors = S.validate(bad, "archive")
    assert not ok


# ---------- check_evidence ----------

def test_evidence_hit():
    src = "项目当前已完成 60% 的开发。"
    obj = {"key_points": [{"point": "p", "evidence": "已完成 60% 的开发"}]}
    assert S.check_evidence(obj, src) == []


def test_evidence_miss_detected():
    src = "项目当前已完成 60% 的开发。"
    obj = {"key_points": [{"point": "p", "evidence": "已完成 90% 的开发"}]}
    issues = S.check_evidence(obj, src)
    assert len(issues) == 1 and "未在原文找到" in issues[0]


def test_evidence_too_short():
    obj = {"key_points": [{"point": "p", "evidence": "完成"}]}
    issues = S.check_evidence(obj, "项目已经完成")
    assert any("过短" in i for i in issues)


def test_evidence_ignores_non_evidence_strings():
    obj = {"key_points": [{"point": "完全不在原文里的一句话", "evidence": "已完成 60% 的开发"}]}
    assert S.check_evidence(obj, "项目当前已完成 60% 的开发。") == []


# ---------- structure 前置校验（不触网） ----------

def test_structure_rejects_short_input():
    r = structure("太短", template="summary", provider="siyu")
    assert not r.ok and "过短" in r.error


def test_structure_unknown_template_raises():
    with pytest.raises(KeyError):
        from prompts.templates import build_user_prompt
        build_user_prompt("nope", "x")


# ---------- build_user_prompt 回归：模板内含 JSON 花括号 ----------

def test_build_user_prompt_survives_json_braces():
    """回归测试：模板正文含 JSON Schema 的 {}，不能用 format()，否则 KeyError。"""
    from prompts.templates import TEMPLATES, build_user_prompt

    for tpl in TEMPLATES:
        out = build_user_prompt(tpl, "示例正文")
        assert "示例正文" in out, f"{tpl} 未插入输入"
        assert "{{INPUT_TEXT}}" not in out, f"{tpl} 占位符未替换"
        assert "{" in out and "}" in out, f"{tpl} 的 Schema 花括号被破坏"


def test_build_user_prompt_output_round_trips_through_extract_json():
    """模板里给的 Schema 示例本身应是合法 JSON 片段（提示词质量检查）。"""
    import json as _json
    from prompts.templates import TEMPLATES
    import re

    for tpl, cfg in TEMPLATES.items():
        m = re.search(r"输出 JSON Schema：\s*(\{.*?\n\})\s*\n", cfg["user"], re.S)
        assert m, f"{tpl} 找不到 Schema 示例"
        _json.loads(m.group(1))  # 不抛异常即为通过


# ---------- to_markdown ----------

def test_to_markdown_summary():
    r = StructResult(ok=True, template="summary", data=GOOD_SUMMARY)
    md = to_markdown(r)
    assert "# T" in md and "关键点" in md


def test_to_markdown_todos_empty_message():
    r = StructResult(ok=True, template="todos", data={"title": "t", "todos": [], "not_todos": []})
    assert "没有明确待办" in to_markdown(r)


def test_to_markdown_failure():
    r = StructResult(ok=False, template="summary", error="boom")
    assert "生成失败" in to_markdown(r)
