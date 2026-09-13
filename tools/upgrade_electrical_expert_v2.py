#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/electrical_diag_v1.json'

def node(i,label,kind='component',verified=True,note=''):
    x={'id':i,'label':label,'kind':kind,'verified':verified}
    if note:x['note']=note
    return x

def diag(title,nodes,edges,measure=None,note=''):
    return {'title':title,'nodes':nodes,'edges':[{'from':a,'to':b} for a,b in edges],'measure_points':measure or [],'note':note or '고장 판별에 필요한 기능 경로만 재작성. 숫자 핀/퓨즈 cavity는 OEM에서 확인된 경우에만 확정 표시.'}

def result(title,result,test,rule,confirm,gate,tools=None,limit=None):
    x={'type':'result','title':title,'result':result,'field_tools':tools or ['디지털 멀티미터','백프로브'],'field_test':test,'rule_out':rule,'confirm_if':confirm,'disassembly_gate':gate}
    if limit:x['oem_limit_note']=limit
    return x

def q(title,question,method,choices,tools=None):
    x={'type':'question','title':title,'question':question,'field_method':method,'choices':choices}
    if tools:x['tools']=tools
    return x

def ensure_catalog(d,item):
    ids={x['id'] for x in d['catalog']}
    if item['id'] not in ids:d['catalog'].append(item)

