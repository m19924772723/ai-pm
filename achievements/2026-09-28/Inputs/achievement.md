# Inputs

## 成果日期
2026-09-28

## 今日成果

1. **URL 抓取真实验证**：真实文章页 3/3 成功（woshipm×2、Prompt Engineering Guide），trafilatura 提取正文 1838–3337 字。
2. **URL 失败降级验证**：36kr 首页（无单一正文）、404 链接、zhihu（403 反爬）全部按预期走"正文提取过短，建议手动粘贴"降级。
3. **PDF 提取验证**：中文文本 PDF 提取成功；纯图扫描件按预期报错（不做 OCR 是明确边界）；文件不存在按预期报错。
4. **Streamlit 界面冒烟测试**：本地启动 health=ok、HTTP 200；用官方 `AppTest` 写 4 条脚本级界面测试全部通过。
5. 项目单元测试从 29 个扩到 **33 个，全部通过**。
6. 新增两个可复现验证脚本：`scripts_urltest.py`、`scripts_pdftest.py`，输出真实数据点到 `logs/`。

## 关键数据

| 场景 | 结果 |
|---|---|
| 文章页抓取 | 3/3 成功 |
| 首页 / 404 / 403 | 全部优雅降级，提示手动粘贴 |
| PDF 中文文本层 | 提取成功（112 字） |
| PDF 扫描件 | 明确报错（不做 OCR 边界） |
| 界面 | 启动 200 + 4 条 AppTest 冒烟测试通过 |

## 可复用成果

- 抓取验证脚本：`../../projects/L1-longtext-struct/scripts_urltest.py`
- PDF 验证脚本：`../../projects/L1-longtext-struct/scripts_pdftest.py`
- 界面测试：`../../projects/L1-longtext-struct/tests/test_app.py`
- 验证证据：`../../projects/L1-longtext-struct/logs/urltest_*.json`、`logs/pdftest_*.json`

## 原始记录

- `../../log/2026-09-28.md`