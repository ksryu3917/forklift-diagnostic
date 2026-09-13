#!/usr/bin/env python3
from pathlib import Path
import json,sys
from collections import Counter
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/test_point_locator_v1.json'
E=ROOT/'app/src/main/assets/expert_diag_v2.json'
D=json.loads(P.read_text(encoding='utf-8'))
expert=json.loads(E.read_text(encoding='utf-8'))
el=json.loads((ROOT/'app/src/main/assets/electrical_diag_v1.json').read_text(encoding='utf-8'))
errors=[]; warnings=[]

REQ_GROUPS=[
 'TM_PRESSURE_TAPS','BRAKE_BLEED_ISOLATION','HYD_MAIN_RELIEF','STEERING_PRIORITY',
 'START_VDROP','OSS_HEALTH','AC_COND_FAN','AC_PRESSURE',
 'DRIVE_AXLE_MECH','WORK_EQUIPMENT_CONTROL','MAST_CYLINDER_DIAG','PARK_BRAKE_ADJUST_TEST',
 'ENG_ECU_HEALTH','ENG_VREF','ENG_CRANK_START','ENG_FUEL_RAIL','ENG_SYNC','ENG_INJECTOR',
 'ENG_AIR_BOOST','ENG_COOLING','ENG_LUBE','ENG_PREHEAT','ENG_COMBUSTION'
]
for r in REQ_GROUPS:
    if r not in D.get('groups',{}): errors.append('missing group '+r)

def point_map(gid): return {x['id']:x for x in D['groups'][gid]['points']}
def blob(gid): return json.dumps(D['groups'][gid],ensure_ascii=False)

# T/M hard gates from SM1018-01 §2-3-4.
tm=point_map('TM_PRESSURE_TAPS')
for x in ['TM1','TM2','TM3','TM4','TM5','TM6','TM7']:
    if x not in tm: errors.append('missing '+x)
for s in ['49~71°C','0~20.5 bar (0~300 psi)','8.3~10.3 bar','9.0~11.0 bar','7.3~8.6 bar','7.3~9.7 bar','0.1~0.7 bar','2.4~3.5 bar','0.7~1.4 bar','5.9~8.0 bar','0.3~0.6 bar','2.5~4.0 bar']:
    if s not in blob('TM_PRESSURE_TAPS'): errors.append('TM OEM spec missing '+s)
for pid,role in [('TM4','전진 클러치'),('TM5','후진 클러치'),('TM7','윤활'),('TM3','컨버터 충전'),('TM2','컨버터 출구'),('TM6','메인/펌프')]:
    if role not in tm[pid].get('label',''): errors.append(f'TM role mismatch {pid}: {role}')

# Brake anti-misuse gate.
bb=D['groups']['BRAKE_BLEED_ISOLATION']; bblob=blob('BRAKE_BLEED_ISOLATION')
if '40 bar는 마스터 릴리프 크래킹 압력이지 액슬 씰 누설판정 압력이 아님' not in bblob: errors.append('brake 40bar anti-misuse note missing')
for x in bb['points']:
    if x['id'] in ('BR2','BR3','BR4') and '40 bar' in x.get('expected',''): errors.append('40 bar misused as leak threshold '+x['id'])

# Hydraulic exact service port + settings.
hblob=blob('HYD_MAIN_RELIEF')
for s in ['니플 어셈블리(1)','300 bar 압력계','50±5°C','D20 181±3.5 bar','D25 195±3.5','D30 215.5±3.5','D33 240(+5,0) bar','155±3.5 bar','28±2 LPM','26±2 LPM']:
    if s not in hblob: errors.append('hyd OEM gate missing '+s)

# Steering inconsistency must remain explicit, never silently reconciled.
sblob=blob('STEERING_PRIORITY')
for s in ['포트(1)','300 bar 압력계','90±3 kPa','1,500~1,570 psi','상충']:
    if s not in sblob: errors.append('steering verify gate missing '+s)
if point_map('STEERING_PRIORITY')['ST3'].get('source_class')!='OEM_VERIFY': errors.append('steering ST3 must remain OEM_VERIFY')

