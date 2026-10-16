# -*- coding: utf-8 -*-
"""检索器：混合检索 = 稠密向量排序 + 中文二元组 BM25 排序，RRF 融合。

为什么做混合（决策记录，面试要讲）：
- 实测 nemotron-3-embed-1b（中转站唯一可用 embedding）对中文语料区分不足：
  501 个块的相关度全挤在 0.69~0.82，ASCII 框线块对任何查询都最相关
- 稠密 alone 会漏掉"查询词原样出现"的块（『跨端点故障转移』命中 log/2026-10-06.md 却排第 4）
- BM25（字符二元组，免中文分词器依赖）补上词面匹配；RRF 融合两个排序，无需调权重
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import config
from index import embed, rerank as rerank_mod, store

# ---------- 词面 token：中文二元组 + 英文小写词 ----------

_RE_TOKEN = re.compile(r"[0-9A-Za-z_]+|[\u4e00-\u9fff]+")


def lexical_tokens(text: str) -> list[str]:
    """『跨端点故障转移』→ [跨端, 端点, 故障, 障转, 转移]；'streamlit' → [streamlit]。

    ASCII 线框图（─│┌…）一个 token 都产生不了 → 天然免疫"图块污染"。
    """
    grams: list[str] = []
    for word in _RE_TOKEN.findall(text):
        if word.isascii():
            grams.append(word.lower())
        elif len(word) >= 2:
            for i in range(len(word) - 1):
                grams.append(word[i:i + 2])
        else:
            grams.append(word)
    return grams


# ---------- BM25 ----------

@dataclass
class BM25:
    k1: float = 1.5
    b: float = 0.75
    n: int = 0
    avgdl: float = 0.0
    df: dict[str, int] = field(default_factory=dict)
    chunk_grams: list[list[str]] = field(default_factory=list)
    _denom: list[float] = field(default_factory=list)  # k1*((1-b)+b*dl/avgdl) 每块预计算

    @classmethod
    def build(cls, texts: list[str], k1: float = 1.5, b: float = 0.75) -> "BM25":
        bm = cls(k1=k1, b=b)
        bm.chunk_grams = [lexical_tokens(t) for t in texts]
        for grams in bm.chunk_grams:
            for g in set(grams):
                bm.df[g] = bm.df.get(g, 0) + 1
        bm.n = len(texts)
        bm.avgdl = sum(len(g) for g in bm.chunk_grams) / max(bm.n, 1)
        bm._denom = [k1 * ((1 - b) + b * len(g) / bm.avgdl) for g in bm.chunk_grams]
        return bm

    def score_all(self, query: str) -> list[float]:
        """每块一个 BM25 得分（未命中 = 0）。"""
        qt = lexical_tokens(query)
        if not qt:
            return [0.0] * self.n
        scores = [0.0] * self.n
        N = self.n
        for t in set(qt):
            df = self.df.get(t, 0)
            if not df:
                continue
            idf = math.log((N + 1) / (df + 0.5))
            for i, grams in enumerate(self.chunk_grams):
                tf = grams.count(t)
                if tf:
                    scores[i] += idf * (tf * (self.k1 + 1)) / (tf + self._denom[i])
        return scores


# ---------- RRF 融合 ----------

def rrf_fuse(ranked: list[list[int]], k: int = 60) -> list[int]:
    """多个排序（块序号列表）→ 一个融合排序（Reciprocal Rank Fusion）。"""
    acc: dict[int, float] = {}
    for ranks in ranked:
        for pos, idx_ in enumerate(ranks):
            acc[idx_] = acc.get(idx_, 0.0) + 1.0 / (k + pos + 1)
    return [i for i, _ in sorted(acc.items(), key=lambda kv: kv[1], reverse=True)]


# ---------- 完整检索 ----------

def search_all(question: str, k: int = 5, dense: bool = True, lexical: bool = True,
            rerank: bool = True, alt_queries: list[str] | None = None,
            lex_floor: int = 0) -> list[store.Hit]:
    """embedding 排序 + BM25 排序 → 候选池 →（可选）cross-encoder 重排 / RRF 融合 → 还原成 Hit（带原文偏移）。

    Day 25 新增参数：
    - alt_queries：查询改写提供的并集候选（含原查询本身时自动去重）。
      每个查询贡献 dense top-POOl + lexical top-POOL 进候选池；重排/词面保底只按
      **原始问题** 打分排序（用户意图为准，改写只负责把池撑大——对齐 woshipm
      《RAG 生产调优 12 策略》的「保留原查询，防改写带偏」）。
    - lex_floor：词面保底条数。重排后的 top-k 里强制并入 lexical top-lex_floor 的块
      （治操作命令题：cross-encoder 对 build_index 这类代码命令块压分，Day 14 记录，
      log/2026-10-08 的 build_index 块 BM25 rank=1 却掉出 top-5）。
      实现：按重排分从尾部把「词面强命中但重排低分」的块补进去，块数仍 = k。
    """
    # corpus 元数据一次取全（Day 18 教训：documents+metadatas 必须同一次 get）
    col = store.get_collection(create=False)
    allg = col.get(include=["documents", "metadatas"])
    texts: list[str] = allg["documents"]
    metas: list = allg["metadatas"]
    n = len(texts)

    queries: list[str] = [question]
    if alt_queries:
        for q in alt_queries:
            if q and q not in queries:
                queries.append(q)

    # dense 候选与全量排名（每个查询一份）
    pos_of: dict[tuple, int] = {}
    for i, m in enumerate(metas):
        pos_of.setdefault((m.get("doc_id", ""), int(m.get("char_start", 0))), i)

    per_query: list[dict] = []
    lex_ranks_primary = None
    for qi, q in enumerate(queries):
        qinfo: dict = {}
        if dense:
            hits = store.query(embed.embed_one(q), k=n)
            qinfo["dense_order"] = [pos_of[(h.doc_id, h.char_start)] for h in hits]
        if lexical:
            bm = BM25.build(texts)
            scores = bm.score_all(q)
            qinfo["lex_rank_all"] = sorted(range(n), key=lambda i: scores[i], reverse=True)
        if qi == 0:
            lex_ranks_primary = qinfo.get("lex_rank_all")
        per_query.append(qinfo)

    # 候选池 = 各查询 (dense top-POOL ∪ lexical top-POOL) 的并集
    pool = config.RERANK_POOL
    cand = []
    for qinfo in per_query:
        if qinfo.get("dense_order"):
            cand += qinfo["dense_order"][:pool]
        if qinfo.get("lex_rank_all"):
            cand += qinfo["lex_rank_all"][:pool]
    cand = list(dict.fromkeys(cand))[:pool * 2 * len(queries) + 64]
    cand_set = set(cand)

    use_rerank = False
    if rerank:
        try:
            use_rerank = rerank_mod.available()
            if use_rerank:
                sc = rerank_mod.rerank(question, [texts[i] for i in cand])
                cand = [cand[j] for j in
                        sorted(range(len(cand)), key=lambda j: sc[j], reverse=True)]
                # 词面保底：把 lexical top-lex_floor（原始查询）强制并入 final top-k
                # （从尾部替换“重排最不认可”的块，保持数量 = k）
                if lex_floor > 0 and lex_ranks_primary is not None:
                    final = cand[:k]
                    for i in lex_ranks_primary[:lex_floor]:
                        if i not in final:
                            final[-1] = i
                            break
                    cand = final
                else:
                    cand = cand[:k]
        except Exception:
            use_rerank = False  # 模型加载/推理失败 → 回退 RRF，不中断检索

    if not use_rerank:
        # RRF 在候选池内重算（多查询时对每个查询的榜内名次求和）
        def _rank_within(full: list[int]) -> dict[int, int]:
            r, pos = {}, 0
            for idx_ in full:
                if idx_ in cand_set:
                    r[idx_] = pos
                    pos += 1
            return r

        acc: dict[int, float] = {}
        for qinfo in per_query:
            dr = _rank_within(qinfo.get("dense_order") or [])
            lr = _rank_within(qinfo.get("lex_rank_all") or [])
            for idx_ in cand:
                acc[idx_] = acc.get(idx_, 0.0) +                     (1.0 / (60 + dr.get(idx_, 10 ** 9) + 1) +
                     1.0 / (60 + lr.get(idx_, 10 ** 9) + 1))
        cand = sorted(cand, key=lambda i: acc.get(i, 0.0), reverse=True)[:k]

    hits: list[store.Hit] = []
    for idx_ in cand:
        m = metas[idx_]
        hits.append(store.Hit(
            chunk_id="", doc_id=m.get("doc_id", ""), text=texts[idx_], score=0.0,
            char_start=int(m.get("char_start", 0)), char_end=int(m.get("char_end", 0)),
            heading_path=m.get("heading_path", ""), source=m.get("source", "")))
    return hits



if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
    q = " ".join(sys.argv[1:]) or "跨端点故障转移"
    for i, h in enumerate(search_all(q, k=5), 1):
        print(f"[{i}] {h.doc_id}｜{h.heading_path[:40]}")
        print(f"     {h.text[:60]!r}")