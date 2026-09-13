#!/usr/bin/env python3
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
R=ROOT/'build/reports'
expert_path=A/'expert_diag_v2.json'
ready=json.loads((R/'field_readiness_v3.json').read_text(encoding='utf-8'))
partial_ids={x['id'] for x in ready['cause_rows'] if x['status']=='FIELD_USABLE_PARTIAL'}
root=json.loads(expert_path.read_text(encoding='utf-8'))


def uniq(seq):
    out=[]
    for x in seq:
        if x and x not in out: out.append(x)
    return out

def short(s,n=24):
    s=re.sub(r'\s+',' ',s).strip()
    return s if len(s)<=n else s[:n-1]+'…'

def node(i,label,role='component',highlight=False):
    return {'id':i,'label':label,'role':role,'highlight':highlight}

def mp(mid,where,check,expected,source='OEM/비교진단'):
    return {'id':mid,'where':where,'check':check,'expected':expected,'source':source}

def diag(title,nodes,edges,mps,note):
    return {'title':title,'kind':'fault_specific_functional_schematic_v7','nodes':nodes,'edges':[{'from':a,'to':b} for a,b in edges],'measure_points':mps,'note':note}

# Each profile returns concrete field additions. The values are diagnostic methods, not invented OEM limits.
def tm_profile(c):
    lc=c.lower()
    if '오일 레벨' in c or '오일 부족' in c or '오일 레벨 낮음' in c:
        return dict(
            nodes=[node('sump','T/M SUMP\nLEVEL','inspect',True),node('suction','흡입 스트레이너/호스','inspect'),node('pump','PUMP\nTap1','measure'),node('main','MAIN\nTap6','measure')],
            edges=[('sump','suction'),('suction','pump'),('pump','main')],mps=['LEVEL','FOAM','Tap1','Tap6'],
            measure=[mp('LEVEL','T/M 지정 레벨 확인부','정지/온도 등 OEM 레벨 조건에서 실제 레벨','정상 레벨 복구 후 동일 증상 재현 여부'),mp('FOAM','T/M 오일/딥스틱','기포·거품·흡입공기 흔적','정상유와 비교; 기포 지속 시 흡입계통 우선')],
            seq=['레벨을 보충하기 전에 외부 누유와 최근 정비/보충 이력을 확인한다.','정상 레벨로 맞춘 뒤 거품이 사라질 때까지 순환시키고 Tap1/Tap6과 주행증상을 다시 비교한다.'],
            ro=['흡입호스/스트레이너 제한 또는 공기유입','펌프/릴리프에 의한 공통 저압'],confirm=['레벨 정상화만으로 Tap 압력과 증상이 함께 정상화될 때 원인 연관성을 확정한다.'],tools=['OEM 지정 오일/레벨 게이지'],loc='트랜스미션 하우징의 지정 오일 레벨 확인부/흡입라인')
    if '펌프' in c and ('손상' in c or '마모' in c or '결함' in c or '소손' in c or '압력' in c):
        return dict(nodes=[node('sump','SUMP/흡입','inspect'),node('pump','T/M PUMP','component',True),node('tap1','Tap1\n펌프 출구','measure'),node('tap6','Tap6\n메인라인','measure'),node('relief','MAIN RELIEF','control')],edges=[('sump','pump'),('pump','tap1'),('tap1','tap6'),('tap1','relief')],mps=['Tap1','Tap6','SUCTION'],measure=[mp('SUCTION','펌프 흡입 호스/스트레이너','꺾임·막힘·공기유입·거품','흡입 이상이 있으면 펌프 마모 확정 금지')],seq=['펌프 구동축/커플링이 실제 회전하고 헛돌지 않는지 확인한다.','Tap1과 Tap6을 같은 유온/RPM에서 비교하고, 릴리프/대규모 누설을 격리한다.'],ro=['흡입 제한/공기혼입','메인 릴리프 열린 고착','대규모 하류 내부누설'],confirm=['흡입·구동·릴리프·대누설을 배제한 상태에서 Tap1 자체가 반복 저압이면 펌프를 확정 후보로 올린다.'],tools=['0~20.5 bar급 T/M 압력계','회전/구동부 육안확인 도구'],loc='토크컨버터/T/M 펌프부와 Tap1·Tap6 시험포트')
    if '릴리프' in c:
        return dict(nodes=[node('pump','PUMP\nTap1','measure'),node('relief',short(c,20),'control',True),node('main','MAIN\nTap6','measure'),node('return','RETURN','return')],edges=[('pump','relief'),('relief','main'),('relief','return')],mps=['Tap1','Tap6','RELIEF RETURN'],measure=[mp('RELIEF RETURN','릴리프 리턴/밸브바디','비정상 지속 바이패스·발열·오염 확인','Tap1/Tap6 조합과 함께 판단')],seq=['조정나사를 먼저 돌리지 말고 밸브 오염·스프링·스풀 자유이동을 확인한다.','Tap1/Tap6 조합으로 펌프출력과 릴리프/하류 문제를 분리한 뒤 재측정한다.'],ro=['펌프 출력 부족','인칭/모듈레이션 구간 손실','시험온도/RPM/포트 오류'],confirm=['펌프출력은 정상인데 릴리프 상태를 교정했을 때 Tap6이 반복 정상화되면 릴리프 원인으로 확정한다.'],tools=['T/M 압력계','청정 작업도구'],loc='T/M 컨트롤밸브 메인/센터 릴리프 위치')
    if any(k in c for k in ('내부 누유','내부누유','시일','클러치 요소','클러치 회로 누유')):
        return dict(nodes=[node('main','Tap6\n공통공급','measure'),node('selector','SELECTOR/MOD','control'),node('apply','Tap4/Tap5\n선택회로','measure'),node('clutch',short(c,18),'component',True),node('drain','내부 LEAK/RETURN','return')],edges=[('main','selector'),('selector','apply'),('apply','clutch'),('clutch','drain')],mps=['Tap6','Tap4','Tap5','LOAD RECHECK'],measure=[mp('LOAD RECHECK','해당 방향 클러치압','무부하 정상 후 부하에서 압력 유지 여부','압력 유지/붕괴를 반복 비교; OEM 별도 부하 한계 미확인 시 임의 bar 금지')],seq=['반대 방향 클러치가 정상인지 비교해 공통펌프 문제를 먼저 배제한다.','Tap6 정상 + 해당 방향 제어밸브 작동 정상인데 해당 Tap만 낮은지 확인한다.','무부하와 부하에서 압력 유지 여부를 비교해 동적 내부누설을 확인한다.'],ro=['공통 공급압 저하','selector/modulation 스풀 불량','솔레노이드/지령 불량'],confirm=['공통압·제어가 정상인데 해당 클러치 회로만 반복적으로 압력을 유지하지 못하고 기계적 슬립이 일치할 때 내부누설/시일을 확정한다.'],tools=['Tap4/Tap5 압력계','Tap6 압력계'],loc='전/후진 클러치 apply 회로 및 입력/리버스 샤프트 시일부')
    if any(k in c for k in ('냉각','쿨러','컨버터 바이패스','컨버터 내부 막힘')):
        return dict(nodes=[node('charge','Tap3\nCONVERTER CHARGE','measure'),node('out','Tap2\nCONV OUT','measure'),node('cooler',short(c,18),'component',True),node('lube','Tap7\nLUBE','measure'),node('return','T/M RETURN','return')],edges=[('charge','out'),('out','cooler'),('cooler','lube'),('lube','return')],mps=['Tap3','Tap2','Tap7','TEMP IN/OUT'],measure=[mp('TEMP IN/OUT','쿨러 입구/출구 라인','같은 부하에서 온도차·호스 꺾임·막힘 비교','압력과 온도 패턴을 함께 보며 코어/라인 제한 분리')],seq=['Tap3→Tap2→쿨러→Tap7 순으로 상·하류를 같은 유온에서 비교한다.','쿨러 외부 핀 막힘/공기흐름과 내부 라인 제한을 분리한다.'],ro=['클러치 슬립에 의한 발열','오일 레벨/공기혼입','상류 컨버터 charge 저압'],confirm=['상류 압력은 정상인데 쿨러 전후에서 압력/온도 패턴이 반복적으로 비정상이고 우회/세척 후 정상화되면 제한을 확정한다.'],tools=['T/M 압력계','접촉식/IR 온도계'],loc='토크컨버터 출구→오일쿨러→윤활회로 라인')
    if '공기' in c or '흡입부 공기' in c:
        return dict(nodes=[node('sump','SUMP LEVEL','inspect'),node('suction',short(c,18),'component',True),node('pump','PUMP/Tap1','measure'),node('main','Tap6','measure')],edges=[('sump','suction'),('suction','pump'),('pump','main')],mps=['LEVEL','FOAM','SUCTION JOINT','Tap1'],measure=[mp('SUCTION JOINT','흡입호스/클램프/씰','오일 누유 없이 공기만 빨아들이는 접합부 포함 확인','거품 발생과 흔들림/클램프 조정 전후 비교')],seq=['오일 표면 거품/유백화와 펌프 소음이 증상과 같이 변하는지 확인한다.','흡입 접합부를 구간별로 재체결/격리한 뒤 거품과 Tap1을 재확인한다.'],ro=['단순 오일 부족','펌프 기계마모','릴리프 열린 고착'],confirm=['흡입부 보수 후 거품·펌프소음·압력 저하가 동시에 사라지면 공기유입을 확정한다.'],tools=['손전등','T/M 압력계'],loc='T/M 오일팬/흡입 스트레이너에서 펌프 입구까지')
    if any(k in c for k in ('오염','이물질','회로 막힘','통로 막힘','오리피스 막힘','라인 또는 내부통로 막힘')):
        return dict(nodes=[node('up','상류 압력/유량','measure'),node('focus',short(c,18),'component',True),node('down','하류 압력/유량','measure'),node('return','RETURN/FILTER','inspect')],edges=[('up','focus'),('focus','down'),('down','return')],mps=['UPSTREAM','DOWNSTREAM','FILTER/DEBRIS'],measure=[mp('UPSTREAM/DOWNSTREAM','의심 제한부 전·후','같은 시험조건에서 압력/반응 비교','상류 정상·하류 이상일 때 제한구간으로 좁힘')],seq=['필터/스트레이너의 금속분·섬유·고무조각을 확인하고 발생원을 기록한다.','의심 유로 전후 압력을 비교하고 청소/플러싱 후 같은 조건으로 재시험한다.'],ro=['펌프 자체 저압','오일 레벨/점도 문제','잘못된 호스 연결'],confirm=['제한부 전후 차이가 재현되고 이물 제거 후 하류 반응이 정상화되면 막힘 원인으로 확정한다.'],tools=['압력계','청정 샘플통/필터 절개도구'],loc='해당 T/M 유로/오리피스/밸브바디 및 필터')
    if any(k in c for k in ('라인 연결 오류','라인 또는 내부통로','외부 오일라인')):
        return dict(nodes=[node('src','SOURCE PORT','source'),node('hose','HOSE/PORT ROUTING','inspect',True),node('dst','DEST PORT','component'),node('test','FUNCTION TEST','measure')],edges=[('src','hose'),('hose','dst'),('dst','test')],mps=['PORT LABEL','HOSE END A/B','POST-REPAIR TEST'],measure=[mp('PORT LABEL','호스 양끝/밸브 포트 각인','원본 유압도와 실제 연결을 1:1 추적','최근 작업 전후와 비교; 색상만으로 판정 금지')],seq=['최근 호스/밸브 작업 여부를 확인하고 호스 양 끝을 손으로 실제 추적한다.','포트 각인/회로도 기능을 대조해 오연결·교차연결·꺾임을 확인한다.'],ro=['펌프/릴리프 내부고장','클러치/컨버터 내부손상'],confirm=['회로도와 다른 연결을 수정한 뒤 압력/기능이 즉시 정상화되면 오연결을 확정한다.'],tools=['유압 회로도','포트 캡/태그'],loc='T/M 외부 오일호스와 컨트롤밸브 포트')
    if any(k in c for k in ('모듈 밸브','셀렉터 스풀','스풀 소착','조립 오류')):
        return dict(nodes=[node('cmd','F/R CMD','control'),node('sol','SOL/ACTUATOR','control'),node('spool',short(c,18),'component',True),node('tap','Tap4/Tap5','measure'),node('return','RETURN','return')],edges=[('cmd','sol'),('sol','spool'),('spool','tap'),('spool','return')],mps=['CMD','PLUNGER/SPOOL','Tap4/5'],measure=[mp('PLUNGER/SPOOL','selector/modulation 밸브','자화만이 아니라 실제 플런저/스풀 이동·복귀','명령 ON/OFF와 기계이동을 직접 비교')],seq=['전기 지령·코일·플런저가 정상인지 먼저 확인한다.','스풀을 작동/해제할 때 Tap4/Tap5가 따라 움직이는지 확인한다.','최근 분해 이력이 있으면 스프링/오리피스/스풀 방향과 조립순서를 OEM 도면과 대조한다.'],ro=['전기 지령/솔레노이드 불량','공통 Tap6 저압','클러치 내부누설'],confirm=['지령/공급압 정상인데 스풀 이동 또는 압력 전환이 재현성 있게 불량이면 밸브 어셈블리 원인으로 확정한다.'],tools=['DMM','T/M 압력계','OEM 분해도'],loc='T/M selector/modulation valve body')
    if any(k in c for k in ('베어링','기타 내부 요소','1방향 클러치','과도한 토크컨버터 스톨','과부하')):
        return dict(nodes=[node('engine','ENGINE RPM/LOAD','measure'),node('converter','TORQUE CONVERTER','component'),node('focus',short(c,18),'component',True),node('output','T/M OUTPUT','inspect')],edges=[('engine','converter'),('converter','focus'),('focus','output')],mps=['RPM/STALL','NOISE LOCATION','OUTPUT ROTATION'],measure=[mp('RPM/STALL','엔진 RPM/부하 반응','F/R·무부하/부하 조건 비교','OEM stall 수치 미연결 시 방향/정상차 비교로만 판정')],seq=['엔진 출력부족과 클러치압 저하를 먼저 배제한다.','N/F/R 및 차량속도/엔진RPM 연동으로 소음·슬립의 회전체 위치를 분리한다.'],ro=['엔진 출력부족','클러치 apply 압력 저하','액슬/유니버설조인트 소음'],confirm=['압력/엔진 조건 정상에서 동일 회전체 조건으로 증상이 반복되고 출력 전달 이상이 일치할 때 기계부 원인으로 확정한다.'],tools=['회전계','청진기/전자청진기','T/M 압력계'],loc='토크컨버터/T/M 입력축·베어링·출력 동력경로')
    # generic but still fault specific
    return dict(nodes=[node('up','상류 조건','measure'),node('focus',short(c,18),'component',True),node('down','하류 반응','measure'),node('compare','정상측/반대방향','compare')],edges=[('up','focus'),('focus','down'),('down','compare')],mps=['UPSTREAM','DOWNSTREAM','COMPARE'],measure=[mp('COMPARE','정상측/반대방향','같은 조건에서 반응 비교','공통 원인과 해당 분기 원인을 분리')],seq=['상류 공통조건을 먼저 측정해 해당 원인 전용 고장인지 확인한다.','정상측/반대방향과 비교해 동일 현상이 공통인지 국부인지 분리한다.'],ro=['상류 공통 공급 문제','측정조건/재현조건 오류'],confirm=['상류 정상 + 해당 분기에서만 이상이 반복될 때 원인 확정도를 높인다.'],tools=['해당 계통 측정기'],loc='해당 T/M 기능분기')

