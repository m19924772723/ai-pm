# -*- coding: utf-8 -*-
"""问答链路：检索 → 相关性把关 → LLM 生成（带故障转移）→ 引用校验。

管线：
  1. retriever.search_all(question, k) → 候选块（每个带 doc/偏移/正文）
  2. 检索端把关：BM25 无任何词面命中的块剔除；一个相关的都没有 → 直接拒答（省一次 LLM 调用）
  3. prompt + LLM（chat_with_fallback，故障转移自动）
  4. 解析 JSON → 引用校验（quote 必须是块文本的完整连续子串，规则见 query/prompt.py）
  5. 返回 QAAnswer（answer / citations / unanswerable / 诊断信息）

引用准确性是本项目的核心指标之一——引用必须能在资料块里逐字定位，
否则"看起来有引用"等于没有（L1 的 evidence 教训）。
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

from index import retriever
from index.store import Hit
from query import llm_error, llm_utils, prompt


class QAError(RuntimeError):
    pass


@dataclass
class QAAnswer:
    question: str
    answer: str = ""
    unanswerable: bool = False
    citations: list[dict] = field(default_factory=list)      # {chunk_id, doc_id, heading_path, quote, char_start, char_end}
    chunks_used: int = 0                                      # 送进 LLM 的块数
    provider: str = ""
    fallback_from: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0
    quote_issues: list[str] = field(default_factory=list)     # 校验剔除的引用
    raw: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        d["citations"] = [{k: v for k, v in c.items()} for c in self.citations]
        return d


# ---------- 引用校验（完整连续子串，空白归一化） ----------

def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _find_quote(chunk_text: str, chunk_id: str, quote: str) -> tuple[bool, str]:
    """quote 是否 chunk_text 的（空白归一化后）连续子串。

    允许空格差异（'10 月 8 日' vs '10月8日'），其余必须逐字一致。
    """
    if not quote or not chunk_text:
        return False, "quote 或块文本为空"
    if quote in chunk_text:
        return True, ""
    if _norm(quote) in _norm(chunk_text):
        return True, "（允许空白差异）"
    return False, f"quote 未在块 {chunk_id} 中找到（非连续子串/改写/删节）"


def check_citation_found(cid: str, texts_by_id: dict[str, str]) -> tuple[bool, int]:
    """把 citations.chunk_id 解析成块序号 + 校验存在。

    模型可能写 chunk_id='1'（用户可见编号，从 1 起）或 'chunk_0'（内部名）——
    两种都接受，统一解析成 used 列表的序号，贴近模型自然输出（L1 教训：让模型
    写用户可见物，而不是内部标识的翻译层）。
    """
    n = len(texts_by_id)
    if cid in texts_by_id:
        m = re.fullmatch(r"chunk_(\d+)", cid)
        return (True, int(m.group(1))) if m else (False, -1)
    if re.fullmatch(r"\d+", cid):
        idx = int(cid) - 1
        if 0 <= idx < n:
            return True, idx
        return False, -1
    return False, -1


def verify_quotes(texts_by_id: dict[str, str], citation: dict) -> tuple[bool, str]:
    found, idx = check_citation_found(str(citation.get("chunk_id", "")), texts_by_id)
    if not found:
        return False, f"chunk_id {citation.get('chunk_id')} 不在本次检索结果中（模型编了块编号）"
    quote = (citation.get("quote") or "").strip()
    chunk_text = texts_by_id[f"chunk_{idx}"]
    return _find_quote(chunk_text, f"chunk_{idx}", quote)


# ---------- JSON 解析 ----------

def extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(json)?\s*|\s*```$", "", raw)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise QAError("输出中没有 JSON 对象")
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise QAError(f"JSON 解析失败: {e}") from None
    if not isinstance(obj, dict):
        raise QAError("JSON 不是对象")
    return obj


# ---------- 检索端拒答 ----------

def _relevant_ok(hits: list[Hit], bm25_top_score: float) -> bool:
    """检索把关：命中的块里至少有一个有词面相关性（BM25 分 > 0）。

    语义相关但词面全不命中是危险的（embedding 对中文区分弱），宁缺毋滥。
    """
    return bm25_top_score > 0 and len(hits) > 0


# ---------- 问答主流程 ----------

def answer(question: str, k: int = 5, provider: str | None = None,
           max_tokens: int = 1024, allow_fallback: bool = True) -> QAAnswer:
    t0 = time.time()
    q = (question or "").strip()
    if len(q) < 2:
        raise QAError("问题过短")

    hits = retriever.search_all(q, k=k)
    bm = retriever.BM25.build([h.text for h in hits])
    bm_scores = bm.score_all(q)
    keep = [h for h, s in zip(hits, bm_scores) if s > 0]
    used = keep or hits  # 全没词面命中时仍给 LLM 看（由其判断是否拒答）

    # 组块字典供引用校验
    texts_by_id = {}
    for i, h in enumerate(used):
        cid = f"chunk_{i}"
        texts_by_id[cid] = h.text

    chunk_objs = [{"id": f"chunk_{i}", "text": h.text} for i, h in enumerate(used)]

    if not _relevant_ok(used, bm_scores[0] if bm_scores else 0):
        return QAAnswer(question=q, unanswerable=True, chunks_used=len(chunk_objs),
                        warnings=["检索无相关块（无任何词面命中），拒答"],
                        elapsed_s=round(time.time() - t0, 2))

    user = prompt.build_user_prompt(q, chunk_objs)
    # 瞬态失败重试 1 次（L1 教训：stepfun 曾出现"空内容"瞬态，重试即成功；
    # 也覆盖 JSON 解析失败——偶发的非 JSON 输出换一次调用通常能救回）
    meta = None
    last_err = ""
    obj = None
    for attempt in range(2):
        try:
            meta = llm_utils.chat_with_fallback(prompt.SYSTEM_PROMPT, user, provider=provider,
                                                max_tokens=max_tokens, allow_fallback=allow_fallback)
            obj = extract_json(meta["text"])
            break
        except (llm_error.LLMError, QAError) as e:
            last_err = str(e)
            if attempt == 0:
                time.sleep(3)
    if meta is None:
        raise QAError(last_err)

    raw = meta["text"]
    if obj is None:
        return QAAnswer(question=q, chunks_used=len(chunk_objs), provider=meta.get("provider", ""),
                        fallback_from=meta.get("fallback_from", []),
                        warnings=meta.get("warnings", []) + [last_err],
                        raw=raw, elapsed_s=round(time.time() - t0, 2))

    unanswerable = bool(obj.get("unanswerable", False))
    citations: list[dict] = []
    issues: list[str] = []
    for c in obj.get("citations", []) or []:
        if not isinstance(c, dict):
            continue
        ok, msg = verify_quotes(texts_by_id, c)
        if not ok:
            issues.append(f"{c.get('chunk_id')}: {msg}")
            continue
        _, idx = check_citation_found(str(c.get("chunk_id", "")), texts_by_id)
        h = used[idx] if 0 <= idx < len(used) else None
        citations.append({
            "chunk_id": f"chunk_{idx}", "doc_id": h.doc_id if h else "",
            "heading_path": h.heading_path if h else "",
            "quote": c["quote"], "char_start": h.char_start if h else 0,
            "char_end": h.char_end if h else 0,
        })

    return QAAnswer(
        question=q,
        answer=str(obj.get("answer", "")),
        unanswerable=unanswerable,
        citations=citations,
        chunks_used=len(chunk_objs),
        provider=meta.get("provider", ""),
        fallback_from=meta.get("fallback_from", []),
        warnings=meta.get("warnings", []),
        quote_issues=issues,
        raw=raw,
        elapsed_s=round(time.time() - t0, 2),
    )


def answer_n(questions: list[str], k: int = 5, **kw) -> list[QAAnswer]:
    """批量问答（评测用）。"""
    return [answer(q, k=k, **kw) for q in questions]