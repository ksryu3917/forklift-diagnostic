# FIELD READINESS V7 · LOCATION + SPECIFICITY

## 현재 판정

**V8.3.1부터 268개 원인을 ‘모두 서로 다른 부품으로 억지 확정’하지 않는다. 분해 전에 구분 가능한 원인은 원인별 분리시험을 두고, 분해 전 구분이 불가능한 내부손상은 shared-assembly boundary에서 멈추도록 품질게이트를 적용했다. 현재 unresolved cross-cause 동일 진단체인은 0이다.**

## 핵심 수치

- 기존 정비지침서 원인: **268** · 모두 실행형 필드 구조 보유
- 원인별 pre-teardown 분리시험을 가진 항목: **62**
- 분해 전 세부부품 과확정을 막는 shared-assembly boundary: **44 causes / 16 groups**
- unresolved cross-cause 동일 진단체인: **0 / 0 groups**
- 전장: **38 graphs / 205 result terminals** · strict TARGET **17**, source-limited **21**
- D24 engine: **21 graphs / 110 result terminals**
- 차량 정비 위치맵: **17 zones** · electrical **38/38** graphs mapped · expert systems **9/9** mapped
- D24 sensor/actuator locator: **18 items**

## V8.3 위치맵 품질게이트

- 진단 화면에서 품번보다 **점검 위치 → 재작성 회로/유압 흐름 → 측정점 → 부하시험 → 격리/바이패스 → 확정**을 먼저 보여준다.
- 차량 전체 위치맵은 치수 CAD가 아니라 정비사용 빠른 locator다. 옵션/마스트/캐빈 사양에 따라 달라질 수 있는 위치는 정확 위치라고 단정하지 않는다.
- 엔진은 별도 D24 센서 위치맵에서 센서 위치·핀/신호·관련 진단을 연결하고 OEM 부품도/외형도를 근거로 연다.

## Specificity gate

- 같은 원인이 다른 증상에서 같은 시험을 공유하는 것은 정상적인 재사용으로 허용한다.
- 서로 다른 원인이 완전히 같은 측정점·점검순서·확정조건·분해조건을 공유하면 자동으로 “완전 독립 TARGET”으로 세지 않는다.
- 분해 전 물리적으로 구분 가능한 원인은 `원인별 분리시험`을 추가한다.
- 같은 어셈블리 내부에서 분해 전 구분이 불가능한 원인은 앱 결과도 세부부품을 확정하지 않고 **해당 어셈블리 내부고장** 수준에서 분해 게이트를 연다.

## 아직 남은 큰 구멍

- 전장 source-limited 항목의 정확 connector cavity / option schematic / analog transfer curve.
- cross-cause shared diagnostic family 중 외부에서 더 분리 가능한 원인들의 개별시험.
- 엔진 위치맵의 OEM 두 방향 장착도 기반 빠른 측면 선택/하이라이트 고도화.
- 실제 Work/GitHub Actions APK에서 화면·자산·release SHA 최종 통합검증.

## 완료판정 규칙

차량 전체 COMPLETE는 위 source-limited 전장과 specificity review가 해소되고, Work 빌드 APK의 실제 화면/자산/commit SHA까지 일치할 때만 선언한다.
