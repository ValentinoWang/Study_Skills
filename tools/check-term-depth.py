#!/usr/bin/env python3
"""Check that terminology-primer cards contain real explanations.

Baseline rule: every collapsed card exposes a one-line gloss and at least one
structured explanatory dimension.

Selected system lessons also carry a richer teaching contract: every core term
must contain intuition, a stricter definition, a current-case mapping and a
boundary.  This prevents a glossary that is technically present but still too
thin to support reasoning for a cross-disciplinary learner.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "skills/learning-page-design-publisher/term-overrides.yml"
ALLOWED_LABELS = {
    "直觉", "一句话直觉", "严格一点", "严格定义", "当前案例", "本案作用",
    "边界", "比喻", "比喻的边界", "怎么观察",
}

RICH_LESSONS = {
    "software-delivery-lifecycle-ai-coding-20260910": {
        "required_labels": {"直觉", "严格定义", "当前案例", "边界"},
        "min_cards": 14,
        "min_plain_chars": 3600,
    },
    "tencent-cloud-dns-icp-mainland-origin-20260831": {
        "required_labels": {"直觉", "严格定义", "当前案例", "边界"},
        "min_cards": 12,
        "min_plain_chars": 3600,
    },
}


def plain(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def registry_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^([a-z0-9][a-z0-9-]+):\n", text))
    out: dict[str, str] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[match.group(1)] = text[match.start():end]
    return out


def main() -> int:
    if not REGISTRY.is_file():
        raise SystemExit(f"missing terminology registry: {REGISTRY}")

    text = REGISTRY.read_text(encoding="utf-8")
    sections = registry_sections(text)
    failures: list[str] = []
    total_cards = 0

    print(f"registry: {REGISTRY.relative_to(ROOT)}")

    for slug, section in sections.items():
        cards = re.findall(r"<details>(.*?)</details>", section, re.S)
        total_cards += len(cards)
        rich = RICH_LESSONS.get(slug)
        print(f"\n{slug}: cards={len(cards)}" + (" [rich]" if rich else ""))

        if rich:
            visible = plain(section)
            if len(cards) < rich["min_cards"]:
                failures.append(f"{slug}: cards={len(cards)} < {rich['min_cards']}")
            if len(visible) < rich["min_plain_chars"]:
                failures.append(
                    f"{slug}: visible term text={len(visible)} < {rich['min_plain_chars']} chars"
                )

        for i, block in enumerate(cards, 1):
            summary_m = re.search(r"<summary>(.*?)</summary>", block, re.S)
            gloss_m = re.search(r'<span class="term-gloss">(.*?)</span>', block, re.S)
            dts = [plain(x) for x in re.findall(r"<dt>(.*?)</dt>", block, re.S)]
            dds = [plain(x) for x in re.findall(r"<dd>(.*?)</dd>", block, re.S)]
            name = plain(summary_m.group(1)) if summary_m else f"card #{i}"
            gloss = plain(gloss_m.group(1)) if gloss_m else ""
            reasons: list[str] = []

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

            if rich:
                missing_labels = sorted(rich["required_labels"] - set(dts))
                if missing_labels:
                    reasons.append("rich lesson missing dimensions: " + ", ".join(missing_labels))
                if len(plain(block)) < 170:
                    reasons.append("rich lesson card is still too short (<170 visible chars)")

            print(f"  {'THIN' if reasons else 'OK  '} {name[:72]}")
            if reasons:
                failures.append(f"{slug} / {name}: {'; '.join(reasons)}")

    if total_cards == 0:
        failures.append("no terminology cards found")

    print()
    if failures:
        print(f"FAIL: {len(failures)} terminology depth problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS: terminology primers meet baseline depth; rich lessons meet the four-dimension contract.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