def main():
    d=json.loads(P.read_text(encoding='utf-8'))
    c=d.setdefault('circuits',{})
    # Primary re-authored diagrams for existing circuits.
    sims={
    'STOP_LAMP':diag('브레이크등 · 필요한 회로만',[
        node('bat','12V/B+','source'),node('fuse','STOP 전원 퓨즈\nOEM cavity 확인 필요','protection',False),node('sw','STOP LAMP SW\n2-pin','switch'),node('branch','후방 분기','junction'),node('rh','COMB RH\nSTOP','load'),node('lh','COMB LH\nSTOP','load'),node('gnd','GND','ground')],
        [('bat','fuse'),('fuse','sw'),('sw','branch'),('branch','rh'),('branch','lh'),('rh','gnd'),('lh','gnd')],['SW 입력','SW 출력','RH STOP','LH STOP','GND 전압강하']),
    'HEAD_LAMP':diag('헤드램프 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','LAMP 계열 퓨즈','protection'),node('sw','LIGHT SW','switch'),node('branch','LH/RH 분기','junction'),node('rh','HEAD RH','load'),node('lh','HEAD LH','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','sw'),('sw','branch'),('branch','rh'),('branch','lh'),('rh','gnd'),('lh','gnd')],['퓨즈 양단','LIGHT SW 출력','램프 B+','램프 GND']),
    'TURN_HAZARD':diag('방향지시/비상등 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','TURN/HAZARD 퓨즈','protection'),node('flash','FLASHER/HAZARD RELAY','control'),node('sw','TURN/HAZARD SW','switch'),node('branch','LH/RH 분기','junction'),node('lamps','TURN LAMPS','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','flash'),('flash','sw'),('sw','branch'),('branch','lamps'),('lamps','gnd')],['퓨즈 양단','플래셔 입력/출력','스위치 출력','램프 B+/GND']),
    'HORN':diag('경적 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','HORN 10A','protection'),node('sw','HORN SW','switch'),node('horn','HORN','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','sw'),('sw','horn'),('horn','gnd')],['퓨즈 양단','HORN 입력','GND 전압강하']),
    'BACKUP':diag('후진등/부저 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','BACK-UP 전원\nOEM cavity 확인 필요','protection',False),node('sw','BACK-UP SW','switch'),node('branch','등/부저 분기','junction'),node('lamp','COMB BACK-UP','load'),node('buzz','BACK-UP BUZZER','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','sw'),('sw','branch'),('branch','lamp'),('branch','buzz'),('lamp','gnd'),('buzz','gnd')],['SW 입력/출력','등 B+','부저 B+','GND']),
    'START':diag('시동 · 필요한 회로만',[node('bat','12V BATTERY','source'),node('cb','CIRCUIT BREAKER','protection'),node('key','KEY SW START','switch'),node('interlock','START 인터록/제어','control'),node('relay','RELAY-START','control'),node('starter','STARTER S/B+','load'),node('gnd','ENGINE/BAT- GND','ground')],[('bat','cb'),('cb','key'),('key','interlock'),('interlock','relay'),('relay','starter'),('starter','gnd')],['배터리 부하전압','KEY START 출력','릴레이 코일/접점','스타터 S','B+ 전압강하','GND 전압강하']),
    'CHARGE':diag('충전 · 필요한 회로만',[node('alt','ALTERNATOR','source'),node('bplus','ALT B+','measure'),node('bat','12V BATTERY','load'),node('exc','충전 지령/경고 회로','control'),node('gnd','ENGINE/BAT- GND','ground')],[('alt','bplus'),('bplus','bat'),('exc','alt'),('alt','gnd')],['ALT B+','배터리 +','알터네이터 케이스 GND']),
    'PARK_INPUT':diag('주차브레이크 입력 · 필요한 회로만',[node('sw','PARKING BRAKE SW','switch'),node('input','OSS/제어 입력','control'),node('logic','주행 인터록 로직','control'),node('out','F/R 허용/차단','load')],[('sw','input'),('input','logic'),('logic','out')],['SW 양단','컨트롤러 입력']),
    'LIFT_LOCK':diag('리프트락 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','LOCK 전원\nOEM cavity 확인 필요','protection',False),node('oss','OSS/제어 출력','control'),node('sol','LIFT LOCK SOL\n12V NC','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','oss'),('oss','sol'),('sol','gnd')],['OSS 출력','솔레노이드 B+','솔레노이드 GND']),
    'GAUGE':diag('계기/센서 · 필요한 회로만',[node('supply','CLUSTER 전원/5V','source'),node('sensor','연료/수온/TM온도 센서','sensor'),node('signal','신호선','measure'),node('cluster','INSTRUMENT CLUSTER','load'),node('gnd','센서/클러스터 GND','ground')],[('supply','sensor'),('sensor','signal'),('signal','cluster'),('sensor','gnd'),('cluster','gnd')],['센서 공급','신호','센서 GND','클러스터 전원/GND']),
    'WORK_REAR':diag('후방 작업등/스트로브 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','LAMP 전원','protection'),node('sw','작업등 명령/스위치','switch'),node('branch','후방 하네스','junction'),node('load','REAR/STROBE/LAMP','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','sw'),('sw','branch'),('branch','load'),('load','gnd')],['퓨즈 양단','부하 B+','부하 GND']),
    'FR_CONTROL':diag('전후진 제어 · 필요한 회로만',[node('fuse','FWD/REV fuse #3','protection'),node('sw','F/R SW\n4↔7 common\n1↔2 F / 1↔3 R','switch'),node('coil','F/R SOLENOID\n10±0.3Ω @25℃','load'),node('plunger','PLUNGER\n약 3.18mm','measure'),node('valve','SELECTOR SPOOL','control')],[('fuse','sw'),('sw','coil'),('coil','plunger'),('plunger','valve')],['스위치 접점','코일 전압/저항','플런저 실제 이동']),
    'OSS_SEAT_INTERLOCK':diag('OSS 시트락 · 센서/5V/CAN/출력만',[node('bat','BAT+/IGN','source'),node('gnd','OSS GND','ground'),node('seat','SEAT SW','sensor'),node('five','5V 기준/풀업','measure'),node('can','CAN H/L + 진단응답','measure'),node('oss','OSS CONTROLLER','control'),node('out','LIFT/F-R LOCK 출력','load')],[('bat','oss'),('gnd','oss'),('seat','oss'),('five','oss'),('can','oss'),('oss','out')],['BAT+/IGN 부하전압','GND 전압강하','SEAT 입력','5V 기준','CAN H/L','진단기 OSS 응답'], '흔들림 반응은 원인 확정이 아니라 재현 트리거. 5V·CAN·전원/GND를 함께 보아 OSS 자체와 하네스를 분리한다.')
    }
    for k,v in sims.items():
        if k in c:c[k]['simplified_diagram']=v

    # A/C electrical circuits: exact fuse/relay/pin identity is not claimed without OEM high-res proof.
    c['AC_POWER']={
      'schematic_id':'HVAC chapter 8-5 + vehicle electrical supply', 'sheet':'HVAC 8-5 / power path OEM VERIFY','oem_pages':[345,346,348,349], 'grid':'HVAC unit / controller',
      'components':[{'name':'A/C CONTROLLER/DISPLAY','grid':'HVAC controller','note':'팬속도 제어는 A/C 디스플레이에서 수행됨'}, {'name':'EVAP BLOWER MOTOR','connector':'4-pin','known':'12V, 10A, 3-stage, direct stage-3 motor test'}, {'name':'THERMOSTAT','connector':'2-pin'}],
      'known_standard':'증발기 블로워 모터 12V, 10A, 3단, 전원 4핀/서모스탯 2핀. 정확한 A/C 전용 fuse cavity와 controller 숫자 pin은 현재 자료에서 미확정.',
      'unverified':['A/C 전용 fuse cavity/정격','A/C controller B+/IGN/GND 숫자 핀','블로워 4핀의 개별 핀 기능'],
      'simplified_diagram':diag('A/C 전원 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','A/C 전원 퓨즈\nOEM VERIFY','protection',False),node('ign','IGN/KEY','switch'),node('ctrl','A/C CONTROLLER','control'),node('blower','BLOWER 4-pin\n12V 10A','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','ign'),('ign','ctrl'),('ctrl','blower'),('blower','gnd')],['퓨즈 양단','컨트롤러 B+/IGN/GND','블로워 4핀 전원/GND'])
    }
    c['AC_COND_FAN']={
      'schematic_id':'HVAC chapter 8-5 + A/C fan functional path', 'sheet':'HVAC 8-5 / exact relay wiring OEM VERIFY','oem_pages':[345,346,349,350], 'grid':'Condenser/fan motor assembly',
      'components':[{'name':'CONDENSER FAN MOTOR','known':'fan motor assembly airflow 1,200 m3/h; 12V vehicle system'}, {'name':'A/C CONTROL / FAN RELAY PATH','note':'exact relay/fuse/pin identity requires higher-resolution OEM electrical source'}],
      'known_standard':'컨덴서 팬 모터 어셈블리 풍량 1,200 m3/h. 차량 12V 계통. 팬 전용 퓨즈/릴레이 숫자ID는 현재 OEM 자료에서 미확정.',
      'unverified':['condenser fan fuse cavity/rating','condenser fan relay exact identifier','fan connector numeric pin roles'],
      'simplified_diagram':diag('컨덴서 팬 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','FAN FUSE\nOEM VERIFY','protection',False),node('relay','FAN RELAY/DRIVER\nOEM VERIFY','control',False),node('fan','CONDENSER FAN','load'),node('gnd','GND','ground'),node('ac','A/C ON / COMP CLUTCH','control')],[('bat','fuse'),('fuse','relay'),('ac','relay'),('relay','fan'),('fan','gnd')],['팬 커넥터 B+','팬 GND 전압강하','릴레이 출력','릴레이 명령'])
    }

    # Additional coverage from actual sheets.
    c['PREHEAT']={'schematic_id':'600123-00120','sheet':'3/4~4/4','oem_pages':[369,370],'grid':'E5~G5','components':[{'name':'RELAY-PREHEAT','grid':'3/4 E5'},{'name':'GLOW PLUGS','grid':'4/4 G5'}],'unverified':['preheat relay numeric terminals/fuse cavity'], 'simplified_diagram':diag('예열 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','PREHEAT 전원','protection'),node('ctrl','ECU/예열 명령','control'),node('relay','RELAY-PREHEAT','control'),node('glow','GLOW PLUGS','load'),node('gnd','ENGINE GND','ground')],[('bat','fuse'),('fuse','relay'),('ctrl','relay'),('relay','glow'),('glow','gnd')],['릴레이 B+','릴레이 출력','글로우 플러그 B+','GND'])}
    c['FUEL_HEATER']={'schematic_id':'600123-00120','sheet':'3/4~4/4','oem_pages':[369,370],'grid':'E5~F5','components':[{'name':'RELAY-FUEL HEATER','grid':'3/4 E5'},{'name':'FUEL HEATER','grid':'4/4 E5'}],'unverified':['fuel-heater exact fuse cavity/pin numbers'], 'simplified_diagram':diag('연료히터 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','FUEL HEATER 전원','protection'),node('ctrl','제어 명령','control'),node('relay','RELAY-FUEL HEATER','control'),node('heater','FUEL HEATER','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','relay'),('ctrl','relay'),('relay','heater'),('heater','gnd')],['릴레이 입력/출력','히터 B+','히터 GND'])}
    c['BRAKE_OIL_WARN']={'schematic_id':'600123-00120','sheet':'1/4','oem_pages':[367],'grid':'A3~A4','components':[{'name':'BRAKE OIL LVL SW','grid':'1/4 A3'},{'name':'INSTRUMENT/MONITOR','grid':'1/4 A4'}],'unverified':['numeric connector pin roles'], 'simplified_diagram':diag('브레이크오일 경고 · 필요한 회로만',[node('sw','BRAKE OIL LVL SW','sensor'),node('sig','SIGNAL','measure'),node('cluster','MONITOR/CLUSTER','load'),node('gnd','GND','ground')],[('sw','sig'),('sig','cluster'),('sw','gnd')],['스위치 전환','신호선','클러스터 입력'])}
    c['CLUSTER_POWER']={'schematic_id':'600123-00120','sheet':'1/4,3/4','oem_pages':[367,369],'grid':'A4~A5 / Fuse box E6','components':[{'name':'INSTRUMENT CLUSTER/MONITOR','grid':'1/4 A4~A5'},{'name':'FUSE BOX','grid':'3/4 E6'}],'fuse_reference':'15A 계기판(정비표)','unverified':['cluster connector numeric B+/IGN/GND pins'], 'simplified_diagram':diag('계기판 전원 · 필요한 회로만',[node('bat','12V/B+','source'),node('fuse','CLUSTER 15A 계열','protection'),node('ign','IGN','switch'),node('cluster','CLUSTER/MONITOR','load'),node('gnd','GND','ground')],[('bat','fuse'),('fuse','ign'),('ign','cluster'),('cluster','gnd')],['퓨즈 양단','클러스터 B+/IGN','클러스터 GND'])}
    c['CAN_NETWORK']={'schematic_id':'600123-00120','sheet':'2/4,4/4','oem_pages':[368,370],'grid':'ECU/CAN connector','components':[{'name':'ECU DCM 3.7','grid':'2/4 H1~I5'},{'name':'CAN CONNECTOR','grid':'4/4 G5~G6'}],'unverified':['D20/25/30/33S(SE)-7 network termination locations/nominal resistance unless OEM source confirms'], 'simplified_diagram':diag('CAN 통신 · 필요한 경로만',[node('diag','DIAG TOOL/CONNECTOR','source'),node('canh','CAN-H','measure'),node('canl','CAN-L','measure'),node('nodes','ECU/OSS 등 NODE','control'),node('power','NODE B+/IGN/GND','source')],[('diag','canh'),('diag','canl'),('canh','nodes'),('canl','nodes'),('power','nodes')],['진단기 응답','CAN-H/L','노드 B+/IGN/GND'],'CAN 저항 60Ω 같은 일반값은 네트워크 구성/종단 위치가 이 모델에서 OEM 확인된 뒤에만 확정 기준으로 사용한다.')}

    # Add/replace executable graphs.
    G=d.setdefault('graphs',{})
    G['E_AC_POWER_NO']={'title':'에어컨 전원 자체가 켜지지 않음 · 전원/컨트롤러/블로워 분리진단','circuit':'AC_POWER','start':'scope','nodes':{
      'scope':q('1. 죽은 범위 분리','어느 상태입니까?',['A/C 디스플레이, 블로워, 컴프레서 반응을 각각 확인한다.','냉매압 진단으로 바로 가지 않는다.'],[{'label':'디스플레이 자체가 완전히 꺼짐','next':'controller_power'},{'label':'디스플레이는 켜지나 블로워가 안 돎','next':'blower_feed'},{'label':'디스플레이/블로워는 켜지나 A/C 작동만 안 됨','next':'ac_output'}]),
      'controller_power':q('2. 컨트롤러 B+/IGN/GND','A/C 컨트롤러까지 전원과 접지가 실제 부하상태에서 정상입니까?',['정확한 숫자 핀은 OEM 고해상도 자료에서 확인 전 임의 지정하지 않는다.','컨트롤러 커넥터 기능선 B+/IGN/GND를 백프로브한다.','GND는 단순 도통보다 작동상태 전압강하를 우선한다.'],[{'label':'B+/IGN 또는 GND 이상','next':'power_path'},{'label':'B+/IGN/GND 모두 정상','next':'controller_dead'}],['DMM','백프로브']),
      'power_path':result('A/C 전원/접지 상류 이상','컨트롤러 자체보다 퓨즈·IGN 전원·GND 경로 문제입니다.',['A/C 전원 퓨즈 입력/출력을 부하상태에서 비교한다.','퓨즈 양단 정상인데 컨트롤러에서 전원이 사라지면 중간 커넥터/하네스를 전단→후단으로 추적한다.','GND 전압강하가 비정상이면 접지점/터미널을 수리 후 재시험한다.'],['A/C 컨트롤러 내부고장','냉매량','컴프레서 기계고장'],['전압이 마지막으로 정상인 지점과 처음 사라지는 지점을 반복 재현'], '상류 불량구간을 특정한 뒤 해당 퓨즈/하네스/접지만 수리한다.',limit='A/C 전용 fuse cavity/정격과 controller 숫자 pin은 현재 자료에서 미확정.'),
      'controller_dead':result('A/C 컨트롤러/디스플레이 자체 고장 가능성 높음','B+/IGN/GND가 정상인데 컨트롤러가 완전 무반응입니다.',['커넥터를 흔들며 B+/IGN/GND가 순간적으로 변하는지 MIN/MAX로 확인한다.','외부 회로가 안정적인데 화면/출력이 전혀 없으면 컨트롤러 내부 전원회로를 의심한다.'],['퓨즈/IGN/GND','외부 하네스'],['컨트롤러 전원/접지 안정 + 외부 접촉불량 배제 + 컨트롤러 무응답 반복'], '전원/GND를 부하상태에서 확인한 뒤 컨트롤러 교환/내부수리 판단.'),
      'blower_feed':q('3. 블로워 4핀 전원','팬 명령을 바꿀 때 증발기 블로워 4핀 커넥터에서 전원/출력이 변합니까?',['매뉴얼 확인값: 블로워 12V, 10A, 3단, 전원커넥터 4핀.','숫자 핀 역할은 미확정이므로 실제 기능선을 확인해 측정한다.','모터 테스트는 매뉴얼의 단계 3 직접연결 조건을 활용한다.'],[{'label':'출력 있음','next':'blower_motor'},{'label':'출력 없음','next':'blower_control'}],['DMM','퓨즈 내장 점퍼선']),
      'blower_motor':result('블로워 모터/GND 쪽','컨트롤 출력은 있으나 블로워가 돌지 않습니다.',['블로워 GND 전압강하를 확인한다.','매뉴얼 사양에 맞게 단계3 직접전원으로 모터 작동을 확인한다.'],['A/C 컨트롤러 전원','냉매회로'],['직접 12V/GND에서도 모터 미작동이면 모터 불량 확정도가 높음'], '직접전원과 GND 정상 확인 후 블로워를 탈거한다.'),
      'blower_control':result('블로워 제어 출력 경로','디스플레이는 살아 있으나 블로워 4핀으로 출력이 나오지 않습니다.',['팬속도 1~3 변경 시 컨트롤러 출력/중간 하네스의 변화를 비교한다.','컨트롤러 바로 출력은 있으나 블로워에서 없으면 하네스, 컨트롤러 출력도 없으면 컨트롤러/속도제어부를 좁힌다.'],['블로워 모터 자체','냉매회로'],['같은 팬명령에서 컨트롤러 전단/후단 비교로 전압이 사라지는 위치 특정'], '고장구간 확인 후 컨트롤러/하네스 해당부분만 수리한다.'),
      'ac_output':q('4. A/C 냉방 명령','A/C ON 시 컴프레서 전자클러치 또는 냉방 출력 명령이 생깁니까?',['매뉴얼상 A/C 작동 시 컴프레서 전자기클러치가 체결된다.','블로워는 정상인데 냉방출력이 없으면 서모스탯/압력조건/클러치 제어를 분리한다.'],[{'label':'클러치/명령 있음','next':'refrigeration'},{'label':'명령 없음','next':'control_inhibit'}]),
      'refrigeration':result('전원고장이 아님 · 냉매/방열 진단으로 이동','A/C 전원과 블로워, 냉방 명령은 살아 있습니다.',['저·고압을 OEM 조건에서 동시측정하고 냉매/팽창/컨덴서 진단으로 이동한다.'],['A/C 전원 전체','블로워 전원'],['A/C 명령과 컴프레서 체결이 확인됨'], '전기 전원회로 분해 없이 냉매회로 진단으로 이동.'),
      'control_inhibit':result('A/C 냉방 제어/인터록 경로','컨트롤러는 켜지지만 컴프레서 냉방 명령이 나오지 않습니다.',['서모스탯 2핀 입력, 온도/압력 보호조건, 클러치 출력 경로를 기능별로 확인한다.','정확한 핀번호는 OEM 원본 검증 전 임의지정하지 않는다.'],['A/C 메인 B+/IGN/GND','블로워 모터 자체'],['어느 입력/출력에서 명령이 차단되는지 백프로브로 반복 확인'], '차단 입력/출력을 특정한 뒤 해당 센서/제어부만 정비한다.',limit='압력스위치/컨트롤러 숫자핀은 현재 소스에서 미확정.')
    }}

    G['E_AC_COND_FAN_NO']={'title':'A/C는 작동하는데 컨덴서 팬이 안 돎 · 팬회로 분리진단','circuit':'AC_COND_FAN','start':'ac_state','nodes':{
      'ac_state':q('1. 냉방 사이클 상태','A/C ON에서 컴프레서 전자클러치가 실제 체결됩니까?',['블로워가 돈다는 것과 냉방 명령이 살아 있다는 것은 다르다.','컴프레서 클러치 체결 여부를 육안/청진으로 확인한다.'],[{'label':'클러치 체결됨 · 팬만 정지','next':'fan_voltage'},{'label':'클러치도 체결 안 됨','next':'ac_control'}]),
      'fan_voltage':q('2. 팬 커넥터 B+','팬이 돌아야 하는 상태에서 컨덴서 팬 커넥터에 배터리 전압이 도달합니까?',['팬 커넥터를 연결한 상태로 백프로브한다.','무부하 12V 확인만 하지 말고 실제 팬명령 상태에서 측정한다.'],[{'label':'B+ 도달','next':'fan_ground'},{'label':'B+ 없음','next':'upstream'}],['DMM','백프로브']),
      'fan_ground':q('3. 팬 GND 전압강하','팬 명령 중 모터 GND→배터리(-) 전압강하가 정상입니까?',['B+가 있어도 GND 고저항이면 모터가 돌지 않을 수 있다.','OEM 전압강하 수치가 없으므로 정상 배선/배터리 기준과 비교하고, 직접 GND 점퍼로 A/B 확인한다.'],[{'label':'GND 정상','next':'direct'},{'label':'GND 불량','next':'ground_bad'}]),
      'ground_bad':result('컨덴서 팬 접지 불량','팬 B+는 있으나 GND 경로가 부하에서 무너집니다.',['접지점/커넥터 전단후단을 부하상태 전압강하로 추적한다.','임시 저저항 GND 점퍼에서 팬이 정상회전하는지 확인한다.'],['팬 모터 코일','상류 릴레이 출력'],['GND 점퍼에서 정상회전 + 원래 GND 경로에서만 전압강하 반복'], '접지 불량지점을 특정한 뒤 단자/배선을 수리한다.'),
      'direct':q('4. 팬 직접전원','퓨즈 내장 점퍼로 팬 모터에 직접 12V/GND를 주면 정상 회전합니까?',['팬 회로에서 분리하고 극성/안전을 확인한다.','직접전원 테스트는 짧게 실시한다.'],[{'label':'직접전원에서도 안 돎/느림','next':'motor_bad'},{'label':'직접전원에서는 정상','next':'control_path'}],['퓨즈 내장 점퍼선']),
      'motor_bad':result('컨덴서 팬 모터 불량','정상 B+/GND 직접공급에도 팬이 정상회전하지 않습니다.',['팬 날개 기계구속/베어링 걸림을 함께 확인한다.','팬 모터 어셈블리 사양상 풍량 1,200 m3/h; 현장에서는 직접회전/소음/전류상태를 정상부품과 비교한다.'],['상류 퓨즈/릴레이','A/C 컨트롤 명령'],['직접 12V/GND에서도 미작동 또는 심한 저속/걸림 반복'], '직접전원 확인 후 팬 모터 어셈블리를 교환한다.'),
      'upstream':q('5. 팬 상류 출력','팬 모터까지 전압이 없을 때 팬 릴레이/드라이버 출력 측에서 전압이 있습니까?',['정확한 relay/fuse ID는 현재 D20/25/30/33S(SE)-7 자료에서 미확정이므로 기능 경로를 실제 배선으로 식별한다.','출력 측과 팬 커넥터를 동시에 비교해 하네스와 제어부를 분리한다.'],[{'label':'상류 출력 있음','next':'fan_harness'},{'label':'상류 출력도 없음','next':'command'}]),
      'fan_harness':result('팬 출력→모터 사이 하네스/커넥터 불량','상류 출력은 있으나 팬 커넥터까지 도달하지 않습니다.',['전단 정상/후단 무전압이 되는 커넥터를 구간별 백프로브한다.','핀 밀림/부식/크림프/굴곡부 부분단선을 흔들림과 부하전압으로 재현한다.'],['팬 모터','A/C 명령'],['특정 구간 전단 정상·후단 이상 반복'], '구간을 특정한 뒤 해당 하네스/커넥터만 수리한다.'),
      'command':q('6. 팬 릴레이/드라이버 명령','A/C ON/컴프레서 체결 상태에서 팬 제어명령은 들어옵니까?',['명령측이 살아 있고 출력이 없으면 릴레이/드라이버 전원/접점, 명령 자체가 없으면 A/C 제어/보호조건으로 분리한다.'],[{'label':'명령 있음','next':'relay_power'},{'label':'명령 없음','next':'ac_control'}]),
      'relay_power':result('팬 릴레이/드라이버 전원 또는 접점 불량 가능성','팬 명령은 있으나 부하출력이 형성되지 않습니다.',['릴레이/드라이버 B+ 입력과 출력 전압을 같은 순간 비교한다.','교환 가능한 동일 릴레이가 OEM상 동일사양임이 확인될 때만 A/B 대체시험한다.'],['팬 모터','하네스 후단','A/C 명령'],['명령+B+ 정상인데 출력 미형성 반복'], '입력/명령 정상 확인 후 릴레이/드라이버를 교환한다.',limit='팬 릴레이 exact ID/pin은 현재 OEM 소스에서 미확정.'),
      'ac_control':result('A/C 팬 명령 생성조건/컨트롤 문제','팬 모터보다 상위의 A/C 냉방/팬 제어조건을 먼저 봐야 합니다.',['A/C 컨트롤 전원, 컴프레서 명령, 온도/압력 보호입력을 확인한다.','컴프레서도 미체결이면 E_AC_POWER_NO 냉방명령 분기로 이동한다.'],['팬 모터 자체'],['팬 제어명령이 생성되지 않는 조건/입력이 특정됨'], '제어입력/컨트롤러 원인을 특정하기 전 팬 모터를 교환하지 않는다.'),
      'control_path':result('팬 모터 정상 · 상류 제어회로 불량','직접전원에서는 팬이 정상입니다.',['원래 커넥터로 복귀해 B+/GND와 릴레이/드라이버 출력/명령을 순서대로 추적한다.'],['팬 모터 기계고장'],['직접전원 정상 + 차량 회로에서만 미작동'], '상류 전원/제어 구간을 특정 후 수리한다.')
    }}

    # Helper generators for new sheet-defined circuits.
    def simple_power_graph(title,circuit,loadname):
      return {'title':title,'circuit':circuit,'start':'feed','nodes':{
       'feed':q('1. 부하 입력전압',f'{loadname} 작동명령 상태에서 부하 B+가 도달합니까?',['부하 커넥터를 연결한 상태로 백프로브하고 배터리전압과 비교한다.'],[{'label':'B+ 있음','next':'ground'},{'label':'B+ 없음','next':'up'}]),
       'ground':q('2. 접지/부하 분리',f'{loadname} GND가 부하상태에서 정상입니까?',['GND→배터리(-) 전압강하 또는 안전한 직접 GND A/B 시험으로 확인한다.'],[{'label':'GND 정상','next':'loadbad'},{'label':'GND 이상','next':'groundbad'}]),
       'loadbad':result(loadname+' 자체 불량 가능성',f'B+와 GND가 정상인데 {loadname}이 작동하지 않습니다.',['부하 자체 저항/기계구속/직접전원을 OEM 허용범위에서 확인한다.'],['상류 전원/접지'],['정상 전원/GND에서도 부하 미작동 반복'], '부하 자체 시험 후 교환한다.'),
       'groundbad':result(loadname+' GND 불량',f'{loadname}의 접지경로가 부하에서 무너집니다.',['접지점까지 구간별 전압강하를 추적한다.'],['부하 자체','상류 B+'],['GND 우회 시 정상작동 + 원래 GND에서만 불량'], '접지 위치 특정 후 수리한다.'),
       'up':q('3. 상류 제어/퓨즈',f'{loadname} 상류 릴레이/제어 출력에는 전압이 있습니까?',['퓨즈 입력/출력→릴레이 B+/명령/출력→하네스 순으로 추적한다.'],[{'label':'상류 출력 있음','next':'harness'},{'label':'상류 출력 없음','next':'control'}]),
       'harness':result(loadname+' 하네스/커넥터 단선 또는 고저항',f'상류 출력은 있으나 {loadname}까지 도달하지 않습니다.',['전단/후단 동시 비교와 흔들림/부하전압으로 단선·핀밀림·크림프를 특정한다.'],['부하 자체','제어명령'],['전압이 사라지는 구간 반복 특정'], '해당 구간만 수리한다.'),
       'control':result(loadname+' 릴레이/명령/전원 경로',f'{loadname} 상류 출력부터 형성되지 않습니다.',['릴레이 B+ 입력, 코일 명령, 접점 출력을 순서대로 확인한다.','정확한 pin/fuse ID는 OEM 확인값만 사용한다.'],['부하/후단 하네스'],['B+·명령·출력 중 최초 이상 지점 특정'], '최초 이상 제어부를 특정 후 수리한다.')
      }}

    G['E_PREHEAT_NO']=simple_power_graph('예열/글로우 작동 안 됨 · 회로 추적','PREHEAT','GLOW PLUGS')
    G['E_FUEL_HEATER_NO']=simple_power_graph('연료히터 작동 안 됨 · 회로 추적','FUEL_HEATER','FUEL HEATER')
    G['E_BRAKE_OIL_WARN']=simple_power_graph('브레이크오일 경고 입력 이상 · 회로 추적','BRAKE_OIL_WARN','BRAKE OIL LVL SW/경고회로')
    G['E_CLUSTER_POWER_NO']=simple_power_graph('계기판/모니터 전원 안 켜짐 · 회로 추적','CLUSTER_POWER','INSTRUMENT CLUSTER')
    G['E_CAN_NETWORK']= {'title':'진단기 통신/CAN 이상 · 노드 전원/배선/컨트롤러 분리진단','circuit':'CAN_NETWORK','start':'scope','nodes':{
       'scope':q('1. 통신범위 분리','진단기에서 어느 모듈이 통신되지 않습니까?',['모든 노드 불통인지 특정 노드만 불통인지 먼저 구분한다.'],[{'label':'여러/모든 모듈 불통','next':'global'},{'label':'특정 모듈만 불통','next':'local_power'}]),
       'global':q('2. 공통 CAN/진단 전원','진단커넥터 전원/GND와 CAN-H/L 물리회로에 공통 이상이 있습니까?',['진단기 자체/커넥터 전원부터 확인한다.','CAN 저항 수치는 이 모델 종단구성이 OEM 확인된 뒤에만 확정기준으로 사용한다.'],[{'label':'공통 이상 확인','next':'global_bad'},{'label':'공통 이상 없음','next':'local_power'}]),
       'global_bad':result('공통 진단/CAN 회로 이상','여러 모듈이 동시에 불통이므로 개별 ECU보다 공통회로를 우선합니다.',['진단커넥터 전원/GND, CAN-H/L 단락/단선, 공통 스플라이스를 구간별 확인한다.'],['개별 OSS/ECU 단독고장'],['공통 회로 수리 후 여러 노드 통신 동시복구'], '공통 통신회로를 수리한다.',limit='60Ω 등 일반 CAN 종단값은 D20/25/30/33S(SE)-7 종단구성 OEM 확인 후 확정기준으로 사용.'),
       'local_power':q('3. 불통 노드 B+/IGN/GND','불통 모듈의 B+/IGN/GND가 부하상태에서 정상입니까?',['컨트롤러 교환 전에 반드시 전원/GND를 백프로브한다.'],[{'label':'전원/GND 이상','next':'node_power'},{'label':'전원/GND 정상','next':'local_can'}]),
       'node_power':result('노드 전원/접지 문제','CAN 자체보다 모듈 전원/GND가 없어 통신하지 못하는 상태입니다.',['퓨즈/IGN/GND 경로를 부하상태 전압강하로 추적한다.'],['모듈 내부 CAN 트랜시버','공통 CAN 배선'],['전원/GND 복구 후 노드 통신 회복'], '전원/접지 수리 후 통신 재확인.'),
       'local_can':q('4. 모듈 커넥터 CAN-H/L','공통 네트워크는 살아 있는데 불통 모듈 커넥터까지 CAN-H/L 물리신호가 도달합니까?',['정상 통신 노드와 비교한다.','오실로스코프가 있으면 신호형상을 비교하고, 전원OFF 저항 측정은 OEM 네트워크 구성 확인 후 사용한다.'],[{'label':'CAN이 로컬 커넥터에서 끊김','next':'local_harness'},{'label':'CAN 도달','next':'node_internal'}],['DMM','오실로스코프(권장)','백프로브']),
       'local_harness':result('해당 노드 CAN 분기 하네스/커넥터 이상','공통 CAN은 정상이나 해당 노드 입구에서만 통신선이 끊깁니다.',['분기 전/후 CAN-H/L을 비교하고 핀밀림/크림프/굴곡부를 흔들림과 함께 확인한다.'],['모듈 내부고장','공통 CAN 문제'],['해당 분기 우회/수리 후 통신 복구'], '로컬 CAN 분기만 수리한다.'),
       'node_internal':result('해당 컨트롤러 자체 통신회로 고장 가능성 높음','전원/GND와 로컬 CAN이 정상인데 모듈만 응답하지 않습니다.',['5V 기준전압 등 컨트롤러 내부 전원 징후가 있으면 함께 확인한다.','외부 5V 센서 단락을 분리해 5V 회복 여부를 확인한다.','전원/GND/CAN/외부 5V 부하를 배제한 뒤 모듈 자체를 판단한다.'],['모듈 전원/GND','로컬 CAN 배선','외부 5V 단락'],['외부회로 정상 + 해당 모듈만 무응답 반복'], '외부회로를 모두 배제한 뒤 컨트롤러 교환/수리한다.')
    }}

    additions=[
      {'id':'E_AC_POWER_NO','group':'에어컨/전장','title':'에어컨 전원 자체가 안 켜짐','sheet':'HVAC 8-5','grid':'A/C controller / blower','ready':'field_graph'},
      {'id':'E_AC_COND_FAN_NO','group':'에어컨/전장','title':'A/C 작동 중 컨덴서 팬이 안 돎','sheet':'HVAC 8-5','grid':'Condenser fan','ready':'field_graph'},
      {'id':'E_PREHEAT_NO','group':'엔진/전장','title':'예열/글로우가 작동하지 않음','sheet':'3/4~4/4','grid':'E5~G5','ready':'field_graph'},
      {'id':'E_FUEL_HEATER_NO','group':'엔진/전장','title':'연료히터가 작동하지 않음','sheet':'3/4~4/4','grid':'E5~F5','ready':'field_graph'},
      {'id':'E_BRAKE_OIL_WARN','group':'램프/경고','title':'브레이크오일 경고등/입력 이상','sheet':'1/4','grid':'A3~A4','ready':'field_graph'},
      {'id':'E_CLUSTER_POWER_NO','group':'계기/센서','title':'계기판/모니터 전원 자체가 안 켜짐','sheet':'1/4,3/4','grid':'A4~A5 / E6','ready':'field_graph'},
      {'id':'E_CAN_NETWORK','group':'통신/컨트롤러','title':'진단기 연결/CAN 통신 이상','sheet':'2/4,4/4','grid':'ECU/CAN connector','ready':'field_graph'},
    ]
    for x in additions:ensure_catalog(d,x)
    # Point catalog items at new circuits by graph name convention already handled in graphs.
    # ensure graph circuits exist and add versions.
    d['version']='0.19-rc-expert-electrical-v2'
    d.setdefault('mapped_diagnostic_rules',{})['expert_rule']='부하 상태 전압강하, 정상측 비교, 구간분할, 컨트롤러 5V/CAN 생존성까지 확인. 흔들림 반응은 원인 확정이 아니라 재현 트리거.'
    P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('catalog',len(d['catalog']),'graphs',len(d['graphs']),'circuits',len(d['circuits']))

if __name__=='__main__':main()
