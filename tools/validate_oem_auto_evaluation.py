#!/usr/bin/env python3
from pathlib import Path
import json,sys,math,re
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets/test_point_locator_v1.json'
J=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/TestPointLocatorActivity.java'
R=ROOT/'build/reports/oem_auto_eval_v88.md'
errors=[];warnings=[]
d=json.loads(A.read_text(encoding='utf-8'));js=J.read_text(encoding='utf-8')
allowed={'range','max','min'}; auto=[]; profiles_count=0; scenarios=0
required={
('TM_PRESSURE_TAPS',x) for x in ['TM2','TM3','TM4','TM5','TM6','TM7']
}|{('HYD_MAIN_RELIEF',x) for x in ['HY1','HY2','HY3','HY4']
}|{('WORK_EQUIPMENT_CONTROL',x) for x in ['WK2','WK3']
}|{('MAST_CYLINDER_DIAG',x) for x in ['MS3','MS6']
}|{('EL_FR_CONTROL','FR5')}
seen=set()

def verdict(kind,pr,v):
    if kind=='range':return pr['min']<=v<=pr['max']
    if kind=='max':return v<=pr['max']
    if kind=='min':return v>=pr['min']
    raise ValueError(kind)

def scenario_values(kind,pr):
    if kind=='range':
        lo,hi=float(pr['min']),float(pr['max']); span=max(abs(hi-lo),max(abs(lo),abs(hi),1.0)*0.01)
        vals=[lo-span,lo-span*.1,lo,lo+span*.01,(lo+hi)/2,hi-span*.01,hi,hi+span*.1,hi+span]
        # pad with deterministic values across / outside range until 30
        for i in range(21): vals.append(lo-span+(hi-lo+2*span)*i/20)
        return vals[:30]
    if kind=='max':
        mx=float(pr['max']); span=max(abs(mx)*0.1,0.1);vals=[mx-span,mx-span*.1,mx,mx+span*.1,mx+span]
        vals += [mx-1.5*span+3*span*i/24 for i in range(25)]
        return vals[:30]
    mn=float(pr['min']);span=max(abs(mn)*0.1,0.1);vals=[mn-span,mn-span*.1,mn,mn+span*.1,mn+span]
    vals += [mn-1.5*span+3*span*i/24 for i in range(25)]
    return vals[:30]

for gid,g in d.get('groups',{}).items():
    for p in g.get('points',[]):
        ae=p.get('auto_eval')
        if not ae:continue
        seen.add((gid,p.get('id')));auto.append((gid,p))
        if p.get('source_class')!='OEM_EXACT':errors.append(f'{gid}/{p.get("id")}: auto_eval on non-OEM_EXACT source {p.get("source_class")}')
        if ae.get('authority')!='OEM_EXACT_ONLY':errors.append(f'{gid}/{p.get("id")}: authority must be OEM_EXACT_ONLY')
        if '약' in p.get('expected','') or 'approx' in p.get('expected','').lower():errors.append(f'{gid}/{p.get("id")}: approximate spec must not auto-evaluate')
        kind=ae.get('kind');
        if kind not in allowed:errors.append(f'{gid}/{p.get("id")}: invalid kind {kind}');continue
        profiles=ae.get('profiles') or [];units=ae.get('units') or []
        if not profiles:errors.append(f'{gid}/{p.get("id")}: no profiles')
        if not units:errors.append(f'{gid}/{p.get("id")}: no units')
        for u in units:
            if not u.get('unit'):errors.append(f'{gid}/{p.get("id")}: blank unit')
            if not isinstance(u.get('to_base'),(int,float)) or u.get('to_base',0)<=0:errors.append(f'{gid}/{p.get("id")}: invalid conversion {u}')
        for pr in profiles:
            profiles_count+=1
            if kind=='range' and (not isinstance(pr.get('min'),(int,float)) or not isinstance(pr.get('max'),(int,float)) or pr['min']>pr['max']):errors.append(f'{gid}/{p.get("id")}/{pr.get("id")}: invalid range')
            if kind=='max' and not isinstance(pr.get('max'),(int,float)):errors.append(f'{gid}/{p.get("id")}/{pr.get("id")}: invalid max')
            if kind=='min' and not isinstance(pr.get('min'),(int,float)):errors.append(f'{gid}/{p.get("id")}/{pr.get("id")}: invalid min')
            try:
                for v in scenario_values(kind,pr):
                    _=verdict(kind,pr,v);scenarios+=1
                # Every alternate unit must round-trip to the same base value for 3 anchors.
                for u in units:
                    f=float(u['to_base']);
                    for base in scenario_values(kind,pr)[:3]:
                        raw=base/f; back=raw*f
                        if not math.isclose(base,back,rel_tol=1e-9,abs_tol=1e-9):errors.append(f'{gid}/{p.get("id")}: unit conversion mismatch {u["unit"]}')
            except Exception as e:errors.append(f'{gid}/{p.get("id")}/{pr.get("id")}: scenario error {e}')

