# FULL REASSESSMENT · D20/25/30/33S(SE)-7 field diagnostic app

## Verdict

**현재 정규화된 정비지침서 범위는 현장 전문가 형식으로 전수 상승했지만, 차량 전체 진단 앱을 “완료”라고 판정하면 안 된다.**

- Manual scope: **64 symptoms / 268 causes**, all expert-format.
- A OEM-executable: **127**
- B field-isolation executable: **141**
- Cause-level logic stress simulations: **8,040** (30 per cause)
- Transmission: **24 graphs / 151 result terminals / 4,530 logic paths**
- Electrical: **21 graphs / 215 nodes / 117 results / 3,510 logic paths**
- Current validator errors: **0 / 0 / 0** (field / electrical / expert)

## Area-by-area judgement

| Area | Status | Evidence | Remaining gap |
|---|---|---|---|
| 정비지침서 64증상/268원인 | **PASS_EXPERT_FORMAT** | 268/268 cause items; A=127, B=141 | B등급은 OEM 숫자/핀 한계가 없는 항목으로 비교·격리 기반. 수치가 확보되면 A로 승격. |
| 트랜스미션 실행 그래프 | **PASS** | 24 graphs / 151 terminals / 4530 path simulations | 실차 로그 축적 후 확률/우선순위 보정 필요. |
| 브레이크 내부누설/피스톤시일 | **PASS_FIELD_LOGIC** | 외부누유→에어→마스터/서보 vs 액슬 격리→좌/우 격리→유체 이동→분해 gate | OEM 전용 leakage-rate 수치가 없는 경우 임의 bar/sec 기준 사용 금지. |
| 전기/차체전장 현재 카탈로그 | **PASS_CURRENT_CATALOG** | 21 graphs catalog / 117 result terminals / 3510 logic simulations | 차량 전체 전장기능을 모두 개별 증상화한 것은 아님. 아래 gap 항목 추가 필요. |
| 재작성 회로 UI | **PASS_ARCHITECTURE** | 모든 실행 전장 circuit에 simplified_diagram + measure_points; OEM 원본은 secondary evidence | 미확정 connector/fuse numeric ID는 고해상도 OEM source 확보 후 확정. |
| OSS/시트 인터록 | **PASS_FIELD_LOGIC / PARTIAL_PINOUT** | 센서 점퍼→OSS 입력→5V→외부 5V 부하 격리→CAN→B+/IGN/GND→출력 | OSS 커넥터 전체 숫자 pin map과 5V branch별 OEM 정상범위는 추가 source 필요. |
| A/C 냉매 진단 | **PASS** | OEM pressure condition: RECIRC, 30~35C, 1500rpm, blower4, COOL; LOW 1.5~2.5bar / HIGH 13.7~15.7bar | 냉매 회로와 실내 blower 공기측을 분리해 재작성 완료. |
| A/C 전원/콘덴서팬 | **PASS_FIELD_LOGIC / PARTIAL_PINOUT** | 전원 dead / blower dead / cooling command + condenser fan B+/GND/direct power/relay-driver split | A/C 전용 fuse cavity, fan relay exact ID, controller numeric pinout은 현재 OEM source 미확정. |
| CAN 진단 | **PASS_FIELD_LOGIC / PARTIAL_TOPOLOGY** | global vs single-node→node power/GND→local CAN H/L→5V external-load isolation→controller | 이 모델의 종단저항 위치/전체 topology가 OEM 검증되기 전 60Ω을 모델 기준으로 하드코딩하지 않음. |
| D24NAP 엔진 진단 | **MAJOR_GAP** | 현재 앱 엔진 화면은 D34 참고자료이며 D24 전용값으로 사용하지 않는다고 표시 | D24NAP 950106-01198 전용 자료의 sensor/switch/harness/ECU/engine troubleshooting을 실제 DB로 ingest해야 함. |
| 전장 전체 증상 universe | **GAP** | 600123-00120 1/4~4/4에서 현재 21개 주요 증상만 실행 그래프화 | seat belt switch, license lamp, hourmeter 개별, 각 gauge 개별, MAIN relay/ECU power, D24 ECU sensor/actuator 개별, optional circuits를 독립 증상그래프로 확장. |
| Cab/wiper/washer 및 옵션장비 | **SOURCE_REQUIRED** | 현재 확보된 600123-00120 4-sheet 범위만으로 모든 cab option 회로를 확정할 수 없음 | 해당 옵션 전장 회로/connector view 자료 확보 필요. |
| 부품번호/가격/공임 | **GAP** | 진단 확정까지는 강화됐으나 모든 원인에 Parts Book part number/price/labor가 연결된 상태는 아님 | Parts Book + 실제 매입/영수증 DB 연동 필요. |

## Design rule now enforced

1. Primary diagnostic screen is an assistant-redrawn fault-specific schematic, not an OEM page copy.
2. A terminal diagnosis requires: measurement/comparison point → rule-outs → confirm condition → teardown/replacement gate.
3. Electrical “continuity OK” never clears wiring by itself when the complaint is intermittent or load-dependent; loaded voltage drop/backprobe/dynamic reproduction is required where applicable.
4. Controller condemnation requires controller power/GND plus its communication/reference-voltage/external-load isolation as relevant. The OSS 5V + CAN case is now the reference quality example.
5. Unknown OEM pins/fuse cavities/thresholds stay UNKNOWN/OEM VERIFY; they are never invented.

## Release decision

**RC EXPERT can be used as a field-diagnostic development build for the covered scope, but not as a “complete vehicle diagnosis” release.**
The next mandatory source-normalization target is D24NAP engine data, followed by full electrical connector/pin/fuse normalization and option/cab circuits.

## External cross-checks used in this reassessment

- Doosan D20S-7 Operation & Maintenance Manual: fuse/relay service information and model-family operating information.
- Doosan D24NAP O&M Manual 950106-01198: confirmed dedicated chapters for electric circuit, switches/sensors, wire harness and ECU; source identified for ingestion.
- Fluke automotive voltage-drop guidance: supports load-state voltage-drop and ground-side testing; generic numerical limits are not promoted to OEM forklift criteria.
- MOTOR 5V-reference diagnostic cases: supports isolating external 5V loads/wiring before condemning a controller and correlating dead reference with no-communication patterns.
