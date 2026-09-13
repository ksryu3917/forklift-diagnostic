# Apply V18 RC EXPERT V8 PARTS to `v18-rc-auto`

Baseline repository: `ksryu3917/forklift-diagnostic`, branch `v18-rc-auto`.
Deployment method already agreed for this project: use **Work + Cloud Browser on github.com**, not the GitHub connector write API.

## Overlay / merge
1. Start Work from the current `v18-rc-auto` HEAD and overlay this package preserving paths.
2. Keep the existing Home/release/SHA stamping behavior from the current app.
3. Add/merge V8 assets and activities:
   - `expert_diag_v2.json`
   - `electrical_diag_v1.json`
   - `engine_diag_d24_v2.json`
   - `engine_sensor_map_d24_v1.json`
   - `parts_reference_v1.json`
   - `parts_views/*`
   - `ExpertDiagnosticActivity.java`
   - `ElectricalDiagnosticActivity.java`
   - `EngineExpertDiagnosticActivity.java`
   - `EngineSensorMapActivity.java`
   - `PartsReferenceActivity.java`
4. Run `python3 tools/apply_parts_ui_patch.py <repo-root>` so Manifest declares `PartsReferenceActivity`.
5. Ensure Manifest/MainActivity links expose:
   - 현장 전문가 진단
   - 전기/차체전장 진단
   - D24 엔진 진단
   - D24 센서 위치/핀맵
   - 부품/분해도 (launch `PartsReferenceActivity` without extras to browse main groups)
6. App identity must be:
   - versionCode `23`
   - versionName `0.18-rc-expert-v8-parts`
   - release state `RC EXPERT V8 PARTS`

## Required validators before commit
Run:
- `python3 tools/validate_expert_v2.py`
- `python3 tools/validate_field_diagnostics.py`
- `python3 tools/validate_electrical_diagnostics.py`
- `python3 tools/validate_engine_d24_v2.py`
- `python3 tools/validate_field_readiness_v3.py`
- `python3 tools/build_field_readiness_v5.py`
- `python3 tools/validate_parts_reference.py`

Required state:
- 64 symptoms / 268 causes / 268 TARGET / 8,040 cause simulations / 0 errors / 0 warnings
- transmission 24 graphs / 151 terminals / 4,530 result-path simulations / 0/0
- electrical 36 graphs / 350 nodes / 192 terminals / 5,760 simulations / 0/0
- D24 engine 21 graphs / 110 terminals / 3,300 simulations / 0/0
- parts linkage: 268 expert + 36 electrical + 21 engine, errors 0 warnings 0
- electrical strict readiness stays honest: 17 TARGET / 19 source-limited PARTIAL unless new OEM connector/pin sources are added

## Parts Book behavior gate
- Source: `SB5120C05` D20/25/30/33S-7 D24 Tier4 Parts Book.
- Exact replacement part must not be silently selected if Parts Book lists model/Serial/change/option variants.
- For serial-sensitive groups, UI must show `모델/Serial/옵션 확인 후 품번 확정`.
- Parts Book generic sensor entries `301308-00480` and `65.27103-7014` must not be auto-labelled CRK/RPS without an explicit source identifying them.
- Diagnostic screen remains first; exploded views are parts/location evidence, not a substitute for measurements.

## Work / GitHub / Actions
1. Commit this V8 overlay to `v18-rc-auto` through github.com in Work.
2. Run Actions from that exact commit.
3. Verify APK `assets/diagnostic_release.json` contains exact build commit SHA and branch `v18-rc-auto`.
4. Verify `versionName=0.18-rc-expert-v8-parts` and state `RC EXPERT V8 PARTS` inside the APK artifact.
5. Install/test that exact artifact, not an older main/0.8.7 build.

## Required field UI smoke tests
- Start no-crank -> related parts shows D24 starter `300516-00034A` plus chassis/start-control group, without pretending starter is the fault before the voltage-drop flow is completed.
- A/C condenser fan no-run -> parts screen shows early fan `210101-00490` vs later dual fan `210101-00569` and serial ranges.
- OSS/seat-lock -> parts screen shows seat-belt interlock harness and option-specific OSS controller group with option warning.
- D24 WTS -> sensor map shows pin/location diagnostic info and Parts Book part `301317-00014D`, plus p211 evidence.

