#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'app/src/main/assets/test_point_locator_v1.json'

def pt(id,label,where,connect,condition,expected='',decision='',source='OEM_EXACT',x=.5,y=.5,note=''):
    d={'id':id,'label':label,'where':where,'connect':connect,'condition':condition,'source_class':source,'x':x,'y':y}
    if expected:d['expected']=expected
    if decision:d['decision']=decision
    if note:d['note']=note
    return d

def grp(title,system,summary,tools,conditions,points,rules,images,diagram_note,source_refs,limitations=None,focus_ids=None):
    return {'title':title,'system':system,'summary':summary,'tools':tools,'conditions':conditions,'points':points,'decision_rules':rules,'oem_images':images,'diagram_note':diagram_note,'source_refs':source_refs,'limitations':limitations or [],'focus_ids':focus_ids or []}

groups={}

groups['TM_PRESSURE_TAPS']=grp(
 '트랜스미션 압력탭 · 어디에 게이지를 물릴지', '트랜스미션',
 'T/M 압력시험은 오일 온도와 회전수를 맞춘 뒤 Tap별 압력을 비교해야 한다. 단순히 “압력 낮음”이 아니라 Tap6↔Tap1, F/R clutch, converter/lube를 분리한다.',
 ['0~20.5 bar (0~300 psi) 압력계','회전계','서미스터 온도탐침','블록/잭스탠드'],
 ['T/M 오일 49~71°C','차량을 평탄한 곳에서 안전 고정','저속 공전과 2,000 rpm을 구분해 기록','F/R clutch는 해당 방향 선택 상태에서 측정'],
 [
  pt('TM1','Tap 1 · 펌프/시스템 압력 비교점','트랜스미션 밸브/유압계통의 Tap1','압력계 연결','N에서 Tap6와 비교','Tap6 정상이라면 Tap1도 정상이어야 함','Tap6 정상 + Tap1 비정상 → 유압 막힘/인칭밸브 계통을 우선 추적','OEM_EXACT',.31,.40,'정확 외형 위치는 OEM p078/p079 확인'),
  pt('TM2','Tap 2 · 컨버터 출구 / 쿨러 입구','트랜스미션 상부 라인 Tap2','압력계 연결','N','저속 0.3~0.6 bar (4~8 psi) / 2,000rpm 2.5~4.0 bar (36~58 psi)','비정상 시 converter outlet/cooler inlet 회로를 분리','OEM_EXACT',.42,.23),
  pt('TM3','Tap 3 · 컨버터 충전(입구)','트랜스미션 상부 라인 Tap3','압력계 연결','N','저속 0.7~1.4 bar (10~20 psi) / 2,000rpm 5.9~8.0 bar (85~115 psi)','Tap3만 낮으면 converter charge 계통을 추적','OEM_EXACT',.28,.20),
  pt('TM4','Tap 4 · 전진 클러치','밸브 바디 하부 측 Tap4','압력계 연결','F 선택','저속 7.3~8.6 bar (105~125 psi) / 2,000rpm 7.3~9.7 bar (105~140 psi)','F에서만 낮으면 전진 솔레노이드/스풀/클러치 공급계통을 좁힘','OEM_EXACT',.73,.67),
  pt('TM5','Tap 5 · 후진 클러치','밸브 바디 측 Tap5','압력계 연결','R 선택','저속 7.3~8.6 bar (105~125 psi) / 2,000rpm 7.3~9.7 bar (105~140 psi)','R에서만 낮으면 후진 솔레노이드/스풀/클러치 공급계통을 좁힘','OEM_EXACT',.80,.43),
  pt('TM6','Tap 6 · 메인/펌프 압력','밸브 본체 위 Tap6','압력계 연결','N','저속 8.3~10.3 bar (120~150 psi) / 2,000rpm 9.0~11.0 bar (130~160 psi)','Tap6와 Tap1 둘 다 낮으면 펌프/메인압 계통. Tap6만 비정상인데 Tap1 정상인 패턴은 매뉴얼 분기와 재확인 필요','OEM_EXACT',.70,.22),
  pt('TM7','Tap 7 · 윤활 압력','트랜스미션 라인 Tap7','압력계 연결','N','저속 0.1~0.7 bar (2~10 psi) / 2,000rpm 2.4~3.5 bar (35~50 psi)','윤활만 낮으면 cooler outlet→lube 공급/내부누설 계통을 좁힘','OEM_EXACT',.49,.47),
 ],
 ['모든 Tap을 같은 오일온도 조건에서 기록한다.','F/R 한쪽만 낮으면 공통 펌프보다 해당 방향 제어/클러치 회로를 우선한다.','Tap6↔Tap1 차이는 인칭/막힘 여부를 가르는 핵심 비교다.','압력조정 전에 원인 격리를 먼저 하고, 임의 shim 조정으로 증상을 덮지 않는다.'],
 ['oem_pages/p078.jpg','oem_pages/p079.jpg'],
 '앱 그림은 OEM 그림 2-22를 정비사 측정 순서에 맞게 단순화한 위치도이며 치수도면이 아니다.',
 ['SM1018-01 §2-3-4, p2-30~31'],
 focus_ids=['TRANSMISSION_CENTER']
)

