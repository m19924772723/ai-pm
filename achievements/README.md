# 成果归档规则

## 目录规则

成果统一放在 `D:\code\hermes\ai_pm\achievements\`，采用“日期 → 英文成果词 → 两类记录”的三级结构：

```text
achievements/
└── YYYY-MM-DD/
    └── EnglishResult/
        ├── achievement.md   # 当天产出的成果、结论、可复用文件
        └── operations.md     # 当天实际操作、验证、提交和关联文件
```

## 命名规则

- 第一层必须是日期：`YYYY-MM-DD`，例如 `2026-09-26`。
- 第二层必须使用简短、明确的英文成果词，例如 `Foundation`、`Quantification`、`Selection`、`Prompting`。
- 不使用 `Day1`、`Work` 等无信息名称。
- 同一天有多个独立成果时，在同一个日期文件夹内建立多个英文成果词文件夹。

## 两类文件的边界

### achievement.md
记录最终留下的成果：做出了什么、得出了什么、解决了什么问题、成果文件在哪里。

### operations.md
记录实际过程：读取了什么、修改/新建了什么、如何验证、Git 提交和远程同步结果、失败与替代方案。

## 与 log 的关系

- `log/YYYY-MM-DD.md`：完整的每日过程日志。
- `achievements/YYYY-MM-DD/EnglishResult/`：按日期和成果词整理后的成果归档。
- 两者都保留；归档文件必须链接回对应原始日志。

## 每日收尾检查

- [ ] 日期文件夹使用 `YYYY-MM-DD`
- [ ] 成果文件夹使用英文成果词
- [ ] `achievement.md` 已写最终产出
- [ ] `operations.md` 已写实际操作和验证
- [ ] 已链接原始 `log/` 文件
- [ ] Git 已提交并同步三平台
- [ ] `achievements/README.md` 的日期索引已更新
