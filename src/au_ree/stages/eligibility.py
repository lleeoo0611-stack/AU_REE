"""04: evidence coverage and explicit global-vs-subset GIS release gates.

G0 requires all frozen r974 baseline alternatives to have four approved GIS
layers. R1/S1/RS are separately labelled subset analyses: every member of the
independently eligible non-spatial candidate subgroup needs approved GIS, and
at least two alternatives are required before a subset can be released.
"""
from __future__ import annotations
import json,math
from ..core import readcsv,utc,digest

GIS_CODES={'road':'I1','rail':'I2','power':'I3','port':'I4'}


def _gis_complete(db,pid):
    coord=db.execute('''SELECT c.verification,c.source_url,pr.approval_ref,pr.source_sha256
            FROM project_coordinates c JOIN approved_project_reviews pr ON pr.project_id=c.project_id
            WHERE c.project_id=?''',(pid,)).fetchone()
    if not coord or coord['verification']!='VERIFIED':return False
    # A coordinate update must originate in an independently approved project review.
    review=db.execute('''SELECT 1 FROM evidence_approvals a JOIN source_documents d
                  ON d.document_id=a.document_id WHERE a.approval_ref=? AND a.record_type='PROJECT_REVIEW'
                  AND a.status='APPROVED' AND d.actual_sha256=? AND d.source_url=?''',
                  (coord['approval_ref'],coord['source_sha256'],coord['source_url'])).fetchone()
    if not review:return False
    for layer,criterion in GIS_CODES.items():
        result=db.execute('''SELECT m.distance_km,m.status,m.source_sha256,m.geometry_sha256,m.source_url,
                                s.verified,s.fingerprint,s.source_url AS layer_url
            FROM gis_metrics m JOIN gis_sources s ON s.layer=?
            WHERE m.project_id=? AND m.criterion=?''',(layer,pid,criterion)).fetchone()
        if not (result and result['status']=='VERIFIED' and result['verified']==1
                and result['distance_km'] is not None and math.isfinite(result['distance_km'])
                and result['distance_km']>=0 and result['geometry_sha256']
                and result['source_sha256'] and result['source_sha256']==result['fingerprint']
                and result['source_url']==result['layer_url']):return False
        approved=db.execute('''SELECT 1 FROM evidence_approvals a JOIN source_documents d ON d.document_id=a.document_id
                 WHERE a.record_type='GIS_LAYER' AND a.status='APPROVED' AND d.source_url=?
                 AND d.actual_sha256=? AND d.hash_status='HASH_MATCH_REVIEW_REQUIRED' LIMIT 1''',
                 (result['source_url'],result['source_sha256'])).fetchone()
        if not approved:return False
    return True


def _global_ids(db,root):
    """Fixed historic pre-FID decision cohort; never infer the denominator from available GIS."""
    fp=root/'inputs'/'legacy_r974_frozen_alternatives.csv'
    ids=[]
    if not fp.exists():return []
    for row in readcsv(fp):
        legacy=row.get('project_id')
        ref=db.execute('SELECT project_id FROM legacy_id_map WHERE legacy_id=?',(legacy,)).fetchone()
        if ref:ids.append(ref['project_id'])
    return sorted(set(ids))


