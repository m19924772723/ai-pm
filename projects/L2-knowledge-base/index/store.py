# -*- coding: utf-8 -*-
"""向量库封装（Chroma）。

存什么：
- 向量：embedding
- 文本：chunk 原文（检索结果直接给用户看）
- 元数据：doc_id / char_start / char_end / heading_path / source
  —— char_start/char_end 是"引用定位到段落"的关键，界面用它高亮原文
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import config


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    text: str
    score: float           # 越小越相关（cosine 距离）
    char_start: int
    char_end: int
    heading_path: str
    source: str


def _client():
    import chromadb

    config.ensure_dirs()
    return chromadb.PersistentClient(path=str(config.INDEX_DIR))


def get_collection(create: bool = True):
    c = _client()
    if create:
        return c.get_or_create_collection(name=config.COLLECTION, metadata={"hnsw:space": "cosine"})
    return c.get_collection(name=config.COLLECTION)


def reset() -> None:
    """清空集合（重建索引用）。"""
    c = _client()
    try:
        c.delete_collection(name=config.COLLECTION)
    except Exception:
        pass


def upsert_chunks(chunks, vectors: list[list[float]], batch: int = 128) -> int:
    col = get_collection()
    total = 0
    for s in range(0, len(chunks), batch):
        part = chunks[s:s + batch]
        col.upsert(
            ids=[c.chunk_id for c in part],
            embeddings=vectors[s:s + batch],
            documents=[c.text for c in part],
            metadatas=[{
                "doc_id": c.doc_id,
                "char_start": c.char_start,
                "char_end": c.char_end,
                "heading_path": c.heading_path,
                "source": c.meta.get("source", ""),
            } for c in part],
        )
        total += len(part)
    return total


def write_manifest(info: dict) -> None:
    config.ensure_dirs()
    (config.INDEX_DIR / "manifest.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


def read_manifest() -> dict:
    p = config.INDEX_DIR / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def count() -> int:
    try:
        return get_collection(create=False).count()
    except Exception:
        return 0


def query(vector: list[float], k: int = 5) -> list[Hit]:
    col = get_collection(create=False)
    res = col.query(query_embeddings=[vector], n_results=k,
                    include=["documents", "metadatas", "distances"])
    hits: list[Hit] = []
    ids = (res.get("ids") or [[]])[0]
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    for i, cid in enumerate(ids):
        m = metas[i] or {}
        hits.append(Hit(chunk_id=cid, doc_id=m.get("doc_id", ""), text=docs[i],
                        score=float(dists[i]), char_start=int(m.get("char_start", 0)),
                        char_end=int(m.get("char_end", 0)),
                        heading_path=m.get("heading_path", ""), source=m.get("source", "")))
    return hits


if __name__ == "__main__":
    print("集合内块数:", count())
    print("manifest:", json.dumps(read_manifest(), ensure_ascii=False)[:300])
