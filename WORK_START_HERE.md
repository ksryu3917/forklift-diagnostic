# 지게차정비프로그램 V20 CLEAN REBUILD — WORK START HERE

이 문서가 이번 재구축의 최상위 실행 지시다.
이전 V8.x ZIP을 순서대로 덧붙이지 않는다.
기존 소스/오버레이/대화는 "요구사항과 검증 증거"로만 사용하고, 앱 런타임 소스는 새로 작성한다.

## 0. 왜 리셋하는가

2026-09-20 확인 기준:
- repository: `ksryu3917/forklift-diagnostic`
- branch: `v18-rc-auto`
- remote HEAD: `1357050c66311945cad45493f1ff043a12ddf85a`
- 위 HEAD는 parent `c84c7a1b8db09733cd0d4009052b48d366e2b398` 위에
  `candidate-9035a4a.bundle.b64.txt` 파일 1개만 추가한 commit이다.
- 기대 candidate `9035a4ae103a1f699a48ba1a63386a63f5290485`는 GitHub commit object로 존재하지 않는다.
- 즉 "원격 branch HEAD", "bundle 안 candidate", "여러 대화창에서 만든 overlay"가 서로 분리되어 있었다.

이 상태에서 기존 overlay를 더 얹지 않는다.

## 1. 새 단일 기준

새 브랜치: `v20-clean-rebuild`

새 identity:
- release: `v20`
- state: `CLEAN REBUILD ALPHA`
- versionCode: `100`
- versionName: `0.20.0-clean-alpha.1`
- applicationId: `com.ryu.forkliftdiagnostic` 유지
- source_branch: `v20-clean-rebuild`
- git_commit_sha: 빌드 시 실제 candidate SHA로 자동 stamp

`PROJECT_STATE.json`이 유일한 프로젝트 상태 파일이다.
버전/기능수/검증결과를 Java, workflow, validator 여러 곳에 따로 hard-code하지 않는다.

## 2. 브랜치/소스 처리

1. 현재 `v18-rc-auto` HEAD를 history anchor로 확인한다.
2. `v20-clean-rebuild`를 생성한다.
3. 기존 런타임 Java/UI 코드는 새 앱에 복사하지 않는다.
4. 기존 자료 중 다음은 "마이그레이션 입력"으로만 사용한다.
   - 기존 268 expert causes
   - 38 electrical graphs
   - D24 21 engine graphs
   - transmission 24 graphs / 151 terminals
   - manual library catalog
   - test-point / measurement worksheet / location-map 데이터
   - 번호판등 terminal-stop 동작 계약
   - pinch zoom + pan + double-tap 동작 계약
   - 다중 제조사 / exact-model scope 계약
   - STUDY 요구사항
   - 전동/리치 field EV 요구사항
5. 기존 `apply_v*.py` overlay 체인은 새 앱 소스 생성에 사용하지 않는다.
6. 각 구 데이터는 새 schema로 변환 후 validator를 통과한 것만 `app/src/main/assets/v20/`으로 가져온다.

## 3. 새 앱 UX — 이 구조 외에 임의 재설계 금지

홈:
1. 현재 차량: 제조사 + 모델 + 동력원 + 전압/사양
2. 차량 선택
3. 차량 진단
4. STUDY
5. 매뉴얼 라이브러리
6. 부품/가격/공임
7. 정비 이력
8. 내 현장 경험
9. 앱/데이터 상태

진단:
`차량 → 증상 검색/계통 → 안전조건 → 지금 할 한 가지 점검 → 입력 → 판정 → 다음 한 가지 → 원인 격리 → 분해 게이트 → 정비방법/부품`

한 화면에 4~5개 입력폼을 미리 펼치지 않는다.
번호판등에서 검증된 "한 점씩 진행" UX를 전체 진단러너의 기본으로 사용한다.

STUDY:
- 진단과 분리된 독립 메뉴
- 전동/리치/디젤/가스 등 동력원별 기본기
- 제조사/차종 차이를 명시
- 그림/재작성 회로/측정 위치 중심
- 절차가 모델별로 다르면 exact-model 선택 후에만 실행 절차 노출
- unknown model에서 숫자/핀/절차 추정 금지

## 4. 현장 진단 품질 계약

모든 증상/원인은 최소 다음 필드를 가져야 한다.

