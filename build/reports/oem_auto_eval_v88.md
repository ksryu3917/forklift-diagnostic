# V8.8 OEM-Exact Automatic Evaluation Validation

- Auto-evaluable measurement points: **15**
- Structured OEM test profiles: **27**
- Deterministic boundary/scenario checks: **810** (= 30 per profile)
- Rule: only `source_class=OEM_EXACT` + explicit numeric limits may set PASS/FAIL automatically.
- Approximate specs, field comparisons, and `OEM_VERIFY` remain manual/HOLD.
- Numeric thresholds are stored in JSON, not hard-coded in Java.
- Errors: **0**
- Warnings: **0**

## Auto-eval points
- `TM_PRESSURE_TAPS/TM2` · Tap 2 · 컨버터 출구 / 쿨러 입구 · 2 profile(s) · bar
- `TM_PRESSURE_TAPS/TM3` · Tap 3 · 컨버터 충전(입구) · 2 profile(s) · bar
- `TM_PRESSURE_TAPS/TM4` · Tap 4 · 전진 클러치 · 2 profile(s) · bar
- `TM_PRESSURE_TAPS/TM5` · Tap 5 · 후진 클러치 · 2 profile(s) · bar
- `TM_PRESSURE_TAPS/TM6` · Tap 6 · 메인/펌프 압력 · 2 profile(s) · bar
- `TM_PRESSURE_TAPS/TM7` · Tap 7 · 윤활 압력 · 2 profile(s) · bar
- `HYD_MAIN_RELIEF/HY1` · 메인 릴리프 · 메인 컨트롤밸브 · 4 profile(s) · bar
- `HYD_MAIN_RELIEF/HY2` · 틸트/AUX 릴리프 · 1 profile(s) · bar
- `HYD_MAIN_RELIEF/HY3` · 틸트 유량 · 1 profile(s) · LPM
- `HYD_MAIN_RELIEF/HY4` · AUX1 유량 · 1 profile(s) · LPM
- `WORK_EQUIPMENT_CONTROL/WK2` · 메인 압력 · 니플(1) · 4 profile(s) · bar
- `WORK_EQUIPMENT_CONTROL/WK3` · 보조 릴리프 압력 · 1 profile(s) · bar
- `MAST_CYLINDER_DIAG/MS3` · 리프트 실린더 drift 시험 · 1 profile(s) · mm
- `MAST_CYLINDER_DIAG/MS6` · 틸트 실린더 좌/우 정렬 · 1 profile(s) · mm
- `EL_FR_CONTROL/FR5` · F/R solenoid coil · 1 profile(s) · ohm

## Errors
- None

## Warnings
- None
