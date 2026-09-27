# L1-1 长文结构化（练手项目）

> 阶梯第 1 级（提示词级）。**不计入正式作品集**——正式案例从 L2 开始。
> 但它的评测方法和踩坑日志会被 L2/L3 复用。

## 一句话

贴一段长文、一个链接或一份 PDF，输出结构化的**摘要 / 关键点 / 标签 / 待办**，每条关键点都带**原文依据**，可切换模板、可一键导出 Markdown。

## 现在能做什么（Day 5 实测，2026-09-27）

| 能力 | 状态 |
|---|---|
| 文本 → 结构化 JSON（摘要模板） | ✅ 已真实调通 |
| JSON 一次解析 + Schema 校验 | ✅ 29 个离线单测通过 |
| 证据回溯检查（幻觉第一道防线） | ✅ 已实现 |
| 待办模板 / 归档模板 | ✅ 已实现并跑通评测 |
| 截断检测（finish_reason / 括号配对） | ✅ 已实现，修掉了 4096 token 截断问题 |
| 网页抓取（trafilatura + 兜底规则） | ✅ 已实现，待真实样例验证失败率 |
| PDF 提取（PyMuPDF） | ✅ 已实现，扫描件明确报错不硬扛 |
| Streamlit 界面 | ✅ 已实现，待手工走查 |
| 20 条评测集 | ⬜ 现 4 条，第 4 周补齐 |

## Day 5 首轮评测数字（4 条样本，stepfun / step-3.7-flash）

| 指标 | 结果 | 依据 |
|---|---|---|
| 格式合规率 | **4/4 = 100%** | 4 条均 `finish_reason=stop`，JSON 可解析且 Schema 通过 |
| 幻觉率 | **0/14 = 0%** | 14 条 evidence 全部能在原文中定位 |
| 要点覆盖率 | **12/13 = 92.3%**（v2 匹配器） | 同批输出用 v1 逐字匹配只有 7/13 = 53.8% |
| 单条耗时 | 8.5–20.9 s | 4 条实测 |
| 单条输出 | 1582–3421 completion tokens | 说明输出预算需 ≥8192，4096 会截断 |

> **重要说明**：覆盖率两个数字的差异来自**匹配器**，不是模型。
> v1 要求整串逐字出现，中文多一个"的"就判失败（"产品经理核心能力" vs "产品经理**的**核心能力"）。
> v2 改为二元组重叠 ≥0.6 且数字必须命中。两个匹配器都是字面级近似，
> **真实覆盖率以第 4 周人工核对为准**——现在只有 4 条样本，不构成结论。
> 复算不需要重跑模型：`rescore.py logs/eval_day5_fixed_*.json`。

## 快速开始

```bash
# 1) 建环境
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt

# 2) 配密钥（只放环境变量，不进仓库）
export SIYU_API_KEY=...        # 或复制 .env.example 为 .env

# 3) 离线单测（不花 API 费用）
.venv/Scripts/python.exe -m pytest tests -q

# 4) 真实链路验证（一次调用）
.venv/Scripts/python.exe scripts_verify.py

# 5) 跑评测集，出三个指标
.venv/Scripts/python.exe run_eval.py --tag day5

# 6) 起界面
.venv/Scripts/streamlit.exe run app.py
```

## 目录

```
L1-longtext-struct/
├── app.py                  # Streamlit 界面（输入 3 种 + 3 模板 + 展示导出）
├── pipeline.py             # 核心链路：文本 → 结构化 JSON（与界面解耦）
├── scripts_verify.py       # 一次真实调用，验证链路
├── run_eval.py             # 跑评测集，算 3 个指标，写 logs/
├── prompts/templates.py    # 3 套提示词（与 docs/L1提示词初稿.md 保持一致）
├── utils/llm.py            # 模型调用封装（密钥只从环境变量读）
├── utils/schema.py         # JSON 提取 + Schema 校验 + 证据回溯
├── extractors/web.py       # 网页正文提取 + 兜底
├── extractors/pdf.py       # PDF 提取
├── tests/eval_set.json     # 评测集（现 4 条，目标 20 条）
├── tests/test_schema.py    # 22 个离线单测
├── data/sample_inputs/     # 测试输入
└── logs/                   # 评测结果与运行记录
```

## 三个指标怎么算

| 指标 | 算法 | 目标 |
|---|---|---|
| 格式合规率 | JSON 一次解析成功且 Schema 通过的样本 / 全部样本 | 95%+ |
| 要点覆盖率 | 命中的 gold_points / 全部 gold_points | 50% → 70%+ |
| 幻觉率 | 有问题的 evidence 条数 / 全部 evidence 条数 | < 5% |

> 数字由 `run_eval.py` 产出，写在 `logs/eval_*.json`。**不手写数字。**

## L1 明确不做

登录 / 多用户 · 云端历史同步 · 批量处理 · 浏览器插件 · 多语言 · 自定义模板。

## 已知边界

- 单次输入上限 24000 字，超出直接截断（分块策略待迭代）
- 扫描版 PDF 不支持（不做 OCR）
- 一次调用出结果，不做多轮追问
