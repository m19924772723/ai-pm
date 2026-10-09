# -*- coding: utf-8 -*-
"""LLM 调用封装（L2 复用 L1 的端点表与纪律，L2 独立维护）。

实践积累（在 L1 验证过的）：
- 密钥只从环境变量读，绝不写进代码/仓库
- 推理模型 max_tokens 太小会返回空内容 → 至少 512
- 故障转移要可见：fallback_from 记录转移过程（L1 教训：只测成功路径不够，
  还要测"关掉 fallback 时如实失败"——见 L1 log/2026-10-06.md）
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from query import llm_error


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_mode: str
    model: str
    key_env: str
    timeout: float = 180.0


# 与 L1 同一张端点表（2026-09-27 实测，L1 scripts_probe.py）
PROVIDERS: dict[str, Provider] = {
    "stepfun": Provider("stepfun", "https://api.stepfun.com/v1", "chat_completions", "step-3.7-flash", "HERMES_CUSTOM_STEPFUN_API_KEY"),
    "deepseek": Provider("deepseek", "https://api.deepseek.com/v1", "chat_completions", "deepseek-flash", "HERMES_CUSTOM_DEEPSEEK_API_KEY"),
    "tuoji": Provider("tuoji", "https://api.tuoji.top", "anthropic_messages", "kimi-k3", "TUOJI_API_KEY"),
    "siyu": Provider("siyu", "https://siyu.site", "anthropic_messages", "deepseek-v4-flash", "SIYU_API_KEY"),
}

# 未显式指定时的尝试顺序（按实测可用性排序）
DEFAULT_ORDER = ("stepfun", "deepseek", "tuoji", "siyu")

MIN_SAFE_MAX_TOKENS = 512


def available_providers() -> list[str]:
    return [n for n, p in PROVIDERS.items() if os.environ.get(p.key_env)]


def provider_info(name: str) -> Provider:
    if name not in PROVIDERS:
        raise llm_error.LLMError(f"未知 provider: {name}；可选 {list(PROVIDERS)}")
    p = PROVIDERS[name]
    if not os.environ.get(p.key_env):
        raise llm_error.LLMError(f"provider {name} 缺少环境变量 {p.key_env}")
    return p


def _call_once(system: str, user: str, provider: str, model: str | None = None,
               max_tokens: int = 8192, temperature: float = 0.0) -> dict[str, Any]:
    """单端点调用，返回 {text, finish_reason, usage, model, provider}；失败抛 LLMError。"""
    p = provider_info(provider)
    key = os.environ[p.key_env]
    use_model = model or p.model

    if p.api_mode == "anthropic_messages":
        url = p.base_url.rstrip("/") + "/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        payload = {"model": use_model, "max_tokens": max_tokens, "temperature": temperature,
                   "system": system, "messages": [{"role": "user", "content": user}]}
    else:
        url = p.base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": use_model, "max_tokens": max_tokens, "temperature": temperature,
                   "messages": [{"role": "system", "content": system},
                                {"role": "user", "content": user}]}

    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=p.timeout)
    except httpx.HTTPError as e:
        raise llm_error.LLMError(f"{p.name} 网络错误: {type(e).__name__}") from None
    if r.status_code != 200:
        raise llm_error.LLMError(f"{p.name} HTTP {r.status_code}: {r.text[:200]}")
    body = r.json()

    text = ""
    finish = ""
    usage = {}
    if p.api_mode == "anthropic_messages":
        finish = (body.get("stop_reason") or "")
        usage = body.get("usage") or {}
        text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
    else:
        choice = (body.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        text = msg.get("content") or ""
        finish = choice.get("finish_reason") or ""
        usage = body.get("usage") or {}
    if not text.strip():
        raise llm_error.LLMError(f"{p.name} 返回空内容")
    return {"text": text, "finish_reason": finish, "usage": usage, "model": use_model, "provider": p.name}


def chat_with_fallback(system: str, user: str, provider: str | None = None,
                       model: str | None = None, max_tokens: int = 8192, temperature: float = 0.0,
                       allow_fallback: bool = True) -> dict[str, Any]:
    """带故障转移的调用。

    返回 {text, finish_reason, usage, provider, fallback_from, warnings}
    fallback_from 非空 = 主端点失败过，线上要能看到系统在带病运行。
    全部失败抛 LLMError（消息含每个端点的简要原因，不含密钥）。
    """
    avail = available_providers()
    want = provider or os.environ.get("LLM_PROVIDER")
    first = [want] if want else []
    if allow_fallback:
        candidates = first + [p for p in DEFAULT_ORDER if p not in first and p in avail]
    else:
        candidates = first or avail[:1]

    warnings: list[str] = []
    fallback_from: list[str] = []
    last_err = ""
    for name in candidates:
        try:
            meta = _call_once(system, user, name, model, max_tokens=max_tokens, temperature=temperature)
            if fallback_from:
                warnings.append(f"主端点失败已自动转移：{'、'.join(fallback_from)} → 改用 {name}")
            meta["fallback_from"] = fallback_from
            meta["warnings"] = warnings
            return meta
        except llm_error.LLMError as e:
            fallback_from.append(name)
            last_err = str(e)

    raise llm_error.LLMError(
        f"全部端点失败（{len(fallback_from)} 个）：{'；'.join(fallback_from)}（最后一个：{last_err[:80]}）")