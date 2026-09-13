#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'app/src/main/assets/electrical_diag_v1.json'

def n(i,label,kind='component',verified=True,note=None):
    x={'id':i,'label':label,'kind':kind,'verified':verified}
    if note:x['note']=note
    return x

def sd(title,nodes,edges,measure,note):
    return {'title':title,'nodes':nodes,'edges':[{'from':a,'to':b} for a,b in edges],
            'measure_points':measure,'note':note}

def q(title,question,methods,choices,tools=None):
    x={'type':'question','title':title,'question':question,'field_method':methods,'choices':choices}
    if tools:x['tools']=tools
    return x

def r(title,result,tests,rule,confirm,gate,tools=None,limit=None):
    x={'type':'result','title':title,'result':result,'field_tools':tools or ['디지털 멀티미터','백프로브','OEM 회로도'],
       'field_test':tests,'rule_out':rule,'confirm_if':confirm,'disassembly_gate':gate}
    if limit:x['oem_limit_note']=limit
    return x

def addcat(d, item):
    if item['id'] not in {x['id'] for x in d['catalog']}:
        d['catalog'].append(item)

def source_circuit(title, sheet, pages, grid, components, nodes, edges, measure, note, standards=None, unverified=None, source='600123-00120'):
    x={'schematic_id':source,'sheet':sheet,'oem_pages':pages,'grid':grid,
       'components':components,'images':[f'oem_pages/p{p}.jpg' for p in pages if isinstance(p,int)],
       'simplified_diagram':sd(title,nodes,edges,measure,note)}
    if standards:x['known_standard']=standards
    if unverified:x['unverified']=unverified
    return x

def simple_load_graph(title,circuit,load,upstream='상류 전원/제어'):
    return {'title':title,'circuit':circuit,'start':'scope','nodes':{
      'scope':q('1. 증상 범위','이 부하만 이상입니까, 같은 전원계통의 다른 기능도 같이 이상입니까?',[
          '한 기능만 불량이면 부하/로컬 배선, 여러 기능 동시불량이면 공통 전원·퓨즈·접지부터 본다.',
          '간헐이면 고장 상태를 유지한 채 측정한다. 정상 상태에서만 도통을 찍고 끝내지 않는다.'
      ],[{'label':'이 기능만 이상','next':'feed'},{'label':'여러 기능 함께 이상','next':'upstream'}]),
      'feed':q('2. 부하 B+ 확인',f'{load} 커넥터에 작동 명령 중 B+가 도달합니까?',[
          '커넥터를 연결한 상태에서 백프로브한다.',
          '배터리 실전압과 동시에 비교한다.'
      ],[{'label':'B+ 있음','next':'ground'},{'label':'B+ 없음','next':'upstream'}]),
      'ground':q('3. 부하 GND/직접시험',f'{load} 접지 전압강하가 정상이고 직접전원 시험에서도 작동하지 않습니까?',[
          '부하 상태에서 GND→배터리(-) 전압강하를 본다.',
          '안전한 경우 퓨즈 내장 점퍼로 B+/GND A/B 시험한다.'
      ],[{'label':'GND 불량','next':'ground_bad'},{'label':'B+/GND 정상인데 미작동','next':'load_bad'},{'label':'직접시험 정상','next':'upstream'}]),
      'upstream':q('4. 상류 전원/제어 분리',f'{upstream} 출력에는 전압/명령이 있고 {load}에서만 사라집니까?',[
          '퓨즈 입력/출력→릴레이/스위치 입력/출력→중간 커넥터→부하 순으로 마지막 정상/첫 이상 지점을 찾는다.',
          '정확한 퓨즈 cavity·핀은 OEM 확인값만 사용한다.'
      ],[{'label':'상류 출력 정상·후단에서 소실','next':'harness_bad'},{'label':'상류 출력부터 없음','next':'control_bad'}]),
      'ground_bad':r('접지 경로 불량',f'{load} 전원은 있으나 접지경로가 부하에서 무너집니다.',[
          '접지점/커넥터를 구간별 전압강하로 분리한다.','임시 저저항 GND에서 정상화되는지 A/B 확인한다.'
      ],['부하 자체','상류 B+'],['GND 우회 시 정상 + 원래 GND에서만 반복 불량'],'접지 불량 지점을 특정한 뒤 수리한다.'),
      'load_bad':r(load+' 자체 불량',f'정상 B+/GND에서 {load}이 작동하지 않습니다.',[
          '기계구속/내부저항/직접전원 반응을 확인한다.'
      ],['전원','접지','상류 제어'],['정상 전원·접지에서도 미작동 반복'],'부하 자체 불량을 재현한 뒤 교환한다.'),
      'harness_bad':r('하네스/커넥터 단선·고저항',f'상류 출력은 정상이나 {load}까지 전달되지 않습니다.',[
          '중간 커넥터 전단/후단을 동시에 비교한다.','핀 장력·밀림·크림프·굴곡부를 부하전압과 흔들림으로 재현한다.'
      ],['부하 자체','상류 명령'],['전압이 사라지는 구간이 반복 특정됨'],'특정 구간만 수리한다.'),
      'control_bad':r('상류 전원/스위치/릴레이 문제',f'{load}로 보내는 상류 출력부터 형성되지 않습니다.',[
          '퓨즈 B+→제어 입력→제어 출력 순으로 추적한다.','입력은 정상인데 출력이 없을 때에만 제어부를 불량으로 좁힌다.'
      ],['부하','후단 하네스'],['상류 최초 이상 지점이 반복 특정됨'],'최초 이상 제어부를 특정한 뒤 수리한다.')
    }}