def hydro_profile(c,system='유압'):
    if any(k in c for k in ('오일 레벨','오일레벨','오일 부족','작동유 부족')):
        return dict(nodes=[node('tank','HYD TANK\nLEVEL','inspect',True),node('suction','SUCTION','inspect'),node('pump','PUMP','measure'),node('valve','CONTROL V/V','component')],edges=[('tank','suction'),('suction','pump'),('pump','valve')],mps=['LEVEL','LEAK','PUMP P'],measure=[mp('LEVEL','작동유 탱크 지정 레벨','OEM 조건에서 레벨/거품 확인','보충 후 누유 원인과 재발 여부까지 확인')],seq=['보충 전에 외부누유/실린더 누유/최근 호스작업을 확인한다.','정상 레벨에서 펌프 소음·거품·메인압을 재시험한다.'],ro=['흡입라인 공기유입','펌프/커플링 고장','릴리프 개방'],confirm=['레벨 복구 후 펌프소음/압력/기능이 함께 정상화되고 재누유가 없을 때 연관성을 확정한다.'],tools=['OEM 작동유','레벨 확인도구'],loc='작동유 탱크/흡입호스/펌프')
    if '점도' in c or '사양' in c:
        return dict(nodes=[node('tank','OIL SPEC/TEMP','inspect',True),node('suction','SUCTION','inspect'),node('pump','PUMP','measure'),node('act','ACTUATOR RESPONSE','compare')],edges=[('tank','suction'),('suction','pump'),('pump','act')],mps=['OIL TEMP','SPEC','COLD/HOT RESPONSE'],measure=[mp('COLD/HOT RESPONSE','동일 기능 작동시간/소음','냉간·정상유온에서 반응 비교','점도 영향은 온도와 함께 변해야 함')],seq=['오일 등급/혼유/온도를 확인한 뒤 냉간과 정상유온 반응을 비교한다.','OEM 규격유로 정상화한 뒤 소음/응답/압력을 재시험한다.'],ro=['흡입 제한','펌프 마모','기계적 작동기 구속'],confirm=['규격/유온 정상화에 따라 증상이 재현성 있게 변하면 점도 원인으로 확정도를 높인다.'],tools=['온도계','오일 규격 자료'],loc='작동유 탱크 및 펌프 흡입부')
    if any(k in c for k in ('인입라인','흡입','공기유입')):
        return dict(nodes=[node('tank','TANK','source'),node('strainer','STRAINER','inspect'),node('line',short(c,18),'component',True),node('pump','PUMP IN/OUT','measure')],edges=[('tank','strainer'),('strainer','line'),('line','pump')],mps=['STRAINER','SUCTION JOINT','FOAM/PUMP P'],measure=[mp('SUCTION JOINT','탱크→펌프 흡입라인','꺾임·붕괴·클램프/씰·공기유입','거품/캐비테이션과 펌프압 동시 비교')],seq=['흡입호스 외관만 보지 말고 운전 중 호스 붕괴/거품/캐비테이션을 확인한다.','구간별 접합부를 정상화한 뒤 펌프압과 소음 변화를 재시험한다.'],ro=['오일 레벨 부족','펌프 내부마모','릴리프 이상'],confirm=['흡입 구간 수리 후 거품/소음/압력저하가 동시에 정상화되면 해당 구간 원인으로 확정한다.'],tools=['손전등','압력계'],loc='작동유 탱크→스트레이너→메인펌프 흡입라인')
    if '필터' in c or '이물질' in c or '오염' in c:
        return dict(nodes=[node('tank','TANK','source'),node('filter',short(c,18),'component',True),node('pump','PUMP','measure'),node('return','RETURN','inspect')],edges=[('tank','filter'),('filter','pump'),('pump','return')],mps=['FILTER CONDITION','UP/DOWN RESPONSE','DEBRIS'],measure=[mp('DEBRIS','필터/오일 샘플','금속·고무·섬유 오염물 확인','발생원을 추적하고 필터만 교환해 끝내지 않음')],seq=['필터 절개/오일샘플로 이물 종류를 확인한다.','필터/스트레이너 전후 반응 또는 교환 전후 펌프소음/압력을 비교한다.'],ro=['단순 오일레벨 부족','흡입호스 공기유입','펌프 기계손상'],confirm=['이물 제거/필터 정상화 후 압력·소음이 정상화되고 오염원까지 제거되면 확정한다.'],tools=['필터 절개도구','샘플통'],loc='흡입 스트레이너/리턴필터 및 탱크')
    if '샤프트' in c or '커플링' in c:
        return dict(nodes=[node('engine','ENGINE DRIVE','source'),node('coupling',short(c,18),'component',True),node('pump','PUMP SHAFT','inspect'),node('pressure','SYSTEM P','measure')],edges=[('engine','coupling'),('coupling','pump'),('pump','pressure')],mps=['COUPLING ROTATION','PUMP SHAFT','SYSTEM P'],measure=[mp('COUPLING ROTATION','엔진→펌프 커플링','엔진 회전 시 헛돎/슬립/파손 확인','압력 0/저하와 실제 구동상태 일치 확인')],seq=['펌프를 교환하기 전에 입력축/커플링의 실제 회전을 확인한다.','부하가 걸릴 때만 헛도는지 표시마킹/관찰로 재현한다.'],ro=['흡입 제한','릴리프 열린 고착','펌프 내부마모'],confirm=['입력회전 단절이 압력저하와 동시에 재현되고 커플링 수리 후 정상화되면 확정한다.'],tools=['페인트마커','거울/보어스코프'],loc='엔진 구동부와 메인 유압펌프 커플링')
    if '시일불량' in c:
        return dict(nodes=[node('pump','PUMP','source'),node('seal',short(c,18),'component',True),node('leak','EXTERNAL/INTERNAL LEAK','inspect'),node('tank','TANK LEVEL','compare')],edges=[('pump','seal'),('seal','leak'),('leak','tank')],mps=['SEAL AREA','LEVEL TREND','SYSTEM P'],measure=[mp('SEAL AREA','펌프/축 시일 주변','외부 누유·흡입공기 흔적','누유 위치와 레벨저하/압력변화를 동시에 기록')],seq=['시일 외부 흔적과 흡입공기 가능성을 분리한다.','정상 레벨에서 압력과 누유량 경향을 재확인한다.'],ro=['호스/피팅 누유','과충전/브리더 문제','펌프 본체 크랙'],confirm=['시일부에서 누유/공기유입이 재현되고 해당 시일 수리 후 정상화되면 확정한다.'],tools=['세척제','UV 누유염료(허용 시)'],loc='메인펌프 샤프트/시일부')
    return dict(nodes=[node('tank','TANK','source'),node('focus',short(c,18),'component',True),node('pump','PUMP P','measure'),node('valve','CONTROL V/V','component')],edges=[('tank','focus'),('focus','pump'),('pump','valve')],mps=['UPSTREAM','DOWNSTREAM','RETEST'],measure=[mp('RETEST','의심구간 전/후','수리/격리 전후 기능 비교','동일 유온·부하에서 재현')],seq=['상류 공급과 하류 부하를 분리한다.','의심부 격리/수리 전후를 같은 조건에서 비교한다.'],ro=['공통 공급 문제','하류 작동기 문제'],confirm=['의심부 조치 전후로 증상이 일관되게 변하면 확정한다.'],tools=['유압 압력계'],loc='해당 유압 기능구간')

