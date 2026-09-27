# -*- coding: utf-8 -*-
"""统一的 LLM 调用封装。

规则：
- 密钥只从环境变量读取，绝不写入代码、配置或仓库。
- 统一返回纯文本；JSON 解析由 utils/schema.py 负责。
- 只支持本项目需要的两种协议：anthropic_messages / chat_completions。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_mode: str
    model: str
    key_env: str
    timeout: float = 180.0


# 可用的中转/官方端点。模型名与 key 的环境变量名一一对应。
# 2026-09-27 实测（scripts_probe.py）：
#   stepfun  OK   step-3.7-flash
#   deepseek OK  deepseek-flash（推理模型，max_tokens 过小会返回空内容）
#   tuoji    OK   kimi-k3（deepseek-v4-flash 当前无可用通道；glm-5.3-flash 小 max_tokens 会返回空）
#   siyu     FAIL 403 SUBSCRIPTION_NOT_FOUND（该 key 订阅失效，留在列表里等恢复）
PROVIDERS: dict[str, Provider] = {
    "stepfun": Provider("stepfun", "https://api.stepfun.com/v1", "chat_completions", "step-3.7-flash", "HERMES_CUSTOM_STEPFUN_API_KEY"),
    "deepseek": Provider("deepseek", "https://api.deepseek.com/v1", "chat_completions", "deepseek-flash", "HERMES_CUSTOM_DEEPSEEK_API_KEY"),
    "tuoji": Provider("tuoji", "https://api.tuoji.top", "anthropic_messages", "kimi-k3", "TUOJI_API_KEY"),
    "siyu": Provider("siyu", "https://siyu.site", "anthropic_messages", "deepseek-v4-flash", "SIYU_API_KEY"),
}

# 未显式指定 LLM_PROVIDER 时的尝试顺序（按实测可用性排序）
DEFAULT_ORDER = ("stepfun", "deepseek", "tuoji", "siyu")

# 推理模型会先用掉一部分 token 做推理；max_tokens 太小会导致"返回空内容"
MIN_SAFE_MAX_TOKENS = 512


class LLMError(RuntimeError):
    """调用失败；消息中不含密钥。"""


def available_providers() -> list[str]:
    """返回当前环境里存在密钥的 provider 名称。"""
    return [n for n, p in PROVIDERS.items() if os.environ.get(p.key_env)]


def resolve_provider(name: str | None = None) -> Provider:
    """按名称或环境变量挑选一个可用 provider。"""
    want = name or os.environ.get("LLM_PROVIDER")
    if want:
        if want not in PROVIDERS:
            raise LLMError(f"未知 provider: {want}；可选 {list(PROVIDERS)}")
        p = PROVIDERS[want]
        if not os.environ.get(p.key_env):
            raise LLMError(f"provider {want} 缺少环境变量 {p.key_env}")
        return p
    for cand in DEFAULT_ORDER:
        p = PROVIDERS[cand]
        if os.environ.get(p.key_env):
            return p
    raise LLMError("没有任何可用 provider：需要设置 " + " / ".join(p.key_env for p in PROVIDERS.values()))


def call_llm(system: str, user: str, provider: str | None = None, model: str | None = None,
             max_tokens: int = 8192, temperature: float = 0.0) -> str:
    """调用模型并返回文本；失败抛 LLMError。"""
    return call_llm_meta(system, user, provider=provider, model=model,
                         max_tokens=max_tokens, temperature=temperature)["text"]


def call_llm_meta(system: str, user: str, provider: str | None = None, model: str | None = None,
                  max_tokens: int = 8192, temperature: float = 0.0) -> dict:
    """调用模型，返回 {text, finish_reason, usage, model, provider}。

    finish_reason 用于判断"是否被截断"——L1 的 JSON 解析失败多半是这里的信号。
    """
    p = resolve_provider(provider)
    key = os.environ[p.key_env]
    use_model = model or p.model

    if p.api_mode == "anthropic_messages":
        url = p.base_url.rstrip("/") + "/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": use_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
    else:
        url = p.base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": use_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=p.timeout)
    except httpx.HTTPError as e:
        raise LLMError(f"{p.name} 网络错误: {type(e).__name__}") from None

    if r.status_code != 200:
        body = r.text[:300]
        raise LLMError(f"{p.name} HTTP {r.status_code}: {body}")

    try:
        data = r.json()
    except json.JSONDecodeError:
        raise LLMError(f"{p.name} 返回非 JSON 内容") from None

    if p.api_mode == "anthropic_messages":
        blocks = data.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
        finish_reason = data.get("stop_reason", "")
    else:
        choices = data.get("choices") or []
        text = (choices[0].get("message", {}).get("content") or "") if choices else ""
        finish_reason = (choices[0].get("finish_reason") or "") if choices else ""

    if not text.strip():
        hint = ""
        if max_tokens < MIN_SAFE_MAX_TOKENS:
            hint = f"（max_tokens={max_tokens} 可能过小：推理模型会先消耗推理 token）"
        raise LLMError(f"{p.name} 返回空内容{hint}")

    return {"text": text, "finish_reason": finish_reason, "usage": data.get("usage") or {},
            "model": use_model, "provider": p.name}


def provider_info(provider: str | None = None) -> dict:
    """给日志/README 用的不含密钥的 provider 信息。"""
    p = resolve_provider(provider)
    return {"name": p.name, "base_url": p.base_url, "api_mode": p.api_mode,
            "model": p.model, "key_env": p.key_env}
