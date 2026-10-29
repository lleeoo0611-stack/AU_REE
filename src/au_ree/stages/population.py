"""01: audited Australian REE candidate census, API acquisition, entity resolution.
Never promote a geological occurrence to a mining project solely by name similarity.
"""
from __future__ import annotations
import csv, json, re, math, collections
from pathlib import Path
from ..evidence import reload_registry,verify
from ..core import utc, norm, number, readcsv, digest, event, australian
from ..source_adapters import load_arcgis, load_csv

REE=re.compile(r'\b(?:ree|reo|treo|hree|lree|ndpr|rare\s*earth(?:\s*elements?)?|neodymium|praseodymium|dysprosium|terbium|yttrium)\b',re.I)
def relevance(text,source):
    if source.get('commodity_preclassified_ree') or REE.search(str(text)):return 'REE_PROJECT_RELEVANT'
    if re.search(r'monazite|xenotime',str(text),re.I):return 'REVIEW_REE_MINERAL_ONLY'
    return 'EXCLUDE_NO_REE_EVIDENCE'

STATE_ALIASES={
    'WESTERN AUSTRALIA':'WA','NORTHERN TERRITORY':'NT','SOUTH AUSTRALIA':'SA',
    'QUEENSLAND':'QLD','NEW SOUTH WALES':'NSW','VICTORIA':'VIC','TASMANIA':'TAS',
    'AUSTRALIAN CAPITAL TERRITORY':'ACT',
}
BOUNDS={'WA':(112,130,-36,-13),'NT':(129,139,-27,-10),'SA':(129,142,-39,-24),
        'QLD':(137,154,-30,-9),'NSW':(140,154,-38,-27),
        'VIC':(140,150,-40,-33),'TAS':(143,149,-44,-39)}

def normalize_state(value):
    raw=str(value or '').strip().upper()
    return STATE_ALIASES.get(raw,raw)

def haversine_km(lat,lon,lat2,lon2):
    phi1,phi2=math.radians(lat),math.radians(lat2)
    dphi=phi2-phi1;dlambda=math.radians(lon2-lon)
    a=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 12742*math.asin(min(1,math.sqrt(a)))

def spatial_suggestions(db, candidate):
    lat=number(candidate.get('latitude'));lon=number(candidate.get('longitude'))
    if not australian(lat,lon):return []
    results=[]
    for row in db.execute('SELECT project_id,canonical_name,state,operator_name,latitude,longitude FROM project_master WHERE latitude IS NOT NULL AND longitude IS NOT NULL'):
        if normalize_state(row['state']) != normalize_state(candidate.get('state')):continue
        km=haversine_km(lat,lon,row['latitude'],row['longitude'])
        if km<=25:
            results.append({'project_id':row['project_id'],'project_name':row['canonical_name'],
                'distance_km':round(km,3),'company_same':bool(candidate.get('company') and row['operator_name'] and norm(candidate['company'])==norm(row['operator_name'])),
                'name_same':norm(candidate.get('name'))==norm(row['canonical_name'])})
    return sorted(results,key=lambda x:x['distance_km'])[:8]

def existing_match(db,candidate):
    """Persistent native ID > exact name + state > curated alias; never spatial autolink."""
    name=norm(candidate.get('name'));state=normalize_state(candidate.get('state'))
    native=str(candidate.get('native_id') or '')
    if native:
        mapped=db.execute('SELECT project_id FROM project_aliases WHERE source_key=? AND native_id=? AND native_id<>""',(candidate['source'],native)).fetchall()
        if len({r['project_id'] for r in mapped})==1:return mapped[0]['project_id'],'NATIVE_ID'
    row=db.execute('SELECT project_id FROM project_master WHERE normalized_name=? AND UPPER(COALESCE(state,""))=?',(name,state)).fetchall()
    if len(row)==1:return row[0]['project_id'],'EXACT_NAME_STATE'
    aliases=db.execute('''SELECT DISTINCT p.project_id FROM project_aliases a JOIN project_master p ON a.project_id=p.project_id WHERE a.normalized_alias=? AND UPPER(COALESCE(p.state,''))=?''',(name,state)).fetchall()
    if len(aliases)==1:return aliases[0]['project_id'],'EXACT_ALIAS_STATE'
    return None,'REVIEW_AMBIGUOUS' if (len(row)>1 or len(aliases)>1) else 'NEW'

