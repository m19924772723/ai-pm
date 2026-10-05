# Comparison Operations

## 操作记录

1. `run_eval.py` 增加瞬态故障自动重试（空响应/网络错误重试 1 次，5s 间隔），清理首版残留代码。
2. 后台全量重跑（v4，stepfun，带重试）：19/20，S05 重试两次仍空响应。
3. 单测 38 passed（改动不影响）。
4. 跨端点探测 S05：stepfun 两次失败（空响应 + 截断），deepseek 一次通过（schema=True、5 要点、0 证据问题）。
5. 分析 v4 明细：S04/S13/S19 剩余 miss 为已知匹配器限界，S17 出现 1 条证据跳句（规则违规如实记录）。
6. 更新简历骨架项目 1 栏（四段式 + 数字）。
7. 准备 Day 12 日志与成果归档（本文件），待 Git 提交推送。

## 验证结果

- v4：格式合规 19/20=95%、覆盖率 69/76=90.8%、幻觉率 1/95=1.05%
- 覆盖率归因：匹配器 +11pp、提示词 +7pp（同批输出复算对照）
- S05：stepfun 不稳 / deepseek 可用（端点问题，非产品）

## 失败与阻塞

- S05 在 stepfun 上连续失败（含重试）→ 已用 deepseek 验证输入与提示词无问题；待办：pipeline 故障转移
- S17 严格规则下仍偶发跳句 → 检查器如实计为 1 条（幻觉率口径不变）

## 关联文件

- `../../log/2026-10-04.md`
- `../../projects/L1-longtext-struct/run_eval.py`
- `../../projects/L1-longtext-struct/logs/eval_eval20_v4_*.json`
- `../../docs/简历骨架.md`
