package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;
import org.json.*;
import com.ryu.forkliftdiagnostic.core.AssetJson;
import com.ryu.forkliftdiagnostic.engine.DiagnosticEngine;

public class DiagnosticRunnerActivity extends Activity {
    private LinearLayout body;
    private DiagnosticEngine engine;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        try {
            String file=getIntent().getStringExtra("graph");
            if(file==null || file.contains("..")) throw new IllegalArgumentException("Invalid graph path");
            JSONObject graph=AssetJson.read(this,"v20/"+(file.startsWith("migrated/")?file:"diagnostics/"+file));
            android.content.SharedPreferences prefs=getSharedPreferences("vehicle",0);
            JSONObject vehicle=new JSONObject();
            for(String key:new String[]{"manufacturer","model","engine","powertrain","voltage","variant"})
                vehicle.put(key,prefs.getString(key,""));
            JSONObject refs=AssetJson.read(this,"v20/evidence_registry.json").getJSONObject("entries");
            engine=new DiagnosticEngine(graph,vehicle,refs);
            body=Ui.page(this,graph.getString("title"));
            render();
        } catch(Exception error) {
            body=Ui.page(this,"진단 진행 차단");
            body.addView(Ui.text(this,"선택 차량과 근거·안전조건이 확인되지 않아 절차를 표시하지 않습니다.\n"+error.getMessage(),16,true));
        }
    }

    private void render() throws Exception {
        while(body.getChildCount()>1) body.removeViewAt(1);
        body.post(()->((ScrollView)body.getParent()).smoothScrollTo(0,0));
        JSONObject node=engine.currentNode();
        TextView title=Ui.text(this,node.getString("title"),21,true);
        title.setContentDescription("node_title");body.addView(title);
        String[][] fields={{"first_observation","지금 확인할 것"},{"test_location","위치"},
            {"tool","공구"},{"safety_preconditions","안전조건"},{"operating_condition","작동조건"},
            {"measurement_or_action","측정/행동"},{"expected_basis","판정 근거"},{"evidence_refs","근거"}};
        for(String[] f:fields)add(f[1],node.opt(f[0]));
        JSONArray evidenceIds=node.optJSONArray("evidence_refs");
        if(evidenceIds!=null)for(int i=0;i<evidenceIds.length();i++){
            String ref=evidenceIds.getString(i);Button evidence=Ui.button(this,"근거 보기 · "+ref);
            evidence.setOnClickListener(v->{android.content.Intent intent=new android.content.Intent(this,EvidenceViewerActivity.class);intent.putExtra("evidence_id",ref);startActivity(intent);});body.addView(evidence);
        }
        if(engine.isTerminal()) {
            for(String[] f:new String[][]{{"rule_out","배제된 것"},{"confirm_if","확정 조건"},
                {"teardown_gate","분해 게이트"},{"next_action","다음 조치"},{"do_not","하지 말 것"}})
                add(f[1],node.opt(f[0]));
            TextView stop=Ui.text(this,"TERMINAL STOP · 확인된 범위 이외의 분해·교환 금지",16,true);
            stop.setContentDescription("terminal_stop");body.addView(stop);return;
        }
        CheckBox safe=new CheckBox(this);safe.setText("위 안전조건과 시험조건을 현장에서 확인했습니다");
        safe.setOnCheckedChangeListener((button,checked)->{
            try {engine.acknowledgeSafety(checked);}catch(Exception e){safe.setChecked(false);}
        });body.addView(safe);
        if("measure".equals(node.getString("type"))) {
            String unit=node.getString("unit");
            EditText input=new EditText(this);input.setSingleLine(true);input.setHint(node.optString("prompt","측정값")+" ("+unit+")");
            input.setContentDescription("measurement_value");
            input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER|android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL|android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
            body.addView(input);Button submit=Ui.button(this,"측정값 판정");
            submit.setOnClickListener(v->{try{
                String value=input.getText().toString().trim();
                if(value.isEmpty())throw new IllegalArgumentException("측정값을 입력하세요");
                engine.submitMeasurement(Double.parseDouble(value),unit);render();
            }catch(Exception error){new android.app.AlertDialog.Builder(this).setTitle("진행 차단").setMessage(error.getMessage()).setPositiveButton("확인",null).show();}});
            body.addView(submit);return;
        }
        JSONArray choices=node.getJSONArray("choices");
        for(int i=0;i<choices.length();i++) {
            JSONObject choice=choices.getJSONObject(i);String id=choice.getString("id");
            Button button=Ui.button(this,choice.getString("label"));button.setContentDescription("choice_"+id);
            button.setOnClickListener(v->{try{engine.choose(id);render();}catch(Exception e){
                new android.app.AlertDialog.Builder(this).setTitle("진행 차단").setMessage(e.getMessage()).setPositiveButton("확인",null).show();
            }});body.addView(button);
        }
        body.post(()->((ScrollView)body.getParent()).smoothScrollTo(0,0));
    }

    private void add(String label,Object value) {
        if(value==null || value==JSONObject.NULL)return;
        String text=value.toString();
        if(value instanceof JSONArray){StringBuilder out=new StringBuilder();JSONArray list=(JSONArray)value;
            for(int i=0;i<list.length();i++)out.append("• ").append(list.optString(i)).append('\n');text=out.toString();}
        if(!text.isEmpty())body.addView(Ui.text(this,label+"\n"+text,15,false));
    }
}
