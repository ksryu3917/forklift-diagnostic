import json, pathlib
BASE=pathlib.Path(__file__).resolve().parents[1]
AS=BASE/'app/src/main/assets'
expert=json.load(open(AS/'expert_diag_v2.json'))
elec=json.load(open(AS/'electrical_diag_v1.json'))
engine=json.load(open(AS/'engine_diag_d24_v2.json'))

source={
 'title':'D20S-7/D25S-7/D30S-7/D33S-7 Parts Book',
 'document_id':'SB5120C05',
 'engine':'D24 / DL02-LEF00 / Tier4',
 'models':{'D20S-7':'FDA0U','D25S-7':'FDA0V','D30S-7':'FDA0W','D33S-7':'FDA0X'},
 'rule':'정확 품번은 모델코드와 Serial No. 적용범위를 확인한 뒤 확정. Parts Book에 변경(C), 삭제(DEL), 선택사양/옵션이 있는 경우 단일 품번으로 자동확정 금지.'
}

groups={
 'WHOLE_LOCATION':{'title':'차량 위치 차트','option':'950211-00188','pages':[1570,1571,1572],'views':['parts_views/parts_p1570.png','parts_views/parts_p1571.png','parts_views/parts_p1572.png'],'serial_required':False},
 'ENGINE_ECU':{'title':'D24 ECU','option':'EDL02-P713-001','pages':[210],'views':['parts_views/parts_p210.png'],'parts':[{'no':'300618-00037B','name':'엔진컨트롤유니트','qty':1}],'serial_required':False},
 'ENGINE_SENSOR':{'title':'D24 스위치 & 센서','option':'EDL02-P709-048','pages':[211],'views':['parts_views/parts_p211.png'],'parts':[{'no':'301318-00012A','name':'부스트 센서','qty':1,'note':'Parts Book 대체/변경품 병기됨; Serial/사양 확인 필요'},{'no':'301318-00013B','name':'부스트 센서','qty':1,'note':'대체 후보; 정확 적용범위 별도 확인'},{'no':'301318-00007A','name':'부스트 센서','qty':1,'note':'C 변경품 표기; 정확 적용범위 별도 확인'},{'no':'301317-00014D','name':'수온센서','qty':1},{'no':'65.27427-7001','name':'오일 압력 및 온도 센서','qty':1},{'no':'301308-00135A','name':'캠 스피드 센서','qty':1},{'no':'301308-00376','name':'공기 흐름 센서','qty':1},{'no':'301308-00480','name':'센서','qty':2,'note':'Parts Book 명칭이 generic; 기능 자동확정 금지'},{'no':'65.27103-7014','name':'센서','qty':1,'note':'Parts Book 명칭이 generic; 기능 자동확정 금지'}],'serial_required':True},
 'ENGINE_HARNESS':{'title':'D24 엔진 와이어 하네스','option':'EDL02-P705-220','pages':[212],'views':['parts_views/parts_p212.png'],'parts':[{'no':'310207-02855E','name':'엔진하네스어셈블리','qty':1}],'serial_required':False},
 'ENGINE_GLOW':{'title':'D24 에어히터/글로우','option':'EDL02-P704-042','pages':[213],'views':['parts_views/parts_p213.png'],'parts':[{'no':'300622-00002D','name':'글로우 플러그','qty':4},{'no':'300203-00021','name':'전기 컨넥터','qty':1}],'serial_required':False},
 'STARTER':{'title':'D24 시동 전동기','option':'EDL02-P701-042','pages':[248],'views':['parts_views/parts_p248.png'],'parts':[{'no':'300516-00034A','name':'시동 전동기','qty':1}],'serial_required':False},
 'AC_SYSTEM':{'title':'A/C 시스템','option':'620204-06246','pages':[269,270],'views':['parts_views/parts_p269.png','parts_views/parts_p270.png'],'serial_required':True,'parts':[{'no':'440205-00126','name':'에어컨디셔너어셈블리','qty':1,'apply':'중간 생산구간; 모델별 Serial 범위가 page269에 표기'},{'no':'440205-00144','name':'에어컨디셔너어셈블리','qty':1,'apply':'후기 생산구간; 모델별 Serial 범위가 page269에 표기'},{'no':'400815-00029','name':'증발기어셈블리','qty':1,'apply':'초/중기 Serial 범위'},{'no':'400815-00004','name':'증발기어셈블리','qty':1,'apply':'후기/서비스 구성 page270'},{'no':'440204-00059','name':'콘덴서어셈블리','qty':1},{'no':'210101-00490','name':'팬어셈블리','qty':1,'apply':'초기 계열: FDA0U≤202, FDA0V≤842, FDA0W≤2357, FDA0X≤476'},{'no':'210101-00569','name':'팬어셈블리;콘덴서','qty':2,'apply':'후기 계열: FDA0U≥203, FDA0V≥843, FDA0W≥2358, FDA0X≥477'},{'no':'310207-06478','name':'하네스어셈블리','qty':1,'apply':'page270 변경품; Serial 확인 필요'}]},
 'AC_COMPRESSOR':{'title':'A/C 컴프레서 장착','option':'620204-06297','pages':[502],'views':['parts_views/parts_p502.png'],'serial_required':True,'parts':[{'no':'440205-00026','name':'에어컨디셔너컴프레서어셈블','qty':1},{'no':'130202-00060','name':'에어콘벨트','qty':1},{'no':'310207-06728','name':'하네스어셈블리; D25S-7 NEWOPC AIRC','qty':1},{'no':'A404157','name':'릴레이어셈블리','qty':3,'note':'3개 릴레이의 개별 기능은 Parts Book만으로 특정 금지'},{'no':'310207-02713','name':'하네스어셈블리','qty':1}]},
 'PARK_ACTUATOR':{'title':'주차브레이크 액추에이터','option':'400805-00012','pages':[99],'views':['parts_views/parts_p99.png'],'serial_required':False,'parts':[{'no':'410111-00035','name':'유압밸브','qty':1},{'no':'300715-00153','name':'코일','qty':1},{'no':'401107-02158','name':'로드씨일키트','qty':1},{'no':'410104-00556','name':'체크밸브','qty':1}]},
 'OSS_OPTION':{'title':'OSS/EPB 옵션 배선·컨트롤러','option':'620204-07892','pages':[450],'views':['parts_views/parts_p450.png'],'serial_required':True,'parts':[{'no':'300611-01180','name':'콘트롤러어셈블리; CT100 OSS FOR E','qty':1,'note':'EPB 옵션 페이지 부품. 현재차량 옵션/Serial 확인 후 적용'},{'no':'301409-00034','name':'키스위치어셈블리','qty':1},{'no':'301404-00034','name':'방향스위치어셈블리','qty':1},{'no':'A404157','name':'릴레이어셈블리','qty':1},{'no':'310207-05711','name':'하네스어셈블리','qty':1}]},
 'SEATBELT_INTERLOCK':{'title':'시트벨트 인터로크','option':'D812926','pages':[372],'views':['parts_views/parts_p372.png'],'serial_required':False,'parts':[{'no':'310207-01549','name':'하네스어셈블리','qty':1}]},
 'MAIN_CONTROL_VALVE':{'title':'메인 컨트롤 밸브/리프트 섹션','option':'D518009 / D513675','pages':[294,297],'views':['parts_views/parts_p294.png','parts_views/parts_p297.png'],'serial_required':True,'parts':[{'no':'D513675','name':'리프트 섹션 밸브어셈블리','qty':1},{'no':'D515344','name':'틸트섹션밸브그룹','qty':1},{'no':'D513676','name':'밸브어셈블리; 듀얼 디바이더','qty':1},{'no':'D513680','name':'솔레노이드밸브조립품','qty':1},{'no':'D513502','name':'솔레노이드밸브그룹','qty':1}]},
 'LIFT_LOCK_OPTION':{'title':'리프트락/락킹 디바이스 옵션','option':'620204-16262 / 410116-01959 / 410116-01866','pages':[534,536,538],'views':['parts_views/parts_p534.png','parts_views/parts_p536.png','parts_views/parts_p538.png'],'serial_required':True,'parts':[{'no':'600109-00187','name':'솔레노이드 장착밸브','qty':1},{'no':'D840775','name':'하네스어셈블리','qty':1},{'no':'A404157','name':'릴레이어셈블리','qty':1},{'no':'410135-01088','name':'솔레노이드밸브어셈블리','qty':1}]},
 'TRANSMISSION_GROUP':{'title':'트랜스미션 그룹/펌프/파킹 액추에이터','option':'130902-02417/02418/02331/02332','pages':[119,121,123,133],'views':['parts_views/parts_p119.png','parts_views/parts_p121.png','parts_views/parts_p123.png','parts_views/parts_p133.png'],'serial_required':True,'parts':[{'no':'130902-02329','name':'트랜스미션어셈블리','qty':1},{'no':'D518253','name':'기어펌프','qty':1,'apply':'D20/25/30 계열 일부'},{'no':'D514185','name':'펌프어셈블리','qty':1,'apply':'D33 계열 일부'},{'no':'A334203','name':'온도스위치어셈블리','qty':1},{'no':'400805-00012','name':'파킹브레이크작동기','qty':1},{'no':'301413-00354','name':'압력스위치','qty':1}]},
 'CHASSIS_CORE':{'title':'차체 기본그룹/브레이크·스티어링·배선','option':'general chassis','pages':[31,32],'views':['parts_views/parts_p31.png','parts_views/parts_p32.png'],'serial_required':True,'parts':[{'no':'420212-14898','name':'브레이크 라인즈 그룹','qty':1},{'no':'410102-00001','name':'마스터 실린더 조립품','qty':1},{'no':'410102-00014','name':'브레이크 밸브 조립품','qty':1},{'no':'400322-00049','name':'마스터 실린더 조립품','qty':1},{'no':'190104-00116','name':'스티어 엑슬 그룹','qty':1},{'no':'400331-00072','name':'스티어 실린더 그룹','qty':1},{'no':'310208-00564','name':'배선 그룹','qty':1}]},
 'MAST_CONFIG':{'title':'마스트/리프트 실린더 구성','option':'model mast arrangement','pages':[13,14,15,16,17,18,19,20,21,22],'views':[],'serial_required':True,'note':'마스트 종류(STD/FFL/FFT/QD), 높이, 모델에 따라 실린더/그룹 품번이 다름. 현재차량 마스트 사양 선택 전 단일 품번 금지.'}
}

