# -*- coding: utf-8 -*-
"""生成《产品经理技能使用清单》 -> D:/code/hermes/ai_pm/产品经理技能使用清单.md"""
import json, os, io, datetime
from collections import defaultdict, OrderedDict

rows = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/pm_skills_index.json'), encoding='utf-8'))
by_dir = {r['dir']: r for r in rows}

THEME_CN = OrderedDict([
    ('strategy-positioning',   '战略与定位'),
    ('discovery-research',     '需求发现与用户研究'),
    ('pm-artifacts',           'PM 交付物（PRD / 用户故事）'),
    ('roadmap-planning',       '路线图'),
    ('validation-experiments', '验证与实验'),
    ('finance-metrics',        '财务与商业指标'),
    ('market-intelligence',    '市场情报与竞争分析'),
    ('stakeholder-comms',      '干系人沟通'),
    ('product-lifecycle',      '产品生命周期'),
    ('eol-transition',         '产品下线 / 退市'),
    ('workshops-facilitation', '工作坊与引导'),
    ('ai-agents',              'AI 与智能体编排'),
    ('career-leadership',      '职业成长与晋升'),
    ('meta-authoring',         '元技能：造技能'),
])
TYPE_CN = {'component': '组件', 'interactive': '交互', 'workflow': '工作流'}
TYPE_DESC = {
    'component':   '组件（模板 / 框架）—— 可独立套用的结构化产出物',
    'interactive': '交互（顾问式对话）—— 多轮追问后给出结论或方案',
    'workflow':    '工作流（端到端流程）—— 串联多个步骤跑完整件事',
}

