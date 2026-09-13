#!/usr/bin/env python3
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
tp=json.loads((A/'test_point_locator_v1.json').read_text(encoding='utf-8'))
el=json.loads((A/'electrical_diag_v1.json').read_text(encoding='utf-8'))
loc=json.loads((A/'field_location_map_v1.json').read_text(encoding='utf-8'))

def P(i,label,where,connect,condition,source='FIELD_METHOD',expected='',decision='',note='',x=.5,y=.5):
    d={'id':i,'label':label,'where':where,'connect':connect,'condition':condition,'source_class':source,'x':x,'y':y}
    if expected:d['expected']=expected
    if decision:d['decision']=decision
    if note:d['note']=note
    return d

def G(title,system,summary,points,focus,*,tools=None,conditions=None,rules=None,limitations=None,refs=None,imgs=None,note=None):
    return {
      'title':title,'system':system,'summary':summary,
      'tools':tools or ['DMM MIN/MAX','백프로브','퓨즈된 점퍼선(격리시험이 안전한 경우만)'],
      'conditions':conditions or ['증상이 실제 재현되는 상태에서 측정','커넥터 연결 상태의 부하시험을 우선','미확정 숫자 cavity는 기능선으로 추적하고 임의 지정 금지'],
      'points':points,
      'decision_rules':rules or [],
      'oem_images':imgs or [],
      'diagram_note':note or '원본 전체 배선도가 아니라 이 고장을 가르는 전원→제어→부하→접지와 프로브 지점만 재작성.',
      'source_refs':refs or ['600123-00120 electrical schematic','SM1018-01 service manual'],
      'limitations':limitations or [],
      'focus_ids':focus,
    }

# OEM-exact component/test facts surfaced ahead of raw pages.
specs={
 'STOP_LAMP':[
   {'label':'보호/전원','value':'ACC 15A · turn signal / STOP-strobe / light-switch feed','source':'D20/25/30/33S-7 D24NAP O&M fuse table'},
   {'label':'정지/미등 전구','value':'12 V 27/8 W','source':'SM1018-01 점검·교환 주기'},
 ],
 'HEAD_LAMP':[
   {'label':'보호/릴레이','value':'BAT2 20A → LAMP relay #4; ACC 15A light-switch feed','source':'D20/25/30/33S-7 D24NAP O&M fuse/relay table'},
   {'label':'할로겐 전조등','value':'12 V 55 W','source':'SM1018-01 점검·교환 주기'},
 ],
 'TURN_HAZARD':[
   {'label':'보호','value':'ACC 15A','source':'D20/25/30/33S-7 D24NAP O&M fuse table'},
   {'label':'방향지시 전구','value':'12 V 27 W','source':'SM1018-01 점검·교환 주기'},
 ],
 'HORN':[
   {'label':'현행 명명 fuse-block','value':'BAT3 15A · horn','source':'D20/25/30/33S-7 D24NAP O&M fuse table'},
   {'label':'서비스매뉴얼 일반 점검표','value':'Horn 10A 표기도 존재 · 실제 차량 fuse-label/생산사양 우선','source':'SM1018-01 점검·교환 주기'},
 ],
 'BACKUP':[
   {'label':'관련 주행제어 보호','value':'IGN3 15A · direction switch / reverse relay; REV relay #5','source':'D20/25/30/33S-7 D24NAP O&M fuse/relay table'},
   {'label':'백업등 전구','value':'12 V 10 W','source':'SM1018-01 점검·교환 주기'},
 ],
 'LIFT_LOCK':[
   {'label':'보호','value':'IGN1 15A · lift/unload solenoid','source':'D20/25/30/33S-7 D24NAP O&M fuse table'},
 ],
 'CLUSTER_POWER':[
   {'label':'현행 명명 fuse-block','value':'IGN2 20A · ECU/instrument display power','source':'D20/25/30/33S-7 D24NAP O&M fuse table'},
   {'label':'서비스매뉴얼 일반 점검표','value':'instrument 15A 표기도 존재 · actual fuse-block label/생산사양 우선','source':'SM1018-01 점검·교환 주기'},
 ],
 'AC_POWER':[
   {'label':'블로워 모터','value':'12 V / 10 A / 3단','source':'SM1018-01 §8-5-1'},
   {'label':'블로워 직접시험','value':'3단(Stage 3) 직접 연결 조건','source':'SM1018-01 §8-5-1'},
   {'label':'블로워 전원 커넥터','value':'4-pin, 1.5SQ','source':'SM1018-01 §8-5-1'},
   {'label':'서모스탯','value':'2-pin, 1SQ','source':'SM1018-01 §8-5-1'},
 ],
 'AC_COND_FAN':[
   {'label':'콘덴서 팬 어셈블리','value':'air flow 1,200 m³/h','source':'SM1018-01 §8-5-1'},
   {'label':'주의','value':'air-flow 사양은 전기 합격 전류 기준이 아님','source':'diagnostic interpretation'},
 ],
 'FR_CONTROL':[
   {'label':'F/R 스위치 공통','value':'pin 4↔7 continuity','source':'SM1018-01 §2-4-2'},
   {'label':'전진 접점','value':'F에서 pin 1↔2 continuity; N에서 open','source':'SM1018-01 §2-4-2'},
   {'label':'후진 접점','value':'R에서 pin 1↔3 continuity; N에서 open','source':'SM1018-01 §2-4-2'},
   {'label':'솔레노이드','value':'10±0.3 Ω @25°C; plunger 약 3.18 mm','source':'SM1018-01 transmission spec/procedure'},
 ],
}
for cid,arr in specs.items():
    if cid in el['circuits']: el['circuits'][cid]['verified_test_specs']=arr

