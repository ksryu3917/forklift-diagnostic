package com.ryu.forkliftdiagnostic;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.*;
import com.ryu.forkliftdiagnostic.core.ProjectState;
import com.ryu.forkliftdiagnostic.ui.VehicleSelectActivity;
import com.ryu.forkliftdiagnostic.ui.DiagnosisHomeActivity;
import com.ryu.forkliftdiagnostic.ui.StudyActivity;
import com.ryu.forkliftdiagnostic.ui.EvidenceViewerActivity;
import com.ryu.forkliftdiagnostic.ui.InfoActivity;

public class MainActivity extends Activity {
    private LinearLayout body;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        render();
    }

    @Override public void onResume() {
        super.onResume();
        render();
    }

    private TextView t(String s, int sp, boolean bold) {
        TextView v=new TextView(this); v.setText(s); v.setTextSize(sp);
        v.setTextColor(Color.rgb(25,30,35)); v.setPadding(20,14,20,14);
        if (bold) v.setTypeface(null,1); return v;
    }

    private Button button(String label) {
        Button b=new Button(this); b.setText(label); b.setAllCaps(false);
        b.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);
        return b;
    }

    private void render() {
        ScrollView sv=new ScrollView(this);
        body=new LinearLayout(this); body.setOrientation(LinearLayout.VERTICAL); body.setPadding(24,24,24,48);
        sv.addView(body); setContentView(sv);

        body.addView(t("지게차 정비 V20",24,true));
        try {
            ProjectState s=ProjectState.load(this);
            body.addView(t(s.release+" · "+s.state,15,true));
            body.addView(t("App "+s.versionName+"\nBranch "+s.sourceBranch+"\nGit "+s.gitSha+"\nSchema "+s.schemaVersion,12,false));
        } catch(Exception e) {
            body.addView(t("PROJECT_STATE 로딩 실패: "+e.getMessage(),13,true));
        }

        String m=getSharedPreferences("vehicle",0).getString("manufacturer","미선택");
        String model=getSharedPreferences("vehicle",0).getString("model","차량을 먼저 선택하세요");
        String spec=getSharedPreferences("vehicle",0).getString("spec","");
        body.addView(t("현재 차량\n"+m+" · "+model+(spec.isEmpty()?"":" · "+spec),16,true));
        Button vehicle=button("🚜 차량 선택");
        vehicle.setOnClickListener(v->startActivity(new Intent(this,VehicleSelectActivity.class)));
        body.addView(vehicle);

        Button diag=button("🔧 차량 진단");
        diag.setOnClickListener(v->startActivity(new Intent(this,DiagnosisHomeActivity.class)));
        body.addView(diag);

        Button study=button("📚 STUDY");
        study.setOnClickListener(v->startActivity(new Intent(this,StudyActivity.class)));
        body.addView(study);

        addInfo("📖 매뉴얼 라이브러리","manual"); addInfo("🔩 부품·가격·공임 (진단 뒤)","parts"); addInfo("🧾 정비 이력","history"); addInfo("🧠 내 현장 경험","field");
        Button ev=button("🔍 회로/근거 뷰어 · pinch/pan/double tap"); ev.setOnClickListener(v->startActivity(new Intent(this,EvidenceViewerActivity.class))); body.addView(ev);
        body.addView(t("앱/데이터 상태 · 단일 PROJECT_STATE · 오프라인",12,false));
    }
    private void addInfo(String label,String mode){Button b=button(label);b.setOnClickListener(v->{Intent i=new Intent(this,InfoActivity.class);i.putExtra("mode",mode);startActivity(i);});body.addView(b);}
}
