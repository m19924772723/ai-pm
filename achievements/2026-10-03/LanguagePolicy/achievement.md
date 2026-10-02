# LanguagePolicy

## 成果日期
2026-10-03

## 今日成果

1. **输出语言策略定案**：System Prompt 规则 7"输出语言固定为中文（不跟随输入语言），专有名词/数字/英文术语保持原样"。
2. **S11 复跑验证**：英文论文输入 → 中文输出，schema 通过，ev_issues=0（修复前为"随机中英"，覆盖率误伤 4 条）。
3. 决策依据记录：目标用户是中文知识工作者，中文输出友好；不可预期的中英切换才是缺陷。

## 关键数字

| 项 | 修复前 | 修复后 |
|---|---|---|
| S11 输出语言 | 随机中英 | 固定中文（术语保留） |
| S11 schema / evidence | ok / 0 | ok / 0 |

## 可复用成果

- 提示词规则 v0.3：`../../projects/L1-longtext-struct/prompts/templates.py`（规则 7）
- 决策记录：`../../docs/L1失败案例分析.md` 第三节
- 复跑证据：`../../projects/L1-longtext-struct/logs/day11_s11_v2_data.json`

## 原始记录

- `../../log/2026-10-03.md`
