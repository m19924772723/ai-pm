# operations · 2026-10-12（QAEvalSet）

## 操作序列
1. 核对计划表 → 今日 L2 W3：建 30 条评测集（含 10 条无答案）
2. 统计语料：42 篇（docs 23 + log 19）
3. 写 scripts/build_qa_evalset.py（30 条 + 类型标签 + gold 多候选 + **gold 存在性自校验**）
4. 首跑：校验抓到 2 条无效 gold（projects/README 不在语料）→ 修正为 log/2026-10-08/10-10 → 全过
5. 生成 tests/qa_eval_set.json（30 条, gold_status=draft_manual）
6. build_index --check → in_sync=false（语料 42 篇）→ 重建 → in_sync=true
7. qa_eval.py 升级为从评测集读取（去硬编码），保留 _answer_with_retry
8. 37 单测全过；启动 30 条全量评测（后台）

## 令牌纪律
- 密钥仅环境变量；本轮 LLM 调用 = 30 条评测（后台，约 15 分钟）+ 检索缓存命中

## 失败与修复
- 2 条 gold 无效（指向 projects/README 不在语料）→ 构建脚本自校验当场抓出，修正
- （下一轮若评测数字异常，先看是不是索引又过期——--check 纪律）

## 未完成 / 记录
- 全量评测数字待填
- 上下文相关性指标 + 失败分类（W3 后续）
- gold 待用户抽查后转 reviewed