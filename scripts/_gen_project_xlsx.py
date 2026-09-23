# -*- coding: utf-8 -*-
"""生成《待做产品项目清单》xlsx -> D:/code/hermes/ai_pm/待做产品项目清单.xlsx
   Sheet: 项目总览 / 作品集三案例 / 实习期项目目标 / 待做任务清单(同步) / 里程碑
"""
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'plans/待做产品项目清单.xlsx')
PLAN = os.path.join(HERE, 'plans/AI产品经理求职计划表.xlsx')

# ---------------- 样式 ----------------
H_FILL = PatternFill('solid', fgColor='1F4E79'); H_FONT = Font(bold=True, color='FFFFFF', size=11)
THIN = Side(style='thin', color='BFBFBF'); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
TIP_FONT = Font(bold=True, size=12, color='C00000')
F = lambda c: PatternFill('solid', fgColor=c)
TYPE_FILL = {'作品集（自选）': F('DEEAF6'), '学术结合': F('FFF2CC'),
             '实习产出（真实）': F('E2EFDA'), '加分项（可选）': F('F2F2F2')}

def head(ws, cols, row=1, widths=None):
    for i, c in enumerate(cols, start=1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
    if widths:
        for i, wd in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = wd
    ws.row_dimensions[row].height = 30

def body(ws, rows, start=2, h=34, center_cols=(), fill_by=None):
    r = start
    for row in rows:
        for i, v in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=v); c.border = BORDER
            c.alignment = CENTER if i in center_cols else WRAP
            if fill_by:
                fv = fill_by(row)
                if fv: c.fill = fv
        ws.row_dimensions[r].height = h
        r += 1
    return r

wb = Workbook()

# ==================================================================
# Sheet 1: 项目总览（要做的产品项目名录）
# ==================================================================
ws = wb.active; ws.title = '项目总览'
head(ws, ['序号', '项目名称', '项目类型', '计划时间', '目标用户',
          '要回答的核心面试问题', '核心交付物', '依赖', '优先级', '状态'],
     widths=[6, 30, 17, 20, 24, 34, 30, 10, 9, 10])

PROJECTS = [
 # ---- 第一个项目：研一上 ----
 ('1', '【候选 A】印刷/包装品缺陷检测辅助工具', '学术结合 + 作品集（自选）', '研一上 第 3–16 周',
  '印刷/包装产线质检人员',
  '为什么必须用 AI？（视觉模型 vs 人工目检）',
  '访谈记录 / 竞品矩阵 / 取舍记录 / PRD / 原型 / demo / 实测数据 / 作品集页',
  'A1 定导师、A3 确认数据集', 'P0', '未开始'),
 ('2', '【候选 B】论文/文献阅读与对比 Agent', '作品集（自选）', '研一上 第 3–16 周',
  '研究生 / 科研工作者',
  '为什么必须用 AI？（规则匹配维护成本随时间爆炸）',
  '同上（访谈 6 位同门 / 40 条评测集 / 准确率对比）',
  'A3 决定转 B 后启动', 'P0', '未开始'),
 ('3', '（已淘汰）课程/实习信息聚合助手', '—', '—', '—',
  '答不上"为什么必须用 AI" → 不做',
  '—', '—', '不做', '已淘汰'),

 # ---- 作品集三案例 ----
 ('4', '作品集案例 ①：AI 产品复刻/深度拆解 + 改进方案', '作品集（自选）', '研一下 2027.2–7',
  '该产品现有用户',
  '你的分析深度 & 取舍能力',
  '用户画像+JTBD / 竞品对比矩阵 / 改进 PRD / Figma 原型',
  'B4 拆解练习', 'P0', '未开始'),
 ('5', '作品集案例 ②：端到端产品设计（真实痛点 → 定位 → PRD → 原型）', '作品集（自选）', '研二上 2027.9–2028.1',
  '自选细分人群',
  '能不能从零走完一个完整产品流程',
  '完整 PRD / 定位陈述 / 原型 / 故事板',
  '案例① 完成', 'P0', '未开始'),
 ('6', '作品集案例 ③：数据驱动决策（指标体系 + 归因 + AB 实验设计）', '作品集（自选）', '研二上 2027.9–2028.1',
  '内部/模拟业务方',
  '数据分析能力 & 实验设计能力',
  '指标体系 / 归因报告 / AB 实验设计文档',
  '案例② 完成、E5 SQL 上手', 'P0', '未开始'),

 # ---- 学术结合 ----
 ('7', '小论文：图像缺陷检测方向', '学术结合', '研一下 2027.2–7 投出',
  '—', '（学术硬门槛，非面试用）',
  '投稿记录（期刊名 + 时间 + 录用状态）',
  'A2 选题', 'P0', '未开始'),
 ('8', '大论文（正文 ≥2 万字）', '学术结合', '研二上开题 → 研三上成稿',
  '—', '（学术硬门槛，非面试用）',
  '开题报告 / 实验数据 / 正文',
  'A4 小论文投出', 'P0', '未开始'),

 # ---- 实习产出 ----
 ('9', '第 1 段实习项目产出（中小厂/创业 · AI 产品方向）', '实习产出（真实）', '研一暑假 2027.7–8',
  '该公司真实用户',
  '真实业务里你怎么做判断、拿结果',
  '可量化产出（提效 X% / 转化提升 Y%）+ 实习证明',
  '作品集（案例①）+ 投递', 'P0', '未开始'),
 ('10', '第 2 段实习项目产出（中厂/独角兽日常实习）', '实习产出（真实）', '研二上 2027.9–2028.1',
  '该公司真实用户', '垂直度：必须是 AI 产品方向',
  '可量化产出 + 一段"垂直"经历', '第 1 段实习', 'P0', '未开始'),
 ('11', '第 3 段实习项目产出（大厂暑期实习 → 争取转正）', '实习产出（真实）', '研二暑假 2028.7–8',
  '大厂真实用户', '有没有上线？谁在用？你负责哪部分？',
  '转正 offer（或高评价实习证明 + 可讲项目）', '第 2 段实习', 'P0', '未开始'),

 # ---- 加分项 ----
 ('12', '个人作品集站（myblog portfolio/ 板块）', '加分项（可选）', '第 14–15 周上线',
  '面试官 / HR', '能不能一页看懂你做过什么',
  'portfolio 页上线（含四段式：问题/研究/取舍/效果）',
  'B16 作品集页初稿', 'P0', '未开始'),
 ('13', '开源 Agent 小工具（技术证明）', '加分项（可选）', '按需（第 8 周起随手做）',
  '开发者', '证明"能自己把东西做出来"',
  'GitHub 仓库 + README + star 数', '—', 'P2', '未开始'),
 ('14', '面试作品集话术包（3 分钟版 / 15 分钟版讲法）', '加分项（可选）', '第 16 周',
  '面试官', '被追问三层还稳得住吗',
  '讲法稿 + 录音', 'B18', 'P0', '未开始'),
]
end = body(ws, PROJECTS, center_cols=(1, 3, 4, 8, 9, 10), h=40,
           fill_by=lambda row: TYPE_FILL.get(row[2]))
