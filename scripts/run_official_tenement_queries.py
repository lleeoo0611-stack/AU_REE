#!/usr/bin/env python3
"""Read-only, nationwide source-level *tenement holder* trace; never infer developer.

Input: immutable 487 target rows. Output: evidence-tiered official query response,
source diagnostics and audit CSV/SQLite. Every government API query gets a SHA-256.
Original Project Master remains unchanged. Unavailable source != no title.
"""
from __future__ import annotations
import csv,json,hashlib,collections,concurrent.futures,pathlib,re,sys,time,threading,sqlite3,xml.etree.ElementTree as ET
import requests
from shapely.geometry import shape,Point
P=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('inputs/reverse_trace_targets_487.csv')
O=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else pathlib.Path('work/tenement_reverse_20261029')
O.mkdir(parents=True,exist_ok=True)
REST={
 'WA': [('WA_MINING_TENEMENTS','https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Industry_and_Mining_WFS/MapServer/3')],
 'QLD': [('QLD_EPM','https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Economy/CurrentQldResourceAuthorities/FeatureServer/40'),('QLD_MDL','https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Economy/CurrentQldResourceAuthorities/FeatureServer/80'),('QLD_ML','https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Economy/CurrentQldResourceAuthorities/FeatureServer/120')],
 'TAS': [('TAS_EXPLORATION','https://data.stategrowth.tas.gov.au/ags/rest/services/MRT/TenementsWFS/MapServer/36'),('TAS_MINING','https://data.stategrowth.tas.gov.au/ags/rest/services/MRT/TenementsWFS/MapServer/44')]
}
WFS={
 'NSW':('https://public-gs.geoscience.nsw.gov.au/geoserver/ows',('tenure','titles','title','exploration_and_mining')),
 'VIC':('https://opendata.maps.vic.gov.au/geoserver/wfs',('minten','mineral_tenements','mineral_tenure')),
 'NT':('https://geology.data.nt.gov.au/geoserver/wfs',('mineral_title','mineraltenement','tenure','tenement'))
}
UA='AU-REE-research-tenure-linker/1.0 (government-public-services; no automated company approval)'
thread=threading.local()
def session():
 if not hasattr(thread,'s'):
  s=requests.Session();s.headers.update({'User-Agent':UA,'Accept':'application/json, application/geo+json, application/xml, text/xml;q=0.8'});thread.s=s
 return thread.s

def get(url,params=None,timeout=35):
 e=None
 for attempt in range(3):
  try:
   r=session().get(url,params=params,timeout=(10,timeout))
   if r.status_code in (429,502,503,504):raise requests.HTTPError(str(r.status_code),response=r)
   r.raise_for_status()
   if not r.content:raise ValueError('empty response')
   return r
  except (requests.RequestException,ValueError) as ex:
   e=ex
   if attempt<2:time.sleep((attempt+1)*0.8)
 raise e

def capability(source):
 st,site=source;u,keys=WFS[st]
 try:
  r=get(u,{'service':'WFS','request':'GetCapabilities','version':'2.0.0'},timeout=65)
  root=ET.fromstring(r.content)
  options=[]
  for el in root.iter():
   if el.tag.split('}')[-1]!='FeatureType':continue
   name=next((c.text or '' for c in el if c.tag.split('}')[-1]=='Name'),'')
   title=next((c.text or '' for c in el if c.tag.split('}')[-1]=='Title'),'')
   if name and any(key in (name+' '+title).lower().replace(' ','_') for key in keys):
    if st=='NT' and not name.lower().startswith('mt:'):continue
    if st=='NSW' and 'titles_title_' not in name.lower():continue
    options.append((name,title))
  # ACTUAL layer schema must be public from the official WFS capabilities; otherwise block.
  # For multi-layer response try every candidate, do not silently pick the first.
  return {'state':st,'status':'WFS_DISCOVERED' if options else 'NO_OFFICIAL_TENEMENT_WFS_LAYER_DISCOVERED','url':u,'choices':options[:18],'caps_sha256':hashlib.sha256(r.content).hexdigest()}
 except Exception as e:return {'state':st,'status':'WFS_CAPABILITIES_FAILED','url':u,'error':str(e)[:240], 'choices':[]}

