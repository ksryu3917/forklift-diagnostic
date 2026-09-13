#!/usr/bin/env python3
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
P=BASE/'app/src/main/assets/electrical_diag_v1.json'
d=json.loads(P.read_text(encoding='utf-8'))

def result(title,res,tests,rule,confirm,gate,tools=None,limit=None):
    x={'type':'result','title':title,'result':res,'field_tools':tools or ['디지털 멀티미터','백프로브'],'field_test':tests,'rule_out':rule,'confirm_if':confirm,'disassembly_gate':gate}
    if limit:x['oem_limit_note']=limit
    return x

def q(title,question,methods,choices,tools=None):
    x={'type':'question','title':title,'question':question,'field_method':methods,'choices':[{'label':a,'next':b} for a,b in choices]}
    if tools:x['tools']=tools
    return x

# Catalog additions
ids={x['id'] for x in d['catalog']}
if 'E_WIPER_NO' not in ids:
    d['catalog'].append({'id':'E_WIPER_NO','title':'전/후 와이퍼가 작동하지 않음','group':'캐빈/옵션전장','sheet':'OPTION / Parts Book 620204-07141, 08467, 09003','grid':'option wiring OEM VERIFY','ready':'field_graph_source_limited'})
if 'E_WASHER_NO' not in ids:
    d['catalog'].append({'id':'E_WASHER_NO','title':'와셔액이 분사되지 않음','group':'캐빈/옵션전장','sheet':'OPTION / Parts Book 620204-07141','grid':'option wiring OEM VERIFY','ready':'field_graph_source_limited'})

# Technician-redrawn mini circuits. Exact option fuse/pins remain source-limited.
d['circuits']['WIPER_OPTION']={
 'schematic_id':'SB5120C05 Parts Book + option wiring OEM VERIFY',
 'sheet':'Option circuit source-limited','oem_pages':[], 'grid':'F_FWIP/F_RWIP option groups',
 'components':[
  {'name':'WIPER SWITCH','known':'Parts Book option groups include direction switch assy 301405-00139; exact numeric pin roles require option wiring'},
  {'name':'FRONT WIPER MOTOR','known':'A214302 early / 300512-00042 late, Serial split in SB5120C05'},
  {'name':'REAR WIPER MOTOR','known':'A214302 early / 220210-01910 late, Serial split in SB5120C05'}],
 'images':['parts_views/parts_p488.png','parts_views/parts_p422.png','parts_views/parts_p486.png'],
 'known_standard':'모터/하네스가 Serial에서 변경됨. 실제 부하 상태 B+/GND와 직접전원으로 모터/상류회로를 분리.',
 'unverified':['wiper option fuse cavity/rating','wiper switch numeric pin roles','option relay identity across all cabin configurations'],
 'simplified_diagram':{
  'title':'와이퍼 · 필요한 전원/명령/모터 경로만',
  'nodes':[
   {'id':'bat','label':'12V/B+','kind':'source','verified':True},
   {'id':'fuse','label':'WIPER FUSE\nOEM VERIFY','kind':'protection','verified':False},
   {'id':'sw','label':'WIPER SW\n301405-00139 계열','kind':'switch','verified':True},
   {'id':'harness','label':'OPTION HARNESS','kind':'harness','verified':True},
   {'id':'motor','label':'WIPER MOTOR\nSerial별 품번','kind':'load','verified':True},
   {'id':'gnd','label':'GND','kind':'ground','verified':True}],
  'edges':[{'from':'bat','to':'fuse'},{'from':'fuse','to':'sw'},{'from':'sw','to':'harness'},{'from':'harness','to':'motor'},{'from':'motor','to':'gnd'}],
  'measure_points':['MP1 모터 커넥터 B+ (작동명령 중)','MP2 모터 GND→BAT- 전압강하','MP3 스위치 입력/출력 기능선','MP4 하네스 전단/후단 비교'],
  'note':'전체 옵션도 복사 대신 진단에 필요한 기능경로만 재작성. 퓨즈/숫자핀은 옵션 회로도 확인 전 OEM VERIFY.'},
 'parts_book_reference':{'book':'SB5120C05','front_group':'620204-07141','rear_groups':['620204-08467','620204-09003'],'front_motor_early':'A214302','front_motor_late':'300512-00042','rear_motor_late':'220210-01910'}
}

