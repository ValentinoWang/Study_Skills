#!/usr/bin/env python3
"""Check that terminology-primer cards contain real explanations.

The current published architecture stores the first-use terminology layer in
skills/learning-page-design-publisher/term-overrides.yml.  Every collapsed card
must expose a one-line gloss, and opening it must reveal at least one additional
structured explanatory dimension (intuition, strict meaning, case role or boundary).
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "skills/learning-page-design-publisher/term-overrides.yml"
ALLOWED_LABELS = {"直觉", "一句话直觉", "严格一点", "严格定义", "当前案例", "本案作用", "边界", "比喻", "比喻的边界"}


def plain(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def main() -> int:
    if not REGISTRY.is_file():
        raise SystemExit(f"missing terminology registry: {REGISTRY}")

    text = REGISTRY.read_text(encoding="utf-8")
    cards = re.findall(r"<details>(.*?)</details>", text, re.S)
    failures: list[str] = []

    print(f"registry: {REGISTRY.relative_to(ROOT)}")
    print(f"term cards: {len(cards)}")

    for i, block in enumerate(cards, 1):
        summary_m = re.search(r"<summary>(.*?)</summary>", block, re.S)
        gloss_m = re.search(r'<span class="term-gloss">(.*?)</span>', block, re.S)
        dts = [plain(x) for x in re.findall(r"<dt>(.*?)</dt>", block, re.S)]
        dds = [plain(x) for x in re.findall(r"<dd>(.*?)</dd>", block, re.S)]
        name = plain(summary_m.group(1)) if summary_m else f"card #{i}"
        gloss = plain(gloss_m.group(1)) if gloss_m else ""

        reasons = []
        if not summary_m:
            reasons.append("missing summary")
        if len(gloss) < 8:
            reasons.append("collapsed one-line gloss is missing/thin")
        if "<dl>" not in block or not dds:
            reasons.append("expanded card lacks structured <dl>/<dd> explanation")
        if not any(label in ALLOWED_LABELS for label in dts):
            reasons.append("expanded card lacks a recognized explanatory dimension")
        if dds and all(len(x) < 6 for x in dds):
            reasons.append("expanded explanations are too thin")

        print(f"  {'THIN' if reasons else 'OK  '} {name[:70]}")
        if reasons:
            failures.append(f"{name}: {'; '.join(reasons)}")

    if not cards:
        failures.append("no terminology cards found")

    print()
    if failures:
        print(f"FAIL: {len(failures)} terminology card problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS: all terminology cards expose an immediate gloss plus structured depth.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