# helper link rules

def expert_groups(it):
    sys=it['system']; c=it['cause']
    base={
      '트랜스미션':['TRANSMISSION_GROUP'], '드라이브 액슬':['TRANSMISSION_GROUP'],
      '유압':['MAIN_CONTROL_VALVE'], '작업장치':['MAIN_CONTROL_VALVE'], '마스트':['MAST_CONFIG'],
      '스티어링':['CHASSIS_CORE'], '브레이크':['CHASSIS_CORE'], '주차 브레이크':['PARK_ACTUATOR'],
      '에어컨':['AC_SYSTEM','AC_COMPRESSOR']
    }.get(sys,['WHOLE_LOCATION'])
    if sys=='브레이크' and ('마스터' in c or '브레이크밸브' in c): return ['CHASSIS_CORE']
    if sys in ('유압','작업장치') and ('솔레노이드' in c or '리프트' in c): return ['MAIN_CONTROL_VALVE','LIFT_LOCK_OPTION']
    if sys=='트랜스미션' and ('전기' in c or '솔레노이드' in c): return ['TRANSMISSION_GROUP','CHASSIS_CORE']
    return base

expert_links={it['id']:{'groups':expert_groups(it),'mode':'candidate_group','note':'진단결과와 연결된 부품군. 정확 교환품번은 현재차량 모델/Serial/옵션 확인 후 확정.'} for it in expert['items']}

