#!/usr/bin/env python3
"""Validate structured microcourses; optionally test the real Jekyll artifact.

No learner answers are graded. Browser evidence is limited to the actual checks;
print-media checks do not claim paginated-PDF or Safari validation.
"""
from __future__ import annotations
import argparse
import functools
import http.server
import json
import pathlib
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'skills/learning-page-design-publisher/lessons'
MANIFEST = ROOT / 'skills/learning-page-design-publisher/lesson-manifest.json'
FIELDS = ('id','module','title','goal','prerequisites','objects','baseline','trace','conclusion','change','kept','question','hint','answer','confusion','repair','verify','sources')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(slug, lesson):
    require(lesson.get('MICROCOURSE_VERSION') == 1, f'{slug}: unsupported schema')
    units = lesson.get('UNITS', [])
    require(bool(units), f'{slug}: no units')
    sources = {s['id'] for s in lesson['SOURCES']}
    require(len(sources) == len(lesson['SOURCES']), f'{slug}: duplicate source IDs')
    modules = {m['id'] for m in lesson['MODULES']}
    seen = set()
    for u in units:
        require(all(k in u for k in FIELDS), f'{slug}: missing fields in {u.get("id")}')
        uid = u['id']
        require(uid not in seen, f'{slug}: duplicate unit {uid}')
        require(u['module'] in modules, f'{slug}/{uid}: unknown module')
        require(set(u['prerequisites']) <= seen, f'{slug}/{uid}: forward or unknown prerequisite')
        require(isinstance(u['change'], str) and bool(u['change'].strip()), f'{slug}/{uid}: missing single-change declaration')
        for key in ('kept','question','answer','confusion','repair','verify'):
            require(isinstance(u[key], str) and len(u[key]) >= 6, f'{slug}/{uid}: thin {key}')
        require(len(u['trace']) >= 2, f'{slug}/{uid}: incomplete worked trace')
        require(len(u['objects']) >= 1, f'{slug}/{uid}: no prerequisite objects')
        for obj in u['objects']:
            require(all(isinstance(obj.get(k),str) and obj[k].strip() for k in ('name','meaning','location','example')), f'{slug}/{uid}: unbound object')
        require(bool(u['sources']) and set(u['sources']) <= sources, f'{slug}/{uid}: broken source references')
        seen.add(uid)
    for entry in lesson['GLOSSARY']:
        require(entry['unit'] in seen, f'{slug}: glossary points to unknown unit')
    for s in lesson['SOURCES']:
        require(s['url'].startswith('https://'), f'{slug}: non-HTTPS source')
    src = SOURCE / f'{slug}.json'
    mirror = ROOT / 'docs/_data/lessons' / src.name
    require(mirror.exists() and src.read_bytes() == mirror.read_bytes(), f'{slug}: mirror drift')
    return {'units': len(units), 'modules': len(modules), 'glossary_groups': len(lesson['GLOSSARY']), 'sources': len(sources), 'identity': 'PASS', 'structural_contract': 'PASS', 'learning_outcomes': 'NOT_RUN', 'semantic_review': 'separate human/content review required'}


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/Study_Skills/'):
            self.path = self.path[len('/Study_Skills'):]
        return super().do_GET()
    def log_message(self, *_args):
        pass


