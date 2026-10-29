#!/usr/bin/env python3
"""Generate editable review matrices/SQLite from official spatial query artifact and SA ID joins.

Usage: python build_reverse_workpack.py <official_trace_zip> <original_target_csv> <sa_crosswalk_csv> <output_dir>
Project Master remains unchanged; holder != operator != project owner.
"""
import csv,json,collections,zipfile,io,pathlib,re,sys,sqlite3,hashlib
zip_path=pathlib.Path(sys.argv[1]);target_path=pathlib.Path(sys.argv[2]);sa_path=pathlib.Path(sys.argv[3]);out=pathlib.Path(sys.argv[4]);out.mkdir(parents=True,exist_ok=True)

def source_csv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def zip_csv(z,p):
 with io.TextIOWrapper(z.open(p),encoding='utf-8-sig',errors='replace') as f:return list(csv.DictReader(f))
with zipfile.ZipFile(zip_path) as z:
 links=zip_csv(z,'work/tenement_reverse_20261029/official_site_tenement_holder_links.csv')
 audit=zip_csv(z,'work/tenement_reverse_20261029/target_tenement_trace_status.csv')
 source=json.loads(z.read('work/tenement_reverse_20261029/tenure_source_catalog.json'))
raw=source_csv(target_path);sa=source_csv(sa_path)
assert len(raw)==487 and len(audit)==487 and len({x['target_id'] for x in raw})==487
assert len([x for x in raw if x['cohort']=='LEGACY_86'])==86 and len([x for x in raw if x['cohort']=='UNLINKED_E1_401'])==401

def normalize_holder(a):
 ds=a['dataset'];r=json.loads(a['raw_attributes']);t=a['official_holder_text'].strip()
 if ds.startswith('mt:'):
  m=re.search(r'(?:^|\n|,)\s*Holder\s*-\s*(.+?)(?:\(\s*\d+(?:\.\d+)?\s*%\))?(?:,|\n|$)',t,re.I|re.S)
  if m:t=m.group(1).strip().rstrip(',').strip()
  t=re.sub(r'\s*\(\s*\d+(?:\.\d+)?\s*%\s*\)','',t).strip()
 elif ds.startswith('QLD_'):t=str(r.get('authorisedholdername') or t).strip()
 elif ds.startswith('TAS_'):t=str(r.get('OWNER') or t).strip()
 elif ds=='open-data-platform:minten':t=str(r.get('own_name') or t).strip()
 elif ds.startswith('mining-and-exploration:'):
  t=str(r.get('holder') or r.get('applicant') or t).strip()
 return t

def status(a):
 st=a['state'];d=a['dataset'];x=a['tenure_status_text'].strip().lower()
 if st=='NSW':
  if d.endswith('_granted'):return 'OFFICIAL_CURRENT_GRANTED_LAYER'
  if d.endswith('_historic'):return 'OFFICIAL_HISTORIC_LAYER'
  if d.endswith('_applications'):return 'OFFICIAL_APPLICATION_LAYER'
 if st=='WA':return 'OFFICIAL_CURRENT' if x=='live' else 'OFFICIAL_PENDING_OR_OTHER'
 if st=='QLD':return 'OFFICIAL_CURRENT' if x=='granted' else 'OFFICIAL_APPLICATION_OR_OTHER'
 if st=='TAS':return 'OFFICIAL_CURRENT' if x=='granted' else 'OFFICIAL_PENDING_OR_OTHER'
 if st=='VIC':return 'OFFICIAL_CURRENT' if x=='current' else 'OFFICIAL_HISTORICAL_OR_OTHER'
 if st=='NT':
  if x in ('grant','renew retained'):return 'OFFICIAL_CURRENT_OR_RETAINED'
  if x=='reduction retained':return 'RETAINED_STATUS_NEEDS_DATE_CHECK'
  return 'OFFICIAL_APPLICATION_OR_OTHER'
 return 'STATUS_NOT_CLASSIFIED'

def outcsv(name,data,fields):
 with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data)

clean=[]
for a in links:
 r=json.loads(a['raw_attributes']);company=normalize_holder(a)
 nr={'target_id':a['target_id'],'state':a['state'],'name':a['name'],'tenure_layer':a['dataset'],
 'tenement_id':a['official_title_number'],'tenement_type':str(r.get('permittypeabbreviation') or r.get('TENEMENTTYPE') or r.get('tenementType') or r.get('type') or r.get('layer') or ''),
 'holder_company_candidate':company,'holder_role':'REGISTERED_TENEMENT_HOLDER_OR_APPLICANT','title_status':a['tenure_status_text'],'title_status_class':status(a),
 'relation':'OFFICIAL_POINT_IN_POLYGON','source_url':a['api_url'],'source_response_sha256':a['api_response_sha256'],
 'company_legal_identity_verified':'NO','developer_role_verified':'NO','project_identity_verified':'NO','review_decision':'PENDING_COMPANY_PROJECT_CROSSCHECK'}
 clean.append(nr)
