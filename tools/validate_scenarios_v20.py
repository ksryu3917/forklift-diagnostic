#!/usr/bin/env python3
"""Require 30 distinct *executed* conditions for every shipped terminal."""
from pathlib import Path
import collections
import json
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
data = json.loads((root / 'validation/terminal_scenarios.json').read_text(encoding='utf-8'))
groups = collections.defaultdict(list)
for scenario in data['scenarios']:
    groups[(scenario['graph'], scenario['terminal'])].append(scenario)

expected = set()
for path in (root / 'app/src/main/assets/v20/diagnostics').glob('*.json'):
    graph = json.loads(path.read_text(encoding='utf-8'))
    for node_id, node in graph['nodes'].items():
        if node.get('type') == 'result':
            expected.add((graph['id'], node_id))

errors = []
for key in sorted(expected | set(groups)):
    rows = groups.get(key, [])
    signatures = {
        (row.get('voltage_state'), row.get('command'), row.get('current_or_rpm'),
         row.get('temperature'), row.get('model_scope'), row.get('evidence'),
         tuple(row.get('path', []))) for row in rows
    }
    executed = [row for row in rows if row.get('executed') is True]
    if len(rows) < 30 or len(signatures) < 30:
        errors.append(f'{key}: {len(rows)} rows/{len(signatures)} distinct; need 30')
    if len(executed) < 30:
        errors.append(f'{key}: {len(executed)} executed; generated vectors do not count')
    if executed and any(row.get('observed_terminal') != key[1] for row in executed):
        errors.append(f'{key}: executed row reached the wrong terminal')
    if executed and any(row.get('actual') != row.get('expected') for row in executed):
        errors.append(f'{key}: expected/actual mismatch')
    if not any(row.get('expected') == 'PASS' for row in rows):
        errors.append(f'{key}: missing legal PASS condition')
    if not any(row.get('expected') == 'BLOCK' for row in rows):
        errors.append(f'{key}: missing blocked scope/evidence condition')

print(f'V20_SCENARIO_TERMINALS={len(expected)} ROW_GROUPS={len(groups)} ERRORS={len(errors)}')
for error in errors:
    print('ERROR', error)
if errors:
    raise SystemExit(1)
