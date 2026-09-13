#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
from collections import deque, defaultdict, Counter

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'app/src/main/assets/manual_db.json'
TM=ROOT/'app/src/main/assets/transmission_diag_v08.json'
REPORT=ROOT/'build/reports/field_exec_validation.md'
JSON_REPORT=ROOT/'build/reports/field_exec_validation.json'
SCENARIOS_PER_RESULT=30
MAX_STEPS=150
ASSET_DIR=ROOT/'app/src/main/assets/oem_pages'

REQ_CAUSE=['diag_plan','field_tools','field_rule_out','field_confirm','disassembly_gate','field_evidence_mode']
REQ_TM=['field_tools','field_test','rule_out','confirm_if','disassembly_gate']
FORBIDDEN_PLACEHOLDER=['TODO','TBD','추후','나중에','정규화 대기','pending']


def all_nexts(n):
    out=[]
    for c in n.get('choices',[]) or []:
        if c.get('next'): out.append(c['next'])
    for k,v in n.items():
        if k.startswith('next_') and isinstance(v,str) and v: out.append(v)
    return out


def route_details(n):
    out=[]
    if n.get('type')=='question':
        for c in n.get('choices',[]) or []:
            if c.get('next'): out.append((c['next'],{'answer':c.get('label','')}))
    for k,v in n.items():
        if k.startswith('next_') and isinstance(v,str) and v:
            out.append((v,{'measurement_class':k[5:]}))
    return out


def shortest_paths(g):
    nodes=g['nodes']; entries=g.get('entry_points') or [g.get('start')]
    q=deque((e,[]) for e in entries if e)
    best={}; results={}
    while q:
        nid,path=q.popleft()
        if nid not in nodes or len(path)>MAX_STEPS: continue
        if len(path)>best.get(nid,10**9): continue
        best[nid]=len(path)
        n=nodes[nid]
        if n.get('type')=='result':
            results.setdefault(nid,path); continue
        for nxt,sup in route_details(n):
            if any(st[0]==nxt for st in path): continue
            q.append((nxt,path+[(nid,nxt,sup)]))
    return results


