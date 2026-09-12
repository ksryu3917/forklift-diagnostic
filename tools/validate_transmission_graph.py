#!/usr/bin/env python3
import json, sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "app/src/main/assets/transmission_diag_v08.json"
ASSET_DIR = ROOT / "app/src/main/assets/oem_pages"
REPORT_MD = ROOT / "build/reports/transmission_graph_validation.md"
REPORT_JSON = ROOT / "build/reports/transmission_graph_validation.json"

SCENARIOS_PER_RESULT = 30
MAX_STEPS = 120

FORBIDDEN_PENDING = (
    "추가 정규화",
    "정규화해",
    "추후",
    "나중에",
    "pending",
    "TODO",
    "TBD",
)

MEASURE_NEXT_KEYS = (
    "next_low", "next_normal", "next_high", "next_cross",
    "next_common_low", "next_f_low", "next_r_low", "next_cross_apply"
)

def all_nexts(node):
    out = []
    for c in node.get("choices", []):
        if c.get("next"):
            out.append(c["next"])
    for k, v in node.items():
        if k.startswith("next_") and isinstance(v, str) and v:
            out.append(v)
    return out

def asset_exists(page):
    if not ASSET_DIR.exists():
        return False
    candidates = [
        ASSET_DIR / f"p{page:03d}.jpg",
        ASSET_DIR / f"p{page}.jpg",
        ASSET_DIR / f"p{page:03d}.png",
        ASSET_DIR / f"p{page}.png",
        ASSET_DIR / f"p{page:03d}.webp",
        ASSET_DIR / f"p{page}.webp",
    ]
    return any(x.exists() for x in candidates)

def structural_validate(sid, graph):
    errors, warnings = [], []
    nodes = graph.get("nodes", {})
    start = graph.get("start")
    entries = graph.get("entry_points") or ([start] if start else [])

    if not start or start not in nodes:
        errors.append(f"{sid}: start node missing: {start}")
        return errors, warnings, set()
    for ent in entries:
        if ent not in nodes:
            errors.append(f"{sid}: entry point missing: {ent}")

    # Link integrity
    for nid, node in nodes.items():
        for nxt in all_nexts(node):
            if nxt not in nodes:
                errors.append(f"{sid}/{nid}: broken link -> {nxt}")

        typ = node.get("type", "")
        if typ == "question":
            choices = node.get("choices", [])
            if not choices:
                errors.append(f"{sid}/{nid}: question has no choices")
        elif typ in ("measure", "reverse_pair_measure", "clutch_pair_measure"):
            if typ == "measure":
                if "min" not in node or "max" not in node:
                    errors.append(f"{sid}/{nid}: measure missing min/max")
                elif node["min"] > node["max"]:
                    errors.append(f"{sid}/{nid}: min > max")
                if not any(node.get(k) for k in ("next_low","next_normal","next_high")):
                    errors.append(f"{sid}/{nid}: measure has no low/normal/high route")
            if not node.get("unit") and typ == "measure":
                warnings.append(f"{sid}/{nid}: measure missing unit")
        elif typ == "result":
            if not node.get("result"):
                warnings.append(f"{sid}/{nid}: result text missing")
            if not node.get("action"):
                warnings.append(f"{sid}/{nid}: action text missing")
        else:
            warnings.append(f"{sid}/{nid}: unknown/custom node type '{typ}'")

        # Pending / placeholder terminal checks
        txt = " ".join(str(node.get(k, "")) for k in ("title","question","result","action","note")).lower()
        for bad in FORBIDDEN_PENDING:
            if bad.lower() in txt:
                errors.append(f"{sid}/{nid}: placeholder/pending text detected: '{bad}'")

        # Manual page assets
        for pg in node.get("manual_pages", []) or []:
            try:
                pgi = int(pg)
            except Exception:
                errors.append(f"{sid}/{nid}: invalid manual page value {pg!r}")
                continue
            if not asset_exists(pgi):
                errors.append(f"{sid}/{nid}: manual page asset missing for page {pgi}")

    # Reachability
    seen = set()
    q = deque(entries)
    while q:
        nid = q.popleft()
        if nid in seen or nid not in nodes:
            continue
        seen.add(nid)
        q.extend(all_nexts(nodes[nid]))
    unreachable = sorted(set(nodes) - seen)
    if unreachable:
        warnings.append(f"{sid}: {len(unreachable)} unreachable node(s): " + ", ".join(unreachable[:20]))

    # terminal sanity
    for nid in seen:
        node = nodes[nid]
        if not all_nexts(node) and node.get("type") != "result":
            errors.append(f"{sid}/{nid}: reachable dead-end is not result")

    return errors, warnings, seen

