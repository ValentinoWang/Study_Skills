#!/usr/bin/env python3
"""Apply/check the terminology-first backwash for every canonical lesson.

The migration is now data-driven: term-overrides.yml is the shared first-use
terminology layer, while lesson JSON keeps the original case/content material.
This command verifies every lesson has a terminology pack and then delegates
all deterministic Pages mirroring/wrapper generation to build-lessons.py.

Usage:
    python3 tools/backwash-term-gates.py
    python3 tools/backwash-term-gates.py --check
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
LESSON_DIR = PAGE_SKILL / "lessons"
REGISTRY = PAGE_SKILL / "term-overrides.yml"
BUILD = ROOT / "tools/build-lessons.py"


def registry_slugs(text: str) -> set[str]:
    return set(re.findall(r"(?m)^([a-z0-9][a-z0-9-]+):\n", text))


def main() -> int:
    check_only = "--check" in sys.argv
    if not REGISTRY.is_file():
        raise SystemExit(f"missing terminology registry: {REGISTRY}")

    source_slugs = {p.stem for p in LESSON_DIR.glob("*.json")}
    registered = registry_slugs(REGISTRY.read_text(encoding="utf-8"))
    missing = sorted(source_slugs - registered)
    orphan = sorted(registered - source_slugs)

    if missing:
        print("FAIL: lessons without terminology primer:")
        for slug in missing:
            print(f"  - {slug}")
        return 1
    if orphan:
        print("FAIL: orphan terminology packs without canonical lesson source:")
        for slug in orphan:
            print(f"  - {slug}")
        return 1

    print(f"terminology packs cover all {len(source_slugs)} canonical lesson(s)")
    cmd = [sys.executable, str(BUILD)]
    if check_only:
        cmd.append("--check")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