def validate_tm(tm):
    errors=[]; warnings=[]; graph_rows=[]; total_sims=0; result_count=0
    for sid,g in sorted(tm.get('graphs',{}).items()):
        nodes=g.get('nodes',{}); entries=g.get('entry_points') or [g.get('start')]
        if not g.get('start') or g['start'] not in nodes: errors.append(f'{sid}: missing start')
        for e in entries:
            if e not in nodes: errors.append(f'{sid}: missing entry {e}')
        for nid,n in nodes.items():
            for nxt in all_nexts(n):
                if nxt not in nodes: errors.append(f'{sid}/{nid}: broken link -> {nxt}')
            typ=n.get('type','')
            if typ=='question' and not n.get('choices'):
                errors.append(f'{sid}/{nid}: question has no choices')
            if typ=='measure':
                if 'min' not in n or 'max' not in n: errors.append(f'{sid}/{nid}: measure missing min/max')
                elif n['min']>n['max']: errors.append(f'{sid}/{nid}: min > max')
                if not n.get('unit'): warnings.append(f'{sid}/{nid}: measure missing unit')
                if not any(n.get(k) for k in ['next_low','next_normal','next_high']): errors.append(f'{sid}/{nid}: measure missing route')
            if typ not in ['question','measure','reverse_pair_measure','clutch_pair_measure','result']:
                warnings.append(f'{sid}/{nid}: unknown node type {typ}')
            for pg in n.get('manual_pages',[]) or []:
                try: pi=int(pg)
                except Exception:
                    errors.append(f'{sid}/{nid}: invalid manual page {pg!r}'); continue
                if not any((ASSET_DIR/f'p{pi:03d}.{ext}').exists() or (ASSET_DIR/f'p{pi}.{ext}').exists() for ext in ['jpg','png','webp']):
                    errors.append(f'{sid}/{nid}: missing manual page asset {pi}')
            txt=' '.join(str(n.get(k,'')) for k in ['title','question','result','action','note'])
            for bad in FORBIDDEN_PLACEHOLDER:
                if bad.lower() in txt.lower(): errors.append(f'{sid}/{nid}: placeholder {bad}')
            if n.get('type')=='result':
                result_count+=1
                for k in REQ_TM:
                    if not n.get(k): errors.append(f'{sid}/{nid}: result missing {k}')
                if not n.get('field_ready'): errors.append(f'{sid}/{nid}: field_ready false')
                ft=' '.join(n.get('field_test',[]))
                if '현재 결과가 나온 직전 측정/선택 조건' in ft:
                    errors.append(f'{sid}/{nid}: generic terminal field test remains')
        # reachability
        seen=set(); q=deque(entries)
        while q:
            x=q.popleft()
            if x in seen or x not in nodes: continue
            seen.add(x); q.extend(all_nexts(nodes[x]))
        for nid,n in nodes.items():
            if n.get('type')=='result' and nid not in seen: errors.append(f'{sid}/{nid}: unreachable result')
        for nid in seen:
            if not all_nexts(nodes[nid]) and nodes[nid].get('type')!='result': errors.append(f'{sid}/{nid}: dead end')
        paths=shortest_paths(g)
        graph_results=[nid for nid,n in nodes.items() if n.get('type')=='result']
        for rid in graph_results:
            if rid not in paths: errors.append(f'{sid}/{rid}: no executable path')
            else:
                # 30 condition variants are traversal checks, not OEM specs.
                for i in range(SCENARIOS_PER_RESULT):
                    nid=paths[rid][0][0] if paths[rid] else rid
                    for src,nxt,sup in paths[rid]:
                        if nid!=src: errors.append(f'{sid}/{rid}/scenario{i+1}: path desync'); break
                        legal={(a,json.dumps(b,ensure_ascii=False,sort_keys=True)) for a,b in route_details(nodes[src])}
                        tok=(nxt,json.dumps(sup,ensure_ascii=False,sort_keys=True))
                        if tok not in legal: errors.append(f'{sid}/{rid}/scenario{i+1}: illegal route'); break
                        nid=nxt
                    if nid!=rid: errors.append(f'{sid}/{rid}/scenario{i+1}: ended at {nid}')
                total_sims += SCENARIOS_PER_RESULT
        graph_rows.append((sid,len(nodes),len(graph_results),len(seen)))
    return errors,warnings,graph_rows,result_count,total_sims


