#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/test_point_locator_v1.json'
d=json.loads(P.read_text(encoding='utf-8'))

def pt(id,label,where,connect,condition,expected='',decision='',source='FIELD_METHOD',x=.5,y=.5,note=''):
    o={'id':id,'label':label,'where':where,'connect':connect,'condition':condition,'source_class':source,'x':x,'y':y}
    if expected:o['expected']=expected
    if decision:o['decision']=decision
    if note:o['note']=note
    return o

def grp(title,summary,points,rules,sensors,refs,limitations=None,tools=None,conditions=None,note=''):
    return {'title':title,'system':'엔진','summary':summary,'tools':tools or ['DMM/백프로브','진단기','필요 시 오실로스코프'],
            'conditions':conditions or ['실패/증상이 실제 재현되는 상태에서 기록','센서 커넥터 연결상태 부하시험 우선','OEM 미확인 임계값은 정상차/추세/격리로 판단'],
            'points':points,'decision_rules':rules,'oem_images':[],'diagram_note':note or '센서교환표가 아니라 전원/신호/기계상태를 가르는 측정순서만 재작성.',
            'source_refs':refs,'limitations':limitations or [],'focus_ids':['ENGINE_BAY'],'sensor_focus_ids':sensors}

g=d['groups']

# ECU health / communication
g['ENG_ECU_HEALTH']=grp(
 'D24 ECU 무통신 · 전원/GND/CAN/VREF','진단기 무응답만으로 ECU를 교환하지 않는다. 다른 모듈 통신 비교→ECU 전원/GND→CAN 도달→5V 외부부하 순으로 컨트롤러 생존을 확인한다.',
 [
  pt('EH1','SENSOR 15A fuse','D24 엔진 센서/ECU 전원 분배의 SENSOR 15A FUSE','퓨즈 양단 부하전압','KEY ON','D24 §12-7에 SENSOR 15A FUSE 명시','입력 정상/출력 없음이면 퓨즈/소켓; 양쪽 정상인데 ECU 무응답이면 다음으로','OEM_EXACT',.20,.30),
  pt('EH2','ECU B+ / IGN 공급','ECU DCM 3.7 전원 입력 계통','백프로브로 B+/IGN과 ECU GND 동시 기록','KEY ON 및 크랭킹/증상 순간','','공급이 흔들리면 CAN/ECU 내부판정 전에 전원계통을 수리','OEM_FUNCTION_PIN_VERIFY',.36,.40,'기능은 OEM 확인. 이 화면에서는 미확정 숫자 cavity를 만들지 않음'),
  pt('EH3','ECU POWER GND','ECU 전원접지→배터리 -POST','부하 중 전압강하','KEY ON/크랭킹','','전원은 유지되는데 GND가 뜨면 접지/체결/하네스 우선','FIELD_METHOD',.36,.63),
  pt('EH4','CAN/진단 통신 비교','진단커넥터 및 ECU CAN 경로','다른 모듈 응답과 D24 ECU 응답 비교; 필요 시 CAN 파형/물리선 확인','KEY ON','','다른 모듈 정상 + ECU까지 CAN 도달 + D24만 무응답이면 ECU 내부 CAN/CPU 가능성 상승','OEM_PLUS_FIELD',.58,.35),
  pt('EH5','5V VREF 생존','RPS/BPS/OPTS/EGR VREF branch','ECU138/161/165/164와 센서 분리 전후 비교','KEY ON','확인된 branch는 nominal 5V','외부센서 분리로 5V가 회복되면 외부단락; 전부 분리해도 죽으면 ECU 내부 VREF 가능성','OEM_PLUS_FIELD',.74,.52),
 ],
 ['다른 모듈도 전부 무통신이면 ECU 단품보다 공통 진단전원/CAN부터 본다.','ECU B+/IGN/GND가 부하상태에서 정상이라는 확인 없이 ECU를 확정하지 않는다.','5V 외부부하를 분리하지 않고 VREF 붕괴를 ECU 내부고장으로 단정하지 않는다.'],
 ['RPS','BPS','OPTS','EGR'],['D24 §12-7, §12-18~20; 600123-00120 ECU circuit'],
 ['정확 ECU 전원 connector cavity 중 현재 DB에 확정되지 않은 것은 표시하지 않음.'])

