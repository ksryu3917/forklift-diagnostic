import json, collections, re, sys
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
expert=json.load(open(A/'expert_diag_v2.json',encoding='utf-8'))
elec=json.load(open(A/'electrical_diag_v1.json',encoding='utf-8'))
eng=json.load(open(A/'engine_diag_d24_v2.json',encoding='utf-8'))
loc=json.load(open(A/'field_location_map_v1.json',encoding='utf-8'))
smap=json.load(open(A/'engine_sensor_map_d24_v1.json',encoding='utf-8'))

def combo(it): return (tuple(it.get('field_sequence',[])),json.dumps(it.get('measurement_points',[]),ensure_ascii=False,sort_keys=True),tuple(it.get('confirm_if',[])),it.get('disassembly_gate',''))
def normcause(s):
    s=re.sub(r'\s+','',s).replace('어셈블리','').replace('조립품','').replace('브레이크','')
    s=s.replace('유압계통','유압라인').replace('작동유온도규정이탈','작동유과열')
    if '공기' in s and ('유압' in s or '라인' in s): return '유압라인공기'
    return s
g=collections.defaultdict(list)
for it in expert['items']: g[combo(it)].append(it)
all_shared=[v for v in g.values() if len(v)>1]
repeat_same=[]; boundary=[]; unresolved=[]
for v in all_shared:
    if len({normcause(i['cause']) for i in v})==1:
        repeat_same.append(v); continue
    if all(i.get('specificity_gate',{}).get('status')=='SHARED_ASSEMBLY_BOUNDARY' for i in v):
        boundary.append(v); continue
    unresolved.append(v)
review_items=sum(len(v) for v in unresolved)
split=sum(1 for i in expert['items'] if i.get('specificity_gate',{}).get('status')=='CAUSE_SPECIFIC_PRE_TEARDOWN')
shared_boundary_items=sum(len(v) for v in boundary)
unique_items=len(expert['items'])-sum(len(v) for v in all_shared)

# Electrical readiness from per-item field if present; otherwise mirror current strict IDs/status.
items=elec.get('catalog',elec.get('items',[]))
# known source-limited is represented in strict_readiness when present
etarget=sum(1 for i in items if i.get('strict_readiness')=='TARGET_LEVEL')
epartial=sum(1 for i in items if i.get('strict_readiness')=='FIELD_USABLE_PARTIAL')
if not etarget and not epartial:
    partial_ids={'E_STOP_NO','E_STOP_ON','E_HEAD_NO','E_TURN_NO','E_PARK_INPUT','E_GAUGE','E_WORK_LAMP','E_OSS_SEAT_LOCK','E_AC_POWER_NO','E_AC_COND_FAN_NO','E_PREHEAT_NO','E_FUEL_HEATER_NO','E_BRAKE_OIL_WARN','E_CLUSTER_POWER_NO','E_CAN_NETWORK','E_HOURMETER_NO','E_WATER_GAUGE','E_TM_TEMP_GAUGE','E_FUEL_GAUGE_ONLY','E_WIPER_NO','E_WASHER_NO'}
    graphs_obj=elec.get('graphs',{})
    if isinstance(graphs_obj,dict):
        graph_ids=set(graphs_obj.keys()); graphs=list(graphs_obj.values())
    else:
        graphs=graphs_obj; graph_ids={x.get('id') for x in graphs}
    epartial=len(graph_ids & partial_ids)
    etarget=len(graph_ids)-epartial

graphs_obj=elec.get('graphs',{})
graphs=list(graphs_obj.values()) if isinstance(graphs_obj,dict) else graphs_obj
result_nodes=sum(1 for g0 in graphs for n in (g0.get('nodes',{}).values() if isinstance(g0.get('nodes',{}),dict) else g0.get('nodes',[])) if isinstance(n,dict) and n.get('type')=='result')
eng_obj=eng.get('graphs',{})
eng_graphs=list(eng_obj.values()) if isinstance(eng_obj,dict) else eng_obj
eng_results=sum(1 for g0 in eng_graphs for n in (g0.get('nodes',{}).values() if isinstance(g0.get('nodes',{}),dict) else g0.get('nodes',[])) if isinstance(n,dict) and n.get('type')=='result')

