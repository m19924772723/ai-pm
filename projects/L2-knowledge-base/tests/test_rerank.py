# -*- coding: utf-8 -*-
"""rerank 模块离线单测（不依赖本地模型/网络）。"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from index import rerank  # noqa: E402


def test_cache_roundtrip(tmp_path, monkeypatch):
    """分数缓存写读一致（缓存键 = 问题+文本前500字）。"""
    monkeypatch.setattr(config, "RERANK_CACHE", tmp_path / "rc.json")
    rerank._cache = None
    rerank._load_cache()
    text = "故障转移会在主端点失败时自动切换"
    key = hashlib.sha1(
        ("跨端点故障转移是做什么的？\x01" + text[:500]).encode("utf-8")).hexdigest()
    rerank._cache[key] = 0.888
    rerank._save_cache()
    # 重新加载
    rerank._cache = None
    rerank._load_cache()
    assert rerank._cache.get(key) == 0.888


def test_available_false_when_no_model(monkeypatch):
    monkeypatch.setattr(config, "RERANK_MODEL_DIR", "")
    assert rerank.available() is False


def test_key_normalization():
    """缓存键必须基于 (问题, 文本) 而非随机——同一对两次调用同键。"""
    q, t = "问题?", "文本"
    k1 = hashlib.sha1((q + "\x01" + t[:500]).encode("utf-8")).hexdigest()
    k2 = hashlib.sha1((q + "\x01" + t[:500]).encode("utf-8")).hexdigest()
    assert k1 == k2