# VREF
g['ENG_VREF']=grp(
 'D24 5V 기준전압 · 외부단락 vs ECU 내부','여러 센서가 동시에 비현실값을 보이면 센서 여러 개를 바꾸지 말고 공통 5V branch를 순차 분리한다.',
 [
  pt('VR1','RPS VREF','커먼레일 RPS pin3 / ECU138','백프로브','KEY ON','5V','이 branch만 비정상이면 RPS/하네스; 여러 branch 동시면 공통부하/ECU','OEM_EXACT',.22,.30),
  pt('VR2','BPS VREF','흡기매니폴드 BPS pin1 / ECU161','백프로브','KEY ON','5V','BPS 분리 후 회복되면 BPS/해당 하네스 단락','OEM_EXACT',.45,.30),
  pt('VR3','OPTS VREF','오일압/온도센서 pin3 / ECU165','백프로브','KEY ON','5V','OPTS 분리 후 회복되면 OPTS/해당 하네스 단락','OEM_EXACT',.68,.30),
  pt('VR4','EGR VREF3','EGR 위치센서 VREF / ECU164','백프로브','KEY ON','VREF3 5V branch','EGR 분리 후 회복되면 EGR/하네스 단락','OEM_EXACT',.80,.50),
  pt('VR5','외부 5V 부하 순차분리','RPS/BPS/OPTS/EGR 및 같은 VREF 공유부하','한 번에 하나씩 분리하면서 VR1~4 동시 기록','KEY ON','','특정 부하 분리 때 전체 branch가 회복되면 그 부하/배선; 전부 분리해도 안 회복되면 ECU 내부 VREF 가능성','FIELD_ISOLATION',.50,.70),
 ],
 ['branch 하나만 낮으면 해당 센서/배선을 먼저 격리한다.','여러 branch가 동시에 낮으면 외부 5V 부하를 하나씩 분리해 공통단락을 찾는다.','모든 외부부하를 제외한 뒤에도 ECU측 5V가 비정상일 때만 ECU 내부 VREF를 강하게 본다.'],
 ['RPS','BPS','OPTS','EGR'],['D24 §12-6~15'],['OEM이 별도 허용공차를 명시하지 않은 곳에서 4.8V/5.2V 같은 임의 PASS 범위를 만들지 않음.'])

