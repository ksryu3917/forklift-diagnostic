#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/test_point_locator_v1.json'
E=ROOT/'app/src/main/assets/expert_diag_v2.json'
d=json.loads(P.read_text(encoding='utf-8'))
expert=json.loads(E.read_text(encoding='utf-8'))

def pt(id,label,where,connect,condition,expected='',decision='',source='OEM_EXACT',x=.5,y=.5,note=''):
    o={'id':id,'label':label,'where':where,'connect':connect,'condition':condition,'source_class':source,'x':x,'y':y}
    if expected:o['expected']=expected
    if decision:o['decision']=decision
    if note:o['note']=note
    return o

def grp(title,system,summary,tools,conditions,points,rules,images,diagram_note,source_refs,limitations=None,focus_ids=None):
    return {'title':title,'system':system,'summary':summary,'tools':tools,'conditions':conditions,'points':points,
            'decision_rules':rules,'oem_images':images,'diagram_note':diagram_note,'source_refs':source_refs,
            'limitations':limitations or [],'focus_ids':focus_ids or []}

# Explicitly distinguish post-access OEM assembly/confirmation values from pre-teardown field checks.
d['source_classes']['OEM_EXACT_TEARDOWN']='OEM exact 수치/방법이지만 분해·접근 후 확인/조립 단계. 분해 전 확정값으로 오인 금지'

# Upgrade hydraulic service-port information from visually verified SM1018-01 Fig 5-15/5-16.
h=d['groups']['HYD_MAIN_RELIEF']
h['tools']=['압력 점검 어댑터','압력 튜브','300 bar 압력계','유량계(유량 진단 시)','온도계']
h['conditions']=['차량을 평탄한 곳에 안전 고정','유압 잔압 해제 후 게이지 장착','작동유 정상 작동온도 50±5°C','릴리프 시험은 실린더 끝단에서 최소시간만 유지','호스·피팅 정격 준수']
for x in h['points']:
    if x['id']=='HY1':
        x.update(where='메인 컨트롤밸브 니플 어셈블리(1) · Fig 5-15',connect='압력 점검 어댑터/압력 튜브로 300 bar 압력계 연결',condition='작동유 50±5°C, 마스트를 최대 상승 위치까지 올린 뒤 레버를 유지하고 계기 판독',source_class='OEM_EXACT',expected='D20 181±3.5 bar / D25 195±3.5 bar / D30 215.5±3.5 bar / D33 240(+5,0) bar',note='Fig 5-15에서 니플 어셈블리(1)와 300bar 게이지 연결이 직접 확인됨')
    elif x['id']=='HY2':
        x.update(where='메인 컨트롤밸브 니플 어셈블리(1)에서 동일 300 bar 게이지 사용 · Fig 5-15/5-16',connect='압력 점검 어댑터/압력 튜브 + 300 bar 압력계',condition='작동유 50±5°C, 마스트를 최대 후경 위치까지 기울인 뒤 레버를 유지하고 계기 판독',source_class='OEM_EXACT',expected='D20/D25/D30/D33 모두 155±3.5 bar (2,225±50 psi)',note='보조 릴리프 조정은 Fig 5-16의 점너트(3)/조정나사(4) 절차. 진단 전 임의조정 금지')
h['oem_images']=['oem_pages/p198.jpg','oem_pages/p199.jpg','oem_pages/p200.jpg','oem_pages/p365.jpg']
h['source_refs']=['SM1018-01 §5-2-3 Fig 5-14~5-17','SM1018-01 hydraulic schematic D500093']
h['limitations']=['니플 어셈블리(1)의 나사 규격은 현재 자료에서 확정하지 않음. 임의 어댑터 규격 금지.','§5-2-1의 밸브 단품 사양과 §5-2-3의 차량 모델별 릴리프 시험값을 혼동하지 않는다.']