electrical_map={
 'E_START_NO':['STARTER','CHASSIS_CORE'], 'E_CHARGE':['ENGINE_HARNESS','CHASSIS_CORE'],
 'E_PARK_INPUT':['PARK_ACTUATOR','CHASSIS_CORE'], 'E_LIFT_LOCK':['LIFT_LOCK_OPTION','MAIN_CONTROL_VALVE'],
 'E_OSS_SEAT_LOCK':['OSS_OPTION','SEATBELT_INTERLOCK','CHASSIS_CORE'], 'E_AC_POWER_NO':['AC_SYSTEM','AC_COMPRESSOR'],
 'E_AC_COND_FAN_NO':['AC_SYSTEM','AC_COMPRESSOR'], 'E_PREHEAT_NO':['ENGINE_GLOW','ENGINE_HARNESS'],
 'E_SEATBELT_INPUT':['SEATBELT_INTERLOCK','OSS_OPTION'], 'E_D24_RAIL_PRESSURE':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'E_D24_BOOST_PRESSURE':['ENGINE_SENSOR','ENGINE_HARNESS'], 'E_D24_WATER_TEMP':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'E_D24_MAF':['ENGINE_SENSOR','ENGINE_HARNESS'], 'E_D24_5V_REF':['ENGINE_SENSOR','ENGINE_HARNESS','ENGINE_ECU'],
 'E_D24_ECU_NO_COMM':['ENGINE_ECU','ENGINE_HARNESS'], 'E_D24_CRANK_NO_START':['STARTER','ENGINE_SENSOR','ENGINE_HARNESS','ENGINE_ECU'],
 'E_FR_CONTROL':['TRANSMISSION_GROUP','CHASSIS_CORE'],
 'E_STOP_NO':['CHASSIS_CORE'], 'E_STOP_ON':['CHASSIS_CORE'], 'E_HEAD_NO':['CHASSIS_CORE'], 'E_TURN_NO':['CHASSIS_CORE'],
 'E_HORN_NO':['CHASSIS_CORE'], 'E_BACKUP_NO':['CHASSIS_CORE'], 'E_GAUGE':['CHASSIS_CORE'], 'E_WORK_LAMP':['CHASSIS_CORE'],
 'E_FUEL_HEATER_NO':['ENGINE_HARNESS'], 'E_BRAKE_OIL_WARN':['CHASSIS_CORE'], 'E_CLUSTER_POWER_NO':['CHASSIS_CORE'],
 'E_CAN_NETWORK':['ENGINE_ECU','ENGINE_HARNESS','OSS_OPTION','CHASSIS_CORE'], 'E_LICENSE_NO':['CHASSIS_CORE'],
 'E_HOURMETER_NO':['CHASSIS_CORE'], 'E_REAR_LAMP_NO':['CHASSIS_CORE'], 'E_STROBE_NO':['CHASSIS_CORE'],
 'E_WATER_GAUGE':['CHASSIS_CORE'], 'E_TM_TEMP_GAUGE':['TRANSMISSION_GROUP','CHASSIS_CORE'], 'E_FUEL_GAUGE_ONLY':['CHASSIS_CORE']
}
electrical_links={gid:{'groups':electrical_map.get(gid,['CHASSIS_CORE']),'mode':'diagnostic_link'} for gid in elec['graphs']}

