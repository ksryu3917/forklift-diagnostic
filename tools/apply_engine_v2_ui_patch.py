#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java'
MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'
GRADLE=ROOT/'app/build.gradle'; RELEASE=ROOT/'app/src/main/assets/diagnostic_release.json'
OLD='''Button e=btn("⚙ 엔진 진단 (D34 임시 기준)",false);e.setOnClickListener(v->go(new Screen("engine")));c.addView(e);'''
NEW='''Button e=btn("⚙ D24 엔진 현장진단",true);e.setOnClickListener(v->startActivity(new Intent(MainActivity.this,EngineExpertDiagnosticActivity.class)));c.addView(e);'''

def main():
    if not JAVA.exists(): raise SystemExit('MainActivity.java missing: overlay package onto clean v18-rc-auto checkout first')
    s=JAVA.read_text(encoding='utf-8')
    if 'EngineExpertDiagnosticActivity.class' not in s:
        if s.count(OLD)!=1: raise SystemExit(f'engine button baseline mismatch ({s.count(OLD)}); refusing unsafe patch')
        s=s.replace(OLD,NEW,1)
    JAVA.write_text(s,encoding='utf-8')
    if not MANIFEST.exists(): raise SystemExit('AndroidManifest.xml missing')
    m=MANIFEST.read_text(encoding='utf-8')
    additions=[]
    if '.EngineExpertDiagnosticActivity' not in m: additions.append('    <activity android:name=".EngineExpertDiagnosticActivity" android:exported="false" />\n')
    if '.EngineSensorMapActivity' not in m: additions.append('    <activity android:name=".EngineSensorMapActivity" android:exported="false" />\n')
    if additions:
        marker='''    <activity\n        android:name=".MainActivity"'''
        if m.count(marker)!=1: raise SystemExit('manifest MainActivity marker mismatch; refusing unsafe patch')
        m=m.replace(marker,''.join(additions)+'\n'+marker,1)
    MANIFEST.write_text(m,encoding='utf-8')
    if GRADLE.exists():
        g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 21',g);g=re.sub(r'versionName\s+"[^"]+"','versionName "0.18-rc-field-expert-v6"',g);GRADLE.write_text(g,encoding='utf-8')
    if RELEASE.exists():
        r=json.loads(RELEASE.read_text(encoding='utf-8'));r.update({'release':'v18','state':'RC FIELD EXPERT V6','version_name':'0.18-rc-field-expert-v6','git_commit_sha':'UNSTAMPED_LOCAL_PATCH'});RELEASE.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('D24 engine expert V2 UI patch applied')
if __name__=='__main__': main()
