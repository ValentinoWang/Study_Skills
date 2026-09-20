"""Learning Figure v2: model -> measured scene -> SVG + linear reading view.

Coordinates are generated, never authored in the semantic model. The supported
surface is deliberately small; an unknown kind/operation is BLOCKED, not ignored.
"""
from __future__ import annotations

import copy
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('skills/learning-figure')
SLUG_RE = re.compile(r'^[a-z][a-z0-9-]*$')
KINDS = {'sequence', 'comparison', 'ownership'}
VERSION = '2.0.0'

class ContractError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def safe_path(root: Path, relative: str) -> Path:
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()) or Path(relative).is_absolute():
        raise ContractError(f'FIG-MODEL-001: unsafe repository path {relative!r}')
    return p


def profile(root: Path = ROOT) -> dict:
    return json.loads((root / BASE / 'profiles/readable-v2.json').read_text())


def manifest(root: Path = ROOT) -> dict:
    return json.loads((root / 'skills/learning-page-design-publisher/lesson-manifest.json').read_text())


def entries(root: Path = ROOT):
    for lesson, cfg in manifest(root).items():
        for ref in cfg.get('figures', []):
            if not isinstance(ref, dict) or not ref.get('model'):
                raise ContractError(f'BLOCKED_UNSUPPORTED: {lesson}: migrate legacy figure to a v2 model; do not skip it')
            model = json.loads(safe_path(root, ref['model']).read_text())
            validate_model(model, root)
            if ref.get('id') != model['id']:
                raise ContractError('FIG-MODEL-001: manifest/model identity mismatch')
            yield lesson, cfg, ref, model


def validate_model(model: dict, root: Path = ROOT) -> None:
    from jsonschema import Draft202012Validator
    schema = json.loads((root / BASE / 'schema/figure-v2.schema.json').read_text())
    problems = sorted(Draft202012Validator(schema).iter_errors(model), key=lambda e: str(e.path))
    if problems:
        raise ContractError('FIG-MODEL-001: ' + '; '.join(f'{list(e.path)} {e.message}' for e in problems[:5]))
    if model['kind'] not in KINDS:
        raise ContractError('BLOCKED_UNSUPPORTED: unknown figure kind')
    bindings = model['bindings']
    for name, binding in bindings.items():
        if not all(binding.get(k) for k in ('label', 'definition_id', 'meaning', 'source', 'example')):
            raise ContractError(f'FIG-CONTENT-001: incomplete binding {name}')
    if model['kind'] == 'sequence':
        actors = [a['id'] for a in model['actors']]
        if len(set(actors)) != len(actors):
            raise ContractError('FIG-MODEL-001: duplicate actor')
        seen = set()
        for event in model['events']:
            if event['id'] in seen or any(x not in seen for x in event.get('after', [])):
                raise ContractError('FIG-MODEL-001: duplicate event or forward/cyclic after dependency')
            seen.add(event['id'])
            if event['type'] == 'message':
                if event['from'] not in actors or event['to'] not in actors or event['from'] == event['to']:
                    raise ContractError('FIG-MODEL-001: invalid message endpoints')
            elif event.get('actor') not in actors:
                raise ContractError('FIG-MODEL-001: event actor is missing')
            keys = set(event.get('payload', {}))
            if event['type'] == 'compare_write': keys.add(event['field'])
            if keys - set(bindings):
                raise ContractError(f'FIG-CONTENT-001: unbound fields {sorted(keys - set(bindings))}')
        simulate(model)
    elif model['kind'] == 'comparison':
        if not model.get('rows') or any(r['field'] not in bindings for r in model['rows']):
            raise ContractError('FIG-CONTENT-001: comparison row has no binding')
    else:
        groups = model.get('groups', [])
        ids = [g['id'] for g in groups] + [c['id'] for g in groups for c in g['children']]
        if not groups or len(ids) != len(set(ids)):
            raise ContractError('FIG-MODEL-001: missing/duplicate ownership objects')