# New dedicated electrical probe groups.
groups={}
groups['EL_STOP_LAMP']=G('브레이크등 · 스위치/좌우분기/접지','전장','좌우 동시불량인지 한쪽 불량인지 먼저 가르고, STOP 스위치 양단을 기능 기준으로 찾아 후방 분기와 접지까지 한 번에 비교한다',[
 P('SL1','ACC 15A 양단','시트/후드 아래 fuse block · ACC 15A','퓨즈 입력↔BAT-와 출력↔BAT-를 같은 브레이크 작동 상태에서 비교','KEY ON / 브레이크 페달 작동','OEM_EXACT','ACC 15A가 STOP/strobe/light-switch feed','입력 정상/출력 없음→퓨즈/소켓; 양단 정상→STOP SW로',x=.15,y=.30),
 P('SL2','STOP LAMP SW 상류 기능단','페달부 STOP LAMP SW 2-pin 커넥터','두 단자 중 페달 상태와 무관하게 공급이 유지되는 쪽을 기능상 상류로 식별','KEY ON / 커넥터 연결 백프로브','OEM_FUNCTION_PIN_VERIFY','','숫자 1/2를 공급단으로 미리 단정하지 말고 실제 기능으로 식별',x=.34,y=.30),
 P('SL3','STOP LAMP SW 출력 기능단','같은 2-pin STOP SW 반대 기능단','페달 해제/작동에 따라 출력이 전환되는지 MIN/MAX/백프로브','KEY ON / 페달 해제↔작동','OEM_FUNCTION_PIN_VERIFY','','상류 유지+출력 미전환→스위치/조정; 출력 정상→후방으로',x=.48,y=.50),
 P('SL4','RH COMB STOP 기능단','우측 후미 combination lamp의 STOP terminal','STOP 기능단↔램프 GND 부하전압','브레이크 페달 작동','OEM_FUNCTION_PIN_VERIFY','STOP/TAIL bulb 12V 27/8W','LH 정상/RH 없음→우측 분기/커넥터',x=.70,y=.32),
 P('SL5','LH COMB STOP 기능단','좌측 후미 combination lamp의 STOP terminal','STOP 기능단↔램프 GND 부하전압','브레이크 페달 작동','OEM_FUNCTION_PIN_VERIFY','STOP/TAIL bulb 12V 27/8W','RH 정상/LH 없음→좌측 분기/커넥터',x=.70,y=.62),
 P('SL6','후미 GND 전압강하','각 combination lamp GND↔battery -POST','부하를 켠 채 전압강하','브레이크 페달 작동','FIELD_METHOD','','B+ 도달+GND 쪽만 떠오르면 후미 접지/단자',x=.88,y=.50),
],loc['graph_focus']['E_STOP_NO'],rules=['양쪽 동시불량이면 ACC15/STOP SW/공통 후방분기부터, 한쪽만이면 해당 분기·램프·GND부터.','브레이크등 계속 켜짐은 STOP SW 커넥터 분리로 스위치쪽 고착/조정과 후단 전원단락을 먼저 가른다.','숫자 pin 1/2의 공급/출력 역할은 고해상도 선추적 전 임의 확정 금지.'],limitations=['STOP SW 1/2 공급/출력 역할과 combination lamp numeric cavity는 미확정. 기능단으로 측정.'],refs=['600123-00120 sheet 4/4 F6→I7/I8','SM1018-01 bulb table','D24NAP O&M ACC 15A fuse table'],imgs=['oem_pages/p370.jpg'])

groups['EL_HEAD_LAMP']=G('헤드램프 · relay/스위치/좌우램프','전장','LAMP relay 전원과 light-switch 지령을 먼저 확인하고, 좌우 램프 B+/GND로 공통부와 한쪽 고장을 분리한다',[
 P('HL1','BAT2 20A 양단','fuse block BAT2 20A','퓨즈 입력/출력 부하전압','LIGHT ON','OEM_EXACT','BAT2 20A supplies LAMP relay','입력 정상/출력 없음→퓨즈/소켓',x=.12,y=.32),
 P('HL2','LAMP relay #4 입력/출력','relay box · LAMP relay #4','접점 입력과 출력 동시 백프로브','LIGHT ON','OEM_ID_PLUS_FIELD','','입력 유지+출력 없음/drop→relay/socket',x=.30,y=.32),
 P('HL3','LIGHT SW ACC 입력/출력','운전석 LIGHT SW','ACC 15A feed와 스위치 출력 비교','LIGHT ON','OEM_FUNCTION_PIN_VERIFY','','입력 정상+출력 없음→switch/connector',x=.48,y=.32),
 P('HL4','RH headlamp B+','우측 전방 headlamp connector','B+↔local GND 부하전압','LIGHT ON','OEM_PLUS_FIELD','halogen 12V 55W','LH 정상/RH 없음→우측 하네스/커넥터',x=.70,y=.25),
 P('HL5','LH headlamp B+','좌측 전방 headlamp connector','B+↔local GND 부하전압','LIGHT ON','OEM_PLUS_FIELD','halogen 12V 55W','RH 정상/LH 없음→좌측 하네스/커넥터',x=.70,y=.55),
 P('HL6','헤드램프 GND drop','각 램프 GND↔battery -POST','램프 ON 상태 전압강하','LIGHT ON','FIELD_METHOD','','B+ 정상+GND drop 이상→접지',x=.88,y=.42),
],loc['graph_focus']['E_HEAD_NO'],rules=['양쪽 불량이면 BAT2/relay#4/LIGHT SW 공통부 우선.','한쪽만 불량이면 스위치 교환 전에 해당 램프 B+/GND를 먼저 측정.'],limitations=['lamp/switch numeric cavity는 원본에서 확정된 경우만 사용.'],refs=['600123-00120 sheet 1/4,3/4','SM1018-01 12V55W','D24NAP O&M BAT2 20A / LAMP relay #4 / ACC15'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_TURN_HAZARD']=G('방향지시/비상등 · flasher/스위치/좌우분기','전장','TURN과 HAZARD를 비교해 공통 flasher 전원과 각 스위치/좌우 출력 경로를 분리한다',[
 P('TH1','ACC 15A 양단','fuse block ACC 15A','퓨즈 양단 부하전압','TURN 또는 HAZARD ON','OEM_EXACT','ACC 15A','양단 공급부터 확인',x=.12,y=.35),
 P('TH2','flasher/HAZARD relay 입력','HAZARD relay / flasher unit','입력 공급↔GND','TURN/HAZARD ON','OEM_FUNCTION_PIN_VERIFY','','입력 없음→상류; 입력 있음→출력 확인',x=.30,y=.35),
 P('TH3','flasher 출력','flasher output 기능선','입력과 출력의 pulse/전압을 비교','TURN/HAZARD ON','FIELD_METHOD','','입력 유지+출력 없음→flasher/relay',x=.47,y=.35),
 P('TH4','TURN/HAZARD SW L/R 출력','운전석 turn/hazard switch output','좌/우 지령별 출력 변화','좌/우 각각','OEM_FUNCTION_PIN_VERIFY','','한 방향만 없음→switch/branch',x=.62,y=.52),
 P('TH5','좌/우 turn lamp B+','전/후 turn lamp 기능단','작동측 pulse/부하전압','TURN ON','OEM_PLUS_FIELD','turn bulb 12V 27W','스위치 출력 정상+램프측 없음→하네스',x=.78,y=.30),
 P('TH6','turn lamp GND drop','해당 lamp GND↔battery -POST','부하 중 전압강하','TURN ON','FIELD_METHOD','','B+ 정상+점멸불량/약함→GND/전구',x=.90,y=.55),
],loc['graph_focus']['E_TURN_NO'],rules=['TURN과 HAZARD 둘 다 죽으면 ACC15/flasher 공통부 우선.','HAZARD는 되고 특정 TURN만 안 되면 방향스위치/해당 좌우 분기 우선.'],limitations=['numeric switch/flasher pins/cavity는 OEM 원본 추가확인 전 기능선으로 측정.'],refs=['600123-00120','SM1018-01 12V27W','D24NAP O&M ACC15'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_HORN']=G('경적 · fuse/switch/load/GND','전장','퓨즈 표기 세대차를 고려하되 실제 차량 fuse label을 먼저 보고, 경적 커넥터 부하전압과 GND로 스위치/부하를 분리한다',[
 P('HN1','Horn 보호회로 양단','실차 fuse block의 HORN 표기 fuse','실차 label 확인 후 fuse 양단 전압','KEY ON / HORN 명령','OEM_PLUS_FIELD','D24 O&M named BAT3 15A; SM1018 general table Horn 10A','실차 fuse label/생산사양 우선',x=.16,y=.32),
 P('HN2','HORN SW 기능선','운전석 horn switch','switch 입력/출력 또는 GND-switch 상태전환','HORN 눌림/해제','OEM_FUNCTION_PIN_VERIFY','','switch에서 상태가 안 바뀌면 switch/clock/connector',x=.38,y=.32),
 P('HN3','Horn B+','horn connector','B+↔local GND 부하전압','HORN 눌림','FIELD_METHOD','','공급 정상인데 무음이면 GND/혼 자체',x=.64,y=.32),
 P('HN4','Horn GND drop','horn GND↔battery -POST','명령 중 전압강하','HORN 눌림','FIELD_METHOD','','GND 정상+B+정상→horn load 자체',x=.82,y=.55),
],loc['graph_focus']['E_HORN_NO'],rules=['퓨즈 정격의 문서 세대차를 하나의 절대값으로 섞지 않는다. 실제 fuse block 라벨과 적용 생산사양을 우선한다.'],limitations=['switch numeric pin/cavity는 기능 기준으로 추적.'],refs=['600123-00120 sheet 1/4','SM1018-01 maintenance fuse table','D24NAP O&M named fuse layout'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_BACKUP']=G('후진등/백업부저 · switch/branch/load','전장','후진 선택 자체와 BACK-UP switch 출력, 부저와 좌우 후진등 공통/개별 분기를 비교한다',[
 P('BU1','BACK-UP SW 입력','transmission/reverse switch area','switch input 기능선 전압/상태','KEY ON / R 선택','OEM_FUNCTION_PIN_VERIFY','','입력 없음→상류 REV/direction control',x=.18,y=.32),
 P('BU2','BACK-UP SW 출력','같은 switch output 기능선','N↔R 상태전환 측정','N과 R 비교','OEM_FUNCTION_PIN_VERIFY','','입력 있음+출력 미전환→switch/adjustment',x=.38,y=.32),
 P('BU3','Backup buzzer B+','후방 backup buzzer connector','B+↔GND 부하전압','R 선택','FIELD_METHOD','','등은 정상/부저만 없음→부저 branch/load',x=.62,y=.22),
 P('BU4','RH/LH backup lamp 기능단','rear combination lamp BACK-UP terminal','좌/우 B+ 비교','R 선택','OEM_FUNCTION_PIN_VERIFY','backup bulb 12V 10W','부저 정상/등만 없음→lamp branch',x=.62,y=.52),
 P('BU5','후방 GND drop','buzzer/lamp GND↔battery -POST','부하 중 전압강하','R 선택','FIELD_METHOD','','B+ 정상+GND 이상→rear ground',x=.84,y=.52),
],loc['graph_focus']['E_BACKUP_NO'],rules=['부저와 양쪽 후진등이 모두 죽으면 switch/common branch, 하나만 죽으면 해당 분기/부하를 먼저 본다.','IGN3/REV relay #5는 관련 주행제어 보호정보이며 BACK-UP lamp 전용 fuse라고 과잉표시하지 않는다.'],limitations=['BACK-UP lamp 전용 fuse cavity는 현재 원본에서 미확정.'],refs=['600123-00120 sheet 4/4','SM1018-01 12V10W backup bulb','D24NAP O&M IGN3/REV relay #5 related control'],imgs=['oem_pages/p370.jpg'])

