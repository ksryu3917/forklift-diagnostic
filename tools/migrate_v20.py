#!/usr/bin/env python3
"""Lossless, deterministic migration. Missing source fields stay missing.

This is a schema/parity conversion, NOT evidence of clinical/field correctness.
Runtime completeness is reported separately and cannot be manufactured by defaults.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'migration/input'
OUT = ROOT / 'app/src/main/assets/v20'
MODELS = [f'D{n}{s}-7' for s in ('S', 'SE') for n in (20, 25, 30, 33)]
REQUIRED = ('safety_preconditions', 'first_observation', 'test_location', 'tool',
            'operating_condition', 'measurement_or_action', 'expected_basis',
            'rule_out', 'confirm_if', 'next_action', 'teardown_gate', 'do_not')


def read(name):
    return json.loads((INPUT / name).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def text(value):
    return '\n'.join(str(x) for x in value) if isinstance(value, list) else value


def scope(engine=False):
    value = {'manufacturer': 'DOOSAN', 'models': MODELS}
    if engine:
        value['engine'] = 'D24'
    return value


def main():
    catalog, findings, counts = [], [], {}
    for filename, family in (('transmission_diag_v08.json', 'transmission'),
                             ('electrical_diag_v1.json', 'electrical'),
                             ('engine_diag_d24_v2.json', 'd24')):
        source = read(filename)
        terminals = 0
        for gid, original in source['graphs'].items():
            g = {'schema_version': 20, 'id': family + '__' + gid,
                 'title': original.get('title', gid), 'start': original['start'],
                 'vehicle_scope': scope(family == 'd24'), 'nodes': {},
                 'provenance': {'file': filename, 'pointer': '/graphs/' + gid,
                                'sha256': hashlib.sha256((INPUT / filename).read_bytes()).hexdigest()},
                 'source_record': copy.deepcopy(original)}
            g['entry_points'] = copy.deepcopy(original.get('entry_points', [original['start']]))
            for nid, old in original['nodes'].items():
                node = {'type': old['type'], 'title': old.get('title', nid),
                        'source_pointer': '/graphs/' + gid + '/nodes/' + nid}
                mappings = {'first_observation': ('question', 'result'),
                            'measurement_or_action': ('field_method', 'field_test'),
                            'tool': ('tools', 'field_tools'), 'next_action': ('action',),
                            'teardown_gate': ('disassembly_gate',)}
                for key in REQUIRED:
                    value = old.get(key)
                    if not value:
                        value = next((old[k] for k in mappings.get(key, ()) if old.get(k)), None)
                    if value:
                        node[key] = text(value) if key not in ('rule_out', 'confirm_if', 'do_not', 'safety_preconditions') else value
                node['choices'] = [dict(c, id=c.get('id', f'c{i}'))
                                   for i, c in enumerate(old.get('choices', []))]
                node['result_branches'] = copy.deepcopy(node['choices']) + [
                    {'id': key, 'next': value} for key, value in old.items() if key.startswith('next_')]
                for key in ('min', 'max', 'unit', 'conditions', 'prompt'):
                    if key in old:
                        node[key] = copy.deepcopy(old[key])
                node['vehicle_scope'] = copy.deepcopy(g['vehicle_scope'])
                # A JSON pointer proves migration origin, not an OEM procedure.
                node['evidence_refs'] = copy.deepcopy(old.get('evidence_refs', []))
                missing = [k for k in REQUIRED if not node.get(k)]
                if node['type'] not in ('question', 'result'):
                    missing.append('typed_measurement_runtime')
                if not node['evidence_refs']:
                    missing.append('evidence_refs')
                node['contract_gaps'] = missing
                node['readiness'] = 'OEM_VERIFY' if missing else 'CONTRACT_PRESENT'
                if missing:
                    findings.append({'graph': g['id'], 'node': nid, 'missing': missing})
                if node['type'] == 'result':
                    terminals += 1
                g['nodes'][nid] = node
            file = 'migrated/' + g['id'] + '.json'
            write(OUT / file, g)
            catalog.append({'id': g['id'], 'title': g['title'], 'file': file,
                            'family': family, 'vehicle_scope': g['vehicle_scope'],
                            'contract_complete': not any(n['contract_gaps'] for n in g['nodes'].values())})
        counts[family] = {'graphs': len(source['graphs']), 'terminals': terminals}
    experts = read('expert_diag_v2.json')['items']
    write(OUT / 'expert_causes.json', {'schema_version': 20, 'records': [
        {'id': x['id'], 'vehicle_scope': scope(), 'source_record': x,
         'provenance': {'file': 'expert_diag_v2.json', 'index': i},
         'linked_graph_id': next((g['id'] for g in catalog if g['id'].endswith('__' + (x.get('linked_graph') or '\0'))), None)}
        for i, x in enumerate(experts)]})
    counts['expert_causes'] = len(experts)
    counts['expert_symptoms'] = len({x['symptom_id'] for x in experts})
    for name in ('manual_library_catalog.json', 'study_catalog_v896.json',
                 'field_location_map_v1.json', 'test_point_locator_v1.json',
                 'parts_reference_v1.json', 'source_registry_v1.json',
                 'engine_sensor_map_d24_v1.json', 'manual_db.json'):
        data = read(name)
        write(OUT / 'reference' / name, {'schema_version': 20, 'source_file': name, 'data': data})
    write(OUT / 'catalog.json', {'schema_version': 20, 'graphs': catalog})
    write(ROOT / 'validation/migration_audit.json', {'counts': counts, 'contract_gaps': findings,
          'field_quality_verified': False, 'note': 'Lossless migration only; missing OEM detail blocks runtime procedure.'})
    print(json.dumps({'counts': counts, 'nodes_with_contract_gaps': len(findings)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