def sender_graph(title,circuit,sensor,display,pin_note,signal_method='센서 신호를 실온/열간 또는 실제 상태 변화와 비교한다.'):
    return {'title':title,'circuit':circuit,'start':'scope','nodes':{
      'scope':q('1. 단일계기 vs 공통계기','다른 계기/모니터 기능은 정상입니까?',[
          '다른 계기도 함께 죽으면 센서보다 클러스터 전원/GND 공통부를 먼저 본다.',
          '이 계기만 이상이면 센서 신호회로로 바로 좁힌다.'
      ],[{'label':'다른 계기는 정상','next':'sensor_live'},{'label':'여러 계기 함께 이상','next':'cluster_power'}]),
      'cluster_power':q('2. 클러스터 전원/GND','클러스터 B+/IGN/GND가 부하상태에서 정상입니까?',[
          '퓨즈/클러스터 전원은 무부하 전압보다 부하상태 전압강하로 본다.'
      ],[{'label':'정상','next':'sensor_live'},{'label':'이상','next':'cluster_bad'}]),
      'sensor_live':q('3. 센서 입력 실제값 vs 전기신호',f'{sensor} 실제 상태 변화와 {display} 표시/진단값이 같이 따라갑니까?',[
          pin_note, signal_method,
          '숫자 저항/전압 곡선이 OEM에 없는 경우 임의 정상범위를 만들지 않고 정상차·실제 상태변화와 상관관계로 판정한다.'
      ],[{'label':'신호/표시가 상태변화를 정상 추종','next':'intermittent'},{'label':'신호가 고정/비현실/끊김','next':'circuit_split'}]),
      'circuit_split':q('4. 센서 vs 하네스 vs 표시부 분리',f'{sensor} 커넥터와 컨트롤러/클러스터 입력단을 동시에 비교했을 때 어디서 신호가 달라집니까?',[
          '센서 핀→하네스 반대쪽 입력을 같은 조건에서 비교한다.',
          '커넥터 연결 상태 백프로브를 우선하고 필요하면 센서 대체/시뮬레이션은 OEM 방식으로 한다.'
      ],[{'label':'센서 출력부터 이상','next':'sensor_bad'},{'label':'센서 정상·입력단에서 이상','next':'harness_bad'},{'label':'입력까지 정상·표시만 이상','next':'display_bad'}]),
      'sensor_bad':r(sensor+' 자체 이상',f'{sensor} 출력이 실제 상태 변화와 맞지 않습니다.',[
          '센서 전원/접지(해당 시)를 먼저 확인한다.','센서 자체를 정상부품/실제 물리값과 비교한다.'
      ],['공통 클러스터 전원','하네스 이후'],['센서 바로 출력이 비현실적이며 대체센서/정상상태에서 회복'],'센서 전원·접지 확인 후 센서를 교환한다.'),
      'harness_bad':r(sensor+' 신호 하네스/커넥터 이상','센서측 신호는 정상이나 수신측에서 변형/단절됩니다.',[
          '전단/후단 비교, 핀장력, 크림프, 흔들림, 단락을 확인한다.'
      ],['센서 자체','표시부 자체'],['특정 구간 전단 정상·후단 이상 반복'],'하네스 구간을 특정한 뒤 수리한다.'),
      'display_bad':r(display+' 입력처리/표시부 이상','입력단까지 정상 신호가 도달하지만 표시가 맞지 않습니다.',[
          '진단기 raw value와 패널 표시가 분리 가능한 경우 함께 비교한다.','공통 전원/GND/CAN이 정상인지 확인한다.'
      ],['센서','신호 하네스'],['정상 입력이 확인되는데 표시/처리만 비정상 반복'],'입력/전원/통신 정상 확인 후 표시부/컨트롤러를 판단한다.'),
      'cluster_bad':r('클러스터 공통 전원/GND 문제','여러 계기 동시이상과 공통 전원/GND 이상이 일치합니다.',[
          '퓨즈/IGN/GND를 구간별 부하전압으로 추적한다.'
      ],['개별 센서 여러 개 동시고장'],['공통 전원/GND 복구 후 여러 표시 동시 정상화'],'공통 전원/접지 지점을 특정 후 수리한다.'),
      'intermittent':r('현재 정상 · 간헐조건 재현 필요','현재 센서/표시 상관관계는 정상입니다.',[
          '열간/냉간, 진동, 하네스 움직임, 실제 작업부하에서 MIN/MAX 또는 진단로그로 재현한다.'
      ],['고정 고장'],['실제 민원조건에서도 안정 정상'],'재현 전 예방교환하지 않는다.')
    }}

