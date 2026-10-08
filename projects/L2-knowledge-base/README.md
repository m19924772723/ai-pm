# L2-1 个人知识库问答（案例①）· W1 索引已跑通

> 第一个正式作品集案例。文档索引：把自己的资料（docs/log/计划）做成可以问的库。
> **当前状态：W1 完成**（语料 36 篇 → 501 块 → 索引 → 混合检索 Recall@5=90%）

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
python -m scripts.build_index            # 增量（embedding 有磁盘缓存，秒级）
python -m scripts.build_index --reset    # 清空重建
python -m scripts.build_index --check    # 只检查索引与语料是否同步
```

### 4) 检索
```bash
python -m scripts.search_test "跨端点故障转移是做什么的"
```
输出 Top-5 块，每块带 **doc + heading + 原始字符偏移**——偏移是"引用能高亮到原文"的基础。

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
index/retriever.py     混合检索：稠密 + 中文二元组 BM25 → RRF 融合
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
3. **语料不复制**：直接索引工作区 36 篇真实文档，sha1 指纹判断同步，指标全可复现。
4. **embedding 缓存**：缓存键 = sha1(模型+文本)，改模型/改文本自动失效，重建秒级。

## 已知边界（诚实记录）

- 评测集 10 问 gold 为草案状态（自己标的），需人工复核后转正式
- embedding 模型中文区分弱是已知短板 → 后续候选：本地 BGE 小模型（bge-small-zh-v1.5，零 API 成本）；
  换模型后重建缓存自动失效，用同一套 retrieval_eval 对比数字
- "Day 5 完成了什么"这类跨日期模糊问法仍会漏（日期归一化是 W2 候选改进）
- ASCII 线框图块对稠密检索有污染（BM25 融合后已被中和）
- 尚未接生成（W2：检索 → 答案 + 引用高亮）

## 本周（L2 W1）验收

- [x] 语料整理：36 篇真实文档，130,192 字
- [x] 分块策略：501 块，硬不变量有测试（12 个离线单测）
- [x] 索引跑通：build_index → Chroma 持久化 → 检索返回带偏移的块
- [x] 检索质量有数字：Recall@5 90% / MRR 0.518（混合）vs 0%（稠密对照）