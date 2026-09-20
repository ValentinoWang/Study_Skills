#!/usr/bin/env python3
"""Red/green regressions for Pages-native teaching-flow contracts."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from learning_figures.page_flows import ContractError, entries, synchronize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / 'skills/learning-figure/schema/page-flow-v1.schema.json').read_text())


def model() -> dict:
    return {
        'schema_version': '1.0',
        'id': 'demo-flow',
        'kind': 'pipeline',
        'question': '先看什么？',
        'takeaway': '步骤有明确顺序。',
        'reading_order': '从左到右。',
        'boundary': '这是教学示意。',
        'evidence_type': 'schematic',
        'steps': [
            {'id': 'one', 'label': '① 一', 'detail': '第一步。', 'tone': 'info'},
            {'id': 'two', 'label': '② 二', 'detail': '第二步。', 'tone': 'success'},
        ],
    }


class PageFlowRegressionTests(unittest.TestCase):
    def make_root(self, m: dict | None = None):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        schema = root / 'skills/learning-figure/schema/page-flow-v1.schema.json'
        schema.parent.mkdir(parents=True)
        schema.write_text(json.dumps(SCHEMA), encoding='utf-8')
        path = root / 'skills/learning-figure/page-figures/demo/demo-flow.flow.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(m or model(), ensure_ascii=False), encoding='utf-8')
        return td, root, path

    @staticmethod
    def manifest(**overrides):
        ref = {
            'id': 'demo-flow',
            'model': 'skills/learning-figure/page-figures/demo/demo-flow.flow.json',
            'slot': 'after-map',
        }
        ref.update(overrides.pop('ref', {}))
        cfg = {'page_figures': [ref]}
        cfg.update(overrides)
        return {'demo': cfg}

    def test_valid_model(self):
        td, root, _ = self.make_root()
        with td:
            found = list(entries(self.manifest(), root))
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0][3]['id'], 'demo-flow')

    def test_duplicate_step_id_is_blocked(self):
        m = model(); m['steps'][1]['id'] = 'one'
        td, root, _ = self.make_root(m)
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(), root))

    def test_unknown_slot_is_blocked(self):
        td, root, _ = self.make_root()
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(ref={'slot': 'hero'}), root))

    def test_nonstandard_layout_is_blocked(self):
        td, root, _ = self.make_root()
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(layout='lesson-expanded'), root))

    def test_manifest_model_identity_mismatch_is_blocked(self):
        td, root, _ = self.make_root()
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(ref={'id': 'other-flow'}), root))

    def test_path_traversal_is_blocked(self):
        td, root, _ = self.make_root()
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(ref={'model': '../outside.json'}), root))

    def test_unknown_model_field_is_blocked(self):
        m = model(); m['authored_x'] = 10
        td, root, _ = self.make_root(m)
        with td, self.assertRaises(ContractError):
            list(entries(self.manifest(), root))

    def test_sync_and_drift_detection(self):
        td, root, _ = self.make_root()
        with td:
            manifest = self.manifest()
            self.assertEqual(synchronize(manifest, root, check=False), [])
            self.assertEqual(synchronize(manifest, root, check=True), [])
            mirror = root / 'docs/_data/learning_page_figures/demo.json'
            payload = json.loads(mirror.read_text())
            self.assertEqual(payload['demo-flow']['slot'], 'after-map')
            mirror.write_text('{}\n', encoding='utf-8')
            problems = synchronize(manifest, root, check=True)
            self.assertTrue(any('generated drift' in p for p in problems))

    def test_orphan_mirror_is_blocked_in_check_mode(self):
        td, root, _ = self.make_root()
        with td:
            synchronize(self.manifest(), root, check=False)
            orphan = root / 'docs/_data/learning_page_figures/orphan.json'
            orphan.write_text('{}\n', encoding='utf-8')
            problems = synchronize(self.manifest(), root, check=True)
            self.assertTrue(any('orphan' in p for p in problems))


if __name__ == '__main__':
    unittest.main(verbosity=2)
