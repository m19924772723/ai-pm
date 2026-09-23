# -*- coding: utf-8 -*-
"""生成《AI产品项目名单》xlsx —— 参考 2026 年 GitHub 热门项目（star 数据来自实时查询）
   Sheet: 项目名单 / 难度分级 / 选择指南
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'plans/AI产品项目名单.xlsx')

H_FILL = PatternFill('solid', fgColor='1F4E79'); H_FONT = Font(bold=True, color='FFFFFF', size=11)
THIN = Side(style='thin', color='BFBFBF'); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
F = lambda c: PatternFill('solid', fgColor=c)
LV_FILL = {'L1 入门·提示词级': F('C6EFCE'), 'L2 进阶·检索增强(RAG)': F('DEEAF6'),
           'L3 高阶·Agent 编排': F('E4DFEC'), 'L4 平台·端到端产品': F('FFF2CC')}
REC_FILL = {'★★★ 先做': F('C6EFCE'), '★★ 推荐': F('E2EFDA'), '○ 可选': F('F2F2F2')}

def head(ws, cols, widths):
    for i, c in enumerate(cols, start=1):
        cell = ws.cell(row=1, column=i, value=c)
        cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
    for i, wd in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = wd
    ws.row_dimensions[1].height = 30

def body(ws, rows, start=2, h=64, center_cols=(), fill_map=None, fill_col=None):
    r = start
    for row in rows:
        for i, v in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=v); c.border = BORDER
            c.alignment = CENTER if i in center_cols else WRAP
            if fill_map and fill_col and i == fill_col:
                c.fill = fill_map.get(str(v), F('FFFFFF'))
        ws.row_dimensions[r].height = h
        r += 1
    return r

wb = Workbook()

# ============================================================
# Sheet 1: 项目名单
# ============================================================
ws = wb.active; ws.title = '项目名单'
COLS = ['难度', '编号', '类别', '要做的产品项目', '参考 GitHub 项目（★）', '一句话定义',
        '为什么现在热', 'MVP 功能（2–3 个）', '技术栈参考', '预计工作量', '差异化切入点', '推荐']
W = [16, 7, 10, 30, 30, 26, 30, 34, 26, 10, 26, 13]
ROWS = [
 # ============ L1 入门 ============
 ('L1 入门·提示词级', 'P01', '内容工具',
  'AI 长文结构化笔记：长文/链接 → 摘要+要点+标签+待办',
  'nashsu/llm_wiki ★19.8k（理念）',
  '30 秒把一篇长文变成结构化笔记',
  '信息过载是普遍痛点；LLM Wiki 证明"自动结构化"是刚需',
  '① 三种输入（文本/URL/PDF）② 结构化 JSON 输出 ③ 模板切换',
  'LLM + JSON Schema + Streamlit', '1–2 周',
  '按角色切模板（学生/PM/运营）', '★★★ 先做'),
 ('L1 入门·提示词级', 'P02', '求职工具',
  '简历-JD 匹配诊断：上传简历+JD → 匹配度+缺口+改写建议',
  'Paramchoudhary/ResumeSkills ★2.4k',
  '让求职者知道简历差在哪、怎么改',
  '求职永远刚需；AI 语义匹配碾压关键词匹配',
  '① JD 解析 ② 简历解析 ③ 缺口报告+改写建议',
  'LLM 结构化抽取', '2 周',
  '你自己天天用，迭代闭环快', '★★ 推荐'),
 ('L1 入门·提示词级', 'P03', '内容生成',
  'AI Logo/配图生成器：描述 → 多方案 logo 初稿',
  'Nutlope/logocreator ★8.8k',
  '让没有设计师的小团队也能出 logo',
  '设计门槛被 AI 拉平，开源方案已被验证',
  '① 描述输入 ② 多方案生成 ③ 微调',
  '图像生成 API', '1–2 周',
  '中文品牌语义优化', '○ 可选'),
 ('L1 入门·提示词级', 'P04', '内容生成',
  'AI PPT 大纲/单页生成器：一句话大纲 → 可编辑 PPT',
  'presenton ★10.7k / banana-slides ★15.6k',
  '把做 PPT 的重复劳动交给 AI',
  '打工人最痛场景；AI 生成+人工编辑是确定方向',
  '① 大纲→生成 ② 在线编辑 ③ 导出 pptx',
  'LLM + python-pptx', '2–3 周',
  '支持上传公司模板图', '○ 可选'),

 # ============ L2 进阶 ============
 ('L2 进阶·检索增强(RAG)', 'P05', '知识库',
  '个人知识库问答（本地 RAG）：上传资料 → 问答+精确引用',
  'curiousily/ragbase ★132 / deep-rag ★212',
  '让 AI 基于"你自己的资料"回答问题',
  'RAG 是 AI 应用的基本盘，开源教程完备',
  '① 上传索引 ② 问答 ③ 引用到段落',
  '向量库 + RAG + 引用溯源', '3–4 周',
  '引用到段落级 + 无法回答时明说', '★★★ 先做（第一个正式案例）'),
 ('L2 进阶·检索增强(RAG)', 'P06', '知识库',
  'LLM Wiki 式自动知识库：资料自动变成互联的 wiki',
  'nashsu/llm_wiki ★19.8k',
  '不是一问一答，而是自动建一个知识网络',
  'Karpathy 力推的 LLM Wiki 模式，2026 个人知识方向最热',
  '① 导入资料 ② 自动建词条+互链 ③ 搜索',
  'LLM + 知识图谱 + 本地存储', '3–4 周',
  '增量维护 + 新旧冲突检测', '★★★ 先做（差异化强）'),
 ('L2 进阶·检索增强(RAG)', 'P07', '知识库',
  'AI 第二大脑（Obsidian 集成）：扔资料 → 自动分类归档',
  'AgriciDaniel/claude-obsidian ★15.1k / swarmvault ★695',
  '把散乱笔记变成可检索的第二大脑',
  '个人知识管理正被 AI 重做，Obsidian 生态火热',
  '① 导入 ② 自动分类/链接 ③ 语义搜索',
  'Markdown + LLM + 向量', '3–4 周',
  '与你自己的 myblog/obsidian 打通', '★★ 推荐'),
 ('L2 进阶·检索增强(RAG)', 'P08', '效率工具',
  '多文档对比分析：3–10 份文档抽统一维度，标出矛盾',
  'deep-rag ★212（多跳推理）',
  '普通 RAG 做不好的"跨文档对比"',
  '对比是文档类最高频任务，通用 RAG 解决不了',
  '① 批量上传 ② 维度抽取 ③ 对比表+矛盾高亮',
  'LLM + RAG + 表格渲染', '3 周',
  '矛盾结论高亮', '★★ 推荐'),
 ('L2 进阶·检索增强(RAG)', 'P09', '搜索',
  'AI 搜索问答（带引用）：提问 → 搜索 → 带出处的答案',
  'scira ★11.9k / fireplexity ★2k / MemFree ★1.5k',
  'Perplexity 模式的开源版',
  'AI 搜索是确定性方向，多个开源实现可参考',
  '① 搜索 ② 阅读源 ③ 带引用回答',
  '搜索 API + LLM', '3–4 周',
  '中文信息源优化', '★★ 推荐'),
 ('L2 进阶·检索增强(RAG)', 'P10', '知识库',
  '垂直领域知识库问答（法务/医疗/专利等任选）',
  'OpenSPG/KAG ★9.1k',
  '专业领域"逻辑推理式"问答，突破向量检索天花板',
  'KAG 是 2026 RAG 的 SOTA 方向（9k star）',
  '① 领域文档 ② 知识图谱 ③ 逻辑问答',
  'KAG/知识图谱 + LLM', '4 周',
  '选一个你懂的垂直领域', '○ 进阶可选'),

 # ============ L3 高阶 ============
 ('L3 高阶·Agent 编排', 'P11', '研究工具',
  '深度研究 Agent：给主题 → 自动迭代搜索+读网页+出报告',
  'dzhng/deep-research ★19.7k / MindSearch ★6.9k',
  '开源版 Perplexity Deep Research',
  '2026 最热 AI 应用形态之一，19.7k star',
  '① 拆解问题 ② 多轮搜索阅读 ③ 输出带引用报告',
  'LLM + 搜索 API + Agent loop', '4 周',
  '引用可信度评分', '★★★ 先做（L3 首选）'),
 ('L3 高阶·Agent 编排', 'P12', '自动化',
  '浏览器操作 Agent：让 AI 替你操作浏览器办事',
  'browser-use ★115k / BrowserOS ★13.7k / OpenCLI ★29.5k',
  '自然语言指挥浏览器：填表/比价/收集资料',
  '115k star——现象级方向，2026 最热赛道',
  '① 指令理解 ② 浏览器操作 ③ 结果汇报',
  'browser-use + LLM', '4–5 周',
  '表单填写/信息收集垂直化', '★★★ 先做（最热）'),
 ('L3 高阶·Agent 编排', 'P13', '办公自动化',
  'AI 会议纪要助手：录音 → 转写 → 纪要+待办',
  'Zackriya-Solutions/meetily ★31k / vexa ★2.8k',
  '开完会自动出纪要',
  '本地语音转写爆发（31k star）',
  '① 录音转写 ② 说话人区分 ③ 纪要生成',
  'Whisper + LLM', '4 周',
  '本地运行不传云端', '★★ 推荐'),
 ('L3 高阶·Agent 编排', 'P14', '求职工具',
  '面试模拟陪练 Agent：按 JD+简历出题、追问、评分',
  'Natively ★2.6k（interview copilot）',
  '把面试练习变成和 AI 对话',
  '求职工具热 + 你自己天天要用',
  '① 个性化出题 ② 三层追问 ③ 评分报告',
  'Agent + 评分 rubric', '3–4 周',
  '语音对练模式', '★★ 推荐（自用）'),
 ('L3 高阶·Agent 编排', 'P15', '客服',
  'AI 客服/问答 Agent：知识库+多轮对话+转人工',
  'tgo ★616 / cossistant ★723 / basjoo ★158',
  '企业级客服助手，降本刚需',
  '客服是 Agent 落地最成熟的商业场景',
  '① 知识库问答 ② 多轮对话 ③ 情绪识别转人工',
  'RAG + Agent', '4 周',
  '情绪识别 + 人工接管点', '○ 可选'),
 ('L3 高阶·Agent 编排', 'P16', '语音',
  '本地语音助手：热键呼出，全程本地',
  'AlwaysReddy ★751 / llm-guy/jarvis ★332',
  '唤醒词/热键语音助理',
  '语音交互平民化，本地隐私是卖点',
  '① 语音输入 ② LLM 回答 ③ 语音输出',
  'ASR + LLM + TTS', '3–4 周',
  '挂系统热键', '○ 可选'),
 ('L3 高阶·Agent 编排', 'P17', '办公自动化',
  '邮件/消息自动化 Agent：读邮件 → 分类 → 起草回复',
  'kaymen99/langgraph-email-automation ★275',
  '把邮件整理回复的半自动流程',
  '办公自动化长尾刚需',
  '① 收件解析 ② 分类 ③ 起草回复',
  'LangGraph + LLM', '3 周',
  '人工确认环节设计', '○ 可选'),

 # ============ L4 平台 ============
 ('L4 平台·端到端产品', 'P18', 'AI 基建',
  'Agent 评测/观测平台：给 AI 应用建评测集、追踪、护栏',
  'future-agi ★2k',
  '让 Agent 应用"可度量、可观测、可改进"',
  'Agent 应用爆发，评测是公认缺口——蓝海',
  '① 评测集管理 ② 运行追踪 ③ 改进报告',
  'evals 框架 + 追踪', '4–6 周',
  '差异化最大，竞争者少', '★★★ 研一下首选'),
 ('L4 平台·端到端产品', 'P19', '视频生成',
  'AI 短剧/短视频生产：小说 → 剧本 → 视频全自动',
  'Pixelle-Video ★28.3k / Toonflow ★15.8k / VideoLingo ★18.5k',
  '一句话生成完整短剧',
  '短剧出海/短视频是内容风口（2.8 万+ star 验证）',
  '① 剧本生成 ② 分镜 ③ 视频渲染',
  '视频生成 API + 编排', '4–6 周',
  '中文剧本优化', '○ 可选'),
 ('L4 平台·端到端产品', 'P20', '数字人',
  'AI 数字人/虚拟主播：照片 → 说话数字人，实时交互',
  'duixcom/Duix-Avatar ★15.5k / Henry-23/VideoChat ★1.3k',
  '让一张照片开口说话、实时对话',
  '电商直播/客服场景需求大，开源方案成熟',
  '① 形象定制 ② 语音克隆 ③ 实时对话',
  '数字人框架 + TTS', '4–6 周',
  '电商话术垂直化', '○ 可选'),
 ('L4 平台·端到端产品', 'P21', 'AI 基建',
  '多 Agent 协作/工作流平台：复杂任务拆给多个专职 Agent',
  'ruvnet/ruflo ★73k / UnicomAI/wanwu ★2.5k',
  '让多个 Agent 分工协作跑完一件事',
  'Agent 编排是 2026 主旋律（73k star）',
  '① 任务编排 ② 并行 Agent ③ 结果汇总',
  'Agent 框架 + 任务队列', '4–6 周',
  '面向 PM 的编排模板', '○ 进阶'),
 ('L4 平台·端到端产品', 'P22', '办公生成',
  'AI PPT 全功能产品：文档 → 原生 PPT（图表/动画/配音）',
  'hugohe3/ppt-master ★55.8k',
  '文档一键变可编辑原生 PPT',
  '55.8k star 的 AI 办公爆款',
  '① 文档解析 ② PPT 生成 ③ 导出编辑',
  'pptx 生成 + LLM', '4–6 周',
  '接企业模板库', '○ 可选'),
 ('L4 平台·端到端产品', 'P23', '数据分析',
  'AI 数据分析助手：自然语言 → 连接数据 → 可视化',
  'microsoft/data-formulator ★17.2k',
  '让不会写代码的人也能分析数据',
  '数据平民化方向，微软官方开源验证',
  '① 连数据源 ② 自然语言问 ③ 图表生成',
  'LLM + pandas + 可视化', '4 周',
  '中文报表场景', '○ 可选'),
 ('L4 平台·端到端产品', 'P24', 'AI 安全',
  'Agent 技能安全扫描器：检查技能包里的恶意代码/注入',
  'NVIDIA/SkillSpector ★18k',
  '装任何 AI 技能前先扫一遍安全性',
  'Agent 技能生态爆发，安全是 NVIDIA 都押注的缺口',
  '① 技能解析 ② 风险扫描 ③ 报告',
  '静态分析 + LLM', '4 周',
  '差异化强，蓝海', '○ 可选'),
]
head(ws, COLS, W)
end = body(ws, ROWS, center_cols=(1, 2, 3, 10, 12), h=72, fill_map=LV_FILL, fill_col=1)
ws.freeze_panes = 'D2'; ws.auto_filter.ref = 'A1:L%d' % (end - 1)
ws.cell(row=end + 1, column=4, value='共 %d 个项目，难度从 L1 到 L4。★ 数据来自 2026-09-22 实时查询 GitHub API。' % len(ROWS)).font = Font(bold=True, color='C00000')
ws.cell(row=end + 2, column=4, value='推荐路径：P01 → P05/P06 → P11 或 P12 → P18（研一下）。每一步都复用上一步的技术。').font = Font(bold=True)

# ============================================================
# Sheet 2: 难度分级
# ============================================================
ws = wb.create_sheet('难度分级')
COLS2 = ['难度', '练什么能力', '代表性项目', '预计耗时', '进作品集？', '为什么这么分']
W2 = [18, 34, 44, 12, 20, 44]
ROWS2 = [
 ('L1 入门·提示词级', '提示词工程、结构化输出、失败兜底',
  'P01 长文结构化笔记 · P03 Logo 生成',
  '1–2 周', '✗ 只当练手',
  '只调一次 LLM，无复杂架构；建立"我能做出来"的信心'),
 ('L2 进阶·检索增强(RAG)', '上下文工程、检索质量、引用可信度、幻觉抑制',
  'P05 个人知识库问答 · P06 LLM Wiki · P09 AI 搜索',
  '3–4 周', '✓ 第一个正式案例',
  '加上了知识库与检索，是面试最常考的 AI 应用形态'),
 ('L3 高阶·Agent 编排', 'Agent 设计、工具调用、失败恢复、人工接管点',
  'P11 深度研究 · P12 浏览器 Agent · P13 会议纪要',
  '4 周', '✓ 第二个正式案例',
  '多步决策+工具调用，2026 最热方向，最能体现 AI PM 能力'),
 ('L4 平台·端到端产品', '完整产品闭环、评测体系、埋点、AB 实验',
  'P18 Agent 评测平台 · P19 短剧生产 · P22 AI PPT',
  '4–6 周', '✓ 提供数据素材',
  '从"做出来"到"稳定服务真实用户"，且有真实数据'),
]
head(ws, COLS2, W2)
end = body(ws, ROWS2, center_cols=(1, 4, 5), h=52, fill_map=LV_FILL, fill_col=1)
ws.cell(row=end + 1, column=3, value='★ 不跳级：L2 用 L1 的提示词/评测基础，L3 用 L2 的检索基础，L4 用 L3 的编排基础。').font = Font(bold=True, color='C00000')

# ============================================================
# Sheet 3: 选择指南
# ============================================================
ws = wb.create_sheet('选择指南')
COLS3 = ['主题', '内容']
W3 = [22, 100]
ROWS3 = [
 ('怎么用这份名单', '① 从 L1 挑 1 个 ★★★ 先做（P01 或 P02）② 做完升 L2，从 ★★★ 里选（P05 或 P06）③ L3 从 P11/P12 里选（最热）④ 研一下做 P18（评测平台，蓝海）。'),
 ('三条硬筛选（每个项目开工前问自己）', '① 我自己或身边人是真实用户吗？② 4 周内能做出能跑的 MVP 吗？③ 能说清"为什么必须用 AI"吗？——三条全过才能开工。'),
 ('与现有计划的关系', '这份名单是"项目库"，`待做产品项目清单.xlsx` 的「互联网产品阶梯」是"执行排期"。选定项目后，把编号填进阶梯对应层级即可。'),
 ('怎么参考 GitHub 上的项目', '① 先 README 后代码：理解它解决什么问题、怎么拆的 ② 复刻核心流程，不抄代码 ③ 记录"它没做好的地方"→ 这就是你的差异化切入点 ④ 每参考一个项目，把收获写进踩坑日志。'),
 ('差异化切入点从哪找', '① 中文场景：英文项目普遍忽略中文信息源/中文表达习惯 ② 垂直人群：通用工具 + 特定人群模板 ③ 本地化：很多热项目要云 API，做本地可跑版 ④ 评测与安全：Agent 火了但评测/安全工具少。'),
 ('常见坑', '① 贪大：一上来选 L4 项目 → 崩 ② 抄代码不思考：面试问"为什么这么设计"答不上 ③ 只做技术不做评测：没有数字的作品集没有说服力 ④ 做完了不上线：没有真实用户 = 没有证据。'),
 ('最快路径（如果只想做一件事）', 'P01 长文结构化（L1，2 周）→ P06 LLM Wiki（L2，4 周，第一个案例）→ P12 浏览器 Agent（L3，4 周，第二个案例）。三步正好凑齐作品集，全部不依赖导师。'),
]
head(ws, COLS3, W3)
end = body(ws, ROWS3, center_cols=(1,), h=48, start=2)
for r in range(end, end + 1):
    ws.row_dimensions[r].height = 48

wb.save(OUT)
print('saved:', OUT)
print('sheets:', wb.sheetnames)
print('项目数:', len(ROWS))
