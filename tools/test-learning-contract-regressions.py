#!/usr/bin/env python3
"""Regression tests for learning-contract failures seen in real lessons."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_layout_manifest_prevents_wrapper_regression() -> None:
    build = load_module(ROOT / "tools/build-lessons.py", "build_lessons")
    manifest = json.loads(
        (ROOT / "skills/learning-page-design-publisher/lesson-manifest.json").read_text(encoding="utf-8")
    )
    slug = "software-engineering-two-hour-primer-20260913"
    assert build.layout_for(manifest, slug) == "lesson-expanded"
    expected = build.wrapper(manifest, slug)
    actual = (ROOT / f"docs/lessons/{slug}.html").read_text(encoding="utf-8")
    assert actual == expected, "normal rebuild contract would regress the expanded lesson wrapper"


def test_identifier_used_after_primer_is_rejected() -> None:
    gate = load_module(ROOT / "tools/check-term-gate.py", "term_gate")
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        src = root / "supp"
        src.mkdir()
        (src / "01.html").write_text(
            "<h3>0. 本节先认词 / 先认变量</h3><p>state = 当前状态。</p>"
            "<h3>1. 机制</h3><p>这里才第一次出现 props，但已经开始拿它推理。</p>",
            encoding="utf-8",
        )
        old_root = gate.ROOT
        try:
            gate.ROOT = root
            cfg = {
                "supplement_source_dir": "supp",
                "section_prerequisites": {
                    "deep1": {"file": "01.html", "terms": ["state", "props"]}
                },
            }
            failures = gate.check_declared_prerequisites("fixture", cfg)
        finally:
            gate.ROOT = old_root
        assert any("props" in x for x in failures), failures
        assert not any("state is used without" in x for x in failures), failures


def test_portable_math_rejects_native_mathml_and_retired_renderer() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate")
    bad_math = (
        '<div class="formula-scroll"><math display="block" aria-label="x equals y">'
        '<mi>x</mi><mo>=</mo><mi>y</mi></math></div>'
    )
    failures, _ = math_gate.portable_contract_failures(bad_math, "portable_html")
    assert any("forbids native block MathML" in x for x in failures), failures

    retired = (
        '<div class="formula-scroll"><div class="portable-equation" role="math" aria-label="x equals y">'
        '<span>x</span><span>=</span><span>y</span></div></div>'
    )
    failures, _ = math_gate.portable_contract_failures(retired, "portable_html")
    assert any("retired" in x for x in failures), failures


def test_math_display_requires_wrapper_role_and_label() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate_contract")
    broken = '<div class="math-display"><var>x</var> = <var>y</var></div>'
    failures, _ = math_gate.portable_contract_failures(broken, "portable_html")
    assert any("formula-scroll" in x for x in failures), failures
    assert any("role=math" in x for x in failures), failures
    assert any("aria-label" in x for x in failures), failures

    good = (
        '<div class="formula-scroll"><div class="math-display" role="math" aria-label="x equals y">'
        '<var>x</var><span class="rel">=</span><var>y</var></div></div>'
    )
    failures, parsed = math_gate.portable_contract_failures(good, "portable_html")
    assert not failures, failures
    assert parsed.math_display == 1 and parsed.block_math == 0


def test_math_must_not_be_rendered_as_inline_code_pills() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate_code_pill")
    bad = (
        '<div class="formula-scroll"><div class="math-display" role="math" aria-label="x equals y">'
        '<var>x</var><span class="rel">=</span><var>y</var></div></div>'
        '<p>策略是 <code>a_t∼πθ(·|c_t,g)</code>。</p>'
    )
    failures, _ = math_gate.portable_contract_failures(bad, "portable_html")
    assert any("inline <code>" in x for x in failures), failures

    wrong_tag = (
        '<div class="formula-scroll"><div class="math-display" role="math" aria-label="x equals y">'
        '<var>x</var><span class="rel">=</span><var>y</var></div></div>'
        '<code class="math-inline">x = y</code>'
    )
    failures, _ = math_gate.portable_contract_failures(wrong_tag, "portable_html")
    assert any("must not be attached to <code>" in x for x in failures), failures


def test_math_css_rejects_flex_gap_token_layout() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate_css")
    bad_css = """
.math-inline{background:transparent!important;padding:0!important}
.math-display{display:flex;gap:.34em;white-space:nowrap}
"""
    failures = math_gate.css_contract_failures(
        bad_css,
        '@import url("./learning-math.css");',
    )
    assert any("flex/grid" in x for x in failures), failures
    assert any("gap-based" in x for x in failures), failures

    actual_math = (ROOT / "docs/assets/css/learning-math.css").read_text(encoding="utf-8")
    actual_figure = (ROOT / "docs/assets/css/learning-figure.css").read_text(encoding="utf-8")
    failures = math_gate.css_contract_failures(actual_math, actual_figure)
    assert not failures, failures


def test_math_tables_preserve_readable_width() -> None:
    css = (ROOT / "docs/assets/css/learning-math.css").read_text(encoding="utf-8")
    match = re.search(r"\.math-table\s+table\s*\{([^}]*)\}", css, re.S)
    assert match, "math-heavy tables need an explicit readable-width contract"
    width = re.search(r"min-width\s*:\s*(\d+)px", match.group(1))
    assert width and int(width.group(1)) >= 600, "math table min-width is too small to remain readable"


def main() -> int:
    test_layout_manifest_prevents_wrapper_regression()
    test_identifier_used_after_primer_is_rejected()
    test_portable_math_rejects_native_mathml_and_retired_renderer()
    test_math_display_requires_wrapper_role_and_label()
    test_math_must_not_be_rendered_as_inline_code_pills()
    test_math_css_rejects_flex_gap_token_layout()
    test_math_tables_preserve_readable_width()
    print("PASS: learning-contract regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
