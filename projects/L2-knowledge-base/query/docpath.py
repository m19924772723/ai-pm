# -*- coding: utf-8 -*-
"""把 doc_id 解析成磁盘上的实际文件路径（界面读取原文件高亮用）。

loader 记录 source（相对工作区的目录前缀，如 'ai_pm/docs'），
但 doc_id 形如 'docs/L1-1项目启动说明书.md'（是相对 ai_pm 仓库的路径）。
这里做两层解析：先按 doc_id 直接找，再按 source 前缀找（兼容未来语料目录变动的场景）。
"""
from __future__ import annotations

from pathlib import Path

import config


def resolve_doc_path(doc_id: str, source: str = "") -> Path | None:
    cands = [
        Path(config.ROOT).parent.parent / doc_id,      # 仓库根 + doc_id
        Path(config.ROOT) / doc_id,                     # 项目根 + doc_id
    ]
    if source:
        cands.append(Path(config.ROOT).parent.parent / source / Path(doc_id).name)
    for p in cands:
        if p.exists() and p.is_file():
            return p
    return None


if __name__ == "__main__":
    for did, src in [("docs/L1-1项目启动说明书.md", "ai_pm/docs"),
                     ("log/2026-10-06.md", "ai_pm/log")]:
        p = resolve_doc_path(did, src)
        print(f"{did} → {p}")