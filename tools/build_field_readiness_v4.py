#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v3=json.loads((ROOT/'build/reports/field_readiness_v3.json').read_text(encoding='utf-8'))
eng=json.loads((ROOT/'build/reports/engine_d24_v2_validation.json').read_text(encoding='utf-8'))
edb=json.loads((ROOT/'app/src/main/assets/engine_diag_d24_v2.json').read_text(encoding='utf-8'))
sm=json.loads((ROOT/'app/src/main/assets/engine_sensor_map_d24_v1.json').read_text(encoding='utf-8'))
# Keep V3 strict cause/electrical scores; engine is now separately upgraded.
ca=v3['cause_scope']['counts']; el=v3['electrical_scope']['counts']
eng_oem=sum(1 for x in edb['catalog'] if x.get('readiness')=='OEM_PIN_EXECUTABLE')
eng_field=sum(1 for x in edb['catalog'] if x.get('readiness')=='FIELD_EXECUTABLE')
items=len(sm.get('sensors',[])); numbered=sum(1 for x in sm.get('sensors',[]) if x.get('callout') is not None)
obj={
 'verdict':'NOT_ALL_TARGET_LEVEL',
 'manual_causes':ca,
 'electrical':el,
 'engine':{'benchmark_bundles':21,'graphs':eng['graphs'],'results':eng['results'],'simulations':eng['simulations'],'errors':len(eng['errors']),'warnings':len(eng['warnings']),'oem_pin_executable':eng_oem,'field_executable_source_limited':eng_field},
 'sensor_map':{'items':items,'oem_numbered_callouts':numbered,'geometry':'pseudo-isometric technician locator'},
 'ui_modules':['ElectricalDiagnosticActivity','ExpertDiagnosticActivity','EngineExpertDiagnosticActivity','EngineSensorMapActivity'],
 'release_gate':['268 원인 중 146 partial을 고장전용 측정/도면 수준으로 올릴 것','전장 29 partial의 정확 fuse/relay/connector/pin을 차량 사양별 확정할 것','전장/엔진 위치정보와 테스트포트 위치를 더 연결할 것','Parts Book/부품번호/가격/공임은 별도 검증 DB 필요']
}
(ROOT/'build/reports/field_readiness_v4.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# FIELD READINESS V4 · user benchmark reassessment','',
'## 최종 판정','',
'**아직 전체 앱을 사용자 요구 수준 완료로 판정하지 않는다.** 구조 검증 0-error와 현장 전문가 수준은 다른 기준이다. 이번 V4에서는 D24 엔진 21개 핵심 증상 묶음과 센서 위치맵을 추가했지만, 기존 268개 원인과 전장 일부는 여전히 전용 도면/정확 pin·fuse·동적시험 보강이 필요하다.','',
'## 기존 64증상 / 268원인 · 엄격 재판정','',f'- TARGET_LEVEL: **{ca.get("TARGET_LEVEL",0)}**',f'- FIELD_USABLE_PARTIAL: **{ca.get("FIELD_USABLE_PARTIAL",0)}**','',
'V3의 계통별 엄격점수는 유지한다. 특히 T/M·작업장치·브레이크·스티어링의 반복 템플릿성 도면/측정 위치를 원인별 전용화해야 한다.','',
'## 전장','',f'- 전체 그래프: **{el.get("TARGET_LEVEL",0)+el.get("FIELD_USABLE_PARTIAL",0)}**',f'- TARGET_LEVEL: **{el.get("TARGET_LEVEL",0)}**',f'- FIELD_USABLE_PARTIAL: **{el.get("FIELD_USABLE_PARTIAL",0)}**','',
'`E_START_NO`는 부하 전압강하/START relay input-output/coil command/KEY ST/N-OSS까지 논리는 목표수준으로 재작성했지만, 차량 사양별 정확 relay socket 번호와 fuse cavity가 모두 확정되기 전에는 strict TARGET로 올리지 않는다.','',
'## D24NAP 엔진 V2','',f'- 핵심 증상 묶음: **21 / 21 그래프화**',f'- 결과 종점: **{eng["results"]}**',f'- 결과당 30조건 시뮬레이션: **{eng["simulations"]}**',f'- Validation errors/warnings: **{len(eng["errors"])}/{len(eng["warnings"])}**',f'- OEM pin-level executable: **{eng_oem}**',f'- system-level field executable (일부 정확 수치/핀 source-limited): **{eng_field}**','',
'추가된 엔진 묶음: 냉·열간 hard-start, 작업/주행 중 stall, 저출력, rough idle, 흑연/백연/청연, 과열, 저오일압, 저부스트, 예열, rail 압력 형성, CRK/CAM sync, injector 전기·return·compression 분리.','',
'## D24 센서 위치맵','',f'- 위치 항목: **{items}**',f'- OEM §12-3 numbered callout 직접 연결: **{numbered}**','',
'아이소메트릭은 3D CAD가 아니라 정비사용 pseudo-isometric zone map이다. 센서를 탭하면 위치 설명, sensor connector/ECU pin, OEM 근거, 관련 진단으로 이어지는 구조다. 정확 위치는 OEM callout/engine variant로 최종 확인한다.','',
'## UI 원칙','',
'1. 원본 회로도 전체를 첫 화면에 보여주지 않는다. 고장에 필요한 경로만 재작성한다.','2. 재작성도 아래에 바로 측정점/공구/부하조건을 붙인다.','3. 센서/솔레노이드/테스트포트는 위치맵으로 한 번에 이동한다.','4. 결과에는 rule-out / confirm / teardown gate가 있어야 한다.','5. 정적 continuity나 무부하 12V만으로 배선 정상 판정 금지.','6. OEM 미확인 숫자는 절대로 자동판정값으로 만들지 않는다.','',
'## 아직 release-complete가 아닌 이유','']
for x in obj['release_gate']: lines.append('- '+x)
lines += ['','## 검증 파일','', '- `field_exec_validation.md`: 기존 64/268 실행구조', '- `electrical_validation.md`: 36 전장 그래프 5,760 시뮬레이션', '- `engine_d24_v2_validation.md`: 21 엔진 그래프 3,300 시뮬레이션', '- `FIELD_READINESS_V4.md`: 사용자 기준 엄격 재판정']
(ROOT/'build/reports/FIELD_READINESS_V4.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:35]))