groups['BRAKE_BLEED_ISOLATION']=grp(
 '서비스브레이크 · 마스터/좌우 액슬 격리와 블리더', '브레이크',
 '스폰지·페달 침하·내부누설을 한 번에 “씰 불량”으로 결론내리지 않는다. 먼저 공기/외부누설을 배제하고 마스터와 좌·우 액슬을 구간격리한다.',
 ['투명 호스','플라스틱 병','배출용 렌치','유압 정격 캡/플러그·어댑터','압력계(해당 시험 시)'],
 ['차량 안전고정','유압 작업 전 잔압 해제','블리딩 중 리저버 Full 유지','호스 압착용 바이스그립 사용 금지'],
 [
  pt('BR1','마스터 실린더 P 포트','플로어/페달 하부 마스터 실린더의 P 공급포트','공급유량/상태 확인','엔진 작동 및 브레이크 공급 정상 조건','OEM 동작설명상 약 0.8 GPM 공급','공급 자체가 부족하면 액슬 씰보다 상류 유량분배/공급 문제부터 해결','OEM_EXACT',.30,.26,'40 bar는 마스터 릴리프 크래킹 압력이지 액슬 씰 누설판정 압력이 아님'),
  pt('BR2','마스터 출력 격리점','마스터→액슬로 나가는 서비스브레이크 출력라인','유압 정격 캡/플러그로 회로 격리','페달 침하 재현','고정된 출력에서 페달이 계속 침하하면 마스터 내부 bypass를 강하게 의심','마스터 격리에서 유지되면 downstream 좌/우 액슬로 이동','FIELD_ISOLATION',.40,.43),
  pt('BR3','좌측 드라이브액슬 블리더/라인','좌측 전륜 드라이브액슬 브레이크','투명호스 또는 좌측 회로 격리','블리딩/누설 분리','공기 없는 오일이 나올 때까지 반복','좌측 격리에서 hold가 회복되면 좌측 액슬 내부누설 가능성 상승','OEM_PLUS_FIELD',.22,.74),
  pt('BR4','우측 드라이브액슬 블리더/라인','우측 전륜 드라이브액슬 브레이크','투명호스 또는 우측 회로 격리','블리딩/누설 분리','공기 없는 오일이 나올 때까지 반복','우측 격리에서 hold가 회복되면 우측 액슬 내부누설 가능성 상승','OEM_PLUS_FIELD',.75,.74),
 ],
 ['블리딩: 페달을 펌프 → “아래”에서 블리드 나사 개방 → 다시 조임 → 페달 해제 → 공기 없어질 때까지 반복.','한쪽 액슬을 격리했을 때만 페달 hold가 회복되면 그쪽 내부누설을 좁힌다.','마스터 출력 격리에서도 페달이 침하하면 마스터 내부 bypass를 우선한다.','분해 전에는 “피스톤 씰 립 마모 vs 보어 스코어”처럼 액슬 내부 세부부품을 억지로 확정하지 않는다.'],
 ['oem_pages/p320.jpg','oem_pages/p365.jpg'],
 'OEM 블리딩 위치와 브레이크 계통을 바탕으로, 앱은 마스터→좌/우 액슬 격리 순서만 재작성한다.',
 ['SM1018-01 §7-2-5A, §7-2-1/2, hydraulic schematic D500093'],
 ['OEM에는 액슬 씰 누설의 허용 압력강하 수치가 제시되지 않음. 임의 threshold 금지.'],
 ['COCKPIT_FRONT','HYD_CONTROL','FRONT_DRIVE_AXLE']
)

