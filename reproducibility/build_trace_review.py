"""Replay frozen source searches, native-record checks and reviewed Project relations."""
import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

def read(p):
    with p.open(encoding='utf-8-sig', errors='replace', newline='') as f: return list(csv.DictReader(f))
def write(p, rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text_lines(d):
    return [(int(m[1]), int(m[2])+1 if m[2] else None, m[3]) for m in re.finditer(r'^L(\d+)(?:@P(\d+)(?:-\d+)?)?: ?(.*)$',d.get('text',''),re.M)]
def core_term(name):
    return re.split(r'\b(?:Project|REE|Rare Earths?|Mineral Sands|Uranium|phosphate)\b',name,flags=re.I)[0].strip(' -–').split('–')[0].strip()

def archive_index(root):
    entries=[]
    for folder in ['source_fetch','lead_fetch','followup_fetch']:
        for f in sorted((root/folder).glob('*.json')):
            d=json.loads(f.read_text(encoding='utf-8'));d['_path']=str(f);d['_sha']=sha(f);d['_lines']=text_lines(d);entries.append(d)
    return entries
def locate(d,term):
    normal=lambda v:re.sub(r'[^a-z0-9]+','',v.casefold())
    hits=[x for x in d['_lines'] if normal(term) and normal(term) in normal(x[2])]
    hits.sort(key=lambda x:(bool(re.search(r'rare earth|\bREE\b|owned|resource|located|licen|explor|develop',x[2],re.I)),len(x[2])>50),reverse=True)
    if not hits:return '', ''
    line,page,txt=hits[0];loc=(f'PDF page {page}; ' if page else 'HTML extract; ')+f'line {line}'
    return loc,' '.join(txt.split()[:20])

def apply(root):
    out=root/'deliverable'; research=root/'research_20261029'
    rows=read(out/'487_definition_review.csv'); before={r['target_id']:r.copy() for r in rows}
    baseline=json.loads((research/'targets_441.json').read_text());baseline_ids={r['target_id'] for r in baseline}
    projects=read(out/'project_candidate_evidence_review.csv');bykey={p['candidate_group_key']:p for p in projects}
    gate=read(out/'487_inclusion_gate.csv');gb={r['target_id']:r for r in gate}
    cases=json.loads((research/'reviewed_project_relations.json').read_text())
    changes=[]
    for case in cases:
        names={n.casefold() for n in case['names']};matched=[r for r in rows if r['target_id'] in baseline_ids and r['state']==case['state'] and r['name'].casefold() in names]
        if not matched:continue
        docs=[json.loads((research/f).read_text()) for f in case['sources']]
        available=[d for d in docs if text_lines(d)]
        if not available:raise ValueError('No retrieved source content for '+case['unit'])
        key=case['unit'];urls=';'.join(dict.fromkeys(d['url'] for d in available));ids=[]
        if key in bykey:ids=re.split(r'[;|]+',bykey[key]['target_ids_preserved'])
        ids=sorted({x.strip() for x in ids if x.strip()}|{r['target_id'] for r in matched})
        bykey[key]={**bykey.get(key,{}),'candidate_group_key':key,'canonical_project_unit':key,'target_ids_preserved':';'.join(ids),
                    'source_names':';'.join(sorted({r['name'] for r in matched})), 'state_or_states':case['state'],
                    'project_identity_status':'PASS_FORMAL_NAMED_UNIT','jurisdiction_status':'PASS_AU_FORMAL_SOURCE',
                    'location_status':'PASS_DISCLOSED_LOCALITY_BOUNDARY_PENDING','ree_role_status':'PASS_EXPLICIT_REE_TARGET_OR_PRODUCT',
                    'stage_status':'PASS_EXPLORATION_RESOURCE_OR_DEVELOPMENT','inclusion_gate':'INCLUDE_CANDIDATE',
                    'primary_source_urls':';'.join(dict.fromkeys((bykey.get(key,{}).get('primary_source_urls','')+';'+urls).split(';'))).strip(';'),
                    'evidence_assessment':case['rationale'],'dedup_decision':'SOURCE_REVIEWED_PROJECT_OR_CHILD_CANDIDATE; HUMAN_SIGNOFF_PENDING',
                    'company_name_transfer_and_interest_history':'SOURCE_EVENTS_RECORDED; COMPLETE_CURRENT_TITLE_CHAIN_PENDING',
                    'review_status':'FROZEN_SOURCE_CONTENT_REVIEWED; TARGET_BOUNDARY_AND_FINAL_SIGNOFF_PENDING','as_of_date':'2026-10-29'}
        for r in matched:
            tid=r['target_id'];r.update({'canonical_project_candidate_not_approved':key,'definition_screen_status':'PROJECT_CANDIDATE_REVIEW',
                'condition_1_jurisdiction':'PASS_AU_FORMAL_SOURCE','condition_2_location':'PASS_DISCLOSED_LOCALITY_BOUNDARY_PENDING',
                'condition_3_distinct_project':'PASS_FORMAL_NAMED_PROJECT_OR_EXPLICIT_CHILD','condition_4_ree_role':'PASS_EXPLICIT_REE_TARGET_OR_PRODUCT',
                'condition_5_project_lifecycle':'PASS_EXPLORATION_RESOURCE_OR_DEVELOPMENT','project_identity_check':'PASS_FORMAL_NAMED_PROJECT_OR_EXPLICIT_CHILD',
                'ree_role_check':'PASS_EXPLICIT_REE_TARGET_OR_PRODUCT','project_lifecycle_check':'PASS_EXPLORATION_RESOURCE_OR_DEVELOPMENT',
                'project_linkage_check':'SOURCE_SUPPORTED_CANDIDATE_TARGET_BOUNDARY_PENDING','project_evidence_url':urls,
                'source_evidence_note':case['rationale'],'whole_row_adjudication':'PROJECT_LEVEL_SOURCE_REVIEWED',
                'evidence_status':'PROJECT_DISCLOSURE_AND_NATIVE_SOURCE_REVIEWED; LEGAL_TITLE_CHAIN_PENDING',
                'project_dedup_group_candidate':key,'project_dedup_decision':'RETAIN_SOURCE_IDS; PROJECT_OR_CHILD_CANDIDATE; HUMAN_SIGNOFF_PENDING'})
            gb[tid].update({'candidate_group_key':key,'project_unit_status':'LINKED_TO_REVIEWED_PROJECT_CANDIDATE','inclusion_gate':'INCLUDE_CANDIDATE',
                            'dedup_relation':'SOURCE_SUPPORTED_CANDIDATE; BOUNDARY_AND_SIGNOFF_PENDING','decision_reason':case['rationale'],'primary_source_urls':urls})
            changes.append({'target_id':tid,'source_name':r['name'],'state':r['state'],'prior_disposition':before[tid]['definition_screen_status'],
                            'new_disposition':r['definition_screen_status'],'project_candidate':key,'evidence_files':';'.join(case['sources']),
                            'basis':case['rationale'],'final_admission':'PENDING_REVIEW_NOT_AUTOMATIC'})
    write(out/'487_definition_review.csv',rows);write(out/'487_full_census_adjudication.csv',rows)
    for filename in ['487_row_adjudication_latest_2026-10-29.csv','487_row_adjudication_compact.csv']:
        columns=list(read(out/filename)[0])
        write(out/filename,[{k:r.get(k,'') for k in columns} for r in rows])
    write(out/'project_candidate_evidence_review.csv',list(bykey.values()));write(out/'487_inclusion_gate.csv',gate)
    write(out/'review_queue.csv',[r for r in rows if r['definition_screen_status'].startswith('HOLD')])
    groups=defaultdict(list)
    for r in rows:
        if r.get('canonical_project_candidate_not_approved'):groups[r['canonical_project_candidate_not_approved']].append(r)
    write(out/'project_dedup_candidates.csv',[{'candidate_group_key':k,'canonical_project_candidate_not_approved':k,'candidate_observation_count':len(v),
             'target_ids_preserved':';'.join(x['target_id'] for x in v),'source_names':';'.join(sorted({x['name'] for x in v})),
             'states':';'.join(sorted({x['state'] for x in v})),'review_decision':'PENDING','open_review':'Confirm source-to-boundary identity and legal/company rights; retain original IDs.'} for k,v in groups.items()])
    write(out/'reviewed_project_relation_changes.csv',changes)
    summary=json.loads((out/'487_full_census_adjudication_summary.json').read_text());summary['status_counts']=dict(Counter(r['definition_screen_status'] for r in rows))
    summary['state_status_counts']={s:dict(Counter(r['definition_screen_status'] for r in rows if r['state']==s)) for s in sorted({r['state'] for r in rows})}
    summary['project_level_source_reviewed']=sum(r.get('whole_row_adjudication')=='PROJECT_LEVEL_SOURCE_REVIEWED' for r in rows)
    summary['new_case_groups_reviewed']=len(bykey)
    summary['additional_relation_cases_reviewed']=len(cases)
    summary['source_review_441_completed_pass']='Search and native-record trace performed; unresolved records remain HOLD; final legal title history incomplete.'
    (out/'487_full_census_adjudication_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'FULL_487_CENSUS_ADJUDICATION_2026-10-29.md').write_text('# Latest 487-row source-review state\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\nSee FULL_TRACE_REVIEW_20261030.md for scope and evidence limitations. Candidate groups and row counts are separate; no MCDA performed.\n')
    print(json.dumps({'reviewed_relation_rows':len(changes),'dispositions':summary['status_counts']}))

def audit(root):
    out=root/'deliverable'; research=root/'research_20261029'; archives=archive_index(research)
    byurl={d['url']:d for d in archives};baseline=read(research/'baseline_evidence_95.csv');project={p['entity_id']:p for p in read(out/'project_entity_register.csv')}
    reviews=[];seen=set(); excerpt_sources=set()
    for n,r in enumerate(baseline,1):
        d=byurl.get(r['source_url']);name=project.get(r['entity_id'],{}).get('canonical_name',''); term=core_term(name)
        loc,excerpt=locate(d,term) if d else ('',''); excerpt=excerpt if r['source_url'] not in excerpt_sources else 'See earlier row for this same source; locator preserved.'; excerpt_sources.add(r['source_url']); duplicate=r['evidence_id'] in seen;seen.add(r['evidence_id'])
        status='LOCATOR_FOUND_PROJECT_CONTEXT' if loc else ('RETRIEVED_NO_DIRECT_PROJECT_LOCATOR' if d and d['_lines'] else 'UNAVAILABLE_IN_BROWSER_EXTRACT')
        reviews.append({**r,'original_source_row':n,'duplicate_evidence_id':'YES' if duplicate else 'NO',
            'source_title':d['text'].splitlines()[0] if d else '', 'locator_page_or_section':loc,
            'evidence_excerpt_or_summary':excerpt,'review_status':status,'snapshot_file':str(Path(d['_path']).relative_to(root)).replace('\\','/') if d else '',
            'snapshot_sha256':d['_sha'] if d else '', 'locator_limit':'Browser extract line IDs are snapshot-specific; PDF page is physical page, not printed page.',
            'retrieval_time_utc':d.get('retrieved_utc','') if d else ''})
    assert len(reviews)==95;write(out/'source_evidence_locator_review_95.csv',reviews)
    # Enrich the active register too; preserve newly added source rows.
    active=read(out/'project_evidence_register.csv')
    for r in active:
        d=byurl.get(r['source_url']);nm=project.get(r['entity_id'],{}).get('canonical_name','');term=core_term(nm)
        loc,ex=locate(d,term) if d else ('',''); ex='Named-unit text located; use the cited snapshot locator and reviewed relation rationale.' if loc else '';r.update({'locator_page_or_section':loc,'evidence_excerpt_or_summary':ex,
            'review_status':'TEXT_LOCATED_FINAL_CLAIM_CHECK_PENDING' if loc else 'HOLD_NO_DIRECT_LOCATOR_OR_UNAVAILABLE','source_snapshot':str(Path(d['_path']).relative_to(root)).replace('\\','/') if d else ''})
    write(out/'project_evidence_register.csv',active)
    # Search audit: one query per normalised state/name, no name-only merge.
    searches={}
    for f in sorted((research/'target_search').glob('*.json')):
        d=json.loads(f.read_text());
        for q in d['queries']:searches[q['key']]={'query':q['q'],'archive':str(f.relative_to(root)).replace('\\','/'),'sha':sha(f)}
    raw={r['candidate_id']:r for r in read(root/'scheme_a_upstream/national_screening/nationwide_ree_candidates.csv')}
    current={r['target_id']:r for r in read(out/'487_row_adjudication_latest_2026-10-29.csv')};links=read(out/'487_official_tenure_intersection_evidence.csv');titles=defaultdict(list)
    for r in links:titles[r['target_id']].append(r)
    leads=json.loads((research/'primary_leads_screened.json').read_text());leadmap={r['query_key']:r for r in leads}
    features_cache={};trace=[];native_records=[]
    for t in json.loads((research/'targets_441.json').read_text()):
        tid=t['target_id'];r=current[tid];key=t['state']+'|'+t['name'].strip().lower();search=searches.get(key)
        if not search:raise ValueError('Missing search for '+tid)
        original=raw.get(t.get('candidate_id',''));path=root/'national_raw_upstream/national_raw'/original['source_record_ref'] if original else None
        locator='';count=0;hash_='';native=original.get('native_id','') if original else ''
        if path and path.is_file():
            if path not in features_cache:
                data=json.loads(path.read_text()) if path.suffix=='.json' else read(path)
                fs=data.get('features',[]) if isinstance(data,dict) else data;features_cache[path]=(sha(path),fs)
            hash_,fs=features_cache[path]
            matches=[]
            id_fields={'GA_AIMR_REE_2026':'entity_id','GA_CRITICAL_DEPOSITS_2025':'objectid','NSW_METINDEX':'occurrence_id','NT_MODAT_WFS':'identifier','VIC_MINSITE':'siteid','STATE_TAS_MRT':'DEPOSIT_ID','STATE_WA_MINDEX':'site_code','STATE_QLD_MINOCC':'site_no','SA_GEODATA_MINDEP':'MINERAL_DEPOSIT_NO','SA_CRITICAL_REE':'MINERAL_DEPOSIT_NO'}
            id_field=id_fields.get(original['source_key'])
            if not id_field:raise ValueError('Unknown native identifier schema: '+original['source_key'])
            for ix,f in enumerate(fs):
                attrs=f.get('attributes',f.get('properties',f))
                if native and str(attrs.get(id_field,'')).strip()==native:matches.append((ix,attrs))
            count=len(matches);locator=';'.join(('features/' if path.suffix=='.json' else 'CSV data row ')+str(i if path.suffix=='.json' else i+1) for i,a in matches)
            for ix,a in matches:native_records.append({'target_id':tid,'snapshot':str(path.relative_to(root)).replace('\\','/'),'record_index':ix,'native_id':native,'attributes':a})
        lead=leadmap.get(key,{});fetch=byurl.get(lead.get('source_url',''));loc,ex=locate(fetch,t['name'].replace(' Project','')) if fetch else ('','')
        trace.append({'target_id':tid,'state':t['state'],'original_name':t['name'],'source_key':t.get('source_key',''),'native_id':native,
            'native_snapshot':str(path.relative_to(root)).replace('\\','/') if path and path.is_file() else '', 'native_snapshot_sha256':hash_,
            'native_record_locator':locator,'native_record_matches':count,'native_identity_status':'EXACT_NATIVE_VALUE_MATCH' if count==1 else ('AMBIGUOUS_NATIVE_MATCH' if count>1 else 'MISSING_OR_NOT_RECOVERED'),
            'search_query':search['query'],'search_archive':search['archive'],'search_sha256':search['sha'],
            'additional_source_url':lead.get('source_url',''),'additional_source_locator':loc,
            'additional_source_status':'TEXT_LOCATION_CANDIDATE_REQUIRES_IDENTITY_CHECK' if loc else 'NO_CONFIRMED_PROJECT_RELATION_FROM_SEARCH_ALONE',
            **{f'condition_{i}':r.get(k,'') for i,k in enumerate(['condition_1_jurisdiction','condition_2_location','condition_3_distinct_project','condition_4_ree_role','condition_5_project_lifecycle'],1)},
            'project_candidate':r.get('canonical_project_candidate_not_approved',''),'disposition':r['definition_screen_status'],
            'title_observation_count':len(titles[tid]),'company_rights_review':'SOURCE_OBSERVATIONS_ONLY_CURRENT_TITLE_CHAIN_NOT_PROVEN',
            'dedup_review':'EXACT_SOURCE_IDS_RETAINED_NO_NAME_ONLY_MERGE','remaining_gap':'Confirm target geometry, distinct unit and effective-dated rights; missing evidence stays HOLD.'})
    assert len(trace)==441 and len({r['target_id'] for r in trace})==441
    write(out/'unlinked_441_source_trace.csv',trace)
    (research/'native_record_evidence.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in native_records))
    # Retain title observations separately from company/operator assertions.
    history=[]
    for d in archives:
        for line,page,txt in d['_lines']:
            if re.search(r'acquir|renam|formerly|subsidiar|joint venture|participating interest|holder|ownership|owned|tenement',txt,re.I):
                history.append({'source_url':d['url'],'locator':('PDF page '+str(page)+'; ' if page else '')+'line '+str(line),
                    'observed_statement':'Ownership, transaction or tenure wording found; actor, event and effective date require review at the cited locator.','scope':'DISCLOSED_EVENT_OR_ROLE_NOT_COMPLETE_LEGAL_CHAIN','archive':str(Path(d['_path']).relative_to(root)).replace('\\','/')})
    history=list({(r['source_url'],r['locator'],r['observed_statement']):r for r in history}.values())
    write(out/'company_tenure_disclosure_observations.csv',history)
    write(out/'reviewed_company_rights_events.csv',json.loads((research/'reviewed_company_events.json').read_text()))
    rights=[]
    for pid,p in project.items():
        source_urls={r['source_url'] for r in active if r['entity_id']==pid}
        observed=[h for h in history if h['source_url'] in source_urls]
        rights.append({'project_entity_id':pid,'project_candidate':p['canonical_name'],'source_statement_count':len(observed),'registered_titleholder':'NOT_VERIFIED','operator_proponent':'DISCLOSURE_OBSERVATIONS_SEPARATE_FROM_TITLE','history_review':'PARTIAL_DISCLOSED_EVENTS_ONLY','current_legal_chain':'HOLD_INCOMPLETE','evidence_locators':';'.join(h['archive']+' '+h['locator'] for h in observed[:4]),'required_next_evidence':'Effective-dated registry extract and transaction-completion/rename evidence; original source rows preserved.'})
    write(out/'project_rights_history_review.csv',rights)
    grouped=defaultdict(list)
    for r in trace:
        if r['native_id']:grouped[(r['state'],r['source_key'],r['native_id'])].append(r['target_id'])
    duplicates=[{'state':k[0],'source_key':k[1],'native_id':k[2],'target_ids':';'.join(v),'basis':'EXACT_NATIVE_SOURCE_RECORD_DUPLICATE_ONLY_NOT_PROJECT_MERGE'} for k,v in grouped.items() if len(v)>1]
    write(out/'native_source_duplicate_review.csv',duplicates or [{'state':'','source_key':'','native_id':'','target_ids':'','basis':'NO_REPEATED_SAME_SOURCE_NATIVE_ID_IN_441'}])
    summary={'baseline_unlinked_rows':441,'search_groups':len(searches),'rows_traced':len(trace),'original_evidence_rows':95,'unique_original_urls':len({r['source_url'] for r in baseline}),
             'locator_statuses':dict(Counter(r['review_status'] for r in reviews)),'duplicate_evidence_rows':sum(r['duplicate_evidence_id']=='YES' for r in reviews),
             'native_trace_statuses':dict(Counter(r['native_identity_status'] for r in trace)),'company_tenure_statement_rows':len(history),
             'trace_dispositions':dict(Counter(r['disposition'] for r in trace)),'scope':'All baseline targets searched and native references checked. Candidate relation review is provisional; inaccessible sources and incomplete rights chains remain HOLD/open, not verified absent.'}
    quality=read(out/'quality_gate_487.csv')
    for q in quality:
        if q['check_id']=='EVIDENCE_ROWS_NEEDING_LOCATOR_REVIEW':q['count']=sum(not r['locator_page_or_section'] for r in active)
    write(out/'quality_gate_487.csv',quality)
    qs=json.loads((out/'quality_gate_487_summary.json').read_text());qs['quality_checks']=quality;qs['source_locator_review_95']=summary['locator_statuses'];qs['research_baseline_441_rows_traced']=441
    (out/'quality_gate_487_summary.json').write_text(json.dumps(qs,indent=2)+'\n')
    manifest=json.loads((out/'census_review_manifest.json').read_text());manifest.update({'definition_status_counts':qs['dispositions'],'project_candidate_groups_not_approved':qs['project_entity_candidates'],'review_queue_rows':sum(v for k,v in qs['dispositions'].items() if k.startswith('HOLD')),'latest_linked_rows':qs['targets_with_project_link'],'latest_unlinked_rows':qs['targets_without_project_link'],'source_review_441':summary})
    (out/'census_review_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'trace_research_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--stage',choices=['apply','audit'],required=True);a=p.parse_args()
    (apply if a.stage=='apply' else audit)(Path(a.root).resolve())