def route_details(node):
    """Return (next node, input description) pairs without inventing service limits."""
    out = []
    if node.get("type") == "question":
        for choice in node.get("choices", []):
            if choice.get("next"):
                out.append((choice["next"], {"answer": choice.get("label", "")}))
    for key, nxt in node.items():
        if key.startswith("next_") and isinstance(nxt, str) and nxt:
            out.append((nxt, {"measurement_class": key.removeprefix("next_")}))
    return out

def shortest_result_paths(graph):
    """Find an executable shortest path from any declared entry to every result."""
    nodes = graph["nodes"]
    entries = graph.get("entry_points") or [graph["start"]]
    paths = {}
    queue = deque((entry, []) for entry in entries)
    best_depth = {}
    while queue:
        nid, path = queue.popleft()
        if nid not in nodes or len(path) > MAX_STEPS:
            continue
        if len(path) > best_depth.get(nid, MAX_STEPS + 1):
            continue
        best_depth[nid] = len(path)
        node = nodes[nid]
        if node.get("type") == "result":
            paths.setdefault(nid, path)
            continue
        for nxt, supplied in route_details(node):
            if any(step[0] == nxt for step in path):
                continue
            queue.append((nxt, path + [(nid, nxt, supplied)]))
    return paths

def condition_matrix():
    # These are simulation dimensions, not OEM numeric specifications. 3 x 5 x 2 = 30.
    for temperature in ("cold_start", "service_temperature", "heat_soaked"):
        for duty in ("idle", "creep", "travel", "loaded", "post_load_recheck"):
            for repeat in ("first_occurrence", "repeat_occurrence"):
                yield {
                    "temperature_state": temperature,
                    "duty_state": duty,
                    "repeatability": repeat,
                }

def validate_result_scenarios(sid, graph, count=SCENARIOS_PER_RESULT):
    nodes = graph["nodes"]
    failures = []
    terminal_hits = defaultdict(int)
    edge_hits = defaultdict(int)
    paths = shortest_result_paths(graph)
    reachable_results = sorted(nid for nid, node in nodes.items()
                               if node.get("type") == "result" and nid in paths)
    contexts = list(condition_matrix())
    if len(contexts) < count:
        failures.append(f"condition matrix has only {len(contexts)} variants")
        return failures, terminal_hits, edge_hits, paths

    fingerprints = set()
    for result_id in reachable_results:
        path = paths[result_id]
        for scenario_no, context in enumerate(contexts[:count], 1):
            nid = path[0][0] if path else result_id
            supplied_inputs = []
            for source, expected_next, supplied in path:
                if nid != source:
                    failures.append(f"{result_id}/scenario#{scenario_no}: path desync at {source}")
                    break
                legal = {(nxt, json.dumps(inp, ensure_ascii=False, sort_keys=True))
                         for nxt, inp in route_details(nodes[source])}
                token = (expected_next, json.dumps(supplied, ensure_ascii=False, sort_keys=True))
                if token not in legal:
                    failures.append(f"{result_id}/scenario#{scenario_no}: illegal route {source}->{expected_next}")
                    break
                supplied_inputs.append({"node": source, **supplied})
                edge_hits[(source, expected_next)] += 1
                nid = expected_next
            if nid != result_id or nodes.get(nid, {}).get("type") != "result":
                failures.append(f"{result_id}/scenario#{scenario_no}: ended at {nid}")
                continue
            fingerprint = json.dumps({"target": result_id, "context": context,
                                      "inputs": supplied_inputs}, ensure_ascii=False, sort_keys=True)
            if fingerprint in fingerprints:
                failures.append(f"{result_id}/scenario#{scenario_no}: duplicate scenario")
                continue
            fingerprints.add(fingerprint)
            terminal_hits[result_id] += 1

    for result_id in reachable_results:
        if terminal_hits[result_id] < count:
            failures.append(f"{result_id}: only {terminal_hits[result_id]}/{count} distinct scenarios passed")
    return failures, terminal_hits, edge_hits, paths

