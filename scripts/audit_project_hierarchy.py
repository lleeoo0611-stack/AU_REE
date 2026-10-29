#!/usr/bin/env python3
"""Hierarchy audit; propose relationships without promoting/merging projects."""
from __future__ import annotations
import csv,json,sqlite3,pathlib,re,collections,sys

def norm(s):return re.sub(r'[^a-z0-9]+','',str(s or '').lower())
def write(path,rows,keys):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
def main():
 db=sqlite3.connect(sys.argv[1] if len(sys.argv)>1 else 'work/research.sqlite');db.row_factory=sqlite3.Row
 out=pathlib.Path('work/project_hierarchy');out.mkdir(parents=True,exist_ok=True)
 master=[dict(x) for x in db.execute('SELECT project_id,canonical_name,state,operator_name,population_status FROM project_master')]
 index=collections.defaultdict(list)
 for p in master:index[(norm(p['canonical_name']),p['state'])].append(p['project_id'])
 wa_groups=collections.defaultdict(list);wa_uncoded=[];sa_projects=collections.defaultdict(list)
 rel=[];raw_counts=collections.Counter();record_stats=collections.Counter()
 for row in db.execute("SELECT candidate_id,source_key,raw_name,state,entity_level,decision,original_json FROM population_candidates WHERE source_key!='legacy_r963_frozen'"):
  x=dict(row);raw_counts[x['source_key']]+=1
  if x['decision']=='REVIEW':record_stats[x['source_key']]+=1
  try:attrs=json.loads(x['original_json'] or '{}').get('source_raw_attributes') or {}
  except (ValueError,TypeError):attrs={}
  source=x['source_key'];level=x['entity_level'];parent='';code='';status='UNASSIGNED'
  if source=='STATE_WA_MINDEX':
   code=str(attrs.get('proj_code') or '').strip();parent=str(attrs.get('proj_title') or '').strip()
   level=str(attrs.get('site_type_') or 'UNKNOWN').upper().replace(' ','_')
   if code and x['decision']=='REVIEW':wa_groups[(code,parent)].append(x['candidate_id']);status='OFFICIAL_PARENT_CODE'
   elif x['decision']=='REVIEW':wa_uncoded.append(x['candidate_id'])
  elif source=='STATE_SA_SARIG':
   # Stage 01 CSV adapter preserves immutable raw source layer in native_id.
   raw_id=attrs.get('native_id') or attrs.get('source_original_id') or ''
   if level=='PROJECT' and x['decision']!='EXCLUDED':
    parent=x['raw_name'];code=str(raw_id) or x['candidate_id'];sa_projects[(code,parent) if code else (parent,parent)].append(x['candidate_id']);status='GOVERNMENT_PROJECT_LAYER_UNREVIEWED'
  if x['decision']!='EXCLUDED':
   matched=index.get((norm(parent or x['raw_name']),x['state']),[])
   rel.append({'candidate_id':x['candidate_id'],'source_key':source,'name':x['raw_name'],'state':x['state'],
               'source_entity_level':level,'official_parent_code':code,'official_parent_name':parent,
               'matching_master_ids':';'.join(matched),'relationship_status':status,
               'review_action':('VERIFY_PART_OF_PROJECT' if status=='OFFICIAL_PARENT_CODE' else 'VERIFY_IDENTITY_AND_ROLE')})
 grouped=[]
 for (code,name),ids in sorted(wa_groups.items()):
  matches=index.get((norm(name),'WA'),[])
  grouped.append({'source':'WA_MINDEX','parent_code':code,'parent_name':name,'site_count':len(ids),
                  'existing_master_ids':';'.join(matches),'decision':'PROVISIONAL_PARENT_NO_AUTOMERGE',
                  'reviewer':'','reviewed_at':'','approved_evidence':''})
 for (code,name),ids in sorted(sa_projects.items()):
  matches=index.get((norm(name),'SA'),[])
  grouped.append({'source':'SA_SARIG_PROJECT_LAYER','parent_code':code,'parent_name':name,'site_count':len(ids),
                  'existing_master_ids':';'.join(matches),'decision':'GOVERNMENT_PROJECT_UNVERIFIED',
                  'reviewer':'','reviewed_at':'','approved_evidence':''})
 write(out/'source_entity_relations.csv',rel,['candidate_id','source_key','name','state','source_entity_level','official_parent_code','official_parent_name','matching_master_ids','relationship_status','review_action'])
 write(out/'provisional_parent_groups.csv',grouped,['source','parent_code','parent_name','site_count','existing_master_ids','decision','reviewer','reviewed_at','approved_evidence'])
 wc=[r for r in grouped if r['source']=='WA_MINDEX'];sc=[r for r in grouped if r['source']=='SA_SARIG_PROJECT_LAYER']
 matched_wa=sum(bool(r['existing_master_ids']) for r in wc)
 matched_sa=sum(bool(r['existing_master_ids']) for r in sc)
 report={'frozen_project_master':len(master),'new_official_records':sum(raw_counts.values()),'official_source_candidate_records':dict(raw_counts),
  'review_records_by_source':dict(record_stats),
  'WA_project_parent_groups':len(wc),'WA_sites_assigned_to_parent_groups':sum(r['site_count'] for r in wc),
  'WA_unassigned_ree_sites':len(wa_uncoded),'WA_parent_exact_match_existing_master':matched_wa,
  'WA_parent_unmatched_provisional_groups':len(wc)-matched_wa,
  'SA_project_source_groups':len(sc),'SA_project_exact_match_existing_master':matched_sa,
  'SA_project_unmatched_provisional_groups':len(sc)-matched_sa,
  'three_level_count_status':'PROVISIONAL_NOT_VERIFIED',
  'distinct_project_count_after_verified_dedup':None,
  'method_note':'Parent IDs group sites; geological entities are not independent projects; no manual review approvals in this run.'}
 (out/'hierarchy_count_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()