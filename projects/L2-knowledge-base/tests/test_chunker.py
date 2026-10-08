# -*- coding: utf-8 -*-
"""分块与加载的离线单测（不联网、不花 embedding 费用）。

三条硬不变量：
1. 每个块的 text 必须等于原文 text[char_start:char_end]（引用高亮的前提）
2. 没有块超过 max_chars
3. 正文不被丢字（覆盖率：正文每个字符至少出现在一个块里）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from corpus.chunker import _split_long, chunk_doc, split_blocks  # noqa: E402
from corpus.loader import corpus_fingerprint, load_docs  # noqa: E402


DOC = """# 标题一

第一段内容，讲的是分块策略要保留字符偏移。

## 小节 A

小节 A 的正文。这里有一句话。还有第二句话。

## 小节 B

小节 B 的正文。
"""


def test_offsets_exact():
    for c in chunk_doc("t.md", DOC, max_chars=80, overlap=10):
        assert DOC[c.char_start:c.char_end] == c.text, c.chunk_id


def test_no_chunk_exceeds_max():
    long = "这是一个很长的句子" * 60
    chs = chunk_doc("t.md", "# T\n\n" + long, max_chars=100, overlap=10)
    assert chs
    assert max(len(c.text) for c in chs) <= 100


def test_body_not_lost_when_nothing_filtered():
    """分块窗口不丢正文：min_chars=0 时，丢失的只能是空白（块间空行）。"""
    body = "句子一。" * 100
    doc = "# T\n\n" + body
    chs = chunk_doc("t.md", doc, max_chars=64, overlap=8, min_chars=0)
    covered = set()
    for c in chs:
        covered.update(range(c.char_start, c.char_end))
    missing = [i for i in range(len(doc)) if i not in covered]
    assert all(doc[i].isspace() for i in missing), \
        f"丢了非空白内容: {[doc[i] for i in missing][:20]}"
    assert all(i in covered for i, ch in enumerate(doc) if not ch.isspace()), "正文必须全覆盖"


def test_short_blocks_dropped_by_design():
    """已知边界：低于 min_chars 的块会被丢弃（标题行、极短片段）。

    这是有意的——标题单独作为检索单元没有价值，且 heading_path 已保留层级信息。
    """
    body = "句子一。" * 100
    doc = "# 短标题\n\n" + body
    chs = chunk_doc("t.md", doc, max_chars=64, overlap=8, min_chars=40)
    covered = set()
    for c in chs:
        covered.update(range(c.char_start, c.char_end))
    lost = [i for i in range(len(doc)) if i not in covered]
    lost_text = doc[min(lost):max(lost) + 1] if lost else ""
    assert lost, "应当有被丢弃的短块"
    assert "短标题" in lost_text, "被丢的应只是短标题这类碎片"


def test_heading_path_recorded():
    chs = chunk_doc("t.md", DOC, max_chars=200, overlap=10, min_chars=10)
    paths = {c.heading_path for c in chs}
    assert any("标题一" in p for p in paths), paths
    assert any("小节 A" in p for p in paths), paths


def test_short_chunks_filtered():
    chs = chunk_doc("t.md", DOC, max_chars=200, overlap=10, min_chars=30)
    assert all(len(c.text.strip()) >= 30 for c in chs)


def test_overlap_applied_in_long_split():
    text = "".join(f"第{i}句内容。" for i in range(60))
    pieces = _split_long(text, 0, 60, 20)
    assert len(pieces) > 2
    # 相邻窗口应有重叠
    assert pieces[1][1] < pieces[0][2]


def test_split_blocks_finds_headings():
    blocks = split_blocks(DOC)
    kinds = [b.kind for b in blocks]
    assert kinds.count("heading") == 3
    assert "para" in kinds


def test_chunk_ids_unique_within_doc():
    chs = chunk_doc("t.md", DOC, max_chars=80, overlap=10)
    ids = [c.chunk_id for c in chs]
    assert len(ids) == len(set(ids))


# ---------- loader ----------

def test_load_docs_real_corpus():
    docs = load_docs()
    assert len(docs) >= 20, "真实语料应至少有 20 篇"
    assert all(d.text.strip() for d in docs)
    assert all(d.sha1 for d in docs)


def test_fingerprint_stable_and_sensitive():
    docs = load_docs()
    fp1 = corpus_fingerprint(docs)
    fp2 = corpus_fingerprint(load_docs())
    assert fp1 == fp2, "同一语料指纹必须稳定"
    mutated = [type(docs[0])(doc_id="x", path=docs[0].path, source="s", text="改过的内容", sha1="deadbeef")]
    assert corpus_fingerprint(mutated) != fp1


def test_config_params_sane():
    assert 0 < config.OVERLAP_CHARS < config.MAX_CHARS
    assert config.MIN_CHARS < config.MAX_CHARS