def simulate(model: dict) -> dict:
    """A teaching simulator, NOT a production payment implementation.

Atomic credit commits its processed key, ledger and balance together. A fault
before commit mutates none of them; a lost response after commit cannot undo it.
"""
    state = copy.deepcopy(model.get('initial_state', {}))
    applied = set()
    ledger = []
    results = {}
    for e in model.get('events', []):
        typ = e['type']
        result = {'status': 'observed'}
        if typ == 'compare_write':
            old = state.get(e['field'])
            ok = old == e['expected']
            if ok: state[e['field']] = e['value']
            result = {'status': 'committed' if ok else 'conflict', 'code': 200 if ok else 409,
                      'before': old, 'current': state[e['field']], 'expected': e['expected']}
        elif typ == 'atomic_credit':
            if not e.get('verified') or e['amount'] <= 0:
                raise ContractError('FIG-MODEL-001: atomic_credit requires a verified positive amount')
            key = e['business_key']
            if key in applied:
                result = {'status': 'duplicate', 'code': 200}
            elif e.get('fault') == 'before_commit':
                result = {'status': 'retryable', 'code': 503}
            else:
                applied.add(key)
                ledger.append({'key': key, 'amount': e['amount']})
                state['balance'] = state.get('balance', 0) + e['amount']
                result = {'status': 'committed', 'code': 200}
            result.update(balance=state.get('balance', 0), ledger_entries=len(ledger))
        elif typ == 'message' and e.get('result_of'):
            if e['result_of'] not in results:
                raise ContractError('FIG-MODEL-001: response references an unavailable result')
            result = copy.deepcopy(results[e['result_of']])
        results[e['id']] = result
    for key, value in model.get('expected_final', {}).items():
        actual = len(ledger) if key == 'ledger_entries' else state.get(key)
        if actual != value:
            raise ContractError(f'FIG-MODEL-001: expected final {key}={value}, observed {actual}')
    return {'state': state, 'ledger': ledger, 'results': results}


def event_lines(model: dict, e: dict, simulation: dict) -> list[str]:
    b = model['bindings']
    lines = [e['label']]
    for key, value in e.get('payload', {}).items():
        lines.append(f"{b[key]['label']}：{value}")
    r = simulation['results'][e['id']]
    if e['type'] == 'compare_write':
        lines += [f"期望：{r['expected']}；当前：{r['before']}",
                  f"匹配，原子写入 → {r['current']}" if r['status'] == 'committed' else f"不匹配，拒绝写入\n当前版本保持 {r['current']}"]
    elif e['type'] == 'atomic_credit':
        lines += [f"业务键：{e['business_key']}"]
        if r['status'] == 'committed': lines += ['唯一占位、记账、余额一起提交']
        elif r['status'] == 'duplicate': lines += ['已提交：本次不再记账']
        else: lines += ['提交前失败：不占位、不记账，可重试']
        lines += [f"余额：{r['balance']} 元；账本：{r['ledger_entries']} 笔"]
    elif e.get('result_of'):
        names = {'committed': '已提交', 'conflict': '版本冲突', 'duplicate': '已处理，不重复', 'retryable': '可重试'}
        lines += [f"{r['code']} · {names[r['status']]}"]
    return lines


class Measurer:
    """Measure actual SVG glyph bounds under both declared font families."""
    def __init__(self, page, config: dict):
        self.page, self.config, self.cache = page, config, {}
        page.set_content('<!doctype html><meta charset="utf-8"><svg xmlns="http://www.w3.org/2000/svg" width="2000" height="200"><text id="probe" x="0" y="80"></text></svg>')
        page.evaluate('async () => { await document.fonts.ready; }')

    def measure(self, text: str, size: int = 20) -> dict:
        key = (text, size)
        if key not in self.cache:
            self.cache[key] = self.page.evaluate('''async ({text,size,fonts}) => {
                const t=document.getElementById('probe'), boxes=[];
                for(const family of fonts) {
                  t.style.fontFamily=family;t.style.fontSize=size+'px';t.textContent=text;
                  await document.fonts.ready;
                  const b=t.getBBox();boxes.push({width:b.width,height:b.height});
                }
                return {width:Math.ceil(Math.max(...boxes.map(x=>x.width)))+2,
                        height:Math.ceil(Math.max(...boxes.map(x=>x.height)))};
            }''', {'text': text, 'size': size, 'fonts': self.config['measurement_fonts']})
        return self.cache[key]

    def wrap(self, text: str, width: float, size: int = 20) -> list[str]:
        out=[]
        for source_line in text.split('\n'):
            line=''
            for token in re.findall(r'[A-Za-z0-9_./=-]+|\s+|.', source_line):
                if self.measure(token, size)['width'] > width:
                    raise ContractError(f'FIG-READ-001: unbreakable label {token!r} exceeds width; enlarge/split the model, never truncate')
                if line and self.measure(line+token, size)['width'] > width:
                    out.append(line.rstrip());line=token.lstrip()
                else: line += token
            out.append(line)
        return out


