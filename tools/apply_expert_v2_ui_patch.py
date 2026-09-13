#!/usr/bin/env python3
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java'
MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'
GRADLE=ROOT/'app/build.gradle'
RELEASE=ROOT/'app/src/main/assets/diagnostic_release.json'

OLD='''        body.addView(h);\n\n        LinearLayout p=card();'''
NEW='''        body.addView(h);\n\n        Button expert=btn("🛠 현장 전문가 진단 · 재작성 도면/측정점",true);\n        expert.setOnClickListener(v->{\n            Intent i=new Intent(MainActivity.this,ExpertDiagnosticActivity.class);\n            i.putExtra("cause_id",cid);\n            startActivity(i);\n        });\n        body.addView(expert);\n\n        LinearLayout p=card();'''

def replace_once(s,old,new,label):
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected exactly 1 baseline block, found {n}; refusing unsafe patch')
    return s.replace(old,new,1)

def main():
    if not JAVA.exists(): raise SystemExit('MainActivity.java missing: run in clean v18-rc-auto checkout after field/electrical overlays')
    s=JAVA.read_text(encoding='utf-8')
    if 'ExpertDiagnosticActivity.class' not in s:
        s=replace_once(s,OLD,NEW,'cause expert launch')
        JAVA.write_text(s,encoding='utf-8')
    if not MANIFEST.exists(): raise SystemExit('AndroidManifest.xml missing')
    m=MANIFEST.read_text(encoding='utf-8')
    if '.ExpertDiagnosticActivity' not in m:
        marker='''    <activity\n        android:name=".MainActivity"'''
        insert='''    <activity android:name=".ExpertDiagnosticActivity" android:exported="false" />\n\n    <activity\n        android:name=".MainActivity"'''
        if m.count(marker)!=1: raise SystemExit('manifest MainActivity marker mismatch; refusing unsafe patch')
        m=m.replace(marker,insert,1);MANIFEST.write_text(m,encoding='utf-8')
    if GRADLE.exists():
        g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 21',g);g=re.sub(r'versionName\s+"[^"]+"','versionName "0.18-rc-expert"',g);GRADLE.write_text(g,encoding='utf-8')
    if RELEASE.exists():
        r=json.loads(RELEASE.read_text(encoding='utf-8'));r.update({'release':'v18','state':'RC EXPERT','version_name':'0.18-rc-expert','git_commit_sha':'UNSTAMPED_LOCAL_PATCH'});RELEASE.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('expert v2 UI patch applied')
if __name__=='__main__': main()
