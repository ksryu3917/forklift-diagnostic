import json, collections, sys, re
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
d=json.load(open(ROOT/'app/src/main/assets/expert_diag_v2.json',encoding='utf-8'))
items=d['items']

def combo(it):
    return (tuple(it.get('field_sequence',[])),json.dumps(it.get('measurement_points',[]),ensure_ascii=False,sort_keys=True),tuple(it.get('confirm_if',[])),it.get('disassembly_gate',''))
def normcause(s):
    s=re.sub(r'\s+','',s).replace('어셈블리','').replace('조립품','').replace('브레이크','')
    s=s.replace('유압계통','유압라인').replace('작동유온도규정이탈','작동유과열')
    if '공기' in s and ('유압' in s or '라인' in s): return '유압라인공기'
    return s

g=collections.defaultdict(list)
for it in items:g[combo(it)].append(it)
shared=[v for v in g.values() if len(v)>1]
repeat_same=[]; boundary=[]; unresolved=[]
for v in shared:
    if len({normcause(i['cause']) for i in v})==1:
        repeat_same.append(v); continue
    if all(i.get('specificity_gate',{}).get('status')=='SHARED_ASSEMBLY_BOUNDARY' for i in v):
        boundary.append(v); continue
    unresolved.append(v)
repeat_items=[i for v in repeat_same for i in v]
boundary_items=[i for v in boundary for i in v]
unresolved_items=[i for v in unresolved for i in v]
# A cause is individually distinct if it is not in an exact shared signature at all.
shared_ids={i['id'] for v in shared for i in v}
unique_items=[i for i in items if i['id'] not in shared_ids]
pre=[i for i in items if i.get('specificity_gate',{}).get('status')=='CAUSE_SPECIFIC_PRE_TEARDOWN']
resolved_count=len(unique_items)+len(repeat_items)+len(boundary_items)

lines=['# DIAGNOSTIC SPECIFICITY AUDIT V8.3.1','',
'이 검증은 서로 다른 원인이 완전히 같은 측정점/점검순서/확정조건/분해조건으로 처리되는지를 찾고, 그 공유가 합리적인 “같은 원인 재사용/같은 어셈블리 내부 한계”인지 구분한다.','',
f'- Total causes: **{len(items)}**',
f'- Individually distinct full signatures: **{len(unique_items)}**',
f'- Same-root-cause reuse accepted: **{len(repeat_items)} causes / {len(repeat_same)} groups**',
f'- Explicit shared-assembly boundary accepted: **{len(boundary_items)} causes / {len(boundary)} groups**',
f'- Explicit cause-specific pre-teardown gates present: **{len(pre)}**',
f'- Unresolved cross-cause shared signatures: **{len(unresolved_items)} causes / {len(unresolved)} groups**','',
'## Quality rule','',
'- 같은 원인이 여러 증상에서 동일한 시험으로 확인되는 것은 정상적인 재사용이다.',
'- 서로 다른 세부원인을 분해 전 구분할 수 없으면 앱은 세부부품을 확정하지 않고 `SHARED_ASSEMBLY_BOUNDARY`까지로만 판정해야 한다.',
'- 분해 전 구분 가능한 원인은 `CAUSE_SPECIFIC_PRE_TEARDOWN` 분리시험이 있어야 한다.',
'- unresolved cross-cause group이 1개라도 있으면 “모든 원인이 전문가 수준으로 분리됨”이라고 선언하지 않는다.','',
'## Unresolved groups']
if not unresolved: lines.append('\n- 없음')
for n,v in enumerate(sorted(unresolved,key=lambda v:(v[0].get('system',''),-len(v))),1):
    lines.append(f'\n### {n}. {v[0].get("system")} · {len(v)} causes')
    for it in v: lines.append(f'- `{it["id"]}` {it["symptom"]} → **{it["cause"]}**')
lines += ['','## Accepted shared-assembly groups']
for n,v in enumerate(sorted(boundary,key=lambda v:(v[0].get('system',''),-len(v))),1):
    b=v[0].get('specificity_gate',{}).get('assembly_boundary','')
    lines.append(f'- {v[0].get("system")} · {len(v)} causes → **{b}**')
out=ROOT/'build/reports/diagnostic_specificity_v83.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:19])); print('Report:',out)
if unresolved: raise SystemExit(2)