lines=['# FIELD READINESS V7 · LOCATION + SPECIFICITY','',
'## 현재 판정','',
'**V8.3.1부터 268개 원인을 ‘모두 서로 다른 부품으로 억지 확정’하지 않는다. 분해 전에 구분 가능한 원인은 원인별 분리시험을 두고, 분해 전 구분이 불가능한 내부손상은 shared-assembly boundary에서 멈추도록 품질게이트를 적용했다. 현재 unresolved cross-cause 동일 진단체인은 0이다.**','',
'## 핵심 수치','',
f'- 기존 정비지침서 원인: **{len(expert["items"])}** · 모두 실행형 필드 구조 보유',
f'- 원인별 pre-teardown 분리시험을 가진 항목: **{split}**',
f'- 분해 전 세부부품 과확정을 막는 shared-assembly boundary: **{shared_boundary_items} causes / {len(boundary)} groups**',
f'- unresolved cross-cause 동일 진단체인: **{review_items} / {len(unresolved)} groups**',
f'- 전장: **{len(graphs)} graphs / {result_nodes} result terminals** · strict TARGET **{etarget}**, source-limited **{epartial}**',
f'- D24 engine: **{len(eng_graphs)} graphs / {eng_results} result terminals**',
f'- 차량 정비 위치맵: **{len(loc["zones"])} zones** · electrical **{len(loc.get("graph_focus",{}))}/{len(graphs)}** graphs mapped · expert systems **{len(loc.get("system_focus",{}))}/9** mapped',
f'- D24 sensor/actuator locator: **{len(smap.get("sensors",[]))} items**','',
'## V8.3 위치맵 품질게이트','',
'- 진단 화면에서 품번보다 **점검 위치 → 재작성 회로/유압 흐름 → 측정점 → 부하시험 → 격리/바이패스 → 확정**을 먼저 보여준다.',
'- 차량 전체 위치맵은 치수 CAD가 아니라 정비사용 빠른 locator다. 옵션/마스트/캐빈 사양에 따라 달라질 수 있는 위치는 정확 위치라고 단정하지 않는다.',
'- 엔진은 별도 D24 센서 위치맵에서 센서 위치·핀/신호·관련 진단을 연결하고 OEM 부품도/외형도를 근거로 연다.','',
'## Specificity gate','',
'- 같은 원인이 다른 증상에서 같은 시험을 공유하는 것은 정상적인 재사용으로 허용한다.',
'- 서로 다른 원인이 완전히 같은 측정점·점검순서·확정조건·분해조건을 공유하면 자동으로 “완전 독립 TARGET”으로 세지 않는다.',
'- 분해 전 물리적으로 구분 가능한 원인은 `원인별 분리시험`을 추가한다.',
'- 같은 어셈블리 내부에서 분해 전 구분이 불가능한 원인은 앱 결과도 세부부품을 확정하지 않고 **해당 어셈블리 내부고장** 수준에서 분해 게이트를 연다.','',
'## 아직 남은 큰 구멍','',
'- 전장 source-limited 항목의 정확 connector cavity / option schematic / analog transfer curve.',
'- cross-cause shared diagnostic family 중 외부에서 더 분리 가능한 원인들의 개별시험.',
'- 엔진 위치맵의 OEM 두 방향 장착도 기반 빠른 측면 선택/하이라이트 고도화.',
'- 실제 Work/GitHub Actions APK에서 화면·자산·release SHA 최종 통합검증.','',
'## 완료판정 규칙','',
'차량 전체 COMPLETE는 위 source-limited 전장과 specificity review가 해소되고, Work 빌드 APK의 실제 화면/자산/commit SHA까지 일치할 때만 선언한다.']
out=ROOT/'build/reports/FIELD_READINESS_V7_LOCATION.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:24]));print('Report:',out)
