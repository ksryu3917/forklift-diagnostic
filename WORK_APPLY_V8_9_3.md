# Work 적용 지시 · V8.9.3 FIELD REBUILD

대상: `ksryu3917/forklift-diagnostic` / `v18-rc-auto`

## 절대 규칙
- 이 ZIP을 현재 `v18-rc-auto` HEAD 위에 overlay한다.
- 먼저 `python3 tools/apply_v893_rebuild.py .`를 **한 번만** 실행한다.
- 그 결과로 변경된 MainActivity/Manifest/TestPoint/Electrical/Zoom/build.gradle/release JSON을 모두 같은 커밋에 포함한다.
- build를 통과시키기 위해 source를 CI에서 다시 생성하지 않는다.
- 빈 `retrigger` 커밋을 만들지 않는다.
- 같은 종류 실패는 로그상 새 증거 없이 3번째 재시도하지 않는다.
- emulator API/arch/timeout을 동시에 바꾸지 않는다.

## 적용 전 확인
현재 HEAD와 변경파일을 기록한다.
V8.9.1 D24 runtime integration, V8.9.2 QUICK UI 데이터, 268/268 expert, 38/38 electrical,
21/21 D24 engine, 271 measurement points를 삭제/축소하지 않는다.

## 적용 순서
1. ZIP overlay.
2. `python3 tools/apply_v893_rebuild.py .`
3. `python3 tools/validate_v893_project_integrity.py .`
4. 기존 전체 validator 실행.
5. `gradle :app:assembleDebug` 로컬/Actions build 확인.
6. source diff를 확인하고 **한 개의 기능 커밋**으로 `v18-rc-auto`에 반영.
7. push candidate build가 성공한 뒤에만 `V8.9.3 Final Runtime Gate`를 workflow_dispatch로 1회 실행.
8. runtime 실패 시 즉시 재실행하지 말고 Android test report + FAIL hierarchy/screenshot을 먼저 읽는다.
9. 원인을 특정한 수정만 새 커밋으로 반영한다.
10. runtime 3 tests + required 8 screenshots + APK SHA metadata가 모두 PASS일 때 최종 APK로 인정.

## 최종 identity
- versionCode: 37
- versionName: `0.18-rc-expert-v8.9.3-field-rebuild`
- state: `RC EXPERT V8.9.3 FIELD REBUILD`
- branch: `v18-rc-auto`
- APK `diagnostic_release.json.git_commit_sha` = workflow commit SHA

## 번호판등 필수 실화면
- 시작: LP1 `다른 미등/후미등 정상 여부` 한 점
- LP1 정상 → LP2 `번호판등 +전원` 한 점
- LP2 정상 → LP3 `번호판등 접지 전압강하` 한 점
- LP3 정상 → `전구/소켓 접촉 영역`에서 종료
- LP1 이상 → LP4 공통 LAMP 경로
- 빠른진단에서 4개 측정폼 동시 노출 금지

## Zoom 필수 실화면
- E_LICENSE_NO에서 회로 근거 열기
- 고장 전용 재작성 회로 클릭
- zoom dialog 표시
- pinch 후 screenshot 변화
- drag 후 screenshot 변화

## Validator version rule
- V8.9.3 final gate uses `validate_v893_quick_ui.py`; do not use the old V8.9.2 release-identity check as a final release gate.