# 中文一句话用途（77 条）
GLOSS = {
 'agent-orchestration-advisor': '把复杂 PM 任务拆成并行专职 AI 智能体：设计边界、交接与人工审核点',
 'ai-shaped-readiness-advisor': '评估团队是"AI 工具化"还是真正"AI 原生"，定位下一项该补的能力',
 'context-engineering-advisor': '诊断"上下文堆砌 vs 上下文工程"，救活臃肿脆弱的 AI 工作流',
 'altitude-horizon-framework':  '用"高度 / 视野"模型理解 PM → 产品总监的转变',
 'product-sense-interview-answer': '结构化组织产品感面试口述答案（假设 / 分群 / 痛点优先级 / MVP 取舍）',
 'director-readiness-advisor':  'PM → 产品总监：备战、面试、落地、再校准',
 'vp-cpo-readiness-advisor':    '冲刺 VP / CPO：备战、面试、落地、再校准',
 'executive-onboarding-playbook': '新任 VP / CPO 的 30-60-90 天诊断式入职计划',
 'jobs-to-be-done':             '结构化挖掘用户的"待办任务、痛点与收益"（JTBD）',
 'problem-statement':           '写出以用户为中心的问题陈述：谁被卡住 / 想做什么 / 为何重要 / 感受',
 'proto-persona':               '没研究预算时，用现有信号快速搭出可用的用户画像',
 'discovery-interview-prep':    '规划客户访谈的目标、分群、约束与方法',
 'opportunity-solution-tree':   '从结果 → 机会 → 方案 → 实验搭建机会解决方案树（Teresa Torres）',
 'problem-framing-canvas':      '用 MITRE 问题界定画布，在跳到方案前先把问题说清楚',
 'discovery-process':           '跑完整一轮发现周期：从问题假设到被验证的方案',
 'eol-checklist':               '分阶段的产品下线清单，每一项都有明确负责人',
 'eol-internal-enablement':     '公告前备好支持 FAQ、销售话术与异议处理',
 'eol-message':                 '写出体量合适的下线公告（从简短通知到分阶段沟通）',
 'eol-stakeholder-sequence':    '规划下线的沟通对象、顺序，以及每次谈话必须覆盖的要点',
 'eol-readiness-advisor':       '产品 / 功能下线的 go / no-go 评估，并匹配投入力度',
 'eol-process':                 '端到端跑完产品下线：决策 → 对齐 → 规划 → 准备 → 公告 → 收尾',
 'finance-metrics-quickref':    'SaaS 财务指标、公式与基准速查',
 'saas-economics-efficiency-metrics': '评估 SaaS 单位经济与资本效率（能否高效扩张）',
 'saas-revenue-growth-metrics': '计算与解读 SaaS 收入、留存与增长指标（MRR / 流失 / NRR）',
 'acquisition-channel-advisor': '用单位经济、客户质量与可扩展性评估获客渠道',
 'business-health-diagnostic':  '从增长、留存、效率、资本四个维度诊断 SaaS 业务健康度',
 'feature-investment-advisor':  '用收入影响、成本结构、ROI 与战略评估一个功能该不该做',
 'finance-based-pricing-advisor': '用 ARPU、转化、流失风险、NRR、回本期评估调价',
 'company-research':            '公司研究简报：高管原话、产品战略、组织背景',
 'intelligence-collection-disciplines': '像情报机构一样做竞研：8 种情报搜集学科 + 信号→推断链',
 'pestel-analysis':             'PESTEL 宏观环境分析（政治 / 经济 / 社会 / 技术 / 环境 / 法律）',
 'intel-discipline-advisor':    '把竞争或市场问题分流到对的情报学科、节奏与执行技能',
 'tam-sam-som-calculator':      '带明确假设与口径的 TAM / SAM / SOM 市场规模测算',
 'ansoff-matrix':               '用安索夫矩阵把增长选项映射成带风险评级的排序',
 'autonomous-investigation':    '所有调研技能背后的协议——让 AI 研究无需你盯着也能跑',
 'battle-card-builder':         '用公开证据产出竞品作战卡，每条论断都有标注与出处',
 'company-intel':               '用 7 个分析视角对一家公司 / 行业 / 竞对做结构化情报',
 'competitive-analysis-process': '六步编排完整竞品分析：从格局到战略方向',
 'competitive-intel-watch':     '基于历史快照的定时增量监控——到底变了什么',
 'competitive-research-snapshot': '带引用的竞争格局快照 + 对比矩阵 + "所以意味着什么"',
 'market-landscape-scan':       '用带引用的证据绘制市场细分、玩家、替代品与空白区',
 'pestel-delta-monitor':        'PESTEL 季度重扫：哪些宏观因子动了、哪些假设破了',
 'porters-five-forces':         '用波特五力读行业结构，每项评级都有信号支撑',
 'pricing-packaging-tracker':   '把竞品定价与打包做成可 diff 的时间序列',
 'swot-analysis':               '基于公开证据的 SWOT，并落到"所以该怎么办"',
 'voice-of-customer-miner':     '挖公开评论 / 应用商店 / 论坛，提炼未满足需求与切换触发点',
 'pm-skill-creator':            '对话式设计一个新的 PM 技能',
 'skill-authoring-workflow':    '把原始 PM 素材变成合规、可发布的技能',
 'epic-hypothesis':             '把 Epic 写成可检验的假设：目标用户 / 预期结果 / 验证方式',
 'press-release':               '亚马逊式新闻稿：先定义客户价值，再动手做',
 'storyboard':                  '六格故事板，展示用户从问题到方案的旅程',
 'user-story':                  'Mike Cohn 格式用户故事 + Gherkin 验收标准',
 'user-story-mapping':          '用户故事地图：活动 / 步骤 / 任务 / 发布切片',
 'user-story-splitting':        '用成熟拆分模式把大故事 / Epic 拆成可交付的小故事',
 'epic-breakdown-advisor':      '用 Humanizing Work 拆分模式把 Epic 拆成用户故事',
 'prd-development':             '结构化 PRD：串起问题、用户、方案与成功标准',
 'product-lifecycle-plays':     '判断产品处于生命周期哪一段，在延展 / 替换 / 退市之间选招',
 'lifecycle-play-advisor':      '诊断产品生命周期位置并匹配打法（延展 / 替换 / 退市）',
 'stakeholder-identification':  '动手前先把干系人找全',
 'stakeholder-mapping':         '用两张互补网格给干系人排优先级',
 'incoming-request-advisor':    '把一条消息拆成"字面请求 vs 真实待办任务"',
 'stakeholder-engagement-advisor': '针对特定干系人规划沟通：外联、化解阻力、对齐',
 'positioning-statement':       'Geoffrey Moore 式定位陈述',
 'organic-growth-advisor':      '判断走哪条有机增长路径：新细分 / 新地域 / 新渠道 / 新产品',
 'prioritization-advisor':      '依据阶段、团队情境与干系人需求，选择优先级框架',
 'product-strategy-session':    '端到端产品战略会：定位 → 发现 → 路线图',
 'roadmap-planning':            '战略路线图规划：优先级、Epic 定义、干系人对齐、排序',
 'pol-probe':                   '定义低成本的"Proof of Life"探针：先要残酷真相，再动手做',
 'recommendation-canvas':       '从结果、假设、风险、定位四维评估一个 AI 产品点子',
 'derisk-measurement-advisor':  '明确该测什么、追踪什么，来给产品或 AI 点子降险',
 'lean-ux-canvas':              '引导 Lean UX Canvas v2：业务问题、假设、实验',
 'pol-probe-advisor':           '按假设、风险与资源，挑选合适的 PoL 探针',
 'customer-journey-map':        '客户旅程图：阶段 / 触点 / 行为 / 情绪 / 指标',
 'customer-journey-mapping-workshop': '引导式客户旅程映射工作坊',
 'positioning-workshop':        '定位工作坊：目标客户、未满足需求、品类、收益、差异化',
 'user-story-mapping-workshop': '引导式用户故事映射工作坊，产出结构化地图',
 'workshop-facilitation':       '单步多轮的工作坊引导引擎（其他交互技能复用）',
}

