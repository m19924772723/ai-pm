# -*- coding: utf-8 -*-
"""问答评测（L2 W2）：引用准确率 + 拒答正确率。

两组样本：
- 有答案组（10 条）：每条标注"应引用的黄金 doc_id 前缀"
- 拒答组（10 条）：资料里确实没有答案 → 必须拒答（unanswerable 或"资料中没有"）

可复现：评测集在 scripts/qa_eval_data.py 里是显式数据，跑一次即得数字。
用法：python -m scripts.qa_eval
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query import answer as qa  # noqa: E402

# 有答案组的黄金来源（doc_id 前缀，允许 2 个合理候选——同一内容可能散在多个文档）。
# 语料是工作区真实文档；gold 标错会冤枉系统（首轮已踩：简历问题真实来源是
# docs/简历打造参考文档.md 而非简历骨架.md）。
ANSWERABLE: list[dict] = [
    {"q": "跨端点故障转移是做什么的？", "gold": ["log/2026-10-06.md", "docs/L1复盘.md"]},
    {"q": "L1 的幻觉率是多少？", "gold": ["docs/进度快照-2026-10-07.md", "docs/L1-1项目说明.md"]},
    {"q": "评测集是怎么构建的？", "gold": ["docs/L1评测方法.md", "log/2026-10-01.md"]},
    {"q": "分块为什么要保留字符偏移？", "gold": ["docs/L2-1项目预研.md", "docs/L1复盘.md"]},
    {"q": "向量数据库用 Chroma 还是 FAISS？", "gold": ["docs/L2-1项目预研.md"]},
    {"q": "部署方案是什么？", "gold": ["docs/L1部署上线方案.md", "log/2026-10-03.md"]},
    {"q": "简历里的经历怎么写法？", "gold": ["docs/简历打造参考文档.md", "docs/简历骨架.md"]},
    {"q": "面试怎么练习？", "gold": ["docs/面试准备参考文档.md"]},
    {"q": "Day 5 完成了什么？", "gold": ["log/2026-09-27.md", "log/2026-09-28.md"]},
    {"q": "L1 用的是什么技术栈？", "gold": ["docs/L1技术选型草稿.md", "docs/L1-1项目启动说明书.md"]},
]

# 拒答组：语料里确实不存在答案
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


def _is_refusal(a: qa.QAAnswer) -> bool:
    return qa._is_refusal(a)


def _answer_with_retry(q: str, attempts: int = 2) -> qa.QAAnswer:
    """评测调用：引用为空（瞬态）时重试 1 次。L1 教训：瞬态失败不污染评测。"""
    last = None
    for _ in range(attempts):
        a = qa.answer(q)
        if a.citations or a.unanswerable:
            return a
        last = a
        time.sleep(2)
    return last


def main() -> int:
    t0 = time.time()
    rows = []
    correct = 0
    for item in ANSWERABLE:
        a = _answer_with_retry(item["q"])
        gold = item["gold"]
        cited_docs = {c.get("doc_id", "") for c in a.citations}
        ok = bool(cited_docs) and any(any(d.startswith(g) for g in gold) for d in cited_docs)
        correct += ok
        rows.append({"q": item["q"], "gold": gold, "cited": sorted(cited_docs),
                     "ok": ok, "unanswerable": a.unanswerable})
        print(f"[{'✓' if ok else '✗'}] {item['q']} → 引用 {sorted(cited_docs)[:3]}")
    acc = correct / len(ANSWERABLE)

    ref_correct = 0
    rows_r = []
    for q in UNANSWERABLE:
        a = _answer_with_retry(q)
        ok = _is_refusal(a)
        ref_correct += ok
        rows_r.append({"q": q, "refused": ok, "unanswerable": a.unanswerable,
                       "answer_head": (a.answer or "")[:40]})
        print(f"[{'✓' if ok else '✗'}] {q} → 拒答={ok}")
    ref_acc = ref_correct / len(UNANSWERABLE)

    dt = time.time() - t0
    print(f"\n=== L2 W2 问答评测 ===")
    print(f"引用准确率 = {acc:.0%}（{correct}/{len(ANSWERABLE)}）")
    print(f"拒答正确率 = {ref_acc:.0%}（{ref_correct}/{len(UNANSWERABLE)}）")
    print(f"耗时 {dt:.1f}s")
    json.dump({"citation_accuracy": round(acc, 4), "refusal_accuracy": round(ref_acc, 4),
               "rows": rows, "refusal_rows": rows_r, "elapsed_s": round(dt, 1)},
              open("logs/qa_eval_w2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())