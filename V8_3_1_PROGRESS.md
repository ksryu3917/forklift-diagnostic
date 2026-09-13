# V8.3.1 · Diagnostic Specificity + Technician Location

## 이번 단계 핵심
- 품번보다 진단/점검 위치 우선 원칙 유지.
- 차량 전체 정비 위치맵 17 zone 추가, 전장 38/38 graph와 전문가 9/9 system 연결.
- D24 센서/액추에이터 18개 위치맵 유지, Parts Book p211에서 정확 item이 확인된 BPS/CAM/WTS/OPTS/MAF는 전체 페이지 대신 해당 엔진 방향 근거뷰를 바로 연다.
- 기존 268원인의 진단체인 중복을 별도 감사하여 “그래프가 끝까지 간다 = 원인별 전문가 진단”이라는 과거 기준을 폐기.

## Cause specificity 결과
- 전체 원인: 268
- individually distinct full signatures: 202
- same-root-cause reuse accepted: 22 causes / 10 groups
- explicit shared-assembly boundary: 44 causes / 16 groups
- explicit cause-specific pre-teardown gates: 62 causes
- unresolved cross-cause shared signatures: 0

### 판정 규칙
1. 분해 전에 구분 가능한 원인은 `CAUSE_SPECIFIC_PRE_TEARDOWN` 마지막 분리시험을 반드시 표시.
2. 같은 어셈블리 내부에서 분해 전에 시일/보어/기어 등 세부손상을 나눌 수 없으면 `SHARED_ASSEMBLY_BOUNDARY`에서 멈춤.
3. shared boundary에서는 “피스톤시일 확정”처럼 과도하게 세부 부품을 확정하지 않고, 분해 후 확인항목을 따로 표시.

## 대표적으로 새로 분리한 family
- T/M 인칭 링크 조정 vs 감속스풀 stick-open vs 모듈밸브 소착 vs OFF-position stick
- 드라이브액슬 휠베어링 vs 피니언/링기어 조정 vs backlash vs side/spider gear 구속
- 브레이크 페달 기계저항 vs 잔압 없는 피스톤/디스크 끌림 vs 회전주기성 평탄도 문제 vs 마찰면 글레이징
- 스티어링 컬럼 정렬 vs 스티어링유닛 덮개 체결응력 vs 우선순위밸브 스풀 고착
- A/C 콘덴서 풍량불량 vs 건조기 제한 vs 팽창밸브 문제 vs 냉매 부족 vs 컴프레서 차압형성 불량
- 주차브레이크 케이블 행정불량 vs 브레이크 어셈블리 자체 holding 불량

## 검증
- Expert: 64 symptoms / 268 causes / 8,040 simulations / 0 errors / 0 warnings
- T/M: 24 graphs / 151 results / 4,530 simulations
- Electrical: 38 graphs / 373 nodes / 205 results / 6,150 simulations / 0/0
- D24 engine: 21 graphs / 110 results / 3,300 simulations / 0/0
- Field location: 17 zones / electrical 38/38 / expert systems 9/9 / 0/0
- Engine locator: 18 items / 12 zones / focused p211 evidence views 5 / 0/0
- Specificity: unresolved cross-cause shared signatures 0
- Diagnostic-first UI priority: PASS

## 아직 COMPLETE가 아닌 이유
- 전장 38개 중 strict TARGET 17, source-limited 21은 exact connector cavity/option schematic/analog transfer curve 등의 OEM 근거가 더 필요함.
- 논리 시뮬레이션은 실차 반복시험이 아님.
- Work/GitHub Actions에서 실제 APK 빌드 후 release SHA/화면/asset을 확인해야 최종 통합판정.
