#!/usr/bin/env python3
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'app/src/main/assets/electrical_diag_v1.json'
d=json.loads(P.read_text(encoding='utf-8'))

specs={
'E_HEAD_NO':dict(circuit='HEAD_LAMP', control='LIGHT SW', load='HEAD LAMP-RH/LH', fuse='15A 전조등/후미등 계열(매뉴얼 정기점검표 확인)', pages=[367,369], comps=[('LIGHT SW','1/4 E2'),('HEAD LAMP-RH','1/4 A2'),('HEAD LAMP-LH','3/4 A8'),('FUSE BOX','3/4 E6')], standard='할로겐 전조등 12V 55W'),
'E_TURN_NO':dict(circuit='TURN_HAZARD', control='TURN SIG SW / HAZARD SW / FLASHER UNIT', load='TURN SIGN LAMP-RH/LH', fuse='15A 방향지시등 계열(매뉴얼 정기점검표 확인)', pages=[367,369], comps=[('TURN SIG SW','3/4 A6'),('HAZARD SW','3/4 A6'),('HAZARD RELAY / FLASHER UNIT','3/4 A6 / 4/4 F6'),('TURN SIGN LAMP-RH','1/4 A2'),('TURN SIGN LAMP-LH','3/4 A8')], standard='방향지시등 전구 12V 27W'),
'E_HORN_NO':dict(circuit='HORN', control='HORN SW', load='HORN', fuse='10A 경적(Horn)(매뉴얼 정기점검표 확인)', pages=[367], comps=[('HORN SW','1/4 A3'),('HORN','1/4 A3'),('FUSE BOX','3/4 E6')], standard='차량 12V 계통; 부하 상태 실제 배터리전압과 비교'),
'E_BACKUP_NO':dict(circuit='BACKUP', control='BACK-UP SW', load='BACK-UP BUZZER / COMB LAMP BACK-UP', fuse='정확한 fuse cavity/정격은 회로 고해상도 검증 전 미확정', pages=[370], comps=[('BACK-UP SW','4/4 H7'),('BACK-UP BUZZER','4/4 H7~I7'),('COMB LAMP-RH/LH BACK-UP','4/4 I7~I8')], standard='백업등 전구 12V 10W'),
'E_START_NO':dict(circuit='START', control='KEY SW / RELAY-START', load='STARTER', fuse='10A 시동 릴레이, 30A 키 스위치/시동모터(매뉴얼 정기점검표)', pages=[367,368,369], comps=[('12V BATTERY / CIRCUIT BREAKER','1/4 C1~D2'),('KEY SW','3/4 C5'),('RELAY-START','1/4 F4 / 2/4 E4'),('STARTER','1/4 C1 / 2/4 F1')], standard='12V 전원계통; 무부하 전압만이 아니라 START 명령 중 전압강하 확인'),
'E_CHARGE':dict(circuit='CHARGE', control='ALTERNATOR / ACCEL RELAY', load='BATTERY charging path', fuse='15A 레귤레이터 계열(매뉴얼 정기점검표)', pages=[368], comps=[('ALTERNATOR','2/4 F2'),('ACCEL RELAY','2/4 G2'),('12V BATTERY','2/4 F1'),('CIRCUIT BREAKER','2/4 F1')], standard='정확한 충전전압 범위는 D24 전용 OEM 제원 확인 전 앱이 임의 생성하지 않음'),
'E_PARK_INPUT':dict(circuit='PARK_INPUT', control='PARKING BRAKE SW', load='OSS CONTROLLER / interlock input', fuse='OSS 컨트롤러 15A 계열 표기는 매뉴얼 정기점검표에 있으나 주차SW 전용 cavity는 미확정', pages=[367], comps=[('PARKING BRAKE SW','1/4 C2'),('OSS CONTROLLER','1/4 C2~C4')], standard='스위치 입력 전환은 실제 커넥터에서 해제/체결 상태 비교'),
'E_LIFT_LOCK':dict(circuit='LIFT_LOCK', control='SOL_LIFT LOCK V/V / SOL_UNLOAD V/V', load='lock/unload solenoid valves', fuse='정확한 전용 fuse cavity/정격 미확정', pages=[370], comps=[('SOL_LIFT LOCK V/V','4/4 F5'),('SOL_UNLOAD V/V','4/4 F5'),('FUSE BOX','4/4 E5~E6')], standard='12V 계통; 코일 전압은 실제 배터리전압과 비교'),
'E_GAUGE':dict(circuit='GAUGE', control='INSTRUMENT CLUSTER / sender circuit', load='WATER TEMP / T/M OIL TEMP / FUEL LEVEL indication', fuse='15A 계기판(매뉴얼 정기점검표)', pages=[367,369,370], comps=[('INSTRUMENT CLUSTER','1/4 A4 / 3/4 A5'),('WATER TEMP SENSOR','4/4 G5~G6'),('T/M OIL TEMP SENSOR','4/4 G6'),('FUEL SENSOR','4/4 G6')], standard='센서 저항/전압 숫자는 해당 센서 OEM 표가 없는 상태에서 임의 생성하지 않음'),
'E_WORK_LAMP':dict(circuit='WORK_REAR', control='관련 스위치/릴레이', load='STROBE / REAR LAMP', fuse='전용 fuse cavity/정격은 현재 래스터에서 미확정', pages=[370], comps=[('STROBE','4/4 H6'),('REAR LAMP','4/4 H7'),('FUSE BOX','4/4 E5~E6')], standard='12V 계통; 작동 명령 시 부하 커넥터 전압과 GND 전압강하 측정'),
'E_FR_CONTROL':dict(circuit='FR_CONTROL', control='F/R SWITCH', load='FWD/REV SOLENOID', fuse='FWD/REV fuse #3 (OEM 시험절차)', pages=[367,369], comps=[('F/R SWITCH','1/4 D4'),('FWD/REV SOLENOID','1/4 D4'),('FUSE BOX','3/4 E6')], standard='공통 4↔7; F 1↔2; R 1↔3; 솔레노이드 플런저 약 3.18mm')
}

