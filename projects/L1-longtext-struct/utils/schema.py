# -*- coding: utf-8 -*-
"""结构化输出的解析与校验。

L1 的质量指标之一是"格式合规率"——JSON 能否一次解析成功。
这里集中实现：剥代码块 → 定位 JSON → 解析 → 按 Schema 校验。
"""
from __future__ import annotations

import json
import re
from typing import Any

try:
    import jsonschema
except ImportError:  # 允许无 jsonschema 时只做结构检查
    jsonschema = None


class ParseError(ValueError):
    """模型输出无法解析为预期 JSON。"""


_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def extract_json(text: str) -> dict[str, Any]:
    """从模型输出里取出 JSON 对象。"""
    if not text or not text.strip():
        raise ParseError("输出为空")

    candidate = _FENCE.sub("", text.strip())

    # 优先直接解析
    try:
        obj = json.loads(candidate)
        if isinstance(obj, dict):
            return obj
        raise ParseError(f"顶层不是对象，而是 {type(obj).__name__}")
    except json.JSONDecodeError:
        pass

    # 退一步：括号配对扫描，取第一个完整对象
    start = candidate.find("{")
    if start == -1:
        raise ParseError("输出中找不到 JSON 对象")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(candidate)):
        ch = candidate[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                snippet = candidate[start:i + 1]
                try:
                    obj = json.loads(snippet)
                except json.JSONDecodeError as e:
                    raise ParseError(f"括号配对成功但 JSON 非法: {e.msg}") from None
                if not isinstance(obj, dict):
                    raise ParseError("提取出的不是对象")
                return obj
    raise ParseError("JSON 括号不配对，输出可能被截断")


# 三个模板的 Schema：既是给模型的约束，也是本地校验的依据
SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "one_sentence_summary", "key_points", "tags", "todos", "uncertainties"],
    "properties": {
        "title": {"type": "string"},
        "one_sentence_summary": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["point", "evidence"],
                "properties": {"point": {"type": "string"}, "evidence": {"type": "string"}},
            },
        },
        "tags": {"type": "array", "items": {"type": "string"}},
        "todos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action", "owner", "deadline", "evidence"],
                "properties": {
                    "action": {"type": "string"},
                    "owner": {"type": "string"},
                    "deadline": {"type": "string"},
                    "evidence": {"type": "string"},
                },
            },
        },
        "uncertainties": {"type": "array", "items": {"type": "string"}},
    },
}

TODOS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "todos", "not_todos"],
    "properties": {
        "title": {"type": "string"},
        "todos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action", "owner", "deadline", "deliverable", "priority", "evidence"],
                "properties": {
                    "action": {"type": "string"},
                    "owner": {"type": "string"},
                    "deadline": {"type": "string"},
                    "deliverable": {"type": "string"},
                    "priority": {"enum": ["high", "medium", "low", "unspecified"]},
                    "evidence": {"type": "string"},
                },
            },
        },
        "not_todos": {"type": "array", "items": {"type": "string"}},
    },
}

ARCHIVE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "source_type", "topic", "summary", "claims", "facts", "keywords", "follow_up_questions"],
    "properties": {
        "title": {"type": "string"},
        "source_type": {"enum": ["article", "report", "meeting_note", "paper", "unknown"]},
        "topic": {"type": "string"},
        "summary": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "evidence"],
                "properties": {"claim": {"type": "string"}, "evidence": {"type": "string"}},
            },
        },
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["fact", "evidence"],
                "properties": {"fact": {"type": "string"}, "evidence": {"type": "string"}},
            },
        },
        "keywords": {"type": "array", "items": {"type": "string"}},
        "follow_up_questions": {"type": "array", "items": {"type": "string"}},
    },
}

SCHEMAS = {"summary": SUMMARY_SCHEMA, "todos": TODOS_SCHEMA, "archive": ARCHIVE_SCHEMA}


def validate(obj: dict[str, Any], template: str) -> tuple[bool, list[str]]:
    """按模板 Schema 校验；返回 (是否通过, 错误列表)。"""
    schema = SCHEMAS[template]
    if jsonschema is None:
        missing = [k for k in schema["required"] if k not in obj]
        return (not missing, [f"缺字段 {m}" for m in missing])
    v = jsonschema.Draft202012Validator(schema)
    errors = [f"{'/'.join(str(x) for x in e.path) or '<root>'}: {e.message}" for e in v.iter_errors(obj)]
    return (not errors, errors)


def check_evidence(obj: dict[str, Any], source_text: str, min_len: int = 6) -> list[str]:
    """检查 evidence 是否能在原文里找到（宽松匹配）。

    这是"幻觉率"的第一道人工/半自动筛查：evidence 必须可回溯到原文。
    返回问题描述列表，空列表表示全部命中。
    """
    problems: list[str] = []
    norm_src = _norm(source_text)

    def walk(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}/{i}")
        elif isinstance(node, str) and path.endswith("/evidence"):
            if len(node.strip()) < min_len:
                problems.append(f"{path}: evidence 过短 ({node!r})")
            elif _norm(node) not in norm_src:
                problems.append(f"{path}: evidence 未在原文找到 ({node[:30]!r})")

    walk(obj)
    return problems


def _norm(s: str) -> str:
    """归一化：去掉空白、常见标点差异，便于宽松比对。"""
    s = re.sub(r"\s+", "", s)
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"), ("，", ","), ("。", "."),
                 ("：", ":"), ("；", ";"), ("（", "("), ("）", ")"), ("、", ",")):
        s = s.replace(a, b)
    return s
