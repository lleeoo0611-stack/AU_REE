#!/usr/bin/env python3
"""Generate immutable target set: legacy86 + unlinked E1 401 (no duplicate auto-merges)."""
import csv, json, pathlib, hashlib
P=pathlib.Path('/mnt/data/AU_REE_Evidence_Back_1006_20261029')
OUT=pathlib.Path('/mnt/data/AU_REE_reverse_trace_20261029')

def read(name):
 with open(P/name,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

groups=read('provisional_project_groups_126.csv')
matched={s.strip() for x in groups for s in x['legacy_id_candidates'].split(';') if s.strip()}
legacy=read('legacy_203_crosswalk_audit.csv')
allrows=read('all_1006_evidence_decisions.csv')
e1=read('E1_project_unlinked_review_queue.csv')
assert len(legacy)==203 and len(groups)==126 and len(matched)==117 and len(e1)==401
names={}
def norm(s):return ''.join(x for x in str(s).lower() if x.isalnum())
for c in allrows:
 if c['tier']=='E1_DIRECT_REE':names.setdefault((c['state'],norm(c['name'])),[]).append(c)
rows=[]
for l in legacy:
 if l['project_id'] in matched:continue
 candidates=names.get((l['state'],norm(l['canonical_name'])),[])
 coords=[c for c in candidates if c.get('latitude') and c.get('longitude')]
 c=coords[0] if len(coords)==1 else None
 rows.append({'target_id':'LEGACY:'+l['project_id'],'cohort':'LEGACY_86','state':l['state'],
 'name':l['canonical_name'],'legacy_project_id':l['project_id'],'candidate_id':c['candidate_id'] if c else '',
 'source_key':c['source_key'] if c else '', 'source_native_id':c['native_id'] if c else '',
 'latitude':c['latitude'] if c else '', 'longitude':c['longitude'] if c else '',
 'coordinates_basis':'SAME_STATE_EXACT_E1_NAME_SINGLE_RECORD' if c else ('AMBIGUOUS_EXACT_NAME' if coords else 'NO_MATCHED_GEOLOGICAL_COORDINATE'),
 'historical_project_status':'LEGACY_UNVERIFIED','initial_project_link':'HISTORICAL_PROJECT_ONLY',
 'existing_operator':c.get('operator','') if c else '', 'parent_project_hint':c.get('parent_project_hint','') if c else ''})
for c in e1:
 rows.append({'target_id':'E1:'+c['candidate_id'],'cohort':'UNLINKED_E1_401','state':c['state'],
 'name':c['name'],'legacy_project_id':'','candidate_id':c['candidate_id'], 'source_key':c['source_key'],
 'source_native_id':c['native_id'],'latitude':c['latitude'],'longitude':c['longitude'],
 'coordinates_basis':'OFFICIAL_SOURCE_POINT_UNVERIFIED_GEOMETRY','historical_project_status':'',
 'initial_project_link':'NO_DIRECT_PARENT_PROJECT_KEY','existing_operator':c.get('operator',''), 'parent_project_hint':c.get('parent_project_hint','')})
assert len(rows)==487 and sum(x['cohort']=='LEGACY_86' for x in rows)==86 and sum(x['cohort']=='UNLINKED_E1_401' for x in rows)==401
fields=list(rows[0]);path=OUT/'reverse_trace_targets_487.csv'
with open(path,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
summary={'targets':len(rows),'legacy86':86,'unlinked_e1':401,'sources_with_coordinates':sum(bool(x['latitude'] and x['longitude']) for x in rows),'without_coordinates':sum(not (x['latitude'] and x['longitude']) for x in rows),
 'per_state':{s:{'legacy86':sum(x['state']==s and x['cohort']=='LEGACY_86' for x in rows),'unlinked_e1':sum(x['state']==s and x['cohort']=='UNLINKED_E1_401' for x in rows),'has_coordinates':sum(x['state']==s and bool(x['latitude'] and x['longitude']) for x in rows)} for s in ['WA','SA','QLD','NSW','VIC','NT','TAS']},'targets_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(OUT/'target_manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))