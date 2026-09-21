package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;

public class VehicleSelectActivity extends Activity {
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout body=Ui.page(this,"차량 선택"); add(body,"DOOSAN","D25S-7","D24 디젤"); add(body,"DOOSAN","B25S-7","48V 전동"); add(body,"TOYOTA","8FBR","전동 리치 · exact model procedure 미정규화"); add(body,"OTHER","UNKNOWN MODEL","절차/수치 차단");
    }
    private void add(LinearLayout body,String maker,String model,String spec){Button b=Ui.button(this,maker+" · "+model+"\n"+spec);b.setContentDescription("vehicle_"+maker+"_"+model);b.setOnClickListener(v->{getSharedPreferences("vehicle",0).edit().clear().putString("manufacturer",maker).putString("model",model).putString("spec",spec).putString("engine",spec.contains("D24")?"D24":"").apply();Toast.makeText(this,"현재 차량: "+maker+" "+model,Toast.LENGTH_SHORT).show();finish();});body.addView(b);}
}