groups['EL_CHARGE']=G('충전 · alternator B+/battery/ground drop','전장','알터네이터 자체 전압 한 점만 보고 정상판정하지 않고 ALT B+→battery+와 case→battery-의 부하 전압강하를 동시에 비교한다',[
 P('CH1','배터리 +POST','battery lead post 자체','DMM 기준전압/충전상태 기록','KEY OFF→idle→전기부하','FIELD_METHOD','','POST 값 자체와 변화를 기록',x=.16,y=.48),
 P('CH2','Alternator B+','alternator B+ stud','ALT B+↔BAT-와 BAT+POST를 동시 비교','engine running / load ON','OEM_PLUS_FIELD','','ALT는 올라가는데 battery가 덜 올라가면 B+ path drop',x=.42,y=.32),
 P('CH3','ALT B+→BAT+ drop','ALT B+ stud↔battery +POST','부하 중 전압강하','engine running / electrical load','FIELD_METHOD','','구간 drop 증가→케이블/terminal/breaker',x=.58,y=.50),
 P('CH4','ALT case→BAT- drop','alternator housing↔battery -POST','부하 중 전압강하','engine running / electrical load','FIELD_METHOD','','case ground drop→engine/body/battery ground',x=.75,y=.62),
 P('CH5','BAT7 20A / alternator S','fuse block BAT7 and alternator sense/control branch','퓨즈 양단과 sense/control supply','KEY ON/running','OEM_EXACT','BAT7 20A includes alternator S','주회로 정상+발전 불량이면 excitation/regulator branch',x=.80,y=.30),
],loc['graph_focus']['E_CHARGE'],rules=['알터네이터에서 14V가 보인다는 사실만으로 배터리까지 충전경로 정상이라고 판정하지 않는다.','OEM exact charging voltage range가 현재 D24 자료에 없으면 임의 13.8~14.5 같은 합격선을 만들지 않는다.'],limitations=['정확 D24 충전전압 pass range는 OEM 확인 전 정상차/부하추세와 경로 drop으로 판정.'],refs=['600123-00120 sheet 2/4','D24NAP O&M BAT7 20A'],imgs=['oem_pages/p368.jpg'])

groups['EL_PARK_INPUT']=G('주차브레이크 입력 · switch→OSS','전장','레버/스위치 실제 상태전환과 OSS가 그 입력을 보는지 분리해 switch 자체와 입력하네스/OSS를 가른다',[
 P('PK1','Parking brake switch 상태','parking brake lever/switch','스위치 양단 continuity/전압 상태전환','레버 해제↔2~3 click 이상','OEM_FUNCTION_EXACT','','상태가 기계작동과 같이 바뀌는지',x=.18,y=.35),
 P('PK2','OSS PARK 입력 기능선','OSS controller connector의 PARK input path','switch측 상태와 OSS측 상태 동시 비교','KEY ON / lever toggle','OEM_FUNCTION_PIN_VERIFY','','switch는 바뀌는데 OSS측 안 바뀌면 harness/terminal',x=.45,y=.35),
 P('PK3','OSS BAT4 20A / IGN3 15A','fuse block→OSS power/signal','퓨즈 양단 부하전압','KEY ON','OEM_EXACT','BAT4 20A OSS power; IGN3 15A OSS signal','공통 OSS 입력 다수 이상이면 supply 우선',x=.65,y=.55),
 P('PK4','OSS GND drop','OSS power ground↔battery -POST','부하 중 전압강하','KEY ON / symptom','FIELD_METHOD','','입력선 정상인데 OSS가 오판정하면 GND/컨트롤러 생존 확인',x=.84,y=.42),
],loc['graph_focus']['E_PARK_INPUT'],rules=['switch가 기계적으로 눌리는 것과 OSS가 논리입력을 실제 읽는 것은 별도 확인한다.'],limitations=['OSS PARK numeric cavity는 미확정.'],refs=['600123-00120','D24NAP O&M BAT4/IGN3'],imgs=['oem_pages/p367.jpg'])