def work_profile(c):
    if any(k in c for k in ('과열','온도')):
        return dict(nodes=[node('tank','OIL TEMP','measure'),node('pump','PUMP','source'),node('relief','RELIEF/HEAT','control'),node('spool','CONTROL SPOOL','component',True),node('return','RETURN','return')],edges=[('tank','pump'),('pump','relief'),('relief','spool'),('spool','return')],mps=['OIL TEMP','P','RETURN TEMP'],measure=[mp('RETURN TEMP','밸브 리턴/탱크','작업 전후 온도 변화·지속 릴리프 여부','정상유온에서 스풀 증상 재확인')],seq=['냉간과 정상유온에서 스풀 힘/복귀 차이를 같은 레버 조작으로 비교한다.','지속 릴리프·내부누설·쿨러/리턴 제한 등 열 발생 원인을 먼저 제거한다.'],ro=['스풀 휨/스크래치','링케이지 구속','밸브바디 체결응력'],confirm=['유온을 정상화했을 때 스풀 증상이 사라지고 과열 재현 시 다시 나타나면 열/점도 원인으로 확정도를 높인다.'],tools=['접촉식/IR 온도계','압력계'],loc='작동유 탱크→메인밸브 리턴/릴리프 구간')
    if '이물' in c or '오염' in c or '유로' in c:
        return dict(nodes=[node('p','P PORT','measure'),node('spool',short(c,18),'component',True),node('ab','A/B PORT','measure'),node('return','RETURN/FILTER','inspect')],edges=[('p','spool'),('spool','ab'),('spool','return')],mps=['P','A/B','DEBRIS'],measure=[mp('DEBRIS','스풀/필터/오일','바니시·금속·실링 조각','청소 전후 스풀 자유이동과 A/B 반응 비교')],seq=['외부 링케이지를 분리해 스풀 자체 걸림인지 먼저 확인한다.','오일/필터의 이물 종류를 확인하고 오염원 제거 후 스풀을 재시험한다.'],ro=['외부 링케이지 구속','밸브바디 과다체결/변형','리턴스프링 손상'],confirm=['이물 제거 후 스풀 이동·복귀와 A/B 압력전환이 정상화되면 오염 원인으로 확정한다.'],tools=['청정 작업도구','압력계'],loc='메인 컨트롤밸브 해당 LIFT/TILT/AUX 스풀')
    if any(k in c for k in ('과다조임','토크불량','몸체 뒤틀림','고정볼트')):
        return dict(nodes=[node('mount','VALVE MOUNT BOLTS','inspect',True),node('body','VALVE BODY','component'),node('spool','SPOOL FREE MOVE','compare'),node('ab','A/B RESPONSE','measure')],edges=[('mount','body'),('body','spool'),('spool','ab')],mps=['MOUNT TORQUE','SPOOL FORCE','A/B'],measure=[mp('MOUNT TORQUE','컨트롤밸브 고정볼트','OEM 체결순서/토크와 비교','임의 풀림 상태로 운전하지 말고 감압 후 정비조건에서 확인')],seq=['유압을 완전히 감압하고 외부 링케이지를 분리한 상태에서 스풀 자체 이동저항을 확인한다.','고정볼트/연결피팅을 OEM 체결조건으로 교정한 뒤 스풀 자유이동과 A/B 반응을 재확인한다.'],ro=['스풀 자체 휨/스크래치','오염/바니시','링케이지 정렬불량'],confirm=['OEM 체결상태 교정 전후로 스풀 구속이 반복적으로 변하면 밸브바디 체결응력 원인으로 확정한다.'],tools=['토크렌치','압력계'],loc='메인 컨트롤밸브 바디 고정부/피팅부')
    if '링케이지' in c or '정렬' in c:
        return dict(nodes=[node('lever','OPERATOR LEVER','source'),node('link',short(c,18),'component',True),node('spool','SPOOL','compare'),node('ab','A/B PORT','measure')],edges=[('lever','link'),('link','spool'),('spool','ab')],mps=['LINK TRAVEL','SPOOL TRAVEL','A/B'],measure=[mp('LINK TRAVEL','레버→밸브 링크','레버 전/후 스트로크·걸림·중립복귀','링크 분리 후 스풀 단독 움직임과 비교')],seq=['엔진 OFF/감압 상태에서 링케이지를 스풀에서 분리해 각각 따로 움직여 본다.','링크 단독 불량인지 스풀 내부 불량인지 분리한 뒤 조정한다.'],ro=['스풀 휨/보어 손상','리턴스프링 손상','밸브바디 과다체결'],confirm=['링크 분리 시 스풀이 자유롭고 링크 연결 시에만 걸림이 재현되면 링케이지 원인으로 확정한다.'],tools=['자/캘리퍼','윤활제(지정부위)'],loc='운전레버→메인 컨트롤밸브 외부 링크')
    if '스풀' in c and any(k in c for k in ('휨','마모','스트로크')):
        return dict(nodes=[node('link','LINK DISCONNECT','isolate'),node('spool',short(c,18),'component',True),node('ab','A/B PORT','measure'),node('return','NEUTRAL RETURN','compare')],edges=[('link','spool'),('spool','ab'),('spool','return')],mps=['SPOOL FREE MOVE','FULL STROKE','A/B'],measure=[mp('FULL STROKE','해당 스풀','외부 링크 분리 후 전 스트로크/중립복귀','걸림 위치와 A/B 압력전환이 일치하는지 확인')],seq=['외부 링케이지를 분리해 스풀 자체의 전 스트로크를 확인한다.','감압 상태에서 특정 위치에서만 걸리는지, 중립복귀가 되는지 반복한다.'],ro=['외부 링케이지 정렬불량','밸브바디 과다체결','오일 오염'],confirm=['링크/체결/오염을 배제해도 스풀 자체가 동일 지점에서 걸리면 스풀/보어 기계불량으로 확정한다.'],tools=['다이얼게이지/캘리퍼(필요 시)','압력계'],loc='메인 컨트롤밸브 해당 스풀/보어')
    if '스프링' in c:
        return dict(nodes=[node('lever','LEVER RELEASE','source'),node('spring',short(c,18),'component',True),node('spool','SPOOL NEUTRAL','compare'),node('ab','A/B RESIDUAL','measure')],edges=[('lever','spring'),('spring','spool'),('spool','ab')],mps=['NEUTRAL RETURN','A/B RESIDUAL','SPRING'],measure=[mp('NEUTRAL RETURN','레버 해제 후 스풀','중립까지 완전 복귀하는지','A/B 잔압/작동기 크리프와 함께 판단')],seq=['외부 링크가 자유로운 상태에서 레버 해제 시 스풀이 중립으로 돌아오는지 확인한다.','복귀불량과 A/B 잔압/작동기 크리프가 동시에 나타나는지 확인한다.'],ro=['링케이지 구속','스풀/보어 오염','밸브바디 체결응력'],confirm=['링크와 스풀이 자유로운데 스프링 복귀력이 없고 교환 후 중립이 정상화되면 스프링 원인으로 확정한다.'],tools=['압력계','청정 작업도구'],loc='컨트롤밸브 해당 스풀의 리턴스프링')
    if any(k in c for k in ('시일','플레이트','크랙','누유')):
        return dict(nodes=[node('p','P PORT','measure'),node('body',short(c,18),'component',True),node('ab','A/B PORT','measure'),node('leak','EXTERNAL/INTERNAL LEAK','inspect')],edges=[('p','body'),('body','ab'),('body','leak')],mps=['P','A/B','LEAK LOCATION'],measure=[mp('LEAK LOCATION','밸브바디/시일플레이트/포트','세척 후 누유 시작점을 압력걸어 확인','인접 피팅에서 흘러온 오일과 구분')],seq=['밸브 외부를 세척한 뒤 압력 조건에서 최초 젖는 위치를 찾는다.','필요하면 해당 A/B 포트를 안전하게 격리해 내부누설과 외부누설을 분리한다.'],ro=['인접 호스/피팅 누유','실린더 내부누설','과압/릴리프 이상'],confirm=['최초 누유점/격리시험이 해당 바디·시일을 반복 지목하면 확정한다.'],tools=['세척제','압력계','UV 누유염료(허용 시)'],loc='메인 컨트롤밸브 바디/시일 플레이트')
    if '펌프 토출압' in c or '릴리프' in c:
        return dict(nodes=[node('tank','TANK','source'),node('pump','PUMP/P PORT','measure'),node('relief',short(c,18),'control',True),node('spool','CONTROL SPOOL','component')],edges=[('tank','pump'),('pump','relief'),('relief','spool')],mps=['P','RELIEF','MODEL SPEC'],measure=[mp('P','컨트롤밸브 계기포트','차종별 메인압','D20 181±3.5 / D25 195±3.5 / D30 215.5±3.5 / D33 240(+5,-0) bar, 매뉴얼 회로도')],seq=['차종을 먼저 확정하고 작동유 50±5°C 등 OEM 시험조건에서 압력을 측정한다.','조정 전 펌프 공급·릴리프 스풀 자유이동·하류 대누설을 분리한다.'],ro=['펌프 흡입/구동 문제','실린더/밸브 대내부누설','시험조건 오류'],confirm=['상류 공급 정상 상태에서 릴리프 수리/교정 후 OEM 압력으로 반복 복귀하면 릴리프 원인으로 확정한다.'],tools=['300 bar 압력계','온도계'],loc='메인 컨트롤밸브 계기포트/릴리프')
    if '공기' in c:
        return dict(nodes=[node('tank','TANK','source'),node('pump','PUMP','component'),node('spool','CONTROL V/V','control'),node('act','CYLINDER','component'),node('return','RETURN/BLEED','inspect',True)],edges=[('tank','pump'),('pump','spool'),('spool','act'),('act','return')],mps=['FOAM','ACTUATOR JERK','BLEED/RETURN'],measure=[mp('FOAM','탱크/리턴','거품과 작동기 떨림 동시 확인','흡입누기/저레벨 원인을 먼저 수리')],seq=['레벨/흡입누기를 정상화한 뒤 지정 절차로 공기를 제거한다.','에어 제거 전후 작동기 떨림·소음·압력반응을 비교한다.'],ro=['기계적 마스트 구속','스풀 걸림','펌프 마모'],confirm=['에어 제거 후 떨림/반응지연이 사라지고 거품이 재발하지 않으면 공기혼입을 확정한다.'],tools=['투명 회수호스(허용 시)','OEM bleed 절차'],loc='작동유 탱크/실린더/리턴 경로')
    return dict(nodes=[node('input','INPUT/LINK','source'),node('focus',short(c,18),'component',True),node('ab','A/B RESPONSE','measure'),node('act','ACTUATOR','component')],edges=[('input','focus'),('focus','ab'),('ab','act')],mps=['INPUT','A/B','RETEST'],measure=[mp('RETEST','해당 기능','격리/수리 전후 같은 부하에서 비교','공통 공급과 기계구속을 분리')],seq=['외부 입력/링크와 밸브 내부를 분리해 각각 확인한다.','상류 공급과 하류 작동기를 격리한 뒤 동일 증상 재현 여부를 비교한다.'],ro=['공통 유압 저하','하류 실린더/기계구속'],confirm=['해당 구성품 격리/수리 전후로 증상이 반복적으로 변하면 원인으로 확정한다.'],tools=['압력계'],loc='해당 작업장치 기능부')