## V8.1 additions
- Release: `0.18-rc-expert-v8.1-parts-profile` / code 24 / `RC EXPERT V8.1 PARTS PROFILE`.
- Keep `PartsReferenceActivity` current-vehicle model+Serial profile UI and application filtering.
- Include `upgrade_electrical_v81_wiper.py` / `upgrade_parts_v81.py` source changes and checked-in generated JSON.
- Electrical catalog now includes `E_WIPER_NO` and `E_WASHER_NO`; exact option fuse/pin remains source-limited rather than guessed.
- Smoke test PartsReference with D25S-7 FDA0V Serial 800 vs 900: A/C fan must switch from 210101-00490 to 210101-00569 at Serial 843; front wiper changes at Serial 1345.
- Smoke test D20S-7 FDA0U Serial 177 vs 178: brake module must change 620101-01355 -> 620101-01461.


## V8.2 diagnostic-first priority update
- 품번/Serial 적합성은 정비 진단의 PASS 조건에서 제외. 실제 주문은 차대번호 기준 부품점/EPC 확인을 우선한다.
- Parts Book은 **부품 위치, 조립관계, 하네스/밸브/센서가 속한 그룹, exploded view** 확인에 우선 사용한다.
- 앱 화면 순서도 `점검 위치/재작성도/측정/격리/확정`을 앞에 두고 `분해도/참고 품번`을 결과 뒤로 내렸다.

## V8.3 technician-location update
- Release: `0.18-rc-expert-v8.3-location` / code 26 / `RC EXPERT V8.3 LOCATION`.
- Add `field_location_map_v1.json` and `FieldLocationMapActivity.java`.
- Run updated `tools/apply_parts_ui_patch.py` so Manifest declares all V8.3 activities including `FieldLocationMapActivity`.
- Diagnostic pages must show **점검 위치맵 before parts/part-number information**.
- Electrical graph IDs 38/38 are mapped to physical test zones; expert systems 9/9 are mapped to physical zones.
- Location map is a non-dimensional technician locator. Exact component mounting remains linked to OEM service/Parts Book evidence buttons; do not convert zone coordinates into claimed dimensions.
- Required validator: `python3 tools/validate_field_location_map.py <repo-root>`.

## V8.3.1 specificity + focused engine locator update
- Release identity: versionCode `27`, versionName `0.18-rc-expert-v8.3.1-location-specificity`, state `RC EXPERT V8.3.1 LOCATION SPECIFICITY`.
- Add `tools/validate_diagnostic_specificity.py`, `tools/build_field_readiness_v7.py`, `tools/validate_engine_sensor_locator.py` to CI.
- Expert UI must render `specificity_gate`:
  - `CAUSE_SPECIFIC_PRE_TEARDOWN` → **원인별 마지막 분리시험** before teardown.
  - `SHARED_ASSEMBLY_BOUNDARY` → **분해 전 확정 한계** and post-teardown checks; never name a more specific internal part before opening the assembly.
- Current specificity gate state: 62 causes have explicit cause-specific pre-teardown differentiators; 44 causes in 16 exact-shared groups are intentionally limited at a shared assembly boundary; unresolved cross-cause exact-shared groups = 0.
- Add `parts_views/parts_p211_viewA.png` and `parts_p211_viewB.png`. These are cropped OEM evidence views only; default sensor locator remains the app redraw. BPS/CAM/WTS/OPTS/MAF can open the relevant p211 engine direction directly.
- Required additional validators:
  - `python3 tools/validate_diagnostic_first_priority.py .`
  - `python3 tools/validate_field_location_map.py .`
  - `python3 tools/validate_engine_sensor_locator.py .`
  - `python3 tools/validate_diagnostic_specificity.py .`
  - `python3 tools/build_field_readiness_v7.py .`
- Actions release verification must assert the V8.3.1 version/state and upload `diagnostic_specificity_v83.md` + `FIELD_READINESS_V7_LOCATION.md`.

## V8.4 measurement/test-point locator update
- Release identity: versionCode `28`, versionName `0.18-rc-expert-v8.4-testpoint-locator`, state `RC EXPERT V8.4 TESTPOINT LOCATOR`.
- Add `test_point_locator_v1.json` and `TestPointLocatorActivity.java`; Manifest must declare `TestPointLocatorActivity`.
- Diagnostic-first rule: part numbers remain after diagnosis. The new screen appears before parts and tells the technician **where to connect the DMM/gauge, under what operating state, what OEM value applies, and what branch that result rules in/out**.
- T/M pressure locator must preserve SM1018-01 §2-3-4 exactly: 0–20.5 bar gauge; oil 49–71°C; Tap4 F clutch, Tap5 R clutch, Tap7 lube, Tap3 converter charge, Tap2 converter outlet/cooler inlet, Tap6 main/pump, Tap1 comparison point; do not reorder roles.
- Brake locator must explicitly state that `40 bar` is master-cylinder relief cracking pressure, **not** an axle piston-seal leakage threshold. Left/right axle isolation is field isolation, not an invented OEM leak spec.
- Hydraulic locator must keep D500093 values model-specific and mark gauge test-port identity as `OEM VERIFY` where the source does not give a unique port/adapter.
- OSS locator must never reduce `wiggle = harness fault`; correlate wiggle with VREF/CAN/seat-input restoration.
- Start locator must measure loaded failure-state B+/GND/ST/relay input-output; open-circuit `12V present` is not a pass.
- New required validator: `python3 tools/validate_test_point_locator.py .`.
- Required UI smoke tests:
  - T/M -> **측정포인트 / 압력탭 바로보기** -> Tap1~7 roles and exact 49–71°C pressure table visible, OEM p078/p079 accessible.
  - Brake -> master P / master-output isolation / left-right bleeder visible; no invented seal leak pressure.
  - E_START_NO -> battery POST / starter B+ / ST / case / starter relay #8 / coil / key ST in one point map.
  - E_OSS_SEAT_LOCK -> power/seat input/5V/CAN/output in one point map, with exact pin values not invented.
  - E_AC_COND_FAN_NO -> fan B+/GND/direct power/relay-control sequence; relay number remains source-limited.