groups['EL_LIFT_LOCK']=G('리프트락/언로드 · OSS output→solenoid','전장','안전조건이 만족되는데 리프트가 잠기면 OSS 출력과 솔레노이드 커넥터 B+/GND를 부하상태에서 비교한다',[
 P('LL1','IGN1 15A 양단','fuse block IGN1 15A','퓨즈 양단 부하전압','KEY ON / lift command','OEM_EXACT','IGN1 15A supplies lift/unload solenoid','입력 정상/출력 없음→fuse/socket',x=.15,y=.30),
 P('LL2','OSS lift-lock output','OSS controller→lift-lock/unload control line','명령상태 출력 변화','착석+안전조건 충족 / lift command','OEM_FUNCTION_PIN_VERIFY','','출력이 안 바뀌면 OSS/input logic; 바뀌면 downstream',x=.38,y=.32),
 P('LL3','Lift-lock solenoid B+','hydraulic control valve lift-lock solenoid connector','커넥터 연결 상태 B+↔local GND','lift enable/disable 비교','FIELD_METHOD','','OSS output 정상+solenoid측 없음→harness',x=.62,y=.30),
 P('LL4','Solenoid GND drop','solenoid GND↔battery -POST','명령 중 전압강하','lift enable','FIELD_METHOD','','B+ 정상+GND 이상→GND/connector',x=.78,y=.55),
 P('LL5','Coil electrical vs hydraulic split','solenoid connector / valve spool','전기명령과 실제 자기/밸브 반응 비교; 저항은 정상차/동일coil 비교','lift enable','FIELD_ISOLATION','','전기 정상인데 hydraulic lock 유지→valve/hydraulic branch',x=.90,y=.35),
],loc['graph_focus']['E_LIFT_LOCK'],rules=['시트/OSS 입력이 정상인지와 OSS output이 정상인지 분리한다.','전기출력이 솔레노이드까지 도달하면 계속 OSS만 의심하지 말고 coil/valve hydraulic로 넘어간다.'],limitations=['OSS output/solenoid numeric cavity는 원본 확정 전 기능선으로 측정.'],refs=['600123-00120 sheet 4/4','D24NAP O&M IGN1 15A'],imgs=['oem_pages/p370.jpg'])

groups['EL_GAUGE_COMMON']=G('계기 공통 · cluster power/GND vs sender','전장','연료/수온/TM온도 여러 계기가 같이 죽는지 한 계기만 틀리는지로 공통 cluster supply와 sender 회로를 먼저 분리한다',[
 P('GC1','IGN2 20A 양단','fuse block IGN2 20A','퓨즈 양단 전압','KEY ON','OEM_EXACT','IGN2 20A ECU/instrument display power','여러 계기 동시불량이면 최우선',x=.14,y=.28),
 P('GC2','Cluster B+/IGN 기능선','instrument cluster connector','B+/IGN↔cluster GND 부하전압','KEY ON','OEM_FUNCTION_PIN_VERIFY','','공급이 흔들리면 sender 교환 금지',x=.34,y=.28),
 P('GC3','Cluster GND drop','cluster GND↔battery -POST','부하 중 전압강하','KEY ON / display active','FIELD_METHOD','','공통 계기오류+GND drop→ground',x=.34,y=.58),
 P('GC4','각 sender signal at sensor','WATER/TM/FUEL sender connector','실제 상태변화에 따라 signal이 연속적으로 변하는지','냉간→열간/연료량 변화/주행후','OEM_FUNCTION_PIN_VERIFY','','sender측 변화가 없으면 sensor/ground branch',x=.64,y=.30),
 P('GC5','같은 signal at cluster','cluster corresponding signal function line','sender측과 cluster측 동시비교','같은 상태','OEM_FUNCTION_PIN_VERIFY','','sensor측 정상+cluster측 불일치→harness/connector',x=.80,y=.50),
],loc['graph_focus']['E_GAUGE'],rules=['여러 계기 동시불량은 sensor 여러 개 동시고장보다 cluster power/GND 공통부를 먼저 본다.','transfer curve가 없는 sender는 임의 resistance 숫자를 넣지 않고 실제 상태/정상차/전후단 동시비교로 가른다.'],limitations=['각 gauge numeric cavity 및 일부 sender transfer curve는 미확정.'],refs=['600123-00120 sheet 1/4,4/4','D24NAP O&M IGN2 20A'],imgs=['oem_pages/p367.jpg','oem_pages/p370.jpg'])

groups['EL_WORK_REAR']=G('후방 작업등/경광 · switch→harness→load','전장','옵션별 fuse 번호를 추정하지 않고, 실제 부하 커넥터에서 B+/GND를 잡아 상류 switch/relay와 후방 harness를 거꾸로 추적한다',[
 P('WR1','후방 부하 B+','rear work lamp/strobe connector','B+↔local GND 부하전압','해당 switch ON','FIELD_METHOD','','전압 있음→GND/load; 없음→upstream',x=.65,y=.32),
 P('WR2','후방 부하 GND drop','load GND↔battery -POST','부하 중 전압강하','switch ON','FIELD_METHOD','','B+ 정상+GND drop→rear ground',x=.82,y=.55),
 P('WR3','작업등/경광 switch 출력','cockpit/option switch output function line','입력/출력 비교','switch OFF↔ON','OEM_FUNCTION_PIN_VERIFY','','input 정상+output 없음→switch/connector',x=.38,y=.30),
 P('WR4','relay/후방 harness 전단','option relay/output or rear harness upstream connector','전단/후단 동시 부하전압','switch ON','OEM_VERIFY','','전단 정상/후단 없음→harness/connector',x=.50,y=.55),
],loc['graph_focus']['E_WORK_LAMP'],rules=['옵션 회로 fuse/cavity가 불명확해도 부하에서 거꾸로 올라가면 진단은 가능하다. 숫자 ID는 임의 생성하지 않는다.'],limitations=['옵션별 정확 fuse/relay numeric ID는 source-limited.'],refs=['600123-00120 sheet 4/4','SB5120C05 option lamp groups'],imgs=['oem_pages/p370.jpg'])

