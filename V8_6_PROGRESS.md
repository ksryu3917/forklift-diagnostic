# V8.6 Electrical Probe Completion

## Purpose
Raise every electrical diagnostic graph to the same field-first measurement workflow already used by start/OSS/engine diagnostics: show exactly where to probe, under what state/load, how to compare upstream/downstream, and when a result is sufficient to move to the next branch.

## Current state
- Release: `0.18-rc-expert-v8.6-electrical-probe`
- versionCode: `31`
- State: `RC EXPERT V8.6 ELECTRICAL PROBE`
- Test-point groups: 50
- Measurement/test points: 271
- Expert causes mapped: 268/268
- Engine graphs mapped: 21/21
- Electrical graphs mapped: 38/38

## Electrical additions
Dedicated or shared field probe families now cover STOP lamp, headlamp, turn/hazard, horn, backup lamp/buzzer, charge path, parking-brake input, lift-lock, gauge common, work/rear lamp, F/R control, OSS, A/C power, condenser fan, preheat, fuel heater, brake-oil warning, cluster power, CAN, seatbelt, license lamp, hour meter, rear lamp, strobe, water/TM/fuel gauges, wiper and washer, plus the D24 engine-electrical graphs.

## Anti-overdiagnosis rules
- Loaded-state voltage/drop tests take priority over unloaded presence checks.
- Numeric connector cavities remain unassigned if OEM evidence does not identify them.
- STOP switch 2-pin roles are identified functionally until verified.
- Alternator-local output does not prove battery charging-path integrity.
- CAN terminator position/resistance is not fabricated.
- Gauge transfer curves are not invented where OEM data is absent.
- A/C airflow/component ratings are not used as electrical pass/fail thresholds.

## CI gate
`tools/validate_test_point_locator.py` now requires all 38 electrical graph IDs to resolve to valid point groups with physical focus data. The GitHub Actions identity check is updated from V8.5 to V8.6 and uploads the V8.6 locator report.

## Final local validation
All project validators were rerun after the V8.6 graph-map/CI changes.

- Field executable: 64 symptoms / 268 causes / 4,530 T/M result-path simulations / 0 errors / 0 warnings
- Electrical: 38 graphs / 373 nodes / 205 result terminals / 6,150 simulations / 0/0
- Expert cause diagnostics: 268/268 / 8,040 simulations / 0/0
- D24 engine: 21 graphs / 110 result terminals / 3,300 simulations / 0/0
- Parts linkage: expert 268 + electrical 38 + engine 21 / 0/0
- Physical location map: electrical 38/38 + expert systems 9/9 / 0/0
- Engine sensor locator: 18 items / 0/0
- Test-point locator V8.6: 50 groups / 271 points / expert 268/268 / engine 21/21 / electrical 38/38 / 0/0
- Diagnostic specificity: unresolved cross-cause identical chains 0

Strict electrical source-readiness remains intentionally separate from field executability: 17 TARGET / 21 source-limited PARTIAL. V8.6 makes all 38 field-probe executable without inventing the missing OEM connector cavity/option-network values.

## Build status
This package is a locally validated source overlay. APK build and exact Git commit-SHA stamping are intentionally left for the Work → github.com → Actions flow.
