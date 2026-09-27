# Scaffold Operations

## 操作记录

1. 核对计划表：修正 09-27 / 09-28 / 09-29 三天仍挂着 Day 1 旧任务的问题。
2. 建独立虚拟环境：`uv venv --python 3.11 .venv`，用清华镜像安装 streamlit、trafilatura、pymupdf、httpx、jsonschema、pytest。
3. 写项目文件：
   - `pipeline.py` 核心链路（与界面解耦）
   - `prompts/templates.py` 三套提示词
   - `utils/llm.py` 模型调用封装（密钥只从环境变量读）
   - `utils/schema.py` JSON 提取 + Schema 校验 + 证据回溯
   - `extractors/web.py`、`extractors/pdf.py` 输入层
   - `app.py` Streamlit 界面
   - `tests/eval_set.json` 评测集（4 条起步）
   - `tests/test_schema.py`、`tests/test_eval_matcher.py` 单元测试
   - `run_eval.py`、`rescore.py`、`scripts_probe.py`、`scripts_verify.py` 四个脚本
4. 修 bug 与迭代（每次都有真实验证）：
   - 提示词模板花括号被 `str.format()` 误解析 → 改显式占位符
   - max_tokens 4096 导致归档模板输出截断 → 提到 8192 + 加截断检测
   - 匹配器短路分支未归一化金标 → 两侧统一归一化
   - 匹配器由逐字整串改为二元组重叠 → 覆盖率复算 53.8% → 92.3%
   - 界面里一处硬编码的"通过"假指标 → 改为真实字段
5. 逐个探测 provider，定位 siyu 403 / tuoji 503 / deepseek 空返回 / stepfun 正常，调整默认顺序。
6. 跑评测并保存结果与日志。

## 验证结果

- 单元测试：29 passed（`.venv/Scripts/python.exe -m pytest tests -q`）
- 真实调用：4/4 成功，`finish_reason=stop`
- 评测结果文件：`logs/eval_day5_fixed_20260927_2345.json`
- 复算文件：`logs/rescore_eval_day5_fixed_20260927_2345.json`
- 依赖版本：streamlit 1.64.0 / trafilatura 2.2.0 / PyMuPDF 1.28.2 / httpx 0.28.1

## 失败与阻塞

- siyu 密钥返回 403 SUBSCRIPTION_NOT_FOUND，该 provider 本轮不可用（已在代码注释与 `.env.example` 标注）
- tuoji 的 `deepseek-v4-flash` 返回 503 无可用通道，改用该端点的 `kimi-k3` 验证可用
- Streamlit 界面已写完但**尚未手工走查**，网页抓取与 PDF 提取**尚无真实样例验证**

## 关联文件

- `../../log/2026-09-27.md`
- `../../projects/L1-longtext-struct/README.md`
- `../../plans/AI产品经理学习实践计划表.xlsx`（Day 5 行已更新）
