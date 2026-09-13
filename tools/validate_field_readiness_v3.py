#!/usr/bin/env python3
import json,re,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'app/src/main/assets'; R=ROOT/'build/reports';R.mkdir(parents=True,exist_ok=True)
expert=json.load(open(A/'expert_diag_v2.json',encoding='utf-8'))
elec=json.load(open(A/'electrical_diag_v1.json',encoding='utf-8'))
sensor_map=json.load(open(A/'engine_sensor_map_d24_v1.json',encoding='utf-8'))
engine_v2=json.load(open(A/'engine_diag_d24_v2.json',encoding='utf-8')) if (A/'engine_diag_d24_v2.json').exists() else {'graphs':{}}

def txt(x):
 return ' '.join(str(v) for v in x if v)
def diag_sig(i):
 d=i.get('diagram',{}); raw=json.dumps({'n':[(x.get('id'),x.get('label'),x.get('role')) for x in d.get('nodes',[])],'e':[(x.get('from'),x.get('to')) for x in d.get('edges',[])]},ensure_ascii=False,sort_keys=True);return hashlib.md5(raw.encode()).hexdigest()[:10]
freq=collections.Counter(diag_sig(i) for i in expert['items'])
DYNAMIC=('전압강하','백프로브','min/max','흔들','부하','압력','격리','비교','실측','게이지','직접전원','바이패스')
ELECTRIC=('전기','배선','하네스','스위치','솔레노이드','센서','릴레이','ecu','컨트롤러','퓨즈','전원','접지')

def rate_cause(i):
 gaps=[]; score=0
 fs=i.get('field_sequence',[]); ro=i.get('rule_out',[]); cf=i.get('confirm_if',[]); mp=i.get('measurement_points',[]); src=i.get('oem_source',{}); cause=i.get('cause','').lower(); alltext=txt(fs+ro+cf+[i.get('disassembly_gate','')]).lower()
 if len(fs)>=4: score+=2
 else:gaps.append('field_sequence<4')
 if len(ro)>=2:score+=2
 else:gaps.append('rule_out<2')
 if cf:score+=1
 else:gaps.append('confirm_if 없음')
 if i.get('disassembly_gate'):score+=1
 else:gaps.append('disassembly_gate 없음')
 if src.get('pdf_pages') or src.get('section'):score+=1
 else:gaps.append('OEM source 약함')
 if mp:score+=2
 elif any(k in alltext for k in ('육안','유격','누유','마모','레벨','오염','파손','변형')):score+=1
 else:gaps.append('측정/비교점 부족')
 if i.get('linked_graph') or src.get('ui_tests'):score+=1
 # diagram template penalty
 f=freq[diag_sig(i)]
 if f<=12:score+=1
 elif not(i.get('linked_graph') or src.get('ui_tests')):gaps.append(f'재작성도면 템플릿 반복({f})')
 # electric-like needs live/load test
 if any(k in cause for k in ELECTRIC):
  if any(k in alltext for k in DYNAMIC):score+=1
  else:gaps.append('전기부하/동적 시험 부족')
 # target >=9 and no major generic template gap
 status='TARGET_LEVEL' if score>=9 and not any(x.startswith('재작성도면') for x in gaps) else ('FIELD_USABLE_PARTIAL' if score>=6 else 'INSUFFICIENT')
 return status,score,gaps

cause_rows=[]
for i in expert['items']:
 st,sc,g=rate_cause(i);cause_rows.append({'id':i['id'],'system':i['system'],'symptom':i['symptom'],'cause':i['cause'],'status':st,'score':sc,'gaps':g})
cc=collections.Counter(x['status'] for x in cause_rows); bysys={}
for sys in sorted(set(x['system'] for x in cause_rows)):
 bysys[sys]=dict(collections.Counter(x['status'] for x in cause_rows if x['system']==sys))

