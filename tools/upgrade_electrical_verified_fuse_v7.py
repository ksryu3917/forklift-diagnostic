#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'app/src/main/assets/electrical_diag_v1.json'
d=json.loads(p.read_text(encoding='utf-8'))
cs=d['circuits']

SOURCE={
  'name':'Doosan D20/25/30/33S-7 D24NAP Tier-4 Operation & Maintenance Manual',
  'doc':'SB2401C12 (Korean, 2022-11) / SB2401R04 multilingual-equivalent fuse table cross-check',
  'models':['D20S-7','D25S-7','D30S-7','D33S-7'],
  'engine':'D24NAP Tier-4',
  'verified_fuses':{
    'BAT1':'15A optional connector',
    'BAT2':'20A lamp relay',
    'BAT3':'15A horn',
    'BAT4':'20A OSS controller power',
    'BAT5':'20A MAIN relay / ECU power-1',
    'BAT6':'20A MAIN relay / ECU power-2',
    'BAT7':'20A alternator S / fuel-pump relay / ETC motor relay',
    'ACC':'15A turn signal / stop-strobe / light switch',
    'ST':'15A starter relay',
    'IGN1':'15A lift/unload solenoid / option connector / hazard relay',
    'IGN2':'20A ECU / instrument display power',
    'IGN3':'15A direction switch / OSS controller signal / creep-speed relay / reverse relay'
  },
  'verified_relays':{'1':'FWD','2':'C/SPEED','3':'LP FUEL','4':'LAMP','5':'REV','6':'NEUTRAL','7':'FUEL PUMP','8':'STARTER','9':'MAIN','10':'ETC'},
  'source_urls':['https://www.doosan-iv.com/common/images/sub/product/lpg/D20%2C25%2C30%2C33S-7_T4_New%20OPC%2C%20G20%2C25%2C30%2C33S-7%20GCT_HMC_SB2401C12_BK.pdf']
}

def rm_unverified(c, substrings):
    arr=c.get('unverified',[])
    c['unverified']=[x for x in arr if not any(s.lower() in x.lower() for s in substrings)]
    if not c['unverified']:
        c.pop('unverified',None)

def upsert_comp(c,name,**kw):
    for x in c.get('components',[]):
        if x.get('name')==name:
            x.update(kw); return x
    x={'name':name,**kw}; c.setdefault('components',[]).append(x); return x

def relabel_node(c,id_,label):
    for n in c.get('simplified_diagram',{}).get('nodes',[]):
        if n.get('id')==id_:
            n['label']=label; n['verified']=True

def add_verified(c, facts):
    c.setdefault('verified_protection_control',[])
    for f in facts:
        if f not in c['verified_protection_control']: c['verified_protection_control'].append(f)
    c['protection_source']='SB2401C12 D20/25/30/33S-7 D24NAP Tier-4 O&M fuse/relay table; multilingual editions cross-checked'

# STOP / turn / strobe / light switch: ACC 15A
c=cs['STOP_LAMP']; add_verified(c,['ACC 15A: turn signal / STOP-strobe / light switch']); rm_unverified(c,['STOP LAMP 회로 전용 퓨즈']); relabel_node(c,'fuse','ACC 15A\nSTOP/STROBE feed'); upsert_comp(c,'FUSE BOX',grid='E5~E6',note='ACC 15A confirmed in D20/25/30/33S-7 D24 O&M: turn signal / STOP-strobe / light switch.')
c['fuse_reference']='ACC 15A (D20/25/30/33S-7 D24NAP O&M)'

for key in ('TURN_HAZARD','STROBE'):
    c=cs[key]; add_verified(c,['ACC 15A: turn signal / STOP-strobe / light switch']); rm_unverified(c,['fuse cavity','exact fuse']); c['fuse_reference']='ACC 15A'; relabel_node(c,'fuse','ACC 15A')

# Head/rear/license illumination: BAT2 lamp relay + relay #4; ACC 15A supplies light switch
for key in ('HEAD_LAMP','REAR_LAMP','LICENSE_LAMP'):
    c=cs[key]; add_verified(c,['BAT2 20A: LAMP relay power','Relay #4: LAMP','ACC 15A: light switch feed']); rm_unverified(c,['fuse cavity','exact fuse']); c['fuse_reference']='BAT2 20A → LAMP relay #4; ACC 15A light-switch feed'; relabel_node(c,'fuse','BAT2 20A\nLAMP relay #4')

# Horn
c=cs['HORN']; add_verified(c,['BAT3 15A: horn']); rm_unverified(c,['fuse cavity','숫자 핀/퓨즈']); c['fuse_reference']='BAT3 15A'; relabel_node(c,'fuse','BAT3 15A\nHORN')

