#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
java=root/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java'
manifest=root/'app/src/main/AndroidManifest.xml'
if not java.exists(): raise SystemExit(f'Missing {java}')
if not manifest.exists(): raise SystemExit(f'Missing {manifest}')

s=java.read_text(encoding='utf-8')

# 1) D24 expert engine must replace the legacy temporary D34 entry.
old_engine='''Button e=btn("⚙ 엔진 진단 (D34 임시 기준)",false);e.setOnClickListener(v->go(new Screen("engine")));c.addView(e);'''
new_engine='''Button e=btn("⚙ D24 엔진 현장진단",true);e.setOnClickListener(v->startActivity(new Intent(MainActivity.this,EngineExpertDiagnosticActivity.class)));c.addView(e);'''
if 'EngineExpertDiagnosticActivity.class' not in s:
    n=s.count(old_engine)
    if n!=1: raise SystemExit(f'engine entry baseline mismatch: {n}')
    s=s.replace(old_engine,new_engine,1)

# 2) Electrical expert entry on the vehicle-diagnosis screen.
needle='''        body.addView(c);\n    }\n\n    private void searchSymptoms(String term){'''
if 'Button el=btn("⚡ 전기 / 차체전장 진단"' not in s:
    replacement='''        Button el=btn("⚡ 전기 / 차체전장 진단",true);el.setOnClickListener(v->startActivity(new Intent(MainActivity.this,ElectricalDiagnosticActivity.class)));c.addView(el);\n        body.addView(c);\n    }\n\n    private void searchSymptoms(String term){'''
    n=s.count(needle)
    if n!=1: raise SystemExit(f'electrical entry baseline mismatch: {n}')
    s=s.replace(needle,replacement,1)

# 3) Bridge symptom search to electrical catalog as well.
search_old='''            if(count==0)body.addView(tv("검색 결과가 없습니다.",15,true));\n        }catch(Exception e){fatal(e.toString());}\n    }'''
if '전기/차체전장에서도 검색' not in s:
    search_new='''            Intent ei=new Intent(MainActivity.this,ElectricalDiagnosticActivity.class);ei.putExtra("query",term);\n            Button eb=btn("⚡ 전기/차체전장에서도 검색 · "+term,false);eb.setOnClickListener(v->startActivity(ei));body.addView(eb);\n            if(count==0)body.addView(tv("기계/유압 증상 일치 없음 · 전장 검색을 확인하세요.",15,true));\n        }catch(Exception e){fatal(e.toString());}\n    }'''
    n=s.count(search_old)
    if n!=1: raise SystemExit(f'electrical search bridge mismatch: {n}')
    s=s.replace(search_old,search_new,1)

# 4) Every legacy cause page must expose the 268-cause expert screen.
expert_old='''        body.addView(h);\n\n        LinearLayout p=card();'''
if 'ExpertDiagnosticActivity.class' not in s:
    expert_new='''        body.addView(h);\n\n        Button expert=btn("🛠 현장 전문가 진단 · 재작성 도면/측정점",true);\n        expert.setOnClickListener(v->{\n            Intent i=new Intent(MainActivity.this,ExpertDiagnosticActivity.class);\n            i.putExtra("cause_id",cid);\n            startActivity(i);\n        });\n        body.addView(expert);\n\n        LinearLayout p=card();'''
    n=s.count(expert_old)
    if n!=1: raise SystemExit(f'expert cause bridge mismatch: {n}')
    s=s.replace(expert_old,expert_new,1)

java.write_text(s,encoding='utf-8')

# Manifest safety: all activities reachable from the V8.9 graph must be declared.
m=manifest.read_text(encoding='utf-8')
activities=[
    'ElectricalDiagnosticActivity','EngineExpertDiagnosticActivity','EngineSensorMapActivity',
    'ExpertDiagnosticActivity','FieldLocationMapActivity','PartsReferenceActivity','TestPointLocatorActivity'
]
marker='</application>'
if marker not in m: raise SystemExit('manifest missing </application>')
for name in activities:
    token=f'android:name=".{name}"'
    if token not in m:
        m=m.replace(marker,f'    <activity android:name=".{name}" android:exported="false" />\n  {marker}',1)
manifest.write_text(m,encoding='utf-8')
print('V8.9.1 runtime integration applied: D24 + electrical + expert + manifest')
