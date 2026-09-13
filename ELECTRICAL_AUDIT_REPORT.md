# D20/25/30/33S(SE)-7 electrical diagnostic audit

## OEM source
- Manual: SM1018-01, July 2016
- Vehicle electrical schematic: **600123-00120**
- Sheets: 1/4, 2/4, 3/4, 4/4
- App OEM pages: p367.jpg, p368.jpg, p369.jpg, p370.jpg

## Root cause of the app gap
The app stored chapter 9 schematic pages as images but did not normalize electrical circuits into diagnostic data. Therefore symptoms such as a failed brake lamp had no fuse/switch/connector/pin/load/ground diagnostic chain.

## New diagnostic contract
Every electrical symptom must provide:
1. schematic ID + sheet + grid,
2. circuit components in order,
3. fuse/source information if verified,
4. connector/pin information if verified,
5. physical measurement point,
6. expected electrical state,
7. branch on result,
8. rule-outs,
9. confirmation condition,
10. repair/disassembly gate.

Unknown OEM data may not be guessed. It stays marked as OEM VERIFY/UNKNOWN.

## Brake-lamp graph
Source: 600123-00120 (4/4), F6 → I7~I8.

Verified visible components:
- FUSE BOX at E5~E6
- STOP LAMP SW at F6
- STOP LAMP SW connector: 2 pins, drawing orientation pin 2 upper / pin 1 lower
- COMB LAMP-RH at I7
- COMB LAMP-LH at I8
- rear combination lamp functions: T/S / STOP / TAIL / GND / BACK-UP

Executable diagnostic sequence:
- both lamps vs one-side only,
- switch supply test,
- switch output test with pedal action,
- RH/LH STOP terminal voltage,
- common harness vs side branch isolation,
- GND voltage drop,
- lamp/bulb test.

OEM service table confirms 12 V 27/8 W stop/tail bulb rating. Exact STOP-only fuse cavity/rating is intentionally unresolved in this revision because the stored raster is not legible enough to verify it safely.

## Coverage
13 electrical symptoms are executable graphs, not static menu entries.

Validation: 13 graphs / 136 nodes / 74 result nodes / errors 0 / warnings 0.

## OSS / 시트 인터록 간헐고장 추가 (v3)
- OEM 회로도 `600123-00120 (1/4)`에서 `OSS CONTROLLER`와 `SEAT SW` 기능 입력을 확인. 숫자 terminal 번호는 현재 raster 해상도로 확정하지 않아 `OEM VERIFY` 유지.
- 매뉴얼 동작원리상 운전자 착석 정상 상태에서는 리프트 락 솔레노이드가 개방 상태를 유지하고, 이석 시 제어 신호로 닫혀 하강을 차단. 리프트 락 솔레노이드 코일은 12 VDC, NC 타입.
- 새 그래프 `E_OSS_SEAT_LOCK`: 센서 점퍼 → OSS 입력 백프로브 → 구간 분할 wiggle test → MIN/MAX/부하 전압강하 → 핀 장력/밀림/크림프 → OSS 전원/GND → 리프트락 출력 → 솔레노이드/유압부 순으로 진단.
- 정적 연속성 정상만으로 `배선 정상` 판정 금지. 흔들림에 증상이 반응하면 간헐 접촉불량 검사를 강제.

## OSS / 시트락 실제 현장 사례 반영 (v4)
- 실제 사례: 시트 센서 정상, 센서배선 점퍼 우회 후에도 시트락 유지, 정적 배선/전원 정상, 하네스 흔들림 시 간헐 해제.
- 기존 v3의 문제: `흔들림 반응 = 배선/터미널`로 너무 빨리 좁힐 수 있었음.
- v4 수정: 흔들림은 원인 확정이 아니라 재현 트리거로만 취급.
- 새 핵심 분기: `SEAT SW 입력 확인 → OSS 5V 기준/풀업 상태 → 외부 5V 부하 분리 → 진단기 OSS 통신 → 다른 CAN 모듈 통신 비교 → OSS 커넥터 CAN HI/LO 실신호 → OSS 내부고장 확정`.
- OSS 회로도 600123-00120 (1/4)에는 OSS CONTROLLER에 `SEAT SW`, `BAT+`, `IGN`, `GND`, `CAN HI`, `CAN LO` 기능이 확인됨.
- 매뉴얼 정기점검표의 OSS controller 보호퓨즈 정격은 15A. 정확한 fuse-box cavity 번호는 현재 raster에서 OEM VERIFY 유지.
- 5V는 현장 진단상 OSS 생존/내부 논리전원 판단에 사용하되, 현재 매뉴얼에서 허용오차가 확인되지 않아 4.8~5.2V 같은 임의 합격범위는 만들지 않음.
- CAN 판정 규칙: 다른 모듈까지 모두 진단불가면 공통 CAN/DLC 문제 우선. 다른 모듈은 통신되는데 OSS만 미응답이고, OSS 전원/GND·로컬 CAN 배선/파형이 정상이라면 OSS 내부 CAN 트랜시버/CPU 고장을 강하게 판정.
- 5V 비정상 + OSS 단독 CAN 미응답이 동시에 발생해도, 외부 5V 센서/배선 단락을 먼저 분리한 후 OSS 내부고장 확정.
- 일반 CAN의 약 60Ω 종단저항은 참고값일 뿐, 이 모델의 OEM 토폴로지 확인 전 자동 합격기준으로 사용하지 않음.
