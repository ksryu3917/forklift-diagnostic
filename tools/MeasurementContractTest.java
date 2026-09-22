import com.ryu.forkliftdiagnostic.engine.DiagnosticEngine;
import org.json.*;

/** Synthetic numbers in this file are not field/OEM thresholds. */
public final class MeasurementContractTest {
    static JSONObject graph() throws Exception {
        JSONObject g=EngineContractTest.graph(),nodes=g.getJSONObject("nodes"),n=nodes.getJSONObject("q");
        JSONObject result=nodes.getJSONObject("r");nodes.remove("r");
        JSONArray branches=new JSONArray();
        for(String outcome:new String[]{"low","normal","high"}){
            nodes.put(outcome,new JSONObject(result.toString()));
            branches.put(new JSONObject().put("id","next_"+outcome).put("next",outcome));
        }
        n.put("type","measure").put("unit","synthetic-unit").put("min",10).put("max",20).put("result_branches",branches).put("choices",new JSONArray());
        return g;
    }
    static DiagnosticEngine engine(JSONObject g)throws Exception{return new DiagnosticEngine(g,EngineContractTest.vehicle(),EngineContractTest.refs());}
    public static void main(String[] args)throws Exception{
        double[] values={Math.nextDown(10.0),10,15,20,Math.nextUp(20.0)};
        String[] expected={"low","normal","normal","normal","high"};
        for(int i=0;i<values.length;i++){
            DiagnosticEngine e=engine(graph());e.acknowledgeSafety(true);e.submitMeasurement(values[i],"synthetic-unit");
            if(!e.isTerminal()||!expected[i].equals(e.currentId()))throw new AssertionError("Boundary "+values[i]);
        }
        DiagnosticEngine e=engine(graph());
        EngineContractTest.blocked("SAFETY_NOT_ACKNOWLEDGED",()->e.submitMeasurement(15,"synthetic-unit"));
        e.acknowledgeSafety(true);
        EngineContractTest.blocked("UNIT_MISMATCH",()->e.submitMeasurement(15,"bar"));
        EngineContractTest.blocked("NONFINITE_MEASUREMENT",()->e.submitMeasurement(Double.NaN,"synthetic-unit"));
        EngineContractTest.blocked("NONFINITE_MEASUREMENT",()->e.submitMeasurement(Double.POSITIVE_INFINITY,"synthetic-unit"));
        EngineContractTest.blocked("MEASUREMENT_REQUIRED",()->e.choose("next_normal"));
        if(!"q".equals(e.currentId()))throw new AssertionError("Rejected input advanced state");
        JSONObject wrong=graph();wrong.getJSONObject("nodes").getJSONObject("q").put("min",30);
        EngineContractTest.blocked("INVALID_MEASUREMENT_RANGE",()->engine(wrong));
        JSONObject branch=graph();branch.getJSONObject("nodes").getJSONObject("q").getJSONArray("result_branches").getJSONObject(0).put("next","missing");
        EngineContractTest.blocked("broken next",()->engine(branch));
        JSONObject target=graph();target.getJSONObject("nodes").getJSONObject("normal").remove("teardown_gate");
        DiagnosticEngine atomic=engine(target);atomic.acknowledgeSafety(true);
        EngineContractTest.blocked("CONTRACT_MISSING",()->atomic.submitMeasurement(15,"synthetic-unit"));
        if(!"q".equals(atomic.currentId()))throw new AssertionError("Invalid target advanced state");
        System.out.println("MEASUREMENT CONTRACT PASS: 5 boundary outcomes, 8 rejection checks, 2 atomic-state checks; synthetic only.");
    }
}
