# -*- coding: utf-8 -*-
"""评测匹配器测试。

背景：v1 用"逐字整串"匹配，中文里多一个"的"就判失败，覆盖率虚低（7/13）。
v2 改成"二元组重叠 ≥0.6 且数字必须命中"，同一批模型输出重算得 12/13。
这些用例把这个结论固化下来，避免以后又退回逐字匹配。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_eval import fragments, score_gold  # noqa: E402


def test_fragments_extracts_numbers_and_shingles():
    f = fragments("延迟从 1.2 秒降到 0.8 秒")
    assert "1.2" in f["hard"] and "0.8" in f["hard"]
    assert "延迟" in f["shingles"] and "秒降" in f["shingles"]


def test_v1_style_literal_match_would_fail_on_paraphrase():
    """回归：措辞差一个"的"时，逐字匹配失败，v2 必须通过。"""
    gold = "产品经理核心能力是判断做什么和不做什么"
    model_text = json.dumps({"key_points": [
        {"point": "产品经理的核心能力是判断做什么和不做什么"}]}, ensure_ascii=False)
    assert gold not in model_text  # v1 会判 MISS
    res = score_gold([gold], model_text)
    assert res["hit_points"] == [gold], res["detail"]


def test_numbers_must_match_exactly():
    gold = "延迟从 1.2 秒降到 0.8 秒"
    model_text = json.dumps({"summary": "延迟从 1.5 秒降到 0.8 秒"}, ensure_ascii=False)
    res = score_gold([gold], model_text)
    assert res["hit_points"] == []
    assert res["detail"][gold]["reason"] == "数字缺失"


def test_true_miss_is_still_missed():
    gold = "王五负责完成流失用户访谈"
    model_text = json.dumps({"summary": "本期重点是提升留存"}, ensure_ascii=False)
    res = score_gold([gold], model_text)
    assert res["hit_points"] == [] and res["miss_points"] == [gold]


def test_exact_hit_short_circuits():
    gold = "已完成 60% 的开发"
    res = score_gold([gold], "项目当前已完成 60% 的开发")
    assert res["hit_points"] == [gold]
    assert res["detail"][gold]["reason"] == "逐字命中"


def test_near_miss_still_passes_via_shingles():
    """未逐字出现，但重叠足够，应走二元组路径判通过。"""
    gold = "开发完成 60%"
    res = score_gold([gold], "项目当前已完成 60% 的开发")
    assert res["hit_points"] == [gold]
    assert res["detail"][gold]["reason"] == "通过"


def test_s04_paraphrase_is_below_threshold():
    """记录已知边界：这条改写幅度大，字面匹配器仍判 MISS（人工读为命中）。"""
    gold = "延迟下降归因于缓存尚未验证"
    model_text = json.dumps(
        {"summary": "延迟下降原因暂未通过对照实验验证"}, ensure_ascii=False)
    res = score_gold([gold], model_text)
    assert res["hit_points"] == [], "若这里通过，说明匹配器已升级为语义级，请更新文档数字"


def test_english_gold_matches_english_result():
    """回归：英文结果文本必须能命中英文 gold（修复前 res_shingles 只收中文）。"""
    gold = "Alice finalizes API spec by Friday"
    model_text = json.dumps({"todos": [{
        "action": "finalize the API spec", "owner": "Alice",
        "deadline": "by Friday", "priority": "unspecified"}]}, ensure_ascii=False)
    res = score_gold([gold], model_text)
    assert res["hit_points"] == [gold], res["detail"]


def test_english_numbers_still_required():
    gold = "answer faithfulness improved from 68% to 81%"
    model_text = json.dumps({"summary": "faithfulness went from 50% to 55%"}, ensure_ascii=False)
    res = score_gold([gold], model_text)
    assert res["hit_points"] == [], "数字没变还判中就是 bug"
    assert res["detail"][gold]["reason"] == "数字缺失"
