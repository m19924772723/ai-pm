# -*- coding: utf-8 -*-
"""L2 配置：语料来源、分块参数、端点与存储路径。

原则：分块参数与语料来源都写在这里，改配置改这一处，不散落在代码里。
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------- 路径 ----------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INDEX_DIR = DATA_DIR / "index"          # Chroma 持久化目录（不进 git）
CACHE_DIR = DATA_DIR / "embed_cache"    # embedding 缓存（省钱 + 可复现）

# ---------- 语料来源（真实材料，不复制文件，直接读原路径） ----------
# L2 的产品定位是"查自己的资料"，所以语料就是本工作区的真实文档。
WORKSPACE = ROOT.parent.parent          # D:/code/hermes/ai_pm
CORPUS_SOURCES: list[dict] = [
    {"name": "ai_pm/docs", "glob": "docs/*.md", "desc": "方法论与项目文档"},
    {"name": "ai_pm/log", "glob": "log/*.md", "desc": "每日过程日志"},
]
CORPUS_ROOT = WORKSPACE                 # 相对这个根目录解析上面的 glob

# ---------- 分块 ----------
MAX_CHARS = 512        # 单块目标上限（中文按字符计）
OVERLAP_CHARS = 64     # 相邻块重叠，缓解"答案被切断"
MIN_CHARS = 40         # 小于此长度的孤块丢弃（标题行、空段）

# ---------- Embedding ----------
# 实测（2026-10-08）：tuoji / nemotron-3-embed-1b 可用（2048 维）
# nv-embed-v1 已 EOL（410），stepfun/deepseek 无 embedding 端点
EMBED_PROVIDER = os.environ.get("L2_EMBED_PROVIDER", "tuoji")
EMBED_BASE_URL = os.environ.get("L2_EMBED_BASE_URL", "https://api.tuoji.top/v1")
EMBED_MODEL = os.environ.get("L2_EMBED_MODEL", "nemotron-3-embed-1b")
EMBED_KEY_ENV = "TUOJI_API_KEY"
EMBED_BATCH = 16       # 单次请求条数
EMBED_TIMEOUT = 60.0

# ---------- 向量库 ----------
COLLECTION = "l2_knowledge_base"

# ---------- 生成模型（复用 L1 的跨端点故障转移） ----------
# L1 的 utils/llm.py 可直接复制使用；此处仅记录候选顺序
LLM_CANDIDATES = ("stepfun", "deepseek", "tuoji")


def ensure_dirs() -> None:
    for d in (DATA_DIR, INDEX_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
