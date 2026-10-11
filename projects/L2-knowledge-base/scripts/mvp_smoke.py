# -*- coding: utf-8 -*-
"""MVP 三功能联调自测（Day 19）：上传索引 → 问答 → 引用定位 → 拒答。

对每个用例：
1. 索引同步检查（对应 MVP 功能①索引状态：in_sync + 块数）
2. answer() 问答（功能②）→ 校验有引用/拒答
3. 引用定位：citations 的 quote 落在 docpath 文件偏移切片内（功能③）
4. 汇总输出 pass/fail + 写 logs/mvp_smoke.json

用法：python -m scripts.mvp_smoke
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.loader import load_docs  # noqa: E402
from index import store  # noqa: E402
from query import answer as qa  # noqa: E402
from query.docpath import resolve_doc_path  # noqa: E402

# (问题, 期望行为)  —— 期望：answer=必须给引用 / refuse=必须拒答
CASES = [
    {"q": "跨端点故障转移是做什么的？", "expect": "answer"},
    {"q": "L1 的幻觉率是多少？", "expect": "answer"},
    {"q": "分块策略为什么要保留字符偏移？", "expect": "answer"},
    {"q": "向量数据库用 Chroma 还是 FAISS？", "expect": "answer"},
    {"q": "今天中午吃什么好？", "expect": "refuse"},
    {"q": "如何写一篇 Nature 论文？", "expect": "refuse"},
]


def check_citation_located(c: dict, docs_by_id: dict) -> tuple[bool, str]:
    """校验引用能定位：doc 存在 + 偏移切片含 quote + 磁盘文件存在。"""
    doc = docs_by_id.get(c.get("doc_id", ""))
    if not doc:
        return False, f"doc {c.get('doc_id')} 不在语料"
    slice_ = doc.text[c.get("char_start", 0):c.get("char_end", 0)]
    if c.get("quote") not in slice_:
        return False, "quote 不在偏移切片内"
    p = resolve_doc_path(c.get("doc_id", ""), c.get("doc_id", ""))
    if p is None or not p.exists():
        return False, "docpath 解析不到文件"
    return True, ""


def main() -> int:
    t0 = time.time()
    docs = load_docs()
    docs_by_id = {d.doc_id: d for d in docs}

    # 功能① 索引同步
    man = store.read_manifest()
    in_sync = man.get("fingerprint") == "" or store.count() == man.get("chunks")
    sync_ok = store.count() == man.get("chunks")
    print(f"== MVP 功能① 索引 ==")
    print(f"  语料 {len(docs)} 篇 / 索引 {store.count()} 块 / 块数相符={sync_ok}")

    results = []
    for case in CASES:
        q = case["q"]
        expect = case["expect"]
        row = {"q": q, "expect": expect}
        t1 = time.time()
        a = qa.answer(q)
        row["elapsed_s"] = round(time.time() - t1, 1)
        row["unanswerable"] = a.unanswerable
        row["citations"] = len(a.citations)
        row["provider"] = a.provider
        row["fallback"] = a.fallback_from
        row["warnings"] = a.warnings

        if expect == "refuse":
            ok = a.unanswerable or qa._is_refusal(a)
            row["ok"] = ok
            label = "拒答" if ok else "未拒答"
        else:
            # 必须给出引用，且引用能定位
            loc_ok = True
            loc_msgs = []
            for c in a.citations:
                ok_c, msg = check_citation_located(c, docs_by_id)
                loc_ok = loc_ok and ok_c
                if not ok_c:
                    loc_msgs.append(msg)
            ok = a.citations and loc_ok
            row["ok"] = ok
            row["loc_msgs"] = loc_msgs[:3]
            label = f"引用{len(a.citations)}条+定位{'✓' if loc_ok else '✗'}" if a.citations else "无引用"
        results.append(row)

        head = (a.answer or "").replace("\n", " ")[:60]
        print(f"\n[{'✓' if row['ok'] else '✗'}] {q} → {label}")
        print(f"    耗时{row['elapsed_s']}s provider={a.provider} fallback={a.fallback_from or '无'}")
        if head and not row['unanswerable']:
            print(f"    答案: {head}")
        if row.get("warnings"):
            print(f"    warnings: {row['warnings'][:2]}")

    n_pass = sum(1 for r in results if r["ok"])
    dt = time.time() - t0
    print(f"\n=== MVP 联调自测: {n_pass}/{len(results)} 通过 · 总耗时 {dt:.0f}s ===")
    json.dump({"n_pass": n_pass, "n_total": len(results), "sync_ok": bool(sync_ok),
               "results": results, "elapsed_s": round(dt, 1)},
              open("logs/mvp_smoke.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())