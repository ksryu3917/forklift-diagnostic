#!/usr/bin/env python3
import json, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'

# ---------- Upgrade start/no-crank graph to loaded-voltage-drop logic ----------
p=A/'electrical_diag_v1.json'
d=json.loads(p.read_text(encoding='utf-8'))
g=d['graphs']['E_START_NO']
g['title']='키 START에서 크랭킹 안 됨 · 부하 전압강하/제어회로 분리'
g['start']='reproduce'
g['nodes']={
'reproduce':{
 'type':'question','title':'1. 불발 순간 재현','question':'현재 증상이 재현된 상태입니까?',
 'field_method':['간헐 고장은 정상일 때 측정해서 판정하지 않는다. 반드시 START 불발 순간의 값을 잡는다.','배터리 포스트·스타터 B+·ST(S)·릴레이 입력/출력을 가능한 한 같은 불발 이벤트에서 비교한다.','점프 후 정상 여부, 신품 배터리 직후 정상 여부, 열간/시간경과 조건을 진단 로그에 남긴다.'],
 'tools':['DMM MIN/MAX 또는 기록 가능한 멀티미터','백프로브','리모트 스타터 스위치(안전 인터록 확보 시)'],
 'choices':[{'label':'불발 상태 재현됨','next':'battery_post'},{'label':'현재 정상','next':'intermittent'}]},
'intermittent':{
 'type':'result','title':'간헐 고장 재현 필요','result':'현재 정상 상태만으로 스타터/배선 정상 판정하지 않습니다.',
 'field_tools':['DMM MIN/MAX','백프로브'],'field_test':['START ST단자와 릴레이 출력에 MIN/MAX를 연결하고 하네스/릴레이박스/키스위치 주변을 구간별로 흔들어 재현한다.','냉간/열간/몇 시간 방치 후 조건을 반복해 불발 순간의 최저전압을 기록한다.'],
 'rule_out':['정상 상태의 무부하 12V만으로 정상 판정','스타터 예방교환'],'confirm_if':['불발 이벤트에서 특정 구간 전압이 동시에 붕괴하는 지점을 확보'],'disassembly_gate':'불발 순간 데이터 확보 전 부품교환 금지.'},
'battery_post':{
 'type':'question','title':'2. 배터리 포스트 START 부하전압','question':'START 불발 순간 배터리 납 포스트 자체 전압은 유지됩니까?',
 'field_method':['클램프가 아니라 배터리 납 포스트에 직접 프로브한다.','START 명령을 주는 동안 배터리 전압이 전체적으로 무너지는지 본다.','OEM 시동 허용 최저전압이 확인되지 않은 경우 임의 숫자로 합격/불합격하지 않고 정상 시동 시 값 및 외부점프 전후를 비교한다.'],
 'tools':['DMM MIN/MAX'],
 'choices':[{'label':'배터리 자체 전압이 크게 무너짐','next':'battery_supply'},{'label':'배터리 포스트는 유지','next':'main_bplus'}]},
'battery_supply':{
 'type':'result','title':'배터리/충전상태 우선','result':'불발 순간 배터리 포스트 자체가 무너집니다. ST 제어회로보다 배터리 SOC/내부상태를 먼저 해결해야 합니다.',
 'field_tools':['배터리 부하테스터','충전기','DMM'],'field_test':['배터리 충전상태와 부하시 전압을 확인한다.','제너레이터 B+ 14V만 보지 말고 알터네이터 B+→배터리+ 및 알터네이터 케이스→배터리- 전압강하도 확인한다.','키 OFF 암전류는 시동 간헐고장과 별개 고장일 수 있으므로 시동회로 복구 후 별도 측정한다.'],
 'rule_out':['ST 릴레이 단독고장 확정','스타터 모터 단독고장 확정'],'confirm_if':['충전/배터리 상태 정상화 후 포스트 전압과 크랭킹이 안정됨'],'disassembly_gate':'배터리/충전 문제를 정상화한 후 START 회로를 재시험.'},
'main_bplus':{
 'type':'question','title':'3. 스타터 B+ 주회로 전압강하','question':'불발 순간 배터리 +포스트→스타터 B+ 볼트 전압강하와 B+ 절대전압이 정상측과 비교해 안정적입니까?',
 'field_method':['한 리드는 배터리 +포스트, 다른 리드는 스타터 B+ 볼트에 둔 채 START를 건다.','메인케이블/터미널/크림프가 고저항이면 START 순간에만 전압차가 커진다.','메인 B+ 수리 이력이 있어도 실제 부하 전압강하로 재확인한다.'],
 'tools':['DMM MIN/MAX','백프로브'],
 'choices':[{'label':'B+ 경로 전압강하 비정상','next':'bplus_fault'},{'label':'B+ 경로 안정','next':'ground_drop'}]},
'bplus_fault':{
 'type':'result','title':'배터리 + 주회로 고저항','result':'배터리 포스트는 유지되지만 스타터 B+까지 부하전압이 전달되지 않습니다.',
 'field_tools':['DMM','부하 시험선'],'field_test':['포스트→클램프→메인케이블→스타터 B+를 구간별 전압강하로 쪼갠다.','크림프 내부부식/단자 열화/체결부 발열을 확인한다.'],
 'rule_out':['ST 제어회로','스타터 솔레노이드 자체'],'confirm_if':['특정 구간 우회/수리 후 B+ 전압강하와 크랭킹이 정상화'],'disassembly_gate':'고저항 구간 특정 후 해당 케이블/단자만 수리.'},
'ground_drop':{
 'type':'question','title':'4. 스타터 접지 부하 전압강하','question':'불발 순간 스타터 하우징→배터리 -포스트 접지 전압강하가 정상측과 비교해 안정적입니까?',
 'field_method':['한 리드는 스타터/엔진 금속 하우징, 다른 리드는 배터리 -포스트에 둔다.','외부점프 (-)를 엔진 블록에 직접 연결했을 때 증상이 변하는지도 보조비교로 기록한다.','추가 접지선을 달았어도 실제 불발 순간 전압강하로 배제해야 한다.'],
 'tools':['DMM MIN/MAX'],
 'choices':[{'label':'접지 경로 전압강하 비정상','next':'ground_fault'},{'label':'B+/GND 둘 다 안정','next':'st_loaded'}]},
'ground_fault':{
 'type':'result','title':'엔진/스타터 접지 고저항','result':'스타터 B+는 정상이나 리턴 접지에서 부하전압이 손실됩니다.',
 'field_tools':['DMM','점프케이블'],'field_test':['배터리-→차체→엔진블록→스타터하우징을 구간별 전압강하로 분리한다.','접지점 도장/부식/크림프/볼트 체결을 확인한다.'],
 'rule_out':['배터리 + 주회로','ST 릴레이 접점'],'confirm_if':['접지 우회 또는 수리 시 즉시 크랭킹 정상화'],'disassembly_gate':'불량 접지 구간만 수리.'},
'st_loaded':{
 'type':'question','title':'5. 스타터 ST(S) 단자 부하전압','question':'불발 순간 스타터 ST(S) 단자 전압은 배터리 포스트 전압과 비교해 유지됩니까?',
 'field_method':['스타터 ST 단자를 백프로브하고 START 명령 중 MIN/MAX를 기록한다.','키 ON 무부하에서 12V가 보이는 것은 정상 판정 근거가 아니다. 솔레노이드 코일이 실제 부하를 거는 순간을 측정한다.'],
 'tools':['DMM MIN/MAX','백프로브'],
 'choices':[{'label':'ST 전압이 불발 순간 떨어짐','next':'relay_contact'},{'label':'ST가 안정적으로 유지되는데 무크랭킹','next':'starter_isolate'}]},
'starter_isolate':{
 'type':'result','title':'스타터/솔레노이드 로컬 문제로 좁힘','result':'B+, GND, ST가 불발 순간에도 모두 유지되는데 크랭킹하지 않습니다.',
 'field_tools':['전류 클램프미터','리모트 스타터','DMM'],'field_test':['안전하게 N/P·주차브레이크·고임목 확보 후 스타터 ST 직접구동 또는 정상 스타터 대체로 재확인한다.','두 개 이상의 정상 스타터 대체에서도 동일하면 기계적 엔진 구속/링기어와 측정 오류를 재확인한다.'],
 'rule_out':['배터리 주회로','ST 제어회로'],'confirm_if':['정상 전원 3축(B+/GND/ST)에서 스타터 자체 작동불량이 직접 재현'],'disassembly_gate':'세 전압축 정상 확인 후에만 스타터/링기어 분해.'},
'relay_contact':{
 'type':'question','title':'6. START 릴레이 입력/출력 동시 비교','question':'불발 순간 START 릴레이의 부하입력(30 기능) 전압은 유지되는데 출력(87 기능)만 떨어집니까?',
 'field_method':['정확한 숫자 단자표가 차량 릴레이에 표시된 경우 30/87을 사용하고, 미확정이면 부하 입력/출력 기능선으로 측정한다.','릴레이 입력과 출력, 스타터 ST를 같은 START 이벤트에서 비교한다.','릴레이를 바꿔도 소켓 암단자 장력/핀 밀림/열변색/크림프 불량은 남을 수 있다.'],
 'tools':['DMM 2채널 또는 순차 MIN/MAX','백프로브','동일 규격 수핀/단자 장력 확인도구'],
 'choices':[{'label':'입력 유지·출력만 붕괴','next':'relay_socket_bad'},{'label':'릴레이 입력부터 붕괴','next':'key_feed'},{'label':'입·출력 유지인데 ST만 붕괴','next':'relay_to_st'}]},
'relay_socket_bad':{
 'type':'result','title':'START 릴레이 접점/소켓 고저항','result':'START 릴레이 부하입력은 유지되지만 부하가 걸리면 출력이 무너집니다.',
 'field_tools':['DMM','점퍼선(퓨즈 포함)','단자 장력 확인도구'],'field_test':['릴레이 교환시험과 별도로 소켓 암단자 장력·핀 밀림·열변색·뒤쪽 크림프를 확인한다.','안전 인터록 확보 후 릴레이 부하입력→출력을 임시 바이패스했을 때 매번 정상 크랭킹하는지 확인한다.'],
 'rule_out':['메인 B+/GND','스타터 모터','릴레이 이전 KEY ST 회로'],'confirm_if':['릴레이/소켓 수리 또는 안전한 바이패스에서 ST 전압과 크랭킹이 즉시 안정화'],'disassembly_gate':'릴레이 접점 또는 소켓 불량이 재현된 뒤 해당 부품만 수리/교환.'},
'relay_to_st':{
 'type':'result','title':'START 릴레이→ST 하네스 고저항','result':'릴레이 출력은 정상인데 스타터 ST에서만 부하전압이 사라집니다.',
 'field_tools':['DMM','백프로브'],'field_test':['릴레이 출력→중간커넥터→스타터 ST를 절반분할 방식으로 백프로브해 마지막 정상/첫 이상 지점을 찾는다.','정적 Ω값뿐 아니라 START 부하전압강하와 흔들림시험을 사용한다.'],
 'rule_out':['릴레이 접점','스타터 자체'],'confirm_if':['특정 하네스/커넥터 전단 정상·후단 전압붕괴 반복 재현'],'disassembly_gate':'고장구간 특정 후 해당 단자/하네스만 수리.'},
'key_feed':{
 'type':'question','title':'7. 릴레이 코일명령 vs 부하전원 분리','question':'불발 순간 릴레이 코일 START 명령도 같이 떨어집니까?',
 'field_method':['릴레이 부하접점과 코일제어를 구분한다.','코일명령이 유지되는데 부하입력만 떨어지면 퓨즈박스/전원버스 상류를 추적한다.','코일명령 자체가 떨어지면 KEY ST·중립/OSS 인터록·제어배선으로 이동한다.'],
 'tools':['DMM','백프로브'],
 'choices':[{'label':'코일 START 명령도 떨어짐','next':'key_interlock'},{'label':'코일명령 유지·부하전원만 저하','next':'relay_feed_bad'}]},
'relay_feed_bad':{
 'type':'result','title':'START 릴레이 부하전원 상류 고저항','result':'릴레이 제어명령은 유지되지만 릴레이 부하입력 전원이 START 순간 무너집니다.',
 'field_tools':['DMM'],'field_test':['START fuse/회로차단기/퓨즈박스 내부 버스와 릴레이 입력 사이를 구간별 부하전압강하로 확인한다.'],
 'rule_out':['KEY ST/인터록 제어','스타터 모터'],'confirm_if':['상류 특정 접점 수리 후 릴레이 입력과 ST가 동시에 안정화'],'disassembly_gate':'전압손실 구간 특정 후 퓨즈박스/단자 수리.'},
'key_interlock':{
 'type':'question','title':'8. KEY ST 출력과 인터록 입력 분리','question':'불발 순간 KEY SW의 ST 출력은 유지되는데 릴레이 코일명령만 사라집니까?',
 'field_method':['KEY SW 입력 B+와 ST 출력을 START 중 동시에 비교한다.','KEY ST가 유지되는데 릴레이 코일로 전달되지 않으면 중립스위치/OSS/하네스 인터록 경로를 확인한다.','KEY SW 입력은 유지되고 ST 출력만 무너지면 KEY SW ST 접점 고저항 가능성이 높다.'],
 'tools':['DMM MIN/MAX','백프로브','회로도'],
 'choices':[{'label':'KEY 입력 정상·ST 출력만 붕괴','next':'key_bad'},{'label':'KEY ST 유지·릴레이 명령 소실','next':'interlock_bad'},{'label':'KEY 입력 자체 붕괴','next':'key_supply_bad'}]},
'key_bad':{
 'type':'result','title':'KEY SW ST 접점 고저항/간헐','result':'KEY SW 입력전원은 유지되나 START 출력만 부하/간헐 조건에서 무너집니다.',
 'field_tools':['DMM','백프로브'],'field_test':['KEY B+와 ST 출력 간 전압강하를 START 중 측정한다.','키를 미세하게 움직였을 때 출력이 변하는지 재현한다.'],
 'rule_out':['스타터/릴레이 부하접점','메인 배터리케이블'],'confirm_if':['키스위치 교환/접점수리 후 ST 출력과 크랭킹 안정화'],'disassembly_gate':'KEY 입력 정상·ST 출력 불량 반복 확인 후 교환.'},
'interlock_bad':{
 'type':'result','title':'START 인터록/OSS/중립 회로 간헐','result':'KEY ST는 정상이나 START 릴레이 코일 명령이 인터록 구간에서 소실됩니다.',
 'field_tools':['진단기','DMM','백프로브'],'field_test':['중립/방향레버 입력, OSS start permit, 관련 스위치 입력을 live data와 실제 핀에서 비교한다.','센서 입력이 정상인데 허가출력이 없으면 컨트롤러 전원/GND/CAN 생존성까지 확인한다.'],
 'rule_out':['KEY SW ST 접점','릴레이 부하접점','스타터 모터'],'confirm_if':['특정 인터록 입력/출력 복구 시 릴레이 코일명령과 크랭킹이 동시에 정상화'],'disassembly_gate':'인터록의 입력·컨트롤러 생존·출력 중 끊긴 구간 특정 후 해당 부품만 수리.'},
'key_supply_bad':{
 'type':'result','title':'KEY SW 입력 상류 전원 고저항','result':'START 순간 KEY SW 입력전원 자체가 붕괴합니다.',
 'field_tools':['DMM'],'field_test':['배터리→회로차단기/퓨즈→KEY B+ 입력을 부하전압강하로 역추적한다.'],
 'rule_out':['KEY 내부 ST 접점 단독고장','스타터 모터'],'confirm_if':['상류 전원 접점 수리 후 KEY 입력 및 ST 출력 동시 안정화'],'disassembly_gate':'상류 전압손실 위치 특정 후 수리.'}
}
# Upgrade circuit diagram measure points for start
c=d['circuits']['START']
c['known_standard']='12V system. START failure must be diagnosed under actual solenoid/starter load; unloaded voltage is not sufficient.'
c['simplified_diagram']={
 'title':'무크랭킹 · 필요한 회로와 부하측정점만',
 'nodes':[
  {'id':'bat','label':'BAT +POST\nMP1','kind':'source','verified':True},
  {'id':'main','label':'MAIN B+\nMP2 drop','kind':'power','verified':True},
  {'id':'key','label':'KEY SW\nB+ / ST','kind':'switch','verified':True},
  {'id':'permit','label':'N/OSS START\npermit','kind':'control','verified':True},
  {'id':'relay','label':'START RELAY\nIN / OUT / COIL','kind':'relay','verified':True},
  {'id':'st','label':'STARTER ST(S)\nMP5','kind':'control','verified':True},
  {'id':'starter','label':'STARTER B+\nMOTOR','kind':'load','verified':True},
  {'id':'gnd','label':'CASE → BAT-\nMP6 drop','kind':'ground','verified':True}],
 'edges':[{'from':'bat','to':'main'},{'from':'main','to':'starter'},{'from':'bat','to':'key'},{'from':'key','to':'permit'},{'from':'permit','to':'relay'},{'from':'relay','to':'st'},{'from':'st','to':'starter'},{'from':'starter','to':'gnd'}],
 'measure_points':['MP1 배터리 납 포스트 START 전압','MP2 배터리+ → 스타터 B+ 부하 전압강하','MP3 KEY B+와 ST 출력 동시 비교','MP4 START RELAY 부하입력/출력 + 코일명령 분리','MP5 스타터 ST(S) 불발 순간 MIN/MAX','MP6 스타터 케이스 → 배터리- 부하 전압강하'],
 'note':'불발 순간 측정이 핵심. 정상상태 무부하 12V나 정적 도통만으로 회로 정상 판정 금지.'}

