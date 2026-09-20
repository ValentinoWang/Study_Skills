#!/usr/bin/env python3
"""Focused chart-kit regressions; these do not replace the repository v2 tests."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('chart_exporter', BASE / 'scripts/render-chart.py')
chart = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chart)


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((BASE / 'examples/convergence.chart.json').read_text())

    def bad(self, mutate):
        mutate(self.model)
        with self.assertRaises(chart.ContractError):
            chart.validate(self.model)

    def test_valid_example(self):
        chart.validate(self.model)

    def test_measured_needs_n(self):
        self.bad(lambda m: m['evidence'].update(type='measured'))

    def test_measured_contract(self):
        self.model['evidence'].update(type='measured', sample_size=6, replicate_unit='one independent run')
        chart.validate(self.model)  # Valid structure, not verification that data is real.

    def test_reject_unknown_kind(self):
        self.bad(lambda m: m.update(kind='heatmap'))

    def test_reject_uncertainty_without_renderer(self):
        self.bad(lambda m: m['evidence'].update(uncertainty='95% CI'))

    def test_reject_nan(self):
        self.bad(lambda m: m['series'][0]['y'].__setitem__(0, float('nan')))

    def test_reject_missing(self):
        self.bad(lambda m: m['series'][0]['y'].__setitem__(0, None))

    def test_reject_bool_as_numeric(self):
        self.bad(lambda m: m['series'][0]['x'].__setitem__(0, True))

    def test_reject_unordered_line(self):
        self.bad(lambda m: m['series'][0]['x'].reverse())

    def test_reject_traversal(self):
        self.bad(lambda m: m.update(id='../outside'))

    def test_reject_duplicate_json_key(self):
        with self.assertRaises(chart.ContractError):
            json.loads('{"id":"one","id":"two"}', object_pairs_hook=chart.reject_duplicates)

    def test_reject_unknown_field(self):
        self.bad(lambda m: m.update(ylim=[0, 0.1]))

    def test_reject_lost_axis_definition(self):
        self.bad(lambda m: m['x'].pop('meaning'))

    def test_reject_duplicate_series(self):
        self.bad(lambda m: m['series'][1].update(label=m['series'][0]['label']))

    def test_reject_mismatched_values(self):
        self.bad(lambda m: m['series'][0]['y'].pop())

    def test_reject_too_many_series(self):
        self.bad(lambda m: m['series'].extend(copy.deepcopy(m['series'])))

    def test_no_html_injection(self):
        self.model['question'] = '<script>alert(1)</script>'
        result = chart.fragment(self.model, 'image.svg', 'source.json')
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_no_liquid_injection(self):
        self.model['question'] = '{{ site.secret }} {% include unexpected.html %}'
        result = chart.fragment(self.model, 'image.svg', 'source.json')
        self.assertNotIn('{{', result)
        self.assertNotIn('{%', result)
        self.assertIn('&#123;', result)

    def test_complete_table(self):
        table = chart.table(self.model)
        self.assertEqual(table.count('<td>'), sum(len(s['y']) for s in self.model['series']))

    def test_definitions_before_image(self):
        result = chart.fragment(self.model, 'image.svg', 'source.json')
        self.assertLess(result.index('先认轴与图例'), result.index('<img'))
        self.assertIn('非实测', result)

    def test_web_path_validation(self):
        for path in ('https://example.com/assets', '/assets/../private', '/assets/{{x}}', 'relative'):
            with self.subTest(path=path), self.assertRaises(chart.ContractError):
                chart.build(self.model, path)

    def test_exports_and_reproducibility(self):
        a = chart.build(self.model, '/assets/figures/demo')
        b = chart.build(self.model, '/assets/figures/demo')
        self.assertEqual(a, b)
        report = json.loads(a['convergence.report.json'])
        self.assertEqual(report['checks']['pages_build'], 'NOT_RUN')
        self.assertEqual(report['checks']['browser_layout'], 'NOT_RUN')
        self.assertIn(b'| relative_url', a['convergence.figure.html'])
        root = ET.fromstring(a['convergence.svg'])
        self.assertTrue(root.tag.endswith('svg'))
        self.assertNotIn(b'<script', a['convergence.svg'])
        for name, expected in report['outputs'].items():
            self.assertEqual(chart.digest(a[name]), expected)

    def test_scatter_and_bar(self):
        for kind in ('scatter', 'bar'):
            with self.subTest(kind=kind):
                model = copy.deepcopy(self.model)
                model['kind'] = kind
                if kind == 'bar':
                    for s in model['series']:
                        s['x'] = [str(x) for x in s['x']]
                chart.validate(model)
                self.assertIn(b'<svg', chart.make_svg(model))


if __name__ == '__main__':
    unittest.main(verbosity=2)
