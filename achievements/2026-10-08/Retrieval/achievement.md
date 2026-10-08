# Retrieval（索引与混合检索跑通）

**成果词**：Retrieval —— L2 首个作品集案例的索引与检索引擎

## 做成了什么

| 项 | 结果 |
|---|---|
| 语料 | 36 篇真实工作区文档（docs/log），130,192 字，sha1 指纹 |
| 分块 | 501 块，标题层级 + 句子窗口（512/64/40），精确字符偏移 |
| 索引 | Chroma 持久化 + manifest，--check 同步校验 |
| 检索 | **混合检索（稠密 + 中文二元组 BM25 + RRF）** |
| 评测 | Recall@5 **90%**（9/10）/ MRR 0.518，稠密对照 0% |
| 质量 | 21 个离线单测全过；引用偏移端到端核验 3/3 |

## 为什么这件事重要

L2 被定义为第一个正式作品集案例。W1 就把"检索质量用数字管住"落地了：
- **纯稠密检索在真实中文语料上会是 0 分**——这个发现如果不是实测，到了面试才会露馅
- 混合检索不是"锦上添花"，是**这次语料/模型组合下的必要手段**（embeddimng 模型中文区分不足）
- 每条失败都可以复现：`--dense` 对照一键重跑，指标有脚本产出

## 可复现

```bash
python -m scripts.build_index --check   # 索引与语料同步？
python -m scripts.retrieval_eval --dense    # 0/10（对照）
python -m scripts.retrieval_eval --hybrid   # 9/10, MRR 0.518
python -m scripts.search_test "跨端点故障转移是做什么的"
```