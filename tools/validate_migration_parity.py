#!/usr/bin/env python3
"""Check exact source record parity, graph structure and recovered asset hashes.

Does not label incomplete contracts as executable field coverage.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets/v20'


def read(path):
    return json.loads(path.read_text())


def main():
    index = read(ASSETS / 'catalog.json')['graphs']
    count = 0
    for entry in index:
        graph = read(ASSETS / entry['file'])
        origin = graph['provenance']
        source_file = ROOT / 'migration/input' / origin['file']
        assert hashlib.sha256(source_file.read_bytes()).hexdigest() == origin['sha256']
        original = read(source_file)['graphs'][origin['pointer'].split('/')[-1]]
        assert original == graph['source_record'], graph['id'] + ': source loss'
        assert set(original['nodes']) == set(graph['nodes']), graph['id'] + ': node loss'
        visited = set()
        def walk(nid):
            if nid in visited:
                return
            visited.add(nid)
            node = graph['nodes'][nid]
            old = original['nodes'][nid]
            assert node['type'] == old['type']
            assert [(x['label'], x['next']) for x in node['choices']] == [(x['label'], x['next']) for x in old.get('choices', [])]
            assert len({x['id'] for x in node['choices']}) == len(node['choices'])
            if node['type'] == 'result':
                assert not node['result_branches']
            else:
                assert node['result_branches'], (graph['id'], nid, 'dead end')
            for key in ('min', 'max', 'unit', 'conditions', 'prompt'):
                assert node.get(key) == old.get(key)
            assert {c['id']:c['next'] for c in node['result_branches'] if c['id'].startswith('next_')} == {k:v for k,v in old.items() if k.startswith('next_')}
            for c in node['result_branches']:
                assert c['next'] in graph['nodes'], (graph['id'], nid, 'broken edge')
                walk(c['next'])
        assert graph['entry_points'] == original.get('entry_points', [original['start']])
        for entry_point in graph['entry_points']:
            walk(entry_point)
        assert visited == set(graph['nodes']), (graph['id'], 'unreachable', set(graph['nodes']) - visited)
        count += len(visited)
    originals = read(ROOT / 'migration/input/expert_diag_v2.json')['items']
    migrated = read(ASSETS / 'expert_causes.json')['records']
    assert [x['source_record'] for x in migrated] == originals
    assert len({x['id'] for x in migrated}) == len(migrated)
    print(f'MIGRATION PARITY PASS: {len(index)} graphs, {count} nodes, {len(migrated)} causes; NOT field/runtime verification')


if __name__ == '__main__':
    main()
