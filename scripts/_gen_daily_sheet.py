# -*- coding: utf-8 -*-
"""加 sheet：第1-2周日任务（启动包）"""
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(HERE, 'plans/待做产品项目清单.xlsx')

H_FILL = PatternFill('solid', fgColor='1F4E79'); H_FONT = Font(bold=True, color='FFFFFF', size=11)
THIN = Side(style='thin', color='BFBFBF'); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
F = lambda c: PatternFill('solid', fgColor=c)
TRACK_FILL = {'项目': F('DEEAF6'), '简历': F('E2EFDA'), '面试': F('FCE4D6'),
              '工具': F('F2F2F2'), '复盘': F('FFF2CC')}

wb = load_workbook(XLSX)

COLS = ['天', '日期', '星期', '轨道', '具体任务（当天做完就勾）', '预计耗时', '产出物', '完成']
W = [6, 12, 7, 8, 56, 10, 30, 7]

D = [
 (1, '09-22', '二', '项目', '精读俞军《产品方法论》第 1 部分（前半：产品经理是什么）', '45 分钟', '读书笔记', None),
 (2, '09-23', '三', '项目', '精读俞军第 1 部分（后半）；用自己的话写下"用户价值 = 新体验 − 旧体验 − 替换成本"并各举一例', '60 分钟', '公式理解笔记', None),
 (3, '09-24', '四', '工具', '注册人人都是产品经理（woshipm）+ 精读 2 篇深度分析 + 写笔记；顺手开始收题库（先 8 道）', '90 分钟', '精读笔记 + 8 道题', None),
 (4, '09-25', '五', '项目', 'Figma 注册/装好；跟一个入门教程，画 1 个页面的框线原型', '90 分钟', '1 张框线图', None),
 (5, '09-26', '六', '简历', '建简历骨架文件（一页纸，先把模块搭好，不填空话）', '60 分钟', '简历 v0 骨架', None),
 (6, '09-27', '日', '复盘', '题库补到 20 道；写第 1 周复盘（哪卡住了 / 下周改什么）', '90 分钟', '20 道题库 + 周复盘', None),
 (7, '09-28', '一', '复盘', '补漏；选定要拆解的互联网 AI 产品（从 R1–R5 里挑，建议 R3 AI 编程助手）', '30 分钟', '拆解对象确定', None),
 (8, '09-29', '二', '项目', 'Figma 画完整框线原型（3 个页面：输入 / 结果 / 历史）', '90 分钟', '原型 3 页', None),
 (9, '09-30', '三', '项目', '跑一遍 prd-development 技能，产出 1 份 PRD 骨架', '60 分钟', 'PRD 骨架', None),
 (10, '10-01', '四', '项目', '【国庆可集中】拆解：目标用户 + JTBD 分析', '120 分钟', '拆解文档前半', None),
 (11, '10-02', '五', '项目', '【国庆可集中】拆解：竞品对比矩阵 + 对照 PRD 结构，收尾成文档', '120 分钟', '拆解文档完成', None),
 (12, '10-03', '六', '简历', '写"教育背景"+"技能"两段（AI 工具链 / Python / Figma / SQL）', '60 分钟', '简历 v0.5', None),
 (13, '10-04', '日', '面试', '产品设计题 3 道（六段式，口述并录音，回放复盘）', '120 分钟', '3 份录音 + 复盘', None),
 (14, '10-05', '一', '复盘', '启动包验收：对照下方交付物清单逐项检查', '60 分钟', '启动包验收单', None),
]

if '第1-2周日任务' in wb.sheetnames:
    del wb['第1-2周日任务']
ws = wb.create_sheet('第1-2周日任务', 1)
for i, c in enumerate(COLS, start=1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = CENTER; cell.border = BORDER
for i, wd in enumerate(W, start=1):
    ws.column_dimensions[get_column_letter(i)].width = wd
ws.row_dimensions[1].height = 28

r = 2
for row in D:
    for i, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=i, value=v); c.border = BORDER
        c.alignment = CENTER if i in (1, 2, 3, 4, 6, 8) else WRAP
        if i == 4: c.fill = TRACK_FILL.get(v, F('FFFFFF'))
    ws.row_dimensions[r].height = 40
    r += 1

r += 1
ws.cell(row=r, column=5, value='启动包验收清单（第 14 天逐项打勾）').font = Font(bold=True, size=12, color='C00000')
r += 1
for item in [
 '1. 俞军第 1 部分精读完成，能用自己的话讲清"用户价值公式"',
 '2. 1 份 AI 产品拆解文档（用户 + JTBD + 竞品矩阵 + PRD 结构对照）',
 '3. 1 份 PRD 骨架（知道 PRD 有哪些模块）',
 '4. 1 张 3 页框线原型（Figma）',
 '5. 简历 v0.5（骨架 + 教育背景 + 技能）',
 '6. 20 道大厂产品面试真题题库',
 '7. 3 份产品设计题录音 + 复盘笔记',
 '8. woshipm 已注册，精读 ≥4 篇并写了笔记',
]:
    ws.cell(row=r, column=5, value=item).font = Font(bold=False)
    ws.cell(row=r, column=8, value='☐')
    r += 1

r += 1
ws.cell(row=r, column=5, value='★ 每天只做 1 件事（45–120 分钟）。启动包不追求完美，追求"做完"。').font = Font(bold=True, color='C00000', size=12)
ws.cell(row=r + 1, column=5, value='★ 10-01 ~ 10-03 是国庆假期，已把最耗时的"产品拆解"安排在这几天，可集中处理。').font = Font(bold=True)
ws.cell(row=r + 2, column=5, value='★ 第 15 天（10-06）起进入 L1-1 项目实战，见《L1-1项目启动说明书.md》。').font = Font(bold=True)

ws.freeze_panes = 'E2'
wb.save(XLSX)
print('saved:', XLSX)
print('sheets:', wb.sheetnames)
print('日任务:', len(D), '天 + 验收清单 8 项')