groups['HYD_MAIN_RELIEF']=grp(
 '메인 유압 · 메인/틸트/AUX 압력과 유량', '유압',
 '리프트/틸트/AUX 성능불량은 펌프를 바로 교환하지 않고 메인 릴리프와 기능별 relief/flow를 구분한다.',
 ['적정 범위 유압 압력계','T 피팅/정격 호스','유량계(필요 시)','회전계'],
 ['작동유 온도/레벨 정상','호스·피팅 정격 준수','실린더 end-of-stroke 시험은 최소시간','정확 시험포트는 현재 장착 밸브/서비스포트를 OEM에서 확인'],
 [
  pt('HY1','메인 릴리프 · 메인 컨트롤밸브','메인 컨트롤밸브의 MAIN RELIEF V/V 부근','확인된 메인압 시험포트에 압력계','리프트/기능 부하 시','D20 181±3.5 bar / D25 195±3.5 / D30 215.5±3.5 / D33 240(+5,0) bar','모든 기능 공통 저압이면 펌프/메인릴리프/공급계통을 먼저 분리','OEM_EXACT_SETTING_PORT_VERIFY',.44,.58),
  pt('HY2','틸트/AUX 릴리프','컨트롤밸브 TILT/AUX relief 계통','해당 기능 압력 측정','틸트/AUX 부하 시','155±3.5 bar (2,250±50 psi)','메인압 정상인데 틸트/AUX만 낮으면 해당 섹션 relief/스풀/실린더회로로 분리','OEM_EXACT_SETTING_PORT_VERIFY',.53,.50),
  pt('HY3','틸트 유량','컨트롤밸브 tilt flow-control 회로','유량계 연결','tilt 작동','28±2 LPM','압력 정상인데 속도만 느리면 flow-control/누설/기계저항 쪽','OEM_EXACT',.62,.54),
  pt('HY4','AUX1 유량','컨트롤밸브 AUX1 회로','유량계 연결','AUX1 작동','26±2 LPM','AUX1만 유량 부족이면 AUX1 섹션/flow setting 쪽','OEM_EXACT',.68,.46),
 ],
 ['모든 기능이 약하면 공통 공급(PUMP/MAIN RELIEF)을 먼저 본다.','한 기능만 약하면 해당 section relief/spool/actuator를 분리한다.','메인압이 높다고 유량 정상은 아니다. 속도불량에는 유량/내부누설을 별도 확인한다.'],
 ['oem_pages/p365.jpg','oem_pages/p168.jpg'],
 'D500093 회로에서 펌프→메인컨트롤밸브→유량분배/작동기로 가는 필요한 경로만 단순화한다.',
 ['SM1018-01 hydraulic schematic D500093, §4-2'],
 ['정확한 gauge test-port 나사규격/실차 물리 포트는 현재 자료에서 모두 확정되지 않음. 임의 port 번호 금지.'],
 ['HYD_CONTROL','ENGINE_BAY','MAST_FRONT']
)