# Crank/no-start composite
g['ENG_CRANK_START']=grp(
 'D24 크랭킹 무시동/냉열간 난시동/스톨 · 생존→동기→rail→분사','연료부품부터 교환하지 않는다. ECU 통신과 RPM/sync가 살아 있는지 확인한 뒤 rail actual/command, RPS, IMV, 인젝터 구동/리턴으로 내려간다.',
 [
  pt('CS1','ECU 통신/로그','진단커넥터','D24 ECU 응답 + 실패 순간 로그','크랭킹 또는 스톨 순간','','무통신이면 이 흐름을 멈추고 ENG_ECU_HEALTH로','FIELD_METHOD',.12,.28),
  pt('CS2','Crank RPM / CRK-CAM sync','진단기 RPM/sync + CRK/CAM 회로','진단기 record; 간헐이면 오실로스코프 병행','크랭킹/스톨 순간','','RPM/sync가 끊기면 rail부품보다 CRK/CAM/타이밍으로','OEM_PLUS_FIELD',.28,.45),
  pt('CS3','Rail actual vs commanded','진단기 rail actual/command','두 값을 같은 시간축으로 기록','크랭킹/부하/스톨 직전','','actual이 command를 따라가지 못하면 RPS 신뢰성→저압공급→IMV→HP/return 순서','FIELD_METHOD',.48,.30,'OEM 미확인 “시동 최소 MPa” 임계값은 만들지 않음'),
  pt('CS4','RPS 5V/GND/signal','커먼레일 끝단 RPS','pin3 ECU138 5V / pin2 ECU119 GND / pin1 ECU135 signal','KEY ON 및 크랭킹','pin3=5V 기능 확인','센서회로가 불신뢰면 rail actual 값으로 펌프를 판정하지 않음','OEM_EXACT',.58,.55),
  pt('CS5','저압 연료/공기 혼입','탱크→필터→고압펌프 입구','투명구간/프라이밍/누설 흔적/필터 상태 비교','크랭킹 전·중','','공기혼입/공급부족을 제거하기 전 고압펌프를 확정하지 않음','FIELD_METHOD',.36,.72),
  pt('CS6','IMV command','고압펌프 IMV / ECU177 PWM','진단기 command + 가능 시 스코프/전류','크랭킹/부하','ECU177 PWM control 기능','명령 정상인데 rail 형성불량이면 펌프/고압/return 쪽; 명령 자체 비정상이면 제어/입력 쪽','OEM_PLUS_FIELD',.72,.35),
  pt('CS7','Injector drive','인젝터 #1~4','전류클램프/오실로스코프 또는 진단기 기능','크랭킹/실패 순간','INJ1 ECU126/127; #2 174/150; #3 175/151; #4 125/103','구동 자체가 없으면 연료기계보다 ECU/동기/전기 먼저','OEM_EXACT',.84,.55),
  pt('CS8','Injector return 비교','인젝터 리턴','동일시간/동일조건 4개 비교','크랭킹 또는 안정된 시험조건','','특정 실린더만 과다하게 차이나면 해당 인젝터 leak 가능성 상승','FIELD_ISOLATION',.72,.74,'OEM 확인 없는 cc/min 임계값 생성 금지'),
 ],
 ['ECU 무통신이면 연료계통 진단 중단.','RPM/sync가 사라지면 CRK/CAM부터 해결한다.','RPS 회로가 검증되기 전 rail actual만 보고 펌프/인젝터를 판정하지 않는다.','저압공급·IMV·리턴을 모두 분리한 뒤에 고압펌프를 판단한다.'],
 ['CRK','CAM','RPS','IMV','INJ1','INJ2','INJ3','INJ4','WTS'],['D24 §9 fuel, §12 electrical'],['크랭킹 최소 rail pressure, injector return cc/min은 현재 OEM 확인값이 없어 숫자 기준을 만들지 않음.'],tools=['진단기 record/live data','DMM/백프로브','오실로스코프/전류클램프','연료 공기혼입 확인도구'])

# Rail circuit focused
g['ENG_FUEL_RAIL']=grp(
 'D24 Rail 압력 · RPS/저압공급/IMV/리턴','RPS가 믿을 수 있는지 먼저 확인하고, 실제 rail 형성불량이면 저압공급→IMV→고압펌프→인젝터리턴 순으로 좁힌다.',
 [
  pt('FR1','RPS 5V','RPS pin3 / ECU138','백프로브','KEY ON','5V','없으면 센서교환보다 VREF/하네스','OEM_EXACT',.20,.28),
  pt('FR2','RPS GND','RPS pin2 / ECU119','센서 GND↔ECU/배터리 기준 비교','KEY ON/크랭킹','GND function','GND가 흔들리면 signal 판정 중지','OEM_EXACT',.20,.55),
  pt('FR3','RPS signal / actual','RPS pin1 / ECU135 + 진단기 actual','백프로브와 live data 동시비교','크랭킹/부하','pressure signal function','전기 signal과 live data 일치 후에만 실제압 추세로 사용','OEM_EXACT',.42,.40),
  pt('FR4','저압연료/공기','필터 출구→HP pump inlet','필터/호스/프라이밍/기포 확인','크랭킹 전·중','','저압 공급문제가 있으면 IMV/HP pump 판정 보류','FIELD_METHOD',.50,.70),
  pt('FR5','IMV command','고압펌프 IMV / ECU177','PWM command/파형 확인','크랭킹/부하','ECU177 PWM control','명령은 있는데 rail이 못 오르면 펌프/고압/return 쪽','OEM_EXACT',.65,.30),
  pt('FR6','Rail actual vs commanded','진단기','actual/command 추세 동시기록','크랭킹/부하','','차이가 언제/어떤 부하에서 생기는지로 공급/제어를 분리','FIELD_METHOD',.70,.52),
  pt('FR7','인젝터 리턴 비교','4개 인젝터 리턴','동일시간·동일조건 비교','크랭킹/아이들','','특정 인젝터 과다 리턴이면 rail 형성불량 원인 후보','FIELD_ISOLATION',.84,.70),
 ],
 ['RPS 전원/GND/signal이 불신뢰면 rail live data로 펌프를 판정하지 않는다.','저압공급과 공기혼입을 먼저 배제한다.','OEM 없는 최소 rail MPa와 리턴량 숫자는 사용하지 않는다.'],
 ['RPS','IMV','INJ1','INJ2','INJ3','INJ4'],['D24 §9 fuel; §12 RPS/IMV'])

