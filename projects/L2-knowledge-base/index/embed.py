# -*- coding: utf-8 -*-
"""Embedding 客户端：调中转端点，带磁盘缓存。

为什么要缓存：
1. 重建索引时同样的文本不重复付费（语料 13 万字，全量重算一次不便宜）
2. 评测可复现——缓存命中时结果与上次完全一致
缓存键 = sha1(模型名 + 文本)，改模型/改文本自动失效。
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import httpx

import config


class EmbedError(RuntimeError):
    pass


def _cache_path(text: str) -> Path:
    key = hashlib.sha1(f"{config.EMBED_MODEL}\x00{text}".encode("utf-8")).hexdigest()
    return config.CACHE_DIR / f"{key}.json"


def embed_texts(texts: list[str], use_cache: bool = True, batch: int | None = None) -> list[list[float]]:
    """批量取向量；命中缓存的不发请求。"""
    batch = batch or config.EMBED_BATCH
    config.ensure_dirs()
    key = os.environ.get(config.EMBED_KEY_ENV)
    if not key:
        raise EmbedError(f"缺少环境变量 {config.EMBED_KEY_ENV}")

    out: list[list[float] | None] = [None] * len(texts)
    pending: list[tuple[int, str]] = []
    for i, t in enumerate(texts):
        cp = _cache_path(t)
        if use_cache and cp.exists():
            try:
                out[i] = json.loads(cp.read_text(encoding="utf-8"))
                continue
            except json.JSONDecodeError:
                pass
        pending.append((i, t))

    for s in range(0, len(pending), batch):
        chunk = pending[s:s + batch]
        payload = {"model": config.EMBED_MODEL, "input": [t for _, t in chunk]}
        try:
            r = httpx.post(f"{config.EMBED_BASE_URL}/embeddings",
                           headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                           json=payload, timeout=config.EMBED_TIMEOUT)
        except httpx.HTTPError as e:
            raise EmbedError(f"网络错误: {type(e).__name__}") from None
        if r.status_code != 200:
            raise EmbedError(f"HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        vecs = [item["embedding"] for item in data.get("data", [])]
        if len(vecs) != len(chunk):
            raise EmbedError(f"返回条数不符：请求 {len(chunk)} 条，返回 {len(vecs)} 条")
        for (idx, txt), v in zip(chunk, vecs):
            out[idx] = v
            if use_cache:
                _cache_path(txt).write_text(json.dumps(v), encoding="utf-8")

    if any(v is None for v in out):
        raise EmbedError("有文本未取到向量")
    return [v for v in out if v is not None]


def embed_one(text: str, use_cache: bool = True) -> list[float]:
    return embed_texts([text], use_cache=use_cache)[0]


def cache_stats() -> dict:
    files = list(config.CACHE_DIR.glob("*.json")) if config.CACHE_DIR.exists() else []
    bytes_ = sum(f.stat().st_size for f in files)
    return {"cached_texts": len(files), "cache_mb": round(bytes_ / 1024 / 1024, 2)}


if __name__ == "__main__":
    print("端点:", config.EMBED_BASE_URL, "模型:", config.EMBED_MODEL)
    v = embed_one("分块策略要保留字符偏移，才能做引用定位。")
    print(f"维度 {len(v)}｜前 5 维 {[round(x,4) for x in v[:5]]}")
    print("缓存:", cache_stats())