ws.freeze_panes = 'C2'; ws.auto_filter.ref = 'A1:J%d' % (end - 1)
c = ws.cell(row=end + 1, column=2, value='共 %d 项（含 1 项已淘汰）' % len(PROJECTS)); c.font = TIP_FONT
c = ws.cell(row=end + 2, column=2, value='★ 研一上只做第 1 或第 2 项（二选一），其余是后续规划'); c.font = Font(bold=True)

# ==================================================================
# Sheet 2: 作品集三案例
# ==================================================================
ws = wb.create_sheet('作品集三案例')
head(ws, ['案例', '类型', '做法（做什么）', '产出', '对应面试问题', '计划时间', '状态'],
     widths=[7, 20, 52, 34, 30, 22, 10])
CASES = [
 ('①', 'AI 产品复刻/深度拆解',
  '选 1 个真实 AI 产品：① 用户画像 + JTBD 分析 ② 竞品对比矩阵 ③ 自己设计改进方案 ④ 写 PRD + 画原型\n（只拆解 = 分析作业；加上方案才是产品作品）',
  '分析文档 + 改进 PRD + Figma 原型',
  '分析深度、取舍能力、能不能看出问题',
  '研一下 2027.2–7', '未开始'),
 ('②', '端到端产品设计',
  '从一个真实痛点出发，走完：发现 → 定位 → PRD → 原型 → 故事板\n必须包含"我放弃了什么方案、为什么"',
  '完整 PRD + 定位陈述 + 原型 + 故事板',
  '能不能从零走完完整流程',
  '研二上 2027.9–2028.1', '未开始'),
 ('③', '数据驱动决策',
  '用真实或模拟数据：① 搭指标体系 ② 做归因分析 ③ 设计 AB 实验\n关键是"结论怎么来的"，不是结论本身',
  '指标体系 + 归因报告 + AB 实验设计文档',
  '数据分析、实验设计、严谨性',
  '研二上 2027.9–2028.1', '未开始'),
]
end = body(ws, CASES, center_cols=(1, 6, 7), h=76)
ws.cell(row=end + 1, column=2, value='写法要求：每个案例都要有"我的判断"和"我放弃的方案及原因"').font = TIP_FONT
ws.cell(row=end + 2, column=2, value='放哪：myblog 的 portfolio/ 板块（别人还要从零搭站，你已经有了）').font = Font(bold=True)

# ==================================================================
# Sheet 3: 实习期项目目标
# ==================================================================
ws = wb.create_sheet('实习期项目目标')
head(ws, ['阶段', '目标公司档位', '投递时间', '岗位关键词', '这一段的唯一目的是什么',
          '交付物（可写进简历的）', '状态'],
     widths=[20, 24, 20, 30, 40, 34, 10])
