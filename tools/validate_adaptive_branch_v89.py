#!/usr/bin/env python3
import json, random, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/test_point_locator_v1.json'
d=json.loads(p.read_text(encoding='utf-8'))
errors=[]; warnings=[]; scenarios=0; rule_count=0; groups=[]
valid_status={'PASS','FAIL','HOLD'}

def matches(rule, st):
    w=rule.get('when',{})
    return bool(w) and all(st.get(k,'')==v for k,v in w.items())

def first_match(g, st):
    for r in g['adaptive_branch'].get('rules',[]):
        if matches(r,st): return r.get('id')
    return None

for gid,g in d.get('groups',{}).items():
    ab=g.get('adaptive_branch')
    if not ab: continue
    groups.append(gid)
    pids={x.get('id') for x in g.get('points',[])}
    rules=ab.get('rules',[]); seen=set(); rule_count+=len(rules)
    if not rules: errors.append(f'{gid}: adaptive_branch rules empty')
    for idx,r in enumerate(rules):
        rid=r.get('id','')
        if not rid or rid in seen: errors.append(f'{gid}: duplicate/missing rule id {rid!r}')
        seen.add(rid)
        w=r.get('when',{})
        if not w: errors.append(f'{gid}/{rid}: empty when')
        for pid,status in w.items():
            if pid not in pids: errors.append(f'{gid}/{rid}: unknown condition point {pid}')
            if status not in valid_status: errors.append(f'{gid}/{rid}: invalid status {status}')
        for pid in r.get('next_points',[]):
            if pid not in pids: errors.append(f'{gid}/{rid}: unknown next point {pid}')
        for field in ('title','assessment','level'):
            if not r.get(field): errors.append(f'{gid}/{rid}: missing {field}')
        # Base scenario must select its own ordered rule; catches shadowing/subset mistakes.
        base=dict(w)
        fm=first_match(g,base)
        if fm!=rid: errors.append(f'{gid}/{rid}: shadowed by {fm} on base conditions')
        # 30 controlled variants: keep required states fixed, perturb irrelevant points with blank/HOLD.
        others=sorted(pids-set(w))
        for n in range(30):
            st=dict(w)
            for j,pid in enumerate(others):
                # HOLD is deliberately non-decisive; alternate with unmeasured state.
                if (n+j)%3==0: st[pid]='HOLD'
            got=first_match(g,st)
            scenarios+=1
            if got!=rid:
                errors.append(f'{gid}/{rid}: scenario {n} matched {got}; {st}')
                break

# Required high-value coverage.
required={'START_VDROP','EL_CHARGE','OSS_HEALTH','TM_PRESSURE_TAPS','HYD_MAIN_RELIEF','EL_FR_CONTROL','ENG_ECU_HEALTH','ENG_VREF','ENG_CRANK_START','ENG_FUEL_RAIL','ENG_SYNC','ENG_INJECTOR','ENG_AIR_BOOST','ENG_COOLING','ENG_LUBE','ENG_PREHEAT','ENG_COMBUSTION','EL_CAN_NETWORK','EL_AC_POWER','EL_STOP_LAMP'}
miss=sorted(required-set(groups))
if miss: errors.append('missing required adaptive groups: '+', '.join(miss))

# Real-world regression patterns / intentional logic checks.
examples=[
 ('START_VDROP', {'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'FAIL'}, 'ST04'),
 ('START_VDROP', {'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'PASS','S6':'FAIL'}, 'ST05'),
 ('START_VDROP', {'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'PASS','S6':'PASS'}, 'ST06'),
 ('TM_PRESSURE_TAPS', {'TM6':'PASS','TM4':'FAIL','TM5':'PASS'}, 'TM03'),
 ('TM_PRESSURE_TAPS', {'TM6':'PASS','TM5':'FAIL','TM4':'PASS'}, 'TM04'),
 ('OSS_HEALTH', {'O1':'PASS','O2':'PASS','O3':'PASS','O4':'PASS','O5':'FAIL'}, 'OS05'),
 ('ENG_CRANK_START', {'CS1':'PASS','CS2':'PASS','CS3':'FAIL','CS4':'FAIL'}, 'CS03'),
 ('EL_STOP_LAMP', {'SL3':'PASS','SL4':'FAIL','SL5':'PASS'}, 'SL04'),
]
for gid,st,want in examples:
    got=first_match(d['groups'][gid],st);scenarios+=1
    if got!=want: errors.append(f'regression {gid}: wanted {want}, got {got} for {st}')

report=root/'build/reports/adaptive_branch_v89.md';report.parent.mkdir(parents=True,exist_ok=True)
lines=['# V8.9 Adaptive Multi-point Branch Validation','',f'- Adaptive groups: **{len(groups)}**',f'- Explicit ordered rules: **{rule_count}**',f'- Synthetic branch scenarios: **{scenarios}**',f'- Errors: **{len(errors)}**',f'- Warnings: **{len(warnings)}**','', '## Covered groups']
lines += [f'- {g}: {len(d["groups"][g]["adaptive_branch"]["rules"])} rules' for g in groups]
lines += ['', '## Guardrails','- A matched rule narrows a circuit/system; it does not automatically authorize part replacement.','- No new voltage/pressure threshold is created by the adaptive engine.','- Rule conditions only consume PASS/FAIL/HOLD states already recorded by the worksheet or OEM-exact auto evaluator.']
if errors: lines += ['','## Errors']+[f'- {x}' for x in errors]
report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:12]))
if errors: sys.exit(1)
