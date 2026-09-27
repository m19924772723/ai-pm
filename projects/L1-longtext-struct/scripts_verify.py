# -*- coding: utf-8 -*-
"""Day 5 链路验证脚本：真实调用一次，输出可核验结果。

用法：.venv/Scripts/python.exe scripts_verify.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import structure  # noqa: E402
from prompts.templates import build_user_prompt  # noqa: E402
from utils.llm import available_providers  # noqa: E402

TEXT = (
    "学院要求各项目组在 10 月 8 日前提交中期报告。报告须包含目前进度、风险和下周计划。"
    "张三负责汇总技术进度，李四负责补充用户访谈记录。项目当前已完成 60% 的开发。"
)


def main() -> int:
    print("可用 provider:", available_providers())

    up = build_user_prompt("summary", "测试文本")
    print(f"prompt 长度={len(up)} 含花括号={'{' in up} 占位符已替换={'{{INPUT_TEXT}}' not in up}")

    for prov in available_providers():
        print(f"\n===== provider={prov} =====")
        r = structure(TEXT, template="summary", provider=prov)
        print("ok:", r.ok, "| error:", (r.error or "")[:180])
        print("elapsed:", r.elapsed_s, "| schema_ok:", r.schema_ok,
              "| evidence_issues:", len(r.evidence_issues))
        if r.evidence_issues:
            for p in r.evidence_issues[:3]:
                print("   -", p)
        if r.ok:
            print(json.dumps(r.data, ensure_ascii=False, indent=2)[:1500])
            return 0
        if r.raw:
            print("RAW HEAD:", r.raw[:300].replace("\n", " "))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
