# MVPSmoke（MVP 三功能联调自测）

**成果词**：MVPSmoke —— L2 MVP 三项功能端到端可用，一次通过

## 做成了什么

`scripts/mvp_smoke.py`：一条命令联调并自测 6 个用例（4 问答 + 2 拒答），每用例验证：
1. **功能①索引**：语料/索引块数相符（40 篇/536 块）
2. **功能②问答**：答案带引用（可核查断言有出处）或正确拒答
3. **功能③引用定位**：每条引用 quote 落在磁盘文件偏移切片内 + docpath 可解析

结果：**6/6 通过 · 199s**，落盘 `logs/mvp_smoke.json`。

## 为什么这件事重要

MVP 从"每个功能单独能跑"到"三功能联调一次过"是里程碑：
- 此前"分块偏移"用例在 demo/评测里反复失败，今天引用定位 ✓ → 印证根因是索引过期（已修）
- 每轮 3 次 stepfun 瞬态失败被 fallback 自动救回 → 故障转移是必需
- 验收方式可复现：任何改动后重跑 mvp_smoke 即可回归

## 可复现

```bash
python -m scripts.mvp_smoke          # 6/6 联调自测（约 3 分钟）
python -m pytest tests -q            # 37 单测
python -m scripts.build_index --check  # 索引同步
```