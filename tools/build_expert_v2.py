#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'app/src/main/assets/manual_db.json'
OUT=ROOT/'app/src/main/assets/expert_diag_v2.json'

TOPOLOGIES={
'트랜스미션':[
 ('engine','엔진','source'),('converter','토크컨버터','component'),('pump','T/M 펌프\nTap1/Tap6','measure'),('inch','인칭/감압','control'),('selector','Selector/Modulation','control'),('clutch','F/R 클러치\nTap4/Tap5','measure'),('output','출력축','component'),('axle','드라이브 액슬','load')],
'브레이크':[
 ('hyd','메인 유압','source'),('supply','브레이크 공급분기','measure'),('valve','브레이크밸브/마스터','control'),('line','브레이크 라인','component'),('piston','액슬 브레이크 피스톤','load'),('disc','Wet Disc Pack','load')],
'스티어링':[
 ('tank','작동유 탱크','source'),('pump','메인펌프','measure'),('priority','우선순위밸브','control'),('unit','스티어링유닛','control'),('cyl','조향실린더','load'),('link','액슬/링크','load')],
'유압':[
 ('tank','작동유 탱크','source'),('suction','흡입라인/스트레이너','component'),('pump','메인펌프','measure'),('relief','릴리프/분배','control'),('valve','컨트롤밸브','control'),('act','실린더/작동기','load'),('return','리턴/필터','component')],
'작업장치':[
 ('pump','메인펌프','source'),('relief','릴리프','control'),('spool','LIFT/TILT/AUX 스풀','control'),('check','체크/로드홀딩','control'),('cyl','실린더','load'),('mast','마스트/부하','load'),('return','리턴','component')],
'마스트':[
 ('valve','컨트롤밸브','source'),('line','호스/배관','component'),('cyl','리프트/틸트 실린더','load'),('seal','피스톤/로드 시일','component'),('mast','마스트/캐리지','load')],
'드라이브 액슬':[
 ('tm','T/M 출력','source'),('uj','U-조인트','component'),('pinion','피니언/크라운','component'),('diff','디퍼런셜','component'),('shaft','액슬샤프트','component'),('hub','허브/휠','load')],
'주차 브레이크':[
 ('lever','레버','source'),('cable','케이블','component'),('cam','캠/스트러트','component'),('band','브레이크 밴드','load'),('shaft','회전체','load')],
'에어컨':[
 ('compressor','컴프레서/클러치','source'),('condenser','컨덴서 + 콘덴서팬\n방열','component'),('drier','리시버 드라이어','component'),('expansion','팽창밸브','control'),('evap','증발기','load'),('cabair','실내공기/블로워\n공기측','load')],
}

EDGES={k:[(arr[i][0],arr[i+1][0]) for i in range(len(arr)-1)] for k,arr in TOPOLOGIES.items()}
# A/C는 냉매회로와 실내 공기측을 분리한다. 블로워를 냉매 직렬경로로 그리지 않는다.
EDGES['에어컨']=[('compressor','condenser'),('condenser','drier'),('drier','expansion'),('expansion','evap'),('evap','compressor'),('cabair','evap')]


def has(t,*w):
 t=t.lower(); return any(x.lower() in t for x in w)

