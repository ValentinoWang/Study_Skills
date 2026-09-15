#!/usr/bin/env python3
"""Real historical red SVGs + model, geometry and anti-bypass regression tests.

Every failing example must fail the intended rule, not merely any unrelated gate.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from playwright.sync_api import sync_playwright
from learning_figures.core import (ROOT, BASE, ContractError, validate_model, simulate,
    profile, chromium, entries, Measurer, make_scene, check_placement, digest, json_bytes)
from learning_figures.runner import audit_svg

SLUG='software-engineering-two-hour-primer-20260913'

def read_model(name):
    return json.loads((ROOT/BASE/'figures'/SLUG/(name+'.figure.json')).read_text())

class FigureRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start();cls.browser=chromium(cls.pw)
        cls.page=cls.browser.new_page(viewport={'width':1400,'height':1000})
        measure=Measurer(cls.page,profile());cls.scenes={}
        for name in ('state-to-view','optimistic-lock-race','idempotent-webhook'):
            scene,trace=make_scene(SLUG,read_model(name),measure)
            cls.scenes[name]=(scene.svg(),scene.expected())
        own=json.loads((ROOT/'tests/learning-figures/green/ownership.figure.json').read_text())
        scene,_=make_scene('fixture',own,measure);cls.scenes['ownership']=(scene.svg(),scene.expected())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()

    def check(self,name='optimistic-lock-race',mutation=None,font=None):
        svg,expected=self.scenes[name]
        self.page.set_content('<style>body{margin:0}</style>'+svg)
        if font:self.page.add_style_tag(content=f'svg text{{font-family:{font}!important}}')
        if mutation:self.page.evaluate(mutation)
        return audit_svg(self.page,'svg',expected)

    def must_fail(self,result,rule):
        self.assertNotEqual(result['status'],'PASS')
        self.assertTrue(any(x['rule']==rule for x in result['issues']),result['issues'])

    def test_green_current_diagrams(self):
        for name in self.scenes:
            with self.subTest(name=name):self.assertEqual(self.check(name)['issues'],[])

    def test_green_fallback_fonts(self):
        for name in self.scenes:
            with self.subTest(name=name):self.assertEqual(self.check(name,font='"Noto Serif CJK SC",serif')['issues'],[])

    def test_real_historical_cards_cover_labels(self):
        for name in ('optimistic-lock-race','idempotent-webhook'):
            with self.subTest(name=name):
                svg=(ROOT/'tests/learning-figures/red'/(name+'.svg')).read_text()
                self.page.set_content('<style>svg{width:960px;font-family:"Noto Sans CJK SC"}</style>'+svg)
                self.must_fail(audit_svg(self.page,'svg',{},legacy=True),'FIG-GEOM-002')

    def test_removing_handmade_safe_zones_does_not_hide_collision(self):
        svg=(ROOT/'tests/learning-figures/red/idempotent-webhook.svg').read_text()
        self.page.set_content('<style>svg{width:960px;font-family:"Noto Sans CJK SC"}</style>'+svg)
        self.page.evaluate("document.querySelectorAll('[data-protect]').forEach(x=>x.remove())")
        self.must_fail(audit_svg(self.page,'svg',{},legacy=True),'FIG-GEOM-002')

    def test_unregistered_visible_text(self):
        r=self.check(mutation="""()=>{const x=document.querySelector('text').cloneNode(true);x.removeAttribute('data-label-id');x.removeAttribute('id');document.querySelector('svg').append(x)}""")
        self.must_fail(r,'FIG-COVERAGE-001')

    def test_removing_expected_label(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').remove()"),'FIG-COVERAGE-001')

    def test_hiding_expected_label(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').style.display='none'"),'FIG-COVERAGE-001')

    def test_changing_owner_cannot_bypass_collision(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').dataset.owner='anything'"),'FIG-COVERAGE-001')

    def test_changing_value_cannot_make_text_fit(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').textContent='x'"),'FIG-COVERAGE-001')

    def test_duplicate_label(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('svg').append(document.querySelector('text').cloneNode(true))"),'FIG-COVERAGE-001')

    def test_label_term_metadata_is_checked(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text[data-terms]').dataset.terms='mystery'"),'FIG-COVERAGE-001')

    def test_text_text_collision(self):
        self.must_fail(self.check(mutation="""()=>{const t=[...document.querySelectorAll('text')];const a=t[0].querySelector('tspan'),b=t[1].querySelector('tspan');b.setAttribute('x',a.getAttribute('x'));b.setAttribute('y',a.getAttribute('y'));}"""),'FIG-GEOM-001')

    def test_foreign_card_collision(self):
        self.must_fail(self.check(mutation="""()=>{const t=document.querySelector('[data-label-id="save-a-label"] tspan');t.setAttribute('x','360');t.setAttribute('y','530');}"""),'FIG-GEOM-002')

    def test_painted_line_width(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('[data-edge-id=read-a]').setAttribute('stroke-width','100')"),'FIG-GEOM-002')

    def test_arrowhead_has_real_extent(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('polygon').setAttribute('points','152,208 300,140 300,270')"),'FIG-GEOM-002')

    def test_detached_arrowhead(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('polygon').setAttribute('points','20,208 30,203 30,213')"),'FIG-MODEL-001')

    def test_removing_connector(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('[data-edge-id]').remove()"),'FIG-COVERAGE-001')

    def test_wrong_direction(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('[data-edge-id]').setAttribute('x2','800')"),'FIG-MODEL-001')

    def test_path_is_not_a_silent_escape(self):
        self.must_fail(self.check(mutation="""()=>{const l=document.querySelector('[data-edge-id]'),p=document.createElementNS(l.namespaceURI,'path');p.setAttribute('d','M0 0L100 100');l.replaceWith(p)}"""),'FIG-COVERAGE-001')

    def test_mask_is_blocked(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').setAttribute('mask','url(#fake)')"),'FIG-COVERAGE-001')

    def test_rotation_is_blocked(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').setAttribute('transform','rotate(20)')"),'FIG-CONTAIN-001')

    def test_translated_geometry_is_measured(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').setAttribute('transform','translate(-100,0)')"),'FIG-CONTAIN-001')

    def test_scaling_to_unreadable_is_rejected(self):
        self.must_fail(self.check(mutation="()=>{const s=document.querySelector('svg');s.style.width='360px';s.style.height='auto'}"),'FIG-READ-001')

    def test_text_outside_canvas(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('tspan').setAttribute('x','-50')"),'FIG-CONTAIN-001')

    def test_contrast(self):
        self.must_fail(self.check(mutation="()=>document.querySelector('text').setAttribute('fill','#eeeeee')"),'FIG-A11Y-001')

    def test_parent_contains_children(self):
        self.assertEqual(self.check('ownership')['issues'],[])

    def test_owner_parent_mismatch(self):
        self.must_fail(self.check("ownership",mutation="()=>document.querySelector('[data-node-id=coach-a]').dataset.parent='tenant-b'"),'FIG-COVERAGE-001')

    def test_duplicate_actor_invalid(self):
        m=read_model('optimistic-lock-race');m['actors'][1]['id']=m['actors'][0]['id']
        with self.assertRaises(ContractError):validate_model(m)

    def test_unknown_endpoint_invalid(self):
        m=read_model('optimistic-lock-race');m['events'][0]['from']='missing'
        with self.assertRaises(ContractError):validate_model(m)

    def test_order_dependency_invalid(self):
        m=read_model('optimistic-lock-race');m['events'][0]['after']=['reply-b']
        with self.assertRaises(ContractError):validate_model(m)

    def test_author_coordinates_rejected(self):
        m=read_model('optimistic-lock-race');m['events'][0]['x']=42
        with self.assertRaises(ContractError):validate_model(m)

    def test_unbound_payload_invalid(self):
        m=read_model('optimistic-lock-race');m['events'][0]['payload']['mystery']=1
        with self.assertRaises(ContractError):validate_model(m)

    def test_optimistic_winner_symmetric(self):
        m=read_model('optimistic-lock-race');out=simulate(m)
        for e in m['events']:
            for key in ('from','to'):
                if e.get(key)=='coach-a':e[key]='coach-b'
                elif e.get(key)=='coach-b':e[key]='coach-a'
        self.assertEqual(simulate(m)['state'],out['state'])
        self.assertEqual(simulate(m)['results']['reject-b']['status'],'conflict')

    def test_duplicate_payment_one_entry(self):
        out=simulate(read_model('idempotent-webhook'))
        self.assertEqual(out['state']['balance'],100);self.assertEqual(len(out['ledger']),1)

    def test_before_commit_fault_retry_recovers(self):
        m=read_model('idempotent-webhook');m['events'][2]['fault']='before_commit'
        out=simulate(m);self.assertEqual(out['results']['credit-first']['status'],'retryable')
        self.assertEqual(out['state']['balance'],100);self.assertEqual(len(out['ledger']),1)

    def test_after_commit_response_loss_does_not_double_credit(self):
        m=read_model('idempotent-webhook');m['events'][2]['fault']='response_lost'
        out=simulate(m);self.assertEqual(out['state']['balance'],100);self.assertEqual(len(out['ledger']),1)

    def test_different_event_same_business_effect(self):
        m=read_model('idempotent-webhook');m['events'][5]['payload']['event_id']='evt_99'
        self.assertEqual(len(simulate(m)['ledger']),1)

    def test_distinct_purchase_is_not_deduplicated_by_amount(self):
        m=read_model('idempotent-webhook');m['events'][7]['business_key']='pay_43_credit';m['expected_final']={'balance':200,'ledger_entries':2}
        self.assertEqual(len(simulate(m)['ledger']),2)

    def test_invalid_payment_verification_rejected(self):
        m=read_model('idempotent-webhook');m['events'][2]['verified']=False
        with self.assertRaises(ContractError):validate_model(m)

    def test_stable_placement_and_definitions(self):
        for lesson,cfg,ref,m in entries():self.assertEqual(check_placement(ROOT,cfg,ref,m),[])

    def test_missing_anchor_rejected(self):
        lesson,cfg,ref,m=next(entries());ref=copy.deepcopy(ref);ref['after_id']='missing-anchor'
        self.assertTrue(any('FIG-INTEGRATION' in x for x in check_placement(ROOT,cfg,ref,m)))

class SealRegressions(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('figure_seal',ROOT/'tools/seal-learning-figure-release.py')
        self.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.mod)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.site=self.base/'site';(self.site/'lessons').mkdir(parents=True)
        self.page=self.site/'lessons/sample.html';self.page.write_text('<p>checked</p>')
        self.css=self.site/'style.css';self.css.write_text('p{color:black}')
        assets={str(p.relative_to(self.site)):digest(p.read_bytes()) for p in sorted(self.site.rglob('*')) if p.is_file()}
        self.report={'status':'PASS','cases':[{'lesson':'sample','status':'PASS','page_sha256':digest(self.page.read_bytes())}],
                     'artifact_files':assets,'artifact_digest':digest(json_bytes(assets))}
        self.report_path=self.base/'report.json';self.review_path=self.base/'review.json'
        self.review={'visual_review':'PASS','print_review':'PASS','reviewer':'synthetic-test-only','evidence':['fixture']}
        self.write()
    def write(self):
        self.report_path.write_bytes(json_bytes(self.report))
        self.review['report_sha256']=digest(self.report_path.read_bytes());self.review_path.write_bytes(json_bytes(self.review))
    def call(self):return self.mod.seal(self.site,self.report_path,self.review_path)
    def test_seal_unchanged_candidate(self):self.assertEqual(self.call()['status'],'SEALED_NOT_DEPLOYED')
    def test_seal_rejects_changed_css(self):
        self.css.write_text('p{display:none}')
        with self.assertRaises(ValueError):self.call()
    def test_seal_rejects_changed_page(self):
        self.page.write_text('<p>not checked</p>')
        with self.assertRaises(ValueError):self.call()
    def test_seal_requires_explicit_visual_review(self):
        self.review['visual_review']='NOT_RUN';self.write()
        with self.assertRaises(ValueError):self.call()
    def test_seal_requires_paginated_print_review(self):
        self.review['print_review']='NOT_RUN';self.write()
        with self.assertRaises(ValueError):self.call()
    def test_seal_rejects_blocked_render(self):
        self.report['status']='BLOCKED';self.write()
        with self.assertRaises(ValueError):self.call()
    def test_seal_rejects_empty_coverage(self):
        self.report['cases']=[];self.write()
        with self.assertRaises(ValueError):self.call()
    def test_seal_rejects_stale_review(self):
        self.report['scope']='different';self.report_path.write_bytes(json_bytes(self.report))
        with self.assertRaises(ValueError):self.call()

if __name__=='__main__':unittest.main(verbosity=2)
