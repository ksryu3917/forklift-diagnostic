# 지게차정비프로그램 V20 — 단일 마스터 요구사항

## 목적

현장 정비사가 스마트폰/태블릿에서 오프라인으로 사용하는 진단·학습 앱.
매뉴얼 내용을 보기 좋게 요약하는 앱이 아니라,
**분해 전에 현장에서 원인을 확인·배제·격리·확정하는 앱**이 핵심이다.

## 절대 원칙

1. 매뉴얼/OEM 근거 우선.
2. 확인 불가 수치·핀·포트·절차 추정 금지.
3. 차량/제조사/모델 scope를 넘겨 수치나 절차를 재사용하지 않는다.
4. 진단은 한 번에 한 점씩.
5. 부품번호/가격은 진단 완료 뒤.
6. 실제 측정 위치·공구·조건·판정근거가 없는 원인은 완료로 치지 않는다.
7. static validator와 실제 runtime 검증을 분리한다.
8. 논리 시뮬레이션은 실차 검증이 아니다.
9. 실제 현장 사례에서 누락이 발견되면 해당 범주를 COMPLETE에서 즉시 강등하고 P0 회귀사례로 추가한다.
10. 여러 overlay를 누적 적용하는 개발방식을 중단하고 단일 schema/단일 상태파일/단일 진단엔진으로 간다.

## 유지해야 할 기존 자산

- D20/25/30/33S(SE)-7 기존 매뉴얼 정규화 자산
- 64 symptoms / 268 causes 역사적 coverage
- transmission 24 graph / 151 result
- electrical 38 graph / 205 result
- D24 engine 21 graph / 110 result
- test point / field location / measurement worksheet
- brake hydraulic isolation
- 번호판등 terminal-stop
- pinch zoom / pan / double tap
- manual library 169-record catalog 역사
- 다중 제조사 선택
- STUDY A-Z 구조
- 전동/리치·배터리 학습 및 현장진단 요구
- 정비이력 / 현장경험 / 부품·가격·공임 DB

숫자는 새 schema migration 후 다시 산출한다.
기존 숫자를 맞추기 위해 빈 항목/중복 항목을 만들지 않는다.

## 홈

현재 차량 카드는 항상 제조사+모델을 표시한다.
차량 선택은 진단보다 앞선다.
어디서든 홈으로 돌아갈 수 있어야 한다.

## 진단 러너

각 단계:
- 지금 확인할 것
- 위치
- 공구
- 안전조건
- 작동조건
- 측정/행동
- 정상/이상 판정 근거
- 사용자가 입력할 값 또는 PASS/FAIL
- 다음 단계 1개
- 왜 이 검사를 하는지
- 근거 보기

결과:
- 현재까지 배제된 것
- 강하게 의심되는 범위
- 아직 확정할 수 없는 것
- 분해 가능 조건
- 분해 후 확인할 것
- 정비 방법
- 부품/가격/공임

## 전장

- 무부하 전압만으로 배선 정상 판정 금지.
- 필요한 곳은 loaded voltage drop.
- 퓨즈/컨택터/커넥터/접지/5V ref/CAN/입력/출력 분리.
- AC 모터 U/V/W를 일반 멀티미터 단일 전압값으로 합격/불합격 판정하지 않는다.
- 절연시험은 컨트롤러/센서 분리 및 OEM 시험전압 확인 후.
- 엔코더는 전원/GND/센서측 신호/컨트롤러측 신호로 나눈다.
- 실제 온도와 진단기 온도 불일치 시 센서/배선 분기.

## 전동/리치

최소 계통:
- traction power
- pump/hydraulic power
- EPS
- VCU
- main fuse / contactor
- DC/DC
- battery / BDI / charger
- traction motor / pump motor
- encoder/speed/temp sensor
- drive unit / reduction gear / axle / hub
- electromagnetic brake
- CAN
- safety interlock

육안 식별은 외형 단정이 아니라 `명판 + 굵은 전력선 추적 + 출력 대상 추적`을 기본으로 한다.

## 배터리

학습과 진단을 분리하되 서로 연결한다.
- 전체전압
- DC 전류
- 부하 중 voltage sag
- 셀별 전압
- 비중
- 온도
- 연결바/단자 전압강하
- 실제 사용량/Ah
- 차량 과전류 소비와 배터리 용량저하 분리

"48V니까 몇 V 이하면 불량" 같은 범용 숫자판정 금지.
배터리 제조사/형식/정격비중/온도 기준을 우선한다.

## STUDY

전동·리치에서 실제 업무를 A-Z로 학습 가능해야 한다.
예:
- 배터리 기본/충전/교환
- 컨택터
- 컨트롤러
- AC/DC/PM motor
- encoder
- U/V/W
- insulation
- CAN
- charger
- BDI
- EPS
- pump
- electromagnetic brake
- drive unit
- 실제 고장사례

글만 길게 보여주지 않는다.
한눈에 보는 재작성 그림 → 위치 → 측정 → 실제 사례 → 퀴즈 순서를 우선한다.

## 매뉴얼 라이브러리

문서가 검색된다는 사실과 모델별 정규화 완료를 분리한다.
다른 제조사 문서가 catalog에 있어도 기존 두산 그래프와 자동 연결하지 않는다.
브로셔/제원표를 서비스 절차 근거로 쓰지 않는다.

## 데이터 provenance

모든 numeric limit / pin / connector / torque / procedure는 evidence_ref를 가져야 한다.
근거가 없으면 `OEM_VERIFY` 또는 comparison/isolation로 남긴다.
D34 데이터를 D24 전용값처럼 사용하지 않는다.
Toyota 8FBR처럼 brochure/reference 수준만 있는 경우 procedure를 발명하지 않는다.

## 오프라인

현장 진단은 네트워크 없이 실행 가능해야 한다.
매뉴얼 원문 전체가 APK 용량상 포함되지 않더라도,
정규화된 진단/도면/근거 위치 정보는 오프라인에서 동작해야 한다.
