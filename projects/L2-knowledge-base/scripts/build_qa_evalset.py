# -*- coding: utf-8 -*-
"""L2 正式评测集（W3）：30 条问答对 = 20 有答案 + 10 无答案。

设计（可复现，改样本改脚本重跑）：
- 语料：工作区 42 篇真实文档（docs/ 23 + log/ 19）
- 有答案 20 条：覆盖 事实/决策/对比/复盘/操作 五类，每条标注正确来源 doc_id 前缀
  （允许 2-3 个合理候选——同一内容可能散在多个文档；候选必须对着语料实际存在的文档标）
- 无答案 10 条：语料里确实不存在（测拒答正确率）
- gold 状态：draft_manual（待用户抽查后改 reviewed）

用法：python -m scripts.build_qa_evalset   # 生成 tests/qa_eval_set.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.loader import load_docs  # noqa: E402

# ---------------- 有答案 20 条 ----------------
ANSWERABLE: list[dict] = [
    # 事实类
    {"q": "跨端点故障转移是做什么的？", "type": "fact",
     "gold": ["log/2026-10-06.md", "docs/L1复盘.md"]},
    {"q": "L1 的幻觉率是多少？", "type": "fact",
     "gold": ["docs/进度快照-2026-10-07.md", "docs/L1-1项目说明.md", "log/2026-10-01.md", "log/2026-10-04.md"]},
    {"q": "L1 的要点覆盖率是多少？", "type": "fact",
     "gold": ["docs/进度快照-2026-10-07.md", "docs/L1-1项目说明.md", "docs/L1-1项目启动说明书.md"]},
    {"q": "L1 用了哪个界面框架？", "type": "fact",
     "gold": ["docs/L1技术选型草稿.md", "docs/L1-1项目启动说明书.md"]},
    {"q": "L2 项目用什么向量数据库？", "type": "fact",
         "gold": ["docs/L2-1项目预研.md", "docs/L1技术选型草稿.md", "log/2026-10-08.md"]},
    {"q": "L1 的评测集有多少条？", "type": "fact",
     "gold": ["docs/L1评测方法.md", "docs/进度快照-2026-10-07.md"]},
    # 决策类
    {"q": "为什么 L2 不用 FAISS 用 Chroma？", "type": "decision",
     "gold": ["docs/L2-1项目预研.md"]},
    {"q": "为什么做混合检索而不是纯向量？", "type": "decision",
         "gold": ["docs/L2-1项目预研.md", "log/2026-10-08.md", "projects/L2-knowledge-base/README.md"]},
    {"q": "分块策略为什么要保留字符偏移？", "type": "decision",
     "gold": ["docs/L2-1项目预研.md", "log/2026-10-08.md", "docs/L1复盘.md"]},
    {"q": "L1 为什么不用长上下文硬喂？", "type": "decision",
     "gold": ["docs/L2-1项目预研.md", "docs/L1复盘.md", "docs/L1技术选型草稿.md", "log/2026-09-25.md"]},
    # 对比类
    {"q": "纯稠密检索和混合检索效果差多少？", "type": "compare",
     "gold": ["docs/L2-1项目预研.md", "log/2026-10-08.md"]},
    {"q": "Chroma 和 FAISS 各自优缺点？", "type": "compare",
     "gold": ["docs/L2-1项目预研.md"]},
    # 复盘类
    {"q": "L1 复盘总结出几条诚实不足？", "type": "review",
         "gold": ["docs/L1复盘.md", "log/2026-10-07.md", "docs/周复盘-2026-10-11.md"]},
    {"q": "Day 5 完成了什么？", "type": "review",
     "gold": ["log/2026-09-27.md", "log/2026-09-28.md", "projects/L2-knowledge-base/README.md", "log/2026-10-08.md"]},
    {"q": "Day 15 完成了什么？", "type": "review",
         "gold": ["log/2026-10-07.md", "log/2026-10-06.md"]},
    {"q": "本周（W3）复盘的满意度是几分？", "type": "review",
         "gold": ["docs/周复盘-2026-10-11.md", "log/2026-10-11.md"]},
    # 操作类
    {"q": "如何重建 L2 索引？", "type": "operation",
     "gold": ["log/2026-10-08.md", "log/2026-10-10.md", "projects/L2-knowledge-base/README.md"]},
    {"q": "怎么验证索引和语料同步？", "type": "operation",
     "gold": ["log/2026-10-10.md", "log/2026-10-08.md", "projects/L2-knowledge-base/README.md"]},
    {"q": "简历里的经历怎么写法？", "type": "operation",
     "gold": ["docs/简历打造参考文档.md", "docs/简历骨架.md"]},
    {"q": "面试怎么练习？", "type": "operation",
     "gold": ["docs/面试准备参考文档.md"]},
]

# ---------------- 无答案 10 条 ----------------
UNANSWERABLE: list[str] = [
    "今天中午吃什么好？",
    "我的女朋友叫什么名字？",
    "张三去年的年终奖是多少？",
    "如何使用微信小程序做支付？",
    "英伟达最新的 GPU 型号有哪些？",
    "明天的天气怎么样？",
    "B 站的推荐算法原理是什么？",
    "我家楼下的修车店几点关门？",
    "如何写一篇 Nature 论文？",
    "社保断缴会有什么后果？",
]


def main() -> int:
    docs = load_docs()
    # 校验 gold 前缀确实存在于语料（防止标错冤枉系统——Day 18 教训）
    doc_ids = [d.doc_id for d in docs]
    problems = []
    for item in ANSWERABLE:
        for g in item["gold"]:
            if not any(d.startswith(g) for d in doc_ids):
                problems.append(f"{item['q']} → gold '{g}' 不在语料中")
    if problems:
        print("⚠️ gold 校验失败：")
        for p in problems:
            print(f"  {p}")
        print("（脚本仍生成，但评测时这些 gold 永远判失败——请修正）")
    else:
        print(f"✅ 全部 {len(ANSWERABLE)} 条 gold 前缀都能在语料 {len(docs)} 篇中找到")

    out = {
        "built_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "n_answerable": len(ANSWERABLE),
        "n_unanswerable": len(UNANSWERABLE),
        "gold_status": "draft_manual",
        "answerable": ANSWERABLE,
        "unanswerable": UNANSWERABLE,
    }
    Path("tests/qa_eval_set.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写 tests/qa_eval_set.json（30 条 = {len(ANSWERABLE)} 有答案 + {len(UNANSWERABLE)} 无答案）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())