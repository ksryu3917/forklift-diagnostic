# V8.9 Adaptive Multi-point Branch

- 측정값/정상·이상 판정을 한 점씩 보는 데서 끝내지 않고 여러 포인트의 조합을 평가한다.
- 조합판정은 **배제된 구간 / 현재 남은 계통 / 다음 한 점**을 제시한다.
- 단일 FAIL을 부품교환 확정으로 사용하지 않는다.
- OEM 미확정 수치 임계값을 새로 만들지 않는다.
- 핵심 전장/유압/T/M + D24 엔진 11/11 진단군을 포함한 **20개 계통**에 explicit ordered rules 적용.
- 모든 rule은 point ID validity, shadowing, synthetic 30-condition simulation을 CI에서 검사한다.

## 검증 결과
- Adaptive groups: **20**
- Explicit ordered rules: **137**
- Rule-level synthetic scenarios: **4,118**
- Errors / warnings: **0 / 0**
- Existing validators: field / electrical / expert / engine / parts / location / test-point / worksheet / OEM auto-eval / specificity 모두 PASS
- Existing OEM auto-eval: **15 points / 27 profiles / 810 scenarios / 0 errors**
- Java local syntax-like check: Android SDK classpath 부재로 full compile은 미실행. `javac` 출력에서 syntax-like error pattern은 0.

## 릴리스
- versionCode **34**
- versionName **0.18-rc-expert-v8.9-adaptive-branch**
- state **RC EXPERT V8.9 ADAPTIVE BRANCH**

- D24 engine adaptive coverage: **11/11 measurement groups**