def three_wire_5v_graph(title,circuit,sensor,pins,signal_desc):
    s5,sg,ss=pins['5v'],pins['gnd'],pins['signal']
    return {'title':title,'circuit':circuit,'start':'scan','nodes':{
      'scan':q('1. 진단값/고장범위','이 센서 하나만 이상합니까, 같은 5V 계통의 여러 센서가 동시에 이상합니까?',[
          '여러 센서가 동시에 비현실값이면 개별 센서 교환보다 공통 5V 기준전압을 먼저 본다.',
          '진단기 live data와 실제 기계상태를 함께 기록한다.'
      ],[{'label':'이 센서만 이상','next':'ref'},{'label':'여러 5V 센서 함께 이상','next':'shared5v'}]),
      'ref':q('2. 센서 5V/GND 확인',f'{sensor} {s5}에 5V 공급이 있고 {sg} GND가 안정적입니까?',[
          f'OEM D24NAP 핀: {s5}; {sg}; {ss}.',
          '5V는 커넥터 연결 상태 백프로브로 보고, GND는 ECU 센서리턴 기준과 배터리(-) 양쪽을 비교한다.'
      ],[{'label':'5V/GND 정상','next':'signal'},{'label':'5V 없음/낮음','next':'shared5v'},{'label':'GND 이상','next':'ground_bad'}]),
      'signal':q('3. 신호선 반응',f'{ss} {signal_desc}가 실제 상태 변화에 따라 연속적으로 변하고 진단값과 일치합니까?',[
          'OEM 전압-물리량 곡선이 확보되지 않은 경우 임의 V 기준은 사용하지 않는다.',
          '센서 바로 핀과 ECU 입력측을 동시에/순차 비교한다.'
      ],[{'label':'센서 핀부터 신호 이상','next':'sensor_bad'},{'label':'센서 신호 정상·ECU 입력에서 이상','next':'harness_bad'},{'label':'ECU 입력까지 정상·진단값 이상','next':'ecu_input'}]),
      'shared5v':q('4. 공통 5V 부하 격리','같은 5V 레퍼런스 계통 센서를 하나씩 분리할 때 5V가 회복됩니까?',[
          'RPS/BPS/OPTS/EGR 등 D24의 5V branch를 회로자료에 따라 순차 분리한다.',
          '센서를 뽑을 때마다 5V 회복과 진단통신/다른 센서값 회복을 같이 본다.',
          '모든 외부부하를 분리해도 5V가 회복되지 않으면 ECU 5V 내부회로/전원·접지 쪽으로 넘어간다.'
      ],[{'label':'특정 센서/분기 분리 시 5V 회복','next':'external_short'},{'label':'외부부하 분리해도 회복 안 됨','next':'ecu5v'}]),
      'external_short':r('외부 5V 센서/배선 단락',f'{sensor} 자체 또는 같은 VREF 분기 외부부하가 5V를 끌어내립니다.',[
          '회복을 유발한 센서 커넥터에서 5V-신호-GND 단락/수분/배선눌림을 확인한다.'
      ],['ECU 내부 5V 레귤레이터'],['특정 외부부하 분리 시 5V와 다른 센서/통신이 반복 회복'],'해당 외부센서/분기만 수리한다.'),
      'ground_bad':r('센서 리턴/GND 회로 이상',f'{sensor} 공급은 있으나 {sg} 센서리턴이 불안정합니다.',[
          '센서 GND와 ECU 리턴 핀 사이를 부하상태로 비교하고 커넥터 접촉을 확인한다.'
      ],['5V 공급회로','센서 신호소자'],['GND 우회/수리 시 신호 정상화'],'센서리턴 고장구간을 특정한 뒤 수리한다.'),
      'sensor_bad':r(sensor+' 자체 신호 불량',f'5V/GND는 정상이나 {sensor} 자체 출력이 실제 상태와 맞지 않습니다.',[
          '센서 측 신호를 직접 측정하고 정상부품/실제 물리값과 비교한다.'
      ],['5V 공급','GND','ECU 입력 하네스'],['센서 교체/정상 센서 연결 시 신호 및 진단값 정상화'],'전원/GND 확인 후 센서를 교환한다.'),
      'harness_bad':r(sensor+' 신호선/커넥터 불량','센서측은 정상이나 ECU 입력까지 신호가 전달되지 않습니다.',[
          '센서 신호핀→ECU 입력핀 전단/후단 비교, 핀장력, 크림프, 단락/개방을 동적시험한다.'
      ],['센서 자체','ECU 내부 입력처리'],['특정 구간 전단 정상·후단 이상 반복'],'신호선 구간을 특정한 뒤 수리한다.'),
      'ecu_input':r('ECU 입력처리 이상 가능성 높음','센서와 ECU 커넥터 입력까지 정상인데 진단값이 비정상입니다.',[
          'ECU B+/IGN/GND 및 CAN 통신을 함께 확인한다.','다른 정상 입력과 비교하고 ECU 커넥터 핀장력을 확인한다.'
      ],['센서','신호하네스','5V/GND'],['외부 입력회로 정상 + ECU 해석만 비정상 반복'],'외부회로를 모두 배제한 뒤 ECU를 판단한다.'),
      'ecu5v':r('ECU 5V 기준회로/ECU 전원계통 이상 가능성 높음','외부 5V 부하를 분리해도 5V가 회복되지 않습니다.',[
          'ECU B+/IGN/GND 부하전압을 먼저 확인한다.','ECU 통신 여부와 다른 VREF 출력도 함께 확인한다.'
      ],['외부 5V 센서단락','로컬 5V 배선단락'],['외부부하 배제 + ECU 전원/GND 정상 + 5V 미출력 반복'],'이 조건을 모두 만족한 뒤 ECU 수리/교환을 판단한다.')
    }}

def two_wire_temp_graph(title,circuit,sensor,pins):
    return {'title':title,'circuit':circuit,'start':'live','nodes':{
      'live':q('1. 실제온도와 진단값 비교',f'{sensor} 진단값이 냉간/열간 실제온도 변화와 합리적으로 따라갑니까?',[
          f'OEM D24NAP 핀: {pins}.','냉간 시 주변/냉각수 실제온도와 비교하고 워밍업 중 값 변화의 연속성을 본다.'
      ],[{'label':'고정값/급변/비현실값','next':'pins'},{'label':'정상 추종','next':'intermittent'}]),
      'pins':q('2. 센서핀과 ECU입력 분리',f'{sensor} 센서측 신호/리턴과 ECU 입력측이 같은 변화로 따라갑니까?',[
          '커넥터 연결 상태 백프로브를 우선한다.','OEM 저항-온도표가 없는 경우 임의 Ω 기준을 만들지 않는다.'
      ],[{'label':'센서 출력부터 이상','next':'sensor_bad'},{'label':'센서 정상·ECU측에서 이상','next':'harness_bad'},{'label':'ECU 입력까지 정상·진단값만 이상','next':'ecu_bad'}]),
      'sensor_bad':r(sensor+' 자체 이상','센서 바로 출력이 실제 온도와 일치하지 않습니다.',['실제온도와 정상센서/냉간 기준을 비교한다.'],['하네스','ECU 입력'],['센서대체 시 진단값 정상화'],'센서회로 확인 후 교환한다.'),
      'harness_bad':r(sensor+' 하네스/커넥터 이상','센서측 변화가 ECU까지 전달되지 않습니다.',['핀장력·크림프·단선/단락·흔들림을 전단후단 비교한다.'],['센서','ECU 내부'],['전단 정상·후단 이상 특정'],'해당 구간만 수리한다.'),
      'ecu_bad':r('ECU 입력처리 이상 가능성','ECU 핀까지 신호는 정상인데 진단값만 잘못됩니다.',['ECU 전원/GND/CAN과 해당 핀 접촉을 확인한다.'],['센서','하네스'],['외부회로 정상 + ECU 해석만 비정상'],'외부회로 배제 후 ECU를 판단한다.'),
      'intermittent':r('현재 온도입력 정상','현재는 실제온도와 진단값이 정상 추종합니다.',['열간·진동·커넥터 흔들림에서 로그를 남긴다.'],['고정 고장'],['민원조건에서도 정상 유지'],'재현 전 교환하지 않는다.')
    }}