groups['EL_FR_CONTROL']=G('F/R switch/solenoid · 접점/coil/plunger','전장','OEM 스위치 접점과 solenoid 저항/플런저 기준으로 전기명령과 실제 valve actuation을 분리한다',[
 P('FR1','FWD/REV fuse #3','fuse box F/R fuse #3','퓨즈 양단 전압','KEY ON','OEM_EXACT','','공급없음→fuse/upstream',x=.12,y=.25),
 P('FR2','F/R SW common 4↔7','F/R switch connector','pin 4↔7 continuity','OEM procedure state','OEM_EXACT','4↔7 continuity per OEM','불량→switch/common contact',x=.30,y=.25),
 P('FR3','FWD contact 1↔2','F/R switch connector','pin 1↔2 continuity','F position vs N','OEM_EXACT','F: continuity; N: open','명령 스위치 확인',x=.48,y=.20),
 P('FR4','REV contact 1↔3','F/R switch connector','pin 1↔3 continuity','R position vs N','OEM_EXACT','R: continuity; N: open','명령 스위치 확인',x=.48,y=.46),
 P('FR5','F/R solenoid coil','transmission valve F/R solenoid connector','coil resistance + energized B+/GND','25°C resistance check / command active','OEM_EXACT','10±0.3 Ω @25°C','전기값 정상→plunger/spool로',x=.68,y=.32),
 P('FR6','Solenoid plunger travel','F/R solenoid plunger/valve','실제 plunger movement','energized','OEM_EXACT','approximately 3.18 mm','coil 정상+plunger 부족→solenoid/mechanical',x=.84,y=.32),
],loc['graph_focus']['E_FR_CONTROL'],rules=['솔레노이드 자화만으로 spool 정상판정하지 않는다. 접점→coil→plunger→valve 순서로 확인.'],refs=['SM1018-01 §2-4-2','600123-00120','D24NAP O&M IGN3 / FWD#1 / REV#5'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_AC_POWER']=G('A/C power · controller/blower split','에어컨','화면 dead, 화면 live/blower dead, blower live/compressor no-response를 첫 단계에서 분리하고 냉매 진단으로 바로 가지 않는다',[
 P('AP1','A/C supply fuse 기능선','A/C power supply/fuse path','퓨즈 입력/출력 부하전압','KEY ON / A/C power ON','OEM_VERIFY','','정확 fuse cavity/rating은 미확정; 기능상 공급을 추적',x=.14,y=.30),
 P('AP2','A/C controller B+/IGN','A/C controller connector power functions','B+/IGN↔controller GND','KEY ON','OEM_FUNCTION_PIN_VERIFY','','display dead면 power/GND부터',x=.34,y=.30),
 P('AP3','A/C controller GND drop','controller GND↔battery -POST','부하 중 전압강하','A/C ON attempt','FIELD_METHOD','','B+/IGN 정상+GND 이상→ground',x=.34,y=.58),
 P('AP4','Blower 4-pin supply/GND','evaporator/blower 4-pin connector','기능선 B+/GND 측정','blower command 1/2/3','OEM_FUNCTION_PIN_VERIFY','motor 12V 10A, 3-stage; power connector 4-pin 1.5SQ','controller live+blower dead→blower branch',x=.62,y=.32),
 P('AP5','Blower Stage 3 direct test','blower motor disconnected as OEM test condition','OEM 절차에 맞춰 Stage 3 direct connection','safe direct-test condition','OEM_EXACT','Stage 3 direct connection motor test','direct test fail→blower; pass→controller/resistor/harness',x=.82,y=.32),
 P('AP6','Thermostat 2-pin','A/C thermostat connector','2-pin functional state/input','A/C cooling request','OEM_FUNCTION_PIN_VERIFY','thermostat connector 2-pin 1SQ','blower works but compressor request absent→control/inhibit path',x=.80,y=.58),
],loc['graph_focus']['E_AC_POWER_NO'],rules=['A/C display 자체 dead이면 냉매압부터 보지 않는다.','blower direct Stage 3 test는 OEM motor test fact; numeric pin roles는 별도 확정하지 않는다.'],limitations=['A/C fuse cavity/rating, controller numeric B+/IGN/GND, blower 4-pin individual roles는 source-limited.'],refs=['SM1018-01 §8-5-1/2','SB5120C05 A/C exploded groups'],imgs=['oem_pages/p271.jpg'])

groups['EL_PREHEAT']=G('예열 · relay input/output→heater','전장','예열 명령이 있을 때 relay의 부하전원과 출력, heater/glow 쪽 B+를 같은 이벤트에서 비교한다',[
 P('PH1','Preheat relay B+','engine bay preheat relay load input','relay input↔GND','KEY ON / preheat request','OEM_FUNCTION_PIN_VERIFY','','입력 없음→upstream protection',x=.18,y=.30),
 P('PH2','Preheat relay command','relay coil/control function line','command on/off 확인','preheat request','OEM_FUNCTION_PIN_VERIFY','','명령 없음→ECU/condition/control; 명령 있음→contact output',x=.38,y=.55),
 P('PH3','Preheat relay output','relay load output function terminal','input/output 동시 부하전압','preheat active','OEM_FUNCTION_PIN_VERIFY','','input 유지+output 없음/drop→relay/socket',x=.55,y=.30),
 P('PH4','Glow/Air-heater B+','glow plug/air-heater feed bus','B+↔engine GND','preheat active','FIELD_METHOD','','relay output 정상+load feed 없음→harness/bus',x=.74,y=.30),
 P('PH5','Engine GND','heater return/engine block↔battery -POST','부하 중 voltage drop','preheat active','FIELD_METHOD','','supply 정상+heat fail→load/ground/current branch',x=.88,y=.55),
],loc['graph_focus']['E_PREHEAT_NO'],rules=['relay click만으로 접점 통과 정상판정 금지; input/output를 부하상태에서 비교.'],limitations=['preheat relay numeric terminals/fuse cavity는 미확정.'],refs=['600123-00120 sheet 3/4~4/4','D24 engine preheat circuit'],imgs=['oem_pages/p369.jpg','oem_pages/p370.jpg'])

groups['EL_FUEL_HEATER']=G('연료히터 · relay/load/ground','전장','히터 커넥터에서 부하전압을 먼저 확인하고, 없으면 relay input/output와 명령을 역추적한다',[
 P('FH1','Fuel-heater B+','fuel filter/heater connector','B+↔local GND 부하전압','heater request/low-temp condition','FIELD_METHOD','','B+ 정상→GND/load; 없음→relay/upstream',x=.65,y=.30),
 P('FH2','Fuel-heater GND drop','heater GND↔battery -POST','부하 중 voltage drop','heater active','FIELD_METHOD','','B+ 정상+GND 이상→ground',x=.82,y=.55),
 P('FH3','Fuel-heater relay input/output','engine bay relay/fuse area','relay load IN/OUT simultaneous','heater request','OEM_VERIFY','','IN normal/OUT absent→relay/socket',x=.38,y=.30),
 P('FH4','Fuel-heater command','relay coil/control function line','command presence','heater condition met','OEM_VERIFY','','command absent→control condition/ECU branch',x=.38,y=.58),
],loc['graph_focus']['E_FUEL_HEATER_NO'],rules=['exact cavity가 없어도 load→relay→control의 기능선 역추적으로 고장구간을 자른다.'],limitations=['fuel-heater exact fuse cavity/pin/relay numeric ID source-limited.'],refs=['600123-00120 sheet 3/4','SB5120C05 fuel-heater group'],imgs=['oem_pages/p369.jpg'])

