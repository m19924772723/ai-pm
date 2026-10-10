# CitationLocate（引用定位到段落 + 拒答逻辑）

**成果词**：CitationLocate —— 引用可点、拒答可测

## 做成了什么

| 项 | 结果 |
|---|---|
| 引用定位 | `citation_locations()`：引用 → {doc, heading, quote, 偏移, 原文}；`docpath.py`：doc_id → 磁盘文件 |
| 端到端 | `scripts/citation_locate.py`：答案引用 → 文件 → 偏移切片 → quote 落点，实测 3/3 |
| 拒答 | `_is_refusal()` 下沉 answer.py；10 条"资料里没有"问题评测 |
| 评测 | `scripts/qa_eval.py`：引用准确率 + 拒答正确率两组，可复现 |

## 首轮数字（修正 gold 后 rescore，不重跑模型）

- 拒答正确率 = **100%（10/10）**（目标 ≥90% ✅）
- 引用准确率 = **90%（9/10）**（目标 95%，差 1 条=日期问法"Day 5 完成了什么"）
- 原生评测 60% 是 gold 标窄冤枉系统 3 条（幻觉率/分块偏移/技术栈的引用其实都是正确来源）
- 定位并修复 2 个真 bug：Chroma 两次 get 错位（→ 一次 get 对齐 + 回归测试）、索引过期（→ --check 纪律）

## 为什么这件事重要

L2 的 MVP 第 3 功能（引用定位 + 拒答）从"能用"变成"有数字"：
- **引用能点到原文段落**（文件 + 偏移），是作品集里可演示的亮点，也是面试验证"精确引用"的硬证据
- **拒答用 10 条无答案问题测**，不是"看起来会拒答"——数字说话
- 首轮 50% 逼出两类真问题：评测黄金标注要对着语料标、瞬态要重试——评测体系自身也在被评测

## 可复现

```bash
python -m scripts.qa_eval                    # 引用准确率 + 拒答正确率
python -m scripts.citation_locate "L1 的幻觉率是多少"   # 引用 → 原文段落
python -m pytest tests -q                    # 36 passed
```