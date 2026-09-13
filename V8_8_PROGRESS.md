# V8.8 OEM EXACT AUTO EVALUATION

## 목적
V8.7의 현장 측정 워크시트에서 한 단계 더 나아가, **OEM이 숫자 허용범위를 명확하게 제시한 항목만** 측정값 입력 즉시 자동 정상/이상 판정한다. OEM 허용범위가 없는 항목은 기존 수동 판정/격리 방식으로 유지한다.

## 자동판정 안전규칙
1. `source_class = OEM_EXACT` 필수.
2. `auto_eval.authority = OEM_EXACT_ONLY` 필수.
3. min/max가 구조화된 JSON으로 존재해야 한다.
4. `약`, 기능전압(5V/12V)처럼 허용오차가 없는 값, FIELD 비교, OEM_VERIFY는 자동판정 금지.
5. 자동판정은 **측정 포인트 상태**만 정상/이상으로 기록한다. 원인 확정은 기존 `decision` 격리분기를 계속 수행한다.
6. OEM 수치는 Java에 하드코딩하지 않고 asset JSON에 둔다.

## 현재 자동판정 범위
- 15 measurement points
- 27 test/model profiles
- 810 deterministic boundary scenarios (30/profile)

### T/M
Tap2~Tap7. 각 Tap은 저속 공전과 2,000 rpm 조건을 반드시 별도로 선택한다. bar/psi 입력을 지원한다.

### 유압/작업장치
- 메인 릴리프: D20/D25/D30/D33 모델별 범위
- 보조 릴리프
- Tilt flow
- AUX1 flow
- 작업장치 진단 화면의 동일 OEM 메인/보조 relief 규격

### 마스트
- 정격하중 drift: 10분 기준 최대 100 mm
- 완전 신장 시 좌/우 tilt rod length difference 최대 3.18 mm

### 전장
- F/R solenoid coil: 25°C 10±0.3Ω

## 자동판정 제외 예시
- 간헐 무크랭킹 ST/B+/GND 전압강하: OEM mV 한계 미확인 -> 부하 중 구간비교 유지
- OSS 5V: nominal 5V지만 해당 문서에 허용오차가 구조화되어 있지 않음 -> 비교/안정성 진단 유지
- A/C low/high: 원문이 `약` 범위이고 조건 의존 -> 자동 PASS/FAIL 안 함
- Steering relief: OEM 본문 단위/psi와 회로도 값 상충 -> OEM_VERIFY 유지
- WTS 20°C/110°C 저항: 근사값만 확인 -> 자동 PASS/FAIL 안 함

## UI
- 자동판정 대상은 녹색 `OEM exact 자동판정` 패널을 표시한다.
- 조건/모델이 둘 이상이면 선택 전에는 판정하지 않는다.
- D20/D25/D30/D33 메인 relief는 저장된 현재 차량 모델이 있으면 해당 모델을 선선택한다.
- 단위가 둘 이상이면 단위를 선택하고 base unit으로 변환 후 판정한다.
- 정상/이상 결과에는 `[OEM 자동판정]` 표식을 남긴다.
- 정비사는 수동 정상/이상/보류로 override할 수 있다.

## 검증
- `validate_oem_auto_evaluation.py`: 15 points / 27 profiles / 810 scenarios / 0 errors / 0 warnings.
- 기존 field/electrical/expert/engine/parts/location/test-point/worksheet/specificity validators 전체 재실행: 0 errors / 0 warnings.
- Release: versionCode 33 / `0.18-rc-expert-v8.8-oem-auto-eval` / `RC EXPERT V8.8 OEM AUTO EVAL`.
