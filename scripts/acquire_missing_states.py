#!/usr/bin/env python3
"""Acquire official WFS data for SA/NSW/VIC, NT MODAT with auditable source QA.

Keep ALL original features and hashes. Export only REE-relevant candidates to
Stage 01 CSV. A site/deposit is never assumed a project. Partial downloads fail
closed. An endpoint error remains BLOCKED, never an empty dataset.
"""
from __future__ import annotations
import csv, hashlib, io, json, pathlib, re, time, zipfile
from collections import Counter
import requests

ROOT=pathlib.Path('work/state_acquisition'); ROOT.mkdir(parents=True,exist_ok=True)
S=requests.Session(); S.headers.update({'User-Agent':'AU-REE-academic-geoscience-census/1.0; responsible-public-data-research'})
REE=re.compile(r'(?<![A-Za-z])(?:REE|REO|TREO|HREE|LREE|NdPr|rare\s*earth(?:\s*elements?)?|neodymium|praseodymium|dysprosium|terbium|yttrium|monazite|xenotime)(?![A-Za-z])',re.I)
SERVICES=[
 ('SA_PROJECT_DEVELOPING','SA','https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs','south_australia_mining_projects:developing_projects___minerals','PROJECT'),
 ('SA_PROJECT_MAJOR','SA','https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs','south_australia_mining_projects:major_mines___minerals','PROJECT'),
 ('SA_MINDEP','SA','https://services.sarig.sa.gov.au/vector/mines_and_mineral_deposits/wfs','mines_and_mineral_deposits:all_mines_and_mineral_deposits','DEPOSIT'),
 ('SA_REE_CRITICAL','SA','https://services.sarig.sa.gov.au/vector/south_australian_critical_minerals/wfs','south_australian_critical_minerals:rare_earth_elements','DEPOSIT'),
 ('NSW_METINDEX','NSW','https://public-gs.geoscience.nsw.gov.au/geoserver/ows','mineral-occurrence:mineral_occurrence','OCCURRENCE'),
 ('VIC_MINSITE','VIC','https://opendata.maps.vic.gov.au/geoserver/wfs','open-data-platform:minsite','OCCURRENCE'),
 ('NT_MODAT_WFS','NT','https://geology.data.nt.gov.au/geoserver/wfs','erl:MineralOccurrenceView','OCCURRENCE')
]
FORMAT='application/json'

def fetch(url,params,attempts=4):
    for i in range(attempts):
        try:
            r=S.get(url,params=params,timeout=(20,100));r.raise_for_status();
            if not r.content:raise ValueError('Empty official response')
            return r
        except (requests.RequestException,ValueError):
            if i==attempts-1:raise
            time.sleep(2*(i+1))

def field(a,*keys):
    lower={str(k).lower():v for k,v in a.items()}
    for k in keys:
        v=lower.get(k.lower())
        if v is not None and str(v).strip():return v
    return ''

def coords(feature,a):
    g=feature.get('geometry') or {};p=(g.get('coordinates') or []) if isinstance(g,dict) else []
    if g.get('type')=='Point' and len(p)>=2:return str(p[1]),str(p[0])
    return str(field(a,'latitude','latgda94','lat')),str(field(a,'longitude','longda94','lon'))

def effective_commodity(src,a):
    keys={'SA_PROJECT_DEVELOPING':['COMMODITIES','PROJECT_DESCRIPTION'],
    'SA_PROJECT_MAJOR':['COMMODITIES','PROJECT_DESCRIPTION'],
    'SA_MINDEP':['DEPOSIT_COMMODITIES','DEPOSIT_COMMODITY_CODES','SUMMARY_DESCRIPTION'],
    'SA_REE_CRITICAL':['DEPOSIT_COMMODITIES','DEPOSIT_COMMODITY_CODES','SUMMARY_DESCRIPTION'],
    'NSW_METINDEX':['comm_type','major_commodities','minor_commodities','ore_mineralology','commodity','dep_description'],
    'VIC_MINSITE':['prod_comm','ore_comm','comm','commdsc','ore_mineral','description','mineral','commodities'],
    'NT_MODAT_WFS':['commodity','representativeCommodity_uri','mineralOccurrenceType']}.get(src,[])
    return '; '.join(str(v) for k in keys if (v:=field(a,k)))

def normalize(src,st,entity,feat,source_url):
    a=feat.get('properties') or {};lat,lon=coords(feat,a)
    n={'SA_PROJECT_DEVELOPING':['SITE_NO','PROJECT_NAME'],'SA_PROJECT_MAJOR':['SITE_NO','PROJECT_NAME'],
    'SA_MINDEP':['MINERAL_DEPOSIT_NO','DEPOSIT_NAME'],'SA_REE_CRITICAL':['MINERAL_DEPOSIT_NO','DEPOSIT_NAME'],
    'NSW_METINDEX':['occurrence_id','deposit_name'],'VIC_MINSITE':['siteid','mine_name'],'NT_MODAT_WFS':['identifier','name']}[src]
    native=str(field(a,n[0],n[1])).strip()
    title=str(field(a,n[1],'mine_name','deposit_name')).strip()
    if not native:native=str(feat.get('id',''))
    if src=='VIC_MINSITE':
        # Mine/occurrence labels are source-level, not proof of active project.
        kind=str(field(a,'feat_type','mine_type','feature')).strip().lower()
        if 'mine' in kind:entity='MINE'
    commodity=effective_commodity(src,a)
    if src=='SA_REE_CRITICAL' and not REE.search(commodity):commodity='Rare earth elements; '+commodity
    if not REE.search(commodity):return None
    name=title or str(field(a,'field_name','deposit_name'))
    if not name:return None
    return {'native_id':src+'|'+native,'name':name,'state':st,'latitude':lat,'longitude':lon,
      'company':str(field(a,'OPERATING_COMPANY','PROJECT_OWNER','COMPANY','licence_holder','operator')).strip(),
      'commodity':commodity,'entity_level':entity,'project_name_hint':str(field(a,'PROJECT_NAME','project_name')).strip() if entity!='PROJECT' else name,
      'activity':str(field(a,'DEVELOPMENT_STATUS','PROJECT_STATUS','operation_status','mine_status','status')).strip(),
      'deposit_family':str(field(a,'deposit_class_other','dep_style','geological_deposit_type')).strip(),
      'source_url':source_url}

