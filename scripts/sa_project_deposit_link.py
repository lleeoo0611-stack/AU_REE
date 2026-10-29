#!/usr/bin/env python3
"""Official SA Geodata Project ↔ Deposit linkage for the 401 unlinked E1 records; candidate evidence only."""
import csv,io,zipfile,json,pathlib,re,collections,hashlib
ROOT=pathlib.Path('/mnt/data/AU_REE_reverse_trace_20261029')
ARCHIVE=pathlib.Path('/mnt/data/AU_REE_Australia_National_Unfiltered_Raw_2026-10-29.zip')
with zipfile.ZipFile(ARCHIVE) as z:
 def read(p):return list(csv.DictReader(io.TextIOWrapper(z.open('national_raw/'+p),encoding='utf-8-sig',errors='replace')))
 projects=read('sa_projects/SA_PROJECT_DEVELOPING.csv')+read('sa_projects/SA_PROJECT_MAJOR.csv')
 deposits=read('sa_geodata/sarig_md_details_exp.csv')
index=collections.defaultdict(list)
for p in projects:
 for num in re.findall(r'\d+',p.get('MINERAL_DEPOSIT_NUMBER','')):index[num].append(p)
dep_by_id={p['MINERAL_DEPOSIT_NO']:p for p in deposits}
# Name-only candidates are strictly separate from official identity matches.
def norm(s):return re.sub('[^a-z0-9]','',str(s or '').lower())
dep_name=collections.defaultdict(list)
for d in deposits:dep_name[norm(d['DEPOSIT_NAME'])].append(d)
with open(ROOT/'reverse_trace_targets_487.csv',encoding='utf-8-sig') as f:targets=[x for x in csv.DictReader(f) if x['cohort']=='UNLINKED_E1_401' and x['state']=='SA']
rows=[]
for t in targets:
 match_by_id=[]
 if t['source_key']=='SA_GEODATA_MINDEP':match_by_id= [dep_by_id[t['source_native_id']]] if t['source_native_id'] in dep_by_id else []
 elif t['source_key']=='SA_CRITICAL_REE':
  native=t['source_native_id'];match_by_id=[dep_by_id[native]] if native in dep_by_id else []
 if match_by_id:deps=match_by_id;match_type='DEPOSIT_NATIVE_ID'
 else:deps=dep_name.get(norm(t['name']),[]);match_type='EXACT_NORMALISED_DEPOSIT_NAME_ONLY'
 for d in deps:
  dp=d['MINERAL_DEPOSIT_NO']
  for pr in index.get(dp,[]):
   com=pr.get('COMMODITIES','')+';'+pr.get('COMMODITY_LONG','');ree=bool(re.search(r'\brare\s*earths?\b|\bREE\b',com,re.I))
   rows.append({**{k:t[k] for k in ('target_id','state','name','source_key','source_native_id')},'deposit_number':dp,'deposit_name':d['DEPOSIT_NAME'],'match_basis':match_type,
   'project_name':pr.get('PROJECT_NAME',''),'project_site_no':pr.get('SITE_NO',''),'company_text':pr.get('OPERATING_COMPANY',''),'development_status':pr.get('DEVELOPMENT_STATUS',''),'project_commodities':com,
   'ree_materiality_in_project_commodity':'EXPLICIT_REE' if ree else 'NOT_EXPLICIT',
   'evidence_status':'OFFICIAL_SA_PROJECT_DEPOSIT_RELATION' if match_type=='DEPOSIT_NATIVE_ID' else 'OFFICIAL_PROJECT_WITH_NAME_LINK_CANDIDATE',
   'developer_verified':'NO_HOLDER_VS_OPERATOR_NOT_RESOLVED', 'source_url':'https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs'})
columns=['target_id','state','name','source_key','source_native_id','deposit_number','deposit_name','match_basis','project_name','project_site_no','company_text','development_status','project_commodities','ree_materiality_in_project_commodity','evidence_status','developer_verified','source_url']
with open(ROOT/'sa_official_project_deposit_crosswalk.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
print(json.dumps({'sa_unlinked_e1':len(targets),'project_deposit_crosswalk_rows':len(rows),'target_covered':len(set(x['target_id'] for x in rows)),'direct_id_rows':sum(x['match_basis']=='DEPOSIT_NATIVE_ID' for x in rows),'project_explicit_REE_rows':sum(x['ree_materiality_in_project_commodity']=='EXPLICIT_REE' for x in rows),'sample':rows[:4]},ensure_ascii=False,indent=2))