package com.ryu.forkliftdiagnostic.core;
import android.content.Context; import org.json.JSONObject; import java.io.*; import java.nio.charset.StandardCharsets;
public final class AssetJson {private AssetJson(){} public static JSONObject read(Context c,String path)throws Exception{try(InputStream in=c.getAssets().open(path);ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))>0)out.write(b,0,n);return new JSONObject(out.toString(StandardCharsets.UTF_8.name()));}}}
