# operations · 2026-10-12（HybridRecallFix）

## 操作序列
1. 建 30 条评测集（build_qa_evalset.py，gold 自校验抓出 2 条无效 gold）
2. qa_eval.py 升级为从评测集读取；索引同步（42 篇）
3. 首轮全量评测：引用 40%（8/20），拒答 100%
4. 归因：6 误拒答 + 5 gold 漏标 + 1 真空引用
5. 诊断"如何重建索引"：检索 top5 无 build_index 块 → 查 BM25/dense 排名
   → 正确块 lex_rank=1/dense_rank=147/全库 RRF 后 19 名 → RRF 候选池缺陷
6. 修 retriever.py：候选池 dense-topk ∪ lex-topk + 池内 RRF；回归测试
7. v2 评测：仍 35% → 深查：检索已好（build_index 块进 top5）但 LLM 仍拒
   → 看块内容：README 的 build_index 命令不在语料（log 块只提到 --check 没写命令）
8. 审计 13 条失败 gold 指向的块 → 确认 ②语料范围缺陷（操作题答案在 README）
9. 修 config.py：加 projects/L2-knowledge-base/README.md 进语料；重建索引（44 篇）
10. 验证：操作题命中 README 块；38 单测过；启动 v3 评测（后台）

## 令牌纪律
- 密钥仅环境变量；本轮 LLM 调用 = 3 次评测（30 条 × 40/35）+ 若干诊断，embedding 缓存命中

## 失败与修复（诚实记录）
- 首轮 40% → 修 RRF 候选池 → v2 35%（检索好了但 LLM 仍拒，因答案不在语料）
  → 补 README 进语料 → v3（待数字）
- 认知纠偏：v2 后一度以为"LLM 拒答过严"，深查才发现是语料没有答案——先查数据再怪模型

## 未完成 / 记录
- v3 评测数字待填
- gold 标窄 5 条：rescore（不重跑模型）或补 gold
- 同义改写题（"界面框架"）检索短板 → W4 优化
- 上下文相关性指标（W3 剩余）