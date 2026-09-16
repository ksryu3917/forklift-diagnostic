#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/ryu/forkliftdiagnostic"
ASSETS = ROOT / "app/src/main/assets"

def read(path):
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.write_text(text, encoding="utf-8")

def replace_once(text, old, new, label):
    if new in text:
        return text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly 1 baseline match, got {n}")
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# 1. Materialize the already-agreed V8.9.1 runtime integration into SOURCE.
#    This must be run ONCE by Work and committed. CI must never generate app
#    source before a build again.
# ---------------------------------------------------------------------------
legacy = ROOT / "tools/apply_v891_runtime_integration.py"
if not legacy.exists():
    raise SystemExit("missing tools/apply_v891_runtime_integration.py")
subprocess.run([sys.executable, str(legacy), str(ROOT)], check=True)

# ---------------------------------------------------------------------------
# 2. Stable runtime-test anchors in TestPointLocatorActivity.
# ---------------------------------------------------------------------------
tp_path = JAVA / "TestPointLocatorActivity.java"
tp = read(tp_path)

tp = replace_once(
    tp,
    'base("빠른점검 · "+group.optString("system"));\n        visiblePointIds.clear();',
    'base("빠른점검 · "+group.optString("system"));\n'
    '        body.setContentDescription("testpoint-group:"+groupId);\n'
    '        visiblePointIds.clear();',
    "test-point root test id"
)

tp = replace_once(
    tp,
    'TextView title=tv(displayText(p.optString("label")),21,true);c.addView(title);',
    'TextView title=tv(displayText(p.optString("label")),21,true);'
    'title.setContentDescription("quick-point:"+pid);c.addView(title);',
    "active quick-point test id"
)

tp = replace_once(
    tp,
    'Button ok=decisionBtn("정상",GREEN);Button bad=decisionBtn("이상",Color.rgb(180,45,45));',
    'Button ok=decisionBtn("정상",GREEN);Button bad=decisionBtn("이상",Color.rgb(180,45,45));'
    'ok.setContentDescription("quick-pass:"+pid);bad.setContentDescription("quick-fail:"+pid);',
    "quick decision test ids"
)

write(tp_path, tp)

# ---------------------------------------------------------------------------
# 3. Stable electrical/zoom anchors.
# ---------------------------------------------------------------------------
el_path = JAVA / "ElectricalDiagnosticActivity.java"
el = read(el_path)
el = replace_once(
    el,
    'base(g.optString("title"));\n\n        LinearLayout h=card();',
    'base(g.optString("title"));\n'
    '        body.setContentDescription("electrical-graph:"+gid);\n\n'
    '        LinearLayout h=card();',
    "electrical graph root test id"
)
el = replace_once(
    el,
    'Button more=btn("회로 · 퓨즈/릴레이 · OEM 근거 보기",false);more.setOnClickListener',
    'Button more=btn("회로 · 퓨즈/릴레이 · OEM 근거 보기",false);'
    'more.setContentDescription("circuit-evidence:"+gid);more.setOnClickListener',
    "circuit evidence test id"
)
el = replace_once(
    el,
    'ImageView iv=new ImageView(this);iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);',
    'ImageView iv=new ImageView(this);iv.setContentDescription("circuit-image:"+gid);'
    'iv.setImageBitmap(bm);iv.setAdjustViewBounds(true);iv.setScaleType(ImageView.ScaleType.FIT_CENTER);',
    "circuit image test id"
)
write(el_path, el)

zoom_path = JAVA / "ZoomImageDialog.java"
zoom = read(zoom_path)
zoom = replace_once(
    zoom,
    'hint.setText("두 손가락 확대 · 드래그 이동 · 더블탭 확대/원위치");',
    'hint.setText("두 손가락 확대 · 드래그 이동 · 더블탭 확대/원위치");'
    'hint.setContentDescription("zoom-hint");',
    "zoom hint test id"
)
zoom = replace_once(
    zoom,
    'ZoomImageView view = new ZoomImageView(activity);\n        view.setBackgroundColor(Color.BLACK);',
    'ZoomImageView view = new ZoomImageView(activity);\n'
    '        view.setContentDescription("zoom-image");\n'
    '        view.setBackgroundColor(Color.BLACK);',
    "zoom image test id"
)
write(zoom_path, zoom)

# ---------------------------------------------------------------------------
# 4. Test dependencies. Runtime tests use ActivityScenario/Espresso for
#    deterministic lifecycle/view assertions; UiAutomator is used only for
#    real multi-touch/drag gestures and screenshots.
# ---------------------------------------------------------------------------
gradle_path = ROOT / "app/build.gradle"
gradle = read(gradle_path)
gradle = re.sub(r'versionCode\s+\d+', 'versionCode 37', gradle, count=1)
gradle = re.sub(r'versionName\s+"[^"]+"',
                'versionName "0.18-rc-expert-v8.9.3-field-rebuild"', gradle, count=1)
deps = [
    "androidTestImplementation 'androidx.test:core:1.6.1'",
    "androidTestImplementation 'androidx.test:rules:1.6.1'",
    "androidTestImplementation 'androidx.test.espresso:espresso-core:3.6.1'",
]
for dep in deps:
    if dep not in gradle:
        marker = "dependencies {\n"
        if marker not in gradle:
            raise SystemExit("build.gradle dependencies block missing")
        gradle = gradle.replace(marker, marker + "    " + dep + "\n", 1)
write(gradle_path, gradle)

release_path = ASSETS / "diagnostic_release.json"
release = json.loads(read(release_path))
release.update({
    "release": "v18",
    "state": "RC EXPERT V8.9.3 FIELD REBUILD",
    "version_name": "0.18-rc-expert-v8.9.3-field-rebuild",
    "source_branch": "v18-rc-auto",
    "git_commit_sha": "UNSTAMPED_SOURCE"
})
write(release_path, json.dumps(release, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------------------
# 5. Replace runtime test with lifecycle-stable test. We deliberately do NOT
#    use FLAG_ACTIVITY_CLEAR_TASK and text polling as the launch gate.
# ---------------------------------------------------------------------------
test_src = ROOT / "V893_QuickUiRuntimeTest.java"
dst = ROOT / "app/src/androidTest/java/com/ryu/forkliftdiagnostic/QuickUiRuntimeTest.java"
if not test_src.exists():
    raise SystemExit("overlay missing V893_QuickUiRuntimeTest.java")
write(dst, read(test_src))
test_src.unlink()

print("V8.9.3 FIELD REBUILD source patch applied")
