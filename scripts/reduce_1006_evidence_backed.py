#!/usr/bin/env python3
"""Reproducible conservative evidence-backed REE development project audit.

Reads the FROZEN national 1006-candidate/123323-raw official snapshots.
Produces identity-review layers. Does NOT certify company roles, convert all
WA parent groups into projects or overwrite the legacy Project Master.
"""
from __future__ import annotations
import csv,io,zipfile,json,hashlib,re,collections,sqlite3,sys,pathlib

def norm(s):
    return re.sub(r'[^a-z0-9]+','',str(s or '').casefold())
def decode_csv(z,p):
    return list(csv.DictReader(io.StringIO(z.read(p).decode('utf-8-sig',errors='replace'))))
def write_csv(folder,name,data,columns):
    with (folder/name).open('w',encoding='utf-8-sig',newline='') as o:
        w=csv.DictWriter(o,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(data)
def read_records(rawzip,candidates):
    refs={r['source_record_ref'] for r in candidates if r['source_key']=='STATE_WA_MINDEX'}
    code_set={r['native_id'] for r in candidates if r['source_key']=='STATE_WA_MINDEX'}
    by_code={}
    for f in sorted(refs):
        obj=json.loads(rawzip.read('national_raw/'+f))
        for feat in obj.get('features',[]):
            a=feat.get('attributes') or {}
            key=str(a.get('site_code') or '')
            if key in code_set:
                by_code[key]=a
    return by_code

# Curated independent government project identity links, not a blanket approval.
CURATED=[
    dict(project='Koppamurra',state='SA',developer='Australian Rare Earths Ltd (AR3)',match_token='koppamurra',match='exact_name_or_sa_project',
         evidence_url='https://www.energymining.sa.gov.au/industry/minerals-and-mining/mining/major-projects-and-mining-activities/developing-projects/the-koppamurra-project',
         evidence_kind='Official SA developing project',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
    dict(project='Wudinna',state='SA',developer='Cobra Resources Plc / Andromeda Metals Limited (raw SA project layer)',match_token='wudinna',match='exact_name_or_sa_project',
         evidence_url='sa_projects/SA_PROJECT_DEVELOPING.csv',
         evidence_kind='Frozen government WFS project record',evidence_status='OFFICIAL_PROJECT_REE_LISTED_PROJECT_ROLE_REVIEW'),
    dict(project='Yangibana',state='WA',developer='Official EPA proponent, time-dependent (Wyloo Gascoyne Pty Ltd on retrieved page)',match_token='yangibana',match='WA_parent_or_exact_name',
         evidence_url='https://www.epa.wa.gov.au/en/proposals/yangibana-rare-earths-project',
         evidence_kind='WA EPA development proposal',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
    dict(project='Browns Range',state='WA',developer='Northern Minerals Limited (WA EPA)',match_token='brownsrange',match='WA_parent_or_exact_name',
         evidence_url='https://www.epa.wa.gov.au/en/proposals/browns-range-rare-earth-project',
         evidence_kind='WA EPA development proposal',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
    dict(project='Mt Weld REE',state='WA',developer='Mt Weld Mining Pty Limited (WA EPA)',match_token='mtweld',match='WA_parent_or_exact_name',
         evidence_url='https://epa.wa.gov.au/proposals/mt-weld-rare-earths-project-life-mine-proposal',
         evidence_kind='WA EPA development proposal',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
    dict(project='Nolans',state='NT',developer='Arafura Rare Earths Ltd (NT government)',match_token='nolans',match='GA_name_nolans_bore',
         evidence_url='https://resourcingtheterritory.nt.gov.au/minerals/mines-and-projects/developing-projects',
         evidence_kind='NT government developing projects',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
    dict(project='Dubbo',state='NSW',developer='See NSW Resources current project register (time-dependent)',match_token='dubboproject',match='NSW_name',
         evidence_url='https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects',
         evidence_kind='NSW Resources development project listing',evidence_status='PROJECT_ID_AND_REE_ROLE_EXTERNALLY_SUPPORTED'),
]

def main(screenzip,rawzip,legacyzip,folder):
    folder.mkdir(exist_ok=True,parents=True)
    s=zipfile.ZipFile(screenzip);raw=zipfile.ZipFile(rawzip);old=zipfile.ZipFile(legacyzip)
    src='national_screening/nationwide_ree_candidates.csv'
    cand=decode_csv(s,src)
    assert len(cand)==1006, len(cand)
    lfile=next(x for x in old.namelist() if x.endswith('/inputs/legacy_r963_census.csv'))
    legacy=decode_csv(old,lfile)
    assert len(legacy)==203
    old_index=collections.defaultdict(list)
    for l in legacy:old_index[(l['state'],norm(l['canonical_name']))].append(l['project_id'])
    wa_attrs=read_records(raw,cand)
    group=collections.defaultdict(list)
    official_project_rows=[];queue=[];all_records=[]
    summary_groups=collections.Counter();county=collections.Counter()
    candidate_ids=set()
    for r in cand:
        r=r.copy();cid=r['candidate_id'];assert cid not in candidate_ids;candidate_ids.add(cid)
        tier=r['tier']; sk=r['source_key'];state=r['state'];county[(state,tier)]+=1
        attrs=wa_attrs.get(r['native_id'],{}) if sk=='STATE_WA_MINDEX' else {}
        pc=str(attrs.get('proj_code') or '').strip()
        pn=str(attrs.get('proj_title') or r.get('parent_project_hint') or '').strip()
        if sk=='VIC_MINSITE':pn=''  # VIC project field = database provenance, not mining project
        stage=str(attrs.get('site_stage') or '').strip()
        subtype=str(attrs.get('site_type_') or '').strip()
        old_exact=old_index.get((state,norm(r['name'])),[])
        old_parent=old_index.get((state,norm(pn)),[]) if pc else []
        r.update(wa_project_code=pc if sk=='STATE_WA_MINDEX' else '',wa_site_stage=stage,wa_site_type=subtype,
                 legacy_exact_ids=';'.join(old_exact),legacy_parent_ids=';'.join(old_parent))
        if tier!='E1_DIRECT_REE':
            r['decision']='EXTENDED_GEOLOGICAL_INVENTORY';r['project_evidence']='MINERAL_OR_CONTEXT_ONLY'
        elif sk in ('SA_PROJECT_DEVELOPING','SA_PROJECT_MAJOR') and r['entity_level'].upper()=='PROJECT' and r['operator']:
            r['decision']='GOVERNMENT_NAMED_PROJECT';r['project_evidence']='GOVERNMENT_PROJECT_LAYER_COMPANY_REE_COMMODITY'
            official_project_rows.append(r)
        elif sk=='STATE_WA_MINDEX' and pc and pn:
            r['decision']='OFFICIAL_PARENT_PROJECT_CANDIDATE';r['project_evidence']='WA_MINDEX_PROJECT_CODE_ONLY_NO_COMPANY_IN_THIS_LAYER'
            group[(pc,pn)].append(r)
        else:
            r['decision']='E1_MISSING_PROJECT_LINK';r['project_evidence']='REE_SOURCE_RECORD_ONLY'
            queue.append(r)
        # Independent checks are examples; do not equate records to projects.
        linked=[]
        for e in CURATED:
            if state!=e['state']:continue
            n=norm(r['name']);pnorm=norm(pn)
            token=e['match_token']
            if e['project']=='Mt Weld REE':hit=(('mtweld' in pnorm and 'lynas' in pnorm) or n=='mountweld')
            elif e['project']=='Nolans':hit=(n=='nolansbore')
            elif e['project']=='Dubbo':hit=(n=='dubboproject')
            elif e['project']=='Browns Range':hit=('brownsrange' in pnorm or n=='brownsrange')
            elif e['project']=='Yangibana':hit=('yangibana' in pnorm or n=='yangibana')
            else:hit=n==token or pnorm==token
            if hit:linked.append(e['project'])
        r['external_verified_example_project']=';'.join(linked)
        summary_groups[r['decision']]+=1
        r['audit_status']='NOT_AUTOMATICALLY_ADDED_TO_PROJECT_MASTER'
        # preserve updated candidate list for export
        all_records.append(r)
    # Rebuild queues from final enriched objects; avoid mutating when iterating.
    queue=[r for r in all_records if r['decision']=='E1_MISSING_PROJECT_LINK']
    g_rows=[]
    for (code,title),items in sorted(group.items()):
        oldids=old_index.get(('WA',norm(title)),[])
        stages=collections.Counter(i['wa_site_stage'] for i in items)
        types=collections.Counter(i['wa_site_type'] for i in items)
        g_rows.append({'wa_project_code':code,'project_title':title,'source_site_count':len(items),
          'legacy_exact_ids':';'.join(oldids),'legacy_match_count':len(oldids),'examples':'; '.join(i['name'] for i in items[:4]),
          'site_stages':json.dumps(stages,ensure_ascii=False),'site_types':json.dumps(types,ensure_ascii=False),
          'group_evidence_status':'OFFICIAL_GROUPING_ONLY','company_evidence_status':'NOT_IN_SITE_LAYER',
          'decision':'REQUIRES_REE_PROJECT_DEVELOPMENT_EVIDENCE'})
    l_rows=[]
    for x in legacy:
        related=[r for r in all_records if x['project_id'] in (r['legacy_exact_ids']+';'+r['legacy_parent_ids']).split(';')]
        l_rows.append({**x,'matched_1006_source_records':len(related),'source_keys':';'.join(sorted(set(r['source_key'] for r in related))),
                       'identity_status':'LEGACY_UNVERIFIED','matching_basis':'EXACT_NORMALISED_NAME_OR_WA_PARENT',
                       'evidence_backed_status':'NEEDS_INDEPENDENT_DEVELOPER_PROJECT_EVIDENCE'})
    ex=[]
    for e in CURATED:
        related=[r for r in all_records if e['project'] in (r['external_verified_example_project'].split(';'))]
        ex.append({**e,'candidate_source_records_matched':len(related),'candidate_names':'; '.join(sorted(set(x['name'] for x in related))[:10]),
         'official_project_source_names':';'.join(sorted(set(x['source_key'] for x in related))),
         'review_note':'Source supports project identity/REE goal; current company and stage require dated records and independent audit before MCDA'})
    by_state=[]
    for st in ['WA','SA','NSW','VIC','QLD','NT','TAS']:
        rr=[r for r in all_records if r['state']==st]
        by_state.append({'state':st,'total_source_records':len(rr),'E1_source_records':sum(r['tier']=='E1_DIRECT_REE' for r in rr),
          'E2_E3_extended':sum(r['tier']!='E1_DIRECT_REE' for r in rr),'government_named_project_records':sum(r['decision']=='GOVERNMENT_NAMED_PROJECT' for r in rr),
          'wa_official_parent_site_records':sum(r['decision']=='OFFICIAL_PARENT_PROJECT_CANDIDATE' for r in rr),
          'E1_without_project_relation':sum(r['decision']=='E1_MISSING_PROJECT_LINK' for r in rr),
          'distinct_WA_official_parent_groups':len({r['wa_project_code'] for r in rr if r['wa_project_code']}),
          'curated_government_project_examples':sum(e['state']==st for e in CURATED)})
    assert sum(x['total_source_records'] for x in by_state)==1006
    assert sum(x['E1_source_records'] for x in by_state)==803
    assert len(official_project_rows)==3
    assert sum(x['wa_official_parent_site_records'] for x in by_state)==399
    assert sum(x['E1_without_project_relation'] for x in by_state)==401
    summary={'source_snapshot_screen_count':1006,'E1_records':803,'E2E3_extended_records':203,
             'SA_official_project_records':3,'SA_project_direct_ree_or_separate_resource':2,'SA_project_ree_materiality_review':1,
             'WA_official_parent_site_records':399,'WA_official_parent_groups':len(g_rows),
             'E1_unlinked_source_records':401,'curated_example_project_count':len(ex),'legacy_frozen_count':203,
             'legacy_exact_or_parent_matched_ids':sum(x['matched_1006_source_records']>0 for x in l_rows),
             'legacy_without_exact_or_parent_match_ids':sum(x['matched_1006_source_records']==0 for x in l_rows),
             'project_master_promotions_performed':0,
             'counting_note':'All numbers are source-records except parent groups/curated projects/legacy IDs. Distinct nationwide evidence-backed project count cannot be inferred from these feeds alone.',
             'sources':{'raw_sha256':hashlib.sha256(pathlib.Path(rawzip).read_bytes()).hexdigest(),
                        'screen_sha256':hashlib.sha256(pathlib.Path(screenzip).read_bytes()).hexdigest(),
                        'legacy_sha256':hashlib.sha256(pathlib.Path(legacyzip).read_bytes()).hexdigest()}}
    common=['candidate_id','source_key','native_id','name','state','entity_level','tier','commodity_text','mineral_text','context_excerpt','parent_project_hint','latitude','longitude','operator','source_record_ref','review_status','wa_project_code','wa_site_stage','wa_site_type','legacy_exact_ids','legacy_parent_ids','decision','project_evidence','external_verified_example_project','audit_status']
    write_csv(folder,'all_1006_evidence_decisions.csv',all_records,common)
    write_csv(folder,'E1_project_unlinked_review_queue.csv',queue,common)
    write_csv(folder,'WA_121_official_parent_group_candidates.csv',g_rows,['wa_project_code','project_title','source_site_count','legacy_exact_ids','legacy_match_count','examples','site_stages','site_types','group_evidence_status','company_evidence_status','decision'])
    write_csv(folder,'SA_3_official_project_records.csv',official_project_rows,common)
    write_csv(folder,'legacy_203_crosswalk_audit.csv',l_rows,list(l_rows[0]))
    write_csv(folder,'independently_checked_project_examples.csv',ex,list(ex[0]))
    write_csv(folder,'state_screen_reduction.csv',by_state,list(by_state[0]))
    (folder/'evidence_backed_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    (folder/'evidence_backed_review.sqlite').unlink(missing_ok=True)
    db=sqlite3.connect(folder/'evidence_backed_review.sqlite')
    db.execute('create table candidate_audit(candidate_id text primary key,state text,source_key text,name text,tier text,decision text,wa_project_code text,linked_checked_project text,legacy_exact_ids text,source_record_ref text)')
    db.executemany('insert into candidate_audit values (?,?,?,?,?,?,?,?,?,?)',[(r['candidate_id'],r['state'],r['source_key'],r['name'],r['tier'],r['decision'],r['wa_project_code'],r['external_verified_example_project'],r['legacy_exact_ids'],r['source_record_ref']) for r in all_records])
    db.execute('create table wa_project_parent_group(wa_project_code text primary key,project_title text,site_count integer,legacy_exact_ids text,evidence_status text)')
    db.executemany('insert into wa_project_parent_group values(?,?,?,?,?)',[(r['wa_project_code'],r['project_title'],r['source_site_count'],r['legacy_exact_ids'],r['group_evidence_status']) for r in g_rows])
    db.execute('create table official_project_examples(project text primary key,state text,developer text,evidence_url text,evidence_status text,matched_source_records integer)')
    db.executemany('insert into official_project_examples values(?,?,?,?,?,?)',[(e['project'],e['state'],e['developer'],e['evidence_url'],e['evidence_status'],e['candidate_source_records_matched']) for e in ex])
    db.execute('create table legacy_crosswalk(legacy_project_id text primary key,name text,state text,source_match_count integer,verification text)')
    db.executemany('insert into legacy_crosswalk values(?,?,?,?,?)',[(r['project_id'],r['canonical_name'],r['state'],r['matched_1006_source_records'],r['identity_status']) for r in l_rows]);db.commit()
    assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.close()
    print(json.dumps({k:v for k,v in summary.items() if k!='sources'},ensure_ascii=False,indent=2))
if __name__=='__main__':
    if len(sys.argv)!=5:raise SystemExit('usage: python reduce_1006_evidence_backed.py screen.zip raw.zip legacy-source.zip out_dir')
    main(*sys.argv[1:4],pathlib.Path(sys.argv[4]))