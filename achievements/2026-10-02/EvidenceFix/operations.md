# EvidenceFix Operations

## 操作记录

1. 修正计划表 10-02~10-07 共 6 行为真实任务序列（用户不在家期间的执行计划）。
2. S09：在 `prompts/templates.py` System Prompt 增加规则 6（字段齐全、缺省值），复跑 S09（summary）→ schema 通过、ev_issues=0。
3. S17 第 1 轮：规则 3 改为"单个连续片段"→ 复跑仍有 1 条证据问题（模型删去中间分句，检查器要求连续子串）。
4. 决策：不放松检查器，改为规则 3 定案为"完整连续子串（不得删改拼接）"。
5. S17 第 3 轮复跑：ev_issues=0。
6. 同步 `docs/L1提示词初稿.md` 规则 3、6。
7. 写 `docs/L1失败案例分析.md`（原计划 Day 11 内容提前完成）。
8. 未提交 Git——本日结束时 commit+push（见关联记录）。

## 验证结果

- S09：schema=True, ev_issues=0（复跑数据 logs/day10_fix_data.json）
- S17 v3：schema=True, ev_issues=0（logs/day10_s17_v3_data.json）
- 提示词文档与代码口径一致

## 失败与阻塞

- S17 第 1 轮修复不彻底（删句仍触发检查器）→ 通过收紧规则解决，未放宽检查器
- 无其他阻塞

## 关联文件

- `../../log/2026-10-02.md`
- `../../projects/L1-longtext-struct/prompts/templates.py`
- `../../docs/L1提示词初稿.md`
- `../../docs/L1失败案例分析.md`
- `../../plans/AI产品经理学习实践计划表.xlsx`
