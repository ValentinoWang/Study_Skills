#!/usr/bin/env python3
"""Actual browser QA of the Jekyll-built lesson plus shared-layout regressions."""
from pathlib import Path
import hashlib
import json
import sys
import threading
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
OUT = ROOT / 'course-qa'
OUT.mkdir(exist_ok=True)
SLUG = 'software-engineering-two-hour-primer-20260913'
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1',8765),partial(QuietHandler,directory=str(SITE)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report = {'scope':'Jekyll-built artifact, not yet public Pages readback','pages':[],'failures':[]}
def check(ok,message):
    if not ok: report['failures'].append(message)
pages = sorted((ROOT/'skills/learning-page-design-publisher/lessons').glob('*.json'))
with sync_playwright() as p:
    browser = p.chromium.launch()
    for source in pages:
        slug = source.stem
        record = {'slug':slug,'viewports':[]}
        for width in (1280,390):
            context = browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
            page = context.new_page()
            errors = []
            page.on('pageerror',lambda e:errors.append(str(e)))
            response = page.goto(f'http://127.0.0.1:8765/lessons/{slug}.html',wait_until='networkidle')
            check(response.status == 200,f'{slug}/{width}: HTTP not 200')
            dimensions = page.evaluate('''() => ({root:document.documentElement.scrollWidth,viewport:document.documentElement.clientWidth,terms:document.getElementById('terms').offsetTop,orient:document.getElementById('orient').offsetTop,math:[...document.querySelectorAll('math[display="block"]')].map(m=>({display:getComputedStyle(m).display,wrapped:!!m.closest('.formula-scroll'),width:m.getBoundingClientRect().width,height:m.getBoundingClientRect().height}))})''')
            check(dimensions['root'] <= dimensions['viewport'],f'{slug}/{width}: root overflow {dimensions}')
            check(dimensions['terms'] < dimensions['orient'],f'{slug}/{width}: terminology order')
            check(not errors,f'{slug}/{width}: JS errors {errors}')
            check(all(m['wrapped'] and m['width'] > 0 and m['height'] > 0 and m['display'] not in ('block','flex','grid') for m in dimensions['math']),f'{slug}/{width}: MathML geometry/layout')
            check(page.locator('#terms details summary .term-gloss').count() == page.locator('#terms details').count(),f'{slug}/{width}: gloss count')
            record['viewports'].append({'width':width,'dimensions':dimensions,'js_errors':errors})
            if slug == SLUG:
                page.screenshot(path=str(OUT/f'course-{width}-hero.png'))
                if width == 1280:
                    for target in ('track-ui','track-data','track-auth','track-pay','track-mobile','track-delivery','exercise'):
                        page.locator('#'+target).scroll_into_view_if_needed()
                        page.screenshot(path=str(OUT/f'{target}.png'))
                check(page.locator('#draft').count() == 1,f'{slug}: duplicate draft')
                page.locator('#draft').fill('验收测试：先验证跨租户拒绝，再验证并发与重复事件。')
                page.reload(wait_until='networkidle')
                check('跨租户' in page.locator('#draft').input_value(),f'{slug}: draft not persisted')
                check(page.locator('#final-answer').is_hidden(),f'{slug}: answer unexpectedly visible')
                for target in ('h2','h3','final-answer'):
                    page.locator(f'[data-reveal="{target}"]').click()
                    check(page.locator('#'+target).is_visible(),f'{slug}: reveal {target}')
                check(page.locator('.progress [data-progress="answer"]').is_checked(),f'{slug}: answer progress')
                page.locator('#reset').click()
                check(page.locator('#draft').input_value() == '' and page.locator('#final-answer').is_hidden(),f'{slug}: reset')
                if width == 1280:
                    snapshot = '''() => ({details:[...document.querySelectorAll('details')].map(e=>e.open),hidden:[...document.querySelectorAll('#h2,#h3,#final-answer')].map(e=>e.hidden),saved:localStorage.getItem('study:'+document.body.dataset.lessonId)})'''
                    before = page.evaluate(snapshot)
                    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
                    check(page.locator('details:not([open])').count() == 0 and page.locator('#final-answer').is_visible(),'Print disclosures not opened')
                    page.emulate_media(media='print')
                    page.pdf(path=str(OUT/'software-engineering-two-hour-primer.pdf'),format='A4',print_background=True,prefer_css_page_size=True)
                    page.emulate_media(media='screen')
                    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
                    after = page.evaluate(snapshot)
                    check(before == after,'Print changed persisted or on-screen learning state')
            context.close()
        report['pages'].append(record)
    browser.close()
server.shutdown()
raw = (SITE/'lessons'/f'{SLUG}.html').read_bytes()
report['built_html_sha256'] = hashlib.sha256(raw).hexdigest()
soup = BeautifulSoup(raw,'html.parser')
ids = [x['id'] for x in soup.select('[id]')]
check(len(ids) == len(set(ids)),'Duplicate element IDs in published HTML')
check(all(a['href'][1:] in ids for a in soup.select('a[href^="#"]')),'Broken in-page anchors')
report['new_lesson'] = {'core_term_cards':len(soup.select('#terms details')),'source_count':len(soup.select('[id^="source-s"]')),'math_count':len(soup.select('math')),'stage_count':len(soup.select('[id^="track-"]'))}
report['passed'] = not report['failures']
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if report['passed'] else 1)
