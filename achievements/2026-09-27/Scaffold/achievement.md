# Scaffold

## 成果日期
2026-09-27

## 今日成果

1. 建成 L1 项目骨架 `projects/L1-longtext-struct/`：pipeline、prompts、utils、extractors、tests、logs 六层结构。
2. 三套提示词（摘要/待办/归档）从文档落地为可运行代码，与 `docs/L1提示词初稿.md` 口径一致。
3. 实现结构化输出的完整校验链：JSON 提取 → Schema 校验 → evidence 原文回溯。
4. 实现截断检测：用 `finish_reason` 和括号配对判断"JSON 解析失败"是否由输出被截断引起。
5. 29 个离线单元测试全部通过（不需要联网、不花 API 费用）。
6. 首次真实 API 调用成功，并跑完第一轮评测，产出三个真实指标。
7. 写出 `rescore.py`：换指标定义后可以复算，不必重新调用模型。

## 关键数字（4 条样本，stepfun / step-3.7-flash）

| 指标 | 数字 |
|---|---|
| 格式合规率 | 4/4 = 100% |
| 幻觉率 | 0/14 = 0% |
| 要点覆盖率 | 12/13 = 92.3%（v2 匹配器；v1 逐字匹配为 7/13 = 53.8%） |
| 单条耗时 | 8.5–20.9 s |

> 覆盖率的两个数字差异来自匹配器而非模型，样本仅 4 条，**不构成结论**。

## 可复用成果

- 项目代码：`../../projects/L1-longtext-struct/`
- 项目说明：`../../projects/L1-longtext-struct/README.md`
- 提示词设计：`../../docs/L1提示词初稿.md`
- 评测结果：`../../projects/L1-longtext-struct/logs/eval_day5_fixed_*.json`
- 匹配器对照：`../../projects/L1-longtext-struct/logs/rescore_*.json`

## 原始记录

- `../../log/2026-09-27.md`
