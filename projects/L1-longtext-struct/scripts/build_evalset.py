# -*- coding: utf-8 -*-
"""构建 20 条评测集（可复现）。

构成（对应 L1 说明书 Day 8："长短不一、中英混合、含表格的 PDF"）：
- 长度：短(<500字)×7 / 中(500-2500)×10 / 长(>2500)×2 / 超长(>24000, 触发截断)×1
- 语言：中文×15 / 英文×3 / 中英混合×2
- 模板：summary×9 / todos×6 / archive×5
- 特殊：真实文章×2、含表格 PDF 提取×1、超长截断×1、真实来源注明

gold_points = 人工标注（本脚本作者于 2026-10-01 标注草稿），与输入严格对应、可逐条核对；
建议用户抽查复核后把 meta.gold_status 改为 reviewed。

用法：.venv/Scripts/python.exe scripts/build_evalset.py
产物：tests/eval_set.json（直接覆盖）
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample_inputs"


def read_real(name: str, header: int = 2) -> str:
    """读已保存的真实文本，跳过文件头两行（标题/URL）。"""
    txt = (DATA / name).read_text(encoding="utf-8")
    return txt.split("\n\n", header - 1)[-1].strip() if header else txt


# 真实来源：woshipm 价值公式文章（已保存在 sample_inputs）
WOSHIPM = read_real("woshipm_产品价值公式.txt")

# 真实来源：Prompt Engineering Guide 基本概念页（中文，1838 字，已实测抓取）
PROMPT_GUIDE = """基本概念

你可以通过简单的提示词（Prompts）获得大量结果，但结果的质量与你提供的信息数量和完善度有关。一个提示词可以包含你传递到模型的指令或问题等信息，也可以包含其他详细信息，如上下文、输入或示例等。你可以通过这些元素来更好地指导模型，并因此获得更好的结果。

看下面一个简单的示例：提示词：The sky is，输出：blue。然而，语言模型能够基于我们给出的上下文内容完成续写。输出可能是出乎意料的，或者与你想要完成的任务相去甚远。实际上，这个基本示例突出了提供更多上下文或明确指示你想要实现什么的必要性。这正是提示工程的核心所在。

让我们试着改进一下：提示词：Complete the sentence: The sky is，输出：blue during the day and dark at night。结果是不是要好一些了？本例中，我们告知模型去完善句子，因此输出结果看起来要好得多，因为它完全按照你告诉它要做的（"完善句子"）去做。在本指南中，这种设计有效的提示词以指导模型执行期望任务的方法被称为提示工程。

提示词格式。标准提示词应该遵循以下格式：<问题>? 或 <指令>。你可以将其格式化为问答（QA）格式，这在许多问答数据集中是标准格式：Q: <问题>? A:。当像上面那样提示时，这也被称为零样本提示，即你直接提示模型给出一个回答，而没有提供任何关于你希望它完成的任务的示例或示范。一些大型语言模型具备进行零样本提示的能力，但这取决于手头任务的复杂性和知识，以及模型被训练以在其上表现良好的任务。

