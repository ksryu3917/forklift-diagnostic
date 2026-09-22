#!/usr/bin/env python3
"""Bind the lamp isolation flow to the inspected OEM sheet, without invented limits."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets/v20'
graph_file = ASSETS / 'diagnostics/e_license_terminal_stop.json'
g = json.loads(graph_file.read_text())
scope = {'manufacturer': 'DOOSAN', 'models': [f'D{n}{s}-7' for s in ('S','SE') for n in (20,25,30,33)]}
g['schema_version'] = 20
g['vehicle_scope'] = scope
g['evidence_refs'] = ['DOOSAN_600123_00120_S4']
for node in g['nodes'].values():
    node['vehicle_scope'] = scope
    node['evidence_refs'] = g['evidence_refs']
    node['result_branches'] = node.get('choices', [])
    node['safety_preconditions'] = ['평탄지 주차·중립·주차브레이크 체결·포크 하강·엔진 정지',
        '백프로브 절연부 확인; 단자 간 단락 금지; 탈거·연속성 시험은 미등 OFF 후 실시']
    node['do_not'] = ['도면에서 판독되지 않는 퓨즈 번호·핀 번호·전압강하 한계값을 추정하지 않는다',
        '부하가 실제로 흐르지 않는 상태의 전압만으로 전원·접지를 정상 판정하지 않는다']
    if node['type'] == 'question':
        node['rule_out'] = ['이 단계만으로 부품 고장을 확정하지 않는다']
        node['confirm_if'] = ['같은 점등 조건에서 측정 결과가 반복되고 다음 격리검사와 일치한다']
        node['next_action'] = '현재 점검 결과에 맞는 분기를 선택한다; 불명확하면 진행하지 않는다'
        node['teardown_gate'] = '전원·접지·부하 격리 전 어셈블리 교환 금지'
    else:
        node['tool'] = '디지털 멀티미터·절연 백프로브·차량 적용 형식의 정상 전구'
        node['operating_condition'] = '커넥터 연결·미등 ON·정상 부하가 흐르는 조건; 탈거 시 미등 OFF'
        node['test_location'] = '600123-00120 (4/4) I8 LICENCE LAMP, 후단 커넥터와 접지 경로'
        node['measurement_or_action'] = node['next_action']
g['nodes']['lp2']['measurement_or_action'] = ('미등 ON에서 번호판등 공급 단자와 배터리 음극 사이 전압을 측정하고 '
    '배터리 단자 전압·정상 미등 공급과 같은 부하 조건으로 비교한다. 단선 전구로 전류가 없으면 '
    '차량 적용 형식의 정상 전구를 연결해 재측정한다. 핀 번호는 원문·실차로 확인하며 추정하지 않는다.')
g['nodes']['lp3']['measurement_or_action'] = ('정상 부하가 연결된 미등 ON 상태에서 번호판등 접지 단자와 배터리 음극 사이 전압강하를 '
    '측정하고 정상 후미등 접지 경로와 비교한다. 부하 전류가 확인되지 않으면 접지 정상으로 선택하지 않는다.')
g['nodes']['bulb_socket']['do_not'] += ['전구·소켓 영역에서 멈추며 추가 컨트롤러·하네스 어셈블리 교환으로 진행하지 않는다']
g['nodes']['lamp_common']['result'] = '여러 미등이 함께 꺼져 공통 LAMP 경로를 먼저 격리해야 합니다. 공통 공급 고장으로 아직 확정하지 않습니다.'
g['nodes']['lamp_common']['first_observation'] = g['nodes']['lamp_common']['result']
g['nodes']['lamp_common']['test_location'] = '해당 차량의 미등 공통 공급·스위치·접지 분기; 도면과 실차로 식별'
g['nodes']['lamp_common']['rule_out'] = ['번호판등 전구 단독고장만으로는 다른 미등 불량을 설명할 수 없음; 복합고장은 배제하지 않음']
g['nodes']['feed_fault']['rule_out'] = ['다른 미등이 켜져 공통 공급 전체 상실 가능성은 낮음; 접지·복합고장은 아직 배제하지 않음']
g['nodes']['ground_fault']['confirm_if'] = ['같은 정상 부하에서 접지 구간의 과도한 전압강하가 반복되고 해당 접지 수리 후 정상화']
graph_file.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
registry_file = ASSETS / 'evidence_registry.json'
registry = json.loads(registry_file.read_text())
asset = 'evidence/oem_pages/p370.jpg'
registry['entries']['DOOSAN_600123_00120_S4'] = {
    'status': 'VERIFIED', 'vehicle_scope': scope,
    'locator': 'SM1018-01 PDF p370, 600123-00120 (4/4), I8 LICENCE LAMP / I7-I8 COMB LAMP',
    'asset': asset, 'sha256': hashlib.sha256((ASSETS/asset).read_bytes()).hexdigest(),
    'verified_content': 'Sheet header model family and lamp topology visually inspected; no numeric limits or pin assignments inferred',
    'procedure_basis': 'Loaded electrical isolation and normal-side comparison; not an OEM numeric acceptance specification'}
registry['review_state'] = 'Lamp topology reviewed; other entries remain unverified'
registry_file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
print('Lamp scope and sheet provenance bound; executable scenario/runtime gates still required')
