#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
errors=[]
J=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic'
A=ROOT/'app/src/main/assets'

def need(ok,msg):
    if not ok: errors.append(msg)

tp=(J/'TestPointLocatorActivity.java').read_text(encoding='utf-8')
zoom=(J/'ZoomImageDialog.java').read_text(encoding='utf-8')
el=(J/'ElectricalDiagnosticActivity.java').read_text(encoding='utf-8')
expert=(J/'ExpertDiagnosticActivity.java').read_text(encoding='utf-8')
engine=(J/'EngineExpertDiagnosticActivity.java').read_text(encoding='utf-8')
tpd=json.loads((A/'test_point_locator_v1.json').read_text(encoding='utf-8'))
ed=json.loads((A/'electrical_diag_v1.json').read_text(encoding='utf-8'))

for token in [
    '지금 할 점검','빠른진단으로 돌아가기','전체 측정항목 · 상세기록 보기',
    '작업기록 · 새 작업 / 복사 / 초기화','시험조건 · OEM 근거 / 제한 보기',
    'currentPoint','openLocationOrCircuit','quick-point:','quick-pass:','quick-fail:'
]:
    need(token in tp,'quick UI token missing: '+token)

for bad in ['Generic technician signal-flow backdrop','CONTROL / HARNESS','SOURCE\\",145']:
    need(bad not in tp,'misleading generic electrical point map remains: '+bad)

need('shouldShowPointMap' in tp and '"전장".equals(sys)' in tp,
     'electrical generic point-map suppression missing')
for token in ['ScaleGestureDetector','onDoubleTap','matrix.postTranslate','zoom-image']:
    need(token in zoom,'zoom implementation/runtime anchor missing: '+token)

for name,text in [
    ('ElectricalDiagnosticActivity.java',el),
    ('EngineExpertDiagnosticActivity.java',engine),
    ('ExpertDiagnosticActivity.java',expert)
]:
    need('▶ 바로 측정' in text,name+' quick-measure entry missing')

need('지금 확인' in el,'electrical current-action-first card missing')
need('지금 확인' in engine,'engine current-action-first card missing')
need('상세 근거 · 도면 · 분해조건 보기' in expert,'expert details not collapsed by default')
need('회로 · 퓨즈/릴레이 · OEM 근거 보기' in el,'electrical evidence not collapsed by default')
for token in ['electrical-graph:','circuit-evidence:','circuit-image:']:
    need(token in el,'electrical runtime anchor missing: '+token)

lic=tpd.get('groups',{}).get('EL_LICENSE',{})
need(bool(lic.get('adaptive_branch')),'EL_LICENSE adaptive quick branch missing')
labels={p.get('id'):p.get('label','') for p in lic.get('points',[])}
for pid,word in [('LP1','미등/후미등'),('LP2','번호판등 +전원'),
                 ('LP3','접지 전압강하'),('LP4','LAMP')]:
    need(word in labels.get(pid,''),f'EL_LICENSE {pid} Korean-first label missing: {labels.get(pid)}')

lp4=next((p for p in lic.get('points',[]) if p.get('id')=='LP4'),{})
need(lp4.get('source_class')=='OEM_VERIFY',
     'EL_LICENSE LP4 source must remain OEM_VERIFY while manuals conflict')
need('상충' in (lp4.get('expected','')+lp4.get('note','')),
     'EL_LICENSE fuse-rating conflict note missing')

for cid in ['LICENSE_LAMP','REAR_LAMP','STROBE','HOURMETER','SEAT_BELT']:
    sd=ed.get('circuits',{}).get(cid,{}).get('simplified_diagram',{})
    labs=' | '.join(n.get('label','') for n in sd.get('nodes',[]))
    need(bool(labs),cid+' simplified diagram missing')
    if cid in ['LICENSE_LAMP','REAR_LAMP','STROBE','HOURMETER']:
        need('스위치/제어' not in labs,cid+' still uses generic switch/control node')

liclabs=' | '.join(n.get('label','') for n in
                  ed['circuits']['LICENSE_LAMP']['simplified_diagram']['nodes'])
for token in ['LAMP RELAY #4','REAR/TAIL FEED','LICENSE LAMP']:
    need(token in liclabs,'LICENSE_LAMP topology token missing: '+token)

b=(ROOT/'app/build.gradle').read_text(encoding='utf-8')
r=json.loads((A/'diagnostic_release.json').read_text(encoding='utf-8'))
need('versionCode 37' in b,'versionCode 37 missing')
need('versionName "0.18-rc-expert-v8.9.3-field-rebuild"' in b,'V8.9.3 versionName missing')
need(r.get('state')=='RC EXPERT V8.9.3 FIELD REBUILD','release state mismatch')
need(r.get('version_name')=='0.18-rc-expert-v8.9.3-field-rebuild','release version mismatch')

for f in J.glob('*.java'):
    s=f.read_text(encoding='utf-8')
    need(s.count('{')==s.count('}'),f.name+' brace mismatch')

print('v893_quick_ui_errors=',len(errors))
for e in errors: print('ERROR',e)
if errors: raise SystemExit(1)
print('V8.9.3 QUICK UI STATIC PASS')