d['circuits']['WASHER_OPTION']={
 'schematic_id':'SB5120C05 Parts Book + option wiring OEM VERIFY','sheet':'Option circuit source-limited','oem_pages':[],'grid':'F_FWIP option group',
 'components':[{'name':'WASHER TANK','known':'450108-00013 in front wiper option group'},{'name':'WASHER PUMP/MOTOR','note':'Parts Book excerpt does not identify a separate pump part number; do not invent'},{'name':'WASHER SWITCH','note':'numeric pin roles require option wiring'}],
 'images':['parts_views/parts_p488.png'],
 'known_standard':'전기 고장과 호스/노즐 막힘을 먼저 분리해야 한다.',
 'unverified':['washer pump exact part number','washer fuse cavity/rating','washer switch numeric pin roles'],
 'simplified_diagram':{
  'title':'와셔 · 전기와 유로를 분리한 최소 회로',
  'nodes':[{'id':'bat','label':'12V/B+','kind':'source','verified':True},{'id':'fuse','label':'WASHER FUSE\nOEM VERIFY','kind':'protection','verified':False},{'id':'sw','label':'WASHER COMMAND\nOEM VERIFY','kind':'switch','verified':False},{'id':'pump','label':'WASHER PUMP\nOEM VERIFY','kind':'load','verified':False},{'id':'gnd','label':'GND','kind':'ground','verified':True}],
  'edges':[{'from':'bat','to':'fuse'},{'from':'fuse','to':'sw'},{'from':'sw','to':'pump'},{'from':'pump','to':'gnd'}],
  'measure_points':['MP1 펌프 커넥터 B+ (분사명령 중)','MP2 펌프 GND 전압강하','MP3 스위치 출력','유로: 탱크→호스→노즐 막힘/누설'],
  'note':'전기 명령과 액체 유로를 병행 분리. 별도 펌프 품번/핀은 현재 Parts Book만으로 확정 금지.'},
 'parts_book_reference':{'book':'SB5120C05','front_group':'620204-07141','washer_tank':'450108-00013'}
}

