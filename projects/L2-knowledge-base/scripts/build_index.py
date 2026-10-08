# -*- coding: utf-8 -*-
"""构建索引：语料 → 分块 → 向量 → Chroma。

用法：python -m scripts.build_index            # 增量（缓存 embedding，最快）
      python -m scripts.build_index --reset    # 清空重建
      python -m scripts.build_index --check    # 只检查索引是否与语料同步，不重建
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from corpus.chunker import chunk_all
from corpus.loader import corpus_fingerprint, load_docs
from index import embed, store


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="清空重建")
    ap.add_argument("--check", action="store_true", help="只对比语料指纹与索引状态")
    ap.add_argument("--no-cache", action="store_true", help="不使用 embedding 缓存")
    args = ap.parse_args()

    config.ensure_dirs()
    docs = load_docs()
    fp = corpus_fingerprint(docs)
    man = store.read_manifest()

    if args.check:
        synced = man.get("fingerprint") == fp and store.count() == man.get("chunks")
        print(json.dumps({
            "documents": len(docs), "chunks_in_manifest": man.get("chunks"),
            "chunks_in_index": store.count(), "fingerprint": fp[:12],
            "manifest_fingerprint": str(man.get("fingerprint", ""))[:12],
            "in_sync": bool(synced),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.reset:
        store.reset()

    chunks = chunk_all(docs)
    for c in chunks:
        c.meta["source"] = next((d.source for d in docs if d.doc_id == c.doc_id), "")

    t0 = time.time()
    print(f"语料 {len(docs)} 篇 / {sum(d.chars for d in docs):,} 字 → 分块 {len(chunks)} 个")
    print(f"取向量中（batch={config.EMBED_BATCH}）…")
    vectors = embed.embed_texts([c.text for c in chunks], use_cache=not args.no_cache)
    t_embed = time.time() - t0

    n = store.upsert_chunks(chunks, vectors)
    info = {
        "built_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "documents": len(docs), "chunks": n, "chars": sum(d.chars for d in docs),
        "fingerprint": fp,
        "embed": {"base_url": config.EMBED_BASE_URL, "model": config.EMBED_MODEL,
                  "dim": len(vectors[0]) if vectors else 0},
        "chunk_params": {"max_chars": config.MAX_CHARS, "overlap": config.OVERLAP_CHARS,
                         "min_chars": config.MIN_CHARS},
        "cache": embed.cache_stats(),
    }
    store.write_manifest(info)

    print(f"写入 {n} 块｜embedding 耗时 {t_embed:.1f}s｜总耗时 {time.time()-t0:.1f}s")
    print(f"索引目录: {config.INDEX_DIR}")
    print(json.dumps(info, ensure_ascii=False, indent=2)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