# Steering: service manual gives a physical gauge port but contains an internally inconsistent pressure/unit line.
st=d['groups']['STEERING_PRIORITY']
for x in st['points']:
    if x['id']=='ST3':
        x.update(label='스티어링 압력시험 포트(1)',where='스티어링 제어부 Fig 6-16의 포트(1) 플러그 위치',connect='플러그 제거 후 300 bar 압력계 연결',condition='작동유 정상 작동온도, 운전대를 좌/우 끝단까지 돌려 최소시간 판독',source_class='OEM_VERIFY',expected='매뉴얼 본문은 “90±3 kPa”와 “1,500~1,570 psi”를 함께 기재하여 단위/수치가 상충함',decision='물리 시험포트와 시험절차는 사용하되, 릴리프 판정값은 상충 원문을 최신 OEM 자료로 재확인하기 전 확정하지 않음',note='회로도에는 90 bar 표기도 존재. 본문 psi와 일치하지 않아 앱에서 임의 보정하지 않음')
st['oem_images']=['oem_pages/p303.jpg','oem_pages/p304.jpg','oem_pages/p365.jpg']
st['limitations']=['Fig 6-16 포트(1)+300bar 게이지 절차는 OEM 확인됨. 다만 릴리프 수치는 본문 단위/psi와 회로도 값이 상충하므로 OEM VERIFY로 유지.']

