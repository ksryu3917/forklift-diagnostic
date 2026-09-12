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
    private JSONObject transDiag;
    private String vehicle = "D25S-7";
    private String brand = "두산";
    private String tmVariant = "STD";
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
        tmVariant=prefs.getString("tm_variant","STD");
        try { db=new JSONObject(readAsset("manual_db.json")); brand=db.optString("brand","두산"); }
        catch(Exception e){ fatal("DB 로딩 오류: "+e.getMessage()); return; }
        try { transDiag=new JSONObject(readAsset("transmission_diag_v08.json")); }
        catch(Exception e){ transDiag=new JSONObject(); }
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
        TextView veh=tv(brand+" · "+vehicle+" · "+tmVariant,13,true);veh.setTextColor(Color.WHITE);top.addView(veh);
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
                case "tm_diag":tmDiag(s.a,s.b);break;
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
        c.addView(sp);
        c.addView(tv("트랜스미션 사양",13,true));
        Spinner tvs=new Spinner(this);
        ArrayList<String> tmo=new ArrayList<>();
        tmo.add("기본형 (STD)"); tmo.add("ECT 옵션");
        tvs.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,tmo));
        tvs.setSelection("ECT".equals(tmVariant)?1:0);
        tvs.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> p){}
            public void onItemSelected(android.widget.AdapterView<?> p,View v,int pos,long id){
                tmVariant=pos==1?"ECT":"STD";
                prefs.edit().putString("tm_variant",tmVariant).apply();
            }
        });
        c.addView(tvs);
        body.addView(c);
        Button a=btn("🔧 차량 진단",true);a.setOnClickListener(v->go(new Screen("diagnosis")));body.addView(a);
        Button b=btn("📘 매뉴얼 관리 / 검색",false);b.setOnClickListener(v->go(new Screen("manual")));body.addView(b);
        Button p=btn("📦 부품 / 가격 DB",false);p.setOnClickListener(v->go(new Screen("parts")));body.addView(p);
        Button r=btn("🧾 정비 이력",false);r.setOnClickListener(v->go(new Screen("repair")));body.addView(r);
        Button x=btn("🔩 내 현장 경험",false);x.setOnClickListener(v->go(new Screen("experience")));body.addView(x);
        Button z=btn("ℹ️ 앱 / 데이터 상태",false);z.setOnClickListener(v->go(new Screen("about")));body.addView(z);
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
        JSONObject st=findSymptom(id);
        JSONObject tgs=transDiag==null?null:transDiag.optJSONObject("graphs");
        JSONObject tg=tgs==null?null:tgs.optJSONObject(id);
        if(tg!=null){
            tmDiag(id,tg.optString("start"));
            return;
        }
        baseScreen(st.optString("name"));
        LinearLayout c=card();
        c.addView(tv("가능한 원인",17,true));
        JSONArray a=st.optJSONArray("cause_details");
        for(int i=0;i<a.length();i++){
            JSONObject ca=a.getJSONObject(i);
            boolean g=ca.has("graph");
            Button b=btn((i+1)+". "+ca.optString("name")+(g?"  ▶ 분기진단":"  ▶ 확인"),g);
            String cid=ca.optString("id");
            b.setOnClickListener(v->go(new Screen("cause",id,cid)));
            c.addView(b);
        }
        body.addView(c);
    }



    private void cause(String sid,String cid)throws Exception{
        JSONObject sy=findSymptom(sid),c=findCause(sy,cid);
        baseScreen(c.optString("name"));

        LinearLayout h=card();
        h.addView(tv(c.optString("name"),20,true));
        h.addView(tv("증상 · "+sy.optString("name"),12,false));
        body.addView(h);

        LinearLayout p=card();
        p.addView(tv("확인 순서",16,true));
        addArray(p,c.optJSONArray("diag_plan"),"• ");
        if(c.optBoolean("needs_review",false))
            p.addView(tv("수치 기준이 확실히 연결되지 않은 항목입니다. 관련 없는 검사는 표시하지 않습니다.",11,false));
        body.addView(p);

        if(c.has("graph")){
            Button b=btn("▶ 분기진단 시작",true);
            String gid=c.getString("graph"),st=c.optString("graph_start");
            b.setOnClickListener(v->go(new Screen("graph",gid,st)));
            body.addView(b);
        }

        JSONArray tests=c.optJSONArray("ui_tests");
        if(tests!=null && tests.length()>0){
            LinearLayout q=card();
            q.addView(tv("측정 / 시험",16,true));
            for(int i=0;i<tests.length();i++){
                String tid=tests.optString(i);
                JSONObject pr=db.optJSONObject("procedures").optJSONObject(tid);
                if(pr==null)continue;
                Button b=btn(pr.optString("title"),false);
                final String ftid=tid;
                b.setOnClickListener(v->go(new Screen("procedure",ftid,cid)));
                q.addView(b);
            }
            body.addView(q);
        }

        addSystemVisual(sy.optString("system"));

        if(c.optString("remedy").length()>0){
            LinearLayout r=card();
            r.addView(tv("조치",16,true));
            r.addView(tv(c.optString("remedy"),14,false));
            body.addView(r);
        }
    }



    private String causeGuide(String name,String system){
        return "";
    }



    private void addSystemVisual(String system)throws Exception{
        JSONObject systems=db.optJSONObject("systems");
        if(systems==null)return;
        JSONObject sys=systems.optJSONObject(system);
        if(sys==null)return;

        LinearLayout v=card();
        v.addView(tv("계통 이해도",16,true));
        Bitmap bm=makeConceptDiagram(system,sys.optString("overview"));
        ImageView iv=new ImageView(this);
        iv.setImageBitmap(bm);
        iv.setAdjustViewBounds(true);
        iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        iv.setOnClickListener(x->showCircuit(bm,system+" 계통"));
        v.addView(iv,new LinearLayout.LayoutParams(-1,dp(300)));

        JSONArray pages=sys.optJSONArray("diagram_pages");
        if(loadFirstImage(pages)!=null){
            Button b=btn("세부 도면 보기",false);
            b.setOnClickListener(x->showEvidence(pages,""));
            v.addView(b);
        }
        body.addView(v);
    }



    private Bitmap makeConceptDiagram(String title,String overview){
        if(title.equals("트랜스미션"))return makeTransmissionDiagram();
        int w=1500,h=760;
        Bitmap bm=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(bm);c.drawColor(Color.WHITE);
        Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(46);p.setTypeface(Typeface.DEFAULT_BOLD);
        c.drawText(title+" 계통 흐름",45,65,p);

        String[] a=overview.split("→");
        int n=Math.max(1,a.length);
        int gap=20,box=Math.max(150,(w-90-gap*(n-1))/n);
        int y=220,bh=170;
        for(int i=0;i<n;i++){
            int x=45+i*(box+gap);
            drawNode(c,p,x,y,x+box,y+bh,a[i].trim(),false);
            if(i<n-1)drawArrow(c,p,x+box,y+bh/2,x+box+gap,y+bh/2);
        }
        p.setTypeface(Typeface.DEFAULT);p.setTextAlign(Paint.Align.LEFT);p.setTextSize(25);p.setColor(Color.DKGRAY);
        c.drawText(systemTip(title),45,610,p);
        return bm;
    }

    private String systemTip(String s){
        if(s.equals("유압"))return "진단 핵심: 탱크/흡입 → 펌프 → 우선순위·컨트롤밸브 → 작동기 → 리턴 순으로 압력·유량 손실을 좁힌다.";
        if(s.equals("스티어링"))return "진단 핵심: 공급압 → 우선순위밸브 → 스티어링유닛 → 실린더/링크 순으로 확인한다.";
        if(s.equals("브레이크"))return "진단 핵심: 공급유압 → 마스터실린더 → 라인/에어 → 액슬 브레이크 피스톤 순으로 확인한다.";
        if(s.equals("드라이브 액슬"))return "진단 핵심: 입력 회전 → 피니언/크라운 → 디퍼런셜 → 허브 감속부의 유격·백래시·소음을 분리한다.";
        if(s.equals("작업장치")||s.equals("마스트"))return "진단 핵심: 공급압이 정상인지 먼저 확인한 뒤 밸브 내부누설과 실린더/기계부를 분리한다.";
        if(s.equals("에어컨"))return "진단 핵심: 저압·고압을 동시에 보고 압력 조합으로 냉매·팽창밸브·컨덴서·컴프레서를 구분한다.";
        if(s.equals("ECT"))return "진단 핵심: 입력센서/레버 → 컨트롤러 → 하네스 → 비례밸브 출력 순으로 확인한다.";
        return "입력 → 제어 → 작동부 → 출력 순으로 고장구간을 좁힌다.";
    }

    private Bitmap makeTransmissionDiagram(){
        Bitmap b=Bitmap.createBitmap(1600,900,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b);c.drawColor(Color.WHITE);
        Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(46);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.LEFT);
        c.drawText("트랜스미션 동력·유압 흐름",55,65,p);

        drawNode(c,p,50,170,280,320,"엔진",false);
        drawArrow(c,p,280,245,350,245);
        drawNode(c,p,350,170,610,320,"토크컨버터",false);
        drawArrow(c,p,610,245,690,245);
        drawNode(c,p,690,150,970,340,"오일펌프\nTap 6",true);
        drawArrow(c,p,970,245,1040,245);
        drawNode(c,p,1040,120,1540,370,"컨트롤밸브\nTap 1 비교\nTap 4 F / Tap 5 R",false);

        drawArrow(c,p,1290,370,1080,505);
        drawNode(c,p,850,505,1120,670,"전진 클러치\nTap 4",false);
        drawArrow(c,p,1290,370,1400,505);
        drawNode(c,p,1240,505,1540,670,"후진 클러치\nTap 5",false);

        drawNode(c,p,60,500,350,650,"컨버터 충전\nTap 3",false);
        drawNode(c,p,390,500,680,650,"컨버터 출구\nTap 2",false);
        drawNode(c,p,390,710,680,845,"윤활 회로\nTap 7",false);

        p.setTextAlign(Paint.Align.LEFT);p.setTypeface(Typeface.DEFAULT);p.setTextSize(25);p.setColor(Color.DKGRAY);
        c.drawText("Tap 6과 Tap 1 비교 → 공통 공급 문제와 밸브/인칭 구간 문제를 분리",55,790,p);
        return b;
    }

    private void drawCentered(Canvas c,Paint p,String text,float cx,float cy,int maxw){
        String t=text;if(p.measureText(t)>maxw&&t.length()>8){int m=t.length()/2;c.drawText(t.substring(0,m),cx-p.measureText(t.substring(0,m))/2,cy-18,p);c.drawText(t.substring(m),cx-p.measureText(t.substring(m))/2,cy+22,p);}else c.drawText(t,cx-p.measureText(t)/2,cy,p);
    }

    private void procedure(String pid,String cid)throws Exception{
        JSONObject p=db.getJSONObject("procedures").getJSONObject(pid);
        baseScreen(p.optString("title"));

        if(pid.equals("T_PRESS")||pid.equals("H_RELIEF")||pid.equals("S_PRESS")||pid.equals("AC_PRESS")){
            LinearLayout pos=card();
            pos.addView(tv("측정 위치",16,true));
            Bitmap map=makeMeasurementMap(pid);
            ImageView iv=new ImageView(this);
            iv.setImageBitmap(map);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
            iv.setOnClickListener(v->showCircuit(map,p.optString("title")+" 측정 위치"));
            pos.addView(iv,new LinearLayout.LayoutParams(-1,dp(340)));
            JSONArray pp=p.optJSONArray("pdf_pages");
            if(loadFirstImage(pp)!=null){
                Button raw=btn("실제 도면에서 위치 확인",false);
                raw.setOnClickListener(v->showEvidence(pp,""));
                pos.addView(raw);
            }
            body.addView(pos);
        }

        LinearLayout m=card();
        if(p.optJSONArray("conditions")!=null){m.addView(tv("조건",15,true));addArray(m,p.optJSONArray("conditions"),"• ");}
        if(p.optJSONArray("tools")!=null){m.addView(tv("공구",15,true));addArray(m,p.optJSONArray("tools"),"• ");}
        m.addView(tv("점검",15,true));addArray(m,p.optJSONArray("steps"),"① ");

        String std=p.optString("standard");
        JSONObject sbm=p.optJSONObject("standard_by_model");
        if(sbm!=null)std=sbm.optString(vehicle,std);
        if(std.length()==0)std=p.optString("standard_raw");
        if(std.length()>0)m.addView(tv("기준값 · "+std,15,true));
        if(p.optString("verification").length()>0)m.addView(tv("주의 · "+p.optString("verification"),13,true));
        body.addView(m);

        JSONArray dec=p.optJSONArray("decision");
        if(dec!=null){
            LinearLayout d=card();d.addView(tv("판정",15,true));addArray(d,dec,"→ ");body.addView(d);
        }
    }

    private Bitmap makeMeasurementMap(String pid){
        Bitmap b=Bitmap.createBitmap(1500,850,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b);c.drawColor(Color.WHITE);
        Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(44);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.LEFT);

        if(pid.equals("T_PRESS")){
            c.drawText("트랜스미션 압력 측정 포인트",50,65,p);
            drawNode(c,p,70,180,340,340,"오일펌프\nTap 6",true);
            drawArrow(c,p,340,260,470,260);
            drawNode(c,p,470,140,920,380,"밸브 본체\nTap 1 비교",false);
            drawArrow(c,p,920,220,1040,165);
            drawNode(c,p,1040,90,1430,240,"F 클러치\nTap 4",false);
            drawArrow(c,p,920,300,1040,405);
            drawNode(c,p,1040,340,1430,500,"R 클러치\nTap 5",false);
            drawNode(c,p,160,520,480,690,"컨버터 충전\nTap 3",false);
            drawNode(c,p,570,520,890,690,"출구/쿨러입구\nTap 2",false);
            drawNode(c,p,980,520,1300,690,"윤활\nTap 7",false);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(24);p.setColor(Color.DKGRAY);
            c.drawText("49~71°C · Tap 6/1 비교 · F=Tap4 · R=Tap5 · N=Tap7/3/2",55,785,p);
        }else if(pid.equals("H_RELIEF")){
            c.drawText("메인/보조 릴리프 압력 측정",50,65,p);
            drawNode(c,p,80,230,380,410,"메인펌프",false);
            drawArrow(c,p,380,320,510,320);
            drawNode(c,p,510,180,980,460,"컨트롤밸브\n계기 플러그\n→ 니플 → 300bar 게이지",true);
            drawArrow(c,p,980,250,1110,190);
            drawNode(c,p,1110,100,1430,280,"LIFT\n메인 릴리프",false);
            drawArrow(c,p,980,390,1110,510);
            drawNode(c,p,1110,450,1430,630,"TILT/AUX\n보조 릴리프",false);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(24);p.setColor(Color.DKGRAY);
            c.drawText("작동유 50±5°C · 게이지 연결 위치는 실제 도면에서 함께 확인",55,760,p);
        }else if(pid.equals("S_PRESS")){
            c.drawText("스티어링 압력 측정",50,65,p);
            drawNode(c,p,80,240,360,420,"메인펌프",false);
            drawArrow(c,p,360,330,480,330);
            drawNode(c,p,480,190,850,470,"우선순위밸브\n포트(1)\n300bar 게이지",true);
            drawArrow(c,p,850,330,980,330);
            drawNode(c,p,980,220,1400,440,"스티어링 유닛\n→ 실린더",false);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(24);p.setColor(Color.DKGRAY);
            c.drawText("좌/우 끝단에서 압력 측정 · 원문 단위 불일치 항목은 자동 정상판정하지 않음",55,700,p);
        }else{
            c.drawText("에어컨 저압/고압 동시 측정",50,65,p);
            drawNode(c,p,70,230,360,410,"컴프레서",false);
            drawArrow(c,p,360,320,500,320);
            drawNode(c,p,500,190,850,450,"고압측 서비스포트\n13.7~15.7 bar",true);
            drawArrow(c,p,850,320,990,320);
            drawNode(c,p,990,190,1400,450,"저압측 서비스포트\n1.5~2.5 bar",true);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(24);p.setColor(Color.DKGRAY);
            c.drawText("RECIRC · 흡입 30~35°C · 엔진 1500 rpm · 블로워 4 · COOL",55,700,p);
        }
        return b;
    }

    private void engine()throws Exception{
        baseScreen("엔진 진단");JSONObject er=db.getJSONObject("engine_reference");LinearLayout w=card();w.addView(tv("⚠ "+er.optString("status"),16,true));w.addView(tv(er.optString("title"),15,true));w.addView(tv(er.optString("applicability"),12,false));body.addView(w);
        JSONArray a=db.optJSONArray("engine_dtcs");LinearLayout c=card();c.addView(tv("현재 정규화된 D34 DTC",16,true));for(int i=0;i<a.length();i++){JSONObject d=a.getJSONObject(i);Button b=btn(d.optString("code")+" · "+d.optString("name"),false);String code=d.optString("code");b.setOnClickListener(v->go(new Screen("engine_dtc",code)));c.addView(b);}body.addView(c);
    }


    private void engineDtc(String code)throws Exception{
        JSONArray a=db.optJSONArray("engine_dtcs");JSONObject d=null;
        for(int i=0;i<a.length();i++)if(code.equals(a.getJSONObject(i).optString("code")))d=a.getJSONObject(i);
        if(d==null)return;
        baseScreen(code+" 엔진 DTC");
        LinearLayout w=card();
        w.addView(tv(code+" · "+d.optString("name"),18,true));
        w.addView(tv("D34 참고 데이터 · 현재 선택 차량 D24 전용값으로 사용하지 않음",12,true));
        w.addView(tv("진단 조건 · "+d.optString("condition"),13,false));
        w.addView(tv("설정 조건 · "+d.optString("set_condition"),13,false));
        body.addView(w);
        LinearLayout x=card();
        x.addView(tv("진단 순서",16,true));
        addArray(x,d.optJSONArray("steps"),"① ");
        x.addView(tv("이상 발견 · "+d.optString("yes"),13,true));
        x.addView(tv("이상 없음 · "+d.optString("no"),13,false));
        body.addView(x);
    }



    private void graph(String gid,String stepId)throws Exception{
        JSONObject g=db.getJSONObject("diagnostic_graphs").getJSONObject(gid),
                   st=g.getJSONObject("steps").getJSONObject(stepId);
        baseScreen(st.optString("title"));

        LinearLayout f=card();
        addArray(f,st.optJSONArray("focus"),"• ");
        if(st.optString("why").length()>0)f.addView(tv(st.optString("why"),12,false));
        body.addView(f);

        JSONObject vis=st.optJSONObject("visual");
        if(vis!=null){
            LinearLayout vc=card();vc.addView(tv("위치 / 회로",16,true));
            if(gid.equals("TM_FR_ELECTRICAL")){
                Bitmap cb=makeFRDiagram(stepId);
                ImageView cv=new ImageView(this);cv.setImageBitmap(cb);cv.setAdjustViewBounds(true);
                cv.setOnClickListener(v->showCircuit(cb,"전·후진 전기계통"));
                vc.addView(cv,new LinearLayout.LayoutParams(-1,dp(280)));
            }else{
                ImageView iv=loadFirstImage(vis.optJSONArray("pages"));
                if(iv!=null)vc.addView(iv,new LinearLayout.LayoutParams(-1,dp(340)));
            }
            body.addView(vc);
        }

        LinearLayout m=card();
        if(st.optJSONArray("conditions")!=null){m.addView(tv("조건",15,true));addArray(m,st.optJSONArray("conditions"),"• ");}
        if(st.optJSONArray("tools")!=null){m.addView(tv("공구",15,true));addArray(m,st.optJSONArray("tools"),"• ");}
        m.addView(tv("점검",15,true));addArray(m,st.optJSONArray("instructions"),"① ");
        if(st.optString("standard").length()>0)m.addView(tv("기준값 · "+st.optString("standard"),15,true));
        body.addView(m);

        LinearLayout q=card();
        q.addView(tv(st.optString("question"),18,true));
        JSONArray ch=st.optJSONArray("choices");
        for(int i=0;i<ch.length();i++){
            JSONObject cc=ch.getJSONObject(i);
            Button b=btn(cc.optString("label"),true);
            b.setOnClickListener(v->{try{
                saveDiagLog(gid,stepId,cc.optString("label"));
                if(cc.has("next"))go(new Screen("graph",gid,cc.getString("next")));
                else showResult(cc.optString("result"),cc.optString("action"));
            }catch(Exception e){toast(e.getMessage());}});
            q.addView(b);
            if(cc.optString("meaning").length()>0)q.addView(tv(cc.optString("meaning"),12,false));
        }
        body.addView(q);
    }



    private void tmDiag(String sid,String nodeId)throws Exception{
        JSONObject graphs=transDiag.getJSONObject("graphs");
        JSONObject g=graphs.getJSONObject(sid);
        JSONObject nodes=g.getJSONObject("nodes");
        if("ECT".equals(tmVariant)){
            if("SYM004".equals(sid) && "inch".equals(nodeId) && nodes.has("ect_inch")) nodeId="ect_inch";
            if("SYM005".equals(sid) && "pressure".equals(nodeId) && nodes.has("ect_shift")) nodeId="ect_shift";
        }
        JSONObject n=nodes.getJSONObject(nodeId);
        final String currentNodeId=nodeId;
        JSONObject sy=findSymptom(sid);
        String title=n.optString("title",sy==null?"트랜스미션 진단":sy.optString("name"));
        baseScreen("T/M 진단");

        LinearLayout h=card();
        h.addView(tv(sy==null?title:sy.optString("name"),18,true));
        String note=n.optString("note");
        if(note.length()>0)h.addView(tv(note,13,false));
        body.addView(h);

        JSONArray cond=n.optJSONArray("conditions");
        if(cond!=null && cond.length()>0){
            LinearLayout cc=card(); cc.addView(tv("측정 조건",15,true)); addArray(cc,cond,"• "); body.addView(cc);
        }

        String vis=n.optString("visual");
        if("SYM000".equals(sid) && ("tap6".equals(currentNodeId) || "tap1".equals(currentNodeId) || "pair".equals(currentNodeId))){
            addTmManualPressureImage();
        }else if(vis.length()>0){
            addTmStepVisual(vis);
        }

        String type=n.optString("type");
        if("result".equals(type)){ showTmResult(n); return; }
        if("measure".equals(type)){ showTmMeasure(sid,currentNodeId,n); return; }
        if("clutch_pair_measure".equals(type)){ showTmClutchPairMeasure(sid,currentNodeId,n); return; }

        LinearLayout q=card(); q.addView(tv(n.optString("question"),17,true));
        JSONArray ch=n.optJSONArray("choices");
        if(ch!=null)for(int i=0;i<ch.length();i++){
            JSONObject o=ch.getJSONObject(i);
            Button b=btn(o.optString("label"),true);
            String next=o.optString("next");
            b.setOnClickListener(v->{
                try{ saveDiagLog("TM_V08_"+sid,currentNodeId,o.optString("label")); }
                catch(Exception e){ android.util.Log.w("ForkliftDiag","diag log failed",e); }
                go(new Screen("tm_diag",sid,next));
            });
            q.addView(b);
        }
        body.addView(q);
    }

    private void showTmMeasure(String sid,String nodeId,JSONObject n){
        LinearLayout m=card();
        m.addView(tv(n.optString("prompt"),17,true));
        double lo=n.optDouble("min"),hi=n.optDouble("max");
        String unit=n.optString("unit");
        m.addView(tv(String.format(Locale.US,"정상 범위 · %.1f ~ %.1f %s",lo,hi,unit),15,true));
        EditText v=new EditText(this);
        v.setInputType(android.text.InputType.TYPE_CLASS_NUMBER|android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL|android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
        v.setHint("실측값 입력");
        m.addView(v);
        Button b=btn("실측값으로 판정",true);
        b.setOnClickListener(x->{
            try{
                double val=Double.parseDouble(v.getText().toString().trim());
                String next=val<lo?n.optString("next_low"):val>hi?n.optString("next_high"):n.optString("next_normal");
                saveDiagLog("TM_V08_"+sid,nodeId,String.format(Locale.US,"%.2f %s",val,unit));
                if(next.length()==0){toast("다음 분기 데이터가 없습니다.");return;}
                go(new Screen("tm_diag",sid,next));
            }catch(Exception e){toast("숫자로 입력하세요.");}
        });
        m.addView(b); body.addView(m);
    }


    private void showTmClutchPairMeasure(String sid,String nodeId,JSONObject n){
        LinearLayout m=card();
        m.addView(tv("F 선택",17,true));
        EditText f4=tmPressureInput("Tap4 (bar)");
        EditText f5=tmPressureInput("Tap5 (bar)");
        m.addView(f4); m.addView(f5);

        m.addView(tv("R 선택",17,true));
        EditText r4=tmPressureInput("Tap4 (bar)");
        EditText r5=tmPressureInput("Tap5 (bar)");
        m.addView(r4); m.addView(r5);

        TextView guide=tv("정상: F 선택 Tap4 7.3~8.6 / Tap5 0 · R 선택 Tap5 7.3~8.6 / Tap4 0",13,false);
        m.addView(guide);

        Button b=btn("4개 실측값으로 판정",true);
        b.setOnClickListener(v->{
            try{
                double fv4=Double.parseDouble(f4.getText().toString().trim());
                double fv5=Double.parseDouble(f5.getText().toString().trim());
                double rv4=Double.parseDouble(r4.getText().toString().trim());
                double rv5=Double.parseDouble(r5.getText().toString().trim());

                final double LO=7.3, HI=8.6, ZERO_MAX=0.5;
                boolean fApply=fv4>=LO && fv4<=HI;
                boolean rApply=rv5>=LO && rv5<=HI;
                boolean fOff=fv5<=ZERO_MAX;
                boolean rOff=rv4<=ZERO_MAX;

                String next;
                if(!fOff || !rOff) next=n.optString("next_cross_apply");
                else if(fv4<LO && rv5<LO) next=n.optString("next_common_low");
                else if(fv4<LO && rApply) next=n.optString("next_f_low");
                else if(rv5<LO && fApply) next=n.optString("next_r_low");
                else if(fApply && rApply) next=n.optString("next_normal");
                else if(fv4>HI || rv5>HI) next=n.optString("next_cross_apply");
                else next=n.optString("next_common_low");

                try{
                    saveDiagLog("TM_V083_"+sid,nodeId,
                        String.format(Locale.US,"F:T4 %.2f/T5 %.2f, R:T4 %.2f/T5 %.2f",fv4,fv5,rv4,rv5));
                }catch(Exception e){ android.util.Log.w("ForkliftDiag","diag log failed",e); }
                go(new Screen("tm_diag",sid,next));
            }catch(Exception e){ toast("Tap4/Tap5 네 값을 모두 숫자로 입력하세요."); }
        });
        m.addView(b);
        body.addView(m);
    }

    private EditText tmPressureInput(String hint){
        EditText e=new EditText(this);
        e.setHint(hint);
        e.setTextSize(18);
        e.setInputType(android.text.InputType.TYPE_CLASS_NUMBER |
                       android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL |
                       android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
        e.setPadding(dp(12),dp(10),dp(12),dp(10));
        return e;
    }

    private void showTmResult(JSONObject n){
        LinearLayout r=card(); r.addView(tv("판정",16,true)); r.addView(tv(n.optString("result"),17,true));
        if(n.optString("action").length()>0){ r.addView(tv("다음 점검",15,true)); r.addView(tv(n.optString("action"),14,false)); }
        body.addView(r);
    }


    private void addTmManualPressureImage(){
        try{
            JSONObject ps=db.optJSONObject("procedures");
            JSONObject p=ps==null?null:ps.optJSONObject("T_PRESS");
            JSONArray pages=p==null?null:p.optJSONArray("pdf_pages");
            Bitmap bmp=loadFirstImage(pages);
            if(bmp==null) return;

            LinearLayout c=card();
            c.addView(tv("실제 매뉴얼 · 압력 탭 위치",16,true));
            c.addView(tv("그림을 누르면 확대해서 볼 수 있습니다.",12,false));
            ImageView iv=new ImageView(this);
            iv.setImageBitmap(bmp);
            iv.setAdjustViewBounds(true);
            iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
            iv.setOnClickListener(v->showCircuit(bmp,"압력 탭 위치"));
            c.addView(iv,new LinearLayout.LayoutParams(-1,dp(430)));
            body.addView(c);
        }catch(Exception e){
            android.util.Log.w("ForkliftDiag","manual pressure image failed",e);
        }
    }

    private void addTmStepVisual(String code)throws Exception{
        LinearLayout c=card(); c.addView(tv("측정 위치 / 현재 계통",16,true));
        Bitmap b=makeTmStepVisual(code);
        ImageView iv=new ImageView(this); iv.setImageBitmap(b); iv.setAdjustViewBounds(true); iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        iv.setOnClickListener(v->showCircuit(b,"측정 위치"));
        c.addView(iv,new LinearLayout.LayoutParams(-1,dp(300)));
        if(code.startsWith("TAP")){
            JSONObject ps=db.optJSONObject("procedures");
            JSONObject p=ps==null?null:ps.optJSONObject("T_PRESS");
            JSONArray pages=p==null?null:p.optJSONArray("pdf_pages");
            if(loadFirstImage(pages)!=null){
                Button raw=btn("실제 도면에서 위치 확인",false);
                raw.setOnClickListener(v->showEvidence(pages,""));
                c.addView(raw);
            }
        }
        body.addView(c);
    }

    private Bitmap makeTmStepVisual(String code){
        Bitmap b=Bitmap.createBitmap(1700,980,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b); c.drawColor(Color.WHITE);
        Paint p=new Paint(1); p.setTextAlign(Paint.Align.LEFT);
        p.setColor(NAVY); p.setTextSize(48); p.setTypeface(Typeface.DEFAULT_BOLD);

        if(code.startsWith("SOL_")){
            String dir=code.contains("후진")?"R":code.contains("전진")?"F":"BOTH";
            c.drawText("F/R 전기계통 · 현재 필요한 회로만",55,70,p);
            drawElecBox(c,p,55,230,280,405,"KEY ON",false);
            drawWire(c,p,280,318,385,318,false);
            drawElecBox(c,p,385,205,650,430,"FWD/REV\nFUSE #3",false);
            drawWire(c,p,650,318,755,318,false);
            drawElecBox(c,p,755,150,1120,485,"F/R SWITCH\n공통 4↔7\nF 1↔2\nR 1↔3",true);
            drawWire(c,p,935,485,935,590,false);
            drawElecBox(c,p,745,590,1125,745,"OSS CONTROLLER\n방향지령 보고",false);
            boolean hf="F".equals(dir)||"BOTH".equals(dir);
            boolean hr="R".equals(dir)||"BOTH".equals(dir);
            drawWire(c,p,1120,250,1260,250,hf);
            drawElecBox(c,p,1260,145,1640,355,"F SOLENOID\n10±0.3Ω @25°C\nplunger ≈3.18 mm",hf);
            drawWire(c,p,1120,405,1260,530,hr);
            drawElecBox(c,p,1260,420,1640,655,"R SOLENOID\n10±0.3Ω @25°C\nplunger ≈3.18 mm",hr);
            p.setTypeface(Typeface.DEFAULT); p.setTextSize(27); p.setColor(Color.DKGRAY);
            c.drawText("예비시험: 엔진 OFF · KEY ON · 주차브레이크 해제 · 선택방향 솔레노이드 자화 확인",60,820,p);
            c.drawText("스위치 전원 0V → FWD/REV 퓨즈 #3 및 전원선 확인",60,865,p);
            c.drawText("솔레노이드 정격: 12 VDC (최대 14.5 V) · 1.2 A @25°C",60,910,p);
            return b;
        }

        if(code.equals("TAP45")){
            c.drawText("F/R 클러치 압력 · 두 게이지 관계",55,70,p);
            drawPressurePort(c,p,145,210,"Tap 4","전진 클러치","F 선택","7.3~8.6 bar","R/N: 0 bar",true);
            drawPressurePort(c,p,950,210,"Tap 5","후진 클러치","R 선택","7.3~8.6 bar","F/N: 0 bar",true);
            p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(30);p.setColor(NAVY);
            c.drawText("방향 전환 스톨/끌림에서는 두 압력을 동시에 본다",180,720,p);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(26);p.setColor(Color.DKGRAY);
            c.drawText("정상 예: F 선택 → Tap4 상승 / Tap5 0   ·   R 선택 → Tap5 상승 / Tap4 0",180,770,p);
            c.drawText("반대 클러치 압력이 남으면 해제 회로부터 진단",180,815,p);
            c.drawText("시험 오일온도 49~71°C · 표시값은 저속 공전 기준",180,865,p);
            return b;
        }

        if(code.equals("TAP6") || code.equals("TAP1")){
            boolean t6=code.equals("TAP6");
            c.drawText(t6?"Tap 6 · 공통 메인압 먼저":"Tap 1 · Tap6 저압일 때만",55,70,p);
            drawHydBox(c,p,70,245,330,430,"SUMP /\nSUCTION",false);
            drawArrow(c,p,330,338,440,338);
            drawHydBox(c,p,440,215,725,460,"T/M PUMP",t6);
            drawArrow(c,p,725,338,825,338);
            drawHydBox(c,p,825,180,1150,495,"VALVE BODY\nINCHING / MAIN",!t6);
            drawArrow(c,p,1150,338,1260,338);
            drawHydBox(c,p,1260,215,1600,460,"SELECTOR /\nCLUTCH",false);
            drawTapBadge(c,p,t6?595:975,585,t6?"Tap 6":"Tap 1");
            p.setTypeface(Typeface.DEFAULT); p.setTextSize(28); p.setColor(Color.DKGRAY);
            if(t6){
                c.drawText("8.3~10.3 bar @ 저속공전 · 9.0~11.0 bar @ 2000 rpm",80,760,p);
                c.drawText("Tap6 정상 → Tap1 측정하지 않음",80,810,p);
                c.drawText("Tap6 저압 → 그때 Tap1 비교",80,855,p);
            }else{
                c.drawText("Tap6 저압인 경우에만 비교점으로 사용",80,760,p);
                c.drawText("Tap1 정상 → Tap1~Tap6 유로/인칭 구간",80,810,p);
                c.drawText("Tap1도 저압 → 공통 공급 저압",80,855,p);
            }
            c.drawText("T/M 오일 49~71°C · 게이지 0~20.5 bar",80,905,p);
            return b;
        }

        if(code.equals("TAP3") || code.equals("TAP2") || code.equals("TAP7")){
            c.drawText("컨버터·쿨러·윤활 유로 · 현재 측정점",55,70,p);
            drawHydBox(c,p,55,245,300,430,"PUMP /\nSUPPLY",false);
            drawArrow(c,p,300,338,385,338);
            drawHydBox(c,p,385,205,690,470,"TORQUE\nCONVERTER",code.equals("TAP3"));
            drawArrow(c,p,690,338,790,338);
            drawHydBox(c,p,790,205,1080,470,"COOLER\nINLET",code.equals("TAP2"));
            drawArrow(c,p,1080,338,1180,338);
            drawHydBox(c,p,1180,205,1515,470,"OIL COOLER",false);
            drawArrow(c,p,1350,470,1350,565);
            drawHydBox(c,p,1130,565,1580,760,"CLUTCH / SHAFT\nLUBRICATION",code.equals("TAP7"));
            drawTapBadge(c,p,code.equals("TAP3")?535:code.equals("TAP2")?935:1350,820,code.replace("TAP","Tap "));
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(27);p.setColor(Color.DKGRAY);
            String spec=code.equals("TAP3")?"0.7~1.4 bar idle · 5.9~8.0 bar @2000":
                        code.equals("TAP2")?"0.3~0.6 bar idle · 2.5~4.0 bar @2000":
                        "0.1~0.7 bar idle · 2.4~3.5 bar @2000";
            c.drawText(spec+" · 오일 49~71°C",60,920,p);
            return b;
        }

        if(code.equals("SUCTION")){
            c.drawText("펌프 소음/저압 · 흡입측만 확인",55,70,p);
            drawHydBox(c,p,90,270,390,500,"T/M OIL\nLEVEL",false);
            drawArrow(c,p,390,385,500,385);
            drawHydBox(c,p,500,230,900,540,"STRAINER /\nSUCTION LINE",true);
            drawArrow(c,p,900,385,1020,385);
            drawHydBox(c,p,1020,270,1410,500,"T/M PUMP",false);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(29);p.setColor(Color.DKGRAY);
            c.drawText("먼저: 레벨 → 거품 → 점도/냉간 → 스트레이너 → 흡입 누기",110,700,p);
            c.drawText("이 구간 정상인데 소음 지속 시에만 압력/펌프 내부로 진행",110,755,p);
            return b;
        }

        if(code.equals("STALL")){
            c.drawText("STALL · 엔진 / 컨버터 / 클러치 분리",55,70,p);
            drawHydBox(c,p,75,260,410,495,"ENGINE\nOUTPUT",false);
            drawArrow(c,p,410,378,530,378);
            drawHydBox(c,p,530,210,980,545,"TORQUE CONVERTER\nONE-WAY CLUTCH",true);
            drawArrow(c,p,980,378,1100,378);
            drawHydBox(c,p,1100,250,1570,505,"F/R CLUTCH /\nTRANSMISSION",false);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(28);p.setColor(Color.DKGRAY);
            c.drawText("낮은 stall: 엔진 성능 정상 여부 먼저 → 정상이라면 converter one-way clutch",85,700,p);
            c.drawText("높은 stall: clutch pressure와 함께 봐서 유압 slip / 기계 slip 분리",85,755,p);
            c.drawText("한 번의 stall은 최대 10초 · 시험 사이 1200~1500 rpm으로 냉각",85,810,p);
            return b;
        }

        if(code.equals("ECT")){
            c.drawText("ECT 옵션 · 전자식 변속/인칭 제어",55,70,p);
            drawElecBox(c,p,55,190,365,390,"F/R LEVER\nSIGNAL",false);
            drawElecBox(c,p,55,520,365,720,"INCH PEDAL\nANGLE SENSOR",false);
            drawWire(c,p,365,290,550,380,false);
            drawWire(c,p,365,620,550,500,false);
            drawElecBox(c,p,550,275,980,610,"ECT CONTROLLER\n입력 → 전류제어",true);
            drawWire(c,p,980,365,1120,290,true);
            drawWire(c,p,980,520,1120,610,true);
            drawElecBox(c,p,1120,175,1620,405,"F PROPORTIONAL\nVALVE",true);
            drawElecBox(c,p,1120,500,1620,730,"R PROPORTIONAL\nVALVE",true);
            p.setTypeface(Typeface.DEFAULT);p.setTextSize(27);p.setColor(Color.DKGRAY);
            c.drawText("기본형 기계식 인칭/모듈레이션 밸브 진단과 혼합하지 않음",80,830,p);
            c.drawText("방향변환 시 비례밸브를 점진 제어하여 약 1초 내외로 체결",80,875,p);
            return b;
        }

        c.drawText("현재 단계",55,70,p);
        drawHydBox(c,p,390,270,1310,600,code,true);
        return b;
    }

    private void drawElecBox(Canvas c,Paint p,int l,int t,int r,int b,String text,boolean hi){
        p.setStyle(Paint.Style.FILL);p.setColor(hi?Color.rgb(225,241,255):Color.rgb(244,247,249));c.drawRoundRect(l,t,r,b,25,25,p);
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(hi?8:4);p.setColor(hi?BLUE:Color.rgb(105,120,132));c.drawRoundRect(l,t,r,b,25,25,p);
        p.setStyle(Paint.Style.FILL);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(28);p.setColor(NAVY);p.setTextAlign(Paint.Align.CENTER);
        drawCentered(c,p,text,(l+r)/2f,(t+b)/2f,r-l-24);p.setTextAlign(Paint.Align.LEFT);
    }
    private void drawWire(Canvas c,Paint p,float x1,float y1,float x2,float y2,boolean hi){
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(hi?12:5);p.setColor(hi?BLUE:Color.rgb(105,120,132));c.drawLine(x1,y1,x2,y2,p);p.setStyle(Paint.Style.FILL);
    }
    private void drawHydBox(Canvas c,Paint p,int l,int t,int r,int b,String text,boolean hi){
        drawElecBox(c,p,l,t,r,b,text,hi);
    }
    private void drawTapBadge(Canvas c,Paint p,float cx,float cy,String text){
        p.setStyle(Paint.Style.FILL);p.setColor(BLUE);c.drawCircle(cx,cy,67,p);
        p.setTextAlign(Paint.Align.CENTER);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(28);p.setColor(Color.WHITE);c.drawText(text,cx,cy+10,p);p.setTextAlign(Paint.Align.LEFT);
    }
    private void drawPressurePort(Canvas c,Paint p,int x,int y,String tap,String name,String condition,String range,String off,boolean hi){
        drawElecBox(c,p,x,y,x+600,y+390,name+"\n"+tap+"\n"+condition+" · "+range+"\n"+off,hi);
        drawTapBadge(c,p,x+300,y+490,tap);
    }

    private void addArray(LinearLayout l,JSONArray a,String p){if(a!=null)for(int i=0;i<a.length();i++)l.addView(tv(p+a.optString(i),13,false));}


    private ImageView loadFirstImage(JSONArray pages){
        if(pages==null)return null;
        for(int i=0;i<pages.length();i++){
            int pg=pages.optInt(i);
            String[] names={String.format(Locale.US,"oem_pages/p%03d.jpg",pg),"oem_pages/p"+pg+".jpg"};
            for(String n:names){
                try{
                    InputStream is=getAssets().open(n);
                    Bitmap bm=BitmapFactory.decodeStream(is);is.close();
                    ImageView iv=new ImageView(this);
                    iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
                    iv.setOnClickListener(v->showCircuit(bm,"도면"));
                    return iv;
                }catch(Exception ignored){}
            }
        }
        return null;
    }



    private void showEvidence(JSONArray pages,String source){
        Dialog d=new Dialog(this);
        ScrollView sv=new ScrollView(this);
        LinearLayout l=new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);l.setPadding(dp(12),dp(12),dp(12),dp(20));
        l.addView(tv("세부 도면",18,true));
        boolean any=false;
        if(pages!=null)for(int i=0;i<pages.length();i++){
            int pg=pages.optInt(i);
            String[] names={String.format(Locale.US,"oem_pages/p%03d.jpg",pg),"oem_pages/p"+pg+".jpg"};
            for(String n:names){
                try{
                    InputStream is=getAssets().open(n);
                    Bitmap bm=BitmapFactory.decodeStream(is);is.close();
                    ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);
                    l.addView(iv);any=true;break;
                }catch(Exception ignored){}
            }
        }
        if(!any)l.addView(tv("표시할 도면 이미지가 없습니다.",13,false));
        Button close=btn("닫기",true);close.setOnClickListener(v->d.dismiss());l.addView(close);
        sv.addView(l);d.setContentView(sv);d.show();
        Window w=d.getWindow();if(w!=null)w.setLayout(-1,-1);
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

    private void renderManualResults(String term){
        try{
            baseScreen("검색: "+term);
            JSONArray sy=db.getJSONArray("symptoms");int n=0;
            for(int i=0;i<sy.length();i++){
                JSONObject s=sy.getJSONObject(i);
                if((s.optString("name")+" "+s.optJSONArray("causes")).toLowerCase().contains(term.toLowerCase())){
                    LinearLayout c=card();
                    c.addView(tv(s.optString("system")+" · "+s.optString("name"),15,true));
                    c.addView(tv("원인: "+s.optJSONArray("causes"),12,false));
                    body.addView(c);n++;
                }
            }
            if(n==0)body.addView(tv("검색 결과 없음",15,true));
        }catch(Exception e){fatal(e.toString());}
    }


    private void localList(String title,String key){baseScreen(title);Button add=btn("＋ 새 항목 추가",true);add.setOnClickListener(v->go(new Screen("add",key)));body.addView(add);JSONArray a=loadArray(key);if(a.length()==0){LinearLayout c=card();c.addView(tv("저장된 항목이 없습니다.",14,false));body.addView(c);return;}for(int i=a.length()-1;i>=0;i--){JSONObject o=a.optJSONObject(i);if(o==null)continue;LinearLayout c=card();c.addView(tv(o.optString("title"),16,true));c.addView(tv(o.optString("detail"),13,false));c.addView(tv(o.optString("time")+" · "+o.optString("vehicle"),11,false));body.addView(c);}}
    private void addLocal(String key){String title=key.equals("parts")?"부품/가격 추가":key.equals("repair")?"정비 이력 추가":"현장 경험 추가";baseScreen(title);LinearLayout c=card();EditText t=new EditText(this);t.setHint(key.equals("parts")?"부품명 / 품번":key.equals("repair")?"증상 / 작업 제목":"증상 / 확인된 원인");EditText d=new EditText(this);d.setHint(key.equals("parts")?"업체, 수량, 단가, 비고":key.equals("repair")?"최종진단, 수리내용, 부품비, 공임, 작업시간":"확인방법, 수리, 결과, 냉간/열간/간헐 조건");d.setMinLines(5);d.setGravity(Gravity.TOP);c.addView(t);c.addView(d);Button save=btn("저장",true);save.setOnClickListener(v->{try{JSONArray a=loadArray(key);JSONObject o=new JSONObject();o.put("title",t.getText().toString().trim());o.put("detail",d.getText().toString().trim());o.put("vehicle",vehicle);o.put("time",now());a.put(o);saveArray(key,a);toast("저장했습니다.");back();}catch(Exception e){toast(e.getMessage());}});c.addView(save);body.addView(c);if(key.equals("parts")){LinearLayout n=card();n.addView(tv("영수증 OCR",14,true));n.addView(tv("OCR 자동추출은 아직 연결 전입니다. 현재 버전은 실제 확인한 값을 직접 저장합니다.",12,false));body.addView(n);}}


    private void about()throws Exception{
        baseScreen("앱 / 데이터 상태");
        JSONObject norm=db.optJSONObject("diagnostic_normalization");
        LinearLayout c=card();
        c.addView(tv("FIELD v0.8.3 · SYM000 Field Test · 진단 구조 재설계",18,true));
        c.addView(tv("증상 "+db.getJSONArray("symptoms").length()+"개",13,false));
        c.addView(tv("원인 "+norm.optInt("cause_count",268)+"개 전체 재분류",13,false));
        c.addView(tv("원인 확인 → 필요한 경우에만 계측 → 결과 판정 순서로 표시",13,false));
        c.addView(tv("관련 없는 공통 검사 연결은 화면에서 차단",13,false));
        c.addView(tv("D34 엔진 데이터는 D24 차량과 분리된 참고 데이터",13,false));
        body.addView(c);
    }



    private Bitmap makeFRDiagram(String step){
        Bitmap b=Bitmap.createBitmap(1500,820,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);c.drawColor(Color.WHITE);Paint p=new Paint(1);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.CENTER);String hi=step.startsWith("B_")?"SW":step.startsWith("C_")?"HAR":step.startsWith("D_")?"SOL":"SOL";
        drawNode(c,p,70,280,250,430,"KEY / FUSE\n전원 공급",hi.equals("PWR"));drawArrow(c,p,250,355,350,355);
        drawNode(c,p,350,220,650,490,"F/R LEVER SWITCH\n핀 4-7 공통 확인\nF: 1-2 / R: 1-3",hi.equals("SW"));drawArrow(c,p,650,355,760,355);
        drawNode(c,p,760,250,980,460,"HARNESS\n단선/접속 점검",hi.equals("HAR"));drawArrow(c,p,980,355,1080,260);drawArrow(c,p,980,355,1080,500);
        drawNode(c,p,1080,140,1390,350,"FORWARD SOLENOID\n자화 → 플런저 약 3.18 mm",hi.equals("SOL"));drawNode(c,p,1080,410,1390,620,"REVERSE SOLENOID\n자화 → 플런저 약 3.18 mm",hi.equals("SOL"));
        p.setTextAlign(Paint.Align.LEFT);p.setTextSize(34);p.setColor(Color.rgb(20,45,65));c.drawText("전·후진 전기계통 정비용 재구성도",70,75,p);p.setTextSize(22);p.setTypeface(Typeface.DEFAULT);c.drawText("전원 → F/R 스위치 → 하네스 → 솔레노이드",70,115,p);return b;
    }
    private void drawNode(Canvas c,Paint p,float l,float t,float r,float b,String text,boolean hi){p.setStyle(Paint.Style.FILL);p.setColor(hi?Color.rgb(255,230,180):Color.rgb(232,242,250));c.drawRoundRect(l,t,r,b,24,24,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(hi?8:4);p.setColor(hi?Color.rgb(240,135,20):Color.rgb(40,110,170));c.drawRoundRect(l,t,r,b,24,24,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(20,40,55));p.setTextSize(27);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextAlign(Paint.Align.CENTER);String[] a=text.split("\n");float y=(t+b)/2-(a.length-1)*20;for(String z:a){c.drawText(z,(l+r)/2,y,p);y+=42;}}
    private void drawArrow(Canvas c,Paint p,float x1,float y1,float x2,float y2){p.setColor(Color.rgb(40,110,170));p.setStrokeWidth(7);p.setStyle(Paint.Style.STROKE);c.drawLine(x1,y1,x2,y2,p);c.drawLine(x2,y2,x2-24,y2-18,p);c.drawLine(x2,y2,x2-24,y2+18,p);}
    static class ZoomImageView extends android.widget.ImageView {
        private final Matrix matrix=new Matrix();private final ScaleGestureDetector scale;private final GestureDetector gesture;private float lastX,lastY;private boolean dragging=false;
        public ZoomImageView(Context c){super(c);setScaleType(ScaleType.MATRIX);scale=new ScaleGestureDetector(c,new ScaleGestureDetector.SimpleOnScaleGestureListener(){public boolean onScale(ScaleGestureDetector d){float f=d.getScaleFactor();matrix.postScale(f,f,d.getFocusX(),d.getFocusY());setImageMatrix(matrix);return true;}});gesture=new GestureDetector(c,new GestureDetector.SimpleOnGestureListener(){public boolean onDoubleTap(android.view.MotionEvent e){matrix.postScale(1.7f,1.7f,e.getX(),e.getY());setImageMatrix(matrix);return true;}});}
        @Override public boolean onTouchEvent(android.view.MotionEvent e){scale.onTouchEvent(e);gesture.onTouchEvent(e);switch(e.getActionMasked()){case android.view.MotionEvent.ACTION_DOWN:lastX=e.getX();lastY=e.getY();dragging=true;break;case android.view.MotionEvent.ACTION_MOVE:if(dragging&&!scale.isInProgress()){float dx=e.getX()-lastX,dy=e.getY()-lastY;matrix.postTranslate(dx,dy);setImageMatrix(matrix);lastX=e.getX();lastY=e.getY();}break;case android.view.MotionEvent.ACTION_UP:case android.view.MotionEvent.ACTION_CANCEL:dragging=false;break;}return true;}
        @Override protected void onSizeChanged(int w,int h,int ow,int oh){super.onSizeChanged(w,h,ow,oh);android.graphics.drawable.Drawable d=getDrawable();if(d!=null&&d.getIntrinsicWidth()>0&&d.getIntrinsicHeight()>0){float s=Math.min((float)w/d.getIntrinsicWidth(),(float)h/d.getIntrinsicHeight());matrix.reset();matrix.postScale(s,s);matrix.postTranslate((w-d.getIntrinsicWidth()*s)/2f,(h-d.getIntrinsicHeight()*s)/2f);setImageMatrix(matrix);}}
    }
    private void showCircuit(Bitmap bm,String title){Dialog d=new Dialog(this);LinearLayout r=new LinearLayout(this);r.setOrientation(LinearLayout.VERTICAL);r.setPadding(dp(8),dp(8),dp(8),dp(8));r.setBackgroundColor(Color.WHITE);r.addView(tv(title,17,true));r.addView(tv("두 손가락 확대/축소 · 드래그 이동 · 더블탭 확대",11,false));ZoomImageView iv=new ZoomImageView(this);iv.setImageBitmap(bm);r.addView(iv,new LinearLayout.LayoutParams(-1,0,1));Button close=btn("닫기",true);close.setOnClickListener(v->d.dismiss());r.addView(close);d.setContentView(r);d.show();Window w=d.getWindow();if(w!=null)w.setLayout(-1,-1);}

    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_LONG).show();}
    private void fatal(String s){TextView t=tv(s,15,false);t.setPadding(dp(20),dp(20),dp(20),dp(20));setContentView(t);}
}
