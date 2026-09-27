# -*- coding: utf-8 -*-
"""PDF 正文提取（PyMuPDF）。"""
from __future__ import annotations

from .web import ExtractionError


def extract_from_pdf(path: str, max_pages: int = 60) -> dict:
    """提取 PDF 文本。

    返回 {"path", "title", "text", "pages", "method", "warnings"}。
    扫描版 PDF（无文本层）会明确报错，不做 OCR——这是 L1 的明确边界。
    """
    try:
        import pymupdf as fitz  # PyMuPDF ≥1.24 推荐导入名
    except ImportError:
        try:
            import fitz  # 旧版兼容
        except ImportError:
            raise ExtractionError("未安装 PyMuPDF，请先安装依赖") from None

    try:
        doc = fitz.open(path)
    except Exception as e:
        raise ExtractionError(f"无法打开 PDF: {type(e).__name__}") from None

    warnings: list[str] = []
    total = doc.page_count
    if total > max_pages:
        warnings.append(f"共 {total} 页，只提取前 {max_pages} 页")

    parts: list[str] = []
    for i in range(min(total, max_pages)):
        parts.append(doc.load_page(i).get_text("text"))
    doc.close()

    text = "\n\n".join(p.strip() for p in parts if p.strip())
    if len(text.strip()) < 100:
        raise ExtractionError("PDF 无文本层（可能是扫描件）；L1 不做 OCR，请手动粘贴正文")

    title = ""
    first = parts[0].strip().splitlines() if parts and parts[0].strip() else []
    if first:
        title = first[0].strip()[:80]

    return {"path": path, "title": title, "text": text.strip(), "pages": total,
            "method": "pymupdf", "warnings": warnings}
