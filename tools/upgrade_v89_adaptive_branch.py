import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
asset=ROOT/'app/src/main/assets/test_point_locator_v1.json'
d=json.loads(asset.read_text(encoding='utf-8'))

def rule(i, when, title, assessment, next_points=None, excludes=None, caution='', level='NARROWED'):
    return {
        'id': i, 'when': when, 'title': title, 'level': level,
        'assessment': assessment,
        'excludes': excludes or [], 'next_points': next_points or [],
        'caution': caution,
    }

def set_rules(gid, rules, note):
    g=d['groups'][gid]
    g['adaptive_branch']={
        'mode':'ordered_first_match',
        'rule':'여러 측정결과 조합으로 배제된 구간과 다음 한 점을 좁힌다. 단일 FAIL을 부품확정으로 오인하지 않는다.',
        'note':note,
        'rules':rules,
        'fallback':{'strategy':'first_unresolved_visible','title':'아직 조합판정 전','assessment':'현재 화면에서 아직 판정하지 않은 다음 측정포인트부터 진행한다.'}
    }

set_rules('START_VDROP',[
 rule('ST_BAT','S1 FAIL'.replace(' ',''), '', '')
], '')
# rewrite with dict helpers below (above placeholder removed)
d['groups']['START_VDROP'].pop('adaptive_branch',None)
set_rules('START_VDROP',[
 rule('ST01',{'S1':'FAIL'},'배터리/SOC·포스트 자체부터','START 부하에서 배터리 납 포스트 자체가 무너진다. 하류 케이블/릴레이를 판정하기 전에 배터리 상태·충전상태·포스트 접촉을 해결한다.',[],['스타터 B+ 이후 하류 부품은 아직 확정 불가'],'외부점프로 걸렸다는 사실만으로 배터리 단독고장으로 끝내지 말고 재현상태에서 기록.', 'UPSTREAM'),
 rule('ST02',{'S1':'PASS','S2':'FAIL'},'메인 B+ 경로 고저항','배터리 포스트는 유지되는데 스타터 B+에서만 부하전압이 무너진다. +케이블/단자/크림프/분기 접속부를 우선한다.',[],['배터리 내부','ST 제어회로'],'케이블을 이미 교환했어도 실패 순간 양 끝 전압강하로 확인.', 'ISOLATED'),
 rule('ST03',{'S1':'PASS','S2':'PASS','S4':'FAIL'},'스타터/엔진 접지 경로 고저항','B+ 공급은 유지되지만 스타터 케이스 기준 접지 전압강하가 비정상이다.',[],['배터리 +경로','ST 스위치회로'],'추가 접지선을 달았다는 사실보다 실패 순간 battery− post↔starter case drop을 우선.', 'ISOLATED'),
 rule('ST04',{'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'FAIL'},'START relay #8 접점/소켓 구간','메인 B+/GND는 유지되고 ST가 무너지며 relay 부하 입력/출력 비교가 비정상이다.',[],['배터리','메인 +케이블','엔진접지','스타터 주전원'],'릴레이 자체와 소켓 암단자 장력/크림프를 함께 확인.', 'ISOLATED'),
 rule('ST05',{'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'PASS','S6':'FAIL'},'릴레이 코일명령 상류','relay 접점 경로는 정상인데 코일 명령이 실패한다. KEY ST/N/OSS/interlock 상류를 좁힌다.',['S7'],['스타터 주회로','relay 부하접점'],'간헐 인터록이면 흔들림/좌석/중립 조건을 재현하며 측정.', 'NARROWED'),
 rule('ST06',{'S1':'PASS','S2':'PASS','S4':'PASS','S3':'FAIL','S5':'PASS','S6':'PASS'},'relay→ST 하네스/단자 구간','relay 입력·출력과 코일명령은 정상인데 스타터 ST에서만 전압이 무너진다.',[],['배터리','메인 B+/GND','relay 접점','relay coil control'],'relay 출력단에서 스타터 S단까지 구간별 부하전압강하로 찾는다.', 'ISOLATED'),
 rule('ST07',{'S1':'PASS','S2':'PASS','S4':'PASS','S3':'PASS'},'전기 주공급/START 명령은 현재 정상','실패 순간 B+, GND, ST가 모두 유지된다면 현재 전기 공급경로만으로 무크랭킹을 설명하기 어렵다.',[],['메인 B+ 고저항','접지 고저항','ST 제어전압 부족'],'스타터 솔레노이드 기계작동/피니언·링기어/전류파형 또는 증상 재현조건을 확인.', 'DOWNSTREAM')
], '무크랭킹은 배터리→주전원/접지→ST→relay 부하/코일 순으로 구간을 자른다.')

set_rules('EL_CHARGE',[
 rule('CH01',{'CH3':'FAIL'},'알터네이터 B+→배터리 + 경로','발전기 B+와 배터리 + 사이 부하 전압강하가 비정상이다.',[],['알터네이터 내부를 먼저 교환할 근거'],'케이블/터미널/분기 접속부를 찾는다.','ISOLATED'),
 rule('CH02',{'CH3':'PASS','CH4':'FAIL'},'알터네이터 케이스→배터리 − 접지 경로','양(+) 충전경로는 정상인데 접지 귀환 전압강하가 비정상이다.',[],['B+ 케이블 경로'],'엔진블록/차체/배터리− 접지 체결을 부하상태에서 확인.','ISOLATED'),
 rule('CH03',{'CH3':'PASS','CH4':'PASS','CH2':'FAIL'},'알터네이터 출력/여자 제어 쪽','충전 주케이블의 +/− 전압강하는 정상인데 ALT B+ 출력 자체가 비정상이다.',['CH5'],['충전 B+ 케이블','주접지'],'벨트/알터네이터 내부/센스·여자 제어를 분리.','NARROWED'),
 rule('CH04',{'CH3':'PASS','CH4':'PASS','CH2':'PASS','CH1':'FAIL'},'배터리측 수용/포스트 조건 재확인','알터네이터 출력과 경로는 정상인데 배터리 포스트 상태만 비정상이다.',[],['알터네이터 B+ 경로','알터네이터 접지경로'],'SOC/배터리 내부/포스트 접촉 및 부하 후 회복을 확인.','NARROWED'),
 rule('CH05',{'CH2':'PASS','CH3':'PASS','CH4':'PASS','CH5':'PASS'},'충전계통 주요 전기경로 정상','ALT 출력, B+ 경로, 접지, sense/control이 현재 시험에서 모두 정상이다.',[],['지속적인 주충전 경로 불량'],'방전이 반복되면 키OFF 암전류나 간헐 접촉을 별도 진단.','DOWNSTREAM')
], '14V 한 점으로 끝내지 않고 발전기 출력과 배터리까지 전달되는 경로를 분리한다.')

set_rules('OSS_HEALTH',[
 rule('OS01',{'O1':'FAIL'},'OSS 전원/IGN/GND 공급부터','컨트롤러 생존판정 전에 B+/IGN/GND 공급이 비정상이다.',[],['OSS 내부 PCB 확정'],'전원/접지 수리 후 5V/CAN을 다시 본다.','UPSTREAM'),
 rule('OS02',{'O1':'PASS','O2':'FAIL'},'SEAT 입력 경로','OSS 전원은 정상인데 점퍼/센서 변화가 OSS 입력에서 확인되지 않는다.',[],['OSS 전원고장'],'시트센서 이후 하네스/커넥터/OSS 입력단을 분리.','ISOLATED'),
 rule('OS03',{'O1':'PASS','O3':'FAIL'},'5V VREF 붕괴 · 외부부하 vs OSS 내부','전원/GND는 정상인데 5V 기준회로가 비정상이다. 외부 5V 부하를 순차분리해야 한다.',[],['단순 시트센서만의 문제'],'외부부하 전부 분리 후에도 회복되지 않을 때만 OSS 내부 regulator/PCB 가능성을 올린다.','NARROWED'),
 rule('OS04',{'O1':'PASS','O3':'PASS','O4':'FAIL'},'OSS CAN/CPU 통신 경로','공급과 5V는 살아있는데 OSS 통신 비교가 비정상이다.',[],['전원공급','5V VREF 붕괴'],'다른 CAN 모듈 정상 여부와 OSS까지 CAN 도달을 비교.','NARROWED'),
 rule('OS05',{'O1':'PASS','O2':'PASS','O3':'PASS','O4':'PASS','O5':'FAIL'},'OSS 출력단/후단 lift-lock 회로','컨트롤러 입력·5V·통신 생존은 정상인데 lift-lock 출력만 비정상이다.',[],['시트입력','OSS 전원','OSS CAN 생존'],'OSS output stage와 솔레노이드/하네스를 분리.','ISOLATED'),
 rule('OS06',{'O1':'PASS','O2':'PASS','O3':'PASS','O4':'PASS','O5':'PASS'},'OSS 핵심 전기경로 현재 정상','전원, 입력, 5V, CAN, 출력이 모두 현재 조건에서 정상이다.',[],['지속적인 OSS 전기고장'],'간헐 재현 또는 후단 유압/솔레노이드 기계작동을 확인.','DOWNSTREAM')
], '“배선 흔들면 풀림”은 원인확정이 아니라 재현 트리거로만 취급한다.')

set_rules('TM_PRESSURE_TAPS',[
 rule('TM01',{'TM6':'FAIL','TM1':'FAIL'},'공통 펌프/메인압 계통','Tap6와 Tap1이 함께 낮다. 개별 F/R clutch보다 공통 pump/main pressure 회로를 먼저 좁힌다.',[],['전진만의 고장','후진만의 고장'],'오일온도와 RPM 조건이 동일한지 확인 후 판단.','NARROWED'),
 rule('TM02',{'TM6':'PASS','TM1':'FAIL'},'Tap6 이후 Tap1/인칭·막힘 계통','메인압 Tap6는 정상인데 Tap1만 비정상이다.',[],['펌프 자체 저압'],'인칭밸브/유로 막힘/해당 제어를 우선.','ISOLATED'),
 rule('TM03',{'TM6':'PASS','TM4':'FAIL','TM5':'PASS'},'전진 클러치 공급계통','공통압과 후진은 정상인데 전진 Tap4만 낮다.',[],['공통 펌프','후진 클러치 회로'],'F 솔레노이드→스풀→전진 클러치 공급/내부누설 순서.','ISOLATED'),
 rule('TM04',{'TM6':'PASS','TM5':'FAIL','TM4':'PASS'},'후진 클러치 공급계통','공통압과 전진은 정상인데 후진 Tap5만 낮다.',[],['공통 펌프','전진 클러치 회로'],'R 솔레노이드→스풀→후진 클러치 공급/내부누설 순서.','ISOLATED'),
 rule('TM05',{'TM6':'PASS','TM3':'FAIL'},'컨버터 충전계통','공통 메인압은 정상인데 converter charge Tap3가 낮다.',[],['주펌프 전체 저압'],'charge/regulating 유로를 좁힌다.','ISOLATED'),
 rule('TM06',{'TM6':'PASS','TM3':'PASS','TM2':'FAIL'},'컨버터 출구/쿨러 입구 계통','charge는 정상인데 outlet/cooler inlet Tap2가 비정상이다.',[],['converter charge 부족'],'converter outlet/cooler restriction·회로를 확인.','ISOLATED'),
 rule('TM07',{'TM6':'PASS','TM7':'FAIL'},'윤활 공급계통','메인압은 정상인데 lube Tap7만 비정상이다.',[],['주펌프 전체 저압'],'cooler outlet→lube 공급/내부누설을 확인.','ISOLATED'),
 rule('TM08',{'TM2':'PASS','TM3':'PASS','TM4':'PASS','TM5':'PASS','TM6':'PASS','TM7':'PASS'},'주요 T/M 압력회로 현재 정상','converter/charge/F/R/main/lube가 모두 해당 시험조건에서 정상이다.',[],['지속적인 유압압력 부족'],'기계 클러치/기어/간헐 제어 또는 Tap1/인칭 비교를 계속.','DOWNSTREAM')
], '같은 온도·RPM 조건에서 압력패턴 조합으로 공통계통과 개별계통을 분리한다.')

set_rules('HYD_MAIN_RELIEF',[
 rule('HY01',{'HY1':'FAIL'},'공통 메인유압 공급/릴리프','메인 압력 자체가 비정상이다. 개별 실린더나 AUX를 먼저 분해하지 않는다.',[],['개별 기능만의 고장 확정'],'펌프/메인릴리프/흡입·공급계통을 분리.','UPSTREAM'),
 rule('HY02',{'HY1':'PASS','HY2':'FAIL'},'틸트/AUX 섹션 압력계통','메인압은 정상인데 해당 섹션 릴리프 시험만 비정상이다.',[],['메인펌프 전체 저압'],'section relief/spool/cylinder circuit로 좁힘.','ISOLATED'),
 rule('HY03',{'HY1':'PASS','HY2':'PASS','HY3':'FAIL'},'틸트 유량/누설/기계저항','압력은 정상인데 틸트 유량이 부족하다.',[],['메인압 부족','section relief 저압'],'flow control/내부누설/기계저항을 분리.','NARROWED'),
 rule('HY04',{'HY1':'PASS','HY4':'FAIL'},'AUX1 유량계통','메인압 정상에서 AUX1 유량만 부족하다.',[],['메인펌프 전체 저압'],'AUX1 section/flow setting/누설을 확인.','ISOLATED'),
 rule('HY05',{'HY1':'PASS','HY2':'PASS','HY3':'PASS','HY4':'PASS'},'주요 메인·섹션 압력/유량 현재 정상','현재 시험한 공통압과 섹션 유량이 정상이다.',[],['지속적인 공통 유압부족'],'실린더 내부누설/기계저항/재현조건을 다음으로.','DOWNSTREAM')
], '압력 정상인데 속도만 느린 경우를 펌프불량으로 오판하지 않는다.')

set_rules('EL_FR_CONTROL',[
 rule('FR01',{'FR1':'FAIL'},'F/R 공급퓨즈/상류','FWD/REV 공급 자체가 없다.',[],['솔레노이드 코일 확정'],'fuse #3 및 상류 전원을 먼저 복구.','UPSTREAM'),
 rule('FR02',{'FR1':'PASS','FR2':'FAIL'},'F/R 스위치 공통접점','공급은 정상인데 common 4↔7이 비정상이다.',[],['F/R 솔레노이드'],'스위치/공통접점으로 좁힘.','ISOLATED'),
 rule('FR03',{'FR1':'PASS','FR2':'PASS','FR3':'FAIL'},'전진 스위치 접점','공통은 정상인데 F 1↔2가 비정상이다.',[],['공통전원','후진접점'],'전진 스위치 접점/조정 확인.','ISOLATED'),
 rule('FR04',{'FR1':'PASS','FR2':'PASS','FR4':'FAIL'},'후진 스위치 접점','공통은 정상인데 R 1↔3가 비정상이다.',[],['공통전원','전진접점'],'후진 스위치 접점/조정 확인.','ISOLATED'),
 rule('FR05',{'FR1':'PASS','FR2':'PASS','FR5':'FAIL'},'F/R 솔레노이드 코일/하네스','스위치 공급은 정상인데 솔레노이드 전기시험이 비정상이다.',[],['F/R 스위치 공통'],'코일/커넥터/하네스를 분리.','ISOLATED'),
 rule('FR06',{'FR5':'PASS','FR6':'FAIL'},'솔레노이드 플런저/기계작동','코일은 정상인데 OEM 플런저 이동이 부족하다.',[],['코일 저항불량'],'솔레노이드 기계고착/플런저를 확인.','ISOLATED'),
 rule('FR07',{'FR1':'PASS','FR2':'PASS','FR3':'PASS','FR4':'PASS','FR5':'PASS','FR6':'PASS'},'F/R 전기·솔레노이드 작동 현재 정상','스위치와 코일/플런저가 모두 정상이다.',[],['F/R 전기입력 고장'],'밸브스풀/클러치 압력(Tap4/5) 쪽으로 이동.','DOWNSTREAM')
], '접점→코일→플런저→압력 순으로 넘어간다.')

set_rules('ENG_ECU_HEALTH',[
 rule('EC01',{'EH1':'FAIL'},'SENSOR 15A 공급','ECU 생존판정 전에 SENSOR fuse 공급이 비정상이다.',[],['ECU 내부고장'],'퓨즈/소켓/상류를 먼저 복구.','UPSTREAM'),
 rule('EC02',{'EH1':'PASS','EH2':'FAIL'},'ECU B+/IGN 공급','퓨즈는 정상인데 ECU 전원 공급이 비정상이다.',[],['ECU CPU/CAN 내부'],'전원하네스/릴레이/커넥터를 추적.','ISOLATED'),
 rule('EC03',{'EH2':'PASS','EH3':'FAIL'},'ECU POWER GND','전원은 유지되는데 ECU 접지 전압강하가 비정상이다.',[],['ECU B+ 공급'],'접지/체결/하네스를 먼저 수리.','ISOLATED'),
 rule('EC04',{'EH2':'PASS','EH3':'PASS','EH4':'FAIL'},'ECU CAN/통신 경로','전원/GND는 정상인데 CAN 비교가 비정상이다.',[],['전원·접지'],'다른 모듈과 비교해 branch harness vs ECU transceiver를 분리.','NARROWED'),
 rule('EC05',{'EH2':'PASS','EH3':'PASS','EH4':'PASS','EH5':'FAIL'},'ECU 5V VREF 계통','전원/GND/CAN 도달은 정상인데 5V가 비정상이다.',[],['주전원','주접지','CAN wiring'],'ENG_VREF에서 외부센서 단락과 ECU 내부 regulator를 분리.','NARROWED'),
 rule('EC06',{'EH2':'PASS','EH3':'PASS','EH4':'PASS','EH5':'PASS'},'ECU 외부 생존조건은 현재 정상','전원/GND/CAN/VREF가 모두 정상인데 D24 ECU가 계속 응답하지 않는다면 내부 CPU/소프트웨어/커넥터 간헐 가능성이 올라간다.',[],['지속적인 외부 전원·접지·VREF 문제'],'동일 실패상태 재현과 ECU 커넥터 단자 장력까지 확인 후 내부판정.','NARROWED')
], 'ECU를 교환하기 전에 독립적인 전원/GND/CAN/VREF 생존신호를 확인한다.')

set_rules('ENG_VREF',[
 rule('VR01',{'VR1':'FAIL'},'RPS 5V branch 우선','RPS VREF branch가 비정상이다.',['VR5'],['다른 센서 전체를 한꺼번에 교환'],'RPS/해당 하네스 분리 시 전체 5V 회복 여부를 본다.','NARROWED'),
 rule('VR02',{'VR2':'FAIL'},'BPS 5V branch 우선','BPS VREF branch가 비정상이다.',['VR5'],[],'BPS 분리 전후 공통 5V 변화를 본다.','NARROWED'),
 rule('VR03',{'VR3':'FAIL'},'OPTS 5V branch 우선','OPTS VREF branch가 비정상이다.',['VR5'],[],'OPTS 분리 전후 공통 5V 변화를 본다.','NARROWED'),
 rule('VR04',{'VR4':'FAIL'},'EGR VREF3 branch 우선','EGR VREF branch가 비정상이다.',['VR5'],[],'EGR 분리 전후 공통 5V 변화를 본다.','NARROWED'),
 rule('VR05',{'VR5':'FAIL'},'외부 5V 부하를 모두 떼어도 VREF 불량','외부 5V 부하 순차분리 후에도 기준전압이 회복되지 않는 결과라면 ECU 내부 regulator/PCB 가능성이 크게 올라간다.',[],['개별 외부센서 단락만의 문제'],'전원/GND 정상 조건을 다시 확인한 뒤 ECU 내부판정.','NARROWED'),
 rule('VR06',{'VR1':'PASS','VR2':'PASS','VR3':'PASS','VR4':'PASS','VR5':'PASS'},'5V 기준회로 현재 정상','주요 5V branch와 외부부하 분리시험이 정상이다.',[],['지속적인 공통 5V 붕괴'],'센서 signal 자체/다른 입력계통으로 이동.','DOWNSTREAM')
], '5V가 낮다고 ECU를 바로 교환하지 않고 외부부하 분리로 확인한다.')

set_rules('ENG_CRANK_START',[
 rule('CS01',{'CS1':'FAIL'},'ECU 생존/통신부터','ECU 통신이 성립하지 않는다. Rail·인젝터 기계부품으로 내려가지 않는다.',[],['고압펌프/인젝터 확정'],'ENG_ECU_HEALTH로 이동.','UPSTREAM'),
 rule('CS02',{'CS1':'PASS','CS2':'FAIL'},'CRK/CAM 동기 계통','ECU는 살아있지만 crank RPM/sync가 비정상이다.',[],['Rail 부품 우선교환'],'ENG_SYNC에서 센서쪽/ECU쪽 파형과 기계타이밍을 분리.','ISOLATED'),
 rule('CS03',{'CS1':'PASS','CS2':'PASS','CS3':'FAIL','CS4':'FAIL'},'Rail actual 신뢰성보다 RPS 회로 먼저','Rail actual이 command를 못 따라가며 RPS 5V/GND/signal도 비정상이다.',[],['고압펌프 확정'],'RPS 회로를 정상화한 뒤 rail 판단을 다시 한다.','UPSTREAM'),
 rule('CS04',{'CS1':'PASS','CS2':'PASS','CS3':'FAIL','CS4':'PASS','CS5':'FAIL'},'저압 연료/공기혼입 계통','RPS 회로는 신뢰 가능하지만 rail 형성이 부족하고 저압공급이 비정상이다.',[],['ECU 통신','CRK/CAM','RPS 회로'],'필터/흡입/공기혼입/공급압을 해결 후 재시험.','ISOLATED'),
 rule('CS05',{'CS1':'PASS','CS2':'PASS','CS3':'FAIL','CS4':'PASS','CS5':'PASS','CS6':'FAIL'},'IMV 제어/회로','저압공급과 RPS는 정상인데 IMV command/작동이 비정상이다.',[],['저압공급','RPS 회로'],'IMV 전기/기계와 ECU command 입력조건을 분리.','ISOLATED'),
 rule('CS06',{'CS1':'PASS','CS2':'PASS','CS3':'PASS','CS7':'FAIL'},'인젝터 구동 전기계통','ECU/sync/rail은 정상인데 injector drive가 없다/비정상이다.',[],['Rail 압력부족'],'ECU injector drive/하네스/동기 조건을 확인.','ISOLATED'),
 rule('CS07',{'CS1':'PASS','CS2':'PASS','CS3':'PASS','CS7':'PASS','CS8':'FAIL'},'인젝터 리턴 편차','Rail과 전기구동은 정상인데 특정 인젝터 return이 과다/편차가 크다.',[],['ECU 통신','Rail 형성','인젝터 drive'],'해당 인젝터 누설 가능성을 올리고 실린더 기여/압축과 교차확인.','NARROWED'),
 rule('CS08',{'CS1':'PASS','CS2':'PASS','CS3':'PASS','CS7':'PASS','CS8':'PASS'},'생존·동기·Rail·분사 기본조건 현재 정상','기본 시동조건이 모두 정상인데 시동불량이 지속된다.',[],['지속적인 ECU/Sync/Rail/Injector 기본고장'],'압축/기계타이밍/흡배기/EGR/온도조건으로 이동.','DOWNSTREAM')
], '크랭킹 무시동은 ECU 생존→동기→rail 신뢰성→저압/IMV→분사 순으로 좁힌다.')

set_rules('EL_CAN_NETWORK',[
 rule('CN01',{'CN2':'FAIL'},'문제 노드 B+/IGN 공급','CAN fault 판정 전에 문제 모듈 전원이 비정상이다.',[],['CAN transceiver 확정'],'전원 공급부터 복구.','UPSTREAM'),
 rule('CN02',{'CN2':'PASS','CN3':'FAIL'},'문제 노드 GND 경로','B+/IGN은 정상인데 GND drop이 비정상이다.',[],['CAN pair 단선'],'접지/커넥터/하네스를 수리.','ISOLATED'),
 rule('CN03',{'CN2':'PASS','CN3':'PASS','CN4':'FAIL'},'해당 노드 CAN branch harness','문제 노드 전원/GND는 정상인데 그 노드까지 CAN H/L이 도달하지 않는다.',[],['모듈 전원·접지'],'분기하네스/커넥터를 추적.','ISOLATED'),
 rule('CN04',{'CN2':'PASS','CN3':'PASS','CN4':'PASS','CN5':'FAIL'},'문제 노드/트랜시버 또는 로컬 short','전원/GND/CAN 도달은 정상인데 노드 격리 결과가 비정상이다.',[],['로컬 CAN branch 단선'],'node/transceiver와 로컬 short를 분리.','NARROWED'),
 rule('CN05',{'CN2':'PASS','CN3':'PASS','CN4':'PASS','CN5':'PASS'},'로컬 노드 공급·CAN 경로 현재 정상','문제 노드까지 전원/GND/CAN과 격리시험이 정상이다.',[],['지속적인 단순 branch 전원/배선고장'],'간헐 재현/진단커넥터 공통/소프트웨어 상태를 확인.','DOWNSTREAM')
], '60Ω 같은 일반값을 모델 근거 없이 강제하지 않고 노드별 전원/GND/CAN 도달과 격리로 좁힌다.')

set_rules('EL_AC_POWER',[
 rule('AP01',{'AP1':'FAIL'},'A/C 기능 공급 상류','A/C 공급 기능선이 비정상이다.',[],['컨트롤러/블로워 교환'],'정확 cavity가 미확정이면 기능상 B+ source부터 추적.','UPSTREAM'),
 rule('AP02',{'AP1':'PASS','AP2':'FAIL'},'A/C controller B+/IGN','상류 공급은 있으나 controller 공급이 비정상이다.',[],['블로워모터'],'하네스/커넥터/IG feed를 추적.','ISOLATED'),
 rule('AP03',{'AP2':'PASS','AP3':'FAIL'},'A/C controller GND','controller B+/IGN은 정상인데 GND drop이 비정상이다.',[],['controller 내부'],'접지 경로를 수리.','ISOLATED'),
 rule('AP04',{'AP2':'PASS','AP3':'PASS','AP4':'FAIL'},'블로워 공급/GND branch','controller는 살아있지만 blower connector 부하측정이 비정상이다.',[],['A/C controller 전체 dead'],'controller output/resistor/harness를 좁힘.','ISOLATED'),
 rule('AP05',{'AP4':'PASS','AP5':'FAIL'},'블로워 모터 자체','블로워 connector 공급/GND는 정상인데 Stage 3 direct test가 실패한다.',[],['블로워 공급하네스'],'블로워 모터 기계/전기 자체를 확인.','ISOLATED'),
 rule('AP06',{'AP4':'PASS','AP5':'PASS','AP6':'FAIL'},'컴프레서 요청/서모스탯·inhibit 경로','블로워는 정상인데 thermostat/request 경로가 비정상이다.',[],['블로워모터'],'pressure/inhibit/controller command로 이동.','NARROWED'),
 rule('AP07',{'AP2':'PASS','AP3':'PASS','AP4':'PASS','AP5':'PASS','AP6':'PASS'},'A/C 기본 전원/블로워/request 현재 정상','전원과 블로워, thermostat 기본경로가 정상이다.',[],['전체 A/C power dead'],'컴프레서/냉매압/콘덴서팬 별도 그래프로 이동.','DOWNSTREAM')
], 'display dead / blower dead / compressor request absent를 처음부터 분리한다.')

set_rules('EL_STOP_LAMP',[
 rule('SL01',{'SL1':'FAIL'},'ACC 15A 공급/퓨즈 소켓','STOP 회로 공통공급이 비정상이다.',[],['STOP switch/후미램프'],'퓨즈 양단 부하전압으로 상류를 먼저 복구.','UPSTREAM'),
 rule('SL02',{'SL1':'PASS','SL2':'FAIL'},'STOP switch 상류 기능선','퓨즈는 정상인데 switch 상류까지 공급이 도달하지 않는다.',[],['STOP switch 내부접점'],'퓨즈→switch 사이 하네스/커넥터를 추적.','ISOLATED'),
 rule('SL03',{'SL2':'PASS','SL3':'FAIL'},'STOP switch/조정','상류 전압은 유지되지만 페달작동 시 출력이 전환되지 않는다.',[],['후미 좌우램프'],'switch/기계조정을 확인.','ISOLATED'),
 rule('SL04',{'SL3':'PASS','SL4':'FAIL','SL5':'PASS'},'우측 STOP branch','공통 출력과 좌측은 정상인데 RH만 비정상이다.',[],['STOP switch','좌측 branch'],'우측 하네스/커넥터/램프를 좁힘.','ISOLATED'),
 rule('SL05',{'SL3':'PASS','SL5':'FAIL','SL4':'PASS'},'좌측 STOP branch','공통 출력과 우측은 정상인데 LH만 비정상이다.',[],['STOP switch','우측 branch'],'좌측 하네스/커넥터/램프를 좁힘.','ISOLATED'),
 rule('SL06',{'SL4':'PASS','SL5':'PASS','SL6':'FAIL'},'후미 공통 GND','양쪽 STOP 기능단 B+는 정상인데 GND voltage drop이 비정상이다.',[],['좌우 B+ branch'],'후미 접지/단자를 수리.','ISOLATED'),
 rule('SL07',{'SL1':'PASS','SL2':'PASS','SL3':'PASS','SL4':'PASS','SL5':'PASS','SL6':'PASS'},'브레이크등 기본 회로 현재 정상','공급→switch→좌우 STOP→GND가 모두 정상이다.',[],['지속적인 기본회로 단선'],'간헐 커넥터/전구 접촉 또는 증상 재현조건을 확인.','DOWNSTREAM')
], '스위치 1/2번 역할을 미확정 상태에서 임의 지정하지 않고 기능상 상류/출력으로 측정한다.')

# top-level metadata
d['version']='v1.8.9-adaptive-branch'
d['adaptive_branch_rule']='여러 포인트 조합으로 배제구간/남은계통/다음 측정을 제안한다. 이는 부품 자동확정이 아니며, OEM 미확정 임계값을 새로 만들지 않는다.'
asset.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Java patch
jp=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/TestPointLocatorActivity.java'
s=jp.read_text(encoding='utf-8')
s=s.replace('private android.content.SharedPreferences prefs,sessionPref; private TextView sessionSummary;', 'private android.content.SharedPreferences prefs,sessionPref; private TextView sessionSummary,branchSummary;')
s=s.replace('addSessionCard();\n\n        Button loc=', 'addSessionCard();\n        addAdaptiveBranchCard();\n\n        Button loc=')
# status setters already call updateSessionSummary, which will refresh adaptive summary
old='private void updateSessionSummary(){if(sessionSummary==null||group==null)return;int total=0,pass=0,fail=0,hold=0,valued=0;try{JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject p=pts.getJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;total++;String s=pref(id,"status");if("PASS".equals(s))pass++;else if("FAIL".equals(s))fail++;else if("HOLD".equals(s))hold++;if(!pref(id,"value").trim().isEmpty())valued++;}}catch(Exception ignore){}sessionSummary.setText("표시 "+total+" · 측정값 "+valued+" · 정상 "+pass+" · 이상 "+fail+" · 보류 "+hold+" · 미판정 "+Math.max(0,total-pass-fail-hold));}'
new='private void updateSessionSummary(){if(group==null)return;int total=0,pass=0,fail=0,hold=0,valued=0;try{JSONArray pts=group.getJSONArray("points");for(int i=0;i<pts.length();i++){JSONObject p=pts.getJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;total++;String s=pref(id,"status");if("PASS".equals(s))pass++;else if("FAIL".equals(s))fail++;else if("HOLD".equals(s))hold++;if(!pref(id,"value").trim().isEmpty())valued++;}}catch(Exception ignore){}if(sessionSummary!=null)sessionSummary.setText("표시 "+total+" · 측정값 "+valued+" · 정상 "+pass+" · 이상 "+fail+" · 보류 "+hold+" · 미판정 "+Math.max(0,total-pass-fail-hold));updateAdaptiveBranchSummary();}'
if old not in s: raise SystemExit('updateSessionSummary anchor not found')
s=s.replace(old,new)
anchor='    private String buildSessionText(boolean onlyFail){'
insert=r'''    private void addAdaptiveBranchCard(){
        JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return;
        LinearLayout c=card();c.addView(tv("측정 조합 판정 · 다음 한 점",16,true));c.addView(tv(ab.optString("rule"),11,false));branchSummary=tv("",13,true);branchSummary.setPadding(dp(6),dp(8),dp(6),dp(8));branchSummary.setBackground(bg(Color.rgb(238,244,249),8));c.addView(branchSummary);
        Button b=btn("현재 조합의 다음 점검 자세히",true);b.setOnClickListener(v->showAdaptiveBranchDialog());c.addView(b);String n=ab.optString("note");if(!n.isEmpty())c.addView(tv("주의 · "+n,11,false));body.addView(c);updateAdaptiveBranchSummary();
    }
    private boolean ruleMatches(JSONObject r){try{JSONObject w=r.getJSONObject("when");Iterator<String> it=w.keys();while(it.hasNext()){String id=it.next();if(!w.optString(id).equals(pref(id,"status")))return false;}return w.length()>0;}catch(Exception e){return false;}}
    private JSONObject matchedAdaptiveRule(){JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return null;JSONArray a=ab.optJSONArray("rules");if(a==null)return null;for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&ruleMatches(r))return r;}return null;}
    private JSONObject pointById(String id){JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);if(p!=null&&id.equals(p.optString("id")))return p;}return null;}
    private String nextPointText(JSONObject r){StringBuilder sb=new StringBuilder();JSONArray a=r==null?null:r.optJSONArray("next_points");if(a!=null&&a.length()>0){for(int i=0;i<a.length();i++){String id=a.optString(i);JSONObject p=pointById(id);if(i>0)sb.append("\n");sb.append("[").append(id).append("] ").append(p==null?id:p.optString("label"));}}else{JSONArray pts=group.optJSONArray("points");if(pts!=null)for(int i=0;i<pts.length();i++){JSONObject p=pts.optJSONObject(i);String id=p.optString("id");if(!visiblePointIds.contains(id))continue;if(pref(id,"status").isEmpty()){sb.append("[").append(id).append("] ").append(p.optString("label"));break;}}}return sb.toString();}
    private String adaptiveSummaryText(){JSONObject ab=group.optJSONObject("adaptive_branch");if(ab==null)return "";JSONObject r=matchedAdaptiveRule();if(r==null){String next=nextPointText(null);return "아직 조합판정 전"+(next.isEmpty()?" · 현재 표시 포인트 판정을 더 입력하세요.":"\n→ 다음 측정: "+next);}StringBuilder sb=new StringBuilder();sb.append("현재 분기 · ").append(r.optString("title"));String level=r.optString("level");if(!level.isEmpty())sb.append("  [").append(level).append("]");String a=r.optString("assessment");if(!a.isEmpty())sb.append("\n").append(a);JSONArray ex=r.optJSONArray("excludes");if(ex!=null&&ex.length()>0){sb.append("\n배제/우선순위 하향: ");for(int i=0;i<ex.length();i++){if(i>0)sb.append(" / ");sb.append(ex.optString(i));}}String np=nextPointText(r);if(!np.isEmpty())sb.append("\n→ 다음 측정: ").append(np);String c=r.optString("caution");if(!c.isEmpty())sb.append("\n주의: ").append(c);return sb.toString();}
    private void updateAdaptiveBranchSummary(){if(branchSummary==null)return;String s=adaptiveSummaryText();branchSummary.setText(s);JSONObject r=matchedAdaptiveRule();if(r==null)branchSummary.setTextColor(Color.rgb(70,80,90));else{String lv=r.optString("level");branchSummary.setTextColor("ISOLATED".equals(lv)?Color.rgb(170,55,45):("UPSTREAM".equals(lv)?ORANGE:NAVY));}}
    private void showAdaptiveBranchDialog(){new AlertDialog.Builder(this).setTitle("현재 측정 조합 판정").setMessage(adaptiveSummaryText()+"\n\n※ 이 기능은 측정구간을 좁히는 보조판정입니다. 단일 측정으로 부품교환을 확정하지 않습니다.").setPositiveButton("확인",null).show();}

'''
if anchor not in s: raise SystemExit('buildSessionText anchor not found')
s=s.replace(anchor,insert+anchor)
# append adaptive result to copied summary
old='private String buildSessionText(boolean onlyFail){StringBuilder sb=new StringBuilder();sb.append("작업세션: ").append(sessionLabel).append("\\n").append(group.optString("title")).append("\\n");'
new='private String buildSessionText(boolean onlyFail){StringBuilder sb=new StringBuilder();sb.append("작업세션: ").append(sessionLabel).append("\\n").append(group.optString("title")).append("\\n");String as=adaptiveSummaryText();if(!as.isEmpty())sb.append("\\n[조합판정] ").append(as).append("\\n");'
if old not in s: raise SystemExit('build text anchor missing')
s=s.replace(old,new)
jp.write_text(s,encoding='utf-8')

# versions
bg=ROOT/'app/build.gradle'
t=bg.read_text(encoding='utf-8').replace('versionCode 33','versionCode 34').replace('versionName "0.18-rc-expert-v8.8-oem-auto-eval"','versionName "0.18-rc-expert-v8.9-adaptive-branch"')
bg.write_text(t,encoding='utf-8')
rel=ROOT/'app/src/main/assets/diagnostic_release.json'; rr=json.loads(rel.read_text(encoding='utf-8'));rr.update({'state':'RC EXPERT V8.9 ADAPTIVE BRANCH','version_name':'0.18-rc-expert-v8.9-adaptive-branch','git_commit_sha':'UNSTAMPED_LOCAL_PATCH'});rel.write_text(json.dumps(rr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
wf=ROOT/'.github/workflows/build-apk.yml'; w=wf.read_text(encoding='utf-8');w=w.replace('0.18-rc-expert-v8.8-oem-auto-eval','0.18-rc-expert-v8.9-adaptive-branch').replace('RC EXPERT V8.8 OEM AUTO EVAL','RC EXPERT V8.9 ADAPTIVE BRANCH').replace('forklift-diagnostic-v18-rc-expert-v8.8-oem-auto-eval-','forklift-diagnostic-v18-rc-expert-v8.9-adaptive-branch-').replace('forklift-diagnostic-v18-expert-v8.8-oem-auto-eval-','forklift-diagnostic-v18-expert-v8.9-adaptive-branch-')
# add validator step after auto eval
needle='      - name: Validate OEM-exact automatic evaluation\n        run: python3 tools/validate_oem_auto_evaluation.py .\n'
add=needle+'\n      - name: Validate adaptive multi-point branch engine\n        run: python3 tools/validate_adaptive_branch_v89.py .\n'
if needle in w and 'validate_adaptive_branch_v89.py' not in w:w=w.replace(needle,add)
# add report artifact
w=w.replace('            build/reports/oem_auto_eval_v88.md\n','            build/reports/oem_auto_eval_v88.md\n            build/reports/adaptive_branch_v89.md\n')
wf.write_text(w,encoding='utf-8')

# progress
(ROOT/'V8_9_PROGRESS.md').write_text('''# V8.9 Adaptive Multi-point Branch\n\n- 측정값/정상·이상 판정을 한 점씩 보는 데서 끝내지 않고 여러 포인트의 조합을 평가한다.\n- 조합판정은 **배제된 구간 / 현재 남은 계통 / 다음 한 점**을 제시한다.\n- 단일 FAIL을 부품교환 확정으로 사용하지 않는다.\n- OEM 미확정 수치 임계값을 새로 만들지 않는다.\n- 우선 12개 고가치 계통에 explicit ordered rules 적용: START, CHARGE, OSS, T/M taps, main hydraulic, F/R, ECU health, 5V VREF, crank/no-start, CAN, A/C power, STOP lamp.\n- 모든 rule은 point ID validity, shadowing, synthetic 30-condition simulation을 CI에서 검사한다.\n''',encoding='utf-8')
print('upgraded',asset)