# Sync
g['ENG_SYNC']=grp(
 'D24 CRK/CAM 동기 · 센서쪽 vs ECU쪽 파형','진단 RPM/sync가 끊기는지 먼저 확인하고 센서 커넥터와 ECU측 파형을 비교해 센서/배선/기계타이밍을 분리한다.',
 [
  pt('SY1','CRK 회로','크랭크/타이밍기어 측 하부 CRK','ECU136 CRS NEG / ECU160 CRS POS / ECU187 shield','크랭킹/간헐 재현','CRK signal pair/shield OEM pin','센서쪽 정상+ECU쪽 이상이면 하네스; 양쪽 이상이면 센서/트리거','OEM_EXACT',.25,.55),
  pt('SY2','CAM 회로','실린더헤드/타이밍 상부 CAM','sensor pin2→ECU159 signal, pin3→ECU147 GND; supply 12V','크랭킹/간헐 재현','12V supply / signal / GND function','connector face 방향을 임의로 그리지 않고 번호/ECU 기능만 사용','OEM_EXACT',.25,.30,'CAM connector-face orientation 재확인 전 그래픽 cavity 번호 배치 금지'),
  pt('SY3','CRK/CAM 파형 동시','CRK와 CAM 신호선','2ch oscilloscope','크랭킹/증상 순간','','둘 중 어느 신호가 먼저 깨지는지/사라지는지 기록','FIELD_METHOD',.52,.42),
  pt('SY4','ECU RPM / sync','진단기','RPM/sync record','크랭킹/스톨 순간','','파형 정상인데 ECU sync만 실패하면 ECU 입력/기계 위상 검토','FIELD_METHOD',.72,.30),
  pt('SY5','기계 타이밍','타이밍기어/트리거 관계','OEM 타이밍 마크/기계점검','전기회로 정상 후','','CRK/CAM 파형 자체는 살아 있으나 위상/동기 불일치가 지속되면 기계타이밍 확인','FIELD_ISOLATION',.78,.65),
 ],
 ['간헐은 시동이 다시 걸린 뒤 정적 저항만 재지 말고 증상 순간 파형을 기록한다.','센서측과 ECU측을 비교해 하네스를 분리한다.','전기파형이 모두 정상인 경우에만 기계 타이밍으로 들어간다.'],
 ['CRK','CAM'],['D24 §12-3 callout 2/3; §12-14'])

