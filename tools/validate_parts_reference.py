import json, pathlib, sys
BASE=pathlib.Path(__file__).resolve().parents[1]
AS=BASE/'app/src/main/assets'
errors=[]; warnings=[]
parts=json.load(open(AS/'parts_reference_v1.json'))
expert=json.load(open(AS/'expert_diag_v2.json'))
elec=json.load(open(AS/'electrical_diag_v1.json'))
engine=json.load(open(AS/'engine_diag_d24_v2.json'))
sm=json.load(open(AS/'engine_sensor_map_d24_v1.json'))

def chk(cond,msg):
    if not cond: errors.append(msg)

chk(parts.get('source',{}).get('document_id')=='SB5120C05','parts source id mismatch')
G=parts.get('groups',{})
for gid,g in G.items():
    for a in g.get('views',[]):
        chk((AS/a).exists(),f'missing asset {gid}: {a}')
    for p in g.get('parts',[]):
        chk(bool(p.get('no')) and bool(p.get('name')),f'blank part entry {gid}')
    if g.get('serial_required') and not g.get('parts') and gid!='MAST_CONFIG': warnings.append(f'{gid}: serial_required but no explicit parts list')
L=parts.get('links',{})
for domain, ids in [('expert',[x['id'] for x in expert['items']]),('electrical',list(elec['graphs'])),('engine',list(engine['graphs']))]:
    links=L.get(domain,{})
    chk(len(links)==len(ids),f'{domain} link count {len(links)} != {len(ids)}')
    for i in ids:
        chk(i in links,f'missing {domain} link {i}')
        if i in links:
            gs=links[i].get('groups',[]); chk(bool(gs),f'{domain} link no groups {i}')
            for g in gs: chk(g in G,f'{domain} {i} unknown group {g}')
# Sensor parts quality
sensor={x['id']:x for x in sm.get('sensors',[])}
for sid in ['BPS','WTS','OPTS','CAM','MAF']:
    chk(sid in sensor and sensor[sid].get('parts',{}).get('part_numbers'),f'sensor exact parts missing {sid}')
for sid in ['CRK','RPS']:
    chk(sensor.get(sid,{}).get('parts',{}).get('status')=='GROUP_ONLY',f'{sid} must remain GROUP_ONLY until exact Parts Book identity confirmed')

# Serial-aware applicability integrity
for gid,g in G.items():
    for part in g.get('parts',[]):
        for a in part.get('applications',[]):
            chk(a.get('code') in ('FDA0U','FDA0V','FDA0W','FDA0X'), f'{gid}/{part.get("no")}: bad model code')
            chk(isinstance(a.get('min'), int) and isinstance(a.get('max'), int) and a.get('min') <= a.get('max'), f'{gid}/{part.get("no")}: bad serial range')
for req in ('BRAKE_MODULE','STEER_CYLINDER','LIGHTING_STD','WIPER_FRONT','WIPER_REAR'):
    chk(req in G, 'missing v8.1 part group '+req)
# Critical serial splits must remain explicit.
for gid,early,late in [('AC_SYSTEM','210101-00490','210101-00569'),('WIPER_FRONT','A214302','300512-00042'),('WIPER_REAR','A214302','220210-01910')]:
    by={x.get('no'):x for x in G.get(gid,{}).get('parts',[])}
    chk(early in by and bool(by[early].get('applications')),f'{gid}: early serial split missing')
    chk(late in by and bool(by[late].get('applications')),f'{gid}: late serial split missing')

# Critical parts
critical={'ENGINE_ECU':'300618-00037B','ENGINE_HARNESS':'310207-02855E','STARTER':'300516-00034A','SEATBELT_INTERLOCK':'310207-01549','PARK_ACTUATOR':'300715-00153','AC_COMPRESSOR':'440205-00026'}
for gid,pn in critical.items():
    nums={x.get('no') for x in G.get(gid,{}).get('parts',[])}
    chk(pn in nums,f'critical part {pn} missing in {gid}')
# AC fan serial split
nums={x.get('no'):x for x in G['AC_SYSTEM'].get('parts',[])}
chk('210101-00490' in nums and '210101-00569' in nums,'AC condenser fan early/late split missing')

report={'source':parts['source']['document_id'],'groups':len(G),'expert_links':len(L['expert']),'electrical_links':len(L['electrical']),'engine_links':len(L['engine']),'sensor_map_count':len(sm.get('sensors',[])),'errors':errors,'warnings':warnings}
repdir=BASE/'build/reports';repdir.mkdir(parents=True,exist_ok=True)
json.dump(report,open(repdir/'parts_reference_validation.json','w'),ensure_ascii=False,indent=2)
with open(repdir/'parts_reference_validation.md','w') as f:
    f.write('# Parts Reference Validation\n\n')
    f.write(f"- Source: {report['source']}\n- Part groups: {report['groups']}\n- Expert links: {report['expert_links']}\n- Electrical links: {report['electrical_links']}\n- Engine links: {report['engine_links']}\n- Sensor map: {report['sensor_map_count']}\n- Errors: {len(errors)}\n- Warnings: {len(warnings)}\n")
    if errors: f.write('\n## Errors\n'+'\n'.join('- '+x for x in errors)+'\n')
    if warnings: f.write('\n## Warnings\n'+'\n'.join('- '+x for x in warnings)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