## V8.5 engine measurement / test-point completion (latest override)

This section supersedes older version identities above.

- Release identity: versionCode `30`, versionName `0.18-rc-expert-v8.5-engine-testpoint`, state `RC EXPERT V8.5 ENGINE TESTPOINT`.
- Keep diagnostic-first UI order: **measurement/test point → physical location → redrawn circuit/flow → isolation/confirmation → teardown gate → parts/exploded view**.
- `test_point_locator_v1.json` now contains **23 groups / 147 points**.
- Manual expert diagnostics: **268/268 causes** mapped across all 9 systems. `ExpertDiagnosticActivity` must expose the cause-specific test-point button for every cause; no old five-system UI restriction.
- D24 engine: **21/21 graphs** mapped to 11 engine test-point families. `EngineExpertDiagnosticActivity` must expose `TestPointLocatorActivity` before parts.
- Engine test-point screen links directly to `EngineSensorMapActivity` with sensor focus IDs so probe/scope instructions and actual sensor location are one flow.
- Do not create missing numeric thresholds: no fabricated crank-start rail MPa, injector return cc/min, oil-pressure port thread/spec, CAN resistance location, or unverified option connector cavity.
- Required validator: `python3 tools/validate_test_point_locator.py .` → 23 groups / 147 points / expert 268/268 / engine 21/21 / 0 errors / 0 warnings.
- CI must assert V8.5 identity inside the built APK and upload `build/reports/test_point_locator_v85.md`.

### V8.5 field smoke tests

1. Expert cause from each of the 9 manual systems opens a filtered test-point screen containing only that cause's mapped points.
2. D24 crank-no-start opens ECU communication → RPM/sync → rail actual/command → RPS → low-pressure fuel → IMV → injector drive/return points; no invented minimum rail-pressure number.
3. D24 ECU no-communication shows SENSOR 15A, ECU loaded B+/IGN/GND, CAN comparison, and VREF external-load isolation.
4. D24 CRK/CAM shows exact ECU signal pairs/shield and scope comparison; CAM connector-face orientation remains non-graphical until verified.
5. D24 injector separation shows #1 ECU126/127, #2 174/150, #3 175/151, #4 125/103, then current waveform → return comparison → compression.
6. D24 low-oil-pressure keeps mechanical pressure port as `OEM_VERIFY` until exact port/thread/spec is confirmed; electronic OPTS pins are shown first.
7. Parts/reference button remains after diagnostic/confirmation cards and never becomes a PASS requirement for field diagnosis.

## V8.6 electrical probe completion (latest override)

This section supersedes older release identities above.

- Release identity: versionCode `31`, versionName `0.18-rc-expert-v8.6-electrical-probe`, state `RC EXPERT V8.6 ELECTRICAL PROBE`.
- Electrical diagnostics: **38/38 graphs** must map to a valid measurement/test-point group before APK build.
- `test_point_locator_v1.json` current expected state: **50 groups / 271 points**; expert 268/268; engine 21/21; electrical 38/38.
- Electrical probe screens must keep the field order: loaded power/ground → command/input-output → branch/load → isolation/direct test when safe → conclusion. Open-circuit `12 V present` is not sufficient where the load can expose resistance.
- STOP lamp numeric pin roles stay function-identified until verified; do not assign supply/output to pin 1/2 by guess.
- Charging screen must compare battery POST, alternator B+, ALT B+→BAT+ drop, and ALT case→BAT- drop under load; alternator-local 14 V alone is not a pass.
- CAN screen must isolate controller power/ground and compare other modules before network/component conclusion; exact terminator location/resistance remains source-limited unless OEM source is added.
- A/C power card may show OEM-confirmed blower facts (12 V / 10 A / 3-speed, stage-3 direct test, 4-pin 1.5SQ, thermostat 2-pin 1SQ), but component specs are not to be converted into invented diagnostic thresholds.
- Required validator: `python3 tools/validate_test_point_locator.py .` → 50 groups / 271 points / expert 268/268 / engine 21/21 / electrical 38/38 / 0 errors / 0 warnings.
- Actions must assert V8.6 identity in the APK and upload `build/reports/test_point_locator_v86.md`.


