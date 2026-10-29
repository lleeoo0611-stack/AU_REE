#!/usr/bin/env python3
"""Rebuild a NON-verified nationwide REE review queue from immutable official GitHub artifact.

Usage: python rebuild_review_from_snapshot.py <round2_archive.zip> <output_folder>
Every source record remains linked to original source and geometry. Grouping proposes
candidate relationships; it is never a verified mining Project and never alters MCDA.
"""
from __future__ import annotations
import sys,csv,io,json,sqlite3,tempfile,zipfile,hashlib,re,math,collections
from pathlib import Path

DIRECT=re.compile(r'(?i)(?<![a-z])(?:rare[ -]?earths?|rare[ -]?earth[ -]?elements?|REE|REO|TREO|HREE|LREE|NdPr|neodymium|praseodymium|dysprosium|terbium|yttrium|lanthanum|cerium)(?![a-z])')
INDICATOR=re.compile(r'(?i)(?<![a-z])(?:monazite|xenotime|bastn[aä]site|bastnaesite|allanite)(?![a-z])')

def norm(s):
    s=str(s or '').strip().casefold()
    s=re.sub(r'[^a-z0-9 ]+',' ',s)
    s=re.sub(r'\s+',' ',s)
    return s.strip()

def classify(commodity, source, name=''):
    if source=='GA_AIMR_REE_2026':return 'OFFICIAL_REE_FILTERED'
    if DIRECT.search(str(commodity)):return 'EXPLICIT_REE_COMMODITY'
    if INDICATOR.search(str(commodity)) or INDICATOR.search(str(name)):return 'REE_BEARING_MINERAL_ONLY'
    return 'REE_ROLE_UNDETERMINED'

def load_rows(z,out):
    with tempfile.TemporaryDirectory() as d:
        dbp=Path(d)/'research.sqlite';dbp.write_bytes(z.read('work/research.sqlite'))
        conn=sqlite3.connect(dbp);conn.row_factory=sqlite3.Row
        rows=[]
        for r in conn.execute("SELECT candidate_id,source_key,native_id,raw_name,state,company,latitude,longitude,commodity_text,entity_level,decision,matched_project_id,reason,source_url,original_json FROM population_candidates WHERE decision='REVIEW' AND source_key!='legacy_r963_frozen'"):
            d=dict(r)
            raw=json.loads(d.pop('original_json') or '{}')
            attributes=raw.get('source_raw_attributes') or {}
            d['parent_code']=str(attributes.get('proj_code') or '')
            d['parent_name']=str(attributes.get('proj_title') or raw.get('project_name_hint') or '')
            d['screening_tier']=classify(d['commodity_text'],d['source_key'],d['raw_name'])
            d['raw_record_provenance']='OFFICIAL_ARCGIS_SNAPSHOT_UNVERIFIED'
            rows.append(d)
        return rows

def load_new_wfs(z):
    rows=[];counts={};provenance=[]
    for src in ('NSW_METINDEX','VIC_MINSITE','NT_MODAT_WFS'):
        manifest=json.loads(z.read(f'work/state_acquisition/{src}/manifest.json'))
        expected=manifest['raw_count'];seen=set();n=0;selected=0;duplicates=0
        for chunk in manifest['chunks']:
            key=f'work/state_acquisition/{src}/'+chunk['file']
            content=z.read(key)
            if hashlib.sha256(content).hexdigest()!=chunk['sha256']:
                raise RuntimeError('SHA256 mismatch: '+key)
            feats=json.loads(content)['features']
            if len(feats)!=chunk['rows']:raise RuntimeError('chunk count mismatch: '+key)
            for f in feats:
                a=f.get('properties') or {};n+=1
                def value(*keys):
                    lo={str(k).lower():v for k,v in a.items()}
                    for k in keys:
                        v=lo.get(k.lower())
                        if v is not None and str(v).strip():return str(v)
                    return ''
                name=value(*({'NSW_METINDEX':('deposit_name','all_names'),'VIC_MINSITE':('mine_name','field_name'),'NT_MODAT_WFS':('name',)}[src]))
                ident=value(*({'NSW_METINDEX':('occurrence_id',),'VIC_MINSITE':('siteid',),'NT_MODAT_WFS':('identifier',)}[src])) or str(f.get('id') or '')
                if not ident:raise RuntimeError(src+': no raw identity')
                if ident in seen:
                    duplicates+=1
                    continue
                seen.add(ident)
                if src=='NSW_METINDEX':
                    commodity='; '.join(value(t) for t in ('major_comm','minor_comm','ore_min','other_class','nsw_class','nsw_gen','summary_desc') if value(t))
                    lat=value('latgda94');lon=value('longda94')
                    parent='';company='';entity='OCCURRENCE'
                elif src=='VIC_MINSITE':
                    commodity='; '.join(value(t) for t in ('pri_comm','sec_comm','min_ass','prod_comm') if value(t))
                    lat=value('latitude');lon=value('longitude')
                    parent=value('project');company='';entity='MINE_SITE' if value('site_type')=='MINE' else 'OCCURRENCE'
                else:
                    commodity=value('commodity');lat=lon='';parent='';company='';entity='OCCURRENCE'
                    geo=f.get('geometry') or {}
                    c=geo.get('coordinates') or []
                    if geo.get('type')=='Point' and len(c)>=2:lon,lat=map(str,c[:2])
                tier=classify(commodity,src,name)
                if src=='NSW_METINDEX':
                    declared='; '.join(value(x) for x in ('major_comm','minor_comm'))
                    mineral='; '.join(value(x) for x in ('ore_min','gangue_min'))
                    if DIRECT.search(declared):tier='EXPLICIT_REE_COMMODITY'
                    elif INDICATOR.search(declared):tier='REE_BEARING_MINERAL_ONLY'
                    elif DIRECT.search(mineral) or INDICATOR.search(mineral):tier='REE_BEARING_MINERAL_ONLY'
                    elif tier!='REE_ROLE_UNDETERMINED':tier='GEOLOGICAL_CONTEXT_ONLY'
                elif src=='VIC_MINSITE':
                    declared='; '.join(value(x) for x in ('pri_comm','sec_comm','prod_comm'))
                    mineral=value('min_ass')
                    if DIRECT.search(declared):tier='EXPLICIT_REE_COMMODITY'
                    elif INDICATOR.search(declared) or INDICATOR.search(mineral):tier='REE_BEARING_MINERAL_ONLY'
                    elif tier!='REE_ROLE_UNDETERMINED':tier='NAME_OR_CONTEXT_ONLY'
                if tier=='REE_ROLE_UNDETERMINED':continue
                if not name:continue
                selected+=1
                rows.append({'candidate_id':'','source_key':src,'native_id':ident,'raw_name':name,'state':{'NSW_METINDEX':'NSW','VIC_MINSITE':'VIC','NT_MODAT_WFS':'NT'}[src],
                  'company':company,'latitude':lat,'longitude':lon,'commodity_text':commodity,'entity_level':entity,'decision':'REVIEW','matched_project_id':'',
                  'reason':'REE_COMMODITY_NEEDS_PROJECT_EVIDENCE' if tier=='EXPLICIT_REE_COMMODITY' else 'MINERAL_INDICATOR_NEEDS_REE_MATERIALITY','source_url':manifest['url'],
                  'parent_code':'','parent_name':parent,'screening_tier':tier,'raw_record_provenance':'OFFICIAL_WFS_SNAPSHOT_SHA256_CHECKED_UNVERIFIED'})
        if n!=expected:raise RuntimeError(f'{src}: expected {expected}, got {n}')
        counts[src]={'raw_features':n,'distinct_raw_ids':len(seen),'repeated_raw_ids':duplicates,'screened_candidates':selected,'sha256_manifest_verified':True}
    return rows,counts