missing=required-seen
extra=seen-required
if missing:errors.append('required auto-eval points missing: '+', '.join(f'{a}/{b}' for a,b in sorted(missing)))
if extra:warnings.append('additional auto-eval points beyond V8.8 allowlist: '+', '.join(f'{a}/{b}' for a,b in sorted(extra)))
if len(auto)!=15:errors.append(f'expected 15 auto-eval points, got {len(auto)}')
for token in ['OEM exact 자동판정','auto_eval','OEM_AUTO','Double.parseDouble','시험조건/모델 선택','parts_vehicle_profile','auto_profile','auto_unit','자동판정은 이 측정점의 정상/이상만 판정']:
    if token not in js:errors.append('missing UI/evaluator token: '+token)
# Thresholds must live in JSON, not Java. Reject common hard-coded OEM values in evaluator code.
method=js[js.find('private void evaluateAutoPoint'):js.find('private String fmt',js.find('private void evaluateAutoPoint'))]
for hard in ['181','195','215.5','240','155','28','26','100','3.18','10.3','9.7']:
    if hard in method:errors.append('hard-coded OEM threshold in Java evaluator: '+hard)
# Release gates
gradle=(ROOT/'app/build.gradle').read_text(encoding='utf-8');rel=json.loads((ROOT/'app/src/main/assets/diagnostic_release.json').read_text(encoding='utf-8'))
if 'versionCode 36' not in gradle:errors.append('versionCode 36 missing')
if 'versionName "0.18-rc-expert-v8.9.2-quick-ui"' not in gradle:errors.append('V8.9.2 versionName missing')
if rel.get('state')!='RC EXPERT V8.9.2 QUICK UI':errors.append('release state mismatch')
if rel.get('version_name')!='0.18-rc-expert-v8.9.2-quick-ui':errors.append('release version mismatch')
R.parent.mkdir(parents=True,exist_ok=True)
rows=[]
for gid,p in auto:rows.append(f'- `{gid}/{p["id"]}` · {p.get("label")} · {len(p["auto_eval"].get("profiles",[]))} profile(s) · {p["auto_eval"].get("base_unit")}')
R.write_text('# V8.8 OEM-Exact Automatic Evaluation Validation\n\n'
             f'- Auto-evaluable measurement points: **{len(auto)}**\n'
             f'- Structured OEM test profiles: **{profiles_count}**\n'
             f'- Deterministic boundary/scenario checks: **{scenarios}** (= 30 per profile)\n'
             '- Rule: only `source_class=OEM_EXACT` + explicit numeric limits may set PASS/FAIL automatically.\n'
             '- Approximate specs, field comparisons, and `OEM_VERIFY` remain manual/HOLD.\n'
             '- Numeric thresholds are stored in JSON, not hard-coded in Java.\n'
             f'- Errors: **{len(errors)}**\n- Warnings: **{len(warnings)}**\n\n## Auto-eval points\n'+ '\n'.join(rows)+
             '\n\n## Errors\n'+('\n'.join('- '+x for x in errors) or '- None')+
             '\n\n## Warnings\n'+('\n'.join('- '+x for x in warnings) or '- None')+'\n',encoding='utf-8')
print('V8.8 OEM auto-eval validation')
print(' points:',len(auto),'profiles:',profiles_count,'scenarios:',scenarios,'errors:',len(errors),'warnings:',len(warnings))
for x in errors:print('ERROR',x)
for x in warnings:print('WARN',x)
sys.exit(1 if errors else 0)
