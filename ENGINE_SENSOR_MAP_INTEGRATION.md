# D24NAP sensor location map integration

Add `EngineSensorMapActivity` to the Android manifest as a non-exported activity:

```xml
<activity android:name=".EngineSensorMapActivity" android:exported="false" />
```

`ElectricalDiagnosticActivity` now shows **D24 센서 위치 / 핀맵** for D24 graphs. The map intentionally uses a technician-oriented pseudo-isometric zone view rather than copying the OEM page. Each item retains the OEM §12-3 callout number and the sensor/ECU pin data that is confirmed in 950106-01198.

The map is not a dimensional CAD model. Exact mounting position remains tied to the OEM numbered location figure and engine specification variant.
