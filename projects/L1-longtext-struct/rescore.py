# -*- coding: utf-8 -*-
"""用已保存的评测结果重算指标（不重新调用 API）。

用途：
1. 换了匹配器/指标定义后，不必再花钱重跑模型；
2. 对比不同匹配器给出的覆盖率，判断差异是"模型漏了"还是"匹配器太严"。

用法：.venv/Scripts/python.exe rescore.py logs/eval_day5_fixed_*.json
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from run_eval import score_gold  # noqa: E402
from tests import eval_set_meta  # noqa: E402


def main() -> int:
    pattern = sys.argv[1] if len(sys.argv) > 1 else "logs/eval_day5_fixed_*.json"
    files = sorted(glob.glob(str(ROOT / pattern)))
    if not files:
        print("找不到评测结果文件:", pattern)
        return 1
    path = files[-1]
    d = json.loads(Path(path).read_text(encoding="utf-8"))

    gold_map = {s["id"]: s["gold_points"] for s in eval_set_meta.load()["samples"]}

    rows_out, tot_gold, tot_hit_old, tot_hit_new = [], 0, 0, 0
    for r in d["rows"]:
        gold = gold_map.get(r["id"], [])
        if not r.get("ok"):
            rows_out.append({"id": r["id"], "old_hit": 0, "new_hit": 0,
                             "point_total": len(gold), "note": "该样本调用失败，未计入"})
            tot_gold += len(gold)
            continue
        sc = score_gold(gold, json.dumps(r.get("data") or {}, ensure_ascii=False))
        old_hit = r.get("gold_hit", 0)
        rows_out.append({
            "id": r["id"], "template": r["template"],
            "old_hit": old_hit, "new_hit": len(sc["hit_points"]),
            "point_total": sc["point_total"],
            "new_missed": sc["miss_points"],
            "detail": sc["detail"],
        })
        tot_gold += sc["point_total"]
        tot_hit_old += old_hit
        tot_hit_new += len(sc["hit_points"])

    out = {
        "source_file": Path(path).name,
        "matcher_v1_逐字": round(tot_hit_old / tot_gold, 4) if tot_gold else 0,
        "matcher_v2_二元组重叠": round(tot_hit_new / tot_gold, 4) if tot_gold else 0,
        "counts": {"gold_total": tot_gold, "v1_hit": tot_hit_old, "v2_hit": tot_hit_new},
        "caveat": "两个匹配器都是字面级近似，不是语义判定；真实覆盖率以第 4 周人工核对为准。",
        "rows": rows_out,
    }

    dest = ROOT / "logs" / f"rescore_{Path(path).stem}.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"源文件: {Path(path).name}")
    print(f"要点总数: {tot_gold}")
    print(f"匹配器 v1（逐字整串）覆盖率: {out['matcher_v1_逐字']}  (命中 {tot_hit_old})")
    print(f"匹配器 v2（二元组重叠≥0.6 + 数字必中）覆盖率: {out['matcher_v2_二元组重叠']}  (命中 {tot_hit_new})")
    for row in rows_out:
        if "new_missed" in row:
            print(f"  {row['id']}: v1={row['old_hit']} → v2={row['new_hit']}/{row['point_total']}"
                  f"  剩余未命中={row['new_missed']}")
    print(f"\n明细: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
