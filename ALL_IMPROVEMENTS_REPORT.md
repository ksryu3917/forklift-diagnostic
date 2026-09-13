# 지게차 정비 프로그램 — 현장 실행형 진단 전수 개선 보고

## 1. 기준 변경

기존 완료 기준은 **그래프가 연결되고 결과 노드까지 도달하는가**에 치우쳐 있었다. 이 기준으로는 `밸브 점검`, `시일 확인`, `내부누설 확인`처럼 정비사가 현장에서 무엇을 해야 하는지 빠진 결과도 통과할 수 있었다.

이번 수정부터 완료 기준을 아래처럼 변경했다.

**매뉴얼 근거 → 분해 전 확인 → 유사원인 배제 → 회로/부품 격리 또는 비교 → 실제 측정/관찰 → 확정 조건 → 분해 조건**

OEM/서비스 매뉴얼에 없는 압력강하량·시간·간극 등의 숫자는 새로 만들지 않는다. 숫자 근거가 없으면 정상측 비교, 상/하류 비교, 좌/우 비교, 격리 전/후 비교로 진단한다.

## 2. 이전 v18 검증의 한계

GitHub Actions #20의 실제 validation artifact 기준:

- 트랜스미션 그래프: 23
- 결과 종점: 144
- 결과당 시나리오: 30
- 총 시뮬레이션: 4,320
- 구조 오류/경고: 0/0

하지만 기존 검증기는 result 노드에 `result`와 `action`이 있는지만 보았고, **현장시험·배제조건·확정조건·분해조건의 존재를 검사하지 않았다.** 따라서 구조적으로는 정상이어도 현장 진단으로는 미완성일 수 있었다.

## 3. 전수 개선 범위

- 증상: 64개
- 원인: 268개
- 계통: 9개
  - 트랜스미션 92 원인
  - 드라이브 액슬 20
  - 유압 27
  - 작업장치 26
  - 마스트 8
  - 스티어링 38
  - 브레이크 45
  - 주차 브레이크 3
  - 에어컨 9

모든 원인에 다음 필드를 강제했다.

- `diag_plan`: 현장에서 순서대로 실행할 확인 절차
- `field_tools`: 필요한 공구/측정기
- `field_rule_out`: 먼저 배제해야 할 유사 원인
- `field_confirm`: 해당 원인을 높게 확정할 조건
- `disassembly_gate`: 언제부터 분해해도 되는지
- `field_evidence_mode`: OEM 수치 / 비교격리 / 수리후재시험 / 시각확정 등 판정방식
- `field_ready`: 현장실행 준비 여부

일반적인 “입력→출력 따라가며 점검” fallback은 전 계통에서 제거했다.

## 4. 브레이크 개선

### 피스톤 씰/내부누설

별도 `BRAKE_HYD_ISOLATION` 그래프를 추가했다.

1. 외부 누유 확인
2. 에어와 내부누설 페달감 분리
3. 마스터/브레이크밸브와 액슬 하류 회로 격리
4. 좌/우 액슬 회로 개별 격리
5. 의심측 외부누유 재확인
6. 리저버 감소 + 액슬오일 레벨/성상 변화 확인
7. 반복 재현 후 해당 측만 분해

**호스를 바이스그립으로 집지 않고 정식 유압용 블랭킹 플러그/캡을 쓰도록 명시했다.**

브레이크 피스톤/서보/마스터/브레이크밸브 시일 관련 10개 원인을 이 격리 그래프에 연결했다.

### 그 외 브레이크

- 컨트롤밸브 브레이크 공급부: 공통공급과 브레이크 포트 전후 압력 비교
- 체크밸브: 상/하류 압력 유지와 하류 격리로 일방향 유지기능 확인
- 릴리프/스풀 스프링: 페달 입력 대비 출력압 상승/복귀 비교 후 분해
- 브레이크밸브 풀림: 작동 중 몸체 이동/유효 스트로크 손실 확인 후 정상체결 재시험
- 브레이크밸브 결함: 입구공급 정상 + 하류격리 후에도 출력 이상일 때만 내부 분해
- 디스크/플레이트/피스톤 고착: 유압 잔압을 먼저 배제하고 좌우 휠저항·온도 비교 후 분해
- 외부누유/주조부 크랙: 세척·건조 후 신선한 누유 시작점을 재현

