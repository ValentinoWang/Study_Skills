#!/usr/bin/env python3
"""Build/sync the terminology-first GitHub Pages lesson sources.

Canonical content lives in:
  skills/learning-page-design-publisher/lessons/*.json
  skills/learning-page-design-publisher/term-overrides.yml

GitHub Pages consumes mirrored data under docs/_data and renders every lesson
through docs/_layouts/lesson.html. docs/lessons/*.html are intentionally tiny
Jekyll entry files so one shared layout can enforce "terms before reasoning"
for every lesson.

Usage:
    python3 tools/build-lessons.py
    python3 tools/build-lessons.py --check
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
SOURCE_DIR = PAGE_SKILL / "lessons"
TERM_SOURCE = PAGE_SKILL / "term-overrides.yml"
PAGES_DATA_DIR = ROOT / "docs/_data/lessons"
PAGES_TERM_DATA = ROOT / "docs/_data/term_overrides.yml"
PAGES_LESSON_DIR = ROOT / "docs/lessons"
LAYOUT = ROOT / "docs/_layouts/lesson.html"
NOJEKYLL = ROOT / "docs/.nojekyll"
EXEMPT_PAGES = {"welcome.html"}


def wrapper(slug: str) -> str:
    return f"---\nlayout: lesson\nlesson: {slug}\n---\n"


def sync_file(src: pathlib.Path, dst: pathlib.Path, check_only: bool) -> bool:
    expected = src.read_bytes()
    current = dst.read_bytes() if dst.exists() else None
    if current == expected:
        print(f"  same     {dst.relative_to(ROOT)}")
        return True
    if check_only:
        print(f"  STALE    {dst.relative_to(ROOT)}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(expected)
    print(f"  written  {dst.relative_to(ROOT)}")
    return True


def sync_text(expected: str, dst: pathlib.Path, check_only: bool) -> bool:
    current = dst.read_text(encoding="utf-8") if dst.exists() else None
    if current == expected:
        print(f"  same     {dst.relative_to(ROOT)}")
        return True
    if check_only:
        print(f"  STALE    {dst.relative_to(ROOT)}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(expected, encoding="utf-8")
    print(f"  written  {dst.relative_to(ROOT)}")
    return True


def main() -> int:
    check_only = "--check" in sys.argv
    sources = sorted(SOURCE_DIR.glob("*.json"))
    if not sources:
        raise SystemExit(f"没有课程数据：{SOURCE_DIR}")
    if not TERM_SOURCE.is_file():
        raise SystemExit(f"缺少术语首现注册表：{TERM_SOURCE}")
    if not LAYOUT.is_file():
        raise SystemExit(f"缺少 Pages lesson layout：{LAYOUT}")

    ok = True

    print("lesson data mirrors")
    for src in sources:
        ok &= sync_file(src, PAGES_DATA_DIR / src.name, check_only)

    print("\nterminology registry mirror")
    ok &= sync_file(TERM_SOURCE, PAGES_TERM_DATA, check_only)

    print("\nlesson entry files")
    source_slugs = {p.stem for p in sources}
    for slug in sorted(source_slugs):
        ok &= sync_text(wrapper(slug), PAGES_LESSON_DIR / f"{slug}.html", check_only)

    if PAGES_LESSON_DIR.is_dir():
        for page in sorted(PAGES_LESSON_DIR.glob("*.html")):
            if page.name in EXEMPT_PAGES:
                continue
            if page.stem not in source_slugs:
                if check_only:
                    print(f"  ORPHAN   {page.relative_to(ROOT)}")
                    ok = False
                else:
                    page.unlink()
                    print(f"  removed  {page.relative_to(ROOT)}")

    if NOJEKYLL.exists():
        if check_only:
            print(f"\nFAIL: {NOJEKYLL.relative_to(ROOT)} 会禁用 Jekyll，必须删除。")
            ok = False
        else:
            NOJEKYLL.unlink()
            print(f"\nremoved  {NOJEKYLL.relative_to(ROOT)}")

    if not ok:
        print("\nFAIL: Pages 数据/入口与 canonical lesson sources 不一致。")
        return 1
    print("\nOK: lesson data, terminology registry and Pages entry files are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
