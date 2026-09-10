#!/usr/bin/env python3
"""Validate MathML rendering safety for Study_Skills lessons.

This checker separates three different claims:
  1. artifact identity: two files have the same bytes/hash;
  2. source safety: effective lesson fragments do not sabotage MathML layout;
  3. render safety: the shared layout owns overflow via an outer wrapper and
     preserves the browser's native MathML formatting context.

The terminology registry may override lesson['TERMS_HTML']; in that case the
fallback TERMS_HTML is not part of the effective Pages artifact and must not be
used to fail the build. Legacy bare block MathML in effective lesson fragments
is allowed only because the shared layout deterministically wraps it at runtime.

Optionally pass:
    --built-site /path/to/_site
and the checker also inspects the generated Pages HTML source. Browser/render
QA is still required separately; this checker does not pretend source safety is
visual proof.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSON_DIR = ROOT / "skills/learning-page-design-publisher/lessons"
REGISTRY = ROOT / "skills/learning-page-design-publisher/term-overrides.yml"
LAYOUT = ROOT / "docs/_layouts/lesson.html"

FORBIDDEN_MATH_CSS = re.compile(
    r"math(?:\[[^\]]*\])?\s*\{[^}]*\b(?:display\s*:\s*(?:block|flex|grid)|overflow(?:-x|-y)?\s*:)",
    re.I | re.S,
)
REGISTRY_SLUG = re.compile(r"(?m)^([a-z0-9][a-z0-9-]+):\n")


class MathTreeChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.block_math = 0
        self.wrapped = 0
        self.bare = 0

    def handle_starttag(self, tag: str, attrs):
        attr = dict(attrs)
        cls = set((attr.get("class") or "").split())
        if tag.lower() == "math" and attr.get("display", "").lower() == "block":
            self.block_math += 1
            has_wrapper = any("formula-scroll" in classes for _, classes in self.stack)
            if has_wrapper:
                self.wrapped += 1
            else:
                self.bare += 1
        self.stack.append((tag.lower(), cls))

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


def parse_math(text: str) -> MathTreeChecker:
    parser = MathTreeChecker()
    parser.feed(text)
    return parser


def built_site_arg() -> pathlib.Path | None:
    if "--built-site" not in sys.argv:
        return None
    i = sys.argv.index("--built-site")
    if i + 1 >= len(sys.argv):
        raise SystemExit("--built-site requires a path")
    return pathlib.Path(sys.argv[i + 1]).resolve()


def main() -> int:
    failures: list[str] = []
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.is_file() else ""
    overridden = registry_slugs(registry_text)

    layout = LAYOUT.read_text(encoding="utf-8") if LAYOUT.is_file() else ""
    wrapper_fallback = (
        "querySelectorAll('math[display=\"block\"]')" in layout
        and "formula-scroll" in layout
    )

    print("effective canonical lesson fragments")
    total_math = total_bare = 0
    for path in sorted(LESSON_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = path.stem
        before = len(failures)
        block_math = bare_math = 0

        for key, value in data.items():
            if not isinstance(value, str):
                continue
            # With a term pack, Jekyll renders term_pack.html instead of
            # lesson['TERMS_HTML']; inspect the effective source, not dead fallback.
            if key == "TERMS_HTML" and slug in overridden:
                continue
            if FORBIDDEN_MATH_CSS.search(value):
                failures.append(f"{path.name}:{key}: CSS overrides MathML root layout/overflow")
            if "<math" in value:
                try:
                    parser = parse_math(value)
                except Exception as exc:
                    failures.append(f"{path.name}:{key}: HTML parser failed: {exc}")
                    continue
                block_math += parser.block_math
                bare_math += parser.bare

        total_math += block_math
        total_bare += bare_math
        if bare_math and not wrapper_fallback:
            failures.append(
                f"{path.name}: {bare_math} bare block MathML formula(s) require shared layout wrapper fallback"
            )
        mode = "layout-wrap" if bare_math else "source-wrap"
        print(
            f"  {'PASS' if len(failures)==before else 'FAIL'} {path.name}: "
            f"block-math={block_math}, bare={bare_math}, mode={mode if block_math else 'n/a'}"
        )

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
            before = len(failures)
            if FORBIDDEN_MATH_CSS.search(text):
                failures.append(f"{page.relative_to(built)}: generated HTML contains forbidden MathML-root CSS")
            parser = parse_math(text)
            if parser.bare and not wrapper_fallback:
                failures.append(f"{page.relative_to(built)}: bare block MathML has no runtime wrapper fallback")
            print(
                f"  {'PASS' if len(failures)==before else 'FAIL'} {page.name}: "
                f"block-math={parser.block_math}, bare-before-js={parser.bare}"
            )

    print(f"\nblock MathML checked: {total_math}; legacy bare formulas delegated to layout: {total_bare}")
    print("NOTE: hash/blob equality proves artifact identity only; visual correctness still requires browser render QA.")
    if failures:
        print(f"MATH SAFETY FAIL: {len(failures)} problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("MATH SAFETY PASS: MathML roots retain native layout; overflow belongs to outer wrappers.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
