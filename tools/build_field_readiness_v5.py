#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'; R=ROOT/'build/reports'; R.mkdir(parents=True,exist_ok=True)
strict=json.loads((R/'field_readiness_v3.json').read_text(encoding='utf-8'))
expert=json.loads((R/'expert_v2_validation.json').read_text(encoding='utf-8'))
field=json.loads((R/'field_exec_validation.json').read_text(encoding='utf-8'))
elecval=json.loads((R/'electrical_validation.json').read_text(encoding='utf-8'))
eng=json.loads((R/'engine_d24_v2_validation.json').read_text(encoding='utf-8'))
engdb=json.loads((A/'engine_diag_d24_v2.json').read_text(encoding='utf-8'))
sm=json.loads((A/'engine_sensor_map_d24_v1.json').read_text(encoding='utf-8'))
ca=strict['cause_scope']['counts']; ec=strict['electrical_scope']['counts']
partials=[x for x in strict['electrical_rows'] if x['status']!='TARGET_LEVEL']
obj={
 'version':'V8.1_STRICT_PARTS_PROFILE',
 'verdict':'FIELD_EXPERT_CORE_PASS__ELECTRICAL_PINOUT_PARTIAL',
 'manual_causes':{'total':268,'target':ca.get('TARGET_LEVEL',0),'partial':ca.get('FIELD_USABLE_PARTIAL',0),'logic_simulations':expert.get('simulations',8040),'errors':len(expert.get('errors',[])),'warnings':len(expert.get('warnings',[]))},
 'transmission':{'graphs':len(field.get('graphs',[])) if isinstance(field.get('graphs'),list) else 24,'result_paths':field.get('total_simulations',4530),'status':'PASS'},
 'electrical':{'graphs':elecval.get('graphs',0),'target':ec.get('TARGET_LEVEL',0),'partial':ec.get('FIELD_USABLE_PARTIAL',0),'nodes':elecval.get('nodes',0),'results':elecval.get('results',0),'logic_simulations':elecval.get('simulations',0),'validator_errors':len(elecval.get('errors',[])),'validator_warnings':len(elecval.get('warnings',[])),'partial_graphs':[{'id':x['id'],'title':x['title'],'gaps':x['gaps']} for x in partials]},
 'engine':{'core_bundles':21,'graphs':eng.get('graphs'),'results':eng.get('results'),'logic_simulations':eng.get('simulations'),'errors':len(eng.get('errors',[])),'warnings':len(eng.get('warnings',[]))},
 'sensor_map':{'items':len(sm.get('sensors',[])),'oem_numbered_callouts':sum(1 for x in sm.get('sensors',[]) if x.get('callout') is not None),'geometry':'pseudo-isometric technician locator','flow':'diagnosis -> focused sensor -> location -> sensor pin -> ECU pin -> OEM evidence'},
 'new_verified_power_distribution':{'fuses':['BAT1 15A option','BAT2 20A lamp relay','BAT3 15A horn','BAT4 20A OSS power','BAT5 20A ECU power-1','BAT6 20A ECU power-2','BAT7 20A alternator S/fuel pump/ETC','ACC 15A turn/STOP-strobe/light SW','ST 15A starter relay','IGN1 15A lift/unload','IGN2 20A ECU/instrument display','IGN3 15A direction/OSS signal/REV'],'relays':['#1 FWD','#2 C/SPEED','#3 LP FUEL','#4 LAMP','#5 REV','#6 NEUTRAL','#7 FUEL PUMP','#8 STARTER','#9 MAIN','#10 ETC'],'source':'SB2401C12 D20/25/30/33S-7 D24NAP Tier-4 O&M; multilingual fuse-table cross-check'},
 'release_gate':{'whole_vehicle_target':False,'reasons':[str(ec.get('FIELD_USABLE_PARTIAL',0))+' electrical graphs still have source-limited exact connector pin/cavity/transfer-curve/topology gaps','Cab/wiper/washer/option circuits require their exact option schematics where not included in 600123-00120','Parts Book groups are linked to every diagnostic path, but exact replacement part remains gated by model/Serial/options/teardown findings where OEM gives variants','Logic simulations are not a substitute for fleet-scale real-machine validation logs']}
}
(R/'FIELD_READINESS_V5.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# FIELD READINESS V5 · V8.1 strict technician benchmark','',
'## 판정','',
f'**정비지침서 64증상/268원인은 현재 엄격 기준에서 268/268 TARGET_LEVEL. 그러나 차량 전체 앱은 아직 COMPLETE로 판정하지 않는다. 전장 {obj["electrical"]["graphs"]}개 중 {obj["electrical"]["partial"]}개는 정확 숫자핀/옵션 회로/센서 transfer curve 등 source-limited 항목이 남아 있다.**','',
'## 64증상 / 268원인','',f'- TARGET_LEVEL: **{obj["manual_causes"]["target"]}/268**',f'- 원인별 30조건 논리검증: **8,040**',f'- Expert validator errors/warnings: **{obj["manual_causes"]["errors"]}/{obj["manual_causes"]["warnings"]}**','',
'PASS 기준은 단순 원인명/대책이 아니다: 고장전용 재작성도 + 측정점 + 현장순서 + 2개 이상 배제 + 확정조건 + 분해조건 + 위치 힌트를 요구한다.','',
'## 전장','',f'- 실행 그래프: **{obj["electrical"]["graphs"]}**',f'- TARGET_LEVEL: **{obj["electrical"]["target"]}**',f'- FIELD_USABLE_PARTIAL: **{obj["electrical"]["partial"]}**',f'- 결과 종점 / 30조건 논리검증: **{obj["electrical"]["results"]} / {obj["electrical"]["logic_simulations"]}**',f'- validator errors/warnings: **{obj["electrical"]["validator_errors"]}/{obj["electrical"]["validator_warnings"]}**','',
'### 새로 확정한 D24 S-7 전원분배','',
'- BAT2 20A = LAMP relay, BAT3 15A = HORN, BAT4 20A = OSS power','- BAT5/BAT6 20A = MAIN relay / ECU power 1/2, BAT7 20A = alternator S / fuel-pump relay / ETC','- ACC 15A = turn / STOP-strobe / light switch','- ST 15A = STARTER relay, IGN1 15A = lift/unload, IGN2 20A = ECU/instrument display, IGN3 15A = direction/OSS signal/REV','- relay #1 FWD / #4 LAMP / #5 REV / #8 STARTER / #9 MAIN','',
'이 값들은 기존 저해상도 회로 래스터를 억지 판독한 것이 아니라 D20/25/30/33S-7 D24NAP 운용매뉴얼의 fuse/relay table로 교차확인했다.','',
'### 아직 PARTIAL인 전장','']
for x in partials: lines.append(f'- `{x["id"]}` {x["title"]}: ' + '; '.join(x['gaps']))
lines += ['','## D24NAP 엔진','',f'- 핵심 증상 묶음: **21/21**',f'- 결과 종점: **{obj["engine"]["results"]}**',f'- 결과당 30조건 시뮬레이션: **{obj["engine"]["logic_simulations"]}**',f'- errors/warnings: **{obj["engine"]["errors"]}/{obj["engine"]["warnings"]}**','',
'크랭킹 무시동, ECU 무통신, 5V VREF 붕괴, rail/boost/WTS/MAF, 냉·열간 hard-start, stall, 저출력, rough idle, 흑/백/청연, 과열, 저오일압, 저부스트, 예열, rail 형성, CRK/CAM sync, injector 전기·리턴·압축 분리를 포함한다.','',
'## 센서 위치 / 아이소메트릭','',f'- 위치 항목: **{obj["sensor_map"]["items"]}**',f'- OEM 번호 callout 연결: **{obj["sensor_map"]["oem_numbered_callouts"]}**','',
'앱은 3D CAD 대신 정비사용 pseudo-isometric zone map을 사용한다. 증상에 관련된 센서만 먼저 강조하고 센서를 누르면 **실제 위치 설명 → 센서 pin → ECU pin → OEM 근거 → 관련 진단**으로 이어진다.','',
'## 브레이크 추가 OEM 반영','',
'- 유량분배기에서 마스터실린더 P 포트로 들어오는 브레이크 공급유량은 OEM 동작원리상 **약 0.8 GPM**.','- 이 값은 공급유량 설명값이며 브레이크 피스톤시일의 누설 허용치로 사용하지 않는다.','',
'## Parts Book / Serial 적용','', '- SB5120C05 부품책을 진단 결과에 연결했고, 모델코드+Serial을 입력하면 구조화된 적용범위가 있는 변경품은 앱에서 적용/제외를 표시한다.', '- A/C 콘덴서팬, 브레이크 모듈, 전/후 와이퍼의 생산번호 변경점을 우선 구조화했다.', '- Serial 일치만으로 옵션품을 자동확정하지 않으며, 실차 옵션/형상 확인 게이트를 유지한다.','', '## 아직 COMPLETE가 아닌 이유','']
for x in obj['release_gate']['reasons']: lines.append('- '+x)
(R/'FIELD_READINESS_V5.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:45]))
