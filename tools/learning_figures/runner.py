"""Browser checks and evidence. No screenshot baselines are auto-approved."""
from __future__ import annotations
import functools
import http.server
import json
from pathlib import Path
import threading
from contextlib import contextmanager
from .core import ROOT, BASE, profile, entries, chromium, digest, json_bytes, environment

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def translate_path(self, path):
        # Serve an unchanged GitHub project-Pages artifact at its deployed baseurl.
        if path.startswith('/Study_Skills/'):
            path=path[len('/Study_Skills'):]
        return super().translate_path(path)

@contextmanager
def serve(directory: Path):
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(directory)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:server.shutdown();server.server_close();thread.join()


def audit_svg(page, selector, expected, *, root=ROOT, legacy=False):
    return page.evaluate((root/'tools/learning_figures/browser.js').read_text(),dict(selector=selector,expected=expected,config=profile(root),legacy=legacy))


def page_contract(page, ref, model, record):
    return page.evaluate('''({ref,model,record})=>{
      const out=[],fail=(message)=>out.push({rule:'FIG-INTEGRATION-001',status:'FAIL',objects:[ref.id],message});
      const all=[...document.querySelectorAll('figure.lf-v2')].filter(e=>e.dataset.figureId===ref.id);
      if(all.length!==1){fail('figure missing or duplicated');return out;}
      const f=all[0],a=document.getElementById(ref.after_id);
      if(f.dataset.modelDigest!==record.model_digest)fail('rendered model digest differs from candidate');
      if(!a||a.nextElementSibling!==f||!f.closest('#'+ref.section_id))fail('wrong build-time insertion point');
      const visible=el=>{for(let p=el;p;p=p.parentElement){const c=getComputedStyle(p);if(c.display==='none'||c.visibility==='hidden'||+c.opacity===0||p.hidden||p.tagName==='DETAILS'&&!p.open&&!el.closest('summary'))return false;}return true;};
      for(const b of Object.values(model.bindings)){
        const ds=[...document.querySelectorAll('[id]')].filter(e=>e.id===b.definition_id);
        if(ds.length!==1||!visible(ds[0])||!(ds[0].compareDocumentPosition(f)&Node.DOCUMENT_POSITION_FOLLOWING))fail('definition missing/hidden/late: '+b.definition_id);
      }
      const steps=[...f.querySelectorAll('.lf-steps>li')];
      for(const p of f.querySelectorAll('.lf-steps p'))if(visible(p)&&matchMedia('screen').matches&&parseFloat(getComputedStyle(p).fontSize)<16)fail('linear-view font too small');
      if(steps.length!==record.trace.length)fail('linear view drops an event');
      const norm=s=>s.replace(/\\s+/g,'');
      for(let i=0;i<record.trace.length;i++){
        const expected=record.trace[i],el=steps[i];
        if(!el||el.dataset.eventId!==expected.id||!expected.lines.every(s=>norm(el.textContent).includes(norm(s))))fail('linear view facts differ from event model');
      }
      if(document.documentElement.scrollWidth>innerWidth+1)fail('page root horizontally overflows');
      const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
      if(ids.length!==new Set(ids).size)fail('duplicate DOM IDs');
      return out;
    }''', {'ref':ref,'model':model,'record':record})


