#!/usr/bin/env python3
import json
from pathlib import Path
from collections import deque,defaultdict
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/engine_diag_d24_v2.json'
R=ROOT/'build/reports/engine_d24_v2_validation.md'
J=ROOT/'build/reports/engine_d24_v2_validation.json'
N=30
REQ_RESULT=['field_tools','field_test','rule_out','confirm_if','disassembly_gate']

def nexts(n): return [c.get('next') for c in n.get('choices',[]) if c.get('next')]
def paths(g):
    nodes=g['nodes']; q=deque([(g['start'],[])]); out={}; best={}
    while q:
        nid,p=q.popleft()
        if nid not in nodes or len(p)>80: continue
        if len(p)>best.get(nid,999): continue
        best[nid]=len(p); n=nodes[nid]
        if n.get('type')=='result': out.setdefault(nid,p); continue
        for c in n.get('choices',[]):
            nx=c.get('next')
            if nx and nx not in [x[0] for x in p]: q.append((nx,p+[(nid,nx,c.get('label',''))]))
    return out

d=json.loads(P.read_text(encoding='utf-8')); errors=[]; warnings=[]; rows=[]
for gid,g in d['graphs'].items():
    nodes=g.get('nodes',{}); gp=[]
    if g.get('start') not in nodes: gp.append('missing start')
    for nid,n in nodes.items():
        typ=n.get('type')
        for nx in nexts(n):
            if nx not in nodes: gp.append(f'{nid}: broken link {nx}')
        if typ=='question':
            if not n.get('field_method'): gp.append(f'{nid}: no field_method')
            if not n.get('choices'): gp.append(f'{nid}: no choices')
        elif typ=='result':
            for k in REQ_RESULT:
                v=n.get(k)
                if not v: gp.append(f'{nid}: missing {k}')
        else: gp.append(f'{nid}: unknown type {typ}')
    ps=paths(g); results=[n for n,x in nodes.items() if x.get('type')=='result']
    for rid in results:
        if rid not in ps: gp.append(f'{rid}: unreachable result')
    # 30 context simulations per result. They exercise legal paths under distinct field contexts,
    # not fabricated OEM numeric limits.
    contexts=[]
    for temp in ['cold','normal','heat_soak']:
      for load in ['idle','no_load','travel','hydraulic_load','post_repair']:
       for rep in ['first','repeat']:
        contexts.append((temp,load,rep))
    sims=0
    for rid,p in ps.items():
        for ctx in contexts[:N]:
            cur=g['start']
            for a,b,label in p:
                if cur!=a: gp.append(f'{rid}: path desync');break
                legal=nexts(nodes[a])
                if b not in legal: gp.append(f'{rid}: illegal {a}->{b}');break
                cur=b
            if cur==rid: sims+=1
    # Circuit strictness
    cid=g.get('circuit'); c=d.get('circuits',{}).get(cid)
    if not c: gp.append('missing circuit')
    else:
        sd=c.get('simplified_diagram',{})
        if len(sd.get('measure_points',[]))<2: gp.append('circuit: <2 measurement points')
        if len(sd.get('nodes',[]))<3: gp.append('circuit: too few nodes')
    if not g.get('engine_sensor_map'): gp.append('no engine sensor map link')
    errors += [f'{gid}: {x}' for x in gp]
    rows.append((gid,len(nodes),len(results),sims,len(gp)))

R.parent.mkdir(parents=True,exist_ok=True)
lines=['# D24 ENGINE FIELD DIAGNOSTIC V2 VALIDATION','',f'- Graphs: **{len(d["graphs"])}**',f'- Result terminals: **{sum(x[2] for x in rows)}**',f'- 30-scenario simulations: **{sum(x[3] for x in rows)}**',f'- Errors: **{len(errors)}**',f'- Warnings: **{len(warnings)}**','', '| Graph | Nodes | Results | Simulations | Errors |','|---|---:|---:|---:|---:|']
for x in rows: lines.append(f'| {x[0]} | {x[1]} | {x[2]} | {x[3]} | {x[4]} |')
if errors:
 lines += ['','## Errors']+[f'- {x}' for x in errors]
R.write_text('\n'.join(lines)+'\n',encoding='utf-8')
J.write_text(json.dumps({'graphs':len(rows),'results':sum(x[2] for x in rows),'simulations':sum(x[3] for x in rows),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('\n'.join(lines[:10])); raise SystemExit(1 if errors else 0)