## 5. 트랜스미션 개선

기존 23개 그래프에 누락됐던 `SYM023 중립에서 변속 불능`을 추가하여 24개 그래프로 만들었다.

모든 result 종점에 다음을 강제했다.

- 현장 공구
- 현장 재현/확인 시험
- 배제해야 할 원인
- 확정 조건
- 분해 조건

특히 기존에 일반론으로 끝나던 종점을 다음처럼 수정했다.

- 인칭: STD 링크/감압스풀 완전복귀 또는 ECT 센서/비례밸브 지령 복귀 + 압력 변화 비교
- Tap1↔Tap6: 동일 유온/RPM에서 두 압력을 비교하여 펌프 공통저압과 중간 손실 분리
- 동시체결/잔압: F/R 선택에서 Tap4/Tap5 관계를 직접 확인하고 비선택압이 0인지 확인
- T/M 이후 무주행: 출력축→U조인트→액슬 입력의 실제 회전 전달 추적
- ECT: 레버/인칭 입력→컨트롤러 출력→비례밸브 실제작동→클러치압 확인
- 과열 표시: 실제 독립온도와 센서표시 비교
- 컨버터/쿨러: Tap6→Tap3→Tap2 조합과 입출구 온도로 구간 분리
- 1-way clutch: 엔진 출력 및 방향클러치 압력 정상 확인 후 양방향 stall/소음 패턴
- 정상 결과: 실제 증상 발생 조건을 재현하기 전 수리종료 금지

원인 DB 92개에도 동일 방식으로 현장 확인 로직을 적용해 일반론 fallback을 제거했다.

## 6. 스티어링 개선

- 실린더 내부누설: 메인/우선순위 공급 정상 → L/R 압력 비교 → 실린더/유닛 격리 → 기계 링크 배제
- 우선순위/릴리프: 입구와 스티어링 공급 전후 압력 비교, 조정은 고착/오염/스프링 확인 후 마지막
- 컬럼/유닛 정렬: 기계 걸림과 유압저압을 분리하고 정상 체결/정렬 후 재시험
- 스티어링유닛: 상류압 정상 + 하류 링크 정상 상태에서 L/R 출력과 스풀복귀 비교
- 스티어액슬/링크: 유압 제거 및 안전지지 후 무부하 기계 구속 확인
- 펌프 누유: 세척 후 실제 시작점 + 샤프트 유격/커플링 정렬 확인

## 7. 유압/작업장치 개선

### 유압

- 펌프 마모: 레벨/점도/흡입/구동/릴리프/대규모 하류누설을 먼저 배제
- 펌프 샤프트 시일: 누유 시작점 + 축유격/정렬 + 과열/조립이력 확인
- 과열의 시스템 내부누설: 중립/각 기능별 온도 상승 비교와 기능별 격리
- 실린더 외부누유: 호스/피팅 vs 로드글랜드 시작점 분리, 로드 손상/정렬 확인

### 작업장치

- 체크밸브: 공급압 정상 확인 후 역류/미착좌 확인, 세척 전후 재시험
- 스풀 이물: 링크 영향과 밸브 자체 걸림 분리, 오일/필터 오염원까지 처리
- 밸브바디 과다체결/뒤틀림: 체결응력 정상화 전후 스풀 이동 비교
- 링케이지/스트로크: 레버 이동과 실제 스풀 전스트로크 비교
- 스풀/리턴스프링: 외부링크·이물·체결응력 배제 후 자체 복귀 확인
- 밸브 시일/스풀마모: 세척 후 정확한 누유 시작점, 체결과 스풀보어 상태 분리
- 밸브몸체 크랙: 피팅/플러그/시일부 누유를 배제한 후 몸체 자체 누유 재현
- 유온 이탈: 실제 독립온도 측정 후 냉간/정상유온에서 스풀 반응 비교

## 8. 드라이브 액슬/마스트/주차브레이크/에어컨 개선

### 드라이브 액슬

오일 레벨/규격 → 외부 회전체 소음 배제 → 유격/백래시/회전저항 → 금속분/국부 청진 → 해당 내부부품 순으로 분리한다. 브리더 막힘, 오일시일, 축 길이, 베어링/체결부도 각각 별도 현장 절차를 만들었다.

