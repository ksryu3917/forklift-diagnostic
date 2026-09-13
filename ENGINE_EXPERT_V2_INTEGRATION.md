# D24 Engine Expert V2 integration

Add to `app/src/main/AndroidManifest.xml` inside `<application>`:

```xml
<activity android:name=".EngineExpertDiagnosticActivity" android:exported="false" />
<activity android:name=".EngineSensorMapActivity" android:exported="false" />
```

From Home, replace the temporary D34 engine entry with a launch button to `EngineExpertDiagnosticActivity` for D24NAP-equipped D20/25/30/33S(SE)-7.

Assets:
- `engine_diag_d24_v2.json` — 21 field-executable benchmark symptom graphs
- `engine_sensor_map_d24_v1.json` — pseudo-isometric sensor locator + OEM callout/pins

Display rule:
1. show fault-specific redrawn path first;
2. show immediate measurement points;
3. provide sensor location/pin map in one tap;
4. raw OEM evidence is secondary;
5. never invent OEM thresholds.
