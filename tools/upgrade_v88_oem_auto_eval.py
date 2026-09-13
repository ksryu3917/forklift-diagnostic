#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/test_point_locator_v1.json'
d=json.loads(P.read_text(encoding='utf-8'))

def unit(name,to_base=1.0):
    return {'unit':name,'to_base':to_base}

def add(gid,pid,kind,base_unit,profiles,units=None,selector=None,note=None):
    pt=next(x for x in d['groups'][gid]['points'] if x['id']==pid)
    if pt.get('source_class')!='OEM_EXACT':
        raise SystemExit(f'{gid}/{pid} is not OEM_EXACT: {pt.get("source_class")}')
    ae={'kind':kind,'base_unit':base_unit,'profiles':profiles,'units':units or [unit(base_unit)],'authority':'OEM_EXACT_ONLY'}
    if selector: ae['profile_selector']=selector
    if note: ae['note']=note
    pt['auto_eval']=ae

def prof(id,label,min=None,max=None):
    x={'id':id,'label':label}
    if min is not None:x['min']=min
    if max is not None:x['max']=max
    return x

bar_units=[unit('bar',1.0),unit('psi',0.0689475729)]
# T/M pressure taps: operator must select low idle vs 2,000 rpm before judgement.
add('TM_PRESSURE_TAPS','TM2','range','bar',[prof('idle','저속 공전',0.3,0.6),prof('rpm2000','2,000 rpm',2.5,4.0)],bar_units)
add('TM_PRESSURE_TAPS','TM3','range','bar',[prof('idle','저속 공전',0.7,1.4),prof('rpm2000','2,000 rpm',5.9,8.0)],bar_units)
add('TM_PRESSURE_TAPS','TM4','range','bar',[prof('idle','저속 공전 · F 선택',7.3,8.6),prof('rpm2000','2,000 rpm · F 선택',7.3,9.7)],bar_units)
add('TM_PRESSURE_TAPS','TM5','range','bar',[prof('idle','저속 공전 · R 선택',7.3,8.6),prof('rpm2000','2,000 rpm · R 선택',7.3,9.7)],bar_units)
add('TM_PRESSURE_TAPS','TM6','range','bar',[prof('idle','저속 공전 · N',8.3,10.3),prof('rpm2000','2,000 rpm · N',9.0,11.0)],bar_units)
add('TM_PRESSURE_TAPS','TM7','range','bar',[prof('idle','저속 공전 · N',0.1,0.7),prof('rpm2000','2,000 rpm · N',2.4,3.5)],bar_units)
# Main hydraulic relief: current-vehicle model can preselect, but operator may change it.
main_profiles=[prof('D20S-7','D20S-7',177.5,184.5),prof('D25S-7','D25S-7',191.5,198.5),prof('D30S-7','D30S-7',212.0,219.0),prof('D33S-7','D33S-7',240.0,245.0)]
add('HYD_MAIN_RELIEF','HY1','range','bar',main_profiles,bar_units,'vehicle_model')
add('HYD_MAIN_RELIEF','HY2','range','bar',[prof('all','D20/D25/D30/D33',151.5,158.5)],bar_units)
add('HYD_MAIN_RELIEF','HY3','range','LPM',[prof('all','Tilt 작동',26.0,30.0)])
add('HYD_MAIN_RELIEF','HY4','range','LPM',[prof('all','AUX1 작동',24.0,28.0)])
# Same OEM pressure standards exposed in work-equipment control flow.
add('WORK_EQUIPMENT_CONTROL','WK2','range','bar',main_profiles,bar_units,'vehicle_model')
add('WORK_EQUIPMENT_CONTROL','WK3','range','bar',[prof('all','보조 릴리프',151.5,158.5)],bar_units)
# Mechanical limits with explicit OEM inequality/range.
add('MAST_CYLINDER_DIAG','MS3','max','mm',[prof('10min','10분 drift',None,100.0)])
add('MAST_CYLINDER_DIAG','MS6','max','mm',[prof('full_extend','완전 신장 · 좌우 로드 길이 차',None,3.18)])
# Electrical resistance with OEM tolerance.
add('EL_FR_CONTROL','FR5','range','ohm',[prof('25c','25°C 코일저항',9.7,10.3)])

# V8.8 metadata
D=d
D['version']='v1.8.8-oem-auto-eval'
D['auto_eval_rule']='자동판정은 source_class=OEM_EXACT 이면서 구조화된 허용범위/상한/하한이 있는 포인트에만 허용. 약(approx), 비교판정, OEM_VERIFY, FIELD 값에는 자동 PASS/FAIL 금지.'
P.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('auto_eval points',sum(1 for g in D['groups'].values() for p in g.get('points',[]) if p.get('auto_eval')))