def graph_quality(gid,g):
 gaps=[]; cir=elec.get('circuits',{}).get(g.get('circuit'),{})
 sd=cir.get('simplified_diagram')
 if not sd:gaps.append('재작성 회로 없음')
 elif len(sd.get('measure_points',[]))<3:gaps.append('회로 측정점 부족')
 if cir.get('unverified'):gaps.append('정확 pin/fuse/cavity 일부 미확정')
 results=[n for n in g.get('nodes',{}).values() if n.get('type')=='result']
 for n in results:
  for k in ('field_test','rule_out','confirm_if'):
   if not n.get(k):gaps.append('결과노드 '+k+' 누락');break
  if not n.get('disassembly_gate'):gaps.append('결과노드 disassembly gate 누락');break
 qtexts=' '.join(' '.join(n.get('field_method',[])) for n in g.get('nodes',{}).values()).lower()
 # require dynamic/load testing for key electrical classes
 if any(k in gid for k in ('START','OSS','STOP','AC_','CHARGE','CAN')) and not any(k in qtexts for k in DYNAMIC): gaps.append('동적/부하시험 약함')
 if gid.startswith('E_D24') and not g.get('engine_sensor_map'):gaps.append('D24 센서 위치맵 미연결')
 status='TARGET_LEVEL' if not gaps else ('FIELD_USABLE_PARTIAL' if not any('재작성 회로 없음' in x or '결과노드' in x for x in gaps) else 'INSUFFICIENT')
 return status,gaps,len(results),len(g.get('nodes',{}))

elec_rows=[]
for gid,g in elec['graphs'].items():
 st,gaps,res,nodes=graph_quality(gid,g);elec_rows.append({'id':gid,'title':g.get('title'),'status':st,'gaps':gaps,'nodes':nodes,'results':res})
ec=collections.Counter(x['status'] for x in elec_rows)

engine_required=[
 ('크랭킹 무시동','E_D24_CRANK_NO_START'),('ECU 무통신','E_D24_ECU_NO_COMM'),('5V 기준전압 붕괴','E_D24_5V_REF'),('레일압 센서/회로','E_D24_RAIL_PRESSURE'),('부스트압 센서/회로','E_D24_BOOST_PRESSURE'),('수온센서/회로','E_D24_WATER_TEMP'),('MAF/흡기온도','E_D24_MAF'),
 ('시동은 도나 시동 어려움/열간·냉간 hard start','EN_HARD_START'),('주행/작업 중 엔진 스톨','EN_STALL'),('출력저하/부하에서 힘없음','EN_LOW_POWER'),('아이들 불안정/부조','EN_ROUGH_IDLE'),('검은연기','EN_BLACK_SMOKE'),('흰연기','EN_WHITE_SMOKE'),('청색연기/오일소모','EN_BLUE_SMOKE'),('엔진 과열','EN_OVERHEAT'),('저오일압','EN_LOW_OIL_PRESS'),('부스트 부족/터보 기계진단','EN_LOW_BOOST'),('프리히트/에어히터 불량','EN_PREHEAT'),('IMV/저압연료/고압계통 분리','EN_FUEL_PRESSURE'),('CRK/CAM 전용 파형/동기 진단','EN_CRK_CAM_SYNC'),('인젝터 전기/리턴/기계 분리','EN_INJECTOR_SEPARATE')
]
engine_rows=[]
for name,gid in engine_required:
 present=gid in engine_v2.get('graphs',{})
 engine_rows.append({'symptom':name,'graph':gid,'status':'COVERED' if present else 'GAP'})
# sensor position coverage
sensors=sensor_map['sensors']; sp_exact=sum(1 for s in sensors if s.get('callout') is not None); sp_total=len(sensors)