# Start and OSS field gates.
start=blob('START_VDROP')
for s in ['DMM MIN/MAX','STARTER relay #8','오픈회로 전압만으로 정상판정 금지','KEY ST','배터리 + 납 포스트','스타터 ST/S 단자']:
    if s not in start: errors.append('start gate missing '+s)
if any(x in start.lower() for x in ['0.2v','0.5v','200mv','500mv']): warnings.append('generic voltage-drop threshold detected; verify OEM before use')
oss=blob('OSS_HEALTH')
for s in ['5V 기준회로','CAN H/L + 진단통신','외부 5V 부하','wiggle','SEAT 입력','Lift-lock 출력']:
    if s not in oss: errors.append('OSS gate missing '+s)

# A/C pressure OEM condition/spec.
ac=blob('AC_PRESSURE')
for s in ['30~35°C','1,500 rpm','1.5~2.5 bar','13.7~15.7 bar']:
    if s not in ac: errors.append('A/C OEM test condition/spec missing '+s)
if point_map('AC_COND_FAN')['AC4'].get('source_class')!='OEM_VERIFY': errors.append('A/C fan relay exact ID must remain source-limited/OEM_VERIFY')

# Drive axle: external isolation vs teardown-only values must stay separated.
da=point_map('DRIVE_AXLE_MECH'); dab=blob('DRIVE_AXLE_MECH')
for x in [f'DA{i}' for i in range(1,13)]:
    if x not in da: errors.append('drive axle point missing '+x)
for s in ['0.15~0.20 mm','1.5~2.0 N·m','초기 135 N·m','최종 50±5 N·m','분해 전 판정값으로 사용 금지']:
    if s not in dab: errors.append('drive axle OEM/teardown gate missing '+s)
for x in ['DA6','DA7','DA8','DA9']:
    if da[x].get('source_class')!='OEM_EXACT_TEARDOWN': errors.append(x+' must be teardown-only OEM exact')

# Work equipment: link/spool isolation before bench leakage; exact bench values are teardown-only where appropriate.
wk=point_map('WORK_EQUIPMENT_CONTROL'); wkb=blob('WORK_EQUIPMENT_CONTROL')
for x in [f'WK{i}' for i in range(1,15)]:
    if x not in wk: errors.append('work equipment point missing '+x)
for s in ['50±5°C','니플(1)','최대 7 cc/min @ 206 bar','최대 30 cc/min @ 206 bar','최대 30 cc/min @ 137 bar','최대 50 cc/min @ 137 bar','최대 246 cc/min @ 137 bar','링크 해제']:
    if s not in wkb: errors.append('work equipment gate missing '+s)
for x in ['WK7','WK8','WK9','WK11']:
    if wk[x].get('source_class')!='OEM_EXACT_TEARDOWN': errors.append(x+' must be teardown-only OEM exact')

# Mast: specified drift and alignment, but internal cause still requires circuit isolation.
ms=point_map('MAST_CYLINDER_DIAG'); msb=blob('MAST_CYLINDER_DIAG')
for x in [f'MS{i}' for i in range(1,9)]:
    if x not in ms: errors.append('mast point missing '+x)
for s in ['45~55°C','2.5 m','10분','drift ≤100 mm / 10 min','≤3.18 mm','밸브 vs 실린더 회로 격리']:
    if s not in msb: errors.append('mast OEM/isolation gate missing '+s)

# Parking brake exact adjustment + performance confirmation.
pb=point_map('PARK_BRAKE_ADJUST_TEST'); pbb=blob('PARK_BRAKE_ADJUST_TEST')
for x in [f'PB{i}' for i in range(1,6)]:
    if x not in pb: errors.append('parking brake point missing '+x)
for s in ['2~3번째 클릭','5.6~6.8 N·m','1.2~1.5 바퀴','15%','차량이 움직이지 않아야 함']:
    if s not in pbb: errors.append('parking brake OEM gate missing '+s)