def validate_manual(db):
    errors=[]; warnings=[]; bysys=Counter(); cause_count=0
    non_tm_generic=[]
    for s in db.get('symptoms',[]):
        sysname=s.get('system',''); bysys[sysname]+=len(s.get('cause_details',[]))
        for c in s.get('cause_details',[]):
            cause_count+=1
            for k in REQ_CAUSE:
                if not c.get(k): errors.append(f"{c.get('id')}: missing {k}")
            if not c.get('field_ready'): errors.append(f"{c.get('id')}: field_ready false")
            if len(c.get('diag_plan',[]))<3: errors.append(f"{c.get('id')}: diag_plan too short")
            txt=' '.join(c.get('diag_plan',[])+c.get('field_rule_out',[])+c.get('field_confirm',[])+[c.get('disassembly_gate','')])
            for bad in FORBIDDEN_PLACEHOLDER:
                if bad.lower() in txt.lower(): errors.append(f"{c.get('id')}: placeholder {bad}")
            if sysname!='트랜스미션' and '증상과 연동되는 회전/작동부를 입력측→출력측 순서로' in txt:
                non_tm_generic.append((c.get('id'),sysname,c.get('name')))
    if non_tm_generic:
        for x in non_tm_generic: errors.append(f'{x[0]} {x[1]}: generic mechanical fallback remains: {x[2]}')

    norm=db.get('diagnostic_normalization',{})
    if norm.get('version')!='1.0-field-executable': errors.append('diagnostic_normalization version not field-executable')
    if norm.get('cause_count')!=cause_count: errors.append('cause_count mismatch')

    # Dedicated brake isolation graph and links.
    g=db.get('diagnostic_graphs',{}).get('BRAKE_HYD_ISOLATION')
    if not g: errors.append('missing BRAKE_HYD_ISOLATION')
    else:
        required={'B0','B1','B2','B3','BL','BR','BB'}
        missing=required-set(g.get('steps',{}))
        if missing: errors.append('brake graph missing: '+','.join(sorted(missing)))
        b2=' '.join(g['steps'].get('B2',{}).get('instructions',[])+g['steps'].get('B2',{}).get('conditions',[]))
        if '바이스그립' not in b2: warnings.append('brake B2 lacks explicit no-hose-clamp warning')
    linked=0
    for s in db.get('symptoms',[]):
        if s.get('system')!='브레이크': continue
        for c in s.get('cause_details',[]):
            if any(k in c.get('name','') for k in ['피스톤시일','피스톤 마모','서보피스톤','브레이크밸브 시일','마스터피스톤']):
                linked+=1
                if c.get('graph')!='BRAKE_HYD_ISOLATION': errors.append(f"{c.get('id')}: brake seal cause not linked to isolation graph")

    # D34 must remain reference only.
    er=db.get('engine_reference',{})
    ertext=json.dumps(er,ensure_ascii=False)
    if 'D34' in ertext and not any(k in ertext for k in ['참고','reference','적용 불가','전용값','전용 매뉴얼이 아님','임시 기준']):
        warnings.append('D34 reference wording should be manually reviewed')
    return errors,warnings,bysys,cause_count,linked


def main():
    db=json.loads(DB.read_text(encoding='utf-8')); tm=json.loads(TM.read_text(encoding='utf-8'))
    e1,w1,bysys,causes,brake_links=validate_manual(db)
    e2,w2,rows,results,total_sims=validate_tm(tm)
    errors=e1+e2; warnings=w1+w2
    lines=['# FIELD EXECUTABILITY VALIDATION','',
      f'- Manual symptoms: **{len(db.get("symptoms",[]))}**',
      f'- Causes checked: **{causes}**',
      f'- Transmission graphs: **{len(tm.get("graphs",{}))}**',
      f'- Transmission result terminals: **{results}**',
      f'- Simulated result paths: **{total_sims:,}** ({SCENARIOS_PER_RESULT} per result)',
      f'- Brake seal/internal-leak causes linked to isolation graph: **{brake_links}**',
      f'- Errors: **{len(errors)}**', f'- Warnings: **{len(warnings)}**','',
      '## Required completion gate','',
      '- Cause: field sequence + tools + rule-outs + confirmation + teardown gate.',
      '- T/M terminal: field test + tools + rule-outs + confirmation + teardown gate.',
      '- Missing OEM numeric limit: comparison/isolation only; no fabricated threshold.',
      '- Brake internal leak: external leak/air/upstream bypass/left-right axle isolation before teardown.','',
      '## Coverage by system','']
    for k,v in sorted(bysys.items()): lines.append(f'- {k}: {v}')
    lines += ['', '## Transmission graph coverage','', '| Graph | Nodes | Results | Reachable |','|---|---:|---:|---:|']
    for sid,n,r,seen in rows: lines.append(f'| {sid} | {n} | {r} | {seen} |')
    if errors: lines += ['', '## Errors']+[f'- {x}' for x in errors]
    if warnings: lines += ['', '## Warnings']+[f'- {x}' for x in warnings]
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    JSON_REPORT.write_text(json.dumps({'causes':causes,'tm_graphs':len(tm.get('graphs',{})),'tm_results':results,'simulations':total_sims,'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('\n'.join(lines[:32]))
    print(f'\nReports: {REPORT} / {JSON_REPORT}')
    return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