基于以上标准格式，一种流行且有效的提示技术被称为少样本提示，其中你提供示例（即示范）。你可以按照以下格式组织少样本提示：<问题>? <答案> <问题>? <答案> <问题>? <答案> <问题>?。请记住，使用问答格式并非必须。提示格式取决于手头的任务。例如，你可以执行一个简单的分类任务，并给出如下所示的示例来给任务示范。语言模型可以基于一些说明了解和学习某些任务，而小样本提示正好可以赋能上下文学习能力。我们将在接下来的章节中更广泛的讨论如何使用零样本提示和小样本提示。"""

# 含表格的 PDF 报告的提取文本（scripts/make_table_pdf.py 生成 PDF 后由 extract_from_pdf 真实提取，
# 表格列按文本块分行——这正是"含表格 PDF"的真实提取形态，拿它当输入才诚实）
TABLE_REPORT = """月度经营报告（2026 年 9 月）
指标
8 月
9 月
环比
新增用户
4200
5100
+21.4%
次周留存
31%
33%
+2pp
月收入
18.6 万21.2 万+14.0%
客服工单
203
187
-7.9%
一、核心指标
（见上方表格）
二、结论
1. 新增用户连续三个月增长，9 月达到 5100 人。
2. 次周留存提升 2 个百分点，主要来自新手引导改版。
3. 月收入突破 20 万，客单价保持稳定。
4. 客服工单下降，但高峰时段排队仍超 10 分钟，建议下季度扩编一名客服。
三、风险
- 10 月 15 日需完成合规备案，否则影响十一活动。
- 服务器迁移计划在 10 月 8 日执行，需提前通知全部商户。"""


def long_text(repeat: int = 260) -> str:
    """生成超长中文文本（>24000 字），考察长文不崩 + 截断警告路径。"""
    para = (
        "长文评测样本正文。本项目致力于把长文档结构化为可核验的信息，要求每条结论都能在原文中找到依据。"
        "评测样本需要覆盖多种长度、语言和体裁，以检验结构化工具在不同输入下的稳定性。"
        "数字、日期与主体名称必须保留原貌，例如 10 月 8 日、60%、张三和王五。"
        "当输入超过 24000 字时，系统应当截断并给出明确警告，而不是报错中断。\n"
    )
    return para * repeat


SAMPLES = [
    # ---------- 保留的 Day5 四条 ----------
    {
        "id": "S01", "template": "summary", "lang": "zh", "len_class": "short",
        "scene": "课程小组通知", "source": "合成",
        "input": "学院要求各项目组在 10 月 8 日前提交中期报告。报告须包含目前进度、风险和下周计划。张三负责汇总技术进度，李四负责补充用户访谈记录。项目当前已完成 60% 的开发。",
        "gold_points": ["10 月 8 日前提交中期报告", "报告含进度、风险、下周计划", "张三汇总技术进度", "李四补充用户访谈记录", "开发完成 60%"],
        "notes": "基础功能验证：日期、责任人、进度数字必须保留",
    },
    {
        "id": "S02", "template": "summary", "lang": "zh", "len_class": "short",
        "scene": "观点文章（无待办）", "source": "合成",
        "input": "很多人以为产品经理的工作是画原型和写文档。实际上，产品经理的核心能力是判断做什么和不做什么。原型和文档只是表达方式，判断力才是稀缺资源。一个只会上传下达的产品经理，很快会被流程替代。",
        "gold_points": ["产品经理核心能力是判断做什么和不做什么", "原型文档只是表达方式", "判断力是稀缺资源"],
        "notes": "负样本：全文没有待办，todos 必须是空数组",
    },
    {
        "id": "S03", "template": "todos", "lang": "zh", "len_class": "short",
        "scene": "周会纪要（混入观点干扰）", "source": "合成",
        "input": "本季度我们的用户留存明显下滑。王五需要在 9 月 30 日前完成流失用户访谈，至少覆盖 10 人。我认为根本原因是新手引导太长。赵六负责在下周五前给出一版缩短 30% 的引导方案。另外，团队士气也需要关注。",
        "gold_points": ["王五 9 月 30 日前完成流失用户访谈，覆盖至少 10 人", "赵六下周五前给出缩短 30% 的引导方案"],
        "notes": "干扰项：留存下滑/士气是背景观点，不是待办",
    },
    {
        "id": "S04", "template": "archive", "lang": "zh", "len_class": "short",
        "scene": "灰度测试报告", "source": "合成",
        "input": "本次灰度测试于 9 月 20 日上线，覆盖 2000 名用户。测试期间接口平均延迟从 1.2 秒降到 0.8 秒。我们认为延迟下降主要来自缓存命中率提升，但这个结论还没有做对照实验验证。",
        "gold_points": ["9 月 20 日上线，覆盖 2000 名用户", "延迟从 1.2 秒降到 0.8 秒", "延迟下降归因于缓存尚未验证"],
        "notes": "facts 与 claims 分开：归因是未验证主张",
    },
    # ---------- 真实来源 ----------
    {
        "id": "S05", "template": "summary", "lang": "zh", "len_class": "long",
        "scene": "产品方法论文章", "source": "真实 woshipm(2595761) 2776字",
        "input": WOSHIPM,
        "gold_points": [
            "产品价值 =（新体验 - 旧体验）- 迁移成本",
            "存量市场竞争是用户迁移/产品替换的竞争",
            "体验差大于迁移成本时用户做出使用新产品的决定",
            "绝对价值没有意义，相对价值才是竞争筹码",
            "降低迁移成本的手段分为内在动力与外部刺激",
        ],
        "notes": "真实长文；检验长输入下的结构化稳定性与证据约束",
    },
    {
        "id": "S06", "template": "archive", "lang": "zh", "len_class": "medium",
        "scene": "技术文档页", "source": "真实 promptingguide.ai/zh/introduction/basics 1838字",
        "input": PROMPT_GUIDE,
        "gold_points": [
            "提示词质量与提供的信息数量和完善度有关",
            "提示工程是设计有效提示词以指导模型执行期望任务的方法",
            "零样本提示是直接给出指令而不提供示例",
            "少样本提示通过提供示例（示范）赋能上下文学习",
            "标准提示词格式为问题或指令，可组织为问答格式",
        ],
        "notes": "真实技术文档；归档模式应区分概念与事实",
    },
    # ---------- 中文 ----------
    {
        "id": "S07", "template": "summary", "lang": "zh", "len_class": "short",
        "scene": "健康科普公众号文", "source": "合成",
        "input": "春季是过敏高发期。医学研究表明，每天开窗通风 15 分钟可以有效降低室内尘螨浓度。医生建议，过敏人群外出佩戴防尘口罩，回家后及时清洗鼻腔。如果症状持续超过一周，应尽早就医，不建议自行长期服用抗组胺药。",
        "gold_points": ["每天开窗通风 15 分钟可降低尘螨浓度", "过敏人群外出戴口罩、回家清洗鼻腔", "症状超一周应就医", "不建议长期自行服用抗组胺药"],
        "notes": "日常健康文；要点提取 + 建议类内容",
    },
    {
        "id": "S08", "template": "todos", "lang": "zh", "len_class": "medium",
        "scene": "项目启动会纪要", "source": "合成",
        "input": "10 月 6 日召开智慧校园项目启动会，共 5 家部门参加。会议决定：校办在 10 月 20 日前完成招标文件编制；信息中心于 11 月 1 日前提交流程清单；教务处负责 10 月 30 日前组织一轮供应商演示；财务处确认预算冻结期为 4 周。项目经理建议每周五同步进度，但该建议未获表决。",
        "gold_points": ["校办 10 月 20 日前完成招标文件编制", "信息中心 11 月 1 日前提交流程清单", "教务处 10 月 30 日前组织供应商演示", "财务处确认预算冻结期 4 周"],
        "notes": "多主体多死线；'建议每周五同步'是建议不是决定",
    },
    {
        "id": "S09", "template": "summary", "lang": "en", "len_class": "short",
        "scene": "产品发布备忘录", "source": "合成",
        "input": "We are announcing the GA release of Atlas v2.0 on October 12. The new version reduces cold-start latency by 40% and adds offline mode. The pricing remains unchanged for existing customers until December 31. Team leads should update their onboarding docs before October 10.",
        "gold_points": ["GA release of Atlas v2.0 on October 12", "cold-start latency reduced by 40%", "offline mode added", "pricing unchanged until December 31", "team leads update onboarding docs before October 10"],
        "notes": "英文；日期与百分比是硬指标",
    },
    {
        "id": "S10", "template": "todos", "lang": "en", "len_class": "short",
        "scene": "例会行动项", "source": "合成",
        "input": "Action items from the standup: Alice will finalize the API spec by Friday. Bob to fix the login timeout bug before the sprint review next Wednesday. Carol is investigating the pagination issue, no deadline set. We also discussed hosting a webinar, but nothing was decided.",
        "gold_points": ["Alice finalizes API spec by Friday", "Bob fixes login timeout bug before sprint review next Wednesday"],
        "notes": "英文干扰项：研究中的事项与未决定事项不是待办",
    },
    {
        "id": "S11", "template": "archive", "lang": "en", "len_class": "medium",
        "scene": "论文摘要与结论", "source": "合成",
        "input": "Abstract. We evaluate retrieval-augmented generation pipelines on 1,200 product-support queries. The best configuration combines a dense retriever with a re-ranking model, improving answer faithfulness from 68% to 81% over the baseline. However, all pipelines degrade on out-of-domain queries, which we attribute to sparse coverage in the knowledge base. We release the evaluation dataset under CC-BY license.",
        "gold_points": ["1,200 product-support queries evaluated", "answer faithfulness improved from 68% to 81%", "dense retriever plus re-ranking is the best configuration", "pipelines degrade on out-of-domain queries", "dataset released under CC-BY"],
        "notes": "英文论文式；事实与主张分离",
    },
    {
        "id": "S12", "template": "summary", "lang": "zh-en", "len_class": "short",
        "scene": "技术公告（中英术语混合）", "source": "合成",
        "input": "从 10 月 1 日起，API v1 端点 /v1/legacy 进入维护模式，将于 2027 年 1 月 1 日停用。请所有客户迁移到 /v2/batch，新端点支持 streaming 和 batch 两种模式。迁移期间旧端点保持可用，但不再接收新增 feature 请求。",
        "gold_points": ["API v1 端点 2027 年 1 月 1 日停用", "客户须迁移到 /v2/batch", "新端点支持 streaming 和 batch", "旧端点迁移期间保持可用"],
        "notes": "中英混合；术语必须原样保留",
    },
    {
        "id": "S13", "template": "todos", "lang": "zh-en", "len_class": "medium",
        "scene": "云迁移公告", "source": "合成",
        "input": "公司将于 10 月 8 日执行数据库迁移，预计停机 2 小时。数据组需要在 10 月 5 日前完成全量备份校验；安全组在 10 月 7 日前复核权限白名单；每个业务线负责人必须在迁移前 24 小时确认各自服务的 rollback 方案。建议各部门提前通知客户，这是运营建议而非硬性要求。",
        "gold_points": ["10 月 8 日执行数据库迁移，停机 2 小时", "数据组 10 月 5 日前完成备份校验", "安全组 10 月 7 日前复核权限白名单", "业务线负责人迁移前 24 小时确认 rollback 方案"],
        "notes": "硬待办 4 条 + 1 条软建议（提前通知客户）应进 not_todos",
    },
    {
        "id": "S14", "template": "archive", "lang": "zh", "len_class": "medium",
        "scene": "月度经营报告（含表格，由 PDF 提取）", "source": "真实生成 PDF(pymupdf) → 提取文本",
        "input": TABLE_REPORT,
        "gold_points": [
            "9 月新增用户 5100，环比 +21.4%",
            "次周留存 33%，提升 2 个百分点",
            "月收入 21.2 万，环比 +14.0%",
            "10 月 15 日需完成合规备案",
            "服务器迁移 10 月 8 日执行",
        ],
        "notes": "含表格文本；事实/风险分离，数字必须逐字保留",
    },
    {
        "id": "S15", "template": "summary", "lang": "zh", "len_class": "medium",
        "scene": "行业分析长文", "source": "合成",
        "input": (
            "2026 年大模型应用进入深水区。上半年企业级 Agent 的渗透率从 18% 上升到 34%，但生产环境的落地率不足一半。"
            "头部厂商的竞争焦点从基础模型转向工具链：MCP 协议成为连接模型与系统的默认标准，超过 300 家工具厂商接入。"
            "成本侧，同一任务的推理成本较 2025 年下降约 60%，主要来自缓存与模型蒸馏。"
            "然而，评估仍是最大短板：仅 22% 的企业建立了基于真实轨迹的评测集，多数团队仍在用人工抽查。"
            "监管方面，新版生成式 AI 管理办法将于 2027 年 3 月施行，重点约束训练数据合规与输出溯源。"
            "对应用型团队的建议是：先建评测集，再谈优化；先服务内部场景，再对外发布。\n\n"
            "第二段补充：中小团队与大厂的分化在加剧。大厂凭借算力和数据优势，将 Agent 能力以 API 形式输出；"
            "中小团队则集中在垂直场景（法律、医疗、教育）打磨闭环。三个信号值得关注：一是长上下文模型的成本拐点，"
            "二是浏览器 Agent 的稳定性跃升，三是多模态输入在文档理解场景的渗透。行业报告预计，2027 年底 Agent 相关岗位需求将同比翻倍。"
        ),
        "gold_points": [
            "企业级 Agent 渗透率从 18% 升到 34%",
            "推理成本较 2025 年下降约 60%",
            "仅 22% 企业建立真实轨迹评测集",
            "新版管理办法 2027 年 3 月施行",
            "2027 年底 Agent 岗位需求同比翻倍",
        ],
        "notes": "长文多段；数字密集，全部必须保留",
    },
    {
        "id": "S16", "template": "todos", "lang": "zh", "len_class": "medium",
        "scene": "校园活动策划", "source": "合成",
        "input": "科技文化节定于 11 月 15-16 日举行。筹备组分工如下：宣传组于 10 月 25 日前完成海报和公众号推文；外联组在 10 月 30 日前确认场地与赞助商，暂定礼堂 A 和 B；物资组 11 月 5 日前清点设备并提交采购清单；报名通道 11 月 1 日开放。天气原因外场活动有推迟风险，此点仅供参考通知。",
        "gold_points": ["宣传组 10 月 25 日前完成海报和推文", "外联组 10 月 30 日前确认场地与赞助商", "物资组 11 月 5 日前提交采购清单", "报名通道 11 月 1 日开放"],
        "notes": "多组分工；'天气风险'是背景不是待办",
    },
    {
        "id": "S17", "template": "archive", "lang": "zh", "len_class": "short",
        "scene": "会议纪要归档", "source": "合成",
        "input": "2026-09-25 评审会纪要。议题：新用户首页改版方案。结论：采用方案 B，保留搜索入口权重。参会 12 人，无人反对。遗留问题：暗色模式下对比度不足，交由设计组跟进；数据埋点方案下周二前补齐。",
        "gold_points": ["2026-09-25 召开评审会", "采用方案 B，保留搜索入口权重", "参会 12 人", "遗留：暗色对比度问题与埋点方案"],
        "notes": "纪要素材：时间/结论/人数/遗留",
    },
    {
        "id": "S18", "template": "summary", "lang": "zh", "len_class": "medium",
        "scene": "学术论文摘要", "source": "合成",
        "input": "本文针对印刷品表面缺陷检测场景提出一种轻量分割网络。方法：以 MobileNetV3 为骨干，引入边界回归分支，参数规模 380 万。在 2000 张缺陷图上对比，mIoU 从 61.4% 提升至 74.2%，单帧推理时间 42ms。局限：极端光照条件下召回率下降 12%，后续拟引入图像增强与多尺度融合。",
        "gold_points": ["轻量分割网络，骨干 MobileNetV3，380 万参数", "mIoU 从 61.4% 提升至 74.2%", "单帧推理 42ms", "极端光照下召回率下降 12%"],
        "notes": "论文摘要；方法/数字/局限三类信息",
    },
    {
        "id": "S19", "template": "summary", "lang": "zh", "len_class": "overlong",
        "scene": "超长文本（>24000 字）", "source": "合成（程序生成）",
        "input": long_text(),
        "gold_points": ["超过 24000 字应截断并给出警告", "数字与主体名在截断片段内保留"],
        "notes": "超长路径：必须在 warnings 出现截断提示，不能崩溃",
    },
    {
        "id": "S20", "template": "todos", "lang": "zh", "len_class": "short",
        "scene": "周报（观点与真待办混排）", "source": "合成",
        "input": "本周完成注册流程重构，转化率提升 5 个百分点，我很满意这个结果。下周计划：周一评审新版结算页；周三前修复优惠券重叠使用的 bug，由陈七负责；周五输出 A/B 实验复盘报告。另外，产品文档一直没人更新，这个问题已经拖了很久。",
        "gold_points": ["周一评审新版结算页", "陈七周三前修复优惠券 bug", "周五输出 A/B 实验复盘报告"],
        "notes": "'我很满意''文档没人更新'是观点/抱怨，不是带责任的待办",
    },
]


def stats(samples: list[dict]) -> dict:
    from collections import Counter

    return {
        "count": len(samples),
        "by_template": dict(Counter(s["template"] for s in samples)),
        "by_lang": dict(Counter(s["lang"] for s in samples)),
        "by_len": dict(Counter(s["len_class"] for s in samples)),
        "real_sources": sum(1 for s in samples if s["source"].startswith("真实")),
        "gold_total": sum(len(s["gold_points"]) for s in samples),
    }


def main() -> int:
    st = stats(SAMPLES)
    doc = {
        "meta": {
            "created": "2026-09-27",
            "updated": "2026-10-01",
            "target_count": 20,
            "current_count": len(SAMPLES),
            "gold_status": "draft_manual（2026-10-01 标注草稿，建议人工抽查复核）",
            "metrics": ["要点覆盖率", "幻觉率", "格式合规率"],
            "composition": st,
        },
        "samples": SAMPLES,
    }
    out = ROOT / "tests" / "eval_set.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(st, ensure_ascii=False, indent=2))
    print(f"已写入: {out}（{st['count']} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())