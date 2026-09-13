# V8.5 ENGINE TESTPOINT · 진행/검증 보고서

## 이번 단계 핵심

- 부품번호보다 **실제 측정 위치/시험상태/격리결과**를 우선하는 UI 유지.
- 기존 9개 수동 정비계통 전부의 원인별 측정포인트 연결을 UI까지 완료.
- D24 엔진 21개 실행그래프 전부에 전용 측정포인트 화면 연결.
- 엔진 측정포인트 화면에서 곧바로 센서 위치맵으로 이동하도록 연결.
- GitHub Actions의 오래된 V8.3.1 release assertion을 V8.5로 갱신하고 test-point validator를 필수 단계로 추가.

## 측정포인트 DB

- Groups: **23**
- Measurement / isolation points: **147**
- Manual expert causes mapped: **268 / 268**
- Manual systems mapped: **9 / 9**
- D24 engine graphs mapped: **21 / 21**
- Test-point validator: **0 errors / 0 warnings**

### Manual systems

- Transmission 92 causes
- Drive axle 20
- Hydraulic 27
- Work equipment 26
- Mast 8
- Steering 38
- Brake 45
- Parking brake 3
- A/C 9

### D24 engine test families

- ECU power/GND/CAN/VREF
- 5V VREF branch isolation
- Crank/no-start / hard-start / stall composite
- Rail pressure / RPS / low-pressure fuel / IMV / return
- CRK/CAM synchronization
- Injector electrical / current / return / compression
- MAF / BPS / charge-air / EGR
- Cooling / WTS / actual-temperature comparison
- Lubrication / OPTS / mechanical gauge separation
- Preheat / air-heater loaded circuit
- Low-power / rough-idle / smoke combustion separation

## Numeric anti-fabrication gates retained

- No invented crank-start minimum rail MPa.
- No invented injector-return cc/min threshold.
- No invented general voltage-drop mV threshold where OEM does not provide one.
- D24 mechanical oil-pressure port remains OEM VERIFY until exact port/thread/spec is confirmed.
- Steering manual's internally inconsistent pressure/unit line remains OEM VERIFY instead of silently corrected.
- A/C condenser-fan exact relay ID/cavity remains source-limited.

## Regression validation

All existing validators pass:
- field executable: 64 symptoms / 268 causes / 8,040 cause simulations / 0/0
- transmission: 24 graphs / 151 results / 4,530 simulated result paths / 0/0
- electrical: 38 graphs / 373 nodes / 205 results / 6,150 simulations / 0/0
- expert specificity: unresolved cross-cause shared chain 0
- D24 engine: 21 graphs / 110 results / 3,300 simulations / 0/0
- parts links: 268 expert / 38 electrical / 21 engine / 0/0
- field location map: electrical 38/38, expert systems 9/9
- engine sensor locator: 18 sensors/actuators
- test-point locator: 23 groups / 147 points / expert 268/268 / engine 21/21 / 0/0

## Build identity

- versionCode: `30`
- versionName: `0.18-rc-expert-v8.5-engine-testpoint`
- state: `RC EXPERT V8.5 ENGINE TESTPOINT`
- local patch SHA marker: `UNSTAMPED_LOCAL_PATCH` until Work applies the exact commit and Actions stamps `${github.sha}`.

## Local compile note

The current patch workspace does not contain the Android SDK/runtime classes. A `javac` parse pass was run without `android.jar`; it reports expected missing Android symbols but **no syntax-like parse errors**. The authoritative Android build remains the GitHub Actions build from the exact Work-applied commit.