groups['STEERING_PRIORITY']=grp(
 '스티어링 · 우선순위밸브/LS/실린더 분리', '스티어링',
 '조향불량은 펌프→우선순위밸브→스티어링유닛→실린더를 순서대로 가르고, 리프트/틸트 동시작동 영향을 비교한다.',
 ['유압 압력계','정격 T 피팅/호스','필요 시 유량계','적외선 온도계(국부 발열 확인)'],
 ['작동유 레벨/점도 정상','에어 혼입 배제','좌/우 동일 조건 비교','리프트/틸트 동시작동 전후 비교'],
 [
  pt('ST1','우선순위밸브 공급 P','메인펌프 후 우선순위밸브/컨트롤밸브 공급부','압력/유량 비교','조향 명령 전후','공통 공급이 유지되는지 확인','P가 무너지면 펌프/공급 문제. P 정상인데 steering만 약하면 priority/LS 이후로 이동','OEM_FUNCTION_EXACT',.37,.58),
  pt('ST2','LS 라인','스티어링 유닛↔우선순위밸브의 LS 신호라인','압력 반응 비교','핸들 중립↔좌/우 조향','조향 시 LS가 증가해 priority spool을 steering 쪽으로 이동시켜야 함','LS 반응 없음 → steering unit/LS line; LS 정상인데 유량 배분 없음 → priority spool 쪽','OEM_FUNCTION_EXACT',.48,.39),
  pt('ST3','스티어링 유닛 relief','스티어링 유닛(steer gear) relief 계통','확인된 시험포트에서 압력','조향 end-load 최소시간','유압회로도에 90 bar 표기','정확 test-port가 확인되지 않으면 90 bar를 임의 포트에서 측정기준으로 사용하지 않음','OEM_SCHEMATIC_SETTING_PORT_VERIFY',.63,.28),
  pt('ST4','스티어 실린더 좌/우 포트','후륜 스티어 액슬 중앙 실린더','좌/우 압력/유량 또는 라인 격리','좌회전/우회전 비교','','한쪽만 반응이 다르면 hose/steering unit port/cylinder internal leak로 좁힘','FIELD_ISOLATION',.78,.64),
 ],
 ['리프트/틸트 작동 때만 조향이 깨지면 priority/check/LS 상호작용을 우선한다.','천천히 돌릴 때만 안 돌고 빠르게는 돌면 내부누설/계량부 문제를 별도 의심한다.','실린더 내부누설 확정 전 좌/우 라인과 기계식 액슬 구속을 분리한다.'],
 ['oem_pages/p303.jpg','oem_pages/p365.jpg'],
 '메인펌프→priority→steering unit→cylinder와 LS 복귀만 남긴 재작성 계통도.',
 ['SM1018-01 §6-1/6-4, hydraulic schematic D500093'],
 ['90 bar는 회로도 표기값. 정확 시험포트 위치는 현재 자료에서 미확정.'],
 ['HYD_CONTROL','REAR_STEER_AXLE']
)