def steer_profile(c):
    if any(k in c for k in ('덮개 과다조임','컬럼','정렬')):
        return dict(nodes=[node('wheel','STEERING WHEEL','source'),node('column',short(c,18),'component',True),node('unit','STEERING UNIT','component'),node('lr','L/R PORT','measure')],edges=[('wheel','column'),('column','unit'),('unit','lr')],mps=['COLUMN FREE','UNIT INPUT','L/R'],measure=[mp('COLUMN FREE','컬럼/유니버설조인트','유압부하 제거/안전상태에서 기계적 걸림 비교','컬럼 분리 전후 스티어링유닛 입력축 자유도를 비교')],seq=['전륜을 안전하게 지지하고 엔진 OFF/압력 해제 조건에서 컬럼 기계구속 여부를 확인한다.','컬럼과 스티어링유닛 연결을 분리해 어느 쪽에서 걸림이 남는지 비교한다.'],ro=['스티어링유닛 내부 스풀구속','스티어 액슬 킹핀/링크 기계구속','유압 공급압 이상'],confirm=['컬럼 연결/정렬 교정 전후로 조작력이 즉시 변하고 유닛 단독은 정상일 때 컬럼/체결 원인으로 확정한다.'],tools=['토크렌치','기본 수공구'],loc='핸들→스티어링 컬럼→스티어링유닛 입력부')
    if '윤활 부족' in c:
        return dict(nodes=[node('wheel','WHEEL/COLUMN','source'),node('unit',short(c,18),'component',True),node('lr','L/R PORT','measure'),node('return','RETURN','return')],edges=[('wheel','unit'),('unit','lr'),('unit','return')],mps=['INPUT FEEL','L/R P','RETURN'],measure=[mp('INPUT FEEL','스티어링유닛 입력','냉간/열간·엔진OFF/ON 비교','유압 정상인데 기계적 마찰감이 남는지')],seq=['유압 공급압과 액슬 기계구속을 먼저 배제한다.','OEM 허용부위 윤활/정비 후 입력 마찰감과 복귀를 재확인한다.'],ro=['컬럼 정렬불량','유닛 스풀구속','스티어 액슬 기계구속'],confirm=['유압/액슬 정상 상태에서 윤활 정비 전후 조작력이 반복적으로 개선되면 원인으로 확정한다.'],tools=['OEM 지정 윤활제'],loc='스티어링유닛/컬럼 연결부')
    if any(k in c for k in ('작동유 부족','점도','공기혼입','계통 공기')):
        base=hydro_profile(c,'스티어링')
        base['nodes']=[node('tank','HYD TANK','inspect'),node('priority','PRIORITY V/V','measure'),node('unit','STEERING UNIT','measure'),node('cyl','STEER CYL L/R','component',True),node('return','RETURN','return')]
        base['edges']=[('tank','priority'),('priority','unit'),('unit','cyl'),('cyl','return')]
        base['mps']=['TANK','PRIORITY P','L/R','RETURN']
        base['loc']='작동유 탱크→우선순위밸브→스티어링유닛→실린더'
        return base
    if '호스 연결' in c or '유압라인' in c:
        return dict(nodes=[node('priority','PRIORITY','source'),node('hose',short(c,18),'component',True),node('unit','STEERING UNIT','component'),node('cyl','STEER CYL','component')],edges=[('priority','hose'),('hose','unit'),('unit','cyl')],mps=['HOSE FITTING','UP/DOWN P','LEAK'],measure=[mp('HOSE FITTING','조향 고압호스/피팅','누유·호스 비틀림·압력시 팽창','상류/하류 압력반응 비교')],seq=['호스 라우팅/꺾임/피팅 체결을 확인하고 압력 조건에서 누유를 찾는다.','호스 전후 반응을 비교해 내부박리/제한 여부를 확인한다.'],ro=['우선순위밸브 문제','스티어링유닛 내부누설','실린더 기계구속'],confirm=['해당 호스/피팅 수리 후 조향압·응답이 정상화되면 확정한다.'],tools=['압력계','토크렌치'],loc='우선순위밸브↔스티어링유닛↔실린더 호스')
    if '샤프트 시일' in c:
        return dict(nodes=[node('input','COLUMN INPUT','source'),node('seal',short(c,18),'component',True),node('unit','STEERING UNIT','component'),node('drain','EXTERNAL LEAK','inspect')],edges=[('input','seal'),('seal','unit'),('seal','drain')],mps=['SEAL LEAK','SUPPLY P','RETURN'],measure=[mp('SEAL LEAK','스티어링유닛 입력축 시일','세척 후 최초 누유점','인접호스에서 흘러온 오일과 분리')],seq=['유닛 주변을 세척하고 실제 조향압력에서 누유 시작점을 관찰한다.','공급압 과다/리턴 막힘을 먼저 배제한 뒤 시일을 판정한다.'],ro=['인접 호스/피팅 누유','리턴라인 제한','비정상 공급압'],confirm=['정상압력에서 입력축 시일 자체에서 반복 누유하고 수리 후 사라지면 확정한다.'],tools=['세척제','압력계'],loc='스티어링유닛 컬럼 입력축 시일')
    if '스풀' in c or '스티어링유닛 작동불량' in c:
        return dict(nodes=[node('priority','PRIORITY P','measure'),node('unit',short(c,18),'component',True),node('left','L PORT','measure'),node('right','R PORT','measure'),node('cyl','CYLINDER','component')],edges=[('priority','unit'),('unit','left'),('unit','right'),('left','cyl'),('right','cyl')],mps=['SUPPLY','L','R','MECH ISOLATE'],measure=[mp('L/R','스티어링유닛 좌/우 출구','좌/우 조향 명령에 따른 압력/유량 반전','실린더/액슬 기계구속 분리 후 비교')],seq=['공급압 정상 여부를 먼저 확인하고 좌/우 출구 반응을 비교한다.','실린더/링크 기계구속을 배제한 상태에서도 한 방향/중립 반응이 비정상인지 확인한다.'],ro=['우선순위밸브 공급문제','실린더 내부누설/액슬 기계구속','컬럼 정렬불량'],confirm=['공급 정상 + 하류 기계부 정상인데 유닛 L/R 전환만 반복 불량이면 스티어링유닛을 확정한다.'],tools=['스티어링 압력계','기본 수공구'],loc='스티어링유닛 및 L/R 출구포트')
    if '오염' in c:
        return dict(nodes=[node('tank','TANK/FILTER','inspect'),node('priority','PRIORITY','component'),node('unit','STEERING UNIT','component',True),node('return','RETURN','inspect')],edges=[('tank','priority'),('priority','unit'),('unit','return')],mps=['OIL SAMPLE','FILTER','L/R'],measure=[mp('OIL SAMPLE','탱크/필터','금속·바니시·고무조각','오염원 제거 전 단순 밸브교환 금지')],seq=['필터/오일의 이물 종류와 발생원을 확인한다.','플러싱/오염원 제거 후 유닛 L/R 반응을 재시험한다.'],ro=['오일 레벨/점도 문제','컬럼/액슬 기계구속','우선순위밸브 압력문제'],confirm=['오염 제거 후 조향 반응/복귀가 정상화되고 오염 재발이 없을 때 확정한다.'],tools=['오일 샘플통','필터 절개도구'],loc='탱크/필터→우선순위밸브→스티어링유닛')
    return dict(nodes=[node('supply','SUPPLY','measure'),node('focus',short(c,18),'component',True),node('lr','L/R','measure'),node('cyl','CYL/AXLE','compare')],edges=[('supply','focus'),('focus','lr'),('lr','cyl')],mps=['SUPPLY','L/R','COMPARE'],measure=[mp('COMPARE','좌/우 또는 정상측','동일조건 비교','공통 공급과 국부 원인을 분리')],seq=['공급압과 하류 기계부를 먼저 분리한다.','좌/우 방향 또는 정상차와 비교해 국부 고장인지 확인한다.'],ro=['공통 공급압 문제','액슬/실린더 기계구속'],confirm=['상·하류 정상에서 해당 부품 반응만 반복 이상이면 확정한다.'],tools=['압력계'],loc='스티어링 해당 기능부')

