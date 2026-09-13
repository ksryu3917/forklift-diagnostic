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

public class FieldLocationMapActivity extends Activity {
    private JSONObject data; private LinearLayout body; private final LinkedHashSet<String> focus=new LinkedHashSet<>();
    private final int NAVY=Color.rgb(16,38,58), BLUE=Color.rgb(17,117,214), ORANGE=Color.rgb(222,126,20), BG=Color.rgb(242,245,247);

    @Override public void onCreate(Bundle b){super.onCreate(b);try{
        data=new JSONObject(readAsset("field_location_map_v1.json"));
        resolveFocus(); render();
    }catch(Exception e){fatal("점검 위치맵 로딩 오류: "+e.getMessage());}}

    private String readAsset(String n)throws Exception{InputStream is=getAssets().open(n);ByteArrayOutputStream os=new ByteArrayOutputStream();byte[] b=new byte[8192];int r;while((r=is.read(b))>0)os.write(b,0,r);is.close();return os.toString(StandardCharsets.UTF_8.name());}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);} 
    private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}
    private TextView tv(String s,int sp,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));v.setPadding(dp(3),dp(5),dp(3),dp(5));if(bold)v.setTypeface(null,Typeface.BOLD);return v;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;}
    private Button btn(String s){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(13);b.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);b.setTextColor(Color.rgb(25,30,35));b.setBackground(bg(Color.rgb(231,236,240),10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(50));p.setMargins(0,dp(3),0,dp(3));b.setLayoutParams(p);return b;}

    private void resolveFocus()throws Exception{
        String ids=getIntent().getStringExtra("focus_ids");
        if(ids!=null&&!ids.trim().isEmpty())for(String x:ids.split(","))if(!x.trim().isEmpty())focus.add(x.trim());
        String gid=getIntent().getStringExtra("graph_id");
        if(focus.isEmpty()&&gid!=null){JSONArray a=data.getJSONObject("graph_focus").optJSONArray(gid);addIds(a);}
        String sys=getIntent().getStringExtra("system");
        if(focus.isEmpty()&&sys!=null){JSONArray a=data.getJSONObject("system_focus").optJSONArray(sys);addIds(a);}
    }
    private void addIds(JSONArray a){if(a==null)return;for(int i=0;i<a.length();i++)focus.add(a.optString(i));}

    private void render()throws Exception{
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(7),dp(8),dp(7));top.setBackgroundColor(NAVY);
        Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(50)));
        TextView title=tv("점검 위치맵",18,true);title.setTextColor(Color.WHITE);top.addView(title,new LinearLayout.LayoutParams(0,dp(50),1));root.addView(top);
        ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);root.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);

        LinearLayout intro=card();intro.addView(tv("정비사가 프로브/압력계를 어디에 가져갈지 먼저 찾는 화면",17,true));intro.addView(tv(data.optString("rule"),12,false));
        if(!focus.isEmpty())intro.addView(tv("이번 진단 관련 위치만 강조 · "+focus.size()+"개",13,true));body.addView(intro);

        Bitmap bm=drawTruck();LinearLayout mc=card();ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);iv.setOnClickListener(v->showBitmap(bm));mc.addView(iv,new LinearLayout.LayoutParams(-1,dp(390)));body.addView(mc);

        JSONObject zones=data.getJSONObject("zones");
        if(!focus.isEmpty()){
            body.addView(tv("이 고장에서 먼저 갈 위치",16,true));
            for(String id:focus)if(zones.has(id))addZoneCard(id,zones.getJSONObject(id),true);
            body.addView(tv("전체 차량 위치",16,true));
        }
        Iterator<String> it=zones.keys(); while(it.hasNext()){String id=it.next();if(focus.contains(id))continue;addZoneCard(id,zones.getJSONObject(id),false);}

        Button oem=btn("OEM 차량 위치차트 보기 · SB5120C05");oem.setOnClickListener(v->showLocationCharts());body.addView(oem);
    }

    private void addZoneCard(String id,JSONObject z,boolean primary){
        LinearLayout c=card();
        TextView h=tv((primary?"▶ ":"")+z.optString("label"),16,true);if(primary)h.setTextColor(ORANGE);c.addView(h);
        c.addView(tv("접근 · "+z.optString("access"),13,false));
        JSONArray tp=z.optJSONArray("test_points");if(tp!=null&&tp.length()>0){c.addView(tv("여기서 바로 볼 것",13,true));for(int i=0;i<tp.length();i++)c.addView(tv("• "+tp.optString(i),13,false));}
        c.addView(tv("위치 정확도 · "+z.optString("certainty"),11,false));
        JSONArray ev=z.optJSONArray("evidence");if(ev!=null){for(int i=0;i<ev.length();i++){final String asset=ev.optString(i);Button b=btn("OEM 위치/분해도 근거 보기 · "+asset.substring(asset.lastIndexOf('/')+1));b.setOnClickListener(v->showAsset(asset));c.addView(b);}}
        body.addView(c);
    }

    private Bitmap drawTruck()throws Exception{
        int w=1600,h=900;Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);c.drawColor(Color.WHITE);Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(42);p.setTypeface(Typeface.DEFAULT_BOLD);c.drawText("D20/25/30/33S-7 · 정비사용 위치맵",45,60,p);
        // simplified side/isometric forklift, intentionally non-dimensional
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(12);p.setColor(Color.rgb(90,105,115));
        RectF bodyR=new RectF(520,390,1320,690);c.drawRoundRect(bodyR,35,35,p);
        c.drawRect(710,190,1080,410,p); // guard/cab
        c.drawLine(360,150,360,680,p);c.drawLine(390,150,390,680,p);c.drawLine(360,160,250,730,p); // mast
        c.drawRect(180,690,430,735,p); // forks
        c.drawCircle(565,700,115,p);c.drawCircle(1235,700,105,p);
        c.drawLine(1080,410,1320,390,p);c.drawLine(1320,390,1430,530,p);c.drawLine(1430,530,1320,690,p); // counterweight
        p.setStyle(Paint.Style.FILL);
        JSONObject zones=data.getJSONObject("zones");Iterator<String> it=zones.keys();
        while(it.hasNext()){
            String id=it.next();JSONObject z=zones.getJSONObject(id);if(!focus.isEmpty()&&!focus.contains(id))continue;
            float x=(float)(z.optDouble("x",0.5)*w),y=(float)(z.optDouble("y",0.5)*h);
            p.setColor(focus.contains(id)?ORANGE:BLUE);c.drawCircle(x,y,22,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);c.drawCircle(x,y,34,p);p.setStyle(Paint.Style.FILL);
            p.setColor(Color.rgb(25,30,35));p.setTextSize(22);p.setTypeface(Typeface.DEFAULT_BOLD);drawLabel(c,p,z.optString("label"),x+42,y-6);
        }
        p.setColor(Color.DKGRAY);p.setTextSize(19);p.setTypeface(Typeface.DEFAULT);c.drawText("※ 빠른 접근용 재작성 위치맵. 치수/정확 장착은 각 OEM 근거 버튼에서 최종 확인.",45,860,p);return b;
    }
    private void drawLabel(Canvas c,Paint p,String s,float x,float y){String[] a=wrap(s,15);for(int i=0;i<a.length;i++)c.drawText(a[i],x,y+i*27,p);}
    private String[] wrap(String s,int n){if(s.length()<=n)return new String[]{s};ArrayList<String> a=new ArrayList<>();for(int i=0;i<s.length();i+=n)a.add(s.substring(i,Math.min(s.length(),i+n)));return a.toArray(new String[0]);}

    private void showLocationCharts(){final String[] a={"parts_views/parts_p1570.png","parts_views/parts_p1571.png","parts_views/parts_p1572.png"};showAssetList(a,0);}
    private void showAssetList(String[] a,int i){if(i>=a.length)return;showAsset(a[i]);}
    private void showAsset(String asset){try{InputStream is=getAssets().open(asset);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm!=null)showBitmap(bm);}catch(Exception e){Toast.makeText(this,"OEM 이미지를 열 수 없습니다: "+asset,Toast.LENGTH_SHORT).show();}}
    private void showBitmap(Bitmap bm){Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);sv.addView(iv);d.setContentView(sv);d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-1);}
    private void fatal(String s){TextView t=new TextView(this);t.setText(s);t.setTextSize(16);t.setPadding(30,30,30,30);setContentView(t);}
}
