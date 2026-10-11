# operations · 2026-10-11（MVPSmoke）

## 操作序列
1. 核对日期/计划表 → 今日 L2 W2 收尾：MVP 三功能联调 + 自测
2. build_index --check → in_sync=false（又新增文档）→ 重建索引（40 篇/536 块）
3. 写 scripts/mvp_smoke.py（6 用例 × 三功能验证 + 结果落盘 json）
4. 后台跑联调 → 6/6 通过（199s）
5. 周复盘 docs/周复盘-2026-10-11.md（W3：L1 收尾 + L2 开工，自评 8/10）

## 令牌纪律
- 密钥仅环境变量；本轮 LLM 调用 6 次（联调用例）+ 检索 embedding 缓存命中

## 观察
- stepfun 瞬态失败 3/6 用例（fallback 到 deepseek/tuoji）→ 故障转移必需
- 分块偏移用例恢复 ✓（索引过期修复的直接受益）

## 未完成 / 记录
- 30 条正式评测集 + 上下文相关性（W3）
- Streamlit 界面（W3/W4）