from pathlib import Path
import json,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
asset=root/'app/src/main/assets/field_location_map_v1.json'
elec=root/'app/src/main/assets/electrical_diag_v1.json'
expert=root/'app/src/main/assets/expert_diag_v2.json'
errs=[]; warns=[]
d=json.loads(asset.read_text())
e=json.loads(elec.read_text())
x=json.loads(expert.read_text())
z=d['zones']; gf=d['graph_focus']; sf=d['system_focus']
for zid,v in z.items():
    for k in ('label','access','test_points','certainty'):
        if not v.get(k): errs.append(f'zone {zid} missing {k}')
    if not (0 <= v.get('x',-1) <= 1 and 0 <= v.get('y',-1) <= 1): errs.append(f'zone {zid} coordinates')
    for a in v.get('evidence',[]):
        if not (root/'app/src/main/assets'/a).exists(): errs.append(f'zone {zid} missing asset {a}')
ids={c['id'] for c in e['catalog']}
missing=sorted(ids-set(gf))
extra=sorted(set(gf)-ids)
if missing: errs.append('electrical graph focus missing: '+','.join(missing))
if extra: warns.append('focus has extra graph ids: '+','.join(extra))
for gid,arr in gf.items():
    for zid in arr:
        if zid not in z: errs.append(f'{gid} unknown zone {zid}')
systems={i['system'] for i in x['items']}
missing_sys=sorted(systems-set(sf))
if missing_sys: errs.append('expert system focus missing: '+','.join(missing_sys))
for s,arr in sf.items():
    for zid in arr:
        if zid not in z: errs.append(f'system {s} unknown zone {zid}')
java=(root/'app/src/main/java/com/ryu/forkliftdiagnostic/FieldLocationMapActivity.java').read_text()
for must in ('점검 위치맵','여기서 바로 볼 것','OEM 위치/분해도 근거 보기'):
    if must not in java: errs.append('UI marker missing '+must)
print('Field location zones:',len(z))
print('Electrical graph focus:',len(gf),'/',len(ids))
print('Expert systems:',len(sf),'/',len(systems))
print('Errors:',len(errs),'Warnings:',len(warns))
for a in errs: print('ERROR',a)
for a in warns: print('WARN',a)
if errs: raise SystemExit(1)
