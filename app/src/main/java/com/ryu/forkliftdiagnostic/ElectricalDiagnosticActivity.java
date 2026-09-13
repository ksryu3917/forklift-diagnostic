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

public class ElectricalDiagnosticActivity extends Activity {
    private LinearLayout body;
    private JSONObject data;
    private final int NAVY=Color.rgb(16,38,58), BLUE=Color.rgb(17,117,214), BG=Color.rgb(242,245,247);

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        try{
            data=new JSONObject(readAsset("electrical_diag_v1.json"));
            String graph=getIntent().getStringExtra("graph_id");
            if(graph!=null && graph.length()>0) openItem(graph); else home();
        }
        catch(Exception e){ fatal("전장 진단 DB 로딩 오류: "+e.getMessage()); }
    }

    private String readAsset(String name)throws Exception{
        InputStream is=getAssets().open(name); ByteArrayOutputStream os=new ByteArrayOutputStream();
        byte[] buf=new byte[8192]; int n; while((n=is.read(buf))>0)os.write(buf,0,n); is.close();
        return os.toString(StandardCharsets.UTF_8.name());
    }
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);}
    private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}
    private TextView tv(String s,int sp,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));v.setPadding(dp(3),dp(5),dp(3),dp(5));if(bold)v.setTypeface(null,1);return v;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;}
    private Button btn(String s,boolean primary){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(15);b.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);b.setTextColor(primary?Color.WHITE:Color.rgb(25,30,35));b.setBackground(bg(primary?BLUE:Color.rgb(231,236,240),10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(54));p.setMargins(0,dp(4),0,dp(4));b.setLayoutParams(p);return b;}

    private void base(String title){
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(10),dp(8),dp(10),dp(8));top.setBackgroundColor(NAVY);
        Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->onBackPressed());top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(52)));
        TextView t=tv(title,18,true);t.setTextColor(Color.WHITE);top.addView(t,new LinearLayout.LayoutParams(0,dp(52),1));
        Button h=new Button(this);h.setText("⌂");h.setTextSize(24);h.setTextColor(Color.WHITE);h.setBackgroundColor(Color.TRANSPARENT);h.setOnClickListener(v->home());top.addView(h,new LinearLayout.LayoutParams(dp(52),dp(52)));
        ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);
        root.addView(top);root.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);
    }

    private void home(){
        try{
            base("전기 / 차체전장 진단");
            JSONObject src=data.getJSONObject("source");
            LinearLayout s=card();s.addView(tv("OEM 회로 기반",17,true));s.addView(tv(src.optString("schematic_id")+" · "+src.optString("scope","D24 TIER-4"),13,false));s.addView(tv("회로도는 부록 이미지가 아니라 진단 데이터로 사용합니다.",14,true));s.addView(tv(src.optString("rule"),12,false));body.addView(s);
            JSONArray cat=data.getJSONArray("catalog"); String group="";
            String query=getIntent().getStringExtra("query");
            if(query==null)query=""; query=query.trim().toLowerCase(Locale.ROOT);
            int shown=0;
            for(int i=0;i<cat.length();i++){
                JSONObject x=cat.getJSONObject(i);
                String hay=(x.optString("title")+" "+x.optString("group")+" "+x.optString("id")).toLowerCase(Locale.ROOT);
                if(query.length()>0 && !hay.contains(query))continue;
                String g=x.optString("group");
                if(!g.equals(group)){group=g;body.addView(tv(group,16,true));}
                String label=x.optString("title")+"  ·  "+x.optString("sheet")+" / "+x.optString("grid");
                Button b=btn(label,"field_graph".equals(x.optString("ready")));final String id=x.getString("id");b.setOnClickListener(v->openItem(id));body.addView(b);shown++;
            }
            if(shown==0 && query.length()>0)body.addView(tv("전장 진단에서 일치하는 항목이 없습니다.",14,true));
        }catch(Exception e){fatal(e.toString());}
    }

    private JSONObject catalogItem(String id)throws Exception{JSONArray a=data.getJSONArray("catalog");for(int i=0;i<a.length();i++){JSONObject x=a.getJSONObject(i);if(id.equals(x.optString("id")))return x;}return null;}
    private void openItem(String id){
        try{
            JSONObject graphs=data.optJSONObject("graphs");
            if(graphs!=null && graphs.has(id)){JSONObject g=graphs.getJSONObject(id);renderGraph(id,g.getString("start"));return;}
            showMapped(id);
        }catch(Exception e){fatal(e.toString());}
    }

    private void sourceCard(JSONObject item){
        try{
            LinearLayout c=card();c.addView(tv("회로 위치",16,true));c.addView(tv("도면 600123-00120 · "+item.optString("sheet")+" · Grid "+item.optString("grid"),14,true));
            String ready=item.optString("ready");
            if("mapped".equals(ready))c.addView(tv("현재는 회로 위치가 정규화된 단계입니다. 정확한 핀/퓨즈 표기는 원본에서 확인된 항목만 표시합니다.",12,false));
            body.addView(c);
        }catch(Exception ignore){}
    }

    private void showMapped(String id)throws Exception{
        JSONObject item=catalogItem(id);base(item.optString("title"));sourceCard(item);
        Button loc=btn("◎ 이 고장 점검 위치맵",true); loc.setOnClickListener(v->{android.content.Intent it=new android.content.Intent(this,FieldLocationMapActivity.class);it.putExtra("graph_id",id);startActivity(it);}); body.addView(loc);
        if("E_FR_CONTROL".equals(id)){
            JSONObject p=data.getJSONObject("circuits").getJSONObject("FR_CONTROL").getJSONObject("oem_procedure");
            LinearLayout c=card();c.addView(tv("OEM 확인값",16,true));
            c.addView(tv("• 퓨즈: "+p.optString("fuse"),14,false));
            c.addView(tv("• 공통 접점: "+p.optString("switch_common"),14,false));
            c.addView(tv("• 전진 접점: "+p.optString("forward"),14,false));
            c.addView(tv("• 후진 접점: "+p.optString("reverse"),14,false));
            c.addView(tv("• 솔레노이드 플런저: "+p.optString("solenoid_plunger"),14,false));body.addView(c);
        }
        LinearLayout d=card();d.addView(tv("현장 기본 추적 순서",16,true));JSONArray a=data.getJSONObject("mapped_diagnostic_rules").getJSONArray("default_electrical_chain");addArray(d,a,"① ");d.addView(tv("주의 · "+data.getJSONObject("mapped_diagnostic_rules").optString("no_guess_rule"),12,true));body.addView(d);
        LinearLayout wait=card();wait.addView(tv("상태",15,true));wait.addView(tv("회로 sheet/grid 연결 완료. 개별 커넥터 핀·퓨즈 cavity까지 원본에서 검증되지 않은 값은 표시하지 않습니다.",13,false));body.addView(wait);
    }

    private void renderGraph(String gid,String nodeId)throws Exception{
        JSONObject g=data.getJSONObject("graphs").getJSONObject(gid),n=g.getJSONObject("nodes").getJSONObject(nodeId);
        base(g.optString("title"));
        JSONObject item=catalogItem(gid);if(item!=null)sourceCard(item);
        Button loc=btn("◎ 이 고장 점검 위치맵",true); loc.setOnClickListener(v->{android.content.Intent it=new android.content.Intent(this,FieldLocationMapActivity.class);it.putExtra("graph_id",gid);startActivity(it);}); body.addView(loc);
        if(hasTestPointGraph(gid)){
            Button tp=btn("⊙ 프로브 / 측정포인트 바로보기",true);
            tp.setOnClickListener(v->{android.content.Intent it=new android.content.Intent(this,TestPointLocatorActivity.class);it.putExtra("graph_id",gid);startActivity(it);});
            body.addView(tp);
        }
        if(g.optString("engine_sensor_map").length()>0){ Button sm=btn("D24 센서 위치 / 핀맵",false); sm.setOnClickListener(v->startActivity(new android.content.Intent(this,EngineSensorMapActivity.class))); body.addView(sm); }
        JSONObject cir=data.getJSONObject("circuits").optJSONObject(g.optString("circuit"));
        if(cir!=null)addCircuitEvidence(cir,nodeId);
        LinearLayout h=card();h.addView(tv(n.optString("title"),18,true));
        if(n.optString("question").length()>0)h.addView(tv(n.optString("question"),16,true));
        addSection(h,"현장 확인 방법",n.optJSONArray("field_method"),"① ");
        addSection(h,"공구",n.optJSONArray("tools"),"• ");body.addView(h);
        if("result".equals(n.optString("type"))){showResult(n);Button pr=btn("분해도 / 부품 위치 참고 (품번은 후순위)",false);pr.setOnClickListener(v->openParts("electrical",gid));body.addView(pr);return;}
        JSONArray ch=n.optJSONArray("choices");if(ch!=null)for(int i=0;i<ch.length();i++){
            JSONObject o=ch.getJSONObject(i);Button b=btn(o.optString("label"),i==0);final String next=o.optString("next");b.setOnClickListener(v->{try{renderGraph(gid,next);}catch(Exception e){fatal(e.toString());}});body.addView(b);
        }
    }

    private void addCircuitEvidence(JSONObject c,String nodeId){
        try{
            JSONObject sd=c.optJSONObject("simplified_diagram");
            if(sd!=null){
                LinearLayout d=card();
                d.addView(tv("고장 전용 재작성 회로",16,true));
                d.addView(tv("원본 전체 회로를 복사하지 않고 이 증상을 가르는 전원·제어·부하·접지·측정점만 표시",12,false));
                Bitmap bm=drawSimplifiedCircuit(sd);
                ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
                iv.setOnClickListener(v->showBitmap(bm));
                d.addView(iv,new LinearLayout.LayoutParams(-1,dp(320)));
                JSONArray mp=sd.optJSONArray("measure_points");
                if(mp!=null&&mp.length()>0){d.addView(tv("측정점",14,true));addArray(d,mp,"• ");}
                body.addView(d);
            }

            JSONArray verified=c.optJSONArray("verified_protection_control");
            if(verified!=null && verified.length()>0){
                LinearLayout vp=card();
                vp.addView(tv("확정 퓨즈 / 릴레이 / 전원",16,true));
                addArray(vp,verified,"✓ ");
                if(c.optString("fuse_reference").length()>0) vp.addView(tv("퓨즈 · "+c.optString("fuse_reference"),13,true));
                if(c.optString("relay_reference").length()>0) vp.addView(tv("릴레이 · "+c.optString("relay_reference"),13,true));
                if(c.optString("power_reference").length()>0) vp.addView(tv("전원 · "+c.optString("power_reference"),13,true));
                vp.addView(tv("확정값만 표시합니다. 미확정 숫자핀은 아래에 별도로 표시합니다.",11,false));
                body.addView(vp);
            }

            JSONArray specs=c.optJSONArray("verified_test_specs");
            if(specs!=null && specs.length()>0){
                LinearLayout sp=card();
                sp.addView(tv("OEM 확인 시험값 / 부하사양",16,true));
                sp.addView(tv("진단에 직접 쓰는 확인값만 먼저 표시합니다. 구성품 사양을 합격 임계값으로 오용하지 않습니다.",11,false));
                for(int i=0;i<specs.length();i++){
                    JSONObject x=specs.optJSONObject(i); if(x==null) continue;
                    sp.addView(tv("✓ "+x.optString("label")+" · "+x.optString("value"),13,true));
                    if(x.optString("source").length()>0) sp.addView(tv("   근거 · "+x.optString("source"),11,false));
                }
                body.addView(sp);
            }

            LinearLayout m=card();
            m.addView(tv("OEM 회로 근거",16,true));
            m.addView(tv("도면 "+c.optString("schematic_id")+" · "+c.optString("sheet")+" · Grid "+c.optString("grid"),13,true));
            JSONArray comps=c.optJSONArray("components");
            if(comps!=null){for(int i=0;i<comps.length();i++){
                JSONObject x=comps.getJSONObject(i);
                m.addView(tv("• "+x.optString("name")+" · "+x.optString("grid")+(x.optString("connector").length()>0?" · "+x.optString("connector"):""),13,false));
            }}
            JSONArray imgs=c.optJSONArray("images");
            if(imgs!=null&&imgs.length()>0){
                m.addView(tv("원본은 판정 근거 확인용입니다. 기본 화면에는 재작성 회로만 표시합니다.",12,false));
                for(int i=0;i<imgs.length();i++){
                    final String asset=imgs.optString(i);
                    Button b=btn("OEM 원본 근거 보기 · "+(i+1),false);
                    b.setOnClickListener(v->showAssetImage(asset));
                    m.addView(b);
                }
            }
            body.addView(m);

            if(c.optJSONArray("unverified")!=null){
                LinearLayout u=card();u.addView(tv("OEM 미확정 · 임의값 금지",15,true));
                addArray(u,c.optJSONArray("unverified"),"• ");body.addView(u);
            }
        }catch(Exception ignore){}
    }

    private Bitmap drawSimplifiedCircuit(JSONObject d)throws Exception{
        JSONArray nodes=d.getJSONArray("nodes"),edges=d.getJSONArray("edges");
        int n=nodes.length(),w=1600,h=n<=6?650:850;
        Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);Canvas cv=new Canvas(b);cv.drawColor(Color.WHITE);Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(42);p.setTypeface(Typeface.DEFAULT_BOLD);cv.drawText(d.optString("title","진단용 재작성 회로"),45,60,p);
        Map<String,RectF> box=new HashMap<>();int cols=n<=6?n:4,rows=(n+cols-1)/cols;float margin=45,gap=24,top=135,bw=(w-margin*2-gap*(cols-1))/cols,bh=145;
        for(int i=0;i<n;i++){JSONObject x=nodes.getJSONObject(i);int row=i/cols,col=i%cols;float left=margin+col*(bw+gap),t=top+row*(bh+110);box.put(x.getString("id"),new RectF(left,t,left+bw,t+bh));}
        p.setStrokeWidth(8);p.setColor(Color.rgb(95,110,120));
        for(int i=0;i<edges.length();i++){JSONObject e=edges.getJSONObject(i);RectF a=box.get(e.getString("from")),z=box.get(e.getString("to"));if(a==null||z==null)continue;float x1=a.right,y1=a.centerY(),x2=z.left,y2=z.centerY();if(z.left<=a.left){x1=a.centerX();y1=a.bottom;x2=z.centerX();y2=z.top;}cv.drawLine(x1,y1,x2,y2,p);drawCircuitArrow(cv,p,x1,y1,x2,y2);}
        for(int i=0;i<n;i++){
            JSONObject x=nodes.getJSONObject(i);RectF r=box.get(x.getString("id"));boolean verified=x.optBoolean("verified",false);
            p.setStyle(Paint.Style.FILL);p.setColor(verified?Color.rgb(234,241,247):Color.rgb(255,244,214));cv.drawRoundRect(r,22,22,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(verified?4:7);p.setColor(verified?NAVY:Color.rgb(190,110,0));cv.drawRoundRect(r,22,22,p);
            p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(25,30,35));p.setTextSize(26);p.setTypeface(Typeface.DEFAULT_BOLD);drawCircuitText(cv,p,x.optString("label"),r.centerX(),r.centerY());
        }
        return b;
    }
    private void drawCircuitArrow(Canvas c,Paint p,float x1,float y1,float x2,float y2){double a=Math.atan2(y2-y1,x2-x1);float len=22;float ax=(float)(x2-len*Math.cos(a-0.55)),ay=(float)(y2-len*Math.sin(a-0.55));float bx=(float)(x2-len*Math.cos(a+0.55)),by=(float)(y2-len*Math.sin(a+0.55));c.drawLine(x2,y2,ax,ay,p);c.drawLine(x2,y2,bx,by,p);}
    private void drawCircuitText(Canvas c,Paint p,String text,float cx,float cy){String[] ls=text.split("\\n");float total=(ls.length-1)*34;for(int i=0;i<ls.length;i++){float tw=p.measureText(ls[i]);c.drawText(ls[i],cx-tw/2,cy-total/2+i*34,p);}}
    private void showAssetImage(String asset){try{InputStream is=getAssets().open(asset);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm!=null)showBitmap(bm);}catch(Exception e){Toast.makeText(this,"OEM 원본 이미지를 열 수 없습니다.",Toast.LENGTH_SHORT).show();}}

    private void addAssetImage(String asset){
        try{InputStream is=getAssets().open(asset);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm==null)return;LinearLayout c=card();c.addView(tv("회로 확대 · "+asset.substring(asset.lastIndexOf('/')+1),13,true));ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);iv.setOnClickListener(v->showBitmap(bm));c.addView(iv,new LinearLayout.LayoutParams(-1,dp(280)));body.addView(c);}catch(Exception ignore){}
    }
    private void showBitmap(Bitmap bm){Dialog d=new Dialog(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);d.setContentView(iv);Window w=d.getWindow();if(w!=null)w.setLayout(-1,-1);d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-1);}
    private void showResult(JSONObject n){
        LinearLayout r=card();r.addView(tv("판정",16,true));r.addView(tv(n.optString("result"),17,true));body.addView(r);
        addResult("현장 공구",n.optJSONArray("field_tools"));addResult("현장 확인 / 재현 시험",n.optJSONArray("field_test"));addResult("먼저 배제한 원인",n.optJSONArray("rule_out"));addResult("확정 조건",n.optJSONArray("confirm_if"));
        if(n.optString("disassembly_gate").length()>0){LinearLayout c=card();c.addView(tv("분해/교환 조건",16,true));c.addView(tv(n.optString("disassembly_gate"),14,true));body.addView(c);}
        if(n.optString("oem_limit_note").length()>0){LinearLayout c=card();c.addView(tv("OEM 값 제한",15,true));c.addView(tv(n.optString("oem_limit_note"),12,false));body.addView(c);}
    }
    private void addResult(String title,JSONArray a){if(a==null||a.length()==0)return;LinearLayout c=card();c.addView(tv(title,16,true));addArray(c,a,"• ");body.addView(c);}
    private void addSection(LinearLayout c,String title,JSONArray a,String prefix){if(a==null||a.length()==0)return;c.addView(tv(title,15,true));addArray(c,a,prefix);}
    private void addArray(LinearLayout c,JSONArray a,String prefix){if(a==null)return;for(int i=0;i<a.length();i++)c.addView(tv(prefix+a.optString(i),14,false));}
    private boolean hasTestPointGraph(String gid){
        try{JSONObject t=new JSONObject(readAsset("test_point_locator_v1.json"));return t.getJSONObject("graph_map").has(gid);}
        catch(Exception e){return false;}
    }
    private void openParts(String domain,String ref){android.content.Intent it=new android.content.Intent(this,PartsReferenceActivity.class);it.putExtra("domain",domain);it.putExtra("ref_id",ref);startActivity(it);}
    private void fatal(String s){TextView t=new TextView(this);t.setText(s);t.setTextSize(16);t.setPadding(30,30,30,30);setContentView(t);}
}