report={
 'version':'v3-strict-field-readiness','cause_scope':{'total':len(cause_rows),'counts':dict(cc),'by_system':bysys},
 'electrical_scope':{'total_graphs':len(elec_rows),'counts':dict(ec)},
 'engine_scope':{'required_cases':len(engine_rows),'covered':sum(1 for x in engine_rows if x['status']=='COVERED'),'gaps':sum(1 for x in engine_rows if x['status']=='GAP')},
 'sensor_location_map':{'items':sp_total,'oem_numbered_callouts':sp_exact,'map_file':'engine_sensor_map_d24_v1.json','geometry':'technician isometric zone redraw, not dimensional CAD'},
 'cause_rows':cause_rows,'electrical_rows':elec_rows,'engine_rows':engine_rows
}
(R/'field_readiness_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines=['# FIELD READINESS V3 · strict reassessment','',
'## 결론','',
'**현재 앱은 전체 항목이 사용자 요구 수준에 도달했다고 판정할 수 없다.** 기존 validator는 연결/필드 존재를 잘 검사하지만, 이번 V3는 고장별 재작성도면의 전용성·실제 측정점·동적/부하시험·엔진 증상 universe·센서 위치 접근성까지 별도로 본다.','',
'## 64증상 / 268원인 재판정','',f'- TARGET_LEVEL: **{cc.get("TARGET_LEVEL",0)}**',f'- FIELD_USABLE_PARTIAL: **{cc.get("FIELD_USABLE_PARTIAL",0)}**',f'- INSUFFICIENT: **{cc.get("INSUFFICIENT",0)}**','',
'| 계통 | TARGET | PARTIAL | INSUFFICIENT |','|---|---:|---:|---:|']
for sys,c in bysys.items():lines.append(f'| {sys} | {c.get("TARGET_LEVEL",0)} | {c.get("FIELD_USABLE_PARTIAL",0)} | {c.get("INSUFFICIENT",0)} |')
lines += ['', '## 전장 실행 그래프 재판정','',f'- 전체: **{len(elec_rows)}**',f'- TARGET_LEVEL: **{ec.get("TARGET_LEVEL",0)}**',f'- FIELD_USABLE_PARTIAL: **{ec.get("FIELD_USABLE_PARTIAL",0)}**',f'- INSUFFICIENT: **{ec.get("INSUFFICIENT",0)}**','']
for x in elec_rows:
 if x['status']!='TARGET_LEVEL':lines.append(f'- **{x["id"]}** · {x["title"]} → {x["status"]}: ' + '; '.join(x['gaps']))
lines += ['', '## D24NAP 엔진 커버리지','',f'- 기준 증상/진단 묶음: **{len(engine_rows)}**',f'- 현재 그래프 보유: **{sum(1 for x in engine_rows if x["status"]=="COVERED")}**',f'- 아직 GAP: **{sum(1 for x in engine_rows if x["status"]=="GAP")}**','']
for x in engine_rows:lines.append(f'- {"✅" if x["status"]=="COVERED" else "❌"} {x["symptom"]}' + (f' → `{x["graph"]}`' if x['graph'] else ''))
lines += ['', '## 센서 위치맵','',f'- D24 위치/핀 항목: **{sp_total}**',f'- OEM §12-3 번호 callout 직접 연결: **{sp_exact}**', '- 앱용 아이소메트릭은 **가능**. 3D CAD 대신 zone 기반 pseudo-isometric 엔진 그림 + OEM callout 번호 + 센서핀/ECU핀 + 정확 위치 근거 버튼 방식이 현장 가독성에 더 적합하다.', '- 위치맵은 치수도면이 아니며 엔진 사양 variant에 따라 OEM 외형도/번호도면으로 최종 확인한다.','', '## 이번 기준에서 PASS하려면','',
'1. 고장 전용 재작성 회로/유압/동력도에 **그 고장에 필요한 요소만** 있어야 한다.',
'2. 측정 위치와 공구, 실제 부하/온도/방향/인터록 조건을 지정해야 한다.',
'3. 정적 도통/무부하 12V만으로 배선 정상 판정 금지. 간헐/부하 고장은 전압강하·백프로브·MIN/MAX·흔들림/열간 재현을 요구한다.',
'4. ECU/OSS 등 컨트롤러 교환 전 B+/IGN/GND + CAN + 5V reference/external load isolation을 요구한다.',
'5. 결과는 rule-out + confirm_if + disassembly_gate까지 있어야 한다.',
'6. 센서/밸브/테스트포트는 앱에서 바로 위치를 찾을 수 있어야 한다.',
'7. OEM에 없는 숫자는 임의로 만들지 않고 정상측 비교/명령값 대비/격리시험으로 처리한다.','',
'## 시동 무크랭킹 reference case','',
'`E_START_NO`를 사용자 제시 사례 수준으로 재작성했다: 불발 순간 배터리 포스트 → 메인 B+ drop → GND drop → ST(S) MIN/MAX → START relay 부하입력/출력 + coil 명령 → KEY ST → N/OSS 인터록 순으로 분리한다. 스타터 교환 이력만으로 스타터를 다시 의심하지 않는다.']
(R/'FIELD_READINESS_V3.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'cause':dict(cc),'electrical':dict(ec),'engine':report['engine_scope'],'sensor_map':report['sensor_location_map']},ensure_ascii=False,indent=2))