def rest_check(spec):
 key,url=spec
 try:
  r=get(url,{'f':'json'})
  d=r.json();fields=[f['name'] for f in d.get('fields',[])];geo=d.get('geometryType')
  return {'key':key,'url':url,'status':'READY' if geo=='esriGeometryPolygon' and fields else 'LAYER_SCHEMA_UNEXPECTED',
  'fields':fields,'geometryType':geo,'metadata_sha256':hashlib.sha256(r.content).hexdigest()}
 except Exception as e:return {'key':key,'url':url,'status':'METADATA_FAILED','error':str(e)[:240]}

def getpoint(row):
 try:
  lon=float(row['longitude']);lat=float(row['latitude'])
  if not (110<lon<160 and -45<lat<0):return None
  return (lon,lat)
 except (ValueError,KeyError,TypeError):return None

def select_field(d,choices):
 z={k.lower():v for k,v in d.items()}
 for k in choices:
  v=z.get(k.lower());
  if v is not None and str(v).strip() and str(v).lower()!='null':return str(v)
 return ''

def classify_status(attrs):
 status=select_field(attrs,['permitstatus','rstatus','tenstatus','status','status_desc','licence_status','licstatus','authority_status'])
 if status.lower() in ('pending','application','applied','withdrawn','cancelled','expired','surrendered','refused'):
  return 'TENURE_APPLICATION_OR_NONCURRENT',status
 if status.lower() in ('live','granted','current','active','in force','curre','renew retained','renewed'):
  return 'TENURE_OVERLAP_REPORTED_CURRENT',status
 return 'TENURE_OVERLAP_STATUS_REVIEW',status