class Scene:
    def __init__(self, prefix: str, width: float, model: dict, measure: Measurer):
        self.prefix,self.width,self.model,self.measure = prefix,width,model,measure
        self.nodes=[];self.labels=[];self.edges=[];self.guides=[];self.height=0

    def label(self, ident, owner, role, text, x, y, width, terms=(), size=20):
        lines=self.measure.wrap(text,width,size)
        self.labels.append(dict(id=ident,owner=owner,role=role,text=text,lines=lines,x=x,y=y,size=size,terms=list(terms)))
        return len(lines)*32

    def node(self, ident, x,y,w,h,text,role='event',parent='',tone='neutral',terms=()):
        self.nodes.append(dict(id=ident,x=x,y=y,width=w,height=h,role=role,parent=parent,tone=tone))
        self.label(ident+'-text',ident,'node',text,x+20,y+16,w-40,terms)

    def edge(self, ident,x1,y,x2,source,target,role='message'):
        self.edges.append(dict(id=ident,x1=x1,y1=y,x2=x2,y2=y,source=source,target=target,role=role))

    def svg(self):
        esc=lambda s:html.escape(str(s),quote=True)
        p=self.prefix
        title=f'{p}-title';desc=f'{p}-desc'
        chunks=[f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{title} {desc}" data-figure-id="{esc(self.model["id"])}" data-renderer="learning-figure-v2" viewBox="0 0 {self.width:g} {self.height:g}" width="{self.width:g}" height="{self.height:g}" style="font-family:{esc(self.measure.config["font_family"])};background:#fff">',
                f'<title id="{title}">{esc(self.model["question"])}</title><desc id="{desc}">{esc(self.model["takeaway"])}</desc>']
        for ident,x in self.guides:
            chunks.append(f'<line data-guide-id="{ident}" x1="{x:g}" x2="{x:g}" y1="94" y2="{self.height-32:g}" stroke="#667085" stroke-width="1" stroke-dasharray="4 7"/>')
        for e in self.edges:
            chunks.append(f'<line id="{p}-{e["id"]}" data-edge-id="{e["id"]}" data-role="message" data-from="{e["source"]}" data-to="{e["target"]}" x1="{e["x1"]:g}" y1="{e["y1"]:g}" x2="{e["x2"]:g}" y2="{e["y2"]:g}" stroke="#475467" stroke-width="2"/>')
            direction=1 if e['x2']>e['x1'] else -1
            x,y=e['x2'],e['y2']
            points=f'{x:g},{y:g} {x-direction*10:g},{y-5:g} {x-direction*10:g},{y+5:g}'
            chunks.append(f'<polygon id="{p}-{e["id"]}-head" data-head-for="{e["id"]}" points="{points}" fill="#475467"/>')
        tones={'neutral':('#f8fafc','#475467'),'actor':('#eef2ff','#4f46e5'),'good':('#edf8f2','#16704a'),'bad':('#fff4f2','#b42318'),'panel':('#f8fafc','#475467')}
        for n in self.nodes:
            fill,stroke=tones[n['tone']]
            chunks.append(f'<rect id="{p}-{n["id"]}" data-node-id="{n["id"]}" data-parent="{n["parent"]}" data-role="{n["role"]}" x="{n["x"]:g}" y="{n["y"]:g}" width="{n["width"]:g}" height="{n["height"]:g}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        for t in self.labels:
            attrs=f'id="{p}-{t["id"]}" data-label-id="{t["id"]}" data-owner="{t["owner"]}" data-role="{t["role"]}" data-terms="{esc(" ".join(t["terms"]))}" font-size="{t["size"]}" fill="#1d2939"'
            spans=''.join(f'<tspan x="{t["x"]:g}" y="{t["y"]+26+i*32:g}">{esc(line)}</tspan>' for i,line in enumerate(t['lines']))
            chunks.append(f'<text {attrs}>{spans}</text>')
        return '\n'.join(chunks+['</svg>'])+'\n'

    def expected(self):
        return {'guides': [i for i,x in self.guides], 'labels':{t['id']:{k:t[k] for k in ('text','owner','role','terms')} for t in self.labels},
                'nodes':{n['id']:{'parent':n['parent'],'role':n['role']} for n in self.nodes},
                'edges':{e['id']:{'from':e['source'],'to':e['target']} for e in self.edges}}


def make_scene(lesson: str, model: dict, measure: Measurer) -> tuple[Scene,list[dict]]:
    p=lesson+'--'+model['id']
    trace=[]
    if model['kind']=='sequence':
        actors=model['actors'];gap=300;left=32
        width=64+(len(actors)-1)*gap+240
        scene=Scene(p,width,model,measure)
        centers={a['id']:left+120+i*gap for i,a in enumerate(actors)}
        for a in actors:
            scene.node(a['id'],centers[a['id']]-120,28,240,66,a['label'],'actor',tone='actor')
        simulation=simulate(model);y=130
        for i,e in enumerate(model['events']):
            lines=event_lines(model,e,simulation);text='\n'.join(lines)
            terms=list(e.get('payload',{}))
            if e['type']=='compare_write':terms += [e['field']]
            if e['type']=='message':
                x1,x2=centers[e['from']],centers[e['to']]
                w=abs(x2-x1)-64
                h=scene.label(e['id']+'-label',e['id'],'message',text,min(x1,x2)+32,y,w,terms)
                scene.edge(e['id'],x1,y+h+14,x2,e['from'],e['to'])
                route=next(a['label'] for a in actors if a['id']==e['from'])+' → '+next(a['label'] for a in actors if a['id']==e['to'])
                y+=h+58
            else:
                w=min(240,width-64)
                h=len(measure.wrap(text,w-40))*32+32
                x=max(32,min(width-w-32,centers[e['actor']]-w/2))
                outcome=simulation['results'][e['id']]['status']
                tone='bad' if outcome in ('conflict','retryable') else 'good' if outcome=='committed' else 'neutral'
                scene.node(e['id'],x,y,w,h,text,'event',tone=tone,terms=terms)
                route=next(a['label'] for a in actors if a['id']==e['actor'])+' · 本地步骤'
                y+=h+32
            trace.append({'id':e['id'],'route':route,'lines':lines,'after':e.get('after',[])})
        scene.height=y+16
        scene.guides=list(centers.items())
    elif model['kind']=='comparison':
        scene=Scene(p,824,model,measure)
        y=30;panel_w=360
        heights=[max(len(measure.wrap(model['bindings'][r['field']]['label']+'\n'+str(r[s]),280))*32+32 for s in ('before','after')) for r in model['rows']]
        total=116+sum(heights)+24*(len(heights)-1)
        for j,side in enumerate(['before','after']):
            x=32+j*400;ident='panel-'+side
            scene.nodes.append(dict(id=ident,x=x,y=30,width=panel_w,height=total,role='panel',parent='',tone='panel'))
            scene.label(ident+'-title',ident,'node',model['titles'][side],x+20,46,panel_w-40)
            cy=114
            for r,h in zip(model['rows'],heights):
                field=r['field'];text=model['bindings'][field]['label']+'\n'+str(r[side])
                scene.node(side+'-'+field,x+20,cy,320,h,text,parent=ident,tone='good' if side=='after' and r['before']!=r['after'] else 'neutral',terms=[field])
                cy+=h+24
            trace.append({'id':side,'route':model['titles'][side],'lines':[model['bindings'][r['field']]['label']+'：'+str(r[side]) for r in model['rows']],'after':[]})
        scene.height=30+total+32
    else:
        width=64+len(model['groups'])*360+(len(model['groups'])-1)*32
        scene=Scene(p,width,model,measure);maxh=0
        for i,g in enumerate(model['groups']):
            x=32+i*392;children=g['children'];hs=[len(measure.wrap(c['label'],280))*32+32 for c in children]
            total=116+sum(hs)+24*(len(hs)-1);maxh=max(maxh,total)
            scene.nodes.append(dict(id=g['id'],x=x,y=30,width=360,height=total,role='panel',parent='',tone='panel'))
            scene.label(g['id']+'-title',g['id'],'node',g['label'],x+20,46,320)
            cy=114
            for c,h in zip(children,hs):
                scene.node(c['id'],x+20,cy,320,h,c['label'],parent=g['id']);cy+=h+24
            trace.append({'id':g['id'],'route':g['label'],'lines':[c['label'] for c in children],'after':[]})
        scene.height=maxh+62
    return scene,trace


def render_component(lesson: str, model: dict, scene: Scene, trace: list[dict], signature: str) -> str:
    e=lambda s:html.escape(str(s),quote=True)
    svg=scene.svg().rstrip()
    # A distinct DOM namespace for the optional mobile full diagram.
    full=svg.replace(scene.prefix,scene.prefix+'--full')
    ident='fig-'+model['id'];title=ident+'-heading'
    steps=''.join('<li data-event-id="'+e(t['id'])+'"><strong>'+e(t['route'])+'</strong>'+''.join('<p>'+e(line)+'</p>' for line in t['lines'])+'</li>' for t in trace)
    return (f'<figure class="learning-figure lf-v2" id="{ident}" data-figure-id="{e(model["id"])}" data-model-digest="{signature}" aria-labelledby="{title}">\n'
            f'<figcaption id="{title}"><span class="lf-kicker">图解 · 教学示例</span><strong>{e(model["question"])}</strong></figcaption>\n'
            f'<p class="lf-reading">{e(model["reading_order"])}</p>\n'
            f'<div class="lf-wide lf-scroll" tabindex="0" role="region" aria-label="{e(model["question"])}，可横向滚动" style="--lf-min:{math.ceil(scene.width*.84)}px">{svg}</div>\n'
            f'<div class="lf-linear"><ol class="lf-steps">{steps}</ol></div>\n'
            f'<details class="lf-full"><summary>查看完整图（可横向滚动）</summary><div class="lf-scroll" tabindex="0" style="--lf-min:{math.ceil(scene.width*.84)}px">{full}</div></details>\n'
            f'<p class="lf-takeaway"><strong>结论：</strong>{e(model["takeaway"])}</p>\n'
            f'<p class="lf-boundary"><strong>边界：</strong>{e(model["boundary"])}</p>\n</figure>\n')


def environment(config):
    fonts={}
    for family in config['required_font_families']:
        try:
            actual=subprocess.check_output(['fc-match','-f','%{family}',family],text=True).strip()
        except (OSError,subprocess.CalledProcessError) as exc:
            raise ContractError(f'BLOCKED_FONT: fc-match unavailable: {exc}') from exc
        if family not in actual:
            raise ContractError(f'BLOCKED_FONT: required {family}, resolved {actual}; install fonts-noto-cjk')
        fonts[family]=actual
    return {'font_policy':fonts,'renderer_version':VERSION}


def chromium(playwright):
    executable=os.environ.get('FIGURE_CHROMIUM') or shutil.which('chromium') or shutil.which('chromium-browser')
    return playwright.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])


