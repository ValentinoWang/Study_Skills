#!/usr/bin/env python3
"""Regression tests for learning-contract failures seen in real lessons."""
from __future__ import annotations

import importlib.util
import json
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


def test_portable_math_rejects_native_mathml_and_bad_fallbacks() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate")
    bad_math = (
        '<div class="formula-scroll"><math display="block" aria-label="x equals y">'
        '<mi>x</mi><mo>=</mo><mi>y</mi></math></div>'
    )
    failures, _ = math_gate.portable_contract_failures(bad_math, "portable_html")
    assert any("forbids native block MathML" in x for x in failures), failures

    bad_fallback = (
        '<div class="formula-scroll"><div class="portable-equation" role="math" aria-label="x equals y">'
        '<span class="eq-var">x</span><span class="eq-op">=</span><span class="eq-var">y</span></div></div>'
        '<div class="formula-fallback">x = y</div>'
    )
    failures, _ = math_gate.portable_contract_failures(bad_fallback, "portable_html")
    assert any("fallback" in x for x in failures), failures


def test_portable_math_requires_wrapper_role_and_label() -> None:
    math_gate = load_module(ROOT / "tools/check-math-render-safety.py", "math_gate_contract")
    broken = '<div class="portable-equation"><span>x = y</span></div>'
    failures, _ = math_gate.portable_contract_failures(broken, "portable_html")
    assert any("formula-scroll" in x for x in failures), failures
    assert any("role=math" in x for x in failures), failures
    assert any("aria-label" in x for x in failures), failures

    good = (
        '<div class="formula-scroll"><div class="portable-equation" role="math" aria-label="x equals y">'
        '<span class="eq-var">x</span><span class="eq-op">=</span><span class="eq-var">y</span>'
        '</div></div>'
    )
    failures, parsed = math_gate.portable_contract_failures(good, "portable_html")
    assert not failures, failures
    assert parsed.portable == 1 and parsed.block_math == 0


def main() -> int:
    test_layout_manifest_prevents_wrapper_regression()
    test_identifier_used_after_primer_is_rejected()
    test_portable_math_rejects_native_mathml_and_bad_fallbacks()
    test_portable_math_requires_wrapper_role_and_label()
    print("PASS: learning-contract regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
