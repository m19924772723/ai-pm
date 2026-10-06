# Fallback

## 成果日期
2026-10-06

## 今日成果

1. **跨端点故障转移落地**：`pipeline.structure(..., allow_fallback=True)` 默认开启；主端点失败自动改用下一个可用端点，结果带 `fallback_from`、warnings 记录转移原因。
2. **真实场景双验证**：用真的失效端点 siyu（403 订阅失效）验证——开 fallback 时自动切到 stepfun 并成功（5 要点/schema 通过/0 证据问题）；关 fallback 时如实失败。
3. **评测方法沉淀文档** `docs/L1评测方法.md`：三指标算法与限界、评测集构建矩阵、复算能力、**四类失败框架**（真 bug / 依赖故障 / 测量工具 / 策略）、匹配器三重坑、报告写法、L2/L3 复用清单。
4. 项目 README 终版更新；单测 38 → **41 passed**。

## 关键数字

| 项 | 值 |
|---|---|
| 故障转移验证 | siyu(403) → stepfun 接管，ok=True，schema 通过 |
| 单测 | 41 passed |
| 新增文档 | `docs/L1评测方法.md` |

## 可复用成果

- 故障转移代码：`../../projects/L1-longtext-struct/pipeline.py`（`_provider_candidates` + `allow_fallback`）
- 验证证据：`../../projects/L1-longtext-struct/logs/day14_fallback_data.json`
- 评测方法（L2/L3 复用）：`../../docs/L1评测方法.md`
- 部署方案：`../../docs/L1部署上线方案.md`

## 原始记录

- `../../log/2026-10-06.md`
