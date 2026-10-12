# RRF 候选池 + 语料补全（Day 20 检索修复）

**成果词**：HybridRecallFix —— 30 条评测逼出的检索真 bug 与语料范围缺陷

## 事由

30 条正式评测集首轮：引用准确率 40%（8/20）。比 W2 的 90% 大滑坡——不是系统变差，
是评测集变大暴露出小样本没暴露的问题。

## 归因（13 条失败 = 三类，不是数字表面那么糟）

### ① 检索真 bug（最重要）：混合检索 RRF 在全库算，lexical 强命中被 dense 稀释
- "如何重建 L2 索引"：正确块（含 build_index 命令）**BM25 词面排名第 1**
- 但 nemotron embedding（中文弱）给它的 dense 排名是 147
- 全库 RRF 融合后掉到 19 → 没进 top-5 → LLM 拿到无关块 → 误拒答
- **根因**：名义上"稠密+词面融合"，实际 dense 主导；lexical 强命中是稀缺信号却被淹没

### ② 语料范围缺陷（2 条）：操作类问题的答案在项目 README，不在知识库
- "如何重建 L2 索引"/"怎么验证索引同步"的官方答案是 README 的 `python -m scripts.build_index`
- 但语料只含 docs/log，不含 projects/*/README.md

### ③ gold 标窄（5 条）+ 真检索短板（同义改写题）
- 幻觉率/要点覆盖率/向量库/复盘/满意度：系统引了真实来源，gold 没含 → 评测集问题
- "L1 用了哪个界面框架"：正确块 dense_rank=89/lex_rank=192 都没进 top-5 → 同义改写题，
  embedding 弱 + 词面不重叠，是真实短板（非 RRF 能解，W4 优化项）

## 修复

1. **RRF 候选池**（index/retriever.py search_all）：
   - 候选池 = dense top-k ∪ lexical top-k（lexical 强制保底）
   - RRF 在候选池内重算，词面强命中块在池内 rank 靠前必进 top-k
   - 配回归测试 `test_lexical_topk_always_in_results`
   - 验证：build_index 块从"top-5 外" → "top-5 第 3 位"
2. **语料补全**（config.py CORPUS_SOURCES）：加 `projects/L2-knowledge-base/README.md`
   （项目用户手册——操作命令的官方文档，本就该在知识库）
   - 44 篇语料，重建索引 in_sync=true
   - 验证："如何重建 L2 索引"命中 README 块（第 3 位）

## 为什么这件事重要

- **评测集规模是质检器**：10 条草案看着 90%，扩到 30 条立刻现形——评测集要早扩、正式化
- **不能无限调系统拟合不准的 gold**：13 条失败里 5 条是 gold 标窄，1-2 条是语料范围，
  真正该修的是 RRF 候选池（②③属于评测/语料的补齐，不是模型问题）
- 每个修复都有"修前现象 → 根因 → 修法 → 验证"完整证据链（面试讲"失败怎么排查"的弹药）

## 可复现

```bash
python -m scripts.qa_eval --out logs/qa_eval_w3_v3.json   # 三重改进后评测
python -m pytest tests -q                                  # 38 单测
```

## 当前数字（v3 评测跑完后填）

- 引用准确率 / 拒答正确率：待填（后台 30 条全量评测中）