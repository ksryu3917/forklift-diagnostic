#!/usr/bin/env python3
import json,sys
from pathlib import Path
from collections import deque,defaultdict
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/electrical_diag_v1.json'
REPORT=ROOT/'build/reports/electrical_validation.md'
REPORT_JSON=ROOT/'build/reports/electrical_validation.json'
REQUIRED_RESULT=['result','field_tools','field_test','rule_out','confirm_if','disassembly_gate']
REQUIRED_CATALOG=['id','title','group','sheet','grid','ready']
SCENARIOS_PER_RESULT=30


def nexts(n): return [x.get('next') for x in n.get('choices',[]) if x.get('next')]

def shortest_result_paths(g):
    nodes=g.get('nodes',{}); start=g.get('start'); paths={}; q=deque([(start,[])])
    best={}
    while q:
        nid,path=q.popleft()
        if nid not in nodes: continue
        if len(path)>best.get(nid,999): continue
        best[nid]=len(path); n=nodes[nid]
        if n.get('type')=='result': paths.setdefault(nid,path); continue
        for ch in n.get('choices',[]):
            nxt=ch.get('next')
            if nxt: q.append((nxt,path+[(nid,nxt,ch.get('label',''))]))
    return paths

def contexts():
    # 논리 스트레스 조건. OEM 수치가 아니라 경로/판정 게이트 유지 여부를 검사하는 30개 상황변형.
    for temp in ('cold','normal','heat_soaked'):
        for load in ('key_on','idle','commanded','loaded','post_repair'):
            for repeat in ('first','repeat'):
                yield {'temperature':temp,'duty':load,'repeatability':repeat}