groups['START_VDROP']=grp(
 '무크랭킹/간헐시동 · 부하중 전압강하', '전장',
 'ST에 12V가 “보인다”는 이유로 회로를 정상판정하지 않는다. 실패가 재현된 순간 B+/GND/ST/릴레이를 부하상태에서 잘라 측정한다.',
 ['DMM MIN/MAX','리모트 스타터 스위치(안전조건 충족 시)','백프로브','퓨즈된 점퍼선'],
 ['N/주차브레이크/고임목','시동불발 순간 측정','배터리 납 포스트에 직접 프로브','오픈회로 전압만으로 정상판정 금지'],
 [
  pt('S1','배터리 + 납 포스트','배터리 +POST 자체','DMM + 기준','KEY START','실패 순간 기준전압 유지 여부','포스트 자체가 무너지면 배터리/충전상태부터. 유지되면 downstream','FIELD_METHOD',.15,.50),
  pt('S2','스타터 B+ 스터드','스타터 모터의 메인 B+ 볼트','BAT+POST↔STARTER B+ 전압강하','KEY START','','큰 drop이면 +케이블/단자/크림프. 이미 교환했어도 실패상태에서 다시 확인','FIELD_METHOD',.36,.50),
  pt('S3','스타터 ST/S 단자','스타터 솔레노이드 S/ST','ST↔BAT- 또는 MIN/MAX','KEY START','불발 순간에도 충분한 제어전압이 유지되는지','ST만 무너지면 스타터보다 앞단 START control 쪽','FIELD_METHOD',.56,.50),
  pt('S4','스타터 CASE / 엔진블록','스타터 하우징↔배터리 -POST','전압강하','KEY START','','큰 drop이면 접지/체결부 문제','FIELD_METHOD',.50,.72),
  pt('S5','STARTER relay #8 접점 입력/출력','시트/후드 아래 릴레이박스','relay contact IN/OUT 동시 백프로브','KEY START','','입력 유지 + 출력 drop → 릴레이 접점/소켓 고저항','OEM_ID_PLUS_FIELD',.70,.32),
  pt('S6','STARTER relay #8 코일명령','relay coil 양단/제어선','코일 명령 유지 여부','KEY START','','코일 명령 자체가 떨어지면 KEY ST/N/OSS/interlock 상류','FIELD_METHOD',.72,.55),
  pt('S7','KEY ST 출력','운전석 키스위치 ST 출력','키 B+↔ST 동시 측정','KEY START','','키 B+ 유지 + ST 출력 drop → 키 ST 접점/커넥터 고저항','FIELD_METHOD',.88,.47),
 ],
 ['스타터 B+와 접지가 정상이고 ST 직접 인가에서 매번 크랭킹되면 스타터/주회로는 상당 부분 배제된다.','Relay 접점 입력은 유지되는데 출력만 떨어지면 relay/socket을 확정한다.','Relay coil 명령 자체가 끊기면 KEY ST/Neutral/OSS interlock을 상류로 추적한다.','외부 점프에서 걸린다는 사실만으로 배터리 불량으로 확정하지 않는다.'],
 [],
 '전압강하 측정 순서만 남긴 정비사용 신호 흐름도. 숫자 허용값은 모델 OEM 기준이 없으면 앱이 임의로 만들지 않는다.',
 ['S-7 O&M fuse/relay table; field loaded voltage-drop method'],
 ['OEM 전압강하 허용 mV 수치가 확인되지 않은 구간은 정상차/동일구간 비교와 “어디서 무너지는가”로 판정.'],
 ['BATTERY_GROUND','ENGINE_BAY','UNDER_SEAT_RELAY','COCKPIT_FRONT']
)

groups['OSS_HEALTH']=grp(
 'OSS/시트락 · 컨트롤러 생존(5V + CAN) 확인', '전장',
 '시트센서 점퍼 후에도 동일하면 센서만 계속 추적하지 않는다. OSS B+/IGN/GND, 5V 기준, CAN 통신, 출력 순으로 컨트롤러가 실제 살아 있는지 본다.',
 ['DMM MIN/MAX','진단기','백프로브','오실로스코프(가능 시)'],
 ['시트입력 점퍼는 시험용으로만 사용','다른 CAN 모듈 통신 상태와 비교','5V 외부부하를 순차분리','wiggle은 원인확정이 아니라 재현 트리거'],
 [
  pt('O1','OSS B+ / IGN / GND','OSS 컨트롤러 커넥터 전원·접지','부하상태 백프로브','KEY ON / 증상 재현','','전원/접지가 불안정하면 컨트롤러 판정 전에 공급회로 수리','OEM_FUNCTION_PIN_VERIFY',.20,.52),
  pt('O2','SEAT 입력','OSS의 시트 입력선','실제 센서 vs 점퍼 비교','착석/이석/점퍼','','점퍼에서도 입력이 OSS측에서 안 바뀌면 센서 뒤 배선/입력단으로 좁힘','FIELD_ISOLATION',.38,.32),
  pt('O3','5V 기준회로','OSS 관련 5V 센서/기준신호','VREF 측정 + 외부부하 순차분리','KEY ON','명목 5V의 존재/안정성을 정상차와 비교','외부부하를 모두 분리해도 5V가 무너지면 OSS 내부 regulator/PCB 가능성 상승','FIELD_METHOD_OEM_VALUE_VERIFY',.48,.58),
  pt('O4','CAN H/L + 진단통신','OSS 커넥터 CAN H/L 및 진단기','OSS 응답/다른모듈 비교','KEY ON','','다른 모듈 정상 + OSS 구간 CAN 도달 + OSS만 무응답이면 OSS 내부 CAN/CPU 의심','FIELD_METHOD',.68,.34),
  pt('O5','Lift-lock 출력','OSS→리프트락 솔레노이드 제어출력','명령과 실제 출력 비교','착석/안전조건 충족','','입력/5V/CAN 생존 정상인데 출력만 비정상 → OSS output stage/후단회로 분리','FIELD_METHOD',.82,.58),
 ],
 ['센서 점퍼=OSS 정상이라는 뜻이 아니다. OSS가 입력을 읽고 통신하고 출력하는지 별도로 확인한다.','하네스 흔들 때 락이 풀리면 동시에 VREF/CAN/SEAT 입력 중 무엇이 회복되는지 기록한다.','B+/IGN/GND 정상 + 외부 5V 부하 배제 + OSS만 무통신 + VREF 비정상 조합이면 OSS 내부고장 판정 근거가 강해진다.'],
 [],
 'OSS를 블랙박스로 보지 않고 Power/Input/VREF/CAN/Output의 5블록으로 재작성.',
 ['600123-00120 OSS power/seat/CAN circuits; S-7 fuse/relay O&M cross-check'],
 ['OSS 숫자핀/cavity 및 정확 5V 허용공차가 현재 자료에서 모두 확정된 것은 아님. 임의 숫자 금지.'],
 ['SEAT_OSS','UNDER_SEAT_RELAY','HYD_CONTROL','COCKPIT_FRONT']
)