# 场景速查（场景 -> 技能 dir 列表）
SCEN = [
 ('写 PRD / 需求文档',                 ['prd-development', 'problem-statement', 'epic-hypothesis']),
 ('需求该不该做 / 排优先级',           ['prioritization-advisor', 'feature-investment-advisor', 'incoming-request-advisor']),
 ('规划季度 / 年度路线图',             ['roadmap-planning', 'epic-breakdown-advisor', 'product-strategy-session']),
 ('做市场 / 竞品分析',                 ['competitive-research-snapshot', 'company-intel', 'battle-card-builder', 'market-landscape-scan', 'voice-of-customer-miner']),
 ('测算市场规模 TAM/SAM/SOM',          ['tam-sam-som-calculator', 'ansoff-matrix', 'porters-five-forces']),
 ('算 SaaS 指标 / 体检业务',           ['saas-revenue-growth-metrics', 'saas-economics-efficiency-metrics', 'business-health-diagnostic', 'finance-metrics-quickref']),
 ('要不要涨价 / 怎么打包',             ['finance-based-pricing-advisor', 'pricing-packaging-tracker']),
 ('用户研究 / 客户访谈',               ['discovery-interview-prep', 'jobs-to-be-done', 'proto-persona', 'problem-framing-canvas', 'opportunity-solution-tree']),
 ('写用户故事 / 拆 Epic',              ['user-story', 'user-story-splitting', 'user-story-mapping', 'epic-breakdown-advisor']),
 ('定位 / 战略',                       ['positioning-statement', 'positioning-workshop', 'product-strategy-session', 'organic-growth-advisor']),
 ('验证一个点子（含 AI 点子）',        ['pol-probe', 'pol-probe-advisor', 'recommendation-canvas', 'derisk-measurement-advisor', 'lean-ux-canvas']),
 ('干系人沟通 / 老板提需求',           ['incoming-request-advisor', 'stakeholder-identification', 'stakeholder-mapping', 'stakeholder-engagement-advisor']),
 ('产品要下线 / 退市',                 ['eol-readiness-advisor', 'eol-process', 'eol-message', 'eol-checklist']),
 ('办工作坊',                          ['workshop-facilitation', 'positioning-workshop', 'customer-journey-mapping-workshop', 'user-story-mapping-workshop']),
 ('晋升 / 面试 / 入职',                ['director-readiness-advisor', 'vp-cpo-readiness-advisor', 'product-sense-interview-answer', 'executive-onboarding-playbook', 'altitude-horizon-framework']),
 ('用 AI 改造 PM 工作流',              ['agent-orchestration-advisor', 'ai-shaped-readiness-advisor', 'context-engineering-advisor']),
]

def esc(s): return s.replace('|', '\\|')

out = io.StringIO()
w = out.write
w('# 产品经理技能使用清单\n\n')
w('> 技能库：`deanpeters/Product-Manager-Skills`（GitHub 7030 ★，PM 领域星数第一，作者 Dean Peters，活跃维护）\n')
w('> 安装位置：`D:\\code\\hermes\\skills\\product-management\\`　共 **77 个技能**，全部 enabled、local 源\n')
w('> 工作目录：`D:\\code\\hermes\\ai_pm\\`　本清单生成于 %s\n\n' % datetime.date.today().isoformat())
w('---\n\n')

