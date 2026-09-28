# -*- coding: utf-8 -*-
"""Day 6：用真实 URL 验证网页抓取 + 失败降级。

用法：.venv/Scripts/python.exe scripts_urltest.py
记录：真实成功/失败/方法/长度/警告，写到 logs/urltest_*.json —— 这是"抓取失败率"的第一个数据点。
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

# 已知可访问的正文页（前一轮网站连通性实测 200）+ 一个已知 403 的（验证降级）
URLS = [
    "https://www.woshipm.com/pmd/2595761.html",            # 文章页
    "https://www.promptingguide.ai/zh/introduction/basics",  # 文档页
    "https://36kr.com/",                                   # 首页
    "https://www.zhihu.com/",                              # 预期失败：403 反爬
]


def main() -> int:
    rows, t0 = [], time.time()
    for u in URLS:
        print(f"[{u[:50]}] … ", end="", flush=True)
        row = {"url": u}
        try:
            r = extract_from_url(u, timeout=25)
            row.update({"ok": True, "method": r["method"], "len": len(r["text"]),
                        "title": r["title"][:60], "warnings": r["warnings"]})
            print(f"OK method={r['method']} len={len(r['text'])} title={r['title'][:30]!r}")
        except ExtractionError as e:
            row.update({"ok": False, "error": str(e)})
            print(f"FAIL {str(e)[:60]}")
        rows.append(row)

    ok_n = sum(1 for r in rows if r["ok"])
    out = {
        "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "attempted": len(rows), "succeeded": ok_n,
        "失败率": round(1 - ok_n / len(rows), 3),
        "rows": rows, "note": "首轮真实 URL 抓取数据点；样本含一个故意失败的 403，失败率不代表真实场景",
    }
    dest = ROOT / "logs" / f"urltest_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n成功 {ok_n}/{len(rows)}，失败率 {out['失败率']}，明细: {dest}")
    return 0 if ok_n >= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