def brake_profile(c, sid):
    if '페달 스트로크' in c or '페달 정렬' in c or '연결장치 정렬' in c:
        return dict(nodes=[node('pedal','BRAKE PEDAL','source'),node('link',short(c,18),'component',True),node('master','MASTER CYL','component'),node('out','BRAKE OUT','measure')],edges=[('pedal','link'),('link','master'),('master','out')],mps=['PEDAL GEOMETRY','PUSHROD','B-OUT'],measure=[mp('PEDAL GEOMETRY','D20/25/30/33S-7 페달조정','piston rod clearance 1 mm; yoke A 63.5 mm; rod B 281.5±1 mm; stop C 5±1.5 mm; inner screw D 20±1.5 mm','OEM 7-2-3, p314; SE-7은 별도 7-2-4 기준 사용'),mp('PUSHROD','마스터 푸시로드','master pushrod travel 32.5 mm','OEM 7-2-1 주요사양')],seq=['차량 모델 S/SE를 먼저 구분해 해당 페달 조정치를 사용한다.','페달/링크를 손으로 복귀시켜 기계적 걸림·휨·유격을 확인한다.','조정 후 B-OUT 압력/제동력을 같은 조건에서 재시험한다.'],ro=['유압계통 공기','마스터/브레이크밸브 내부누설','액슬 브레이크 기계고장'],confirm=['OEM 페달기하 교정 후 푸시로드 스트로크와 제동압/제동력이 함께 정상화되면 페달/링크 원인으로 확정한다.'],tools=['자/캘리퍼','토크렌치'],loc='브레이크 페달→링크→마스터실린더 푸시로드')
    if '공기' in c:
        return dict(nodes=[node('reservoir','BRAKE RESERVOIR','inspect'),node('master','MASTER CYL','component'),node('line',short(c,18),'component',True),node('axle','AXLE BRAKE L/R','component')],edges=[('reservoir','master'),('master','line'),('line','axle')],mps=['PEDAL FEEL','BLEED L/R','RESERVOIR'],measure=[mp('PEDAL FEEL','브레이크 페달','펌핑 시 단단해지는지/스펀지감','공기 가능성의 예비시험일 뿐 단독 확정 금지')],seq=['리저버 레벨/외부누유를 먼저 확인한 뒤 OEM 순서로 에어를 제거한다.','블리드 전후 페달감과 B-OUT/제동력을 비교하고 기포가 재발하는지 확인한다.'],ro=['페달 조정불량','마스터 내부 바이패스','액슬 피스톤 시일누설'],confirm=['에어 제거 후 페달감·압력·제동력이 정상화되고 기포가 재발하지 않을 때 확정한다.'],tools=['브레이크 블리드 호스/용기','적정 브레이크유'],loc='브레이크 리저버→마스터→좌/우 액슬 블리더')
    if '작동유 부족' in c:
        return dict(nodes=[node('tank','MAIN HYD LEVEL','inspect',True),node('supply','BRAKE SUPPLY','measure'),node('master','MASTER','component'),node('axle','AXLE BRAKE','component')],edges=[('tank','supply'),('supply','master'),('master','axle')],mps=['HYD LEVEL','SUPPLY','LEAK'],measure=[mp('HYD LEVEL','작동유 탱크','OEM 레벨조건','보충 전 누유원인 확인')],seq=['작동유 부족 원인을 외부누유/최근정비/다른 작동기 누유까지 추적한다.','정상 레벨에서 브레이크 공급반응과 메인유압 기능을 재시험한다.'],ro=['브레이크 전용 밸브/마스터 결함','브레이크 라인 공기','페달 조정불량'],confirm=['레벨 정상화로 브레이크와 공통 유압기능이 함께 정상화되면 연관성을 확정한다.'],tools=['작동유 레벨 확인도구'],loc='작동유 탱크→컨트롤밸브 브레이크 공급분기')
    if '체크밸브' in c:
        return dict(nodes=[node('main','MAIN HYD','source'),node('orifice','ORIFICE','component'),node('check',short(c,18),'component',True),node('master','MASTER IN','measure'),node('return','BACKFLOW BLOCK','compare')],edges=[('main','orifice'),('orifice','check'),('check','master'),('master','return')],mps=['CHECK UP','CHECK DOWN','PRESSURE HOLD'],measure=[mp('PRESSURE HOLD','체크밸브 전/후','공급 후 역류/압력유지 반응 비교','OEM 누설 허용치 미확인 시 임의 시간/압력강하 수치 금지')],seq=['공통 유압공급 정상 상태에서 체크밸브 전/후 반응을 비교한다.','하류를 안전하게 격리해 하류누설과 체크밸브 역류를 분리한다.'],ro=['마스터/브레이크밸브 내부누설','액슬 시일 대누설','공통 메인유압 저하'],confirm=['하류 격리 후에도 체크밸브 전후의 역류/유지불량이 반복되면 체크밸브를 확정한다.'],tools=['브레이크 공급용 게이지/어댑터','블랭킹 플러그'],loc='메인 컨트롤밸브→오리피스→브레이크 체크밸브')
    if '릴리프' in c or '스풀 스프링' in c:
        return dict(nodes=[node('main','MAIN HYD','source'),node('supply','BRAKE SUPPLY','measure'),node('valve',short(c,18),'component',True),node('bout','B-OUT','measure'),node('return','RETURN','return')],edges=[('main','supply'),('supply','valve'),('valve','bout'),('valve','return')],mps=['B-IN','B-OUT','RETURN'],measure=[mp('B-OUT','브레이크밸브 출구','페달 apply/release 시 압력 형성·복귀','마스터 relief cracking 40 bar는 주요사양이며 피스톤시일 누설판정치로 오용 금지')],seq=['B-IN 정상 상태에서 페달 작동에 따른 B-OUT 상승·복귀를 확인한다.','액슬 하류를 격리해 밸브 자체와 하류 대누설을 분리한다.','분해 전 스프링 파손/스풀 복귀불량이 압력패턴과 일치하는지 확인한다.'],ro=['공통 공급유량 부족','마스터/액슬 하류 누설','페달 스트로크 불충분'],confirm=['공급·하류를 배제한 상태에서 밸브 출력/복귀만 반복 비정상이면 해당 릴리프/스풀 스프링을 확정한다.'],tools=['브레이크 회로 압력계','블랭킹 플러그'],loc='브레이크밸브/마스터 밸브바디')
    if '브레이크밸브 풀림' in c:
        return dict(nodes=[node('pedal','PEDAL/LINK','source'),node('mount',short(c,18),'component',True),node('valve','BRAKE VALVE','component'),node('line','PORT/LINES','inspect')],edges=[('pedal','mount'),('mount','valve'),('valve','line')],mps=['MOUNT MOVEMENT','PORT STRAIN','B-OUT'],measure=[mp('MOUNT MOVEMENT','브레이크밸브 고정부','페달 작동 시 밸브바디 움직임/포트 응력','OEM 체결상태로 교정 후 재시험')],seq=['페달 작동 중 밸브바디/브래킷이 움직이는지 관찰한다.','유압 감압 후 고정부·포트 체결과 링크 정렬을 OEM 상태로 복구한다.'],ro=['페달 링크 휨/정렬불량','브레이크밸브 내부누설','라인 공기'],confirm=['고정부 정상화 후 페달 스트로크와 제동압이 안정되면 풀림 원인으로 확정한다.'],tools=['토크렌치','마킹펜'],loc='페달 링크와 브레이크밸브 고정 브래킷')
    if '주조품 구멍' in c or '크랙' in c:
        return dict(nodes=[node('supply','BRAKE SUPPLY','source'),node('body',short(c,18),'component',True),node('leak','FIRST WET POINT','inspect'),node('out','B-OUT','measure')],edges=[('supply','body'),('body','leak'),('body','out')],mps=['BODY CLEAN','PRESSURIZE','LEAK ORIGIN'],measure=[mp('LEAK ORIGIN','브레이크 밸브/마스터 주조바디','세척 후 압력 걸었을 때 최초 젖는 지점','피팅/호스에서 흘러온 오일과 구분')],seq=['바디를 완전히 세척/건조하고 안전하게 압력을 걸어 누유 시작점을 관찰한다.','인접 피팅을 닦아가며 최초 젖는 위치가 주조바디인지 분리한다.'],ro=['피팅/호스 누유','블리더 누유','리저버 넘침'],confirm=['주조바디 자체에서 누유가 반복 재현되면 바디결함으로 확정한다.'],tools=['세척제','거울/UV 염료(허용 시)'],loc='브레이크밸브/마스터 주조바디')
    if '공급유량' in c or '브레이크밸브 결함' in c:
        return dict(nodes=[node('main','MAIN HYD','measure'),node('supply','BRAKE BRANCH','measure'),node('valve',short(c,18),'component',True),node('master','MASTER/B-OUT','measure'),node('axle','AXLE L/R','isolate')],edges=[('main','supply'),('supply','valve'),('valve','master'),('master','axle')],mps=['MAIN','B-IN','B-OUT','AXLE L/R'],measure=[mp('AXLE L/R','좌/우 액슬 브레이크 입구','정식 캡/블랭크로 좌·우/하류 격리','바이스그립으로 호스 압착 금지')],seq=['메인유압과 브레이크 B-IN을 같은 조건에서 비교한다.','B-IN 정상/B-OUT 이상이면 하류를 격리해 밸브/마스터와 액슬누설을 분리한다.','좌우 액슬을 개별 격리해 특정 분기에서만 압력/페달이 회복되는지 확인한다.'],ro=['공통 메인유압 저하','페달/링크 조정불량','액슬 피스톤 시일 대누설'],confirm=['공급 정상 + 하류 격리 후에도 B-OUT 반응이 비정상이면 브레이크밸브/마스터 내부를 확정 후보로 올린다.'],tools=['브레이크 압력계','정격 블랭킹 플러그'],loc='컨트롤밸브 브레이크 분기→브레이크밸브/마스터→좌우 액슬')
    return dict(nodes=[node('pedal','PEDAL','source'),node('focus',short(c,18),'component',True),node('bout','B-OUT','measure'),node('axle','AXLE L/R','compare')],edges=[('pedal','focus'),('focus','bout'),('bout','axle')],mps=['PEDAL','B-OUT','L/R'],measure=[mp('L/R','좌/우 브레이크','동일 입력에서 반응 비교','공통원인과 한쪽 고장을 분리')],seq=['기계입력과 유압출력을 분리해 확인한다.','좌/우 액슬 반응과 정상측을 비교한다.'],ro=['페달 조정불량','공통 공급저하'],confirm=['상류 정상에서 해당 구성품 반응만 반복 비정상이면 확정한다.'],tools=['브레이크 압력계'],loc='해당 브레이크 기능부')