def candidate_upsert(db,c):
    """Census inclusion is not MCDA eligibility nor identity verification."""
    lat=number(c.get('latitude'));lon=number(c.get('longitude'))
    native=str(c.get('native_id') or '')
    name=str(c.get('name') or '').strip()
    state=normalize_state(c.get('state'))
    company=str(c.get('company') or '').strip()
    entity=str(c.get('entity_level') or 'UNKNOWN').upper()
    key=digest([c['source'],native])[:32] if native else digest([c['source'],name,state])[:32]
    role=relevance(c.get('commodity',''),c)
    if c.get('state_conflict') or (c.get('state_jurisdiction') in BOUNDS and state!=c.get('state_jurisdiction')):
        status,reason,pid='REVIEW','STATE_SOURCE_CONFLICT',None
    elif state in BOUNDS and australian(lat,lon):
        lo,hi,down,up=BOUNDS[state]
        if not (lo-1<=lon<=hi+1 and down-1<=lat<=up+1):
            status,reason,pid='REVIEW','STATE_COORDINATE_MISMATCH',None
        else:status,reason,pid=None,None,None
    else:status,reason,pid=None,None,None
    possible=[]
    if status is None:
        if not name:status,reason='EXCLUDED','NO_NAME'
        elif role=='EXCLUDE_NO_REE_EVIDENCE':status,reason='EXCLUDED','NOT_REE'
        elif lat is not None and lon is not None and not australian(lat,lon):status,reason='EXCLUDED','OUTSIDE_AU'
        elif role=='REVIEW_REE_MINERAL_ONLY':status,reason='REVIEW','MINERAL_OCCURRENCE_NEEDS_EVIDENCE'
        else:
            matched,method=existing_match(db,c)
            if entity!='PROJECT':
                status='REVIEW'
                reason='ENTITY_LEVEL_'+entity if not matched else 'DEPOSIT_POSSIBLE_PARENT_'+method
                pid=matched  # suggestion only; NOT a verified relation nor a merged Project.
                possible=spatial_suggestions(db,c)
            elif matched:
                master=db.execute('SELECT operator_name FROM project_master WHERE project_id=?',(matched,)).fetchone()
                operator=master['operator_name'] if master else None
                if company and operator and norm(company)!=norm(operator):
                    status,reason,pid='REVIEW','COMPANY_OPERATOR_CONFLICT',matched
                else:
                    status,reason,pid='MERGED',method,matched
                    # Do not replace previously reviewed coordinate or identity data.
                    db.execute('INSERT OR IGNORE INTO project_aliases(project_id,alias,normalized_alias,source_key,native_id) VALUES(?,?,?,?,?)',
                               (pid,name,norm(name),c['source'],native))
                    if c.get('legacy_id'):db.execute('INSERT OR REPLACE INTO legacy_id_map(legacy_id,project_id) VALUES(?,?)',(c['legacy_id'],pid))
            elif method=='REVIEW_AMBIGUOUS':status,reason='REVIEW',method
            elif not state:status,reason='REVIEW','STATE_UNCONFIRMED'
            elif (lat is None or lon is None) and c['source']!='legacy_r963_frozen':status,reason='REVIEW','MISSING_COORDINATE'
            else:
                possible=spatial_suggestions(db,c)
                # Proximity does not establish identity. A nearby project is a review.
                if possible and c['source']!='legacy_r963_frozen':
                    status,reason='REVIEW','NEARBY_PROJECT_POSSIBLE_DUPLICATE'
                else:
                    numbers=[int(x[0]) for x in db.execute("SELECT SUBSTR(project_id,8) FROM project_master WHERE project_id GLOB 'AU-REE-[0-9]*'") if str(x[0]).isdigit()]
                    pid=f'AU-REE-{max(numbers,default=0)+1:05d}'
                    db.execute('''INSERT INTO project_master(project_id,canonical_name,normalized_name,state,latitude,longitude,activity,lifecycle,ree_role,deposit_family,population_status,identity_source,operator_name,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (pid,name,norm(name),state,lat,lon,'UNKNOWN','UNKNOWN','REE_UNCONFIRMED',
                         c.get('deposit_family') or 'UNKNOWN','LEGACY_UNVERIFIED' if c['source']=='legacy_r963_frozen' else 'CENSUS_UNVERIFIED',c['source'],company or None,utc()))
                    if lat is not None and lon is not None:
                        db.execute('INSERT OR IGNORE INTO project_coordinates(project_id,latitude,longitude,quality,uncertainty_km,source_url,verification,updated_at) VALUES(?,?,?,?,?,?,?,?)',
                                   (pid,lat,lon,'SOURCE_CANDIDATE' if c.get('official') else 'LEGACY',None,c.get('source_url'),
                                    'SOURCE_BACKED_NEEDS_PROJECT_REVIEW' if c.get('official') else 'LEGACY_NEEDS_REVIEW',utc()))
                    db.execute('INSERT OR IGNORE INTO project_aliases(project_id,alias,normalized_alias,source_key,native_id) VALUES(?,?,?,?,?)',
                               (pid,name,norm(name),c['source'],native))
                    if c.get('legacy_id'):db.execute('INSERT OR REPLACE INTO legacy_id_map(legacy_id,project_id) VALUES(?,?)',(c['legacy_id'],pid))
                    status,reason='ADDED','PROVISIONAL_PROJECT_CENSUS'+('_OPERATOR_PENDING' if not company else '')
    if not possible and status=='REVIEW':possible=spatial_suggestions(db,c)
    payload={**c,'normalisation':{'state':state,'company':company or None,'company_validation':'SOURCE_REPORTED_UNVERIFIED' if company else 'NOT_REPORTED',
                                'state_validation':'SOURCE_REPORTED_UNVERIFIED',
                                'possible_duplicates':possible,'project_name_hint':c.get('project_name_hint')}}
    db.execute('''INSERT INTO population_candidates(candidate_id,source_key,native_id,raw_name,normalized_name,state,company,latitude,longitude,commodity_text,entity_level,ree_role,decision,matched_project_id,reason,source_url,original_json,first_seen,last_seen) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(candidate_id) DO UPDATE SET last_seen=excluded.last_seen,original_json=excluded.original_json,decision=excluded.decision,matched_project_id=excluded.matched_project_id,reason=excluded.reason,company=excluded.company,state=excluded.state''',
       (key,c['source'],native,name,norm(name),state,company or None,lat,lon,c.get('commodity'),entity,role,status,pid,reason,c.get('source_url'),json.dumps(payload,ensure_ascii=False,default=str),utc(),utc()))
    if status in ('REVIEW','EXCLUDED'):event(db,'population',key,status,reason)
    return status

def seed_rows(path):
    for r in readcsv(path):
        # Legacy census is not a fresh discovery and must retain this provenance.
        yield {'source':'legacy_r963_frozen','native_id':r.get('project_id'),'legacy_id':r.get('project_id'),
               'name':r.get('canonical_name'),'state':r.get('state'),'latitude':None,'longitude':None,
               'commodity':'REE','entity_level':'PROJECT','official':False,'source_url':'',
               'ree_role':'REE_UNCONFIRMED','stage':'UNKNOWN','activity':'UNKNOWN'}

def run(db,ctx):
    cfg=ctx['sources'];counts={};failures=[]
    registry=reload_registry(db,ctx['root'],ctx['criteria']['freeze_date'])
    db.execute('DELETE FROM approved_project_reviews')
    # Reviews are replayed from the independently approved input, never left
    # trusted after an approval/document change. Historic snapshot remains unverified.
    prior=db.execute("SELECT project_id FROM project_coordinates WHERE quality='RESEARCHER_VERIFIED'").fetchall()
    for x in prior:
        pid=x['project_id']
        db.execute("UPDATE project_master SET activity='UNKNOWN', lifecycle='UNKNOWN', ree_role='REE_UNCONFIRMED', deposit_family='UNKNOWN',latitude=NULL,longitude=NULL WHERE project_id=?",(pid,))
        db.execute('DELETE FROM project_coordinates WHERE project_id=?',(pid,))
    selected=set(ctx.get('source_keys') or [])
    sources=[source for source in cfg['sources'] if not selected or source['key'] in selected]
    # Explicitly snapshot legacy identity first; missing coordinates are REVIEW unless legacy seeded
    # maps to a known project with a source-backed coordinate at a later update.
    seed=ctx['root']/'inputs'/'legacy_r963_census.csv'
    if seed.exists():
        for c in seed_rows(seed):
            # Existing r963 UUIDs represent a frozen historical census. Preserve their IDs
            # in the crosswalk and use deterministic insertion without pretending current verification.
            status=candidate_upsert(db,c);counts[status]=counts.get(status,0)+1
        db.execute('''INSERT INTO source_registry(source_key,source_url,source_type,dataset_date,fetched_at,raw_sha256,record_count,fetch_status) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET fetched_at=excluded.fetched_at,raw_sha256=excluded.raw_sha256,record_count=excluded.record_count,fetch_status=excluded.fetch_status''',('legacy_r963_frozen','','csv','2026-10-12',utc(),ctx['hash_file'](seed),sum(counts.values()),'HISTORICAL_SEED'))
    # Historical coordinate/feasibility evidence from r974 is imported as a frozen
    # audit seed. It never counts as a newly verified current-stage decision.
    frozen=ctx['root']/'inputs'/'legacy_r974_frozen_alternatives.csv'
    if frozen.exists():
        for r in readcsv(frozen):
            link=db.execute('SELECT project_id FROM legacy_id_map WHERE legacy_id=?',(r.get('project_id'),)).fetchone()
            if not link:continue
            lat=number(r.get('latitude'));lon=number(r.get('longitude'))
            if australian(lat,lon):
                db.execute('UPDATE project_master SET latitude=COALESCE(latitude,?),longitude=COALESCE(longitude,?),updated_at=? WHERE project_id=?',(lat,lon,utc(),link['project_id']))
                db.execute('INSERT OR IGNORE INTO project_coordinates(project_id,latitude,longitude,quality,uncertainty_km,source_url,verification,updated_at) VALUES(?,?,?,?,?,?,?,?)',(link['project_id'],lat,lon,r.get('coordinate_quality'),number(r.get('coordinate_uncertainty_km')),None,'LEGACY_FROZEN_NEEDS_REVIEW',utc()))
                event(db,'population',link['project_id'],'FROZEN_COORDINATE_SEED','Legacy r974 project location; independent evidence review required')
    for src in sources:
        if not src.get('enabled',False):continue
        n=0;rawhash=None
        try:
            if src['type']=='arcgis':
                rows,rawhash,snapshot_dir=load_arcgis(src,ctx['workspace']/'cache'/'census',offline=ctx['offline'])
            elif src['type']=='csv':
                rows,rawhash,fetch_status=load_csv(src,ctx['root'])
                if rows is None:
                    db.execute('''INSERT INTO source_registry(source_key,source_url,source_type,dataset_date,fetched_at,raw_sha256,record_count,fetch_status,error) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET fetched_at=excluded.fetched_at,record_count=excluded.record_count,fetch_status=excluded.fetch_status,error=excluded.error''',
                      (src['key'],src.get('source_documentation'),src['type'],cfg.get('as_of'),utc(),None,0,fetch_status,None))
                    counts[fetch_status]=counts.get(fetch_status,0)+1
                    continue
            else:raise ValueError('Unsupported source type '+str(src['type']))
            for row in rows:
                status=candidate_upsert(db,row)
                counts[status]=counts.get(status,0)+1
                n+=1
            db.execute('''INSERT INTO source_registry(source_key,source_url,source_type,dataset_date,fetched_at,raw_sha256,record_count,fetch_status,error) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET source_url=excluded.source_url,fetched_at=excluded.fetched_at,raw_sha256=excluded.raw_sha256,record_count=excluded.record_count,fetch_status=excluded.fetch_status,error=excluded.error''',
                 (src['key'],src.get('url') or src.get('source_documentation'),src['type'],cfg.get('as_of'),utc(),rawhash,n,'CACHED_OR_FETCHED_UNVERIFIED',None))
        except Exception as ex:
            failures.append({'source':src['key'],'error':str(ex)})
            db.execute('''INSERT INTO source_registry(source_key,source_url,source_type,dataset_date,fetched_at,record_count,fetch_status,error) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET fetched_at=excluded.fetched_at,fetch_status=excluded.fetch_status,error=excluded.error''',
                      (src['key'],src.get('url') or src.get('source_documentation'),src['type'],cfg.get('as_of'),utc(),n,'OFFLINE_CACHE_MISSING' if ctx['offline'] and 'OFFLINE:' in str(ex) else 'FETCH_FAILED',str(ex)[:2000]))
            event(db,'population',src['key'],'SOURCE_FETCH_FAIL',str(ex))
    # Researcher-reviewed identity, coordinates and current lifecycle are loaded
    # before GIS materialisation so coordinate changes invalidate downstream work.
    reviews=ctx['root']/'inputs'/'project_reviews.csv'
    reviewed=0
    if reviews.exists():
        for row in readcsv(reviews):
            pid=row.get('project_id');source=row.get('source_url','')
            if not pid or not db.execute('SELECT 1 FROM project_master WHERE project_id=?',(pid,)).fetchone():continue
            if not(row.get('evidence_date') and row.get('evidence_date')<=ctx['criteria']['freeze_date'] and verify(db,row.get('approval_ref'),'PROJECT_REVIEW',source,row.get('source_sha256'))):
                event(db,'population',pid,'REVIEW_REJECTED','Missing verifiable source URL/date/hash');continue
            fields={k:row.get(k) for k in ('activity','lifecycle','ree_role','deposit_family') if row.get(k)}
            if fields:
                db.execute('UPDATE project_master SET '+','.join(k+'=?' for k in fields)+',updated_at=? WHERE project_id=?',(*fields.values(),utc(),pid))
            lat=number(row.get('latitude'));lon=number(row.get('longitude'))
            if australian(lat,lon):
                db.execute('UPDATE project_master SET latitude=?,longitude=?,updated_at=? WHERE project_id=?',(lat,lon,utc(),pid))
                db.execute('INSERT OR REPLACE INTO project_coordinates(project_id,latitude,longitude,quality,uncertainty_km,source_url,verification,updated_at) VALUES(?,?,?,?,?,?,?,?)',(pid,lat,lon,'RESEARCHER_VERIFIED',number(row.get('coordinate_uncertainty_km')),source,'VERIFIED',utc()))
            db.execute('INSERT OR REPLACE INTO approved_project_reviews(project_id,approval_ref,source_sha256) VALUES(?,?,?)',
                       (pid,row.get('approval_ref'),row.get('source_sha256')))
            event(db,'population',pid,'CURRENT_PROJECT_EVIDENCE_REVIEW',json.dumps({'fields':fields,'url':source,'date':row.get('evidence_date')},ensure_ascii=False))
            reviewed+=1
    return {'counts':counts,'source_failures':failures,'master_projects':db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0],
            'evidence_registry':registry,'reviewed_project_updates':reviewed,'review_candidates':db.execute("SELECT COUNT(*) FROM population_candidates WHERE decision='REVIEW'").fetchone()[0],
            'source_statuses':dict(db.execute('SELECT fetch_status,COUNT(*) FROM source_registry GROUP BY fetch_status').fetchall()),'selected_sources':sorted(selected) if selected else 'ALL_ENABLED','company_recorded':db.execute('SELECT COUNT(*) FROM project_master WHERE operator_name IS NOT NULL AND operator_name<>""').fetchone()[0], 'status':'OFFLINE_SOURCES_PENDING' if failures and ctx['offline'] else ('PARTIAL_SOURCE_FAILURE' if failures else 'COMPLETED')}
