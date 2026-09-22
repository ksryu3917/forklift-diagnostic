package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.*;
import android.view.*;
import android.widget.LinearLayout;
import com.ryu.forkliftdiagnostic.core.AssetJson;
import org.json.*;
import java.io.*;
import java.security.MessageDigest;
import java.util.Locale;

/** Displays only registered, hash-checked evidence for the selected vehicle. */
public class EvidenceViewerActivity extends Activity {
    private Bitmap page;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout body=Ui.page(this,"OEM 회로/근거 뷰어");
        try {
            String id=getIntent().getStringExtra("evidence_id");
            if(id==null) id="DOOSAN_600123_00120_S4";
            JSONObject entry=AssetJson.read(this,"v20/evidence_registry.json").getJSONObject("entries").getJSONObject(id);
            if(!"VERIFIED".equals(entry.getString("status"))) throw new IOException("검토되지 않은 근거입니다");
            JSONObject scope=entry.getJSONObject("vehicle_scope");
            android.content.SharedPreferences vehicle=getSharedPreferences("vehicle",0);
            boolean modelMatches=false;
            JSONArray models=scope.getJSONArray("models");
            for(int i=0;i<models.length();i++) if(models.getString(i).equals(vehicle.getString("model",""))) modelMatches=true;
            if(!modelMatches || !scope.getString("manufacturer").equals(vehicle.getString("manufacturer","")))
                throw new IOException("선택 차량과 문서 적용 모델이 일치하지 않습니다");
            String asset=entry.getString("asset");
            if(!asset.startsWith("evidence/") || asset.contains("..")) throw new IOException("잘못된 근거 경로");
            ByteArrayOutputStream bytes=new ByteArrayOutputStream();
            try(InputStream input=getAssets().open("v20/"+asset)) {
                byte[] buffer=new byte[8192]; int count;
                while((count=input.read(buffer))!=-1) bytes.write(buffer,0,count);
            }
            byte[] data=bytes.toByteArray();
            StringBuilder digest=new StringBuilder();
            for(byte value:MessageDigest.getInstance("SHA-256").digest(data)) digest.append(String.format(Locale.US,"%02x",value&255));
            if(!digest.toString().equals(entry.getString("sha256"))) throw new IOException("문서 파일 무결성 확인 실패");
            page=BitmapFactory.decodeByteArray(data,0,data.length);
            if(page==null) throw new IOException("이미지를 읽을 수 없습니다");
            body.addView(Ui.text(this,entry.getString("locator"),14,true));
            body.addView(Ui.text(this,"원문 회로를 확대하여 확인하세요. 판독할 수 없는 핀 번호나 수치는 추정하지 마세요.",14,false));
            ZoomView view=new ZoomView();
            view.setContentDescription("zoom_pan_canvas");
            body.addView(view,new LinearLayout.LayoutParams(-1,(int)(420*getResources().getDisplayMetrics().density)));
        } catch(Exception error) {
            body.addView(Ui.text(this,"근거 표시 차단\n"+error.getMessage(),16,true));
        }
    }

    class ZoomView extends View {
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
        private float zoom=1,tx=0,ty=0,lastX,lastY;
        private final ScaleGestureDetector scaleDetector;
        private final GestureDetector gestureDetector;
        ZoomView() {
            super(EvidenceViewerActivity.this);
            scaleDetector=new ScaleGestureDetector(getContext(),new ScaleGestureDetector.SimpleOnScaleGestureListener(){
                @Override public boolean onScale(ScaleGestureDetector detector) {
                    setZoom(zoom*detector.getScaleFactor(),detector.getFocusX(),detector.getFocusY()); return true;
                }
            });
            gestureDetector=new GestureDetector(getContext(),new GestureDetector.SimpleOnGestureListener(){
                @Override public boolean onDown(MotionEvent event){return true;}
                @Override public boolean onDoubleTap(MotionEvent event){setZoom(zoom>1?1:3,event.getX(),event.getY());return true;}
            });
        }
        private float fit(){return Math.min((float)getWidth()/page.getWidth(),(float)getHeight()/page.getHeight());}
        private void clamp(){
            float xLimit=Math.max(0,(page.getWidth()*fit()*zoom-getWidth())/2);
            float yLimit=Math.max(0,(page.getHeight()*fit()*zoom-getHeight())/2);
            tx=Math.max(-xLimit,Math.min(xLimit,tx));ty=Math.max(-yLimit,Math.min(yLimit,ty));
        }
        private void setZoom(float value,float x,float y){
            float next=Math.max(1,Math.min(8,value)),ratio=next/zoom;
            tx=(x-getWidth()/2f)*(1-ratio)+tx*ratio;
            ty=(y-getHeight()/2f)*(1-ratio)+ty*ratio;
            zoom=next;clamp();invalidate();
        }
        @Override protected void onSizeChanged(int w,int h,int oldW,int oldH){clamp();}
        @Override protected void onDraw(Canvas canvas){
            super.onDraw(canvas);canvas.drawColor(Color.WHITE);
            canvas.save();canvas.translate(getWidth()/2f+tx,getHeight()/2f+ty);
            canvas.scale(fit()*zoom,fit()*zoom);
            canvas.drawBitmap(page,-page.getWidth()/2f,-page.getHeight()/2f,paint);canvas.restore();
        }
        @Override public boolean onTouchEvent(MotionEvent event){
            getParent().requestDisallowInterceptTouchEvent(true);
            scaleDetector.onTouchEvent(event);gestureDetector.onTouchEvent(event);
            int action=event.getActionMasked();
            if(action==MotionEvent.ACTION_DOWN){lastX=event.getX();lastY=event.getY();}
            else if(action==MotionEvent.ACTION_MOVE){
                if(event.getPointerCount()==1&&!scaleDetector.isInProgress()&&zoom>1){
                    tx+=event.getX()-lastX;ty+=event.getY()-lastY;clamp();invalidate();
                }
                lastX=event.getX();lastY=event.getY();
            } else if(action==MotionEvent.ACTION_POINTER_UP){
                int remaining=event.getActionIndex()==0?1:0;
                lastX=event.getX(remaining);lastY=event.getY(remaining);
            } else if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){
                getParent().requestDisallowInterceptTouchEvent(false);
                if(action==MotionEvent.ACTION_UP)performClick();
            }
            return true;
        }
        @Override public boolean performClick(){super.performClick();return true;}
    }
}
