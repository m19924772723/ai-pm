# QAEvalSet（30 条正式评测集）

**成果词**：QAEvalSet —— L2 问答从 10 条草案 → 30 条正式评测集

## 做成了什么

| 项 | 结果 |
|---|---|
| 评测集 | **30 条 = 20 有答案 + 10 无答案** |
| 类型覆盖 | fact×6 / decision×4 / compare×2 / review×4 / operation×4 |
| 可复现 | `scripts/build_qa_evalset.py` 一键生成 `tests/qa_eval_set.json` |
| gold 校验 | 构建脚本自校验 gold 前缀是否真在语料中（当场抓出 2 条无效 gold 并修正） |
| 评测升级 | `qa_eval.py` 从评测集读取（不再硬编码），保留瞬态重试 |
| 索引 | 语料 42 篇，重建后 in_sync=true |

## 为什么这件事重要

W3 排期目标之一是"建 30 条评测集 + 跑 4 指标"。今天的评测集把 L2 的验证从"10 条草案"
升级为"30 条正式"：
- **类型覆盖**让数字不只是"平均效果"，还能拆出 fact/decision/compare 分别看短板
- **gold 自校验**防止自己标错冤枉系统（Day 18 教训工程化：错了当场报，不等评测判死）
- 语料范围明确为 docs/log（42 篇），操作类问题 gold 也要落在这个范围

## 可复现

```bash
python -m scripts.build_qa_evalset    # 生成 30 条 + gold 校验
python -m scripts.qa_eval --out logs/qa_eval_w3.json   # 全量评测（约 15 分钟）
```

## 当前数字（评测跑完后填）

- 引用准确率 / 拒答正确率：待填（后台 30 条全量评测中）