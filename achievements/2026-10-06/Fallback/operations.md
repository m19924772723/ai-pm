# Fallback Operations

## 操作记录

1. 改 `pipeline.py`：
   - 新增 `_provider_candidates(explicit, allow_fallback)`（显式端点排第一 + 默认顺序兜底，去重）
   - `structure()` 改为多端点尝试循环，记录 `attempts`；成功时把失败端点写入 `fallback_from` 并追加 warning
   - `StructResult` 增加 `fallback_from` 字段；全部失败时报"全部端点失败（N 个）+ 每个端点原因"
2. 新增 3 条离线单测（候选顺序：关 fallback 只试显式、开 fallback 显式排第一且不重复、无显式时用默认顺序）。
3. 真实双场景验证（`logs/day14_fallback_data.json`）：
   - A：`provider='siyu', allow_fallback=True` → ok=True，实际用 stepfun，fallback_from=['siyu']
   - B：`provider='siyu', allow_fallback=False` → ok=False，错误如实上报
4. 写 `docs/L1评测方法.md`（评测方法沉淀）。
5. 更新项目 README（故障转移状态、测试数 41、已完成待办表述）。
6. 全量测试 41 passed。

## 验证结果

- 场景 A：ok=True、schema=True、key_points=5、ev_issues=0、fallback_from=['siyu']、warning 含转移原因
- 场景 B：ok=False、"全部端点失败（1 个）"
- 单测：41 passed

## 失败与阻塞

- 场景 B 中 siyu 的错误从 403 变成 ConnectError（端点网络抖动），但错误如实上报未吞
- 仍待用户：部署上线（需账号操作）、评测集 gold 抽查复核

## 关联文件

- `../../log/2026-10-06.md`
- `../../projects/L1-longtext-struct/pipeline.py`
- `../../docs/L1评测方法.md`
- `../../projects/L1-longtext-struct/logs/day14_fallback_data.json`
