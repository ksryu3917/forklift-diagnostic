# V8.7 FIELD WORKSHEET progress

## Why this revision exists
V8.6 could show where to connect a probe/gauge and what to compare, but it did not let the technician record the actual failed-state measurement inside the diagnostic flow. V8.7 closes that workflow gap.

## Field workflow now implemented
- All existing **50 test-point groups / 271 measurement-isolation points** use one shared worksheet UI.
- Each displayed point stores:
  - measured value as free field text including units/waveform description,
  - field note / reproduction condition,
  - technician judgement: **PASS / FAIL / HOLD**.
- A FAIL does not auto-replace OEM logic. The card immediately exposes the point's existing `decision` as the **next branch**.
- The worksheet summarizes measured/pass/fail/hold/unjudged counts.
- `이상 포인트의 다음 분기만 모아보기` collapses the current failure evidence into a short next-action list.
- Current measurements can be copied as text for service notes.

## Job/session separation
Measurements are not stored globally by point anymore. An active **field-work session** is created and included in every storage key. The technician can start `새 작업 시작 · 다른 차량/현장` with a free label such as a fleet number/customer/job name. Chassis/Serial entry is deliberately **not mandatory** because this feature is for diagnosis, not parts ordering. Previous session values therefore do not silently contaminate a different truck.

## No fabricated thresholds
V8.7 deliberately does not parse arbitrary numeric input and auto-pass/fail it. The source-backed `expected` value remains visible; the technician records the measurement and chooses PASS/FAIL/HOLD. This prevents source-limited circuits from acquiring invented thresholds. A later auto-judge field may only be added to points whose OEM numeric criterion is structured and explicitly verified.

## Validation
- `validate_measurement_worksheet.py`: **50 groups / 271 points / 0 errors / 0 warnings**.
- Existing V8.6 test-point validator remains: expert 268/268, engine 21/21, electrical 38/38.
- Java syntax-like parse check: 0 syntax-like errors (Android SDK unavailable in this local runtime; full Android compile remains an Actions step).

## Release identity
- versionCode: **32**
- versionName: **0.18-rc-expert-v8.7-field-worksheet**
- state: **RC EXPERT V8.7 FIELD WORKSHEET**
- branch target: `v18-rc-auto`