def highlight(system,cause):
 n=cause
 if system=='트랜스미션':
  if has(n,'오일 레벨','오일레벨','오일 부족','오일 과다','오염 오일'): return ['pump']
  if has(n,'컨버터','바이패스 오리피스','쿨러','냉각'): return ['converter'] if '컨버터' in n else ['pump']
  if has(n,'펌프'): return ['pump']
  if has(n,'인칭'): return ['inch']
  if has(n,'모듈','selector','셀렉터','스풀','릴리프'): return ['selector']
  if has(n,'클러치','시일링','피스톤 시일'): return ['clutch']
  if has(n,'기어','베어링','기계 고장'): return ['output']
  if has(n,'전기','솔레노이드'): return ['selector']
  return ['selector']
 if system=='브레이크':
  if has(n,'페달'): return ['valve']
  if has(n,'공급유량','컨트롤밸브','체크밸브'): return ['supply']
  if has(n,'브레이크밸브','마스터','서보'): return ['valve']
  if has(n,'라인','연결'): return ['line']
  if has(n,'피스톤','시일'): return ['piston']
  if has(n,'디스크','플레이트'): return ['disc']
  return ['valve']
 if system=='스티어링':
  if has(n,'펌프'): return ['pump']
  if has(n,'우선순위','릴리프'): return ['priority']
  if has(n,'스티어링유닛','컬럼'): return ['unit']
  if has(n,'실린더'): return ['cyl']
  if has(n,'액슬','연결장치'): return ['link']
  return ['unit']
 if system=='유압':
  if has(n,'오일 레벨','점도','오일부족'): return ['tank']
  if has(n,'인입','흡입','필터'): return ['suction']
  if has(n,'펌프','샤프트 시일'): return ['pump']
  if has(n,'릴리프'): return ['relief']
  if has(n,'시스템 누출'): return ['valve','act']
  if has(n,'실린더','피스톤로드'): return ['act']
  return ['valve']
 if system=='작업장치':
  if has(n,'릴리프'): return ['relief']
  if has(n,'스풀','링케이지','볼트','몸체'): return ['spool']
  if has(n,'체크'): return ['check']
  if has(n,'시일','누유'): return ['spool']
  if has(n,'펌프'): return ['pump']
  return ['spool']
 if system=='마스트':
  if has(n,'피스톤시일','헤드 시일','로드','와이퍼'): return ['seal']
  if has(n,'정렬'): return ['cyl','mast']
  if has(n,'실린더'): return ['cyl']
  return ['cyl']
 if system=='드라이브 액슬':
  if has(n,'피니언','드라이브기어','백래시'): return ['pinion']
  if has(n,'디퍼런셜','사이드기어','스파이더','스러스트'): return ['diff']
  if has(n,'축 길이'): return ['shaft']
  if has(n,'휠','허브','베어링','스터드'): return ['hub']
  if has(n,'오일시일','브리더','윤활'): return ['pinion','diff']
  return ['diff']
 if system=='주차 브레이크':
  if '케이블' in n: return ['cable']
  if '밴드' in n: return ['band']
  return ['cam']
 if system=='에어컨':
  if has(n,'컴프레서'): return ['compressor']
  if has(n,'컨덴서','팬'): return ['condenser']
  if has(n,'건조기','수분','오물'): return ['drier']
  if has(n,'팽창밸브'): return ['expansion']
  if has(n,'냉매','가스 누출','과다','공기유입'): return ['compressor','condenser','expansion','evap']
  return ['compressor']
 return []


