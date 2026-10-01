# Evaluation Operations

## 操作记录

1. 核对日期与计划表：10-01 为 Day 8/9（09-30 已跳并入），修正 09-30/10-01/10-02 任务。
2. 写 `scripts/build_evalset.py`：20 条样本（含真实来源 woshipm/promptingguide、合成样本、程序生成超长文本），gold_points 手工标注。
3. 写 `scripts/make_table_pdf.py` 生成含表格 PDF，用 `extract_from_pdf` 真实提取，把**真实提取文本**（表格列按块分行）作为 S14 输入——修正了我原本手焊的 Markdown 表格常量。
4. 构建评测集并校验字段/长度/gold；S19 长度 42120 字。
5. 后台跑 20 条全量评测（`run_eval.py --tag eval20 --provider stepfun`，耗时 446s）。
6. 深挖结果：S15 空内容 → 重试通过（瞬态）；S09 schema 未过（英文缺字段）；S17 证据 1 处跳句；覆盖率 miss 17 条逐条对照。
7. 修复匹配器两个 bug（英文 shingles 缺失、归一化文本丢单词边界），新增 2 条英文回归测试。
8. `rescore.py` 用同一份模型输出复算：66.7% → 78.2%。
9. 修正 S15 len_class（467 字实为 medium），重建评测集。
10. 全量测试 38 passed；计划表 10-01 标记完成、10-02 改为 S09/S17 修复任务。

## 验证结果

- 评测集：20 条，字段/gold/长度校验通过
- 全量评测：19/20 成功，S15 重试后 20/20 可达
- 匹配器修复后复算：61/78
- 单元测试：38 passed
- S19 截断警告已确认触发

## 失败与阻塞

- S15 首次调用返回空内容 → 重试 OK，分类为 API 瞬时故障（已记录，不改产品）
- 匹配器两处 bug 均为测量工具问题，非产品问题；修复后未重跑模型即完成复算
- S09 英文 schema 未过、S17 证据跳句 → 列为 Day 10 修复项，今日未改提示词（保持一次一改一回归的节奏）

## 关联文件

- `../../log/2026-10-01.md`
- `../../projects/L1-longtext-struct/scripts/build_evalset.py`
- `../../projects/L1-longtext-struct/scripts/make_table_pdf.py`
- `../../projects/L1-longtext-struct/tests/eval_set.json`
- `../../projects/L1-longtext-struct/run_eval.py`、`rescore.py`
- `../../plans/AI产品经理学习实践计划表.xlsx`