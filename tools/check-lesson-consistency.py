#!/usr/bin/env python3
"""Check canonical lesson, layout, wrapper and supplemental-source consistency."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
SOURCE_DIR = PAGE_SKILL / "lessons"
TERM_SOURCE = PAGE_SKILL / "term-overrides.yml"
MANIFEST = PAGE_SKILL / "lesson-manifest.json"
DATA_DIR = ROOT / "docs/_data/lessons"
TERM_DATA = ROOT / "docs/_data/term_overrides.yml"
ENTRY_DIR = ROOT / "docs/lessons"
LAYOUT_DIR = ROOT / "docs/_layouts"
NOJEKYLL = ROOT / "docs/.nojekyll"
EXEMPT = {"welcome.html"}


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("lesson-manifest.json must contain an object")
    return data


def layout_for(manifest: dict[str, dict], slug: str) -> str:
    return str(manifest.get(slug, {}).get("layout", "lesson"))


def wrapper(manifest: dict[str, dict], slug: str) -> str:
    return f"---\nlayout: {layout_for(manifest, slug)}\nlesson: {slug}\n---\n"


def compare_tree(src_dir: pathlib.Path, dst_dir: pathlib.Path) -> list[str]:
    failures: list[str] = []
    if not src_dir.is_dir():
        return [f"missing supplemental source dir: {src_dir.relative_to(ROOT)}"]
    if not dst_dir.is_dir():
        return [f"missing supplemental Pages dir: {dst_dir.relative_to(ROOT)}"]
    src = {p.relative_to(src_dir): p for p in src_dir.rglob("*") if p.is_file()}
    dst = {p.relative_to(dst_dir): p for p in dst_dir.rglob("*") if p.is_file()}
    for rel in sorted(set(src) | set(dst)):
        if rel not in src:
            failures.append(f"orphan supplemental Pages file: {(dst_dir / rel).relative_to(ROOT)}")
        elif rel not in dst:
            failures.append(f"missing supplemental mirror: {(dst_dir / rel).relative_to(ROOT)}")
        elif src[rel].read_bytes() != dst[rel].read_bytes():
            failures.append(f"supplemental mirror mismatch: {(dst_dir / rel).relative_to(ROOT)}")
    return failures


def main() -> int:
    failures: list[str] = []
    manifest = load_manifest()
    sources = sorted(SOURCE_DIR.glob("*.json"))
    slugs = {p.stem for p in sources}

    extra_manifest = sorted(set(manifest) - slugs)
    if extra_manifest:
        failures.append("manifest entries without canonical lesson: " + ", ".join(extra_manifest))

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

    print("\nJekyll lesson entry files and layouts")
    for slug in sorted(slugs):
        page = ENTRY_DIR / f"{slug}.html"
        expected = wrapper(manifest, slug)
        ok = page.is_file() and page.read_text(encoding="utf-8") == expected
        print(f"  {'OK  ' if ok else 'DRIFT'} {page.relative_to(ROOT)}")
        if not ok:
            failures.append(f"entry wrapper mismatch: {page.relative_to(ROOT)}")
        layout = LAYOUT_DIR / f"{layout_for(manifest, slug)}.html"
        if not layout.is_file():
            failures.append(f"missing configured layout: {layout.relative_to(ROOT)}")

    if ENTRY_DIR.is_dir():
        for page in sorted(ENTRY_DIR.glob("*.html")):
            if page.name in EXEMPT:
                continue
            if page.stem not in slugs:
                failures.append(f"orphan lesson entry: {page.relative_to(ROOT)}")

    print("\nlesson supplemental mirrors")
    for slug, cfg in sorted(manifest.items()):
        src_rel = cfg.get("supplement_source_dir")
        dst_rel = cfg.get("supplement_pages_dir")
        if bool(src_rel) != bool(dst_rel):
            failures.append(f"{slug}: supplement source/pages dirs must be declared together")
            continue
        if not src_rel:
            continue
        local = compare_tree(ROOT / str(src_rel), ROOT / str(dst_rel))
        print(f"  {'OK  ' if not local else 'DRIFT'} {slug}")
        failures.extend(f"{slug}: {x}" for x in local)

    print("\nlayout learning-order contracts")
    for layout_name in sorted({layout_for(manifest, slug) for slug in slugs}):
        layout = LAYOUT_DIR / f"{layout_name}.html"
        if not layout.is_file():
            continue
        text = layout.read_text(encoding="utf-8")
        checks = {
            "uses lesson data": "site.data.lessons[page.lesson]" in text,
            "has terms section": 'id="terms"' in text,
        }
        if layout_name == "lesson":
            a, b = text.find('id="terms"'), text.find('id="orient"')
            checks["terms before orientation"] = a >= 0 and b >= 0 and a < b
            checks["terminology fallback/registry"] = (
                "site.data.term_overrides[page.lesson]" in text or "lesson['TERMS_HTML']" in text
            )
        for label, ok in checks.items():
            print(f"  {'OK  ' if ok else 'FAIL'} {layout_name}: {label}")
            if not ok:
                failures.append(f"layout {layout_name} failed: {label}")

    if NOJEKYLL.exists():
        failures.append("docs/.nojekyll exists and disables Jekyll")

    print()
    if failures:
        print(f"FAIL: {len(failures)} consistency problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS: canonical data, supplemental chapters, wrappers and configured layouts are consistent.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