# Full cause-specific coverage: all 268 causes, no subset-only pass.
cm=D.get('cause_map',{})
items=expert.get('items',[])
if len(items)!=268: warnings.append('expert item count is not 268: '+str(len(items)))
if len(cm)!=len(items): errors.append(f'cause_map must cover every expert item: {len(cm)} vs {len(items)}')
valid_systems=['트랜스미션','브레이크','유압','스티어링','에어컨','드라이브 액슬','작업장치','마스트','주차 브레이크']
counts=Counter()
for it in items:
    cid=it['id']; sysn=it.get('system',''); counts[sysn]+=1
    m=cm.get(cid)
    if not m: errors.append('cause test-point map missing '+cid); continue
    gid=m.get('group',''); ids=m.get('point_ids') or []
    if gid not in D['groups']: errors.append(cid+' bad group '+gid); continue
    if D['groups'][gid].get('system')!=sysn: errors.append(f'{cid} system/group mismatch {sysn}/{gid}')
    pids={x['id'] for x in D['groups'][gid].get('points',[])}
    if not ids: errors.append('cause test-point selection empty '+cid)
    for pid in ids:
        if pid not in pids: errors.append(f'{cid} references missing point {gid}/{pid}')
for sysn in valid_systems:
    if counts[sysn]==0: errors.append('expert system empty '+sysn)
    if sysn not in D.get('system_map',{}): errors.append('system map missing '+sysn)
    elif D['system_map'][sysn] not in D['groups']: errors.append('system map target missing '+sysn)
extra=[x for x in counts if x not in valid_systems]
if extra: warnings.append('unrecognized expert systems: '+','.join(extra))

# D24 engine: all 21 diagnostic graphs must open a dedicated measurement locator.
eng=json.loads((ROOT/'app/src/main/assets/engine_diag_d24_v2.json').read_text(encoding='utf-8'))
em=D.get('engine_graph_map',{})
if len(em)!=len(eng.get('graphs',{})): errors.append(f'engine graph map must cover all engine graphs: {len(em)} vs {len(eng.get("graphs",{}))}')
for gid in eng.get('graphs',{}):
    tg=em.get(gid)
    if not tg: errors.append('engine graph test-point map missing '+gid); continue
    if tg not in D['groups']: errors.append(gid+' engine test-point target missing '+str(tg)); continue
    if D['groups'][tg].get('system')!='엔진': errors.append(gid+' mapped to non-engine group '+tg)
    if D.get('graph_map',{}).get(gid)!=tg: errors.append(gid+' graph_map/engine_graph_map mismatch')
for gid in ['ENG_ECU_HEALTH','ENG_VREF','ENG_CRANK_START','ENG_FUEL_RAIL','ENG_SYNC','ENG_INJECTOR','ENG_AIR_BOOST','ENG_COOLING','ENG_LUBE','ENG_PREHEAT','ENG_COMBUSTION']:
    g=D['groups'][gid]
    if not g.get('sensor_focus_ids'): errors.append(gid+' has no sensor_focus_ids')
# Exact-pin / no-fabrication engine gates.
for s0 in ['ECU138','ECU161','ECU165','ECU164','SENSOR 15A']:
    if s0 not in blob('ENG_ECU_HEALTH')+blob('ENG_VREF'): errors.append('engine ECU/VREF gate missing '+s0)
for s0 in ['RPS pin3 / ECU138','RPS pin2 / ECU119','RPS pin1 / ECU135','ECU177','OEM 미확인 “시동 최소 MPa” 임계값은 만들지 않음']:
    if s0 not in blob('ENG_CRANK_START')+blob('ENG_FUEL_RAIL'): errors.append('engine fuel/rail gate missing '+s0)
for s0 in ['ECU136 CRS NEG','ECU160 CRS POS','ECU187 shield','ECU159','ECU147','12V']:
    if s0 not in blob('ENG_SYNC'): errors.append('engine sync gate missing '+s0)
for s0 in ['ECU126','ECU127','ECU174','ECU150','ECU175','ECU151','ECU125','ECU103','OEM 확인 없는 절대 cc/min 기준 금지']:
    if s0 not in blob('ENG_INJECTOR'): errors.append('engine injector gate missing '+s0)