engine_map={
 'E_D24_CRANK_NO_START':['STARTER','ENGINE_SENSOR','ENGINE_HARNESS','ENGINE_ECU'],
 'E_D24_ECU_NO_COMM':['ENGINE_ECU','ENGINE_HARNESS'], 'E_D24_5V_REF':['ENGINE_SENSOR','ENGINE_HARNESS','ENGINE_ECU'],
 'E_D24_RAIL_PRESSURE':['ENGINE_SENSOR','ENGINE_HARNESS'], 'E_D24_BOOST_PRESSURE':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'E_D24_WATER_TEMP':['ENGINE_SENSOR','ENGINE_HARNESS'], 'E_D24_MAF':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'EN_HARD_START':['STARTER','ENGINE_GLOW','ENGINE_SENSOR','ENGINE_HARNESS'], 'EN_STALL':['ENGINE_SENSOR','ENGINE_HARNESS','ENGINE_ECU'],
 'EN_LOW_POWER':['ENGINE_SENSOR','ENGINE_HARNESS'], 'EN_ROUGH_IDLE':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'EN_BLACK_SMOKE':['ENGINE_SENSOR'], 'EN_WHITE_SMOKE':['ENGINE_SENSOR','ENGINE_GLOW'], 'EN_BLUE_SMOKE':['ENGINE_SENSOR'],
 'EN_OVERHEAT':['ENGINE_SENSOR'], 'EN_LOW_OIL_PRESS':['ENGINE_SENSOR'], 'EN_LOW_BOOST':['ENGINE_SENSOR'],
 'EN_PREHEAT':['ENGINE_GLOW','ENGINE_HARNESS'], 'EN_FUEL_PRESSURE':['ENGINE_SENSOR','ENGINE_HARNESS'],
 'EN_CRK_CAM_SYNC':['ENGINE_SENSOR','ENGINE_HARNESS'], 'EN_INJECTOR_SEPARATE':['ENGINE_HARNESS','ENGINE_SENSOR']
}
engine_links={gid:{'groups':engine_map.get(gid,['ENGINE_SENSOR']),'mode':'diagnostic_link'} for gid in engine['graphs']}

out={'version':'1.0-parts-integrated','source':source,'groups':groups,'links':{'expert':expert_links,'electrical':electrical_links,'engine':engine_links},
     'coverage':{'expert_links':len(expert_links),'expert_total':len(expert['items']),'electrical_links':len(electrical_links),'electrical_total':len(elec['graphs']),'engine_links':len(engine_links),'engine_total':len(engine['graphs'])},
     'display_rules':['부품번호보다 적용조건을 먼저 표시','Serial 미입력 시 변경품/옵션부품 자동확정 금지','진단결과에서 관련 exploded view를 바로 열 수 있게 함','OEM 부품도는 근거/위치 확인용; 진단 회로도와 혼합하지 않음']}
json.dump(out,open(AS/'parts_reference_v1.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(out['coverage'],ensure_ascii=False))
