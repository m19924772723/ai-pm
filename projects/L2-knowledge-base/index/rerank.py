# -*- coding: utf-8 -*-
"""重排器：bce-reranker-base_v1（本地 cross-encoder，零 API 成本）。

为什么需要（Day 22 定位）：
- nemotron dense 对中文区分弱 + 每日日志词面高度重叠 → 稠密/词面两榜 top 都被日志块挤占，
  RRF 融合后 top-5 平均只有 1.5 块相关（上下文相关性 30%，目标 60%）。
- 把候选池交给 cross-encoder 重排 = 第三个、更强的相关性信号：直接判 (question, chunk)
  语义相关度，不再依赖两榜各自排名的质量。

约束：
- 模型目录缺失/加载失败 → available()=False，检索端回退纯 RRF（行为同前，不崩）。
- 分数磁盘缓存（键 = sha1(query + text)），同一评测/问答重复跑不重复推理。
- 推理发生在 CPU（fp16），单对约 1s——只有候选池（默认 40 块/榜）要过模型。
"""
from __future__ import annotations

import hashlib
import json
import threading

import config

_model = None
_lock = threading.Lock()
_cache: dict | None = None
_CACHE_VERSION = "1"


def _load_cache() -> None:
    global _cache
    if _cache is None:
        _cache = {}
        p = Path(config.RERANK_CACHE)
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if d.get("version") == _CACHE_VERSION:
                    _cache = d.get("scores", {})
            except Exception:
                _cache = {}


def _save_cache() -> None:
    try:
        Path(config.RERANK_CACHE).write_text(
            json.dumps({"version": _CACHE_VERSION, "scores": _cache}, ensure_ascii=False),
            encoding="utf-8")
    except Exception:
        pass


def available() -> bool:
    """模型目录可用的静态判断（不加载模型，加载失败由调用方捕获回退）。"""
    return bool(config.RERANK_MODEL_DIR)


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from FlagEmbedding import FlagReranker
                _model = FlagReranker(config.RERANK_MODEL_DIR, use_fp16=True, device="cpu")
    return _model


def rerank(question: str, texts: list[str]) -> list[float]:
    """(question, chunk) 交叉编码分数列表（越大越相关）。缓存命中跳过推理。"""
    _load_cache()
    keys: list[str] = []
    missing: list[int] = []
    out = [0.0] * len(texts)
    for i, t in enumerate(texts):
        key = hashlib.sha1((question + "" + t[:500]).encode("utf-8")).hexdigest()
        keys.append(key)
        if key in _cache:
            out[i] = _cache[key]
        else:
            missing.append(i)
    if missing:
        model = _get_model()
        pairs = [[question, texts[i][:500]] for i in missing]
        scores = model.compute_score(pairs, batch_size=64, normalize=True)
        for j, i in enumerate(missing):
            out[i] = float(scores[j])
            _cache[keys[i]] = float(scores[j])
        _save_cache()
    return out
