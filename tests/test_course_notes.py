"""Exercise the durable one-document workflow with temporary courseware."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "course_notes.py"


class CourseNotesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "deck.html"
        self.source.write_text("<html>lesson</html>", encoding="utf-8")
        self.notes = self.root / "lesson.md"
        self.progress = self.root / "progress.json"

    def run_cli(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def initialize(self) -> None:
        ids = self.root / "ids.json"
        ids.write_text(json.dumps(["intro", "force", "end"]), encoding="utf-8")
        self.run_cli(
            "init", "--source", self.source, "--pages", "3",
            "--ids-json", ids, "--markdown", self.notes,
            "--progress", self.progress,
        )

    def test_page_order_and_explicit_replace_preserve_other_text(self) -> None:
        self.initialize()
        one = self.root / "one.md"
        three = self.root / "three.md"
        one.write_text("Explain prerequisite and formula carefully.", encoding="utf-8")
        three.write_text("Explain diagram and example carefully.", encoding="utf-8")
        self.run_cli("upsert", "--progress", self.progress, "--page", "3", "--input", three)
        self.notes.write_text(self.notes.read_text(encoding="utf-8") + "\nPersonal note.\n", encoding="utf-8")
        self.run_cli("upsert", "--progress", self.progress, "--page", "1", "--input", one)
        text = self.notes.read_text(encoding="utf-8")
        self.assertLess(text.index("page:1:start"), text.index("page:3:start"))
        self.assertIn("Personal note.", text)
        self.run_cli("upsert", "--progress", self.progress, "--page", "1", "--input", one, ok=False)
        one.write_text("Merged revised explanation.", encoding="utf-8")
        self.run_cli("upsert", "--progress", self.progress, "--page", "1", "--input", one, "--replace")
        text = self.notes.read_text(encoding="utf-8")
        self.assertEqual(text.count("page:1:start"), 1)
        self.assertIn("Merged revised explanation.", text)
        self.assertIn("Personal note.", text)

    def test_audit_detects_missing_taught_section_and_source_change(self) -> None:
        self.initialize()
        ledger = json.loads(self.progress.read_text(encoding="utf-8"))
        ledger["pages"][0]["status"] = "taught"
        self.progress.write_text(json.dumps(ledger), encoding="utf-8")
        result = self.run_cli("audit", "--progress", self.progress, ok=False)
        self.assertIn("taught but has no Markdown", result.stdout)
        ledger["pages"][0]["status"] = "unseen"
        self.progress.write_text(json.dumps(ledger), encoding="utf-8")
        self.source.write_text("<html>changed</html>", encoding="utf-8")
        result = self.run_cli("audit", "--progress", self.progress)
        self.assertIn("Source changed", result.stdout)

    def test_accounted_page_requires_reason_and_completion_counts(self) -> None:
        self.initialize()
        self.run_cli(
            "status", "--progress", self.progress, "--page", "1",
            "--state", "accounted", ok=False,
        )
        self.run_cli(
            "status", "--progress", self.progress, "--page", "1",
            "--state", "accounted", "--reason", "cover only",
        )
        result = self.run_cli("audit", "--progress", self.progress)
        report = json.loads(result.stdout)
        self.assertEqual(report["status_counts"]["accounted"], 1)
        self.assertEqual(report["next_page"], 2)
        self.assertFalse(report["complete"])

    def test_short_page_needs_explicit_source_review(self) -> None:
        self.initialize()
        draft = self.root / "short.md"
        draft.write_text("A short but complete explanation.", encoding="utf-8")
        self.run_cli("upsert", "--progress", self.progress, "--page", "2", "--input", draft, "--state", "taught")
        report = json.loads(self.run_cli("audit", "--progress", self.progress).stdout)
        self.assertTrue(any("Page 2" in warning for warning in report["warnings"]))
        self.run_cli(
            "review", "--progress", self.progress, "--page", "2",
            "--note", "Checked against the one-sentence source page; all terms explained.",
        )
        report = json.loads(self.run_cli("audit", "--progress", self.progress).stdout)
        self.assertFalse(report["warnings"])

    def test_batch_saves_in_page_order_and_rejects_invalid_batch_without_changes(self) -> None:
        self.initialize()
        batch = self.root / "batch.json"
        batch.write_text(json.dumps([
            {"page": 3, "content": "Last page explanation.", "state": "taught"},
            {"page": 1, "content": "First page explanation.", "state": "taught"},
        ]), encoding="utf-8")
        self.run_cli("upsert-batch", "--progress", self.progress, "--input", batch)
        text = self.notes.read_text(encoding="utf-8")
        self.assertLess(text.index("page:1:start"), text.index("page:3:start"))
        ledger = json.loads(self.progress.read_text(encoding="utf-8"))
        self.assertEqual(ledger["next_page"], 2)

        before_notes = self.notes.read_bytes()
        before_progress = self.progress.read_bytes()
        batch.write_text(json.dumps([
            {"page": 1, "content": "Would replace", "state": "taught", "replace": True},
            {"page": 2, "content": "", "state": "taught"},
        ]), encoding="utf-8")
        self.run_cli("upsert-batch", "--progress", self.progress, "--input", batch, ok=False)
        self.assertEqual(self.notes.read_bytes(), before_notes)
        self.assertEqual(self.progress.read_bytes(), before_progress)


if __name__ == "__main__":
    unittest.main()
