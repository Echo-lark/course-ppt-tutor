"""Inventory PPTX slide order, text, notes, and visual object counts.

This is an extraction aid, not a substitute for rendering and visual inspection.
Only Python's standard library is used; embedded code and macros are never run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def xml_file(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def relationships(zf: zipfile.ZipFile, base: str) -> dict[str, tuple[str, str]]:
    folder, filename = posixpath.split(base)
    rels_name = posixpath.join(folder, "_rels", filename + ".rels")
    if rels_name not in zf.namelist():
        return {}
    result = {}
    for rel in xml_file(zf, rels_name).findall(f"{{{PKG}}}Relationship"):
        target = rel.attrib.get("Target", "")
        if rel.attrib.get("TargetMode") == "External":
            continue
        resolved = (target.lstrip("/") if target.startswith("/") else
                    posixpath.normpath(posixpath.join(folder, target)))
        result[rel.attrib["Id"]] = (rel.attrib.get("Type", ""), resolved)
    return result


def gather_text(root: ET.Element) -> str:
    # XML text can include invisible shapes; the result is an unverified aid.
    parts = []
    for node in root.iter():
        if node.tag in {f"{{{A}}}t", f"{{{M}}}t"} and node.text:
            parts.append(node.text)
    return "\n".join(parts)


def inventory(path: Path) -> dict:
    if not zipfile.is_zipfile(path):
        raise ValueError("Input is not a ZIP-based PPTX file")
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        if "ppt/presentation.xml" not in names:
            raise ValueError("PPTX presentation.xml is missing")
        presentation = xml_file(zf, "ppt/presentation.xml")
        presentation_rels = relationships(zf, "ppt/presentation.xml")
        ids = presentation.findall(f".//{{{P}}}sldId")
        slides = []
        for number, slide_id in enumerate(ids, 1):
            rid = slide_id.attrib.get(f"{{{R}}}id")
            rel = presentation_rels.get(rid or "")
            if not rel or rel[1] not in names:
                slides.append({"number": number, "status": "missing-slide-xml"})
                continue
            slide_name = rel[1]
            root = xml_file(zf, slide_name)
            slide_rels = relationships(zf, slide_name)
            notes = []
            for kind, target in slide_rels.values():
                if kind.endswith("/notesSlide") and target in names:
                    notes.append(gather_text(xml_file(zf, target)))
            slides.append({
                "number": number,
                "slide_xml": slide_name,
                "text_unverified": gather_text(root),
                "speaker_notes_unverified": "\n".join(notes),
                "picture_count": len(root.findall(f".//{{{P}}}pic")),
                "table_count": len(root.findall(f".//{{{A}}}tbl")),
                "chart_count": sum(1 for n in root.iter() if n.tag.endswith("}chart")),
                "math_object_count": sum(1 for n in root.iter() if n.tag in {f"{{{M}}}oMath", f"{{{M}}}oMathPara"}),
            })
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"source": str(path.resolve()), "sha256": digest.hexdigest(),
            "slide_count": len(slides), "slides": slides,
            "warning": "Extracted XML text and object counts require visual verification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = inventory(args.pptx)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"Inventory failed: {exc}", file=sys.stderr)
        return 1
    data = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data + "\n", encoding="utf-8")
        print(f"{result['slide_count']} slides inventoried: {args.output}")
    else:
        print(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
