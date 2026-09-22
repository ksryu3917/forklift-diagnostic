package com.ryu.forkliftdiagnostic.ui;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.*;
import com.ryu.forkliftdiagnostic.core.AssetJson;
import org.json.*;
import java.util.Locale;

public class InfoActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        String mode=getIntent().getStringExtra("mode");
        LinearLayout body=Ui.page(this,title(mode));
        if("manual".equals(mode)) {
            try { showManuals(body); }
            catch(Exception error){body.addView(Ui.text(this,"문서 목록 읽기 실패: "+error.getMessage(),16,true));}
        } else if("parts".equals(mode)) {
            body.addView(Ui.text(this,"부품번호·가격·공임은 terminal 진단 결과 뒤에만 연결됩니다. 현재 부품 연결 기능은 구현 중입니다.",16,true));
        } else {
            body.addView(Ui.text(this,"이 기능은 아직 구현되지 않았습니다. 입력·저장 완료로 간주하지 마세요.",16,false));
        }
    }

    private void showManuals(LinearLayout body) throws Exception {
        JSONArray documents=AssetJson.read(this,"v20/reference/manual_library_catalog.json").getJSONObject("data").getJSONArray("documents");
        body.addView(Ui.text(this,"문서 목록 "+documents.length()+"건 · 원문 파일 전체가 APK에 포함된 것은 아닙니다. 목록 등록·문서 식별과 진단 근거 검증은 서로 다른 상태입니다.",15,false));
        EditText query=new EditText(this);query.setSingleLine(true);query.setHint("문서명 / 제조사 / 모델 검색");body.addView(query);
        CheckBox exact=new CheckBox(this);exact.setText("선택 차량과 제조사·모델이 명시적으로 일치하는 문서만");body.addView(exact);
        TextView count=Ui.text(this,"",14,true);body.addView(count);
        LinearLayout results=new LinearLayout(this);results.setOrientation(LinearLayout.VERTICAL);body.addView(results);
        Runnable filter=()->{
            results.removeAllViews();int matches=0;
            String term=query.getText().toString().trim().toLowerCase(Locale.ROOT);
            android.content.SharedPreferences vehicle=getSharedPreferences("vehicle",0);
            for(int i=0;i<documents.length();i++){
                JSONObject doc=documents.optJSONObject(i);if(doc==null)continue;
                JSONArray models=doc.optJSONArray("models");boolean modelMatches=false;
                if(models!=null)for(int k=0;k<models.length();k++)if(models.optString(k).equalsIgnoreCase(vehicle.getString("model","")))modelMatches=true;
                boolean scoped=modelMatches&&doc.optString("manufacturer").equalsIgnoreCase(vehicle.getString("manufacturer",""));
                if(exact.isChecked()&&!scoped)continue;
                String searchable=doc.optString("name")+" "+doc.optString("manufacturer")+" "+doc.optString("search_text")+" "+(models==null?"":models.toString());
                if(!searchable.toLowerCase(Locale.ROOT).contains(term))continue;
                matches++;
                Button row=Ui.button(this,doc.optString("name")+"\n"+doc.optString("manufacturer")+" · "+doc.optString("document_type")+" · "+doc.optString("review_state")+"\n"+(scoped?"적용 모델 일치":"선택 모델 적용 여부 미확인"));
                row.setOnClickListener(v->new android.app.AlertDialog.Builder(this).setTitle(doc.optString("name"))
                    .setMessage("자료 ID: "+doc.optString("id")+"\n모델: "+doc.optString("models","미확인")+"\n문서 상태: "+doc.optString("review_state")+"\n정규화 상태: "+doc.optString("normalization_state")+"\n원문 페이지 수: "+doc.optString("page_count","미확인")+"\n\n이 화면은 문서 목록 정보입니다. 원문이 확인되지 않은 시험 수치나 핀맵을 진단에 적용하지 않습니다.")
                    .setPositiveButton("닫기",null).show());
                results.addView(row);
            }
            count.setText(matches+"건 검색됨");
        };
        query.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int start,int count,int after){}public void onTextChanged(CharSequence s,int start,int before,int count){filter.run();}public void afterTextChanged(Editable s){}});
        exact.setOnCheckedChangeListener((button,checked)->filter.run());filter.run();
    }
    private String title(String mode){if("manual".equals(mode))return "매뉴얼 라이브러리";if("parts".equals(mode))return "부품·가격·공임";if("history".equals(mode))return "정비 이력";return "내 현장 경험";}
}