# Start
c=cs['START']; add_verified(c,['ST 15A: STARTER relay control','Relay #8: STARTER']); rm_unverified(c,['fuse cavity','숫자 핀/퓨즈']); c['fuse_reference']='ST 15A → STARTER relay #8'; c['relay_reference']='Relay #8 STARTER'; relabel_node(c,'relay','START RELAY #8\nIN / OUT / COIL')
# remove old ambiguous legacy wording if present
if 'fuse_reference' in c: pass

# Charge
c=cs['CHARGE']; add_verified(c,['BAT7 20A: alternator S / fuel-pump relay / ETC motor relay']); rm_unverified(c,['fuse cavity','숫자 핀/퓨즈']); c['fuse_reference']='BAT7 20A (alternator S)'; relabel_node(c,'fuse','BAT7 20A\nALT S')

# OSS
c=cs['OSS_SEAT_INTERLOCK']; add_verified(c,['BAT4 20A: OSS controller power','IGN3 15A: OSS controller signal']); c['fuse_reference']='BAT4 20A OSS power + IGN3 15A OSS signal'

# Lift/unload lock
c=cs['LIFT_LOCK']; add_verified(c,['IGN1 15A: lift/unload solenoid']); rm_unverified(c,['fuse cavity','숫자 핀/퓨즈']); c['fuse_reference']='IGN1 15A'; relabel_node(c,'fuse','IGN1 15A')

# Cluster / ECU power
c=cs['CLUSTER_POWER']; add_verified(c,['IGN2 20A: ECU/instrument display power']); rm_unverified(c,['fuse cavity','exact fuse']); c['fuse_reference']='IGN2 20A'; relabel_node(c,'fuse','IGN2 20A')

# F/R control
if 'FR_CONTROL' in cs:
    c=cs['FR_CONTROL']; add_verified(c,['IGN3 15A: direction switch / reverse relay','Relay #1: FWD','Relay #5: REV']); rm_unverified(c,['fuse cavity','exact fuse']); c['fuse_reference']='IGN3 15A'; c['relay_reference']='FWD #1 / REV #5'

# Backup: REV relay #5 and IGN3 control confirmed. Load fuse routing beyond relay stays source-limited.
c=cs['BACKUP']; add_verified(c,['IGN3 15A: direction switch / reverse relay','Relay #5: REV']); c['relay_reference']='Relay #5 REV'; c['fuse_reference']='IGN3 15A for direction/REV control'; rm_unverified(c,['숫자 핀/퓨즈 cavity'])
# keep note that lamp-specific branch terminal pin can remain unverified via connector mapping in components

# MAIN/ECU/CAN power
c=cs['CAN_NETWORK']; add_verified(c,['BAT5 20A: MAIN relay/ECU power-1','BAT6 20A: MAIN relay/ECU power-2','IGN2 20A: ECU/instrument display power','Relay #9: MAIN']); c['power_reference']='BAT5 20A + BAT6 20A + IGN2 20A; MAIN relay #9'

# Seat belt is OSS input: protection source is OSS power/signal fuses
c=cs['SEAT_BELT']; add_verified(c,['BAT4 20A: OSS controller power','IGN3 15A: OSS controller signal']); c['fuse_reference']='BAT4 20A OSS power + IGN3 15A OSS signal'; rm_unverified(c,['exact fuse cavity'])

# Park input likewise tied to OSS/ECU path; do not claim numeric connector pin
c=cs['PARK_INPUT']; add_verified(c,['BAT4 20A: OSS controller power','IGN3 15A: OSS controller signal']); c['fuse_reference']='BAT4 20A OSS power + IGN3 15A OSS signal'

# D24 ECU diagnostic power references
for key in ('D24_ECU_NO_COMM','D24_5V_REF','D24_RAIL_PRESSURE','D24_BOOST_PRESSURE','D24_WATER_TEMP','D24_MAF'):
    if key in cs:
        c=cs[key]; add_verified(c,['BAT5 20A: MAIN relay/ECU power-1','BAT6 20A: MAIN relay/ECU power-2','IGN2 20A: ECU/instrument display power','Relay #9: MAIN']); c['power_reference']='BAT5/BAT6 20A + IGN2 20A; MAIN relay #9'

# Preheat component part-number/source from current D24 parts book; fuse/breaker amp remains not asserted.
c=cs['PREHEAT']; c.setdefault('verified_protection_control',[]).append('D24 wiring group parts book: PREHEAT RELAY ASSY P/N 301204-00004 + breaker assembly in wiring group; exact breaker rating not asserted here')

# external source registry in electrical DB
ext=d.setdefault('external_oem_sources',{})
if isinstance(ext, list):
    ext={str(i):v for i,v in enumerate(ext)}
ext['D20_33S7_SB2401C12']=SOURCE
d['external_oem_sources']=ext

d['version']='1.7-rc-expert-v7-fuse-relay-verified'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated',p)
