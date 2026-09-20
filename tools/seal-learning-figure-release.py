#!/usr/bin/env python3
"""Seal only an explicitly reviewed built artifact. Does NOT deploy to Pages.

Review is a separate record, bound to the exact render report digest; this tool
never invents PASS or auto-approves screenshots. Re-run after any artifact change.
"""
import argparse
import json
from pathlib import Path
from learning_figures.core import digest,json_bytes


def seal(site,report_path,review_path):
    report=json.loads(report_path.read_text());review=json.loads(review_path.read_text())
    if report.get('status')!='PASS' or not report.get('cases'):
        raise ValueError('BLOCKED: required render cases did not pass')
    if review.get('report_sha256')!=digest(report_path.read_bytes()):
        raise ValueError('FAIL: visual review targets a different render report')
    for field in ('visual_review','print_review'):
        if review.get(field)!='PASS':raise ValueError(f'BLOCKED: {field} must be explicitly reviewed')
    if not review.get('reviewer') or not review.get('evidence'):
        raise ValueError('BLOCKED: reviewer and concrete evidence references required')
    for case in report['cases']:
        page=site/'lessons'/(case['lesson']+'.html')
        if case.get('status')!='PASS' or digest(page.read_bytes())!=case['page_sha256']:
            raise ValueError('FAIL: checked page no longer matches the candidate')
    assets={str(p.relative_to(site)):digest(p.read_bytes()) for p in sorted(site.rglob('*')) if p.is_file()}
    if assets != report.get('artifact_files') or digest(json_bytes(assets))!=report.get('artifact_digest'):
        raise ValueError('FAIL: artifact assets changed or full asset evidence is missing')
    return {'status':'SEALED_NOT_DEPLOYED','artifact_files':assets,'artifact_digest':digest(json_bytes(assets)),
            'render_report_sha256':digest(report_path.read_bytes()),'review_sha256':digest(review_path.read_bytes()),
            'transport':report.get('transport'),'automatic_pages_gate':'NOT_CONFIGURED',
            'note':'This seal is not a user acceptance signature and does not change repository Pages settings.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--site',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.resolve().is_relative_to(a.site.resolve()):raise SystemExit('FAIL: evidence must be outside the sealed artifact')
    try:result=seal(a.site,a.report,a.review)
    except (ValueError,KeyError,OSError) as e:print(e);raise SystemExit(1)
    a.output.write_bytes(json_bytes(result));print(result['status'],result['artifact_digest'])
