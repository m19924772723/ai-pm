# -*- coding: utf-8 -*-
"""rerank 速度基准：fp16 vs fp32，40 对推理耗时（找慢的根因）。"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config

pairs = [[f"跨端点故障转移是做什么的第{i}个变体？", f"故障转移会在主端点失败时自动切换，记录 fallback_from，第 {i} 段相关内容。"] for i in range(40)]


def bench(fp16: bool, batch: int, n: int = 40) -> float:
    from FlagEmbedding import FlagReranker
    m = FlagReranker(config.RERANK_MODEL_DIR, use_fp16=fp16, device="cpu")
    t0 = time.time()
    m.compute_score(pairs[:n], batch_size=batch, normalize=True)
    dt = time.time() - t0
    return dt


if __name__ == "__main__":
    for fp16 in (True, False):
        for batch in (64, 16):
            try:
                dt = bench(fp16, batch)
                print(f"fp16={fp16} batch={batch}: {dt:.1f}s for 40 pairs  ({dt/40*1000:.0f} ms/pair)")
            except Exception as e:
                print(f"fp16={fp16} batch={batch}: FAIL {str(e)[:100]}")