def one_rest(row,spec):
 key,url=spec;loc=getpoint(row)
 if not loc:return [],{'query_status':'TARGET_COORD_MISSING','dataset':key,'sha256':''}
 lon,lat=loc
 params={'f':'json','geometry':f'{lon:.8f},{lat:.8f}','geometryType':'esriGeometryPoint','inSR':'4326','spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'false','resultRecordCount':100}
 try:
  r=get(url+'/query',params=params)
  d=r.json()
  if 'error' in d:raise ValueError(str(d['error'])[:220])
  if d.get('exceededTransferLimit'):raise ValueError('exceededTransferLimit')
  if not isinstance(d.get('features'),list):raise ValueError('no features array')
  sha=hashlib.sha256(r.content).hexdigest();links=[]
  for ix,f in enumerate(d['features']):
   a=f.get('attributes') or {}
   tid=select_field(a,['tenid','tenement_no','tenement','ten_no','licence','licence_id','resourceauthorityid','permitnumber','permit_no','displayname','name','tag','number','fileid','id'])
   holder=select_field(a,['holder1','authorisedholdername','owner','principal_holder','principalholder','holder','holder_name','holdername','licensee','licence_holder','licensee_name','company','operator','company_name'])
   condition,status=classify_status(a)
   links.append({'target_id':row['target_id'],'state':row['state'],'name':row['name'],'dataset':key,'official_title_number':tid,'official_holder_text':holder,'tenure_status_text':status,
    'evidence_tier':'OFFICIAL_SPATIAL_INTERSECTION','relation_status':condition,'api_response_sha256':sha,'api_url':url,'raw_attributes':json.dumps(a,ensure_ascii=False,sort_keys=True),
    'project_identity':'NOT_ESTABLISHED','developer_role':'NOT_ESTABLISHED','review_action':'VALIDATE_HOLDER_AND_PROJECT_DEVELOPMENT'})
  return links,{'query_status':'SUCCESS','dataset':key,'sha256':sha,'n':len(links)}
 except Exception as e:return [],{'query_status':'SOURCE_QUERY_ERROR','dataset':key,'error':str(e)[:300],'sha256':''}

def one_wfs(row,option):
 st=row['state'];u,_=WFS[st];loc=getpoint(row)
 if not loc:return [],{'query_status':'TARGET_COORD_MISSING','dataset':option,'sha256':''}
 lon,lat=loc
 # Bounding-box is for retrieval only; shapely point-in-polygon check follows.
 w=0.002;box=f'{lon-w:.7f},{lat-w:.7f},{lon+w:.7f},{lat+w:.7f},EPSG:4326'
 params={'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':option,'count':'100','srsName':'EPSG:4326','outputFormat':'application/json','bbox':box}
 try:
  r=get(u,params=params,timeout=60);d=r.json()
  if 'features' not in d:raise ValueError('no GeoJSON features')
  if len(d['features'])>=100:raise ValueError('WFS count cap reached, partial query')
  sha=hashlib.sha256(r.content).hexdigest();links=[];ambig=0
  for f in d['features']:
   a=f.get('properties') or {}
   try:
    geom=shape(f.get('geometry'));exact=geom.covers(Point(lon,lat))
   except Exception:ambig+=1;continue
   if not exact:continue
   tid=select_field(a,['tenid','tag','title','application','license_no','licence','licence_no','licence_number','mineral_title','tenementno','authorisation','name','ten_num','fileid','identifier'])
   holder=select_field(a,['holder','own_name','holder_name','holder1','licensee','licence_holder','company','principal_holder','applicant','owner','registered_holder'])
   cond,status=classify_status(a)
   links.append({'target_id':row['target_id'],'state':st,'name':row['name'],'dataset':option,'official_title_number':tid,'official_holder_text':holder,'tenure_status_text':status,
   'evidence_tier':'OFFICIAL_SPATIAL_INTERSECTION','relation_status':cond,'api_response_sha256':sha,'api_url':u,'raw_attributes':json.dumps(a,sort_keys=True,ensure_ascii=False),
   'project_identity':'NOT_ESTABLISHED','developer_role':'NOT_ESTABLISHED','review_action':'VALIDATE_HOLDER_AND_PROJECT_DEVELOPMENT'})
  return links,{'query_status':'SUCCESS' if not ambig else 'PARTIAL_GEOMETRY_PARSE','dataset':option,'sha256':sha,'n':len(links),'unparsed':ambig}
 except Exception as e:return [],{'query_status':'SOURCE_QUERY_ERROR','dataset':option,'error':str(e)[:280],'sha256':''}

with P.open(encoding='utf-8-sig',newline='') as f:targets=list(csv.DictReader(f))
assert len(targets)==487 and len(set(r['target_id'] for r in targets))==487
catalog=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 jobs=[pool.submit(rest_check,s) for v in REST.values() for s in v]
 for f in concurrent.futures.as_completed(jobs):catalog.append(f.result())
 for st in WFS:
  catalog.append(capability((st,WFS[st])))
# SA source currently unlocated; preserve official project->deposit evidence separately.
catalog.append({'state':'SA','status':'SA_PROJECT_DEPOSIT_ID_OFFLINE_ARCHIVE_ONLY','url':'https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs','description':'SA official direct project/deposit join executed separately; no tenement-holder spatial source validated'})
(O/'tenure_source_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
print('CATALOG='+json.dumps([{k:x.get(k) for k in ('state','key','status','choices','error')} for x in catalog],ensure_ascii=False),flush=True)
ready={d['key'] for d in catalog if d.get('status')=='READY'}
wfschoice={c['state']:[x[0] for x in c['choices'][:3]] for c in catalog if c.get('status')=='WFS_DISCOVERED'}
locks=collections.Counter();links=[];reports=[]
def query(row):
 st=row['state'];geo=getpoint(row)
 if not geo:return [],{'target_id':row['target_id'],'state':st,'cohort':row['cohort'],'target_status':'NO_USABLE_COORDINATES','datasets_attempted':0,'datasets_succeeded':0,'tenure_links':0,'dataset_errors':''}
 if st=='SA':return [],{'target_id':row['target_id'],'state':st,'cohort':row['cohort'],'target_status':'OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED','datasets_attempted':0,'datasets_succeeded':0,'tenure_links':0,'dataset_errors':'SA official project-deposit evidence separate'}
 specs=[s for s in REST.get(st,[]) if s[0] in ready]
 res=[];out=[]
 for s in specs:
  v,d=one_rest(row,s);res+=v;out.append(d)
 for opt in wfschoice.get(st,[]):
  v,d=one_wfs(row,opt);res+=v;out.append(d)
 success=sum(x['query_status']=='SUCCESS' for x in out)
 bad=[x['dataset']+':'+x.get('error',x['query_status']) for x in out if x['query_status']!='SUCCESS']
 result='TENURE_INTERSECTS_PENDING_COMPANY_VERIFICATION' if res else ('NO_OVERLAP_IN_QUERIED_LAYERS' if success==len(out) and out else 'SOURCE_UNAVAILABLE_OR_PARTIAL')
 return res,{'target_id':row['target_id'],'state':st,'cohort':row['cohort'],'target_status':result,'datasets_attempted':len(out),'datasets_succeeded':success,'tenure_links':len(res),'dataset_errors':' | '.join(bad)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 fs=[pool.submit(query,t) for t in targets]
 for i,f in enumerate(concurrent.futures.as_completed(fs),1):
  rr,dd=f.result();links.extend(rr);reports.append(dd)
  if i%50==0:print('PROGRESS',i,'of',len(targets),'intersections',len(links),flush=True)

def save(path,values,cols):
 with (O/path).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(values)
linkcols=['target_id','state','name','dataset','official_title_number','official_holder_text','tenure_status_text','evidence_tier','relation_status','api_response_sha256','api_url','raw_attributes','project_identity','developer_role','review_action']
statuscols=['target_id','state','cohort','target_status','datasets_attempted','datasets_succeeded','tenure_links','dataset_errors']
save('official_site_tenement_holder_links.csv',sorted(links,key=lambda x:(x['target_id'],x['dataset'],x['official_title_number'])),linkcols)
save('target_tenement_trace_status.csv',sorted(reports,key=lambda x:x['target_id']),statuscols)
summary={'target_count':len(targets),'source_status':[{k:x.get(k) for k in ('state','key','status','error')} for x in catalog],
 'target_status':dict(collections.Counter(x['target_status'] for x in reports)),
 'per_state':{st:{'targets':sum(x['state']==st for x in reports),'tenure_hit_targets':sum(x['state']==st and x['tenure_links']>0 for x in reports),'link_rows':sum(x['state']==st for x in links),'source_unavailable':sum(x['state']==st and x['target_status'] in ('SOURCE_UNAVAILABLE_OR_PARTIAL','OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED') for x in reports)} for st in ('WA','SA','QLD','NSW','VIC','NT','TAS')},
 'distinct_holder_texts':len({x['official_holder_text'].casefold() for x in links if x['official_holder_text']}),
 'provenance_notes':['Official title-holder names do NOT prove project developer/owner.','Current titles cannot establish historical ownership at discovery date.','A zero result from unverified/failed API is never interpreted as absence of titles.','Project Master not modified.']}
(O/'reverse_tenement_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
db=sqlite3.connect(O/'reverse_trace_evidence.sqlite')
for table,rows,columns in [('targets',targets,list(targets[0])),('official_tenure_matches',links,linkcols),('target_trace_status',reports,statuscols)]:
 defs=','.join('"'+x+'" TEXT' for x in columns);db.execute('CREATE TABLE IF NOT EXISTS "'+table+'" ('+defs+')')
 if rows:db.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?' for _ in columns)+')',[[str(row.get(k,'')) for k in columns] for row in rows])
db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close()
print('FINAL_SUMMARY='+json.dumps(summary,ensure_ascii=False),flush=True)
