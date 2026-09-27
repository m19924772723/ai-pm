# -*- coding: utf-8 -*-
"""L1-1 长文结构化 —— Streamlit 界面。

启动：streamlit run app.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from extractors.pdf import extract_from_pdf
from extractors.web import ExtractionError, extract_from_url
from pipeline import MAX_CHARS, structure, to_markdown
from prompts.templates import TEMPLATES
from utils.llm import available_providers

st.set_page_config(page_title="长文结构化助手", page_icon="📄", layout="wide")

st.title("长文结构化助手")
st.caption("粘贴或上传一篇文章，一键出摘要 / 待办 / 归档结果。结果只依据原文，每条关键点都带原文依据。")

with st.sidebar:
    st.subheader("设置")
    provs = available_providers()
    if not provs:
        st.error("未检测到可用的模型密钥。请在环境变量中配置后再试。")
        st.stop()
    provider = st.selectbox("模型端点", provs, index=0)
    st.caption("密钥只从环境变量读取，不会写入仓库。")
    st.divider()
    st.caption(f"单次输入上限 {MAX_CHARS} 字，超出会截断。")

tab_text, tab_url, tab_pdf = st.tabs(["粘贴文本", "链接抓取", "PDF 上传"])

source_text, source_label, extract_warnings = "", "", []
extract_method = ""

with tab_text:
    t = st.text_area("把文章正文粘贴到这里", height=240, key="paste",
                     placeholder="粘贴一篇公众号长文、报告或论文正文…")
    if t.strip():
        source_text, source_label = t, "粘贴文本"

with tab_url:
    u = st.text_input("网页链接", key="url", placeholder="https://…")
    if st.button("抓取正文", key="btn_url") and u.strip():
        try:
            with st.spinner("抓取中…"):
                r = extract_from_url(u.strip())
            st.session_state["url_result"] = r
        except ExtractionError as e:
            st.error(f"抓取失败：{e}。请改用「粘贴文本」。")
            st.session_state.pop("url_result", None)
    if st.session_state.get("url_result"):
        r = st.session_state["url_result"]
        st.success(f"抓取成功（{r['method']}，{len(r['text'])} 字）")
        st.text_area("抓到的正文（可编辑）", value=r["text"], height=180, key="url_text")
        source_text = st.session_state.get("url_text") or r["text"]
        source_label, extract_warnings, extract_method = u, r["warnings"], r["method"]

with tab_pdf:
    f = st.file_uploader("上传 PDF", type=["pdf"], key="pdf")
    if f is not None:
        tmp = Path("data/sample_inputs") / f"upload_{f.name}"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(f.getbuffer())
        try:
            r = extract_from_pdf(str(tmp))
            st.success(f"提取成功（{r['pages']} 页，{len(r['text'])} 字）")
            st.text_area("提取的正文（可编辑）", value=r["text"], height=180, key="pdf_text")
            source_text = st.session_state.get("pdf_text") or r["text"]
            source_label, extract_warnings, extract_method = f.name, r["warnings"], r["method"]
        except ExtractionError as e:
            st.error(f"提取失败：{e}")

st.divider()
c1, c2 = st.columns([3, 1])
with c1:
    template = st.radio("输出模板", list(TEMPLATES), horizontal=True,
                        format_func=lambda k: TEMPLATES[k]["name"])
with c2:
    go = st.button("一键结构化", type="primary", use_container_width=True)

st.caption(f"当前输入：{source_label or '（还没有内容）'}｜{len(source_text)} 字")

if go:
    if not source_text.strip():
        st.warning("请先粘贴文本、抓取链接或上传 PDF。")
    else:
        with st.spinner("生成中…"):
            res = structure(source_text, template=template, provider=provider)
        st.session_state["result"] = res
        st.session_state["result_md"] = to_markdown(res)

res = st.session_state.get("result")
if res is not None:
    st.divider()
    if not res.ok:
        st.error(f"生成失败：{res.error}")
        if res.raw:
            with st.expander("查看模型原始输出"):
                st.code(res.raw)
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("耗时", f"{res.elapsed_s}s")
        m2.metric("JSON 解析", "通过")
        m3.metric("Schema 校验", "通过" if res.schema_ok else "未通过")
        m4.metric("依据可回溯", f"{len(res.evidence_issues)} 处问题")
        if res.truncated:
            st.error(f"输出被截断（finish_reason={res.finish_reason or '未知'}）——JSON 不完整。"
                     f"提高 max_tokens 或精简模板字段。")
        if res.warnings:
            st.warning("；".join(res.warnings))
        if not res.schema_ok:
            st.warning("Schema 问题：" + "；".join(res.schema_errors[:5]))
        if res.evidence_issues:
            with st.expander(f"检测到 {len(res.evidence_issues)} 处依据问题（幻觉风险）"):
                for p in res.evidence_issues:
                    st.write("- " + p)

        md = st.session_state.get("result_md", "")
        st.markdown(md)
        with st.expander("复制 Markdown / 查看 JSON"):
            st.code(md, language="markdown")
            st.code(json.dumps(res.data, ensure_ascii=False, indent=2), language="json")
