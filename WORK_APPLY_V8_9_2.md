# Work 적용 지시

`forklift_v8_9_2_quick_ui_hotfix.zip`을 `ksryu3917/forklift-diagnostic`의 `v18-rc-auto` 최신 V8.9.1 위에 overlay 적용한다.

필수 확인:
1. 기존 V8.9.1 D24 runtime integration은 유지한다.
2. `versionCode=36`, `versionName=0.18-rc-expert-v8.9.2-quick-ui`, state=`RC EXPERT V8.9.2 QUICK UI`.
3. `python3 tools/validate_v892_quick_ui.py .` 포함 전체 Actions validator 통과.
4. 번호판등 빠른진단 실화면 확인:
   - 처음에는 `다른 미등/후미등 정상 여부` 한 점만 보일 것.
   - 정상 선택 → `번호판등 +전원`.
   - +전원 정상 → `번호판등 접지 전압강하`.
   - +전원/접지 모두 정상 → `전구/소켓 접촉 영역`에서 멈출 것.
   - 다른 미등도 이상 선택 → 공통 LAMP relay/light switch 경로로 갈 것.
   - 기본 화면에서 4개 포인트 입력폼을 한꺼번에 펼치지 않을 것.
5. 전장/엔진/전문가 진단도 현재 질문 또는 `바로 측정`이 먼저 보이고 상세 근거는 접혀 있을 것.
6. 회로/사진을 누르면 pinch zoom/drag/double tap이 실제 동작할 것.
7. Generic `SOURCE → CONTROL/HARNESS → LOAD/SIGNAL → GND` 포인트맵이 전장 화면에 다시 보이면 실패.
8. GitHub Actions로 APK를 새 커밋에서 빌드하고 artifact SHA와 APK 내부 diagnostic_release.json SHA/branch/version/state 일치 확인.
9. 마지막에는 설치 가능한 실제 `.apk` 파일을 가져온다.
