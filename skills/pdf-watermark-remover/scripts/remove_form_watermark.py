#!/usr/bin/env python3
"""Remove directly invoked, explicitly tagged Form-XObject PDF watermarks.

The writer appends a small incremental update rather than serializing every PDF
object again. That preserves complex source content streams and leaves the
source file unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, IndirectObject, NameObject


DO_PATTERN = re.compile(rb"/([^\s/<>{}\[\]()]+)\s+Do\b")


def is_watermark_form(xobject: Any) -> bool:
    """Return True only for a Form object explicitly tagged as a watermark."""
    if xobject.get("/Subtype") != "/Form":
        return False
    piece_info = xobject.get("/PieceInfo") or {}
    compound_type = piece_info.get("/ADBE_CompoundType") or {}
    return compound_type.get("/Private") == "/Watermark"


def stream_references(page: Any) -> list[IndirectObject]:
    contents = page.raw_get("/Contents")
    if isinstance(contents, IndirectObject):
        return [contents]
    if isinstance(contents, ArrayObject):
        if not all(isinstance(item, IndirectObject) for item in contents):
            raise ValueError("page has a direct content stream; cannot safely create an incremental update")
        return list(contents)
    raise ValueError("page has no indirect /Contents stream")


def direct_watermark_names(page: Any, content_data: bytes) -> set[bytes]:
    resources = page.get("/Resources") or {}
    xobjects = resources.get("/XObject") or {}
    names: set[bytes] = set()
    for match in DO_PATTERN.finditer(content_data):
        raw_name = match.group(1)
        try:
            resource = xobjects[NameObject("/" + raw_name.decode("latin-1"))].get_object()
        except (KeyError, UnicodeDecodeError):
            continue
        if is_watermark_form(resource):
            names.add(raw_name)
    return names


def remove_calls(content_data: bytes, watermark_names: set[bytes]) -> tuple[bytes, int]:
    removed = 0

    def replace(match: re.Match[bytes]) -> bytes:
        nonlocal removed
        if match.group(1) in watermark_names:
            removed += 1
            # A balanced no-op keeps any surrounding q/Q graphics-state scope valid.
            return b"q Q"
        return match.group(0)

    return DO_PATTERN.sub(replace, content_data), removed


def build_incremental_pdf(source_data: bytes, reader: PdfReader) -> tuple[bytes, dict[str, int]]:
    if reader.is_encrypted:
        raise ValueError("encrypted PDFs are not supported")
    if b"/ByteRange" in source_data:
        raise ValueError("digitally signed PDFs are not supported")

    updates: dict[tuple[int, int], tuple[bytes, bool]] = {}
    removed_references = 0
    for page in reader.pages:
        for ref in stream_references(page):
            stream = ref.get_object()
            filter_name = stream.get("/Filter")
            if filter_name not in (None, "/FlateDecode"):
                raise ValueError(f"unsupported content stream filter {filter_name} in object {ref.idnum}")
            original = stream.get_data()
            names = direct_watermark_names(page, original)
            if not names:
                continue
            updated, removed = remove_calls(original, names)
            if removed:
                payload = zlib.compress(updated) if filter_name == "/FlateDecode" else updated
                updates[(ref.idnum, ref.generation)] = (payload, filter_name == "/FlateDecode")
                removed_references += removed

    if not updates:
        raise ValueError("no direct Form XObject explicitly tagged /Watermark was found")

    marker = b"startxref"
    marker_pos = source_data.rfind(marker)
    if marker_pos < 0:
        raise ValueError("source PDF has no startxref marker")
    try:
        previous_xref = int(source_data[marker_pos:].splitlines()[1])
    except (IndexError, ValueError) as exc:
        raise ValueError("cannot read source PDF cross-reference offset") from exc

    output = bytearray(source_data)
    output.extend(b"\n")
    offsets: list[tuple[int, int, int]] = []
    for (object_id, generation), (payload, use_flate) in sorted(updates.items()):
        offsets.append((object_id, generation, len(output)))
        stream_filter = b" /Filter /FlateDecode" if use_flate else b""
        output.extend(f"{object_id} {generation} obj\n<< /Length {len(payload)}".encode())
        output.extend(stream_filter)
        output.extend(b" >>\nstream\n")
        output.extend(payload)
        output.extend(b"\nendstream\nendobj\n")

    xref_offset = len(output)
    output.extend(b"xref\n")
    for object_id, generation, offset in offsets:
        output.extend(f"{object_id} 1\n{offset:010} {generation:05} n \n".encode())

    root = reader.trailer.raw_get("/Root")
    info = reader.trailer.raw_get("/Info")
    if not isinstance(root, IndirectObject):
        raise ValueError("source PDF has no indirect /Root")
    trailer = f"trailer\n<< /Size {reader.trailer.get('/Size')} /Root {root.idnum} {root.generation} R /Prev {previous_xref}"
    if isinstance(info, IndirectObject):
        trailer += f" /Info {info.idnum} {info.generation} R"
    trailer += f" >>\nstartxref\n{xref_offset}\n%%EOF\n"
    output.extend(trailer.encode())
    return bytes(output), {"removed_references": removed_references, "updated_streams": len(updates)}


def count_direct_watermark_references(reader: PdfReader) -> int:
    total = 0
    for page in reader.pages:
        for ref in stream_references(page):
            names = direct_watermark_names(page, ref.get_object().get_data())
            if names:
                _, count = remove_calls(ref.get_object().get_data(), names)
                total += count
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("source and output must be different files")
    if not source.is_file():
        raise SystemExit(f"source PDF not found: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)

    source_data = source.read_bytes()
    source_reader = PdfReader(source)
    output_data, report = build_incremental_pdf(source_data, source_reader)
    with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as temporary:
        temporary.write(output_data)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, output)

    output_reader = PdfReader(output)
    report.update(
        {
            "source": str(source),
            "output": str(output),
            "source_pages": len(source_reader.pages),
            "output_pages": len(output_reader.pages),
            "remaining_direct_watermark_references": count_direct_watermark_references(output_reader),
        }
    )
    if report["source_pages"] != report["output_pages"] or report["remaining_direct_watermark_references"]:
        raise SystemExit(f"output validation failed: {json.dumps(report, ensure_ascii=False)}")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