def run(db,ctx):
    cfg=ctx['eligibility'];crit={x['code']:dict(x) for x in db.execute('SELECT * FROM criteria')}
    db.execute('DELETE FROM coverage');db.execute('DELETE FROM eligibility');db.execute('DELETE FROM gis_release_gates')
    projects=[dict(x) for x in db.execute('SELECT * FROM project_master ORDER BY project_id')]
    coverage_rows=[];summary_rows=[];scenario_rows={s:[] for s in cfg['scenarios']}
    records_by_pid={};base_by_pid={};gis_by_pid={}
    for p in projects:
        pid=p['project_id'];values={x['criterion']:dict(x) for x in db.execute('SELECT * FROM criterion_values WHERE project_id=?',(pid,))}
        records={}
        for code,cc in crit.items():
            x=values.get(code);value=x['value'] if x else None
            good=bool(x and x['quality']=='VERIFIED' and value is not None and math.isfinite(value))
            if cc['basis']=='DIRECT_TREO':good=good and bool(x and x['basis']=='DIRECT_TREO')
            if cc['basis']=='DIRECT_MAGNET_REO_SHARE':good=good and bool(x and x['basis']=='DIRECT_MAGNET_REO_SHARE')
            if code in GIS_CODES.values():good=good and bool(_gis_complete(db,pid))
            reason='OK' if good else (x.get('issue') if x else 'NO_OBSERVATION') or 'UNVERIFIED'
            if code in GIS_CODES.values() and not good:reason='GIS_SOURCE_OR_COHORT_APPROVAL_PENDING'
            records[code]={'value':value if good else None,'good':good,'domain':cc['domain'],'reason':reason}
            db.execute('INSERT INTO coverage(project_id,criterion,domain,status,value,quality,reason) VALUES(?,?,?,?,?,?,?)',
                       (pid,code,cc['domain'],'PRESENT' if good else 'MISSING',value if good else None,'VERIFIED' if good else 'UNVERIFIED',reason))
            coverage_rows.append({'project_id':pid,'project_name':p['canonical_name'],'criterion':code,'domain':cc['domain'],
                                  'status':'PRESENT' if good else 'MISSING','value':value if good else '','reason':reason})
        records_by_pid[pid]=records;gis_by_pid[pid]=_gis_complete(db,pid)
        base=[]
        if p['country']!='Australia':base.append('G1_NON_AUSTRALIA')
        if p['ree_role'] not in ('REE_PRIMARY','REE_COPRODUCT','REE_BYPRODUCT'):base.append('G3_REE_MATERIALITY_UNCONFIRMED')
        if (p['activity'] or '').upper() not in cfg['activity_allow']:base.append('G4_NOT_CONFIRMED_ACTIVE')
        life=(p['lifecycle'] or '').upper()
        if life not in cfg['stage_allow']:base.append('G5_NOT_PRE_FID_SCOPING_TO_DFS')
        if any(x in life for x in cfg['exclude_stages']):base.append('G5_FID_OR_OPERATIONAL')
        location=db.execute('SELECT verification FROM project_coordinates WHERE project_id=?',(pid,)).fetchone()
        if p['latitude'] is None or p['longitude'] is None or not location or location['verification']!='VERIFIED':base.append('G7_NO_VERIFIED_LOCATION')
        if not db.execute('SELECT 1 FROM approved_project_reviews WHERE project_id=?',(pid,)).fetchone():base.append('G8_PROJECT_REVIEW_APPROVAL_PENDING')
        resource=db.execute('''SELECT 1 FROM observations o JOIN evidence_links l ON l.record_type='OBSERVATION' AND l.record_id=o.obs_id
             JOIN evidence_approvals a ON a.approval_ref=l.approval_ref AND a.status='APPROVED'
             WHERE o.project_id=? AND ((o.variable='resource_standard' AND UPPER(COALESCE(o.text_value,'')) LIKE '%JORC%')
             OR (o.variable='jorc_resource_present' AND o.numeric_value=1)) AND o.verification='VERIFIED' LIMIT 1''',(pid,)).fetchone()
        if not resource:base.append('G6_JORC_RESOURCE_EVIDENCE_PENDING')
        base_by_pid[pid]=base

    allids=_global_ids(db,ctx['root']);minimum=int(cfg.get('minimum_subset_size',2))
    gate={}
    for scenario,sc in cfg['scenarios'].items():
        if scenario==cfg.get('global_scenario','G0_BASELINE'):
            scope='GLOBAL_FROZEN_19'
            cohort=allids
            expected=int(cfg.get('global_cohort_expected_count',19))
            consistent=(len(cohort)==expected)
            reason='GLOBAL_COHORT_COUNT_MISMATCH' if not consistent else 'NOT_ALL_GLOBAL_GIS_APPROVED'
            if consistent and all(gis_by_pid.get(pid,False) for pid in cohort):
                # v1.0.1 R exporter only supports complete point matrices.
                # Never publish a small point subset under the GLOBAL baseline label.
                matrix_complete=all(not base_by_pid.get(pid) and all(records_by_pid[pid][k]['good'] for k in sc['criteria']) for pid in cohort)
                if not matrix_complete:
                    consistent=False
                    reason='GLOBAL_POINT_MATRIX_INCOMPLETE'
        else:
            scope='SUBSET_ONLY'
            non_gis=[k for k in sc.get('requires',[]) if k not in GIS_CODES.values()]
            cohort=sorted(pid for pid in base_by_pid if not base_by_pid[pid]
                          and all(records_by_pid[pid][k]['good'] for k in non_gis))
            consistent=len(cohort)>=minimum
            reason='SUBSET_BELOW_MINIMUM_N' if not consistent else 'SUBSET_GIS_APPROVAL_INCOMPLETE'
        done=sum(bool(gis_by_pid.get(pid)) for pid in cohort)
        released=bool(consistent and done==len(cohort))
        status=('RELEASED_GLOBAL' if scope.startswith('GLOBAL') else 'RELEASED_SUBSET') if released else 'BLOCKED'
        reason='ALL_MEMBERS_GIS_APPROVED' if released else reason
        gate[scenario]={'scope':scope,'cohort_size':len(cohort),'gis_complete':done,
                        'status':status,'reason':reason,'cohort_sha256':digest(cohort)}
        db.execute('''INSERT INTO gis_release_gates(scenario,scope,cohort_size,gis_complete,status,cohort_sha256,reason,evaluated_at)
                      VALUES(?,?,?,?,?,?,?,?)''',(scenario,scope,len(cohort),done,status,digest(cohort),reason,utc()))

    per_scenario={s:{'eligible':0,'point_ready':0,'total':len(projects),'gis_gate':gate[s]} for s in cfg['scenarios']}
    for p in projects:
        pid=p['project_id'];records=records_by_pid[pid]
        summary={'project_id':pid,'project_name':p['canonical_name'],'state':p['state'],
                 'activity':p['activity'],'lifecycle':p['lifecycle'],'deposit_family':p['deposit_family']}
        for scenario,sc in cfg['scenarios'].items():
            columns=sc['criteria'];ready=sum(records[k]['good'] for k in columns)
            rate=ready/len(columns);domains=len({records[k]['domain'] for k in columns if records[k]['good']})
            reasons=list(base_by_pid[pid])
            if scenario==cfg.get('global_scenario','G0_BASELINE') and pid not in allids:
                reasons.append('NOT_IN_GLOBAL_FROZEN_COHORT')
            if gate[scenario]['status']=='BLOCKED':reasons.append('GIS_RELEASE_'+gate[scenario]['reason'])
            for key in sc.get('requires',[]):
                if not records[key]['good']:reasons.append('MANDATORY_'+key+'_MISSING')
            if rate < cfg['minimum_coverage_fraction']:reasons.append('COVERAGE_BELOW_THRESHOLD')
            if domains < min(cfg['minimum_domain_count'],len({crit[k]['domain'] for k in columns})):
                reasons.append('INSUFFICIENT_DOMAIN_COVERAGE')
            eligible=int(not reasons)
            point_ready=int(bool(eligible and all(records[k]['good'] for k in columns)))
            db.execute('INSERT INTO eligibility(project_id,scenario,eligible,point_ready,coverage_fraction,domain_count,reasons_json,evaluated_at) VALUES(?,?,?,?,?,?,?,?)',
                       (pid,scenario,eligible,point_ready,rate,domains,json.dumps(reasons),utc()))
            per_scenario[scenario]['eligible']+=eligible;per_scenario[scenario]['point_ready']+=point_ready
            summary[f'{scenario}_eligible']=eligible;summary[f'{scenario}_point_ready']=point_ready
            summary[f'{scenario}_coverage_pct']=round(rate*100,1);summary[f'{scenario}_reason']=';'.join(reasons)
            if point_ready:
                scenario_rows[scenario].append({**{k:summary.get(k) for k in ['project_id','project_name','state','lifecycle','deposit_family']},
                                               **{k:records[k]['value'] for k in columns}})
        summary_rows.append(summary)
    ctx['artifacts']['gis_release_gates.csv']=([dict(x) for x in db.execute('SELECT * FROM gis_release_gates ORDER BY scenario')],
        ['scenario','scope','cohort_size','gis_complete','status','cohort_sha256','reason','evaluated_at'])
    ctx['artifacts']['mcda_eligibility_long.csv']=([dict(x) for x in db.execute('SELECT * FROM eligibility ORDER BY project_id,scenario')],
        ['project_id','scenario','eligible','point_ready','coverage_fraction','domain_count','reasons_json','evaluated_at'])
    ctx['artifacts']['mcda_alternatives.csv']=([{'project_id':e['project_id'],'project_name':p['canonical_name'],'scenario':e['scenario'],
        'point_ready':e['point_ready'],'coverage_fraction':e['coverage_fraction']} for e in db.execute('SELECT * FROM eligibility WHERE eligible=1 ORDER BY scenario,project_id')
        for p in db.execute('SELECT canonical_name FROM project_master WHERE project_id=?',(e['project_id'],))],
        ['project_id','project_name','scenario','point_ready','coverage_fraction'])
    ctx['artifacts']['alternatives_completeness.csv']=(summary_rows,list(summary_rows[0]) if summary_rows else ['project_id','project_name'])
    ctx['artifacts']['criterion_coverage_long.csv']=(coverage_rows,['project_id','project_name','criterion','domain','status','value','reason'])
    for scenario,rows in scenario_rows.items():
        ctx['artifacts'][f'matrix_{scenario}.csv']=(rows,['project_id','project_name','state','lifecycle','deposit_family',*cfg['scenarios'][scenario]['criteria']])
    return {'projects_audited':len(projects),'scenarios':per_scenario,'status':'MCDA_ELIGIBILITY_AUDITED'}
