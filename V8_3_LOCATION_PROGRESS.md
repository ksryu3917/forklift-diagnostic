# V8.3 · Technician Location Map

## 목적
진단 결과보다 먼저 정비사가 **어디로 가서 어디에 프로브/압력계를 대야 하는지** 찾게 한다. 품번은 진단 완료 뒤 참고정보로 유지한다.

## 추가
- 차량 전체 정비 위치맵 `field_location_map_v1.json`
- 전장 38개 그래프 전부 물리 점검 zone 연결
- 기존 전문가 진단 9개 시스템 전부 위치 zone 연결
- START 무크랭킹: 배터리/엔진룸/시트하부 릴레이/키스위치 위치를 한 화면에 강조
- OSS: 시트/OSS + 퓨즈/릴레이 + 유압 리프트락 위치 강조
- A/C 팬: A/C 옵션구역 + 엔진룸 + 릴레이구역 강조
- 브레이크: 페달/마스터 + 유압제어 + 전륜 드라이브액슬 강조

## 위치정확도 원칙
- 맵 자체는 빠른 접근용 재작성 그림이며 치수도가 아니다.
- OEM 확인 버튼에서 해당 Parts Book exploded view / service evidence를 연다.
- 옵션/Serial에 따라 위치가 달라질 수 있는 항목은 OPTION_DEPENDENT로 표시한다.
- 정확 장착 근거가 없는 항목은 zone만 표시하고 숫자핀/치수/정확좌표를 만들지 않는다.

## V8.3.1 · cause-specificity / D24 위치 근거뷰
- 전체 268 원인의 `field_sequence + measurement_points + confirm_if + disassembly_gate` 중복을 별도 감사한다.
- 같은 원인의 다중 증상 재사용은 허용하지만, 서로 다른 원인이 동일 전체 진단체인을 공유하면 `cross-cause shared`로 남긴다.
- 가장 큰 T/M 인칭/모듈밸브 family 13개에 **원인별 pre-teardown 분리시험**을 추가했다.
- 현재 cross-cause 동일 전체 진단체인: 98 causes / 32 groups. 이 수치는 숨기지 않고 다음 보강목록으로 사용한다.
- D24 Parts Book p211의 실제 두 엔진 방향에서 필요한 부분만 잘라 `parts_p211_viewA/B` 근거뷰를 만들었다. 기본 화면은 재작성 아이소메트릭이고, 정확 Parts Book item이 확인된 BPS/CAM/WTS/OPTS/MAF에만 해당 방향 근거뷰 버튼을 제공한다.
- `validate_engine_sensor_locator.py`, `validate_diagnostic_specificity.py`, `build_field_readiness_v7.py`를 CI gate에 추가했다.
