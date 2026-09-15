#!/usr/bin/env python3
"""Offline Chromium checks of chart exports; NOT a Jekyll or Pages acceptance test."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--id', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--offline', action='store_true', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', args.id):
        parser.error('id must be a safe lowercase slug')
    from playwright.sync_api import sync_playwright
    base = args.directory
    args.out.mkdir(parents=True, exist_ok=True)
    export_report = (base / f'{args.id}.report.json').read_bytes()
    for name, expected in json.loads(export_report)['outputs'].items():
        if Path(name).name != name:
            raise ValueError('Unsafe artifact path in report')
        if hashlib.sha256((base / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Artifact drift: {name}')
    source = (base / f'{args.id}.preview.html').read_text()
    source = source.replace('<link rel="stylesheet" href="learning-chart.css">',
                            '<style>' + (base / 'learning-chart.css').read_text() + '</style>')
    source = source.replace(f'src="{args.id}.svg"', 'src="data:image/svg+xml;base64,' +
                            base64.b64encode((base / f'{args.id}.svg').read_bytes()).decode() + '"')
    report = {'scope': 'Offline standalone export DOM; embeds the same CSS/SVG bytes. Not Jekyll, network or Pages QA.',
              'export_report_sha256': hashlib.sha256(export_report).hexdigest(),
              'pages_build': 'NOT_RUN', 'public_readback': 'NOT_RUN', 'pagination': 'NOT_RUN',
              'independent_visual_review': 'NOT_RUN', 'cases': []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=shutil.which('chromium'), headless=True,
                                       args=['--no-sandbox'])
            for name, width, js, media in [('desktop', 1280, True, 'screen'), ('mobile', 390, True, 'screen'),
                                          ('small', 320, True, 'screen'), ('no-js', 1280, False, 'screen'),
                                          ('print', 794, False, 'print')]:
                context = browser.new_context(viewport={'width': width, 'height': 1000}, java_script_enabled=js)
                page = context.new_page()
                page.route('**/*', lambda route: route.abort())  # No live dependencies in offline inspection.
                page.emulate_media(media=media)
                page.set_content(source)
                page.evaluate('() => document.fonts.ready')
                state = page.evaluate('''() => ({
                    rootOverflow: document.documentElement.scrollWidth > innerWidth + 1,
                    dataVisible: getComputedStyle(document.querySelector('.lf-chart-linear')).display !== 'none',
                    definitionsBeforeImage: !!(document.querySelector('.lf-chart-definitions').compareDocumentPosition(document.querySelector('img')) & Node.DOCUMENT_POSITION_FOLLOWING),
                    scripts: document.scripts.length,
                    visibleFontMinimum: Math.min(...[...document.querySelectorAll('.lf-chart p,.lf-chart td,.lf-chart dd')].filter(x => x.getBoundingClientRect().height).map(x => parseFloat(getComputedStyle(x).fontSize)))
                })''')
                state['name'] = name
                if name in ('mobile', 'small'):
                    summary = page.locator('.lf-chart-full summary')
                    summary.focus()
                    summary.press('Enter')
                    page.locator('.lf-chart-full img').evaluate('(x) => x.decode()')
                    state['keyboardExpanded'] = page.locator('.lf-chart-full').get_attribute('open') is not None
                    state['expandedImageWidth'] = page.locator('.lf-chart-full img').evaluate('(x) => x.getBoundingClientRect().width')
                    state['expandedRootOverflow'] = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                    summary.press('Enter')
                elif name != 'print':
                    page.locator('.lf-chart-wide img').evaluate('(x) => x.decode()')
                    state['imageLoaded'] = True
                passed = (not state['rootOverflow'] and state['definitionsBeforeImage'] and
                          state['scripts'] == 0 and state['visibleFontMinimum'] >= 16)
                if name in ('mobile', 'small', 'print'):
                    passed = passed and state['dataVisible']
                if name in ('mobile', 'small'):
                    passed = passed and state['keyboardExpanded'] and not state['expandedRootOverflow']
                state['status'] = 'PASS' if passed else 'FAIL'
                path = args.out / f'{name}.png'
                page.screenshot(path=str(path), full_page=True)
                state['screenshot_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                report['cases'].append(state)
                context.close()
            browser.close()
        report['status'] = 'PASS' if all(c['status'] == 'PASS' for c in report['cases']) else 'FAIL'
    except Exception as exc:
        report['status'] = 'BLOCKED'
        report['error'] = str(exc)
    (args.out / 'chart-preview.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
