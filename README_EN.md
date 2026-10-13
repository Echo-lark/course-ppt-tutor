# course-ppt-tutor

[![Tests](https://github.com/Echo-lark/course-ppt-tutor/actions/workflows/tests.yml/badge.svg)](https://github.com/Echo-lark/course-ppt-tutor/actions/workflows/tests.yml)

English | [中文](README.md)

A Codex skill that turns lecture slides into a **complete, beginner-friendly, page-by-page lesson**. It explains prerequisites, diagrams, notation, derivations, worked examples, and common misconceptions. All teaching for a deck goes into **one continuously updated Markdown file**, with a page ledger so a long course can be resumed without silently skipping or shortening its later pages.

This is for self-study or thorough revision of PPT/PPTX, slide PDFs, and local HTML courseware previews with their page data. It is not a slide generator or a summary prompt. See the [self-authored two-page demonstration](examples/synthetic-lesson.md) for the intended teaching style.

## Install

Codex needs file access to the courseware and permission to write the Markdown output. The optional helper scripts use only Python 3.10+ standard library. Clone the repository directly into your personal skills directory:

```bash
# macOS / Linux
git clone https://github.com/Echo-lark/course-ppt-tutor.git "$HOME/.codex/skills/course-ppt-tutor"
```

```powershell
# Windows PowerShell
git clone https://github.com/Echo-lark/course-ppt-tutor.git "$HOME\.codex\skills\course-ppt-tutor"
```

For an existing installation, run `git pull` inside that directory. Start a new Codex session if the skill is not discovered immediately.

## Ask for a lesson

Upload or point Codex to a deck, then ask:

> Use course-ppt-tutor to teach this entire deck from zero background, page by page. Explain every formula step and figure. Keep one Markdown document, and do not compress the later pages into a summary.

You can request a page range or say “continue” later. The skill reads the same Markdown and progress record, rechecks the next source pages, and resumes from the exact page. Administrative pages are accounted for briefly; knowledge pages receive full teaching. Plain-text/Unicode equations are the default for readers without LaTeX rendering, and you can request another notation.

## What is inside

| File | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Teaching workflow and completion criteria |
| [`references/teaching-depth.md`](references/teaching-depth.md) | Beginner-level depth, derivations, diagrams, and readable math |
| [`references/html-courseware.md`](references/html-courseware.md) | Local HTML preview and page-data inspection |
| [`scripts/pptx_inventory.py`](scripts/pptx_inventory.py) | PPTX order, text, notes, and object-count inventory |
| [`scripts/course_notes.py`](scripts/course_notes.py) | Durable single-document updates and structural coverage audit |
| [`tests/`](tests) | Synthetic regression tests; no real courseware is bundled |

The scripts are aids. Extracted text cannot replace viewing a slide, and an audit cannot prove that an explanation is factually correct or complete. The agent must compare each taught page with the source. Scanned PDFs require available OCR or vision capability. HTML previews require both local page data and visual inspection where possible.

## Optional helper commands

Run from **your course-material directory**, keeping the source and generated notes outside the skill repository. Bash example:

```bash
SKILL_DIR="$HOME/.codex/skills/course-ppt-tutor"
python "$SKILL_DIR/scripts/pptx_inventory.py" ./lecture.pptx --output ./lecture-inventory.json
python "$SKILL_DIR/scripts/course_notes.py" init --source ./lecture.pptx --pages 20 --markdown ./lecture-notes.md --progress ./lecture-progress.json
python "$SKILL_DIR/scripts/course_notes.py" upsert --progress ./lecture-progress.json --page 1 --input ./page-1-draft.md --state taught
python "$SKILL_DIR/scripts/course_notes.py" status --progress ./lecture-progress.json --page 2 --state accounted --reason "cover page"
python "$SKILL_DIR/scripts/course_notes.py" audit --progress ./lecture-progress.json
```

`upsert` defaults to `inspected`; use `--state taught` only after reviewing the page against the source. Replacing a section requires `--replace` after merging any learner edits. For HTML previews, repeat `--source` for the entry HTML and relevant data files, and pass an ordered JSON array of page IDs with `--ids-json`. Slide PDFs use the same notes tool without the PPTX inventory step. If Python is unavailable, the skill retains the same one-document and page-ledger requirements manually.

## Contribute and license

Run `python -m unittest discover -s tests -v` before submitting changes. See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under [MIT](LICENSE).

Do not commit instructor slides, private notes, or generated learner documents to this public repository. The bundled example is synthetic.
