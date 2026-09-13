# V8.4 Test-point Locator Progress

## What changed
The app now has a dedicated technician measurement-point layer between diagnosis and parts information. It is designed around the question: **where exactly should I put the probe/gauge next?**

### Added locator groups
- Transmission pressure taps (Tap1~Tap7)
- Service-brake master/left-right axle isolation and bleed points
- Main hydraulic relief / tilt-AUX relief and flow points
- Steering priority / LS / cylinder comparison points
- Intermittent no-crank loaded voltage-drop points
- OSS controller-health points (power, seat input, 5V, CAN, output)
- A/C condenser-fan electrical points

## OEM exact data newly normalized
### Transmission
- Gauge: 0–20.5 bar (0–300 psi)
- T/M oil temperature: 49–71°C
- Tap4: forward clutch; Tap5: reverse clutch; Tap7: lubrication; Tap3: converter charge; Tap2: converter outlet/cooler inlet; Tap6: main/pump; Tap1: comparison point
- Main line N: 8.3–10.3 bar idle / 9.0–11.0 bar at 2,000 rpm
- F/R clutch: 7.3–8.6 bar idle / 7.3–9.7 bar at 2,000 rpm
- Lube N: 0.1–0.7 / 2.4–3.5 bar
- Converter charge N: 0.7–1.4 / 5.9–8.0 bar
- Converter outlet/cooler inlet N: 0.3–0.6 / 2.5–4.0 bar

### Hydraulic
- Main relief: D20 181±3.5 bar; D25 195±3.5; D30 215.5±3.5; D33 240(+5,0) bar
- Tilt/AUX relief: 155±3.5 bar
- Tilt flow: 28±2 LPM; AUX1: 26±2 LPM
- Exact gauge-port identity remains source-limited where SM does not identify one unique external port.

### Brake
- Master pushrod stroke 32.5 mm; displacement 18 cc; relief cracking 40 bar; supply approximately 0.8 GPM.
- `40 bar` is explicitly blocked from being used as a piston-seal leakage threshold.
- OEM bleed sequence and left/right drive-axle bleed locations are linked.

## Validation
See `build/reports/test_point_locator_v84.md`.
