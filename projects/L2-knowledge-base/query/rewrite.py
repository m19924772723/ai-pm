# -*- coding: utf-8 -*-
"""查询改写（query rewriting，Day 25 新增）。

为什么做（W4 遗留缺口，Day 14/22/24 三次记录的同一类失败）：
- 同义改写题：用户口语问法 ≠ 文档写法。「L1 用了哪个界面框架？」vs 原文
  「前端/UI Streamlit」——词面不重叠，gold 块 dense_rank≈148/lex_rank≈78，
  候选池（top-30×2）根本装不下。
- 日期模糊题：「Day 15 完成了什么？」→ 真实答案在 log/2026-10-07.md，
  但 nemotron 对 "Day 15" → 日期 的映射无感（dense_rank=550）。

做法（对齐 woshipm《RAG 从 Demo 到生产》12 策略的"查询改写"要点）：
- **保留原始查询，改写查询作为并集候选**——防止改写带偏（原题照常检索）。
- 两条改写通道，都离线可复现：
  1. 规则通道：日期归一化。「Day N / 第 N 天」→ 追加日期串（Day 1 = 2026-09-23，
     每周一至日连续编号，见 log/ 文件名与进度快照核对，线性 +N-1 天）。
  2. LLM 通道：把口语问题改写成"文档里可能出现"的检索表达；结果写缓存
     data/query_rewrites.json（gitignore，不重复付费），评测只读缓存不调网。
- 改写只负责"把候选池撑大"，重排仍用原始问题打分（用户意图为准）。

用法：
    from query import rewrite
    rewrite.rewrite("Day 5 完成了什么？", cache_only=True)
    # -> ["Day 5 完成了什么？ 2026-09-27", "…", …]  首个元素必是原查询
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
from pathlib import Path

import config

CACHE_FILE = config.DATA_DIR / "query_rewrites.json"

# Day 1 = 2026-09-23（首次开工日，进度快照核对过：Day 14=10-06、Day 15=10-07）
DAY1 = _dt.date(2026, 9, 23)

_RE_DAY = re.compile(r"(?i)(?:day|第)\s*(\d{1,3})\s*(?:天|日|\.)?")
# 只匹配明确单一日号（1~99），避免误伤正文里的长数字
_RE_DAY_SAFE = re.compile(r"(?i)\bday\s*(\d{1,2})\b|第\s*(\d{1,2})\s*天")

_REWRITE_SYSTEM = (
    "你是个人知识库（一名 AI 产品经理的工作文档、日志、项目笔记）的检索查询改写器。\n"
    "把用户问题改写成一条更利于检索的查询：\n"
    "1) 保留原问题意图；\n"
    "2) 补充知识库文档里可能出现的写法（技术术语、专名、文件名关键词、具体数字）；\n"
    "3) 只输出一条改写结果，不超过 40 字，不要解释、引号或序号；\n"
    "4) 若问题本身已是精确检索表达，可原样返回。"
)

_cache: dict | None = None


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        _cache = {}
        if CACHE_FILE.exists():
            try:
                d = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                if isinstance(d, dict):
                    _cache = d
            except Exception:
                _cache = {}
    return _cache


def _save_cache() -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(_cache, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass


def day_date(number: int) -> str:
    """Day N 对应的日期串 YYYY-MM-DD（Day 1 = 2026-09-23，线性加 N-1 天）。"""
    return str(DAY1 + _dt.timedelta(days=number - 1))


def expand_day(question: str) -> str:
    """规则通道：query 里出现 Day N / 第 N 天 → 追加对应日期，返回新查询（无日期则原样）。"""
    m = _RE_DAY_SAFE.search(question)
    if not m:
        return question
    n = int(m.group(1) or m.group(2))
    if n < 1 or n > 99:
        return question
    return f"{question} {day_date(n)}"


def _llm_rewrite(question: str) -> str:
    """LLM 通道：口语问题 → 检索表达。失败返回原问题（不抛、不阻塞检索）。"""
    from query import llm_utils
    try:
        meta = llm_utils.chat_with_fallback(_REWRITE_SYSTEM, question,
                                            model=None, max_tokens=256, temperature=0.0)
        text = meta["text"].strip().strip('"')
        return text if text and len(text) <= 80 else question
    except Exception:
        return question


def rewrite(question: str, cache_only: bool = False, use_llm: bool = True) -> list[str]:
    """返回检索用查询列表：[原查询(含日期扩展), 改写查询(含日期扩展)]。

    - cache_only=True：只读缓存（评测用，保证离线、可复现、不重复付费）。
      缓存缺失时改写查询降级为原查询——不隐式调网。
    - use_llm=False：纯规则（日期归一化），不碰 LLM（离线单测用）。
    - 所有版本都含规则通道（日期扩展）。
    """
    expanded = expand_day(question)
    kept = expanded if expanded != question else question   # 原查询（规则扩展后）
    out = [kept]

    if not os.environ.get("L2_REWRITE_OFF"):
        cache = _load_cache()
        entry = cache.get(question) if cache_only else None
        if entry is None and cache_only:
            # 缓存未命中：降级原查询（评测能不能复现的标准是缓存存在性，不是网络）
            return out
        if use_llm and entry is None and not cache_only:
            rw = _llm_rewrite(question)
            entry = {"rewritten": rw, "provider": "llm"}
            cache[question] = entry
            _save_cache()
        rw = entry["rewritten"] if isinstance(entry, dict) else rw if use_llm else question
        rw = expand_day(rw) if rw else question
        if rw and rw not in out:
            out.append(rw)
    return out


def gen_cache_for(questions: list[str]) -> dict:
    """对给定问题列表逐个生成改写缓存（LLM 通道 + 规则），失败跳过。返回新生成条数。"""
    cache = _load_cache()
    made = 0
    for q in questions:
        if q in cache:
            continue
        rw = _llm_rewrite(q)
        cache[q] = {"rewritten": rw, "provider": "llm"}
        _save_cache()   # 逐条落盘：中途挂了也不丢前面
        made += 1
    return {"cached": len(cache), "generated": made}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "L1 用了哪个界面框架？"
    print("原查询:", q)
    print("日期扩展:", expand_day(q))
    print("rewrite(cache_only=True):", rewrite(q, cache_only=True))
    print("rewrite(LLM 在线):", rewrite(q))