# Injectors
g['ENG_INJECTOR']=grp(
 'D24 인젝터/실린더 분리 · 전기구동→리턴→압축','특정 실린더 이상을 인젝터로 바로 확정하지 않는다. 구동파형, 리턴비교, 실린더 기계압축을 분리한다.',
 [
  pt('IJ1','Injector #1 drive','실린더헤드 #1 인젝터/ECU','ECU126 low / ECU127 high; 전류클램프/스코프','크랭킹/아이들','OEM ECU pair','구동 비정상이면 전기/ECU/하네스; 정상인데 기여도 낮으면 리턴/압축','OEM_EXACT',.20,.25),
  pt('IJ2','Injector #2 drive','실린더헤드 #2','ECU174 low / ECU150 high','크랭킹/아이들','OEM ECU pair','','OEM_EXACT',.38,.25),
  pt('IJ3','Injector #3 drive','실린더헤드 #3','ECU175 low / ECU151 high','크랭킹/아이들','OEM ECU pair','','OEM_EXACT',.56,.25),
  pt('IJ4','Injector #4 drive','실린더헤드 #4','ECU125 low / ECU103 high','크랭킹/아이들','OEM ECU pair','','OEM_EXACT',.74,.25),
  pt('IJ5','4기통 전류파형 비교','#1~4 인젝터 하네스','전류클램프/오실로스코프','같은 회전수/온도','','한 채널만 형상이 다르면 해당 실린더 전기부하/인젝터 의심','FIELD_ISOLATION',.34,.55),
  pt('IJ6','리턴량 상대비교','4개 인젝터 return','동일시간 동일조건 수집','동일 rpm/온도','','특정 실린더만 뚜렷하게 과다하면 내부 leak 후보','FIELD_ISOLATION',.58,.55,'OEM 확인 없는 절대 cc/min 기준 금지'),
  pt('IJ7','압축/실린더 기계','문제 실린더','압축/상대압축 또는 승인된 기계시험','전기/리턴 비교 후','','인젝터 전기/리턴이 정상인데 기여도 문제가 남으면 압축/밸브/기계로','FIELD_METHOD',.76,.65),
 ],
 ['시험등을 인젝터 구동선에 직접 물리지 않는다.','전기구동 이상과 내부 leak을 하나로 묶지 않는다.','인젝터 증상이 남아도 압축이 나쁘면 인젝터 교환만으로 결론내리지 않는다.'],
 ['INJ1','INJ2','INJ3','INJ4','RPS'],['D24 §9 injector; §12-13'],tools=['진단기 cylinder/cut-out 기능(지원 시)','전류클램프+오실로스코프','리턴 비교 도구','압축/상대압축 도구'])

# Air/boost
g['ENG_AIR_BOOST']=grp(
 'D24 흡기/부스트 · MAF/BPS/차지누설/EGR','저부스트나 검은연기는 터보부터 바꾸지 않는다. MAF/BPS 회로가 믿을 수 있는지 확인한 뒤 차지호스 누설, EGR, 터보/배기제한으로 이동한다.',
 [
  pt('AB1','MAF 12V','에어클리너 이후 MAF pin4 / ECU137','백프로브','KEY ON/엔진 RUN','12V supply function','공급없음이면 MAF 교환 금지','OEM_EXACT',.18,.25),
  pt('AB2','MAF GND','MAF pin3 / ECU120','GND 기준 비교','RUN/부하','GND function','','OEM_EXACT',.18,.50),
  pt('AB3','MAF flow/temp','MAF pin1→ECU228 flow / pin2→ECU235 temp','진단 live + 필요 시 신호측정','RUN/부하','OEM pin functions','값이 실제 부하/흡기상태와 연속적으로 변하는지 비교','OEM_EXACT',.32,.38),
  pt('AB4','BPS 5V/GND/signal','흡기매니폴드 BPS','pin1 ECU161 5V / pin2 ECU167 GND / pin3 ECU112 pressure','KEY ON/RUN','5V + OEM pin functions','회로검증 전 boost live data로 터보 판정 금지','OEM_EXACT',.50,.30),
  pt('AB5','차지호스 누설/붕괴','터보→인터쿨러/흡기매니폴드','육안/압력누설 또는 부하 시 호스거동','실제 부하','','누설/호스붕괴가 있으면 터보 자체 판정 전에 수리','FIELD_METHOD',.62,.62),
  pt('AB6','EGR command/position','EGR 밸브 어셈블리','진단 command/actual + VREF/position 확인','RUN/부하','','EGR가 과개방/고착되면 MAF/BPS/연기/출력에 영향','OEM_PLUS_FIELD',.76,.35),
  pt('AB7','터보/배기 제한','터보축/액추에이터/배기누설·막힘','기계점검/부하 trend','센서/호스/EGR 정상 후','','여기까지 배제된 뒤 터보/배기계통으로','FIELD_ISOLATION',.82,.68),
 ],
 ['MAF/BPS 회로가 불신뢰면 진단값만으로 터보를 판정하지 않는다.','실제 부하에서 차지호스 누설/붕괴를 먼저 찾는다.','EGR command/actual을 확인한 뒤 터보 자체로 간다.'],
 ['MAF','BPS','EGR'],['D24 §10 intake/exhaust; §12-11'])