def mk_result(title,result,tests,rule,confirm,gate):
    return {'type':'result','title':title,'result':result,'field_tools':['디지털 멀티미터','백프로브','OEM 회로도'], 'field_test':tests,'rule_out':rule,'confirm_if':confirm,'disassembly_gate':gate}

def make_graph(gid,s):
    # General field electrical graph. It localizes the fault; it does not invent unverified pin/fuse IDs.
    return {
      'title': next(x['title'] for x in d['catalog'] if x['id']==gid)+' · 회로 추적',
      'circuit':s['circuit'],'start':'scope','nodes':{
        'scope':{'type':'question','title':'1. 증상 범위와 관련 기능 비교','question':'같은 전원/스위치 계통의 다른 기능도 함께 이상합니까?','field_method':[f"회로도에서 {s['control']} → {s['load']} 경로를 표시한다.",'한쪽/양쪽 또는 단일부하/공통부하인지 먼저 구분해 불필요하게 상류 부품을 교환하지 않는다.'], 'choices':[{'label':'관련 기능도 함께 이상','next':'power'},{'label':'이 기능만 이상','next':'load_feed'}]},
        'power':{'type':'question','title':'2. 전원/퓨즈 부하전압','question':'해당 회로의 퓨즈/전원 분기 양단에 부하 상태 배터리 전압이 있습니까?','field_method':[f"퓨즈 정보: {s['fuse']}",'퓨즈는 육안만 보지 말고 입력측/출력측을 실제 작동 명령 상태에서 전압 측정한다.','정확한 cavity가 원본에서 확인되지 않은 회로는 차량 퓨즈박스 표기와 고해상도 OEM 회로를 먼저 대조한다.'], 'choices':[{'label':'입·출력 전원 정상','next':'control'},{'label':'전원/퓨즈에서 끊김','next':'power_bad'}]},
        'power_bad':mk_result('전원/퓨즈 상류 문제',f"{s['control']} 이전 전원 경로에서 공급이 끊깁니다.",[f"{s['fuse']}를 기준으로 퓨즈 전후 전압을 비교한다.",'전압이 처음 사라지는 커넥터/분기점을 찾는다.'],[s['control']+' 자체',s['load']+' 자체'],['상류 전압 정상 지점과 0V 지점 사이가 반복적으로 특정됨'],'전압 단절 구간을 특정한 뒤 그 구간만 수리한다.'),
        'control':{'type':'question','title':'3. 스위치/릴레이 입력→출력','question':f"작동 명령 시 {s['control']}의 입력은 정상이고 출력도 전환됩니까?",'field_method':['입력전압, 명령 상태, 출력전압을 같은 조건에서 동시에 비교한다.','핀번호가 원본에서 확인된 경우에만 숫자 핀을 표시하고, 미확인 핀은 기능명 기준으로 측정한다.'], 'choices':[{'label':'출력 정상','next':'load_feed'},{'label':'입력 정상·출력 없음','next':'control_bad'}]},
        'control_bad':mk_result('제어부 출력 불량',f"{s['control']} 입력은 있으나 출력이 전환되지 않습니다.",[f"{s['control']}의 기계작동/접점/릴레이 코일과 접점을 분리 점검한다.",'수리/대체 후 출력과 증상을 재시험한다.'],['상류 전원','후단 부하/접지'],['입력 정상 + 명령 정상 + 출력 불량이 반복됨'],'제어부 입력/명령을 확인한 뒤 해당 스위치/릴레이만 수리한다.'),
        'load_feed':{'type':'question','title':'4. 부하 커넥터 전압','question':f"작동 명령 시 {s['load']} 입력단에 배터리 전압이 도달합니까?",'field_method':[f"OEM 기준/주의: {s['standard']}",'제어부 출력과 부하 입력을 비교해 중간 하네스에서 전압이 사라지는지 확인한다.'], 'choices':[{'label':'부하 입력 전압 정상','next':'ground'},{'label':'부하 입력 0V/낮음','next':'harness_bad'}]},
        'harness_bad':mk_result('제어부→부하 하네스/커넥터 문제',f"{s['control']} 출력 이후 {s['load']} 입력까지 전압이 전달되지 않습니다.",['중간 커넥터를 순서대로 백프로브해 마지막 정상 지점/첫 이상 지점을 찾는다.','핀 밀림·부식·장력저하·단선·단락을 확인한다.'],['상류 퓨즈/전원',s['load']+' 내부'],['특정 커넥터 전단 정상/후단 이상이 같은 조건에서 재현됨'],'고장구간 특정 후 해당 하네스/커넥터만 수리한다.'),
        'ground':{'type':'question','title':'5. 부하 GND/실제 작동','question':f"{s['load']}의 접지 전압강하가 정상이고 실제 부하가 작동합니까?",'field_method':['부하가 켜지는 명령 상태에서 부하 GND단과 배터리 음극 사이 전압강하를 측정한다.','전원과 GND가 정상인데 작동하지 않으면 부하 자체를 의심한다.'], 'choices':[{'label':'GND 불량','next':'ground_bad'},{'label':'전원/GND 정상인데 미작동','next':'load_bad'},{'label':'정상 작동','next':'retest'}]},
        'ground_bad':mk_result('접지 경로 불량',f"{s['load']} 전원은 도달하지만 GND 경로가 정상적이지 않습니다.",['접지점→차체→배터리 음극을 구간별 전압강하로 분리한다.','접지 볼트 풀림·부식·도장·핀 접촉불량을 확인한다.'],['전원/퓨즈',s['control']+' 출력'],['접지 복구 후 동일 명령에서 정상작동됨'],'접지 불량 지점을 특정 후 해당 접지점만 수리한다.'),
        'load_bad':mk_result('부하 자체 불량',f"{s['load']} 입력전원과 GND는 정상인데 실제 작동하지 않습니다.",[f"{s['standard']}",'정상 부품 대체 또는 부품 자체 연속성/저항/기계작동을 OEM 기준으로 확인한다.'],['전원/퓨즈','제어부','하네스','접지'],['정상 전원/GND에서 대체 부하가 작동하거나 해당 부하 내부 이상이 확인됨'],'전원/GND 확인 후 부하를 교환/분해한다.'),
        'retest':mk_result('현재 회로 작동 정상','현재 시험조건에서는 회로가 정상 작동합니다.',['간헐 고장이라면 흔들림시험·열간/냉간·실제 작업조건으로 재현한다.','진단 로그에 측정 위치와 전압을 저장한다.'],['고정 고장'],['실제 고장조건에서도 정상으로 유지되면 회로 정상 판정'],'간헐 고장 재현 전 부품을 예방 교환하지 않는다.')
      }
    }