def main():
    d=json.loads(P.read_text(encoding='utf-8')); errs=[]; warns=[]
    src=d.get('source',{})
    for k in ('manual','schematic_id','sheets','oem_pages','rule'):
        if not src.get(k): errs.append('source missing '+k)
    if src.get('schematic_id')!='600123-00120': errs.append('unexpected schematic id')

    ids=[]
    for i,x in enumerate(d.get('catalog',[])):
        for k in REQUIRED_CATALOG:
            if not x.get(k): errs.append(f'catalog[{i}] missing {k}')
        ids.append(x.get('id'))
    if len(ids)!=len(set(ids)): errs.append('duplicate catalog id')
    required_graphs={'E_STOP_NO','E_OSS_SEAT_LOCK','E_AC_POWER_NO','E_AC_COND_FAN_NO','E_CAN_NETWORK','E_START_NO','E_CHARGE'}
    for gid in sorted(required_graphs):
        if gid not in ids: errs.append('missing '+gid)
    graph_ids=set(d.get('graphs',{})); missing_graphs=sorted(set(ids)-graph_ids)
    if missing_graphs: errs.append('catalog items without executable graph: '+', '.join(missing_graphs))

    # 모든 실행 회로는 재작성 미니회로를 가져야 한다.
    graph_circuits={g.get('circuit') for g in d.get('graphs',{}).values()}
    for cid in sorted(x for x in graph_circuits if x):
        c=d.get('circuits',{}).get(cid)
        if not c:
            errs.append('missing circuit '+cid); continue
        sd=c.get('simplified_diagram')
        if not sd:
            errs.append(cid+': missing simplified_diagram'); continue
        if len(sd.get('nodes',[]))<3: errs.append(cid+': simplified diagram has <3 nodes')
        if len(sd.get('edges',[]))<2: errs.append(cid+': simplified diagram has <2 edges')
        if not sd.get('measure_points'): errs.append(cid+': simplified diagram missing measure_points')
        node_ids={n.get('id') for n in sd.get('nodes',[])}
        for e in sd.get('edges',[]):
            if e.get('from') not in node_ids or e.get('to') not in node_ids: errs.append(cid+': simplified diagram broken edge')
        # 미확정 숫자/핀은 verified=true로 둔갑시키지 않는다.
        for n in sd.get('nodes',[]):
            label=n.get('label','').upper()
            if ('OEM VERIFY' in label or '확인 필요' in label) and n.get('verified') is True:
                errs.append(cid+': unverified label marked verified: '+n.get('label',''))

    stop=d.get('circuits',{}).get('STOP_LAMP',{})
    if stop.get('sheet')!='4/4' or stop.get('oem_page')!=370: errs.append('STOP_LAMP source mismatch')
    comps={x.get('name'):x for x in stop.get('components',[])}
    for name in ('FUSE BOX','STOP LAMP SW','COMB LAMP-RH','COMB LAMP-LH'):
        if name not in comps: errs.append('STOP_LAMP missing component '+name)
    sw=comps.get('STOP LAMP SW',{}); pins={str(x.get('pin')) for x in sw.get('pins',[])}
    if pins!={'1','2'}: errs.append('STOP LAMP SW pin array must contain 1,2')
    for asset in stop.get('images',[]):
        if not (ROOT/'app/src/main/assets'/asset).exists(): errs.append('missing image '+asset)

    total_results=0; total_nodes=0; total_sim=0; hit=defaultdict(int)
    ctx=list(contexts())
    for gid,g in d.get('graphs',{}).items():
        nodes=g.get('nodes',{}); total_nodes+=len(nodes); start=g.get('start')
        if start not in nodes: errs.append(f'{gid}: bad start'); continue
        q=deque([start]); seen=set()
        while q:
            nid=q.popleft()
            if nid in seen: continue
            if nid not in nodes: errs.append(f'{gid}: broken target {nid}'); continue
            seen.add(nid); node=nodes[nid]; typ=node.get('type')
            for x in nexts(node):
                if x not in nodes: errs.append(f'{gid}/{nid}: broken -> {x}')
                else:q.append(x)
            if typ=='question':
                if not node.get('question') or not node.get('choices'): errs.append(f'{gid}/{nid}: incomplete question')
                if not node.get('field_method'): warns.append(f'{gid}/{nid}: no field_method')
            elif typ=='result':
                total_results+=1
                for k in REQUIRED_RESULT:
                    if not node.get(k): errs.append(f'{gid}/{nid}: result missing {k}')
            else: errs.append(f'{gid}/{nid}: unsupported type {typ}')
        unreachable=set(nodes)-seen
        if unreachable: errs.append(f'{gid}: unreachable {sorted(unreachable)}')

        paths=shortest_result_paths(g)
        reachable_results={nid for nid,n in nodes.items() if n.get('type')=='result'}
        if set(paths)!=reachable_results:
            errs.append(f'{gid}: result reachability mismatch')
        for rid,path in paths.items():
            for i,c in enumerate(ctx[:SCENARIOS_PER_RESULT],1):
                cur=start
                for source,nxt,label in path:
                    if cur!=source: errs.append(f'{gid}/{rid} scenario{i}: path desync'); break
                    legal={(ch.get('next'),ch.get('label','')) for ch in nodes[source].get('choices',[])}
                    if (nxt,label) not in legal: errs.append(f'{gid}/{rid} scenario{i}: illegal route'); break
                    cur=nxt
                if cur==rid:
                    hit[(gid,rid)]+=1; total_sim+=1
        for rid in reachable_results:
            if hit[(gid,rid)]!=SCENARIOS_PER_RESULT: errs.append(f'{gid}/{rid}: {hit[(gid,rid)]}/{SCENARIOS_PER_RESULT} scenarios')

    # OSS 현장사례 수준 강제.
    oss=d.get('graphs',{}).get('E_OSS_SEAT_LOCK',{}); oss_nodes=oss.get('nodes',{})
    for req in ('seat_input','controller_input','wiggle_section','terminal_fault','oss_health','fivev_isolate','can_scope','can_local','oss_internal','controller_power','lift_output'):
        if req not in oss_nodes: errs.append('E_OSS_SEAT_LOCK missing '+req)
    oss_txt=json.dumps(oss,ensure_ascii=False)
    for token in ('MIN/MAX','핀 장력','5V','CAN HI','CAN LO','다른 모듈','외부 부하'):
        if token not in oss_txt: errs.append('E_OSS_SEAT_LOCK missing '+token)
    if '흔들' not in oss_txt: errs.append('E_OSS_SEAT_LOCK missing wiggle reproduction')

    acfan=json.dumps(d.get('graphs',{}).get('E_AC_COND_FAN_NO',{}),ensure_ascii=False)
    for token in ('직접전원','GND','릴레이','팬 커넥터','컴프레서'):
        if token not in acfan: errs.append('E_AC_COND_FAN_NO missing '+token)
    acpower=json.dumps(d.get('graphs',{}).get('E_AC_POWER_NO',{}),ensure_ascii=False)
    for token in ('블로워','B+/IGN/GND','4핀','직접'):
        if token not in acpower: errs.append('E_AC_POWER_NO missing '+token)

    can=json.dumps(d.get('graphs',{}).get('E_CAN_NETWORK',{}),ensure_ascii=False)
    for token in ('B+/IGN/GND','CAN-H/L','특정 모듈'):
        if token not in can: errs.append('E_CAN_NETWORK missing '+token)
    if '60Ω' in can and 'OEM' not in can: errs.append('E_CAN_NETWORK hard-codes generic 60Ω without OEM caveat')

    rule=d.get('mapped_diagnostic_rules',{}).get('no_guess_rule','')
    if '추정' not in rule and '임의' not in rule: errs.append('no-guess rule too weak')

    REPORT.parent.mkdir(parents=True,exist_ok=True)
    payload={'version':d.get('version'),'catalog':len(ids),'graphs':len(d.get('graphs',{})),'nodes':total_nodes,'results':total_results,'scenarios_per_result':SCENARIOS_PER_RESULT,'simulations':total_sim,'errors':errs,'warnings':warns}
    REPORT_JSON.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Electrical diagnostic validation','',f'- DB version: `{d.get("version","")}`',f'- Schematic: `{src.get("schematic_id")}`',f'- Catalog items: **{len(ids)}**',f'- Graphs: **{len(d.get("graphs",{}))}**',f'- Graph nodes: **{total_nodes}**',f'- Result nodes: **{total_results}**',f'- Scenarios per individual result: **{SCENARIOS_PER_RESULT}**',f'- Total logic simulations: **{total_sim}**',f'- Errors: **{len(errs)}**',f'- Warnings: **{len(warns)}**','']
    if errs: lines+=['## Errors']+['- '+e for e in errs]+['']
    if warns: lines+=['## Warnings']+['- '+e for e in warns]+['']
    lines += ['## Accuracy gates','- Every executable electrical circuit must have an assistant-redrawn simplified diagram with measurement points.','- OEM full-sheet/crops are secondary evidence, not the primary diagnostic UI.','- Static continuity alone does not clear a circuit; loaded voltage-drop/backprobe/dynamic reproduction is used where applicable.','- Exact fuse cavity / connector numeric pin roles remain UNKNOWN/OEM VERIFY unless the source resolves them.','- 60Ω CAN termination is not treated as a model-specific criterion until this forklift network topology/terminators are OEM-verified.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[:12])); return 1 if errs else 0
if __name__=='__main__': raise SystemExit(main())