# Cooling
g['ENG_COOLING']=grp(
 'D24 과열/수온 · WTS vs 실제온도→순환→서모스탯','계기/진단값만 보고 과열을 확정하지 않는다. WTS와 실제 접촉온도를 교차하고 냉각수/라디에이터/펌프/서모스탯 순서로 간다.',
 [
  pt('CL1','WTS signal/GND','냉각수 통로/서모스탯 계통 WTS','pin1→ECU145 GND / pin2→ECU109 temp','냉간→워밍업','OEM pin functions','진단값이 실제온도와 어긋나면 냉각기계보다 센서/배선 먼저','OEM_EXACT',.22,.32),
  pt('CL2','WTS 저항 기준','WTS 분리 측정','센서 저항/온도 비교','센서 온도 안정','20°C ≈2.5 kΩ / 110°C ≈0.148 kΩ','스펙과 크게 어긋나면 WTS 자체 후보','OEM_EXACT',.22,.58),
  pt('CL3','실제 금속/냉각수 온도','서모스탯 하우징/라디에이터 입출구','접촉식 온도계 또는 승인된 방법','워밍업/과열 재현','','WTS live와 실제를 교차하여 “센서만 높은 것”과 실제 과열 분리','FIELD_METHOD',.46,.35),
  pt('CL4','냉각수 레벨/캡/외부누설','리저버/라디에이터/호스','냉간 레벨·압력누설 흔적','냉간 안전상태','','부족/누설/캡 문제 교정 후 재현','FIELD_METHOD',.46,.65),
  pt('CL5','라디에이터 입출구 패턴','라디에이터 상/하 호스','입출구 온도 trend 비교','워밍업','','순환/열교환 패턴이 비정상이면 막힘/서모스탯/펌프 분기','FIELD_METHOD',.68,.30),
  pt('CL6','서모스탯/워터펌프','서모스탯 하우징/펌프 구동','온도상승 패턴·벨트/임펠러/유량 정황','센서 신뢰성 확인 후','','순환이 안 되면 thermostat/pump 계통으로','FIELD_ISOLATION',.78,.55),
  pt('CL7','내부가스/헤드계통','냉각계','연소가스/지속기포/압력상승 및 오일·냉각수 교차오염 확인','외부/순환계 정상 후','','내부누설 정황이 일치할 때 헤드/가스켓/크랙 분해검사 허용','FIELD_METHOD',.84,.73),
 ],
 ['WTS live와 실제온도가 안 맞으면 센서회로부터 해결한다.','실제 과열이면 레벨/외부누설→열교환→순환 순으로 간다.','내부 엔진 분해는 외부 냉각/순환원인을 배제한 뒤 허용한다.'],
 ['WTS'],['D24 §7 cooling; §12-12 WTS'])