def outputs(root: Path = ROOT) -> dict[Path,bytes]:
    from playwright.sync_api import sync_playwright
    cfg=profile(root);environment(cfg);result={};data={}
    with sync_playwright() as pw:
        browser=chromium(pw);page=browser.new_page();measure=Measurer(page,cfg)
        for lesson,lesson_cfg,ref,model in entries(root):
            signature=digest(json_bytes(model))
            scene,trace=make_scene(lesson,model,measure)
            svg=scene.svg().encode()
            # .svg files are generated mirrors; the JSON is the canonical model.
            result[root/BASE/'figures'/lesson/(model['id']+'.svg')]=svg
            result[root/'docs/assets/figures'/lesson/(model['id']+'.svg')]=svg
            include_path='learning-figures/'+lesson+'/'+model['id']+'.svg'
            result[root/'docs/_includes'/include_path]=svg
            data.setdefault(lesson,{})[model['id']]={
                'model_digest':signature,'question':model['question'],'takeaway':model['takeaway'],
                'reading_order':model['reading_order'],'boundary':model['boundary'],
                'svg_include':include_path,'prefix':scene.prefix,'min_width':math.ceil(scene.width*.84),
                'expected':scene.expected(),'svg_digest':digest(svg),'trace':trace,
                'generator_digest':generator_digest(root)}
        browser.close()
    for lesson,items in data.items():result[root/'docs/_data/learning_figures'/(lesson+'.json')]=json_bytes(items)
    return result


