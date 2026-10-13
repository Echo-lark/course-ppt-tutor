# course-ppt-tutor

[English](README_EN.md) | 中文

给上传的 PPT、PPTX、课件 PDF 或本地 HTML 动态预览做**零基础、逐页、完整讲解**。默认先补前置知识，再解释课件里的概念、公式推导、图表、例题与易错点；讲解持续写入同一份 Markdown。封面和纯行政页会记账，但不占用知识页的讲解篇幅。

这个 Codex skill 针对“前面讲得细、后面只读幻灯片”和“续写时丢页或重复”这两个常见问题。`SKILL.md` 是 AI 的工作规则；脚本只帮忙盘点页序、保存进度和检查文档结构，**不能代替 AI 阅读图像或判断讲解质量**。

**特色**：每个知识页都解释“是什么、为什么、怎么推出来”，公式不跳关键步骤；长课件分批写入同一文档；继续学习时读取页码进度；默认使用无需 LaTeX 渲染的普通文字和 Unicode 公式。教学示例见[两页自创课件演示](examples/synthetic-lesson.md)。

## 仓库结构

- `SKILL.md`：逐页讲解、连续写入、零基础教学和完成条件。
- `scripts/pptx_inventory.py`：列出 PPTX 页序、可提取文字、备注及对象数量；仍需看渲染页。
- `scripts/course_notes.py`：管理单一 Markdown、页状态与结构检查。
- `references/teaching-depth.md`：零基础讲解深度、逐步推导、跨页衔接和适合平板阅读的公式写法。
- `references/html-courseware.md`：HTML 动态预览及本地页面数据的核对清单。
- `agents/openai.yaml`：Codex 中显示的名称和简介。
- `tests/`：防止续写、覆盖和漏页检查退化的测试。

## 安装

需要能读取课件及写入 Markdown 的 Codex 环境。脚本使用 Python 3.10+ 标准库；没有 Python 时，skill 仍可按 `SKILL.md` 手动维护同一份文档和进度。

在未安装过该 skill 的机器上，将仓库直接克隆到 Codex 的个人 skills 目录：

```powershell
# Windows PowerShell
git clone https://github.com/Echo-lark/course-ppt-tutor.git "$HOME\.codex\skills\course-ppt-tutor"
```

```bash
# macOS / Linux
git clone https://github.com/Echo-lark/course-ppt-tutor.git "$HOME/.codex/skills/course-ppt-tutor"
```

已安装时，在该目录运行 `git pull` 更新。若 Codex 没有立刻发现新 skill，重新开启一次会话。

## 使用

上传课件后可以说：

> 用 course-ppt-tutor 从零基础逐页讲解这份课件。全部讲解写到同一个 Markdown；不要总结代替讲解，也不要在后半段缩写。

可以指定只讲某些页；之后说“继续”时，会读取同一个 Markdown 和进度记录。默认讲解语言跟随用户，中文提问时使用中文，并保留必要的原文术语和符号。考虑到平板显示问题，默认使用普通文字和 Unicode 公式，逐行解释计算过程；你也可以随时指定别的公式格式。讲解深度以课件内容为准：稀疏页不凑字数，推导页必须把中间步骤与理由讲清楚。

讲解默认写入一份持续更新的 Markdown；进度保存在旁边的 JSON。实际文件位置由用户指定或由当前任务选择，不会自动提交到这个仓库。

如果需手动运行辅助脚本，下面以 PowerShell 为例。请把示例路径换成自己的实际路径：

```powershell
python scripts/pptx_inventory.py .\chapter.pptx --output .\chapter-inventory.json
python scripts/course_notes.py init --source .\chapter.pptx --pages 20 --markdown .\chapter-notes.md --progress .\chapter-progress.json --title "第 1 章讲解"
python scripts/course_notes.py upsert --progress .\chapter-progress.json --page 1 --input .\page-1-draft.md --state taught
python scripts/course_notes.py status --progress .\chapter-progress.json --page 2 --state accounted --reason "封面，无知识内容"
python scripts/course_notes.py audit --progress .\chapter-progress.json
```

`upsert` 默认把新段落标为 `inspected`，核对课件后才显式传 `--state taught`。它默认拒绝覆盖已经写过的页。确实要修改时，先读旧段并合并用户的改动，再加 `--replace`。`audit` 检查页数、状态、重复段落、源文件变化，并提示显著偏短的讲解；它不能证明某页已经讲透。若某页确实内容很少、已核对完整，可用 `review --progress <进度文件> --page <页码> --note <核对理由>` 记录判断。HTML 预览可重复传 `--source` 指定 HTML 和数据文件，并通过 `--ids-json` 提供按显示顺序排列的页面 ID 数组。PDF 无需运行 PPTX 盘点脚本，但可使用相同的 Markdown/进度工具。

## 范围与限制

- PPTX 文本盘点不能代替渲染检查；扫描版 PDF 需要可用的 OCR 或视觉读取能力；HTML 预览需同时检查本地页面数据与实际显示。
- `audit` 只能检查页码、文档结构和异常短的段落，不能证明知识点正确或讲解完整。每页仍须对照课件核查。
- 课件、生成的讲解及学习进度通常属于个人学习数据，不应提交到公开仓库。本仓库只包含工具和自创示例。

## 开发与许可

运行 `python -m unittest discover -s tests -v` 检查脚本。贡献方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。本项目采用 [MIT License](LICENSE)。
