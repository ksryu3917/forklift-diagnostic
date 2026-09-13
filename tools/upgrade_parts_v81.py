#!/usr/bin/env python3
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
AS=BASE/'app/src/main/assets'
p=AS/'parts_reference_v1.json'
d=json.loads(p.read_text(encoding='utf-8'))
G=d['groups']; L=d['links']

def apps(ranges):
    return [{'code':code,'min':mn,'max':mx} for code,mn,mx in ranges]
EARLY=apps([('FDA0U',1,324),('FDA0V',1,1344),('FDA0W',1,3582),('FDA0X',1,642)])
LATE=apps([('FDA0U',325,999999),('FDA0V',1345,999999),('FDA0W',3583,999999),('FDA0X',643,999999)])
AC_EARLY=apps([('FDA0U',1,202),('FDA0V',1,842),('FDA0W',1,2357),('FDA0X',1,476)])
AC_LATE=apps([('FDA0U',203,999999),('FDA0V',843,999999),('FDA0W',2358,999999),('FDA0X',477,999999)])

# Structured applicability for already-known A/C fan split.
for x in G.get('AC_SYSTEM',{}).get('parts',[]):
    if x.get('no')=='210101-00490': x['applications']=AC_EARLY
    if x.get('no')=='210101-00569': x['applications']=AC_LATE

G['BRAKE_MODULE']={
 'title':'브레이크 모듈 · Serial 변경점','option':'620101-01355 / 01461 / 01356 / 01462',
 'pages':[52,54,71,72],
 'views':['parts_views/parts_p52.png','parts_views/parts_p54.png','parts_views/parts_p71.png','parts_views/parts_p72.png'],
 'serial_required':True,
 'note':'브레이크 모듈 자체가 모델/Serial 경계에서 변경된다. 내부 정비품은 현재 모듈 식별 후 확정.',
 'parts':[
  {'no':'620101-01355','name':'브레이크 모듈','qty':1,'applications':apps([('FDA0U',1,177),('FDA0V',1,754),('FDA0W',1,2233)])},
  {'no':'620101-01461','name':'브레이크 모듈','qty':1,'applications':apps([('FDA0U',178,999999),('FDA0V',755,999999),('FDA0W',2234,999999)])},
  {'no':'620101-01356','name':'브레이크 모듈 · D33','qty':1,'applications':apps([('FDA0X',1,449)])},
  {'no':'620101-01462','name':'브레이크 모듈 · D33','qty':1,'applications':apps([('FDA0X',450,999999)])},
  {'no':'420212-14898','name':'브레이크 라인즈 그룹','qty':1,'note':'모듈과 함께 차체 구성 확인'},
  {'no':'410102-00001','name':'마스터 실린더 조립품','qty':1,'note':'차체 목록상 서비스 부품; 현재 모듈/실차 구성 대조'},
  {'no':'410102-00014','name':'브레이크 밸브 조립품','qty':1,'note':'차체 목록상 서비스 부품; 현재 모듈/실차 구성 대조'},
  {'no':'400322-00049','name':'마스터 실린더 조립품','qty':1,'note':'변경 구성 가능; 실차 부품 식별 우선'}
 ]}

G['STEER_CYLINDER']={
 'title':'스티어 실린더 · 씰/로드 구성','option':'400331-00072','pages':[93],
 'views':['parts_views/parts_p93.png'],'serial_required':False,
 'parts':[
  {'no':'D511839','name':'실린더튜브어셈블리','qty':1},
  {'no':'400337-00768','name':'실린더로드어셈블리','qty':1},
  {'no':'401106-00461','name':'오일씨일키트','qty':1}
 ]}

G['LIGHTING_STD']={
 'title':'램프/경광등 서비스 부품','option':'620204-06242 / 06243 / 06244',
 'pages':[355,357,358,409,414,436],
 'views':['parts_views/parts_p355.png','parts_views/parts_p357.png','parts_views/parts_p358.png','parts_views/parts_p409.png','parts_views/parts_p414.png','parts_views/parts_p436.png'],
 'serial_required':True,
 'note':'STD/옵션 램프 구성이 공존한다. 현재 장착 램프 형상/옵션을 부품도와 대조.',
 'parts':[
  {'no':'301005-01649','name':'콤비램프 어셈블리','qty':2,'note':'620204-06242'},
  {'no':'301005-01747','name':'램프어셈블리','qty':2,'note':'620204-06242'},
  {'no':'301005-01628','name':'후미 램프어셈블리','qty':1,'note':'620204-06243'},
  {'no':'301008-00061','name':'스트로브 어셈블리','qty':1,'note':'620204-06244'},
  {'no':'301005-01757','name':'리어 램프어셈블리','qty':1,'note':'620204-08689'},
  {'no':'301005-01300','name':'옵션 콤비네이션 램프','qty':2,'note':'620204-08406'},
  {'no':'301005-01449','name':'옵션 전방 램프','qty':2,'note':'620204-08404'}
 ]}

