# -*- coding: utf-8 -*-
"""网页正文提取。失败时抛出 ExtractionError，由上层降级为“请手动粘贴”。"""
from __future__ import annotations


class ExtractionError(RuntimeError):
    """提取失败，需要降级处理。"""


def extract_from_url(url: str, timeout: int = 30) -> dict:
    """抓取网页正文。

    返回 {"url", "title", "text", "method", "warnings"}。
    method: trafilatura / fallback（说明用了哪条路径，便于统计失败率）。
    """
    if not url or not url.strip():
        raise ExtractionError("URL 为空")

    import httpx

    try:
        r = httpx.get(url, timeout=timeout, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (compatible; L1-struct/0.1)"})
    except Exception as e:
        raise ExtractionError(f"请求失败: {type(e).__name__}") from None

    if r.status_code != 200:
        raise ExtractionError(f"HTTP {r.status_code}")
    html = r.text
    if len(html) < 200:
        raise ExtractionError("页面内容过短，可能是反爬或空页")

    warnings: list[str] = []
    text, title, method = "", "", ""

    try:
        import trafilatura

        text = trafilatura.extract(html, include_comments=False, include_tables=True) or ""
        meta = trafilatura.extract_metadata(html)
        title = (getattr(meta, "title", "") or "") if meta else ""
        method = "trafilatura"
    except ImportError:
        warnings.append("未安装 trafilatura，使用兜底规则")
    except Exception as e:
        warnings.append(f"trafilatura 异常: {type(e).__name__}")

    if len(text.strip()) < 200:
        fallback = _fallback_extract(html)
        if len(fallback) > len(text):
            warnings.append(f"trafilatura 结果过短({len(text)}字)，改用兜底规则({len(fallback)}字)")
            text, method = fallback, "fallback"

    if len(text.strip()) < 200:
        raise ExtractionError("正文提取结果过短，建议手动粘贴")

    return {"url": url, "title": title, "text": text.strip(), "method": method, "warnings": warnings}


def _fallback_extract(html: str) -> str:
    """兜底：去掉 script/style，剥标签，保留段落。"""
    import re

    html = re.sub(r"(?is)<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", " ", html)
    blocks = re.findall(r"(?is)<(?:p|h1|h2|h3|li|blockquote)[^>]*>(.*?)</(?:p|h1|h2|h3|li|blockquote)>", html)
    parts = []
    for b in blocks:
        t = re.sub(r"(?s)<[^>]+>", "", b)
        t = re.sub(r"&nbsp;?", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 15:
            parts.append(t)
    return "\n\n".join(parts)
