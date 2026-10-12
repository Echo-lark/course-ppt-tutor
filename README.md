# course-ppt-tutor

给上传的 PPT、PPTX、课件 PDF 或本地 HTML 动态预览做**零基础、逐页、完整讲解**。默认先补前置知识，再解释课件里的概念、公式推导、图表、例题与易错点；讲解持续写入同一份 Markdown。封面和纯行政页会记账，但不占用知识页的讲解篇幅。

这是一个专门解决“前面讲得细、后面只读幻灯片”和“续写时丢页或重复”的个人 Codex skill。`SKILL.md` 是 AI 的工作规则；脚本只帮忙盘点页序、保存进度和检查文档结构，**不能代替 AI 阅读图像或判断讲解质量**。

## 仓库结构

- `SKILL.md`：逐页讲解、连续写入、零基础教学和完成条件。
- `scripts/pptx_inventory.py`：列出 PPTX 页序、可提取文字、备注及对象数量；仍需看渲染页。
- `scripts/course_notes.py`：管理单一 Markdown、页状态与结构检查。
- `references/html-courseware.md`：HTML 动态预览及本地页面数据的核对清单。
- `agents/openai.yaml`：Codex 中显示的名称和简介。
- `tests/`：防止续写、覆盖和漏页检查退化的测试。

## 使用

把此仓库放在 Codex 能发现的 skills 目录。当前本机目录就是 `C:\Users\Echo\.codex\skills\course-ppt-tutor`。上传课件后可以说：

> 用 course-ppt-tutor 从零基础逐页讲解这份课件。全部讲解写到同一个 Markdown；不要总结代替讲解，也不要在后半段缩写。

可以指定只讲某些页；之后说“继续”时，会读取同一个 Markdown 和进度记录。默认讲解语言跟随用户，中文提问时使用中文，并保留必要的原文术语和符号。

如果需手动运行辅助脚本，下面以 PowerShell 为例。课件文件和讲解文件的路径换成自己的实际路径：

```powershell
python scripts/pptx_inventory.py "D:\课件\chapter.pptx" --output "D:\学习\chapter-inventory.json"
python scripts/course_notes.py init --source "D:\课件\chapter.pptx" --pages 20 --markdown "D:\学习\chapter-讲解.md" --progress "D:\学习\chapter-progress.json" --title "第 1 章讲解"
python scripts/course_notes.py upsert --progress "D:\学习\chapter-progress.json" --page 1 --input "D:\学习\page-1-draft.md" --state taught
python scripts/course_notes.py status --progress "D:\学习\chapter-progress.json" --page 2 --state accounted --reason "封面，无知识内容"
python scripts/course_notes.py audit --progress "D:\学习\chapter-progress.json"
```

`upsert` 默认把新段落标为 `inspected`，核对课件后才显式传 `--state taught`。它默认拒绝覆盖已经写过的页。确实要修改时，先读旧段并合并用户的改动，再加 `--replace`。`audit` 检查页数、状态、重复段落、源文件变化，并提示显著偏短的讲解；它不能证明某页已经讲透。若某页确实内容很少、已核对完整，可用 `review --progress <进度文件> --page <页码> --note <核对理由>` 记录判断。HTML 预览可重复传 `--source` 指定 HTML 和数据文件，并通过 `--ids-json` 提供按显示顺序排列的页面 ID 数组。PDF 无需运行 PPTX 盘点脚本，但可使用相同的 Markdown/进度工具。

讲解文件、上传的课件和每次学习的进度记录属于个人学习数据，不应提交到这个 skill 仓库。
