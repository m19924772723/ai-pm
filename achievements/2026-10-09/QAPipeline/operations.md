# operations · 2026-10-09（QAPipeline + Reading）

## 操作序列
1. 读 L1 utils/llm.py（端点表/纪律）+ pipeline.py 40-118 行（故障转移模式）
2. 写 query/llm_error.py + query/llm_utils.py（端点表复制 + chat_with_fallback 内置故障转移循环）
3. 写 query/prompt.py（QA 提示词：只基于块回答/quote 逐字连续子串/固定中文/JSON Schema）
4. 写 query/answer.py（管线 + verify_quotes + extract_json + 检索端拒答 _relevant_ok）
5. 写 scripts/qa_demo.py（4 问验证）+ tests/test_qa.py（11 条）
6. 首跑 qa_demo：**4 个端点全失败** → 单测复刻 3/3 OK → 判定瞬态，给 answer 加重试 1 次
7. 二跑：链路通，但 quote_issues=3 条（模型写用户可见编号 "1"/"4"，schema 要内部名 chunk_0）
   → 修 check_citation_found（接受两种形式）+ answer 构造处统一解析 + 测试补齐
8. 三跑：Q1/Q2 引用全过校验；Q3 变"资料中没有"（覆盖不足，记录）；Q4 拒答正确
9. 学习线：L1 extractors/web.py 抓 woshipm《高质量RAG数据集》4694 字
   → 精读笔记 docs/woshipm精读-高质量RAG数据集.md（含 3 条对照发现）
10. 单测 32 passed 收尾

## 令牌纪律
- 密钥仅环境变量；无密钥写入仓库文件
- 本轮 LLM 调用 ~20 次（4 问 × 3 轮 + 诊断复刻），embedding 命中磁盘缓存

## 失败与修复（诚实记录）
- 首跑全端点失败：瞬态（非代码 bug）→ 加重试；错误串只带最后原因（待改进，已记录）
- chunk_id schema 不自洽：模型输出用户可见编号 → 解析器接受双形式
- deepseek 偶发非 JSON → JSON 失败纳入重试
- 我自己的 bug：import Hit 从 retriever 而非 store（ImportError）；测试期望与解析语义不一致修了 3 次

## 未完成 / 记录
- Q3 检索块覆盖不足（demo 命中的块不含"分块策略"段）→ W2 评测校准
- 30 条问答评测集未建
- 端点瞬态失败频率未统计（后续评测自然统计）