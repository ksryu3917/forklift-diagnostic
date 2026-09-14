#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
java=(root/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
errors=[]
if '엔진 진단 (D34 임시 기준)' in java: errors.append('legacy D34 engine entry still visible')
for token in ['EngineExpertDiagnosticActivity.class','ElectricalDiagnosticActivity.class','ExpertDiagnosticActivity.class']:
    if token not in java: errors.append(f'MainActivity missing {token}')
for name in ['ElectricalDiagnosticActivity','EngineExpertDiagnosticActivity','EngineSensorMapActivity','ExpertDiagnosticActivity','FieldLocationMapActivity','PartsReferenceActivity','TestPointLocatorActivity']:
    if f'android:name=".{name}"' not in manifest: errors.append(f'manifest missing {name}')
if manifest.count('android.intent.action.MAIN') != 1: errors.append('launcher MAIN count != 1')
if manifest.count('android.intent.category.LAUNCHER') != 1: errors.append('launcher category count != 1')
# Guard the exact user-facing D24 entry and removal of the old screen route.
if '⚙ D24 엔진 현장진단' not in java: errors.append('D24 engine button text missing')
if 'new Screen("engine")' in java and 'case "engine":engine();' in java:
    # Legacy method may remain for reference, but it must not be reachable from the visible engine button.
    if 'e.setOnClickListener(v->go(new Screen("engine")))' in java: errors.append('visible engine button still routes to legacy engine()')
print('integration_errors=',len(errors))
for e in errors: print('ERROR',e)
if errors: raise SystemExit(1)
print('V8.9.1 runtime integration PASS')
