# L2-1 个人知识库问答（案例①）

> 第一个正式作品集案例。文档索引：把自己的资料（docs/log/计划）做成可以问的库。
> **当前状态：W4 检索优化中**（Day 22：cross-encoder 重排上线——召回 100% / MRR 0.71 / 上下文相关性 55%，目标 60%）

## 当前四指标（Day 22，2026-10-14，30 条评测集）

| 指标 | Day21（RRF） | Day22（rerank） | 目标 |
|---|---|---|---|
| 召回率 Recall@5 | 90%（18/20） | **100%（20/20）** | ≥90% |
| MRR | 0.552 | **0.713** | - |
| 上下文相关性 | 30%（旧 gold）/ 38%（修正 gold） | **55%** | ≥60%（差 5pp） |
| 引用准确率 / 拒答 | 80% / 100% | 见 logs/qa_eval_w4.json | ≥95% / ≥90% |

> ⚠️ Day 22 修正了评测口径（不是调数字）：语料 42→48 篇后，原 gold（10-12 标注）偏窄——
> 9 题补录了确实含答案的新增文档（逐块核对过），旧 gold 一项未删。修正只把「测量」补齐，系统提升单独看：
> 同一修正 gold 下 RRF=38% → rerank=55%（+17pp）；同一旧 gold 下 30%→35%（+5pp）。

## 怎么用

### 1) 建环境（一次性）
```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 2) 配置密钥
把 `TUOJI_API_KEY` 放进环境变量（或 `.env`，已被 .gitignore 排除，永不提交）。
embedding 走内部中转站：`api.tuoji.top` + `nemotron-3-embed-1b`（2048 维）。

### 3) 重建索引（语料变了才需要）
```bash
python -m scripts.build_index --check    # 先检查索引与语料是否同步！
python -m scripts.build_index            # 增量（embedding 有磁盘缓存，秒级）
python -m scripts.build_index --reset    # 清空重建
```
> ⚠️ **Day 18 踩坑**：语料每天在变（log/ + docs/ 新增），索引会过期。
> 症状 = 检索"偶尔"漏掉新文档、问答引用错误。**评测/问答前先 `--check`，`in_sync: false` 就先重建**。

### 4) 检索
```bash
python -m scripts.search_test "跨端点故障转移是做什么的"
```
输出 Top-5 块，每块带 **doc + heading + 原始字符偏移**——偏移是"引用能高亮到原文"的基础。
Day 22 起检索 = 候选池（稠密 top-30 ∪ 词面 top-30）→ **bce-reranker 重排**（本地 cross-encoder，零 API 成本）。
重排分数有磁盘缓存（`data/rerank_cache.json`）；模型目录缺失时自动回退纯 RRF（旧行为）。

```bash
python -m scripts.retrieval_eval          # 四指标（召回/MRR/上下文相关性）含重排
L2_RERANK_MODEL_DIR=...  python ...       # 可用环境变量覆盖重排模型目录
```

### 5) 评测
```bash
python -m scripts.retrieval_eval --hybrid   # 混合（默认）
python -m scripts.retrieval_eval --dense    # 稠密对照
```

## 结构

```
config.py              语料来源/分块参数/端点配置（改配置只改这一处）
corpus/loader.py       语料加载（不复制文件，直接读原路径 + sha1 指纹）
corpus/chunker.py      分块：标题层级切段 + 长段句子窗口（带字符偏移，可精确引用）
index/embed.py         embedding 客户端（磁盘缓存，重建不重复付费）
index/store.py         Chroma 封装（cosine，元数据带 char_start/char_end）
index/retriever.py     混合检索：稠密 + 中文二元组 BM25 → 候选池 →（重排/RRF 二选一）
index/rerank.py         bce-reranker 本地重排器（CPU + fp16 + 磁盘缓存，Day 22 新增）
scripts/build_index.py 建索引 CLI（--reset / --check）
scripts/search_test.py Top-K 检索自测
scripts/retrieval_eval.py 10 问评测（Recall@5 / MRR）
tests/                 19 个离线单测
data/index/            Chroma 持久化（gitignore）
data/embed_cache/      embedding 缓存（gitignore）
```

## 关键决策（面试要讲）

1. **分块策略：标题优先 + 句子窗口兜底，512 字上限 + 64 字重叠**
   每块记录原文 char_start/char_end，保证"引用可以精确高亮到原文某一段"。
   硬不变量有测试：块文本 == 原文切片、无块超限、正文不丢（只允许丢空白与短碎片）。
2. **混合检索（稠密 + BM25 融合），不是纯向量**
   实测：中转站唯一可用 embedding（nemotron-3-embed-1b）对中文区分不足，
   501 个块相关度全挤在 0.69~0.82，纯稠密 10 问 Recall@5 = **0/10**，Top1 是 ASCII 线框图。
   加中文二元组 BM25 + RRF 融合后 = **9/10（90%），MRR 0.518**。
   教训：**检索质量先测再信，指标要能复现（`--dense` 对照一键跑）**。
3. **语料不复制**：直接索引工作区 48 篇真实文档，sha1 指纹判断同步，指标全可复现。
4. **embedding 缓存**：缓存键 = sha1(模型+文本)，改模型/改文本自动失效，重建秒级。
5. **重排救检索噪声（Day 22）**：RRF 把两榜 top 全让给每日日志（ctx 30%），换
   bce-reranker-base_v1 重排后 MRR 0.55→0.71、召回 90→100%、ctx 30→55%。
   但跨编码器对「操作命令题」（重建索引/build_index）和「同义改写题」（界面框架 vs Streamlit）仍弱——
   W4 剩：查询改写 + 命令题词面兜底。

## 已知边界（诚实记录）

- 评测集 30 条 gold 为 **draft_manual**（2026-10-14 补录过 9 题，仍待用户抽查后转 reviewed）
- 上下文相关性 55% 未达 60% 目标：剩两类检索缺口——①同义改写题（"界面框架" vs 原文"前端/UI Streamlit"，
  词面不重叠、embedding 中文弱），W4 计划做查询改写；②操作命令题（"如何重建 L2 索引"），
  cross-encoder 对代码命令块评分偏低，W4 计划词面兜底
- "Day 5 完成了什么"跨日期问法：评测里 Day 5/Day 15 的 gold 依赖日期-天数映射，仍不稳（日期归一化候选）
- 重排推理在 CPU（fp16）约 1s/对，单问检索 ~30-60s（分数有磁盘缓存，重复问秒回）
- ASCII 线框图块对稠密检索有污染（BM25 融合后已被中和）
- L1/L2 接口（问答 + 引用高亮）已在 mvp_smoke 验证，Streamlit 界面仍未接

## 本周（L2 W1）验收

- [x] 语料整理：36 篇真实文档，130,192 字
- [x] 分块策略：501 块，硬不变量有测试（12 个离线单测）
- [x] 索引跑通：build_index → Chroma 持久化 → 检索返回带偏移的块
- [x] 检索质量有数字：Recall@5 90% / MRR 0.518（混合）vs 0%（稠密对照）