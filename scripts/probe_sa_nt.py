import requests, json, pathlib, zipfile, io
S=requests.Session();OUT=pathlib.Path('work/probe2');OUT.mkdir(parents=True,exist_ok=True)
sources={'SA_projects':('https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs','south_australia_mining_projects:developing_projects___minerals'),
         'SA_deposits':('https://services.sarig.sa.gov.au/vector/mines_and_mineral_deposits/wfs','mines_and_mineral_deposits:all_mines_and_mineral_deposits'),
         'SA_critical':('https://services.sarig.sa.gov.au/vector/south_australian_critical_minerals/wfs','south_australian_critical_minerals:rare_earth_elements')}
report={}
for name,(url,typ) in sources.items():
 report[name]=[]
 for version,fmt in [('2.0.0','application/json'),('2.0.0','json'),('1.1.0','application/json'),('1.1.0','csv'),('1.0.0','json'),('2.0.0','GML2')]:
  params={'service':'WFS','version':version,'request':'GetFeature','typeNames':typ,'typeName':typ,'maxFeatures':1,'count':1,'outputFormat':fmt}
  try:
   r=S.get(url,params=params,timeout=30)
   report[name].append({'version':version,'format':fmt,'status':r.status_code,'content_type':r.headers.get('content-type'),'body':r.text[:420],'url':r.url})
  except Exception as e:report[name].append({'version':version,'format':fmt,'error':str(e)[:170]})
urls=[
'https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/81745/1/DIP003-MODAT.zip',
'https://www.geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/81745/1/DIP003-MODAT.zip',
'https://geoscience.nt.gov.au/contents/prod/Downloads/Mineral_Deposits/MINERALOCCURRENCES_csv.zip',
'https://geoscience.nt.gov.au/web/server/api/core/handle/1/81745',
'https://geoscience.nt.gov.au/web/handle/1/81745',
'https://geoscience.nt.gov.au/web/entities/publication/dip003',
'https://geoscience.nt.gov.au/downloads/NTWideDownloads.html',
]
report['NT']=[]
for url in urls:
 try:
  r=S.get(url,timeout=35,stream=True)
  buf=b''
  for chunk in r.iter_content(8192):
   buf+=chunk
   if len(buf)>=16384:break
  report['NT'].append({'url':url,'status':r.status_code,'final_url':r.url,'content_type':r.headers.get('content-type'),'content_length':r.headers.get('content-length'),'head':buf[:100].hex(),'headtext':buf[:300].decode('utf8','replace') if buf[:2]!=b'PK' else 'PK archive'})
 except Exception as e:report['NT'].append({'url':url,'error':str(e)[:200]})
(OUT/'diagnostics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
for k,v in report.items():
 print(k)
 for x in v:print(' ',x.get('version',''),x.get('format',''),x.get('status'),x.get('content_type'),x.get('content_length'),(x.get('body','') or x.get('headtext',''))[:120])