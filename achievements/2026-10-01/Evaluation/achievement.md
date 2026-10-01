# Evaluation

## 成果日期
2026-10-01

## 今日成果

1. **20 条评测集建成**（`scripts/build_evalset.py` → `tests/eval_set.json`）：短10/中8/长1/超长1，中文15/英文3/中英混合2，summary9/todos6/archive5，真实来源3，78 个 gold 点（draft_manual）。
2. **含表格 PDF 样本真实化**：`scripts/make_table_pdf.py` 生成 → `extract_from_pdf` 真实提取文本作 S14 输入。
3. **首轮 20 条全量评测出数字**：格式合规率 90%、要点覆盖率 78.2%（匹配器 v2）、幻觉率 1.05%。
4. **S15 偶发失败重试通过**：分类为 API 瞬时故障。
5. **修复匹配器两个 bug**：英文结果未进 shingles 集合；`_norm` 去空格导致英文单词边界丢失。38 测试全过。
6. **S19 超长截断路径验证**：42119 字正确截断 + 警告，不崩溃。
7. 17 条未命中逐条分类（改写/语言切换/字段分离/行为样本），定位 2 个真问题（S09 英文 schema、S17 证据跳句）。

## 关键数字

| 指标 | 数字 |
|---|---|
| 评测集 | 20 条 / 78 gold |
| 格式合规率 | 18/20 = 90% |
| 要点覆盖率 | 61/78 = 78.2%（v2 匹配器复算；评测时旧匹配器 67.1%） |
| 幻觉率 | 1/95 = 1.05% |
| 超长截断 | ✅ 正确截断 + 警告 |
| 单元测试 | 38 passed |

## 可复用成果

- 评测集构建：`../../projects/L1-longtext-struct/scripts/build_evalset.py`
- 表格 PDF：`../../projects/L1-longtext-struct/scripts/make_table_pdf.py`
- 评测集：`../../projects/L1-longtext-struct/tests/eval_set.json`
- 评测结果：`../../projects/L1-longtext-struct/logs/eval_eval20_*.json`
- 复算结果：`../../projects/L1-longtext-struct/logs/rescore_eval_eval20_*.json`

## 原始记录

- `../../log/2026-10-01.md`