# Drive axle: pre-teardown localization first; exact backlash/preload/adjustment values are only used after access.
d['groups']['DRIVE_AXLE_MECH']=grp(
 '드라이브 액슬 · 허브/디퍼런셜/피니언 측정점','드라이브 액슬',
 '소음·누유·한쪽 휠 무구동을 곧바로 디퍼런셜 분해로 보내지 않는다. 외부 오일/브리더/허브유격/입력피니언/좌우 회전 비교로 먼저 위치를 좁힌 뒤, 분해가 허용된 경우에만 백래시·베어링 예압·치면패턴 OEM 수치를 사용한다.',
 ['다이얼 게이지','다이얼 토크 렌치','토크렌치','오일 샘플 트레이/자석','잭/잭스탠드','기어 치면 패턴 점검재'],
 ['차량 평탄 고정 및 구동륜 안전 지지','외부 점검은 오일 누유/브리더/허브/입력요크 순서','좌우 회전 비교는 반대측 구속·차동작용을 고려','DA6~DA9는 분해/접근 후 확인값이며 분해 전 판정값으로 사용 금지'],
 [
  pt('DA1','오일 레벨·사양·브리더','드라이브 액슬 하우징 주입/레벨부와 에어브리더','레벨/유종/브리더 통기 확인','냉간 정지, 평탄면','OEM 지정 레벨/유종을 사용하고 과충전 금지','부족/과다/오유종/브리더 막힘을 먼저 교정한 뒤 누유·소음 재현','OEM_FUNCTION_EXACT',.50,.68),
  pt('DA2','드레인 오일/금속분','액슬 하우징 배출유','깨끗한 트레이에 일부 채취, 자석/육안 비교','이상음 재현 후 정지','','금속편/과다 분진이 있으면 기어·베어링 내부손상 가능성 상승','FIELD_METHOD',.48,.77),
  pt('DA3','입력 요크/피니언','드라이브 액슬 중앙 입력요크와 피니언축','손회전/축·반경 유격/국부소음 비교','중립, 차량 완전 고정','','입력부에서 유격/거친 회전이 집중되면 피니언 베어링/기어계통 쪽으로 좁힘','FIELD_ISOLATION',.50,.38),
  pt('DA4','좌측 허브/휠베어링','좌측 전륜 허브','12-6시/3-9시 유격 + 손회전 drag/noise','좌측 휠 부상, 안전지지','','좌측에서만 유격/거친회전이 재현되면 중앙 디퍼런셜보다 좌측 허브/베어링 우선','FIELD_ISOLATION',.20,.58),
  pt('DA5','우측 허브/휠베어링','우측 전륜 허브','12-6시/3-9시 유격 + 손회전 drag/noise','우측 휠 부상, 안전지지','','우측에서만 유격/거친회전이 재현되면 중앙 디퍼런셜보다 우측 허브/베어링 우선','FIELD_ISOLATION',.80,.58),
  pt('DA6','휠베어링 너트 조정','허브 베어링 잠금너트','토크렌치 + 허브 베어링 잠금너트 인스톨러','허브 분해/재조립 단계','초기 135 N·m 조임 → 허브를 두드리고 수회 회전해 안착 → 잠금너트 탈거/와셔 설치 → 최종 50±5 N·m','조정 후 회전저항/유격을 재확인하고 잠금와셔 탭 고정','OEM_EXACT_TEARDOWN',.18,.73,'분해 전 외부 유격만으로 이 수치를 적용해 너트를 임의조정하지 않음'),
  pt('DA7','링기어-피니언 백래시','디퍼런셜 크라운휠/베벨피니언','다이얼 게이지','디퍼런셜 접근 후 크라운휠을 100° 회전시키며 여러 지점 측정','0.15~0.20 mm','범위 이탈 시 피니언/크라운휠 조정과 치면패턴을 함께 확인','OEM_EXACT_TEARDOWN',.47,.50),
  pt('DA8','피니언 베어링 롤링토크','요크/피니언 리테이너','다이얼 토크렌치','피니언 베어링 조정·조립 단계','1.5~2.0 N·m','2.0 N·m 초과면 shim 추가, 1.5 N·m 미만이면 shim 제거하여 예압 조정','OEM_EXACT_TEARDOWN',.56,.31,'요크/리테이너 임시 조임 180±15 N·m; 최종 Loctite 242 후 180±15 N·m 절차가 OEM에 기재됨'),
  pt('DA9','링기어 치면 접촉패턴','크라운휠 톱니','기어 치면 패턴 점검재','디퍼런셜 접근 후 크라운휠 회전','OEM 그림의 정상 접촉패턴과 비교','맞물림 깊이 과다/부족 패턴이면 피니언 깊이 조정 원인으로 확정','OEM_EXACT_TEARDOWN',.62,.46),
  pt('DA10','좌/우 차동 회전비교','좌·우 드라이브 샤프트/허브','한쪽 회전시키며 반대측/입력요크 반응 비교','양 휠 부상·안전지지, 변속 N','','한쪽만 전달 끊김/걸림이면 해당 샤프트·사이드기어 쪽, 양쪽 공통이면 중앙기어/입력쪽','FIELD_ISOLATION',.50,.60),
  pt('DA11','누유 시작점','허브 씰·피니언 씰·하우징 접합부','세척/건조 후 짧은 재운전, 최초 젖음점 추적','오일 레벨 정상화 후','','브리더/과충전 교정 후에도 동일 씰에서 최초 젖음이 재현되면 씰/축면 쪽','FIELD_METHOD',.69,.70),
  pt('DA12','휠 전달부/샤프트 체결','휠 스터드·허브·드라이브샤프트 전달부','체결/회전입력-출력 동시 관찰','휠 무구동 재현 또는 안전 부상','','입력은 도는데 허브출력이 없으면 샤프트/스플라인/허브기어; 허브는 도는데 휠이 안 돌면 스터드/휠 체결','FIELD_ISOLATION',.78,.72)
 ],
 ['오일/브리더/허브 외부점검에서 원인이 잡히면 디퍼런셜을 열지 않는다.','주행소음이 속도비례이고 입력요크에 집중되면 DA3→DA8/DA9로, 회전할 때만 나면 DA10으로 좌우 차동작용을 먼저 비교한다.','0.15~0.20 mm 백래시와 1.5~2.0 N·m 롤링토크는 디퍼런셜 접근 후의 OEM 확인값이며 “분해해야 할지” 결정하는 외부값이 아니다.'],
 ['oem_pages/p157.jpg','oem_pages/p160.jpg'],
 '중앙 디퍼런셜/입력피니언과 좌우 허브를 분리해 그린 위치도. 파란 포인트는 외부 격리, 녹색 OEM 수치는 분해 후 확인 단계로 구분한다.',
 ['SM1018-01 §3-4/3-5, Fig 3-24~3-25','SM1018-01 휠허브 베어링 재조립 절차'],
 ['축 길이/스플라인 치수의 정확 허용값은 현재 자료에서 확정되지 않아 비교/육안 단계까지만 사용.'],
 ['FRONT_DRIVE_AXLE','TRANSMISSION_CENTER'])

