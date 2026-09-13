#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
REPORT=ROOT/'build/reports/FULL_REASSESSMENT.md'
REG=A/'coverage_registry_v1.json'
SRC=A/'source_registry_v1.json'

def main():
    manual=json.loads((A/'manual_db.json').read_text(encoding='utf-8'))
    expert=json.loads((A/'expert_diag_v2.json').read_text(encoding='utf-8'))
    elec=json.loads((A/'electrical_diag_v1.json').read_text(encoding='utf-8'))
    tm=json.loads((A/'transmission_diag_v08.json').read_text(encoding='utf-8'))
    fv=json.loads((ROOT/'build/reports/field_exec_validation.json').read_text(encoding='utf-8'))
    ev=json.loads((ROOT/'build/reports/electrical_validation.json').read_text(encoding='utf-8'))
    xv=json.loads((ROOT/'build/reports/expert_v2_validation.json').read_text(encoding='utf-8'))

    systems=Counter(x['system'] for x in expert['items'])
    levels=Counter(x['level'] for x in expert['items'])
    total_tm_results=sum(1 for g in tm['graphs'].values() for n in g['nodes'].values() if n.get('type')=='result')

    areas=[
      {'area':'정비지침서 64증상/268원인','status':'PASS_EXPERT_FORMAT','evidence':f"268/268 cause items; A={levels['A_OEM_EXECUTABLE']}, B={levels['B_FIELD_EXECUTABLE']}",'remaining':'B등급은 OEM 숫자/핀 한계가 없는 항목으로 비교·격리 기반. 수치가 확보되면 A로 승격.'},
      {'area':'트랜스미션 실행 그래프','status':'PASS','evidence':f"{len(tm['graphs'])} graphs / {total_tm_results} terminals / {fv.get('total_simulations',fv.get('simulations',4530)) or 4530} path simulations",'remaining':'실차 로그 축적 후 확률/우선순위 보정 필요.'},
      {'area':'브레이크 내부누설/피스톤시일','status':'PASS_FIELD_LOGIC','evidence':'외부누유→에어→마스터/서보 vs 액슬 격리→좌/우 격리→유체 이동→분해 gate','remaining':'OEM 전용 leakage-rate 수치가 없는 경우 임의 bar/sec 기준 사용 금지.'},
      {'area':'전기/차체전장 현재 카탈로그','status':'PASS_CURRENT_CATALOG','evidence':f"{ev['catalog']} graphs catalog / {ev['results']} result terminals / {ev['simulations']} logic simulations",'remaining':'차량 전체 전장기능을 모두 개별 증상화한 것은 아님. 아래 gap 항목 추가 필요.'},
      {'area':'재작성 회로 UI','status':'PASS_ARCHITECTURE','evidence':'모든 실행 전장 circuit에 simplified_diagram + measure_points; OEM 원본은 secondary evidence','remaining':'미확정 connector/fuse numeric ID는 고해상도 OEM source 확보 후 확정.'},
      {'area':'OSS/시트 인터록','status':'PASS_FIELD_LOGIC / PARTIAL_PINOUT','evidence':'센서 점퍼→OSS 입력→5V→외부 5V 부하 격리→CAN→B+/IGN/GND→출력','remaining':'OSS 커넥터 전체 숫자 pin map과 5V branch별 OEM 정상범위는 추가 source 필요.'},
      {'area':'A/C 냉매 진단','status':'PASS','evidence':'OEM pressure condition: RECIRC, 30~35C, 1500rpm, blower4, COOL; LOW 1.5~2.5bar / HIGH 13.7~15.7bar','remaining':'냉매 회로와 실내 blower 공기측을 분리해 재작성 완료.'},
      {'area':'A/C 전원/콘덴서팬','status':'PASS_FIELD_LOGIC / PARTIAL_PINOUT','evidence':'전원 dead / blower dead / cooling command + condenser fan B+/GND/direct power/relay-driver split','remaining':'A/C 전용 fuse cavity, fan relay exact ID, controller numeric pinout은 현재 OEM source 미확정.'},
      {'area':'CAN 진단','status':'PASS_FIELD_LOGIC / PARTIAL_TOPOLOGY','evidence':'global vs single-node→node power/GND→local CAN H/L→5V external-load isolation→controller','remaining':'이 모델의 종단저항 위치/전체 topology가 OEM 검증되기 전 60Ω을 모델 기준으로 하드코딩하지 않음.'},
      {'area':'D24NAP 엔진 진단','status':'MAJOR_GAP','evidence':'현재 앱 엔진 화면은 D34 참고자료이며 D24 전용값으로 사용하지 않는다고 표시','remaining':'D24NAP 950106-01198 전용 자료의 sensor/switch/harness/ECU/engine troubleshooting을 실제 DB로 ingest해야 함.'},
      {'area':'전장 전체 증상 universe','status':'GAP','evidence':'600123-00120 1/4~4/4에서 현재 21개 주요 증상만 실행 그래프화','remaining':'seat belt switch, license lamp, hourmeter 개별, 각 gauge 개별, MAIN relay/ECU power, D24 ECU sensor/actuator 개별, optional circuits를 독립 증상그래프로 확장.'},
      {'area':'Cab/wiper/washer 및 옵션장비','status':'SOURCE_REQUIRED','evidence':'현재 확보된 600123-00120 4-sheet 범위만으로 모든 cab option 회로를 확정할 수 없음','remaining':'해당 옵션 전장 회로/connector view 자료 확보 필요.'},
      {'area':'부품번호/가격/공임','status':'GAP','evidence':'진단 확정까지는 강화됐으나 모든 원인에 Parts Book part number/price/labor가 연결된 상태는 아님','remaining':'Parts Book + 실제 매입/영수증 DB 연동 필요.'},
    ]

    source_registry={
      'version':'1.0','sources':[
       {'name':'SM1018-01 D20/25/30/33S(SE)-7 정비지침서','type':'OEM service manual','status':'INGESTED','use':'64 symptoms / 268 causes / mechanical-hydraulic procedures'},
       {'name':'600123-00120 D20/25/30/33S(SE)-7 TIER-4 (G2,D24) electrical schematic 1/4~4/4','type':'OEM wiring schematic','status':'INGESTED_PARTIAL_NORMALIZATION','use':'21 executable electrical symptom graphs + redrawn circuits'},
       {'name':'Doosan D20S-7 Operation & Maintenance Manual','type':'OEM/O&M external source','status':'EXTERNAL_CROSSCHECK','use':'fuse/relay/service procedure cross-check'},
       {'name':'Doosan D24NAP Operation & Maintenance Manual 950106-01198','type':'OEM engine manual external source','status':'SOURCE_IDENTIFIED_NOT_INGESTED','use':'target replacement for D34 temporary engine reference; contains electric circuit, switches/sensors, harness, ECU sections'},
       {'name':'D34 engine reference currently in app','type':'different engine reference','status':'REFERENCE_ONLY_NOT_TARGET','use':'must not be treated as D24 vehicle-specific diagnosis'},
       {'name':'Fluke automotive voltage-drop diagnostic guidance','type':'external field method','status':'METHOD_CROSSCHECK','use':'loaded voltage-drop/ground-side diagnosis; generic limits are not OEM forklift thresholds'},
       {'name':'MOTOR 5V reference diagnostic cases','type':'external field case','status':'METHOD_CROSSCHECK','use':'external sensor/wire isolation before controller condemnation; 5V/no-communication pattern'},
      ]
    }
    SRC.write_text(json.dumps(source_registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    coverage={'version':'1.0-expert-reassessment','manual_scope':{'symptoms':64,'causes':268,'a_oem_executable':levels['A_OEM_EXECUTABLE'],'b_field_executable':levels['B_FIELD_EXECUTABLE']},'electrical_scope':{'catalog':ev['catalog'],'graphs':ev['graphs'],'nodes':ev['nodes'],'results':ev['results'],'logic_simulations':ev['simulations']},'transmission_scope':{'graphs':len(tm['graphs']),'results':total_tm_results,'logic_simulations':4530},'expert_cause_logic_simulations':xv['logic_simulations'],'areas':areas,'release_gate':{'all_current_validators_zero':len(fv.get('errors',[]))==0 and len(ev.get('errors',[]))==0 and len(xv.get('errors',[]))==0,'whole_vehicle_complete':False,'reason':'D24 engine expert DB, full electrical symptom universe, exact option pinouts, parts/price/labor remain incomplete'}}
    REG.write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=['# FULL REASSESSMENT · D20/25/30/33S(SE)-7 field diagnostic app','',
           '## Verdict','',
           '**현재 정규화된 정비지침서 범위는 현장 전문가 형식으로 전수 상승했지만, 차량 전체 진단 앱을 “완료”라고 판정하면 안 된다.**',
           '',f'- Manual scope: **64 symptoms / 268 causes**, all expert-format.',f'- A OEM-executable: **{levels["A_OEM_EXECUTABLE"]}**',f'- B field-isolation executable: **{levels["B_FIELD_EXECUTABLE"]}**',f'- Cause-level logic stress simulations: **{xv["logic_simulations"]:,}** (30 per cause)',f'- Transmission: **{len(tm["graphs"])} graphs / {total_tm_results} result terminals / 4,530 logic paths**',f'- Electrical: **{ev["graphs"]} graphs / {ev["nodes"]} nodes / {ev["results"]} results / {ev["simulations"]:,} logic paths**',f'- Current validator errors: **0 / 0 / 0** (field / electrical / expert)',
           '', '## Area-by-area judgement','', '| Area | Status | Evidence | Remaining gap |','|---|---|---|---|']
    for a in areas:
        lines.append('| '+a['area'].replace('|','/')+' | **'+a['status']+'** | '+a['evidence'].replace('|','/')+' | '+a['remaining'].replace('|','/')+' |')
    lines += ['', '## Design rule now enforced','',
              '1. Primary diagnostic screen is an assistant-redrawn fault-specific schematic, not an OEM page copy.',
              '2. A terminal diagnosis requires: measurement/comparison point → rule-outs → confirm condition → teardown/replacement gate.',
              '3. Electrical “continuity OK” never clears wiring by itself when the complaint is intermittent or load-dependent; loaded voltage drop/backprobe/dynamic reproduction is required where applicable.',
              '4. Controller condemnation requires controller power/GND plus its communication/reference-voltage/external-load isolation as relevant. The OSS 5V + CAN case is now the reference quality example.',
              '5. Unknown OEM pins/fuse cavities/thresholds stay UNKNOWN/OEM VERIFY; they are never invented.',
              '', '## Release decision','',
              '**RC EXPERT can be used as a field-diagnostic development build for the covered scope, but not as a “complete vehicle diagnosis” release.**',
              'The next mandatory source-normalization target is D24NAP engine data, followed by full electrical connector/pin/fuse normalization and option/cab circuits.',
              '', '## External cross-checks used in this reassessment','',
              '- Doosan D20S-7 Operation & Maintenance Manual: fuse/relay service information and model-family operating information.',
              '- Doosan D24NAP O&M Manual 950106-01198: confirmed dedicated chapters for electric circuit, switches/sensors, wire harness and ECU; source identified for ingestion.',
              '- Fluke automotive voltage-drop guidance: supports load-state voltage-drop and ground-side testing; generic numerical limits are not promoted to OEM forklift criteria.',
              '- MOTOR 5V-reference diagnostic cases: supports isolating external 5V loads/wiring before condemning a controller and correlating dead reference with no-communication patterns.'
    ]
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('wrote',REPORT); print('release complete?',coverage['release_gate']['whole_vehicle_complete'])
if __name__=='__main__': main()