INTERN = [
 ('第 1 段 · 研一暑假 2027.7–8', '中小厂 / 创业 / AI 初创 / 行业数字化',
  '2027.4 起投', 'AI 产品实习、产品助理、数据产品实习',
  '把"0 经验"变成"有经验"——破 0 最重要，不计较公司大小',
  '1 段 ≥2 个月的产品实习（简历第一条）', '未开始'),
 ('第 2 段 · 研二上 2027.9–2028.1', '中厂 / 独角兽（日常实习）',
  '2027.9 起投', 'AI 产品实习（必须垂直）',
  '补"垂直度"——日常实习门槛低于暑期实习，是大厂暑期实习的跳板',
  '1 段中厂/独角兽 AI 产品实习', '未开始'),
 ('第 3 段 · 研二暑假 2028.7–8', '大厂（暑期实习）',
  '2028.3–4 集中投', 'AI 产品经理暑期实习',
  '★ 拿到 offer 最稳的路径——比秋招正面厮杀概率高得多',
  '转正 offer（或高评价证明 + 可讲项目）', '未开始'),
]
end = body(ws, INTERN, center_cols=(1, 3, 7), h=64)
ws.cell(row=end + 1, column=2, value='★ 铁律：投大厂前，简历里必须先有一段"垂直"的 AI 产品经历，否则会被直接筛掉').font = TIP_FONT
ws.cell(row=end + 2, column=2, value='★ 实习期间同时投秋招，永远两条腿走路（Leader 的口头承诺不可押注）').font = Font(bold=True)

# ==================================================================
# Sheet 4: 待做任务清单（从计划表同步）
# ==================================================================
ws = wb.create_sheet('待做任务清单')
src = load_workbook(PLAN)
S = src['待做清单']
head(ws, [S.cell(row=1, column=i).value for i in range(1, 9)],
     widths=[7, 13, 46, 15, 24, 8, 9, 7])
CAT_FILL = {'学业线': F('FFF2CC'), '项目线': F('DEEAF6'), '简历线': F('E2EFDA'),
            '面试线': F('FCE4D6'), '资产与工具线': F('F2F2F2')}
r = 2
for row in S.iter_rows(min_row=2, max_row=S.max_row, max_col=8, values_only=True):
    if row[1] is None or row[0] is None or not str(row[0])[0].isalpha():
        continue
    for i, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 4, 6, 7, 8) else WRAP
        if i == 2: c.fill = CAT_FILL.get(row[1], F('FFFFFF'))
    ws.row_dimensions[r].height = 32
    r += 1
ws.freeze_panes = 'C2'; ws.auto_filter.ref = 'A1:H%d' % (r - 1)
ws.cell(row=r + 1, column=2, value='共 %d 项（同步自《AI产品经理求职计划表.xlsx》）' % (r - 2)).font = Font(bold=True)

# ==================================================================
# Sheet 5: 里程碑
# ==================================================================
ws = wb.create_sheet('里程碑')
head(ws, ['里程碑', '时间', '说明', '关联项目', '状态'], widths=[34, 24, 44, 14, 10])
MS = [
 ('小论文投出', '研一下 2027.2–7', '学术成果硬节点', '项目 7', '未开始'),
 ('作品集案例 ① 完成', '研一下 2027.2–7', '作品集从 0 到 1', '项目 4', '未开始'),
 ('第 1 段实习（中小厂/创业）', '研一暑假 2027.7–8', '破 0，拿到第一段产品实习', '项目 9', '未开始'),
 ('作品集案例 ②③ 完成', '研二上 2027.9–2028.1', '作品集扩到 3 个案例', '项目 5、6', '未开始'),
 ('第 2 段实习（中厂/独角兽）', '研二上 2027.9–2028.1', '补垂直度', '项目 10', '未开始'),
 ('大论文开题', '研二上 2027.9–2028.1', '选题须与实习兼容', '项目 8', '未开始'),
 ('★ 投大厂暑期实习', '研二下 2028.2–6', '整条路最关键的一枪', '项目 11', '未开始'),
 ('暑期实习 → 转正', '研二暑假 2028.7–8', 'offer 最稳路径', '项目 11', '未开始'),
 ('秋招', '研三上 2028.9–12', '正面战场（有 2–3 段实习 + 作品集）', '—', '未开始'),
 ('大论文答辩 + 入职', '研三下 2029.1–6', '收尾', '项目 8', '未开始'),
]
end = body(ws, MS, center_cols=(2, 4, 5), h=32)

wb.save(OUT)
print('saved:', OUT)
print('sheets:', wb.sheetnames)
print('项目总览:', len(PROJECTS), '项 | 作品集案例:', len(CASES), '| 实习段:', len(INTERN),
      '| 任务清单:', r - 2, '项 | 里程碑:', len(MS))