# Wiper executable graph
d['graphs']['E_WIPER_NO']={
 'title':'전/후 와이퍼가 작동하지 않음 · 부하전압/모터/명령 분리','circuit':'WIPER_OPTION','start':'scope','nodes':{
  'scope':q('1. 증상 범위','전방/후방/둘 다 중 어디가 작동하지 않습니까?',['캐빈 옵션과 Serial을 먼저 기록한다.','전·후방 모두 불량이면 공통전원/스위치 계통을 우선하고 한쪽만이면 해당 모터/하네스를 우선한다.'],[('전·후방 모두','motor_feed'),('전방만','motor_feed'),('후방만','motor_feed')]),
  'motor_feed':q('2. 모터 커넥터 부하전압','와이퍼 작동 명령 중 해당 모터 커넥터 B+가 유지됩니까?',['커넥터를 연결한 상태로 백프로브한다.','무부하 12V 또는 정적 도통만으로 정상 판정하지 않는다.','Serial에 따라 전방 모터가 A214302→300512-00042, 후방은 A214302→220210-01910으로 변경될 수 있으므로 현재차량 부품을 먼저 확인한다.'],[('B+ 정상','ground'),('B+ 없음/낮음','switch_output')],['DMM MIN/MAX','백프로브']),
  'ground':q('3. 모터 GND 부하 전압강하','작동명령 중 모터 GND→배터리(-) 전압강하가 정상측과 비교해 안정적입니까?',['모터가 멈춘 상태에서도 명령을 유지하고 측정한다.','OEM 수치가 없으면 임의 mV 기준을 만들지 말고 정상차/임시 저저항 GND 점퍼와 A/B 비교한다.'],[('GND 불량','ground_bad'),('GND 정상','direct')]),
  'ground_bad':result('와이퍼 모터 접지 고저항','모터 B+는 도달하지만 실제 부하에서 접지 경로가 무너집니다.',['모터 GND→차체→BAT-를 구간별 전압강하로 나눈다.','임시 GND 점퍼에서 작동 복귀하는지 확인한다.'],['스위치/상류전원','모터 B+ 공급'],['GND 우회/수리 시 동일 조건에서 즉시 정상 작동'],'접지 위치 특정 후 해당 단자/하네스만 수리.'),
  'direct':q('4. 모터 직접전원','회로에서 분리한 모터에 퓨즈 내장 12V/GND를 직접 공급하면 정상 작동합니까?',['현재 모터 커넥터 극성과 회로를 확인한 뒤 짧게 직접전원 시험한다.','기계링크/와이퍼암 구속도 함께 분리 확인한다.'],[('직접전원에서도 미작동/느림','motor_bad'),('직접전원 정상','upstream')],['퓨즈 내장 점퍼선','DMM']),
  'motor_bad':result('와이퍼 모터/기계링크 불량','정상 직접전원에서도 모터가 정상 회전하지 않거나 링크가 구속됩니다.',['와이퍼암/링크를 분리해 모터 단독회전을 확인한다.','Parts Book Serial 적용품번과 현재 장착품을 대조한다.'],['상류 스위치','차량측 하네스'],['직접전원에서 모터 자체 미작동 또는 링크 분리 전후로 구속이 명확히 재현'],'직접전원/기계구속 분리 후 모터 또는 링크만 교환.'),
  'switch_output':q('5. 스위치/제어 출력','작동명령 시 스위치 입력은 유지되고 모터 방향 출력 기능선이 전환됩니까?',['Parts Book은 301405-00139 방향스위치 어셈블리를 확인하지만 숫자핀 기능은 옵션 회로도 없이는 확정하지 않는다.','입력/출력을 같은 명령 순간 비교한다.'],[('입력 정상·출력 없음','control_bad'),('출력 정상','harness_bad'),('입력부터 없음','power_bad')]),
  'power_bad':result('와이퍼 공통전원/보호회로 문제','스위치 입력 전원부터 형성되지 않습니다.',['실차 퓨즈박스 라벨과 옵션 회로도를 대조해 해당 보호회로를 식별한다.','퓨즈 양단을 명령 상태에서 측정하고 첫 무전압 지점을 찾는다.'],['와이퍼 모터','스위치 출력 이후 하네스'],['상류 정상지점과 첫 무전압 지점 사이가 반복 특정됨'],'정확한 보호회로/단절구간 확인 후 수리.',['DMM','백프로브'],'와이퍼 옵션 퓨즈 cavity/rating은 현재 소스에서 미확정.'),
  'control_bad':result('와이퍼 스위치/제어부 출력 불량','전원 입력은 유지되지만 와이퍼 명령 출력이 형성되지 않습니다.',['스위치 커넥터 핀 장력/밀림과 작동 시 출력 변화를 확인한다.','동일 사양 스위치 대체는 Parts Book/옵션 일치가 확인될 때만 시행한다.'],['모터','후단 하네스','공통전원'],['입력 정상 + 명령 반복 + 출력 미형성'],'스위치 입력/명령 정상 확인 후 제어부 교환.'),
  'harness_bad':result('스위치→와이퍼 모터 하네스/커넥터 불량','스위치 출력은 있으나 모터 커넥터까지 부하전압이 전달되지 않습니다.',['중간 커넥터를 절반분할 백프로브해 마지막 정상/첫 이상을 찾는다.','흔들림은 원인 확정이 아니라 재현 트리거로 사용하고 전압변화를 동시에 기록한다.'],['모터 자체','스위치 출력'],['특정 커넥터/하네스 전단 정상·후단 이상이 재현'],'고장구간 특정 후 해당 단자/하네스만 수리.'),
  'upstream':result('와이퍼 모터 정상 · 차량측 제어회로 문제','모터는 직접전원에서 정상입니다.',['원래 커넥터로 복원해 스위치 출력→중간 하네스→모터 입력을 부하 상태로 추적한다.','간헐이면 MIN/MAX와 구간별 흔들림시험을 병행한다.'],['모터 내부고장'],['직접전원 정상 + 차량 회로에서만 미작동'],'상류 회로 고장지점 특정 전 모터를 교환하지 않는다.')
 }}

