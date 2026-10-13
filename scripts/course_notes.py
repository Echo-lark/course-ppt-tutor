"""Keep one courseware explanation Markdown and a page ledger in sync.

This checks file structure and page accounting. It cannot judge teaching quality.
Only Python's standard library is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import tempfile
from pathlib import Path

PAGES_START = "<!-- course-ppt-tutor:pages -->"
PAGES_END = "<!-- course-ppt-tutor:endpages -->"
BLOCK = re.compile(
    r"<!-- course-ppt-tutor:page:(\d+):start -->\n"
    r"(.*?)"
    r"<!-- course-ppt-tutor:page:\1:end -->\n?",
    re.DOTALL,
)
ANY_PAGE_MARKER = re.compile(r"<!-- course-ppt-tutor:page:\d+:(?:start|end) -->")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_json(path: Path, value: dict) -> None:
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def save_ledger(path: Path, ledger: dict) -> None:
    ledger["total_pages"] = len(ledger["pages"])
    ledger["next_page"] = next(
        (page["number"] for page in ledger["pages"]
         if page["status"] not in {"taught", "accounted"}),
        None,
    )
    save_json(path, ledger)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(progress: Path) -> tuple[dict, Path, str]:
    ledger = json.loads(progress.read_text(encoding="utf-8"))
    notes = Path(ledger["markdown"])
    body = notes.read_text(encoding="utf-8")
    if body.count(PAGES_START) != 1 or body.count(PAGES_END) != 1:
        raise ValueError("Markdown needs exactly one page area with start/end markers")
    if body.index(PAGES_START) >= body.index(PAGES_END):
        raise ValueError("Markdown page area markers are out of order")
    return ledger, notes, body


def blocks(body: str) -> dict[int, tuple[re.Match[str], str]]:
    area = body.split(PAGES_START, 1)[1].split(PAGES_END, 1)[0]
    matches = list(BLOCK.finditer(area))
    if len(ANY_PAGE_MARKER.findall(area)) != len(matches) * 2:
        raise ValueError("Markdown has an unmatched or malformed page marker")
    result = {}
    for match in matches:
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"Duplicate Markdown section for page {number}")
        result[number] = (match, match.group(2))
    return result


def page_record(ledger: dict, number: int) -> dict:
    if number < 1 or number > len(ledger["pages"]):
        raise ValueError(f"Page {number} is outside 1..{len(ledger['pages'])}")
    return ledger["pages"][number - 1]


def init(args: argparse.Namespace) -> None:
    if args.pages < 1:
        raise ValueError("--pages must be positive")
    if args.markdown.resolve() == args.progress.resolve():
        raise ValueError("Markdown and progress paths must differ")
    if args.markdown.exists() or args.progress.exists():
        raise ValueError("A target already exists; resume it instead of overwriting it")
    ids = list(range(1, args.pages + 1))
    if args.ids_json:
        ids = json.loads(args.ids_json.read_text(encoding="utf-8"))
        if (not isinstance(ids, list) or len(ids) != args.pages
                or any(not isinstance(value, (str, int)) or not str(value).strip() for value in ids)
                or len(set(map(str, ids))) != len(ids)):
            raise ValueError("--ids-json must be an array of unique text/number IDs, one per page")
    sources = []
    for path in args.source:
        if not path.is_file():
            raise ValueError(f"Source file is missing: {path}")
        sources.append({"path": str(path.resolve()), "sha256": sha256(path)})
    ledger = {
        "version": 1,
        "markdown": str(args.markdown.resolve()),
        "sources": sources,
        "learner_level": "beginner",
        "accepted_preferences": [
            "Explain every substantive page from zero prior course knowledge.",
            "Show intermediate derivation steps and why each step is valid.",
            "Use plain text/Unicode math readable without LaTeX rendering unless changed by the learner.",
            "Keep one continuously updated Markdown for this courseware set.",
        ],
        "unresolved_items": [],
        "pages": [
            {"number": i, "source_id": str(ids[i - 1]), "status": "unseen", "subject": "", "reason": "", "review_note": ""}
            for i in range(1, args.pages + 1)
        ],
    }
    title = args.title or args.markdown.stem
    content = f"# {title}\n\n{PAGES_START}\n{PAGES_END}\n"
    atomic_write(args.markdown, content)
    save_ledger(args.progress, ledger)
    print(f"Initialized {args.pages} pages: {args.markdown}")


def upsert(args: argparse.Namespace) -> None:
    ledger, notes, body = load(args.progress)
    page = page_record(ledger, args.page)
    if page["status"] == "accounted":
        raise ValueError("This page is accounted as non-content; change its status first")
    content = args.input.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("The page explanation is empty")
    if "<!-- course-ppt-tutor:" in content:
        raise ValueError("The page explanation contains a reserved course-ppt-tutor marker")
    existing = blocks(body)
    if args.page in existing and not args.replace:
        raise ValueError("Page already has a section; merge edits and pass --replace explicitly")
    heading = f"## Page {args.page} · source {page['source_id']}\n\n"
    section = (
        f"<!-- course-ppt-tutor:page:{args.page}:start -->\n"
        f"{heading}{content}\n"
        f"<!-- course-ppt-tutor:page:{args.page}:end -->\n"
    )
    if args.page in existing:
        pattern = re.compile(
            rf"<!-- course-ppt-tutor:page:{args.page}:start -->\n.*?"
            rf"<!-- course-ppt-tutor:page:{args.page}:end -->\n?",
            re.DOTALL,
        )
        body, count = pattern.subn(lambda _: section, body, count=1)
        if count != 1:
            raise ValueError("Could not safely replace page section")
    else:
        later = sorted(n for n in existing if n > args.page)
        anchor = f"<!-- course-ppt-tutor:page:{later[0]}:start -->" if later else PAGES_END
        body = body.replace(anchor, section + anchor, 1)
    atomic_write(notes, body)
    page["status"] = args.state
    page["subject"] = args.subject or page["subject"]
    page["reason"] = ""
    page["review_note"] = ""
    save_ledger(args.progress, ledger)
    print(f"Saved page {args.page} as {args.state}: {notes}")


def set_status(args: argparse.Namespace) -> None:
    ledger, _, body = load(args.progress)
    page = page_record(ledger, args.page)
    present = args.page in blocks(body)
    if args.state == "accounted" and present:
        raise ValueError("Page has a teaching section; revise it instead of accounting it away")
    if args.state in {"accounted", "blocked"} and not args.reason:
        raise ValueError("A reason is required for accounted or blocked pages")
    page["status"] = args.state
    page["reason"] = args.reason or ""
    page["subject"] = args.subject or page["subject"]
    save_ledger(args.progress, ledger)
    print(f"Page {args.page}: {args.state}")


def review(args: argparse.Namespace) -> None:
    ledger, _, body = load(args.progress)
    page = page_record(ledger, args.page)
    if page["status"] != "taught" or args.page not in blocks(body):
        raise ValueError("Only a taught page with a Markdown section can receive a review note")
    page["review_note"] = args.note.strip()
    if not page["review_note"]:
        raise ValueError("The review note is empty")
    save_ledger(args.progress, ledger)
    print(f"Recorded review of page {args.page}")


def audit(args: argparse.Namespace) -> int:
    ledger, _, body = load(args.progress)
    existing = blocks(body)
    errors = []
    warnings = []
    valid = {p["number"] for p in ledger["pages"]}
    for number in existing:
        if number not in valid:
            errors.append(f"Markdown page {number} is not in the ledger")
    lengths = []
    for page in ledger["pages"]:
        number, state = page["number"], page["status"]
        if state == "taught" and number not in existing:
            errors.append(f"Page {number} is taught but has no Markdown section")
        if state == "accounted" and number in existing:
            errors.append(f"Page {number} is accounted but has a Markdown section")
        if state in {"blocked", "accounted"} and not page["reason"]:
            errors.append(f"Page {number} needs a reason for {state}")
        if state == "taught" and number in existing:
            length = len(existing[number][1].strip())
            if length < args.short_threshold and not page.get("review_note"):
                warnings.append(f"Page {number} has only {length} characters; review its depth")
            if len(lengths) >= 3 and length < statistics.median(lengths) / 3 and not page.get("review_note"):
                warnings.append(f"Page {number} is much shorter than earlier taught pages; review its depth")
            lengths.append(length)
    for source in ledger["sources"]:
        path = Path(source["path"])
        if not path.is_file():
            warnings.append(f"Source is missing: {path}")
        elif sha256(path) != source["sha256"]:
            warnings.append(f"Source changed since initialization: {path}")
    counts = {state: sum(p["status"] == state for p in ledger["pages"])
              for state in ("unseen", "inspected", "taught", "blocked", "accounted")}
    remaining = [p["number"] for p in ledger["pages"] if p["status"] not in {"taught", "accounted"}]
    report = {"total": len(ledger["pages"]), "status_counts": counts,
              "next_page": remaining[0] if remaining else None,
              "complete": not remaining and not errors and not warnings,
              "errors": errors, "warnings": warnings,
              "note": "Structural checks and length warnings cannot prove semantic completeness."}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="Create one Markdown and progress ledger")
    p.add_argument("--markdown", required=True, type=Path)
    p.add_argument("--progress", required=True, type=Path)
    p.add_argument("--pages", required=True, type=int)
    p.add_argument("--source", action="append", required=True, type=Path)
    p.add_argument("--ids-json", type=Path, help="JSON array of source page IDs in display order")
    p.add_argument("--title")
    p.set_defaults(func=init)
    p = sub.add_parser("upsert", help="Insert or explicitly replace a page explanation")
    p.add_argument("--progress", required=True, type=Path)
    p.add_argument("--page", required=True, type=int)
    p.add_argument("--input", required=True, type=Path, help="UTF-8 Markdown for this page")
    p.add_argument("--state", choices=["inspected", "taught"], default="inspected")
    p.add_argument("--subject")
    p.add_argument("--replace", action="store_true")
    p.set_defaults(func=upsert)
    p = sub.add_parser("status", help="Record a non-teaching page or reading limit")
    p.add_argument("--progress", required=True, type=Path)
    p.add_argument("--page", required=True, type=int)
    p.add_argument("--state", required=True, choices=["unseen", "inspected", "blocked", "accounted"])
    p.add_argument("--reason")
    p.add_argument("--subject")
    p.set_defaults(func=set_status)
    p = sub.add_parser("review", help="Record manual review of a flagged short taught page")
    p.add_argument("--progress", required=True, type=Path)
    p.add_argument("--page", required=True, type=int)
    p.add_argument("--note", required=True, help="Why this short page is complete after source review")
    p.set_defaults(func=review)
    p = sub.add_parser("audit", help="Check page coverage and flag unusually short sections")
    p.add_argument("--progress", required=True, type=Path)
    p.add_argument("--short-threshold", type=int, default=300)
    p.set_defaults(func=audit)
    args = parser.parse_args()
    try:
        result = args.func(args)
        return result if isinstance(result, int) else 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