# Work equipment/control valve diagnostics.
d['groups']['WORK_EQUIPMENT_CONTROL']=grp(
 '작업장치 · 컨트롤밸브 스풀/릴리프/체크밸브','작업장치',
 '스풀 고착·복귀불량·마스트 역하강·지연급동작을 하나의 “밸브 불량”으로 묶지 않는다. 오일 상태→링케이지 분리→스풀 복귀→공통압력/보조압력→로드체크→필요 시 벤치누설 순서로 좁힌다.',
 ['300 bar 압력계','압력 점검 어댑터/압력 튜브','온도계','유량/누설 측정 장비(벤치 확인 시)','기본 수공구','깨끗한 오일 샘플 용기'],
 ['차량 안전고정·유압 잔압 해제','릴리프 압력시험 시 작동유 50±5°C','스풀 기계점검은 링크를 분리해 밸브 자체 복귀와 구분','WK7~WK11 누설수치는 밸브 단품/시험조건 확인용이며 실차 임의 유량누설 기준으로 사용 금지'],
 [
  pt('WK1','작동유 상태/기포/오염','작동유 탱크/리턴유 샘플점','온도계 + 투명 샘플 용기','증상 직후','릴리프 시험 표준온도는 50±5°C. 이것을 “허용 최고온도”로 오인 금지','기포/오염/점도 이상이 있으면 밸브 내부판정 전에 원인 제거','OEM_PLUS_FIELD',.18,.22),
  pt('WK2','메인 압력 · 니플(1)','컨트롤밸브 니플 어셈블리(1) Fig 5-15','300 bar 압력계','50±5°C, 마스트 최대 상승 후 레버 유지','D20 181±3.5 / D25 195±3.5 / D30 215.5±3.5 / D33 240(+5,0) bar','공통압력이 낮으면 체크/스풀 세부보다 펌프·메인릴리프/공급계통 우선','OEM_EXACT',.28,.50),
  pt('WK3','보조 릴리프 압력','동일 니플 어셈블리(1) 게이지','300 bar 압력계','50±5°C, 마스트 최대 후경 후 레버 유지','155±3.5 bar','메인압 정상 + 보조압만 낮으면 보조 릴리프/해당 섹션으로 좁힘','OEM_EXACT',.38,.48),
  pt('WK4','LIFT 링크/스풀 입력','컨트롤밸브 LIFT spool 외부 링크','링크 해제 전/후 수동 full stroke·중립복귀 비교','엔진 OFF, 잔압 해제','','링크 해제 후 정상복귀면 링크/정렬; 그대로 걸리면 스풀/몸체/오염 쪽','FIELD_ISOLATION',.52,.30),
  pt('WK5','TILT/AUX 링크/스풀 입력','TILT/AUX spool 외부 링크','링크 해제 전/후 수동 full stroke·중립복귀 비교','엔진 OFF, 잔압 해제','','특정 섹션만 걸리면 해당 스풀/링크/리턴스프링으로 좁힘','FIELD_ISOLATION',.60,.38),
  pt('WK6','스풀 자유행정/중립복귀','문제 섹션 스풀 끝단','링크 완전 분리 후 손으로 전행정/복귀 확인','엔진 OFF, 잔압 해제','','외부 링크가 없는 상태에서도 뻑뻑/복귀불량이면 스풀 휨·오염·몸체변형 가능성 상승','FIELD_ISOLATION',.67,.46),
  pt('WK7','LIFT spool 벤치 누설','LIFT spool section','시험 유량 수집','밸브 격리/시험장비에서 206 bar','최대 7 cc/min @ 206 bar','초과 시 LIFT spool/보어 마모를 분해 후 확정','OEM_EXACT_TEARDOWN',.72,.25),
  pt('WK8','TILT spool 벤치 누설','TILT spool section','시험 유량 수집','밸브 격리/시험장비에서 206 bar','최대 30 cc/min @ 206 bar','초과 시 TILT spool/보어 마모를 분해 후 확정','OEM_EXACT_TEARDOWN',.76,.34),
  pt('WK9','기타 spool 벤치 누설','AUX 등 기타 spool section','시험 유량 수집','밸브 격리/시험장비에서 137 bar','최대 30 cc/min @ 137 bar','초과 시 해당 spool/보어 마모 확인','OEM_EXACT_TEARDOWN',.80,.43),
  pt('WK10','Load check 누설','문제 섹션 load check/포펫','시험 유량 수집 또는 부하 hold 비교','밸브 격리시험 137 bar / 실차는 부하 hold 비교','OEM 단품시험 최대 50 cc/min @ 137 bar','마스트 역하강이 load check 격리/세척 후 사라지면 check seat/poppet 원인 확정','OEM_PLUS_FIELD',.69,.64),
  pt('WK11','Tilt lock 누설','Tilt lock valve','시험 유량 수집','밸브 격리시험 137 bar','최대 246 cc/min @ 137 bar','틸트 drift가 해당 회로 격리에서 사라지면 tilt lock 계통으로 좁힘','OEM_EXACT_TEARDOWN',.78,.61),
  pt('WK12','밸브 장착/몸체 뒤틀림','컨트롤밸브 장착볼트/브래킷','장착응력 해제 전후 스풀 복귀 비교','엔진 OFF, 잔압 해제','','고정 응력을 정상화했을 때만 스풀 복귀가 회복되면 장착/몸체 뒤틀림 가능성 높음','FIELD_METHOD_OEM_VALUE_VERIFY',.50,.72,'정확 장착볼트 토크값은 현재 확보자료에서 미확정. 임의 토크값 금지'),
  pt('WK13','리턴 스프링','문제 spool return cap/spring','링크 분리 후 복귀력/좌우 또는 인접섹션 비교','엔진 OFF, 잔압 해제','','스풀 자체가 자유로운데 복귀력만 없으면 return spring/cap 쪽','FIELD_ISOLATION',.63,.74),
  pt('WK14','시일플레이트/밸브몸체 외부누유','밸브 section 접합부·seal plate·body','세척/건조 후 작동, 최초 젖음점 추적','정상 압력에서 짧게 재현','','접합부/플레이트에서 시작하면 느슨함·시일; body 금속에서 시작하면 crack 가능성','FIELD_METHOD',.42,.70)
 ],
 ['스풀 조작불량은 먼저 링크를 떼어 밸브 자체와 외부기구를 분리한다.','마스트가 LIFT 명령 중 하강하면 WK2 공통압력 확인 후 WK10 load check를 우선한다.','압력은 정상인데 중립복귀가 안 되면 릴리프를 만지지 말고 WK4~WK6/WK12/WK13으로 간다.','벤치 누설수치는 분해후 확인값이지 실차에서 임의로 “누유 허용치”로 적용하지 않는다.'],
 ['oem_pages/p188.jpg','oem_pages/p198.jpg','oem_pages/p199.jpg','oem_pages/p200.jpg'],
 '컨트롤밸브를 인렛→LIFT→TILT/AUX→아웃렛 순서로 단순화하고, 실제 진단은 링크/스풀/압력/체크/누설 포인트만 남긴다.',
 ['SM1018-01 §5-2-1 컨트롤밸브 사양','SM1018-01 §5-2-3 릴리프 압력 점검'],
 ['정확 밸브 장착볼트 토크는 현재 자료에서 확정되지 않음.','50±5°C는 릴리프 시험 조건이며 작동유의 고장/과열 한계값이 아님.'],
 ['HYD_CONTROL','MAST_FRONT'])

