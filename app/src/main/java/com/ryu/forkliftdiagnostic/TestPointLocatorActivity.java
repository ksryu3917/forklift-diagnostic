package com.ryu.forkliftdiagnostic;

import android.app.*;
import android.os.*;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;
import android.text.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class TestPointLocatorActivity extends Activity {
    private JSONObject data, group; private String groupId=""; private LinearLayout body; private final LinkedHashSet<String> pointFilter=new LinkedHashSet<>();
    private android.content.SharedPreferences prefs,sessionPref; private TextView sessionSummary,branchSummary; private final LinkedHashSet<String> visiblePointIds=new LinkedHashSet<>();
    private String activeSession="",sessionLabel="";
    private String sourceGraphId=""; private boolean detailMode=false;
    private final int NAVY=Color.rgb(16,38,58), BLUE=Color.rgb(17,117,214), ORANGE=Color.rgb(222,126,20), BG=Color.rgb(242,245,247), GREEN=Color.rgb(28,125,80);

    @Override public void onCreate(Bundle b){super.onCreate(b);prefs=getSharedPreferences("field_measurements_v1",MODE_PRIVATE);sessionPref=getSharedPreferences("field_measurement_session",MODE_PRIVATE);ensureSession();try{data=new JSONObject(readAsset("test_point_locator_v1.json"));resolve();if(group==null)home();else render();}catch(Exception e){fatal("측정포인트 로딩 오류: "+e.getMessage());}}
    private String readAsset(String n)throws Exception{InputStream is=getAssets().open(n);ByteArrayOutputStream os=new ByteArrayOutputStream();byte[] b=new byte[8192];int r;while((r=is.read(b))>0)os.write(b,0,r);is.close();return os.toString(StandardCharsets.UTF_8.name());}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);} 
    private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}
    private TextView tv(String s,int sp,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));v.setPadding(dp(3),dp(5),dp(3),dp(5));if(bold)v.setTypeface(null,Typeface.BOLD);return v;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;}
    private Button btn(String s,boolean primary){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(13);b.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);b.setTextColor(primary?Color.WHITE:Color.rgb(25,30,35));b.setBackground(bg(primary?BLUE:Color.rgb(231,236,240),10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(50));p.setMargins(0,dp(3),0,dp(3));b.setLayoutParams(p);return b;}

    private void resolve()throws Exception{
        String id=getIntent().getStringExtra("group_id");
        String directGraph=getIntent().getStringExtra("graph_id"); if(directGraph!=null) sourceGraphId=directGraph;
        String cid=getIntent().getStringExtra("cause_id");
        if((id==null||id.isEmpty())&&cid!=null&&!cid.isEmpty()){
            JSONObject cm=data.optJSONObject("cause_map");
            JSONObject m=cm==null?null:cm.optJSONObject(cid);
            if(m!=null){id=m.optString("group");JSONArray a=m.optJSONArray("point_ids");if(a!=null)for(int i=0;i<a.length();i++)pointFilter.add(a.optString(i));}
        }
        if(id==null||id.isEmpty()){
            String gid=getIntent().getStringExtra("graph_id");
            if(gid!=null){sourceGraphId=gid;id=data.getJSONObject("graph_map").optString(gid,"");}
        }
        if(id==null||id.isEmpty()){
            String sys=getIntent().getStringExtra("system");
            if(sys!=null)id=data.getJSONObject("system_map").optString(sys,"");
        }
        if(id!=null&&!id.isEmpty()&&data.getJSONObject("groups").has(id)){groupId=id;group=data.getJSONObject("groups").getJSONObject(id);}
    }
    private void base(String title){LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(7),dp(8),dp(7));top.setBackgroundColor(NAVY);Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(50)));TextView t=tv(title,18,true);t.setTextColor(Color.WHITE);top.addView(t,new LinearLayout.LayoutParams(0,dp(50),1));root.addView(top);ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);root.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);}

    private void home()throws Exception{base("측정포인트 / 압력탭");LinearLayout i=card();i.addView(tv("부품번호보다 먼저 · 어디에 프로브/게이지를 물릴지",17,true));i.addView(tv(data.optString("rule"),12,false));body.addView(i);JSONObject gs=data.getJSONObject("groups");Iterator<String> it=gs.keys();while(it.hasNext()){String id=it.next();JSONObject g=gs.getJSONObject(id);Button b=btn(g.optString("title"),false);b.setOnClickListener(v->{android.content.Intent x=getIntent();x.putExtra("group_id",id);x.removeExtra("graph_id");x.removeExtra("system");recreate();});body.addView(b);}}

    private void render()throws Exception{
        base("빠른점검 · "+group.optString("system"));
        visiblePointIds.clear();
        JSONArray all=group.getJSONArray("points");
        for(int i=0;i<all.length();i++){
            JSONObject x=all.getJSONObject(i);
            if(pointFilter.isEmpty()||pointFilter.contains(x.optString("id"))) visiblePointIds.add(x.optString("id"));
        }
        String mode=getIntent().getStringExtra("mode"); detailMode="detail".equals(mode);
        if(detailMode) renderDetail(); else renderQuick();
    }

    private void renderQuick()throws Exception{
        LinearLayout head=card();
        head.addView(tv(group.optString("title"),19,true));
        head.addView(tv(group.optString("summary"),12,false));
        TextView sess=tv("작업 · "+sessionLabel+"   |   "+progressText(),11,true);sess.setTextColor(Color.rgb(75,85,95));head.addView(sess);
        body.addView(head);

        JSONObject rule=matchedAdaptiveRule();
        if(rule!=null){
            LinearLayout branch=card();
            branch.addView(tv("현재까지 판정",14,true));
            String a=rule.optString("assessment"); if(a.isEmpty()) a=rule.optString("title");
            branch.addView(tv(a,13,true));
            JSONArray ex=rule.optJSONArray("excludes");
            if(ex!=null&&ex.length()>0){StringBuilder b=new StringBuilder("우선순위 하향 · ");for(int i=0;i<ex.length();i++){if(i>0)b.append(" / ");b.append(ex.optString(i));}branch.addView(tv(b.toString(),11,false));}
            body.addView(branch);
        }

        JSONObject current=currentPoint(rule);
        if(current!=null){
            addQuickPoint(current);
        }else{
            LinearLayout done=card();
            JSONObject fail=firstFailedPoint();
            if(fail!=null){done.addView(tv("이상 구간이 잡혔습니다.",18,true));if(!fail.optString("decision").isEmpty())done.addView(tv(displayText(fail.optString("decision")),14,true));}
            else done.addView(tv("이 화면의 필수 점검이 끝났습니다.",18,true));
            String sum=adaptiveSummaryText();if(!sum.isEmpty())done.addView(tv(displayText(sum),13,false));
            Button abnormal=btn("이상으로 기록된 항목만 보기",true);abnormal.setOnClickListener(v->showAbnormalSummary());done.addView(abnormal);body.addView(done);
        }

        LinearLayout nav=card();
        Button loc=btn("◎ 위치 / 실제 회로 보기",true);loc.setOnClickListener(v->openLocationOrCircuit());nav.addView(loc);
        Button detail=btn("전체 측정항목 · 상세기록 보기",false);detail.setOnClickListener(v->{getIntent().putExtra("mode","detail");recreate();});nav.addView(detail);
        Button record=btn("작업기록 · 새 작업 / 복사 / 초기화",false);record.setOnClickListener(v->showWorkMenu());nav.addView(record);
        Button evidence=btn("시험조건 · OEM 근거 / 제한 보기",false);evidence.setOnClickListener(v->showEvidenceDialog());nav.addView(evidence);
        body.addView(nav);
    }

    private void renderDetail()throws Exception{
        LinearLayout head=card();head.addView(tv(group.optString("title"),18,true));head.addView(tv("상세모드 · 모든 포인트를 한 번에 확인할 때만 사용",12,false));head.addView(tv("작업 · "+sessionLabel+"   |   "+progressText(),11,true));body.addView(head);
        Button quick=btn("← 빠른진단으로 돌아가기",true);quick.setOnClickListener(v->{getIntent().removeExtra("mode");recreate();});body.addView(quick);
        Button loc=btn("◎ 위치 / 실제 회로 보기",false);loc.setOnClickListener(v->openLocationOrCircuit());body.addView(loc);
        if(shouldShowPointMap()){
            Bitmap bm=drawPointMap();LinearLayout mc=card();mc.addView(tv("측정 위치 개요",15,true));ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);iv.setOnClickListener(v->showBitmap(bm));mc.addView(iv,new LinearLayout.LayoutParams(-1,dp(250)));mc.addView(tv("그림을 누르면 두 손가락 확대 가능",11,false));body.addView(mc);
        }
        JSONArray pts=group.getJSONArray("points");int shown=0;for(int i=0;i<pts.length();i++){JSONObject x=pts.getJSONObject(i);if(!visiblePointIds.contains(x.optString("id")))continue;addDetailedPoint(++shown,x);}
        Button evidence=btn("시험조건 · OEM 근거 / 제한 보기",false);evidence.setOnClickListener(v->showEvidenceDialog());body.addView(evidence);
    }

    private JSONObject currentPoint(JSONObject rule){
        JSONArray preferred=rule==null?null:rule.optJSONArray("next_points");
        if(rule!=null && preferred!=null){
            for(int i=0;i<preferred.length();i++){JSONObject p=pointById(preferred.optString(i));if(p!=null&&visiblePointIds.contains(p.optString("id"))&&pref(p.optString("id"),"status").isEmpty())return p;}
            return null;
        }
        JSONArray pts=group.optJSONArray("points");
        boolean hasAdaptive=group.optJSONObject("adaptive_branch")!=null;
        if(pts!=null)for(int i=0;i<pts.length();i++){
            JSONObject p=pts.optJSONObject(i);if(p==null)continue;String id=p.optString("id");if(!visiblePointIds.contains(id))continue;
            String st=pref(id,"status");
            if(!hasAdaptive && "FAIL".equals(st)) return null;
            if(st.isEmpty()) return p;
        }
        return null;
    }

    private JSONObject firstFailedPoint(){JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);if(p!=null&&visiblePointIds.contains(p.optString("id"))&&"FAIL".equals(pref(p.optString("id"),"status")))return p;}return null;}

    private void addQuickPoint(JSONObject p){
        final String pid=p.optString("id");
        LinearLayout c=card();
        TextView now=tv("지금 할 점검",14,true);now.setTextColor(BLUE);c.addView(now);
        TextView title=tv(displayText(p.optString("label")),21,true);c.addView(title);
        c.addView(tv("어디서 · "+displayText(p.optString("where")),15,true));
        c.addView(tv("연결 · "+displayText(p.optString("connect")),14,false));
        c.addView(tv("상태 · "+displayText(p.optString("condition")),14,false));
        if(!p.optString("expected").isEmpty())c.addView(tv("기준 · "+displayText(p.optString("expected")),14,true));
        if(!p.optString("note").isEmpty())c.addView(tv("주의 · "+displayText(p.optString("note")),11,false));

        if(p.optJSONObject("auto_eval")!=null){
            Button value=btn("측정값 입력 → OEM 자동판정",true);value.setOnClickListener(v->showPointRecordDialog(p,true));c.addView(value);
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);
            Button ok=miniBtn("수동 정상");Button bad=miniBtn("수동 이상");
            ok.setOnClickListener(v->{setManualStatus(pid,"PASS");recreate();});bad.setOnClickListener(v->{setManualStatus(pid,"FAIL");recreate();});
            row.addView(ok);row.addView(bad);c.addView(row);
        }else{
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);
            Button ok=decisionBtn("정상",GREEN);Button bad=decisionBtn("이상",Color.rgb(180,45,45));
            ok.setOnClickListener(v->{setManualStatus(pid,"PASS");recreate();});bad.setOnClickListener(v->{setManualStatus(pid,"FAIL");recreate();});
            row.addView(ok,new LinearLayout.LayoutParams(0,dp(58),1));row.addView(bad,new LinearLayout.LayoutParams(0,dp(58),1));c.addView(row);
        }
        Button note=btn("측정값 / 메모 기록",false);note.setOnClickListener(v->showPointRecordDialog(p,false));c.addView(note);
        String old=pref(pid,"status");if(!old.isEmpty())c.addView(tv("현재 기록 · "+statusKo(old),12,true));
        body.addView(c);

        if(!p.optString("decision").isEmpty()){
            LinearLayout next=card();next.addView(tv("이상이면",13,true));next.addView(tv(displayText(p.optString("decision")),14,true));body.addView(next);
        }
    }

    private Button decisionBtn(String text,int color){Button b=new Button(this);b.setText(text);b.setAllCaps(false);b.setTextSize(17);b.setTextColor(Color.WHITE);b.setBackground(bg(color,10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(58),1);p.setMargins(dp(3),dp(4),dp(3),dp(4));b.setLayoutParams(p);return b;}
    private void setManualStatus(String pid,String st){setStatus(pid,st);prefs.edit().putString(key(pid,"status_source"),"MANUAL").apply();}

    private void addDetailedPoint(int num,JSONObject p){
        LinearLayout c=card();String pid=p.optString("id");TextView h=tv(num+". "+displayText(p.optString("label")),16,true);String cls=p.optString("source_class");if(cls.contains("VERIFY"))h.setTextColor(ORANGE);else if(cls.startsWith("OEM"))h.setTextColor(GREEN);else h.setTextColor(BLUE);c.addView(h);
        c.addView(tv("위치 · "+displayText(p.optString("where")),13,true));c.addView(tv("연결 · "+displayText(p.optString("connect")),12,false));c.addView(tv("상태 · "+displayText(p.optString("condition")),12,false));
        if(!p.optString("expected").isEmpty())c.addView(tv("기준 · "+displayText(p.optString("expected")),12,true));
        String st=pref(pid,"status");c.addView(tv("판정 · "+statusKo(st)+(pref(pid,"value").isEmpty()?"":" · 측정 "+pref(pid,"value")),12,true));
        Button rec=btn("기록 / 판정 수정",false);rec.setOnClickListener(v->showPointRecordDialog(p,p.optJSONObject("auto_eval")!=null));c.addView(rec);body.addView(c);
    }

    private void showPointRecordDialog(JSONObject p,boolean focusValue){
        String pid=p.optString("id"); final Dialog d=new Dialog(this);LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(14),dp(16),dp(14));root.setBackgroundColor(Color.WHITE);
        root.addView(tv(displayText(p.optString("label")),18,true));root.addView(tv("위치 · "+displayText(p.optString("where")),12,false));
        TextView st=tv("",12,true);final EditText value;
        if(p.optJSONObject("auto_eval")!=null)value=addAutoEval(root,p,pid,st);else{value=new EditText(this);value.setHint("측정값 · 단위 포함");value.setText(pref(pid,"value"));value.setTextSize(14);value.setBackground(bg(Color.rgb(246,248,250),8));value.setPadding(dp(10),dp(10),dp(10),dp(10));root.addView(value);value.addTextChangedListener(saveWatcher(pid,"value"));}
        EditText note=new EditText(this);note.setHint("현장 메모 · 재현조건/좌우비교/흔들림 반응");note.setText(pref(pid,"note"));note.setMinLines(2);note.setBackground(bg(Color.rgb(246,248,250),8));note.setPadding(dp(10),dp(10),dp(10),dp(10));root.addView(note);note.addTextChangedListener(saveWatcher(pid,"note"));
        LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);Button ok=miniBtn("정상");Button bad=miniBtn("이상");Button hold=miniBtn("보류");Button clear=miniBtn("초기화");
        ok.setOnClickListener(v->{setManualStatus(pid,"PASS");refreshStatusText(st,p);});bad.setOnClickListener(v->{setManualStatus(pid,"FAIL");refreshStatusText(st,p);});hold.setOnClickListener(v->{setManualStatus(pid,"HOLD");refreshStatusText(st,p);});clear.setOnClickListener(v->{prefs.edit().remove(key(pid,"status")).remove(key(pid,"value")).remove(key(pid,"note")).remove(key(pid,"status_source")).remove(key(pid,"auto_profile")).remove(key(pid,"auto_unit")).remove(key(pid,"auto_base_value")).apply();value.setText("");note.setText("");refreshStatusText(st,p);});
        row.addView(ok);row.addView(bad);row.addView(hold);row.addView(clear);root.addView(row);refreshStatusText(st,p);root.addView(st);
        Button close=btn("저장하고 닫기",true);close.setOnClickListener(v->{d.dismiss();recreate();});root.addView(close);
        ScrollView sv=new ScrollView(this);sv.addView(root);d.setContentView(sv);d.setOnDismissListener(x->updateSessionSummary());d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-2);if(focusValue)value.requestFocus();
    }

    private void openLocationOrCircuit(){
        String sys=group.optString("system");
        if(("전장".equals(sys)||"에어컨".equals(sys))&&!sourceGraphId.isEmpty()){
            android.content.Intent it=new android.content.Intent(this,ElectricalDiagnosticActivity.class);it.putExtra("graph_id",sourceGraphId);startActivity(it);return;
        }
        if("엔진".equals(sys)){
            android.content.Intent it=new android.content.Intent(this,EngineSensorMapActivity.class);JSONArray a=group.optJSONArray("sensor_focus_ids");StringBuilder s=new StringBuilder();if(a!=null)for(int k=0;k<a.length();k++){if(k>0)s.append(",");s.append(a.optString(k));}it.putExtra("focus_ids",s.toString());startActivity(it);return;
        }
        android.content.Intent it=new android.content.Intent(this,FieldLocationMapActivity.class);JSONArray a=group.optJSONArray("focus_ids");StringBuilder s=new StringBuilder();if(a!=null)for(int k=0;k<a.length();k++){if(k>0)s.append(",");s.append(a.optString(k));}it.putExtra("focus_ids",s.toString());startActivity(it);
    }

    private boolean shouldShowPointMap(){String sys=group.optString("system");return !("전장".equals(sys)||"에어컨".equals(sys));}

    private String progressText(){int total=0,done=0,fail=0;JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);if(p==null||!visiblePointIds.contains(p.optString("id")))continue;total++;String st=pref(p.optString("id"),"status");if(!st.isEmpty())done++;if("FAIL".equals(st))fail++;}return done+"/"+total+" 판정"+(fail>0?" · 이상 "+fail:"");}

    private void showWorkMenu(){
        final String[] items={"현재 기록 요약 복사","이상 항목만 보기","새 작업 시작","현재 화면 기록 초기화"};
        new AlertDialog.Builder(this).setTitle("작업기록 · "+sessionLabel).setItems(items,(d,w)->{if(w==0)copySessionSummary();else if(w==1)showAbnormalSummary();else if(w==2)newSessionDialog();else confirmResetSession();}).setNegativeButton("닫기",null).show();
    }

    private void showEvidenceDialog(){
        StringBuilder sb=new StringBuilder();JSONArray a=group.optJSONArray("conditions");if(a!=null&&a.length()>0){sb.append("[시험 전 조건]\n");for(int i=0;i<a.length();i++)sb.append("• ").append(displayText(a.optString(i))).append("\n");}
        a=group.optJSONArray("tools");if(a!=null&&a.length()>0){sb.append("\n[공구]\n");for(int i=0;i<a.length();i++)sb.append("• ").append(displayText(a.optString(i))).append("\n");}
        a=group.optJSONArray("limitations");if(a!=null&&a.length()>0){sb.append("\n[OEM 미확정 / 과잉판정 금지]\n");for(int i=0;i<a.length();i++)sb.append("• ").append(displayText(a.optString(i))).append("\n");}
        a=group.optJSONArray("source_refs");if(a!=null&&a.length()>0){sb.append("\n[근거]\n");for(int i=0;i<a.length();i++)sb.append("• ").append(a.optString(i)).append("\n");}
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("시험조건 / 근거").setMessage(sb.length()==0?"추가 표시 정보 없음":sb.toString()).setPositiveButton("닫기",null).setNeutralButton("OEM 이미지",null).create();dialog.setOnShowListener(x->{Button b=dialog.getButton(AlertDialog.BUTTON_NEUTRAL);b.setOnClickListener(v->showFirstOemImage());});dialog.show();
    }
    private void showFirstOemImage(){JSONArray imgs=group.optJSONArray("oem_images");if(imgs==null||imgs.length()==0){Toast.makeText(this,"연결된 OEM 이미지가 없습니다.",Toast.LENGTH_SHORT).show();return;}if(imgs.length()==1){showAsset(imgs.optString(0));return;}String[] names=new String[imgs.length()];for(int i=0;i<imgs.length();i++){String a=imgs.optString(i);names[i]=a.substring(a.lastIndexOf('/')+1);}new AlertDialog.Builder(this).setTitle("OEM 근거 선택").setItems(names,(d,w)->showAsset(imgs.optString(w))).show();}

    private String displayText(String s){if(s==null)return "";String x=s;String[][] r={{"License lamp","번호판등"},{"license lamp","번호판등"},{"License GND drop","번호판등 접지 전압강하"},{"rear/tail lamp","후미등/미등"},{"rear lamp","후미등"},{"rear lamps","후미등"},{"tail lamp","미등"},{"loaded voltage drop","부하 전압강하"},{"loaded voltage","부하전압"},{"common rear-light output comparison","공통 후미등 출력 비교"},{"common feed","공통전원"},{"branch/harness","분기배선/하네스"},{"light switch","라이트 스위치"},{"relay","릴레이"},{"LIGHT ON","라이트 ON"},{"battery -POST","배터리 -포스트"},{"socket","소켓"},{"connector","커넥터"},{"ground","접지"},{"GND","접지(GND)"}};for(String[] q:r)x=x.replace(q[0],q[1]);return x;}

    private EditText addAutoEval(LinearLayout parent,JSONObject p,String pid,TextView statusText){
        JSONObject ae=p.optJSONObject("auto_eval");LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(10),dp(9),dp(10),dp(9));panel.setBackground(bg(Color.rgb(235,247,239),9));LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(-1,-2);pp.setMargins(0,dp(4),0,dp(5));panel.setLayoutParams(pp);panel.addView(tv("OEM exact 자동판정 · 구조화된 허용범위만",13,true));panel.addView(tv("시험조건/모델과 단위를 맞춘 뒤 숫자만 입력합니다. 자동판정은 이 측정점의 정상/이상만 판정하며 원인 확정은 다음 격리분기를 계속 따라갑니다.",11,false));
        JSONArray profiles=ae.optJSONArray("profiles");JSONArray units=ae.optJSONArray("units");
        final Spinner profileSp=new Spinner(this);final Spinner unitSp=new Spinner(this);final TextView result=tv("자동판정 대기",12,true);
        boolean multiProfile=profiles!=null&&profiles.length()>1;boolean multiUnit=units!=null&&units.length()>1;
        ArrayList<String> profileLabels=new ArrayList<>();if(multiProfile)profileLabels.add("시험조건/모델 선택");if(profiles!=null)for(int i=0;i<profiles.length();i++)profileLabels.add(profiles.optJSONObject(i).optString("label"));
        if(multiProfile){profileSp.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,profileLabels));String saved=pref(pid,"auto_profile");if(saved.isEmpty()&&"vehicle_model".equals(ae.optString("profile_selector")))saved=getSharedPreferences("parts_vehicle_profile",MODE_PRIVATE).getString("model","");int sel=0;for(int i=0;i<profiles.length();i++)if(saved.equals(profiles.optJSONObject(i).optString("id")))sel=i+1;profileSp.setSelection(sel);panel.addView(tv("시험조건 / 현재차량 모델",11,true));panel.addView(profileSp);}
        else if(profiles!=null&&profiles.length()==1)panel.addView(tv("시험조건 · "+profiles.optJSONObject(0).optString("label"),11,true));
        ArrayList<String> unitLabels=new ArrayList<>();if(units!=null)for(int i=0;i<units.length();i++)unitLabels.add(units.optJSONObject(i).optString("unit"));
        if(multiUnit){unitSp.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,unitLabels));String su=pref(pid,"auto_unit");int us=0;for(int i=0;i<unitLabels.size();i++)if(su.equals(unitLabels.get(i)))us=i;unitSp.setSelection(us);panel.addView(tv("입력 단위",11,true));panel.addView(unitSp);}else if(!unitLabels.isEmpty())panel.addView(tv("입력 단위 · "+unitLabels.get(0),11,true));
        final EditText value=new EditText(this);value.setSingleLine(true);value.setInputType(android.text.InputType.TYPE_CLASS_NUMBER|android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL|android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);value.setHint("숫자만 입력");value.setText(pref(pid,"value"));value.setTextSize(14);value.setPadding(dp(10),dp(8),dp(10),dp(8));value.setBackground(bg(Color.WHITE,8));panel.addView(value,new LinearLayout.LayoutParams(-1,-2));panel.addView(result);parent.addView(panel);
        final Runnable eval=()->evaluateAutoPoint(p,pid,value,profileSp,unitSp,result,statusText,multiProfile,multiUnit);
        value.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int a){}public void onTextChanged(CharSequence s,int st,int before,int count){prefs.edit().putString(key(pid,"value"),s.toString()).apply();eval.run();updateSessionSummary();}public void afterTextChanged(Editable e){}});
        if(multiProfile)profileSp.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onNothingSelected(android.widget.AdapterView<?> p){}public void onItemSelected(android.widget.AdapterView<?> a,View v,int pos,long id){if(pos>0)prefs.edit().putString(key(pid,"auto_profile"),profiles.optJSONObject(pos-1).optString("id")).apply();else prefs.edit().remove(key(pid,"auto_profile")).apply();eval.run();}});
        if(multiUnit)unitSp.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onNothingSelected(android.widget.AdapterView<?> p){}public void onItemSelected(android.widget.AdapterView<?> a,View v,int pos,long id){prefs.edit().putString(key(pid,"auto_unit"),units.optJSONObject(pos).optString("unit")).apply();eval.run();}});
        eval.run();return value;
    }

    private void evaluateAutoPoint(JSONObject p,String pid,EditText value,Spinner profileSp,Spinner unitSp,TextView result,TextView statusText,boolean multiProfile,boolean multiUnit){
        try{
            JSONObject ae=p.optJSONObject("auto_eval");if(ae==null)return;String raw=value.getText().toString().trim();if(raw.isEmpty()){result.setText("자동판정 대기 · 측정값을 입력하세요.");result.setTextColor(Color.GRAY);return;}
            JSONArray profiles=ae.getJSONArray("profiles");int pi=multiProfile?profileSp.getSelectedItemPosition()-1:0;if(pi<0||pi>=profiles.length()){result.setText("자동판정 대기 · 시험조건/모델을 먼저 선택하세요.");result.setTextColor(ORANGE);return;}JSONObject pr=profiles.getJSONObject(pi);
            double measured=Double.parseDouble(raw.replace(",","."));JSONArray units=ae.getJSONArray("units");int ui=multiUnit?unitSp.getSelectedItemPosition():0;if(ui<0||ui>=units.length())ui=0;JSONObject u=units.getJSONObject(ui);double base=measured*u.optDouble("to_base",1.0);String kind=ae.optString("kind");boolean pass;String spec;
            if("range".equals(kind)){double mn=pr.getDouble("min"),mx=pr.getDouble("max");pass=base>=mn&&base<=mx;spec=fmt(mn)+"~"+fmt(mx)+" "+ae.optString("base_unit");}
            else if("max".equals(kind)){double mx=pr.getDouble("max");pass=base<=mx;spec="≤"+fmt(mx)+" "+ae.optString("base_unit");}
            else if("min".equals(kind)){double mn=pr.getDouble("min");pass=base>=mn;spec="≥"+fmt(mn)+" "+ae.optString("base_unit");}
            else{result.setText("자동판정 보류 · 지원하지 않는 판정형식");result.setTextColor(ORANGE);return;}
            prefs.edit().putString(key(pid,"auto_profile"),pr.optString("id")).putString(key(pid,"auto_unit"),u.optString("unit")).putString(key(pid,"auto_base_value"),String.valueOf(base)).putString(key(pid,"status_source"),"OEM_AUTO").apply();setStatus(pid,pass?"PASS":"FAIL");
            String txt="자동판정 · "+(pass?"정상":"이상")+" · "+pr.optString("label")+" · OEM "+spec;if(!pass&&p.optString("decision").length()>0)txt+="\n→ 다음 분기: "+p.optString("decision");result.setText(txt);result.setTextColor(pass?GREEN:Color.rgb(180,45,45));refreshStatusText(statusText,p);updateSessionSummary();
        }catch(NumberFormatException n){result.setText("자동판정 대기 · 숫자만 입력하세요.");result.setTextColor(ORANGE);}catch(Exception e){result.setText("자동판정 보류 · 조건/데이터 확인 필요");result.setTextColor(ORANGE);}
    }
    private String fmt(double v){if(Math.abs(v-Math.rint(v))<0.000001)return String.valueOf((long)Math.rint(v));String s=String.format(java.util.Locale.US,"%.3f",v);while(s.endsWith("0"))s=s.substring(0,s.length()-1);if(s.endsWith("."))s=s.substring(0,s.length()-1);return s;}
    private void ensureSession(){activeSession=sessionPref.getString("active_id","");sessionLabel=sessionPref.getString("active_label","");if(activeSession.isEmpty()){activeSession="S"+System.currentTimeMillis();sessionLabel="현장작업 "+new java.text.SimpleDateFormat("MM-dd HH:mm",java.util.Locale.KOREA).format(new java.util.Date());sessionPref.edit().putString("active_id",activeSession).putString("active_label",sessionLabel).apply();}}
    private String key(String pid,String field){return "m."+activeSession+"."+groupId+"."+pid+"."+field;}
    private String pref(String pid,String field){return prefs==null?"":prefs.getString(key(pid,field),"");}
    private void setStatus(String pid,String status){prefs.edit().putString(key(pid,"status"),status).putLong(key(pid,"time"),System.currentTimeMillis()).apply();}
    private TextWatcher saveWatcher(final String pid,final String field){return new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int a){}public void onTextChanged(CharSequence s,int st,int before,int count){prefs.edit().putString(key(pid,field),s.toString()).apply();updateSessionSummary();}public void afterTextChanged(Editable e){}};}
    private Button miniBtn(String s){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(11);b.setPadding(dp(2),0,dp(2),0);b.setBackground(bg(Color.rgb(231,236,240),8));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(44),1);p.setMargins(dp(2),0,dp(2),0);b.setLayoutParams(p);return b;}
    private void refreshStatusText(TextView v,JSONObject p){String pid=p.optString("id"),st=pref(pid,"status"),src=pref(pid,"status_source");String tag="OEM_AUTO".equals(src)?" [OEM 자동판정]":"";if("PASS".equals(st)){v.setText("● 정상으로 기록"+tag+" · 다음 포인트로 진행");v.setTextColor(GREEN);}else if("FAIL".equals(st)){v.setText("● 이상으로 기록"+tag+" · 다음 분기: "+p.optString("decision","해당 구간을 격리/확정"));v.setTextColor(Color.rgb(180,45,45));}else if("HOLD".equals(st)){v.setText("● 보류 · 재현조건/OEM 기준 확인 후 판정");v.setTextColor(ORANGE);}else{v.setText("○ 미판정");v.setTextColor(Color.GRAY);}}
    private void addSessionCard(){
        LinearLayout c=card();c.addView(tv("현장 측정 워크시트",16,true));c.addView(tv("작업세션 · "+sessionLabel,13,true));c.addView(tv("측정값을 직접 기록합니다. 자동판정은 OEM exact 허용범위가 구조화된 항목에만 작동하며, OEM 근거가 없는 숫자 임계값은 생성하지 않습니다.",11,false));sessionSummary=tv("",13,true);c.addView(sessionSummary);updateSessionSummary();
        Button bad=btn("이상 포인트의 다음 분기만 모아보기",true);bad.setOnClickListener(v->showAbnormalSummary());c.addView(bad);
        Button copy=btn("현재 측정 기록 요약 복사",false);copy.setOnClickListener(v->copySessionSummary());c.addView(copy);
        Button fresh=btn("새 작업 시작 · 다른 차량/현장",false);fresh.setOnClickListener(v->newSessionDialog());c.addView(fresh);
        Button reset=btn("현재 화면 기록 초기화",false);reset.setOnClickListener(v->confirmResetSession());c.addView(reset);body.addView(c);
    }
    private void updateSessionSummary(){if(group==null)return;int total=0,pass=0,fail=0,hold=0,valued=0;try{JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject p=pts.getJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;total++;String s=pref(id,"status");if("PASS".equals(s))pass++;else if("FAIL".equals(s))fail++;else if("HOLD".equals(s))hold++;if(!pref(id,"value").trim().isEmpty())valued++;}}catch(Exception ignore){}if(sessionSummary!=null)sessionSummary.setText("표시 "+total+" · 측정값 "+valued+" · 정상 "+pass+" · 이상 "+fail+" · 보류 "+hold+" · 미판정 "+Math.max(0,total-pass-fail-hold));updateAdaptiveBranchSummary();}
    private void addAdaptiveBranchCard(){
        JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return;
        LinearLayout c=card();c.addView(tv("측정 조합 판정 · 다음 한 점",16,true));c.addView(tv(ab.optString("rule"),11,false));branchSummary=tv("",13,true);branchSummary.setPadding(dp(6),dp(8),dp(6),dp(8));branchSummary.setBackground(bg(Color.rgb(238,244,249),8));c.addView(branchSummary);
        Button b=btn("현재 조합의 다음 점검 자세히",true);b.setOnClickListener(v->showAdaptiveBranchDialog());c.addView(b);String n=ab.optString("note");if(!n.isEmpty())c.addView(tv("주의 · "+n,11,false));body.addView(c);updateAdaptiveBranchSummary();
    }
    private boolean ruleMatches(JSONObject r){try{JSONObject w=r.getJSONObject("when");Iterator<String> it=w.keys();while(it.hasNext()){String id=it.next();if(!w.optString(id).equals(pref(id,"status")))return false;}return w.length()>0;}catch(Exception e){return false;}}
    private JSONObject matchedAdaptiveRule(){JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return null;JSONArray a=ab.optJSONArray("rules");if(a==null)return null;for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&ruleMatches(r))return r;}return null;}
    private JSONObject pointById(String id){JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);if(p!=null&&id.equals(p.optString("id")))return p;}return null;}
    private String nextPointText(JSONObject r){StringBuilder sb=new StringBuilder();JSONArray a=r==null?null:r.optJSONArray("next_points");if(a!=null&&a.length()>0){for(int i=0;i<a.length();i++){String id=a.optString(i);JSONObject p=pointById(id);if(i>0)sb.append("\n");sb.append("[").append(id).append("] ").append(p==null?id:p.optString("label"));}}else{JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;if(pref(id,"status").isEmpty()){sb.append("[").append(id).append("] ").append(p.optString("label"));break;}}}return sb.toString();}
    private String adaptiveSummaryText(){JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return "";JSONObject r=matchedAdaptiveRule();if(r==null){String next=nextPointText(null);return "아직 조합판정 전"+(next.isEmpty()?" · 현재 표시 포인트 판정을 더 입력하세요.":"\n→ 다음 측정: "+next);}StringBuilder sb=new StringBuilder();sb.append("현재 분기 · ").append(r.optString("title"));String level=r.optString("level");if(!level.isEmpty())sb.append("  [").append(level).append("]");String a=r.optString("assessment");if(!a.isEmpty())sb.append("\n").append(a);JSONArray ex=r.optJSONArray("excludes");if(ex!=null&&ex.length()>0){sb.append("\n배제/우선순위 하향: ");for(int i=0;i<ex.length();i++){if(i>0)sb.append(" / ");sb.append(ex.optString(i));}}String np=nextPointText(r);if(!np.isEmpty())sb.append("\n→ 다음 측정: ").append(np);String c=r.optString("caution");if(!c.isEmpty())sb.append("\n주의: ").append(c);return sb.toString();}
    private void updateAdaptiveBranchSummary(){if(branchSummary==null)return;String s=adaptiveSummaryText();branchSummary.setText(s);JSONObject r=matchedAdaptiveRule();if(r==null)branchSummary.setTextColor(Color.rgb(70,80,90));else{String lv=r.optString("level");branchSummary.setTextColor("ISOLATED".equals(lv)?Color.rgb(170,55,45):("UPSTREAM".equals(lv)?ORANGE:NAVY));}}
    private void showAdaptiveBranchDialog(){new AlertDialog.Builder(this).setTitle("현재 측정 조합 판정").setMessage(adaptiveSummaryText()+"\n\n※ 이 기능은 측정구간을 좁히는 보조판정입니다. 단일 측정으로 부품교환을 확정하지 않습니다.").setPositiveButton("확인",null).show();}

    private String buildSessionText(boolean onlyFail){StringBuilder sb=new StringBuilder();sb.append("작업세션: ").append(sessionLabel).append("\n").append(group.optString("title")).append("\n");String as=adaptiveSummaryText();if(!as.isEmpty())sb.append("\n[조합판정] ").append(as).append("\n");try{JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject p=pts.getJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;String st=pref(id,"status");if(onlyFail&&!"FAIL".equals(st))continue;if(st.isEmpty()&&pref(id,"value").trim().isEmpty()&&pref(id,"note").trim().isEmpty())continue;sb.append("\n[").append(id).append("] ").append(p.optString("label")).append(" · ").append(statusKo(st));if("OEM_AUTO".equals(pref(id,"status_source")))sb.append("[OEM자동]");String val=pref(id,"value").trim();if(!val.isEmpty()){sb.append(" · 측정 ").append(val);String au=pref(id,"auto_unit");if(!au.isEmpty())sb.append(" ").append(au);String ap=pref(id,"auto_profile");if(!ap.isEmpty())sb.append(" · 조건 ").append(ap);}String n=pref(id,"note").trim();if(!n.isEmpty())sb.append(" · 메모 ").append(n);if("FAIL".equals(st)&&p.optString("decision").length()>0)sb.append("\n  → 다음 분기: ").append(p.optString("decision"));} }catch(Exception ignore){}return sb.toString();}
    private String statusKo(String s){if("PASS".equals(s))return "정상";if("FAIL".equals(s))return "이상";if("HOLD".equals(s))return "보류";return "미판정";}
    private void showAbnormalSummary(){boolean any=false;try{JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){String id=pts.getJSONObject(i).optString("id");if(visiblePointIds.contains(id)&&"FAIL".equals(pref(id,"status"))){any=true;break;}}}catch(Exception ignore){}String t=any?buildSessionText(true):"현재 이상으로 기록된 포인트가 없습니다.";new AlertDialog.Builder(this).setTitle("이상 포인트 · 다음 분기").setMessage(t).setPositiveButton("확인",null).show();}
    private void copySessionSummary(){String t=buildSessionText(false);android.content.ClipboardManager cm=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);cm.setPrimaryClip(android.content.ClipData.newPlainText("field-measurements",t));Toast.makeText(this,"측정 기록을 복사했습니다.",Toast.LENGTH_SHORT).show();}
    private void newSessionDialog(){EditText e=new EditText(this);e.setHint("예: D25S-7 3호기 / 고객사A / 현장1");e.setSingleLine(true);new AlertDialog.Builder(this).setTitle("새 작업 시작").setMessage("측정기록을 다른 작업과 섞지 않도록 새 세션을 만듭니다. 차대번호 입력은 필수가 아닙니다.").setView(e).setNegativeButton("취소",null).setPositiveButton("시작",(d,w)->{String label=e.getText().toString().trim();activeSession="S"+System.currentTimeMillis();sessionLabel=label.isEmpty()?"현장작업 "+new java.text.SimpleDateFormat("MM-dd HH:mm",java.util.Locale.KOREA).format(new java.util.Date()):label;sessionPref.edit().putString("active_id",activeSession).putString("active_label",sessionLabel).apply();recreate();}).show();}
    private void confirmResetSession(){new AlertDialog.Builder(this).setTitle("현재 화면 기록 초기화").setMessage("현재 작업세션에서 이 화면의 측정값/판정만 지웁니다.").setNegativeButton("취소",null).setPositiveButton("초기화",(d,w)->{android.content.SharedPreferences.Editor e=prefs.edit();for(String id:visiblePointIds){e.remove(key(id,"status")).remove(key(id,"value")).remove(key(id,"note")).remove(key(id,"time")).remove(key(id,"status_source")).remove(key(id,"auto_profile")).remove(key(id,"auto_unit")).remove(key(id,"auto_base_value"));}e.apply();recreate();}).show();}

    private String sourceLabel(String c){try{return data.getJSONObject("source_classes").optString(c,c);}catch(Exception e){return c;}}

    private Bitmap drawPointMap()throws Exception{
        int w=1600,h=850;Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);c.drawColor(Color.WHITE);Paint p=new Paint(1);p.setColor(NAVY);p.setTextSize(40);p.setTypeface(Typeface.DEFAULT_BOLD);c.drawText(group.optString("title"),45,58,p);
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(10);p.setColor(Color.rgb(100,115,125));
        if("TM_PRESSURE_TAPS".equals(groupId)){c.drawRoundRect(new RectF(250,185,1320,700),80,80,p);c.drawRect(1020,280,1400,620,p);}
        else if("BRAKE_BLEED_ISOLATION".equals(groupId)){c.drawRect(480,190,950,350,p);c.drawLine(715,350,715,500,p);c.drawLine(715,500,340,650,p);c.drawLine(715,500,1100,650,p);c.drawCircle(310,665,110,p);c.drawCircle(1130,665,110,p);}
        else if("HYD_MAIN_RELIEF".equals(groupId)||"STEERING_PRIORITY".equals(groupId)){c.drawRoundRect(new RectF(190,230,600,620),55,55,p);c.drawLine(600,420,870,420,p);c.drawRoundRect(new RectF(870,260,1250,590),50,50,p);c.drawLine(1250,420,1420,420,p);}
        else if("START_VDROP".equals(groupId)){c.drawRect(100,340,310,570,p);c.drawLine(310,455,610,455,p);c.drawRoundRect(new RectF(610,330,900,580),55,55,p);c.drawLine(900,455,1180,455,p);c.drawRoundRect(new RectF(1180,300,1500,610),65,65,p);}
        else if("OSS_HEALTH".equals(groupId)){c.drawRoundRect(new RectF(580,230,1030,650),70,70,p);c.drawLine(230,320,580,320,p);c.drawLine(230,460,580,460,p);c.drawLine(1030,330,1390,330,p);c.drawLine(1030,520,1390,520,p);}
        else if("AC_COND_FAN".equals(groupId)){c.drawCircle(800,440,210,p);for(int a=0;a<6;a++){double q=a*Math.PI/3;c.drawLine(800,440,(float)(800+190*Math.cos(q)),(float)(440+190*Math.sin(q)),p);}c.drawLine(300,440,590,440,p);c.drawLine(1010,440,1320,440,p);}
        else if("AC_PRESSURE".equals(groupId)){c.drawRoundRect(new RectF(250,300,650,610),60,60,p);c.drawLine(650,455,950,455,p);c.drawRoundRect(new RectF(950,260,1350,650),60,60,p);c.drawLine(800,220,800,690,p);}
        else if("DRIVE_AXLE_MECH".equals(groupId)){c.drawCircle(330,575,150,p);c.drawCircle(1270,575,150,p);c.drawRoundRect(new RectF(610,300,990,650),70,70,p);c.drawLine(480,575,610,500,p);c.drawLine(990,500,1120,575,p);c.drawLine(800,300,800,180,p);}
        else if("WORK_EQUIPMENT_CONTROL".equals(groupId)){c.drawRoundRect(new RectF(250,220,1350,650),70,70,p);for(int i=0;i<5;i++)c.drawLine(450+i*175,250,450+i*175,620,p);c.drawLine(100,435,250,435,p);c.drawLine(1350,435,1510,435,p);}
        else if("MAST_CYLINDER_DIAG".equals(groupId)){c.drawLine(430,150,430,720,p);c.drawLine(500,150,500,720,p);c.drawLine(1100,150,1100,720,p);c.drawLine(1170,150,1170,720,p);c.drawRoundRect(new RectF(675,250,925,690),45,45,p);c.drawLine(465,280,675,340,p);c.drawLine(1135,280,925,340,p);}
        else if("PARK_BRAKE_ADJUST_TEST".equals(groupId)){c.drawRoundRect(new RectF(190,250,510,620),55,55,p);c.drawLine(510,435,810,435,p);c.drawRoundRect(new RectF(810,300,1110,570),45,45,p);c.drawLine(1110,435,1380,435,p);c.drawCircle(1410,435,95,p);}
        else if("엔진".equals(group.optString("system"))){
            c.drawRoundRect(new RectF(250,220,1220,680),90,90,p);
            c.drawRoundRect(new RectF(1150,300,1450,590),55,55,p);
            c.drawLine(180,340,250,340,p);c.drawLine(180,540,250,540,p);
            c.drawLine(1220,430,1450,430,p);
            c.drawRect(500,150,950,260,p);
        }

        p.setStyle(Paint.Style.FILL);JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject x=pts.getJSONObject(i);if(!pointFilter.isEmpty()&&!pointFilter.contains(x.optString("id")))continue;float px=(float)(x.optDouble("x",.5)*w),py=(float)(x.optDouble("y",.5)*h);String sc=x.optString("source_class");p.setColor(sc.contains("VERIFY")?ORANGE:(sc.startsWith("OEM")?GREEN:BLUE));c.drawCircle(px,py,23,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);c.drawCircle(px,py,34,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(25,30,35));p.setTextSize(23);p.setTypeface(Typeface.DEFAULT_BOLD);String label=x.optString("id")+" "+shortLabel(x.optString("label"));drawLabel(c,p,label,px+42,py-6);}
        p.setColor(Color.DKGRAY);p.setTextSize(18);p.setTypeface(Typeface.DEFAULT);c.drawText("※ 포인트를 찾는 재작성 그림. 정확 피팅/커넥터 형상은 OEM 근거에서 최종 확인.",45,820,p);return b;
    }
    private String shortLabel(String s){int k=s.indexOf('·');if(k>=0&&k+1<s.length())s=s.substring(k+1).trim();return s.length()>20?s.substring(0,20)+"…":s;}
    private void drawLabel(Canvas c,Paint p,String s,float x,float y){String[] a=wrap(s,18);for(int i=0;i<a.length;i++)c.drawText(a[i],x,y+i*28,p);}private String[] wrap(String s,int n){if(s.length()<=n)return new String[]{s};ArrayList<String>a=new ArrayList<>();for(int i=0;i<s.length();i+=n)a.add(s.substring(i,Math.min(s.length(),i+n)));return a.toArray(new String[0]);}
    private void showAsset(String a){try{InputStream is=getAssets().open(a);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm!=null)showBitmap(bm);}catch(Exception e){Toast.makeText(this,"OEM 근거 이미지를 열 수 없습니다: "+a,Toast.LENGTH_SHORT).show();}}
    private void showBitmap(Bitmap bm){ZoomImageDialog.show(this,bm);}
    private void fatal(String s){TextView t=new TextView(this);t.setText(s);t.setTextSize(16);t.setPadding(30,30,30,30);setContentView(t);}
}
