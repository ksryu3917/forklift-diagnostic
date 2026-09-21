package com.ryu.forkliftdiagnostic.engine;

import org.json.JSONObject;
import org.json.JSONArray;
import java.util.HashSet;
import java.util.Set;

/**
 * V20 핵심 원칙:
 * - UI에 현재 node 하나만 제공한다.
 * - next id가 없는 비-terminal은 거부한다.
 * - scope/evidence/teardown 판정은 UI가 아니라 engine 계층에서 한다.
 */
public final class DiagnosticEngine {
    private final JSONObject graph;
    private final JSONObject vehicle;
    private final JSONObject evidence;
    private String currentId;
    private String safetyNode = "";

    public DiagnosticEngine(JSONObject graph, JSONObject vehicle, JSONObject evidence) throws Exception {
        this.graph = new JSONObject(graph.toString());
        this.vehicle = new JSONObject(vehicle.toString());
        this.evidence = new JSONObject(evidence.toString());
        this.currentId = graph.getString("start");
        validateReachability();
        requireNode(currentId);
    }

    public JSONObject currentNode() throws Exception {
        requireNode(currentId);
        return new JSONObject(graph.getJSONObject("nodes").getJSONObject(currentId).toString());
    }

    public String currentId() { return currentId; }

    public void acknowledgeSafety(boolean accepted) throws Exception {
        requireNode(currentId);
        safetyNode = accepted ? currentId : "";
    }

    public boolean isTerminal() throws Exception {
        return "result".equals(currentNode().optString("type"));
    }

    public void choose(String choiceId) throws Exception {
        JSONObject n = currentNode();
        if (isTerminal()) throw new IllegalStateException("TERMINAL_STOP");
        if (!currentId.equals(safetyNode)) throw new IllegalStateException("SAFETY_NOT_ACKNOWLEDGED");
        JSONArray choices = n.optJSONArray("choices");
        if (choices == null) throw new IllegalStateException("현재 node는 선택형이 아닙니다.");
        for (int i=0;i<choices.length();i++) {
            JSONObject c = choices.getJSONObject(i);
            if (choiceId.equals(c.optString("id"))) {
                String next = c.optString("next");
                if (!graph.getJSONObject("nodes").has(next))
                    throw new IllegalStateException("broken next: "+next);
                requireNode(next);
                currentId = next;
                safetyNode = "";
                return;
            }
        }
        throw new IllegalArgumentException("unknown choice: "+choiceId);
    }

    private void validateReachability() throws Exception {
        JSONObject nodes = graph.getJSONObject("nodes");
        if (!nodes.has(currentId)) throw new IllegalStateException("missing start");
        Set<String> seen = new HashSet<>();
        JSONArray entries=graph.optJSONArray("entry_points");
        if(entries==null) walk(currentId, nodes, seen, new HashSet<>());
        else for(int i=0;i<entries.length();i++) walk(entries.getString(i),nodes,seen,new HashSet<>());
        if (seen.size() != nodes.length()) throw new IllegalStateException("UNREACHABLE_NODE");
    }

    private void walk(String id, JSONObject nodes, Set<String> seen, Set<String> active) throws Exception {
        if (active.contains(id)) throw new IllegalStateException("CYCLE: "+id);
        if (!seen.add(id)) return;
        active.add(id);
        JSONObject n = nodes.getJSONObject(id);
        JSONArray choices = n.optJSONArray("choices");
        if ("result".equals(n.getString("type"))) {
            if (choices != null && choices.length() > 0) throw new IllegalStateException("TERMINAL_HAS_CHOICES");
            active.remove(id);
            return;
        }
        if (!"question".equals(n.getString("type")) || choices == null || choices.length() == 0)
            throw new IllegalStateException("DEAD_END: "+id);
        Set<String> choiceIds = new HashSet<>();
        for (int i=0;i<choices.length();i++) {
            String choiceId = choices.getJSONObject(i).getString("id");
            if (choiceId.isEmpty() || !choiceIds.add(choiceId)) throw new IllegalStateException("DUPLICATE_CHOICE");
            String next = choices.getJSONObject(i).optString("next");
            if (!nodes.has(next)) throw new IllegalStateException("broken next: "+id+" -> "+next);
            walk(next, nodes, seen, active);
        }
        active.remove(id);
    }

    private void requireScope(JSONObject scope) throws Exception {
        String maker = vehicle.optString("manufacturer");
        String model = vehicle.optString("model");
        if (maker.isEmpty() || model.isEmpty() || model.contains("UNKNOWN") ||
            !maker.equals(scope.optString("manufacturer")) || "ALL".equals(maker))
            throw new IllegalStateException("EXACT_MODEL_REQUIRED");
        JSONArray models = scope.optJSONArray("models");
        boolean found = false;
        if (models != null) for (int i=0; i<models.length(); i++)
            if (model.equals(models.getString(i))) found = true;
        if (!found) throw new IllegalStateException("MODEL_OUT_OF_SCOPE");
        for (String key : new String[]{"engine", "powertrain", "voltage", "variant"})
            if (scope.has(key) && !scope.getString(key).equals(vehicle.optString(key)))
                throw new IllegalStateException("VARIANT_OUT_OF_SCOPE: "+key);
    }

    private void requireNode(String id) throws Exception {
        JSONObject node = graph.getJSONObject("nodes").getJSONObject(id);
        requireScope(graph.getJSONObject("vehicle_scope"));
        if (node.has("vehicle_scope")) requireScope(node.getJSONObject("vehicle_scope"));
        JSONArray gaps = node.optJSONArray("contract_gaps");
        if ("OEM_VERIFY".equals(node.optString("readiness")) || (gaps != null && gaps.length()>0))
            throw new IllegalStateException("OEM_VERIFY: "+id);
        for (String key : new String[]{"safety_preconditions", "first_observation", "test_location", "tool",
                "operating_condition", "measurement_or_action", "expected_basis"}) requireValue(node,key);
        JSONArray refs = node.optJSONArray("evidence_refs");
        if (refs == null || refs.length()==0) throw new IllegalStateException("EVIDENCE_MISSING: "+id);
        for (int i=0; i<refs.length(); i++) {
            JSONObject ref = evidence.optJSONObject(refs.getString(i));
            if (ref == null || !"VERIFIED".equals(ref.optString("status")))
                throw new IllegalStateException("EVIDENCE_UNVERIFIED: "+refs.getString(i));
            requireScope(ref.getJSONObject("vehicle_scope"));
            requireValue(ref,"locator");
        }
        if ("result".equals(node.getString("type")))
            for (String key : new String[]{"rule_out", "confirm_if", "next_action", "teardown_gate", "do_not"})
                requireValue(node,key);
    }

    private static void requireValue(JSONObject node, String key) {
        Object value = node.opt(key);
        if (value == null || value == JSONObject.NULL || value.toString().trim().isEmpty() ||
            (value instanceof JSONArray && ((JSONArray)value).length()==0))
            throw new IllegalStateException("CONTRACT_MISSING: "+key);
    }
}