### 마스트

로드/글랜드 외부누유, 로드 손상, 실린더 내부누설, 밸브 내부누설, 정렬불량, 와이퍼/오염을 서로 분리한다. 자연침하/전경시험은 OEM 절차가 있을 때 해당 값으로 판단하고, 없는 누설한계는 만들지 않는다.

### 주차브레이크

기존 잘못된 유압/펌프성 일반론을 제거하고 레버→케이블→캠/스트러트→밴드 이동/복귀→조정→유지성능 순으로 변경했다.

### 에어컨

R-134a 저압/고압을 지정조건에서 동시에 보고 냉매 부족·제한·컨덴서 방열·과충전·공기혼입·팽창밸브·컴프레서를 압력 조합과 온도로 구분한다. 한쪽 압력만 보고 냉매를 보충/배출하지 않도록 했다.

## 9. 엔진

현재 D20/25/30/33S(SE)-7의 D24 전용 엔진 정비자료가 아닌 G2-D34 자료는 **참고 자료로만 유지**한다. D34 수치/핀 정보를 D24 정상값으로 사용하지 않는다는 경고를 유지했다.

## 10. UI 개선 패치

`MainActivity` 원인/결과 화면에 다음 카드가 보이도록 소스 패처를 작성했다.

- 현장 공구
- 현장 확인/재현 시험
- 먼저 배제할 원인
- 확정 조건
- 분해 조건
- OEM 수치/자료 미연결 경고

기존 앱의 단순 `판정 + 다음 점검` 결과 화면으로 끝나지 않도록 한다.

## 11. 새 검증 기준 및 결과

새 `validate_field_diagnostics.py`는 다음을 검사한다.

- 268개 원인의 현장필드 완전성
- 트랜스미션 모든 결과 종점의 현장필드 완전성
- 그래프 링크/도달성/비결과 dead-end
- question choices
- measure min/max/unit/분기
- 관련 매뉴얼 이미지 asset 존재
- placeholder/TODO
- 브레이크 격리그래프 필수단계와 시일원인 연결
- 일반론 fallback 잔존 여부
- 각 트랜스미션 결과까지 30개 경로 시뮬레이션

최종 로컬 검증 결과:

- 64 symptoms
- 268 causes
- 24 T/M graphs
- 151 T/M result terminals
- 4,530 simulated paths
- Errors: **0**
- Warnings: **0**
- 일반론 cause fallback: **0**
- 일반론 T/M terminal fallback: **0**

## 12. 빌드/릴리즈 변경 준비

대상 버전:

- release: `v18`
- state: `RC FIELD`
- Android versionCode: `19`
- versionName: `0.18-rc-field`
- branch target: `v18-rc-auto`

Actions는 빌드 시 `diagnostic_release.json`에 실제 `github.sha`와 `github.ref_name`을 스탬프하고 APK 내부 값이 일치하는지 검증하도록 구성했다.

## 13. 현재 원격 상태

이 패키지는 마지막 성공 원격 커밋 `1be4dcc94bba3dbe8f005ceab1119e5bac099295`의 APK/DB를 기준으로 만든 **로컬 수정본**이다.

현재 채팅의 GitHub 연결은 읽기는 가능하지만 write 호출이 403 `Resource not accessible by integration`으로 차단되어 있으므로, 이 보고서의 수정사항을 원격 `v18-rc-auto`에 반영했다고 주장하지 않는다. 또한 이번 채팅은 이전 Work의 로컬 컴퓨터 세션 자체가 연결된 상태가 아니다.

따라서 **코드/DB/검증 패치는 완성**, **원격 커밋·실제 새 Actions APK 생성은 미실행** 상태다.

## Electrical / chassis electrical audit added after field feedback

The previous RC FIELD work still treated chapter 9 circuit drawings mainly as evidence images. That is not sufficient for a field diagnostic application. The electrical subsystem is now separately normalized from OEM schematic **600123-00120 (1/4~4/4)**.

