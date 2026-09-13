#!/usr/bin/env python3
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java'
MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'
GRADLE=ROOT/'app/build.gradle'
RELEASE=ROOT/'app/src/main/assets/diagnostic_release.json'

DIAG_OLD='''        Button e=btn("⚙ 엔진 진단 (D34 임시 기준)",false);e.setOnClickListener(v->go(new Screen("engine")));c.addView(e);body.addView(c);'''
DIAG_NEW='''        Button e=btn("⚙ 엔진 진단 (D34 임시 기준)",false);e.setOnClickListener(v->go(new Screen("engine")));c.addView(e);\n        Button el=btn("⚡ 전기 / 차체전장 진단",true);el.setOnClickListener(v->startActivity(new Intent(MainActivity.this,ElectricalDiagnosticActivity.class)));c.addView(el);\n        body.addView(c);'''

SEARCH_OLD='''            if(count==0)body.addView(tv("검색 결과가 없습니다.",15,true));\n'''
SEARCH_NEW='''            Intent ei=new Intent(MainActivity.this,ElectricalDiagnosticActivity.class);ei.putExtra("query",term);\n            Button eb=btn("⚡ 전기/차체전장에서도 검색 · "+term,false);eb.setOnClickListener(v->startActivity(ei));body.addView(eb);\n            count++;\n            if(count==0)body.addView(tv("검색 결과가 없습니다.",15,true));\n'''

SYSTEMS_OLD='''        for(String s:set){Button b=btn(s,false);b.setOnClickListener(v->go(new Screen("symptoms",s)));body.addView(b);}\n    }\n'''
SYSTEMS_NEW='''        for(String s:set){Button b=btn(s,false);b.setOnClickListener(v->go(new Screen("symptoms",s)));body.addView(b);}\n        Button eb=btn("전기 / 차체전장",true);eb.setOnClickListener(v->startActivity(new Intent(MainActivity.this,ElectricalDiagnosticActivity.class)));body.addView(eb);\n    }\n'''

def replace_once(s,old,new,label):
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: baseline mismatch ({n}), refusing unsafe patch')
    return s.replace(old,new,1)

def main():
    if not JAVA.exists(): raise SystemExit('MainActivity.java missing: run inside checkout of v18-rc-auto')
    s=JAVA.read_text(encoding='utf-8')
    if 'ElectricalDiagnosticActivity.class' not in s:
        s=replace_once(s,DIAG_OLD,DIAG_NEW,'diagnosis electrical button')
    if '전기/차체전장에서도 검색' not in s:
        s=replace_once(s,SEARCH_OLD,SEARCH_NEW,'electrical search bridge')
    if 'Button eb=btn("전기 / 차체전장"' not in s:
        s=replace_once(s,SYSTEMS_OLD,SYSTEMS_NEW,'electrical system button')
    JAVA.write_text(s,encoding='utf-8')

    if not MANIFEST.exists(): raise SystemExit('AndroidManifest.xml missing')
    m=MANIFEST.read_text(encoding='utf-8')
    if '.ElectricalDiagnosticActivity' not in m:
        marker='''    <activity\n        android:name=".MainActivity"'''
        insert='''    <activity android:name=".ElectricalDiagnosticActivity" android:exported="false" />\n\n    <activity\n        android:name=".MainActivity"'''
        if m.count(marker)!=1: raise SystemExit('manifest activity marker mismatch; refusing unsafe patch')
        m=m.replace(marker,insert,1);MANIFEST.write_text(m,encoding='utf-8')

    if GRADLE.exists():
        g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 20',g);g=re.sub(r'versionName\s+"[^"]+"','versionName "0.18-rc-field-elec"',g);GRADLE.write_text(g,encoding='utf-8')
    if RELEASE.exists():
        r=json.loads(RELEASE.read_text(encoding='utf-8'));r.update({'release':'v18','state':'RC FIELD ELEC','version_name':'0.18-rc-field-elec','git_commit_sha':'UNSTAMPED_LOCAL_PATCH'});RELEASE.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('electrical UI/search/system patch applied')
if __name__=='__main__':main()
