#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/MainActivity.java'
GRADLE=ROOT/'app/build.gradle'
RELEASE=ROOT/'app/src/main/assets/diagnostic_release.json'

CAUSE_OLD=r"""        body.addView(p);

        if(c.has("graph")){
"""
CAUSE_NEW=r"""        body.addView(p);

        if(c.optBoolean("field_ready",false)){
            JSONArray tools=c.optJSONArray("field_tools");
            if(tools!=null && tools.length()>0){
                LinearLayout fc=card(); fc.addView(tv("현장 공구",16,true)); addArray(fc,tools,"• "); body.addView(fc);
            }
            JSONArray rule=c.optJSONArray("field_rule_out");
            if(rule!=null && rule.length()>0){
                LinearLayout fc=card(); fc.addView(tv("먼저 배제할 원인",16,true)); addArray(fc,rule,"• "); body.addView(fc);
            }
            JSONArray conf=c.optJSONArray("field_confirm");
            if(conf!=null && conf.length()>0){
                LinearLayout fc=card(); fc.addView(tv("확정 조건",16,true)); addArray(fc,conf,"• "); body.addView(fc);
            }
            String gate=c.optString("disassembly_gate");
            if(gate.length()>0){
                LinearLayout fc=card(); fc.addView(tv("분해 조건",16,true)); fc.addView(tv(gate,14,true)); body.addView(fc);
            }
            String review=c.optString("field_review_note");
            if(review.length()>0){
                LinearLayout fc=card(); fc.addView(tv("OEM 기준 제한",15,true)); fc.addView(tv(review,12,false)); body.addView(fc);
            }
        }

        if(c.has("graph")){
"""

TM_OLD=r"""    private void showTmResult(JSONObject n){
        LinearLayout r=card(); r.addView(tv("판정",16,true)); r.addView(tv(n.optString("result"),17,true));
        if(n.optString("action").length()>0){ r.addView(tv("다음 점검",15,true)); r.addView(tv(n.optString("action"),14,false)); }
        body.addView(r);
    }
"""
TM_NEW=r"""    private void showTmResult(JSONObject n){
        LinearLayout r=card();
        r.addView(tv("판정",16,true));
        r.addView(tv(n.optString("result"),17,true));
        if(n.optString("action").length()>0){
            r.addView(tv("다음 점검",15,true));
            r.addView(tv(n.optString("action"),14,false));
        }
        body.addView(r);

        JSONArray tools=n.optJSONArray("field_tools");
        if(tools!=null && tools.length()>0){
            LinearLayout c=card(); c.addView(tv("현장 공구",16,true)); addArray(c,tools,"• "); body.addView(c);
        }
        JSONArray tests=n.optJSONArray("field_test");
        if(tests!=null && tests.length()>0){
            LinearLayout c=card(); c.addView(tv("현장 확인 / 재현 시험",16,true)); addArray(c,tests,"① "); body.addView(c);
        }
        JSONArray rule=n.optJSONArray("rule_out");
        if(rule!=null && rule.length()>0){
            LinearLayout c=card(); c.addView(tv("먼저 배제할 원인",16,true)); addArray(c,rule,"• "); body.addView(c);
        }
        JSONArray conf=n.optJSONArray("confirm_if");
        if(conf!=null && conf.length()>0){
            LinearLayout c=card(); c.addView(tv("확정 조건",16,true)); addArray(c,conf,"• "); body.addView(c);
        }
        String gate=n.optString("disassembly_gate");
        if(gate.length()>0){
            LinearLayout c=card(); c.addView(tv("분해 조건",16,true)); c.addView(tv(gate,14,true)); body.addView(c);
        }
    }
"""

def replace_once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'{label}: expected exactly 1 baseline block, found {n}')
    return text.replace(old,new,1)

def main():
    if not JAVA.exists(): raise SystemExit(f'missing {JAVA}')
    text=JAVA.read_text(encoding='utf-8')
    # Idempotent: detect already-patched UI.
    if '현장 확인 / 재현 시험' not in text:
        text=replace_once(text,CAUSE_OLD,CAUSE_NEW,'cause field UI')
        text=replace_once(text,TM_OLD,TM_NEW,'TM result field UI')
        JAVA.write_text(text,encoding='utf-8')

    if GRADLE.exists():
        g=GRADLE.read_text(encoding='utf-8')
        g=re.sub(r'versionCode\s+\d+', 'versionCode 19', g)
        g=re.sub(r'versionName\s+"[^"]+"', 'versionName "0.18-rc-field"', g)
        GRADLE.write_text(g,encoding='utf-8')

    if RELEASE.exists():
        r=json.loads(RELEASE.read_text(encoding='utf-8'))
        r['release']='v18'
        r['state']='RC FIELD'
        r['version_name']='0.18-rc-field'
        # Workflow should stamp the real branch/SHA at build time. Until then do not lie.
        r['source_branch']=r.get('source_branch','v18-rc-auto')
        r['git_commit_sha']='UNSTAMPED_LOCAL_PATCH'
        RELEASE.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    print('field UI/build metadata patch applied')

if __name__=='__main__': main()