def measure_points(system,cause,c):
 src=c.get('source',''); pgs=c.get('pdf_pages',[])
 base={'source':src,'pdf_pages':pgs}
 if system=='트랜스미션':
  pts=[
   {'id':'Tap6','where':'메인라인/공통 공급','check':'공통 공급압','expected':'OEM 시험조건에서 8.3~10.3 bar','source':'T_PRESS'},
   {'id':'Tap4','where':'전진 클러치 회로','check':'F 선택 apply / 반대방향 release','expected':'선택 시 7.3~8.6 bar, 비선택 시 0 bar','source':'T_PRESS'},
   {'id':'Tap5','where':'후진 클러치 회로','check':'R 선택 apply / 반대방향 release','expected':'선택 시 7.3~8.6 bar, 비선택 시 0 bar','source':'T_PRESS'}]
  if has(cause,'컨버터'): pts += [{'id':'Tap3','where':'컨버터 charge','check':'충전압','expected':'0.7~1.4 bar','source':'T_PRESS'},{'id':'Tap2','where':'컨버터 출구/쿨러 입구','check':'출구압','expected':'0.3~0.6 bar','source':'T_PRESS'}]
  if has(cause,'윤활'): pts += [{'id':'Tap7','where':'윤활회로','check':'윤활압','expected':'0.1~0.7 bar','source':'T_PRESS'}]
  return pts
 if system=='브레이크':
  return [dict(base,id='B-IN',where='브레이크밸브/마스터 입구 또는 공급분기',check='공급 존재/반응',expected='상류 공통압과 비교'),dict(base,id='B-OUT',where='브레이크밸브/마스터 출구',check='페달 작동 시 압력 형성/해제',expected='입구 정상 + 출구 반응 비교; OEM 누설 허용치 없으면 임의 수치 금지'),dict(base,id='AXLE-L/R',where='좌/우 액슬 브레이크 입구',check='격리 전후 비교',expected='한쪽 격리 시 증상 정상화 여부')]
 if system=='스티어링':
  return [dict(base,id='S-IN',where='우선순위밸브 입구',check='메인펌프 공급',expected='OEM S_PRESS 조건'),dict(base,id='S-OUT',where='우선순위밸브 조향 공급 포트',check='조향 공급압',expected='좌/우 끝단 및 입구와 비교'),dict(base,id='CYL-L/R',where='조향실린더 L/R',check='방향별 출력/내부누설',expected='정상측/반대방향 비교')]
 if system in ('유압','작업장치','마스트'):
  return [dict(base,id='P',where='메인펌프/컨트롤밸브 계기 포트',check='공급압',expected='차종별 OEM 시스템압/릴리프 기준 사용'),dict(base,id='A/B',where='해당 스풀/실린더 포트',check='명령 시 압력/유지/복귀',expected='공통 공급과 비교; OEM 수치 없으면 격리 전후 비교'),dict(base,id='RETURN',where='리턴/탱크 복귀',check='제한/비정상 발열',expected='기능별 정상측과 비교')]
 if system=='드라이브 액슬':
  return [dict(base,id='INPUT',where='T/M 출력/U-조인트 입력',check='입력회전/유격',expected='동일 조건 좌우/정상상태 비교'),dict(base,id='BACKLASH',where='피니언-크라운/디퍼런셜',check='백래시/회전저항/치면',expected='해당 OEM 조정 절차의 수치 사용'),dict(base,id='HUB',where='좌/우 허브',check='축/반경 유격·소음',expected='정상측 비교 + OEM 한계값 있을 때만 수치판정')]
 if system=='주차 브레이크':
  return [dict(base,id='LEVER',where='주차브레이크 레버',check='유효 스트로크/복귀',expected='OEM 조정 절차'),dict(base,id='CABLE',where='케이블/캠',check='실제 이동 전달',expected='레버 이동이 밴드까지 손실 없이 전달'),dict(base,id='BAND',where='밴드/회전체',check='체결력/마모',expected='OEM 조정·마모 한계 있을 때만 수치')]
 if system=='에어컨':
  return [dict(base,id='LOW',where='저압 서비스포트',check='저압',expected='RECIRC·흡입 30~35℃·1500 rpm·블로워4·COOL에서 1.5~2.5 bar'),dict(base,id='HIGH',where='고압 서비스포트',check='고압',expected='동일 조건에서 13.7~15.7 bar'),dict(base,id='TEMP',where='컨덴서/증발기 전후',check='온도/방열 패턴',expected='압력 조합과 함께 비교')]
 return []


def make_diagram(system,cause,c):
    """고장과 직접 관련된 기능구간만 남긴 진단용 미니 도면.

    전체 계통을 매번 복사하지 않는다. 원인 노드 주변의 상류/하류와
    측정에 필요한 공급/출력 경로만 남긴다.
    """
    arr=TOPOLOGIES[system]
    node_map={i:(i,lab,role) for i,lab,role in arr}
    order=[i for i,_,_ in arr]
    hi=set(highlight(system,cause))
    edges=EDGES[system]

    # A/C 냉매계통은 순환회로라 원인에 따라 필요한 가지를 명시적으로 고른다.
    if system=='에어컨':
        if has(cause,'팬'):
            keep={'compressor','condenser','drier'}
        elif has(cause,'블로워'):
            keep={'cabair','evap','expansion'}
        elif has(cause,'팽창밸브'):
            keep={'drier','expansion','evap','compressor'}
        elif has(cause,'건조기','수분','오물'):
            keep={'condenser','drier','expansion','evap'}
        elif has(cause,'컴프레서'):
            keep={'evap','compressor','condenser','drier'}
        else:
            keep={'compressor','condenser','drier','expansion','evap'}
    else:
        idx=[order.index(x) for x in hi if x in order]
        if idx:
            lo=max(0,min(idx)-2); hi_i=min(len(order)-1,max(idx)+1)
            keep=set(order[lo:hi_i+1])
        else:
            keep=set(order[:4])
        # 최소 4개 노드를 보장하되 전체 계통은 불필요하게 보여주지 않는다.
        while len(keep)<min(4,len(order)):
            pos=[order.index(x) for x in keep]
            if max(pos)<len(order)-1: keep.add(order[max(pos)+1])
            elif min(pos)>0: keep.add(order[min(pos)-1])
            else: break

    kept_nodes=[node_map[i] for i in order if i in keep]
    kept_edges=[(a,b) for a,b in edges if a in keep and b in keep]
    # 순환/분기 때문에 edge가 부족한 경우 원래 기능 연결 중 keep에 닿는 핵심 edge를 추가한다.
    if len(kept_edges)<2:
        kept_edges=[(a,b) for a,b in edges if a in keep or b in keep][:max(2,len(keep)-1)]
        for a,b in kept_edges:
            keep.add(a); keep.add(b)
        kept_nodes=[node_map[i] for i in order if i in keep]

    return {
      'title':f'{system} · {cause} 진단용 재작성 흐름도',
      'kind':'fault_specific_functional_schematic',
      'nodes':[{'id':i,'label':lab,'role':role,'highlight':i in hi} for i,lab,role in kept_nodes],
      'edges':[{'from':a,'to':b} for a,b in kept_edges if a in keep and b in keep],
      'measure_points':[x['id'] for x in measure_points(system,cause,c)],
      'note':'원본 전체 도면을 복사하지 않고, 이 원인을 배제/확정하는 데 필요한 기능구간만 재작성. 정확한 OEM 포트/핀/수치는 원문 확인값만 표시.'
    }


