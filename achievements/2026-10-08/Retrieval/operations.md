# operations · 2026-10-08（Retrieval）

## 操作序列
1. 探 embedding 端点：tuoji nemotron-3-embed-1b ✅（2048 维）/ nv-embed-v1 ❌ EOL；stepfun/deepseek 无 embedding
   → 确定 embedding 走 tuoji
2. 建 `projects/L2-knowledge-base/` 骨架 + uv venv 装 chromadb/httpx/streamlit/pytest（清华镜像，后台）
3. 写 config.py（语料 glob/分块参数/端点）→ corpus/loader.py（sha1 指纹）→ corpus/chunker.py（标题层级 + 句子窗口 + 偏移）
4. 包结构修正：直接跑文件 import 失败 → `touch __init__.py` + `python -m` 运行
5. 分块验证：501 块，最长超 512（604）→ 修 `_split_long` 边界 off-by-one + 硬切保险 → 最长恰 512，偏移自检 0 不符
6. 写 index/embed.py（磁盘缓存，键=sha1(模型+文本)）+ index/store.py（Chroma cosine + 元数据）+ scripts/build_index.py
7. 建索引：501 块写入成功（首批带缓存）；chunk_id 重复 bug → chunker 末尾统一重编号 + 全量唯一性验证
8. 检索初测：Top-K 全错（Top1 是 ASCII 线框图，命中不带查询词）→ 诊断三步：
   a) 向量退化？同文本 3 次调用 cos=1.00000 → 否
   b) Chroma 召回？numpy 全量余弦排序结果相同 → 否
   c) 根因：embedding 模型对中文区分不足（0.69~0.82 全挤在一起）
9. 写 index/retriever.py：lexical_tokens（中文二元组 + ASCII 词）→ BM25（k1=1.5,b=0.75）→ RRF(k=60) 融合
10. 写 scripts/retrieval_eval.py（10 问 gold 草案）+ scripts/diagnose_embed.py
11. 评测：稠密 0/10 → 混合 9/10（Recall@5 90% / MRR 0.518）
12. 修复自己评测脚本 2 个 bug（`g` 泄漏、startswith 方向）；单测全过 21
13. 引用偏移端到端核验 3/3（命中块文本 == 原文切片）
14. 项目配套：README / requirements.txt / .gitignore / .env.example

## 令牌纪律
- 密钥仅环境变量读取（os.environ），.env 不入库；本日无密钥写入任何文件
- TUOJI_API_KEY 已存在当前会话环境变量中，未复制到仓库文件

## 未完成 / 记录
- gold 10 问待人工复核
- W2 生成 + 引用高亮未开工（下一个单元）