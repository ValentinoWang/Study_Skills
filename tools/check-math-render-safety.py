#!/usr/bin/env python3
"""Validate portable formula and MathML rendering safety for Study_Skills lessons.

The default contract for simple algebra / set / state-transition formulas is
portable HTML, not native MathML. Native MathML remains available for complex
structures where semantic math markup materially helps (fractions, matrices,
roots, integrals, etc.).

This checker separates:
  1. artifact identity: canonical source / mirrors are the same bytes;
  2. source safety: the chosen math mode follows its structural contract;
  3. rendered-source safety: the built Pages HTML keeps the same contract.

For lessons declaring `math_mode: portable_html` in lesson-manifest.json:
  - native <math> is forbidden;
  - every .portable-equation must be inside .formula-scroll;
  - every .portable-equation must expose role="math" and an aria-label;
  - visible fallback layers such as .math-fallback / .formula-fallback are forbidden.

Optionally pass:
    --built-site /path/to/_site
and the checker also inspects generated Pages HTML. Actual cross-browser visual
QA is still distinct evidence; this gate prevents the known failure mode from
being reintroduced structurally.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
LESSON_DIR = PAGE_SKILL / "lessons"
REGISTRY = PAGE_SKILL / "term-overrides.yml"
MANIFEST = PAGE_SKILL / "lesson-manifest.json"
LAYOUT = ROOT / "docs/_layouts/lesson.html"
PORTABLE_CSS = ROOT / "docs/assets/css/learning-figure.css"

FORBIDDEN_MATH_CSS = re.compile(
    r"math(?:\[[^\]]*\])?\s*\{[^}]*\b(?:display\s*:\s*(?:block|flex|grid)|overflow(?:-x|-y)?\s*:)",
    re.I | re.S,
)
REGISTRY_SLUG = re.compile(r"(?m)^([a-z0-9][a-z0-9-]+):\n")
VISIBLE_FALLBACK = re.compile(
    r'class\s*=\s*["\'][^"\']*(?:math-fallback|formula-fallback)[^"\']*["\']',
    re.I,
)


class FormulaTreeChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.block_math = 0
        self.math_wrapped = 0
        self.math_bare = 0
        self.portable = 0
        self.portable_wrapped = 0
        self.portable_missing_role = 0
        self.portable_missing_label = 0

    def handle_starttag(self, tag: str, attrs):
        attr = dict(attrs)
        cls = set((attr.get("class") or "").split())
        lower = tag.lower()
        ancestors = [classes for _, classes in self.stack]

        if lower == "math" and attr.get("display", "").lower() == "block":
            self.block_math += 1
            has_wrapper = any("formula-scroll" in classes for classes in ancestors)
            if has_wrapper:
                self.math_wrapped += 1
            else:
                self.math_bare += 1

        if "portable-equation" in cls:
            self.portable += 1
            if any("formula-scroll" in classes for classes in ancestors):
                self.portable_wrapped += 1
            if attr.get("role") != "math":
                self.portable_missing_role += 1
            if not (attr.get("aria-label") or "").strip():
                self.portable_missing_label += 1

        self.stack.append((lower, cls))

    def handle_startendtag(self, tag: str, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack:
            self.stack.pop()

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def registry_slugs(text: str) -> set[str]:
    return set(REGISTRY_SLUG.findall(text))


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.is_file():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("lesson-manifest.json must contain an object")
    return data


def parse_fragment(text: str) -> FormulaTreeChecker:
    parser = FormulaTreeChecker()
    parser.feed(text)
    return parser


def built_site_arg() -> pathlib.Path | None:
    if "--built-site" not in sys.argv:
        return None
    i = sys.argv.index("--built-site")
    if i + 1 >= len(sys.argv):
        raise SystemExit("--built-site requires a path")
    return pathlib.Path(sys.argv[i + 1]).resolve()


def portable_contract_failures(text: str, mode: str) -> tuple[list[str], FormulaTreeChecker]:
    failures: list[str] = []
    parser = parse_fragment(text)
    if mode == "portable_html" and parser.block_math:
        failures.append("portable_html forbids native block MathML")
    if mode == "portable_html" and parser.portable == 0:
        failures.append("portable_html lesson contains no .portable-equation")
    if parser.portable and parser.portable_wrapped != parser.portable:
        failures.append("every .portable-equation must be inside .formula-scroll")
    if parser.portable_missing_role:
        failures.append("every .portable-equation must use role=math")
    if parser.portable_missing_label:
        failures.append("every .portable-equation must have aria-label")
    if VISIBLE_FALLBACK.search(text):
        failures.append("visible math/formula fallback layer is forbidden")
    return failures, parser


def main() -> int:
    failures: list[str] = []
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.is_file() else ""
    overridden = registry_slugs(registry_text)
    manifest = load_manifest()

    layout = LAYOUT.read_text(encoding="utf-8") if LAYOUT.is_file() else ""
    wrapper_fallback = (
        "querySelectorAll('math[display=\"block\"]')" in layout
        and "formula-scroll" in layout
    )

    css = PORTABLE_CSS.read_text(encoding="utf-8") if PORTABLE_CSS.is_file() else ""
    css_checks = {
        "portable equation class exists": ".portable-equation" in css,
        "portable equation does not wrap tokens": "white-space:nowrap" in css.replace(" ", ""),
        "portable subscript styling exists": ".portable-equation sub" in css,
    }

    print("effective canonical lesson fragments")
    total_math = total_bare = total_portable = 0
    for path in sorted(LESSON_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = path.stem
        cfg = manifest.get(slug, {}) if isinstance(manifest.get(slug, {}), dict) else {}
        mode = str(cfg.get("math_mode", "legacy_or_mixed"))
        before = len(failures)
        combined_parts: list[str] = []

        for key, value in data.items():
            if not isinstance(value, str):
                continue
            if key == "TERMS_HTML" and slug in overridden:
                continue
            if FORBIDDEN_MATH_CSS.search(value):
                failures.append(f"{path.name}:{key}: CSS overrides MathML root layout/overflow")
            combined_parts.append(value)

        combined = "\n".join(combined_parts)
        local, parser = portable_contract_failures(combined, mode)
        failures.extend(f"{path.name}: {item}" for item in local)
        total_math += parser.block_math
        total_bare += parser.math_bare
        total_portable += parser.portable

        if parser.math_bare and not wrapper_fallback:
            failures.append(
                f"{path.name}: {parser.math_bare} bare block MathML formula(s) require shared layout wrapper fallback"
            )

        print(
            f"  {'PASS' if len(failures)==before else 'FAIL'} {path.name}: "
            f"mode={mode}, block-math={parser.block_math}, portable={parser.portable}, bare={parser.math_bare}"
        )

    print("\nportable formula CSS contract")
    if not PORTABLE_CSS.is_file():
        failures.append("missing docs/assets/css/learning-figure.css")
    for label, ok in css_checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {label}")
        if not ok:
            failures.append(f"portable CSS: {label}")

    print("\nterminology registry")
    if not REGISTRY.is_file():
        failures.append("missing terminology registry")
    elif FORBIDDEN_MATH_CSS.search(registry_text):
        failures.append("term-overrides.yml: CSS overrides MathML root layout/overflow")
        print("  FAIL forbidden MathML-root CSS")
    else:
        print("  PASS no MathML-root layout override")

    print("\nshared layout")
    if not layout:
        failures.append("missing docs/_layouts/lesson.html")
    checks = {
        "formula-scroll owns horizontal overflow": (
            ".formula-scroll" in layout and "overflow-x:auto" in layout.replace(" ", "")
        ),
        "layout does not force MathML display": not re.search(
            r"math[^\{]*\{[^}]*display\s*:", layout, re.I | re.S
        ),
        "layout does not put overflow on MathML root": not re.search(
            r"math[^\{]*\{[^}]*overflow(?:-x|-y)?\s*:", layout, re.I | re.S
        ),
        "legacy block MathML is wrapped externally": wrapper_fallback,
        "legacy MathML receives an accessible label": (
            "setAttribute('aria-label'" in layout or 'setAttribute("aria-label"' in layout
        ),
    }
    for label, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {label}")
        if not ok:
            failures.append(f"layout: {label}")

    built = built_site_arg()
    if built is not None:
        print("\ngenerated Pages HTML source")
        for page in sorted((built / "lessons").glob("*.html")):
            text = page.read_text(encoding="utf-8")
            slug = page.stem
            cfg = manifest.get(slug, {}) if isinstance(manifest.get(slug, {}), dict) else {}
            mode = str(cfg.get("math_mode", "legacy_or_mixed"))
            before = len(failures)
            if FORBIDDEN_MATH_CSS.search(text):
                failures.append(f"{page.relative_to(built)}: generated HTML contains forbidden MathML-root CSS")
            local, parser = portable_contract_failures(text, mode)
            failures.extend(f"{page.relative_to(built)}: {item}" for item in local)
            if parser.math_bare and not wrapper_fallback:
                failures.append(f"{page.relative_to(built)}: bare block MathML has no runtime wrapper fallback")
            print(
                f"  {'PASS' if len(failures)==before else 'FAIL'} {page.name}: "
                f"mode={mode}, block-math={parser.block_math}, portable={parser.portable}, bare-before-js={parser.math_bare}"
            )

    print(
        f"\nformulas checked: block MathML={total_math}, portable HTML={total_portable}, "
        f"legacy bare MathML delegated to layout={total_bare}"
    )
    print("NOTE: source and blob checks do not replace cross-browser visual QA; portable_html prevents known native-MathML duplication structurally.")
    if failures:
        print(f"MATH SAFETY FAIL: {len(failures)} problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("MATH SAFETY PASS: declared formula modes follow portable/MathML contracts.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
