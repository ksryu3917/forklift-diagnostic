# FIELD READINESS V4 · user benchmark reassessment

## 최종 판정

**아직 전체 앱을 사용자 요구 수준 완료로 판정하지 않는다.** 구조 검증 0-error와 현장 전문가 수준은 다른 기준이다. 이번 V4에서는 D24 엔진 21개 핵심 증상 묶음과 센서 위치맵을 추가했지만, 기존 268개 원인과 전장 일부는 여전히 전용 도면/정확 pin·fuse·동적시험 보강이 필요하다.

## 기존 64증상 / 268원인 · 엄격 재판정

- TARGET_LEVEL: **122**
- FIELD_USABLE_PARTIAL: **146**

V3의 계통별 엄격점수는 유지한다. 특히 T/M·작업장치·브레이크·스티어링의 반복 템플릿성 도면/측정 위치를 원인별 전용화해야 한다.

## 전장

- 전체 그래프: **36**
- TARGET_LEVEL: **7**
- FIELD_USABLE_PARTIAL: **29**

`E_START_NO`는 부하 전압강하/START relay input-output/coil command/KEY ST/N-OSS까지 논리는 목표수준으로 재작성했지만, 차량 사양별 정확 relay socket 번호와 fuse cavity가 모두 확정되기 전에는 strict TARGET로 올리지 않는다.

## D24NAP 엔진 V2

- 핵심 증상 묶음: **21 / 21 그래프화**
- 결과 종점: **110**
- 결과당 30조건 시뮬레이션: **3300**
- Validation errors/warnings: **0/0**
- OEM pin-level executable: **7**
- system-level field executable (일부 정확 수치/핀 source-limited): **14**

추가된 엔진 묶음: 냉·열간 hard-start, 작업/주행 중 stall, 저출력, rough idle, 흑연/백연/청연, 과열, 저오일압, 저부스트, 예열, rail 압력 형성, CRK/CAM sync, injector 전기·return·compression 분리.

## D24 센서 위치맵

- 위치 항목: **18**
- OEM §12-3 numbered callout 직접 연결: **16**

아이소메트릭은 3D CAD가 아니라 정비사용 pseudo-isometric zone map이다. 센서를 탭하면 위치 설명, sensor connector/ECU pin, OEM 근거, 관련 진단으로 이어지는 구조다. 정확 위치는 OEM callout/engine variant로 최종 확인한다.

## UI 원칙

1. 원본 회로도 전체를 첫 화면에 보여주지 않는다. 고장에 필요한 경로만 재작성한다.
2. 재작성도 아래에 바로 측정점/공구/부하조건을 붙인다.
3. 센서/솔레노이드/테스트포트는 위치맵으로 한 번에 이동한다.
4. 결과에는 rule-out / confirm / teardown gate가 있어야 한다.
5. 정적 continuity나 무부하 12V만으로 배선 정상 판정 금지.
6. OEM 미확인 숫자는 절대로 자동판정값으로 만들지 않는다.

## 아직 release-complete가 아닌 이유

- 268 원인 중 146 partial을 고장전용 측정/도면 수준으로 올릴 것
- 전장 29 partial의 정확 fuse/relay/connector/pin을 차량 사양별 확정할 것
- 전장/엔진 위치정보와 테스트포트 위치를 더 연결할 것
- Parts Book/부품번호/가격/공임은 별도 검증 DB 필요

## 검증 파일

- `field_exec_validation.md`: 기존 64/268 실행구조
- `electrical_validation.md`: 36 전장 그래프 5,760 시뮬레이션
- `engine_d24_v2_validation.md`: 21 엔진 그래프 3,300 시뮬레이션
- `FIELD_READINESS_V4.md`: 사용자 기준 엄격 재판정
