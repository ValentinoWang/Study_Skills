"""Synchronize small Pages-native teaching flows from canonical JSON models.

These figures are semantic HTML/CSS rendered by Jekyll. They intentionally do
not enter the v2 SVG geometry checker, whose guarantees apply to a different
rendering surface.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('skills/learning-figure')
SCHEMA = BASE / 'schema/page-flow-v1.schema.json'
DATA_DIR = Path('docs/_data/learning_page_figures')
SLOTS = {'after-orient', 'after-map', 'after-case', 'after-mapping'}
LAYOUT_SLOTS = {'lesson': SLOTS, 'lesson-microcourse': {'after-orient'}}


class ContractError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def safe_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ContractError(f'PAGE-FLOW-MODEL-001: unsafe repository path {relative!r}')
    return path


def entries(manifest: dict, root: Path = ROOT):
    from jsonschema import Draft202012Validator

    schema = json.loads((root / SCHEMA).read_text(encoding='utf-8'))
    validator = Draft202012Validator(schema)
    for lesson, cfg in manifest.items():
        refs = cfg.get('page_figures', [])
        if not refs:
            continue
        layout_name = cfg.get('layout', 'lesson')
        if layout_name not in LAYOUT_SLOTS:
            raise ContractError(f'PAGE-FLOW-INTEGRATION-001: {lesson}: unsupported layout {layout_name!r}')
        if not isinstance(refs, list):
            raise ContractError(f'PAGE-FLOW-MODEL-001: {lesson}: page_figures must be a list')
        seen = set()
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {'id', 'model', 'slot'}:
                raise ContractError(f'PAGE-FLOW-MODEL-001: {lesson}: ref requires exactly id/model/slot')
            if ref['id'] in seen:
                raise ContractError(f'PAGE-FLOW-MODEL-001: {lesson}: duplicate id {ref["id"]}')
            seen.add(ref['id'])
            if ref['slot'] not in LAYOUT_SLOTS[layout_name]:
                raise ContractError(f'PAGE-FLOW-INTEGRATION-001: unsupported slot {ref["slot"]!r} for {layout_name}')
            model_path = safe_path(root, ref['model'])
            if not model_path.is_file():
                raise ContractError(f'PAGE-FLOW-MODEL-001: missing {ref["model"]}')
            model = json.loads(model_path.read_text(encoding='utf-8'))
            problems = sorted(validator.iter_errors(model), key=lambda e: str(e.path))
            if problems:
                raise ContractError('PAGE-FLOW-MODEL-001: ' + '; '.join(
                    f'{list(e.path)} {e.message}' for e in problems[:5]
                ))
            ids = [step['id'] for step in model['steps']]
            if len(ids) != len(set(ids)):
                raise ContractError(f'PAGE-FLOW-MODEL-001: {model["id"]}: duplicate step id')
            if ref['id'] != model['id']:
                raise ContractError(f'PAGE-FLOW-MODEL-001: {lesson}: manifest/model identity mismatch')
            yield lesson, cfg, ref, model, model_path


def expected_outputs(manifest: dict, root: Path = ROOT) -> dict[Path, bytes]:
    grouped: dict[str, dict] = {}
    for lesson, _cfg, ref, model, model_path in entries(manifest, root):
        item = dict(model)
        item['slot'] = ref['slot']
        item['model_digest'] = digest(model_path.read_bytes())
        grouped.setdefault(lesson, {})[model['id']] = item
    return {root / DATA_DIR / f'{lesson}.json': json_bytes(items) for lesson, items in grouped.items()}


def synchronize(manifest: dict, root: Path = ROOT, check: bool = False) -> list[str]:
    problems = []
    expected = expected_outputs(manifest, root)
    data_dir = root / DATA_DIR
    for path, content in expected.items():
        if not path.exists() or path.read_bytes() != content:
            if check:
                problems.append(f'PAGE-FLOW-ARTIFACT-001: generated drift {path.relative_to(root)}')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    if data_dir.is_dir():
        for path in sorted(data_dir.glob('*.json')):
            if path not in expected:
                if check:
                    problems.append(f'PAGE-FLOW-ARTIFACT-001: orphan {path.relative_to(root)}')
                else:
                    path.unlink()
    return problems


def static_check(manifest: dict, root: Path = ROOT) -> list[str]:
    problems = []
    renderer = root / 'docs/_includes/learning-page-figure.html'
    slot_renderer = root / 'docs/_includes/learning-page-figure-slot.html'
    css = root / 'docs/assets/css/learning-figure.css'
    for required in (renderer, slot_renderer, css):
        if not required.is_file():
            problems.append(f'PAGE-FLOW-INTEGRATION-001: missing {required.relative_to(root)}')
    layouts = {'lesson'} | {
        cfg.get('layout', 'lesson') for cfg in manifest.values() if cfg.get('page_figures')
    }
    for layout_name in sorted(layouts):
        if layout_name not in LAYOUT_SLOTS:
            continue  # entries reports unsupported layouts, without reading arbitrary paths.
        layout = root / 'docs/_layouts' / f'{layout_name}.html'
        if not layout.is_file():
            problems.append(f'PAGE-FLOW-INTEGRATION-001: missing {layout.relative_to(root)}')
            continue
        text = layout.read_text(encoding='utf-8')
        if "'/assets/css/learning-figure.css' | relative_url" not in text:
            problems.append(f'PAGE-FLOW-INTEGRATION-001: {layout_name} layout must load learning-figure.css via relative_url')
        slots = {
            ref['slot'] for cfg in manifest.values()
            if cfg.get('layout', 'lesson') == layout_name
            for ref in cfg.get('page_figures', [])
        }
        for slot in sorted(slots):
            token = f'{{% include learning-page-figure-slot.html slot="{slot}" %}}'
            if text.count(token) != 1:
                problems.append(f'PAGE-FLOW-INTEGRATION-001: {layout_name} layout requires exactly one {token}')
    try:
        list(entries(manifest, root))
    except (ContractError, json.JSONDecodeError, OSError) as exc:
        problems.append(str(exc))
    return problems
