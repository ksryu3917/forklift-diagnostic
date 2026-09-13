# FIELD READINESS V3 · strict reassessment

## 결론

**현재 앱은 전체 항목이 사용자 요구 수준에 도달했다고 판정할 수 없다.** 기존 validator는 연결/필드 존재를 잘 검사하지만, 이번 V3는 고장별 재작성도면의 전용성·실제 측정점·동적/부하시험·엔진 증상 universe·센서 위치 접근성까지 별도로 본다.

## 64증상 / 268원인 재판정

- TARGET_LEVEL: **268**
- FIELD_USABLE_PARTIAL: **0**
- INSUFFICIENT: **0**

| 계통 | TARGET | PARTIAL | INSUFFICIENT |
|---|---:|---:|---:|
| 드라이브 액슬 | 20 | 0 | 0 |
| 마스트 | 8 | 0 | 0 |
| 브레이크 | 45 | 0 | 0 |
| 스티어링 | 38 | 0 | 0 |
| 에어컨 | 9 | 0 | 0 |
| 유압 | 27 | 0 | 0 |
| 작업장치 | 26 | 0 | 0 |
| 주차 브레이크 | 3 | 0 | 0 |
| 트랜스미션 | 92 | 0 | 0 |

## 전장 실행 그래프 재판정

- 전체: **38**
- TARGET_LEVEL: **17**
- FIELD_USABLE_PARTIAL: **21**
- INSUFFICIENT: **0**

- **E_STOP_NO** · 브레이크등 미점등 · 현장 전기진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_STOP_ON** · 브레이크등 상시점등 · 현장 전기진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_HEAD_NO** · 헤드램프가 안 들어옴 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_TURN_NO** · 방향지시등/비상등이 작동하지 않음 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_PARK_INPUT** · 주차브레이크 전기 신호 이상 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_GAUGE** · 연료/수온/TM온도 계기 이상 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_WORK_LAMP** · 리어램프/스트로브/작업등 불량 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_OSS_SEAT_LOCK** · 시트/OSS 인터록이 풀리지 않음 · 센서/5V/CAN/간헐 통합진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_AC_POWER_NO** · 에어컨 전원 자체가 켜지지 않음 · 전원/컨트롤러/블로워 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_AC_COND_FAN_NO** · A/C는 작동하는데 컨덴서 팬이 안 돎 · 팬회로 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_PREHEAT_NO** · 예열/글로우 작동 안 됨 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_FUEL_HEATER_NO** · 연료히터 작동 안 됨 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_BRAKE_OIL_WARN** · 브레이크오일 경고 입력 이상 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_CLUSTER_POWER_NO** · 계기판/모니터 전원 안 켜짐 · 회로 추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_CAN_NETWORK** · 진단기 통신/CAN 이상 · 노드 전원/배선/컨트롤러 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_HOURMETER_NO** · 아워미터가 작동/적산하지 않음 · 현장 회로추적 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_WATER_GAUGE** · 수온 게이지만 비정상 · 센서/표시 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_TM_TEMP_GAUGE** · T/M 오일온도 게이지만 비정상 · 센서/표시 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_FUEL_GAUGE_ONLY** · 연료 게이지만 비정상 · 센서/표시 분리진단 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_WIPER_NO** · 전/후 와이퍼가 작동하지 않음 · 부하전압/모터/명령 분리 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정
- **E_WASHER_NO** · 와셔액이 분사되지 않음 · 유로/펌프전원/스위치 분리 → FIELD_USABLE_PARTIAL: 정확 pin/fuse/cavity 일부 미확정

## D24NAP 엔진 커버리지

- 기준 증상/진단 묶음: **21**
- 현재 그래프 보유: **21**
- 아직 GAP: **0**

- ✅ 크랭킹 무시동 → `E_D24_CRANK_NO_START`
- ✅ ECU 무통신 → `E_D24_ECU_NO_COMM`
- ✅ 5V 기준전압 붕괴 → `E_D24_5V_REF`
- ✅ 레일압 센서/회로 → `E_D24_RAIL_PRESSURE`
- ✅ 부스트압 센서/회로 → `E_D24_BOOST_PRESSURE`
- ✅ 수온센서/회로 → `E_D24_WATER_TEMP`
- ✅ MAF/흡기온도 → `E_D24_MAF`
- ✅ 시동은 도나 시동 어려움/열간·냉간 hard start → `EN_HARD_START`
- ✅ 주행/작업 중 엔진 스톨 → `EN_STALL`
- ✅ 출력저하/부하에서 힘없음 → `EN_LOW_POWER`
- ✅ 아이들 불안정/부조 → `EN_ROUGH_IDLE`
- ✅ 검은연기 → `EN_BLACK_SMOKE`
- ✅ 흰연기 → `EN_WHITE_SMOKE`
- ✅ 청색연기/오일소모 → `EN_BLUE_SMOKE`
- ✅ 엔진 과열 → `EN_OVERHEAT`
- ✅ 저오일압 → `EN_LOW_OIL_PRESS`
- ✅ 부스트 부족/터보 기계진단 → `EN_LOW_BOOST`
- ✅ 프리히트/에어히터 불량 → `EN_PREHEAT`
- ✅ IMV/저압연료/고압계통 분리 → `EN_FUEL_PRESSURE`
- ✅ CRK/CAM 전용 파형/동기 진단 → `EN_CRK_CAM_SYNC`
- ✅ 인젝터 전기/리턴/기계 분리 → `EN_INJECTOR_SEPARATE`

## 센서 위치맵

- D24 위치/핀 항목: **18**
- OEM §12-3 번호 callout 직접 연결: **16**
- 앱용 아이소메트릭은 **가능**. 3D CAD 대신 zone 기반 pseudo-isometric 엔진 그림 + OEM callout 번호 + 센서핀/ECU핀 + 정확 위치 근거 버튼 방식이 현장 가독성에 더 적합하다.
- 위치맵은 치수도면이 아니며 엔진 사양 variant에 따라 OEM 외형도/번호도면으로 최종 확인한다.

## 이번 기준에서 PASS하려면

1. 고장 전용 재작성 회로/유압/동력도에 **그 고장에 필요한 요소만** 있어야 한다.
2. 측정 위치와 공구, 실제 부하/온도/방향/인터록 조건을 지정해야 한다.
3. 정적 도통/무부하 12V만으로 배선 정상 판정 금지. 간헐/부하 고장은 전압강하·백프로브·MIN/MAX·흔들림/열간 재현을 요구한다.
4. ECU/OSS 등 컨트롤러 교환 전 B+/IGN/GND + CAN + 5V reference/external load isolation을 요구한다.
5. 결과는 rule-out + confirm_if + disassembly_gate까지 있어야 한다.
6. 센서/밸브/테스트포트는 앱에서 바로 위치를 찾을 수 있어야 한다.
7. OEM에 없는 숫자는 임의로 만들지 않고 정상측 비교/명령값 대비/격리시험으로 처리한다.

## 시동 무크랭킹 reference case

`E_START_NO`를 사용자 제시 사례 수준으로 재작성했다: 불발 순간 배터리 포스트 → 메인 B+ drop → GND drop → ST(S) MIN/MAX → START relay 부하입력/출력 + coil 명령 → KEY ST → N/OSS 인터록 순으로 분리한다. 스타터 교환 이력만으로 스타터를 다시 의심하지 않는다.