def field_level(c):
 mode=c.get('field_evidence_mode','')
 if c.get('ui_tests') or c.get('graph') or mode in ('oem_numeric','oem_procedure_chain'):
  return 'A_OEM_EXECUTABLE'
 if mode in ('comparative_isolation','visual_confirm','repair_and_retest'):
  return 'B_FIELD_EXECUTABLE'
 return 'C_REVIEW'


def main():
 d=json.loads(DB.read_text(encoding='utf-8'))
 items=[]; levels=Counter(); systems=Counter()
 for s in d['symptoms']:
  system=s['system']; sid=s['id']; sym=s['name']
  for c in s.get('cause_details',[]):
   level=field_level(c); levels[level]+=1; systems[system]+=1
   items.append({
    'id':c['id'],'symptom_id':sid,'system':system,'symptom':sym,'cause':c['name'],
    'level':level,'oem_source':{'section':c.get('source',''),'pdf_pages':c.get('pdf_pages',[]),'ui_tests':c.get('ui_tests',[])},
    'diagram':make_diagram(system,c['name'],c),
    'measurement_points':measure_points(system,c['name'],c),
    'field_sequence':c.get('diag_plan',[]),'tools':c.get('field_tools',[]),
    'rule_out':c.get('field_rule_out',[]),'confirm_if':c.get('field_confirm',[]),
    'disassembly_gate':c.get('disassembly_gate',''),'evidence_mode':c.get('field_evidence_mode',''),
    'linked_graph':c.get('graph'),
    'accuracy_gate':c.get('field_review_note') or ('OEM에 수치/핀 한계가 없으면 정상측 비교·회로 격리로 판정하고 임의 기준값을 만들지 않는다.')
   })
 out={
  'version':'0.19-expert-field-v2',
  'scope':'D20/25/30/33S(SE)-7 all normalized causes',
  'definition':'정비사가 분해 전에 실제 현장에서 원인을 배제/확정할 수 있는 실행형 진단 + 고장 전용 재작성 도면',
  'source_manual':d['manual'],
  'counts':{'symptoms':len(d['symptoms']),'causes':len(items),'by_system':dict(systems),'levels':dict(levels)},
  'quality_gate':{
    'required':['diagram','measurement_points','field_sequence','tools','rule_out','confirm_if','disassembly_gate','oem_source'],
    'electrical_rule':'정적 도통 정상만으로 배선 정상 판정 금지; 부하 전압강하/백프로브/흔들림 재현/CAN·5V 컨트롤러 생존성까지 필요 시 확인',
    'diagram_rule':'원본 페이지 전체를 기본 화면에 복사하지 않고, 고장과 관련된 기능 경로만 재작성. OEM 원본은 근거 확인용 보조 화면.',
    'numeric_rule':'OEM 수치가 확인되지 않으면 임의 기준 금지.'
  },
  'items':items
 }
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out['counts'],ensure_ascii=False,indent=2))

if __name__=='__main__': main()
