# Inputs Operations

## 操作记录

1. 核对计划表日期与任务：确认 2026-09-28 为 Day 6、任务为"三种输入 + 失败降级"。
2. 写 `scripts_urltest.py`：对 4 个 URL 跑抓取，记录成功/方法/长度/警告。
3. 跑第一轮 URL 测试：woshipm、promptingguide 成功；36kr 首页与 zhihu 失败（含故意失败样本）。
4. 第二轮补充：另 1 篇真实文章页成功（woshipm/4234595），jiqizhixin 虚构链接失败（404 降级）。
5. 写 `scripts_pdftest.py`：生成中文文本 PDF + 纯图扫描件 PDF，验证正常/扫描件/不存在三条路径。
6. 修复测试脚本生成的 PDF 无文本层问题：`TextWriter` 改为 `page.insert_text(fontname="china-s")`。
7. 启动 Streamlit（headless 端口 8511），curl 验证 health=ok、页面 200，结束后 kill 进程。
8. 写 `tests/test_app.py` 界面冒烟测试，迭代修复 3 处断言写法后 4 条全过。
9. 全量测试 `pytest tests -q` → 33 passed。
10. 更新计划表 Day 6 行标记完成。

## 验证结果

- URL 文章页真实成功率：3/3
- PDF 三条路径：全部按预期（成功/明确报错/明确报错）
- Streamlit：health=ok、HTTP 200、AppTest 4/4
- 全量单元测试：33 passed

## 失败与修复

- 生成的测试 PDF 无文本层（属测试脚本 bug，不是提取器 bug）→ 改用 `insert_text`
- AppTest 断言三处写错（fixture 名、title 文本位置、radio options 位置）→ 逐条修正

## 关联文件

- `../../log/2026-09-28.md`
- `../../projects/L1-longtext-struct/scripts_urltest.py`
- `../../projects/L1-longtext-struct/scripts_pdftest.py`
- `../../projects/L1-longtext-struct/tests/test_app.py`
- `../../plans/AI产品经理学习实践计划表.xlsx`（Day 6 已标记完成）