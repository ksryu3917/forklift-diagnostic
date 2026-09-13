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

public class EngineSensorMapActivity extends Activity {
    private JSONObject data; private LinearLayout body; private final LinkedHashSet<String> focus=new LinkedHashSet<>();
    private final int NAVY=Color.rgb(16,38,58), BLUE=Color.rgb(17,117,214), BG=Color.rgb(242,245,247);
    @Override public void onCreate(Bundle b){super.onCreate(b);try{data=new JSONObject(readAsset("engine_sensor_map_d24_v1.json"));String f=getIntent().getStringExtra("focus_ids");if(f!=null)for(String x:f.split(","))if(!x.trim().isEmpty())focus.add(x.trim());render();}catch(Exception e){TextView t=new TextView(this);t.setText("센서 위치맵 오류: "+e);setContentView(t);}}
    private String readAsset(String n)throws Exception{InputStream is=getAssets().open(n);ByteArrayOutputStream os=new ByteArrayOutputStream();byte[] b=new byte[8192];int r;while((r=is.read(b))>0)os.write(b,0,r);is.close();return os.toString(StandardCharsets.UTF_8.name());}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);} private GradientDrawable bg(int c,int r){GradientDrawable g=new GradientDrawable();g.setColor(c);g.setCornerRadius(dp(r));return g;}
    private TextView tv(String s,int sp,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(Color.rgb(25,30,35));v.setPadding(dp(3),dp(5),dp(3),dp(5));if(bold)v.setTypeface(null,Typeface.BOLD);return v;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(14),dp(12),dp(14),dp(12));c.setBackground(bg(Color.WHITE,12));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,0,0,dp(10));c.setLayoutParams(p);return c;}
    private Button btn(String s){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(13);b.setTextColor(Color.rgb(25,30,35));b.setBackground(bg(Color.rgb(231,236,240),10));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(48));p.setMargins(0,dp(3),0,dp(3));b.setLayoutParams(p);return b;}
    private void render()throws Exception{
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(7),dp(8),dp(7));top.setBackgroundColor(NAVY);Button back=new Button(this);back.setText("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());top.addView(back,new LinearLayout.LayoutParams(dp(48),dp(50)));TextView title=tv("D24NAP 센서 위치맵",18,true);title.setTextColor(Color.WHITE);top.addView(title,new LinearLayout.LayoutParams(0,dp(50),1));root.addView(top);
        ScrollView sv=new ScrollView(this);body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(10),dp(10),dp(10),dp(30));sv.addView(body);root.addView(sv,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);
        LinearLayout intro=card();intro.addView(tv("정비사용 빠른 위치 찾기",17,true));intro.addView(tv("3D 모델 대신 OEM §12-3 번호도면 + SB5120C05 스위치&센서 부품도를 대조해 엔진 구역을 아이소메트릭 형태로 재작성합니다. 치수도면이 아니며, 최종 위치는 OEM callout/부품도로 교차확인합니다.",12,false));body.addView(intro);
        Button pb=btn("◎ OEM 스위치&센서 부품도 확인 · SB5120 p211");pb.setOnClickListener(v->showAsset("parts_views/parts_p211.png"));body.addView(pb);
        Bitmap bm=drawIso();LinearLayout map=card();ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);map.addView(iv,new LinearLayout.LayoutParams(-1,dp(360)));body.addView(map);
        JSONArray a=data.getJSONArray("sensors");
        if(!focus.isEmpty()){body.addView(tv("이 진단에서 먼저 볼 센서/액추에이터",16,true));for(String id:focus){for(int i=0;i<a.length();i++){JSONObject s=a.getJSONObject(i);if(id.equals(s.optString("id"))){Button b=btn("▶ "+(s.isNull("callout")?"":"#"+s.optInt("callout")+" · ")+s.optString("kr"));b.setOnClickListener(v->showSensor(s));body.addView(b);break;}}}body.addView(tv("전체 D24 위치",16,true));}
        for(int i=0;i<a.length();i++){JSONObject s=a.getJSONObject(i);Button b=btn((s.isNull("callout")?"·":"#"+s.optInt("callout")+" · ")+s.optString("kr"));b.setOnClickListener(v->showSensor(s));body.addView(b);}
    }
    private Bitmap drawIso()throws Exception{
        int w=1600,h=920;Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);c.drawColor(Color.WHITE);Paint p=new Paint(1);
        p.setColor(NAVY);p.setTextSize(42);p.setTypeface(Typeface.DEFAULT_BOLD);c.drawText("D24NAP · 앱용 아이소메트릭 센서 구역맵",45,58,p);
        // pseudo-isometric engine block
        Path top=new Path();top.moveTo(390,250);top.lineTo(1010,155);top.lineTo(1320,330);top.lineTo(690,430);top.close();p.setColor(Color.rgb(222,230,235));c.drawPath(top,p);Path side=new Path();side.moveTo(690,430);side.lineTo(1320,330);side.lineTo(1320,690);side.lineTo(690,800);side.close();p.setColor(Color.rgb(204,216,225));c.drawPath(side,p);Path front=new Path();front.moveTo(390,250);front.lineTo(690,430);front.lineTo(690,800);front.lineTo(390,610);front.close();p.setColor(Color.rgb(188,203,214));c.drawPath(front,p);
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(NAVY);c.drawPath(top,p);c.drawPath(side,p);c.drawPath(front,p);p.setStyle(Paint.Style.FILL);
        JSONArray zones=data.getJSONArray("views").getJSONObject(0).getJSONArray("zones");
        Map<String,List<JSONObject>> by=new LinkedHashMap<>();JSONArray sensors=data.getJSONArray("sensors");for(int i=0;i<sensors.length();i++){JSONObject s=sensors.getJSONObject(i);by.computeIfAbsent(s.optString("zone"),k->new ArrayList<>()).add(s);}
        for(int i=0;i<zones.length();i++){JSONObject z=zones.getJSONObject(i);float x=(float)(z.getDouble("x")*w),y=(float)(z.getDouble("y")*h);List<JSONObject> ss=by.get(z.getString("id"));if(ss==null)continue;p.setColor(BLUE);c.drawCircle(x,y,18,p);p.setColor(Color.rgb(25,30,35));p.setTextSize(22);p.setTypeface(Typeface.DEFAULT_BOLD);String label=z.optString("label")+"\n"+shortNames(ss);drawLines(c,p,label,x+25,y-5);}
        p.setTextSize(20);p.setTypeface(Typeface.DEFAULT);p.setColor(Color.DKGRAY);c.drawText("※ 위치는 빠른 탐색용 zone. OEM §12-3 callout 번호와 실제 엔진 사양으로 최종 확인.",45,875,p);return b;
    }
    private String shortNames(List<JSONObject> ss){StringBuilder x=new StringBuilder();for(int i=0;i<ss.size();i++){if(i>0)x.append("/");x.append(ss.get(i).optString("id"));}return x.toString();}
    private void drawLines(Canvas c,Paint p,String s,float x,float y){String[] a=s.split("\\n");for(int i=0;i<a.length;i++)c.drawText(a[i],x,y+i*28,p);}

    private void showAsset(String asset){try{InputStream is=getAssets().open(asset);Bitmap bm=BitmapFactory.decodeStream(is);is.close();if(bm==null)return;Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);sv.addView(iv);d.setContentView(sv);d.show();if(d.getWindow()!=null)d.getWindow().setLayout(-1,-1);}catch(Exception e){Toast.makeText(this,"부품도 이미지를 열 수 없습니다.",Toast.LENGTH_SHORT).show();}}
    private void showSensor(JSONObject s){Dialog d=new Dialog(this);ScrollView sv=new ScrollView(this);LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(18),dp(18),dp(18),dp(22));c.addView(tv((s.isNull("callout")?"":"OEM #"+s.optInt("callout")+" · ")+s.optString("kr"),19,true));c.addView(tv(s.optString("name"),13,false));c.addView(tv("위치 · "+s.optString("location"),15,true));c.addView(tv("핀/신호 · "+s.optString("pins"),13,false));c.addView(tv("근거 · "+s.optString("oem_ref"),12,false));
        String exactView=s.optString("parts_location_view");
        if(exactView!=null && !exactView.isEmpty()){Button eb=btn("◎ 이 센서가 표시된 OEM 엔진 방향만 보기");eb.setOnClickListener(v->showAsset(exactView));c.addView(eb);if(s.optString("parts_location_note").length()>0)c.addView(tv(s.optString("parts_location_note"),11,false));}
        Button pb=btn("OEM 전체 스위치&센서 부품도 보기");pb.setOnClickListener(v->showAsset("parts_views/parts_p211.png"));c.addView(pb);
        JSONObject pr=s.optJSONObject("parts");if(pr!=null){c.addView(tv("참고 부품정보 · 주문은 차대번호 기준 부품점 확인",13,true));JSONArray pn=pr.optJSONArray("part_numbers");if(pn!=null&&pn.length()>0){StringBuilder z=new StringBuilder();for(int i=0;i<pn.length();i++){if(i>0)z.append(" / ");z.append(pn.optString(i));}c.addView(tv("참고 품번 · "+z,12,false));}if(pr.optString("name").length()>0)c.addView(tv("명칭 · "+pr.optString("name"),12,false));if(pr.optString("note").length()>0)c.addView(tv("주의 · "+pr.optString("note"),11,false));}
        c.addView(tv("주의 · 이 화면의 엔진 형상은 위치 탐색용 재작성 그림이며 치수/정비분해도 자체가 아닙니다.",11,false));sv.addView(c);d.setContentView(sv);d.show();Window w=d.getWindow();if(w!=null)w.setLayout(-1,-2);}
}
