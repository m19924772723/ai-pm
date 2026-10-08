# -*- coding: utf-8 -*-
"""诊断：embedding 质量是否可用。

现象：检索距离全挤在一起（0.30 上下），Top-1 明显不相关。
可能原因：
  A. 向量退化（不同文本的向量几乎相同）
  B. 该模型需要 input_type / 指令前缀（query vs document）
  C. 分词或语言问题（中文支持差）
  D. 单纯的 top-k 排序问题（阈值/距离度量）

用法：python -m scripts.diagnose_embed
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index import embed, store  # noqa: E402


def cos(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb + 1e-12)


def main() -> int:
    print("=== A. 向量是否退化（不同文本的余弦相似度）===")
    texts = [
        "分块策略要保留字符偏移，才能做引用定位",
        "今天中午吃西红柿炒鸡蛋和米饭",
        "跨端点故障转移解决依赖失效问题",
        "L1 的幻觉率是 1.05%",
    ]
    vecs = embed.embed_texts(texts, use_cache=False)
    print(f"维度 {len(vecs[0])}｜各向量 L2 范数: {[round(math.sqrt(sum(x*x for x in v)),3) for v in vecs]}")
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            print(f"  cos(文本{i},文本{j}) = {cos(vecs[i], vecs[j]):+.4f}")
    print("  → 若任意两段无关文本的 cos > 0.9，说明向量退化，检索不可用\n")

    print("=== B. 查询向量 vs 文档向量（同一句话自比）===")
    q = "分块策略要保留字符偏移"
    vq = embed.embed_one(q, use_cache=False)
    vd = embed.embed_one("分块策略要保留字符偏移，才能做引用定位", use_cache=False)
    vother = embed.embed_one("今天中午吃西红柿炒鸡蛋", use_cache=False)
    print(f"  cos(查询, 相关文本) = {cos(vq, vd):+.4f}")
    print(f"  cos(查询, 无关文本) = {cos(vq, vother):+.4f}")
    print("  → 两者差距应明显（>0.1）\n")

    print("=== C. 索引里实际存的向量是否同源（取前 3 块自比）===")
    col = store.get_collection(create=False)
    got = col.get(limit=3, include=["embeddings", "documents"])
    embs = got.get("embeddings")
    if embs is not None and len(embs) >= 2:
        print(f"  块间 cos: {cos(list(embs[0]), list(embs[1])):+.4f}")
        print(f"  块文本: {str(got['documents'][0])[:40]!r} / {str(got['documents'][1])[:40]!r}")
    else:
        print("  取不到向量")

    print("\n=== D. 关键词基线对比（同问题，谁排第一）===")
    for qq in ["跨端点故障转移", "幻觉率"]:
        hits = store.query(embed.embed_one(qq, use_cache=False), k=3)
        # 简单关键词得分：块文本里出现查询字的比例
        def kw_score(text: str, query: str) -> float:
            qs = set(query)
            ts = set(text)
            return len(qs & ts) / max(len(qs), 1)
        print(f"  问题『{qq}』")
        for i, h in enumerate(hits, 1):
            print(f"    向量[{i}] d={h.score:.4f}｜kw={kw_score(h.text, qq):.2f}｜{h.doc_id}｜{h.text[:36]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