def save_csv(path,rows,cols):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    archive=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(archive) as z:
        previous=load_rows(z,out)
        new,source_qa=load_new_wfs(z)
        all_rows=previous+new
        group=collections.Counter((r['state'],r['source_key']) for r in all_rows)
        tiers=collections.Counter(r['screening_tier'] for r in all_rows)
        # Candidate exact name/state groups are REVIEW suggestions, never forced merges.
        matched=collections.defaultdict(list)
        for r in all_rows:
            key=(r['state'],norm(r['raw_name']))
            if key[1]:matched[key].append(r)
        pairs=[]
        for (st,key),group_rows in matched.items():
            if len(set(r['source_key'] for r in group_rows))<2:continue
            for i,a in enumerate(group_rows):
                for b in group_rows[i+1:]:
                    if a['source_key']==b['source_key']:continue
                    pairs.append({'state':st,'normalized_name':key,'source_a':a['source_key'],'native_a':a['native_id'],'name_a':a['raw_name'],
                    'source_b':b['source_key'],'native_b':b['native_id'],'name_b':b['raw_name'],
                    'decision':'SUGGEST_SAME_GEOLOGICAL_ENTITY_NOT_PROJECT_MERGE','reviewer':'','evidence_ref':''})
        hierarchy=json.loads(z.read('work/project_hierarchy/hierarchy_count_audit.json'))
        header=['candidate_id','source_key','native_id','raw_name','state','company','latitude','longitude','entity_level','commodity_text','screening_tier',
            'decision','matched_project_id','parent_code','parent_name','reason','raw_record_provenance','source_url']
        save_csv(out/'nationwide_ree_candidate_review.csv',all_rows,header)
        save_csv(out/'cross_source_exact_name_state_review.csv',pairs,['state','normalized_name','source_a','native_a','name_a','source_b','native_b','name_b','decision','reviewer','evidence_ref'])
        source_rows=[{'state':st,'source':src,'candidate_count':n} for (st,src),n in sorted(group.items())]
        save_csv(out/'source_candidate_counts.csv',source_rows,['state','source','candidate_count'])
        save_csv(out/'screening_tier_counts.csv',[{'screening_tier':k,'records':v} for k,v in sorted(tiers.items())],['screening_tier','records'])
        report={'snapshot':'2026-10-29','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
          'existing_five_source_review_candidates':len(previous),'three_additional_states_screened':len(new),'total_candidate_records_not_unique_projects':len(all_rows),
          'source_qa':source_qa,'tier_counts':tiers,'per_state_source':source_rows,'cross_source_exact_pairs':len(pairs),
          'historical_project_master':hierarchy['frozen_project_master'], 'wa_parent_groups_provisional':hierarchy['WA_project_parent_groups'],
          'verified_distinct_project_count':None,'all_states_coverage':'PARTIAL_SA_PENDING',
          'cautions':['raw candidate counts are not unique deposits nor unique mining projects','mineral associations are not confirmed economic REE resource','do not promote to VERIFIED without independent source review']}
        (out/'national_review_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('source_qa','per_state_source')},ensure_ascii=False,indent=2,default=dict))
if __name__=='__main__':main()