G['WIPER_FRONT']={
 'title':'전방 와이퍼/와셔 · Serial 변경점','option':'620204-07141',
 'pages':[487,488],'views':['parts_views/parts_p488.png'],'serial_required':True,
 'note':'모듈러 캐빈 전방 와이퍼 기준. 캐빈/옵션 형식이 다르면 해당 옵션 부품도를 별도 확인.',
 'parts':[
  {'no':'450108-00013','name':'윈도우와셔탱크','qty':1},
  {'no':'A214302','name':'와이퍼모터','qty':1,'applications':EARLY},
  {'no':'300512-00042','name':'와이퍼모터','qty':1,'applications':LATE},
  {'no':'A334166','name':'하네스조립품','qty':1,'applications':EARLY},
  {'no':'310207-08884','name':'하네스어셈블리','qty':1,'applications':LATE,'note':'부품책 변경품'},
  {'no':'301405-00139','name':'방향스위치어셈블리','qty':1,'note':'와이퍼 옵션군에서 확인; 핀기능은 별도 회로 근거 필요'}
 ]}

G['WIPER_REAR']={
 'title':'리어 와이퍼 · Serial 변경점','option':'620204-08467 / 620204-09003',
 'pages':[422,486],
 'views':['parts_views/parts_p422.png','parts_views/parts_p486.png'],'serial_required':True,
 'note':'모듈러 캐빈/캐빈 옵션에 따라 그룹이 다르다. 현재 캐빈 옵션 확인 필수.',
 'parts':[
  {'no':'A214302','name':'리어 와이퍼모터 · 초기','qty':1,'applications':EARLY},
  {'no':'220210-01910','name':'리어 와이퍼모터 · 변경품','qty':1,'applications':LATE},
  {'no':'A404124','name':'리어 와이퍼 하네스 · 초기','qty':1,'applications':EARLY},
  {'no':'310207-10236','name':'리어 와이퍼 하네스 · 변경품','qty':1,'applications':LATE},
  {'no':'301405-00139','name':'방향스위치어셈블리','qty':1}
 ]}

# Improve domain links using actual parts groups.
for iid,link in L.get('expert',{}).items():
    # IDs themselves don't reveal system reliably here; retain existing and augment via original groups.
    gs=link.get('groups',[])
    if 'CHASSIS_CORE' in gs and ('BRAKE' in iid.upper()):
        link['groups']=list(dict.fromkeys(['BRAKE_MODULE']+gs))

em=L.get('electrical',{})
for gid in ['E_STOP_NO','E_STOP_ON','E_HEAD_NO','E_TURN_NO','E_WORK_LAMP','E_LICENSE_NO','E_REAR_LAMP_NO','E_STROBE_NO']:
    if gid in em: em[gid]['groups']=list(dict.fromkeys(['LIGHTING_STD']+em[gid].get('groups',[])))
for gid in ['E_WIPER_NO','E_WASHER_NO']:
    em[gid]={'groups':['WIPER_FRONT','WIPER_REAR'],'mode':'diagnostic_link','note':'캐빈 옵션 및 Serial에 따라 와이퍼 모터/하네스 변경'}

# Update metadata.
d['version']='1.1-parts-profile-serial-aware'
d['source']['profile_rule']='현재차량 모델과 Serial을 저장해 applications 범위가 있는 품번은 자동 일치/제외 표시. 옵션 의존품은 Serial 일치만으로 자동확정하지 않음.'
d['display_rules']=[
 '현재차량 모델/Serial을 먼저 표시하고 Serial 범위가 구조화된 품번은 적용/제외를 자동 표시',
 '옵션/형상 의존품은 Serial이 맞아도 실차 옵션 확인 전 자동확정 금지',
 '부품번호보다 진단 결론과 적용조건을 먼저 표시',
 '진단결과에서 관련 exploded view를 바로 열 수 있게 함',
 'OEM 부품도는 근거/위치 확인용; 진단 회로도와 혼합하지 않음'
]
d['coverage']['part_groups']=len(G)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('groups',len(G),'electrical links',len(em))
