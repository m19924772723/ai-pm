# Templates Operations

## 操作记录

1. 核对仓库状态：发现 HEAD 为 `1181dfd`（另一会话在 09-28 做的 hello-agents 母本入库），确认其叠在本人 Day 6 提交 `2a5a56f` 之上，历史完整、无冲突后继续。
2. 写 `scripts_demo.py`：抓取 woshipm 真实文章 → 依次跑三模板 → 存结构化结果与 Markdown 渲染。
3. 跑 demo：3/3 成功，但待办模板 ev_issues=3。
4. 逐条对照原文分类证据问题（改写/删节/跨句拼接），确认无幻觉。
5. 改 `prompts/templates.py` 的 System Prompt 第 3 条为强制逐字连续引用。
6. 同文重跑待办模板：ev_issues 3 → 0（`logs/demo_todos_v2_*.json`）。
7. 用评测集 S01（summary，含 3 条死线待办）/ S03（todos，含 2 条）回归，确认真实待办照常提取；S02 正确给 0。
8. 补 `tests/test_schema.py` 的 to_markdown 全渲染测试（+4 条）。
9. 同步 `docs/L1提示词初稿.md` 第 3 条规则，保持文档与代码口径一致。
10. 写精读材料 `docs/woshipm精读-产品价值公式.md`。
11. 全量测试 `pytest tests -q` → 36 passed；计划表 Day 7 标记完成。

## 验证结果

- 三模板端到端：3/3，Schema 全通过
- evidence 严格化 A/B：3 → 0
- 真实待办回归：S01 3/3、S03 2/2 命中
- 全量测试：36 passed
- 文档与代码口径：已同步

## 失败与阻塞

- 无功能失败；今日主要产出是"发现弱引用并修正 + 回归验证"
- siyu 密钥订阅失效仍待用户决定（不阻塞）

## 关联文件

- `../../log/2026-09-29.md`
- `../../projects/L1-longtext-struct/scripts_demo.py`
- `../../projects/L1-longtext-struct/prompts/templates.py`
- `../../docs/L1提示词初稿.md`
- `../../plans/AI产品经理学习实践计划表.xlsx`（Day 7 已标记完成）