groups['EL_BRAKE_OIL_WARN']=G('브레이크오일 경고 · switch→signal→cluster','전장','실제 오일레벨/float 기계상태와 switch 상태, cluster 입력을 분리해 오일부족과 회로오류를 구분한다',[
 P('BW1','실제 brake reservoir level','brake reservoir','실제 fluid level/float 자유움직임 육안확인','vehicle level/safe','OEM_FUNCTION_EXACT','','실제 low면 회로진단 전에 원인/누유 확인',x=.18,y=.55),
 P('BW2','Brake oil level switch','reservoir level switch connector','switch state toggle/continuity','float low↔normal state','OEM_FUNCTION_PIN_VERIFY','','switch 자체가 안 바뀌면 sensor/switch',x=.38,y=.30),
 P('BW3','Signal at cluster side','cluster warning input function line','switch side와 cluster side 동시 비교','KEY ON / float state change','OEM_FUNCTION_PIN_VERIFY','','switch side changes but cluster side not→harness/connector',x=.62,y=.30),
 P('BW4','Cluster power/GND','instrument cluster power/ground','IGN supply and GND drop','KEY ON','OEM_PLUS_FIELD','','여러 warnings/gauges 동시이상→cluster common supply',x=.82,y=.55),
],loc['graph_focus']['E_BRAKE_OIL_WARN'],rules=['경고등 점등 자체를 sensor fault로 단정하지 않고 실제 fluid low/leak부터 배제.'],limitations=['numeric connector pin roles 미확정.'],refs=['600123-00120','SM1018-01 brake system'],imgs=['oem_pages/p367.jpg','oem_pages/p370.jpg'])

groups['EL_CLUSTER_POWER']=G('계기판 전원 · IGN2/B+/GND','전장','계기판이 완전히 죽었을 때 sender를 건드리지 않고 IGN2→cluster B+/IGN→GND 순서로 생존전원을 확인한다',[
 P('CP1','IGN2 20A 양단','fuse block IGN2 20A','fuse input/output voltage','KEY ON','OEM_EXACT','IGN2 20A ECU/instrument display power','input normal/output absent→fuse/socket',x=.18,y=.30),
 P('CP2','Cluster B+/IGN','instrument cluster connector power functions','B+/IGN↔cluster GND loaded voltage','KEY ON','OEM_FUNCTION_PIN_VERIFY','','supply missing→harness/key/fuse branch',x=.45,y=.30),
 P('CP3','Cluster GND drop','cluster GND↔battery -POST','loaded voltage drop','KEY ON / display attempt','FIELD_METHOD','','power normal+GND drop→ground/connector',x=.65,y=.55),
 P('CP4','Cluster wake/display response','cluster itself','power/GND stable while display remains dead','KEY ON','FIELD_ISOLATION','','supply stable+no wake→cluster internal likelihood rises',x=.82,y=.32),
],loc['graph_focus']['E_CLUSTER_POWER_NO'],rules=['SM1018 일반표의 instrument 15A와 current-layout O&M IGN2 20A를 섞어 하나의 fuse cavity로 간주하지 않는다. 실차 named fuse-block 적용사양을 우선.'],limitations=['cluster numeric B+/IGN/GND cavity 미확정.'],refs=['600123-00120','D24NAP O&M IGN2 20A','SM1018-01 general maintenance fuse table'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_CAN_NETWORK']=G('CAN 통신 · all-node vs single-node','전장','60Ω 일반론으로 바로 판정하지 않고, 전체 노드 불통인지 단일 노드 불통인지→해당 노드 power/GND→CAN H/L 도달 순으로 본다',[
 P('CN1','진단커넥터/scan response','vehicle diagnostic connector','어떤 모듈이 응답/무응답인지 목록화','KEY ON','FIELD_METHOD','','all nodes dead→common diag/CAN/power; one node dead→local',x=.16,y=.30),
 P('CN2','문제 node B+/IGN','ECU/OSS/ECT 등 문제 controller connector','power functions loaded voltage','KEY ON','OEM_FUNCTION_PIN_VERIFY','','power 불안정이면 CAN controller fault 판정 금지',x=.38,y=.28),
 P('CN3','문제 node GND drop','controller GND↔battery -POST','loaded voltage drop','KEY ON','FIELD_METHOD','','GND rise→ground/harness',x=.38,y=.58),
 P('CN4','CAN-H / CAN-L at node','problem node CAN pair','H/L 상태/파형을 diagnostic connector/other node와 비교','KEY ON','OEM_FUNCTION_PIN_VERIFY','','network elsewhere normal+local pair absent→branch harness',x=.64,y=.30),
 P('CN5','Node isolation/reconnect','problem node connector','문제 node 분리 전후 다른 modules communication 비교','KEY OFF disconnect→KEY ON retest','FIELD_ISOLATION','','분리 후 network 회복→node/transceiver or local short branch',x=.82,y=.50),
],loc['graph_focus']['E_CAN_NETWORK'],tools=['진단기','DMM/백프로브','오실로스코프(가능 시)'],rules=['이 모델의 termination 위치와 nominal resistance가 OEM 확정되지 않은 상태에서 “무조건 60Ω”을 합격선으로 넣지 않는다.','다른 모듈 통신비교가 single-node controller fault 판정의 핵심.'],limitations=['network termination locations/nominal resistance source-limited.'],refs=['600123-00120 ECU/CAN circuit'],imgs=['oem_pages/p368.jpg','oem_pages/p370.jpg'])

groups['EL_SEATBELT']=G('시트벨트 입력 · switch→OSS','전장','벨트 buckle switch 실제 전환과 OSS 입력을 비교해 switch/하네스/controller input을 분리한다',[
 P('SB1','Seat-belt switch','seat/buckle switch connector','buckle open↔latched state change','KEY ON / buckle toggle','OEM_FUNCTION_PIN_VERIFY','','switch 상태가 안 바뀌면 switch/connector',x=.24,y=.30),
 P('SB2','OSS seat-belt input','OSS controller input function line','switch side vs OSS side simultaneous','buckle toggle','OEM_FUNCTION_PIN_VERIFY','','switch normal+OSS side no change→harness/terminal',x=.52,y=.30),
 P('SB3','OSS BAT4/IGN3/GND','OSS power/signal supply and GND','fuse/supply loaded voltage + GND drop','KEY ON','OEM_PLUS_FIELD','BAT4 20A + IGN3 15A','여러 OSS inputs abnormal→common supply/controller health',x=.78,y=.52),
],loc['graph_focus']['E_SEATBELT_INPUT'],rules=['buckle switch jumper만으로 OSS 전체 정상판정하지 않는다. OSS input에서 실제 변화 확인.'],refs=['600123-00120','D24NAP O&M OSS supplies'],imgs=['oem_pages/p367.jpg','oem_pages/p370.jpg'])

groups['EL_LICENSE']=G('번호판등 · lamp B+/GND','전장','다른 tail/rear lamp와 비교해 공통 lamp relay/feed인지 번호판등 로컬 branch인지 가른다',[
 P('LP1','다른 rear/tail lamp 비교','rear lamp group','같은 light-switch 상태에서 동시작동 비교','LIGHT ON','FIELD_ISOLATION','','다른 rear lamps도 dead→common feed; license only→local',x=.18,y=.30),
 P('LP2','License lamp B+','license lamp connector/socket','B+↔local GND loaded voltage','LIGHT ON','FIELD_METHOD','','B+ 없음→branch/harness; 있음→GND/bulb',x=.55,y=.30),
 P('LP3','License GND drop','lamp GND↔battery -POST','loaded voltage drop','LIGHT ON','FIELD_METHOD','','B+ normal+GND bad→ground',x=.78,y=.55),
 P('LP4','LAMP relay/light-switch common','relay #4 / light switch feed','common rear-light output comparison','LIGHT ON','OEM_PLUS_FIELD','BAT2 20A→LAMP relay #4; ACC15 light-switch feed','other lamps also fail only',x=.35,y=.58),
],loc['graph_focus']['E_LICENSE_NO'],rules=['번호판등 단독불량이면 relay부터 바꾸지 말고 socket B+/GND 먼저.'],refs=['600123-00120','D24NAP O&M LAMP relay #4'],imgs=['oem_pages/p370.jpg'])

