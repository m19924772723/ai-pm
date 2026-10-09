# QAPipeline（问答链路 + 引用块返回）

**成果词**：QAPipeline —— L2 从"能检索"到"能问答带引用"

## 做成了什么

| 项 | 结果 |
|---|---|
| 管线 | 检索 → 词面把关 → LLM（故障转移）→ JSON → **引用校验** → 答案 |
| 引用 | quote 必须块文本连续子串；命中块带 doc_id + 原文偏移（可高亮） |
| 拒答 | 检索无相关 → 直接拒答省一次 LLM；资料无答案 → unanswerable |
| 故障转移 | 复用 L1 端点表，fallback_from 全程可见（实测 stepfun→deepseek→tuoji 自动转移） |
| 瞬态 | 调用失败/JSON 解析失败重试 1 次（本轮实际触发并修好） |
| 质量 | 32 个离线单测全过；4 问验证：2 完整带引用 + 1 拒答 + 1 覆盖不足（记录） |

## 为什么这件事重要

问答链路的验收点不是"答案像不像样"，而是**每条引用能不能在原文定位**——
L1 用 evidence 连续子串校验学到的教训，在 L2 变成 citations 校验：
- 模型编的块编号（chunk_id 不在结果中）→ 校验拒绝 → 修解析器（接受用户可见编号）
- 改写/拼接的 quote → 校验拒绝（"未在块中找到"）
- 输出的引用带 doc_id + char_start/char_end → 界面可以直接做原文高亮

## 可复现

```bash
python -m scripts.qa_demo                      # 4 问演示（含拒答）
python -m pytest tests -q                      # 32 passed
```