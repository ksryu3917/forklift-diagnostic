# V8.9.1 Integration Hotfix

Target: ksryu3917/forklift-diagnostic / v18-rc-auto

Purpose: fix the installed V8.9 navigation defect where the visible engine button still opens the legacy D34 temporary screen even though D24 expert classes/assets are present.

Apply this overlay, commit, and let Actions run. The workflow itself applies `tools/apply_v891_runtime_integration.py` before validation/build and then runs `tools/validate_v891_runtime_integration.py`.

Required user-visible smoke tests after installing the artifact:
1. 차량 진단 -> `⚙ D24 엔진 현장진단` opens `D24 엔진 현장진단`, not the D34 temporary DTC screen.
2. The D24 screen shows sensor location/pin map and the 21 engine graph catalog.
3. 차량 진단 also exposes `⚡ 전기 / 차체전장 진단`.
4. A legacy cause page exposes `🛠 현장 전문가 진단 · 재작성 도면/측정점` and opens the 268-cause expert activity.
5. Sensor map / test-point / field-location / parts-reference screens open without ActivityNotFoundException.
6. App/Data status shows versionName `0.18-rc-expert-v8.9.1-integration`, state `RC EXPERT V8.9.1 INTEGRATION`, branch `v18-rc-auto`, and the exact build commit SHA.

Do not reuse older V8.9 artifacts.
