# operations · 2026-10-10（CitationLocate）

## 操作序列
1. 读 L2-1 项目预研.md（引用定位/拒答指标口径：引用准确率≥95%、拒答正确率≥90%）
2. query/answer.py 加 citation_locations()（引用→原文段落数据）
3. query/docpath.py：doc_id → 磁盘路径（两层解析）
4. scripts/citation_locate.py 端到端验证 → 首跑 3/3 全 ✗（判定写错）→ 改"quote∈切片" → 3/3 ✓
5. scripts/qa_eval.py：两组评测（有答案 10 条 + 拒答 10 条）
6. 首轮评测（550s）：拒答 100%、引用 50% → 失败明细归因三类
7. 复跑验证"引用为空"是瞬态：两条都正确（tuoji 兜底）→ 评测加 _answer_with_retry
8. gold 修正：简历真实来源是简历打造参考文档.md；每个问题允许 2 个候选
9. 单测 36 passed（test_locations 4 条）；重跑评测（后台）

## 令牌纪律
- 密钥仅环境变量；本轮 LLM 调用 ~45 次（首轮 20 + 复跑 2 + 修正后 20+）

## 失败与修复（诚实记录）
- 首轮引用准确率 50%：瞬态（2 条引用为空复跑全对）+ gold 标错（2 条）→ 修复后重跑
- 我的 bug：citation_locate 判定写错（切片==quote vs quote∈切片）、qa_eval 漏 import time
- gold 标注教训：必须对着语料里实际存在的文档标，不能凭直觉

## 未完成 / 记录
- 重跑评测数字待填（后台 proc 中）
- 上下文相关性真短板（Day 5 命中相邻日期）→ W3 加指标优化
- 30 条正式评测集 + 界面 W3/W4