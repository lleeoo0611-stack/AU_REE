"""Scheme A: raw features -> geological entities -> independently approved projects.

Distance/name matching only proposes candidate pairs. Neither a mineral occurrence
nor an API label is sufficient evidence of an independent development project.
"""
from __future__ import annotations
import json,re
from datetime import date
from collections import defaultdict
from pathlib import Path
from .core import digest,norm,utc,number,readcsv,event
from .evidence import verify

DIRECT=re.compile(r'(?<![a-z])(?:ree|reo|treo|hree|lree|ndpr|rare[ -]?earth(?:[ -]?elements?)?|neodymium|praseodymium|dysprosium|terbium|yttrium|lanthanum|cerium)(?![a-z])',re.I)
MINERAL=re.compile(r'\b(?:monazite|xenotime|allanite|bastn[aä]site|bastnaesite)\b',re.I)


def screening_tier(c):
    text=str(c.get('commodity') or '')
    if c.get('commodity_preclassified_ree') or DIRECT.search(text):return 'E1_DIRECT_REE'
    if MINERAL.search(text):return 'E2_REE_MINERAL_ONLY'
    if DIRECT.search(str(c.get('name') or '')) or MINERAL.search(str(c.get('name') or '')):
        return 'E3_NAME_CONTEXT_ONLY'
    return 'E0_NOT_REE'


def register_feature(db,c,candidate_id,tier,level):
    """Store immutable per-record hash; keep native row plus source cache separately."""
    if c.get('source')=='legacy_r963_frozen':return
    raw=c.get('source_raw_attributes') or c
    rawsha=digest({'attributes':raw,'latitude':c.get('latitude'),
                   'longitude':c.get('longitude'),'source_url':c.get('source_url')})
    db.execute('''INSERT OR IGNORE INTO source_feature_snapshot
      (candidate_id,source_key,native_id,record_sha256,source_manifest_sha256,source_url,observed_at)
      VALUES(?,?,?,?,?,?,?)''',(candidate_id,c['source'],str(c.get('native_id') or ''),rawsha,
      c.get('source_snapshot_sha256'),str(c.get('source_url') or ''),utc()))
    if tier=='E0_NOT_REE' or not c.get('name'):return
    if level=='PROJECT' and tier=='E1_DIRECT_REE':return
    eid='GEO-'+digest([c['source'],c.get('native_id') or candidate_id])[:20]
    db.execute('''INSERT INTO geological_entity(entity_id,canonical_name,state,latitude,longitude,
          entity_level,screening_tier,identity_status,first_seen,last_seen) VALUES(?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(entity_id) DO UPDATE SET screening_tier=excluded.screening_tier,
          last_seen=excluded.last_seen''',(eid,str(c.get('name')),str(c.get('state') or ''),
          number(c.get('latitude')),number(c.get('longitude')),level,tier,'SOURCE_SCOPED_UNVERIFIED',utc(),utc()))
    db.execute('''INSERT OR REPLACE INTO geological_entity_source(entity_id,candidate_id,source_key,
          native_id,record_sha256) VALUES(?,?,?,?,?)''',(eid,candidate_id,c['source'],
          str(c.get('native_id') or ''),rawsha))
    db.execute('''INSERT INTO extended_occurrence_inventory(candidate_id,entity_id,screening_tier,
          disposition,source_sha256,updated_at) VALUES(?,?,?,?,?,?)
          ON CONFLICT(candidate_id) DO UPDATE SET screening_tier=excluded.screening_tier,
          disposition=excluded.disposition,source_sha256=excluded.source_sha256,
          updated_at=excluded.updated_at''',(candidate_id,eid,tier,
          'BACKGROUND_ONLY' if tier.startswith('E2_') or tier.startswith('E3_') else 'GEOLOGICAL_CANDIDATE',
          rawsha,utc()))


