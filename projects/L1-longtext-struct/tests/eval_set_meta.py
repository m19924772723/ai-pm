# -*- coding: utf-8 -*-
"""评测集说明。

⚠️ 这不是 20 条评测集。L1 说明书的计划是第 4 周（Day 8–9）建成 20 条并人工标注。
   现在只有 4 条，用于 Day 5 打通链路和验证评测脚本本身是否可用。

字段：
  id            编号
  template      针对哪个模板
  input         输入文本（真实来源，注明出处）
  gold_points   人工标注的"标准关键点"（用于算要点覆盖率）
  notes         该样本想覆盖的失败模式
"""
from __future__ import annotations

import json
from pathlib import Path

EVAL_PATH = Path(__file__).parent / "eval_set.json"

TARGET_SAMPLES = 20  # 说明书目标


def load() -> dict:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


def stats() -> dict:
    d = load()
    items = d.get("samples", [])
    by_tpl: dict[str, int] = {}
    for s in items:
        by_tpl[s["template"]] = by_tpl.get(s["template"], 0) + 1
    return {"count": len(items), "target": TARGET_SAMPLES,
            "by_template": by_tpl, "gap": max(0, TARGET_SAMPLES - len(items))}


if __name__ == "__main__":
    print(json.dumps(stats(), ensure_ascii=False, indent=2))
