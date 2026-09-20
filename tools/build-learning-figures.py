#!/usr/bin/env python3
"""Generate/check v2 SVG and HTML. Missing renderer/font dependencies block."""
import argparse
from learning_figures.core import synchronize, ContractError

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    failures=synchronize(check=args.check)
    for x in failures:print(x)
    print('FAIL' if failures else 'PASS: measured figure outputs match the models')
    return 1 if failures else 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ImportError,ContractError) as exc:print('BLOCKED:',exc);raise SystemExit(2)
