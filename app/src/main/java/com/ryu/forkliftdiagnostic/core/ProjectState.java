package com.ryu.forkliftdiagnostic.core;

import android.content.Context;
import org.json.JSONObject;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

public final class ProjectState {
    public final String release, state, versionName, sourceBranch, gitSha;
    public final int schemaVersion;

    private ProjectState(JSONObject j) {
        release = j.optString("release", "UNKNOWN");
        state = j.optString("state", "UNKNOWN");
        versionName = j.optString("version_name", "UNKNOWN");
        sourceBranch = j.optString("source_branch", "UNKNOWN");
        gitSha = j.optString("git_commit_sha", "UNKNOWN");
        schemaVersion = j.optInt("schema_version", -1);
    }

    public static ProjectState load(Context c) throws Exception {
        try (InputStream in = c.getAssets().open("v20/project_state.json");
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] b = new byte[8192];
            int n;
            while ((n = in.read(b)) > 0) out.write(b, 0, n);
            return new ProjectState(new JSONObject(out.toString(StandardCharsets.UTF_8.name())));
        }
    }
}
