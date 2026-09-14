#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
errors=[]; warnings=[]
J=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic'
tp=(J/'TestPointLocatorActivity.java').read_text(encoding='utf-8')
zoom=(J/'ZoomImageDialog.java').read_text(encoding='utf-8')
el=(J/'ElectricalDiagnosticActivity.java').read_text(encoding='utf-8')
assets=ROOT/'app/src/main/assets'
tpd=json.loads((assets/'test_point_locator_v1.json').read_text(encoding='utf-8'))
ed=json.loads((assets/'electrical_diag_v1.json').read_text(encoding='utf-8'))

for token in ['지금 할 점검','빠른진단으로 돌아가기','전체 측정항목 · 상세기록 보기','작업기록 · 새 작업 / 복사 / 초기화','시험조건 · OEM 근거 / 제한 보기','currentPoint','openLocationOrCircuit']:
    if token not in tp: errors.append('quick UI token missing: '+token)
for bad in ['Generic technician signal-flow backdrop','CONTROL / HARNESS','SOURCE\",145']:
    if bad in tp: errors.append('misleading generic electrical point map remains: '+bad)
if 'shouldShowPointMap' not in tp or '"전장".equals(sys)' not in tp: errors.append('electrical generic point-map suppression missing')
if 'ScaleGestureDetector' not in zoom or 'onDoubleTap' not in zoom or 'matrix.postTranslate' not in zoom: errors.append('pinch/pan/double-tap zoom implementation incomplete')
for name in ['ElectricalDiagnosticActivity.java','EngineExpertDiagnosticActivity.java','ExpertDiagnosticActivity.java']:
    text=(J/name).read_text(encoding='utf-8')
    if '▶ 바로 측정' not in text: errors.append(name+' quick-measure entry missing')
    if name!='ExpertDiagnosticActivity.java' and '지금 확인' not in text: errors.append(name+' current-action-first card missing')
if '상세 근거 · 도면 · 분해조건 보기' not in (J/'ExpertDiagnosticActivity.java').read_text(encoding='utf-8'): errors.append('expert details not collapsed by default')
if '회로 · 퓨즈/릴레이 · OEM 근거 보기' not in el: errors.append('electrical evidence not collapsed by default')
for name in ['ElectricalDiagnosticActivity.java','ExpertDiagnosticActivity.java','FieldLocationMapActivity.java','TestPointLocatorActivity.java']:
    text=(J/name).read_text(encoding='utf-8')
    if 'ZoomImageDialog.show' not in text: errors.append(name+' does not use shared zoom viewer')
for name in ['EngineExpertDiagnosticActivity.java','EngineSensorMapActivity.java','PartsReferenceActivity.java']:
    text=(J/name).read_text(encoding='utf-8')
    if 'ZoomImageDialog.show' not in text: errors.append(name+' zoom integration missing')

lic=tpd.get('groups',{}).get('EL_LICENSE',{})
if not lic.get('adaptive_branch'): errors.append('EL_LICENSE adaptive quick branch missing')
labels={p.get('id'):p.get('label','') for p in lic.get('points',[])}
for pid,word in [('LP1','미등/후미등'),('LP2','번호판등 +전원'),('LP3','접지 전압강하'),('LP4','LAMP 릴레이')]:
    if word not in labels.get(pid,''): errors.append(f'EL_LICENSE {pid} Korean-first label missing: {labels.get(pid)}')
# LP4 must not present a single fuse rating as undisputed OEM exact.
lp4=next((p for p in lic.get('points',[]) if p.get('id')=='LP4'),{})
if lp4.get('source_class')!='OEM_VERIFY': errors.append('EL_LICENSE LP4 source must be OEM_VERIFY while manuals conflict')
if '상충' not in (lp4.get('expected','')+lp4.get('note','')): errors.append('EL_LICENSE fuse-rating conflict note missing')

for cid in ['LICENSE_LAMP','REAR_LAMP','STROBE','HOURMETER','SEAT_BELT']:
    sd=ed.get('circuits',{}).get(cid,{}).get('simplified_diagram',{})
    labs=' | '.join(n.get('label','') for n in sd.get('nodes',[]))
    if not labs: errors.append(cid+' simplified diagram missing')
    if cid in ['LICENSE_LAMP','REAR_LAMP','STROBE','HOURMETER'] and '스위치/제어' in labs: errors.append(cid+' still uses generic switch/control node')
liclabs=' | '.join(n.get('label','') for n in ed['circuits']['LICENSE_LAMP']['simplified_diagram']['nodes'])
for token in ['LAMP RELAY #4','REAR/TAIL FEED','LICENSE LAMP']:
    if token not in liclabs: errors.append('LICENSE_LAMP topology token missing: '+token)

# Release identity
b=(ROOT/'app/build.gradle').read_text(encoding='utf-8')
r=json.loads((assets/'diagnostic_release.json').read_text(encoding='utf-8'))
if 'versionCode 36' not in b: errors.append('versionCode 36 missing')
if 'versionName "0.18-rc-expert-v8.9.2-quick-ui"' not in b: errors.append('V8.9.2 versionName missing')
if r.get('state')!='RC EXPERT V8.9.2 QUICK UI': errors.append('release state mismatch')
if r.get('version_name')!='0.18-rc-expert-v8.9.2-quick-ui': errors.append('release version mismatch')

# rough syntax balance
for f in J.glob('*.java'):
    s=f.read_text(encoding='utf-8')
    if s.count('{')!=s.count('}'): errors.append(f.name+' brace mismatch')

print('v892_quick_ui_errors=',len(errors),'warnings=',len(warnings))
for e in errors: print('ERROR',e)
for w in warnings: print('WARN',w)
if errors: raise SystemExit(1)
print('V8.9.2 QUICK UI PASS')
