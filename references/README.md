# references/ —— 本地参考库（外部仓库用 junction 挂进来，不入 git）

这里的每个条目都是**外部仓库的 Windows 目录联接（junction）**，实体文件放在 `D:\code\<仓库名>`，
本目录只提供一个「从 ai-pm 里一步能点到」的入口。

## 为什么用 junction 而不是把仓库拷进来

| 方案 | 问题 |
|---|---|
| 直接拷进 `references/` | 一个仓库 300 MB+，`git add` 会把整个仓库塞进 ai-pm，推三平台直接失败 |
| git submodule | 需要在三个远程都配好、每次 push 都要处理 submodule 状态，日常太重 |
| **junction（当前做法）** | 实体在 D 盘正常目录里，git 只看得到一个空目录（已在 `.gitignore` 排除），资源管理和版本管理互不干扰 |

## 查看 / 维护

```bash
# 看当前挂了哪些参考库
ls /d/code/hermes/ai_pm/references

# 判断某条目是 junction 还是真目录
cmd //c dir /al "D:\code\hermes\ai_pm\references"

# 新增一个参考库（先把仓库克隆到 D:\code\<名字>，再挂链接）
cmd //c mklink /J "D:\code\hermes\ai_pm\references\<名字>" "D:\code\<名字>"
# 挂完必须在 .gitignore 里加一行 references/<名字>/，否则 git 会看到整个仓库
```

## 当前条目

| 条目 | 实体路径 | 是什么 |
|---|---|---|
| `hello-agents/` | `D:\code\hello-agents` | Datawhale《从零开始构建智能体》教程（16 章中文 + 每章可运行代码 + 14 篇补充），AI Agent 开发的母本。索引见 [`../docs/hello-agents-学习索引.md`](../docs/hello-agents-学习索引.md) |