# Mast/cylinder localization.
d['groups']['MAST_CYLINDER_DIAG']=grp(
 '마스트 실린더 · 외부누유/내부누설/정렬/와이퍼','마스트',
 '로드부 누유와 내부누설을 구분하고, 내부누설은 OEM drift 시험으로 먼저 확인한 뒤 밸브회로와 실린더를 격리한다. 틸트로드 마모는 정렬값을 우선 확인한다.',
 ['줄자','온도계','안전 블록/클램프','유압 정격 캡/플러그(회로격리 시)','직선자/다이얼 게이지(필요 시)','깨끗한 오일 샘플 용기'],
 ['마스트/캐리지는 OEM 절차대로 기계적으로 안전 지지','가압라인을 하중 상태에서 임의로 풀지 않음','drift 시험 전 체인장력/틸트 정렬/힌지 체결 확인','로드/시일 외부누유는 세척·건조 후 재작동하여 최초 젖음점 확인'],
 [
  pt('MS1','로드/헤드 시일 외부누유','리프트/틸트 실린더 로드가 헤드를 통과하는 부위','세척/건조 후 얇은 종이/육안으로 최초 젖음점 확인','무부하→정상작동 반복','','헤드/로드 접점에서 직접 시작되면 head seal/wiper/rod 표면을 좁힘','FIELD_METHOD',.30,.42),
  pt('MS2','실린더 로드 표면/직진성','문제 실린더 로드 전행정','육안/직선자 또는 다이얼 비교','압력 해제·안전지지 후 로드 노출','스크래치·국부마모·휨 유무','한쪽 방향만 반복마모면 시일만 교환하기 전에 정렬/사이드로드 확인','FIELD_ISOLATION',.36,.58),
  pt('MS3','리프트 실린더 drift 시험','마스트/리프트 실린더 로드','줄자로 로드 수축거리 측정','정격하중, 작동유 45~55°C, 마스트 수직, 2.5 m 상승(불가시 최대), 10분','drift ≤100 mm / 10 min','초과하면 실린더 또는 컨트롤밸브 내부누설 가능. MS4로 격리','OEM_EXACT',.50,.35),
  pt('MS4','밸브 vs 실린더 회로 격리','문제 실린더 공급라인과 컨트롤밸브 사이','압력 해제 후 정격 캡/플러그로 구간 격리','마스트를 기계적으로 완전 지지한 뒤 안전 절차로 재시험','','격리 후 drift가 사라지면 밸브/체크측, 그대로면 실린더 내부누설 가능성 상승','FIELD_ISOLATION',.58,.48,'가압·하중 상태에서 라인을 풀어 확인하는 방식 금지'),
  pt('MS5','실린더 에어 배출 나사','스탠다드/2차 리프트 실린더 고정/배기 나사','OEM bleed 절차로 기포 확인','블리딩 완료 후','기포가 없어질 때까지 반복; 최종 고정나사 5~7 N·m','공기 제거 후에도 동일 증상이면 내부누설/기계정렬로 이동','OEM_EXACT',.44,.72),
  pt('MS6','틸트 실린더 좌/우 정렬','좌·우 틸트 실린더 로드/클레비스','양쪽 전행정/로드길이 비교','최대 후경/완전 신장 상태','완전히 펴졌을 때 두 실린더 로드 길이 차 ≤3.18 mm','범위 초과 또는 한쪽만 먼저 끝단 도달하면 정렬불량을 rod 편마모 원인으로 우선','OEM_EXACT',.64,.58),
  pt('MS7','작동유 오염 샘플','작동유 탱크/리턴유','투명 용기에 샘플 채취','증상 직후','','입자/수분/변색이 있으면 rod/seal 반복마모의 상류원인으로 기록','FIELD_METHOD',.22,.72),
  pt('MS8','와이퍼/이물 유입점','실린더 로드 입구 wiper ring','로드 청소 전후 이물 포획/립 손상 확인','압력 해제·로드 노출','','와이퍼 립 손상/이물 포획이 rod 흠집 위치와 일치하면 원인연계가 강함','FIELD_METHOD',.72,.72)
 ],
 ['외부누유는 MS1에서 시작점을 잡고 MS2/MS6으로 로드손상 원인을 분리한다.','내부누설 의심은 MS3 OEM drift를 먼저 하고, 초과 시 MS4로 밸브와 실린더를 가른다.','피스톤시일인지 보어 스코어인지 외부에서 구분 못 하면 “실린더 내부누설”에서 분해를 허용하고 분해 후 세부원인을 확인한다.'],
 ['oem_pages/p234.jpg','oem_pages/p235.jpg','oem_pages/p245.jpg','oem_pages/p246.jpg'],
 '마스트와 실린더를 단순화해 외부 시일/로드, drift 측정, 좌우 정렬, 회로 격리점만 표시한다.',
 ['SM1018-01 §5-3 틸트 실린더 정렬','SM1018-01 §5-3 스탠다드/2차 실린더 자연침하 시험'],
 ['100 mm/10min은 지정 시험조건에서의 OEM drift 기준. 무부하/다른 온도 결과에 그대로 적용하지 않는다.'],
 ['MAST_FRONT','HYD_CONTROL'])

