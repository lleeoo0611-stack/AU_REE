"""Read-only official geoservice discovery for four as-yet uncaptured Australian states."""
import requests, xml.etree.ElementTree as ET, json, pathlib, zipfile, io, re
from urllib.parse import urlparse
SERVICES={
 'SA_projects':'https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs',
 'SA_deposits':'https://services.sarig.sa.gov.au/vector/mines_and_mineral_deposits/wfs',
 'SA_critical':'https://services.sarig.sa.gov.au/vector/south_australian_critical_minerals/wfs',
 'NSW_mineral_occurrences':'https://public-gs.geoscience.nsw.gov.au/geoserver/ows',
 'VIC_minsite':'https://opendata.maps.vic.gov.au/geoserver/wfs',
}
NT='https://geoscience.nt.gov.au/contents/prod/Downloads/Mineral_Deposits/MINERALOCCURRENCES_csv.zip'
REQUESTS=requests.Session();REQUESTS.headers.update({'User-Agent':'AU-REE-research-census/1.0 (public-data provenance audit)'})

def get(url,params=None,timeout=45):
 r=REQUESTS.get(url,params=params,timeout=timeout);r.raise_for_status();return r

def probe(name,url):
 result={'url':url,'status':'INIT','feature_types':[],'candidates':[]}
 try:
  r=get(url,{'service':'WFS','version':'2.0.0','request':'GetCapabilities'},timeout=50)
  (pathlib.Path('work/probe')/(name+'_capabilities.xml')).write_bytes(r.content)
  root=ET.fromstring(r.content)
  for ft in root.iter():
   if ft.tag.split('}')[-1]!='FeatureType':continue
   nm=next((c.text for c in ft if c.tag.split('}')[-1]=='Name'),None)
   title=next((c.text for c in ft if c.tag.split('}')[-1]=='Title'),None)
   if nm:result['feature_types'].append({'name':nm,'title':title})
  keys={'SA_projects':['project','mine'],'SA_deposits':['deposit','mineral','mine'],
       'SA_critical':['critical','mineral'], 'NSW_mineral_occurrences':['mineral','occurr','metindex'],
       'VIC_minsite':['minsite']}.get(name,[])
  score=lambda v: sum(2 if key in (v['name'] or '').lower() else 1 if key in (v['title'] or '').lower() else 0 for key in keys)
  candidates=sorted(result['feature_types'],key=score,reverse=True)
  for ft in candidates[:min(6,len(candidates))]:
   if not score(ft):continue
   one={**ft,'score':score(ft)}
   try:
    p={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':ft['name'],'count':'1','startIndex':'0','outputFormat':'application/json','srsName':'EPSG:4326'}
    q=get(url,p,timeout=45)
    d=q.json()
    one.update({'numberMatched':d.get('numberMatched'), 'numberReturned':d.get('numberReturned'), 'properties':list((d.get('features') or [{}])[0].get('properties',{})), 'sample':(d.get('features') or [{}])[0].get('properties',{})})
   except Exception as e:one['error']=str(e)[:250]
   result['candidates'].append(one)
  result['status']='SUCCESS' if result['feature_types'] else 'NO_FEATURE_TYPES'
 except Exception as e:result.update(status='FAIL',error=str(e)[:500])
 return result

def main():
 pathlib.Path('work/probe').mkdir(parents=True,exist_ok=True)
 report={k:probe(k,u) for k,u in SERVICES.items()}
 try:
  r=get(NT,timeout=90);name='NT_modat'
  (pathlib.Path('work/probe')/'NT_modat.zip').write_bytes(r.content)
  with zipfile.ZipFile(io.BytesIO(r.content)) as z:
   report[name]={'status':'SUCCESS','url':NT,'zip_files':[{'name':x.filename,'bytes':x.file_size} for x in z.infolist()],'zip_bytes':len(r.content)}
 except Exception as e:report['NT_modat']={'status':'FAIL','url':NT,'error':str(e)[:500]}
 pathlib.Path('work/probe/state_probe.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 for k,v in report.items():
  print(k,v['status'],'types',len(v.get('feature_types',[])),'candidate names',[(x['name'],x.get('numberMatched'),x.get('error')) for x in v.get('candidates',[])],v.get('error',''))

if __name__=='__main__':main()