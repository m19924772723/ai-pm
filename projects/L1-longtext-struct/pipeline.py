# -*- coding: utf-8 -*-
"""L1 核心链路：文本 → 结构化 JSON。

这个模块是"产品逻辑"，与 Streamlit 界面解耦，方便被 CLI、测试和评测脚本复用。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any

from prompts.templates import SYSTEM_PROMPT, build_user_prompt
from utils import schema as schema_utils
from utils.llm import LLMError, call_llm_meta, provider_info

# 输入过长的保护阈值：超过就先截断并记录（分块策略留到后续迭代）
MAX_CHARS = 24000
# 输出预算：推理模型会先消耗一部分 token，4096 曾导致 JSON 被截断
MAX_TOKENS = 8192


@dataclass
class StructResult:
    ok: bool
    template: str
    data: dict[str, Any] | None = None
    raw: str = ""
    error: str = ""
    elapsed_s: float = 0.0
    provider: dict[str, Any] = field(default_factory=dict)
    schema_ok: bool = False
    schema_errors: list[str] = field(default_factory=list)
    evidence_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    finish_reason: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def structure(text: str, template: str = "summary", provider: str | None = None,
              max_tokens: int = MAX_TOKENS) -> StructResult:
    """把长文结构化为指定模板的 JSON。"""
    warnings: list[str] = []
    src = (text or "").strip()
    if len(src) < 50:
        return StructResult(ok=False, template=template, error="输入过短（少于 50 字）")

    if len(src) > MAX_CHARS:
        warnings.append(f"输入 {len(src)} 字超过 {MAX_CHARS} 字，已截断（分块策略待迭代）")
        src = src[:MAX_CHARS]

    try:
        info = provider_info(provider)
    except LLMError as e:
        return StructResult(ok=False, template=template, error=str(e))

    user_prompt = build_user_prompt(template, src)
    t0 = time.time()
    try:
        meta = call_llm_meta(SYSTEM_PROMPT, user_prompt, provider=provider, max_tokens=max_tokens)
    except LLMError as e:
        return StructResult(ok=False, template=template, error=str(e), provider=info,
                            elapsed_s=round(time.time() - t0, 2))
    elapsed = round(time.time() - t0, 2)

    raw = meta["text"]
    finish_reason = meta.get("finish_reason", "") or ""
    usage = meta.get("usage") or {}
    # 截断信号：finish_reason 表示长度用尽，或 JSON 括号不配对
    truncated = finish_reason in ("length", "max_tokens") or _unbalanced(raw)
    if finish_reason in ("length", "max_tokens"):
        warnings.append(f"输出被截断（finish_reason={finish_reason}）：max_tokens={max_tokens} 已用尽，"
                        f"需提高预算或精简 Schema")

    try:
        data = schema_utils.extract_json(raw)
    except schema_utils.ParseError as e:
        err = f"JSON 解析失败: {e}"
        if truncated:
            err += "；根因是输出被截断（见 warnings），不是模型不会写 JSON"
        return StructResult(ok=False, template=template, raw=raw, error=err, provider=info,
                            elapsed_s=elapsed, warnings=warnings, finish_reason=finish_reason,
                            usage=usage, truncated=truncated)

    ok_schema, schema_errors = schema_utils.validate(data, template)
    evidence_issues = schema_utils.check_evidence(data, src)

    return StructResult(ok=True, template=template, data=data, raw=raw, provider=info,
                        elapsed_s=elapsed, schema_ok=ok_schema, schema_errors=schema_errors,
                        evidence_issues=evidence_issues, warnings=warnings,
                        finish_reason=finish_reason, usage=usage, truncated=truncated)


def _unbalanced(text: str) -> bool:
    """粗判 JSON 是否被截断：花括号/方括号不配对（忽略字符串内部）。"""
    depth_c, depth_b, in_str, esc = 0, 0, False, False
    for ch in text:
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
            depth_c += 1
        elif ch == "}":
            depth_c -= 1
        elif ch == "[":
            depth_b += 1
        elif ch == "]":
            depth_b -= 1
    return in_str or depth_c != 0 or depth_b != 0


def to_markdown(result: StructResult) -> str:
    """把结构化结果渲染成 Markdown，供"一键复制"。"""
    if not result.ok or not result.data:
        return f"生成失败：{result.error}"
    d = result.data
    lines: list[str] = [f"# {d.get('title', '（无标题）')}", ""]

    if result.template == "summary":
        lines += [f"> {d.get('one_sentence_summary', '')}", "", "## 关键点", ""]
        for kp in d.get("key_points", []):
            lines.append(f"- **{kp.get('point', '')}**")
            lines.append(f"  - 依据：{kp.get('evidence', '')}")
        if d.get("tags"):
            lines += ["", "**标签**：" + " · ".join(d["tags"])]
        if d.get("todos"):
            lines += ["", "## 待办", ""]
            for t in d["todos"]:
                lines.append(f"- [ ] {t.get('action', '')}（{t.get('owner', '未指定')} · {t.get('deadline', '未指定')}）")
        if d.get("uncertainties"):
            lines += ["", "## 待确认", ""] + [f"- {u}" for u in d["uncertainties"]]

    elif result.template == "todos":
        lines += ["## 待办", ""]
        if not d.get("todos"):
            lines.append("（原文没有明确待办）")
        for t in d.get("todos", []):
            lines.append(f"- [ ] {t.get('action', '')}")
            lines.append(f"  - 负责人：{t.get('owner', '未指定')}｜截止：{t.get('deadline', '未指定')}"
                         f"｜产出：{t.get('deliverable', '未指定')}｜优先级：{t.get('priority', 'unspecified')}")
        if d.get("not_todos"):
            lines += ["", "## 不算待办的内容", ""] + [f"- {x}" for x in d["not_todos"]]

    else:
        lines += [f"**类型**：{d.get('source_type', 'unknown')}｜**主题**：{d.get('topic', '')}", "",
                  f"> {d.get('summary', '')}", ""]
        if d.get("claims"):
            lines += ["## 主张", ""] + [f"- {c.get('claim', '')}（依据：{c.get('evidence', '')}）" for c in d["claims"]]
        if d.get("facts"):
            lines += ["", "## 事实", ""] + [f"- {f.get('fact', '')}（依据：{f.get('evidence', '')}）" for f in d["facts"]]
        if d.get("keywords"):
            lines += ["", "**关键词**：" + " · ".join(d["keywords"])]
        if d.get("follow_up_questions"):
            lines += ["", "## 待确认问题", ""] + [f"- {q}" for q in d["follow_up_questions"]]

    if result.warnings:
        lines += ["", "---", "", "**警告**：" + "；".join(result.warnings)]
    return "\n".join(lines)