w('## 一、怎么用（3 种方式）\n\n')
w('**1. 直接说人话（推荐）**——不需要记技能名，描述你的处境就会自动触发。例：\n\n')
w('```\n我需要一个 XX 功能的 PRD，背景是……\n这个需求该不该做？我们只有 2 个前端，Q2 要上线\n帮我测算一下这个细分市场的 TAM/SAM/SOM\n季度复盘：我们 NRR 掉到 95%，帮我体检一下\n```\n\n')
w('**2. 点名调用**——想精确控制时直接报技能名：\n\n')
w('```\n用 prd-development 帮我写 PRD，输入是下面这些发现笔记：……\n用 roadmap-planning 把 15 个竞争性项目排成 Q2 路线图\n```\n\n')
w('**3. 组合调用（威力最大的用法）**——上游技能产出结构化素材，喂给下游技能。例：\n\n')
w('```\ncompany-intel → battle-card-builder → positioning-statement → prd-development → roadmap-planning\n（摸清对手 → 作战卡 → 定位 → PRD → 路线图）\n```\n\n')
w('> 库内技能是刻意按"可串联"设计的：`company-intel`、`competitive-research-snapshot` 等的输出格式\n')
w('> 可以直接喂给 `swot-analysis` / `pestel-analysis` / `positioning-statement` / `battle-card-builder`。\n\n')
w('---\n\n')

w('## 二、77 个技能全清单（按主题分组）\n\n')
w('类型说明：**组件** = 模板 / 框架，一次性套用；**交互** = 顾问式多轮对话，先追问再给结论；**工作流** = 端到端多步骤流程。\n\n')

themes = defaultdict(list)
for r in rows:
    themes[r['theme']].append(r)
order = list(THEME_CN.keys()) + [t for t in themes if t not in THEME_CN]
seen = set()
for th in order:
    if th in seen or th not in themes:
        continue
    seen.add(th)
    items = sorted(themes[th], key=lambda r: (r['type'], r['dir']))
    w('### %s（%d）\n\n' % (THEME_CN.get(th, th), len(items)))
    w('| 技能 | 类型 | 耗时 | 用途 |\n|---|---|---|---|\n')
    for r in items:
        w('| `%s` | %s | %s | %s |\n' % (
            r['dir'], TYPE_CN.get(r['type'], r['type']),
            esc(r['est']) or '—', esc(GLOSS.get(r['dir'], r['desc'][:60]))))
    w('\n')
    # 触发示例
    w('<details><summary>触发示例（可直接照抄改写）</summary>\n\n')
    for r in items:
        if r['scenarios']:
            w('- **%s** → `%s`\n' % (esc(r['scenarios'][0]), r['dir']))
    w('\n</details>\n\n')

w('---\n\n')
w('## 三、场景速查（我要办这件事，该用哪些）\n\n')
w('| 我要做的事 | 技能（按推荐顺序） |\n|---|---|\n')
for name, dirs in SCEN:
    w('| %s | %s |\n' % (name, ' · '.join('`%s`' % d for d in dirs)))
w('\n---\n\n')

w('## 四、按类型索引\n\n')
for t in ('component', 'interactive', 'workflow'):
    items = sorted([r['dir'] for r in rows if r['type'] == t])
    w('- **%s**（%d）：%s\n' % (TYPE_DESC[t], len(items), '、'.join('`%s`' % d for d in items)))
w('\n---\n\n')

w('## 五、备注\n\n')
w('- 技能本体在 `D:\\code\\hermes\\skills\\product-management\\<技能名>\\SKILL.md`；部分技能带 `template.md`（可直接套的模板）。\n')
w('- 每个技能正文包含：Purpose / Input / 执行步骤 / 输出格式 / 质量校验。需要看细节时直接让我读某个技能的 SKILL.md。\n')
w('- 77 个技能的描述常驻系统提示词，约占 1.26 万字符上下文；若嫌重，可按主题裁掉不用的（例如只留 delivery + strategy）。\n')
w('- 这是"技能"不是"命令"：无需斜杠，说需求即触发；想强制指定就报技能名。\n')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs/产品经理技能使用清单.md')
open(path, 'w', encoding='utf-8').write(out.getvalue())
print('written:', path, len(out.getvalue()), 'chars')
