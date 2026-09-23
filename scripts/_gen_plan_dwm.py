# -*- coding: utf-8 -*-
"""生成《AI产品经理学习实践计划表》xlsx —— 每日/每周/每月，起算 2026-09-23
   Sheet: 总览 / 每日节律 / 每日打卡(126天) / 每周计划(18周) / 每月计划
"""
import os
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'plans/AI产品经理学习实践计划表.xlsx')
D0 = date(2026, 9, 23)
WK = '一二三四五六日'

H_FILL = PatternFill('solid', fgColor='1F4E79'); H_FONT = Font(bold=True, color='FFFFFF', size=11)
THIN = Side(style='thin', color='BFBFBF'); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
F = lambda c: PatternFill('solid', fgColor=c)
TRACK = {'项目线': F('DEEAF6'), '学习线': F('FFF2CC'), '面试线': F('FCE4D6'), '记录': F('F2F2F2'), '复盘': F('E4DFEC')}
PHASE_FILL = {'启动包': F('FFF2CC'), 'L1 提示词级': F('C6EFCE'), 'L2 检索增强': F('DEEAF6'),
              'L3 Agent 编排': F('E4DFEC'), '评测与数据': F('FCE4D6'), '包装上线': F('E2EFDA'), '缓冲': F('F2F2F2')}

# ---------------- 18 周内容 ----------------
WEEKS = [
 (1, '启动包', '俞军《产品方法论》第1部分 + 用户价值公式；Prompt Engineering Guide 前 3 章',
     'Figma 装好画 1 页框线；建简历骨架（一页纸）', '—（打基础，不开项目）', '公式能否用自己的话讲清'),
 (2, '启动包', '跑一遍 prd-development；woshipm 精读 2 篇；题库收满 20 道',
     'Figma 画 3 页原型；拆解 1 个 AI 产品；写教育+技能两段', '选定 L1 项目方向', '启动包 8 项验收清单'),
 (3, 'L1 提示词级', 'Ollama + Open WebUI 装好跑通；Promptfoo 入门',
     '搭 FastAPI + Streamlit 骨架；模型 API 跑通', 'L1-1 输入层 + JSON Schema 设计', '能否跑通"文本→结构化 JSON"'),
 (4, 'L1 提示词级', 'Langfuse 入门；学怎么写评测方法',
     '找 2 个同学试用并收反馈', 'L1-1 完成 + 建 20 条评测集 + 出数字', 'L1 前后对比数字拿到了吗'),
 (5, 'L2 检索增强', 'RAGFlow 或 LlamaIndex 文档；把 Dify 玩透',
     '选定 L2 方向（个人知识库问答 / LLM Wiki）', 'L2 上传与索引跑通', '检索质量初步如何'),
 (6, 'L2 检索增强', '向量检索与 rerank 原理；上下文工程',
     '实现引用溯源（定位到段落）', 'L2 问答 + 精确引用', '幻觉率是多少'),
 (7, 'L2 检索增强', 'Ragas 指标；OpenAI Evals 框架',
     '界面打磨；找 5 人试用', 'L2 完整可用 v0.1', '试用反馈里最集中的问题'),
 (8, 'L2 检索增强', '评测体系搭建方法',
     '建评测集 30–50 条', 'L2 出数字 + 失败分析 → ★ 第一个作品集案例完成', '案例①能讲 15 分钟吗'),
 (9, 'L3 Agent 编排', 'LangGraph 教程；browser-use 入门',
     '选定 L3 方向（深度研究 Agent / 浏览器 Agent）', 'L3 骨架跑通', 'Agent loop 能否稳定跑完'),
 (10, 'L3 Agent 编排', 'MCP 服务器；工具调用设计',
      '接 2–3 个工具', 'L3 核心流程可用', '失败恢复做得如何'),
 (11, 'L3 Agent 编排', 'agentic_security 红队；失败恢复模式',
      '加失败重试 + 人工接管点', 'L3 v0.2 + 真实用户试用（5–10 人）', '真实用户数'),
 (12, 'L3 Agent 编排', 'DeepEval / Promptfoo 进阶',
      '建 L3 评测集', 'L3 出数字 → ★ 第二个作品集案例完成', '案例②能讲 15 分钟吗'),
 (13, '评测与数据', '指标体系 + AB 实验设计',
      'Metabase 做看板', '案例③素材：指标树 + 归因 + 实验设计', '数字是否可复现'),
 (14, '包装上线', '简历四段式；product-sense 六段式框架',
      '简历补实测数字 + 全文重写删空话', 'myblog portfolio/ 板块搭建', '简历里"负责/参与"删净了吗'),
 (15, '包装上线', '部署：Docker + Vercel/Railway',
      '部署上线；发给 10–20 人使用', '作品集上线 + 真实用户数', '有没有 10 个真实用户'),
 (16, '包装上线', '面试四类题型系统复习',
      '写 3 分钟/15 分钟讲法；找人做 1 次模拟面试', '讲法稿 + 录音', '被追问三层稳不稳'),
 (17, '缓冲', '复盘全部录音，列出薄弱题型',
      '8 项弹药清单逐项检查', '补漏（缺哪项补哪项）', '哪一格还没证据'),
 (18, '缓冲', '规划研一下学习路线',
      '建实习投递台账（公司/岗位/渠道/进度）', '研一下计划：小论文 + 第 2 个作品', '研一下三件事定下来了吗'),
]

