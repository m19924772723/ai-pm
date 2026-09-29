# -*- coding: utf-8 -*-
"""Day 7：三模板接线端到端验证。

同一篇真实文章（woshipm · 俞军产品价值公式）分别跑
摘要 / 待办 / 归档 三个模板，验证：抓取 → 结构化 → Schema → Markdown 渲染全链路。

用法：.venv/Scripts/python.exe scripts_demo.py
产物：logs/demo_<ts>.json（结构化结果 + 指标）、logs/demo_markdown_<ts>.md（三个模板的 Markdown 渲染）
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extractors.web import ExtractionError, extract_from_url  # noqa: E402
from pipeline import MAX_CHARS, structure, to_markdown  # noqa: E402

URL = "https://www.woshipm.com/pmd/2595761.html"  # 已验证可访问的真实文章页


def main() -> int:
    # 1) 抓取
    print(f"抓取: {URL}")
    art = extract_from_url(URL, timeout=30)
    text = art["text"]
    print(f"  方法={art['method']} 标题={art['title'][:40]!r} 正文={len(text)} 字")
    if len(text) > MAX_CHARS:
        print(f"  超长截断到 {MAX_CHARS}")
        text = text[:MAX_CHARS]

    # 2) 三个模板接线
    rows, md_blocks = [], []
    for tpl in ("summary", "todos", "archive"):
        print(f"[{tpl}] 调用中 … ", end="", flush=True)
        t0 = time.time()
        r = structure(text, template=tpl)
        dt = time.time() - t0
        if r.ok:
            print(f"OK {dt:.1f}s schema={r.schema_ok} ev_issues={len(r.evidence_issues)}")
            md = to_markdown(r)
            rows.append({
                "template": tpl, "ok": True, "elapsed_s": round(dt, 2),
                "finish_reason": r.finish_reason, "truncated": r.truncated,
                "schema_ok": r.schema_ok, "schema_errors": r.schema_errors[:3],
                "evidence_issues": r.evidence_issues[:5], "usage": r.usage,
                "data": r.data, "raw": r.raw[:3000],
            })
            md_blocks.append(f"# 模板：{tpl}\n\n{md}\n\n---\n")
        else:
            print(f"FAIL {r.error[:80]}")
            rows.append({"template": tpl, "ok": False, "error": r.error, "raw": r.raw[:500]})

    # 3) 存证据
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = ROOT / "logs" / f"demo_{stamp}.json"
    out.write_text(json.dumps({
        "run_at": str(datetime.now()), "url": URL, "title": art["title"],
        "article_len": len(text), "rows": rows,
        "note": "同一篇文章三种模板的全链路验证；sample 只有 1 篇，仅验证链路可用，不构成效果结论",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = ROOT / "logs" / f"demo_markdown_{stamp}.md"
    md_path.write_text("\n".join(md_blocks), encoding="utf-8")

    # 4) 保存文章正文供 woshipm 精读材料用
    (ROOT / "data" / "sample_inputs" / "woshipm_产品价值公式.txt").write_text(
        f"标题: {art['title']}\nURL: {URL}\n\n{text}", encoding="utf-8")

    n_ok = sum(1 for r in rows if r["ok"])
    print(f"\n三模板接线: {n_ok}/3 成功 | 证据: {out.name}")
    print(f"Markdown 渲染: {md_path.name}")
    return 0 if n_ok == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())