groups['AC_COND_FAN']=grp(
 'A/C 작동 · 콘덴서팬만 미작동', '에어컨',
 'A/C 전체 전원불량과 분리한다. 컴프레서/블로워가 살아 있는데 팬만 정지하면 팬 전원·접지·직접구동·릴레이/제어순으로 간다.',
 ['DMM MIN/MAX','퓨즈된 점퍼선','클램프미터(선택)','냉매 게이지(전기회로 정상 후)'],
 ['A/C ON','컴프레서 클러치 실제 체결 확인','팬 장시간 정지 상태에서 고압 상승 주의','팬 직접전원은 퓨즈된 점퍼 사용'],
 [
  pt('AC1','콘덴서 팬 커넥터 B+','콘덴서 팬 모터 커넥터','B+↔GND 부하전압','A/C ON','','B+가 정상인데 무회전 → GND/모터로 이동','FIELD_METHOD',.40,.38),
  pt('AC2','팬 GND','팬 모터 GND↔배터리 -POST','전압강하','A/C ON','','GND drop 이상이면 접지/커넥터','FIELD_METHOD',.40,.62),
  pt('AC3','팬 직접전원','팬 모터 분리 커넥터','퓨즈된 B+/GND 직접공급','엔진 OFF 또는 안전조건','정상회전 여부','직접전원에서도 안 돌면 모터 자체를 강하게 확정','FIELD_ISOLATION',.60,.50),
  pt('AC4','팬 릴레이/드라이버 출력','A/C 팬 구동 relay/driver 회로','입력/출력 동시 측정','A/C ON','','입력은 있는데 출력이 없으면 relay/socket/driver','OEM_VERIFY',.76,.35,'현재 자료에서 정확 fan relay ID/cavity는 미확정'),
  pt('AC5','A/C 제어/압력조건','A/C controller/pressure-control input','명령/조건신호 확인','A/C ON','','relay command 자체가 없으면 controller/pressure inhibit 원인으로 이동','OEM_VERIFY',.84,.62),
 ],
 ['전압이 팬 커넥터까지 오면 모터와 GND를 먼저 확정한다.','직접전원 정상인데 vehicle command가 없으면 상류 relay/control로 이동한다.','팬 전기회로를 정상화한 뒤에야 냉매 고압/저압 진단으로 넘어간다.'],
 ['oem_pages/p271.jpg'],
 '팬모터와 제어경로만 표시. 정확 fan relay 번호가 확인되지 않은 상태에서는 “relay #x”를 만들지 않는다.',
 ['SM1018-01 §8-5; SB5120C05 A/C condenser/fan exploded view'],
 ['콘덴서팬 전용 relay ID/cavity 및 A/C controller 숫자핀은 source-limited.'],
 ['AC_CAB','ENGINE_BAY','UNDER_SEAT_RELAY']
)


