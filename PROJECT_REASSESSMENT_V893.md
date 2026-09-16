# V8.9.3 전체 재검토 · 10 PASS AUDIT

기준 브랜치: `v18-rc-auto`
검토 기준 HEAD: `0c823ebfdf7f21efe143d4a6c3201db8c8a91e1d`

이 문서는 “같은 validator를 10번 돌렸다”는 의미가 아니다.
서로 다른 실패축을 10회 독립적으로 검토하고, 각 결과를 다음 검토와 재작성 설계에 반영한 기록이다.

## 1. 요구사항/역사 일관성
- 현장 순서: 측정/비교 → 격리 → 확정 → 분해 → 부품.
- 부품번호가 진단 PASS 조건이 되어서는 안 됨.
- OEM 미확정 수치/핀/포트는 추정 금지.
- 번호판등은 다른 미등 상태를 먼저 한 점으로 묻고 로컬/공통 경로를 분리.
- 회로/사진은 실제 pinch zoom + pan 검증 필요.

## 2. 매뉴얼/정규화 범위
- 64 symptoms / 268 causes.
- cause당 30 logic conditions = 8,040 logic simulations.
- transmission 24 graphs / 151 terminals / 4,530 paths.
- electrical 38 graphs / 205 result terminals / 6,150 simulations.
- D24 engine 21 graphs / 110 terminals / 3,300 simulations.
- 이 수치는 실차 8,040대 시험이 아니라 논리 스트레스 테스트임.

## 3. 현장진단 원칙
- 브레이크 내부누설은 외부누유/에어/마스터·서보/좌우 액슬 격리를 거쳐 분해 gate로 진행.
- 40 bar는 master-cylinder relief cracking pressure이며 axle piston seal leak threshold로 쓰지 않음.
- T/M Tap 역할/온도/RPM은 OEM 근거 순서를 유지.
- loaded voltage/drop이 필요한 전장은 open-circuit “12V 있음”만으로 PASS하지 않음.

## 4. Work/Actions 행동
- 브랜치에 다수의 emulator API/arch/timeout/retrigger 변경이 누적됨.
- 실패 원인 확인보다 환경 변경→재실행 패턴이 길게 이어진 구간이 있었음.
- 앞으로 동일 종류 실패 2회 이후 새 증거 없이 재시도 금지.

## 5. 최신 APK identity
- 최신 build job 자체는 성공.
- APK 내부 release/state/version/branch/SHA가 HEAD와 일치함.
- 옛 v0.8.7 artifact 문제와 현재 문제를 혼동하지 않음.

## 6. 최신 runtime 실패 원인
- emulator는 느리지만 실제로 boot 완료됨.
- instrumentation app/test compile 완료.
- 3개 테스트 모두 기능 중간이 아니라 START helper 첫 UI assertion에서 실패.
- 따라서 API 변경부터 할 문제가 아니며 launch/view assertion 설계부터 바로잡아야 함.

## 7. build/runtime source parity
- push build는 `apply_v891_runtime_integration.py`로 checkout 소스를 변형.
- runtime-ui는 clean checkout을 별도 빌드하며 그 변형 단계를 생략.
- 따라서 빌드된 APK와 runtime test source가 동일하다는 보장이 없었음.
- V8.9.3은 runtime integration을 source에 커밋하고 CI source-generation을 제거.

## 8. validator 의미
- 기존 V8.9.2 validator는 문자열/JSON/메서드 존재 검사가 중심.
- 정적 PASS != 실제 화면 PASS.
- V8.9.3은 JSON branch simulation + stable UI anchors + ActivityScenario/Espresso + real gesture test를 분리.

## 9. 보고서 authoritative 상태
- 최신 artifact에 옛 21-graph reassessment와 현재 38-graph reports가 같이 존재.
- 시대가 다른 보고서를 한 artifact에 섞지 않음.
- V8.9.3 이후 authoritative current-state report만 최종 검증의 근거로 사용.

## 10. 실행/릴리스 전략
- push: 빠른 static/data/build candidate gate만.
- runtime: Work가 final candidate commit을 확정한 뒤 수동 1회.
- runtime 실패 시 hierarchy XML + screenshot + Android test report를 증거로 남김.
- blind retry 금지.
- runtime 8개 required screenshot + test PASS + exact SHA metadata가 모두 맞을 때만 VERIFIED APK 업로드.

## V8.9.3 변경 핵심
1. V8.9.1 runtime integration을 생성단계가 아니라 committed source로 고정.
2. 번호판등 quick point에 stable accessibility test id 부여.
3. electrical graph/circuit/zoom에 stable runtime test id 부여.
4. `FLAG_ACTIVITY_CLEAR_TASK` + UiAutomator text polling launch gate 제거.
5. `ActivityScenario`/Espresso로 실제 Activity lifecycle과 화면을 검증.
6. UiAutomator는 실제 pinch/drag 및 screenshot에만 사용.
7. 실패 시 hierarchy/screenshot 자동 보존.
8. runtime-ui를 every-push build와 분리.
9. KVM 권한 문제가 실제 로그에 확인된 경우에만 권한 조정.
10. candidate APK와 runtime-VERIFIED APK를 명확히 구분.

## 실패 증거 보존 추가 규칙
- instrumentation 실패 시 즉시 emulator를 버리지 않는다.
- FAIL screenshot/window hierarchy를 host로 pull한 뒤 원래 실패코드를 반환한다.
- 같은 실패를 다시 돌리기 전에 이 증거를 먼저 읽는다.