- `safety_preconditions`
- `first_observation`
- `test_location`
- `tool`
- `operating_condition`
- `measurement_or_action`
- `expected_basis` = OEM numeric / OEM procedure / normal-side comparison / isolation
- `result_branches`
- `rule_out`
- `confirm_if`
- `next_action`
- `teardown_gate`
- `do_not`
- `evidence_refs`
- `vehicle_scope`

원인명만 나열하거나 "점검한다", "확인한다"로 끝나면 FAIL.
분해 전에 확인 가능한 원인은 반드시 pre-teardown isolation이 있어야 한다.
분해 전 구분 불가능한 경우 어셈블리 경계까지만 확정한다.

## 5. P0 실제 현장 회귀사례

`requirements/p0_regressions.json`의 모든 사례는 앱에서 처음부터 끝까지 실행 가능해야 한다.

특히 `EV_REACH_NO_TRAVEL_MECH_001`:
- 리치
- 전원 정상
- 주행 불가
- 주행 명령 때 모터 상단 브레이크 디스크/모터축은 회전
- 커플링 정상
- 차량을 안전하게 띄우면 구동휠은 회전하지만 모터까지 쿵쿵 충격
- 브레이크를 OEM 절차로 해제하고 손회전 시 특정 위치에서 떡떡 걸림
- 앱은 모터/컨트롤러 교환으로 가지 않고
  `안전 리프트 → 무부하 회전 → 브레이크 해제 → 손회전/주기성 걸림/백래시 → 모터축-감속기입력-출력-휠 동시성 → 오일/금속편 → 감속기/기어/베어링/스플라인 분리`
  흐름을 제공해야 한다.
- 이 흐름 전에 모터/액슬 분해를 지시하면 FAIL.

이 실제사례는 전동/리치 진단의 최소 기준이지 고급 기능이 아니다.

## 6. 검증 기준

"30회 검증"의 정의:
- 같은 validator를 30번 반복하는 것이 아니다.
- 각 개별 결과 terminal/원인마다 최소 30개의 서로 다른 입력 조건·경계·오류·정상 조합을 생성한다.
- 동일 path를 seed만 바꿔 반복한 것은 카운트하지 않는다.
- 각 시나리오에서 합법 branch, terminal 도달, scope, teardown gate, evidence 계약을 검증한다.

필수 gate:
1. repository/state audit
2. schema
3. model scope / cross-brand leakage
4. diagnostic graph
5. P0 real-field regressions
6. legacy migration parity
7. static Android source
8. APK build
9. instrumentation APK build
10. actual runtime UI
11. screenshot/window-hierarchy evidence
12. APK internal release/state/version/source_branch/git_commit_sha
13. APK SHA == GitHub candidate SHA
14. VERIFIED APK

정적 PASS를 실제 화면 PASS라고 보고하지 않는다.
논리 simulation을 실차 검증이라고 부르지 않는다.

## 7. runtime 필수 화면

기존 8장 증거는 유지:
1. 번호판등 LP1
2. LP2 +전원
3. LP3 접지 전압강하
4. 전구/소켓 terminal stop
5. 공통 LAMP branch
6. zoom before
7. pinch after
8. drag after

V20에서 추가:
9. 제조사/모델 선택
10. STUDY 홈
11. STUDY exact-model scope stop
12. 전동/리치 실고장 `모터 회전 + 차 안 감` 첫 점검
13. 차량 띄움/브레이크해제/손회전 branch
14. 기계적 걸림 → 감속기/액슬 isolation result
15. 배터리 "완충 후 3시간" V/A + 셀/비중 branch
16. release identity 화면

## 8. 실패 처리

실패하면 사용자에게 일반적인 기술 승인 질문을 하지 않는다.
`로그 확인 → 실패유형 분류 → 최소 수정 → 동일 gate 재실행`으로 진행한다.

동일 원인의 runtime 실패를 증거 없이 반복 실행하지 않는다.
실패 시 screenshot + hierarchy XML + test report를 먼저 보존한다.

## 9. 최종 완료 보고 조건

다음이 모두 만족될 때만 "VERIFIED"라고 보고한다.
- 새 앱 코드가 legacy runtime source를 import하지 않음
- 마이그레이션 데이터 계약 충족
- 모든 validator 0 error
- P0 실제사례 PASS
- APK/instrumentation build PASS
- runtime 필수 화면 PASS
- evidence 보존
- APK 내부 identity와 GitHub candidate SHA 일치
- VERIFIED APK artifact 생성

중간에 "거의 완료", "validator 통과했으니 완료"라고 보고하지 않는다.
