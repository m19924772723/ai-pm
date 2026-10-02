# EvidenceFix

## 成果日期
2026-10-02

## 今日成果

1. **S09 英文 schema 修复**：System Prompt 新增"输出必须包含 Schema 全部字段，缺省填 未指定/unspecified，禁止删除键"。复跑：schema 通过、ev_issues=0。
2. **S17 证据规则定案**：证据约束从"允许删去中间若干字"改为"evidence 必须是原文**完整连续子串**（逐字一致，不得删改拼接）"。复跑：ev_issues=0。
3. **约束设计决策**：宁可让模型多抄原文，也不允许改写/删节——证据可追溯性优先，测量保持简单（连续子串判断）。
4. **失败案例分析文档**：`docs/L1失败案例分析.md`，首轮 20 条四类失败全分类（真 bug 2 / API 瞬态 1 / 匹配器限界 ~11 / 策略 4），含语言切换策略的 A/B 选项分析。

## 关键数字

| 项 | 修复前 | 修复后 |
|---|---|---|
| S09 schema | 未过 | 通过（ev_issues=0） |
| S17 evidence | 1 条跳句 | 0 条（完整连续子串） |

## 可复用成果

- 提示词规则 v0.2：`../../projects/L1-longtext-struct/prompts/templates.py`（规则 3、6）
- 同步文档：`../../docs/L1提示词初稿.md`
- 失败案例分类：`../../docs/L1失败案例分析.md`
- 复跑证据：`../../projects/L1-longtext-struct/logs/day10_fix_*.json`、`logs/day10_s17_v3_data.json`

## 原始记录

- `../../log/2026-10-02.md`
