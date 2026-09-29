# Templates

## 成果日期
2026-09-29

## 今日成果

1. **三模板接线端到端验证**（`scripts_demo.py`）：同一篇真实文章跑摘要/待办/归档，**3/3 成功**，Schema 全通过，产出结构化结果与三份 Markdown 渲染。
2. **发现并修复 evidence 弱引用问题**：待办模板 3 条 evidence 无法逐字回溯，逐条对照原文后分类为**改写 / 删节 / 跨句拼接**（均非幻觉）→ System Prompt 第 3 条改为强制"连续原文片段、逐字引用、不得跨句拼接"。
3. **A/B 对比**：同文待办模板 ev_issues **3 → 0**；用评测集 S01/S03（含真实死线待办）回归，确认真实待办照常提取（王五/赵六全中），S02（无待办）正确给 0。
4. **渲染测试补齐**：待办/归档全字段 Markdown 渲染 + 警告追加，test_schema 21 → 25 条。
5. **woshipm 精读材料**：`docs/woshipm精读-产品价值公式.md`（核心结论、与 L1 迁移成本的关联、金句、3 道自测题），全文存样。

## 关键数字

| 项 | 数字 |
|---|---|
| 三模板接线 | 3/3 成功 |
| 待办模板 evidence 问题 | 3 → 0（同文 A/B） |
| 真实待办回归 | S01 3 条、S03 2 条全部命中，无遗漏 |
| 全量测试 | 36 passed |

## 可复用成果

- 端到端验证脚本：`../../projects/L1-longtext-struct/scripts_demo.py`
- 三模板 Markdown 渲染：`../../projects/L1-longtext-struct/logs/demo_markdown_*.md`
- A/B 证据：`../../projects/L1-longtext-struct/logs/demo_*.json`、`logs/demo_todos_v2_*.json`
- 精读材料：`../../docs/woshipm精读-产品价值公式.md`
- 文章正文样：`../../projects/L1-longtext-struct/data/sample_inputs/woshipm_产品价值公式.txt`

## 原始记录

- `../../log/2026-09-29.md`