cols=list(clean[0]);outcsv('official_tenement_holder_candidates.csv',clean,cols)
linksby=collections.defaultdict(list)
for l in clean:linksby[l['target_id']].append(l)
saby=collections.defaultdict(list)
for r in sa:saby[r['target_id']].append(r)
statusby={x['target_id']:x for x in audit}

cases=[
('Balranald Mineral Sands Project','NSW','Iluka Resources Limited','MINERAL_SANDS_WITH_REE_BEARING_MINERALS','https://www.nsw.gov.au/ministerial-releases/two-major-nsw-critical-minerals-projects-to-benefit-from-australia-first-royalty-deferral-scheme','NSW government official project and proponent; REE recovery role requires project-specific corroboration'),
('Copi Mineral Sands Project','NSW','RZ Resources Limited','REE_AS_SECONDARY_PROJECT_COMMODITY','https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects','NSW Resources lists Copi, RZ Resources, and REE as other commodity'),
('Doradilla Project','NSW','Sky Metals Limited','REE_AS_SECONDARY_PROJECT_COMMODITY','https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects','NSW Resources lists Doradilla Tin Project and REE other commodity; alias review'),
('Narraburra REE Project','NSW','Orbit Resources Limited','PRIMARY_REE','https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects','NSW Resources lists Narraburra REE Project as primary REE'),
('Donald Mineral Sands Project','VIC','The Donald Project Pty Ltd / Astron Corporation Ltd','REE_ASSOCIATED_MINERAL_SANDS','https://resources.vic.gov.au/landholders-and-community/key-site-updates/donald-mineral-sands-project','Victorian Resources confirms project and current licensee transfer (2024)'),
('Goschen Project','VIC','VHM Ltd','REE_AND_MINERAL_SANDS','https://resources.vic.gov.au/landholders-and-community/key-site-updates/goschen-rare-earths-and-mineral-sands-project','Victorian Resources verifies REE project, VHM and MIN007256'),
('Avonbank Project','VIC','WIM Resource Pty Ltd','REE_AND_MINERAL_SANDS','https://resources.vic.gov.au/about-us/news/mining-licence-granted-for-avonbank-project','Victorian Resources 6 October 2026 mining licence and REE development'),
('Fingerboards Project','VIC','Gippsland Critical Minerals Pty Ltd','REE_MINERAL_SANDS_RESOURCE_REVIEW','https://resources.vic.gov.au/landholders-and-community/key-site-updates/fingerboards-mineral-sands-project','Victorian Resources identifies company and retention titles RL2023/RL2026'),
('Wimmera (WIM100 & WIM50)','VIC','Iluka Resources','MINERAL_SANDS_REE_ROLE_REVIEW','https://resources.vic.gov.au/__data/assets/pdf_file/0010/1191844/fe17b69e802fb6308e5100ce9c62e30dfbc8624.pdf','Victorian government 2026 critical-minerals presentation lists Wimmera and Iluka'),
('Goschen Central Project','VIC','ACDC Metals','MINERAL_SANDS_REE_ROLE_REVIEW','https://resources.vic.gov.au/__data/assets/pdf_file/0010/1191844/fe17b69e802fb6308e5100ce9c62e30dfbc8624.pdf','Victorian government 2026 project list identifies Goschen Central and ACDC Metals'),
('Charley Creek','NT','Enova Mining Ltd','PRIMARY_REE','https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree','NT official rare earth project listing under feasibility'),
('Barkly','NT','Barkly Rare Earths Limited','PRIMARY_REE','https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree','NT official rare earth project listing under feasibility')]
legacy_index={x['name'].lower():x for x in raw if x['cohort']=='LEGACY_86'}
curated=[]
for name,st,company,material,url,note in cases:
 key=name.lower()
 if key not in legacy_index:continue
 t=legacy_index[key]
 curated.append({'target_id':t['target_id'],'project_name':name,'state':st,'official_company_reported':company,'ree_role_evidence':material,'evidence_category':'GOVERNMENT_PUBLISHED_PROJECT_COMPANY','government_evidence_url':url,'source_finding':note,'link_to_site_tenure':'NOT_REQUIRED_FOR_PROJECT_EXISTENCE','identity_decision':'REVIEW_NOT_AUTO_APPROVED'})