# Parking brake exact adjustment and performance test.
d['groups']['PARK_BRAKE_ADJUST_TEST']=grp(
 '주차브레이크 · 레버/케이블/밴드 조정과 15% 성능시험','주차 브레이크',
 '주차브레이크가 안 들면 밴드부터 교환하지 않는다. 레버/케이블 실제 스트로크→밴드 조정나사→입력축 밴드 작동→정격하중 15% 경사 성능시험 순서로 확인한다.',
 ['토크렌치','기본 수공구','고임목','안전한 15% 시험경사(성능시험 시)'],
 ['주차브레이크 조정 중 차량 완전 고임','밴드/케이블 접근 시 플로어플레이트 제거 절차 준수','경사 성능시험은 안전통제된 장소에서 정격하중 사용','시험 중 주차브레이크가 듣지 않으면 운전브레이크를 사용할 수 있어야 함'],
 [
  pt('PB1','레버/스위치 작동점','운전석 주차브레이크 레버와 스위치','클릭수/스위치 변화/케이블 이동 동시 관찰','레버 해제→체결','스위치는 주차브레이크를 넣을 때 2~3번째 클릭에서 작동하도록 조정','스위치만 문제인지 실제 케이블/밴드 스트로크도 부족한지 분리','OEM_EXACT',.22,.28),
  pt('PB2','밴드 조정나사(4)','트랜스미션 입력축 브레이크밴드 조정부','토크렌치로 나사(4) 조정','주차브레이크 해제 후 조정','나사(4) 5.6~6.8 N·m 조임 → 1.2~1.5 바퀴 풀어 고정 후 너트(5) 조임','정확 조정 후에도 holding 부족이면 케이블 실제스트로크/밴드마모로 이동','OEM_EXACT',.68,.48),
  pt('PB3','제어 케이블 스트로크','레버↔트랜스미션 주차브레이크 케이블','레버 입력과 T/M측 레버 이동 동시 비교','해제→각 클릭 체결','','운전석 레버는 움직이는데 T/M측 이동이 늦거나 짧으면 cable/고정부 조정·고착 원인','FIELD_ISOLATION',.45,.40),
  pt('PB4','입력축 밴드 작동','트랜스미션 입력축 클러치팩 외주 브레이크밴드/레버','케이블 체결 시 캠/스트럿/밴드 조임 실제 이동 확인','차량 고임, 엔진 OFF','','케이블 스트로크 정상인데 밴드 조임이 부족/편마모면 band/캠/스트럿 내부로 좁힘','OEM_PLUS_FIELD',.76,.62),
  pt('PB5','15% 경사 성능시험','안전 통제된 15% 오르막','차량 자체 holding 확인','정격하중, 오르막 중간에서 서비스브레이크로 정지 후 주차브레이크 체결','차량이 움직이지 않아야 함','PB1~PB4 조정 정상인데 굴러가면 밴드마모/작동기구 내부고장 가능성 상승','OEM_EXACT',.50,.75)
 ],
 ['레버 감각만으로 밴드 상태를 판정하지 않고 PB3/PB4에서 실제 케이블과 밴드 움직임을 본다.','PB2 OEM 조정값을 먼저 맞춘 뒤 PB5 성능시험을 한다.','조정값 정상 + 케이블 전스트로크 정상 + 15% 시험 실패면 밴드 마모/내부작동기구 쪽으로 분해 게이트를 연다.'],
 ['oem_pages/p328.jpg','oem_pages/p329.jpg'],
 '운전석 레버→케이블→트랜스미션 입력축 브레이크밴드로 이어지는 기계경로와 조정/시험점만 표시한다.',
 ['SM1018-01 §7-3-3 조정','SM1018-01 §7-3-4 성능시험'],
 [],['COCKPIT_FRONT','TRANSMISSION_CENTER'])

