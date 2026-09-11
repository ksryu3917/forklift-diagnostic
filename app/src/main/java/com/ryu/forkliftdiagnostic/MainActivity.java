package com.ryu.forkliftdiagnostic;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.*;
import android.net.Uri;
import android.provider.OpenableColumns;
import android.database.Cursor;
import android.view.*;
import android.widget.*;
import android.graphics.drawable.GradientDrawable;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity {
    private LinearLayout body;
    private JSONObject db;
    private String vehicle = "D25S-7";
    private String brand = "두산";
    private final ArrayList<Screen> history = new ArrayList<>();
    private SharedPreferences prefs;
    private final int PICK_PDF = 1001;
    private final int BLUE = Color.rgb(17,117,214);
    private final int NAVY = Color.rgb(16,38,58);
    private final int BG = Color.rgb(242,245,247);

    static class Screen {
        String type,a,b;
        Screen(String t){type=t;}
        Screen(String t,String a){type=t;this.a=a;}
        Screen(String t,String a,String b){type=t;this.a=a;this.b=b;}
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs=getSharedPreferences("forklift_diag",MODE_PRIVATE);
        vehicle=prefs.getString("vehicle","D25S-7");
        try { db=new JSONObject(readAsset("manual_db.json")); brand=db.optString("brand","두산"); }
        catch(Exception e){ fatal("DB 로딩 오류: "+e.getMessage()); return; }
        show(new Screen("home"),false);
    }

    private String readAsset(String name) throws IOException {
        InputStream is=getAssets().open(name);
        ByteArrayOutputStream os=new ByteArrayOutputStream();
        byte[] buf=new byte[8192]; int n;
        while((n=is.read(buf))>0) os.write(buf,0,n);
        is.close(); return os.toString(StandardCharsets.UTF_8.name());
    }

    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);}
    private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}

    private TextView tv(String s,int sp,boolean bold){
        TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));
        v.setPadding(dp(2),dp(5),dp(2),dp(5));if(bold)v.setTypeface(null,1);return v;
    }

    private LinearLayout card(){
        LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;
    }

    private Button btn(String s,boolean primary){
        Button b=new Button(this);b.setText(s);b.setTextSize(15);b.setAllCaps(false);b.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);
        b.setTextColor(primary?Color.WHITE:Color.rgb(25,30,35));b.setBackground(bg(primary?BLUE:Color.rgb(231,236,240),10));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(52));p.setMargins(0,dp(4),0,dp(4));b.setLayoutParams(p);return b;
    }

    private void baseScreen(String title){
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(6),dp(10),dp(6));top.setBackgroundColor(NAVY);
        if(history.size()>1){
            Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->back());
            top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(50)));
        }
        TextView t=tv(title,18,true);t.setTextColor(Color.WHITE);top.addView(t,new LinearLayout.LayoutParams(0,dp(50),1));
        TextView veh=tv(brand+" · "+vehicle,13,true);veh.setTextColor(Color.WHITE);top.addView(veh);
        Button home=new Button(this);home.setText("⌂");home.setTextSize(24);home.setTextColor(Color.WHITE);home.setBackgroundColor(Color.TRANSPARENT);home.setOnClickListener(v->show(new Screen("home"),false));top.addView(home,new LinearLayout.LayoutParams(dp(52),dp(50)));
        ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);
        root.addView(top);root.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);
    }

    private void show(Screen s,boolean push){if(push)history.add(s);else{history.clear();history.add(s);}render(s);}
    private void go(Screen s){history.add(s);render(s);}
    private void back(){if(history.size()<=1){finish();return;}history.remove(history.size()-1);render(history.get(history.size()-1));}
    @Override public void onBackPressed(){back();}

    private void render(Screen s){
        try{
            switch(s.type){
                case "home":home();break;
                case "diagnosis":diagnosis();break;
                case "systems":systems();break;
                case "symptoms":symptoms(s.a);break;
                case "symptom":symptom(s.a);break;
                case "cause":cause(s.a,s.b);break;
                case "graph":graph(s.a,s.b);break;
                case "manual":manual();break;
                case "search":manualSearch();break;
                case "parts":localList("부품 / 가격 DB","parts");break;
                case "repair":localList("정비 이력","repair");break;
                case "experience":localList("내 현장 경험","experience");break;
                case "add":addLocal(s.a);break;
                case "about":about();break;
                case "procedure":procedure(s.a,s.b);break;
                case "engine":engine();break;
                case "engine_dtc":engineDtc(s.a);break;
            }
        }catch(Exception e){fatal("화면 오류: "+e.getMessage());}
    }

    private void home() throws Exception{
        baseScreen("지게차 정비 어시스턴트");
        LinearLayout c=card();c.addView(tv("현재 차량",14,true));
        c.addView(tv(brand+" · "+vehicle,18,true));
        Spinner sp=new Spinner(this);JSONArray models=db.getJSONObject("manual").getJSONArray("models");ArrayList<String> ms=new ArrayList<>();
        for(int i=0;i<models.length();i++)ms.add(models.getString(i));
        sp.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,ms));sp.setSelection(Math.max(0,ms.indexOf(vehicle)));
        sp.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> p){}
            public void onItemSelected(android.widget.AdapterView<?> p,View v,int pos,long id){vehicle=ms.get(pos);prefs.edit().putString("vehicle",vehicle).apply();}
        });
        c.addView(sp);body.addView(c);
        Button a=btn("🔧 차량 진단",true);a.setOnClickListener(v->go(new Screen("diagnosis")));body.addView(a);
        Button b=btn("📘 매뉴얼 관리 / 검색",false);b.setOnClickListener(v->go(new Screen("manual")));body.addView(b);
        Button p=btn("📦 부품 / 가격 DB",false);p.setOnClickListener(v->go(new Screen("parts")));body.addView(p);
        Button r=btn("🧾 정비 이력",false);r.setOnClickListener(v->go(new Screen("repair")));body.addView(r);
        Button x=btn("🔩 내 현장 경험",false);x.setOnClickListener(v->go(new Screen("experience")));body.addView(x);
        Button z=btn("ℹ️ 앱 / 데이터 상태",false);z.setOnClickListener(v->go(new Screen("about")));body.addView(z);
        LinearLayout n=card();n.addView(tv("핵심 원칙",16,true));n.addView(tv("각 진단 STEP에서 정비사가 지금 봐야 할 자료만 보여주고, 측정/관찰 결과에 따라 다음 STEP으로 자동 분기합니다. OEM 원문은 근거 확인용 옵션입니다.",13,false));body.addView(n);
    }

    private void diagnosis() throws Exception{
        baseScreen("차량 진단");
        LinearLayout c=card();c.addView(tv(brand+" · "+vehicle+" · 증상 검색",17,true));
        EditText q=new EditText(this);q.setHint("예: 전진 안됨, 브레이크, 조향");c.addView(q);
        Button s=btn("증상 검색",true);s.setOnClickListener(v->{String term=q.getText().toString().trim();if(term.length()==0)go(new Screen("systems"));else searchSymptoms(term);});c.addView(s);
        Button y=btn("계통별로 찾기",false);y.setOnClickListener(v->go(new Screen("systems")));c.addView(y);
        Button e=btn("⚙ 엔진 진단 (D34 임시 기준)",false);e.setOnClickListener(v->go(new Screen("engine")));c.addView(e);body.addView(c);
    }

    private void searchSymptoms(String term){
        try{
            baseScreen("검색: "+term);JSONArray sy=db.getJSONArray("symptoms");int count=0;
            for(int i=0;i<sy.length();i++){JSONObject s=sy.getJSONObject(i);String hay=s.optString("name")+" "+s.optString("system")+" "+s.optJSONArray("causes");
                if(hay.toLowerCase().contains(term.toLowerCase())){Button b=btn(s.optString("system")+" · "+s.optString("name"),false);String id=s.optString("id");b.setOnClickListener(v->go(new Screen("symptom",id)));body.addView(b);count++;}}
            if(count==0)body.addView(tv("검색 결과가 없습니다.",15,true));
        }catch(Exception e){fatal(e.toString());}
    }

    private void systems() throws Exception{
        baseScreen("계통 선택");JSONArray sy=db.getJSONArray("symptoms");LinkedHashSet<String> set=new LinkedHashSet<>();
        for(int i=0;i<sy.length();i++)set.add(sy.getJSONObject(i).optString("system"));
        for(String s:set){Button b=btn(s,false);b.setOnClickListener(v->go(new Screen("symptoms",s)));body.addView(b);}
    }

    private void symptoms(String system) throws Exception{
        baseScreen(system+" 증상");JSONArray sy=db.getJSONArray("symptoms");
        for(int i=0;i<sy.length();i++){JSONObject s=sy.getJSONObject(i);if(system.equals(s.optString("system"))){Button b=btn(s.optString("name"),false);String id=s.optString("id");b.setOnClickListener(v->go(new Screen("symptom",id)));body.addView(b);}}
    }

    private JSONObject findSymptom(String id) throws Exception{
        JSONArray sy=db.getJSONArray("symptoms");for(int i=0;i<sy.length();i++)if(id.equals(sy.getJSONObject(i).optString("id")))return sy.getJSONObject(i);return null;
    }

    private JSONObject findCause(JSONObject s,String cid)throws Exception{
        JSONArray a=s.optJSONArray("cause_details");for(int i=0;i<a.length();i++)if(cid.equals(a.getJSONObject(i).optString("id")))return a.getJSONObject(i);return null;
    }

    private void symptom(String id)throws Exception{
        JSONObject s=findSymptom(id);baseScreen(s.optString("name"));LinearLayout c=card();c.addView(tv("가능한 원인",17,true));JSONArray a=s.optJSONArray("cause_details");
        for(int i=0;i<a.length();i++){JSONObject ca=a.getJSONObject(i);boolean g=ca.has("graph");String mode=ca.optString("verification_mode");String tag=g?"  ▶ 분기진단":mode.equals("oem_procedure_chain")?"  ▶ 점검절차":"  ▶ OEM 확인";Button b=btn((i+1)+". "+ca.optString("name")+tag,g);String cid=ca.optString("id");b.setOnClickListener(v->go(new Screen("cause",id,cid)));c.addView(b);}body.addView(c);
        LinearLayout src=card();src.addView(tv("OEM 근거",14,true));src.addView(tv(s.optString("source")+" / PDF "+s.optJSONArray("pdf_pages")+"쪽",13,false));body.addView(src);
    }

    private void cause(String sid,String cid)throws Exception{
        JSONObject sy=findSymptom(sid),c=findCause(sy,cid);baseScreen(c.optString("name"));
        LinearLayout x=card();x.addView(tv("현재 원인",13,true));x.addView(tv(c.optString("name"),19,true));x.addView(tv(c.optString("normalization_status","OEM 원인 정규화"),12,false));x.addView(tv("근거: "+c.optString("source")+" / PDF "+c.optJSONArray("pdf_pages"),12,false));body.addView(x);
        if(c.has("graph")){Button b=btn("실행형 분기진단 시작",true);String gid=c.getString("graph"),st=c.optString("graph_start");b.setOnClickListener(v->go(new Screen("graph",gid,st)));body.addView(b);}
        JSONArray tests=c.optJSONArray("tests");
        if(tests!=null && tests.length()>0){LinearLayout p=card();p.addView(tv("OEM 점검 절차",16,true));p.addView(tv("이 원인과 연결된 매뉴얼 검사만 표시합니다.",12,false));for(int i=0;i<tests.length();i++){String tid=tests.optString(i);JSONObject pr=db.optJSONObject("procedures").optJSONObject(tid);if(pr==null)continue;Button b=btn(pr.optString("title"),false);b.setOnClickListener(v->go(new Screen("procedure",tid,cid)));p.addView(b);}body.addView(p);}
        if(c.optString("remedy").length()>0){LinearLayout r=card();r.addView(tv("OEM 대책",16,true));r.addView(tv(c.optString("remedy"),14,false));body.addView(r);}
        if((tests==null||tests.length()==0)&&!c.has("graph")){LinearLayout w=card();w.addView(tv("OEM 원인표 기반 항목",15,true));w.addView(tv("이 원인은 매뉴얼 고장진단표에 명시되어 있지만 별도 측정 기준/분기 절차는 확인되지 않았습니다. 임의의 수치나 검사 순서는 만들지 않습니다.",13,false));body.addView(w);}
    }

    private void procedure(String pid,String cid)throws Exception{
        JSONObject p=db.getJSONObject("procedures").getJSONObject(pid);baseScreen(p.optString("title"));
        LinearLayout h=card();h.addView(tv(p.optString("system")+" · OEM 점검",13,true));h.addView(tv("근거: "+p.optString("source")+" / PDF "+p.optJSONArray("pdf_pages"),12,false));body.addView(h);
        LinearLayout m=card();if(p.optJSONArray("conditions")!=null){m.addView(tv("점검 조건",15,true));addArray(m,p.optJSONArray("conditions"),"• ");}if(p.optJSONArray("tools")!=null){m.addView(tv("필요 공구",15,true));addArray(m,p.optJSONArray("tools"),"• ");}m.addView(tv("점검 방법",15,true));addArray(m,p.optJSONArray("steps"),"① ");String std=p.optString("standard");JSONObject sbm=p.optJSONObject("standard_by_model");if(sbm!=null)std=sbm.optString(vehicle,std);if(std.length()>0)m.addView(tv("OEM 기준: "+std,15,true));if(p.optString("verification").length()>0)m.addView(tv("주의: "+p.optString("verification"),13,true));body.addView(m);
        JSONArray dec=p.optJSONArray("decision");if(dec!=null){LinearLayout d=card();d.addView(tv("판정 연결",15,true));addArray(d,dec,"• ");body.addView(d);}
        LinearLayout q=card();q.addView(tv("현장 확인 결과",16,true));Button ok=btn("기준 만족 / 이상 없음",false);ok.setOnClickListener(v->showResult("현재 검사 정상","다음 연결 검사 또는 다른 원인을 확인하십시오."));q.addView(ok);Button ng=btn("기준 이탈 / 이상 발견",true);ng.setOnClickListener(v->showResult("이상 확인","해당 OEM 점검 절차의 대책/판정 기준에 따라 수리 후 재검사하십시오."));q.addView(ng);body.addView(q);
    }

    private void engine()throws Exception{
        baseScreen("엔진 진단");JSONObject er=db.getJSONObject("engine_reference");LinearLayout w=card();w.addView(tv("⚠ "+er.optString("status"),16,true));w.addView(tv(er.optString("title"),15,true));w.addView(tv(er.optString("applicability"),12,false));body.addView(w);
        JSONArray a=db.optJSONArray("engine_dtcs");LinearLayout c=card();c.addView(tv("현재 정규화된 D34 DTC",16,true));for(int i=0;i<a.length();i++){JSONObject d=a.getJSONObject(i);Button b=btn(d.optString("code")+" · "+d.optString("name"),false);String code=d.optString("code");b.setOnClickListener(v->go(new Screen("engine_dtc",code)));c.addView(b);}body.addView(c);
    }

    private void engineDtc(String code)throws Exception{
        JSONArray a=db.optJSONArray("engine_dtcs");JSONObject d=null;for(int i=0;i<a.length();i++)if(code.equals(a.getJSONObject(i).optString("code")))d=a.getJSONObject(i);if(d==null)return;baseScreen(code+" 엔진 DTC");
        LinearLayout w=card();w.addView(tv(code+" · "+d.optString("name"),18,true));w.addView(tv("D34 임시 기준 — 현재 차량 전용 수치로 간주하지 않음",12,true));w.addView(tv("진단 실시 조건: "+d.optString("condition"),13,false));w.addView(tv("설정 조건: "+d.optString("set_condition"),13,false));body.addView(w);
        LinearLayout s=card();s.addView(tv("OEM 진단 순서",16,true));addArray(s,d.optJSONArray("steps"),"① ");s.addView(tv("이상 발견: "+d.optString("yes"),13,true));s.addView(tv("이상 없음: "+d.optString("no"),13,false));s.addView(tv("근거: "+d.optString("source"),11,false));body.addView(s);
    }

    private void graph(String gid,String stepId)throws Exception{
        JSONObject g=db.getJSONObject("diagnostic_graphs").getJSONObject(gid),s=g.getJSONObject("steps").getJSONObject(stepId);baseScreen(s.optString("title"));
        LinearLayout f=card();f.addView(tv("지금 정비사가 봐야 할 것",16,true));addArray(f,s.optJSONArray("focus"),"• ");if(s.optString("why").length()>0)f.addView(tv(s.optString("why"),12,false));body.addView(f);
        JSONObject vis=s.optJSONObject("visual");if(vis!=null){LinearLayout vc=card();vc.addView(tv("관련 자료",16,true));if(gid.equals("TM_FR_ELECTRICAL")){vc.addView(tv("정비용 재구성 회로도 (OEM 원본 기반)",14,true));ImageView cv=new ImageView(this);Bitmap cb=makeFRDiagram(stepId);cv.setImageBitmap(cb);cv.setAdjustViewBounds(true);cv.setOnClickListener(v->showCircuit(cb,"전·후진 전기계통 재구성도"));vc.addView(cv,new LinearLayout.LayoutParams(-1,dp(260)));vc.addView(tv("탭하면 크게 볼 수 있습니다. 파란 경로=계통 흐름, 주황=현재 점검 대상",11,false));}else{vc.addView(tv(vis.optString("label"),13,false));ImageView iv=loadFirstImage(vis.optJSONArray("pages"));if(iv!=null)vc.addView(iv,new LinearLayout.LayoutParams(-1,dp(340)));else vc.addView(tv("이 STEP 전용 그림은 아직 분리되지 않았습니다.",12,false));}body.addView(vc);}
        LinearLayout m=card();m.addView(tv("점검 조건",15,true));addArray(m,s.optJSONArray("conditions"),"• ");m.addView(tv("필요 공구",15,true));addArray(m,s.optJSONArray("tools"),"• ");m.addView(tv("점검 방법",15,true));addArray(m,s.optJSONArray("instructions"),"① ");if(s.optString("standard").length()>0)m.addView(tv("OEM 기준: "+s.optString("standard"),15,true));body.addView(m);
        LinearLayout q=card();q.addView(tv(s.optString("question"),18,true));JSONArray ch=s.optJSONArray("choices");
        for(int i=0;i<ch.length();i++){JSONObject cc=ch.getJSONObject(i);Button b=btn(cc.optString("label"),true);b.setOnClickListener(v->{try{saveDiagLog(gid,stepId,cc.optString("label"));if(cc.has("next"))go(new Screen("graph",gid,cc.getString("next")));else showResult(cc.optString("result"),cc.optString("action"));}catch(Exception e){toast(e.getMessage());}});q.addView(b);if(cc.optString("meaning").length()>0)q.addView(tv(cc.optString("meaning"),12,false));}body.addView(q);
        Button src=btn("OEM 근거 원문 보기 (옵션)",false);src.setOnClickListener(v->showEvidence(s.optJSONArray("evidence_pages"),g.optString("source")));body.addView(src);
    }

    private void addArray(LinearLayout l,JSONArray a,String p){if(a!=null)for(int i=0;i<a.length();i++)l.addView(tv(p+a.optString(i),13,false));}

    private ImageView loadFirstImage(JSONArray pages){
        if(pages==null)return null;for(int i=0;i<pages.length();i++){String n="oem_pages/p"+pages.optInt(i)+".jpg";try{InputStream is=getAssets().open(n);Bitmap bm=BitmapFactory.decodeStream(is);is.close();ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);return iv;}catch(Exception ignored){}}return null;
    }

    private void showEvidence(JSONArray pages,String source){
        Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);l.setPadding(dp(12),dp(12),dp(12),dp(20));l.addView(tv("OEM 근거 원문",18,true));l.addView(tv(source,12,false));boolean any=false;
        if(pages!=null)for(int i=0;i<pages.length();i++){String n="oem_pages/p"+pages.optInt(i)+".jpg";try{InputStream is=getAssets().open(n);Bitmap bm=BitmapFactory.decodeStream(is);is.close();ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);l.addView(iv);any=true;}catch(Exception ignored){}}
        if(!any)l.addView(tv("현재 내장된 원문 이미지에 해당 페이지가 없습니다. DB 페이지 참조는 유지됩니다.",13,false));Button close=btn("닫기",true);close.setOnClickListener(v->d.dismiss());l.addView(close);sv.addView(l);d.setContentView(sv);d.show();Window w=d.getWindow();if(w!=null)w.setLayout(-1,-1);
    }

    private void showResult(String r,String a){new AlertDialog.Builder(this).setTitle(r).setMessage(a).setPositiveButton("확인",null).show();}

    private void saveDiagLog(String gid,String step,String choice)throws Exception{JSONArray a=loadArray("diaglog");JSONObject o=new JSONObject();o.put("vehicle",vehicle);o.put("graph",gid);o.put("step",step);o.put("choice",choice);o.put("time",now());a.put(o);saveArray("diaglog",a);}
    private String now(){return new SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.KOREA).format(new Date());}
    private JSONArray loadArray(String key){try{return new JSONArray(prefs.getString(key,"[]"));}catch(Exception e){return new JSONArray();}}
    private void saveArray(String key,JSONArray a){prefs.edit().putString(key,a.toString()).apply();}

    private void manual()throws Exception{
        baseScreen("매뉴얼 관리");JSONObject m=db.getJSONObject("manual");LinearLayout c=card();c.addView(tv(m.optString("title"),17,true));c.addView(tv("판본 "+m.optString("edition")+" · "+m.optInt("page_count")+"쪽",13,false));c.addView(tv("브랜드 "+brand+" · 증상 "+db.getJSONArray("symptoms").length()+"개 / 원인 268개 정규화",13,false));body.addView(c);
        Button s=btn("매뉴얼 / 데이터 검색",true);s.setOnClickListener(v->go(new Screen("search")));body.addView(s);
        Button add=btn("＋ 새 PDF 매뉴얼 등록",false);add.setOnClickListener(v->pickPdf());body.addView(add);
        JSONArray pending=loadArray("manuals_pending");if(pending.length()>0){LinearLayout p=card();p.addView(tv("추가 등록된 매뉴얼",15,true));for(int i=0;i<pending.length();i++)p.addView(tv("• "+pending.optJSONObject(i).optString("name")+" · AI 분석 연결 대기",13,false));body.addView(p);}
        LinearLayout rule=card();rule.addView(tv("새 매뉴얼 분석 원칙",15,true));rule.addView(tv("증상 → 원인 → STEP → 해당 STEP에 필요한 회로/위치/측정자료 → 결과 입력 → 다음 분기. 분기 참조가 끝까지 연결되지 않으면 분석 완료 처리하지 않습니다.",13,false));body.addView(rule);
    }

    private void pickPdf(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("application/pdf");i.addCategory(Intent.CATEGORY_OPENABLE);startActivityForResult(i,PICK_PDF);}
    @Override protected void onActivityResult(int req,int res,Intent data){super.onActivityResult(req,res,data);if(req==PICK_PDF&&res==RESULT_OK&&data!=null&&data.getData()!=null){Uri u=data.getData();String n=fileName(u);JSONArray a=loadArray("manuals_pending");JSONObject o=new JSONObject();try{o.put("name",n);o.put("uri",u.toString());o.put("added",now());a.put(o);saveArray("manuals_pending",a);}catch(Exception ignored){}toast("등록됨: "+n+" (AI 분석 연결은 후속 단계)");render(history.get(history.size()-1));}}
    private String fileName(Uri u){String n="manual.pdf";Cursor c=getContentResolver().query(u,null,null,null,null);if(c!=null){try{if(c.moveToFirst()){int idx=c.getColumnIndex(OpenableColumns.DISPLAY_NAME);if(idx>=0)n=c.getString(idx);}}finally{c.close();}}return n;}

    private void manualSearch(){baseScreen("매뉴얼 / 데이터 검색");LinearLayout c=card();EditText q=new EditText(this);q.setHint("키워드 입력");c.addView(q);Button b=btn("검색",true);b.setOnClickListener(v->{String term=q.getText().toString().trim();if(term.length()>0)renderManualResults(term);});c.addView(b);body.addView(c);}
    private void renderManualResults(String term){try{baseScreen("검색: "+term);JSONArray sy=db.getJSONArray("symptoms");int n=0;for(int i=0;i<sy.length();i++){JSONObject s=sy.getJSONObject(i);if((s.optString("name")+" "+s.optJSONArray("causes")+" "+s.optString("source")).toLowerCase().contains(term.toLowerCase())){LinearLayout c=card();c.addView(tv(s.optString("system")+" · "+s.optString("name"),15,true));c.addView(tv("원인: "+s.optJSONArray("causes"),12,false));c.addView(tv("근거: "+s.optString("source")+" / PDF "+s.optJSONArray("pdf_pages"),12,false));body.addView(c);n++;}}if(n==0)body.addView(tv("검색 결과 없음",15,true));}catch(Exception e){fatal(e.toString());}}

    private void localList(String title,String key){baseScreen(title);Button add=btn("＋ 새 항목 추가",true);add.setOnClickListener(v->go(new Screen("add",key)));body.addView(add);JSONArray a=loadArray(key);if(a.length()==0){LinearLayout c=card();c.addView(tv("저장된 항목이 없습니다.",14,false));body.addView(c);return;}for(int i=a.length()-1;i>=0;i--){JSONObject o=a.optJSONObject(i);if(o==null)continue;LinearLayout c=card();c.addView(tv(o.optString("title"),16,true));c.addView(tv(o.optString("detail"),13,false));c.addView(tv(o.optString("time")+" · "+o.optString("vehicle"),11,false));body.addView(c);}}
    private void addLocal(String key){String title=key.equals("parts")?"부품/가격 추가":key.equals("repair")?"정비 이력 추가":"현장 경험 추가";baseScreen(title);LinearLayout c=card();EditText t=new EditText(this);t.setHint(key.equals("parts")?"부품명 / 품번":key.equals("repair")?"증상 / 작업 제목":"증상 / 확인된 원인");EditText d=new EditText(this);d.setHint(key.equals("parts")?"업체, 수량, 단가, 비고":key.equals("repair")?"최종진단, 수리내용, 부품비, 공임, 작업시간":"확인방법, 수리, 결과, 냉간/열간/간헐 조건");d.setMinLines(5);d.setGravity(Gravity.TOP);c.addView(t);c.addView(d);Button save=btn("저장",true);save.setOnClickListener(v->{try{JSONArray a=loadArray(key);JSONObject o=new JSONObject();o.put("title",t.getText().toString().trim());o.put("detail",d.getText().toString().trim());o.put("vehicle",vehicle);o.put("time",now());a.put(o);saveArray(key,a);toast("저장했습니다.");back();}catch(Exception e){toast(e.getMessage());}});c.addView(save);body.addView(c);if(key.equals("parts")){LinearLayout n=card();n.addView(tv("영수증 OCR",14,true));n.addView(tv("OCR 자동추출은 아직 연결 전입니다. 현재 버전은 실제 확인한 값을 직접 저장합니다.",12,false));body.addView(n);}}

    private void about()throws Exception{
        baseScreen("앱 / 데이터 상태");LinearLayout c=card();c.addView(tv("Android 네이티브 FIELD v0.2",18,true));c.addView(tv("단일 HTML/WebView가 아니라 Android 화면 + JSON DB + 개별 OEM 이미지로 구성됩니다.",13,false));c.addView(tv("내장 증상: "+db.getJSONArray("symptoms").length()+"개",13,false));c.addView(tv("실행형 정밀 분기그래프: "+db.getJSONObject("diagnostic_graphs").length()+"개 + 전체 원인 OEM 절차/근거 정규화",13,false));c.addView(tv("OEM 중요 이미지: 94개",13,false));body.addView(c);
        LinearLayout w=card();w.addView(tv("현재 완성도",15,true));w.addView(tv("64개 증상/268개 원인은 정규화 표시를 완료했습니다. 전용 OEM 검사절차가 있는 항목은 직접 실행할 수 있고, 매뉴얼에 원인표만 있는 항목은 임의 기준을 만들지 않고 OEM 근거/대책을 그대로 구분합니다. D34 엔진은 임시 기준 데이터입니다.",13,false));body.addView(w);
    }


    private Bitmap makeFRDiagram(String step){
        Bitmap b=Bitmap.createBitmap(1500,820,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);c.drawColor(Color.WHITE);Paint p=new Paint(1);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.CENTER);String hi=step.startsWith("B_")?"SW":step.startsWith("C_")?"HAR":step.startsWith("D_")?"SOL":"SOL";
        drawNode(c,p,70,280,250,430,"KEY / FUSE\n전원 공급",hi.equals("PWR"));drawArrow(c,p,250,355,350,355);
        drawNode(c,p,350,220,650,490,"F/R LEVER SWITCH\n핀 4-7 공통 확인\nF: 1-2 / R: 1-3",hi.equals("SW"));drawArrow(c,p,650,355,760,355);
        drawNode(c,p,760,250,980,460,"HARNESS\n단선/접속 점검",hi.equals("HAR"));drawArrow(c,p,980,355,1080,260);drawArrow(c,p,980,355,1080,500);
        drawNode(c,p,1080,140,1390,350,"FORWARD SOLENOID\n자화 → 플런저 약 3.18 mm",hi.equals("SOL"));drawNode(c,p,1080,410,1390,620,"REVERSE SOLENOID\n자화 → 플런저 약 3.18 mm",hi.equals("SOL"));
        p.setTextAlign(Paint.Align.LEFT);p.setTextSize(34);p.setColor(Color.rgb(20,45,65));c.drawText("전·후진 전기계통 정비용 재구성도",70,75,p);p.setTextSize(22);p.setTypeface(Typeface.DEFAULT);c.drawText("OEM 2-4-2 절차 기반 · 원본 근거는 별도 보기",70,115,p);return b;
    }
    private void drawNode(Canvas c,Paint p,float l,float t,float r,float b,String text,boolean hi){p.setStyle(Paint.Style.FILL);p.setColor(hi?Color.rgb(255,230,180):Color.rgb(232,242,250));c.drawRoundRect(l,t,r,b,24,24,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(hi?8:4);p.setColor(hi?Color.rgb(240,135,20):Color.rgb(40,110,170));c.drawRoundRect(l,t,r,b,24,24,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(20,40,55));p.setTextSize(27);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.CENTER);String[] a=text.split("\n");float y=(t+b)/2-(a.length-1)*20;for(String z:a){c.drawText(z,(l+r)/2,y,p);y+=42;}}
    private void drawArrow(Canvas c,Paint p,float x1,float y1,float x2,float y2){p.setColor(Color.rgb(40,110,170));p.setStrokeWidth(7);p.setStyle(Paint.Style.STROKE);c.drawLine(x1,y1,x2,y2,p);c.drawLine(x2,y2,x2-24,y2-18,p);c.drawLine(x2,y2,x2-24,y2+18,p);}
    private void showCircuit(Bitmap bm,String title){Dialog d=new Dialog(this);LinearLayout r=new LinearLayout(this);r.setOrientation(LinearLayout.VERTICAL);r.setPadding(dp(8),dp(8),dp(8),dp(8));r.addView(tv(title,18,true));HorizontalScrollView hs=new HorizontalScrollView(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);hs.addView(iv,new HorizontalScrollView.LayoutParams(dp(1200),dp(650)));r.addView(hs,new LinearLayout.LayoutParams(-1,0,1));Button close=btn("닫기",true);close.setOnClickListener(v->d.dismiss());r.addView(close);d.setContentView(r);d.show();Window w=d.getWindow();if(w!=null)w.setLayout(-1,-1);}

    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_LONG).show();}
    private void fatal(String s){TextView t=tv(s,15,false);t.setPadding(dp(20),dp(20),dp(20),dp(20));setContentView(t);}
}
