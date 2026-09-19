#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
p = ROOT / 'app/src/main/assets/manual_library_catalog.json'
errors=[]
def need(ok,msg):
    if not ok: errors.append(msg)

need(p.exists(),'manual_library_catalog.json missing')
if p.exists():
    d=json.loads(p.read_text(encoding='utf-8'))
    docs=d.get('documents',[])
    need(d.get('schema_version')=='1.0','manual catalog schema mismatch')
    need(len(docs)>=169,f'manual catalog must index at least 169 technical PDFs, got {len(docs)}')
    names=[x.get('name','') for x in docs]
    need('26062204701.pdf' not in names,'private/non-maintenance insurance document must not be indexed')
    need('downloadfile.pdf' not in names,'private/non-maintenance purchase document must not be indexed')
    ids=[x.get('id') for x in docs]
    need(len(ids)==len(set(ids)),'manual catalog ids must be unique')
    for x in docs:
        for k in ('id','name','manufacturer','document_type','review_state','search_text'):
            need(bool(x.get(k)),f"{x.get('id','?')}: missing {k}")
    b=next((x for x in docs if x.get('name')=='정비_B15S~B35S-7.pdf'),None)
    need(bool(b),'SM1033-00 source missing')
    if b:
        need(b.get('manual_code')=='SM1033-00','SM1033-00 manual code mismatch')
        need(b.get('page_count')==610,'SM1033-00 page count mismatch')
        required={'B15S-7','B18S-7','B20S-7','B25S-7','B30S-7','B32S-7','B35S-7','B20SE-7','B25SE-7'}
        need(required.issubset(set(b.get('models',[]))),'SM1033-00 model coverage incomplete')
        need(b.get('review_state')=='identity_verified','SM1033-00 identity must be verified')
        facts=b.get('verified_field_facts',[])
        need(len(facts)>=7,'SM1033-00 verified field facts incomplete')
        fids={f.get('id') for f in facts}
        for fid in {'SM1033-F1-LOAD-VOLTAGE-DROP','SM1033-F2-ACCEL-SIGNAL','SM1033-BRAKE-BLEED','SM1033-STEER-PRESSURE'}:
            need(fid in fids,'SM1033-00 required field fact missing: '+fid)
    pol=d.get('diagnostic_source_policy',{})
    for k in ('field_priority','no_cross_model_guess','no_unverified_threshold','catalog_is_not_diagnosis'):
        need(bool(pol.get(k)),f'manual source policy missing {k}')

print('manual_library_catalog_errors=',len(errors))
for e in errors: print('ERROR',e)
if errors: raise SystemExit(1)
print('V8.9.4 MANUAL LIBRARY CATALOG PASS')
