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
        String cid=getIntent().getStringExtra("cause_id");
        if((id==null||id.isEmpty())&&cid!=null&&!cid.isEmpty()){
            JSONObject cm=data.optJSONObject("cause_map");
            JSONObject m=cm==null?null:cm.optJSONObject(cid);
            if(m!=null){id=m.optString("group");JSONArray a=m.optJSONArray("point_ids");if(a!=null)for(int i=0;i<a.length();i++)pointFilter.add(a.optString(i));}
        }
        if(id==null||id.isEmpty()){
            String gid=getIntent().getStringExtra("graph_id");
            if(gid!=null)id=data.getJSONObject("graph_map").optString(gid,"");
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
        base("측정포인트 · "+group.optString("system"));
        LinearLayout intro=card();intro.addView(tv(group.optString("title"),18,true));intro.addView(tv(group.optString("summary"),13,false));intro.addView(tv("판정 기준 · OEM exact / 현장 격리 / OEM VERIFY를 분리 표시",11,true));if(!pointFilter.isEmpty())intro.addView(tv("현재 원인 관련 포인트만 표시 · "+pointFilter.size()+"개",12,true));body.addView(intro);
        visiblePointIds.clear();JSONArray allPtsForSession=group.getJSONArray("points");for(int i=0;i<allPtsForSession.length();i++){JSONObject x=allPtsForSession.getJSONObject(i);if(pointFilter.isEmpty()||pointFilter.contains(x.optString("id")))visiblePointIds.add(x.optString("id"));}
        addSessionCard();
        addAdaptiveBranchCard();

        Button loc=btn("엔진".equals(group.optString("system"))?"◎ D24 센서/측정 위치 먼저 보기":"◎ 차량에서 이 점검 위치 먼저 보기",true);
        loc.setOnClickListener(v->{
            if("엔진".equals(group.optString("system"))){
                android.content.Intent it=new android.content.Intent(this,EngineSensorMapActivity.class);
                JSONArray a=group.optJSONArray("sensor_focus_ids");StringBuilder s=new StringBuilder();if(a!=null)for(int k=0;k<a.length();k++){if(k>0)s.append(",");s.append(a.optString(k));}
                it.putExtra("focus_ids",s.toString());startActivity(it);
            }else{
                android.content.Intent it=new android.content.Intent(this,FieldLocationMapActivity.class);JSONArray a=group.optJSONArray("focus_ids");StringBuilder s=new StringBuilder();if(a!=null)for(int k=0;k<a.length();k++){if(k>0)s.append(",");s.append(a.optString(k));}it.putExtra("focus_ids",s.toString());startActivity(it);
            }
        });body.addView(loc);

        Bitmap bm=drawPointMap();LinearLayout mc=card();mc.addView(tv("정비사용 재작성 포인트맵",16,true));mc.addView(tv(group.optString("diagram_note"),11,false));ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);iv.setOnClickListener(v->showBitmap(bm));mc.addView(iv,new LinearLayout.LayoutParams(-1,dp(360)));mc.addView(tv("● 녹색=OEM exact/기능확인  ● 파랑=현장 격리·비교  ● 주황=OEM 추가확인 필요",11,true));body.addView(mc);

        JSONArray cond=group.optJSONArray("conditions");if(cond!=null){LinearLayout c=card();c.addView(tv("시험 전 조건",16,true));for(int i=0;i<cond.length();i++)c.addView(tv("• "+cond.optString(i),13,false));body.addView(c);}
        JSONArray tools=group.optJSONArray("tools");if(tools!=null){LinearLayout c=card();c.addView(tv("공구",15,true));for(int i=0;i<tools.length();i++)c.addView(tv("• "+tools.optString(i),13,false));body.addView(c);}

        body.addView(tv("측정 순서 / 연결 위치",17,true));JSONArray pts=group.getJSONArray("points");int shown=0;for(int i=0;i<pts.length();i++){JSONObject x=pts.getJSONObject(i);if(!pointFilter.isEmpty()&&!pointFilter.contains(x.optString("id")))continue;addPoint(++shown,x);}
        JSONArray rules=group.optJSONArray("decision_rules");if(rules!=null){LinearLayout c=card();c.addView(tv("결과를 이렇게 가른다",16,true));for(int i=0;i<rules.length();i++)c.addView(tv("→ "+rules.optString(i),13,false));body.addView(c);}
        JSONArray lim=group.optJSONArray("limitations");if(lim!=null&&lim.length()>0){LinearLayout c=card();c.addView(tv("OEM 미확정 / 과잉판정 금지",15,true));for(int i=0;i<lim.length();i++)c.addView(tv("• "+lim.optString(i),12,false));body.addView(c);}
        JSONArray refs=group.optJSONArray("source_refs");if(refs!=null){LinearLayout c=card();c.addView(tv("근거",14,true));for(int i=0;i<refs.length();i++)c.addView(tv("• "+refs.optString(i),12,false));body.addView(c);}
        JSONArray imgs=group.optJSONArray("oem_images");if(imgs!=null&&imgs.length()>0){LinearLayout c=card();c.addView(tv("OEM 원본은 마지막 확인용",15,true));for(int i=0;i<imgs.length();i++){final String a=imgs.optString(i);Button b=btn("OEM 근거 보기 · "+a.substring(a.lastIndexOf('/')+1),false);b.setOnClickListener(v->showAsset(a));c.addView(b);}body.addView(c);}
    }

    private void addPoint(int num,JSONObject p){
        LinearLayout c=card();String cls=p.optString("source_class"),pid=p.optString("id");TextView h=tv(num+". "+p.optString("label"),16,true);if(cls.contains("VERIFY"))h.setTextColor(ORANGE);else if(cls.startsWith("OEM"))h.setTextColor(GREEN);else h.setTextColor(BLUE);c.addView(h);c.addView(tv("연결 위치 · "+p.optString("where"),14,true));c.addView(tv("무엇을 연결 · "+p.optString("connect"),13,false));c.addView(tv("시험 상태 · "+p.optString("condition"),13,false));if(p.optString("expected").length()>0)c.addView(tv("OEM/비교 기준 · "+p.optString("expected"),13,true));if(p.optString("decision").length()>0)c.addView(tv("결과 분기 · "+p.optString("decision"),13,false));if(p.optString("note").length()>0)c.addView(tv("주의 · "+p.optString("note"),11,false));c.addView(tv("근거등급 · "+sourceLabel(cls),11,true));
        c.addView(tv("현장 측정 기록",14,true));
        TextView st=tv("",12,true);
        final EditText value;
        if(p.optJSONObject("auto_eval")!=null)value=addAutoEval(c,p,pid,st);else{
            value=new EditText(this);value.setSingleLine(false);value.setMinLines(1);value.setHint("측정값 · 단위 포함 (예: 10.8 V / 195 bar / 파형 정상)");value.setText(pref(pid,"value"));value.setTextSize(13);value.setPadding(dp(10),dp(8),dp(10),dp(8));value.setBackground(bg(Color.rgb(246,248,250),8));c.addView(value,new LinearLayout.LayoutParams(-1,-2));value.addTextChangedListener(saveWatcher(pid,"value"));
        }
        EditText note=new EditText(this);note.setSingleLine(false);note.setMinLines(1);note.setHint("현장 메모 · 재현조건/좌우비교/흔들림 반응 등");note.setText(pref(pid,"note"));note.setTextSize(12);note.setPadding(dp(10),dp(8),dp(10),dp(8));note.setBackground(bg(Color.rgb(246,248,250),8));LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(-1,-2);np.setMargins(0,dp(6),0,0);c.addView(note,np);note.addTextChangedListener(saveWatcher(pid,"note"));
        refreshStatusText(st,p);
        LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setPadding(0,dp(5),0,0);
        Button ok=miniBtn(p.optJSONObject("auto_eval")!=null?"수동 정상":"정상");Button bad=miniBtn(p.optJSONObject("auto_eval")!=null?"수동 이상":"이상");Button hold=miniBtn("보류");Button clear=miniBtn("초기화");
        ok.setOnClickListener(v->{setStatus(pid,"PASS");prefs.edit().putString(key(pid,"status_source"),"MANUAL").apply();refreshStatusText(st,p);updateSessionSummary();});bad.setOnClickListener(v->{setStatus(pid,"FAIL");prefs.edit().putString(key(pid,"status_source"),"MANUAL").apply();refreshStatusText(st,p);updateSessionSummary();});hold.setOnClickListener(v->{setStatus(pid,"HOLD");prefs.edit().putString(key(pid,"status_source"),"MANUAL").apply();refreshStatusText(st,p);updateSessionSummary();});clear.setOnClickListener(v->{prefs.edit().remove(key(pid,"status")).remove(key(pid,"value")).remove(key(pid,"note")).remove(key(pid,"status_source")).remove(key(pid,"auto_profile")).remove(key(pid,"auto_unit")).remove(key(pid,"auto_base_value")).apply();value.setText("");note.setText("");refreshStatusText(st,p);updateSessionSummary();});
        row.addView(ok,new LinearLayout.LayoutParams(0,dp(44),1));row.addView(bad,new LinearLayout.LayoutParams(0,dp(44),1));row.addView(hold,new LinearLayout.LayoutParams(0,dp(44),1));row.addView(clear,new LinearLayout.LayoutParams(0,dp(44),1));c.addView(row);c.addView(st);body.addView(c);
    }

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
        else if("전장".equals(group.optString("system"))||"에어컨".equals(group.optString("system"))){
            // Generic technician signal-flow backdrop for circuit-specific probe groups.
            // Exact connector geometry remains in the OEM evidence; this view answers where to probe next.
            c.drawRoundRect(new RectF(90,285,340,575),42,42,p);
            c.drawLine(340,430,520,430,p);
            c.drawRoundRect(new RectF(520,250,820,610),50,50,p);
            c.drawLine(820,430,1010,430,p);
            c.drawRoundRect(new RectF(1010,250,1320,610),50,50,p);
            c.drawLine(1320,430,1490,430,p);
            c.drawLine(1165,610,1165,720,p);
            p.setStyle(Paint.Style.FILL);p.setTextSize(27);p.setTypeface(Typeface.DEFAULT_BOLD);p.setColor(Color.rgb(75,90,100));
            c.drawText("SOURCE",145,445,p);c.drawText("CONTROL / HARNESS",545,445,p);c.drawText("LOAD / SIGNAL",1040,445,p);c.drawText("GND",1125,755,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(10);p.setColor(Color.rgb(100,115,125));
        }
        p.setStyle(Paint.Style.FILL);JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject x=pts.getJSONObject(i);if(!pointFilter.isEmpty()&&!pointFilter.contains(x.optString("id")))continue;float px=(float)(x.optDouble("x",.5)*w),py=(float)(x.optDouble("y",.5)*h);String sc=x.optString("source_class");p.setColor(sc.contains("VERIFY")?ORANGE:(sc.startsWith("OEM")?GREEN:BLUE));c.drawCircle(px,py,23,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);c.drawCircle(px,py,34,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(25,30,35));p.setTextSize(23);p.setTypeface(Typeface.DEFAULT_BOLD);String label=x.optString("id")+" "+shortLabel(x.optString("label"));drawLabel(c,p,label,px+42,py-6);}
        p.setColor(Color.DKGRAY);p.setTextSize(18);p.setTypeface(Typeface.DEFAULT);c.drawText("※ 포인트를 찾는 재작성 그림. 정확 피팅/커넥터 형상은 OEM 근거에서 최종 확인.",45,820,p);return b;
    }
    private String shortLabel(String s){int k=s.indexOf('·');if(k>=0&&k+1<s.length())s=s.substring(k+1).trim();return s.length()>20?s.substring(0,20)+"…":s;}
    private void drawLabel(Canvas c,Paint p,String s,float x,float y){String[] a=wrap(s,18);for(int i=0;i<a.length;i++)c.drawText(a[i],x,y+i*28,p);}private String[] wrap(String s,int n){if(s.length()<=n)return new String[]{s};ArrayList<String>a=new ArrayList<>();for(int i=0;i<s.length();i+=n)a.add(s.substring(i,Math.min(s.length(),i+n)));return a.toArray(new String[0]);}
    private void showAsset(String a){try{InputStream is=getAssets().open(a);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm!=null)showBitmap(bm);}catch(Exception e){Toast.makeText(this,"OEM 근거 이미지를 열 수 없습니다: "+a,Toast.LENGTH_SHORT).show();}}
    private void showBitmap(Bitmap bm){Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);sv.addView(iv);d.setContentView(sv);d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-1);}
    private void fatal(String s){TextView t=new TextView(this);t.setText(s);t.setTextSize(16);t.setPadding(30,30,30,30);setContentView(t);}
}