## V8.7 field worksheet completion (latest override)

This section supersedes older release identities above.

- Release identity: versionCode `32`, versionName `0.18-rc-expert-v8.7-field-worksheet`, state `RC EXPERT V8.7 FIELD WORKSHEET`.
- Keep V8.6 diagnostic/test-point coverage unchanged: 50 groups / 271 points; expert 268/268; engine 21/21; electrical 38/38.
- Every displayed test point must expose persisted **measured value + field note + PASS/FAIL/HOLD** controls.
- Measurement storage must be scoped by an active field-work session so a different truck/job cannot silently inherit prior readings. Serial/chassis entry is not required for the diagnostic session label.
- FAIL status must surface the existing source-backed `decision` as the next branch; the worksheet must not invent a numerical limit from free-text values.
- Required validator: `python3 tools/validate_measurement_worksheet.py .` -> 50 groups / 271 points / 0 errors / 0 warnings.
- Actions must assert V8.7 identity in the built APK and upload `build/reports/measurement_worksheet_v87.md`.
- Work deployment remains: Cloud Browser on github.com -> `v18-rc-auto` -> Actions -> verify artifact commit SHA and `diagnostic_release.json`.

## V8.8 OEM-exact automatic evaluation (latest override)

This section supersedes older release identities above.

- Release identity: versionCode `33`, versionName `0.18-rc-expert-v8.8-oem-auto-eval`, state `RC EXPERT V8.8 OEM AUTO EVAL`.
- V8.7 worksheet behavior remains available for all 271 points. **Automatic PASS/FAIL is allowed only when the point itself is `source_class=OEM_EXACT` and the asset contains an explicit structured `auto_eval` numeric rule.**
- Current auto-evaluable points: **15 points / 27 OEM profiles**. All other points remain manual PASS/FAIL/HOLD and may not infer thresholds from free text.
- Automatic evaluation currently covers:
  - T/M pressure Tap2~Tap7 with explicit low-idle vs 2,000 rpm profile selection.
  - Main hydraulic relief model-specific D20/D25/D30/D33 ranges; current vehicle model may preselect but technician can change the profile.
  - Auxiliary relief, tilt flow, AUX1 flow.
  - Work-equipment main/aux relief duplicates where the same OEM spec is used in that diagnostic path.
  - Mast lift drift max limit and tilt-cylinder left/right rod-length difference max limit.
  - F/R solenoid coil resistance at 25°C.
- A/C pressure values described as `약`, 5 V/12 V functions without an OEM tolerance, CAN comparison, voltage-drop field methods, steering pressure with conflicting OEM text, and any `OEM_VERIFY`/FIELD point **must not auto-PASS/FAIL**.
- Bar inputs support bar or psi selection and convert to the base unit before comparison. Numeric limits live in `test_point_locator_v1.json`, not in Java code.
- Auto-evaluation judges only that measurement point. It must still display and preserve the existing next isolation branch; it must not declare the root cause solely because one measured value failed.
- Required validator: `python3 tools/validate_oem_auto_evaluation.py .` -> 15 points / 27 profiles / 810 deterministic scenarios (=30 per profile) / 0 errors / 0 warnings.
- `validate_measurement_worksheet.py` must continue to pass and confirm arbitrary threshold generation is prohibited.
- Actions must assert V8.8 identity in the built APK and upload `build/reports/oem_auto_eval_v88.md`.
- Work deployment remains: Cloud Browser on github.com -> `v18-rc-auto` -> Actions -> verify artifact commit SHA and `diagnostic_release.json`.


## V8.9 Adaptive Branch 적용

- 대상 브랜치: `v18-rc-auto`
- versionCode: `34`
- versionName: `0.18-rc-expert-v8.9-adaptive-branch`
- release state: `RC EXPERT V8.9 ADAPTIVE BRANCH`
- 추가 CI: `python3 tools/validate_adaptive_branch_v89.py .`
- CI는 20개 핵심 계통(엔진 11/11 포함)의 137개 explicit multi-point rules를 검사하고 rule당 30개 controlled synthetic 조건을 검증한다.
- Work에서 github.com 직접 적용 후 Actions artifact가 실제 적용 commit SHA에서 빌드됐는지 확인한다.
