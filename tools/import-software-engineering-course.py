#!/usr/bin/env python3
"""Import the complete authored course into canonical lesson/Pages paths.
Does not commit or push. Validates the source payload before changing files.
"""
from pathlib import Path
import hashlib
import json
import lzma
import re
import subprocess
ROOT = Path(__file__).resolve().parents[1]
SLUG = 'software-engineering-two-hour-primer-20260913'
EXPECTED = '6b8b3df6cece312d01be15013ef97356d986f60c08e1d42a6ee77c3e0223bf89'
CANONICAL_HASH = 'efbc455c112744937764468ebcaca956134d4b046cf104e15f677b1fe8304ccf'
raw = lzma.decompress(b''.join((ROOT / f'tools/.course-import/part-{i}').read_bytes() for i in range(7)))
assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'Payload integrity failure'
lesson = json.loads(raw)
assert lesson['LESSON_ID'] == SLUG

def normalize(value):
    # Recover intended bold spans next to CJK punctuation; preserve code verbatim.
    blocks = re.split(r'(<pre\b[\s\S]*?</pre>|<script\b[\s\S]*?</script>)', value, flags=re.I)
    for i in range(0, len(blocks), 2):
        text = blocks[i].replace('<strong>', '**').replace('</strong>', '**')
        blocks[i] = re.sub(r'\*\*([^*]+?)\*\*', r'<strong>\1</strong>', text)
    return ''.join(blocks)

for key, value in list(lesson.items()):
    if key.endswith('_HTML'):
        lesson[key] = normalize(value)
raw = (json.dumps(lesson, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
assert hashlib.sha256(raw).hexdigest() == CANONICAL_HASH, 'Canonical transformation drift'
canonical = ROOT / f'skills/learning-page-design-publisher/lessons/{SLUG}.json'
if canonical.exists():
    assert canonical.read_bytes() == raw, 'Refuse overwriting a divergent lesson'
else:
    canonical.write_bytes(raw)
registry = ROOT / 'skills/learning-page-design-publisher/term-overrides.yml'
old = registry.read_text(encoding='utf-8')
if f'\n{SLUG}:\n' not in '\n' + old:
    entry = SLUG + ':\n  checklist: ' + json.dumps(lesson['TERMS_CHECKLIST_LABEL'], ensure_ascii=False) + '\n  html: |\n'
    entry += '\n'.join('    ' + line for line in lesson['TERMS_HTML'].splitlines()) + '\n'
    registry.write_text(old + ('' if old.endswith('\n') else '\n') + '\n' + entry, encoding='utf-8')
index = ROOT / 'docs/index.html'
text = index.read_text(encoding='utf-8')
if f'lessons/{SLUG}.html' not in text:
    needle = '<section class="grid" aria-label="课程列表">'
    assert text.count(needle) == 1, 'Homepage insertion point changed'
    card = f'\n<a class="card" href="lessons/{SLUG}.html"><span class="tag">SOFTWARE ENGINEERING · 2 HOURS</span><h2>{lesson["TITLE"]}</h2><p>一张宏观地图与六条主线：页面和接口、数据与状态、权限和租户、支付计费、移动端，以及从自动验证到可靠交付。包含分段练习、综合排错与参考答案。</p><div class="meta"><time datetime="2026-09-13">2026-09-13</time> · 120 min · 入门 → 工程判断 →</div></a>'
    index.write_text(text.replace(needle, needle + card, 1), encoding='utf-8')
layout = ROOT / 'docs/_layouts/lesson.html'
text = layout.read_text(encoding='utf-8')
marker = '/* Print disclosure: restore screen state without changing saved progress. */'
if marker not in text:
    needle = '  keys.forEach(k=>sync(k,!!st.checks[k]));upd();'
    assert text.count(needle) == 1, 'Layout print insertion point changed'
    patch = '''  /* Print disclosure: restore screen state without changing saved progress. */
  let printState=null;
  window.addEventListener('beforeprint',()=>{
    if(printState)return;
    printState={details:[...document.querySelectorAll('details')].map(e=>[e,e.open]),hints:[...document.querySelectorAll('#h2,#h3,#final-answer')].map(e=>[e,e.hidden])};
    printState.details.forEach(([e])=>e.open=true);
    printState.hints.forEach(([e])=>e.hidden=false);
  });
  window.addEventListener('afterprint',()=>{
    if(!printState)return;const snapshot=printState;printState=null;
    snapshot.details.forEach(([e,v])=>e.open=v);
    snapshot.hints.forEach(([e,v])=>e.hidden=v);
  });
'''
    layout.write_text(text.replace(needle, patch + needle, 1), encoding='utf-8')
subprocess.run(['python3', str(ROOT / 'tools/build-lessons.py')], cwd=ROOT, check=True)
print('IMPORTED', SLUG, 'canonical sha256=' + CANONICAL_HASH)
