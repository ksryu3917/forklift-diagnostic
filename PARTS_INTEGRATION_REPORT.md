# V8 Parts Book integration report

## Source
- Doosan Parts Book `SB5120C05`
- Models: D20S-7 / D25S-7 / D30S-7 / D33S-7
- Model codes: FDA0U / FDA0V / FDA0W / FDA0X
- Engine: D24 / DL02-LEF00 / Tier 4
- Source rule: exact replacement part number is not auto-approved until model code + Serial No. + option/applicability are compatible.

## App changes
- Added `parts_reference_v1.json`
- Added `PartsReferenceActivity.java`
- Added 25 Parts Book view assets under `assets/parts_views/`
- Every expert cause, electrical graph, and D24 engine graph now has a parts-reference link:
  - 268 / 268 expert cause links
  - 36 / 36 electrical graph links
  - 21 / 21 D24 engine graph links
- Diagnostic screens now expose `관련 부품 / 분해도 / 적용 Serial` directly from the fault workflow.
- Parts screen separates **diagnostic conclusion** from **replacement part confirmation**. It presents linked part groups first and blocks silent exact-part assumptions on serial-sensitive groups.

## D24 sensor map integration
Parts Book `EDL02-P709-048` is connected to the D24 sensor map.

Exact or explicitly named Parts Book items:
- Boost sensor family: 301318-00012A / 301318-00013B / 301318-00007A (alternates/change candidates; do not auto-pick one without applicability confirmation)
- Coolant temperature sensor: 301317-00014D
- Oil pressure & temperature sensor: 65.27427-7001
- Cam speed sensor: 301308-00135A
- Air flow sensor: 301308-00376

The Parts Book also contains generic `sensor` entries 301308-00480 (qty 2) and 65.27103-7014. Their function is not explicitly named in this Parts Book table, so V8 does **not** assign them to CRK/RPS/etc. by guess. CRK/RPS remain GROUP_ONLY until a source explicitly identifies the part number.

Other exact D24 service parts integrated:
- ECU: 300618-00037B
- Engine harness: 310207-02855E
- Starter: 300516-00034A
- Glow plug: 300622-00002D (qty 4)

## A/C improvement
The Parts Book gives a real serial split for condenser fan configuration.
- Early configuration fan assembly: 210101-00490
  - FDA0U 1~202
  - FDA0V 1~842
  - FDA0W 1~2357
  - FDA0X 1~476
- Later configuration condenser fan assembly: 210101-00569 (qty 2)
  - FDA0U 203~
  - FDA0V 843~
  - FDA0W 2358~
  - FDA0X 477~
- Condenser: 440204-00059
- Compressor: 440205-00026
- A/C compressor group includes relay assy A404157 qty 3, but Parts Book alone does not identify which individual relay is the condenser-fan relay; V8 does not invent that mapping.

## OSS / safety / parking
- Seat belt interlock group D812926 -> harness 310207-01549
- EPB option page 620204-07892 includes controller 300611-01180 `CT100 OSS FOR E...`, direction switch, harness and relay. This is explicitly treated as option-specific, not a universal OSS controller part number.
- Parking brake actuator group 400805-00012 includes hydraulic valve 410111-00035, coil 300715-00153, rod seal kit 401107-02158 and check valve 410104-00556.

## Position / exploded-view support
- Whole-truck Location Chart 950211-00188 is included as reference views.
- D24 sensor-map quick view remains an app redraw; exact OEM parts/sensor exploded view is available behind the evidence button.
- The default diagnostic screen is still the technician flow and simplified circuit/hydraulic path; Parts Book pages are evidence/position/part confirmation screens rather than the main diagnostic UI.

## Validation
`tools/validate_parts_reference.py`
- part groups: 16
- expert links: 268/268
- electrical links: 36/36
- engine links: 21/21
- D24 sensor map items: 18
- errors: 0
- warnings: 0

This validation checks linkage/source integrity. It does not claim every one of 268 causes has a unique exact replacement part number; many faults correctly link to an assembly/part group first because exact part selection depends on Serial/options or teardown findings.

## V8.1 Serial-aware upgrade
- Parts group count: 21.
- Added exact Serial split groups for brake module and front/rear wiper motors/harnesses.
- Parts UI stores current model + Serial and marks structured part candidates as `적용` / `현재 Serial 범위 외`.
- A/C condenser fan split is now machine-readable: early 1-fan vs late 2-fan configuration by FDA0U/V/W/X Serial.
- Added lighting exploded-view groups and steering-cylinder service parts.
- Serial match does not override option/physical-configuration checks.


## V8.2 diagnostic-first priority update
- 품번/Serial 적합성은 정비 진단의 PASS 조건에서 제외. 실제 주문은 차대번호 기준 부품점/EPC 확인을 우선한다.
- Parts Book은 **부품 위치, 조립관계, 하네스/밸브/센서가 속한 그룹, exploded view** 확인에 우선 사용한다.
- 앱 화면 순서도 `점검 위치/재작성도/측정/격리/확정`을 앞에 두고 `분해도/참고 품번`을 결과 뒤로 내렸다.