def week_of(d):
    return (d - D0).days // 7 + 1

def wrow(w):
    return WEEKS[w - 1]

wb = Workbook()

# ===================== Sheet 1: 总览 =====================
ws = wb.active; ws.title = '总览'
ws.column_dimensions['A'].width = 18; ws.column_dimensions['B'].width = 104
ROWS = [
 ('AI 产品经理学习实践计划表', ''),
 ('', ''),
 ('起算日', '2026-09-23（周三）'),
 ('周期', '18 周，2026-09-23 ~ 2027-01-26（共 126 天）'),
 ('三层结构', '每日节律（固定习惯）→ 每周计划（推进节奏）→ 每月计划（里程碑验收）'),
 ('', ''),
 ('【每日时间预算】约 2–3.5 小时', ''),
 ('① 项目推进', '90 分钟（周一至周五）／180 分钟（周六集中）—— 主线，占 60% 时间'),
 ('② 信息摄入', '30 分钟（精读 1 篇 或 课程/开源项目）—— 通勤/睡前，不占项目时间'),
 ('③ 记录', '15 分钟 —— 踩坑日志 + 当日一行复盘（面试素材来源）'),
 ('④ 面试练习', '周日 90 分钟（3 道题 + 录音 + 复盘）'),
 ('⑤ 周复盘', '周日 30 分钟 —— 对照 8 个面试问题检查哪格没证据'),
 ('', ''),
 ('【三条轨道】', ''),
 ('学习线', '读书、课程、开源项目阅读、方法论——决定"想得对不对"'),
 ('实践线', '装工具、跑通环境、找人试用、部署上线——决定"做不做得出来"'),
 ('项目线', '★ 主线：L1 → L2 → L3 三个项目，产出全部面试证据'),
 ('', ''),
 ('【18 周阶段划分】', ''),
 ('第 1–2 周', '启动包：打基础 + 定 L1 方向'),
 ('第 3–4 周', 'L1 提示词级项目：练手，出第一组评测数字'),
 ('第 5–8 周', 'L2 检索增强项目：★ 第一个作品集案例'),
 ('第 9–12 周', 'L3 Agent 项目：★ 第二个作品集案例'),
 ('第 13 周', '评测与数据：案例③素材（指标树 + 归因 + AB 实验设计）'),
 ('第 14–16 周', '包装上线：作品集页 + 真实用户 + 讲法稿'),
 ('第 17–18 周', '缓冲补漏 + 规划研一下'),
 ('', ''),
 ('【每天必做三件事】', '① 项目推进 ② 信息摄入 30 分钟 ③ 记录一行'),
 ('【每周必做三件事】', '① 周复盘 ② 1 次 commit（项目起）③ 简历素材库更新'),
 ('【每月必做】', '月末交付物盘点 + 下月计划调整'),
]
r = 1
for a, b in ROWS:
    ca = ws.cell(row=r, column=1, value=a); cb = ws.cell(row=r, column=2, value=b)
    if r == 1:
        ca.font = Font(bold=True, size=16, color='1F4E79'); ws.row_dimensions[r].height = 26
    elif a.startswith('【'):
        ca.font = Font(bold=True, size=12, color='C00000')
    else:
        ca.font = Font(bold=True)
    cb.alignment = WRAP
    r += 1

