#!/usr/bin/env python3
"""Synchronize canonical learning sources into GitHub Pages inputs.

Default lessons use the shared ``lesson`` layout. Per-lesson exceptions are
explicitly declared in ``skills/learning-page-design-publisher/lesson-manifest.json``.

The manifest also declares:
- canonical supplemental chapter sources and Pages include mirrors;
- canonical teaching-figure sources and public SVG mirrors.

A normal rebuild must not silently collapse a long-form course, drop supplemental
chapters, or publish a figure different from the canonical source.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
SOURCE_DIR = PAGE_SKILL / "lessons"
TERM_SOURCE = PAGE_SKILL / "term-overrides.yml"
MANIFEST = PAGE_SKILL / "lesson-manifest.json"
PAGES_DATA_DIR = ROOT / "docs/_data/lessons"
PAGES_TERM_DATA = ROOT / "docs/_data/term_overrides.yml"
PAGES_LESSON_DIR = ROOT / "docs/lessons"
LAYOUT_DIR = ROOT / "docs/_layouts"
NOJEKYLL = ROOT / "docs/.nojekyll"
EXEMPT_PAGES = {"welcome.html"}


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("lesson-manifest.json must contain an object")
    return data


def config_for(manifest: dict[str, dict], slug: str) -> dict:
    cfg = manifest.get(slug, {})
    if not isinstance(cfg, dict):
        raise SystemExit(f"manifest entry must be an object: {slug}")
    return cfg


def layout_for(manifest: dict[str, dict], slug: str) -> str:
    return str(config_for(manifest, slug).get("layout", "lesson"))


def wrapper(manifest: dict[str, dict], slug: str) -> str:
    return f"---\nlayout: {layout_for(manifest, slug)}\nlesson: {slug}\n---\n"


def sync_bytes(expected: bytes, dst: pathlib.Path, check_only: bool) -> bool:
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


def sync_file(src: pathlib.Path, dst: pathlib.Path, check_only: bool) -> bool:
    return sync_bytes(src.read_bytes(), dst, check_only)


def sync_text(expected: str, dst: pathlib.Path, check_only: bool) -> bool:
    return sync_bytes(expected.encode("utf-8"), dst, check_only)


def mirror_supplements(manifest: dict[str, dict], check_only: bool) -> bool:
    ok = True
    print("\nlesson supplemental mirrors")
    for slug, cfg in sorted(manifest.items()):
        src_rel = cfg.get("supplement_source_dir")
        dst_rel = cfg.get("supplement_pages_dir")
        if bool(src_rel) != bool(dst_rel):
            print(f"  FAIL {slug}: both supplement_source_dir and supplement_pages_dir are required")
            ok = False
            continue
        if not src_rel:
            continue
        src_dir = ROOT / str(src_rel)
        dst_dir = ROOT / str(dst_rel)
        if not src_dir.is_dir():
            print(f"  FAIL {slug}: missing {src_dir.relative_to(ROOT)}")
            ok = False
            continue
        source_files = sorted(p for p in src_dir.rglob("*") if p.is_file())
        source_rel = {p.relative_to(src_dir) for p in source_files}
        for src in source_files:
            ok &= sync_file(src, dst_dir / src.relative_to(src_dir), check_only)
        if dst_dir.is_dir():
            for dst in sorted(p for p in dst_dir.rglob("*") if p.is_file()):
                rel = dst.relative_to(dst_dir)
                if rel in source_rel:
                    continue
                if check_only:
                    print(f"  ORPHAN   {dst.relative_to(ROOT)}")
                    ok = False
                else:
                    dst.unlink()
                    print(f"  removed  {dst.relative_to(ROOT)}")
    return ok


def mirror_figures(manifest: dict[str, dict], check_only: bool) -> bool:
    ok = True
    print("\nteaching figure mirrors")
    seen_public: set[pathlib.Path] = set()
    for slug, cfg in sorted(manifest.items()):
        figures = cfg.get("figures", [])
        if not figures:
            continue
        if not isinstance(figures, list):
            print(f"  FAIL {slug}: figures must be a list")
            ok = False
            continue
        for spec in figures:
            if not isinstance(spec, dict):
                print(f"  FAIL {slug}: figure spec must be an object")
                ok = False
                continue
            figure_id = str(spec.get("id", "<missing-id>"))
            source_rel = spec.get("source")
            public_rel = spec.get("public_path")
            if not source_rel or not public_rel:
                print(f"  FAIL {slug}/{figure_id}: source and public_path are required")
                ok = False
                continue
            src = ROOT / str(source_rel)
            dst = ROOT / str(public_rel)
            if not src.is_file():
                print(f"  FAIL {slug}/{figure_id}: missing {src.relative_to(ROOT)}")
                ok = False
                continue
            if dst in seen_public:
                print(f"  FAIL {slug}/{figure_id}: duplicate public_path {dst.relative_to(ROOT)}")
                ok = False
                continue
            seen_public.add(dst)
            ok &= sync_file(src, dst, check_only)
    return ok


def main() -> int:
    check_only = "--check" in sys.argv
    manifest = load_manifest()
    sources = sorted(SOURCE_DIR.glob("*.json"))
    if not sources:
        raise SystemExit(f"没有课程数据：{SOURCE_DIR}")
    if not TERM_SOURCE.is_file():
        raise SystemExit(f"缺少术语首现注册表：{TERM_SOURCE}")

    ok = True
    source_slugs = {p.stem for p in sources}
    unknown = sorted(set(manifest) - source_slugs)
    if unknown:
        print("manifest entries without canonical lesson:", ", ".join(unknown))
        ok = False

    print("lesson data mirrors")
    for src in sources:
        ok &= sync_file(src, PAGES_DATA_DIR / src.name, check_only)

    print("\nterminology registry mirror")
    ok &= sync_file(TERM_SOURCE, PAGES_TERM_DATA, check_only)

    ok &= mirror_supplements(manifest, check_only)
    ok &= mirror_figures(manifest, check_only)

    print("\nlesson entry files")
    for slug in sorted(source_slugs):
        layout = layout_for(manifest, slug)
        layout_file = LAYOUT_DIR / f"{layout}.html"
        if not layout_file.is_file():
            print(f"  FAIL {slug}: missing layout {layout_file.relative_to(ROOT)}")
            ok = False
        ok &= sync_text(wrapper(manifest, slug), PAGES_LESSON_DIR / f"{slug}.html", check_only)

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
        print("\nFAIL: Pages 数据、补充章节、教学图或入口与 canonical sources 不一致。")
        return 1
    print("\nOK: lesson data, supplements, figures, terminology registry and Pages entries are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
