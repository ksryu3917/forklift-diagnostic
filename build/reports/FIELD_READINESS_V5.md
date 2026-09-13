# FIELD READINESS V5 · V8.1 strict technician benchmark

## 판정

**정비지침서 64증상/268원인은 현재 엄격 기준에서 268/268 TARGET_LEVEL. 그러나 차량 전체 앱은 아직 COMPLETE로 판정하지 않는다. 전장 38개 중 21개는 정확 숫자핀/옵션 회로/센서 transfer curve 등 source-limited 항목이 남아 있다.**

## 64증상 / 268원인

- TARGET_LEVEL: **268/268**
- 원인별 30조건 논리검증: **8,040**
- Expert validator errors/warnings: **0/0**

PASS 기준은 단순 원인명/대책이 아니다: 고장전용 재작성도 + 측정점 + 현장순서 + 2개 이상 배제 + 확정조건 + 분해조건 + 위치 힌트를 요구한다.

## 전장

- 실행 그래프: **38**
- TARGET_LEVEL: **17**
- FIELD_USABLE_PARTIAL: **21**
- 결과 종점 / 30조건 논리검증: **205 / 6150**
- validator errors/warnings: **0/0**

### 새로 확정한 D24 S-7 전원분배

- BAT2 20A = LAMP relay, BAT3 15A = HORN, BAT4 20A = OSS power
- BAT5/BAT6 20A = MAIN relay / ECU power 1/2, BAT7 20A = alternator S / fuel-pump relay / ETC
- ACC 15A = turn / STOP-strobe / light switch
- ST 15A = STARTER relay, IGN1 15A = lift/unload, IGN2 20A = ECU/instrument display, IGN3 15A = direction/OSS signal/REV
- relay #1 FWD / #4 LAMP / #5 REV / #8 STARTER / #9 MAIN

이 값들은 기존 저해상도 회로 래스터를 억지 판독한 것이 아니라 D20/25/30/33S-7 D24NAP 운용매뉴얼의 fuse/relay table로 교차확인했다.

### 아직 PARTIAL인 전장

- `E_STOP_NO` 브레이크등 미점등 · 현장 전기진단: 정확 pin/fuse/cavity 일부 미확정
- `E_STOP_ON` 브레이크등 상시점등 · 현장 전기진단: 정확 pin/fuse/cavity 일부 미확정
- `E_HEAD_NO` 헤드램프가 안 들어옴 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_TURN_NO` 방향지시등/비상등이 작동하지 않음 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_PARK_INPUT` 주차브레이크 전기 신호 이상 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_GAUGE` 연료/수온/TM온도 계기 이상 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_WORK_LAMP` 리어램프/스트로브/작업등 불량 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_OSS_SEAT_LOCK` 시트/OSS 인터록이 풀리지 않음 · 센서/5V/CAN/간헐 통합진단: 정확 pin/fuse/cavity 일부 미확정
- `E_AC_POWER_NO` 에어컨 전원 자체가 켜지지 않음 · 전원/컨트롤러/블로워 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_AC_COND_FAN_NO` A/C는 작동하는데 컨덴서 팬이 안 돎 · 팬회로 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_PREHEAT_NO` 예열/글로우 작동 안 됨 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_FUEL_HEATER_NO` 연료히터 작동 안 됨 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_BRAKE_OIL_WARN` 브레이크오일 경고 입력 이상 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_CLUSTER_POWER_NO` 계기판/모니터 전원 안 켜짐 · 회로 추적: 정확 pin/fuse/cavity 일부 미확정
- `E_CAN_NETWORK` 진단기 통신/CAN 이상 · 노드 전원/배선/컨트롤러 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_HOURMETER_NO` 아워미터가 작동/적산하지 않음 · 현장 회로추적: 정확 pin/fuse/cavity 일부 미확정
- `E_WATER_GAUGE` 수온 게이지만 비정상 · 센서/표시 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_TM_TEMP_GAUGE` T/M 오일온도 게이지만 비정상 · 센서/표시 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_FUEL_GAUGE_ONLY` 연료 게이지만 비정상 · 센서/표시 분리진단: 정확 pin/fuse/cavity 일부 미확정
- `E_WIPER_NO` 전/후 와이퍼가 작동하지 않음 · 부하전압/모터/명령 분리: 정확 pin/fuse/cavity 일부 미확정
- `E_WASHER_NO` 와셔액이 분사되지 않음 · 유로/펌프전원/스위치 분리: 정확 pin/fuse/cavity 일부 미확정

## D24NAP 엔진

- 핵심 증상 묶음: **21/21**
- 결과 종점: **110**
- 결과당 30조건 시뮬레이션: **3300**
- errors/warnings: **0/0**

크랭킹 무시동, ECU 무통신, 5V VREF 붕괴, rail/boost/WTS/MAF, 냉·열간 hard-start, stall, 저출력, rough idle, 흑/백/청연, 과열, 저오일압, 저부스트, 예열, rail 형성, CRK/CAM sync, injector 전기·리턴·압축 분리를 포함한다.

## 센서 위치 / 아이소메트릭

- 위치 항목: **18**
- OEM 번호 callout 연결: **16**

앱은 3D CAD 대신 정비사용 pseudo-isometric zone map을 사용한다. 증상에 관련된 센서만 먼저 강조하고 센서를 누르면 **실제 위치 설명 → 센서 pin → ECU pin → OEM 근거 → 관련 진단**으로 이어진다.

## 브레이크 추가 OEM 반영

- 유량분배기에서 마스터실린더 P 포트로 들어오는 브레이크 공급유량은 OEM 동작원리상 **약 0.8 GPM**.
- 이 값은 공급유량 설명값이며 브레이크 피스톤시일의 누설 허용치로 사용하지 않는다.

## Parts Book / Serial 적용

- SB5120C05 부품책을 진단 결과에 연결했고, 모델코드+Serial을 입력하면 구조화된 적용범위가 있는 변경품은 앱에서 적용/제외를 표시한다.
- A/C 콘덴서팬, 브레이크 모듈, 전/후 와이퍼의 생산번호 변경점을 우선 구조화했다.
- Serial 일치만으로 옵션품을 자동확정하지 않으며, 실차 옵션/형상 확인 게이트를 유지한다.

## 아직 COMPLETE가 아닌 이유

- 21 electrical graphs still have source-limited exact connector pin/cavity/transfer-curve/topology gaps
- Cab/wiper/washer/option circuits require their exact option schematics where not included in 600123-00120
- Parts Book groups are linked to every diagnostic path, but exact replacement part remains gated by model/Serial/options/teardown findings where OEM gives variants
- Logic simulations are not a substitute for fleet-scale real-machine validation logs