# ===================== Sheet 2: 每日节律 =====================
ws = wb.create_sheet('每日节律')
COLS = ['星期', '轨道', '固定动作', '时长', '产出', '完成']
W = [8, 10, 62, 12, 34, 7]
for i, c in enumerate(COLS, start=1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
for i, wd in enumerate(W, start=1):
    ws.column_dimensions[get_column_letter(i)].width = wd
ws.row_dimensions[1].height = 28

RHYTHM = [
 ('一', '项目线', '推进本周项目任务（写代码 / 调提示词 / 改设计）', '90 分钟', '当日进度', None),
 ('一', '记录', '记一行：今天卡在哪、怎么试的、结果如何', '15 分钟', '踩坑日志', None),
 ('二', '项目线', '推进本周项目任务', '90 分钟', '当日进度', None),
 ('二', '学习线', 'woshipm 精读 1 篇 + 写笔记（每周 2 篇之一）', '30 分钟', '精读笔记', None),
 ('二', '记录', '记一行踩坑日志', '15 分钟', '踩坑日志', None),
 ('三', '项目线', '推进本周项目任务', '90 分钟', '当日进度', None),
 ('三', '学习线', '看课程 或 读开源项目源码（生成式AI入门 / awesome-llm-apps）', '45 分钟', '学习笔记', None),
 ('三', '记录', '记一行踩坑日志', '15 分钟', '踩坑日志', None),
 ('四', '项目线', '推进本周项目任务', '90 分钟', '当日进度', None),
 ('四', '记录', '记一行踩坑日志', '15 分钟', '踩坑日志', None),
 ('五', '项目线', '推进本周项目任务', '90 分钟', '当日进度', None),
 ('五', '学习线', 'woshipm 精读 1 篇 + 写笔记（每周 2 篇之二）', '30 分钟', '精读笔记', None),
 ('五', '复盘', '周中检查：本周目标完成几成？要不要调？', '15 分钟', '调整决定', None),
 ('六', '项目线', '★ 集中推进（一周里唯一的大块时间）', '180 分钟', '显著进度', None),
 ('六', '学习线', '看课程 或 读开源项目源码', '45 分钟', '学习笔记', None),
 ('六', '记录', '记一行踩坑日志', '15 分钟', '踩坑日志', None),
 ('日', '面试线', '练 3 道面试题（按题型轮换）+ 录音 + 回放复盘', '90 分钟', '3 份录音 + 复盘', None),
 ('日', '复盘', '★ 周复盘：对照 8 个面试问题，检查哪一格还没证据', '30 分钟', '周复盘记录', None),
]
r = 2
for row in RHYTHM:
    for i, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 4, 6) else WRAP
        if i == 2: c.fill = TRACK.get(v, F('FFFFFF'))
    ws.row_dimensions[r].height = 34
    r += 1
ws.cell(row=r + 1, column=3, value='每天必做三件事：① 项目推进 ② 信息摄入 30 分钟 ③ 记录一行。周日不推进项目，只做面试练习和复盘。').font = Font(bold=True, color='C00000', size=12)
ws.freeze_panes = 'C2'

# ===================== Sheet 3: 每日打卡 =====================
ws = wb.create_sheet('每日打卡')
COLS3 = ['日期', '星期', '周次', '阶段', '项目线（当日任务）', '学习线', '面试线', '记录', '完成']
W3 = [12, 7, 7, 14, 40, 32, 26, 16, 7]
for i, c in enumerate(COLS3, start=1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
for i, wd in enumerate(W3, start=1):
    ws.column_dimensions[get_column_letter(i)].width = wd
ws.row_dimensions[1].height = 28

r = 2
for n in range(126):
    d = D0 + timedelta(days=n)
    w = week_of(d); wkrow = wrow(w)
    phase, proj, sx = wkrow[1], wkrow[4], wkrow[3]
    dow = WK[d.weekday()]
    # 启动包阶段（无项目）时，用实践线内容当当日任务
    is_startup = proj.startswith('—')
    # 项目线当日任务
    if dow == '日':
        pj = '—（周日不推进项目）'
    elif dow == '六':
        pj = '★ 集中推进：' + (sx if is_startup else proj)
    elif is_startup:
        pj = '启动包任务：' + sx
    else:
        pj = '推进：' + proj
    # 学习线
    if dow in ('二', '五'):
        lx = 'woshipm 精读 1 篇 + 笔记'
    elif dow in ('三', '六'):
        lx = '课程 / 开源项目源码阅读'
    elif dow == '日':
        lx = '—（周日留给面试练习）'
    else:
        lx = '—（信息摄入可在通勤完成）'
    # 面试线
    if dow == '日':
        iv = '练 3 道题 + 录音 + 复盘'
    elif dow == '三':
        iv = '复习上周录音（15 分钟）'
    else:
        iv = '—'
    rec = '踩坑日志一行' if dow != '日' else '周复盘记录'
    vals = [d.isoformat(), dow, 'W%d' % w, phase, pj, lx, iv, rec, None]
    for i, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 3, 4, 9) else WRAP
        if i == 4: c.fill = PHASE_FILL.get(phase, F('FFFFFF'))
        if i == 9: c.value = '☐'
        if i == 9: c.alignment = CENTER
    ws.row_dimensions[r].height = 30
    r += 1
ws.freeze_panes = 'E2'
ws.auto_filter.ref = 'A1:I%d' % (r - 1)
ws.cell(row=r + 1, column=5, value='共 126 天（2026-09-23 ~ 2027-01-26）。每天做完把"完成"列打勾。').font = Font(bold=True, color='C00000')

