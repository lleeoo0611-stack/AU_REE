#!/usr/bin/env python3
"""Import audited 86+401 reverse traces to pipeline SQLite, without modifying Project Master.

python scripts/import_reverse_evidence.py --db work/research.sqlite \
 --folder /path/to/editable_review/outputs --sa /path/to/sa_official_project_deposit_crosswalk.csv
"""
import argparse,csv,sqlite3,hashlib,json,pathlib

def rows(f):
 with f.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def h(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def import_rows(db, folder, sa, migration):
 targets=rows(folder/'487_target_resolution_matrix.csv');holders=rows(folder/'official_tenement_holder_candidates.csv');documents=rows(folder/'independent_government_project_company_evidence.csv');sa_docs=rows(sa)
 assert len(targets)==487 and len(set(x['target_id'] for x in targets))==487
 assert sum(x['cohort']=='LEGACY_86' for x in targets)==86
 assert sum(x['cohort']=='UNLINKED_E1_401' for x in targets)==401
 before=db.execute('SELECT count(*) FROM project_master').fetchone()[0] if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='project_master'").fetchone() else None
 db.executescript(migration.read_text(encoding='utf8'))
 for t in targets:
  args=(t['target_id'],t['cohort'],t['state'],t['name'],t['legacy_project_id'] or None,t['candidate_id'] or None,float(t['latitude']) if t['latitude'] else None,float(t['longitude']) if t['longitude'] else None,t['coordinates_basis'],t['trace_outcome'])
  db.execute('INSERT INTO reverse_trace_targets (target_id,cohort,state,record_name,legacy_project_id,source_candidate_id,latitude,longitude,coordinate_basis,trace_outcome) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(target_id) DO UPDATE SET trace_outcome=excluded.trace_outcome, latitude=excluded.latitude,longitude=excluded.longitude',args)
 for t in holders:
  eid=h('|'.join([t['target_id'],t['tenure_layer'],t['tenement_id'],t['source_response_sha256'],t['holder_company_candidate']]))
  db.execute('INSERT OR REPLACE INTO reverse_tenement_observations (evidence_id,target_id,source_layer,tenement_number,title_type,title_status,status_class,registered_holder_text,source_url,source_response_sha256) VALUES (?,?,?,?,?,?,?,?,?,?)',
   (eid,t['target_id'],t['tenure_layer'],t['tenement_id'],t['tenement_type'],t['title_status'],t['title_status_class'],t['holder_company_candidate'],t['source_url'],t['source_response_sha256']))
 for t in documents:
  eid=h(t['target_id']+'|'+t['government_evidence_url'])
  db.execute('INSERT OR REPLACE INTO reverse_project_document_evidence (evidence_id,target_id,evidence_type,project_name,source_company_text,ree_materiality_status,official_source_url,identity_decision) VALUES (?,?,?,?,?,?,?,?)',
  (eid,t['target_id'],'GOVERNMENT_WEB_PROJECT_LISTING',t['project_name'],t['official_company_reported'],t['ree_role_evidence'],t['government_evidence_url'],t['identity_decision']))
 for t in sa_docs:
  eid=h(t['target_id']+'|SA|'+t['deposit_number']+'|'+t['project_name'])
  db.execute('INSERT OR REPLACE INTO reverse_project_document_evidence (evidence_id,target_id,evidence_type,project_name,source_company_text,ree_materiality_status,official_source_url,identity_decision) VALUES (?,?,?,?,?,?,?,?)',
  (eid,t['target_id'],'SA_OFFICIAL_DEPOSIT_PROJECT_ID' if t['match_basis']=='DEPOSIT_NATIVE_ID' else 'SA_OFFICIAL_PROJECT_EXACT_DEPOSIT_NAME',t['project_name'],t['company_text'],t['ree_materiality_in_project_commodity'],t['source_url'],'REVIEW_REQUIRED'))
 digest=h('|'.join(filehash(folder/x) for x in ['487_target_resolution_matrix.csv','official_tenement_holder_candidates.csv','independent_government_project_company_evidence.csv'])+'|'+filehash(sa))
 db.execute('INSERT OR REPLACE INTO reverse_trace_snapshots VALUES (?,?,?,?,?,0)',('2026-10-29_487', '2026-10-29_GH_Actions_tenement_reverse',filehash(folder/'487_target_resolution_matrix.csv'),digest,'2026-10-29'))
 db.commit()
 after=db.execute('SELECT count(*) FROM project_master').fetchone()[0] if before is not None else None
 assert before==after and db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 return {'targets':len(targets),'holder_links':len(holders),'government_docs':len(documents),'sa_project_deposit_links':len(sa_docs),'project_master_before':before,'project_master_after':after,'integrity_check':'ok'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--db',required=True,type=pathlib.Path);p.add_argument('--folder',required=True,type=pathlib.Path);p.add_argument('--sa',required=True,type=pathlib.Path);p.add_argument('--migration',type=pathlib.Path,default=pathlib.Path('db/migrations/0005_reverse_tenement.sql'));a=p.parse_args()
 with sqlite3.connect(a.db) as db:
  db.execute('PRAGMA foreign_keys=ON')
  print(json.dumps(import_rows(db,a.folder,a.sa,a.migration),ensure_ascii=False,indent=2))
