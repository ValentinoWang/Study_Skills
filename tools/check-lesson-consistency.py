#!/usr/bin/env python3
"""Check the current terminology-first GitHub Pages lesson architecture.

The published page is no longer a hand-written/static copy of lesson-template.html.
Consistency now means:
  1. canonical lesson JSON == docs/_data/lessons mirror;
  2. canonical term registry == docs/_data/term_overrides.yml;
  3. each docs/lessons page is the deterministic Jekyll wrapper for its slug;
  4. the shared layout renders terminology before the main orientation;
  5. docs/.nojekyll is absent so Pages can run Jekyll.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
SOURCE_DIR = PAGE_SKILL / "lessons"
TERM_SOURCE = PAGE_SKILL / "term-overrides.yml"
DATA_DIR = ROOT / "docs/_data/lessons"
TERM_DATA = ROOT / "docs/_data/term_overrides.yml"
ENTRY_DIR = ROOT / "docs/lessons"
LAYOUT = ROOT / "docs/_layouts/lesson.html"
NOJEKYLL = ROOT / "docs/.nojekyll"
EXEMPT = {"welcome.html"}


def wrapper(slug: str) -> str:
    return f"---\nlayout: lesson\nlesson: {slug}\n---\n"


def main() -> int:
    failures: list[str] = []
    sources = sorted(SOURCE_DIR.glob("*.json"))
    slugs = {p.stem for p in sources}

    print("canonical lesson data mirrors")
    for src in sources:
        dst = DATA_DIR / src.name
        ok = dst.is_file() and src.read_bytes() == dst.read_bytes()
        print(f"  {'OK  ' if ok else 'DRIFT'} {src.name}")
        if not ok:
            failures.append(f"data mirror mismatch: {dst.relative_to(ROOT)}")

    if not TERM_SOURCE.is_file() or not TERM_DATA.is_file() or TERM_SOURCE.read_bytes() != TERM_DATA.read_bytes():
        failures.append("terminology registry mirror mismatch")
        print("  DRIFT terminology registry")
    else:
        print("  OK   terminology registry")

    print("\nJekyll lesson entry files")
    for slug in sorted(slugs):
        page = ENTRY_DIR / f"{slug}.html"
        expected = wrapper(slug)
        ok = page.is_file() and page.read_text(encoding="utf-8") == expected
        print(f"  {'OK  ' if ok else 'DRIFT'} {page.relative_to(ROOT)}")
        if not ok:
            failures.append(f"entry wrapper mismatch: {page.relative_to(ROOT)}")

    if ENTRY_DIR.is_dir():
        for page in sorted(ENTRY_DIR.glob("*.html")):
            if page.name in EXEMPT:
                continue
            if page.stem not in slugs:
                failures.append(f"orphan lesson entry: {page.relative_to(ROOT)}")

    print("\nshared Pages layout")
    if not LAYOUT.is_file():
        failures.append("missing docs/_layouts/lesson.html")
    else:
        text = LAYOUT.read_text(encoding="utf-8")
        terms_pos = text.find('id="terms"')
        orient_pos = text.find('id="orient"')
        checks = {
            "uses lesson data": "site.data.lessons[page.lesson]" in text,
            "uses terminology registry": "site.data.term_overrides[page.lesson]" in text,
            "terms before orientation": terms_pos >= 0 and orient_pos >= 0 and terms_pos < orient_pos,
            "collapsed gloss support": "term-gloss" in text,
        }
        for label, ok in checks.items():
            print(f"  {'OK  ' if ok else 'FAIL'} {label}")
            if not ok:
                failures.append(f"layout check failed: {label}")

    if NOJEKYLL.exists():
        failures.append("docs/.nojekyll exists and disables the Jekyll lesson layout")

    print()
    if failures:
        print(f"FAIL: {len(failures)} consistency problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS: canonical lesson data, terminology registry, wrappers and Pages layout are consistent.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
