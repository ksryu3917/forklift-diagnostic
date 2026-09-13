# FIELD DIAGNOSTIC AUDIT

- Manual symptoms: **64**
- Cause details upgraded: **268**
- Systems: **9**
- Transmission graphs: **24**
- Transmission result terminals upgraded: **151**
- Brake field isolation graph: **BRAKE_HYD_ISOLATION**
- Errors: **0**
- Warnings: **0**

## Cause coverage by system

- 드라이브 액슬: 20
- 마스트: 8
- 브레이크: 45
- 스티어링: 38
- 에어컨: 9
- 유압: 27
- 작업장치: 26
- 주차 브레이크: 3
- 트랜스미션: 92

## Enforcement
- Every cause has a field sequence, rule-outs, confirmation conditions and a teardown gate.
- Transmission terminal results cannot be accepted as complete with only `action` text.
- OEM numeric limits are reused only when already in the data/manual; missing limits are not fabricated.
- Brake piston-seal diagnosis requires circuit isolation instead of symptom-name matching.
- D34 engine data remains reference-only and must not be presented as D24 vehicle limits.
