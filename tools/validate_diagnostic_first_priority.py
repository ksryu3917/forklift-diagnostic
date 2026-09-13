from pathlib import Path
R=Path(__file__).resolve().parents[1]
J=R/'app/src/main/java/com/ryu/forkliftdiagnostic'
def ok(cond,msg):
    if not cond: raise SystemExit('FAIL: '+msg)
expert=(J/'ExpertDiagnosticActivity.java').read_text()
engine=(J/'EngineExpertDiagnosticActivity.java').read_text()
elec=(J/'ElectricalDiagnosticActivity.java').read_text()
smap=(J/'EngineSensorMapActivity.java').read_text()
parts=(J/'PartsReferenceActivity.java').read_text()
ok('품번은 후순위' in expert,'expert parts button must be secondary')
ok('품번은 후순위' in engine,'engine parts button must be secondary')
ok('품번은 후순위' in elec,'electrical parts button must be secondary')
ok('주문은 차대번호 기준 부품점 확인' in smap,'sensor map part numbers must be reference-only')
ok('정비 우선순위' in parts and '실제 주문은 차대번호 기준' in parts,'parts screen must state diagnostic-first policy')
ok(engine.find('이 증상 관련 센서 위치 / 핀맵') < engine.find('품번은 후순위'),'engine sensor/location must precede parts')
print('DIAGNOSTIC-FIRST UI PRIORITY: PASS')