### What was added
- `electrical_diag_v1.json`: 13 executable electrical symptom graphs / 136 nodes / 74 result terminals.
- `ElectricalDiagnosticActivity.java`: dedicated circuit-driven UI.
- Main-screen patch: **전기 / 차체전장 진단** entry, system entry, and search bridge.
- Relevant OEM sheet/grid is shown before measurements.
- Circuit component chain, connector pin data where actually readable, fuse reference where OEM text is explicit, test points, rule-outs, confirmation and repair/disassembly gate are shown.
- Relevant circuit crops are bundled for STOP LAMP so the technician does not need to search an entire schematic sheet.
- `validate_electrical_diagnostics.py`: fails on broken graphs, missing field confirmation data, missing OEM image assets, missing STOP switch pin array, or catalog items without executable graphs.

### STOP LAMP example now implemented
OEM source: `600123-00120 (4/4)`, F6 to I7~I8.

Flow:
1. Both sides vs one side failure.
2. STOP LAMP SW 2-pin connector input-power check.
3. Pedal-operated switch output check.
4. RH/LH combination-lamp STOP terminal voltage check.
5. Common harness vs one-side branch isolation.
6. Lamp GND voltage-drop check.
7. Lamp/bulb confirmation.

Verified from the stored circuit image:
- `STOP LAMP SW` exists at F6.
- Its connector is 2-pin; drawing orientation is upper terminal pin 2, lower terminal pin 1.
- RH/LH combination lamps identify `T/S`, `STOP`, `TAIL`, `GND`, `BACK-UP` terminal functions.
- Manual maintenance data specifies STOP/TAIL bulb capacity as **12 V 27/8 W**.

Deliberately NOT fabricated:
- The exact STOP-only fuse cavity number/rating is not reliably legible in the current stored raster circuit image.
- Which of STOP switch pins 1/2 is feed vs switched output is not hard-coded until the high-resolution original trace is verified.
- Numeric combination-lamp connector cavity mapping is not hard-coded where the raster is not legible.

The UI therefore instructs the technician to measure both STOP-switch terminals to identify feed/output and explicitly flags the unresolved OEM identity rather than inventing a pin role or fuse number.

### Other electrical graphs now covered
- Head lamps
- Turn signals / hazard
- Horn
- Back-up lamp / buzzer
- Starter no-crank
- Charging circuit
- Parking-brake electrical input / OSS path
- Lift-lock / unload solenoids
- Fuel / water-temperature / T/M-temperature indication
- Rear lamp / strobe / work-lamp path
- F/R switch and transmission solenoid electrical control

For F/R control, the manual procedure already provides exact values and the graph stores them: FWD/REV fuse #3; switch common 4↔7; forward 1↔2; reverse 1↔3; solenoid plunger approximately 3.18 mm.

### Validation after electrical normalization
- Existing mechanical/hydraulic field validation: 64 symptoms / 268 causes / 24 T/M graphs / 151 T/M terminals / 4,530 simulated result paths / 0 errors / 0 warnings.
- New chassis-electrical validation: **13 electrical symptom graphs / 136 nodes / 74 result terminals / 0 errors / 0 warnings.**

Remote GitHub write is still not claimed: the connected GitHub integration returns HTTP 403 on write operations. The patch is prepared for the `v18-rc-auto` checkout and the write/build step must be performed in a Work session or other environment with repository write permission.

## V8 · Parts Book / location / serial integration
- Integrated Doosan Parts Book SB5120C05 for D20/25/30/33S-7 D24 Tier4.
- Added diagnostic-to-parts linking for 268 expert causes, 36 electrical graphs, 21 D24 engine graphs.
- Added D24 ECU/harness/starter/glow and named sensor part references.
- Added A/C condenser-fan early/late serial split and compressor/harness/relay group reference.
- Added seat-belt interlock, OSS option group, parking-brake actuator parts.
- Added whole-truck Location Chart and relevant exploded-view assets.
- Exact part number is gated by model/Serial/options; generic sensor item identities are not guessed.


## V8.2 diagnostic-first priority update
- 품번/Serial 적합성은 정비 진단의 PASS 조건에서 제외. 실제 주문은 차대번호 기준 부품점/EPC 확인을 우선한다.
- Parts Book은 **부품 위치, 조립관계, 하네스/밸브/센서가 속한 그룹, exploded view** 확인에 우선 사용한다.
- 앱 화면 순서도 `점검 위치/재작성도/측정/격리/확정`을 앞에 두고 `분해도/참고 품번`을 결과 뒤로 내렸다.