def axle_profile(c):
    if '부족' in c:
        return dict(nodes=[node('fill','AXLE LEVEL/FILL','inspect',True),node('diff','DIFFERENTIAL','component'),node('hub','L/R HUB','compare'),node('breather','BREATHER','inspect')],edges=[('fill','diff'),('diff','hub'),('diff','breather')],mps=['LEVEL','LEAK','L/R TEMP'],measure=[mp('L/R TEMP','좌/우 허브/액슬','동일 주행 후 온도·소음 비교','오일 레벨 복구 전 장시간 주행 금지')],seq=['지정 레벨에서 실제 오일량을 확인하고 누유점/씰 흔적을 찾는다.','정상 레벨·규격유로 복구 후 좌우 허브 온도/소음과 주행증상을 재확인한다.'],ro=['베어링/기어 기계손상','브레이크 끌림','잘못된 오일 규격'],confirm=['레벨 복구로 소음/온도가 개선되고 누유원인까지 수리되면 확정한다.'],tools=['OEM axle oil','온도계'],loc='드라이브액슬 레벨/주입 플러그와 좌우 허브')
    if '과다' in c:
        return dict(nodes=[node('fill','AXLE LEVEL','inspect',True),node('breather','BREATHER','inspect'),node('seal','SEALS','inspect'),node('hub','HUB/TEMP','compare')],edges=[('fill','breather'),('breather','seal'),('seal','hub')],mps=['LEVEL','BREATHER','SEAL LEAK'],measure=[mp('BREATHER','액슬 브리더','막힘/압력축적·오일분출','정상 레벨 교정 전후 누유/발열 비교')],seq=['과다주입 여부를 지정 레벨 기준으로 확인한다.','브리더 막힘을 함께 확인한 뒤 레벨 교정 후 누유/온도를 재시험한다.'],ro=['브리더 막힘','시일 손상','잘못된 오일 점도'],confirm=['정상 레벨/브리더 복구 후 누유·발열이 정상화되면 확정한다.'],tools=['레벨 확인도구'],loc='드라이브액슬 주입/레벨 플러그와 브리더')
    if '사양' in c or '종류' in c:
        return dict(nodes=[node('sample','OIL SAMPLE/SPEC','inspect',True),node('diff','DIFF GEARS','component'),node('brake','WET BRAKE','component'),node('hub','HUB TEMP/NOISE','compare')],edges=[('sample','diff'),('sample','brake'),('diff','hub'),('brake','hub')],mps=['SPEC','CONTAMINATION','TEMP/NOISE'],measure=[mp('SPEC','액슬 오일 샘플/정비이력','OEM 지정 규격/혼유 여부','색만으로 규격 판정하지 말고 용기/이력 확인')],seq=['최근 교환이력과 실제 주입유 규격을 확인한다.','규격유로 교환 후 동일 주행조건에서 브레이크소음/허브온도/기어소음을 비교한다.'],ro=['오일 레벨 이상','브레이크 디스크/기어 기계손상','브리더 막힘'],confirm=['규격유 교환으로 증상이 재현성 있게 개선되고 다른 원인이 배제되면 확정한다.'],tools=['오일 샘플통','OEM 윤활유 표'],loc='드라이브액슬 오일 주입부/습식브레이크 하우징')
    if '브리더' in c:
        return dict(nodes=[node('housing','AXLE HOUSING','source'),node('breather','BREATHER','component',True),node('seal','SEALS','inspect'),node('level','OIL LEVEL','inspect')],edges=[('housing','breather'),('housing','seal'),('housing','level')],mps=['BREATHER FLOW','SEAL LEAK','LEVEL'],measure=[mp('BREATHER FLOW','액슬 브리더','막힘/오염/호스꺾임','청소 전후 하우징 압력징후·누유 비교')],seq=['브리더 캡/통로를 분리해 막힘을 확인하고 청소한다.','오일 레벨이 정상인데 시일에서 분출/누유가 생기는지 재시험한다.'],ro=['오일 과다','시일 자체손상','과열/잘못된 오일'],confirm=['브리더 복구 후 누유/압력징후가 사라지면 확정한다.'],tools=['저압 에어/세척도구(분리상태에서)'],loc='드라이브액슬 상부 브리더')
    return dict(nodes=[node('input','AXLE INPUT','source'),node('focus',short(c,18),'component',True),node('hub','L/R HUB','compare')],edges=[('input','focus'),('focus','hub')],mps=['COMPARE'],measure=[mp('COMPARE','좌/우 허브','소음/온도/유격 비교','한쪽/공통 원인 분리')],seq=['좌우를 동일조건에서 비교한다.','윤활과 브레이크 원인을 분리한다.'],ro=['브레이크 끌림','베어링/기어손상'],confirm=['해당 조치 전후로 증상이 반복 변화하면 확정한다.'],tools=['온도계'],loc='드라이브액슬 해당부')

