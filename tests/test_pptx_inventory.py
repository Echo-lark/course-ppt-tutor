"""Verify slide order and note extraction using a synthetic PPTX ZIP."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pptx_inventory.py"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


class PptxInventoryTest(unittest.TestCase):
    def test_presentation_order_not_filename_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "ppt/presentation.xml",
                    f'<p:presentation xmlns:p="{P}" xmlns:r="{R}">'
                    '<p:sldIdLst><p:sldId id="256" r:id="rIdA"/>'
                    '<p:sldId id="257" r:id="rIdB"/></p:sldIdLst></p:presentation>',
                )
                archive.writestr(
                    "ppt/_rels/presentation.xml.rels",
                    f'<Relationships xmlns="{PKG}">'
                    f'<Relationship Id="rIdA" Type="{R}/slide" Target="slides/slide2.xml"/>'
                    f'<Relationship Id="rIdB" Type="{R}/slide" Target="slides/slide1.xml"/>'
                    '</Relationships>',
                )
                archive.writestr(
                    "ppt/slides/slide2.xml",
                    f'<p:sld xmlns:p="{P}" xmlns:a="{A}">'
                    '<p:cSld><p:spTree><a:t>First displayed</a:t><p:pic/>'
                    '</p:spTree></p:cSld></p:sld>',
                )
                archive.writestr(
                    "ppt/slides/slide1.xml",
                    f'<p:sld xmlns:p="{P}" xmlns:a="{A}">'
                    '<p:cSld><p:spTree><a:t>Second displayed</a:t><a:tbl/>'
                    '</p:spTree></p:cSld></p:sld>',
                )
                archive.writestr(
                    "ppt/slides/_rels/slide2.xml.rels",
                    f'<Relationships xmlns="{PKG}">'
                    f'<Relationship Id="rIdN" Type="{R}/notesSlide" Target="../notesSlides/notesSlide1.xml"/>'
                    '</Relationships>',
                )
                archive.writestr(
                    "ppt/notesSlides/notesSlide1.xml",
                    f'<p:notes xmlns:p="{P}" xmlns:a="{A}"><a:t>Speaker detail</a:t></p:notes>',
                )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["slide_count"], 2)
            self.assertEqual([slide["text_unverified"] for slide in data["slides"]],
                             ["First displayed", "Second displayed"])
            self.assertEqual(data["slides"][0]["speaker_notes_unverified"], "Speaker detail")
            self.assertEqual(data["slides"][0]["picture_count"], 1)
            self.assertEqual(data["slides"][1]["table_count"], 1)
            self.assertEqual(len(data["sha256"]), 64)

    def test_invalid_input_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not-a-deck.pptx"
            path.write_text("not a zip", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Inventory failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
