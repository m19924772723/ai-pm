# -*- coding: utf-8 -*-
"""Day 6：PDF 提取验证（真实文件，非 mock）。

生成两份测试 PDF：
1. 中文文本 PDF —— 验证正常提取路径
2. 纯图片 PDF（扫描件模拟）—— 验证"无文本层"报错路径

用法：.venv/Scripts/python.exe scripts_pdftest.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extractors.pdf import ExtractionError, extract_from_pdf  # noqa: E402

DATA = ROOT / "data" / "sample_inputs"


def make_text_pdf(path: Path) -> None:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    text = ("L1 项目 PDF 提取测试文档。\n"
            "本季度用户留存下滑，王五需要在 9 月 30 日前完成流失用户访谈，至少覆盖 10 人。\n"
            "赵六负责在下周五前给出一版缩短 30% 的引导方案。\n"
            "测试数据：接口平均延迟从 1.2 秒降到 0.8 秒。")
    # fontname="china-s" 是 PyMuPDF 内置简体中文字体；insert_text 会正确写文本层
    page.insert_text((50, 80), text, fontname="china-s", fontsize=14)
    doc.save(path)


def make_image_pdf(path: Path) -> None:
    """纯图片 PDF：用一张空白图填充，模拟扫描件（无文本层）。"""
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 400, 500), 0)
    pix.clear_with(255)  # 空白白图
    page.insert_image(page.rect, pixmap=pix)
    doc.save(path)


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    text_pdf = DATA / "test_text_zh.pdf"
    image_pdf = DATA / "test_scan_sim.pdf"
    make_text_pdf(text_pdf)
    make_image_pdf(image_pdf)
    print(f"已生成: {text_pdf.name} / {image_pdf.name}")

    rows = []
    # 正常路径
    r = extract_from_pdf(str(text_pdf))
    print(f"[文本PDF] OK pages={r['pages']} len={len(r['text'])} title={r['title']!r}")
    print(f"  文本开头: {r['text'][:60]!r}")
    rows.append({"case": "text_pdf", "ok": True, "pages": r["pages"], "len": len(r["text"]),
                 "title": r["title"], "warnings": r["warnings"]})

    # 扫描件路径
    try:
        extract_from_pdf(str(image_pdf))
        print("[扫描件] 意外成功（不应发生）")
        rows.append({"case": "scan_sim", "ok": True, "error": ""})
    except ExtractionError as e:
        print(f"[扫描件] 按预期失败: {str(e)[:60]}")
        rows.append({"case": "scan_sim", "ok": False, "error": str(e)})

    # 文件不存在路径
    try:
        extract_from_pdf(str(DATA / "nope.pdf"))
        print("[不存在] 意外成功")
    except ExtractionError as e:
        print(f"[不存在] 按预期失败: {str(e)[:60]}")
        rows.append({"case": "missing", "ok": False, "error": str(e)})

    dest = ROOT / "logs" / f"pdftest_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    dest.write_text(json.dumps({"run_at": str(datetime.now()), "rows": rows},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n明细: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
