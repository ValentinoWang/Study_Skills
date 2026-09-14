#!/usr/bin/env python3
"""Regression tests for learning-figure failures seen in Study_Skills."""
from __future__ import annotations

import importlib.util
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_connector_crossing_protected_text_is_rejected() -> None:
    gate = load_module(ROOT / "tools/check-learning-figures.py", "figure_gate")
    bad = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" data-figure-id="x" '
        'viewBox="0 0 200 100"><title>x</title><desc>x</desc>'
        '<defs><marker id="a"/></defs>'
        '<rect id="safe" data-protect="text" x="60" y="30" width="80" height="40" fill="none"/>'
        '<line data-connector="bad" x1="10" y1="50" x2="190" y2="50" marker-end="url(#a)"/>'
        '<text data-term="state" x="80" y="55" font-size="20">state</text></svg>'
    )
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "bad.svg"
        p.write_text(bad, encoding="utf-8")
        failures = gate.check_svg(p, {"id": "x", "requires": ["state"]})
    assert any("crosses protected text zone" in x for x in failures), failures


def test_connector_around_protected_text_passes_geometry() -> None:
    gate = load_module(ROOT / "tools/check-learning-figures.py", "figure_gate_green")
    good = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" data-figure-id="x" '
        'viewBox="0 0 200 100"><title>x</title><desc>x</desc>'
        '<defs><marker id="a"/></defs>'
        '<rect id="safe" data-protect="text" x="60" y="30" width="80" height="40" fill="none"/>'
        '<line data-connector="good" x1="10" y1="15" x2="190" y2="15" marker-end="url(#a)"/>'
        '<text data-term="state" x="80" y="55" font-size="20">state</text></svg>'
    )
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "good.svg"
        p.write_text(good, encoding="utf-8")
        failures = gate.check_svg(p, {"id": "x", "requires": ["state"]})
    assert not any("crosses protected text zone" in x for x in failures), failures


def test_manifest_figure_requires_are_declared_in_section_prerequisites() -> None:
    gate = load_module(ROOT / "tools/check-learning-figures.py", "figure_gate_manifest")
    cfg = {"section_prerequisites": {"deep1": {"file": "01.html", "terms": ["state"]}}}
    assert gate.section_prerequisites(cfg, "deep1") == {"state"}
    missing = {"props"} - gate.section_prerequisites(cfg, "deep1")
    assert missing == {"props"}


def main() -> int:
    test_connector_crossing_protected_text_is_rejected()
    test_connector_around_protected_text_passes_geometry()
    test_manifest_figure_requires_are_declared_in_section_prerequisites()
    print("PASS: learning-figure regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
