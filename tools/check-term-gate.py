#!/usr/bin/env python3
"""Check that learning pages establish core terminology before main reasoning."""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
TEMPLATE = PAGE_SKILL / "assets/lesson-template.html"
LESSON_DIR = PAGE_SKILL / "lessons"

REQUIRED = {
    "frontend-fast-feedback-pipeline-20260910": [
        "Runtime",
        "Hot Module Replacement",
        "Hot Reload",
        "Incremental Compilation",
        "Mock API",
        "API Proxy",
        "Target Runtime",
        "Production Build",
        "Docker Build",
        "End-to-End Testing",
        "Readback",
    ],
    "software-delivery-lifecycle-ai-coding-20260910": [
        "AI Agent",
        "Hot Module Replacement",
        "Smoke Test",
        "Software Delivery Lifecycle",
        "Feedback Loop",
        "Quality Assurance",
        "Acceptance",
        "Continuous Integration",
        "Continuous Delivery",
        "Artifact",
        "Observability",
    ],
    "git-three-state-divergence-20260831": [
        "git checkout",
        "git fetch",
        "Git worktree",
        "Fast-forward",
        "Commit",
        "HEAD",
        "origin/main",
        "Working tree",
        "ahead / behind",
        "merge conflict",
    ],
    "tencent-cloud-dns-icp-mainland-origin-20260831": [
        "Domain Name System",
        "Application Programming Interface",
        "Cloud Virtual Machine",
        "ICP",
        "Transport Layer Security",
        "Cross-Origin Resource Sharing",
    ],
}


def clean(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").strip()


def summaries(html: str) -> list[str]:
    return [clean(x) for x in re.findall(r"<summary>(.*?)</summary>", html, re.S)]


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)
    print(f"FAIL {msg}")


def main() -> int:
    failures: list[str] = []
    template = TEMPLATE.read_text(encoding="utf-8")

    p_terms = template.find("{{TERMS_HTML}}")
    p_orient = template.find("{{ORIENTATION_HTML}}")
    if p_terms < 0 or p_orient < 0 or p_terms >= p_orient:
        fail("canonical template must render TERMS_HTML before ORIENTATION_HTML", failures)
    else:
        print("OK   canonical template: terminology appears before orientation")

    if "term-gloss" not in template or "querySelectorAll('#terms details')" not in template:
        fail("canonical template must expose first-dd term gloss while details are collapsed", failures)
    else:
        print("OK   canonical template: collapsed term cards expose a one-line gloss")

    for path in sorted(LESSON_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        lid = data.get("LESSON_ID", path.stem)
        terms = data.get("TERMS_HTML", "")
        ss = summaries(terms)
        joined = "\n".join(ss).lower()
        print(f"\n{lid}")

        if "先认词" not in clean(terms)[:220]:
            fail(f"{lid}: TERMS_HTML lacks a visible terminology-primer intro", failures)
        else:
            print("OK   primer intro")

        detail_blocks = re.findall(r"<details>(.*?)</details>", terms, re.S)
        if not detail_blocks:
            fail(f"{lid}: no terminology details", failures)
        for i, block in enumerate(detail_blocks, 1):
            summary = re.search(r"<summary>(.*?)</summary>", block, re.S)
            first_dd = re.search(r"<dd>(.*?)</dd>", block, re.S)
            if not summary or not first_dd or not clean(first_dd.group(1)):
                fail(f"{lid}: term card #{i} lacks summary or first intuitive definition", failures)

        missing = [term for term in REQUIRED.get(lid, []) if term.lower() not in joined]
        if missing:
            fail(f"{lid}: missing core term cards: {', '.join(missing)}", failures)
        else:
            print(f"OK   required core terms covered ({len(REQUIRED.get(lid, []))})")

    print()
    if failures:
        print(f"TERM GATE FAIL: {len(failures)} problem(s)")
        return 1
    print("TERM GATE PASS: terminology is introduced before main reasoning and core lesson vocab is covered.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