def main():
    if not JSON_PATH.exists():
        print(f"ERROR: missing {JSON_PATH}", file=sys.stderr)
        return 2

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    graphs = data.get("graphs", {})

    all_errors = []
    all_warnings = []
    graph_rows = []
    detail = {}

    for sid in sorted(graphs):
        graph = graphs[sid]
        errors, warnings, reachable = structural_validate(sid, graph)
        sim_fail, terminals, edges, result_paths = validate_result_scenarios(sid, graph)

        all_results = {nid for nid, node in graph.get("nodes", {}).items()
                       if node.get("type") == "result"}
        unreachable_results = sorted(all_results - set(result_paths))
        if unreachable_results:
            errors.append(f"{sid}: unreachable result(s): " + ", ".join(unreachable_results))

        errors.extend(f"{sid}: {x}" for x in sim_fail)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        graph_rows.append({
            "sid": sid,
            "nodes": len(graph.get("nodes", {})),
            "reachable": len(reachable),
            "results": len(all_results),
            "simulations": len(terminals) * SCENARIOS_PER_RESULT,
            "terminals_hit": len(terminals),
            "errors": len(errors),
            "warnings": len(warnings),
        })
        detail[sid] = {
            "errors": errors,
            "warnings": warnings,
            "terminal_hits": dict(sorted(terminals.items())),
            "edge_hits": {f"{a}->{b}": n for (a,b), n in sorted(edges.items())},
        }

    # Write JSON report
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps({
        "version": data.get("version"),
        "graphs": graph_rows,
        "errors": all_errors,
        "warnings": all_warnings,
        "detail": detail,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Write Markdown report
    lines = []
    lines.append("# Transmission diagnostic graph validation")
    lines.append("")
    lines.append(f"- DB version: `{data.get('version','')}`")
    lines.append(f"- Graphs: **{len(graphs)}**")
    lines.append(f"- Scenarios per individual result: **{SCENARIOS_PER_RESULT}**")
    lines.append(f"- Total simulations: **{sum(r['simulations'] for r in graph_rows)}**")
    lines.append(f"- Errors: **{len(all_errors)}**")
    lines.append(f"- Warnings: **{len(all_warnings)}**")
    lines.append("")
    lines.append("| Symptom | Nodes | Reachable | Results | Scenarios | Results hit | Errors | Warnings |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in graph_rows:
        lines.append(f"| {r['sid']} | {r['nodes']} | {r['reachable']} | {r['results']} | {r['simulations']} | {r['terminals_hit']} | {r['errors']} | {r['warnings']} |")

    if all_errors:
        lines.append("")
        lines.append("## Errors")
        for x in all_errors:
            lines.append(f"- {x}")

    if all_warnings:
        lines.append("")
        lines.append("## Warnings")
        for x in all_warnings:
            lines.append(f"- {x}")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines[:12]))
    print(f"\nReports:\n  {REPORT_MD}\n  {REPORT_JSON}")

    return 1 if all_errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
