# DIAGNOSTIC SPECIFICITY AUDIT V8.3.1

이 검증은 서로 다른 원인이 완전히 같은 측정점/점검순서/확정조건/분해조건으로 처리되는지를 찾고, 그 공유가 합리적인 “같은 원인 재사용/같은 어셈블리 내부 한계”인지 구분한다.

- Total causes: **268**
- Individually distinct full signatures: **202**
- Same-root-cause reuse accepted: **22 causes / 10 groups**
- Explicit shared-assembly boundary accepted: **44 causes / 16 groups**
- Explicit cause-specific pre-teardown gates present: **62**
- Unresolved cross-cause shared signatures: **0 causes / 0 groups**

## Quality rule

- 같은 원인이 여러 증상에서 동일한 시험으로 확인되는 것은 정상적인 재사용이다.
- 서로 다른 세부원인을 분해 전 구분할 수 없으면 앱은 세부부품을 확정하지 않고 `SHARED_ASSEMBLY_BOUNDARY`까지로만 판정해야 한다.
- 분해 전 구분 가능한 원인은 `CAUSE_SPECIFIC_PRE_TEARDOWN` 분리시험이 있어야 한다.
- unresolved cross-cause group이 1개라도 있으면 “모든 원인이 전문가 수준으로 분리됨”이라고 선언하지 않는다.

## Unresolved groups

- 없음

## Accepted shared-assembly groups
- 드라이브 액슬 · 5 causes → **드라이브액슬/디퍼런셜 내부 기어계통 고장**
- 드라이브 액슬 · 2 causes → **드라이브액슬 윤활유 규격 오류**
- 마스트 · 2 causes → **리프트/틸트 실린더 내부 바이패스**
- 브레이크 · 3 causes → **브레이크밸브/서보 제어 내부 스프링·릴리프 계통 고장**
- 브레이크 · 3 causes → **드라이브액슬 습식브레이크 내부 누설/피스톤 계통**
- 브레이크 · 2 causes → **마스터/서보 내부 바이패스 중 서보피스톤 구간**
- 스티어링 · 3 causes → **우선순위밸브 체크/릴리프 내부 제어계통**
- 스티어링 · 2 causes → **스티어링 실린더 내부 누설/마모**
- 유압 · 4 causes → **메인 유압펌프 내부마모/용적효율 저하**
- 유압 · 3 causes → **유압펌프 샤프트시일 실패**
- 작업장치 · 3 causes → **메인 컨트롤밸브 오염/이물 계통**
- 작업장치 · 2 causes → **컨트롤 레버/링케이지 정렬불량**
- 작업장치 · 2 causes → **컨트롤밸브 복귀스프링 손상**
- 작업장치 · 2 causes → **리프트 체크밸브 밀폐불량**
- 트랜스미션 · 3 causes → **트랜스미션 내부 기계계통 고장**
- 트랜스미션 · 3 causes → **토크컨버터 내부 성능/원웨이 계통**
