#!/usr/bin/env python3
"""Synchronize lessons, v2 SVG figures, and Pages-native flow figures.

Layouts, supplements and figures share lesson-manifest.json. A rebuild must not
regress wrappers, move figures through client-side JavaScript, or leave a
canonical page-flow model unmirrored into Jekyll data.
"""
from __future__ import annotations
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL=ROOT/'skills/learning-page-design-publisher'
SOURCE_DIR=PAGE_SKILL/'lessons'
TERM_SOURCE=PAGE_SKILL/'term-overrides.yml'
MANIFEST=PAGE_SKILL/'lesson-manifest.json'
PAGES_DATA_DIR=ROOT/'docs/_data/lessons'
PAGES_TERM_DATA=ROOT/'docs/_data/term_overrides.yml'
PAGES_LESSON_DIR=ROOT/'docs/lessons'
LAYOUT_DIR=ROOT/'docs/_layouts'
NOJEKYLL=ROOT/'docs/.nojekyll'
EXEMPT_PAGES={'welcome.html'}

def load_manifest():
    if not MANIFEST.exists():return {}
    data=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if not isinstance(data,dict):raise SystemExit('lesson-manifest.json must contain an object')
    return data

def config_for(manifest,slug):
    cfg=manifest.get(slug,{})
    if not isinstance(cfg,dict):raise SystemExit(f'manifest entry must be an object: {slug}')
    return cfg

def layout_for(manifest,slug):return str(config_for(manifest,slug).get('layout','lesson'))

def wrapper(manifest,slug):return f'---\nlayout: {layout_for(manifest,slug)}\nlesson: {slug}\n---\n'

def sync_bytes(expected,dst,check_only):
    current=dst.read_bytes() if dst.exists() else None
    if current==expected:print(f'  same     {dst.relative_to(ROOT)}');return True
    if check_only:print(f'  STALE    {dst.relative_to(ROOT)}');return False
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(expected)
    print(f'  written  {dst.relative_to(ROOT)}');return True

def sync_file(src,dst,check_only):return sync_bytes(src.read_bytes(),dst,check_only)

def sync_text(expected,dst,check_only):return sync_bytes(expected.encode('utf-8'),dst,check_only)

def mirror_supplements(manifest,check_only):
    ok=True
    print('\nlesson supplemental mirrors')
    for slug,cfg in sorted(manifest.items()):
        src_rel,dst_rel=cfg.get('supplement_source_dir'),cfg.get('supplement_pages_dir')
        if bool(src_rel)!=bool(dst_rel):
            print(f'  FAIL {slug}: both supplement source/pages directories required');ok=False;continue
        if not src_rel:continue
        src_dir,dst_dir=ROOT/str(src_rel),ROOT/str(dst_rel)
        if not src_dir.is_dir():print(f'  FAIL {slug}: missing {src_rel}');ok=False;continue
        sources=sorted(p for p in src_dir.rglob('*') if p.is_file())
        rels={p.relative_to(src_dir) for p in sources}
        for src in sources:ok &= sync_file(src,dst_dir/src.relative_to(src_dir),check_only)
        if dst_dir.is_dir():
            for dst in sorted(p for p in dst_dir.rglob('*') if p.is_file()):
                if dst.relative_to(dst_dir) not in rels:
                    if check_only:print(f'  ORPHAN {dst.relative_to(ROOT)}');ok=False
                    else:dst.unlink();print(f'  removed {dst.relative_to(ROOT)}')
    return ok

def mirror_figures(manifest,check_only):
    if not any(cfg.get('figures') for cfg in manifest.values()):return True
    from learning_figures.core import synchronize,static_check
    problems=synchronize(ROOT,check=check_only)+static_check(ROOT)
    for problem in problems:print('  '+problem)
    return not problems

def mirror_page_flows(manifest,check_only):
    if not any(cfg.get('page_figures') for cfg in manifest.values()):return True
    from learning_figures.page_flows import synchronize,static_check
    problems=synchronize(manifest,ROOT,check=check_only)+static_check(manifest,ROOT)
    for problem in problems:print('  '+problem)
    return not problems

def main():
    check_only='--check' in sys.argv;manifest=load_manifest()
    sources=sorted(SOURCE_DIR.glob('*.json'))
    if not sources:raise SystemExit(f'没有课程数据：{SOURCE_DIR}')
    if not TERM_SOURCE.is_file():raise SystemExit(f'缺少术语首现注册表：{TERM_SOURCE}')
    source_slugs={p.stem for p in sources};unknown=sorted(set(manifest)-source_slugs);ok=not unknown
    if unknown:print('manifest entries without canonical lesson:',', '.join(unknown))
    # Validate/generate figures before writing any lesson mirrors. Missing runtime blocks.
    ok &= mirror_figures(manifest,check_only)
    ok &= mirror_page_flows(manifest,check_only)
    if not ok:return 1
    print('lesson data mirrors')
    for src in sources:ok &= sync_file(src,PAGES_DATA_DIR/src.name,check_only)
    print('\nterminology registry mirror');ok &= sync_file(TERM_SOURCE,PAGES_TERM_DATA,check_only)
    ok &= mirror_supplements(manifest,check_only)
    print('\nlesson entry files')
    for slug in sorted(source_slugs):
        layout_file=LAYOUT_DIR/f'{layout_for(manifest,slug)}.html'
        if not layout_file.is_file():print(f'  FAIL {slug}: missing layout');ok=False
        ok &= sync_text(wrapper(manifest,slug),PAGES_LESSON_DIR/f'{slug}.html',check_only)
    if PAGES_LESSON_DIR.is_dir():
        for page in sorted(PAGES_LESSON_DIR.glob('*.html')):
            if page.name not in EXEMPT_PAGES and page.stem not in source_slugs:
                if check_only:print(f'  ORPHAN {page.relative_to(ROOT)}');ok=False
                else:page.unlink();print(f'  removed {page.relative_to(ROOT)}')
    if NOJEKYLL.exists():
        if check_only:print('FAIL: docs/.nojekyll disables Jekyll');ok=False
        else:NOJEKYLL.unlink()
    print('\nOK: canonical lesson, figure, supplement and wrapper synchronization.' if ok else '\nFAIL: generated source drift.')
    return 0 if ok else 1
if __name__=='__main__':
    try:raise SystemExit(main())
    except ImportError as exc:print('BLOCKED: install tools/learning-figures-requirements.txt:',exc);raise SystemExit(2)