# ---------- D24 engine sensor/location map ----------
sensors={
 'EGTS': {'callout':1,'name':'Exhaust Gas Temperature Sensor','kr':'배기가스 온도센서','zone':'exhaust','location':'터보차저 배기측/배기가스 경로','oem_ref':'D24 §12-3 callout 1 / §12-11','pins':'2핀; ECU169 GND / ECU194 temperature signal'},
 'CAM': {'callout':2,'name':'Cam Shaft Position Sensor','kr':'캠축 위치센서','zone':'timing_top','location':'실린더헤드/캠 기준 위치, 타이밍기어 측 상부','oem_ref':'D24 §12-3 callout 2 / §12-14','pins':'sensor pin2→ECU159 signal, pin3→ECU147 GND; supply 12V (manual table layout must be rechecked before numeric connector-face rendering)'},
 'CRK': {'callout':3,'name':'Crank Shaft Position Sensor','kr':'크랭크축 위치센서','zone':'timing_low','location':'크랭크/타이밍기어 측 하부','oem_ref':'D24 §12-3 callout 3 / §12-14','pins':'ECU136 CRS NEG / ECU160 CRS POS / ECU187 shield'},
 'EGR': {'callout':4,'name':'EGR Valve Position Sensor','kr':'EGR 위치센서','zone':'egr','location':'EGR 밸브 어셈블리','oem_ref':'D24 §12-3 callout 4 / §12-15','pins':'VREF3/position/GND + H-bridge control; exact connector-face map from §12-15'},
 'WTS': {'callout':5,'name':'Water Temperature Sensor','kr':'냉각수 온도센서','zone':'coolant','location':'엔진 냉각수 통로/서모스탯 계통','oem_ref':'D24 §12-3 callout 5 / §12-12','pins':'pin1→ECU145 GND, pin2→ECU109 temperature signal; 20°C 2.5kΩ, 110°C 0.148kΩ in specifications'},
 'BTS': {'callout':6,'name':'Boost Temperature Sensor','kr':'부스트/흡기온도센서','zone':'intake','location':'흡기 매니폴드/부스트 공기 통로','oem_ref':'D24 §12-3 callout 6 / §12-11','pins':'pin1→ECU123 GND, pin2→ECU106 temperature signal'},
 'FTS': {'callout':7,'name':'Fuel Temperature Sensor','kr':'연료 온도센서','zone':'pump','location':'고압 연료펌프','oem_ref':'D24 §12-3 callout 7 / §12-12','pins':'pin1→ECU110 temperature signal, pin2→ECU146 GND'},
 'IMV': {'callout':8,'name':'Inlet Metering Valve','kr':'연료 계량밸브(IMV)','zone':'pump','location':'고압 연료펌프 입구 계량부','oem_ref':'D24 §12-3 callout 8 / §12-15','pins':'PWM control ECU177 (manual circuit table)'},
 'OPTS': {'callout':9,'name':'Oil Pressure and Temperature Sensor','kr':'오일 압력/온도센서','zone':'block','location':'엔진 블록 오일 갤러리/윤활계통','oem_ref':'D24 §12-3 callout 9 / §12-12','pins':'pin1→ECU148 GND, pin2→ECU104 temp, pin3→ECU165 5V, pin4→ECU111 pressure'},
 'KNOCK': {'callout':10,'name':'Knock Sensor','kr':'노크센서','zone':'block','location':'실린더 블록 측면','oem_ref':'D24 §12-3 callout 10 / §12-14~15','pins':'piezo sensor; exact #1/#2 pins per §12-14~15'},
 'BPS': {'callout':11,'name':'Boost Pressure Sensor','kr':'부스트 압력센서','zone':'intake','location':'흡기 매니폴드','oem_ref':'D24 §12-3 callout 11 / §12-11','pins':'pin1→ECU161 5V, pin2→ECU167 GND, pin3→ECU112 pressure'},
 'RPS': {'callout':12,'name':'Rail Pressure Sensor','kr':'레일압력센서','zone':'rail','location':'커먼레일 끝단','oem_ref':'D24 §12-3 callout 12 / §12-12','pins':'pin1→ECU135 pressure, pin2→ECU119 GND, pin3→ECU138 5V'},
 'INJ4': {'callout':13,'name':'Injector #4','kr':'4번 인젝터','zone':'top','location':'실린더헤드 상부 #4','oem_ref':'D24 §12-3 callout 13 / §12-13','pins':'ECU125 low side / ECU103 high side'},
 'INJ3': {'callout':14,'name':'Injector #3','kr':'3번 인젝터','zone':'top','location':'실린더헤드 상부 #3','oem_ref':'D24 §12-3 callout 14 / §12-13','pins':'ECU175 low side / ECU151 high side'},
 'INJ2': {'callout':15,'name':'Injector #2','kr':'2번 인젝터','zone':'top','location':'실린더헤드 상부 #2','oem_ref':'D24 §12-3 callout 15 / §12-13','pins':'ECU174 low side / ECU150 high side'},
 'INJ1': {'callout':16,'name':'Injector #1','kr':'1번 인젝터','zone':'top','location':'실린더헤드 상부 #1','oem_ref':'D24 §12-3 callout 16 / §12-13','pins':'ECU126 low side / ECU127 high side'},
 'MAF': {'callout':None,'name':'Mass Air Flow Sensor','kr':'흡입공기유량/온도센서(MAF)','zone':'air_inlet','location':'에어클리너 이후 초기 흡기 덕트','oem_ref':'D24 §12-11','pins':'pin1→ECU228 flow frequency, pin2→ECU235 intake temp, pin3→ECU120 GND, pin4→ECU137 12V'},
 'WIFS': {'callout':None,'name':'Water In Fuel Sensor','kr':'연료 수분센서','zone':'fuel_filter','location':'연료필터/수분분리기','oem_ref':'D24 §12-16','pins':'connector pin map from §12-16; do not invent if raster unavailable'}
}
mapdata={
 'version':'1.0-d24-field-location','engine':'D24NAP','manual':'950106-01198','source_pages':['3-14~3-29 outside/isometric drawings','12-3 electric parts','12-11~12-16 switches and sensors'],
 'display_rule':'앱 기본 화면은 OEM 원본 복사가 아니라 엔진 zone+센서 callout을 재작성. 정확 위치 확인 버튼에서 OEM §12-3/외형도를 연다.',
 'views':[
  {'id':'iso','title':'아이소메트릭 빠른 위치','zones':[{'id':'rail','label':'커먼레일/상부','x':0.57,'y':0.24},{'id':'top','label':'인젝터 상부','x':0.50,'y':0.18},{'id':'intake','label':'흡기매니폴드','x':0.68,'y':0.40},{'id':'air_inlet','label':'흡기덕트','x':0.84,'y':0.25},{'id':'exhaust','label':'터보/배기','x':0.22,'y':0.32},{'id':'egr','label':'EGR','x':0.28,'y':0.23},{'id':'pump','label':'고압펌프','x':0.67,'y':0.58},{'id':'coolant','label':'냉각수/서모스탯','x':0.38,'y':0.34},{'id':'timing_top','label':'타이밍 상부','x':0.38,'y':0.20},{'id':'timing_low','label':'크랭크/타이밍 하부','x':0.34,'y':0.65},{'id':'block','label':'실린더블록 측면','x':0.47,'y':0.56},{'id':'fuel_filter','label':'연료필터 외부','x':0.86,'y':0.66}]}
 ],
 'sensors':[{'id':k,**v} for k,v in sensors.items()],
 'accuracy':{'zone_geometry':'APP_REDRAW_NOT_DIMENSIONAL','callout_1_16':'OEM §12-3 NUMBERED','connector_pins':'OEM text/table where recorded','warning':'장착 사양(DL02-...)에 따라 외형 배치가 다를 수 있으므로 차량 엔진 코드/사양을 선택한 후 표시'}
}
(A/'engine_sensor_map_d24_v1.json').write_text(json.dumps(mapdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# source registry update
sp=A/'source_registry_v1.json'; s=json.loads(sp.read_text(encoding='utf-8'))
for src in s['sources']:
 if src['name'].startswith('Doosan D24NAP Operation'):
  src['status']='INGESTED_PARTIAL_ENGINE_EXPERT'
  src['use']='D24 sensor/ECU pin tables, Electric Parts callout map, outside/isometric drawings, cooling/lube/fuel/intake-exhaust failure diagnosis; engine symptom graph expansion target'
  src['reference']='950106-01198; public cross-check via ManualsLib/PDFCoffee/servicemanualdownload mirror'
# update schematic status count
a=[x for x in s['sources'] if x['name'].startswith('600123-00120')]
if a:a[0]['use']='36 executable electrical symptom graphs + redrawn circuits; exact unverified pins/cavities remain UNKNOWN'
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Add sensor map metadata to D24 circuits/graphs
for cid in ['D24_RPS','D24_BPS','D24_WTS','D24_MAF','D24_VREF','D24_ECU_HEALTH','D24_CRANK_NO_START']:
 if cid in d.get('circuits',{}): d['circuits'][cid]['engine_sensor_map']='engine_sensor_map_d24_v1.json'
for gid in list(d['graphs']):
 if gid.startswith('E_D24'):
  d['graphs'][gid]['engine_sensor_map']='engine_sensor_map_d24_v1.json'

d['version']='1.6-rc-expert-v6'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated',p)
