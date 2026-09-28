# Hello-Agents 学习索引（本地母本）

> **一句话**：Datawhale《从零开始构建智能体》开源教程 —— 16 章中文正文 + 每章可运行代码 + 14 篇补充 + 55 个社区共创 Agent 项目。
> **定位**：这是本仓库 **AI Agent 开发的统一参考库**。做 L2 / L3 / L4 需要「Agent 怎么写」时，第一站查这里，不再零散搜网页。

## 0. 本地位置与版本

| 项 | 值 |
|---|---|
| 实体路径 | `D:\code\hello-agents`（D 盘，不占 C 盘；缓存已在 `D:\code\environment\cache`） |
| 仓库内快捷入口 | `D:\code\hermes\ai_pm\references\hello-agents`（Windows 目录联接，指向上面同一份文件，不入 git） |
| 来源 | https://github.com/datawhalechina/hello-agents （★81.0k，2026-09-28 查询） |
| 入库版本 | `main` @ `8c57a6c`（2026-09-26 上游最后更新）｜浅克隆，2148 个文件 / 344 MB |
| 在线版（备用） | https://datawhalechina.github.io/hello-agents/ ｜ 国内加速 https://hello-agents.datawhale.cc |
| 要跑通代码的环境要求 | Python 3.10+，OpenAI 兼容接口（我们的 stepfun / deepseek 端点就是），配置文件见 `code/chapter4/.env.example` |

## 1. 怎么用（四条固定动线）

### 1.1 查概念 → 读本地 Markdown（离线、可 grep）

中文正文在 `docs/chapterN/第X章 xxx.md`，英文版是同一目录的 `ChapterN-xxx.md`。
图在 `docs/images/N-figures/`，**离线看的时候图片能正常显示**（相对路径都在）。

```bash
# 举例：读第七章「构建你的Agent框架」
start "" "D:\code\hello-agents\docs\chapter7\第七章 构建你的Agent框架.md"   # cmd 用 start

# 在全部 16 章里全文检索一个概念（比翻网页快）
cd /d/code/hello-agents/docs
rg -n "上下文工程" --glob "chapter*/*.md" | head -20
```

### 1.2 要参考实现 → 直接看 `code/`（有对应代码的章节能立刻跑）

```bash
cd /d/code/hello-agents/code/chapter4
cp .env.example .env        # 填 LLM_MODEL_ID / LLM_API_KEY / LLM_BASE_URL
python ReAct.py             # 第四章：ReAct 范式的完整实现
python Reflection.py        # 第四章：反思范式
python Plan_and_solve.py    # 第四章：计划-求解范式
```

> 注意：`code/chapter4/llm_client.py` 是全书最常用的 LLM 客户端（流式、OpenAI 兼容），
> 我们自己的 L1/L2 项目里那套「显式截断信号 + max_tokens 给足」的经验，可以直接跟它的实现对照。

### 1.3 要抄作业 → `Co-creation-projects/`（55 个社区共创项目）

按「名字-项目名」组织，每个都有 README + 可运行代码。挑同类型看它的目录结构和提示词写法。

```bash
ls /d/code/hello-agents/Co-creation-projects            # 55 个，按场景挑
ls -d /d/code/hello-agents/Co-creation-projects/*Agent* | head
# 例：`Apricity-InnocoreAI`（多 Agent 论文分析）、`CC1227871-StockInsightAgent`（RAG+反思的股票分析）
```

### 1.4 更新（上游仍在活跃更新）

```bash
cd /d/code/hello-agents && git pull --depth 1 origin main    # 浅克隆，只拉最新一次提交
```

## 2. 16 章地图（按「什么时候读」排，不要通读）

