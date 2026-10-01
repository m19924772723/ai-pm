# -*- coding: utf-8 -*-
"""生成含表格的 PDF（S14 评测样本的数据源）。

用法：.venv/Scripts/python.exe scripts/make_table_pdf.py
产物：data/sample_inputs/table_report.pdf
然后：用 scripts_pdftest.py 同款逻辑提取，核对文本与 build_evalset.py 的 TABLE_REPORT 一致。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TABLE_LINES = [
    ("指标", "8 月", "9 月", "环比"),
    ("新增用户", "4200", "5100", "+21.4%"),
    ("次周留存", "31%", "33%", "+2pp"),
    ("月收入", "18.6 万", "21.2 万", "+14.0%"),
    ("客服工单", "203", "187", "-7.9%"),
]

BODY = """一、核心指标

（见上方表格）

二、结论
1. 新增用户连续三个月增长，9 月达到 5100 人。
2. 次周留存提升 2 个百分点，主要来自新手引导改版。
3. 月收入突破 20 万，客单价保持稳定。
4. 客服工单下降，但高峰时段排队仍超 10 分钟，建议下季度扩编一名客服。

三、风险
- 10 月 15 日需完成合规备案，否则影响十一活动。
- 服务器迁移计划在 10 月 8 日执行，需提前通知全部商户。"""


def main() -> int:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    y = 60
    page.insert_text((50, y), "月度经营报告（2026 年 9 月）", fontname="china-s", fontsize=16)
    y += 36

    # 表头/表体用等宽空格排版，保持列对齐（提取时按行返回）
    col_w = [130, 70, 70, 80]
    for row in TABLE_LINES:
        x = 50
        for ci, cell in enumerate(row):
            page.insert_text((x, y), cell, fontname="china-s", fontsize=12)
            x += col_w[ci]
        y += 24

    y += 12
    for block in BODY.split("\n"):
        if not block.strip():
            y += 12
            continue
        page.insert_text((50, y), block, fontname="china-s", fontsize=12)
        y += 20

    out = ROOT / "data" / "sample_inputs" / "table_report.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    doc.close()

    # 立即提取并打印，供与 build_evalset.py 的常量核对
    from extractors.pdf import extract_from_pdf

    r = extract_from_pdf(str(out))
    print(f"已生成并于 {r['method']} 提取 {len(r['text'])} 字：{out.name}")
    print("---- 提取文本预览 ----")
    print(r["text"][:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())