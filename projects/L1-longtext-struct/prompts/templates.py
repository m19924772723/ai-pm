# -*- coding: utf-8 -*-
"""三个模板的提示词。

与 docs/L1提示词初稿.md 保持一致：改提示词时两处一起改。
设计要点：
- 只用原文信息，信息不足写"原文未提供"或空数组
- 每条关键点/待办必须带 evidence 原文短引
- 只输出 JSON，不输出解释
"""

SYSTEM_PROMPT = """你是“长文结构化助手”。你的工作是仅依据用户提供的原文，提取可验证的信息，并输出符合指定 JSON Schema 的结果。

硬性规则：
1. 不使用原文以外的知识补充事实、背景、数字、人物或结论。
2. 原文没有明确支持的信息，填“原文未提供”或空数组，不要猜测。
3. evidence 必须是原文中的**连续原文片段**，逐字引用原文（允许删去中间若干字，但不得改写用词、不得跨句拼接、不得合并多句）。
4. 保留原文中的数字、日期、主体名称和限定条件；不能擅自改写其含义。
5. 只输出合法 JSON，不要 Markdown 代码块、前言、解释或额外字段。"""

SUMMARY_USER = """任务：将下列文章结构化为“摘要模式”。

输出目标：帮助读者在 30 秒内知道文章的主题、结论、关键论据和可执行事项。

输出 JSON Schema：
{
  "title": "string，文章标题；没有则写原文未提供",
  "one_sentence_summary": "string，不超过 60 字",
  "key_points": [
    {"point": "string，不超过 50 字", "evidence": "string，原文短引，不超过 40 字"}
  ],
  "tags": ["string，2-5 个"],
  "todos": [
    {"action": "string，原文明确要求执行的动作；没有则为空数组",
     "owner": "string，原文明确指定的主体；没有则写未指定",
     "deadline": "string，原文明确给出的时间；没有则写未指定",
     "evidence": "string，原文短引，不超过 40 字"}
  ],
  "uncertainties": ["string，原文存在冲突、信息不足或无法判定之处"]
}

约束：
- key_points 输出 3-5 条；原文不足 3 条时按实际数量输出。
- tags 只用原文明确出现或可直接归纳的主题词。
- 不要把推测写成事实。

文章原文：
<<<
{{INPUT_TEXT}}
>>>"""

TODOS_USER = """任务：从下列文章中只提取“明确需要行动”的事项，生成待办模式 JSON。

判断标准：只有原文包含明确动作、责任主体、截止时间或交付物中的至少一项时，才能作为待办。观点、愿望、背景介绍不是待办。

输出 JSON Schema：
{
  "title": "string，文章标题；没有则写原文未提供",
  "todos": [
    {"action": "string，动作以动词开头",
     "owner": "string，原文明确指定的主体；没有则写未指定",
     "deadline": "string，原文明确给出的时间；没有则写未指定",
     "deliverable": "string，原文明确要求的产出；没有则写未指定",
     "priority": "high | medium | low | unspecified",
     "evidence": "string，原文短引，不超过 40 字"}
  ],
  "not_todos": ["string，容易被误判为待办但实际只是观点/背景的内容"]
}

约束：
- 原文没有明确待办时，todos 必须是 []；不能为了填充而编造。
- priority 只有原文给出紧急程度时才填 high/medium/low，否则填 unspecified。
- 只输出合法 JSON。

文章原文：
<<<
{{INPUT_TEXT}}
>>>"""

ARCHIVE_USER = """任务：将下列文章整理为可检索的归档卡片。

输出 JSON Schema：
{
  "title": "string，文章标题；没有则写原文未提供",
  "source_type": "article | report | meeting_note | paper | unknown",
  "topic": "string，文章的核心主题",
  "summary": "string，不超过 100 字",
  "claims": [
    {"claim": "string，原文中的核心主张", "evidence": "string，原文短引，不超过 40 字"}
  ],
  "facts": [
    {"fact": "string，含数字、日期、名称或可核验事实", "evidence": "string，原文短引，不超过 40 字"}
  ],
  "keywords": ["string，3-7 个"],
  "follow_up_questions": ["string，原文未回答但继续阅读前值得确认的问题"]
}

约束：
- claims 与 facts 分开：主张不是事实。
- 原文没有数字/日期/名称等可核验事实时，facts 可为空数组。
- follow_up_questions 只能基于原文缺口提出，不要回答问题。
- 只输出合法 JSON。

文章原文：
<<<
{{INPUT_TEXT}}
>>>"""

PLACEHOLDER = "{{INPUT_TEXT}}"

TEMPLATES = {
    "summary": {"name": "摘要模式", "user": SUMMARY_USER},
    "todos": {"name": "待办模式", "user": TODOS_USER},
    "archive": {"name": "归档模式", "user": ARCHIVE_USER},
}


def build_user_prompt(template: str, input_text: str) -> str:
    """按模板拼出完整 User Prompt。

    注意：模板正文里有 JSON Schema 的花括号，**不能用 str.format()**，
    否则会抛 KeyError。这里用显式占位符替换。
    """
    if template not in TEMPLATES:
        raise KeyError(f"未知模板: {template}；可选 {list(TEMPLATES)}")
    return TEMPLATES[template]["user"].replace(PLACEHOLDER, input_text)
