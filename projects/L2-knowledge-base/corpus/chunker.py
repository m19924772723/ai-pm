# -*- coding: utf-8 -*-
"""分块策略（L2 的核心决策之一）。

策略：**按标题层级切段 + 超长段落按句子窗口切分（带重叠）**
1. 按 markdown 标题（#/##/###…）切出语义段落
2. 段落超过 MAX_CHARS → 在句子边界切窗口，窗口间保留 OVERLAP_CHARS 重叠
3. **每块记录原文的 char_start/char_end**，且 `text == 原文[start:end]`
   —— 这一条是为了"引用定位到段落"：界面可以直接用偏移高亮原文，不用二次搜索

取舍说明（面试可讲）：
- 纯固定长度切分会切断语义（标题与正文分家）
- 纯按标题切分会让某些长章节单块过大，检索精度差
- 混合策略：结构优先，长度兜底
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import config

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
# 句子边界：中文句末标点 / 换行
_SENT_END = re.compile(r"[。！？；!?;]\s*|\n+")


@dataclass
class Block:
    kind: str            # heading | para
    text: str
    start: int
    end: int
    level: int = 0       # 标题层级


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    char_start: int
    char_end: int
    heading_path: str
    index_in_doc: int
    meta: dict = field(default_factory=dict)


def split_blocks(text: str) -> list[Block]:
    """把 markdown 拆成标题块与段落块，保留原文偏移。"""
    blocks: list[Block] = []
    heads = [(m.start(), m.end(), len(m.group(1)), m.group(2).strip()) for m in _HEADING.finditer(text)]

    # 标题行本身作为 heading 块
    for hs, he, lvl, title in heads:
        blocks.append(Block("heading", text[hs:he].strip(), hs, he, lvl))

    # 非标题区间按空行切段
    bounds = [(0, len(text))]
    segments: list[tuple[int, int]] = []
    cursor = 0
    for hs, he, _, _ in heads:
        if hs > cursor:
            segments.append((cursor, hs))
        cursor = he
    if cursor < len(text):
        segments.append((cursor, len(text)))

    for s, e in segments:
        for m in re.finditer(r"[^\n]+(?:\n(?!\s*\n)[^\n]+)*", text[s:e]):
            seg = text[s + m.start():s + m.end()]
            if len(seg.strip()) < 1:
                continue
            blocks.append(Block("para", seg.strip("\n"), s + m.start() + len(seg) - len(seg.lstrip("\n")),
                                s + m.start() + len(seg.rstrip("\n")), 0))
    blocks.sort(key=lambda b: (b.start, b.end))
    return _drop_heading_dupes(blocks)


def _drop_heading_dupes(blocks: list[Block]) -> list[Block]:
    """段落切分可能把标题行也带进来，去掉重叠的段落块。"""
    out: list[Block] = []
    for b in blocks:
        if b.kind == "para" and out and out[-1].kind == "heading" and b.start <= out[-1].end:
            # 段落与标题区间重叠 → 只保留标题块
            if b.end <= out[-1].end or b.text.strip() == out[-1].text.strip():
                continue
        out.append(b)
    return out


def _make_cuts(text: str, max_chars: int) -> list[int]:
    """句子边界集合；单句超过 max_chars 时在句中按 max_chars 插硬切点。

    没有这一步的话，"一个超长句子"会导致窗口要么超限、要么丢内容。
    """
    raw = [0] + [m.end() for m in _SENT_END.finditer(text)]
    if raw[-1] < len(text):
        raw.append(len(text))
    raw = sorted(set(raw))
    cuts: list[int] = [raw[0]]
    for a, b in zip(raw, raw[1:]):
        if b - a > max_chars:
            x = a
            while x + max_chars < b:
                x += max_chars
                cuts.append(x)
        cuts.append(b)
    return cuts


def _split_long(text: str, start: int, max_chars: int, overlap: int) -> list[tuple[str, int, int]]:
    """把一个超长段落按句子窗口切开，返回 (文本, 起, 止) 列表。

    窗口长度保证 ≤ max_chars；相邻窗口保留约 overlap 字重叠。
    """
    cuts = _make_cuts(text, max_chars)
    pieces: list[tuple[str, int, int]] = []
    i, n = 0, len(cuts)
    while i < n - 1:
        # 最远的合法右边界
        j = i + 1
        while j < n and cuts[j] - cuts[i] <= max_chars:
            j += 1
        end = j - 1
        pieces.append((text[cuts[i]:cuts[end]], start + cuts[i], start + cuts[end]))
        if end >= n - 1:
            break
        # 下一窗口起点：从 end 往前退到刚好 ≥ overlap 的边界（但不前进）
        k = end
        while k > i + 1 and cuts[end] - cuts[k] < overlap:
            k -= 1
        i = max(k, i + 1)
    return pieces


def chunk_doc(doc_id: str, text: str, max_chars: int | None = None,
              overlap: int | None = None, min_chars: int | None = None) -> list[Chunk]:
    """把一篇文档切成块（text 与原文偏移严格对应）。"""
    max_chars = max_chars or config.MAX_CHARS
    overlap = overlap if overlap is not None else config.OVERLAP_CHARS
    min_chars = min_chars if min_chars is not None else config.MIN_CHARS

    blocks = split_blocks(text)
    chunks: list[Chunk] = []
    heading_stack: list[tuple[int, str]] = []
    cur: list[tuple[str, int, int]] = []

    def flush() -> None:
        nonlocal cur
        if not cur:
            return
        s, e = cur[0][1], cur[-1][2]
        body = text[s:e]
        path = " > ".join(t for _, t in heading_stack) or "(无标题)"
        idx = len(chunks)
        chunks.append(Chunk(chunk_id=f"{doc_id}#{idx}", doc_id=doc_id, text=body,
                            char_start=s, char_end=e, heading_path=path, index_in_doc=idx))
        cur = []

    for b in blocks:
        if b.kind == "heading":
            flush()
            while heading_stack and heading_stack[-1][0] >= b.level:
                heading_stack.pop()
            heading_stack.append((b.level, b.text.lstrip("# ").strip()))
            cur.append((b.text, b.start, b.end))
            continue

        if b.end - b.start > max_chars:
            flush()
            for piece, ps, pe in _split_long(b.text, b.start, max_chars, overlap):
                if len(piece.strip()) < min_chars:
                    continue
                path = " > ".join(t for _, t in heading_stack) or "(无标题)"
                idx = len(chunks)
                chunks.append(Chunk(chunk_id=f"{doc_id}#{idx}", doc_id=doc_id,
                                    text=text[ps:pe], char_start=ps, char_end=pe,
                                    heading_path=path, index_in_doc=idx))
            continue

        cur_len = (cur[-1][2] - cur[0][1]) if cur else 0
        if cur and cur_len + (b.end - b.start) > max_chars:
            flush()
            cur.append((b.text, b.start, b.end))
            continue
        cur.append((b.text, b.start, b.end))

    flush()
    # 丢掉过短的孤块（纯标题块等）
    kept = [c for c in chunks if len(c.text.strip()) >= min_chars] if min_chars else chunks
    # 硬切保险：块间空行会让 span 超出 max_chars，这里保证没有任何块超过上限
    final: list[Chunk] = []
    for c in kept:
        if len(c.text) <= max_chars:
            final.append(c)
            continue
        for piece, ps, pe in _split_long(c.text, c.char_start, max_chars, overlap):
            if len(piece.strip()) < min_chars:
                continue
            final.append(Chunk(chunk_id=f"{doc_id}#{len(final)}", doc_id=doc_id,
                               text=text[ps:pe], char_start=ps, char_end=pe,
                               heading_path=c.heading_path, index_in_doc=len(final)))
    # 统一重新编号：过滤与硬切都会打乱序号，不重编会出现重复 chunk_id（Chroma 会直接报错）
    for i, c in enumerate(final):
        c.chunk_id = f"{doc_id}#{i}"
        c.index_in_doc = i
    return final


def chunk_all(docs, **kw) -> list[Chunk]:
    out: list[Chunk] = []
    for d in docs:
        out.extend(chunk_doc(d.doc_id, d.text, **kw))
    return out


if __name__ == "__main__":
    from corpus.loader import load_docs
    docs = load_docs()
    chs = chunk_all(docs)
    lens = [len(c.text) for c in chs]
    print(f"文档 {len(docs)} 篇 → 块 {len(chs)} 个｜平均 {sum(lens)//max(len(lens),1)} 字｜"
          f"最长 {max(lens)} 字｜最短 {min(lens)} 字")
    # 偏移自检：块的 text 必须等于原文切片
    bad = 0
    by_id = {d.doc_id: d.text for d in docs}
    for c in chs:
        if by_id[c.doc_id][c.char_start:c.char_end] != c.text:
            bad += 1
    print(f"偏移自检不符的块: {bad}")