for s0 in ['ECU137','ECU120','ECU228','ECU235','ECU161','ECU167','ECU112']:
    if s0 not in blob('ENG_AIR_BOOST'): errors.append('engine air/boost gate missing '+s0)
for s0 in ['ECU145','ECU109','20°C ≈2.5 kΩ','110°C ≈0.148 kΩ']:
    if s0 not in blob('ENG_COOLING'): errors.append('engine cooling gate missing '+s0)
for s0 in ['ECU165','ECU148','ECU111','ECU104','임의 규격/수치 금지']:
    if s0 not in blob('ENG_LUBE'): errors.append('engine lube gate missing '+s0)
if point_map('ENG_LUBE')['OL4'].get('source_class')!='OEM_VERIFY': errors.append('engine mechanical oil pressure port must remain OEM_VERIFY until exact port/spec confirmed')
# Engine UI must expose the test-point screen before sensor/parts references.
engj=(ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/EngineExpertDiagnosticActivity.java').read_text(encoding='utf-8')
if 'TestPointLocatorActivity.class' not in engj or 'graph_id' not in engj: errors.append('EngineExpertDiagnosticActivity no graph-specific test-point link')
tpj=(ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/TestPointLocatorActivity.java').read_text(encoding='utf-8')
for s0 in ['EngineSensorMapActivity.class','sensor_focus_ids','"엔진".equals(group.optString("system"))']:
    if s0 not in tpj: errors.append('TestPointLocatorActivity engine-location hook missing '+s0)

# Source classes and point schema.
for gid,g in D['groups'].items():
    if not g.get('points'): errors.append(gid+' no points')
    if not g.get('focus_ids'): errors.append(gid+' no physical focus_ids')
    for x in g['points']:
        if x.get('source_class') not in D['source_classes']: errors.append(gid+'/'+x.get('id','?')+' bad source_class '+x.get('source_class',''))
        for k in ['where','connect','condition']:
            if not x.get(k): errors.append(gid+'/'+x.get('id','?')+' missing '+k)

# Electrical V8.6 gate: every electrical graph must open a valid measurement/test-point map.
egraphs=el.get('graphs',{})
egm=D.get('graph_map',{})
electrical_mapped=0
for gid in egraphs:
    tg=egm.get(gid)
    if not tg:
        errors.append('electrical graph test-point map missing '+gid); continue
    if tg not in D.get('groups',{}):
        errors.append(gid+' electrical test-point target missing '+str(tg)); continue
    g=D['groups'][tg]
    if not g.get('points'):
        errors.append(gid+' electrical test-point target has no points '+tg); continue
    if not g.get('focus_ids'):
        errors.append(gid+' electrical test-point target has no physical focus '+tg); continue
    electrical_mapped+=1
if len(egraphs)!=38: errors.append('electrical graph count must be 38 for V8.6: '+str(len(egraphs)))
if electrical_mapped!=len(egraphs): errors.append(f'electrical graph test-point coverage incomplete: {electrical_mapped}/{len(egraphs)}')

# Required V8.6 probe families / anti-fabrication gates.
for gid in ['EL_STOP_LAMP','EL_HEAD_LAMP','EL_TURN_HAZARD','EL_HORN','EL_BACKUP','EL_CHARGE','EL_PARK_INPUT','EL_LIFT_LOCK','EL_GAUGE_COMMON','EL_WORK_REAR','EL_FR_CONTROL','EL_AC_POWER','EL_PREHEAT','EL_FUEL_HEATER','EL_BRAKE_OIL_WARN','EL_CLUSTER_POWER','EL_CAN_NETWORK','EL_SEATBELT','EL_LICENSE','EL_HOURMETER','EL_REAR_LAMP','EL_STROBE','EL_WATER_GAUGE','EL_TM_TEMP_GAUGE','EL_FUEL_GAUGE','EL_WIPER','EL_WASHER']:
    if gid not in D.get('groups',{}): errors.append('V8.6 electrical probe group missing '+gid)
for token in ['ACC 15A','STOP LAMP SW','기능상 상류','숫자 1/2를 공급단으로 미리 단정하지 말고']:
    if token not in blob('EL_STOP_LAMP'): errors.append('stop-lamp anti-guess gate missing '+token)
for token in ['ALT B+→BAT+ drop','ALT case→BAT- drop','알터네이터에서 14V가 보인다는 사실만으로']:
    if token not in blob('EL_CHARGE'): errors.append('charge loaded-drop gate missing '+token)
for token in ['CAN H/L','단일 노드','termination']:
    if token not in blob('EL_CAN_NETWORK'): errors.append('CAN isolation gate missing '+token)
for token in ['4-pin, 1.5SQ','3단(Stage 3) 직접 연결 조건']:
    if token not in json.dumps(el.get('circuits',{}).get('AC_POWER',{}),ensure_ascii=False): errors.append('A/C verified electrical spec missing '+token)

# UI hooks: all 268 expert causes must expose TestPointLocator; new 4 group drawings must exist.
j=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/TestPointLocatorActivity.java'
if not j.exists(): errors.append('TestPointLocatorActivity missing')
else:
    js=j.read_text(encoding='utf-8')
    for s in ['측정 순서 / 연결 위치','OEM 미확정 / 과잉판정 금지','source_class','FieldLocationMapActivity','cause_id','pointFilter','DRIVE_AXLE_MECH','WORK_EQUIPMENT_CONTROL','MAST_CYLINDER_DIAG','PARK_BRAKE_ADJUST_TEST']:
        if s not in js: errors.append('activity UI gate missing '+s)
expj=(ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/ExpertDiagnosticActivity.java').read_text(encoding='utf-8')
if 'TestPointLocatorActivity.class' not in expj: errors.append('ExpertDiagnosticActivity no test-point link')
if 'cause_id' not in expj: errors.append('ExpertDiagnosticActivity does not pass cause_id')
for old in ['"트랜스미션".equals(sys)||"브레이크".equals(sys)','"스티어링".equals(sys)||"에어컨".equals(sys)']:
    if old in expj: errors.append('ExpertDiagnosticActivity still limits test-points to old five-system subset')
elj=(ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/ElectricalDiagnosticActivity.java').read_text(encoding='utf-8')
if 'TestPointLocatorActivity.class' not in elj: errors.append('ElectricalDiagnosticActivity no test-point link')

print('Test-point locator validation V8.6')
print(' groups:',len(D['groups']))
print(' points:',sum(len(g['points']) for g in D['groups'].values()))
print(' expert causes:',len(items),'mapped:',len(cm))
print(' engine graphs:',len(eng.get('graphs',{})),'mapped:',len(em))
print(' electrical graphs:',len(egraphs),'mapped:',electrical_mapped)
print(' system coverage:',dict(counts))
print(' errors:',len(errors),'warnings:',len(warnings))
for e in errors: print('ERROR',e)
for w in warnings: print('WARN',w)
report=ROOT/'build/reports/test_point_locator_v86.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# V8.6 Test-point Locator Validation\n\n'
                  f'- Groups: {len(D["groups"])}\n'
                  f'- Measurement/test points: {sum(len(g["points"]) for g in D["groups"].values())}\n'
                  f'- Expert causes: {len(items)}\n'
                  f'- Cause mappings: {len(cm)}\n'
                  f'- Engine graph mappings: {len(em)} / {len(eng.get("graphs",{}))}\n'
                  f'- Electrical graph mappings: {electrical_mapped} / {len(egraphs)}\n'
                  f'- Errors: {len(errors)}\n'
                  f'- Warnings: {len(warnings)}\n\n'
                  '## System coverage\n'+''.join(f'- {k}: {v}\n' for k,v in counts.items())+'\n'
                  '## Errors\n'+('\n'.join('- '+x for x in errors) or '- None')+'\n\n'
                  '## Warnings\n'+('\n'.join('- '+x for x in warnings) or '- None')+'\n',encoding='utf-8')
sys.exit(1 if errors else 0)
