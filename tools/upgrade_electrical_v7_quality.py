#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'app/src/main/assets/electrical_diag_v1.json'
d=json.loads(p.read_text(encoding='utf-8'))

# STOP always-on: add loaded/dynamic confirmation so wiggle/voltage is not confused with static continuity.
g=d['graphs']['E_STOP_ON']
g['nodes']['switch_state']['field_method'] += [
    '브레이크 페달을 해제/작동하면서 STOP SW 양단 전압을 백프로브하고 MIN/MAX 또는 로그로 변화를 확인한다.',
    '커넥터/스위치 하네스를 흔들 때 램프 상태와 SW 양단 전압이 동시에 변하는지 확인한다. 흔들림 반응만으로 배선불량을 확정하지 않는다.'
]
g['nodes']['adjust_or_switch']['field_test'] += [
    '스위치 연결 상태에서 페달 해제 시 입력전압은 유지되고 출력이 OFF 상태로 전환되는지 부하 상태에서 확인한다.'
]

# Park input: correct verified protection references and add >=3 meaningful measurement points.
c=d['circuits']['PARK_INPUT']
c['simplified_diagram']['measure_points']=[
    'PARK SW 양단 상태전환',
    'OSS PARK 입력 백프로브',
    'BAT4 20A OSS 전원 / IGN3 15A OSS 신호',
    'OSS GND 전압강하'
]
g=d['graphs']['E_PARK_INPUT']
for n in g['nodes'].values():
    fm=n.get('field_method')
    if fm:
        n['field_method']=[x.replace('OSS 컨트롤러 15A 계열 표기는 매뉴얼 정기점검표에 있으나 주차SW 전용 cavity는 미확정',
                                      'D20/25/30/33S-7 D24 O&M 확인: BAT4 20A=OSS 전원, IGN3 15A=OSS 신호. PARK SW 숫자핀은 현재 source에서 미확정') for x in fm]
    ft=n.get('field_test')
    if ft:
        n['field_test']=[x.replace('OSS 컨트롤러 15A 계열 표기는 매뉴얼 정기점검표에 있으나 주차SW 전용 cavity는 미확정',
                                    'BAT4 20A OSS 전원과 IGN3 15A OSS 신호') for x in ft]

# D24 WTS: sensor signal, sensor-ground voltage drop, and scan/physical temperature comparison are three separate checks.
c=d['circuits']['D24_WTS']
c['simplified_diagram']['measure_points']=[
    'WTS pin2 / ECU109 signal',
    'WTS pin1 / ECU145 sensor return-GND voltage drop',
    '진단기 WTS actual ↔ 실제 냉각수/주변온도 추종 비교'
]

# General graph source metadata for verified fuse/relay table.
for gid,g in d['graphs'].items():
    cir=d.get('circuits',{}).get(g.get('circuit'),{})
    if cir.get('verified_protection_control'):
        g['protection_reference']=cir['verified_protection_control']
        g['protection_source']=cir.get('protection_source')

p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('electrical v7 quality patch applied')
