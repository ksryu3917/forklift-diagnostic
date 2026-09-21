package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;
import org.json.*;
import com.ryu.forkliftdiagnostic.core.AssetJson;

public class StudyActivity extends Activity {
    private JSONObject catalog;
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        try {catalog=AssetJson.read(this,"v20/reference/study_catalog_v896.json").getJSONObject("data");home();}
        catch(Exception e){LinearLayout body=Ui.page(this,"STUDY");body.addView(Ui.text(this,e.getMessage(),16,true));}
    }
    private void home() throws Exception {
        LinearLayout body=Ui.page(this,"STUDY · 진단과 독립");
        body.addView(Ui.text(this,"전동·리치 A–Z · 공통 원리",21,true));
        body.addView(Ui.text(this,"아래는 공통 원리 학습입니다. 실제 차량의 수치·핀·탈거·브레이크 해제 절차는 해당 모델의 OEM 근거로 확인해야 합니다.",16,false));
        JSONArray lessons=catalog.getJSONArray("common_lessons");
        for(int i=0;i<lessons.length();i++){
            JSONObject lesson=lessons.getJSONObject(i);Button button=Ui.button(this,lesson.getString("title")+"\n"+lesson.optString("subtitle"));
            button.setOnClickListener(v->showLesson(lesson));body.addView(button);
        }
        TextView stop=Ui.text(this,"EXACT MODEL STOP · 모델별 작업 절차의 OEM 근거 연결은 아직 검증 중입니다.",16,true);
        stop.setContentDescription("study_scope_stop");body.addView(stop);
    }
    private void showLesson(JSONObject lesson) {
        LinearLayout body=Ui.page(this,lesson.optString("title"));
        add(body,"원리",lesson.optJSONArray("concept"));
        add(body,"구성 요소",lesson.optJSONArray("checkpoints"));
        add(body,"고장 유형",lesson.optJSONArray("common_faults"));
        add(body,"피해야 할 판단",lesson.optJSONArray("mistakes"));
        body.addView(Ui.text(this,"생각해 볼 사례\n"+lesson.optString("practice"),17,true));
        body.addView(Ui.text(this,"공통 원리 학습 · 특정 모델 작업 지시로 사용하지 마세요.",15,false));
        Button back=Ui.button(this,"STUDY 목록");back.setOnClickListener(v->{try{home();}catch(Exception e){Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show();}});body.addView(back);
    }
    private void add(LinearLayout body,String title,JSONArray list){
        if(list==null)return;body.addView(Ui.text(this,title,18,true));
        for(int i=0;i<list.length();i++)body.addView(Ui.text(this,"• "+list.optString(i),16,false));
    }
}
