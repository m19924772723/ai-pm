# -*- coding: utf-8 -*-
"""评测脚本：跑评测集，算三个指标。

用法：
    .venv/Scripts/python.exe run_eval.py                # 跑全部样本
    .venv/Scripts/python.exe run_eval.py --limit 1      # 只跑第一条（省 API 费用）
    .venv/Scripts/python.exe run_eval.py --tag day5     # 结果写到 logs/eval_<tag>.json

指标：
    要点覆盖率 = 命中的 gold_points / 全部 gold_points
    幻觉率     = 有问题的 evidence 条数 / 全部 evidence 条数
    格式合规率 = JSON 一次解析成功且 Schema 通过的样本 / 全部样本

注意：这是把"真实调用日志变成评测样本"的第一版；样本量小，数字只作趋势参考。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import structure  # noqa: E402
from tests import eval_set_meta  # noqa: E402
from utils.llm import provider_info, resolve_provider  # noqa: E402


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).lower()


def count_evidence(obj) -> int:
    n = 0

    def walk(x):
        nonlocal n
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "evidence" and isinstance(v, str):
                    n += 1
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    return n


def fragments(gold: str) -> dict:
    """把人工标注的要点拆成可核验成分。

    - hard: 数字/百分数等硬指标（必须精确出现）
    - shingles: 中文二元组 + 英文单词（允许措辞差异，用重叠率判定）

    为什么不用逐字匹配：中文加一个"的"就能让整串判断失败
    （模型写"产品经理的核心能力"，金标写"产品经理核心能力"），
    会产生大量假阴性。见 logs/ 里的对照记录。
    """
    hard = re.findall(r"[0-9]+(?:\.[0-9]+)?%?", gold)
    zh = re.sub(r"[^\u4e00-\u9fa5]", "", gold)
    shingles = {zh[i:i + 2] for i in range(len(zh) - 1)}
    en = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", gold)}
    return {"hard": hard, "shingles": shingles | en}


def score_gold(gold: list[str], result_text: str, threshold: float = 0.6) -> dict:
    """要点命中判定：二元组重叠率 ≥ threshold 且所有数字都出现。

    ⚠️ 仍是字面级近似，不理解同义改写（"拿下"vs"获取"）。只作趋势参考，
    第 4 周人工标注时以人工核对为准。
    """
    text = _norm(result_text)
    zh_res = re.sub(r"[^\u4e00-\u9fa5]", "", text)
    res_shingles = {zh_res[i:i + 2] for i in range(len(zh_res) - 1)}
    # 英文词从**原始**结果文本提取：_norm 会去掉空格把短语黏成一个词（"API spec"→"apispec"），
    # 在归一化文本上按 [A-Za-z]{3,} 提取会漏掉单词边界。之前只收中文二元组是第一个 bug，这里是第二个。
    res_shingles |= {w.lower() for w in re.findall(r"[A-Za-z]{3,}", result_text)}
    hit_points, miss_points, det = [], [], {}

    for g in gold:
        if _norm(g) in text:  # 归一化后逐字命中，直接过
            det[g] = {"ratio": 1.0, "reason": "逐字命中"}
            hit_points.append(g)
            continue
        f = fragments(g)
        hard_miss = [h for h in f["hard"] if h.lower() not in text]
        total = len(f["shingles"])
        if total == 0:
            det[g] = {"ratio": 0.0, "reason": "无可比成分"}
            miss_points.append(g)
            continue
        owned = f["shingles"] & res_shingles
        ratio = len(owned) / total
        ok = (ratio >= threshold) and not hard_miss
        det[g] = {"ratio": round(ratio, 3), "hard_miss": hard_miss,
                  "shingle_miss": sorted(f["shingles"] - res_shingles)[:5],
                  "reason": "通过" if ok else ("数字缺失" if hard_miss else "重叠不足")}
        (hit_points if ok else miss_points).append(g)

    return {"hit_points": hit_points, "miss_points": miss_points,
            "point_total": len(hit_points) + len(miss_points), "detail": det}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 条")
    ap.add_argument("--tag", default="run", help="结果文件名标签")
    ap.add_argument("--provider", default=None)
    args = ap.parse_args()

    data = eval_set_meta.load()
    samples = data["samples"]
    if args.limit:
        samples = samples[: args.limit]

    rows, t_start = [], time.time()
    for s in samples:
        print(f"[{s['id']}] {s['template']} … ", end="", flush=True)
        r = structure(s["input"], template=s["template"], provider=args.provider)
        n_ev = count_evidence(r.data) if r.data else 0
        issues = r.evidence_issues if r.ok else []
        sc = score_gold(s["gold_points"], json.dumps(r.data or {}, ensure_ascii=False)) if r.ok \
            else {"hit_points": [], "miss_points": s["gold_points"], "point_total": len(s["gold_points"]), "detail": {}}
        row = {
            "id": s["id"], "template": s["template"], "ok": r.ok, "error": r.error,
            "schema_ok": r.schema_ok, "schema_errors": r.schema_errors[:3],
            "elapsed_s": r.elapsed_s, "evidence_total": n_ev, "evidence_issues": len(issues),
            "evidence_issue_detail": issues[:3],
            "finish_reason": r.finish_reason, "truncated": r.truncated,
            "usage": r.usage, "warnings": r.warnings,
            "gold_total": sc["point_total"], "gold_hit": len(sc["hit_points"]),
            "gold_missed": sc["miss_points"], "gold_detail": sc["detail"],
            "data": r.data, "raw": r.raw[:4000],
        }
        rows.append(row)
        print("OK" if r.ok else f"FAIL({(r.error or '')[:40]})")

    total = len(rows)
    fmt_ok = sum(1 for r in rows if r["ok"] and r["schema_ok"])
    ev_total = sum(r["evidence_total"] for r in rows)
    ev_bad = sum(r["evidence_issues"] for r in rows)
    # 覆盖率只统计非 behavior 样本（S19 的 gold 描述的是系统行为，不是内容要点）
    gold_total = sum(r["gold_total"] for r in rows if r["id"] != "S19")
    gold_hit = sum(r["gold_hit"] for r in rows if r["id"] != "S19")

    summary = {
        "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "provider": provider_info(args.provider),
        "sample_count": total,
        "metric_格式合规率": round(fmt_ok / total, 4) if total else 0,
        "metric_要点覆盖率": round(gold_hit / gold_total, 4) if gold_total else 0,
        "metric_幻觉率": round(ev_bad / ev_total, 4) if ev_total else 0,
        "counts": {"format_ok": fmt_ok, "evidence_total": ev_total, "evidence_issues": ev_bad,
                   "gold_total": gold_total, "gold_hit": gold_hit},
        "duration_s": round(time.time() - t_start, 1),
        "caveat": "样本量小（见 tests/eval_set.json 的 current_count），数字只反映当前链路是否可用，不构成上线结论。",
    }

    out_dir = ROOT / "logs"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = out_dir / f"eval_{args.tag}_{stamp}.json"
    out.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== 指标 ===")
    for k, v in summary.items():
        if k.startswith("metric_") or k in ("sample_count", "duration_s"):
            print(f"{k}: {v}")
    print(f"\n明细已写入: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
