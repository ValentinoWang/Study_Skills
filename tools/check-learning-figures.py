#!/usr/bin/env python3
"""Static identity/placement gate. This is NOT the browser render gate."""
from learning_figures.core import static_check, ContractError
if __name__=='__main__':
    try:
        failures=static_check()
        for x in failures:print(x)
        print('FAIL' if failures else 'PASS: figure models, definitions, placements and derived identity; rendered checks NOT_RUN')
        raise SystemExit(1 if failures else 0)
    except (ImportError,ContractError,KeyError,ValueError) as exc:
        print('BLOCKED:',exc);raise SystemExit(2)
