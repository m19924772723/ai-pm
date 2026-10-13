# operations · 2026-10-13（Metrics4）

## 操作序列
1. 核对计划表 → 今日 L2 W3：跑 4 检索指标 + 失败分类
2. 升级 retrieval_eval.py：读 tests/qa_eval_set.json 的 20 条有答案题，新增上下文相关性（top5 相关块占比）
3. build_index --check → in_sync=false → 重建（缓存秒级）
4. 跑检索评测（20 条，8s）：召回 90%、上下文相关性 30%、MRR 0.527
5. 失败明细归类（词面重叠题被稀释 vs 同义改写题真漏）
6. 学习线：抓 woshipm《RAG落地复盘与检索优化》6727 字 → 精读笔记（六坑映射 + W4 清单）
7. 写 docs/L2指标汇总-W3.md（4 指标 + 关系 + 口径）
8. 日志 + 归档 + 计划表打勾 + 提交

## 令牌纪律
- 密钥仅环境变量；本轮无 LLM 评测调用（检索指标纯本地 + embedding 缓存）
- 精读抓取 2 次（腾讯云失败换 woshipm）

## 失败与修复
- 腾讯云 JS 渲染抓不到 → 换 woshipm 原文（主题更对口）
- 索引又过期（in_sync=false）→ 重建；教训：评测前必查 --check 成为条件反射

## 未完成 / 记录
- W4：Rerank 精排 + 查询改写（治上下文相关性 30%）
- gold 用户抽查 → reviewed