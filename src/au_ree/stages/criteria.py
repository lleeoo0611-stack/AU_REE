"""02: criteria registry and provenance-bearing observation ingestion.
Frozen r968 evidence is historical, and is not blindly promoted to current verified MCDA data.
"""
from __future__ import annotations
import json
from ..evidence import reload_registry,verify
from ..core import utc, digest, readcsv, number, event

def ingest(db,rows,tag,as_of=None):
    n=0
    for r in rows:
        legacy_id=r.get('project_id') or r.get('legacy_id')
        mapping=db.execute('SELECT project_id FROM legacy_id_map WHERE legacy_id=?',(legacy_id,)).fetchone()
        pid=mapping['project_id'] if mapping else legacy_id
        if not db.execute('SELECT 1 FROM project_master WHERE project_id=?',(pid,)).fetchone():
            event(db,'criteria',legacy_id,'ORPHAN_OBSERVATION','No project identity match');continue
        if as_of and ((r.get('effective_date') or '') > as_of or (r.get('publication_date') or '') > as_of):
            event(db,'criteria',legacy_id,'POST_CUTOFF_EVIDENCE','Future-dated observation held out of snapshot');continue
        var=str(r.get('variable') or '').strip()
        if not var:continue
        raw=r.get('standard_value',r.get('raw_value'))
        numeric=number(r.get('numeric_value',raw));title=r.get('source_title') or ''
        oid=digest([tag,pid,var,str(raw),r.get('effective_date'),r.get('source_url'),r.get('source_page')])[:32]
        claimed=r.get('verification',r.get('verification_status','UNVERIFIED'))
        if tag=='r968_frozen':
            verification='LEGACY_FROZEN_'+str(claimed)
        else:
            approved=verify(db,r.get('approval_ref'),'OBSERVATION',r.get('source_url'),r.get('source_sha256'))
            verification='VERIFIED' if approved else 'REVIEW_PENDING'
            if not approved:
                event(db,'criteria',oid,'EVIDENCE_APPROVAL_PENDING',str(r.get('approval_ref') or 'MISSING_APPROVAL_REF'))
        db.execute('''INSERT OR REPLACE INTO observations(obs_id,project_id,variable,numeric_value,text_value,unit,basis,effective_date,publication_date,source_url,source_title,source_page,source_sha256,verification,captured_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
          (oid,pid,var,numeric,str(raw) if raw is not None else None,r.get('unit') or r.get('standard_unit'),r.get('basis'),r.get('effective_date'),r.get('publication_date'),r.get('source_url'),title,r.get('source_page'),r.get('source_sha256'),verification,utc()))
        if verification=='VERIFIED':
            db.execute("INSERT OR REPLACE INTO evidence_links(record_type,record_id,approval_ref) VALUES('OBSERVATION',?,?)",(oid,r.get('approval_ref')))
        n+=1
    return n

def derive_metrics(db):
    """Derive source-compatible metrics. Never convert THM/MzEq into TREO.

    Inputs must be VERIFIED/ACCEPTED and from the same source hash and
    effective date; their provenance is preserved as a derived formula record.
    """
    from math import isfinite
    source=db.execute("""SELECT o.* FROM observations o JOIN evidence_links l ON l.record_id=o.obs_id AND l.record_type='OBSERVATION' JOIN evidence_approvals a ON a.approval_ref=l.approval_ref AND a.status='APPROVED' WHERE o.verification='VERIFIED'
             AND o.numeric_value IS NOT NULL AND o.source_sha256 IS NOT NULL AND o.source_url IS NOT NULL
             ORDER BY o.effective_date DESC,o.obs_id DESC""").fetchall()
    groups={}
    for o in source:
        if not isfinite(o['numeric_value']):continue
        key=(o['project_id'],o['source_sha256'],o['effective_date'],o['source_url'])
        groups.setdefault(key,{})[o['variable']]=o
    count=0
    for (pid,sha,dt,url),metrics in groups.items():
        choices=[]
        ore=metrics.get('ore_mt');grade=metrics.get('treo_grade_pct')
        if ore and grade and ore['basis']=='DIRECT_TREO' and grade['basis']=='DIRECT_TREO':
            if ore['numeric_value']>0 and 0<grade['numeric_value']<=100:
                choices.append(('contained_treo_kt',ore['numeric_value']*grade['numeric_value']*10.0,'kt TREO','DIRECT_TREO',[ore,grade]))
        four=['nd2o3_pct_treo','pr6o11_pct_treo','dy2o3_pct_treo','tb4o7_pct_treo']
        if all(k in metrics for k in four):
            members=[metrics[k] for k in four]
            if all(m['basis']=='PCT_TREO_REO_COMPONENT' and 0<=m['numeric_value']<=100 for m in members):
                share=sum(m['numeric_value'] for m in members)
                if share<=100+1e-8:choices.append(('magnet_reo_share_pct',share,'%','DIRECT_MAGNET_REO_SHARE',members))
        for var,val,unit,basis,inputs in choices:
            oid=digest(['derived:v1',pid,var,sha,dt,sorted(o['obs_id'] for o in inputs)])[:32]
            db.execute("""INSERT OR REPLACE INTO observations
             (obs_id,project_id,variable,numeric_value,text_value,unit,basis,effective_date,
              publication_date,source_url,source_title,source_page,source_sha256,verification,captured_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (oid,pid,var,round(val,12),json.dumps({'formula':'ore_mt * treo_grade_pct * 10' if var=='contained_treo_kt' else 'Nd2O3 + Pr6O11 + Dy2O3 + Tb4O7 (% TREO)',
                      'inputs':[o['obs_id'] for o in inputs]},ensure_ascii=False),unit,basis,dt,
               inputs[0]['publication_date'],url,'DERIVED from validated source-compatible components',
               ';'.join(str(o['source_page'] or '') for o in inputs),sha,'ACCEPTED_DERIVED',utc()))
            count+=1
    return count

def run(db,ctx):
    cfg=ctx['criteria'];registry=reload_registry(db,ctx['root'],cfg['freeze_date'])
    # Replay evidence from the current frozen inputs; remove stale approved and
    # derived rows when documents, source claims or reviewer decisions change.
    db.execute("DELETE FROM evidence_links WHERE record_type='OBSERVATION'")
    db.execute('DELETE FROM criterion_values');db.execute('DELETE FROM observations')
    db.execute('DELETE FROM criteria');db.execute('DELETE FROM variable_dictionary')
    for c in cfg['criteria']:
        db.execute('INSERT INTO criteria(code,domain,label,direction,unit,basis,mandatory,description,config_version) VALUES(?,?,?,?,?,?,?,?,?)',
            (c['code'],c['domain'],c['name'],c['direction'],c['unit'],c['basis'],int(c.get('mandatory',False)),c.get('description',''),cfg['version']))
        db.execute('INSERT INTO variable_dictionary(code,domain,unit,expected_basis,source_priority,provenance_required) VALUES(?,?,?,?,?,?)',
            (c['variable'],c['domain'],c['unit'],c['basis'],'JORC/ASX authorized > technical report > official government > company',1))
    total=0
    frozen=ctx['root']/'inputs'/'legacy_r968_observations.csv'
    if frozen.exists():total+=ingest(db,readcsv(frozen),'r968_frozen',cfg['freeze_date'])
    update=ctx['root']/'inputs'/'verified_observations.csv'
    if update.exists():total+=ingest(db,readcsv(update),'researcher_updates',cfg['freeze_date'])
    derived = derive_metrics(db)
    db.execute('DELETE FROM criterion_values')
    codes={r['code']:r for r in cfg['criteria']}
    for p in db.execute('SELECT project_id FROM project_master').fetchall():
        pid=p['project_id']
        for code,c in codes.items():
            # All quantitative MCDA values must be traceable and explicitly VERIFIED or ACCEPTED.
            obs=db.execute('''SELECT * FROM observations WHERE project_id=? AND variable=? AND numeric_value IS NOT NULL ORDER BY effective_date DESC, obs_id DESC''',(pid,c['variable'])).fetchall()
            valid=[o for o in obs if o['verification'] in ('VERIFIED','ACCEPTED_DERIVED') and o['source_url'] and o['basis']==c['basis'] and o['source_sha256'] and (o['verification']=='ACCEPTED_DERIVED' or db.execute("SELECT 1 FROM evidence_links l JOIN evidence_approvals a ON l.approval_ref=a.approval_ref AND a.status='APPROVED' WHERE l.record_type='OBSERVATION' AND l.record_id=?",(o['obs_id'],)).fetchone())]
            # Effective date first, then direct attested values before derived values on equal dates.
            o=sorted(valid,key=lambda x:(x['effective_date'] or '', x['verification']!='ACCEPTED_DERIVED', x['obs_id']),reverse=True)[0] if valid else None
            issue='' if o else ('SOURCE_BASIS_OR_VERIFICATION_PENDING' if obs else 'MISSING')
            db.execute('INSERT OR REPLACE INTO criterion_values(project_id,criterion,value,unit,basis,observation_id,quality,issue) VALUES(?,?,?,?,?,?,?,?)',
                (pid,code,o['numeric_value'] if o else None,c['unit'],c['basis'],o['obs_id'] if o else None,'VERIFIED' if o else 'NOT_SCORED',issue))
    ctx['artifacts']['source_documents_audit.csv']=([dict(x) for x in db.execute('SELECT * FROM source_documents ORDER BY document_id')],
        ['document_id','file_path','source_url','declared_sha256','actual_sha256','hash_status','checked_at'])
    ctx['artifacts']['evidence_approvals_audit.csv']=([dict(x) for x in db.execute('SELECT * FROM evidence_approvals ORDER BY approval_ref')],
        ['approval_ref','record_type','document_id','reviewer','decision','reviewed_at','status','notes'])
    ctx['artifacts']['criteria_dictionary.csv']=([dict(r) for r in db.execute('SELECT * FROM criteria ORDER BY code')],
        ['code','domain','label','direction','unit','basis','mandatory','description','config_version'])
    ctx['artifacts']['variable_dictionary.csv']=([dict(r) for r in db.execute('SELECT * FROM variable_dictionary ORDER BY code')],
        ['code','domain','unit','expected_basis','source_priority','provenance_required'])
    ctx['artifacts']['observations_evidence.csv']=([dict(r) for r in db.execute('SELECT * FROM observations ORDER BY project_id,variable,effective_date')],
        ['obs_id','project_id','variable','numeric_value','text_value','unit','basis','effective_date','publication_date','source_url','source_title','source_page','source_sha256','verification','captured_at'])
    ctx['artifacts']['criterion_values.csv']=([dict(r) for r in db.execute('SELECT * FROM criterion_values ORDER BY project_id,criterion')],
        ['project_id','criterion','value','unit','basis','observation_id','quality','issue'])
    return {'criteria':len(codes),'imported_observations':total,'stored_observations':db.execute('SELECT count(*) FROM observations').fetchone()[0],
            'verified_scoring_values':db.execute("SELECT COUNT(*) FROM criterion_values WHERE quality='VERIFIED'").fetchone()[0], 'derived_observations':derived,
            'evidence_registry':registry,'status':'CRITERIA_REGISTERED_EVIDENCE_GATED'}