# Lubrication
g['ENG_LUBE']=grp(
 'D24 저오일압 · OPTS vs 기계게이지','OPTS 경고만으로 베어링/펌프를 분해하지 않는다. 센서회로와 기계 실압을 분리한 뒤 오일/필터→펌프/릴리프→내부누설로 간다.',
 [
  pt('OL1','OPTS 5V','엔진 블록 오일갤러리 OPTS pin3 / ECU165','백프로브','KEY ON','5V','없으면 sensor보다 VREF/배선','OEM_EXACT',.20,.28),
  pt('OL2','OPTS GND','OPTS pin1 / ECU148','GND 비교','KEY ON/RUN','GND function','','OEM_EXACT',.20,.50),
  pt('OL3','OPTS pressure/temp signal','pin4→ECU111 pressure / pin2→ECU104 temp','live data + 신호 trend','RUN/온도변화','OEM pin functions','센서회로가 불신뢰면 경고값만으로 기계분해 금지','OEM_EXACT',.38,.38),
  pt('OL4','기계 오일압 게이지','D24 OEM 승인 압력포트','기계식 압력게이지','냉/열간 및 rpm 기록','','전자센서와 실제압을 분리','OEM_VERIFY',.58,.30,'현재 확보 DB에서 정확 포트 나사규격/압력 판정표는 미확정. 임의 규격/수치 금지'),
  pt('OL5','오일 레벨/점도/필터','오일팬/딥스틱/필터','레벨·오염·연료희석·필터 상태','냉간/정지','','기본 공급문제가 있으면 펌프/베어링 판정 보류','FIELD_METHOD',.58,.62),
  pt('OL6','펌프/릴리프/내부누설','윤활펌프/릴리프/터보오일/갤러리','기계압력 패턴과 누유/소음 비교','센서 정상화·오일기본 확인 후','','실압이 실제로 낮을 때만 펌프/릴리프/clearance 분해진단','FIELD_ISOLATION',.80,.48),
 ],
 ['센서회로와 기계실압을 반드시 분리한다.','기계압력 포트/규격이 확정되지 않은 상태에서 임의 어댑터를 사용하지 않는다.','실압이 정상이라면 엔진 내부를 열지 않고 OPTS/배선/표시계통으로 돌아간다.'],
 ['OPTS'],['D24 §8 lubrication; §12 OPTS'])

# Preheat
g['ENG_PREHEAT']=grp(
 'D24 예열/에어히터 · 요구→릴레이→실부하','표시등이 들어온다고 히터가 실제로 가열된다고 보지 않는다. WTS/흡기조건→ECU 요구→릴레이 코일→접점 출력→히터 전류/GND를 본다.',
 [
  pt('PH1','WTS/흡기 온도 입력','WTS/MAF intake temp','진단값을 실제 온도와 비교','냉간','WTS/MAF OEM input functions','온도 입력이 거짓이면 예열제어 판단 전에 센서회로 해결','OEM_PLUS_FIELD',.18,.35),
  pt('PH2','ECU preheat request','진단기/ECU command','request/indicator 상태 기록','냉간 KEY ON','','요구 자체가 없으면 입력/ECU logic; 요구 있으면 relay로','FIELD_METHOD',.35,.30),
  pt('PH3','Air heater relay coil','에어히터 릴레이 코일회로','코일명령 부하상태 측정','preheat request ON','','코일명령 정상인데 접점출력 없음이면 relay/socket','OEM_FUNCTION_PIN_VERIFY',.52,.30),
  pt('PH4','Relay input/output loaded','에어히터 릴레이 접점 IN/OUT','동시 전압측정','preheat ON','','입력 유지+출력 붕괴면 접점/소켓 고저항','FIELD_METHOD',.65,.48),
  pt('PH5','Heater actual current','에어히터 주전원선','DC clamp current','preheat ON','','명령/전압은 있는데 전류가 없으면 히터 open/연결불량','FIELD_METHOD',.78,.32),
  pt('PH6','Heater GND','히터/엔진 접지','부하중 GND drop','preheat ON','','GND가 뜨면 히터 자체교환 전 접지수리','FIELD_METHOD',.78,.62),
 ],
 ['예열 표시등 대신 실부하 전류를 확인한다.','릴레이 정확 cavity/퓨즈 위치가 미확정이면 임의 번호를 만들지 않는다.','온도입력→명령→코일→접점→부하 순서로 잘라간다.'],
 ['WTS','MAF'],['D24 §12-8 Air Heater'],['차량 사양별 heater fuse/relay cavity는 차량회로 매칭 전 OEM VERIFY.'])

