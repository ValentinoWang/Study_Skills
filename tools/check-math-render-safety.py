#!/usr/bin/env python3
"""Validate Study_Skills formula authoring and rendered-source contracts.

The current contract separates three things that used to be mixed together:

1. code: executable identifiers / snippets -> <code> / <pre><code>;
2. simple math: semantic HTML typography -> .math-inline / .math-display;
3. complex 2-D math: MathML / controlled renderer, only when structurally needed.

For lessons declaring ``math_mode: portable_html`` in lesson-manifest.json:

- native block <math> is forbidden;
- the retired flex-token renderer ``.portable-equation`` is forbidden;
- block equations use ``.math-display`` inside ``.formula-scroll``;
- each .math-display has role="math" and aria-label;
- inline equations use ``.math-inline`` and must never be a <code> element;
- obvious mathematical expressions may not be left in inline <code> pills;
- visible fallback layers are forbidden.

The CSS gate also rejects flex/grid/gap token layout for .math-display. Mathematical
spacing must come from a normal inline formatting context, with explicit relation
spacing only where needed.

Optionally pass ``--built-site /path/to/_site`` to apply the same structural checks
to the generated GitHub Pages HTML. Browser visual QA remains separate evidence.
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
MATH_CSS = ROOT / "docs/assets/css/learning-math.css"
FIGURE_CSS = ROOT / "docs/assets/css/learning-figure.css"

FORBIDDEN_MATH_CSS = re.compile(
    r"math(?:\[[^\]]*\])?\s*\{[^}]*\b(?:display\s*:\s*(?:block|flex|grid)|overflow(?:-x|-y)?\s*:)",
    re.I | re.S,
)
REGISTRY_SLUG = re.compile(r"(?m)^([a-z0-9][a-z0-9-]+):\n")
VISIBLE_FALLBACK = re.compile(
    r'class\s*=\s*["\'][^"\']*(?:math-fallback|formula-fallback)[^"\']*["\']',
    re.I,
)
MATH_GLYPHS = set("∈∩∪⊂⊆⊃⊇∼≈≠≤≥πδΣΘρ𝒜𝓜𝓡𝒢𝒮𝒪𝒞𝒦τλμνΩΦξ")
SUBSCRIPT_FORMULA = re.compile(
    r"(?:[A-Za-z]|[Α-ω]|[𝒜-𝓩𝒶-𝓏])_[A-Za-z0-9+\-]+\s*(?:=|∈|⊂|⊆|→|←|~|∼)"
)
FUNCTION_FORMULA = re.compile(r"(?:^|\s)[A-Za-z𝒜-𝓩]\s*=\s*[A-Za-z𝒜-𝓩]+\s*[\(\[]")


class FormulaTreeChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.block_math = 0
        self.math_wrapped = 0
        self.math_bare = 0
        self.math_display = 0
        self.math_display_wrapped = 0
        self.math_display_missing_role = 0
        self.math_display_missing_label = 0
        self.math_inline = 0
        self.math_inline_on_code = 0
        self.retired_portable = 0
        self.pre_depth = 0
        self._inline_code_chunks: list[str] | None = None
        self.inline_code_texts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        attr = dict(attrs)
        cls = set((attr.get("class") or "").split())
        lower = tag.lower()
        ancestors = [classes for _, classes in self.stack]

        if lower == "pre":
            self.pre_depth += 1

        if lower == "code" and self.pre_depth == 0:
            self._inline_code_chunks = []

        if lower == "math" and attr.get("display", "").lower() == "block":
            self.block_math += 1
            has_wrapper = any("formula-scroll" in classes for classes in ancestors)
            if has_wrapper:
                self.math_wrapped += 1
            else:
                self.math_bare += 1

        if "portable-equation" in cls:
            self.retired_portable += 1

        if "math-display" in cls:
            self.math_display += 1
            if any("formula-scroll" in classes for classes in ancestors):
                self.math_display_wrapped += 1
            if attr.get("role") != "math":
                self.math_display_missing_role += 1
            if not (attr.get("aria-label") or "").strip():
                self.math_display_missing_label += 1
            if lower == "code":
                self.math_inline_on_code += 1

        if "math-inline" in cls:
            self.math_inline += 1
            if lower == "code":
                self.math_inline_on_code += 1

        self.stack.append((lower, cls))

    def handle_data(self, data: str) -> None:
        if self._inline_code_chunks is not None:
            self._inline_code_chunks.append(data)

    def handle_startendtag(self, tag: str, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str):
        lower = tag.lower()
        if lower == "code" and self._inline_code_chunks is not None:
            self.inline_code_texts.append("".join(self._inline_code_chunks).strip())
            self._inline_code_chunks = None
        if lower == "pre" and self.pre_depth:
            self.pre_depth -= 1

        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == lower:
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


def looks_like_math_in_code(text: str) -> bool:
    """Conservative detector for the recurring 'formula rendered as code pill' bug."""
    value = re.sub(r"\s+", " ", text.strip())
    if not value:
        return False
    if any(ch in value for ch in MATH_GLYPHS):
        return True
    if SUBSCRIPT_FORMULA.search(value):
        return True
    if FUNCTION_FORMULA.search(value):
        return True
    return False


def portable_contract_failures(text: str, mode: str) -> tuple[list[str], FormulaTreeChecker]:
    failures: list[str] = []
    parser = parse_fragment(text)

    if mode == "portable_html":
        if parser.block_math:
            failures.append("portable_html forbids native block MathML")
        if parser.retired_portable:
            failures.append("retired .portable-equation flex-token renderer is forbidden")
        if parser.math_display == 0:
            failures.append("portable_html lesson contains no .math-display equation")
        offenders = [x for x in parser.inline_code_texts if looks_like_math_in_code(x)]
        if offenders:
            sample = "; ".join(repr(x[:80]) for x in offenders[:4])
            failures.append(f"mathematical expressions must not use inline <code>: {sample}")

    if parser.math_display and parser.math_display_wrapped != parser.math_display:
        failures.append("every .math-display must be inside .formula-scroll")
    if parser.math_display_missing_role:
        failures.append("every .math-display must use role=math")
    if parser.math_display_missing_label:
        failures.append("every .math-display must have aria-label")
    if parser.math_inline_on_code:
        failures.append(".math-inline/.math-display must not be attached to <code>")
    if VISIBLE_FALLBACK.search(text):
        failures.append("visible math/formula fallback layer is forbidden")

    return failures, parser


def css_contract_failures(math_css: str, figure_css: str) -> list[str]:
    failures: list[str] = []
    compact = re.sub(r"\s+", "", math_css)

    if ".math-inline" not in math_css:
        failures.append("learning-math.css must define .math-inline")
    if ".math-display" not in math_css:
        failures.append("learning-math.css must define .math-display")
    if "background:transparent!important" not in compact:
        failures.append("inline math must explicitly remove code-like backgrounds")
    if "padding:0!important" not in compact:
        failures.append("inline math must explicitly remove code-like padding")
    if ".portable-equation" in math_css:
        failures.append("learning-math.css must not revive .portable-equation")

    display_match = re.search(r"\.math-display\s*\{([^}]*)\}", math_css, re.S)
    if not display_match:
        failures.append("learning-math.css has no standalone .math-display block")
    else:
        block = display_match.group(1)
        if re.search(r"display\s*:\s*(?:flex|inline-flex|grid)", block, re.I):
            failures.append(".math-display may not use flex/grid token layout")
        if re.search(r"\bgap\s*:", block, re.I):
            failures.append(".math-display may not use gap-based token spacing")
        if not re.search(r"display\s*:\s*block", block, re.I):
            failures.append(".math-display must use normal block + inline formatting context")
        if not re.search(r"white-space\s*:\s*nowrap", block, re.I):
            failures.append(".math-display must keep an equation on one typographic line")

    if "learning-math.css" not in figure_css:
        failures.append("lesson CSS chain must include learning-math.css")
    return failures


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

    math_css = MATH_CSS.read_text(encoding="utf-8") if MATH_CSS.is_file() else ""
    figure_css = FIGURE_CSS.read_text(encoding="utf-8") if FIGURE_CSS.is_file() else ""

    print("effective canonical lesson fragments")
    total_math = total_bare = total_display = total_inline = 0
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
        total_display += parser.math_display
        total_inline += parser.math_inline

        if parser.math_bare and not wrapper_fallback:
            failures.append(
                f"{path.name}: {parser.math_bare} bare block MathML formula(s) require shared layout wrapper fallback"
            )

        print(
            f"  {'PASS' if len(failures)==before else 'FAIL'} {path.name}: "
            f"mode={mode}, block-math={parser.block_math}, display={parser.math_display}, "
            f"inline={parser.math_inline}, retired={parser.retired_portable}"
        )

    print("\nsemantic math CSS contract")
    if not MATH_CSS.is_file():
        failures.append("missing docs/assets/css/learning-math.css")
    if not FIGURE_CSS.is_file():
        failures.append("missing docs/assets/css/learning-figure.css")
    css_failures = css_contract_failures(math_css, figure_css)
    for item in css_failures:
        print(f"  FAIL {item}")
        failures.append(f"math CSS: {item}")
    if not css_failures:
        print("  PASS normal inline math formatting; no flex/grid/gap token renderer")

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
                f"mode={mode}, block-math={parser.block_math}, display={parser.math_display}, "
                f"inline={parser.math_inline}, retired={parser.retired_portable}"
            )

    print(
        f"\nformulas checked: block MathML={total_math}, math-display={total_display}, "
        f"math-inline={total_inline}, legacy bare MathML={total_bare}"
    )
    print("NOTE: this gate catches structural regressions; browser visual QA remains separate evidence.")
    if failures:
        print(f"MATH SAFETY FAIL: {len(failures)} problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("MATH SAFETY PASS: math and code use separate presentation contracts.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
