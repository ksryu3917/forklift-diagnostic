import com.ryu.forkliftdiagnostic.engine.DiagnosticEngine;
import org.json.JSONObject;
import java.nio.file.Files;
import java.nio.file.Path;

/** Executes the shipped lamp graph; these four paths do not satisfy 30 conditions per terminal. */
public final class LampFlowTest {
    public static void main(String[] args) throws Exception {
        Path assets=Path.of("app/src/main/assets/v20");
        JSONObject graph=new JSONObject(Files.readString(assets.resolve("diagnostics/e_license_terminal_stop.json")));
        JSONObject refs=new JSONObject(Files.readString(assets.resolve("evidence_registry.json"))).getJSONObject("entries");
        JSONObject vehicle=new JSONObject().put("manufacturer","DOOSAN").put("model","D25S-7");
        String[][] paths={{"lamp_common","abnormal"},{"feed_fault","normal","absent"},
            {"ground_fault","normal","present","high"},{"bulb_socket","normal","present","normal"}};
        for(String[] path:paths){
            DiagnosticEngine engine=new DiagnosticEngine(graph,vehicle,refs);
            for(int i=1;i<path.length;i++){
                String before=engine.currentId();
                try{engine.choose(path[i]);throw new AssertionError("Safety bypass");}
                catch(IllegalStateException expected){if(!expected.getMessage().equals("SAFETY_NOT_ACKNOWLEDGED"))throw expected;}
                if(!before.equals(engine.currentId()))throw new AssertionError("Rejected action advanced graph");
                engine.acknowledgeSafety(true);engine.choose(path[i]);
            }
            if(!engine.isTerminal()||!path[0].equals(engine.currentId()))throw new AssertionError("Wrong terminal");
            try{engine.choose("normal");throw new AssertionError("Terminal did not stop");}
            catch(IllegalStateException expected){if(!expected.getMessage().equals("TERMINAL_STOP"))throw expected;}
            System.out.println("SHIPPED LAMP PATH PASS: "+path[0]);
        }
        System.out.println("4 actual graph paths passed; NOT 30-condition coverage or field/runtime verification.");
    }
}
