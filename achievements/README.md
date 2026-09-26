# 成果归档规则

## 目录规则

成果统一放在 `D:\code\hermes\ai_pm\achievements\`。

每一天建立一个英文成果词文件夹，文件夹内固定两个文件：

```text
achievements/
└── EnglishResult/
    ├── achievement.md   # 当天产出的成果、结论、可复用文件
    └── operations.md     # 当天实际操作、验证、提交和关联文件
```

## 命名规则

- 文件夹必须使用简短、明确的英文成果词：`Foundation`、`Quantification`、`Selection`、`Prompting`。
- 不使用日期作为成果文件夹名；日期写在 `achievement.md` 内。
- 成果词必须能回答“这一天完成了什么”，不能写 `Day1`、`Work` 这类无信息名称。

## 两类文件的边界

### achievement.md
记录最终留下的成果：

- 做出了什么文件/文档/代码；
- 得出了什么可复用结论；
- 解决了什么问题；
- 成果的路径和原始日志路径。

### operations.md
记录实际过程：

- 读了哪些文件或资料；
- 修改/新建了哪些文件；
- 用什么命令或工具验证；
- Git 提交和远程同步结果；
- 失败、阻塞和替代方案。

## 与 log 的关系

- `log/YYYY-MM-DD.md`：完整的每日过程日志，保留原始学习记录。
- `achievements/EnglishResult/`：从每日日志提炼出的成果和操作归档，方便按成果查找。
- 两者都保留，不互相覆盖；归档文件必须链接回对应原始日志。

## 每日收尾检查

- [ ] 成果文件夹名称是英文成果词
- [ ] `achievement.md` 已写最终产出
- [ ] `operations.md` 已写实际操作和验证
- [ ] 已链接原始 `log/` 文件
- [ ] Git 已提交并同步三平台
- [ ] README 的成果归档索引已更新
