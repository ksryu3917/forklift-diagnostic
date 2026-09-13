from pathlib import Path
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
manifest=root/'app/src/main/AndroidManifest.xml'
if not manifest.exists():
    raise SystemExit(f'Missing {manifest}')
s=manifest.read_text(encoding='utf-8')
activities=[
    'PartsReferenceActivity',
    'TestPointLocatorActivity',
    'FieldLocationMapActivity',
    'EngineSensorMapActivity',
    'EngineExpertDiagnosticActivity',
    'ExpertDiagnosticActivity',
    'ElectricalDiagnosticActivity',
]
marker='</application>'
if marker not in s: raise SystemExit('Manifest has no </application>')
changed=False
for name in activities:
    token=f'android:name=".{name}"'
    if token not in s:
        s=s.replace(marker,f'        <activity android:name=".{name}" android:exported="false" />\n    '+marker)
        changed=True
        print('Added',name,'to manifest')
if changed: manifest.write_text(s,encoding='utf-8')
else: print('All V8.4 activities already present')