assert len(curated)>=10
outcsv('independent_government_project_company_evidence.csv',curated,list(curated[0]))
curby=collections.defaultdict(list)
for x in curated:curby[x['target_id']].append(x)
res=[]
for r in raw:
 id=r['target_id'];l=linksby[id];sa_links=saby[id];docs=curby[id];stat=statusby[id]
 c=[x for x in l if x['title_status_class'] in ('OFFICIAL_CURRENT','OFFICIAL_CURRENT_GRANTED_LAYER','OFFICIAL_CURRENT_OR_RETAINED')]
 holders=sorted({x['holder_company_candidate'] for x in c if x['holder_company_candidate']})
 allholders=sorted({x['holder_company_candidate'] for x in l if x['holder_company_candidate']})
 if docs:result='GOVERNMENT_PROJECT_AND_COMPANY_CANDIDATE'
 elif sa_links:result='SA_OFFICIAL_PROJECT_DEPOSIT_LINK_CANDIDATE'
 elif c:result='CURRENT_TENEMENT_HOLDER_CANDIDATE'
 elif l:result='HISTORIC_OR_PENDING_TENEMENT_HOLDER_CANDIDATE'
 elif stat['target_status']=='NO_USABLE_COORDINATES':result='LOCATION_NEEDED'
 elif stat['target_status']=='OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED':result='SA_TENEMENT_SOURCE_PENDING'
 elif stat['target_status']=='NO_OVERLAP_IN_QUERIED_LAYERS':result='NO_OFFICIAL_TENEMENT_INTERSECTION_ON_QUERY_DATE'
 else:result='SOURCE_OR_GEOMETRY_REVIEW'
 res.append({'target_id':id,'cohort':r['cohort'],'state':r['state'],'name':r['name'],'legacy_project_id':r['legacy_project_id'],'candidate_id':r['candidate_id'],
 'latitude':r['latitude'],'longitude':r['longitude'],'coordinates_basis':r['coordinates_basis'],'trace_outcome':result,
 'official_tenure_link_count':len(l),'official_current_tenure_count':len(c),'current_holder_candidates':' | '.join(holders),'any_status_holder_candidates':' | '.join(allholders),
 'sa_project_deposit_links':len(sa_links),'government_project_company_docs':len(docs),'official_link_urls':' | '.join(sorted({x['source_url'] for x in l}|{x['source_url'] for x in sa_links}|{x['government_evidence_url'] for x in docs})),
 'project_master_action':'NO_AUTO_MERGE_OR_INSERT','required_next_evidence':('DOCUMENT_APPROVAL_AND_REE_MATERIALITY' if docs or sa_links else 'COMPANY_ASX_REPORT_OR_TENEMENT_HISTORY_AND_PROJECT_SCOPE')})
outcsv('487_target_resolution_matrix.csv',res,list(res[0]))

summ={'source_run_artifact':'nationwide-487-tenement-company-reverse-trace','total_targets':487,'legacy_unmatched':86,'unlinked_E1':401,
 'official_intersected_target_count':len({x['target_id'] for x in clean}),'official_tenure_intersection_rows':len(clean),
 'strict_current_title_target_count':len({x['target_id'] for x in clean if x['title_status_class'] in ('OFFICIAL_CURRENT','OFFICIAL_CURRENT_GRANTED_LAYER','OFFICIAL_CURRENT_OR_RETAINED')}),
 'company_name_candidate_count':len({x['holder_company_candidate'].lower() for x in clean if x['holder_company_candidate']}),
 'sa_project_id_or_name_link_targets':sum(bool(x) for x in saby.values()),'government_project_evidence_targets':sum(bool(x) for x in curby.values()),
 'resolution_outcome':dict(collections.Counter(x['trace_outcome'] for x in res)),
 'state_outcomes':{st:{'legacy':sum(x['state']==st and x['cohort']=='LEGACY_86' for x in res),'e1_unlinked':sum(x['state']==st and x['cohort']=='UNLINKED_E1_401' for x in res),'tenure_hit':sum(x['state']==st and int(x['official_tenure_link_count'])>0 for x in res),'strict_current_tenure':sum(x['state']==st and int(x['official_current_tenure_count'])>0 for x in res),'official_sa_project':sum(x['state']==st and int(x['sa_project_deposit_links'])>0 for x in res),'government_company_project':sum(x['state']==st and int(x['government_project_company_docs'])>0 for x in res)} for st in ('WA','SA','QLD','NSW','VIC','NT','TAS')},
 'project_master_auto_approved_count':0,'source_hashes':{'tenement_zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'target_csv_sha256':hashlib.sha256(target_path.read_bytes()).hexdigest(),'sa_crosswalk_sha256':hashlib.sha256(sa_path.read_bytes()).hexdigest()}}
(out/'reverse_trace_final_summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'official_tenement_source_catalog.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
con=sqlite3.connect(out/'reverse_trace_review.sqlite')
for table,rows in [('targets_487',res),('title_holder_evidence',clean),('sa_project_deposit_links',sa),('government_project_company_evidence',curated)]:
 columns=list(rows[0]) if rows else []
 if not columns:continue
 con.execute('CREATE TABLE IF NOT EXISTS "'+table+'" ('+', '.join('"'+c+'" TEXT' for c in columns)+')')
 con.executemany('INSERT INTO "'+table+'" VALUES('+','.join('?' for _ in columns)+')',[[str(x.get(c,'')) for c in columns] for x in rows])
con.commit();assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok';con.close()
print(json.dumps(summ,ensure_ascii=False,indent=2))
