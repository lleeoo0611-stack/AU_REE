"""v1.0.1 release and provenance regression tests. All fixtures are synthetic.
No external HTTP or real project status is used in these tests.
"""
from __future__ import annotations
import csv,hashlib,json,sqlite3
from pathlib import Path
import pytest
from au_ree.core import connect,setup
from au_ree.evidence import reload_registry,verify
from au_ree.stages.criteria import ingest,derive_metrics
from au_ree.stages.eligibility import run as eligibility_run
from au_ree.stages.gis import run as gis_run

ROOT=Path(__file__).resolve().parents[1]
CRITERIA=json.loads((ROOT/'config/criteria.json').read_text())
ELIGIBILITY=json.loads((ROOT/'config/eligibility.json').read_text())


def csvwrite(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def build_registry(tmp_path, count=2):
    archive=tmp_path/'inputs'/'evidence';archive.mkdir(parents=True,exist_ok=True)
    docs=[];approvals=[]
    def add(document_id,data,url,refs):
        file=archive/(document_id+'.json');file.write_bytes(data)
        sha=hashlib.sha256(data).hexdigest()
        docs.append({'document_id':document_id,'file_path':f'inputs/evidence/{document_id}.json','source_url':url,'sha256':sha})
        for ref,typ in refs:
            approvals.append({'approval_ref':ref,'record_type':typ,'document_id':document_id,
                             'reviewer':'synthetic reviewer A','decision':'APPROVED','reviewed_at':'2026-10-15','notes':'synthetic isolated fixture'})
        return sha
    url='https://example.gov.au/synthetic-report'
    sha=add('report',b'SYNTHETIC REE study, JORC disclosure',url,
            [(f'project-{i}','PROJECT_REVIEW') for i in range(count)]+[(f'obs-{i}','OBSERVATION') for i in range(count)])
    layers={}
    for layer in ('road','rail','power','port'):
        geo=json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point',
                    'coordinates':[120,-25]},'properties':{'synthetic':layer}}]},sort_keys=True).encode()
        layurl=f'https://example.gov.au/synthetic-{layer}'
        layers[layer]={'sha':add(layer,geo,layurl,[(f'layer-{layer}','GIS_LAYER')]),'url':layurl,
                       'path':f'inputs/evidence/{layer}.json','ref':f'layer-{layer}'}
    csvwrite(tmp_path/'inputs'/'source_documents.csv',docs,['document_id','file_path','source_url','sha256'])
    csvwrite(tmp_path/'inputs'/'evidence_approvals.csv',approvals,
             ['approval_ref','record_type','document_id','reviewer','decision','reviewed_at','notes'])
    return sha,url,layers


