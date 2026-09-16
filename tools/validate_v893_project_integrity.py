#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
J = ROOT / "app/src/main/java/com/ryu/forkliftdiagnostic"
A = ROOT / "app/src/main/assets"
errors=[]

def need(cond, msg):
    if not cond: errors.append(msg)

# Release identity.
g=(ROOT/"app/build.gradle").read_text(encoding="utf-8")
r=json.loads((A/"diagnostic_release.json").read_text(encoding="utf-8"))
need("versionCode 37" in g, "versionCode 37 missing")
need('versionName "0.18-rc-expert-v8.9.3-field-rebuild"' in g, "V8.9.3 versionName missing")
need(r.get("state")=="RC EXPERT V8.9.3 FIELD REBUILD", "release state mismatch")
need(r.get("version_name")=="0.18-rc-expert-v8.9.3-field-rebuild", "release version mismatch")

# Source must already contain the runtime integration. A build may validate
# source, but may not generate/patch MainActivity or Manifest.
main=(J/"MainActivity.java").read_text(encoding="utf-8")
manifest=(ROOT/"app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
need("D24 엔진 현장진단" in main, "D24 runtime entry is not committed into MainActivity source")
need("EngineExpertDiagnosticActivity.class" in main, "D24 activity link missing in source")
need("전기 / 차체전장 진단" in main, "electrical runtime entry missing in source")
need("D34 임시 기준" not in main, "legacy D34 temporary entry still present")
for activity in [
    "ElectricalDiagnosticActivity","EngineExpertDiagnosticActivity","EngineSensorMapActivity",
    "ExpertDiagnosticActivity","FieldLocationMapActivity","PartsReferenceActivity","TestPointLocatorActivity"
]:
    need(f'android:name=".{activity}"' in manifest, f"Manifest activity missing: {activity}")

# Quick UI must have deterministic runtime anchors.
tp=(J/"TestPointLocatorActivity.java").read_text(encoding="utf-8")
el=(J/"ElectricalDiagnosticActivity.java").read_text(encoding="utf-8")
zoom=(J/"ZoomImageDialog.java").read_text(encoding="utf-8")
for token in ["testpoint-group:", "quick-point:", "quick-pass:", "quick-fail:"]:
    need(token in tp, "TestPoint runtime test anchor missing: "+token)
for token in ["electrical-graph:", "circuit-evidence:", "circuit-image:"]:
    need(token in el, "Electrical runtime test anchor missing: "+token)
for token in ["zoom-hint", "zoom-image", "ScaleGestureDetector", "matrix.postTranslate", "onDoubleTap"]:
    need(token in zoom, "Zoom runtime contract missing: "+token)

# License-lamp adaptive branch: simulate the exact requested field path.
d=json.loads((A/"test_point_locator_v1.json").read_text(encoding="utf-8"))
lic=d.get("groups",{}).get("EL_LICENSE",{})
points={p.get("id"):p for p in lic.get("points",[])}
for pid, text in [
    ("LP1","다른 미등/후미등 정상 여부"),
    ("LP2","번호판등 +전원"),
    ("LP3","번호판등 접지 전압강하"),
    ("LP4","LAMP")
]:
    need(pid in points and text in points[pid].get("label",""), f"EL_LICENSE {pid} contract mismatch")

rules=lic.get("adaptive_branch",{}).get("rules",[])
def first_rule(state):
    for rr in rules:
        when=rr.get("when",{})
        if when and all(state.get(k)==v for k,v in when.items()):
            return rr
    return None

# Empty state -> LP1 (implicit first point)
need(lic.get("points",[{}])[0].get("id")=="LP1", "EL_LICENSE first point must be LP1")
r1=first_rule({"LP1":"PASS"})
need(r1 and r1.get("next_points")==["LP2"], "LP1 PASS must move only to LP2")
rf=first_rule({"LP1":"FAIL"})
need(rf and rf.get("next_points")==["LP4"], "LP1 FAIL must move to common LAMP LP4")
r2=first_rule({"LP1":"PASS","LP2":"PASS"})
need(r2 and r2.get("next_points")==["LP3"], "LP1+LP2 PASS must move only to LP3")
r3=first_rule({"LP1":"PASS","LP2":"PASS","LP3":"PASS"})
need(r3 and not r3.get("next_points") and "전구/소켓" in
     (r3.get("title","")+r3.get("assessment","")),
     "LP1+LP2+LP3 PASS must stop at bulb/socket contact area")

# Ordered-first-match must keep more-specific rules ahead of broader prefixes.
def specificity(rr): return len(rr.get("when",{}))
for i, rr in enumerate(rules):
    wi=rr.get("when",{})
    for later in rules[i+1:]:
        wl=later.get("when",{})
        if wi and wl and len(wi) < len(wl) and all(wl.get(k)==v for k,v in wi.items()):
            errors.append("adaptive rule shadowing: broader rule precedes a more-specific rule: "
                          + rr.get("id","?")+" before "+later.get("id","?"))

# Runtime test contract.
t=(ROOT/"app/src/androidTest/java/com/ryu/forkliftdiagnostic/QuickUiRuntimeTest.java").read_text(encoding="utf-8")
for token in ["ActivityScenario.launch", "quick-point:LP1", "quick-pass:LP1",
              "quick-fail:LP1", "zoom-image", "dumpWindowHierarchy"]:
    need(token in t, "runtime test contract missing: "+token)
need("FLAG_ACTIVITY_CLEAR_TASK" not in t, "runtime test must not clear the whole task while launching")
need("By.textContains(\"다른 미등/후미등 정상 여부\")" not in t,
     "launch gate must not depend on UiAutomator Korean text polling")

# CI contract: push build is fast; heavy runtime gate is manual-only.
build=(ROOT/".github/workflows/build-apk.yml").read_text(encoding="utf-8")
runtime=(ROOT/".github/workflows/runtime-ui.yml").read_text(encoding="utf-8")
need("apply_v891_runtime_integration.py" not in build,
     "build workflow still mutates source with apply_v891_runtime_integration.py")
need("runtime-ui:" not in build, "heavy runtime-ui job still coupled to every push")
need("workflow_dispatch:" in runtime, "runtime UI workflow is not manually dispatchable")
need("push:" not in runtime, "runtime UI workflow must not run on every push")
need("validate_v893_project_integrity.py" in build, "V8.9.3 integrity validator missing from build")
need("validate_v893_project_integrity.py" in runtime, "V8.9.3 integrity validator missing from runtime gate")

print("v893_project_integrity_errors=", len(errors))
for e in errors: print("ERROR",e)
if errors: raise SystemExit(1)
print("V8.9.3 PROJECT INTEGRITY PASS")