def render_check(slug, lesson, site, output, base_url):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    url = base_url + '/Study_Skills/lessons/' + slug + '.html'
    require((site / 'lessons' / f'{slug}.html').is_file(), f'{slug}: no built page')
    results = {'browser': 'Chromium', 'widths': [], 'paginated_pdf': 'NOT_RUN', 'independent_engine': 'NOT_RUN'}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for width in (1280, 390, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url, wait_until='networkidle')
                require(page.locator('details.unit').count() == len(lesson['UNITS']), f'{width}: missing units')
                require(page.locator('details.unit[open]').count() == 1, f'{width}: initial open units')
                require(page.locator('.answer-body:visible').count() == 0, f'{width}: initial answer leak')
                for u in lesson['UNITS']:
                    page.select_option('#unit-select', u['id'])
                    page.click('#open-unit')
                    page.locator('#'+u['id']+' .prediction').wait_for(state='visible')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'{width}/{u["id"]}: root overflow')
                    require(page.locator('details.unit[open]').count() == 1, f'{width}: multiple open units')
                    if u['id'] in ('U05','U20','U29'):
                        page.locator('#'+u['id']).screenshot(path=str(output / f'{width}-{u["id"]}.png'))
                page.select_option('#unit-select', lesson['UNITS'][0]['id'])
                page.click('#open-unit')
                uid = lesson['UNITS'][0]['id']
                page.click('#'+uid+' [data-help-for] > summary')
                require(page.locator('#'+uid+' .hint-body').is_visible(), f'{width}: hint does not open')
                require(page.locator('#help-'+uid).is_visible(), f'{width}: help exposure not tracked')
                page.click('#'+uid+' [data-answer-for] > summary')
                require(page.locator('#'+uid+' .answer-body').is_visible(), f'{width}: answer does not open')
                page.fill('#note-'+uid, '页面测试：这是临时自评笔记，不是学习成绩。')
                page.select_option('#evidence-'+uid, 'assisted')
                page.locator('#'+uid+' .save-notes').click()
                require('已保存' in page.locator('#note-status').inner_text(), f'{width}: save not confirmed')
                page.reload(wait_until='networkidle')
                require(page.locator('#note-'+uid).input_value().startswith('页面测试'), f'{width}: note restore failed')
                require(page.locator('#evidence-'+uid).input_value() == 'assisted', f'{width}: evidence restore failed')
                require(page.locator('#help-'+uid).is_visible(), f'{width}: help history lost')
                require(page.locator('.answer-body:visible').count() == 0, f'{width}: restored notes exposed answer')
                page.fill('#glossary-filter', 'CIDR')
                require(0 < page.locator('.glossary-entry:visible').count() < len(lesson['GLOSSARY']), f'{width}: glossary filter failed')
                page.evaluate('localStorage.clear()')
                require(not errors, f'{width}: browser errors {errors}')
                results['widths'].append({'width':width,'all_units_overflow':'PASS','prediction_visibility':'PASS','help_answer_controls':'PASS','explicit_save_restore':'PASS','glossary_filter':'PASS'})
                context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':900})
            page = context.new_page()
            page.goto(url,wait_until='networkidle')
            require(page.locator('.unit').count() == len(lesson['UNITS']), 'no-JS: missing lesson text')
            require(page.locator('.unit').first.locator('.prediction').is_visible(), 'no-JS: first prediction absent')
            require(page.locator('.answer-body:visible').count() == 0, 'no-JS: answer leak')
            page.locator('.unit').first.locator('[data-answer-for] > summary').click()
            require(page.locator('.unit').first.locator('.answer-body').is_visible(), 'no-JS: native details broken')
            page.screenshot(path=str(output / '390-nojs.png'),full_page=False)
            results['no_javascript']='PASS'
            context.close()
            context=browser.new_context(viewport={'width':1280,'height':900})
            page=context.new_page();page.goto(url,wait_until='networkidle')
            page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
            page.emulate_media(media='print')
            require(page.locator('.unit[open]').count()==len(lesson['UNITS']), 'print: units not expanded')
            require(page.locator('.print-answers').is_visible(), 'print: separate answers missing')
            require(page.locator('.unit .feedback:visible').count()==0, 'print: feedback leaked into student pages')
            require(page.locator('.print-answer').count()==len(lesson['UNITS']), 'print: answer appendix incomplete')
            page.screenshot(path=str(output/'print-media.png'),full_page=False)
            results['print_media']='PASS'
            context.close()
        finally:
            browser.close()
    return results


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--built-site',type=pathlib.Path);parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path('/tmp/microcourse-evidence'))
    args=parser.parse_args();manifest=json.loads(MANIFEST.read_text())
    lessons={slug:json.loads((SOURCE/f'{slug}.json').read_text()) for slug,cfg in manifest.items() if cfg.get('layout')=='lesson-microcourse'}
    report={slug:validate(slug,lesson) for slug,lesson in lessons.items()}
    if args.built_site:
        site=args.built_site.resolve()
        handler=functools.partial(SiteHandler,directory=str(site))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            for slug,lesson in lessons.items():
                report[slug]['render']=render_check(slug,lesson,site,args.output/slug,f'http://127.0.0.1:{server.server_port}')
        finally:
            server.shutdown();server.server_close()
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'microcourse-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print('PASS: microcourse observable contracts. No learning-outcome or paginated-PDF claim.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