def seed_projects(db,tmp_path,active=2,total=19):
    sha,url,layers=build_registry(tmp_path,active)
    with (tmp_path/'inputs'/'legacy_r974_frozen_alternatives.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['project_id']);w.writerows([[f'LEG-{i}'] for i in range(total)])
    for c in CRITERIA['criteria']:
        db.execute('INSERT INTO criteria(code,domain,label,direction,unit,basis,mandatory,description,config_version) VALUES(?,?,?,?,?,?,?,?,?)',
                   (c['code'],c['domain'],c['name'],c['direction'],c['unit'],c['basis'],0,'','v1.0.1-test'))
    reload_registry(db,tmp_path,'2026-10-29')
    for layer,item in layers.items():
        db.execute('INSERT INTO gis_sources(layer,source_url,source_type,verified,fingerprint,status,queried_at) VALUES(?,?,?,?,?,?,?)',
                   (layer,item['url'],'local_geojson',1,item['sha'],'APPROVED_ARCHIVED_LAYER','now'))
    for i in range(total):
        pid=f'AU-REE-TEST{i:02d}'
        cid=f'SYNTHETIC-PROJECT-{i}'
        verified=i<active
        db.execute('INSERT INTO legacy_id_map(legacy_id,project_id) VALUES(?,?)',(f'LEG-{i}',pid))
        db.execute('''INSERT INTO project_master(project_id,canonical_name,normalized_name,state,country,
                    latitude,longitude,activity,lifecycle,ree_role,deposit_family,population_status,identity_source)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                   (pid,f'Synthetic project {i}',f'synthetic project {i}','WA','Australia',-25,120,
                    'ACTIVE' if verified else 'UNKNOWN','PFS' if verified else 'UNKNOWN',
                    'REE_PRIMARY' if verified else 'REE_UNCONFIRMED','HARD_ROCK',
                    'EVIDENCE_BACKED_PROJECT' if verified else 'CENSUS',
                    ('APPROVED_CANDIDATE:'+cid) if verified else None))
        if i>=active:continue
        # These are isolated synthetic independent identity decisions, not
        # human signoffs in the real Australian Census.
        db.execute('''INSERT INTO population_candidates(candidate_id,source_key,native_id,raw_name,
                    normalized_name,state,entity_level) VALUES(?,?,?,?,?,?,?)''',
                   (cid,'SYNTHETIC',str(i),f'Synthetic project {i}',f'synthetic project {i}','WA','PROJECT'))
        db.execute('''INSERT INTO identity_review_decisions(candidate_id,review_decision,approval_ref,
                    source_url,source_sha256,review_status,resolved_project_id,review_reason,reviewed_at)
                    VALUES(?, 'APPROVE_NEW_PROJECT',?,?,?,'DOCUMENT_APPROVED',?,'EVIDENCE_APPROVED',?)''',
                   (cid,f'project-{i}',url,sha,pid,'2026-10-15'))
        db.execute('INSERT INTO project_coordinates(project_id,latitude,longitude,verification,source_url) VALUES(?,?,?,?,?)',
                   (pid,-25,120,'VERIFIED',url))
        db.execute('INSERT INTO approved_project_reviews(project_id,approval_ref,source_sha256) VALUES(?,?,?)',(pid,f'project-{i}',sha))
        db.execute('INSERT INTO observations(obs_id,project_id,variable,numeric_value,source_url,source_sha256,verification) VALUES(?,?,?,?,?,?,?)',
                   (f'jorc-{i}',pid,'jorc_resource_present',1,url,sha,'VERIFIED'))
        db.execute("INSERT INTO evidence_links(record_type,record_id,approval_ref) VALUES('OBSERVATION',?,?)",(f'jorc-{i}',f'obs-{i}'))
        for c in CRITERIA['criteria']:
            db.execute('INSERT INTO criterion_values(project_id,criterion,value,unit,basis,quality,issue) VALUES(?,?,?,?,?,?,?)',
                       (pid,c['code'],2.0,c['unit'],c['basis'],'VERIFIED',''))
        for layer,criterion in [('road','I1'),('rail','I2'),('power','I3'),('port','I4')]:
            item=layers[layer]
            db.execute('INSERT INTO gis_metrics(project_id,criterion,distance_km,method,source_url,source_sha256,geometry_sha256,status) VALUES(?,?,?,?,?,?,?,?)',
                       (pid,criterion,10.0,'synthetic projected',item['url'],item['sha'],hashlib.sha256(layer.encode()).hexdigest(),'VERIFIED'))
    return sha,url,layers


def test_registry_rejects_self_claims_tampering_future_reviews(tmp_path):
    sha,url,layers=build_registry(tmp_path,1)
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    result=reload_registry(db,tmp_path,'2026-10-29')
    assert result['approved']==6 and result['hash_matched']==5
    assert verify(db,'obs-0','OBSERVATION',url,sha)
    assert not verify(db,'obs-0','OBSERVATION',url,'0'*64)
    assert not verify(db,'project-0','OBSERVATION',url,sha)
    path=tmp_path/'inputs'/'evidence'/'report.json';path.write_bytes(b'TAMPERED BYTES')
    result=reload_registry(db,tmp_path,'2026-10-29')
    assert result['approved']==4
    assert not verify(db,'obs-0','OBSERVATION',url,sha)
    path.write_bytes(b'SYNTHETIC REE study, JORC disclosure')
    file=tmp_path/'inputs'/'evidence_approvals.csv'
    rows=list(csv.DictReader(file.open()))
    for r in rows:
        if r['approval_ref']=='obs-0':r['reviewed_at']='2027-01-01'
    csvwrite(file,rows,list(rows[0]))
    reload_registry(db,tmp_path,'2026-10-29')
    assert not verify(db,'obs-0','OBSERVATION',url,sha)
    db.close()


def test_claimed_verified_does_not_score_without_independent_approval(tmp_path):
    sha,url,_=build_registry(tmp_path,1)
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,population_status) VALUES('P1','Synthetic','synthetic','CENSUS')")
    reload_registry(db,tmp_path,'2026-10-29')
    base={'project_id':'P1','variable':'ore_mt','numeric_value':'10','basis':'DIRECT_TREO','source_url':url,
          'source_sha256':sha,'verification':'VERIFIED','effective_date':'2026-10-01'}
    assert ingest(db,[base],'researcher_updates','2026-10-29')==1
    assert db.execute('SELECT verification FROM observations').fetchone()[0]=='REVIEW_PENDING'
    assert db.execute('SELECT count(*) FROM evidence_links').fetchone()[0]==0
    assert ingest(db,[{**base,'approval_ref':'obs-0'}],'researcher_updates','2026-10-29')==1
    assert db.execute('SELECT verification FROM observations').fetchone()[0]=='VERIFIED'
    assert db.execute('SELECT count(*) FROM evidence_links').fetchone()[0]==1
    db.close()


def test_gis_full_global_blocked_but_verified_two_project_subset_released(tmp_path):
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    seed_projects(db,tmp_path,active=2)
    ctx={'root':tmp_path,'eligibility':ELIGIBILITY,'artifacts':{}}
    result=eligibility_run(db,ctx)
    assert result['scenarios']['G0_BASELINE']['gis_gate']['cohort_size']==19
    assert result['scenarios']['G0_BASELINE']['gis_gate']['gis_complete']==2
    assert result['scenarios']['G0_BASELINE']['gis_gate']['status']=='BLOCKED'
    assert result['scenarios']['R1_STRICT']['gis_gate']['scope']=='SUBSET_ONLY'
    assert result['scenarios']['R1_STRICT']['gis_gate']['status']=='RELEASED_SUBSET'
    assert result['scenarios']['R1_STRICT']['point_ready']==2
    assert len(ctx['artifacts']['matrix_R1_STRICT.csv'][0])==2
    assert not ctx['artifacts']['matrix_G0_BASELINE.csv'][0]
    db.close()


def test_missing_approval_for_one_layer_revokes_subset_and_matrix(tmp_path):
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    seed_projects(db,tmp_path,active=2)
    db.execute("UPDATE evidence_approvals SET status='NOT_APPROVED' WHERE approval_ref='layer-power'")
    ctx={'root':tmp_path,'eligibility':ELIGIBILITY,'artifacts':{}}
    out=eligibility_run(db,ctx)
    assert out['scenarios']['R1_STRICT']['gis_gate']['status']=='BLOCKED'
    assert out['scenarios']['R1_STRICT']['point_ready']==0
    assert not ctx['artifacts']['matrix_R1_STRICT.csv'][0]
    db.close()


def test_global_requires_all_nineteen_point_ready_even_with_all_gis(tmp_path):
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    seed_projects(db,tmp_path,active=19)
    ctx={'root':tmp_path,'eligibility':ELIGIBILITY,'artifacts':{}}
    out=eligibility_run(db,ctx)
    assert out['scenarios']['G0_BASELINE']['gis_gate']['status']=='RELEASED_GLOBAL'
    assert len(ctx['artifacts']['matrix_G0_BASELINE.csv'][0])==19
    db.execute("DELETE FROM criterion_values WHERE project_id='AU-REE-TEST18' AND criterion='T2'")
    out=eligibility_run(db,{'root':tmp_path,'eligibility':ELIGIBILITY,'artifacts':{}})
    assert out['scenarios']['G0_BASELINE']['gis_gate']['status']=='BLOCKED'
    assert out['scenarios']['G0_BASELINE']['gis_gate']['reason']=='GLOBAL_POINT_MATRIX_INCOMPLETE'
    db.close()


def test_offline_gis_local_layer_requires_document_approval(tmp_path):
    sha,url,layers=build_registry(tmp_path,1)
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    reload_registry(db,tmp_path,'2026-10-29')
    db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,latitude,longitude,population_status) VALUES('P1','Synthetic','synthetic',-25,120,'CENSUS')")
    db.execute('INSERT INTO project_coordinates(project_id,latitude,longitude,verification,source_url) VALUES(?,?,?,?,?)',('P1',-25,120,'VERIFIED',url))
    cfg={'layers':{layer:{'local_geojson':item['path'],'official_source_url':item['url'],'expected_sha256':item['sha'],
                          'approval_ref':item['ref'],'mode':'full'} for layer,item in layers.items()},'radii_km':[25]}
    r=gis_run(db,{'gis':cfg,'root':tmp_path,'workspace':tmp_path/'work','offline':True,'artifacts':{}})
    assert r['status']=='GIS_COMPLETE'
    assert db.execute("SELECT COUNT(*) FROM gis_metrics WHERE status='VERIFIED'").fetchone()[0]==4
    db.execute("UPDATE evidence_approvals SET status='NOT_APPROVED' WHERE approval_ref='layer-rail'")
    r=gis_run(db,{'gis':cfg,'root':tmp_path,'workspace':tmp_path/'work','offline':True,'artifacts':{}})
    assert r['status']=='GIS_NOT_RELEASED'
    assert db.execute("SELECT status FROM gis_metrics WHERE criterion='I2'").fetchone()[0]!='VERIFIED'
    db.close()


def test_revoked_evidence_removed_on_stage_replay(tmp_path):
    """A previously scored observation must not survive deletion of its approval."""
    from au_ree.stages.criteria import run as criteria_run
    sha,url,_=build_registry(tmp_path,1)
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,population_status) VALUES('P1','Synthetic','synthetic','CENSUS')")
    csvwrite(tmp_path/'inputs'/'verified_observations.csv',[
        {'project_id':'P1','variable':'processing_complexity_ord','numeric_value':1,
         'basis':'PROCESS_ASSESSED','source_url':url,'source_sha256':sha,'verification':'VERIFIED',
         'effective_date':'2026-10-01','approval_ref':'obs-0'}],
        ['project_id','variable','numeric_value','basis','source_url','source_sha256','verification','effective_date','approval_ref'])
    ctx={'criteria':CRITERIA,'root':tmp_path,'artifacts':{}}
    result=criteria_run(db,ctx)
    assert result['verified_scoring_values']==1
    assert db.execute("SELECT verification FROM observations").fetchone()[0]=='VERIFIED'
    rows=list(csv.DictReader((tmp_path/'inputs'/'evidence_approvals.csv').open()))
    for row in rows:
        if row['approval_ref']=='obs-0':row['decision']='REJECTED'
    csvwrite(tmp_path/'inputs'/'evidence_approvals.csv',rows,list(rows[0]))
    result=criteria_run(db,{'criteria':CRITERIA,'root':tmp_path,'artifacts':{}})
    assert result['verified_scoring_values']==0
    assert db.execute("SELECT verification FROM observations").fetchone()[0]=='REVIEW_PENDING'
    assert db.execute("SELECT COUNT(*) FROM evidence_links").fetchone()[0]==0
    assert db.execute("SELECT quality FROM criterion_values WHERE criterion='T1'").fetchone()[0]=='NOT_SCORED'
    db.close()


def test_project_review_requires_distinct_approval(tmp_path):
    """Typing a hash and source URL into project_reviews.csv cannot verify coordinates."""
    from au_ree.stages.population import run as population_run
    sha,url,_=build_registry(tmp_path,1)
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,country,population_status,activity,lifecycle,ree_role) VALUES('P1','Synthetic','synthetic','Australia','CENSUS','UNKNOWN','UNKNOWN','REE_UNCONFIRMED')")
    rows=[{'project_id':'P1','activity':'ACTIVE','lifecycle':'PFS','ree_role':'REE_PRIMARY','latitude':'-25',
           'longitude':'120','source_url':url,'source_sha256':sha,'evidence_date':'2026-10-01','approval_ref':''}]
    f=tmp_path/'inputs'/'project_reviews.csv'
    csvwrite(f,rows,list(rows[0]))
    ctx={'sources':{'sources':[]},'criteria':CRITERIA,'root':tmp_path,'workspace':tmp_path/'work',
         'offline':True,'artifacts':{},'hash_file':lambda p:hashlib.sha256(p.read_bytes()).hexdigest()}
    result=population_run(db,ctx)
    assert result['reviewed_project_updates']==0
    assert db.execute("SELECT activity FROM project_master WHERE project_id='P1'").fetchone()[0]=='UNKNOWN'
    rows[0]['approval_ref']='project-0';csvwrite(f,rows,list(rows[0]))
    result=population_run(db,ctx)
    assert result['reviewed_project_updates']==1
    assert db.execute("SELECT activity FROM project_master WHERE project_id='P1'").fetchone()[0]=='ACTIVE'
    assert db.execute("SELECT verification FROM project_coordinates WHERE project_id='P1'").fetchone()[0]=='VERIFIED'
    # Revoke previously approved review: replay must not retain stale VERIFIED location.
    approval_file=tmp_path/'inputs'/'evidence_approvals.csv'
    allrows=list(csv.DictReader(approval_file.open()))
    for row in allrows:
        if row['approval_ref']=='project-0':row['decision']='REJECTED'
    csvwrite(approval_file,allrows,list(allrows[0]))
    result=population_run(db,ctx)
    assert result['reviewed_project_updates']==0
    assert db.execute("SELECT activity FROM project_master WHERE project_id='P1'").fetchone()[0]=='UNKNOWN'
    assert db.execute("SELECT COUNT(*) FROM project_coordinates WHERE project_id='P1'").fetchone()[0]==0
    db.close()


def test_stage_failure_preserves_canonical_sqlite(tmp_path,monkeypatch):
    """A crashed stage must not publish partially verified records."""
    from types import SimpleNamespace
    from au_ree import cli
    from au_ree.core import filehash
    dbpath=tmp_path/'database.sqlite';workspace=tmp_path/'work';workspace.mkdir()
    args=SimpleNamespace(db=dbpath,workspace=workspace,offline=True,refresh=False)
    configs=cli.cfgs()
    cli.run_one('population',args,configs)
    before=filehash(dbpath)
    def crash(db,ctx):
        db.execute("INSERT INTO audit_events(stage,entity_id,kind,message,time) VALUES('criteria','fixture','TEST','not committed','now')")
        raise RuntimeError('synthetic stage failure before commit')
    monkeypatch.setitem(cli.RUNNERS,'criteria',crash)
    with pytest.raises(RuntimeError,match='synthetic stage failure'):
        cli.run_one('criteria',args,configs)
    assert filehash(dbpath)==before
    db=connect(dbpath)
    assert db.execute("SELECT COUNT(*) FROM audit_events WHERE message='not committed'").fetchone()[0]==0
    assert db.execute("SELECT COUNT(*) FROM stage_runs WHERE stage='criteria'").fetchone()[0]==0
    db.close()