def propose_dedup(db):
    """Build exact-name and 1-km proximity reviews without any implicit merge."""
    rows=[dict(r) for r in db.execute('''SELECT c.candidate_id,c.source_key,c.normalized_name,c.state,
            c.latitude,c.longitude,c.company,c.entity_level FROM population_candidates c
            WHERE c.decision!='EXCLUDED' AND c.source_key!='legacy_r963_frozen' ORDER BY c.candidate_id''')]
    buckets=defaultdict(list)
    for r in rows:
        if r['state'] and r['normalized_name']:buckets[(r['state'],r['normalized_name'])].append(r)
    pairs={}
    def push(a,b,rule,distance=None):
        if a['source_key']==b['source_key']:return
        x,y=sorted((a['candidate_id'],b['candidate_id']))
        key=digest([x,y])[:32]
        if key not in pairs or rule=='EXACT_NAME_STATE':
            pairs[key]=(x,y,rule,distance)
    for group in buckets.values():
        for i,a in enumerate(group):
            for b in group[i+1:]:push(a,b,'EXACT_NAME_STATE')
    # Fixed bounding bins prevent quadratic comparisons of national raw inventory.
    location=defaultdict(list)
    for r in rows:
        if r['latitude'] is not None and r['longitude'] is not None:
            location[(r['state'],int(r['latitude']*10),int(r['longitude']*10))].append(r)
    from .stages.population import haversine_km
    for (state,ilat,ilon),group in location.items():
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                for a in group:
                    for b in location.get((state,ilat+dx,ilon+dy),()):
                        if a['candidate_id']>=b['candidate_id'] or a['source_key']==b['source_key']:continue
                        d=haversine_km(a['latitude'],a['longitude'],b['latitude'],b['longitude'])
                        if d<=1:push(a,b,'WITHIN_1KM_REVIEW',round(d,4))
    for key,(a,b,rule,d) in sorted(pairs.items()):
        db.execute('''INSERT INTO dedup_candidate_pairs(pair_id,candidate_a,candidate_b,rule,distance_km,
          decision_status,updated_at) VALUES(?,?,?,?,?,'PROPOSED_ONLY',?)
          ON CONFLICT(pair_id) DO UPDATE SET rule=excluded.rule,distance_km=excluded.distance_km,
          updated_at=excluded.updated_at''',(key,a,b,rule,d,utc()))
    return len(pairs)


def propose_parents(db):
    """Unverified source-provided project labels create links, not project identities."""
    proposed=0
    for row in db.execute('''SELECT s.entity_id,c.original_json,c.state FROM geological_entity_source s
         JOIN population_candidates c ON c.candidate_id=s.candidate_id''').fetchall():
        attrs=json.loads(row['original_json'] or '{}')
        hint=attrs.get('project_name_hint')
        if not hint:continue
        masters=db.execute('SELECT project_id FROM project_master WHERE normalized_name=? AND state=?',
                           (norm(hint),row['state'])).fetchall()
        if len(masters)!=1:continue
        db.execute('''INSERT OR IGNORE INTO project_geological_relation
          (project_id,entity_id,relation_type,decision_status,source_ref,updated_at)
          VALUES(?,?,'PART_OF_PROJECT','PROPOSED_ONLY','SOURCE_PROJECT_HINT',?)''',
          (masters[0]['project_id'],row['entity_id'],utc()))
        proposed+=1
    return proposed


def stable_approved_project_id(candidate_id):
    """Order-independent numeric ID for a source candidate with approved Project evidence.

    Explicit human-assigned project IDs are respected instead. The source
    candidate_id must be stable across rebuilds; conflicting occupied IDs
    remain blocked, never silently reassigned.
    """
    suffix=int(digest(['APPROVED_PROJECT_V1',candidate_id])[:15],16) % 10**12
    return f'AU-REE-{suffix:012d}'


def independently_approved_project(db, project_id, *, root=None):
    """Check the independent Project identity, not only a scored/GIS review.

    A legacy or merely named Project has no admitted development identity.
    Release requires the approved source Project candidate, a matching stable
    master ID and a currently verifiable original approval document.
    """
    row=db.execute('''SELECT p.project_id,p.state,p.population_status,
        p.identity_source,c.candidate_id,c.entity_level,c.state AS source_state,
        i.review_status,i.review_decision,i.resolved_project_id,i.approval_ref,
        i.source_url,i.source_sha256
        FROM project_master p
        JOIN population_candidates c ON p.identity_source='APPROVED_CANDIDATE:' || c.candidate_id
        JOIN identity_review_decisions i ON i.candidate_id=c.candidate_id
        WHERE p.project_id=?''',(project_id,)).fetchone()
    return bool(row and row['population_status']=='EVIDENCE_BACKED_PROJECT'
        and row['entity_level']=='PROJECT' and row['state']==row['source_state']
        and row['review_status']=='DOCUMENT_APPROVED'
        and row['review_decision'] in ('APPROVE_NEW_PROJECT','CONFIRM_LEGACY_PROJECT')
        and row['resolved_project_id']==row['project_id']
        and verify(db,row['approval_ref'],'PROJECT_REVIEW',
                   row['source_url'],row['source_sha256'],root=root))


