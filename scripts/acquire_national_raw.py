#!/usr/bin/env python3
"""National raw-first minerals evidence acquisition. NEVER filters by REE before source QA.

Government scopes: GA nationwide layer ×2, WA/QLD/TAS ArcGIS, NSW/VIC/NT WFS,
South Australia statewide SA Geodata MINDEP package ×4, plus SA project WFS ×3.
ACT has no separate survey in the AGSON catalogue; the nationwide GA layers are
retained, and ACT source parity is marked national-only, not state-complete.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys,time,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
import requests
from au_ree.core import config
from au_ree.source_adapters import load_arcgis

HERE=Path(__file__).resolve().parents[1]
S3='https://dem-sdp.s3-ap-southeast-2.amazonaws.com/'
S3_KEYS=('sarig_md_details_exp.csv','sarig_md_commodity_exp.csv','sarig_md_mineralogy_exp.csv','sarig_md_reference_exp.csv')
WFS=[('NSW_METINDEX','NSW','https://public-gs.geoscience.nsw.gov.au/geoserver/ows','mineral-occurrence:mineral_occurrence'),
     ('VIC_MINSITE','VIC','https://opendata.maps.vic.gov.au/geoserver/wfs','open-data-platform:minsite'),
     ('NT_MODAT_WFS','NT','https://geology.data.nt.gov.au/geoserver/wfs','erl:MineralOccurrenceView')]
SA_WFS=[('SA_PROJECT_DEVELOPING','south_australia_mining_projects','south_australia_mining_projects:developing_projects___minerals'),
        ('SA_PROJECT_MAJOR','south_australia_mining_projects','south_australia_mining_projects:major_mines___minerals'),
        ('SA_CRITICAL_REE','south_australian_critical_minerals','south_australian_critical_minerals:rare_earth_elements')]

session=requests.Session()
session.headers.update({'User-Agent':'AU-REE-unfiltered-government-inventory/1.0 (academic; public-data-licence)'})

def utc():return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()
def get(url,params=None,timeout=120,attempts=3,stream=False):
    error=None
    for i in range(attempts):
        try:
            r=session.get(url,params=params,timeout=(15,timeout),stream=stream)
            r.raise_for_status()
            return r
        except (requests.RequestException,ValueError) as e:
            error=e
            if i+1<attempts:time.sleep(2*(i+1))
    raise RuntimeError(f'{url} {type(error).__name__}: {str(error)[:280]}')

def write_json_atomic(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,path)

def sa_bucket_listing(root):
    r=get(S3,{'list-type':'2','max-keys':'1000'})
    (root/'sa_geodata').mkdir(exist_ok=True,parents=True)
    (root/'sa_geodata'/'s3-listing.xml').write_bytes(r.content)
    doc=ET.fromstring(r.content)
    ns={'s3':'http://s3.amazonaws.com/doc/2006-03-01/'}
    all_objects={}
    for x in doc.findall('s3:Contents',ns):
        name=x.findtext('s3:Key',default='',namespaces=ns)
        all_objects[name]={'size':int(x.findtext('s3:Size',default='-1',namespaces=ns)),
                           'last_modified':x.findtext('s3:LastModified',namespaces=ns)}
    if doc.findtext('s3:IsTruncated',default='false',namespaces=ns)=='true':
        raise RuntimeError('SA S3 listing truncated; paginate before release')
    missing=set(S3_KEYS)-set(all_objects)
    if missing:raise RuntimeError('SA source package files missing: '+repr(missing))
    return all_objects

def fetch_sa_geodata(root):
    all_objects=sa_bucket_listing(root)
    out=[]
    for key in S3_KEYS:
        dest=root/'sa_geodata'/key
        if not dest.exists() or dest.stat().st_size!=all_objects[key]['size']:
            r=get(S3+quote(key),stream=True,timeout=200)
            tmp=dest.with_name(dest.name+'.tmp')
            with tmp.open('wb') as f:
                for chunk in r.iter_content(1024*1024):
                    if chunk:f.write(chunk)
            if tmp.stat().st_size!=all_objects[key]['size']:
                raise RuntimeError(f'SA source size mismatch {key} expected={all_objects[key]["size"]} actual={tmp.stat().st_size}')
            os.replace(tmp,dest)
        with dest.open('r',encoding='utf-8-sig',errors='replace',newline='') as f:
            csv.field_size_limit(100_000_000)
            reader=csv.reader(f);header=next(reader,None)
            if not header:raise RuntimeError(f'{key} lacks CSV header')
            n=sum(1 for _ in reader)
        out.append({'key':'SA_GEODATA_'+key,'state':'SA','format':'csv','path':str(dest.relative_to(root)),
                    'count':n,'size_bytes':dest.stat().st_size,'sha256':sha(dest),
                    'origin':S3+quote(key),'s3_modified':all_objects[key]['last_modified'],
                    'source_scope':'UNFILTERED_MINERAL_DATABASE','status':'RAW_COMPLETE'})
        print(key,'RAW rows',n,flush=True)
    return out

def fetch_sa_wfs(root):
    out=[]
    for key,service,typename in SA_WFS:
        url=f'https://services.sarig.sa.gov.au/vector/{service}/wfs'
        params={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':typename,
                'count':'10000','outputFormat':'csv'}
        r=get(url,params,timeout=120)
        if 'csv' not in r.headers.get('Content-Type','').lower() or not r.content:
            raise RuntimeError(f'{key} unexpected format: {r.headers.get("Content-Type")}')
        dest=root/'sa_projects'/(key+'.csv');dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(r.content)
        with dest.open('r',encoding='utf-8-sig',errors='replace',newline='') as f:
            rd=csv.reader(f);header=next(rd,None)
            if not header:raise RuntimeError(key+' missing header')
            n=sum(1 for _ in rd)
        if n>=10000:raise RuntimeError(f'{key}: 10000 source cap reached; must implement pagination')
        out.append({'key':key,'state':'SA','format':'csv','path':str(dest.relative_to(root)),
          'count':n,'sha256':sha(dest),'origin':url,'typename':typename,
          'source_scope':'UNFILTERED_GOVERNMENT_PROJECT_LAYER','status':'RAW_COMPLETE'})
        print(key,'RAW project rows',n,flush=True)
    return out

def fetch_wfs(root,source,page_size=1000):
    key,state,url,typename=source
    out=root/'wfs'/key;out.mkdir(parents=True,exist_ok=True)
    expected=None;total=0;chunks=[];offset=0
    while True:
        params={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':typename,
                'outputFormat':'application/json','count':str(page_size),'startIndex':str(offset)}
        r=get(url,params,timeout=150)
        obj=r.json()
        if obj.get('type')!='FeatureCollection' or not isinstance(obj.get('features'),list):
            raise RuntimeError(f'{key} WFS response is not complete FeatureCollection')
        if expected is None:
            val=obj.get('numberMatched')
            if not isinstance(val,int):raise RuntimeError(f'{key} no integer numberMatched; cannot certify national coverage: {val}')
            expected=val
        features=obj['features'];n=len(features)
        if n>page_size:raise RuntimeError(f'{key} server exceeded requested page size')
        dest=out/f'features_{offset:07d}.json'
        dest.write_bytes(r.content)
        chunks.append({'path':str(dest.relative_to(root)),'count':n,'sha256':sha(dest)})
        total+=n;offset+=n
        if total>=expected:break
        if n==0 or n<page_size:raise RuntimeError(f'{key} incomplete page total={total} expected={expected}')
        if offset>200000:raise RuntimeError(f'{key} exceeded 200k limit, enlarge safely')
    if total!=expected:raise RuntimeError(f'{key} total mismatch: {total}!={expected}')
    manifest={'key':key,'state':state,'format':'geojson','origin':url,'typename':typename,
              'count':total,'expected':expected,'chunks':chunks,'source_scope':'UNFILTERED_OFFICIAL_WFS',
              'status':'RAW_COMPLETE'}
    write_json_atomic(out/'manifest.json',manifest)
    print(key,'RAW features',total,flush=True)
    return manifest

def fetch_arcgis(root,source):
    rows,digest,where=load_arcgis(source,root/'arcgis',offline=False)
    # load_arcgis caches all IDs and every feature chunk before parse/return.
    data=json.loads((Path(where)/'manifest.json').read_text())
    if data['records']!=len(rows):raise RuntimeError(source['key']+' cached count mismatch')
    return {'key':source['key'],'state':source.get('state_fixed','NATIONAL'),
            'format':'arcgis_json','origin':source['url'],'count':len(rows),
            'cache_path':str(Path(where).relative_to(root)),'manifest_sha256':sha(Path(where)/'manifest.json'),
            'source_scope':'UNFILTERED_OFFICIAL_ARCGIS_LAYER','status':'RAW_COMPLETE'}

def acquire(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    report={'schema':'AU_REE_RAW_FIRST_V1','as_of':utc(),'policy':'NO_REE_FILTERING_UNTIL_ALL_RAW_SOURCES_PASS',
            'sources':{},'errors':{},'jurisdiction_status':{},'complete':False}
    def run(key,func):
        try:report['sources'][key]=func()
        except Exception as exc:
            report['errors'][key]=str(exc)[:1600]
            print('SOURCE_FAILED',key,str(exc)[:350],flush=True)
        finally:write_json_atomic(root/'national_raw_manifest.json',report)
    all_sources=config('sources.json')['sources']
    for source in all_sources:
        if source.get('type')=='arcgis' and source.get('enabled'):
            run(source['key'],lambda source=source:fetch_arcgis(root,source))
    for s in WFS:run(s[0],lambda s=s:fetch_wfs(root,s))
    run('SA_GEODATA',lambda:fetch_sa_geodata(root))
    run('SA_PROJECT_WFS',lambda:fetch_sa_wfs(root))
    states={'WA':['STATE_WA_MINDEX'],'QLD':['STATE_QLD_MINOCC'],'TAS':['STATE_TAS_MRT'],
            'NSW':['NSW_METINDEX'],'VIC':['VIC_MINSITE'],'NT':['NT_MODAT_WFS'],
            'SA':['SA_GEODATA','SA_PROJECT_WFS']}
    for state,keys in states.items():
        report['jurisdiction_status'][state]='RAW_COMPLETE' if all(k in report['sources'] for k in keys) else 'RAW_INCOMPLETE'
    report['jurisdiction_status']['ACT']='NATIONAL_GA_SCOPE_ONLY_NOT_INDEPENDENT_STATE_SURVEY'
    report['jurisdiction_status']['GA_NATIONAL']='RAW_COMPLETE' if all(k in report['sources'] for k in ('GA_AIMR_REE_2026','GA_CRITICAL_DEPOSITS_2025')) else 'RAW_INCOMPLETE'
    report['complete']=all(v=='RAW_COMPLETE' for k,v in report['jurisdiction_status'].items() if k!='ACT')
    write_json_atomic(root/'national_raw_manifest.json',report)
    print('NATIONAL_RAW_COMPLETE',report['complete'],'source_failures',report['errors'],flush=True)
    return 0 if report['complete'] else 2

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path('work/national_raw'))
    args=ap.parse_args();raise SystemExit(acquire(args.out))