groups['AC_PRESSURE']=grp(
 'A/C 냉매압력 · 저압/고압 서비스포트', '에어컨',
 '냉각성능 불량은 팬/전원 문제가 아닌 경우 저압·고압을 같은 시험조건에서 동시에 읽어 패턴으로 좁힌다.',
 ['R-134a 매니폴드 게이지','온도계','회전계'],
 ['RECIRC 위치','공기 흡입구 30~35°C','엔진 1,500 rpm','블로워 최대','온도컨트롤 COOL','저압/고압을 동시에 기록'],
 [
  pt('ACL','저압 서비스포트','A/C low-side 서비스포트','매니폴드 저압측 호스','위 표준조건','정상 약 1.5~2.5 bar (21.8~36.3 psi)','진공/낮음/높음 패턴을 고압측과 함께 해석','OEM_EXACT',.34,.56),
  pt('ACH','고압 서비스포트','A/C high-side 서비스포트','매니폴드 고압측 호스','위 표준조건','정상 약 13.7~15.7 bar (198.7~227.7 psi)','저압과 함께 과충전/막힘/응축불량/컴프레서 문제를 분리','OEM_EXACT',.70,.44),
 ],
 ['저압·고압 모두 낮음 → 냉매부족/누설 또는 건조기 흐름제한 패턴을 표와 대조한다.','저압 진공 + 고압 매우 낮음 → 수분/오염 막힘·팽창밸브 쪽 패턴을 대조한다.','저압·고압 모두 매우 높음 → 냉매 과다/콘덴서 방열불량·팬/공기혼입 등으로 분기한다.','팬 미작동이 확인되면 냉매량을 건드리기 전에 AC_COND_FAN 전기진단으로 이동한다.'],
 ['oem_pages/p350.jpg','oem_pages/p351.jpg'],
 '저압/고압 두 서비스포트와 시험조건만 보여주는 정비사용 압력맵.',
 ['SM1018-01 §8-5-3, p8-16~17'],
 ['주변온도에 따라 압력계 지시가 달라질 수 있다고 OEM이 명시. 위 수치는 매뉴얼의 지정 시험조건 기준.'],
 ['AC_CAB','ENGINE_BAY']
)

# Cause-specific test-point selection. This is intentionally diagnostic-first: show only points relevant to the current cause.
expert=json.loads((ROOT/'app/src/main/assets/expert_diag_v2.json').read_text(encoding='utf-8'))
cause_map={}
for it in expert['items']:
    cid=it['id']; sys=it['system']; text=(it.get('cause','')+' '+it.get('symptom',''))
    gid=''; ids=[]
    if sys=='트랜스미션':
        gid='TM_PRESSURE_TAPS'
        symptom=it.get('symptom','')
        if '전진만 작동하고 후진 안 됨' in symptom:
            ids += ['TM5']
        elif '후진만 작동하고 전진 안 됨' in symptom:
            ids += ['TM4']
        else:
            if any(k in it.get('cause','') for k in ['후진','리버스','Reverse','reverse']): ids += ['TM5']
            if any(k in it.get('cause','') for k in ['전진','Forward','forward']): ids += ['TM4']
            if not ids and ('전진/후진' in symptom or '주행' in symptom): ids += ['TM4','TM5']
        if any(k in text for k in ['윤활','베어링','냉각']): ids += ['TM7']
        if any(k in text for k in ['컨버터','쿨러','스톨']): ids += ['TM2','TM3']
        if any(k in text for k in ['펌프','메인','릴리프','인칭','내부 누유','내부누유','모듈','오염','막힘','오일 부족','오일없음']): ids += ['TM6','TM1']
        if not ids: ids=['TM6','TM1']
        # common pressure context before direction-specific interpretation
        if ('TM4' in ids or 'TM5' in ids) and 'TM6' not in ids: ids=['TM6']+ids
    elif sys=='브레이크':
        gid='BRAKE_BLEED_ISOLATION'
        if '공기' in text or '스폰지' in text: ids=['BR3','BR4']
        elif any(k in text for k in ['마스터','서보','릴리프','체크밸브','공급유량','브레이크밸브','브레이크스풀']): ids=['BR1','BR2']
        elif any(k in text for k in ['액슬','피스톤','시일','디스크','제동력','내부 누유','내부누유']): ids=['BR2','BR3','BR4']
        else: ids=['BR1','BR2','BR3','BR4']
    elif sys=='유압':
        gid='HYD_MAIN_RELIEF'
        if '틸트' in text: ids=['HY1','HY2','HY3']
        elif any(k in text for k in ['AUX','보조','사이드']): ids=['HY1','HY2','HY4']
        elif any(k in text for k in ['펌프','릴리프','압력','누출','누유','온도','과부하']): ids=['HY1']
        else: ids=['HY1']
    elif sys=='스티어링':
        gid='STEERING_PRIORITY'
        if any(k in text for k in ['실린더','피스톤','시일','액슬']): ids=['ST1','ST4']
        elif any(k in text for k in ['우선순위','체크밸브','부하감지','LS']): ids=['ST1','ST2','ST3']
        elif any(k in text for k in ['펌프압','펌프','압력 낮']): ids=['ST1','ST3']
        elif any(k in text for k in ['스티어링유닛','밸브스풀','센터']): ids=['ST2','ST3','ST4']
        else: ids=['ST1','ST2','ST4']
    elif sys=='에어컨':
        if cid=='SYM063_C02' or ('컨덴서' in text and '팬' in text): gid='AC_COND_FAN'; ids=['AC1','AC2','AC3','AC4','AC5']
        else: gid='AC_PRESSURE'; ids=['ACL','ACH']
    if gid:
        # stable dedup
        out=[]
        for x in ids:
            if x not in out: out.append(x)
        cause_map[cid]={'group':gid,'point_ids':out}