groups['EL_HOURMETER']=G('아워미터 · supply/run-signal/ground','전장','계기판 전원은 살아있는데 적산만 안 되는지 먼저 분리하고, hourmeter supply와 run/enable 기능신호를 확인한다',[
 P('HM1','Cluster/common supply','cluster/hourmeter shared supply','KEY ON supply and GND compare','KEY ON','OEM_FUNCTION_PIN_VERIFY','','cluster also dead→common power group',x=.18,y=.30),
 P('HM2','Hourmeter B+/IGN','hourmeter connector/function line','loaded voltage','KEY ON / engine run','OEM_FUNCTION_PIN_VERIFY','','supply absent→harness/fuse/control',x=.45,y=.30),
 P('HM3','Hourmeter enable/run signal','hourmeter control function line','engine stopped vs running state change','engine OFF↔running','OEM_VERIFY','','supply normal but no enable→upstream control',x=.62,y=.55),
 P('HM4','Hourmeter GND drop','hourmeter GND↔battery -POST','loaded voltage drop','KEY ON/running','FIELD_METHOD','','supply/enable/GND normal+no count→hourmeter itself',x=.82,y=.35),
],loc['graph_focus']['E_HOURMETER_NO'],rules=['numeric pin/cavity가 없으면 기능신호를 실제 상태변화로 식별한다.'],limitations=['exact fuse cavity/hourmeter numeric pin source-limited.'],refs=['600123-00120'],imgs=['oem_pages/p367.jpg','oem_pages/p369.jpg'])

groups['EL_REAR_LAMP']=G('리어램프 · common feed vs local branch','전장','전방/다른 lamp와 비교해 LAMP relay/light-switch 공통부와 후방 harness/load를 분리한다',[
 P('RL1','LAMP relay #4 output','relay box LAMP relay #4','input/output loaded voltage','LIGHT ON','OEM_ID_PLUS_FIELD','BAT2 20A→relay #4','front/rear both dead면 common',x=.20,y=.30),
 P('RL2','Rear lamp B+','rear lamp connector','B+↔local GND loaded voltage','LIGHT ON','FIELD_METHOD','','relay output normal+rear absent→harness',x=.55,y=.30),
 P('RL3','Rear lamp GND drop','rear lamp GND↔battery -POST','loaded voltage drop','LIGHT ON','FIELD_METHOD','','B+ normal+ground bad→rear ground',x=.78,y=.55),
],loc['graph_focus']['E_REAR_LAMP_NO'],rules=['전방 lamps 정상+rear only dead면 relay 교환보다 rear branch부터.'],refs=['600123-00120','D24NAP O&M BAT2/LAMP#4'],imgs=['oem_pages/p370.jpg'])

groups['EL_STROBE']=G('스트로브/경광등 · ACC feed/option branch','전장','ACC15 공통 feed 존재와 strobe option switch/output, load GND를 순서대로 확인한다',[
 P('ST1','ACC 15A 양단','fuse block ACC 15A','fuse both sides loaded voltage','STROBE ON','OEM_EXACT','ACC15 includes STOP/strobe/light-switch feed','input/output compare',x=.16,y=.30),
 P('ST2','Strobe switch/output','option switch/control function line','input/output compare','OFF↔ON','OEM_FUNCTION_PIN_VERIFY','','input normal/output absent→switch/control',x=.42,y=.30),
 P('ST3','Strobe B+','strobe/beacon connector','B+↔local GND','ON','FIELD_METHOD','','B+ normal→GND/load',x=.65,y=.30),
 P('ST4','Strobe GND drop','strobe GND↔battery -POST','loaded voltage drop','ON','FIELD_METHOD','','B+/GND normal+no light→load',x=.82,y=.55),
],loc['graph_focus']['E_STROBE_NO'],rules=['strobe option configuration must be recorded; exact numeric option pins are not guessed.'],limitations=['option connector numeric pins source-limited.'],refs=['600123-00120 sheet 4/4','D24NAP O&M ACC15'],imgs=['oem_pages/p370.jpg'])

def gauge_group(prefix,title,sensor,display,focus):
 return G(title,'전장',f'{sensor}의 실제 변화와 sensor-side signal, display-side signal을 동시에 비교해 sender/하네스/표시부를 분리한다',[
  P(prefix+'1',sensor+' 실제상태/센서','sensor mounting location','실제 물리상태와 connector 상태 기록','냉간/열간 또는 level 변화','OEM_FUNCTION_EXACT','','실제상태 먼저 기록',x=.18,y=.30),
  P(prefix+'2',sensor+' signal at sender','sensor connector signal function line','signal/continuity/voltage trend','실제 상태 변화','OEM_FUNCTION_PIN_VERIFY','','sender-side 변화 없음→sensor/return',x=.40,y=.30),
  P(prefix+'3','같은 signal at display side','cluster/display corresponding input function line','sender-side와 동시비교','same condition','OEM_FUNCTION_PIN_VERIFY','','sender 정상+display side 다름→harness/connector',x=.62,y=.30),
  P(prefix+'4','Cluster common power/GND','cluster IGN2 supply/GND','supply loaded voltage + GND drop','KEY ON','OEM_PLUS_FIELD','IGN2 20A current-layout O&M','signal 도달+display only wrong→display processing',x=.82,y=.55),
 ],focus,rules=['OEM transfer curve가 없으면 임의 resistance/voltage 숫자를 합격기준으로 만들지 않는다. 실제 상태추종과 전후단 비교로 구간을 자른다.'],limitations=['sensor transfer curve와 일부 numeric cavity source-limited.'],refs=['600123-00120 gauge/sender circuits','D24NAP O&M IGN2 20A'],imgs=['oem_pages/p367.jpg','oem_pages/p370.jpg'])

groups['EL_WATER_GAUGE']=gauge_group('WG','수온 게이지 · sender→display','WATER TEMP SENDER','WATER TEMP GAUGE',loc['graph_focus']['E_WATER_GAUGE'])
groups['EL_TM_TEMP_GAUGE']=gauge_group('TG','T/M 오일온도 게이지 · sender→display','T/M OIL TEMP SENDER','T/M TEMP GAUGE',loc['graph_focus']['E_TM_TEMP_GAUGE'])
groups['EL_FUEL_GAUGE']=gauge_group('FG','연료 게이지 · sender→display','FUEL LEVEL SENDER','FUEL LEVEL GAUGE',loc['graph_focus']['E_FUEL_GAUGE_ONLY'])