def main():
    d=json.loads(P.read_text(encoding='utf-8'))
    C=d.setdefault('circuits',{}); G=d.setdefault('graphs',{})
    d.setdefault('external_oem_sources',{})['D24NAP_950106_01198']={
      'title':'Doosan D24NAP Operation & Maintenance Manual 950106-01198',
      'status':'EXTERNAL_OEM_TEXT_INGESTED_FOR_ELECTRIC_SECTION',
      'sections':['12-3 Electric Parts','12-4~12-7 Circuit Diagram','12-11~12-16 Switches and Sensors','12-17 Wire harness','12-18~12-20 ECU'],
      'rule':'D24-specific pin/function labels may be used only where the OEM text explicitly resolves them.'
    }

    # Body electrical features visible in 600123-00120.
    body_specs=[
      ('E_SEATBELT_INPUT','시트벨트 스위치/경고 입력 이상','OSS/안전 인터록','4/4','H7','SEAT_BELT','SEAT BELT SW / OSS input',[370],
       [('SEAT BELT SW','4/4 H7'),('OSS CONTROLLER','1/4 C3~C4')]),
      ('E_LICENSE_NO','번호판등이 안 들어옴','램프/경고','4/4','I8','LICENSE_LAMP','LICENCE LAMP',[370],[('LICENCE LAMP','4/4 I8')]),
      ('E_HOURMETER_NO','아워미터가 작동/적산하지 않음','계기/센서','1/4,3/4','A4~A5','HOURMETER','HOURMETER',[367,369],[('HOURMETER','1/4 A4~A5 / 3/4 A4')]),
      ('E_REAR_LAMP_NO','리어램프가 안 들어옴','램프/경고','4/4','H7','REAR_LAMP','REAR LAMP',[370],[('REAR LAMP','4/4 H7')]),
      ('E_STROBE_NO','스트로브/경광등이 안 켜짐','램프/경고','4/4','H6','STROBE','STROBE',[370],[('STROBE','4/4 H6')]),
    ]
    for gid,title,group,sheet,grid,cid,load,pages,comps in body_specs:
        addcat(d,{'id':gid,'title':title,'group':group,'sheet':sheet,'grid':grid,'ready':'field_graph'})
        C[cid]=source_circuit(title+' · 필요한 경로만',sheet,pages,grid,[{'name':a,'grid':b} for a,b in comps],
            [n('source','B+/IGN','source'),n('control',load if 'SW' in load else '스위치/제어','control'),n('load',load,'load'),n('gnd','GND','ground')],
            [('source','control'),('control','load'),('load','gnd')],['B+/IGN','제어 입력/출력','부하 B+','GND 전압강하'],
            '전체 도면이 아니라 이 기능의 전원-제어-부하-접지만 재작성. 핀번호는 OEM에서 명확한 값만 사용.',unverified=['exact fuse cavity/connector numeric pin if not legible'])
        G[gid]=simple_load_graph(title+' · 현장 회로추적',cid,load)

    # Dedicated body gauge graphs (separate from the old grouped graph).
    gauge_defs=[
      ('E_WATER_GAUGE','수온 게이지만 비정상','WATER_GAUGE','WATER TEMP SENDER','WATER TEMP GAUGE','600123-00120 1/4~4/4: 수온 gauge/sender 기능선; 정확한 sender 곡선은 OEM 표 없으면 임의값 금지'),
      ('E_TM_TEMP_GAUGE','T/M 오일온도 게이지만 비정상','TM_TEMP_GAUGE','T/M OIL TEMP SENDER','T/M TEMP GAUGE','600123-00120: T/M OIL TEMP sender/gauge 기능선; 정상차/실제온도 비교'),
      ('E_FUEL_GAUGE_ONLY','연료 게이지만 비정상','FUEL_GAUGE','FUEL LEVEL SENDER','FUEL LEVEL GAUGE','600123-00120: FUEL LEVEL sender/gauge 기능선; 탱크 실제수위 변화와 비교'),
    ]
    for gid,title,cid,sensor,display,pnote in gauge_defs:
        addcat(d,{'id':gid,'title':title,'group':'계기/센서','sheet':'1/4,4/4','grid':'A4~A5 / G6','ready':'field_graph'})
        C[cid]=source_circuit(title+' · 센서/표시만','1/4,4/4',[367,370],'A4~A5 / G6',
            [{'name':sensor,'grid':'4/4 G6'},{'name':display,'grid':'1/4 A4~A5'}],
            [n('sensor',sensor,'sensor'),n('signal','SIGNAL','measure'),n('display',display,'load'),n('gnd','GND/RETURN','ground')],
            [('sensor','signal'),('signal','display'),('sensor','gnd'),('display','gnd')],['센서 신호','수신측 신호','공통 전원/GND'],pnote,unverified=['sensor transfer curve unless separately verified'])
        G[gid]=sender_graph(title+' · 센서/표시 분리진단',cid,sensor,display,pnote)

    # D24 exact sensor circuits from OEM engine manual 950106-01198.
    d24_src='D24NAP 950106-01198 §12'
    d24_common_note='D24NAP OEM §12의 센서 핀/ECU pin을 재작성. 전체 원본페이지 대신 해당 3~4선만 표시.'

    # Rail pressure: sensor pin 1 signal ECU135, pin2 GND ECU119, pin3 5V ECU138.
    C['D24_RPS']=source_circuit('D24 RPS · 3선만', 'D24 §12-12', [], 'RPS',
      [{'name':'RPS pin1 → ECU135','role':'pressure signal'},{'name':'RPS pin2 → ECU119','role':'ground'},{'name':'RPS pin3 → ECU138','role':'5V'}],
      [n('vref','ECU138 → RPS pin3\n5V','source'),n('sensor','RAIL PRESSURE SENSOR','sensor'),n('sig','RPS pin1 → ECU135\npressure signal','measure'),n('gnd','RPS pin2 → ECU119\nGND','ground')],
      [('vref','sensor'),('sensor','sig'),('sensor','gnd')],['ECU138/RPS3 5V','ECU119/RPS2 GND','RPS1/ECU135 signal'],d24_common_note,
      standards='Supply voltage explicitly 5V at RPS sensor pin3 / ECU138.',source=d24_src)
    addcat(d,{'id':'E_D24_RAIL_PRESSURE','title':'D24 레일압력 센서값 비정상/고정','group':'D24 엔진/센서','sheet':'D24 §12-12','grid':'RPS','ready':'oem_pin_graph'})
    G['E_D24_RAIL_PRESSURE']=three_wire_5v_graph('D24 RPS 값 비정상 · 핀단위', 'D24_RPS','RPS',
      {'5v':'sensor pin3 / ECU138','gnd':'sensor pin2 / ECU119','signal':'sensor pin1 / ECU135'},'pressure signal')

    # Boost pressure: pin1 5V ECU161, pin2 GND ECU167, pin3 signal ECU112.
    C['D24_BPS']=source_circuit('D24 BPS · 3선만','D24 §12-11',[],'BPS',
      [{'name':'BPS pin1 → ECU161','role':'5V'},{'name':'BPS pin2 → ECU167','role':'ground'},{'name':'BPS pin3 → ECU112','role':'pressure signal'}],
      [n('vref','ECU161 → BPS pin1\n5V','source'),n('sensor','BOOST PRESSURE SENSOR','sensor'),n('sig','BPS pin3 → ECU112\npressure signal','measure'),n('gnd','BPS pin2 → ECU167\nGND','ground')],
      [('vref','sensor'),('sensor','sig'),('sensor','gnd')],['ECU161/BPS1 5V','ECU167/BPS2 GND','BPS3/ECU112 signal'],d24_common_note,
      standards='Supply voltage explicitly 5V at BPS sensor pin1 / ECU161.',source=d24_src)
    addcat(d,{'id':'E_D24_BOOST_PRESSURE','title':'D24 부스트압력 센서값 비정상/고정','group':'D24 엔진/센서','sheet':'D24 §12-11','grid':'BPS','ready':'oem_pin_graph'})
    G['E_D24_BOOST_PRESSURE']=three_wire_5v_graph('D24 BPS 값 비정상 · 핀단위','D24_BPS','BPS',
      {'5v':'sensor pin1 / ECU161','gnd':'sensor pin2 / ECU167','signal':'sensor pin3 / ECU112'},'pressure signal')

    # WTS exact 2-pin.
    C['D24_WTS']=source_circuit('D24 WTS · 2선만','D24 §12-12',[],'WTS',
      [{'name':'WTS pin1 → ECU145','role':'ground'},{'name':'WTS pin2 → ECU109','role':'temperature signal'}],
      [n('sensor','WATER TEMP SENSOR','sensor'),n('sig','WTS pin2 → ECU109\ntemp signal','measure'),n('gnd','WTS pin1 → ECU145\nGND','ground')],
      [('sensor','sig'),('sensor','gnd')],['WTS2/ECU109 signal','WTS1/ECU145 GND'],d24_common_note,source=d24_src)
    addcat(d,{'id':'E_D24_WATER_TEMP','title':'D24 ECU 수온값 비정상/고정','group':'D24 엔진/센서','sheet':'D24 §12-12','grid':'WTS','ready':'oem_pin_graph'})
    G['E_D24_WATER_TEMP']=two_wire_temp_graph('D24 WTS 값 비정상 · 핀단위','D24_WTS','WTS','pin1 ECU145 GND / pin2 ECU109 temperature signal')

    # MAF exact 4 pin.
    C['D24_MAF']=source_circuit('D24 MAF · 4선만','D24 §12-11',[],'MAF',
      [{'name':'MAF pin1 → ECU228','role':'air flow frequency'},{'name':'MAF pin2 → ECU235','role':'intake temp'},{'name':'MAF pin3 → ECU120','role':'ground'},{'name':'MAF pin4 → ECU137','role':'12V supply'}],
      [n('supply','ECU137 → MAF4\n12V','source'),n('sensor','MAF','sensor'),n('flow','MAF1 → ECU228\nflow frequency','measure'),n('temp','MAF2 → ECU235\nintake temp','measure'),n('gnd','MAF3 → ECU120\nGND','ground')],
      [('supply','sensor'),('sensor','flow'),('sensor','temp'),('sensor','gnd')],['MAF4/ECU137 12V','MAF3/ECU120 GND','MAF1/ECU228 flow','MAF2/ECU235 temp'],d24_common_note,
      standards='MAF supply explicitly 12V on sensor pin4 / ECU137.',source=d24_src)
    addcat(d,{'id':'E_D24_MAF','title':'D24 MAF/흡기온도 값 비정상','group':'D24 엔진/센서','sheet':'D24 §12-11','grid':'MAF','ready':'oem_pin_graph'})
    G['E_D24_MAF']={'title':'D24 MAF/흡기온도 · 4핀 분리진단','circuit':'D24_MAF','start':'supply','nodes':{
      'supply':q('1. 12V/GND','MAF pin4/ECU137 공급 12V와 pin3/ECU120 GND가 정상입니까?',['OEM 핀기능을 그대로 사용한다.','커넥터 연결 상태로 공급과 GND를 측정한다.'],[{'label':'정상','next':'signals'},{'label':'공급/GND 이상','next':'powerbad'}]),
      'signals':q('2. 두 출력 분리','pin1/ECU228 air-flow frequency와 pin2/ECU235 intake-temperature 중 어느 신호가 비정상입니까?',['두 출력이 동시에 죽으면 공급/GND/센서공통, 하나만 죽으면 해당 신호소자/선로를 우선한다.','진단기 live data와 센서핀을 비교한다.'],[{'label':'flow만 이상','next':'flowbad'},{'label':'temperature만 이상','next':'tempbad'},{'label':'둘 다 이상','next':'sensorbad'}]),
      'powerbad':r('MAF 공급/GND 회로 이상','센서 자체 판단 전에 12V 또는 GND가 비정상입니다.',['ECU137→MAF4와 ECU120→MAF3 구간을 추적한다.'],['MAF 신호소자'],['공급/GND 복구 후 두 live data 정상화'],'공급/GND 구간만 수리한다.'),
      'flowbad':r('MAF airflow signal 회로 이상','공급/GND와 온도신호는 정상이나 flow frequency만 비정상입니다.',['MAF1→ECU228 전단/후단 비교 및 센서대체로 분리한다.'],['공급/GND','온도신호회로'],['센서핀 또는 하네스 어느 지점에서 신호가 사라지는지 특정'],'해당 센서/신호선만 수리한다.'),
      'tempbad':r('MAF intake-temperature signal 회로 이상','공급/GND와 airflow는 정상이나 intake temp 신호만 비정상입니다.',['MAF2→ECU235 신호를 실온/흡기온도 변화와 비교한다.'],['공급/GND','airflow signal'],['센서핀 또는 하네스의 이상 위치 특정'],'해당 센서/신호선만 수리한다.'),
      'sensorbad':r('MAF 공통 내부고장/커넥터 가능성','정상 12V/GND인데 두 출력이 함께 비정상입니다.',['커넥터 핀장력/수분을 확인한 뒤 정상센서 A/B로 확인한다.'],['차량 공급/GND'],['정상센서에서 두 신호 모두 회복'],'공급/GND와 커넥터 확인 후 센서를 교환한다.')
    }}

    # D24 shared 5V collapse / controller health graph.
    C['D24_VREF']=source_circuit('D24 5V VREF · 공유분기만','D24 §12-6~12-15',[],'VREF1/2/3',
      [{'name':'RPS 5V','grid':'ECU138 → sensor pin3'},{'name':'BPS 5V','grid':'ECU161 → sensor pin1'},{'name':'OPTS 5V','grid':'ECU165 → sensor pin3'},{'name':'EGR VREF','grid':'ECU164'}],
      [n('ecu','ECU DCM 3.7','control'),n('rps','VREF1 ECU138\nRPS pin3','measure'),n('bps','VREF2 ECU161\nBPS pin1','measure'),n('opts','VREF3 ECU165\nOPTS pin3','measure'),n('egr','VREF3 ECU164\nEGR','measure'),n('loads','5V 센서/하네스','load')],
      [('ecu','rps'),('ecu','bps'),('ecu','opts'),('ecu','egr'),('rps','loads'),('bps','loads'),('opts','loads'),('egr','loads')],
      ['ECU138','ECU161','ECU165','ECU164','센서 분리 전/후 5V'],
      '공통 5V 고장은 센서를 하나씩 분리해 외부 단락과 ECU 내부 VREF를 분리한다. OEM이 5V라고 명시한 branch만 표시.',
      standards='RPS ECU138=5V, BPS ECU161=5V, OPTS ECU165=5V, EGR ECU164=VREF3 according to D24 §12.',source=d24_src)
    addcat(d,{'id':'E_D24_5V_REF','title':'D24 여러 센서 5V 기준전압이 낮거나 사라짐','group':'D24 엔진/ECU','sheet':'D24 §12-6~12-15','grid':'VREF1/2/3','ready':'oem_pin_graph'})
    G['E_D24_5V_REF']={'title':'D24 5V 기준전압 붕괴 · 외부단락/ECU 분리','circuit':'D24_VREF','start':'scope','nodes':{
      'scope':q('1. 영향범위','RPS/BPS/OPTS/EGR 등 여러 센서가 동시에 비현실값이고 해당 VREF가 낮습니까?',['여러 센서 동시고장은 공통 5V branch를 우선한다.','ECU138/161/165/164 중 실제 영향 branch를 측정한다.'],[{'label':'여러 branch/센서 동시 이상','next':'isolate'},{'label':'한 센서만 이상','next':'single'}]),
      'single':r('개별 센서 그래프로 이동','공통 VREF 붕괴보다 한 센서/한 branch 문제입니다.',['해당 RPS/BPS/OPTS/EGR 전용 핀 그래프로 이동한다.'],['ECU 전체 5V 고장'],['다른 5V branch 정상'],'공통 ECU를 교환하지 않는다.'),
      'isolate':q('2. 외부 5V 부하 순차분리','5V 센서/branch를 하나씩 분리할 때 VREF가 정상 5V로 회복됩니까?',['RPS ECU138, BPS ECU161, OPTS ECU165, EGR ECU164 branch를 회로자료에 맞춰 순차 분리한다.','분리마다 다른 센서 live data와 ECU 통신상태를 같이 기록한다.'],[{'label':'특정 branch 분리 시 회복','next':'external'},{'label':'모두 분리해도 회복 안 됨','next':'ecu_power'}]),
      'external':r('외부 5V 센서/배선 단락','특정 외부 branch가 VREF를 끌어내립니다.',['해당 branch의 5V↔GND/신호 단락, 커넥터 수분, 눌림을 추적한다.'],['ECU 내부 VREF'],['특정 branch 분리 시 5V/다른 센서/통신이 반복 회복'],'해당 branch만 수리한다.'),
      'ecu_power':q('3. ECU 전원/GND/통신 생존성','외부 5V 부하 분리 후 ECU B+/IGN/GND와 진단통신은 정상입니까?',['ECU 내부 VREF를 확정하기 전에 ECU 전원/GND를 부하상태로 본다.','통신불가가 동반되면 CAN/ECU power 문제를 함께 분리한다.'],[{'label':'전원/GND 또는 통신도 이상','next':'ecu_supply'},{'label':'전원/GND·통신 정상인데 VREF 없음','next':'ecu_internal'}]),
      'ecu_supply':r('ECU 공통 전원/GND/CAN 문제 우선','5V 이전에 ECU 자체 생존 조건이 깨져 있습니다.',['ECU B+/IGN/GND와 로컬 CAN을 먼저 복구한다.'],['개별 5V센서'],['공통회로 복구 후 VREF와 통신 동시 회복'],'ECU 교환 전에 공통회로를 수리한다.'),
      'ecu_internal':r('ECU 내부 VREF 회로 고장 가능성 높음','외부부하 제거, ECU 전원/GND/통신 정상인데 OEM 5V VREF가 나오지 않습니다.',['각 VREF pin을 재측정하고 커넥터 핀장력/단락을 마지막으로 확인한다.'],['외부 5V 단락','ECU 전원/GND','CAN'],['외부부하 배제 후에도 VREF 미출력 반복'],'이 조건을 만족한 뒤 ECU 수리/교환을 판단한다.')
    }}

    # D24 ECU communication/power; vehicle schematic p368 + OEM engine manual.
    C['D24_ECU_HEALTH']=source_circuit('D24 ECU 생존성 · 전원/GND/CAN/VREF만','600123-00120 2/4 + D24 §12-18~20',[368],'ECU DCM 3.7',
      [{'name':'ECU DCM 3.7','grid':'600123-00120 2/4 H1~H4'},{'name':'Engine diagnosis CAN','grid':'D24 §12-19~20'},{'name':'SENSOR 15A FUSE','grid':'D24 §12-7'}],
      [n('battery','B+/IGN','source'),n('fuse','SENSOR 15A FUSE / ECU supply','control'),n('ecu','ECU DCM 3.7','control'),n('can','Diagnosis/CAN','measure'),n('vref','5V VREF outputs','measure'),n('gnd','ECU POWER GND','ground')],
      [('battery','fuse'),('fuse','ecu'),('gnd','ecu'),('ecu','can'),('ecu','vref')],['ECU B+/IGN','ECU GND voltage-drop','SENSOR 15A FUSE','CAN response','5V VREF'],
      '진단기 무응답은 ECU교환 결론이 아니다. 전원/GND→CAN 물리선→5V 외부부하를 배제한 뒤 ECU를 판단.',standards='D24 §12-7 explicitly lists SENSOR 15A FUSE; §12-18~20 identifies ECU diagnosis/CAN.',source='600123-00120 + D24NAP 950106-01198')
    addcat(d,{'id':'E_D24_ECU_NO_COMM','title':'D24 ECU 진단기 통신 안 됨','group':'D24 엔진/ECU','sheet':'2/4 + D24 §12-18~20','grid':'ECU DCM 3.7','ready':'field_graph'})
    G['E_D24_ECU_NO_COMM']={'title':'D24 ECU 무통신 · 전원/GND/CAN/5V 분리','circuit':'D24_ECU_HEALTH','start':'other','nodes':{
      'other':q('1. 다른 모듈 통신 비교','차량의 다른 CAN 모듈은 진단기에 정상 응답합니까?',['다른 모듈이 응답하면 진단커넥터/진단기 전체고장 가능성을 크게 낮춘다.'],[{'label':'다른 모듈 정상·D24 ECU만 무응답','next':'power'},{'label':'여러 모듈 모두 무응답','next':'global'}]),
      'global':r('공통 진단/CAN 회로 우선','여러 모듈이 모두 무응답이면 D24 ECU 단독고장으로 볼 수 없습니다.',['진단커넥터 전원/GND와 공통 CAN 회로를 먼저 확인한다.'],['D24 ECU 단독고장'],['공통회로 복구 후 여러 모듈 동시 통신회복'],'공통 통신회로부터 수리한다.'),
      'power':q('2. D24 ECU 전원/GND','ECU B+/IGN과 POWER GND가 부하상태에서 안정적입니까?',['무부하 12V만 보지 말고 KEY ON/크랭킹 중 MIN/MAX와 GND 전압강하를 본다.','D24 §12-7 SENSOR 15A FUSE 공급도 확인한다.'],[{'label':'전원/GND 이상','next':'power_bad'},{'label':'정상','next':'local_can'}]),
      'power_bad':r('D24 ECU 전원/GND 공급불량','ECU가 통신할 생존전원이 확보되지 않았습니다.',['SENSOR 15A FUSE/ECU 공급/접지를 전단후단으로 추적한다.'],['ECU CAN 트랜시버'],['공급복구 후 ECU 통신과 5V VREF 동시 회복'],'전원/GND 고장구간을 수리한다.'),
      'local_can':q('3. ECU 커넥터 CAN','D24 ECU 로컬 CAN선에 정상 통신활동이 도달합니까?',['오실로스코프로 정상 통신노드와 비교하는 것이 가장 좋다.','모델 종단구성 확인 전 60Ω을 하드코딩하지 않는다.'],[{'label':'ECU 입구에서 CAN 끊김','next':'can_harness'},{'label':'CAN 도달·ECU만 무응답','next':'vref'}],['오실로스코프','DMM','백프로브']),
      'can_harness':r('D24 ECU 로컬 CAN 분기불량','공통 네트워크는 살아있지만 ECU 입구까지 CAN이 도달하지 않습니다.',['분기 커넥터/핀장력/단선·단락을 구간별 비교한다.'],['ECU 내부'],['로컬 분기 수리 후 통신 회복'],'로컬 CAN 구간만 수리한다.'),
      'vref':q('4. ECU 5V 기준전압 생존','RPS/BPS/OPTS 등 OEM 5V VREF 출력도 비정상입니까?',['무통신 + 5V 붕괴는 ECU 자체 가능성을 높이지만, 외부 5V 센서단락을 먼저 배제한다.'],[{'label':'5V도 비정상','next':'isolate5'},{'label':'5V 정상','next':'ecu_internal'}]),
      'isolate5':q('5. 외부 5V 부하 분리','5V 센서들을 분리하면 VREF 또는 ECU 통신이 회복됩니까?',['RPS/BPS/OPTS/EGR branch를 순차 분리한다.'],[{'label':'특정 branch 분리 시 회복','next':'external5'},{'label':'모두 분리해도 회복 안 됨','next':'ecu_internal'}]),
      'external5':r('외부 5V 단락이 ECU를 다운시킴','외부 센서/하네스 단락 때문에 VREF/통신이 무너집니다.',['회복을 유발한 branch의 5V-신호-GND 단락을 확인한다.'],['ECU 내부고장'],['특정 branch 분리 시 통신/VREF 반복회복'],'외부 branch만 수리한다.'),
      'ecu_internal':r('D24 ECU 자체고장 가능성 높음','다른 모듈 통신 정상, ECU B+/IGN/GND 정상, 로컬 CAN 도달, 외부 5V 부하까지 배제했는데 ECU가 응답하지 않습니다.',['ECU 커넥터 핀장력/수분을 마지막 확인하고 동일사양 정상 ECU/전문 bench test로 교차검증한다.'],['전원/GND','로컬 CAN 하네스','외부 5V 단락'],['외부회로 전부 정상 + ECU만 지속 무응답'],'이 조건에서만 ECU 수리/교환을 확정한다.')
    }}

    # D24 cranks-no-start field graph using scanner/RPM/rail pressure path. No invented pressure threshold.
    C['D24_CRANK_NO_START']=source_circuit('D24 크랭킹 무시동 · 필요한 제어경로','D24 fuel §9 + electric §12',[],'ECU/RPS/CRK/CAM/IMV/INJ',
      [{'name':'CRK','grid':'§12-14'},{'name':'CAM','grid':'§12-14'},{'name':'RPS','grid':'§12-12'},{'name':'IMV','grid':'§12-15'},{'name':'INJ #1~4','grid':'§12-13'}],
      [n('crk','CRK/CAM speed-sync','measure'),n('ecu','ECU','control'),n('imv','IMV / high-pressure pump','control'),n('rail','RPS / common rail','measure'),n('inj','Injectors','load')],
      [('crk','ecu'),('ecu','imv'),('imv','rail'),('rail','inj'),('ecu','inj')],['scan RPM/sync','RPS actual/commanded','IMV command','injector drive'],
      '무시동은 센서교환부터 하지 않고 ECU 생존→CRK/CAM→레일압 형성→IMV/연료공급→인젝터 구동 순으로 좁힌다.',source=d24_src)
    addcat(d,{'id':'E_D24_CRANK_NO_START','title':'D24 크랭킹은 되는데 시동 안 걸림','group':'D24 엔진/시동','sheet':'D24 §9 + §12','grid':'CRK/CAM/RPS/IMV/INJ','ready':'field_graph'})
    G['E_D24_CRANK_NO_START']={'title':'D24 크랭킹 무시동 · ECU/동기/레일압/분사 분리','circuit':'D24_CRANK_NO_START','start':'comm','nodes':{
      'comm':q('1. ECU 생존/통신','크랭킹 중 D24 ECU 진단통신과 live data가 유지됩니까?',['통신 자체가 끊기면 연료부품보다 ECU 전원/GND/CAN부터 본다.'],[{'label':'통신 정상','next':'rpm'},{'label':'통신 불가/크랭킹 중 끊김','next':'comm_bad'}]),
      'comm_bad':r('ECU 생존성 문제 우선','무시동보다 먼저 ECU가 크랭킹 중 살아있는지 해결해야 합니다.',['E_D24_ECU_NO_COMM 그래프로 이동해 B+/IGN/GND/CAN/5V를 분리한다.'],['인젝터/고압펌프 단독고장'],['ECU 통신이 크랭킹 중 안정화'],'ECU 생존성 복구 후 무시동 진단을 재개한다.'),
      'rpm':q('2. 크랭크/캠 동기','크랭킹 중 진단기에 엔진 RPM이 들어오고 CRK/CAM 동기 관련 이상이 없습니까?',['CRK는 ECU159 signal/147 GND, crank pair 136/160 및 shield 187 관련 OEM표를 참고한다.','캠 관련 ECU pin은 OEM §12 회로표와 센서표를 사용한다.'],[{'label':'RPM/동기 이상','next':'speed_bad'},{'label':'RPM/동기 정상','next':'rail'}]),
      'speed_bad':r('CRK/CAM 신호계통 우선','ECU가 엔진 회전을 제대로 인식하지 못합니다.',['센서 전원/GND/신호를 오실로스코프로 비교하고 센서 갭/기계 타이밍을 확인한다.','하네스 shield/커넥터를 함께 본다.'],['레일압 센서','인젝터'],['정상 CRK/CAM 신호와 진단 RPM/동기 회복'],'동기 신호 원인을 해결 후 재시동한다.',tools=['진단기','오실로스코프','DMM']),
      'rail':q('3. 레일압 형성','크랭킹 중 실제 레일압이 명령을 따라 상승합니까?',['RPS pin1/ECU135 signal, pin2/ECU119 GND, pin3/ECU138 5V를 먼저 검증한다.','D24 OEM에 없는 시동허용 MPa 숫자를 임의 생성하지 않고 진단기 command/actual과 정상차·OEM 고장코드를 비교한다.'],[{'label':'실제압 형성 실패/명령과 크게 불일치','next':'fuel_control'},{'label':'레일압 형성/센서 정상','next':'inject'}]),
      'fuel_control':q('4. 고압연료 제어 분리','저압 연료공급이 정상이고 IMV ECU177 PWM 명령/배선도 정상입니까?',['IMV는 고압펌프 유입량을 제어한다.','연료필터/공기혼입/저압공급을 먼저 배제하고 IMV 명령→실제 레일압 반응을 본다.'],[{'label':'저압공급/IMV 회로 이상','next':'fuel_bad'},{'label':'공급/IMV 정상인데 압력 형성 실패','next':'hp_bad'}]),
      'fuel_bad':r('저압공급/IMV 제어 문제','고압펌프 자체를 분해하기 전에 공급 또는 IMV 제어에서 이상이 확인됩니다.',['확인된 저압공급·공기혼입·IMV PWM/하네스를 복구하고 rail actual을 재시험한다.'],['인젝터 전기구동'],['수리 후 rail actual이 command를 따라 회복'],'확인된 공급/IMV 부분만 먼저 수리한다.'),
      'hp_bad':r('고압계통 기계/누설 추가검사','RPS와 IMV 명령/저압공급이 정상인데 레일압이 형성되지 않습니다.',['고압펌프, rail pressure leakage, injector return/내부누설을 OEM 연료계통 절차로 분리한다.','고압연료 안전절차를 준수한다.'],['RPS 전기회로','IMV 전기명령'],['기계적 누설/고압펌프 원인이 별도 시험에서 특정됨'],'고압계통 원인 특정 후에만 분해한다.'),
      'inject':q('5. 분사구동','레일압/동기 정상인데 ECU가 인젝터를 구동하고 있습니까?',['OEM injector pair: #1 ECU126/127, #2 174/150, #3 175/151, #4 125/103.','전류파형/진단기 cylinder test가 가능하면 구동을 확인하고 무작정 시험등을 연결하지 않는다.'],[{'label':'인젝터 구동 없음','next':'inj_control'},{'label':'구동 있음·여전히 무시동','next':'mechanical'}],['진단기','전류클램프/오실로스코프(권장)','OEM 회로']),
      'inj_control':r('ECU 분사허가/인젝터 구동회로 문제','동기와 레일압은 정상이나 분사구동이 없습니다.',['DTC/인터록/ECU 출력과 인젝터 하네스를 확인한다.','모든 인젝터 공통이면 ECU 공급/허가, 한 실린더면 해당 pair를 우선한다.'],['RPS','고압펌프 기계'],['구동안됨 원인이 ECU허가/하네스/출력으로 특정'],'고압펌프를 분해하지 말고 전기구동 원인을 먼저 수리한다.'),
      'mechanical':r('연료분사 이후 기계/연소 조건으로 이동','ECU 생존, 동기, 레일압, 인젝터 구동까지 확인됐습니다.',['압축, EGR stuck-open/흡기막힘, 분사품질/인젝터 리턴, 기계타이밍을 확인한다.'],['ECU 통신','CRK/CAM 전기','RPS 기본회로'],['기계/연소 원인이 별도 시험에서 특정됨'],'기계원인 특정 후 해당 계통을 분해한다.')
    }}

    # Bump version/rules.
    d['version']='0.20-rc-expert-electrical-d24-v3'
    d['mapped_diagnostic_rules']['symptom_universe_rule']='회로도에 보이는 기능은 가능한 한 개별 증상그래프로 분리하고, 한 기능을 grouped generic graph에만 묻어두지 않는다.'
    d['mapped_diagnostic_rules']['d24_rule']='D24NAP 950106-01198 §12에서 확인한 sensor/ECU pin은 재작성 회로에 직접 표시. OEM이 해상하지 않은 수치/핀은 UNKNOWN으로 유지.'
    P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('catalog',len(d['catalog']),'graphs',len(d['graphs']),'circuits',len(d['circuits']))

if __name__=='__main__': main()
