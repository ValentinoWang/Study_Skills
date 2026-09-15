#!/usr/bin/env python3
"""Build small, auditable web charts. No network, eval, or browser runtime.

This exporter is independent of the v2 mechanism-diagram geometry validator.
Its report never certifies scientific interpretation, browser QA, or deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import math
from pathlib import Path
import platform
import re
import sys

BASE = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'
SLUG = re.compile(r'[a-z][a-z0-9-]{0,63}\Z')


class ContractError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ContractError(f'{label}: expected nonempty text, at most 1000 characters')
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ContractError(f'{label}: control characters are not supported')
    return value


def keys(value: object, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ContractError(f'{label}: expected exactly {sorted(expected)}')


def number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def validate(model: dict) -> None:
    keys(model, {'version', 'id', 'kind', 'question', 'takeaway', 'boundary',
                 'reading_order', 'evidence', 'x', 'y', 'series'}, 'model')
    if type(model['version']) is not int or model['version'] != 1:
        raise ContractError('Unsupported chart model version')
    if not isinstance(model['id'], str) or not SLUG.fullmatch(model['id']):
        raise ContractError('id: expected a safe lowercase slug')
    if model['kind'] not in ('line', 'scatter', 'bar'):
        raise ContractError('BLOCKED_UNSUPPORTED: supported kinds are line, scatter, bar')
    for field in ('question', 'takeaway', 'boundary', 'reading_order'):
        text(model[field], field)
    for axis in ('x', 'y'):
        keys(model[axis], {'label', 'unit', 'meaning'}, axis)
        for field in ('label', 'unit', 'meaning'):
            text(model[axis][field], f'{axis}.{field}')
    ev = model['evidence']
    keys(ev, {'type', 'source', 'sample_size', 'replicate_unit', 'aggregation',
              'uncertainty', 'transformations'}, 'evidence')
    if ev['type'] not in ('teaching-example', 'measured'):
        raise ContractError('evidence.type: expected teaching-example or measured')
    for field in ('source', 'replicate_unit', 'aggregation'):
        text(ev[field], f'evidence.{field}')
    if ev['uncertainty'] != 'not-estimated':
        raise ContractError('BLOCKED_UNSUPPORTED: this exporter does not render uncertainty intervals')
    if not isinstance(ev['transformations'], list):
        raise ContractError('transformations must be an explicit list; use [] for none')
    for item in ev['transformations']:
        text(item, 'transformation')
    n = ev['sample_size']
    if n is not None and (type(n) is not int or n < 1):
        raise ContractError('sample_size must be a positive integer or null')
    if ev['type'] == 'measured' and n is None:
        raise ContractError('Measured data requires sample size and replication unit')
    series = model['series']
    if not isinstance(series, list) or not 1 <= len(series) <= 3:
        raise ContractError('Split the figure: supported series count is 1..3')
    labels = set()
    for s in series:
        keys(s, {'label', 'meaning', 'x', 'y'}, 'series')
        label = text(s['label'], 'series.label')
        text(s['meaning'], 'series.meaning')
        if label in labels:
            raise ContractError('Series labels must be unique')
        labels.add(label)
        if not isinstance(s['x'], list) or not isinstance(s['y'], list):
            raise ContractError('Series x/y must be lists')
        if len(s['x']) != len(s['y']) or not 1 <= len(s['x']) <= 30:
            raise ContractError('Series needs 1..30 paired observations; split larger figures')
        if not all(number(v) for v in s['y']):
            raise ContractError('BLOCKED_UNSUPPORTED: missing/nonfinite y; do not silently impute or omit')
        if model['kind'] == 'bar':
            if not all(isinstance(v, str) and v.strip() for v in s['x']):
                raise ContractError('Bar x must contain nonempty category labels')
            if len(set(s['x'])) != len(s['x']) or s['x'] != series[0]['x']:
                raise ContractError('Bars require unique, identically ordered categories')
        elif not all(number(v) for v in s['x']):
            raise ContractError('Numeric chart requires finite numeric x values')
        elif model['kind'] == 'line' and any(a >= b for a, b in zip(s['x'], s['x'][1:])):
            raise ContractError('Line x must be strictly increasing; ordering is not silently changed')
        if model['kind'] == 'line' and len(s['x']) < 2:
            raise ContractError('A line requires at least two points')


def esc(value: object) -> str:
    # Prevent authored prose from becoming Liquid code in the generated include.
    return html.escape(str(value), quote=True).replace('{', '&#123;').replace('}', '&#125;')


def axis_label(axis: dict) -> str:
    return f"{axis['label']} ({axis['unit']})"


def make_svg(model: dict) -> bytes:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.ft2font import FT2Font

    # Select a local font containing every plotted glyph; fail instead of tofu.
    plotted = ''.join([axis_label(model['x']), axis_label(model['y'])] +
                      [s['label'] for s in model['series']] +
                      ([str(v) for v in model['series'][0]['x']] if model['kind'] == 'bar' else []))
    required = {ord(c) for c in plotted if not c.isspace()}
    candidates = ['Noto Sans CJK SC', 'Noto Sans CJK JP', 'DejaVu Sans']
    selected = None
    for name in candidates:
        try:
            path = font_manager.findfont(name, fallback_to_default=False)
            if required <= set(FT2Font(path).get_charmap()):
                selected = path
                break
        except ValueError:
            continue
    if selected is None:
        raise ContractError('BLOCKED_FONT: install a local font containing the plotted labels (e.g. fonts-noto-cjk)')
    # Paths isolate the image from client font substitution. HTML retains text/data.
    with plt.rc_context({'font.family': font_manager.FontProperties(fname=selected).get_name(),
                         'font.size': 14, 'svg.fonttype': 'path',
                         'svg.hashsalt': digest(json_bytes(model)),
                         'text.usetex': False, 'text.parse_math': False}):
        fig, ax = plt.subplots(figsize=(8, 4.8), layout='constrained')
        try:
            markers, lines, hatches = ('o', 's', '^'), ('-', '--', ':'), ('', '//', 'xx')
            for i, s in enumerate(model['series']):
                if model['kind'] == 'line':
                    ax.plot(s['x'], s['y'], marker=markers[i], linestyle=lines[i],
                            linewidth=2, markersize=6, label=s['label'])
                elif model['kind'] == 'scatter':
                    ax.scatter(s['x'], s['y'], marker=markers[i], s=50, label=s['label'])
                else:
                    width = 0.8 / len(model['series'])
                    positions = [j + (i - (len(model['series']) - 1) / 2) * width
                                 for j in range(len(s['x']))]
                    ax.bar(positions, s['y'], width=width, hatch=hatches[i], label=s['label'])
            if model['kind'] == 'bar':
                ax.set_xticks(range(len(model['series'][0]['x'])), model['series'][0]['x'])
                lo, hi = ax.get_ylim()
                ax.set_ylim(min(0, lo), max(0, hi))
            ax.set(xlabel=axis_label(model['x']), ylabel=axis_label(model['y']))
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(axis='y', alpha=0.2)
            ax.set_axisbelow(True)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), frameon=False,
                      ncol=1 if len(model['series']) == 3 else len(model['series']))
            stream = io.BytesIO()
            fig.savefig(stream, format='svg', metadata={'Date': None, 'Title': model['question'],
                                                       'Description': model['takeaway']})
            return stream.getvalue()
        finally:
            plt.close(fig)


def table(model: dict) -> str:
    series = model['series']
    if all(s['x'] == series[0]['x'] for s in series):
        headers = [axis_label(model['x'])] + [s['label'] for s in series]
        rows = ''.join('<tr><th scope="row">' + esc(x) + '</th>' +
                       ''.join('<td>' + esc(s['y'][i]) + '</td>' for s in series) + '</tr>'
                       for i, x in enumerate(series[0]['x']))
    else:
        headers = ['系列', axis_label(model['x']), axis_label(model['y'])]
        rows = ''.join('<tr><th scope="row">' + esc(s['label']) + '</th><td>' + esc(x) +
                       '</td><td>' + esc(y) + '</td></tr>'
                       for s in series for x, y in zip(s['x'], s['y']))
    head = ''.join('<th scope="col">' + esc(h) + '</th>' for h in headers)
    return ('<div class="lf-chart-table" tabindex="0" role="region" aria-label="源数据，可横向滚动">'
            f'<table><caption>完整点值 · {esc(axis_label(model["y"]))}</caption>'
            '<thead><tr>' + head + '</tr></thead><tbody>' + rows + '</tbody></table></div>')



def fragment(model: dict, image_url: str, source_url: str) -> str:
    ev, ident = model['evidence'], 'chart-' + model['id']
    badge = '教学示例 · 非实测' if ev['type'] == 'teaching-example' else '实测数据 · 待独立审阅'
    provenance = (f'<p class="lf-chart-note"><strong>数据口径：</strong>{esc(ev["source"])}；'
                  f'样本量：{esc(ev["sample_size"] if ev["sample_size"] is not None else "不适用")}；'
                  f'重复单位：{esc(ev["replicate_unit"])}；聚合：{esc(ev["aggregation"])}；'
                  f'变换：{esc("；".join(ev["transformations"]) or "无")}；未估计不确定性。</p>')
    image = (f'<div class="lf-chart-scroll" tabindex="0" role="region" aria-label="完整图，可横向滚动">'
             f'<img src="{image_url}" alt="{esc(model["question"] + "；" + model["takeaway"])}" '
             'width="800" height="480" loading="lazy" decoding="async"></div>')
    data = table(model)
    definitions = ''.join(f'<dt>{esc(axis_label(model[a]))}</dt><dd>{esc(model[a]["meaning"])}</dd>' for a in ('x', 'y'))
    definitions += ''.join(f'<dt>{esc(s["label"])}</dt><dd>{esc(s["meaning"])}</dd>' for s in model['series'])
    return f'''<figure class="lf-chart" id="{ident}" aria-labelledby="{ident}-title" data-chart-model="{digest(json_bytes(model))}">
<figcaption id="{ident}-title"><span class="lf-chart-kicker">{badge}</span><strong>{esc(model['question'])}</strong></figcaption>
<div class="lf-chart-definitions"><strong>先认轴与图例</strong><dl>{definitions}</dl></div>
<p class="lf-chart-reading">{esc(model['reading_order'])}</p>
<div class="lf-chart-wide">{image}</div>
<p class="lf-chart-takeaway"><strong>读图结论：</strong>{esc(model['takeaway'])}</p>
<div class="lf-chart-linear">{data}</div>
<details class="lf-chart-full"><summary>展开完整图（可横向滚动）</summary>{image}</details>
<details class="lf-chart-source"><summary>查看全部点值</summary>{data}</details>
{provenance}
<p class="lf-chart-note"><strong>适用边界：</strong>{esc(model['boundary'])}</p>
<p class="lf-chart-download"><a href="{source_url}">下载图形源模型与数据 JSON</a></p>
</figure>
'''


def build(model: dict, web_path: str) -> dict[str, bytes]:
    validate(model)
    if not re.fullmatch(r'(?:/[A-Za-z0-9_-]+)+', web_path):
        raise ContractError('web-path must be a site-relative path without baseurl, dots, or Liquid')
    ident = model['id']
    css = (BASE / 'assets/chart.css').read_bytes()
    raw = json_bytes(model)
    svg = make_svg(model)
    liquid = lambda suffix: "{{ '" + web_path + '/' + ident + suffix + "' | relative_url }}"
    page_fragment = fragment(model, liquid('.svg'), liquid('.source.json'))
    preview_fragment = fragment(model, ident + '.svg', ident + '.source.json')
    preview = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
               '<meta name="viewport" content="width=device-width, initial-scale=1">'
               f'<title>{esc(model["question"])}</title><link rel="stylesheet" href="learning-chart.css">'
               '</head><body><main style="max-width:960px;margin:32px auto;padding:0 16px">'
               '<p>Learning Figure · 静态图表预览（不是 Pages 部署证明）</p>' +
               preview_fragment + '</main></body></html>\n')
    outputs = {ident + '.svg': svg, ident + '.source.json': raw,
               ident + '.figure.html': page_fragment.encode(),
               ident + '.preview.html': preview.encode(), 'learning-chart.css': css}
    import matplotlib
    report = {'exporter_version': VERSION, 'model_sha256': digest(raw),
              'renderer_sha256': digest(Path(__file__).read_bytes()),
              'style_sha256': digest(css), 'python_version': platform.python_version(),
              'matplotlib_version': matplotlib.__version__,
              'evidence_type': model['evidence']['type'],
              'outputs': {name: digest(data) for name, data in outputs.items()},
              'checks': {'input_contract': 'PASS', 'artifact_export': 'PASS',
                         'scientific_review': 'NOT_RUN', 'browser_layout': 'NOT_RUN',
                         'visual_review': 'NOT_RUN', 'pagination': 'NOT_RUN',
                         'pages_build': 'NOT_RUN', 'public_readback': 'NOT_RUN'}}
    outputs[ident + '.report.json'] = json_bytes(report)
    return outputs


def reject_duplicates(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--web-path', required=True, help='e.g. /assets/figures/my-lesson; omit /Study_Skills')
    parser.add_argument('--check', action='store_true', help='Compare generated bytes without writing')
    args = parser.parse_args()
    try:
        model = json.loads(args.model.read_text(encoding='utf-8'), object_pairs_hook=reject_duplicates)
        outputs = build(model, args.web_path)
        if args.check:
            drift = [name for name, data in outputs.items()
                     if not (args.out / name).is_file() or (args.out / name).read_bytes() != data]
            if drift:
                raise ContractError('Generated artifact drift: ' + ', '.join(drift))
        else:
            args.out.mkdir(parents=True, exist_ok=True)
            for name, data in outputs.items():
                target = args.out / name
                temporary = target.with_suffix(target.suffix + '.tmp')
                temporary.write_bytes(data)
                temporary.replace(target)
        print('PASS: input/export identity only. Scientific, browser, and Pages checks remain separate.')
        return 0
    except (OSError, ValueError, TypeError, KeyError, ImportError) as exc:
        print(f'FAIL/BLOCKED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