# Combustion / low power / smoke / rough idle
g['ENG_COMBUSTION']=grp(
 'D24 출력저하/부조/연기 · 공기→rail→실린더 기여→기계','연기색만으로 인젝터/터보를 찍지 않는다. 실제 부하에서 공기량/부스트, rail 추세, 실린더 기여/리턴, 압축을 같은 조건으로 비교한다.',
 [
  pt('CB1','재현조건 로그','진단기 + 육안','냉/열간, rpm, 부하, 연기색/지속, 오일·냉각수소모 기록','증상 재현','','조건이 달라지면 비교값 해석도 분리','FIELD_METHOD',.12,.30),
  pt('CB2','MAF/BPS 신뢰성','MAF/BPS','MAF 12V/GND/flow-temp + BPS 5V/GND/signal','실제 부하','OEM pin functions','센서회로가 틀리면 “공기부족/부스트부족” 진단값을 믿지 않음','OEM_PLUS_FIELD',.30,.28),
  pt('CB3','차지/EGR/배기','차지호스/EGR/배기계통','누설·붕괴·EGR command/actual·배기제한 확인','실제 부하','','공기계통 원인이 있으면 연료부품 판정 보류','FIELD_METHOD',.46,.50),
  pt('CB4','Rail actual/command','진단기','rail 추세 동시기록','증상 부하','','압력추세가 무너지면 ENG_FUEL_RAIL로 이동','FIELD_METHOD',.60,.28),
  pt('CB5','실린더 기여/cut-out','진단기 지원 기능','#1~4 상대기여 비교','동일 rpm/온도','','특정 실린더만 문제면 인젝터/압축으로 좁힘','FIELD_ISOLATION',.70,.48),
  pt('CB6','Injector return/current','#1~4 인젝터','리턴상대비교 + 전류파형','동일조건','','전기/내부 leak을 분리','FIELD_ISOLATION',.80,.32),
  pt('CB7','압축/기계','문제 실린더/엔진','압축/상대압축/밸브기계 확인','공기/rail/injector 분리 후','','연료/전기 정상인데 기여도 문제면 기계원인으로','FIELD_METHOD',.82,.65),
 ],
 ['검은연기=인젝터, 흰연기=압축 같은 단순 색상확정 금지.','실제 부하에서 MAF/BPS/rail을 같은 시간축으로 본다.','특정실린더는 전기구동→리턴→압축 순서로 분리한다.'],
 ['MAF','BPS','EGR','RPS','INJ1','INJ2','INJ3','INJ4','WTS'],['D24 §9 fuel; §10 intake/exhaust; §11 mechanical; §12 sensors'])

# Add graph mapping for all 21 engine graphs.
engine_map={
 'E_D24_CRANK_NO_START':'ENG_CRANK_START',
 'E_D24_ECU_NO_COMM':'ENG_ECU_HEALTH',
 'E_D24_5V_REF':'ENG_VREF',
 'E_D24_RAIL_PRESSURE':'ENG_FUEL_RAIL',
 'E_D24_BOOST_PRESSURE':'ENG_AIR_BOOST',
 'E_D24_WATER_TEMP':'ENG_COOLING',
 'E_D24_MAF':'ENG_AIR_BOOST',
 'EN_HARD_START':'ENG_CRANK_START',
 'EN_STALL':'ENG_CRANK_START',
 'EN_LOW_POWER':'ENG_COMBUSTION',
 'EN_ROUGH_IDLE':'ENG_COMBUSTION',
 'EN_BLACK_SMOKE':'ENG_COMBUSTION',
 'EN_WHITE_SMOKE':'ENG_COMBUSTION',
 'EN_BLUE_SMOKE':'ENG_COMBUSTION',
 'EN_OVERHEAT':'ENG_COOLING',
 'EN_LOW_OIL_PRESS':'ENG_LUBE',
 'EN_LOW_BOOST':'ENG_AIR_BOOST',
 'EN_PREHEAT':'ENG_PREHEAT',
 'EN_FUEL_PRESSURE':'ENG_FUEL_RAIL',
 'EN_CRK_CAM_SYNC':'ENG_SYNC',
 'EN_INJECTOR_SEPARATE':'ENG_INJECTOR'
}
d.setdefault('graph_map',{}).update(engine_map)
d['engine_graph_map']=engine_map
d['version']='1.1-v8.5-engine-testpoint'
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('engine groups added:',len([k for k,v in g.items() if v.get('system')=='엔진']))
print('engine graph map:',len(engine_map))