# ===================== Sheet 4: 每周计划 =====================
ws = wb.create_sheet('每周计划')
COLS4 = ['周次', '日期', '阶段', '学习线（读书/课程/开源）', '实践线（装工具/试用/上线）', '项目线（★ 主线）', '周日复盘检查点', '完成']
W4 = [7, 22, 14, 42, 38, 44, 30, 7]
for i, c in enumerate(COLS4, start=1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
for i, wd in enumerate(W4, start=1):
    ws.column_dimensions[get_column_letter(i)].width = wd
ws.row_dimensions[1].height = 30

r = 2
for w, phase, lx, sx, pj, ck in WEEKS:
    a = D0 + timedelta(days=(w - 1) * 7); b = a + timedelta(days=6)
    vals = ['W%d' % w, '%s ~ %s' % (a.isoformat(), b.isoformat()), phase, lx, sx, pj, ck, '☐']
    for i, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 3, 8) else WRAP
        if i == 3: c.fill = PHASE_FILL.get(phase, F('FFFFFF'))
    ws.row_dimensions[r].height = 56
    r += 1
ws.freeze_panes = 'D2'
ws.auto_filter.ref = 'A1:H%d' % (r - 1)
ws.cell(row=r + 1, column=4, value='每周固定动作：① 周复盘 ② 1 次 commit（第 3 周起）③ 简历素材库更新（把本周产出翻译成简历语言）').font = Font(bold=True, color='C00000')

# ===================== Sheet 5: 每月计划 =====================
ws = wb.create_sheet('每月计划')
COLS5 = ['月份', '日期范围', '阶段', '学习目标', '实践目标', '项目目标', '月末交付物（验收）', '完成']
W5 = [12, 24, 20, 36, 34, 36, 36, 7]
for i, c in enumerate(COLS5, start=1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
for i, wd in enumerate(W5, start=1):
    ws.column_dimensions[get_column_letter(i)].width = wd
ws.row_dimensions[1].height = 30

MONTHS = [
 ('2026-09', '09-23 ~ 09-30（8 天）', '启动包启动',
  '俞军《产品方法论》第 1 部分 + 用户价值公式', 'Figma 装好；建简历骨架',
  '选定 L1 项目方向', '① 公式能用自己的话讲清 ② 简历骨架文件 ③ Figma 能画框线', '☐'),
 ('2026-10', '10-01 ~ 10-31（31 天）', '启动包完成 + L1 项目',
  'Prompt Engineering Guide；Promptfoo / Langfuse 入门', '拆解 1 个 AI 产品；FastAPI + Streamlit 骨架跑通',
  'L1 项目完成 + 20 条评测集', '① 产品拆解文档 ② 3 页原型 ③ 20 道题库 ④ ★ L1 前后对比数字', '☐'),
 ('2026-11', '11-01 ~ 11-30（30 天）', 'L2 检索增强项目',
  'RAGFlow/LlamaIndex；向量检索与 rerank；上下文工程；Ragas',
  'Dify 玩透；引用溯源实现；找 5 人试用',
  'L2 完整可用 + 评测集 30–50 条', '① ★ 第一个作品集案例（能讲 15 分钟）② 检索质量与幻觉率数字', '☐'),
 ('2026-12', '12-01 ~ 12-31（31 天）', 'L3 Agent 项目 + 评测',
  'LangGraph；browser-use；MCP；agentic_security 红队；AB 实验设计',
  '接 2–3 个工具；失败重试 + 人工接管；部署（Docker）',
  'L3 出数字 + 案例③素材', '① ★ 第二个作品集案例 ② 案例③素材（指标树+归因+实验设计）', '☐'),
 ('2027-01', '01-01 ~ 01-26（26 天）', '包装上线',
  '面试四类题型系统复习；product-sense 六段式',
  '部署上线；发 10–20 人使用；简历重写；模拟面试',
  '作品集上线 + 讲法稿', '① 作品集页上线 ② 真实用户数 ③ 3 分钟/15 分钟讲法 ④ 研一下计划', '☐'),
]
r = 2
for row in MONTHS:
    for i, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 8) else WRAP
        if i == 1: c.fill = F('FFF2CC')
    ws.row_dimensions[r].height = 64
    r += 1
ws.cell(row=r + 1, column=4, value='每月固定动作：月末做交付物盘点（对照上表逐项打勾）+ 调整下月计划。').font = Font(bold=True, color='C00000', size=12)
ws.cell(row=r + 2, column=4, value='★ 三条止损规则：第 3 周没定 L1 方向 → 直接选长文结构化；第 12 周核心跑不通 → 砍到只剩 1 个功能；第 15 周没上线 → 现有版本先放上去。').font = Font(bold=True)

wb.save(OUT)
print('saved:', OUT)
print('sheets:', wb.sheetnames)
print('每日打卡天数:', 126, '| 周计划:', len(WEEKS), '| 月计划:', len(MONTHS))
print('起止:', D0.isoformat(), '~', (D0 + timedelta(days=125)).isoformat())
