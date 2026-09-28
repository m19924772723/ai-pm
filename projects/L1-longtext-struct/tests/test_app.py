# -*- coding: utf-8 -*-
"""Streamlit 界面冒烟测试（无浏览器，脚本级）。

用官方 AppTest 跑 app.py，能抓到脚本执行/渲染期的异常。
用法：.venv/Scripts/python.exe -m pytest tests/test_app.py -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402


@pytest.fixture()
def at_():
    os.environ.setdefault("HERMES_CUSTOM_STEPFUN_API_KEY", "test-not-real")
    at_ = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at_.run()
    return at_


def test_app_boots_without_exception(at_):
    assert not at_.exception, at_.exception


def test_app_renders_title_and_tabs(at_):
    assert any("长文结构化助手" in (t.value or "") for t in at_.title)
    # 三个输入 tab
    tabs = {t.label for t in at_.tabs}
    assert {"粘贴文本", "链接抓取", "PDF 上传"} <= tabs, tabs


def test_app_has_template_radio(at_):
    # format_func 应用在 options 上，label 只是标题文字
    assert at_.radio, "应至少有 1 个模板选择"
    opts = set(at_.radio[0].options)
    assert {"摘要模式", "待办模式", "归档模式"} <= opts, opts


def test_app_sidebar_shows_provider_selector(at_):
    # 侧边栏 selectbox：available_providers() 至少返回 stepfun
    assert at_.selectbox, "应至少有 1 个模型端点下拉框"
