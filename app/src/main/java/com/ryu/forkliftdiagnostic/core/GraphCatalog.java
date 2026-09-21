package com.ryu.forkliftdiagnostic.core;

import android.content.Context;
import org.json.JSONArray;
import org.json.JSONObject;

public final class GraphCatalog {
    private GraphCatalog() {}

    public static JSONArray forVehicle(Context context, String manufacturer, String model) throws Exception {
        JSONArray all = AssetJson.read(context,"v20/catalog.json").getJSONArray("graphs");
        JSONArray result = new JSONArray();
        for (int i=0;i<all.length();i++) {
            JSONObject entry=all.getJSONObject(i);
            JSONObject scope=entry.getJSONObject("vehicle_scope");
            if (!manufacturer.equals(scope.getString("manufacturer"))) continue;
            JSONArray models=scope.getJSONArray("models");
            for (int j=0;j<models.length();j++) if(model.equals(models.getString(j))) {
                result.put(entry); break;
            }
        }
        return result;
    }
}
