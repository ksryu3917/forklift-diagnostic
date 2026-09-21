import com.ryu.forkliftdiagnostic.engine.DiagnosticEngine;
import org.json.*;

/** Synthetic engine invariants only; not the terminal-level field scenario gate. */
public final class EngineContractTest {
    interface Checked { void run() throws Exception; }
    static int passed;
    static JSONObject scope() throws Exception {
        return new JSONObject("{\"manufacturer\":\"DOOSAN\",\"models\":[\"D25S-7\"],\"engine\":\"D24\"}");
    }
    static JSONObject vehicle() throws Exception {
        return new JSONObject("{\"manufacturer\":\"DOOSAN\",\"model\":\"D25S-7\",\"engine\":\"D24\"}");
    }
    static JSONObject refs() throws Exception {
        return new JSONObject().put("test-only", new JSONObject().put("status","VERIFIED")
            .put("locator","synthetic test fixture, never bundled with app").put("vehicle_scope",scope()));
    }
    static JSONObject graph() throws Exception {
        JSONObject question=new JSONObject().put("type","question").put("title","Synthetic question");
        for(String k:new String[]{"safety_preconditions","first_observation","test_location","tool",
            "operating_condition","measurement_or_action","expected_basis"})question.put(k,"fixture");
        question.put("evidence_refs",new JSONArray().put("test-only"));
        question.put("choices",new JSONArray().put(new JSONObject().put("id","yes").put("label","yes").put("next","r")));
        JSONObject result=new JSONObject(question.toString()).put("type","result").put("choices",new JSONArray());
        for(String k:new String[]{"rule_out","confirm_if","next_action","teardown_gate","do_not"})result.put(k,"fixture");
        return new JSONObject().put("start","q").put("vehicle_scope",scope()).put("nodes",new JSONObject().put("q",question).put("r",result));
    }
    static void blocked(String code, Checked action) throws Exception {
        try {action.run();} catch(Exception e) {
            if(e.getMessage()!=null && e.getMessage().contains(code)){passed++;return;}
            throw new AssertionError("Expected "+code+", got "+e,e);
        }
        throw new AssertionError("Did not block: "+code);
    }
    public static void main(String[] args) throws Exception {
        blocked("EXACT_MODEL_REQUIRED",()->new DiagnosticEngine(graph(),new JSONObject(),refs()));
        blocked("EXACT_MODEL_REQUIRED",()->new DiagnosticEngine(graph(),vehicle().put("manufacturer","TOYOTA"),refs()));
        blocked("MODEL_OUT_OF_SCOPE",()->new DiagnosticEngine(graph(),vehicle().put("model","D30S-7"),refs()));
        blocked("VARIANT_OUT_OF_SCOPE",()->new DiagnosticEngine(graph(),vehicle().put("engine","D34"),refs()));
        blocked("EVIDENCE_UNVERIFIED",()->new DiagnosticEngine(graph(),vehicle(),new JSONObject()));
        JSONObject wrongRef=refs();wrongRef.getJSONObject("test-only").put("vehicle_scope",new JSONObject().put("manufacturer","TOYOTA").put("models",new JSONArray().put("8FBR")));
        blocked("EXACT_MODEL_REQUIRED",()->new DiagnosticEngine(graph(),vehicle(),wrongRef));
        JSONObject broken=graph();broken.getJSONObject("nodes").getJSONObject("q").getJSONArray("choices").getJSONObject(0).put("next","missing");
        blocked("broken next",()->new DiagnosticEngine(broken,vehicle(),refs()));
        JSONObject dead=graph();dead.getJSONObject("nodes").getJSONObject("q").put("choices",new JSONArray());
        blocked("DEAD_END",()->new DiagnosticEngine(dead,vehicle(),refs()));
        JSONObject cyclic=graph();cyclic.getJSONObject("nodes").getJSONObject("q").getJSONArray("choices").getJSONObject(0).put("next","q");
        blocked("CYCLE",()->new DiagnosticEngine(cyclic,vehicle(),refs()));
        JSONObject terminal=graph();terminal.getJSONObject("nodes").getJSONObject("r").put("choices",new JSONArray().put(new JSONObject().put("id","loop").put("next","q")));
        blocked("TERMINAL_HAS_CHOICES",()->new DiagnosticEngine(terminal,vehicle(),refs()));
        JSONObject missing=graph();missing.getJSONObject("nodes").getJSONObject("q").remove("tool");
        blocked("CONTRACT_MISSING",()->new DiagnosticEngine(missing,vehicle(),refs()));
        DiagnosticEngine engine=new DiagnosticEngine(graph(),vehicle(),refs());
        blocked("SAFETY_NOT_ACKNOWLEDGED",()->engine.choose("yes"));
        engine.acknowledgeSafety(true);
        blocked("unknown choice",()->engine.choose("no"));
        if(!engine.currentId().equals("q"))throw new AssertionError("Failure advanced state");passed++;
        engine.choose("yes");if(!engine.isTerminal())throw new AssertionError("Terminal not reached");passed++;
        blocked("TERMINAL_STOP",()->engine.choose("yes"));
        JSONObject snapshot=graph();DiagnosticEngine immutable=new DiagnosticEngine(snapshot,vehicle(),refs());
        snapshot.getJSONObject("nodes").getJSONObject("q").put("tool","");
        immutable.currentNode().put("tool","");immutable.currentNode();passed++;
        JSONObject target=graph();target.getJSONObject("nodes").getJSONObject("r").remove("teardown_gate");
        DiagnosticEngine atomic=new DiagnosticEngine(target,vehicle(),refs());atomic.acknowledgeSafety(true);
        blocked("CONTRACT_MISSING",()->atomic.choose("yes"));
        if(!atomic.currentId().equals("q"))throw new AssertionError("Invalid target advanced state");passed++;
        System.out.println("ENGINE CONTRACT PASS: "+passed+" synthetic assertions. Not terminal 30-scenario or Android runtime proof.");
    }
}
