#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ELEC=ROOT/'app/src/main/assets/electrical_diag_v1.json'
OUT=ROOT/'app/src/main/assets/engine_diag_d24_v2.json'

e=json.loads(ELEC.read_text(encoding='utf-8'))

# Helpers

def res(title,result,tests,rule,confirm,gate,tools=None,note=''):
    d={"type":"result","title":title,"result":result,
       "field_tools":tools or ["진단기","디지털 멀티미터","OEM 서비스자료"],
       "field_test":tests,"rule_out":rule,"confirm_if":confirm,"disassembly_gate":gate}
    if note: d['oem_limit_note']=note
    return d

def q(title,question,choices,methods,tools=None):
    d={"type":"question","title":title,"question":question,"field_method":methods,
       "choices":[{"label":a,"next":b} for a,b in choices]}
    if tools: d['tools']=tools
    return d

def circuit(cid,title,nodes,edges,points,refs,note,components=None,unverified=None):
    c={"schematic_id":"D24NAP 950106-01198","sheet":refs,"grid":"field-redrawn",
       "oem_pages":[],"images":[],"components":components or [],
       "simplified_diagram":{"title":title,"nodes":nodes,"edges":edges,"measure_points":points,"note":note}}
    if unverified: c['unverified']=unverified
    return c

def N(i,label,kind='measure',verified=True): return {"id":i,"label":label,"kind":kind,"verified":verified}
def E(a,b): return {"from":a,"to":b}

# Carry over 7 D24 expert graphs/circuits from electrical DB.
carry=[
 ('E_D24_CRANK_NO_START','D24_CRANK_NO_START','크랭킹은 하나 시동 안 됨'),
 ('E_D24_ECU_NO_COMM','D24_ECU_HEALTH','D24 ECU 진단기 통신 안 됨'),
 ('E_D24_5V_REF','D24_VREF','5V 기준전압 붕괴/여러 센서 동시 이상'),
 ('E_D24_RAIL_PRESSURE','D24_RPS','레일압력센서 값/회로 이상'),
 ('E_D24_BOOST_PRESSURE','D24_BPS','부스트압력센서 값/회로 이상'),
 ('E_D24_WATER_TEMP','D24_WTS','냉각수온센서 값 비정상'),
 ('E_D24_MAF','D24_MAF','MAF/흡기온도 값 비정상'),
]
graphs={}; circuits={}; catalog=[]
for gid,cid,title in carry:
    graphs[gid]=e['graphs'][gid]
    circuits[cid]=e['circuits'][cid]
    catalog.append({"id":gid,"title":title,"group":"ECU/센서","circuit":cid,"readiness":"OEM_PIN_EXECUTABLE"})

# 1 Hard start
cid='D24_HARD_START'
circuits[cid]=circuit(cid,'D24 냉간/열간 시동불량 · 필요한 계통만',
 [N('batt','Cranking speed / ECU alive','source'),N('pre','Air heater / preheat','control'),N('sync','CRK/CAM sync'),N('rail','RPS actual vs command'),N('fuel','Low fuel → IMV → HP pump','control'),N('inj','Injector drive / return','load'),N('comp','Compression / mechanical','load')],
 [E('batt','pre'),E('batt','sync'),E('sync','rail'),E('rail','fuel'),E('fuel','inj'),E('inj','comp')],
 ['크랭킹 중 ECU 통신/RPM','예열 명령·출력','CRK/CAM sync','rail actual/command','IMV command','injector drive/return'],
 'D24 §2 winter/cold start, §9 fuel, §12 electrical',
 '냉간/열간을 분리하고 전기 생존→동기→레일압→분사→압축 순으로 좁힌다.',
 unverified=['OEM이 명시하지 않은 시동허용 rail pressure 임계값은 임의 생성하지 않음'])
