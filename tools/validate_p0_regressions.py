#!/usr/bin/env python3
"""Reject token-only P0 drafts and require executable, evidence-backed graphs."""
from pathlib import Path
import json
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
CASES = json.loads((ROOT / "requirements/p0_regressions.json").read_text(encoding="utf-8"))["cases"]
GRAPH_DIR = ROOT / "app/src/main/assets/v20/diagnostics"
EVIDENCE = json.loads((ROOT / "app/src/main/assets/v20/evidence_registry.json").read_text(encoding="utf-8"))["entries"]
FILES = {
    "EV_REACH_NO_TRAVEL_MECH_001": "ev_reach_no_travel_mech.json",
    "EV_BATTERY_SHORT_RUNTIME_001": "ev_battery_short_runtime.json",
    "EV_NO_TRAVEL_CONTROL_001": "ev_no_travel_control.json",
    "EV_HIGH_CURRENT_LOW_RPM_001": "ev_high_current_low_rpm.json",
    "EV_TEMP_SENSOR_FALSE_HIGH_001": "ev_temp_sensor_false_high.json",
    "E_LICENSE_TERMINAL_STOP_001": "e_license_terminal_stop.json",
    "BRAKE_INTERNAL_LEAK_001": "brake_internal_leak.json",
    "D24_CRANK_NO_START_001": "d24_crank_no_start.json",
}
NODE_FIELDS = ("safety_preconditions", "first_observation", "test_location", "tool",
               "operating_condition", "measurement_or_action", "expected_basis", "evidence_refs")
RESULT_FIELDS = ("rule_out", "confirm_if", "next_action", "teardown_gate", "do_not")
errors = []


def missing(value):
    return value is None or value == "" or value == []


def validate_scope(label, scope):
    maker = scope.get("manufacturer", "")
    models = scope.get("models", [])
    if not maker or maker == "ALL":
        errors.append(f"{label}: exact manufacturer required")
    if not models:
        errors.append(f"{label}: exact model list required")
    for model in models:
        if any(token in model for token in ("EXACT_", "UNKNOWN", "/", "(")):
            errors.append(f"{label}: placeholder or shorthand model is not executable: {model}")


for case in CASES:
    case_id = case["id"]
    filename = FILES.get(case_id)
    if not filename:
        errors.append(f"{case_id}: no graph mapping")
        continue
    path = GRAPH_DIR / filename
    if not path.exists():
        errors.append(f"{case_id}: missing graph {filename}")
        continue
    graph = json.loads(path.read_text(encoding="utf-8"))
    if graph.get("id") != case_id:
        errors.append(f"{case_id}: graph id mismatch")
    validate_scope(case_id, graph.get("vehicle_scope", {}))
    nodes = graph.get("nodes", {})
    start = graph.get("start")
    if start not in nodes:
        errors.append(f"{case_id}: missing start node")
        continue
    seen, active, terminals = set(), set(), set()

    def walk(node_id):
        if node_id in active:
            errors.append(f"{case_id}/{node_id}: cycle")
            return
        if node_id in seen:
            return
        seen.add(node_id)
        active.add(node_id)
        node = nodes[node_id]
        for field in NODE_FIELDS:
            if missing(node.get(field)):
                errors.append(f"{case_id}/{node_id}: missing {field}")
        for ref in node.get("evidence_refs", []):
            entry = EVIDENCE.get(ref)
            if not entry or entry.get("status") != "VERIFIED":
                errors.append(f"{case_id}/{node_id}: unverified evidence {ref}")
        if node.get("vehicle_scope"):
            validate_scope(f"{case_id}/{node_id}", node["vehicle_scope"])
        if node.get("type") == "result":
            terminals.add(node_id)
            if node.get("choices"):
                errors.append(f"{case_id}/{node_id}: terminal has choices")
            for field in RESULT_FIELDS:
                if missing(node.get(field)):
                    errors.append(f"{case_id}/{node_id}: missing {field}")
        else:
            choices = node.get("choices", [])
            if not choices:
                errors.append(f"{case_id}/{node_id}: non-terminal dead end")
            for choice in choices:
                target = choice.get("next")
                if target not in nodes:
                    errors.append(f"{case_id}/{node_id}: broken next {target}")
                else:
                    walk(target)
        active.remove(node_id)

    walk(start)
    unreachable = sorted(set(nodes) - seen)
    if unreachable:
        errors.append(f"{case_id}: unreachable nodes {unreachable}")
    if not terminals:
        errors.append(f"{case_id}: no reachable terminal")
    text = json.dumps(graph, ensure_ascii=False).casefold()
    for phrase in case.get("must_route_through", []):
        words = [word for word in phrase.casefold().replace("/", " ").split() if len(word) >= 2]
        if words and not any(word in text for word in words):
            errors.append(f"{case_id}: route requirement absent: {phrase}")

print(f"P0_EXECUTABLE_CASES={len(CASES)} ERRORS={len(errors)}")
for error in errors:
    print("ERROR", error)
if errors:
    raise SystemExit(1)