def apply_identity_decisions(db,root,freeze_date):
    """Only an independently APPROVED archived document may create/link a Project."""
    path=Path(root)/'inputs'/'project_identity_decisions.csv'
    decisions=readcsv(path) if path.exists() else []
    candidate_ids=[(r.get('candidate_id') or '').strip() for r in decisions]
    if len(candidate_ids)!=len(set(candidate_ids)):
        raise ValueError('Duplicate candidate_id in Project identity decision ledger')
    # Approve independent Project parents before resolving child/source links.
    # Otherwise the lexical candidate_id order controls whether an otherwise
    # valid, same-batch Project–Deposit relationship is accepted.
    order={'APPROVE_NEW_PROJECT':0,'CONFIRM_LEGACY_PROJECT':0,'LINK_EXISTING_PROJECT':1}
    rows=sorted(decisions,key=lambda r:(
        order.get((r.get('decision') or '').strip().upper(),2),
        r.get('candidate_id','')
    ))
    # Revocation is fail-closed, but preserves prior audit and canonical IDs.
    db.execute("UPDATE project_master SET population_status='IDENTITY_APPROVAL_EXPIRED', activity='UNKNOWN', lifecycle='UNKNOWN', ree_role='REE_UNCONFIRMED' WHERE identity_source LIKE 'APPROVED_CANDIDATE:%'")
    db.execute("UPDATE project_geological_relation SET decision_status='APPROVAL_EXPIRED' WHERE approval_ref IS NOT NULL")
    db.execute("UPDATE population_candidates SET decision='REVIEW',reason='IDENTITY_APPROVAL_RECHECK',matched_project_id=NULL WHERE decision='APPROVED_PROJECT_IDENTITY'")
    stats={'approved_new':0,'confirmed_legacy':0,'linked_existing':0,'rejected_or_pending':0}
    for r in rows:
        cid=(r.get('candidate_id') or '').strip()
        action=(r.get('decision') or '').strip().upper()
        candidate=db.execute('SELECT * FROM population_candidates WHERE candidate_id=?',(cid,)).fetchone()
        ref=(r.get('approval_ref') or '').strip()
        source=(r.get('source_url') or '').strip()
        sha=(r.get('source_sha256') or '').strip()
        evidence_date=(r.get('evidence_date') or '').strip()
        try:
            evidence_day=date.fromisoformat(evidence_date)
            cutoff_day=date.fromisoformat(str(freeze_date))
        except ValueError:
            evidence_day=cutoff_day=None
        valid=bool(candidate and action in ('APPROVE_NEW_PROJECT','CONFIRM_LEGACY_PROJECT','LINK_EXISTING_PROJECT')
          and evidence_day is not None and cutoff_day is not None
          and evidence_day<=cutoff_day and verify(db,ref,'PROJECT_REVIEW',source,sha,root=root))
        if candidate is None:
            event(db,'population',cid,'UNKNOWN_IDENTITY_CANDIDATE','No matching source feature')
            stats['rejected_or_pending']+=1
            continue
        pid=(r.get('project_id') or '').strip()
        project_name=(r.get('project_name') or '').strip()
        reason='EVIDENCE_APPROVED' if valid else 'INDEPENDENT_DOCUMENT_APPROVAL_REQUIRED'
        if valid and not candidate['state']:valid=False;reason='STATE_REQUIRED'
        if valid and action in ('APPROVE_NEW_PROJECT','CONFIRM_LEGACY_PROJECT') and candidate['entity_level']!='PROJECT':
            valid=False;reason='SOURCE_ENTITY_IS_NOT_A_PROJECT'
        if valid and action=='APPROVE_NEW_PROJECT':
            if not project_name:valid=False;reason='PROJECT_NAME_REQUIRED'
            else:
                existing=db.execute('SELECT project_id,identity_source FROM project_master WHERE normalized_name=? AND state=?',
                    (norm(project_name),candidate['state'])).fetchone()
                if existing and existing['identity_source']!='APPROVED_CANDIDATE:'+cid:
                    valid=False;reason='POSSIBLE_EXISTING_PROJECT_USE_LINK_REVIEW'
            if valid:
                prior=db.execute('SELECT resolved_project_id FROM identity_review_decisions WHERE candidate_id=?',(cid,)).fetchone()
                prior_id=prior['resolved_project_id'] if prior else None
                # Only a Project owned by this approved source candidate can
                # establish a historical ID. Unapproved input must never pin it.
                owner=(db.execute('SELECT identity_source FROM project_master WHERE project_id=?',(prior_id,)).fetchone()
                       if prior_id else None)
                trusted_prior=prior_id if owner and owner['identity_source']=='APPROVED_CANDIDATE:'+cid else None
                if trusted_prior and pid and pid!=trusted_prior:
                    valid=False;reason='STABLE_PROJECT_ID_CHANGE_REQUIRES_CORRECTION'
                if trusted_prior:
                    pid=trusted_prior
                elif not pid:
                    pid=stable_approved_project_id(cid)
                if valid:
                    occupied=db.execute('SELECT identity_source FROM project_master WHERE project_id=?',(pid,)).fetchone()
                    if occupied and occupied['identity_source']!='APPROVED_CANDIDATE:'+cid:
                        valid=False;reason='PROJECT_ID_ALREADY_OCCUPIED'
                    elif not occupied:
                        db.execute('''INSERT INTO project_master(project_id,canonical_name,normalized_name,state,
                          population_status,identity_source,updated_at) VALUES(?,?,?,?,'EVIDENCE_BACKED_PROJECT',?,?)''',
                          (pid,project_name,norm(project_name),candidate['state'],'APPROVED_CANDIDATE:'+cid,utc()))
                    else:
                        db.execute("UPDATE project_master SET population_status='EVIDENCE_BACKED_PROJECT',updated_at=? WHERE project_id=? AND identity_source=?",
                                   (utc(),pid,'APPROVED_CANDIDATE:'+cid))
                if valid:stats['approved_new']+=1
        elif valid and action=='CONFIRM_LEGACY_PROJECT':
            # A signed issuer report may verify an existing historical Project
            # without creating a duplicate Project or changing its stable ID.
            # This is an explicit correction, never an automatic name merge.
            master=db.execute('''SELECT project_id,canonical_name,normalized_name,state,
                population_status,identity_source FROM project_master WHERE project_id=?''',
                (pid,)).fetchone()
            prior=db.execute('SELECT resolved_project_id FROM identity_review_decisions WHERE candidate_id=?',
                             (cid,)).fetchone()
            prior_id=prior['resolved_project_id'] if prior else None
            if not pid or not master:
                valid=False;reason='LEGACY_PROJECT_ID_REQUIRED'
            elif master['state']!=candidate['state']:
                valid=False;reason='LEGACY_PROJECT_STATE_CONFLICT'
            elif not project_name or norm(project_name)!=master['normalized_name']:
                valid=False;reason='LEGACY_PROJECT_SCOPE_NAME_REQUIRES_REVIEW'
            elif prior_id and prior_id!=pid:
                valid=False;reason='STABLE_LEGACY_PROJECT_ID_CHANGE_REQUIRES_CORRECTION'
            elif not db.execute('SELECT 1 FROM legacy_id_map WHERE project_id=?',(pid,)).fetchone():
                valid=False;reason='LEGACY_PROVENANCE_MAPPING_MISSING'
            elif master['identity_source'] not in ('legacy_r963_frozen','APPROVED_CANDIDATE:'+cid):
                valid=False;reason='LEGACY_PROJECT_ALREADY_CLAIMED_OR_NOT_LEGACY'
            elif master['population_status'] not in ('LEGACY_UNVERIFIED',
                                                       'IDENTITY_APPROVAL_EXPIRED'):
                valid=False;reason='LEGACY_PROJECT_STATUS_CONFLICT'
            else:
                db.execute('''UPDATE project_master SET population_status='EVIDENCE_BACKED_PROJECT',
                    identity_source=?,updated_at=? WHERE project_id=?''',
                    ('APPROVED_CANDIDATE:'+cid,utc(),pid))
                event(db,'population',pid,'LEGACY_PROJECT_IDENTITY_CONFIRMED',
                      json.dumps({'candidate_id':cid,'approval_ref':ref,
                                  'prior_identity_source':master['identity_source']},
                                 ensure_ascii=False))
                stats['confirmed_legacy']+=1
        elif valid and action=='LINK_EXISTING_PROJECT':
            old=db.execute('SELECT resolved_project_id FROM identity_review_decisions WHERE candidate_id=?',
                           (cid,)).fetchone()
            if old and old['resolved_project_id'] and old['resolved_project_id']!=pid:
                valid=False;reason='STABLE_PROJECT_LINK_CHANGE_REQUIRES_CORRECTION'
            master=db.execute('''SELECT project_id,state,population_status,identity_source
                FROM project_master WHERE project_id=?''',(pid,)).fetchone()
            if not valid:
                pass  # A prior independently approved link cannot be silently moved.
            elif not master or master['state']!=candidate['state']:
                valid=False;reason='PROJECT_MISSING_OR_STATE_CONFLICT'
            elif (master['population_status']!='EVIDENCE_BACKED_PROJECT'
                  or not str(master['identity_source'] or '').startswith('APPROVED_CANDIDATE:')):
                valid=False;reason='PARENT_PROJECT_IDENTITY_NOT_INDEPENDENTLY_APPROVED'
            elif candidate['entity_level']!='PROJECT' and not db.execute(
                  'SELECT 1 FROM geological_entity_source WHERE candidate_id=?',(cid,)).fetchone():
                valid=False;reason='GEOLOGICAL_ENTITY_SOURCE_MISSING'
            else:
                stats['linked_existing']+=1
        if valid:
            db.execute("UPDATE population_candidates SET decision='APPROVED_PROJECT_IDENTITY',reason='DOCUMENT_APPROVED',matched_project_id=? WHERE candidate_id=?",(pid,cid))
            if action=='LINK_EXISTING_PROJECT' and candidate['entity_level']!='PROJECT':
                er=db.execute('SELECT entity_id FROM geological_entity_source WHERE candidate_id=?',(cid,)).fetchone()
                if er:
                    db.execute('''INSERT INTO project_geological_relation(project_id,entity_id,relation_type,
                      decision_status,source_ref,approval_ref,updated_at) VALUES(?,?,'PART_OF_PROJECT',
                      'DOCUMENT_APPROVED',?,?,?) ON CONFLICT(project_id,entity_id) DO UPDATE SET
                      decision_status='DOCUMENT_APPROVED',source_ref=excluded.source_ref,
                      approval_ref=excluded.approval_ref,updated_at=excluded.updated_at''',(pid,er['entity_id'],source,ref,utc()))
            elif candidate['entity_level']=='PROJECT':
                db.execute('''INSERT OR IGNORE INTO project_aliases(project_id,alias,normalized_alias,source_key,native_id)
                  VALUES(?,?,?,?,?)''',(pid,candidate['raw_name'],candidate['normalized_name'],candidate['source_key'],candidate['native_id'] or ''))
        else:stats['rejected_or_pending']+=1
        db.execute('''INSERT INTO identity_review_decisions(candidate_id,review_decision,approval_ref,
          source_url,source_sha256,review_status,resolved_project_id,review_reason,reviewed_at)
          VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(candidate_id) DO UPDATE SET
          review_decision=excluded.review_decision,approval_ref=excluded.approval_ref,
          source_url=excluded.source_url,source_sha256=excluded.source_sha256,
          review_status=excluded.review_status,review_reason=excluded.review_reason,
          resolved_project_id=CASE WHEN excluded.review_status='DOCUMENT_APPROVED'
            THEN excluded.resolved_project_id ELSE identity_review_decisions.resolved_project_id END,
          reviewed_at=excluded.reviewed_at''',(cid,action,ref,source,sha,
          'DOCUMENT_APPROVED' if valid else 'REVIEW_PENDING',pid if valid else None,reason,utc()))
        if not valid:event(db,'population',cid,'IDENTITY_DECISION_REJECTED',reason)
    return stats
