#!/usr/bin/env python3
"""Scheme-A national screen. Strictly consumes complete archived FULL RAW snapshot.

No API calls, no direct project promotion, no automatic geological identity merges.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re,sqlite3,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from verify_national_raw import verify
from au_ree.core import config
from au_ree.source_adapters import parse_arcgis

DIRECT=re.compile(r'(?<![a-z])(?:ree|reo|treo|hree|lree|ndpr|rare[ -]?earth(?:s|[ -]?elements?)?|neodymium|praseodymium|dysprosium|terbium|yttrium|lanthanum|cerium|pr6o11|nd2o3|dy2o3|tb4o7)(?![a-z])',re.I)
MINERAL=re.compile(r'\b(?:monazite|xenotime|allanite|bastn[aä]site|bastnaesite)\b',re.I)

def tier(declared='',mineral='',context='',preclassified=False):
    if preclassified or DIRECT.search(str(declared or '')):return 'E1_DIRECT_REE'
    if MINERAL.search(str(declared or '')) or MINERAL.search(str(mineral or '')):return 'E2_REE_MINERAL_ONLY'
    if DIRECT.search(str(mineral or '')) or DIRECT.search(str(context or '')) or MINERAL.search(str(context or '')):return 'E3_GEOLOGICAL_CONTEXT'
    return 'E0_NOT_REE'

def normal(s):return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',str(s or '').lower())).strip()
def stable_hash(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,default=str).encode()).hexdigest()
def get(a,*names):
    lower={str(k).lower():v for k,v in a.items()}
    for k in names:
        x=lower.get(k.lower())
        if x is not None and str(x).strip() and str(x).lower()!='none':return str(x).strip()
    return ''
def point(feature,props):
    geom=feature.get('geometry') or {}
    if isinstance(geom,dict) and geom.get('type')=='Point':
        x=geom.get('coordinates') or []
        if len(x)>=2:return x[1],x[0]
    return get(props,'latgda94','latitude','LATITUDE_GDA2020'),get(props,'longda94','longitude','LONGITUDE_GDA2020')
def float_or_blank(x):
    try:
        a=float(x)
        return a if math.isfinite(a) and a!=-999 else ''
    except (TypeError,ValueError):return ''

def make_candidate(source,native,name,state,level,declared='',mineral='',context='',parent='',lat='',lon='',operator='',raw_ref='',preclassified=False):
    cls=tier(declared,mineral,context,preclassified)
    if cls=='E0_NOT_REE':return None
    return {'candidate_id':'C-'+stable_hash([source,str(native)])[:22],'source_key':source,
            'native_id':str(native),'name':str(name or '').strip(), 'state':state,
            'entity_level':level,'tier':cls,'commodity_text':str(declared or ''),
            'mineral_text':str(mineral or ''),'context_excerpt':str(context or '')[:300],
            'parent_project_hint':str(parent or ''),'latitude':float_or_blank(lat),
            'longitude':float_or_blank(lon),'operator':str(operator or ''),
            'source_record_ref':raw_ref,'review_status':'SOURCE_CANDIDATE_UNVERIFIED',
            'project_master_action':'REQUIRES_INDEPENDENT_PROJECT_EVIDENCE'}

def read_csv(path):
    with path.open('r',encoding='utf-8-sig',errors='replace',newline='') as f:
        csv.field_size_limit(100_000_000)
        yield from csv.DictReader(f)

def save_csv(path,rows,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

FIELDS=['candidate_id','source_key','native_id','name','state','entity_level','tier','commodity_text','mineral_text','context_excerpt','parent_project_hint','latitude','longitude','operator','source_record_ref','review_status','project_master_action']

def screen(root,out):
    root=Path(root);out=Path(out)
    if not verify(root):raise RuntimeError('Cannot screen: national raw gate must PASS')
    manifest=json.loads((root/'national_raw_manifest.json').read_text())
    rows=[];raw_counts=Counter();screen_counts=Counter();native_seen=defaultdict(set)
    def push(src,native,record):
        raw_counts[src]+=1
        if record is None:return
        if native in native_seen[src]:return
        native_seen[src].add(native)
        rows.append(record);screen_counts[(src,record['tier'])]+=1

    source_map={s['key']:s for s in config('sources.json')['sources'] if s.get('type')=='arcgis'}
    for source_key,source in source_map.items():
        archive=manifest['sources'][source_key]
        base=root/archive['cache_path']
        m=json.loads((base/'manifest.json').read_text())
        for chunk in m['chunks']:
            features=json.loads((base/chunk['file']).read_text())['features']
            for f in features:
                c=parse_arcgis(f,source);a=c['source_raw_attributes'];native=c.get('native_id') or stable_hash(a)[:22]
                declared=c.get('commodity') or ''
                if source_key=='STATE_TAS_MRT':
                    declared=get(a,'COMMODITIES','COMMODITY_CATEGORY')
                    mineral=''
                    context=get(a,'DESCRIPTION')
                else:
                    mineral=get(a,'mineralogy','ore_minerals')
                    context=get(a,'description')
                record=make_candidate(source_key,native,c['name'],c['state'],c['entity_level'],declared,mineral,context,
                      c.get('project_name_hint'),c.get('latitude'),c.get('longitude'),c.get('company'),
                      f"{archive['cache_path']}/{chunk['file']}",source.get('commodity_preclassified_ree',False))
                push(source_key,native,record)
    for src in ['NSW_METINDEX','VIC_MINSITE','NT_MODAT_WFS']:
        m=manifest['sources'][src]
        for chunk in m['chunks']:
            for feat in json.loads((root/chunk['path']).read_text())['features']:
                a=feat.get('properties') or {};lat,lon=point(feat,a)
                if src=='NSW_METINDEX':
                    native=get(a,'occurrence_id') or feat.get('id')
                    name=get(a,'deposit_name','all_names','metal_no')
                    declared='; '.join(filter(None,[get(a,'major_comm'),get(a,'minor_comm')]))
                    mineral='; '.join(filter(None,[get(a,'ore_min'),get(a,'gangue_min')]))
                    context='; '.join(filter(None,[get(a,'summary_desc'),get(a,'nsw_class'),get(a,'nsw_gen'),get(a,'other_class')]))
                    level='OCCURRENCE';parent='';operator=''
                elif src=='VIC_MINSITE':
                    native=get(a,'siteid') or feat.get('id')
                    name=get(a,'mine_name','field_name')
                    declared='; '.join(filter(None,[get(a,'pri_comm'),get(a,'sec_comm'),get(a,'prod_comm')]))
                    mineral=get(a,'min_ass')
                    context='; '.join(filter(None,[get(a,'dep_style'),get(a,'dep_ty_gen'),get(a,'dep_ty_sp')]))
                    parent=get(a,'project');level='MINE_SITE' if 'mine' in get(a,'site_type','mine_type').lower() else 'OCCURRENCE';operator=''
                else:
                    native=get(a,'identifier') or feat.get('id')
                    name=get(a,'name');declared=get(a,'commodity','representativeCommodity_uri')
                    mineral='';context=get(a,'mineralOccurrenceType','geologicHistory')
                    parent='';level='OCCURRENCE';operator=''
                rec=make_candidate(src,native,name,m['state'],level,declared,mineral,context,parent,lat,lon,operator,chunk['path'])
                push(src,native,rec)

    # SA Geodata relational database: join all commodities and mineralogy by MINERAL_DEPOSIT_NO.
    sa_root=root/'sa_geodata'
    com=defaultdict(list);miner=defaultdict(list);ref_count=Counter()
    for a in read_csv(sa_root/'sarig_md_commodity_exp.csv'):
        com[a['MINERAL_DEPOSIT_NO']].append(a.get('COMMODITY_NAME') or a.get('COMMODITY_CODE') or '')
    for a in read_csv(sa_root/'sarig_md_mineralogy_exp.csv'):
        miner[a['MINERAL_DEPOSIT_NO']].append(a.get('MINERAL') or '')
    for a in read_csv(sa_root/'sarig_md_reference_exp.csv'):
        ref_count[a['MINERAL_DEPOSIT_NO']]+=1
    for a in read_csv(sa_root/'sarig_md_details_exp.csv'):
        native=a['MINERAL_DEPOSIT_NO']
        declared='; '.join([a.get('COMMODITIES') or '',*com.get(native,[])])
        mineral='; '.join([a.get('MINEROLOGY_ORE') or '',a.get('MINEROLOGY_GANGUE') or '',*miner.get(native,[])])
        rec=make_candidate('SA_GEODATA_MINDEP',native,a.get('DEPOSIT_NAME'),'SA',a.get('DEPOSIT_CLASS') or 'DEPOSIT',
           declared,mineral,a.get('DEPOSIT_SUMMARY'),'',a.get('LATITUDE_GDA2020'),a.get('LONGITUDE_GDA2020'),'','sa_geodata/sarig_md_details_exp.csv')
        push('SA_GEODATA_MINDEP',native,rec)
    for x in manifest['sources']['SA_PROJECT_WFS']:
        source=x['key']
        for a in read_csv(root/x['path']):
            native=a.get('MINERAL_DEPOSIT_NO') or a.get('SITE_NO') or a.get('OBJECTID') or a.get('FID')
            if source=='SA_CRITICAL_REE':
                name=a.get('DEPOSIT_NAME');declared=a.get('DEPOSIT_COMMODITIES');
                mineral='';context=a.get('SUMMARY_DESCRIPTION');level='DEPOSIT';parent='';operator=''
                lat=a.get('LATITUDE');lon=a.get('LONGITUDE')
            else:
                name=a.get('PROJECT_NAME');declared=a.get('COMMODITIES');
                mineral='';context=a.get('PROJECT_DESCRIPTION');level='PROJECT';parent=name;operator=a.get('OPERATING_COMPANY')
                lat=a.get('LATITUDE');lon=a.get('LONGITUDE')
            rec=make_candidate(source,native,name,'SA',level,declared,mineral,context,parent,lat,lon,operator,x['path'],preclassified=(source=='SA_CRITICAL_REE'))
            push(source,native,rec)
    # Exact name/State is only a candidate pair; never perform an automatic entity merge.
    matched=defaultdict(list)
    for r in rows:
        if r['name']:matched[(r['state'],normal(r['name']))].append(r)
    pairs=[]
    for (state,name),group in sorted(matched.items()):
        for i,a in enumerate(group):
            for b in group[i+1:]:
                if a['source_key']==b['source_key']:continue
                pairs.append({'state':state,'normalized_name':name,'candidate_a':a['candidate_id'],'candidate_b':b['candidate_id'],
                              'source_a':a['source_key'],'source_b':b['source_key'],'rule':'EXACT_NAME_STATE_REVIEW',
                              'decision':'PROPOSED_ONLY'})
    state_rows=[]
    for state in ['WA','QLD','TAS','NSW','VIC','NT','SA']:
        state_rows.append({'state':state,'unfiltered_raw_records':sum(v for k,v in raw_counts.items() if k in ({'WA':['STATE_WA_MINDEX'],'QLD':['STATE_QLD_MINOCC'],'TAS':['STATE_TAS_MRT'],'NSW':['NSW_METINDEX'],'VIC':['VIC_MINSITE'],'NT':['NT_MODAT_WFS'],'SA':['SA_GEODATA_MINDEP','SA_PROJECT_DEVELOPING','SA_PROJECT_MAJOR','SA_CRITICAL_REE']}[state])),
                           'screened_source_candidates':sum(1 for x in rows if x['state']==state)})
    out.mkdir(parents=True,exist_ok=True)
    save_csv(out/'nationwide_ree_candidates.csv',rows,FIELDS)
    save_csv(out/'cross_source_exact_name_review.csv',pairs,['state','normalized_name','candidate_a','candidate_b','source_a','source_b','rule','decision'])
    save_csv(out/'source_raw_and_screening_counts.csv',state_rows,['state','unfiltered_raw_records','screened_source_candidates'])
    counts=Counter(x['tier'] for x in rows)
    save_csv(out/'tier_summary.csv',[{'tier':k,'records':v} for k,v in sorted(counts.items())],['tier','records'])
    summary={'source_archive_manifest_sha256':hashlib.sha256((root/'national_raw_manifest.json').read_bytes()).hexdigest(),
             'gate':'PASSED_BEFORE_SCREENING','source_raw_counts':dict(raw_counts),
             'screened_candidate_records':len(rows),'tier_counts':dict(counts),
             'cross_source_exact_name_pairs':len(pairs),'SA_reference_links_preserved':sum(ref_count.values()),
             'project_master_new_records':0,'project_identity_merges_automatic':0,
             'screening_status':'SCHEME_A_REVIEW_ONLY'}
    (out/'screening_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    db=sqlite3.connect(out/'national_screening_review.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS source_candidates(candidate_id TEXT PRIMARY KEY,source_key TEXT,native_id TEXT,name TEXT,state TEXT,entity_level TEXT,tier TEXT,latitude TEXT,longitude TEXT,project_master_action TEXT,source_record_ref TEXT)')
    db.execute('DELETE FROM source_candidates')
    db.executemany('INSERT INTO source_candidates VALUES(?,?,?,?,?,?,?,?,?,?,?)',[(r['candidate_id'],r['source_key'],r['native_id'],r['name'],r['state'],r['entity_level'],r['tier'],str(r['latitude']),str(r['longitude']),r['project_master_action'],r['source_record_ref']) for r in rows]);db.commit();db.close()
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raw-dir',type=Path,default=Path('work/national_raw'))
    ap.add_argument('--out',type=Path,default=Path('work/national_screening'))
    args=ap.parse_args();screen(args.raw_dir,args.out)
