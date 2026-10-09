# -*- coding: utf-8 -*-
"""统一错误类型（L2 各模块共用）。"""
from __future__ import annotations


class LLMError(RuntimeError):
    """LLM 调用失败；消息中不携带任何密钥。"""