# -*- coding: utf-8 -*-
"""逐个探测可用 provider：一次极短调用，打印真实结果（不打印密钥）。

用法：.venv/Scripts/python.exe scripts_probe.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.llm import PROVIDERS, call_llm, provider_info  # noqa: E402

SYSTEM = "只输出 JSON，不要解释。"
USER = '输出这个 JSON，不要改动：{"ok": true}'


def main() -> int:
    ok_list = []
    for name in PROVIDERS:
        try:
            info = provider_info(name)
        except Exception as e:
            print(f"[{name:9}] 跳过（缺密钥）: {e}")
            continue
        try:
            out = call_llm(SYSTEM, USER, provider=name, max_tokens=64)
            print(f"[{name:9}] OK  model={info['model']}  reply={out.strip()[:60]!r}")
            ok_list.append(name)
        except Exception as e:
            print(f"[{name:9}] FAIL  {str(e)[:160]}")
    print("\n可用 provider:", ok_list)
    return 0 if ok_list else 1


if __name__ == "__main__":
    raise SystemExit(main())
