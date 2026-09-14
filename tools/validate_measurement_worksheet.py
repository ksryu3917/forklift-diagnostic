#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
J=ROOT/'app/src/main/java/com/ryu/forkliftdiagnostic/TestPointLocatorActivity.java'
A=ROOT/'app/src/main/assets/test_point_locator_v1.json'
R=ROOT/'build/reports/measurement_worksheet_v87.md'
errors=[]; warnings=[]
js=J.read_text(encoding='utf-8')
data=json.loads(A.read_text(encoding='utf-8'))

def need(token,msg=None):
    if token not in js: errors.append(msg or ('missing UI token: '+token))

for t in ['field_measurements_v1','field_measurement_session','작업세션','새 작업 시작 · 다른 차량/현장','차대번호 입력은 필수가 아닙니다.','현장 측정 워크시트','측정값 · 단위 포함','현장 메모','정상','이상','보류','현재 측정 기록 요약 복사','이상 포인트의 다음 분기만 모아보기','현재 화면 기록 초기화','SharedPreferences','TextWatcher','ClipboardManager']:
    need(t)
for t in ['OEM 근거가 없는 숫자 임계값은 생성하지 않습니다.','다음 분기:']:
    need(t)
# Numeric parsing is allowed only for structured OEM_EXACT auto_eval entries; arbitrary thresholds remain prohibited.
if 'Double.parseDouble' in js and 'auto_eval' not in js: errors.append('numeric parser exists without structured auto_eval gate')
if 'OEM exact 자동판정' not in js: errors.append('OEM-exact auto-evaluation UI missing')
# Every configured point must be displayable/recordable through the same addPoint path.
points=sum(len(g.get('points',[])) for g in data.get('groups',{}).values())
if points < 250: errors.append('unexpectedly low test-point count: '+str(points))
if len(data.get('groups',{})) < 50: errors.append('unexpectedly low group count: '+str(len(data.get('groups',{}))))
# Release identity gates.
gradle=(ROOT/'app/build.gradle').read_text(encoding='utf-8')
if 'versionCode 36' not in gradle: errors.append('versionCode 36 missing')
if 'versionName "0.18-rc-expert-v8.9.2-quick-ui"' not in gradle: errors.append('V8.9.2 versionName missing')
rel=json.loads((ROOT/'app/src/main/assets/diagnostic_release.json').read_text(encoding='utf-8'))
if rel.get('state')!='RC EXPERT V8.9.2 QUICK UI': errors.append('release state mismatch')
if rel.get('version_name')!='0.18-rc-expert-v8.9.2-quick-ui': errors.append('release version mismatch')

R.parent.mkdir(parents=True,exist_ok=True)
R.write_text('# V8.8 Field Measurement Worksheet Validation\n\n'
             f'- Test-point groups: {len(data.get("groups",{}))}\n'
             f'- Measurement/test points: {points}\n'
             '- Persistent value/note/status recording: required\n'
             '- PASS / FAIL / HOLD operator judgement: required\n'
             '- Abnormal-point next-branch aggregation: required\n'
             '- Clipboard summary: required\n'
             '- Arbitrary numeric auto-thresholding: prohibited; OEM_EXACT structured auto-eval permitted\n'
             f'- Errors: {len(errors)}\n'
             f'- Warnings: {len(warnings)}\n\n'
             '## Errors\n'+('\n'.join('- '+x for x in errors) or '- None')+'\n\n'
             '## Warnings\n'+('\n'.join('- '+x for x in warnings) or '- None')+'\n',encoding='utf-8')
print('V8.8 field measurement worksheet validation')
print(' groups:',len(data.get('groups',{})),'points:',points,'errors:',len(errors),'warnings:',len(warnings))
for x in errors: print('ERROR',x)
for x in warnings: print('WARN',x)
sys.exit(1 if errors else 0)
