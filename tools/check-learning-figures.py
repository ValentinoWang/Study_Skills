#!/usr/bin/env python3
"""Validate Study_Skills teaching-figure contracts.

The gate checks:
- manifest contract completeness;
- canonical/public SVG identity;
- SVG accessibility metadata and vector structure;
- data-term labels against figure prerequisites and section prerequisites;
- the target lesson section actually embeds the public figure;
- stable line-vs-protected-text geometry failures.

This is a semantic/static gate, not a substitute for final browser render QA.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills/learning-page-design-publisher/lesson-manifest.json"

REQUIRED_FIELDS = {
    "id", "section_id", "question", "takeaway", "source", "public_path",
    "requires", "mobile_strategy", "evidence_type", "embed_file", "layout_include",
}
MOBILE_STRATEGIES = {"stack", "scroll", "responsive"}
EVIDENCE_TYPES = {"teaching-example", "schematic", "measured-data"}


def load_manifest() -> dict[str, dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("lesson-manifest.json must contain an object")
    return data


def tag_name(elem: ET.Element) -> str:
    return elem.tag.split("}", 1)[-1]


def numeric(elem: ET.Element, name: str) -> float:
    raw = elem.attrib.get(name)
    if raw is None:
        raise ValueError(f"missing numeric {name}")
    return float(raw)


def point_inside_rect(x: float, y: float, rect: tuple[float, float, float, float], eps: float = 1e-6) -> bool:
    rx, ry, rw, rh = rect
    return rx + eps < x < rx + rw - eps and ry + eps < y < ry + rh - eps


def segment_hits_rect_interior(
    line: tuple[float, float, float, float],
    rect: tuple[float, float, float, float],
) -> bool:
    """Liang-Barsky style clipping against axis-aligned protected rectangles."""
    x1, y1, x2, y2 = line
    if point_inside_rect(x1, y1, rect) or point_inside_rect(x2, y2, rect):
        return True

    rx, ry, rw, rh = rect
    left, right = rx, rx + rw
    top, bottom = ry, ry + rh
    dx, dy = x2 - x1, y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - left, right - x1, y1 - top, bottom - y1)
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)
        if u1 > u2:
            return False

    if u2 - u1 <= 1e-8:
        return False
    mid = (u1 + u2) / 2
    mx, my = x1 + mid * dx, y1 + mid * dy
    return point_inside_rect(mx, my, rect)


def section_prerequisites(cfg: dict, section_id: str) -> set[str]:
    section_cfg = cfg.get("section_prerequisites") or {}
    spec = section_cfg.get(section_id) or {}
    return {str(x).lower() for x in spec.get("terms", [])}


def svg_text_terms(root: ET.Element) -> set[str]:
    terms: set[str] = set()
    for elem in root.iter():
        term = elem.attrib.get("data-term")
        if term:
            terms.add(term)
    return terms


def svg_has_title_desc(root: ET.Element) -> tuple[bool, bool]:
    has_title = any(tag_name(e) == "title" and "".join(e.itertext()).strip() for e in root.iter())
    has_desc = any(tag_name(e) == "desc" and "".join(e.itertext()).strip() for e in root.iter())
    return has_title, has_desc


def check_geometry(root: ET.Element, figure_id: str) -> list[str]:
    failures: list[str] = []
    protected: list[tuple[str, tuple[float, float, float, float]]] = []
    connectors: list[tuple[str, tuple[float, float, float, float], ET.Element]] = []

    for elem in root.iter():
        name = tag_name(elem)
        if name == "rect" and elem.attrib.get("data-protect") == "text":
            try:
                protected.append((
                    elem.attrib.get("id", "<protected>"),
                    (numeric(elem, "x"), numeric(elem, "y"), numeric(elem, "width"), numeric(elem, "height")),
                ))
            except ValueError as exc:
                failures.append(f"{figure_id}: protected rect {exc}")
        if name == "line" and elem.attrib.get("data-connector"):
            try:
                connectors.append((
                    elem.attrib.get("data-connector", "<connector>"),
                    (numeric(elem, "x1"), numeric(elem, "y1"), numeric(elem, "x2"), numeric(elem, "y2")),
                    elem,
                ))
            except ValueError as exc:
                failures.append(f"{figure_id}: connector line {exc}")

    for connector_id, line, elem in connectors:
        if "marker-end" not in elem.attrib:
            failures.append(f"{figure_id}: connector {connector_id} lacks marker-end")
        for protected_id, rect in protected:
            if segment_hits_rect_interior(line, rect):
                failures.append(
                    f"{figure_id}: connector {connector_id} crosses protected text zone {protected_id}; "
                    "reroute the line or resize/move the protected zone"
                )
    return failures


def check_svg(path: pathlib.Path, spec: dict) -> list[str]:
    failures: list[str] = []
    figure_id = str(spec["id"])
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{figure_id}: SVG parse failed: {exc}"]

    if tag_name(root) != "svg":
        return [f"{figure_id}: root element is not svg"]
    if not root.attrib.get("viewBox"):
        failures.append(f"{figure_id}: SVG lacks viewBox")
    if root.attrib.get("role") != "img":
        failures.append(f"{figure_id}: SVG root must use role=img")
    if root.attrib.get("data-figure-id") != figure_id:
        failures.append(f"{figure_id}: data-figure-id mismatch")
    has_title, has_desc = svg_has_title_desc(root)
    if not has_title:
        failures.append(f"{figure_id}: SVG lacks non-empty <title>")
    if not has_desc:
        failures.append(f"{figure_id}: SVG lacks non-empty <desc>")
    if any(tag_name(e) == "image" for e in root.iter()):
        failures.append(f"{figure_id}: schematic SVG must not hide raster <image> assets")

    required = {str(x) for x in spec.get("requires", [])}
    data_terms = svg_text_terms(root)
    undeclared = sorted(data_terms - required)
    missing_in_svg = sorted(required - data_terms)
    if undeclared:
        failures.append(f"{figure_id}: SVG data-term labels are not declared in requires: {', '.join(undeclared)}")
    if missing_in_svg:
        failures.append(f"{figure_id}: requires terms not represented by SVG data-term labels: {', '.join(missing_in_svg)}")

    for elem in root.iter():
        if tag_name(elem) != "text":
            continue
        raw = elem.attrib.get("font-size")
        if raw is None:
            failures.append(f"{figure_id}: every SVG <text> must declare font-size explicitly")
            continue
        try:
            size = float(re.sub(r"[^0-9.]", "", raw))
        except ValueError:
            failures.append(f"{figure_id}: invalid font-size {raw!r}")
            continue
        if size < 18:
            failures.append(f"{figure_id}: text font-size {size:g} is below the 18-unit teaching-diagram floor")

    failures.extend(check_geometry(root, figure_id))
    return failures


def check_figure(slug: str, cfg: dict, spec: dict) -> list[str]:
    failures: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(spec))
    figure_id = str(spec.get("id", "<missing-id>"))
    if missing:
        return [f"{slug}/{figure_id}: missing manifest fields: {', '.join(missing)}"]

    if spec["mobile_strategy"] not in MOBILE_STRATEGIES:
        failures.append(f"{slug}/{figure_id}: invalid mobile_strategy={spec['mobile_strategy']!r}")
    if spec["evidence_type"] not in EVIDENCE_TYPES:
        failures.append(f"{slug}/{figure_id}: invalid evidence_type={spec['evidence_type']!r}")
    if len(str(spec["question"]).strip()) < 8:
        failures.append(f"{slug}/{figure_id}: learning question is too thin")
    if len(str(spec["takeaway"]).strip()) < 12:
        failures.append(f"{slug}/{figure_id}: takeaway is too thin")

    source = ROOT / str(spec["source"])
    public = ROOT / str(spec["public_path"])
    if not source.is_file():
        failures.append(f"{slug}/{figure_id}: missing canonical figure source {source.relative_to(ROOT)}")
        return failures
    if not public.is_file():
        failures.append(f"{slug}/{figure_id}: missing public figure mirror {public.relative_to(ROOT)}")
    elif source.read_bytes() != public.read_bytes():
        failures.append(f"{slug}/{figure_id}: canonical/public figure bytes differ")

    if source.suffix.lower() != ".svg":
        failures.append(f"{slug}/{figure_id}: current schematic figure gate expects SVG source")
    else:
        failures.extend(f"{slug}/{msg}" for msg in check_svg(source, spec))

    section_id = str(spec["section_id"])
    requires = {str(x).lower() for x in spec.get("requires", [])}
    available = section_prerequisites(cfg, section_id)
    missing_prereq = sorted(requires - available)
    if missing_prereq:
        failures.append(
            f"{slug}/{figure_id}: figure requires terms not declared in {section_id} prerequisites: "
            + ", ".join(missing_prereq)
        )

    supplement = cfg.get("supplement_source_dir")
    section_spec = (cfg.get("section_prerequisites") or {}).get(section_id) or {}
    section_file = section_spec.get("file")
    if not supplement or not section_file:
        failures.append(f"{slug}/{figure_id}: target section has no canonical supplement file")
        return failures

    section_path = ROOT / str(supplement) / str(section_file)
    if not section_path.is_file():
        failures.append(f"{slug}/{figure_id}: missing target section source {section_path.relative_to(ROOT)}")
        return failures

    embed_path = ROOT / str(supplement) / str(spec["embed_file"])
    if not embed_path.is_file():
        failures.append(f"{slug}/{figure_id}: missing canonical figure embed {embed_path.relative_to(ROOT)}")
        return failures
    embed_html = embed_path.read_text(encoding="utf-8")
    if f'data-figure-id="{figure_id}"' not in embed_html:
        failures.append(f"{slug}/{figure_id}: embed file lacks data-figure-id")
    public_url = "/" + str(spec["public_path"]).removeprefix("docs/")
    if public_url not in embed_html:
        failures.append(f"{slug}/{figure_id}: embed file does not reference public figure path {public_url}")
    if spec["mobile_strategy"] == "scroll" and "learning-figure-scroll" not in embed_html:
        failures.append(f"{slug}/{figure_id}: scroll strategy requires a learning-figure-scroll wrapper")

    layout_name = str(cfg.get("layout", "lesson"))
    layout_path = ROOT / "docs/_layouts" / f"{layout_name}.html"
    include_token = "{% include " + str(spec["layout_include"]) + " %}"
    if not layout_path.is_file():
        failures.append(f"{slug}/{figure_id}: missing configured layout {layout_path.relative_to(ROOT)}")
    elif include_token not in layout_path.read_text(encoding="utf-8"):
        failures.append(f"{slug}/{figure_id}: configured layout does not include {spec['layout_include']}")

    if spec["evidence_type"] == "measured-data":
        for field in ("data_source", "unit"):
            if not spec.get(field):
                failures.append(f"{slug}/{figure_id}: measured-data figure requires {field}")
    return failures


def main() -> int:
    manifest = load_manifest()
    failures: list[str] = []
    figure_count = 0
    print("teaching figures")
    for slug, cfg in sorted(manifest.items()):
        figures = cfg.get("figures", [])
        if figures and not isinstance(figures, list):
            failures.append(f"{slug}: figures must be a list")
            continue
        for spec in figures:
            figure_count += 1
            local = check_figure(slug, cfg, spec)
            figure_id = spec.get("id", "<missing-id>") if isinstance(spec, dict) else "<invalid>"
            print(f"  {'OK  ' if not local else 'FAIL'} {slug}/{figure_id}: problems={len(local)}")
            failures.extend(local)

    print()
    if failures:
        print(f"FIGURE GATE FAIL: {len(failures)} problem(s)")
        for item in failures:
            print("  -", item)
        return 1
    print(f"FIGURE GATE PASS: {figure_count} teaching figure(s) satisfy source, prerequisite and SVG guards.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
