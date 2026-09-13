package com.ryu.forkliftdiagnostic;

import android.app.*;
import android.os.*;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class ExpertDiagnosticActivity extends Activity {
    private LinearLayout body;
    private JSONObject root,item;
    private final int NAVY=Color.rgb(16,38,58), BLUE=Color.rgb(17,117,214), BG=Color.rgb(242,245,247);

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        try{
            root=new JSONObject(readAsset("expert_diag_v2.json"));
            String cid=getIntent().getStringExtra("cause_id");
            item=findItem(cid);
            if(item==null) throw new Exception("원인 진단 데이터가 없습니다: "+cid);
            render();
        }catch(Exception e){fatal("전문가 진단 로딩 오류: "+e.getMessage());}
    }

    private String readAsset(String name)throws Exception{
        InputStream is=getAssets().open(name); ByteArrayOutputStream os=new ByteArrayOutputStream();
        byte[] buf=new byte[8192]; int n; while((n=is.read(buf))>0) os.write(buf,0,n); is.close();
        return os.toString(StandardCharsets.UTF_8.name());
    }
    private JSONObject findItem(String id)throws Exception{
        JSONArray a=root.getJSONArray("items");
        for(int i=0;i<a.length();i++){JSONObject x=a.getJSONObject(i);if(id!=null&&id.equals(x.optString("id")))return x;}return null;
    }
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);}
    private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}
    private TextView tv(String s,int sp,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));v.setPadding(dp(3),dp(5),dp(3),dp(5));if(bold)v.setTypeface(null,1);return v;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;}
    private Button btn(String s,boolean primary){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(14);b.setTextColor(primary?Color.WHITE:Color.rgb(25,30,35));b.setBackground(bg(primary?BLUE:Color.rgb(231,236,240),10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(52));p.setMargins(0,dp(4),0,dp(4));b.setLayoutParams(p);return b;}
    private void base(String title){
        LinearLayout rootv=new LinearLayout(this);rootv.setOrientation(LinearLayout.VERTICAL);rootv.setBackgroundColor(BG);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(10),dp(8),dp(10),dp(8));top.setBackgroundColor(NAVY);
        Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(52)));
        TextView t=tv(title,18,true);t.setTextColor(Color.WHITE);top.addView(t,new LinearLayout.LayoutParams(0,dp(52),1));
        ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);
        rootv.addView(top);rootv.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(rootv);
    }

    private void render()throws Exception{
        base("현장 전문가 진단");
        LinearLayout h=card();
        h.addView(tv(item.optString("system")+" · "+item.optString("symptom"),13,false));
        h.addView(tv(item.optString("cause"),20,true));
        String level=item.optString("level");
        h.addView(tv("진단 등급 · "+("A_OEM_EXECUTABLE".equals(level)?"A · OEM 절차/수치 연결":"B · 현장 격리/비교 실행형"),12,true));
        body.addView(h);

        addQuickView(item.optJSONObject("quick_view"));
        // All 268 expert causes are mapped in test_point_locator_v1.json.
        // The test-point screen comes before parts and before any teardown decision.
        Button tp=btn("⊙ 이 원인 측정포인트 / 압력탭 바로보기",true);
        tp.setOnClickListener(v->{android.content.Intent it=new android.content.Intent(this,TestPointLocatorActivity.class);it.putExtra("cause_id",item.optString("id"));it.putExtra("system",item.optString("system"));startActivity(it);});
        body.addView(tp);
        Button loc=btn("◎ 이 고장 점검 위치맵",true);
        loc.setOnClickListener(v->{android.content.Intent it=new android.content.Intent(this,FieldLocationMapActivity.class);it.putExtra("system",item.optString("system"));it.putExtra("context",item.optString("cause"));startActivity(it);});
        body.addView(loc);
        addComponentLocator(item.optJSONObject("component_locator"));
        addSimplifiedDiagram(item.getJSONObject("diagram"));
        addMeasurementPoints(item.optJSONArray("measurement_points"));
        addArrayCard("분해 전 현장 점검 순서",item.optJSONArray("field_sequence"),"① ");
        addArrayCard("필요 공구",item.optJSONArray("tools"),"• ");
        addArrayCard("먼저 배제할 원인",item.optJSONArray("rule_out"),"• ");
        addArrayCard("확정 조건",item.optJSONArray("confirm_if"),"• ");
        addSpecificityGate(item.optJSONObject("specificity_gate"), item.optJSONObject("diagnostic_limit"));

        LinearLayout g=card();g.addView(tv("분해/교환 조건",16,true));g.addView(tv(item.optString("disassembly_gate"),14,true));body.addView(g);
        LinearLayout lim=card();lim.addView(tv("정확도 게이트",15,true));lim.addView(tv(item.optString("accuracy_gate"),12,false));body.addView(lim);
        addSourceEvidence(item.optJSONObject("oem_source"));
        Button parts=btn("분해도 / 부품 위치 참고 (품번은 후순위)",false);
        parts.setOnClickListener(v->openParts("expert",item.optString("id")));
        body.addView(parts);
    }


    private void addSpecificityGate(JSONObject sg, JSONObject lim){
        if(sg==null)return;
        String st=sg.optString("status");
        LinearLayout c=card();
        if("CAUSE_SPECIFIC_PRE_TEARDOWN".equals(st)){
            c.addView(tv("원인별 마지막 분리시험",16,true));
            c.addView(tv(sg.optString("check"),14,true));
            if(sg.optString("confirm").length()>0)c.addView(tv("확정 · "+sg.optString("confirm"),12,false));
        }else if("SHARED_ASSEMBLY_BOUNDARY".equals(st)){
            c.addView(tv("분해 전 확정 한계",16,true));
            c.addView(tv("여기까지 확정 · "+sg.optString("assembly_boundary"),14,true));
            if(lim!=null){
                c.addView(tv(lim.optString("limit"),12,false));
                JSONArray a=lim.optJSONArray("post_teardown_checks");
                if(a!=null&&a.length()>0){c.addView(tv("분해 후 구분",13,true));for(int i=0;i<a.length();i++)c.addView(tv("• "+a.optString(i),12,false));}
            }
            c.addView(tv("세부 부품을 분해 전에 억지로 확정하지 않음",11,true));
        }else return;
        body.addView(c);
    }

    private void addQuickView(JSONObject q){
        if(q==null)return;
        JSONArray a=q.optJSONArray("steps");
        if(a==null||a.length()==0)return;
        LinearLayout c=card();
        c.addView(tv(q.optString("title","현장에서 먼저 할 3가지"),17,true));
        for(int i=0;i<a.length()&&i<3;i++) c.addView(tv((i+1)+". "+a.optString(i),15,i==0));
        JSONArray dn=q.optJSONArray("do_not");
        if(dn!=null&&dn.length()>0){c.addView(tv("바로 하지 말 것",13,true));for(int i=0;i<dn.length();i++)c.addView(tv("• "+dn.optString(i),12,false));}
        body.addView(c);
    }

    private void addComponentLocator(JSONObject l){
        if(l==null||l.optString("summary").length()==0)return;
        LinearLayout c=card();
        c.addView(tv("점검 위치 / 접근 위치",16,true));
        c.addView(tv(l.optString("summary"),14,true));
        JSONArray p=l.optJSONArray("oem_pages");
        if(p!=null&&p.length()>0)c.addView(tv("OEM 위치 근거 페이지 · "+p.toString(),12,false));
        body.addView(c);
    }

    private void addMeasurementPoints(JSONArray a)throws Exception{
        if(a==null||a.length()==0)return;
        LinearLayout c=card();c.addView(tv("측정점 / 비교점",16,true));
        for(int i=0;i<a.length();i++){
            JSONObject p=a.getJSONObject(i);
            c.addView(tv(p.optString("id")+" · "+p.optString("where"),14,true));
            c.addView(tv("측정: "+p.optString("check"),13,false));
            c.addView(tv("판정: "+p.optString("expected"),12,false));
        }
        body.addView(c);
    }

    private void addArrayCard(String title,JSONArray a,String prefix){
        if(a==null||a.length()==0)return;LinearLayout c=card();c.addView(tv(title,16,true));
        for(int i=0;i<a.length();i++)c.addView(tv(prefix+a.optString(i),14,false));body.addView(c);
    }

    private void addSimplifiedDiagram(JSONObject d)throws Exception{
        LinearLayout c=card();c.addView(tv("고장 전용 재작성 도면",16,true));
        c.addView(tv("원본 전체 회로를 복사하지 않고 이 고장을 가르는 경로만 표시",12,false));
        Bitmap bm=drawDiagram(d);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);iv.setOnClickListener(v->showBitmap(bm));c.addView(iv,new LinearLayout.LayoutParams(-1,dp(290)));body.addView(c);
    }

    private Bitmap drawDiagram(JSONObject d)throws Exception{
        JSONArray nodes=d.getJSONArray("nodes"),edges=d.getJSONArray("edges");int n=nodes.length();
        int w=1600,h=n<=6?650:820;Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);Canvas cv=new Canvas(b);cv.drawColor(Color.WHITE);Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(42);p.setTypeface(Typeface.DEFAULT_BOLD);cv.drawText(d.optString("title"),45,60,p);
        Map<String,RectF> box=new HashMap<>();
        int cols=n<=6?n:4;int rows=(n+cols-1)/cols;float margin=45,gap=24,top=135;float bw=(w-margin*2-gap*(cols-1))/cols;float bh=145;
        for(int i=0;i<n;i++){
            JSONObject x=nodes.getJSONObject(i);int row=i/cols,col=i%cols;float left=margin+col*(bw+gap),t=top+row*(bh+110);RectF r=new RectF(left,t,left+bw,t+bh);box.put(x.getString("id"),r);
        }
        p.setStrokeWidth(8);p.setColor(Color.rgb(95,110,120));
        for(int i=0;i<edges.length();i++){JSONObject e=edges.getJSONObject(i);RectF a=box.get(e.getString("from")),z=box.get(e.getString("to"));if(a==null||z==null)continue;float x1=a.right,y1=a.centerY(),x2=z.left,y2=z.centerY();if(z.left<a.left){x1=a.centerX();y1=a.bottom;x2=z.centerX();y2=z.top;}cv.drawLine(x1,y1,x2,y2,p);drawArrow(cv,p,x1,y1,x2,y2);}
        for(int i=0;i<n;i++){
            JSONObject x=nodes.getJSONObject(i);RectF r=box.get(x.getString("id"));p.setStyle(Paint.Style.FILL);p.setColor(x.optBoolean("highlight")?Color.rgb(255,237,195):Color.rgb(234,241,247));cv.drawRoundRect(r,22,22,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(x.optBoolean("highlight")?8:4);p.setColor(x.optBoolean("highlight")?Color.rgb(210,115,0):NAVY);cv.drawRoundRect(r,22,22,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(25,30,35));p.setTextSize(27);p.setTypeface(Typeface.DEFAULT_BOLD);drawCenterLines(cv,p,x.optString("label"),r.centerX(),r.centerY());
        }
        return b;
    }
    private void drawArrow(Canvas c,Paint p,float x1,float y1,float x2,float y2){double a=Math.atan2(y2-y1,x2-x1);float len=22;float ax=(float)(x2-len*Math.cos(a-0.55)),ay=(float)(y2-len*Math.sin(a-0.55));float bx=(float)(x2-len*Math.cos(a+0.55)),by=(float)(y2-len*Math.sin(a+0.55));c.drawLine(x2,y2,ax,ay,p);c.drawLine(x2,y2,bx,by,p);}
    private void drawCenterLines(Canvas c,Paint p,String text,float cx,float cy){String[] ls=text.split("\\n");float total=(ls.length-1)*34;for(int i=0;i<ls.length;i++){float tw=p.measureText(ls[i]);c.drawText(ls[i],cx-tw/2,cy-total/2+i*34,p);}}

    private void addSourceEvidence(JSONObject s){
        if(s==null)return;LinearLayout c=card();c.addView(tv("OEM 근거",16,true));c.addView(tv("정비지침서 · "+s.optString("section"),13,true));JSONArray p=s.optJSONArray("pdf_pages");if(p!=null)c.addView(tv("관련 PDF 페이지: "+p.toString(),12,false));JSONArray tests=s.optJSONArray("ui_tests");if(tests!=null&&tests.length()>0)c.addView(tv("연결된 OEM 시험: "+tests.toString(),12,false));
        if(p!=null){for(int i=0;i<p.length();i++){final int pg=p.optInt(i,-1);if(pg<0)continue;Button b=btn("OEM 원본 근거 보기 · p"+pg,false);b.setOnClickListener(v->showOemPage(pg));c.addView(b);}}
        body.addView(c);
    }
    private void showOemPage(int pg){
        Bitmap bm=loadPage(pg);if(bm==null){Toast.makeText(this,"해당 OEM 페이지 이미지가 APK에 없습니다.",Toast.LENGTH_SHORT).show();return;}showBitmap(bm);
    }
    private Bitmap loadPage(int pg){String[] names={String.format(Locale.US,"oem_pages/p%03d.jpg",pg),"oem_pages/p"+pg+".jpg",String.format(Locale.US,"oem_pages/p%03d.png",pg),"oem_pages/p"+pg+".png"};for(String n:names){try{InputStream is=getAssets().open(n);Bitmap b=BitmapFactory.decodeStream(is);is.close();if(b!=null)return b;}catch(Exception ignore){}}return null;}
    private void showBitmap(Bitmap bm){Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);sv.addView(iv);d.setContentView(sv);d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-1);}
    private void openParts(String domain,String ref){android.content.Intent it=new android.content.Intent(this,PartsReferenceActivity.class);it.putExtra("domain",domain);it.putExtra("ref_id",ref);startActivity(it);}
    private void fatal(String s){TextView t=new TextView(this);t.setText(s);t.setTextSize(16);t.setPadding(30,30,30,30);setContentView(t);}
}
