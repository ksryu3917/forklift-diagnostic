package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*; import android.content.Intent;
import org.json.*;
import android.text.Editable;
import android.text.TextWatcher;
import com.ryu.forkliftdiagnostic.core.GraphCatalog;

public class DiagnosisHomeActivity extends Activity {
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout body=Ui.page(this,"차량 진단 · 한 번에 한 점");
        String maker=getSharedPreferences("vehicle",0).getString("manufacturer","");
        String model=getSharedPreferences("vehicle",0).getString("model","");
        body.addView(Ui.text(this,"현재 차량: "+maker+" · "+model,18,true));
        if("DOOSAN".equals(maker) && model.matches("D(20|25|30|33)S(E)?-7"))
            add(body,"번호판등 순차 진단","e_license_terminal_stop.json");
        EditText search=new EditText(this); search.setHint("증상 또는 계통 검색"); body.addView(search);
        LinearLayout results=new LinearLayout(this);results.setOrientation(LinearLayout.VERTICAL);body.addView(results);
        try {
            JSONArray catalog=GraphCatalog.forVehicle(this,maker,model);
            show(results,catalog,"");
            search.addTextChangedListener(new TextWatcher(){
                public void beforeTextChanged(CharSequence s,int st,int c,int a){}
                public void onTextChanged(CharSequence s,int st,int before,int count){show(results,catalog,s.toString());}
                public void afterTextChanged(Editable e){}
            });
        } catch(Exception e){body.addView(Ui.text(this,"진단 목록 오류: "+e.getMessage(),16,true));}
    }
    private void show(LinearLayout body,JSONArray catalog,String query){
        body.removeAllViews();int found=0;
        for(int i=0;i<catalog.length();i++)try{
            JSONObject e=catalog.getJSONObject(i);
            if(!(e.getString("title")+e.getString("family")).toLowerCase(java.util.Locale.ROOT).contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
            add(body,e.getString("title")+(e.optBoolean("contract_complete")?"":" · OEM 근거 확인 필요"),e.getString("file"));found++;
        }catch(Exception ignored){}
        if(found==0)body.addView(Ui.text(this,"선택 차량에 일치하는 진단이 없습니다. 다른 차종 절차를 대신 표시하지 않습니다.",16,true));
    }
    private void add(LinearLayout body,String title,String file){Button b=Ui.button(this,title);b.setContentDescription("diag_"+file);b.setOnClickListener(v->{Intent i=new Intent(this,DiagnosticRunnerActivity.class);i.putExtra("graph",file);startActivity(i);});body.addView(b);}
}
