# V8.1 Parts/Serial/Option Progress

## What changed
- Parts Book source: SB5120C05, D20S-7/D25S-7/D30S-7/D33S-7, D24 Tier4.
- Parts groups expanded: 16 -> 21.
- PartsReferenceActivity now stores current model + Serial and evaluates structured applicability ranges.
- Serial-aware groups now include A/C condenser fan, brake module, front wiper, rear wiper.
- Lighting and steering-cylinder exploded views added.
- Electrical graphs expanded 36 -> 38 with E_WIPER_NO and E_WASHER_NO.
- Wiper/washer option fuse cavities and numeric switch pins remain source-limited; no guessed identifiers are written.

## OEM serial examples encoded
- A/C condenser fan:
  - 210101-00490: FDA0U 1-202 / FDA0V 1-842 / FDA0W 1-2357 / FDA0X 1-476
  - 210101-00569: FDA0U 203+ / FDA0V 843+ / FDA0W 2358+ / FDA0X 477+
- Brake module:
  - D20/D25/D30 early 620101-01355 -> late 620101-01461 at U178/V755/W2234
  - D33 early 620101-01356 -> late 620101-01462 at X450
- Front wiper motor:
  - A214302 early -> 300512-00042 late at U325/V1345/W3583/X643
- Rear wiper motor:
  - A214302 early -> 220210-01910 late at U325/V1345/W3583/X643

## Validation
- Expert manual causes: 268/268 TARGET, 8040 simulations, 0 errors / 0 warnings.
- Electrical: 38 graphs, 373 nodes, 205 result terminals, 6150 simulations, 0 errors / 0 warnings.
- Strict electrical readiness: 17 TARGET / 21 source-limited PARTIAL.
- D24 engine: 21 graphs, 110 result terminals, 3300 simulations, 0 errors / 0 warnings.
- Parts links: expert 268 / electrical 38 / engine 21; 21 part groups; 0 errors / 0 warnings.

## Release identity
- versionCode 24
- versionName 0.18-rc-expert-v8.1-parts-profile
- state RC EXPERT V8.1 PARTS PROFILE
- source branch v18-rc-auto
- local source is UNSTAMPED_LOCAL_PATCH until Work/GitHub Actions stamps the real commit SHA.


## V8.2 diagnostic-first priority update
- 품번/Serial 적합성은 정비 진단의 PASS 조건에서 제외. 실제 주문은 차대번호 기준 부품점/EPC 확인을 우선한다.
- Parts Book은 **부품 위치, 조립관계, 하네스/밸브/센서가 속한 그룹, exploded view** 확인에 우선 사용한다.
- 앱 화면 순서도 `점검 위치/재작성도/측정/격리/확정`을 앞에 두고 `분해도/참고 품번`을 결과 뒤로 내렸다.
