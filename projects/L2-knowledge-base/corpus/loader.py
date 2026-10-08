# -*- coding: utf-8 -*-
"""语料加载：把配置里的来源 glob 展开成文档列表。

设计要点：
- **不复制文件**，直接读原路径（语料就是工作区真实文档，改了立刻能重建索引）
- 记录每个文档的 sha1，用来判断"是否需要重建索引"
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import config


@dataclass
class Doc:
    doc_id: str          # 相对 WORKSPACE 的路径（稳定 id）
    path: Path           # 绝对路径
    source: str          # 来源组名（如 ai_pm/docs）
    text: str            # 原文
    sha1: str            # 内容指纹

    @property
    def chars(self) -> int:
        return len(self.text)


def _doc_id(path: Path) -> str:
    try:
        return path.relative_to(config.CORPUS_ROOT).as_posix()
    except ValueError:
        return path.name


def load_docs(sources: list[dict] | None = None, exts: tuple[str, ...] = (".md", ".txt")) -> list[Doc]:
    """按配置加载语料文档，按 doc_id 排序保证可复现。"""
    srcs = sources if sources is not None else config.CORPUS_SOURCES
    docs: dict[str, Doc] = {}
    for s in srcs:
        for p in sorted(config.CORPUS_ROOT.glob(s["glob"])):
            if p.suffix.lower() not in exts or not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if len(text.strip()) < config.MIN_CHARS:
                continue
            did = _doc_id(p)
            docs[did] = Doc(doc_id=did, path=p, source=s["name"], text=text,
                            sha1=hashlib.sha1(text.encode("utf-8")).hexdigest())
    return [docs[k] for k in sorted(docs)]


def corpus_fingerprint(docs: list[Doc]) -> str:
    """整个语料的指纹：任何文档变化都会变，用来判断是否需要重建索引。"""
    h = hashlib.sha1()
    for d in docs:
        h.update(d.doc_id.encode())
        h.update(d.sha1.encode())
    return h.hexdigest()


if __name__ == "__main__":
    ds = load_docs()
    print(f"文档数: {len(ds)}｜总字符: {sum(d.chars for d in ds):,}｜指纹: {corpus_fingerprint(ds)[:12]}")
    for d in ds[:5]:
        print(f"  {d.doc_id}  {d.chars} 字  [{d.source}]")
