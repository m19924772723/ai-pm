# -*- coding: utf-8 -*-
"""生成 git 推送记录 md：数据全部来自 git log / git ls-remote，不手写。"""
import subprocess
from datetime import datetime

OUT = r"D:/code/hermes/ai_pm/docs/git推送记录.md"


def run(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()


def main():
    # 全部提交（旧→新）
    log = run('git -C "D:/code/hermes/ai_pm" log --format="%h|%ad|%s" --date=format:"%Y-%m-%d %H:%M" --reverse')
    commits = [line.split("|", 2) for line in log.splitlines() if line]
    total = len(commits)

    # 每日分组（取日期前缀）
    by_day: dict[str, list] = {}
    for h, d, s in commits:
        day = d[:10]
        by_day.setdefault(day, []).append((h, d[11:], s))

    head = run('git -C "D:/code/hermes/ai_pm" rev-parse HEAD')

    # 三平台状态（各自带推送密钥，日常推送同款；subprocess 直接传参避免引号丢失）
    remotes = {}
    key_map = {"origin": "id_ed25519_gh", "gitee": "id_ed25519_mirror", "atomgit": "id_ed25519_mirror"}
    home = __import__("os").path.expanduser("~")
    for r in ("origin", "gitee", "atomgit"):
        key = key_map[r]
        env = {"GIT_SSH_COMMAND": f"ssh -i {home}/.ssh/{key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"}
        p = subprocess.run(
            ["git", "-C", r"D:/code/hermes/ai_pm", "ls-remote", r, "main"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**__import__("os").environ, **env})
        rmt = p.stdout.strip().split()[:1]
        rmt = rmt[0] if rmt else ""
        remotes[r] = "✅ 已同步" if rmt == head else ("⚠️ 需推送" if rmt else "⚠️ 无分支/未连通")

    lines = [
        "# Git 推送记录（PM 仓库）",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} · 数据来源：git log / git ls-remote（脚本产出，不手写）",
        "",
        "## 一、仓库与远程",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 本地路径 | `D:\\code\\hermes\\ai_pm` |",
        "| 分支 | main |",
        f"| 本地 HEAD | `{head}` |",
        f"| 提交总数 | **{total}** |",
        "",
        "| 远程 | 地址 | 状态 |",
        "|---|---|---|",
        "| GitHub | `github.com/m19924772723/ai-pm` | " + remotes["origin"] + " |",
        "| Gitee | `gitee.com/o19924772723/ai-pm` | " + remotes["gitee"] + " |",
        "| AtomGit | `atomgit.com/gc_I7FD3NNP/ai-pm` | " + remotes["atomgit"] + " |",
        "",
        "> 推送方式：日常手动 `git push`；每晚 22:00 daily.sh 自动 commit + 推三平台",
        "> 密钥：origin 用 id_ed25519_gh，gitee/atomgit 用 id_ed25519_mirror；先 unset 代理直连",
        "",
        "## 二、提交明细（按日期）",
        "",
        "| 日期 | 提交数 | 提交 | 内容 |",
        "|---|---|---|---|",
    ]
    for day in sorted(by_day):
        items = by_day[day]
        first = items[0]
        rest = items[1:]
        line = f"| {day} | {len(items)} | `{first[0]}` | {first[2]}"
        if rest:
            line += " <br> " + " <br> ".join(f"`{h}` {s}" for h, _, s in rest)
        lines.append(line + " |")

    lines += [
        "",
        "## 三、统计",
        "",
        f"- 首提交：`{commits[0][0]}`（{commits[0][1]}）{commits[0][2]}",
        f"- 最新提交：`{commits[-1][0]}`（{commits[-1][1]}）{commits[-1][2]}",
        f"- 共 {total} 个提交，覆盖 {len(by_day)} 天",
        "",
        "## 四、说明",
        "",
        "- 有几个日期无任务提交（09-25/09-30/10-03/10-04/10-07）：09-30 跳过节、部分任务提交合并进相邻日期",
        "- 本文件由 `scripts/` 下的生成脚本产出；再次生成会覆盖，内容以 git 为准",
        "",
    ]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已写 {OUT}（{total} 提交 / {len(by_day)} 天）")


if __name__ == "__main__":
    main()