# Washer executable graph
d['graphs']['E_WASHER_NO']={
 'title':'와셔액이 분사되지 않음 · 유로/펌프전원/스위치 분리','circuit':'WASHER_OPTION','start':'fluid','nodes':{
  'fluid':q('1. 액체 유로 먼저 분리','탱크에 액이 있고 호스/노즐이 막히거나 빠진 흔적이 없습니까?',['탱크 450108-00013, 호스, 노즐을 육안 확인한다.','펌프 소리가 나는데 분사가 없으면 전기회로보다 호스/노즐/탱크 유로를 먼저 본다.'],[('유로 막힘/누설 있음','fluid_bad'),('유로 이상 없음','pump_feed')]),
  'fluid_bad':result('와셔 유로 막힘/누설','전기 구동 전후와 무관하게 액체 경로에서 막힘/이탈/누설이 확인됩니다.',['노즐을 분리해 호스 단에서 토출 여부를 확인한다.','호스 꺾임/동결/이탈/노즐 막힘을 순서대로 확인한다.'],['스위치 전기접점','펌프 전원(유로 고장이 확정된 경우)'],['막힘/누설 복구 후 정상 분사'],'유로 불량지점만 수리.'),
  'pump_feed':q('2. 펌프 커넥터 부하전압','분사 명령 중 펌프/탱크측 구동 커넥터에 B+가 도달합니까?',['펌프가 Parts Book에서 별도 품번으로 명확히 식별되지 않았으므로 실차 탱크의 전기 커넥터를 먼저 확인한다.','명령 중 연결 상태 백프로브로 측정한다.'],[('B+ 정상','pump_ground'),('B+ 없음','switch')]),
  'pump_ground':q('3. 펌프 GND','분사 명령 중 펌프 GND→BAT- 경로가 정상입니까?',['부하 상태 전압강하와 임시 GND 점퍼를 비교한다.'],[('GND 불량','gnd_bad'),('GND 정상','direct')]),
  'gnd_bad':result('와셔 펌프 접지 불량','펌프 공급전압은 있으나 접지 경로가 부하에서 무너집니다.',['접지 경로를 구간별 전압강하로 추적한다.','임시 GND에서 분사가 복귀하는지 확인한다.'],['상류 스위치','유로 막힘'],['접지 우회에서 펌프/분사 정상'],'접지 불량 위치 특정 후 수리.'),
  'direct':q('4. 펌프 직접구동','극성을 확인한 뒤 퓨즈 내장 직접전원에서 펌프가 작동합니까?',['실차 커넥터 기능을 확인한 경우에만 직접구동한다.','펌프 소리뿐 아니라 실제 토출을 확인한다.'],[('직접전원에서도 미작동','pump_bad'),('직접전원 정상','upstream')]),
  'pump_bad':result('와셔 펌프/탱크 구동부 불량','전원/GND가 정상이고 직접구동에서도 펌프가 작동하지 않습니다.',['탱크 내부 이물/펌프 구속 여부를 확인한다.','현재 Parts Book 자료는 별도 펌프 품번을 확정하지 못하므로 실차 부품표기/추가 옵션자료 확인 후 주문한다.'],['스위치','차량측 하네스'],['직접전원 미작동이 반복'],'펌프 기능 불량 확정 후 분해/교환.',limit='별도 washer pump part number는 현재 Parts Book에서 미확정.'),
  'switch':q('5. 분사 스위치 출력','분사 명령 시 스위치 입력은 유지되고 출력 기능선이 전환됩니까?',['숫자핀은 옵션 회로도 확인 전 임의 지정하지 않는다.','입력/출력을 같은 명령 순간 비교한다.'],[('입력 정상·출력 없음','control_bad'),('출력 정상','harness_bad'),('입력 없음','power_bad')]),
  'control_bad':result('와셔 스위치/제어 출력 불량','입력전원은 있으나 분사 명령 출력이 형성되지 않습니다.',['스위치 단자 장력/밀림과 작동 출력을 확인한다.'],['펌프','후단 하네스'],['입력 정상 + 반복 명령 + 출력 없음'],'스위치 입력 정상 확인 후 제어부 수리/교환.'),
  'harness_bad':result('스위치→와셔 펌프 하네스 불량','스위치 출력은 있으나 펌프 커넥터까지 도달하지 않습니다.',['중간 커넥터 전단/후단을 부하상태로 비교한다.','핀 밀림/부식/부분단선을 확인한다.'],['스위치','펌프 자체'],['특정 구간에서만 전압이 사라짐'],'고장구간 특정 후 하네스/단자 수리.'),
  'power_bad':result('와셔 상류 전원/보호회로 문제','분사 스위치 입력부터 전원이 없습니다.',['실차 퓨즈박스 라벨과 옵션 배선을 대조해 보호회로를 찾는다.','퓨즈 양단/스위치 입력까지 첫 단절지점을 추적한다.'],['펌프','후단 하네스'],['상류 첫 단절지점 반복 특정'],'정확한 보호회로 확인 후 수리.',limit='washer option fuse cavity/rating은 현재 소스에서 미확정.'),
  'upstream':result('와셔 펌프 정상 · 상류 제어회로 문제','직접전원에서는 펌프가 정상 작동합니다.',['원래 회로에서 스위치 출력과 하네스를 다시 부하상태로 추적한다.'],['펌프 내부고장'],['직접전원 정상 + 차량회로에서만 미작동'],'상류 고장구간 특정 후 수리.')
 }}

d['version']='1.8-rc-expert-v8.1-parts-wiper'
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('catalog',len(d['catalog']),'graphs',len(d['graphs']))