def _audit_site(site: Path, output: Path, *, root=ROOT, engine='chromium', offline=False) -> dict:
    from playwright.sync_api import sync_playwright
    if output.resolve().is_relative_to(site.resolve()):
        raise ValueError('FIG-ARTIFACT-001: evidence directory must be outside artifact')
    output.mkdir(parents=True,exist_ok=True)
    assets={str(p.relative_to(site)):digest(p.read_bytes()) for p in sorted(site.rglob('*')) if p.is_file()}
    font_environment=environment(profile(root))
    required_cases=[('desktop',1280,True,None),('desktop-wide',1440,True,None),('mobile',390,True,None),('narrow-no-js',320,False,None),('fallback',1280,True,'"Noto Serif CJK SC",serif'),('print-media',794,False,None)]
    results=[]
    with serve(site) as url, sync_playwright() as pw:
        try:
            browser=chromium(pw) if engine=='chromium' else pw.webkit.launch(headless=True)
        except Exception as exc:
            report={'status':'BLOCKED','engine':engine,'message':str(exc),'cases':[]}
            (output/'report.json').write_bytes(json_bytes(report));return report
        browser_version=browser.version
        by_lesson={}
        for lesson,cfg,ref,m in entries(root):by_lesson.setdefault(lesson,[]).append((ref,m))
        for lesson,figures in by_lesson.items():
            records=json.loads((root/'docs/_data/learning_figures'/f'{lesson}.json').read_text())
            source=site/'lessons'/f'{lesson}.html'
            if not source.is_file():
                results.append({'lesson':lesson,'status':'FAIL','issues':[{'rule':'FIG-INTEGRATION-001','message':'built lesson missing'}]});continue
            for name,width,js,font in required_cases:
                context=browser.new_context(viewport={'width':width,'height':1000},java_script_enabled=js,device_scale_factor=1)
                page=context.new_page();page.set_default_timeout(8000);runtime_errors=[];page.on('pageerror',lambda e: runtime_errors.append(str(e)))
                if offline:
                    # Explicit offline mode for environments that prohibit navigation.
                    # Original HTML bytes are unchanged; resolve stylesheet bytes from the same artifact.
                    from bs4 import BeautifulSoup
                    from urllib.parse import urlsplit
                    content=source.read_text()
                    page.set_content(content,wait_until='load')
                    for link in BeautifulSoup(content,'html.parser').select('link[rel=stylesheet]'):
                        path=urlsplit(link['href']).path.removeprefix('/Study_Skills/')
                        asset=site/path.lstrip('/') if link['href'].startswith('/') else source.parent/path
                        if not asset.is_file():raise RuntimeError(f'FIG-INTEGRATION-001: missing local CSS {path}')
                        page.evaluate("css=>{const s=document.createElement('style');s.textContent=css;document.head.append(s)}",asset.read_text())
                else:
                    page.goto(f'{url}/lessons/{lesson}.html',wait_until='networkidle')
                page.evaluate("()=>{const s=document.createElement('style');s.textContent='html{scroll-behavior:auto!important}';document.head.append(s)}")
                if name=='print-media':page.emulate_media(media='print')
                if font:page.evaluate("css=>{const s=document.createElement('style');s.textContent=css;document.head.append(s)}",f'.lf-v2 svg text {{font-family:{font}!important}}')
                for ref,m in figures:
                    record=records[m['id']];issues=page_contract(page,ref,m,record);audits=[]
                    base=f'figure.lf-v2[data-figure-id="{m["id"]}"]'
                    if name=='print-media':
                        if page.locator(base+' .lf-linear').is_hidden():issues.append({'rule':'FIG-INTEGRATION-001','status':'FAIL','message':'print trace hidden'})
                    elif width>=821:
                        audits.append(audit_svg(page,base+' .lf-wide svg',record['expected'],root=root))
                    else:
                        # Native details work without page JavaScript. Verify the optional full diagram too.
                        if page.locator(base+' .lf-linear').is_hidden():issues.append({'rule':'FIG-INTEGRATION-001','status':'FAIL','message':'mobile trace hidden'})
                        page.locator(base+' .lf-full summary').click()
                        audits.append(audit_svg(page,base+' .lf-full svg',record['expected'],root=root))
                        page.locator(base+' .lf-full summary').click()
                    for a in audits:issues+=a['issues']
                    if runtime_errors:issues.append({'rule':'FIG-INTEGRATION-001','status':'FAIL','message':'browser script errors: '+str(runtime_errors)})
                    shot=f'{lesson}--{m["id"]}--{name}.png'
                    page.locator(base).screenshot(path=str(output/shot))
                    results.append({'lesson':lesson,'figure':m['id'],'case':name,'viewport':width,'javascript':js,'font_override':font,
                                    'status':'FAIL' if issues else 'PASS','issues':issues,'geometry':audits,'screenshot':shot,
                                    'page_sha256':digest(source.read_bytes()),'model_digest':record['model_digest'],'svg_digest':record['svg_digest']})
                print(lesson,name,'checked',flush=True)
                (output/'partial.json').write_bytes(json_bytes(results))
                context.close()
        browser.close()
    final_assets={str(p.relative_to(site)):digest(p.read_bytes()) for p in sorted(site.rglob('*')) if p.is_file()}
    if final_assets!=assets:
        results.append({'status':'FAIL','issues':[{'rule':'FIG-ARTIFACT-001','message':'artifact changed during audit'}]})
    report={'status':'PASS' if results and all(r['status']=='PASS' for r in results) else 'FAIL','engine':engine,'browser_version':browser_version,'transport':'offline HTML + exact artifact CSS bytes' if offline else 'local HTTP artifact',
            'scope':'built candidate pages; CSS geometry, source identity, static insertion, no-JS, linear mobile/print-media. Print-media is not paginated PDF proof.',
            'visual_review':'NOT_RUN','public_readback':'NOT_RUN','artifact_files':assets,'artifact_digest':digest(json_bytes(assets)),
            'font_environment':font_environment,'cases':results}
    (output/'report.json').write_bytes(json_bytes(report));return report


def audit_site(site: Path, output: Path, *, root=ROOT, engine='chromium', offline=False) -> dict:
    """Fail closed and preserve the exact blocker rather than silently skipping QA."""
    if output.resolve().is_relative_to(site.resolve()):
        raise ValueError('evidence must be outside artifact')
    try:
        return _audit_site(site,output,root=root,engine=engine,offline=offline)
    except Exception as exc:
        output.mkdir(parents=True,exist_ok=True)
        report={'status':'BLOCKED','engine':engine,'transport':'offline' if offline else 'local HTTP',
                'message':str(exc),'cases':[],'visual_review':'NOT_RUN','public_readback':'NOT_RUN'}
        (output/'report.json').write_bytes(json_bytes(report))
        return report