def generator_digest(root: Path = ROOT) -> str:
    paths=sorted((root/'tools/learning_figures').glob('*.py'))+sorted((root/'tools/learning_figures').glob('*.js'))+sorted((root/BASE/'profiles').glob('*.json'))+sorted((root/BASE/'schema').glob('*.json'))
    return digest(b''.join(str(p.relative_to(root)).encode()+b'\0'+p.read_bytes() for p in paths))


def synchronize(root: Path = ROOT, check: bool = False) -> list[str]:
    problems=[]
    # Validate ALL models before writing ANY generated output.
    generated=outputs(root)
    for path,content in generated.items():
        if not path.exists() or path.read_bytes()!=content:
            if check: problems.append(f'FIG-ARTIFACT-001: generated drift {path.relative_to(root)}')
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    return problems


def check_placement(root: Path, cfg: dict, ref: dict, model: dict) -> list[str]:
    """Check canonical anchor/definition order; actual visibility is browser QA."""
    from bs4 import BeautifulSoup
    section=(cfg.get('section_prerequisites',{}).get(ref['section_id']) or {})
    src=safe_path(root,cfg['supplement_source_dir'])/section['file']
    text=src.read_text();soup=BeautifulSoup(text,'html.parser');problems=[]
    anchor=soup.find_all(id=ref['after_id'])
    if len(anchor)!=1:return [f'FIG-INTEGRATION-001: {ref["id"]} requires exactly one #{ref["after_id"]}']
    token='{% include learning-figure.html lesson=page.lesson figure="'+model['id']+'" %}'
    if text.count(token)!=1:problems.append(f'FIG-INTEGRATION-001: {model["id"]}: missing/duplicate build-time include')
    position=text.find(token)
    marker=text.find('id="'+ref['after_id']+'"')
    close=text.find('</'+anchor[0].name+'>',marker)+len(anchor[0].name)+3
    if marker<0 or position<close or text[close:position].strip():
        problems.append(f'FIG-INTEGRATION-001: {model["id"]}: include must immediately follow anchor')
    for key,b in model['bindings'].items():
        defs=soup.find_all(id=b['definition_id'])
        if len(defs)!=1 or text.find('id="'+b['definition_id']+'"')>position:
            problems.append(f'FIG-CONTENT-001: {key}: missing/late/duplicate visible definition')
        elif defs[0].has_attr('hidden') or not defs[0].get_text(strip=True):
            problems.append(f'FIG-CONTENT-001: {key}: empty/hidden definition')
    if 'document.currentScript' in text:problems.append('FIG-INTEGRATION-001: runtime mover remains')
    return problems