def get_profile(item):
    c=item['cause']; sys=item['system']
    if sys=='트랜스미션': return tm_profile(c)
    if sys=='드라이브 액슬': return axle_profile(c)
    if sys=='유압': return hydro_profile(c)
    if sys=='작업장치': return work_profile(c)
    if sys=='스티어링': return steer_profile(c)
    if sys=='브레이크': return brake_profile(c,item['symptom_id'])
    return None

changed=[]
for item in root['items']:
    if item['id'] not in partial_ids: continue
    p=get_profile(item)
    if not p: continue
    cause=item['cause']; sys=item['system']
    item['diagram']=diag(f"{sys} · {cause} · 현장 격리도",p['nodes'],p['edges'],p['mps'],"이 원인을 확정/배제하는 데 필요한 경로만 표시. 원본 도면의 위치/수치가 확인되지 않은 항목은 정상측 비교와 격리시험으로 처리한다.")
    # merge measurement points, preferring profile IDs
    old=[x for x in item.get('measurement_points',[]) if x.get('id') not in {m['id'] for m in p['measure']}]
    item['measurement_points']=p['measure']+old[:3]
    item['field_sequence']=uniq(item.get('field_sequence',[])+p['seq'])
    item['rule_out']=uniq(p['ro']+item.get('rule_out',[]))
    item['confirm_if']=uniq(p['confirm']+item.get('confirm_if',[]))
    item['tools']=uniq(item.get('tools',[])+p['tools'])
    item['component_locator']={'summary':p['loc'],'oem_pages':item.get('oem_source',{}).get('pdf_pages',[]),'mode':'technician_location_hint'}
    item['quick_view']={
        'title':'현장에서 먼저 할 3가지',
        'steps':item['field_sequence'][:3],
        'do_not':['정상 상태의 정적 도통/육안만으로 정상 판정하지 않는다.','원인 구간이 특정되기 전에 예방교환/분해하지 않는다.']
    }
    item['level']='A_FIELD_EXPERT_V7'
    changed.append(item['id'])

root['version']='2.7-field-expert-all-causes'
root['definition']='64개 증상/268개 원인 전체를 정비사용 고장전용 재작성도+측정점+격리/비교+확정/분해조건으로 제공. V7은 기존 partial 146개를 원인별 전용화.'
root['counts']['v7_upgraded_from_partial']=len(changed)
expert_path.write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'V7_UPGRADED_CAUSES.json').write_text(json.dumps({'count':len(changed),'ids':changed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('upgraded',len(changed))