obj={
 'version':'1.0-v8.4-testpoint',
 'scope':'D20/25/30/33S(SE)-7 D24 Tier-4',
 'rule':'첫 화면에서 부품번호보다 프로브/압력계 연결 위치와 시험조건을 우선. OEM exact / field isolation / OEM VERIFY를 혼합 표시하지 않고 구분한다.',
 'source_classes':{
   'OEM_EXACT':'OEM 매뉴얼에 위치/역할/수치가 직접 확인됨',
   'OEM_PLUS_FIELD':'OEM 위치 + 현장 격리 절차',
   'FIELD_ISOLATION':'현장 회로격리/비교법. OEM 숫자수치로 오인 금지',
   'OEM_VERIFY':'회로 역할은 맞지만 정확 cavity/port ID는 현재 자료에서 미확정',
   'OEM_EXACT_SETTING_PORT_VERIFY':'설정값은 OEM exact, 실제 gauge port는 OEM에서 추가확인 필요',
   'OEM_SCHEMATIC_SETTING_PORT_VERIFY':'회로도 설정값은 확인됨, 시험포트는 미확정',
   'OEM_FUNCTION_EXACT':'OEM 동작원리로 기능/흐름 확인됨',
   'OEM_FUNCTION_PIN_VERIFY':'기능은 OEM 회로로 확인, 숫자핀은 추가검증 필요',
   'FIELD_METHOD':'부하측정/비교 현장법',
   'FIELD_METHOD_OEM_VALUE_VERIFY':'현장법이며 정확 허용공차는 OEM 추가확인',
   'OEM_ID_PLUS_FIELD':'OEM 식별자 + 현장 부하시험'
 },
 'groups':groups,
 'cause_map':cause_map,
 'system_map':{
   '트랜스미션':'TM_PRESSURE_TAPS','브레이크':'BRAKE_BLEED_ISOLATION','유압':'HYD_MAIN_RELIEF','스티어링':'STEERING_PRIORITY','에어컨':'AC_PRESSURE'
 },
 'graph_map':{
   'E_START_NO':'START_VDROP','E_OSS_SEAT_LOCK':'OSS_HEALTH','E_LIFT_LOCK':'OSS_HEALTH','E_AC_COND_FAN_NO':'AC_COND_FAN'
 }
}
OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(OUT)