groups['EL_WIPER']=G('와이퍼 · motor loaded test→switch/harness','전장','전/후방 범위를 먼저 가르고, 모터 커넥터 B+/GND와 직접구동으로 모터/링크를 먼저 분리한 뒤 스위치/옵션 harness로 올라간다',[
 P('WP1','Wiper motor B+','front or rear wiper motor connector','B+↔local GND loaded voltage','wiper command active','FIELD_METHOD','','B+ present→GND/motor; absent→upstream',x=.62,y=.28),
 P('WP2','Wiper motor GND drop','motor GND↔battery -POST','loaded voltage drop','wiper command active','FIELD_METHOD','','B+ normal+GND bad→ground',x=.78,y=.55),
 P('WP3','Wiper motor direct isolation','motor disconnected connector','fused direct B+/GND only when mechanically safe','engine/key safe condition','FIELD_ISOLATION','','direct drive fail→motor/link; pass→vehicle control',x=.82,y=.25),
 P('WP4','Wiper switch input/output','cockpit wiper switch function lines','input/output state compare','OFF/LOW/HIGH as equipped','OEM_VERIFY','','input normal+output absent→switch/control',x=.38,y=.30),
 P('WP5','Harness front vs rear segment','option harness connectors between switch and motor','upstream/downstream loaded voltage compare','wiper command active','FIELD_ISOLATION','','upstream normal/downstream absent→harness/connector',x=.48,y=.58),
],loc['graph_focus']['E_WIPER_NO'],rules=['전/후방 한쪽만 불량이면 해당 motor/harness, 둘 다면 common switch/supply를 먼저 본다.','직접구동은 fused lead와 기계적 간섭 없는 조건에서만.'],limitations=['option fuse cavity/rating, switch numeric pins, relay identity across cabin configs source-limited.'],refs=['SB5120C05 front/rear wiper option groups'],imgs=['parts_views/parts_p488.png','parts_views/parts_p422.png','parts_views/parts_p486.png'])

groups['EL_WASHER']=G('와셔 · 유로와 전기 분리','전장','펌프 소리가 나는데 분사가 안 되는 유로고장과, 펌프 자체/전원/스위치 전기고장을 첫 단계에서 분리한다',[
 P('WS1','탱크→호스→노즐 유로','washer tank/hoses/nozzle','액량, 빠짐, kink, blockage/leak 육안/유로확인','washer command','FIELD_ISOLATION','','pump sound 있음+flow 없음→유로 먼저',x=.20,y=.55),
 P('WS2','Washer pump B+','washer pump connector at tank','B+↔local GND loaded voltage','washer command held','FIELD_METHOD','','B+ present→GND/pump; absent→switch/upstream',x=.55,y=.30),
 P('WS3','Pump GND drop','pump GND↔battery -POST','loaded voltage drop','washer command','FIELD_METHOD','','B+ normal+GND bad→ground',x=.74,y=.55),
 P('WS4','Washer switch output','cockpit washer command function line','input/output state compare','command off↔on','OEM_VERIFY','','switch input normal+output absent→switch/control',x=.36,y=.28),
 P('WS5','Switch→pump harness','option harness upstream/downstream','loaded voltage compare','washer command','FIELD_ISOLATION','','switch output normal+pump absent→harness/connector',x=.48,y=.58),
],loc['graph_focus']['E_WASHER_NO'],rules=['유로막힘과 펌프전기고장을 섞지 않는다. 펌프음/커넥터전압을 먼저 같이 본다.'],limitations=['washer pump exact PN, fuse cavity/rating, switch numeric pins source-limited.'],refs=['SB5120C05 washer tank/front wiper option group'],imgs=['parts_views/parts_p488.png'])

# graph mappings: keep engine/D24 existing mappings, replace/expand vehicle electrical.
map_new={
 'E_STOP_NO':'EL_STOP_LAMP','E_STOP_ON':'EL_STOP_LAMP','E_HEAD_NO':'EL_HEAD_LAMP','E_TURN_NO':'EL_TURN_HAZARD','E_HORN_NO':'EL_HORN','E_BACKUP_NO':'EL_BACKUP',
 'E_START_NO':'START_VDROP','E_CHARGE':'EL_CHARGE','E_PARK_INPUT':'EL_PARK_INPUT','E_LIFT_LOCK':'EL_LIFT_LOCK','E_GAUGE':'EL_GAUGE_COMMON','E_WORK_LAMP':'EL_WORK_REAR','E_FR_CONTROL':'EL_FR_CONTROL',
 'E_OSS_SEAT_LOCK':'OSS_HEALTH','E_AC_POWER_NO':'EL_AC_POWER','E_AC_COND_FAN_NO':'AC_COND_FAN','E_PREHEAT_NO':'EL_PREHEAT','E_FUEL_HEATER_NO':'EL_FUEL_HEATER','E_BRAKE_OIL_WARN':'EL_BRAKE_OIL_WARN',
 'E_CLUSTER_POWER_NO':'EL_CLUSTER_POWER','E_CAN_NETWORK':'EL_CAN_NETWORK','E_SEATBELT_INPUT':'EL_SEATBELT','E_LICENSE_NO':'EL_LICENSE','E_HOURMETER_NO':'EL_HOURMETER','E_REAR_LAMP_NO':'EL_REAR_LAMP','E_STROBE_NO':'EL_STROBE',
 'E_WATER_GAUGE':'EL_WATER_GAUGE','E_TM_TEMP_GAUGE':'EL_TM_TEMP_GAUGE','E_FUEL_GAUGE_ONLY':'EL_FUEL_GAUGE','E_WIPER_NO':'EL_WIPER','E_WASHER_NO':'EL_WASHER',
}
# D24 electrical graph mappings retained from V8.5.
for gid in ['E_D24_RAIL_PRESSURE','E_D24_BOOST_PRESSURE','E_D24_WATER_TEMP','E_D24_MAF','E_D24_5V_REF','E_D24_ECU_NO_COMM','E_D24_CRANK_NO_START']:
    map_new[gid]=tp['graph_map'][gid]

tp['groups'].update(groups)
tp['graph_map'].update(map_new)
tp['version']='v1.6-electrical-probe-coverage'
tp['rule']='정비에서 품번보다 먼저 실제 프로브/게이지 위치, 부하상태, 비교/격리 결과를 보여준다. 전장 38개 그래프 모두 전용 측정포인트 화면을 가진다. OEM 미확정 cavity/threshold는 기능선/비교법으로 유지하고 임의값을 만들지 않는다.'
(A/'test_point_locator_v1.json').write_text(json.dumps(tp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'electrical_diag_v1.json').write_text(json.dumps(el,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Update release identity.
bg=ROOT/'app/build.gradle'
s=bg.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 31',s)
s=re.sub(r'versionName\s+"[^"]+"','versionName "0.18-rc-expert-v8.6-electrical-probe"',s)
bg.write_text(s,encoding='utf-8')
rp=A/'diagnostic_release.json'; r=json.loads(rp.read_text(encoding='utf-8'))
r['state']='RC EXPERT V8.6 ELECTRICAL PROBE'; r['version_name']='0.18-rc-expert-v8.6-electrical-probe'; r['git_commit_sha']='UNSTAMPED_LOCAL_PATCH'; r['source_branch']='v18-rc-auto'; rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('added groups',len(groups),'graph mappings',len(map_new),'total groups',len(tp['groups']),'graph_map',len(tp['graph_map']))