def static_check(root: Path = ROOT) -> list[str]:
    problems=[]
    for lesson,cfg,ref,model in entries(root):
        problems += check_placement(root,cfg,ref,model)
        datafile=root/'docs/_data/learning_figures'/(lesson+'.json')
        if not datafile.is_file():problems.append(f'FIG-ARTIFACT-001: missing {datafile}');continue
        data=json.loads(datafile.read_text()).get(model['id'],{})
        if data.get('model_digest')!=digest(json_bytes(model)) or data.get('generator_digest')!=generator_digest(root):
            problems.append(f'FIG-ARTIFACT-001: stale model/generator for {model["id"]}')
        src=root/BASE/'figures'/lesson/(model['id']+'.svg');dst=root/'docs/assets/figures'/lesson/src.name
        if not src.is_file() or not dst.is_file() or src.read_bytes()!=dst.read_bytes() or digest(src.read_bytes())!=data.get('svg_digest'):
            problems.append(f'FIG-ARTIFACT-001: SVG mirror/digest mismatch {model["id"]}')
        inline=root/'docs/_includes/learning-figures'/lesson/src.name
        if not inline.is_file() or (src.is_file() and inline.read_bytes()!=src.read_bytes()):
            problems.append(f'FIG-ARTIFACT-001: inline SVG mirror mismatch {model["id"]}')
        if data.get('svg_include') != 'learning-figures/'+lesson+'/'+src.name:
            problems.append('FIG-ARTIFACT-001: inline SVG reference drift')
        if src.is_file():
            tree=ET.fromstring(src.read_text())
            allowed={'svg','title','desc','g','rect','line','polygon','text','tspan'}
            for element in tree.iter():
                if element.tag.split('}')[-1] not in allowed:
                    problems.append(f'BLOCKED_UNSUPPORTED: SVG element {element.tag}')
                if any(k.lower().startswith('on') or k in ('href','filter','mask','clip-path') for k in element.attrib):
                    problems.append('BLOCKED_UNSUPPORTED: active/external/masked SVG content')
    return problems
