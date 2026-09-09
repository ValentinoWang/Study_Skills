#!/usr/bin/env python3
"""Validate the terminology-first gate used by current GitHub Pages lessons.

Default checks operate on repository sources. Optionally pass:
    --built-site /path/to/_site
and the checker also validates the actual rendered Pages HTML.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
LESSON_DIR = PAGE_SKILL / "lessons"
REGISTRY = PAGE_SKILL / "term-overrides.yml"
LAYOUT = ROOT / "docs/_layouts/lesson.html"
ENTRY_DIR = ROOT / "docs/lessons"

REQUIRED = {
    "frontend-fast-feedback-pipeline-20260910": [
        "Runtime", "Vite Development Server", "Hot Module Replacement", "Hot Reload",
        "Incremental Compilation", "Mock API", "API Proxy", "Target Runtime",
        "Production Build", "Docker Build", "End-to-End Testing", "Deployment Readback",
    ],
    "software-delivery-lifecycle-ai-coding-20260910": [
        "AI Agent", "Software Delivery Lifecycle", "Feedback Loop", "Hot Module Replacement",
        "Smoke Test", "Quality Assurance", "End-to-End Testing", "Acceptance",
        "User Acceptance Testing", "Continuous Integration", "Continuous Delivery",
        "Artifact", "Observability",
    ],
    "git-three-state-divergence-20260831": [
        "Commit / SHA", "Branch", "HEAD", "git fetch", "origin/main", "git checkout",
        "Working Tree", "Git worktree", "ahead / behind", "Fast-forward Merge", "Merge Conflict",
    ],
    "tencent-cloud-dns-icp-mainland-origin-20260831": [
        "Domain Name System", "Application Programming Interface", "Cloud Virtual Machine",
        "Domain Real-name Verification", "Internet Content Provider", "Transport Layer Security",
        "Reverse Proxy", "Cross-Origin Resource Sharing",
    ],
}


def registry_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^([a-z0-9][a-z0-9-]+):\n", text))
    result: dict[str, str] = {}
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result[match.group(1)] = text[start:end]
    return result


def wrapper(slug: str) -> str:
    return f"---\nlayout: lesson\nlesson: {slug}\n---\n"


def built_site_from_args() -> pathlib.Path | None:
    if "--built-site" not in sys.argv:
        return None
    i = sys.argv.index("--built-site")
    if i + 1 >= len(sys.argv):
        raise SystemExit("--built-site requires a path")
    return pathlib.Path(sys.argv[i + 1]).resolve()


def main() -> int:
    failures: list[str] = []
    if not REGISTRY.is_file():
        raise SystemExit(f"missing registry: {REGISTRY}")
    if not LAYOUT.is_file():
        raise SystemExit(f"missing layout: {LAYOUT}")

    source_slugs = {p.stem for p in LESSON_DIR.glob("*.json")}
    text = REGISTRY.read_text(encoding="utf-8")
    sections = registry_sections(text)

    layout = LAYOUT.read_text(encoding="utf-8")
    p_terms = layout.find('id="terms"')
    p_orient = layout.find('id="orient"')
    if p_terms < 0 or p_orient < 0 or p_terms >= p_orient:
        failures.append("layout does not put terminology before orientation")
    if "site.data.term_overrides[page.lesson]" not in layout:
        failures.append("layout does not consume the terminology registry")
    if "term-gloss" not in layout:
        failures.append("layout lacks collapsed term-gloss support")

    print("registry coverage")
    for slug in sorted(source_slugs):
        block = sections.get(slug, "")
        if not block:
            failures.append(f"{slug}: no terminology registry section")
            print(f"  FAIL {slug}: missing section")
            continue
        lower = block.lower()
        missing = [term for term in REQUIRED.get(slug, []) if term.lower() not in lower]
        details = block.count("<details>")
        glosses = block.count('class="term-gloss"')
        ok = "先认词" in block and not missing and details > 0 and glosses == details
        print(f"  {'OK  ' if ok else 'FAIL'} {slug}: cards={details}, glosses={glosses}, missing={missing}")
        if "先认词" not in block:
            failures.append(f"{slug}: no visible '先认词' primer")
        if missing:
            failures.append(f"{slug}: missing required terms: {', '.join(missing)}")
        if details == 0 or glosses != details:
            failures.append(f"{slug}: every collapsed term card must expose exactly one term-gloss")

        entry = ENTRY_DIR / f"{slug}.html"
        if not entry.is_file() or entry.read_text(encoding="utf-8") != wrapper(slug):
            failures.append(f"{slug}: published entry is not the deterministic lesson wrapper")

    extra = sorted(set(sections) - source_slugs)
    if extra:
        failures.append(f"registry has orphan lesson sections: {', '.join(extra)}")

    built = built_site_from_args()
    if built is not None:
        print("\nrendered Pages artifact")
        for slug in sorted(source_slugs):
            page = built / "lessons" / f"{slug}.html"
            if not page.is_file():
                failures.append(f"{slug}: missing rendered page in {built}")
                continue
            html = page.read_text(encoding="utf-8")
            a, b = html.find('id="terms"'), html.find('id="orient"')
            term_html = html[a:b] if a >= 0 and b > a else ""
            missing = [term for term in REQUIRED.get(slug, []) if term.lower() not in term_html.lower()]
            details = term_html.count("<details>")
            glosses = term_html.count('class="term-gloss"')
            ok = a >= 0 and b > a and not missing and details > 0 and glosses >= details
            print(f"  {'PASS' if ok else 'FAIL'} {slug}: terms_pos={a}, orient_pos={b}, cards={details}, glosses={glosses}")
            if not ok:
                failures.append(f"{slug}: rendered Pages term gate failed; missing={missing}")

    print()
    if failures:
        print(f"TERM GATE FAIL: {len(failures)} problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("TERM GATE PASS: terminology is visible before reasoning for all canonical lessons.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
