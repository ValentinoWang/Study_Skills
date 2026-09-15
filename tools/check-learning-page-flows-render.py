#!/usr/bin/env python3
"""Audit Pages-native teaching flows in an actual Jekyll build artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from learning_figures.core import ROOT, chromium, digest, json_bytes
from learning_figures.page_flows import entries
from learning_figures.runner import serve


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built-site', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    site = args.built_site.resolve()
    out = args.output.resolve()
    if out.is_relative_to(site):
        raise SystemExit('PAGE-FLOW-ARTIFACT-001: evidence must live outside the built artifact')
    out.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((ROOT / 'skills/learning-page-design-publisher/lesson-manifest.json').read_text())
    by_lesson = {}
    for lesson, _cfg, ref, model, _path in entries(manifest, ROOT):
        by_lesson.setdefault(lesson, []).append((ref, model))
    if not by_lesson:
        print('PASS: no Pages-native flows registered')
        return 0

    from playwright.sync_api import sync_playwright

    cases = [('desktop', 1280, True, 'screen'), ('mobile', 390, True, 'screen'),
             ('narrow-no-js', 320, False, 'screen'), ('print-media', 794, False, 'print')]
    results = []
    try:
        with serve(site) as url, sync_playwright() as pw:
            browser = chromium(pw)
            browser_version = browser.version
            for lesson, figures in by_lesson.items():
                page_file = site / 'lessons' / f'{lesson}.html'
                if not page_file.is_file():
                    results.append({'lesson': lesson, 'status': 'FAIL', 'issues': ['built lesson missing']})
                    continue
                for case, width, javascript, media in cases:
                    context = browser.new_context(viewport={'width': width, 'height': 1000}, java_script_enabled=javascript)
                    page = context.new_page()
                    page.goto(f'{url}/lessons/{lesson}.html', wait_until='networkidle')
                    page.emulate_media(media=media)
                    for ref, model in figures:
                        selector = f'#fig-{model["id"]}'
                        issues = page.evaluate('''({selector,model}) => {
                          const issues=[], all=[...document.querySelectorAll(selector)];
                          if(all.length!==1)return ['figure missing or duplicated'];
                          const f=all[0], visible=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'};
                          if(!visible(f))issues.push('figure is not visible');
                          const steps=[...f.querySelectorAll('.lpf-step')];
                          if(steps.length!==model.steps.length)issues.push('step count differs from model');
                          model.steps.forEach((step,i)=>{const el=steps[i];if(!el)return;const t=el.textContent.replace(/\\s+/g,' ');if(!t.includes(step.label)||!t.includes(step.detail))issues.push('step text differs: '+step.id);});
                          const prose=[...f.querySelectorAll('.lpf-reading,.lpf-step p,.lpf-takeaway,.lpf-boundary')].filter(visible);
                          if(prose.some(e=>parseFloat(getComputedStyle(e).fontSize)<16))issues.push('visible figure prose smaller than 16px');
                          if(document.documentElement.scrollWidth>innerWidth+1)issues.push('page root horizontally overflows');
                          if(!f.textContent.includes(model.takeaway)||!f.textContent.includes(model.boundary))issues.push('takeaway/boundary missing');
                          return issues;
                        }''', {'selector': selector, 'model': model})
                        shot = f'{lesson}--{model["id"]}--{case}.png'
                        page.locator(selector).screenshot(path=str(out / shot))
                        results.append({'lesson': lesson, 'figure': model['id'], 'slot': ref['slot'], 'case': case,
                                        'viewport': width, 'javascript': javascript,
                                        'status': 'FAIL' if issues else 'PASS', 'issues': issues,
                                        'screenshot': shot, 'page_sha256': digest(page_file.read_bytes())})
                    context.close()
            browser.close()
        status = 'PASS' if results and all(r['status'] == 'PASS' for r in results) else 'FAIL'
        report = {'status': status, 'browser_version': browser_version,
                  'scope': 'actual Jekyll candidate; desktop/mobile/no-JS/print-media. Not public readback or paginated PDF proof.',
                  'public_readback': 'NOT_RUN', 'pagination': 'NOT_RUN', 'cases': results}
    except Exception as exc:
        report = {'status': 'BLOCKED', 'message': str(exc), 'cases': results,
                  'public_readback': 'NOT_RUN', 'pagination': 'NOT_RUN'}
    (out / 'report.json').write_bytes(json_bytes(report))
    print(report['status'], len(report['cases']), 'page-flow cases; see', out / 'report.json')
    return 0 if report['status'] == 'PASS' else 2 if report['status'] == 'BLOCKED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