def collect_wfs(source):
    key,st,url,typename,entity=source
    directory=ROOT/key;directory.mkdir(parents=True,exist_ok=True)
    selected=[];total=0;raw_sha=[];seen=set();rejections=Counter();expected=None
    for offset in range(0,200000,1000):
        p={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':typename,
           'outputFormat':FORMAT,'count':'1000','startIndex':str(offset)}
        r=fetch(url,p)
        data=r.json()
        if data.get('type')!='FeatureCollection':raise RuntimeError(f'{key}: not GeoJSON FeatureCollection')
        records=data.get('features')
        if not isinstance(records,list):raise RuntimeError(f'{key}: no features')
        if expected is None and isinstance(data.get('numberMatched'),int):expected=data['numberMatched']
        path=directory/f'features_{offset:06d}.json';path.write_bytes(r.content)
        raw_sha.append({'file':path.name,'sha256':hashlib.sha256(r.content).hexdigest(),'rows':len(records)})
        for rec in records:
            a=rec.get('properties') or {}
            item=normalize(key,st,entity,rec,url)
            native=(item or {}).get('native_id') or f'{key}|{field(a,"MINERAL_DEPOSIT_NO","SITE_NO","occurrence_id","siteid")}'
            if native in seen:rejections['DUPLICATE_NATIVE_ID']+=1;continue
            seen.add(native)
            if item:selected.append(item)
        total+=len(records)
        if len(records)<1000:break
    if expected is not None and total!=expected:raise RuntimeError(f'{key}: incomplete download expected {expected}, got {total}')
    if not total:raise RuntimeError(f'{key}: empty official feature collection')
    manifest={'key':key,'url':url,'typename':typename,'entity_level':entity,'raw_count':total,'unique_native_ids':len(seen),
        'ree_candidates':len(selected),'expected':expected,'chunks':raw_sha,'duplicates':dict(rejections),'status':'ACQUIRED_RAW_UNVERIFIED'}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
    return selected,manifest

def nt_diagnostics():
    # The legacy public CSV endpoint returns an HTML maintenance page (not a ZIP).
    # A missing source is reported explicitly; never substitute invented entries.
    url='https://geoscience.nt.gov.au/contents/prod/Downloads/Mineral_Deposits/MINERALOCCURRENCES_csv.zip'
    try:
        r=fetch(url,{},attempts=2)
        if not zipfile.is_zipfile(io.BytesIO(r.content)):
            return {'status':'BLOCKED_OFFICIAL_ENDPOINT_HTML','url':url,'http_code':r.status_code,'content_type':r.headers.get('content-type')}
        # Leave NT raw archive to an independently reviewed adapter once live.
        (ROOT/'NT_MODAT_raw.zip').write_bytes(r.content)
        return {'status':'RAW_ARCHIVED_NEEDS_FORMAT_ADAPTER','url':url,'sha256':hashlib.sha256(r.content).hexdigest()}
    except Exception as e:return {'status':'FAILED','url':url,'error':str(e)[:300]}

def main():
    report={};by_state={'SA':[],'NSW':[],'VIC':[],'NT':[]}
    for source in SERVICES:
        key,state=source[:2]
        try:
            rows,manifest=collect_wfs(source);by_state[state].extend(rows);report[key]=manifest
            print(key,'SUCCESS',manifest['raw_count'],'records;',manifest['ree_candidates'],'REE candidates',flush=True)
        except Exception as e:
            report[key]={'status':'FAILED','error':str(e)[:500]}
            print(key,'FAILED',str(e)[:220],flush=True)
    # Legacy NT CSV endpoint is obsolete; the live official WFS is acquired above.
    report['NT_LEGACY_LINK']={'status':'SUPERSEDED_BY_NT_MODAT_WFS','url':'https://geology.data.nt.gov.au/geoserver/wfs'}
    fields=['native_id','name','state','latitude','longitude','company','commodity','entity_level','project_name_hint','activity','deposit_family','source_url']
    targets={'SA':'sa_sarig.csv','NSW':'nsw_minview.csv','VIC':'vic_minsite.csv','NT':'nt_modat.csv'}
    for st,fname in targets.items():
        relevant=[k for k in report if k.startswith(st+'_')]
        if not all(report[k]['status']=='ACQUIRED_RAW_UNVERIFIED' for k in relevant):continue
        path=pathlib.Path('inputs/state_exports')/fname;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',encoding='utf8',newline='') as out:
            w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(by_state[st])
        report[st+'_CSV']={'status':'GENERATED_REE_CANDIDATES_UNVERIFIED','path':str(path),'candidates':len(by_state[st]),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT/'official_state_acquisition.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print('SOURCE_RESULTS='+json.dumps({k:{'status':v['status'],'raw_count':v.get('raw_count'),'ree_candidates':v.get('ree_candidates')} for k,v in report.items()}),flush=True)
    # Do not suppress source failures: workflow may still continue to Stage 01 for partial QA.
    return 0
if __name__=='__main__':raise SystemExit(main())