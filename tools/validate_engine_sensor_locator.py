import json, sys
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
p=ROOT/'app/src/main/assets/engine_sensor_map_d24_v1.json'
d=json.load(open(p,encoding='utf-8'))
zones={z['id'] for v in d.get('views',[]) for z in v.get('zones',[])}
errors=[]; warnings=[]; exact_views=0
for s in d.get('sensors',[]):
    if s.get('zone') not in zones: errors.append(f"{s.get('id')}: unknown zone {s.get('zone')}")
    for k in ['id','kr','location','pins','oem_ref']:
        if not s.get(k): errors.append(f"{s.get('id')}: missing {k}")
    ev=s.get('parts_location_view')
    if ev:
        exact_views+=1
        if not (ROOT/'app/src/main/assets'/ev).exists(): errors.append(f"{s.get('id')}: missing view asset {ev}")
    if s.get('parts',{}).get('status','').startswith('EXACT') and not ev:
        warnings.append(f"{s.get('id')}: exact Parts Book item but no focused p211 view")
java=(ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/EngineSensorMapActivity.java').read_text(encoding='utf-8')
for marker in ['parts_location_view','이 센서가 표시된 OEM 엔진 방향만 보기','OEM 전체 스위치&센서 부품도 보기']:
    if marker not in java: errors.append('UI marker missing: '+marker)
print('Engine locator sensors:',len(d.get('sensors',[])))
print('Zones:',len(zones))
print('Focused OEM p211 views linked:',exact_views)
print('Errors:',len(errors),'Warnings:',len(warnings))
for e in errors: print('ERROR',e)
for w in warnings: print('WARN',w)
if errors: raise SystemExit(1)
