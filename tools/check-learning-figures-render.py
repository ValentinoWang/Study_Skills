#!/usr/bin/env python3
"""Check an actual built Pages artifact, not a hand-built approximation."""
from pathlib import Path
import argparse
from learning_figures.runner import audit_site

def main():
    p=argparse.ArgumentParser();p.add_argument('--built-site',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--engine',choices=['chromium','webkit'],default='chromium');p.add_argument('--offline',action='store_true');a=p.parse_args()
    report=audit_site(a.built_site.resolve(),a.output.resolve(),engine=a.engine,offline=a.offline)
    print(report['status'],len(report['cases']),'browser cases; see',a.output/'report.json')
    return 0 if report['status']=='PASS' else 2 if report['status']=='BLOCKED' else 1
if __name__=='__main__':raise SystemExit(main())