| 章 | 讲什么 | 什么时候读 | 用在哪 / 面试可答 |
|---|---|---|---|
| 一 初识智能体 | 智能体定义、与 LLM 的区别、工作流 vs 智能体 | 现在（背景知识） | 「AI 是不是必要的」——讲清工作流/Agent 的边界 |
| 二 智能体发展史 | ELIZA 到现代 Agent | 通勤扫读 | 讲产品演进史时的取材 |
| 三 大语言模型基础 | BPE、词向量、Transformer、采样 | 跳过正文细节，只在调参困惑时回查 | 解释「为什么 max_tokens 给不够会截断」 |
| **四 经典范式构建** | **ReAct / Reflection / Plan-and-Solve** | **做 L3 前必读** | L3 的提示词与流程骨架；「为什么用 ReAct 而不是工作流」 |
| 五 低代码平台搭建 | Coze / Dify / FastGPT / n8n | 想快速出原型时 | 「低代码 vs 代码」的产品取舍，PM 视角最对口 |
| 六 框架开发实践 | AgentScope / AutoGen / CAMEL / LangGraph | 选型时对照着读 | 「为什么选 LangGraph」要有对比依据，不要凭印象 |
| **七 构建你的 Agent 框架** | 自己实现 Agent 循环、工具、记忆 | **做 L3 前必读** | L3 的架构图来源；能讲清「框架帮我做了什么」 |
| **八 记忆与检索** | Memory 分层、RAG 管线、MarkItDown 文档处理 | **做 L2 时精读** | L2 的核心方法论（分块/检索/召回评估） |
| **九 上下文工程** | 上下文装配、笔记工具、终端工具、三日工作流 | **做 L3 时读** | 「上下文工程 ≠ 提示词」——AI PM 高频题 |
| 十 智能体通信协议 | MCP、A2A 等协议 | 研一下（L4 / 平台项目） | 讲生态与集成能力 |
| 十一 Agentic-RL | SFT → GRPO 训练 Agent | 了解即可 | 被问「模型怎么训的」时能接话 |
| **十二 智能体性能评估** | 评测维度、指标、基准 | **做 L1 评测延伸 / L3 收尾时读** | **直接对应面试问题 4/5**（效果怎么衡量、好不好） |
| 十三 智能旅行助手 | 前后端完整案例（FastAPI + Vue + 高德/Unsplash） | L4 时当架构参考 | 端到端产品的拆法 |
| 十四 自动化深度研究智能体 | Planner / Search / Summarizer / Reporter 流水线 | **L3 的首选参考实现** | L3 项目直接对标；面试讲架构最有力 |
| 十五 构建赛博小镇 | 多 Agent 社会模拟（Godot + 记忆系统） | 兴趣向 | 多 Agent 协作的想象力素材 |
| 十六 毕业设计 | 从教程到毕业设计的路径 | 暂缓（等选定导师） | — |

## 3. `Extra-Chapter/` 14 篇补充（按需取用）

| 文件 | 什么时候用 |
|---|---|
| `Extra01-面试问题总结.md` | **面试线直接用**：Agent 岗常见问题清单，和本仓 `docs/面试准备参考文档.md` 合并看待 |
| `Extra01-参考答案.md` | 上面那份的答案（240 KB，最厚的一篇） |
| `Extra02-上下文工程补充知识.md` | 第九章的延伸阅读 |
| `Extra03-Dify智能体创建保姆级操作流程.md` | 要出「低代码搭 Agent」的原型时照着做 |
| `Extra05-AgentSkills解读.md`、`Extra08-如何写出好的Skill.md` | 写自己的 Agent Skill 时对照；也解释了我们这套 skill 机制的行业背景 |
| `Extra06-GUIAgent科普与实战.md`、`Extra11-WebAgent科普与实战.md` | L3「浏览器 Agent」方向的产品与技术底稿 |
| `Extra07-环境配置.md` | **跑代码前先读这篇**：Python 版本、API Key、base_url、搜索工具怎么配 |
| `Extra09-Agent应用开发实践踩坑与经验分享.md` | 踩坑经验的横向对照（我们自己 `log/` 的踩坑日志可以跟它比） |
| `Extra10-Agent自进化.md`、`Extra12-旅行助手后训练实战.md` | 进阶，先放着 |
| `Additional-Chapter/N8N_INSTALL_GUIDE.md`、`NODEJS_INSTALL_GUIDE.md` | 要装 n8n / Node 时看（本机 Node 已在 `D:\code\environment\nodejs`） |

## 4. 与项目阶梯的对应关系（本仓 `README.md` 的 L1–L4）

| 阶段 | 从 hello-agents 取什么 |
|---|---|
| L1 长文结构化（进行中） | 第三章「采样参数」+ 第十二章「评估」→ 校准我们的截断信号与评测口径 |
| L2 检索增强 | **第八章**（Memory/RAG 全流程）+ `code/chapter8/10_RAG_Pipeline_Complete.py` |
| L3 Agent 编排 | **第四、六、七、九、十、十四章** + `code/chapter14/helloagents-deepresearch`（深度研究 Agent，与我们的 L3 候选方向重合） |
| L4 端到端 | 第十三、十五章的架构拆法 + 第五、六章的框架选型对比 |
| 面试线 | `Extra01-面试问题总结.md` + 各章「小结」，与本仓 8 个面试问题表逐条对齐 |

## 5. 纪律（避免「收藏了就等于学了」）

1. **不通读**。按项目需要查章节，读完立刻在 `log/YYYY-MM-DD.md` 里写「核心概念 3–5 条 + 面试话术 1 段 + 怎么用进当前项目」。
2. **读代码优先于读正文**。第四章以后的正文，先跑通 `code/` 里的脚本再回头读解释，效率差一倍。
3. **只信本地版本**。上游更新后先 `git pull`，避免拿旧章节的接口写代码。
4. **这里的产出要落回本仓**：任何从本教程得出的结论（指标口径、架构取舍）都必须写进 `docs/` 或 `log/`，否则等于没读。

---

*入库时间：2026-09-28｜维护：跟随上游 `git pull`；本文件是唯一索引，不要在别处重复维护章节目录。*