# Map all expert causes. Keep existing detailed mappings, add all remaining systems.
cm=d.setdefault('cause_map',{})
for it in expert['items']:
    cid,sys,cause,sym=it['id'],it['system'],it.get('cause',''),it.get('symptom','')
    text=cause+' '+sym
    if sys=='드라이브 액슬':
        gid='DRIVE_AXLE_MECH'
        if any(k in cause for k in ['윤활제 부족','사양 불일치','오일 과다','윤활제 종류 오류','브리더']): ids=['DA1']
        elif '오일시일' in cause: ids=['DA1','DA11']
        elif '휠 베어링 조정' in cause: ids=['DA4','DA5','DA6']
        elif '휠베어링 풀림' in cause: ids=['DA4','DA5','DA6','DA12']
        elif '백래시' in cause: ids=['DA3','DA7','DA9']
        elif any(k in cause for k in ['드라이브기어/피니언 조정','피니언 또는 사이드 베어링']): ids=['DA3','DA8','DA7','DA9']
        elif any(k in cause for k in ['기어 손상','드라이브기어 치면']): ids=['DA2','DA3','DA7','DA9','DA10']
        elif any(k in cause for k in ['피니언기어/스파이더','사이드기어 타이트','피니언/사이드기어','스러스트와셔']): ids=['DA10','DA7','DA9']
        elif '축 길이' in cause: ids=['DA10','DA12']
        elif '스터드/너트' in cause: ids=['DA12']
        elif '디퍼런셜 사이드기어/피니언 파손' in cause: ids=['DA10','DA2','DA7','DA9']
        else: ids=['DA1','DA3','DA10']
        cm[cid]={'group':gid,'point_ids':ids}
    elif sys=='작업장치':
        gid='WORK_EQUIPMENT_CONTROL'
        if any(k in cause for k in ['작동유 과열','작동유 온도']): ids=['WK1']
        elif '작동유 이물질' in cause or '유로 이물질' in cause: ids=['WK1','WK6']
        elif '연결부 과다조임' in cause or '밸브 고정볼트' in cause or '밸브고정 볼트' in cause: ids=['WK12','WK6']
        elif '링케이지' in cause: ids=['WK4','WK5','WK6']
        elif '스풀 휨' in cause or '스풀 변형' in cause or '스풀 스트로크' in cause: ids=['WK4','WK5','WK6']
        elif '리턴스프링' in cause or '스프링 파손' in cause: ids=['WK6','WK13']
        elif '시일부 이물질' in cause or '시일플레이트' in cause or '시일 손상' in cause or '밸브몸체 크랙' in cause: ids=['WK14']
        elif '밸브스풀 과다마모' in cause: ids=['WK6','WK7','WK8','WK9']
        elif '체크밸브' in cause: ids=['WK2','WK10']
        elif '펌프 토출압' in cause or '릴리프밸브 손상' in cause or '릴리프밸브 비정상' in cause or '릴리프 컨트롤' in cause: ids=['WK2','WK3']
        elif '회로 공기혼입' in cause: ids=['WK1','WK2']
        else: ids=['WK1','WK2','WK6']
        cm[cid]={'group':gid,'point_ids':ids}
    elif sys=='마스트':
        gid='MAST_CYLINDER_DIAG'
        if '헤드 시일' in cause: ids=['MS1','MS2']
        elif any(k in cause for k in ['로드 과다마모','스크래치','휨']): ids=['MS1','MS2','MS6']
        elif '피스톤시일' in cause: ids=['MS3','MS4']
        elif '실린더 손상' in cause: ids=['MS2','MS3','MS4']
        elif '정렬 불량' in cause: ids=['MS2','MS6']
        elif '작동유 오염' in cause: ids=['MS7','MS1','MS8']
        elif '와이퍼링' in cause: ids=['MS8','MS1','MS2']
        elif '이물질 제거' in cause: ids=['MS8','MS2']
        else: ids=['MS1','MS3','MS6']
        cm[cid]={'group':gid,'point_ids':ids}
    elif sys=='주차 브레이크':
        gid='PARK_BRAKE_ADJUST_TEST'
        if '어셈블리 조정' in cause: ids=['PB1','PB2','PB4','PB5']
        elif '케이블' in cause: ids=['PB1','PB3','PB4','PB5']
        elif '밴드 마모' in cause: ids=['PB2','PB3','PB4','PB5']
        else: ids=['PB1','PB2','PB3','PB4','PB5']
        cm[cid]={'group':gid,'point_ids':ids}

# Expand system routing to all 9 manual diagnostic systems.
d['system_map'].update({
    '드라이브 액슬':'DRIVE_AXLE_MECH',
    '작업장치':'WORK_EQUIPMENT_CONTROL',
    '마스트':'MAST_CYLINDER_DIAG',
    '주차 브레이크':'PARK_BRAKE_ADJUST_TEST'
})
d['version']='1.1-v8.4-all-manual-testpoints'
d['rule']='첫 화면에서 부품번호보다 프로브/압력계/기계 측정 위치와 시험조건을 우선. 268개 모든 매뉴얼 원인에 원인별 포인트를 연결하고, 분해 전 격리값과 분해 후 OEM 확인값을 구분한다.'
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('groups',len(d['groups']),'points',sum(len(g['points']) for g in d['groups'].values()),'cause_map',len(d['cause_map']))
