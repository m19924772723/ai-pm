# logs/ 证据索引

这里是 L1 的**真实运行证据**。所有数字都从这里产出，不手写。

| 文件 | 端点 | 格式合规率 | 要点覆盖率 | 幻觉率 | 说明 |
|---|---|---|---|---|---|
| `eval_day5_20260927_2338.json` | siyu / deepseek-v4-flash | 0.0 | 0.0 | 0 | ❌ 整轮失败：403 SUBSCRIPTION_NOT_FOUND（**依赖故障，非代码问题**） |
| `eval_day5_stepfun_20260927_2342.json` | stepfun / step-3.7-flash | 0.75 | 0.1538 | 0.0 | 修复前：S04 因 max_tokens=4096 被截断；覆盖率受逐字匹配器假阴性拖累 |
| `eval_day5_fixed_20260927_2345.json` | stepfun / step-3.7-flash | **1.0** | **0.5385** | **0.0** | 修复后：max_tokens=8192 + 截断检测；覆盖率数字仍是 v1 逐字匹配器 |
| `rescore_eval_day5_fixed_20260927_2345.json` | — | — | **0.9231** | — | 用 v2 二元组匹配器对**同一批输出**复算，不重新调用模型 |
| `day5_eval_console.txt` | stepfun | — | — | — | `run_eval.py` 的控制台输出（修复前那次） |

## 怎么读这组数字

1. **格式合规率 0.75 → 1.0**：不是模型变强了，是修掉了 max_tokens 截断。
2. **覆盖率 0.5385 → 0.9231**：差异全部来自**匹配器**，模型输出没变（同一份 `eval_day5_fixed_*.json`）。
   v1 要求整串逐字出现，中文多一个"的"就判失败。
3. **幻觉率 0/14**：14 条 `evidence` 全部能在原文中定位——这是 evidence 约束生效的直接证据。

## 复现命令

```bash
cd projects/L1-longtext-struct
.venv/Scripts/python.exe scripts_probe.py                              # 先确认端点可用
.venv/Scripts/python.exe run_eval.py --provider stepfun --tag rerun    # 重跑（花 API 费用）
.venv/Scripts/python.exe rescore.py "logs/eval_day5_fixed_*.json"      # 复算（不花费用）
```

> ⚠️ 样本仅 4 条，匹配器为字面级近似。**这些数字只用来说明链路可用，不构成效果结论**；
> 真实覆盖率以第 4 周人工核对为准。