# circuit metadata and graphs
for gid,s in specs.items():
    if s['circuit'] not in d['circuits']:
        d['circuits'][s['circuit']]={
          'schematic_id':'600123-00120','sheet':next(x['sheet'] for x in d['catalog'] if x['id']==gid),
          'oem_pages':s['pages'],'grid':next(x['grid'] for x in d['catalog'] if x['id']==gid),
          'components':[{'name':a,'grid':b} for a,b in s['comps']],
          'images':[f'oem_pages/p{p}.jpg' for p in s['pages'][:3]],
          'fuse_reference':s['fuse'],'known_standard':s['standard'],
          'unverified':['숫자 핀/퓨즈 cavity는 OEM 원본에서 명확히 확인된 값만 앱에 확정 표시']
        }
    if gid not in d['graphs']:
        d['graphs'][gid]=make_graph(gid,s)

# E_FR_CONTROL should be a graph as well, but prepend exact OEM pin procedure to generic control node.
fr=d['graphs'].get('E_FR_CONTROL')
if fr:
    fr['nodes']['control']['field_method']=[
      'OEM 시험절차: F/R 스위치 공통 핀 4↔7 연속성을 확인한다.',
      '전진: 핀 1↔2는 F에서 연결, N에서 비연결이어야 한다.',
      '후진: 핀 1↔3은 R에서 연결, N에서 비연결이어야 한다.',
      '0V이면 FWD/REV fuse #3 및 연결전선을 먼저 확인한다.',
      '솔레노이드가 자화돼도 끝내지 않고 작동 시 플런저가 약 3.18 mm 이동하는지 확인한다.'
    ]

for x in d['catalog']:
    x['ready']='field_graph'

P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('graphs',len(d['graphs']),'circuits',len(d['circuits']),'catalog',len(d['catalog']))