graphs['EN_HARD_START']={"title":"D24 냉간/열간 시동이 어려움","circuit":cid,"start":"condition","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'condition':q('1. 조건 분리','시동불량이 어느 조건에서 두드러집니까?',[('냉간 위주','cold'),('열간 위주','hot'),('냉·열간 모두','alive')],['냉각수온/흡기온도 live data와 실제 엔진 온도를 비교한다.','방치시간·외기온·재시동 시간을 기록한다.']),
 'cold':q('2A. 냉간 예열','냉간에서 예열 명령과 에어히터 실제 전류/전압강하가 있습니까?',[('예열 작동 이상','pre_bad'),('예열 정상','alive')],['예열 표시만 보지 말고 히터 부하전류 또는 히터 양단 전압을 측정한다.']),
 'pre_bad':res('냉간 예열계통 우선','냉간 시동불량과 예열 실제출력 이상이 함께 있습니다.', ['퓨즈/릴레이/히터/제어명령을 부하상태에서 구간별 측정한다.'],['고압펌프 단독고장'],['예열 출력 복구 후 냉간 시동성이 반복 개선'], '예열 회로 원인 특정 후 해당 부품만 수리.'),
 'hot':q('2B. 열간 생존성','열간 불발 순간 ECU 통신·RPM·5V VREF가 유지됩니까?',[('열간에서 통신/RPM/VREF 끊김','hot_elec'),('모두 유지','rail')],['열간 soak 상태에서 MIN/MAX/진단로그를 남긴다.','센서 냉각/하네스 흔들림은 원인 확정이 아니라 재현 도구로 사용한다.']),
 'hot_elec':res('열간 전자계통 간헐','열간에서 ECU/CRK-CAM/VREF 중 하나가 사라집니다.', ['해당 신호를 열간 상태에서 백프로브/오실로스코프로 재현하고 전원/GND/CAN과 센서 신호를 분리한다.'],['연료기계 단독고장'],['열간 불발과 특정 신호 소실이 동시 재현'], '전자 원인 특정 전 연료계통 분해 금지.'),
 'alive':q('3. ECU/RPM 생존','크랭킹 중 ECU 통신과 RPM/동기가 안정적입니까?',[('아니오','sync_bad'),('예','rail')],['진단기의 RPM만 보지 말고 필요 시 CRK/CAM 파형과 동기를 확인한다.']),
 'sync_bad':res('CRK/CAM/ECU 생존 우선','크랭킹 중 ECU가 회전 정보를 안정적으로 받지 못합니다.', ['EN_CRK_CAM_SYNC로 이동해 센서/배선/파형/기계타이밍을 분리한다.'],['인젝터/고압펌프 교환'],['동기 회복 후 시동성 정상화'], '동기 원인부터 해결.'),
 'rail':q('4. 레일압 형성','크랭킹 중 rail actual이 command를 따라 형성됩니까?',[('형성 실패/불안정','fuel'),('형성 정상','inj')],['RPS 5V/GND/signal을 먼저 검증한다.','OEM 미확인 MPa를 임의 문턱값으로 쓰지 않는다.']),
 'fuel':res('연료압 형성계통으로 이동','동기 이후 rail actual 형성이 실패합니다.', ['EN_FUEL_PRESSURE에서 저압공급→공기혼입→IMV→고압펌프→rail/injector return 순으로 분리한다.'],['예열 단독고장','압축 단독고장'],['연료압 형성 원인이 별도 시험에서 특정'], '원인 특정 후만 고압계통 분해.'),
 'inj':q('5. 분사/기계 분리','인젝터 구동과 실린더별 기여/리턴이 정상입니까?',[('한 실린더/인젝터 이상','inj_bad'),('분사계통 정상','comp')],['전류파형/진단기 cut-out/리턴 비교 중 가능한 방법을 사용한다.']),
 'inj_bad':res('인젝터 계통 우선','시동불량과 인젝터 전기/리턴/기여 이상이 연결됩니다.', ['EN_INJECTOR_SEPARATE로 전기구동·리턴·압축을 분리한다.'],['ECU 전체고장'],['특정 실린더 원인이 반복 확인'], '해당 실린더 원인 특정 후 정비.'),
 'comp':res('압축/기계조건 검사','ECU·동기·레일압·분사 기본조건이 정상인데 시동성이 나쁩니다.', ['압축/밸브타이밍/EGR stuck-open/흡기폐색을 확인한다.'],['기본 ECU/연료압 고장'],['기계적 원인이 압축/누설/타이밍 시험에서 특정'], '기계원인 특정 후 분해.',note='D24 OEM에 없는 압축 허용치를 임의 생성하지 말고 전 실린더 비교 및 해당 서비스 기준을 사용.')
}}
catalog.append({"id":"EN_HARD_START","title":"냉간/열간 시동이 어려움","group":"시동/연료","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# 2 stall
cid='D24_STALL'
circuits[cid]=circuit(cid,'D24 작업/주행 중 꺼짐 · 생존신호 추적',
 [N('ecu','ECU B+/IGN/GND/CAN','control'),N('vref','5V VREF'),N('sync','CRK/CAM'),N('rail','RPS actual/command'),N('imv','IMV / fuel supply','control'),N('inj','Injector drive','load')],
 [E('ecu','vref'),E('ecu','sync'),E('sync','rail'),E('rail','imv'),E('imv','inj')],
 ['stall 직전/직후 ECU comm','5V VREF','RPM/sync','rail actual/command','IMV','injector drive'], 'D24 §9 fuel + §12 electric','꺼지는 순간 사라지는 신호를 잡아 전기/연료/기계를 분리한다.')
graphs['EN_STALL']={"title":"D24 작업/주행 중 엔진이 꺼짐","circuit":cid,"start":"log","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'log':q('1. 꺼지는 순간 로그','엔진이 꺼지는 순간 ECU 통신/전원 또는 전체 계기전원이 함께 끊깁니까?',[('통신/전원 함께 끊김','power'),('통신 유지','rpm')],['가능하면 진단기 기록/플라이트레코드와 DMM MIN/MAX를 동시에 사용한다.','재시동 후 정상값만 보고 판정하지 않는다.']),
 'power':res('ECU 전원/IGN/CAN 간헐 우선','스톨과 ECU 생존신호 소실이 동시에 발생합니다.', ['ECU B+/IGN/GND 전압강하와 main/ECU relay·퓨즈 출력, CAN을 스톨 순간 기록한다.'],['고압펌프 단독고장'],['스톨 순간 특정 공급/통신 회로가 먼저 소실'], '공급/커넥터 원인 특정 후 수리.'),
 'rpm':q('2. 회전신호','스톨 순간 RPM/CRK-CAM sync가 rail pressure보다 먼저 사라집니까?',[('회전신호 먼저 소실','sync'),('회전신호 유지','rail')],['CRK/CAM live-data와 가능하면 파형을 동시에 본다.']),
 'sync':res('CRK/CAM 간헐','엔진 정지 이전에 회전/동기 신호가 먼저 소실됩니다.', ['센서 전원/GND/파형, 커넥터, 열간/진동 재현을 EN_CRK_CAM_SYNC에서 확인한다.'],['연료압 원인'],['신호 소실과 스톨이 반복 동시발생'], '센서/하네스/기계동기 원인 특정 후 정비.'),
 'rail':q('3. 레일압/연료','스톨 직전 rail actual이 command와 분리되어 붕괴합니까?',[('rail actual 붕괴','fuel'),('rail 유지','air')],['RPS 회로가 정상인지 먼저 확인하고 command/actual을 비교한다.']),
 'fuel':res('연료공급/IMV/고압 누설','스톨 직전 연료압 형성이 먼저 무너집니다.', ['EN_FUEL_PRESSURE에서 저압측 공기혼입/필터/IMV/고압펌프/인젝터리턴을 분리한다.'],['CRK/CAM 우선고장'],['연료압 붕괴 원인이 재현시험에서 특정'], '연료고압 부품은 원인 특정 후 분해.'),
 'air':q('4. 공기/EGR/부하','스톨이 유압/주행 부하를 걸 때만 재현되며 ECU·sync·rail이 유지됩니까?',[('부하에서만','load'),('부하와 무관','inj')],['유압 중립과 작동상태를 비교한다.','EGR/흡기폐색 live-data/물리검사를 병행한다.']),
 'load':res('엔진출력 vs 외부과부하 분리','엔진 제어신호가 유지되는데 특정 외부부하에서만 스톨합니다.', ['엔진 무부하 가속성, 유압 relief/펌프 과부하, T/M drag를 분리한다.'],['ECU 생존고장'],['외부부하 제거 시 즉시 스톨 재현 사라짐'], '엔진분해보다 외부부하계통부터 수리.'),
 'inj':res('분사/흡기/기계 추가분리','ECU·sync·rail은 유지되나 스톨합니다.', ['인젝터 구동/기여, EGR stuck, 흡기폐색, 압축·밸브타이밍을 순서대로 확인한다.'],['전원/CAN','기본 rail 압력'],['특정 분사/흡기/기계원인이 재현'], '원인 특정 후 해당 계통만 분해.')
}}
catalog.append({"id":"EN_STALL","title":"작업/주행 중 엔진 꺼짐","group":"시동/연료","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# 3 low power
cid='D24_LOW_POWER'
circuits[cid]=circuit(cid,'D24 부하 힘없음 · 공기/부스트/연료/배기',
 [N('air','Air filter / MAF','source'),N('boost','BPS / hoses / intercooler'),N('turbo','Turbo / actuator','control'),N('egr','EGR','control'),N('fuel','Rail actual / IMV'),N('inj','Injector balance','load'),N('exh','Exhaust restriction','load')],
 [E('air','boost'),E('boost','turbo'),E('turbo','egr'),E('egr','fuel'),E('fuel','inj'),E('inj','exh')],
 ['MAF','BPS command/actual trend','charge hose leak','rail actual/command','injector balance','exhaust restriction'], 'D24 §9 fuel + §10 intake/exhaust','부하에서 공기량·부스트·연료압이 무엇부터 부족해지는지 비교한다.')
graphs['EN_LOW_POWER']={"title":"D24 부하에서 힘이 없음/출력저하","circuit":cid,"start":"air","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'air':q('1. 흡기 기본','에어필터/흡기덕트 막힘·붕괴·누설 및 MAF 값이 정상입니까?',[('이상 있음','air_bad'),('정상','boost')],['무부하가 아니라 실제 부하에서 흡기덕트 수축/누설도 확인한다.','MAF 전원/GND/flow 값을 정상차/엔진상태와 비교한다.']),
 'air_bad':res('흡기/MAF 원인','흡기 저항 또는 MAF 입력 이상이 확인됩니다.', ['필터/덕트 누설·막힘을 복구하고 MAF 회로를 재검증한다.'],['터보 기계고장 확정','인젝터 교환'],['수리 후 부하 출력/MAF 반응 회복'], '흡기 원인부터 수리.'),
 'boost':q('2. 부스트 형성','부하를 걸 때 BPS 실제값이 엔진부하/RPM 상승에 따라 정상적으로 증가하고 charge-air 누설이 없습니까?',[('부스트 부족/누설','turbo'),('부스트 형성 정상','fuel')],['BPS 5V/GND/signal 검증 후 판단한다.','호스·인터쿨러·클램프를 압력/누설 흔적으로 확인한다.']),
 'turbo':q('3. 터보/EGR 분리','흡기누설은 없는데 터보/액추에이터 또는 EGR stuck-open 이상이 확인됩니까?',[('터보/액추에이터 이상','turbo_bad'),('EGR 이상','egr_bad'),('둘 다 뚜렷하지 않음','fuel')],['축유격/휠 접촉/오일흔적/액추에이터 작동을 확인한다.','EGR 명령과 실제 위치/흡기 영향 비교.']),
 'turbo_bad':res('터보/액추에이터 원인','부스트 부족과 터보 기계/제어 이상이 함께 확인됩니다.', ['오일공급/리턴, 휠 손상, 축유격, actuator를 OEM §10 절차로 분리한다.'],['연료압 단독고장'],['터보 원인 수리 후 BPS/출력 회복'], '터보 분해 전 오일/흡배기 외부원인 배제.'),
 'egr_bad':res('EGR 과다개방/제어','부하에서 EGR이 닫혀야 할 조건에 실제 공기량을 떨어뜨리는 이상이 확인됩니다.', ['EGR 위치명령/실제, 밸브 고착, 전기회로를 확인한다.'],['터보 단독고장'],['EGR 격리/수리 후 MAF/BPS/출력 회복'], 'EGR 원인 특정 후 분해.'),
 'fuel':q('4. 연료압/분사','부하에서 rail actual이 command를 따라가고 실린더 기여가 균일합니까?',[('rail actual 부족','fuel_bad'),('한 실린더 기여 이상','inj_bad'),('정상','exh')],['부하 중 command/actual을 기록한다.','인젝터 correction/cut-out/리턴 비교를 사용한다.']),
 'fuel_bad':res('부하 연료압 부족','부하에서만 rail actual이 command를 따라가지 못합니다.', ['EN_FUEL_PRESSURE에서 저압공급/IMV/HP pump/return leak 분리.'],['흡기/부스트 기본원인'],['연료압 원인 수리 후 부하 rail/출력 회복'], '고압펌프는 마지막.'),
 'inj_bad':res('실린더/인젝터 불균형','부하 힘없음과 특정 실린더 기여 이상이 연결됩니다.', ['EN_INJECTOR_SEPARATE에서 전기/리턴/압축 분리.'],['공통 연료압'],['특정 실린더 원인 확인'], '확정 후 해당 실린더만 정비.'),
 'exh':res('배기제한/기계출력 추가검사','공기·부스트·연료가 정상인데 출력이 부족합니다.', ['배기 막힘/DPF 장착사양이면 차압, 배기누설, 압축/밸브타이밍을 확인한다.'],['MAF/BPS/RPS 기본회로'],['배기 또는 기계 원인이 독립시험에서 특정'], '기계분해 전 배기저항을 배제.')
}}
catalog.append({"id":"EN_LOW_POWER","title":"부하에서 힘이 없음/출력저하","group":"출력/연소","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# 4 rough idle
cid='D24_ROUGH_IDLE'
circuits[cid]=circuit(cid,'D24 아이들 부조 · 실린더/rail/공기 분리',
 [N('ecu','ECU / DTC','control'),N('rail','Rail actual/command'),N('inj','Cylinder contribution'),N('return','Injector return'),N('air','MAF/EGR'),N('mech','Compression / mount','load')],
 [E('ecu','rail'),E('rail','inj'),E('inj','return'),E('return','air'),E('air','mech')],
 ['rail actual/command','injector correction/cut-out','return comparison','MAF/EGR','compression comparison'], 'D24 §9 fuel + §10 intake/exhaust + §11 mechanical','공통 rail 불안정과 한 실린더 문제를 먼저 분리한다.')
graphs['EN_ROUGH_IDLE']={"title":"D24 아이들 불안정/부조","circuit":cid,"start":"rail","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'rail':q('1. 공통 rail 안정','아이들에서 rail actual이 command에 안정적으로 따라갑니까?',[('불안정','rail_bad'),('안정','cyl')],['RPS 회로를 검증하고 actual/command 변동을 비교한다.']),
 'rail_bad':res('공통 연료압 제어 우선','부조와 함께 rail actual 제어가 불안정합니다.', ['저압연료/공기혼입/IMV/RPS/고압펌프를 EN_FUEL_PRESSURE로 분리한다.'],['단일 인젝터 확정'],['rail 안정화 후 부조가 같이 개선'], '공통 연료압부터 해결.'),
 'cyl':q('2. 실린더 기여','cut-out/balance 또는 인젝터 correction에서 특정 실린더 차이가 큽니까?',[('특정 실린더','inj'),('공통/뚜렷한 차이 없음','air')],['진단기가 지원하면 cylinder cut-out을 사용한다.','지원 안 하면 배기온도/진동/전류파형을 보조 비교한다.']),
 'inj':res('특정 실린더 분리','특정 실린더 기여가 반복적으로 다릅니다.', ['EN_INJECTOR_SEPARATE에서 구동전류→리턴→압축을 분리한다.'],['공통 rail pressure'],['동일 실린더에서 전기/리턴/압축 중 원인 특정'], '인젝터 교환 전 리턴/압축 배제.'),
 'air':q('3. 공기/EGR','MAF와 EGR 명령/실제에서 아이들 공기량을 흔드는 이상이 있습니까?',[('있음','air_bad'),('없음','mech')],['EGR을 명령변화시켜 실제 반응과 아이들 변화를 확인한다.','흡기누설을 확인한다.']),
 'air_bad':res('흡기/EGR 제어 원인','부조가 공기량/EGR 변화와 연결됩니다.', ['흡기 누설 또는 EGR 고착/전기회로를 수리하고 재평가한다.'],['인젝터 기계고장'],['공기/EGR 복구 후 idle 안정'], '공기계통 먼저.'),
 'mech':res('압축/밸브/마운트 구분','연료압·실린더 분사·공기제어에서 원인이 특정되지 않습니다.', ['압축/누설, 밸브타이밍, 엔진마운트/부하를 비교한다.'],['RPS/BPS 기본회로'],['기계원인 또는 단순 진동전달 원인 특정'], '기계원인 확인 후 분해.')
}}
catalog.append({"id":"EN_ROUGH_IDLE","title":"아이들 불안정/부조","group":"출력/연소","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# Smoke helper graphs

def smoke_graph(gid,title,color,sequence):
    cid='D24_'+gid.replace('EN_','')
    circuits[cid]=circuit(cid,title+' · 원인 분리',
      [N('obs','Smoke condition','measure'),N('air','Air / boost'),N('fuel','Rail / injector'),N('temp','Temperature / preheat'),N('oil','Oil / turbo / breather'),N('mech','Compression / timing')],
      [E('obs','air'),E('obs','fuel'),E('obs','temp'),E('obs','oil'),E('obs','mech')],
      ['냉간/열간/부하/감속 조건','MAF/BPS','rail actual/command','injector balance/return','oil consumption/turbo','compression'],
      'D24 §2 operation + §9 fuel + §10 intake/exhaust + §11 mechanical',
      '연기색만으로 부품을 확정하지 않고 조건과 공기·연료·오일·압축을 교차한다.')
    nodes={
      'cond':q('1. 재현조건','연기는 어느 조건에서 가장 뚜렷합니까?',[('냉간 시동 직후','cold'),('부하/가속','load'),('공회전/상시','steady')],['연기색·냄새·지속시간·부하·냉각수/오일 소모를 기록한다.']),
      'cold':q('2A. 냉간 관련','예열/수온 live-data와 시동 후 연소 안정이 정상입니까?',[('이상','cold_bad'),('정상','common')],['WTS 실제온도 비교, 예열 실제출력, 실린더별 초기 기여를 본다.']),
      'cold_bad':res('냉간 연소조건 우선',f'{color} 연기가 냉간 예열/온도/초기 실린더 기여 이상과 연결됩니다.', ['WTS/예열/인젝터 기여/압축을 분리한다.'],['터보 단독고장'],['냉간 원인 수리 후 연기 감소'], '원인 특정 후 정비.'),
      'load':q('2B. 부하 공기/연료','부하에서 MAF/BPS/rail actual이 명령·엔진상태를 따라갑니까?',[('공기/부스트 이상','air_bad'),('rail/분사 이상','fuel_bad'),('둘 다 정상','common')],['부하에서만 기록한다.','센서 회로 정상 확인 후 데이터를 해석한다.']),
      'air_bad':res('공기/부스트 계통',f'{color} 연기와 흡기/부스트 이상이 함께 있습니다.', ['흡기막힘/charge leak/터보/EGR을 EN_LOW_BOOST로 분리한다.'],['인젝터 단독고장'],['공기계통 복구 후 연기/출력 회복'], '공기계통부터.'),
      'fuel_bad':res('연료/분사 계통',f'{color} 연기와 rail/실린더 분사 이상이 함께 있습니다.', ['EN_FUEL_PRESSURE 및 EN_INJECTOR_SEPARATE로 분리한다.'],['터보 단독'],['연료원인 수리 후 연기 감소'], '연료원인 특정 후.'),
      'steady':q('2C. 오일/냉각수 소모','연기와 함께 엔진오일 또는 냉각수 소모가 확인됩니까?',[('오일 소모','oil'),('냉각수 소모','coolant'),('소모 없음','common')],['레벨을 표시해 실제 변화량/누설을 먼저 확인한다.']),
      'oil':res('오일 유입 경로 검사',f'{color} 연기와 오일소모가 함께 있습니다.', ['터보 compressor/turbine oil leak, breather, valve guide, ring/blow-by를 순서대로 확인한다.'],['연료센서 단독'],['오일 유입 위치가 물리적으로 확인'], '원인 위치 특정 후 분해.'),
      'coolant':res('냉각수 연소실 유입 검사',f'{color} 연기와 냉각수 소모가 함께 있습니다.', ['외부누설 배제 후 압력유지/기포/헤드가스켓·EGR cooler 사양을 점검한다.'],['오일소모 원인'],['냉각수 내부누설 시험 양성'], '내부누설 확인 후 헤드/EGR 계통 분해.'),
      'common':res('분사품질/압축/타이밍 추가분리',f'{color} 연기의 기본 공기·연료·소모 단서가 뚜렷하지 않습니다.', sequence,['단순 색상만으로 부품 확정'],['인젝터/압축/타이밍 중 원인이 독립시험에서 특정'], '특정된 계통만 분해.')
    }
    graphs[gid]={"title":title,"circuit":cid,"start":"cond","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":nodes}
    catalog.append({"id":gid,"title":title,"group":"연기/연소","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

smoke_graph('EN_BLACK_SMOKE','검은연기','검은',['인젝터 과다분사/기여, EGR 과다, 흡기/배기 제한, 기계타이밍을 확인한다.'])
smoke_graph('EN_WHITE_SMOKE','흰연기','흰',['냉간 미연소, 인젝터 분무/누설, 압축, 냉각수 유입을 구분한다.'])
smoke_graph('EN_BLUE_SMOKE','청색연기/오일소모','청색',['터보 오일씰/리턴, 브리더, 밸브가이드, 링/블로바이를 구분한다.'])

# Overheat
cid='D24_OVERHEAT'
circuits[cid]=circuit(cid,'D24 과열 · 센서오류 vs 실제 열원',
 [N('wts','WTS / actual temp'),N('cool','Coolant level / cap','source'),N('air','Radiator airflow / fan-belt'),N('pump','Water pump / circulation','control'),N('therm','Thermostat','control'),N('load','Combustion / head leak','load')],
 [E('wts','cool'),E('cool','air'),E('air','pump'),E('pump','therm'),E('therm','load')],
 ['WTS live vs contact thermometer','coolant level/cap','radiator inlet/outlet pattern','belt/pump flow','thermostat opening behavior','combustion gas/internal leak'], 'D24 §7 cooling + §12 WTS','실제 과열인지 센서표시인지 먼저 분리한 뒤 순환/방열/열발생으로 좁힌다.')
graphs['EN_OVERHEAT']={"title":"D24 엔진 과열","circuit":cid,"start":"real","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'real':q('1. 실제 과열 확인','WTS live 값과 비접촉/접촉 온도 측정이 같은 방향으로 실제 과열을 가리킵니까?',[('계기/센서만 높음','sensor'),('실제 과열','level')],['WTS 저항/신호와 실제 하우징 온도를 교차한다.']),
 'sensor':res('WTS/표시계통 우선','실제 엔진은 과열이 아닌데 표시/진단값만 높습니다.', ['E_D24_WATER_TEMP로 센서/배선/GND를 확인한다.'],['워터펌프','헤드가스켓'],['WTS/표시 수리 후 값 일치'], '냉각계 분해 금지.'),
 'level':q('2. 냉각수/압력유지','냉각수 레벨, 외부누설, 라디에이터캡/압력유지가 정상입니까?',[('이상','level_bad'),('정상','air')],['냉간 레벨과 압력테스트로 확인한다.']),
 'level_bad':res('냉각수 부족/압력유지 불량','냉각계 기본량 또는 압력유지가 무너집니다.', ['누설위치를 특정하고 캡/호스/라디에이터를 확인한다.'],['서모스탯 확정'],['누설/캡 원인 수리 후 과열 재현 사라짐'], '누설원인부터.'),
 'air':q('3. 방열/팬/벨트','라디에이터 외부 막힘, 팬 풍량, 벨트 상태가 정상입니까?',[('이상','air_bad'),('정상','flow')],['부하상태에서 팬 풍량과 라디에이터 전후 온도패턴을 본다.']),
 'air_bad':res('방열/팬구동 원인','냉각수는 있으나 열을 외기로 버리지 못합니다.', ['핀 막힘/팬/벨트를 복구한다.'],['워터펌프 내부'],['방열 복구 후 온도 안정'], '방열계통 먼저.'),
 'flow':q('4. 순환/서모스탯','워터펌프 순환과 서모스탯 개방이 정상입니까?',[('순환 부족','pump_bad'),('서모스탯 이상','therm_bad'),('둘 다 정상','internal')],['상하 호스/라디에이터 온도패턴과 냉각수 순환을 비교한다.','서모스탯은 OEM 검사절차로 개방을 확인한다.']),
 'pump_bad':res('워터펌프/순환 불량','방열부는 정상인데 냉각수 순환이 부족합니다.', ['펌프 구동/임펠러/통로 막힘을 확인한다.'],['WTS 센서'],['펌프/통로 원인이 확인'], '순환 원인 특정 후 분해.'),
 'therm_bad':res('서모스탯 불량','순환경로 중 서모스탯 개방 이상이 확인됩니다.', ['서모스탯 OEM 온도시험/물리검사로 확정한다.'],['라디에이터 외부막힘'],['시험에서 개방 이상 재현'], '서모스탯 교환.'),
 'internal':res('연소가스/내부열원 추가검사','레벨·방열·순환·서모스탯이 정상인데 과열됩니다.', ['헤드가스켓 연소가스, 분사/타이밍, 지속 과부하를 확인한다.'],['기본 냉각외부계통'],['내부누설/연소 또는 과부하 원인이 특정'], '헤드 분해는 내부누설 양성 후.')
}}
catalog.append({"id":"EN_OVERHEAT","title":"엔진 과열","group":"냉각/윤활","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# Low oil pressure
cid='D24_LOW_OIL_PRESS'
circuits[cid]=circuit(cid,'D24 저오일압 · 센서/실압/공급/누설',
 [N('opts','OPTS pressure signal'),N('gauge','Mechanical oil gauge'),N('level','Oil level/viscosity/filter','source'),N('pump','Oil pump/relief','control'),N('leak','Turbo/gallery/internal leak'),N('bearing','Bearing clearance','load')],
 [E('opts','gauge'),E('gauge','level'),E('level','pump'),E('pump','leak'),E('leak','bearing')],
 ['OPTS 5V/GND/signal','mechanical oil pressure port','oil/filter','pump/relief','external/internal leak'], 'D24 §8 lubrication + §12 OPTS','센서 표시와 실제 압력을 기계 게이지로 먼저 분리한다.',unverified=['정확한 압력 포트/규격은 해당 엔진 사양 OEM 절차에 맞춰 연결'])
graphs['EN_LOW_OIL_PRESS']={"title":"D24 엔진오일 압력 낮음/경고","circuit":cid,"start":"verify","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'verify':q('1. 센서 vs 실제압','OPTS 회로를 검증하고 기계식 게이지로 실제 오일압 저하가 확인됩니까?',[('실압 정상·센서값만 이상','sensor'),('실압도 낮음','oil')],['OPTS pin3 ECU165 5V, pin1 ECU148 GND, pin4 ECU111 pressure를 확인한다.','가능한 OEM 압력포트에 기계게이지 연결.']),
 'sensor':res('OPTS/배선 원인','기계 오일압은 정상인데 ECU 표시만 낮습니다.', ['OPTS 전원/GND/signal과 커넥터를 수리한다.'],['오일펌프','베어링'],['센서/배선 복구 후 표시와 기계압 일치'], '윤활계 분해 금지.'),
 'oil':q('2. 오일 기본조건','오일레벨·점도/규격·희석·필터가 정상입니까?',[('이상','oil_bad'),('정상','leak')],['연료희석/과열오일/필터 막힘 또는 잘못된 부품을 확인한다.']),
 'oil_bad':res('오일/필터 조건','실압 저하를 만들 수 있는 오일 기본조건 이상이 있습니다.', ['OEM 규격으로 정상화 후 실제압 재측정.'],['펌프 확정'],['정상화 후 실제압 회복'], '펌프 분해 전 해결.'),
 'leak':q('3. 외부/대누설','터보 오일공급·리턴, 필터하우징, 갤러리 외부누설 또는 내부 대누설 징후가 있습니까?',[('누설 있음','leak_bad'),('뚜렷한 누설 없음','pump')],['누유량과 압력변화를 함께 본다.']),
 'leak_bad':res('윤활유 누설 경로','펌프보다 먼저 압력손실 경로가 확인됩니다.', ['확인된 누설을 복구 후 기계압 재측정.'],['펌프 마모'],['누설 수리 후 압력 회복'], '누설부만 정비.'),
 'pump':q('4. 펌프/릴리프','오일펌프 구동과 relief valve에 열린고착/손상이 확인됩니까?',[('릴리프/펌프 이상','pump_bad'),('정상','bearing')],['OEM §8 펌프/필터 어셈블리 검사절차 사용.']),
 'pump_bad':res('오일펌프/릴리프 원인','기본 오일·누설을 배제한 뒤 펌프/릴리프 이상이 확인됩니다.', ['확인된 펌프/릴리프 부품을 정비.'],['센서 표시오류'],['정비 후 기계압 회복'], '확정 후 펌프 분해.'),
 'bearing':res('내부 베어링/간극 손실 의심','펌프/릴리프와 외부조건이 정상인데 실제압이 계속 낮습니다.', ['열간/냉간 압력패턴, 금속분, 크랭크/캠 베어링 간극을 OEM 기준으로 검사한다.'],['OPTS','외부누설'],['내부간극/손상 확인'], '엔진분해는 내부손실 증거 확보 후.')
}}
catalog.append({"id":"EN_LOW_OIL_PRESS","title":"엔진오일 압력 낮음/경고","group":"냉각/윤활","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# low boost
cid='D24_LOW_BOOST'
circuits[cid]=circuit(cid,'D24 부스트 부족 · 센서/누설/터보/EGR/배기',
 [N('bps','BPS 5V/GND/signal'),N('air','Air filter / MAF'),N('hose','Charge hose/intercooler'),N('turbo','Turbo wheel/shaft/actuator'),N('egr','EGR'),N('exh','Exhaust leak/restriction')],
 [E('bps','air'),E('air','hose'),E('hose','turbo'),E('turbo','egr'),E('egr','exh')],
 ['BPS circuit','MAF','charge leak test','turbo shaft/actuator','EGR command/actual','exhaust leak/restriction'], 'D24 §10 intake/exhaust + §12 BPS/MAF','센서가 틀린지 실제 부스트가 부족한지를 먼저 분리한다.')
graphs['EN_LOW_BOOST']={"title":"D24 부스트 부족/터보 힘없음","circuit":cid,"start":"sensor","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'sensor':q('1. BPS 검증','BPS 5V/GND/signal과 대기압/무부하 기준값이 물리적으로 타당합니까?',[('센서회로 이상','sensor_bad'),('센서 정상·실제 부스트 낮음','air')],['BPS pin1 ECU161 5V, pin2 ECU167 GND, pin3 ECU112 signal을 확인한다.']),
 'sensor_bad':res('BPS/배선 원인','실제 터보를 분해하기 전에 부스트 측정회로가 잘못됐습니다.', ['E_D24_BOOST_PRESSURE로 회로를 수리한다.'],['터보 기계고장'],['BPS 수리 후 실제/진단값 일치'], '터보 분해 금지.'),
 'air':q('2. 흡기공급','에어필터/MAF/흡기덕트에 막힘·붕괴가 있습니까?',[('이상','air_bad'),('정상','leak')],['부하에서 덕트 수축까지 본다.']),
 'air_bad':res('흡기 제한','터보 입구 공기공급이 제한됩니다.', ['필터/덕트/MAF 문제를 복구.'],['터보 내부'],['복구 후 BPS/출력 회복'], '흡기부터.'),
 'leak':q('3. 차지에어 누설','터보 출구→인터쿨러→흡기매니폴드에서 압력누설이 있습니까?',[('누설 있음','leak_bad'),('없음','turbo')],['오일자국/클램프/호스 균열과 압력누설 시험을 사용한다.']),
 'leak_bad':res('차지에어 누설','터보가 만든 압력이 흡기까지 전달되지 않습니다.', ['누설부 수리 후 부하 BPS 재시험.'],['터보 휠'],['수리 후 boost/출력 회복'], '누설부 수리.'),
 'turbo':q('4. 터보 기계/제어','터보 휠 손상·하우징 접촉·비정상 유격·오일공급/리턴 또는 actuator 이상이 있습니까?',[('이상','turbo_bad'),('정상','egr')],['D24 §10 turbo inspection을 사용한다.']),
 'turbo_bad':res('터보 자체/액추에이터','외부흡기 정상 후 터보 기계/제어 이상이 확인됩니다.', ['오일공급 원인을 함께 해결하고 터보 정비.'],['BPS 회로'],['터보 정비 후 boost 회복'], '확정 후 터보 분해.'),
 'egr':q('5. EGR/배기','EGR 과다개방 또는 배기누설/막힘이 확인됩니까?',[('EGR 이상','egr_bad'),('배기 이상','exh_bad'),('없음','other')],['EGR 명령/실제 위치, 터빈 전단 배기누설/후단 restriction을 본다.']),
 'egr_bad':res('EGR 과다/고착','EGR 상태가 실제 흡기량/부스트를 낮춥니다.', ['EGR 밸브/회로를 수리.'],['터보 교환'],['EGR 정상화 후 boost 회복'], 'EGR만 정비.'),
 'exh_bad':res('배기 누설/제한','터빈 구동에 필요한 배기 에너지 또는 후단 배출이 비정상입니다.', ['누설/막힘 위치 수리.'],['터보 코어 단독'],['배기 수리 후 boost 회복'], '배기부터.'),
 'other':res('연료/엔진출력과 교차진단','부스트계통 자체에서 원인이 특정되지 않습니다.', ['rail actual/command, injector contribution, 압축/타이밍을 EN_LOW_POWER에서 확인한다.'],['BPS/흡기누설/터보/EGR 기본'],['엔진출력 원인이 특정'], '터보 재교환 금지.')
}}
catalog.append({"id":"EN_LOW_BOOST","title":"부스트 부족/터보 힘없음","group":"흡배기/과급","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# preheat
cid='D24_PREHEAT'
circuits[cid]=circuit(cid,'D24 예열/에어히터 · 명령→릴레이→부하',
 [N('ecu','ECU preheat request','control'),N('fuse','Heater supply/fuse','source'),N('relay','Air heater relay','control'),N('heater','Air heater','load'),N('gnd','Engine GND','ground')],
 [E('ecu','relay'),E('fuse','relay'),E('relay','heater'),E('heater','gnd')],
 ['ECU request/indicator','relay coil command','relay input/output loaded voltage','heater current','heater GND'], 'D24 §12-8 Air Heater','표시등이 아니라 히터 실제 부하전류를 본다.',unverified=['차량 사양별 에어히터 퓨즈/릴레이 cavity는 차량 회로와 매칭 필요'])
graphs['EN_PREHEAT']={"title":"D24 예열/에어히터 작동 안 됨","circuit":cid,"start":"request","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'request':q('1. 예열 요구','냉간 조건에서 ECU/표시상 예열 요구가 발생합니까?',[('요구 없음','input'),('요구 있음','relay')],['WTS/흡기온도 값이 실제와 맞는지 먼저 확인한다.']),
 'input':res('예열 요구 입력/ECU 조건','히터보다 ECU가 예열을 요구하지 않는 상태입니다.', ['WTS/MAF-IAT 값, ECU DTC/전원/조건을 확인한다.'],['히터 코일 단선 확정'],['잘못된 온도입력/제어조건 수정 후 요구 발생'], '히터 교환 전 제어조건 해결.'),
 'relay':q('2. 릴레이 부하측','예열 요구 시 릴레이 입력은 유지되고 출력과 히터 전류가 발생합니까?',[('입력 있음·출력 없음','relay_bad'),('출력 있음·전류 없음/작음','heater'),('출력/전류 정상','ok')],['릴레이 coil command와 load input/output을 동시에 측정한다.']),
 'relay_bad':res('예열 릴레이/소켓/제어','공급은 있는데 릴레이 출력이 부하상태에서 전달되지 않습니다.', ['coil 명령 정상 여부로 릴레이 접점 vs 제어를 분리하고 소켓 장력/열화를 확인한다.'],['히터 자체'],['바이패스/교환 후 부하전류 회복'], '릴레이/소켓 원인 특정 후.'),
 'heater':res('에어히터/부하회로','릴레이 출력은 정상인데 히터가 실제 전류를 소비하지 않습니다.', ['히터 양단전압/저항/접지와 연결부를 확인한다.'],['ECU 조건'],['히터 단선/접촉불량 확인'], '히터 원인 확인 후 교환.'),
 'ok':res('예열계통 기본 정상','예열 요구·출력·부하전류가 모두 존재합니다.', ['시동불량이면 EN_HARD_START로 이동한다.'],['예열 전기계통'],['동일 조건에서 예열 동작 재현'], '예열부품 교환 금지.')
}}
catalog.append({"id":"EN_PREHEAT","title":"예열/에어히터 작동 안 됨","group":"시동/연료","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# fuel pressure separation
cid='D24_FUEL_PRESS'
circuits[cid]=circuit(cid,'D24 rail 압력 부족 · 저압→IMV→HP→return',
 [N('tank','Tank / filter / air','source'),N('imv','IMV ECU177 PWM','control'),N('pump','High pressure pump','control'),N('rail','Common rail / RPS'),N('return','Injector return/leak','load')],
 [E('tank','imv'),E('imv','pump'),E('pump','rail'),E('rail','return')],
 ['fuel inlet condition/air','IMV command','RPS actual/command','injector return comparison'], 'D24 §9 fuel + §12 RPS/IMV','고압펌프를 마지막에 판단한다.',unverified=['D24 OEM에 확인되지 않은 크랭킹 rail MPa/리턴량 숫자는 임의 생성 금지'])
graphs['EN_FUEL_PRESSURE']={"title":"D24 rail 압력 부족/형성 안 됨","circuit":cid,"start":"rps","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'rps':q('1. RPS 신뢰성','RPS 5V/GND/signal이 정상이고 진단값이 물리적으로 타당합니까?',[('RPS 회로 이상','rps_bad'),('RPS 정상','low')],['RPS pin3 ECU138 5V, pin2 ECU119 GND, pin1 ECU135 signal 확인.']),
 'rps_bad':res('RPS 회로 먼저','압력 자체보다 측정회로 이상이 있습니다.', ['E_D24_RAIL_PRESSURE에서 수리.'],['고압펌프'],['RPS 값 정상화'], '고압계 분해 금지.'),
 'low':q('2. 저압연료/공기혼입','탱크→필터→펌프입구 연료공급에 공기혼입·막힘·누설이 있습니까?',[('이상','low_bad'),('정상','imv')],['투명호스/프라이밍 반응/필터상태/흡입누설을 확인한다.']),
 'low_bad':res('저압공급 원인','고압펌프 입력조건이 확보되지 않았습니다.', ['필터/호스/프라이밍/탱크 통기 원인을 수리.'],['HP pump 확정'],['수리 후 rail actual 회복'], '저압측부터.'),
 'imv':q('3. IMV 제어','ECU177 IMV PWM 명령과 밸브/배선 반응이 정상입니까?',[('명령/배선 이상','imv_bad'),('정상','return')],['가능하면 전류/듀티 파형과 rail 반응을 함께 본다.']),
 'imv_bad':res('IMV 제어 원인','저압공급은 정상이나 펌프 유입량 제어가 비정상입니다.', ['IMV 하네스/코일/밸브 고착을 분리한다.'],['HP pump 내부'],['IMV 복구 후 rail 반응 회복'], 'IMV 확인 후.'),
 'return':q('4. rail 누설/인젝터 리턴','인젝터 return/rail 누설 비교에서 과다 누설 경로가 확인됩니까?',[('특정 인젝터/누설 확인','return_bad'),('뚜렷한 누설 없음','pump')],['모델 OEM 리턴시험 수치가 없으면 실린더간 비교로 1차 분리하고 임의 mL 기준 금지.']),
 'return_bad':res('고압 누설/인젝터 리턴','펌프가 만든 연료가 rail에서 유지되지 못하는 경로가 확인됩니다.', ['확인된 인젝터/rail leak를 정비.'],['HP pump 확정'],['누설 정비 후 rail actual 회복'], '누설경로 먼저.'),
 'pump':res('고압펌프 기계성능 의심','RPS·저압공급·IMV·과다리턴을 배제했는데 rail pressure가 형성되지 않습니다.', ['고압펌프 기계검사/전문 bench test로 최종 확인한다.'],['RPS','저압공급','IMV','과다리턴'],['펌프 성능불량이 별도 시험에서 확인'], '이 조건에서만 고압펌프 분해/교환.')
}}
catalog.append({"id":"EN_FUEL_PRESSURE","title":"rail 압력 부족/형성 안 됨","group":"시동/연료","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# CRK/CAM sync
cid='D24_SYNC'
circuits[cid]=circuit(cid,'D24 CRK/CAM · 전원/파형/동기/기계타이밍',
 [N('ecu','ECU supply','source'),N('crk','CRK pair ECU136/160 + shield187'),N('cam','CAM signal/GND'),N('scope','Scope phase/sync'),N('mech','Trigger wheel / timing','load')],
 [E('ecu','crk'),E('ecu','cam'),E('crk','scope'),E('cam','scope'),E('scope','mech')],
 ['CRK waveform','CAM waveform','ECU RPM/sync','shield/ground','mechanical timing'], 'D24 §12-3/#2/#3 + §12-14','센서교환 전 파형이 센서쪽에서 깨지는지 ECU쪽에서 깨지는지 비교한다.',unverified=['CAM connector-face numeric orientation is kept non-graphical until OEM face orientation is rechecked'])
graphs['EN_CRK_CAM_SYNC']={"title":"D24 CRK/CAM 동기/RPM 신호 이상","circuit":cid,"start":"rpm","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'rpm':q('1. 진단 RPM/동기','크랭킹 중 RPM과 sync 상태가 안정적입니까?',[('RPM 0/간헐 또는 sync 불량','scope'),('정상','ok')],['간헐은 MIN/MAX가 아니라 진단기 record와 scope가 유리하다.']),
 'scope':q('2. 센서측 파형','CRK/CAM 센서 커넥터에서 파형이 안정적입니까?',[('센서측부터 깨짐','sensor'),('센서측 정상·ECU측 깨짐','harness'),('둘 다 정상인데 sync 불량','mech')],['CRK pair와 CAM 신호를 오실로스코프로 확인한다.','열간/진동 조건을 재현한다.']),
 'sensor':res('CRK/CAM 센서/기계 타깃','센서 바로 출력에서 파형이 불안정합니다.', ['센서 설치/갭/오염/타깃 휠 손상과 센서 자체를 검사한다.'],['ECU 입력단'],['센서/타깃 수정 후 파형 회복'], '센서 원인 확인 후 교환.'),
 'harness':res('센서→ECU 하네스/실드','센서측 파형은 정상인데 ECU 입력에서 손실됩니다.', ['핀장력/도체/실드/단락을 양끝 파형 비교로 구간분리한다.'],['센서 자체'],['하네스 수리 후 ECU측 파형과 RPM 회복'], '하네스만 수리.'),
 'mech':res('기계 타이밍/위상 문제','두 센서 파형은 존재하지만 ECU 동기가 맞지 않습니다.', ['타이밍기어/캠-크랭크 관계와 trigger wheel 위치를 OEM 기계타이밍 기준으로 확인한다.'],['단순 센서단선'],['기계위상 이상 확인'], '기계위상 증거 후 타이밍부 분해.'),
 'ok':res('CRK/CAM 기본 정상','크랭킹 RPM/동기가 안정적입니다.', ['무시동이면 E_D24_CRANK_NO_START의 rail 단계로 이동.'],['CRK/CAM'],['동일 조건 반복 정상'], '센서 교환 금지.')
}}
catalog.append({"id":"EN_CRK_CAM_SYNC","title":"CRK/CAM 동기/RPM 신호 이상","group":"ECU/센서","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# injector separation
cid='D24_INJECTOR'
circuits[cid]=circuit(cid,'D24 인젝터 · 전기구동/리턴/압축 분리',
 [N('ecu','ECU injector drive','control'),N('inj','INJ #1~4 connector','load'),N('current','Current waveform'),N('return','Return/leak comparison'),N('comp','Compression / cylinder mech','load')],
 [E('ecu','inj'),E('inj','current'),E('inj','return'),E('return','comp')],
 ['INJ1 ECU126/127','INJ2 174/150','INJ3 175/151','INJ4 125/103','current waveform','return compare','compression'], 'D24 §9 injector + §12-13','인젝터 교환 전 전기구동·리턴·실린더기계를 분리한다.')
graphs['EN_INJECTOR_SEPARATE']={"title":"D24 특정 인젝터/실린더 이상 분리","circuit":cid,"start":"drive","engine_sensor_map":"engine_sensor_map_d24_v1.json","nodes":{
 'drive':q('1. 전기구동','의심 실린더 인젝터의 ECU drive/current waveform이 다른 실린더와 비슷합니까?',[('구동 없음/파형 다름','elec'),('구동 정상','return')],['시험등을 직접 연결하지 말고 전류클램프/오실로스코프/진단기 기능을 사용한다.','INJ OEM ECU pair를 사용한다.']),
 'elec':q('2. ECU vs 하네스','ECU측 구동은 나오는데 인젝터 커넥터에서 사라집니까?',[('ECU 출력 있음·인젝터쪽 없음','harness'),('ECU 출력 자체 없음','ecu')],['양끝을 같은 조건에서 비교한다.']),
 'harness':res('인젝터 하네스/커넥터','ECU 출력은 있으나 인젝터까지 전달되지 않습니다.', ['커넥터 핀장력/단선/단락을 구간분리한다.'],['인젝터 기계불량'],['하네스수리 후 파형/기여 회복'], '인젝터 교환 금지.'),
 'ecu':res('ECU 구동허가/드라이버','rail/sync 조건이 정상인데 특정/공통 인젝터 드라이브가 없습니다.', ['DTC, 공급/허가, ECU driver를 동일 실린더/다른 실린더와 비교한다.'],['인젝터 리턴'],['ECU출력 문제로 특정'], 'ECU는 전원/GND/CAN/외부회로 배제 후 판단.'),
 'return':q('3. 리턴/내부누설','의심 실린더 return이 다른 실린더와 반복적으로 크게 다릅니까?',[('과다/비정상','return_bad'),('비슷함','comp')],['OEM 수치 미확정이면 동조건 실린더 비교로 1차 판정한다.']),
 'return_bad':res('인젝터 내부누설/기계','전기구동은 정상이나 해당 인젝터 내부누설이 비정상입니다.', ['연료오염/rail 상태를 같이 확인하고 인젝터 전문검사/교환.'],['ECU driver'],['인젝터 교환/bench test에서 원인 확인'], '리턴 이상 확인 후 인젝터 정비.'),
 'comp':q('4. 실린더 기계','전기구동과 리턴이 정상인데 해당 실린더 압축/기계상태가 정상입니까?',[('압축/기계 이상','mech'),('정상','quality')],['압축/누설/밸브를 실린더 비교한다.']),
 'mech':res('실린더 기계원인','인젝터를 탓하기 전에 해당 실린더 기계상태 이상이 확인됩니다.', ['밸브/압축/헤드/피스톤 원인을 추가검사.'],['인젝터 전기/리턴'],['기계시험 양성'], '기계원인 특정 후 엔진분해.'),
 'quality':res('분사품질/노즐 정밀검사','구동·리턴·압축이 정상인데 해당 실린더 기여가 계속 다릅니다.', ['인젝터 bench spray/보정 및 연료품질을 확인한다.'],['하네스','대량 압축불량'],['bench test에서 분사품질 이상 확인'], 'bench 근거 후 인젝터 교환.')
}}
catalog.append({"id":"EN_INJECTOR_SEPARATE","title":"특정 인젝터/실린더 이상 분리","group":"시동/연료","circuit":cid,"readiness":"FIELD_EXECUTABLE"})

# Add D24 sensor map reference to every engine graph.
for g in graphs.values(): g.setdefault('engine_sensor_map','engine_sensor_map_d24_v1.json')

out={
 "version":"2.0-d24-field-expert",
 "engine":"D24NAP",
 "manual":"950106-01198",
 "source_rule":"OEM 확인값 우선. OEM 미확인 숫자는 임의 판정 금지. command/actual·정상측 비교·격리·부하/파형시험으로 대체.",
 "external_crosscheck":[
   "Doosan D24NAP O&M 950106-01198 chapters 7 cooling, 8 lubrication, 9 fuel, 10 intake/exhaust, 12 electric",
   "D20/25/30/33S(SE)-7 vehicle service manual SM1018-01 for installed vehicle context"
 ],
 "catalog":catalog,"circuits":circuits,"graphs":graphs,
 "coverage":{"benchmark_bundles":21,"graphs":len(graphs),"status":"21/21 benchmark symptom bundles represented; exact OEM limits/pins remain explicitly unverified where source does not establish them"}
}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('wrote',OUT,'graphs',len(graphs),'circuits',len(circuits))
