from __future__ import annotations
import json,sqlite3,subprocess,sys
from pathlib import Path
import pytest
from shapely.geometry import Point
from au_ree.core import connect,setup,digest
from au_ree.stages.population import candidate_upsert
from au_ree.stages.gis import nearest
from au_ree.stages.eligibility import run as eligibility_run

ROOT=Path(__file__).resolve().parents[1]

def test_census_project_vs_deposit_and_stable_id():
    with sqlite3.connect(':memory:') as raw:
        raw.row_factory=sqlite3.Row;setup(raw)
        base={'source':'state_test','name':'Example REE Project','native_id':'S1','state':'WA','commodity':'rare earth elements',
              'latitude':-25.,'longitude':120.,'entity_level':'PROJECT','official':True,'source_url':'https://data.example.gov.au/project'}
        assert candidate_upsert(raw,base)=='ADDED'
        assert candidate_upsert(raw,base)=='MERGED'
        deposit={**base,'name':'Example Deposit','native_id':'S2','entity_level':'DEPOSIT'}
        assert candidate_upsert(raw,deposit)=='REVIEW'
        assert raw.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==1
        assert raw.execute('SELECT COUNT(*) FROM population_candidates').fetchone()[0]==2

def test_gis_metric_uses_projected_geometry():
    feature={'geometry':{'type':'Point','coordinates':[120.0,-25.0]}}
    dist,checksum=nearest(-25,120,[feature]);assert dist<0.00001;assert len(checksum)==64
    dist,_=nearest(-25.1,120.1,[feature]);assert 5<dist<25

def test_unattested_candidate_cannot_be_point_ready(tmp_path):
    db=connect(tmp_path/'test.sqlite');setup(db)
    cfg=json.loads((ROOT/'config/criteria.json').read_text());e=json.loads((ROOT/'config/eligibility.json').read_text())
    db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,state,country,latitude,longitude,activity,lifecycle,ree_role,deposit_family,population_status,identity_source,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               ('AU-REE-00001','Fixture','fixture','WA','Australia',-25,120,'ACTIVE','PFS','REE_PRIMARY','HARD_ROCK','CENSUS','TEST','now'))
    db.execute("INSERT INTO project_coordinates(project_id,latitude,longitude,verification) VALUES(?,?,?,?)",('AU-REE-00001',-25,120,'VERIFIED'))
    db.execute("INSERT INTO observations(obs_id,project_id,variable,text_value,source_url,source_sha256,verification) VALUES(?,?,?,?,?,?,?)",
               ('j1','AU-REE-00001','resource_standard','JORC 2012','https://example.org/jorc','abcd','VERIFIED'))
    for c in cfg['criteria']:
        db.execute('INSERT INTO criteria(code,domain,label,direction,unit,basis,mandatory,description,config_version) VALUES(?,?,?,?,?,?,?,?,?)',(c['code'],c['domain'],c['name'],c['direction'],c['unit'],c['basis'],0,'','test'))
        if c['code']!='T2':db.execute('INSERT INTO criterion_values(project_id,criterion,value,unit,basis,quality,issue) VALUES(?,?,?,?,?,?,?)',('AU-REE-00001',c['code'],2.0,c['unit'],c['basis'],'VERIFIED',''))
    db.commit()
    ctx={'root':tmp_path,'eligibility':e,'artifacts':{}}
    result=eligibility_run(db,ctx)
    row=db.execute("SELECT eligible,point_ready FROM eligibility WHERE scenario='G0_BASELINE'").fetchone()
    assert tuple(row)==(0,0)
    assert ctx['artifacts']['matrix_G0_BASELINE.csv'][0]==[]
    db.execute("INSERT INTO criterion_values(project_id,criterion,value,unit,basis,quality,issue) VALUES(?,?,?,?,?,?,?)",('AU-REE-00001','T2',1,'ordinal','NORM_ASSESSED','VERIFIED',''))
    eligibility_run(db,ctx)
    row=db.execute("SELECT eligible,point_ready FROM eligibility WHERE scenario='G0_BASELINE'").fetchone()
    assert tuple(row)==(0,0)
    assert len(ctx['artifacts']['matrix_G0_BASELINE.csv'][0])==0
    db.close()

def test_offline_end_to_end_and_checkpoint_reuse(tmp_path):
    db=tmp_path/'research.sqlite';workspace=tmp_path/'work'
    cmd=[sys.executable,'-m','au_ree','run','--through','r_export','--offline','--db',str(db),'--workspace',str(workspace)]
    first=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=45)
    assert first.returncode==0,first.stderr
    again=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=45)
    assert again.returncode==0,again.stderr
    assert again.stdout.count('REUSED')==5
    con=connect(db)
    assert con.execute('SELECT count(*) FROM project_master').fetchone()[0]==203
    assert con.execute('SELECT count(*) FROM criteria').fetchone()[0]==12
    assert con.execute('SELECT count(*) FROM observations').fetchone()[0]==220
    assert con.execute('SELECT count(*) FROM project_coordinates').fetchone()[0]==19
    assert con.execute('SELECT count(*) FROM eligibility WHERE point_ready=1').fetchone()[0]==0
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    con.close()
    for path in ['01_population/population_master.csv','04_eligibility/alternatives_completeness.csv',
                 '04_eligibility/matrix_G0_BASELINE.csv','05_r_export/r_weights.csv']:
        assert (workspace/'outputs'/path).exists()

def test_ga_deposit_remains_review_not_automatically_promoted():
    with sqlite3.connect(':memory:') as db:
        db.row_factory=sqlite3.Row;setup(db)
        candidate={'source':'GA_AIMR_REE_2026','name':'New deposit not a project','native_id': '999',
                   'state':'WA','commodity':'Rare Earth Elements','latitude':-25.,'longitude':121.,
                   'official':True,'entity_level':'DEPOSIT','source_url':'https://services.ga.gov.au/dataset'}
        assert candidate_upsert(db,candidate)=='REVIEW'
        assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==0
        assert db.execute('SELECT reason FROM population_candidates').fetchone()[0]=='ENTITY_LEVEL_DEPOSIT'


def test_source_compatible_derived_resource_and_magnet_share():
    from au_ree.stages.criteria import derive_metrics
    with sqlite3.connect(':memory:') as db:
        db.row_factory=sqlite3.Row;setup(db)
        db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,population_status) VALUES('AU-REE-90001','Test','test','CENSUS')")
        values=[('ore_mt',10,'DIRECT_TREO'),('treo_grade_pct',2.5,'DIRECT_TREO'),
                ('nd2o3_pct_treo',15,'PCT_TREO_REO_COMPONENT'),('pr6o11_pct_treo',5,'PCT_TREO_REO_COMPONENT'),
                ('dy2o3_pct_treo',3,'PCT_TREO_REO_COMPONENT'),('tb4o7_pct_treo',1,'PCT_TREO_REO_COMPONENT')]
        for i,(name,val,basis) in enumerate(values):
            db.execute("INSERT INTO observations(obs_id,project_id,variable,numeric_value,basis,effective_date,source_url,source_sha256,verification) VALUES(?,?,?,?,?,?,?,?,?)",
                  (f'raw{i}','AU-REE-90001',name,val,basis,'2026-10-01','https://example.org/report','sha256-fixture','VERIFIED'))
        # Synthetic approvals are created in the separate reviewer registry.
        db.execute("INSERT INTO source_documents(document_id,file_path,source_url,declared_sha256,actual_sha256,hash_status,checked_at) VALUES('doc','inputs/evidence/test','https://example.org/report','sha256-fixture','sha256-fixture','HASH_MATCH_REVIEW_REQUIRED','now')")
        db.execute("INSERT INTO evidence_approvals(approval_ref,record_type,document_id,reviewer,decision,reviewed_at,status) VALUES('approval','OBSERVATION','doc','QA tester','APPROVED','2026-10-01','APPROVED')")
        for i in range(6):
            db.execute("INSERT INTO evidence_links(record_type,record_id,approval_ref) VALUES('OBSERVATION',?,'approval')",(f'raw{i}',))
        assert derive_metrics(db)==2
        got=dict(db.execute("SELECT variable,numeric_value FROM observations WHERE verification='ACCEPTED_DERIVED'"))
        assert got['contained_treo_kt']==250
        assert got['magnet_reo_share_pct']==24
        assert derive_metrics(db)==2
        assert db.execute("SELECT COUNT(*) FROM observations WHERE verification='ACCEPTED_DERIVED'").fetchone()[0]==2
        db.execute("UPDATE observations SET source_sha256='different-source' WHERE variable='treo_grade_pct'")
        db.execute("DELETE FROM observations WHERE verification='ACCEPTED_DERIVED'")
        assert derive_metrics(db)==1
        assert db.execute("SELECT COUNT(*) FROM observations WHERE variable='contained_treo_kt'").fetchone()[0]==0


def test_frozen_evidence_cutoff_and_nan_rejected():
    from au_ree.stages.criteria import ingest
    from au_ree.core import number
    assert number('nan') is None and number('Infinity') is None
    with sqlite3.connect(':memory:') as db:
        db.row_factory=sqlite3.Row;setup(db)
        db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,population_status) VALUES('AU-REE-90001','Test','test','CENSUS')")
        rows=[{'project_id':'AU-REE-90001','variable':'ore_mt','standard_value':'55','effective_date':'2026-12-01',
            'source_url':'https://example.org/2026','source_sha256':'abc','verification':'VERIFIED'}]
        assert ingest(db,rows,'researcher_updates','2026-10-29')==0
        assert db.execute('SELECT COUNT(*) FROM observations').fetchone()[0]==0
        assert db.execute("SELECT COUNT(*) FROM audit_events WHERE kind='POST_CUTOFF_EVIDENCE'").fetchone()[0]==1


def test_upstream_force_archives_stale_downstream_files(tmp_path):
    db=tmp_path/'research.sqlite';workspace=tmp_path/'work'
    cmd=[sys.executable,'-m','au_ree','run','--through','r_export','--offline','--db',str(db),'--workspace',str(workspace)]
    assert subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=45).returncode==0
    assert (workspace/'outputs'/'05_r_export'/'r_criteria_dictionary.csv').exists()
    single=[sys.executable,'-m','au_ree','run','--stage','population','--force','--offline','--db',str(db),'--workspace',str(workspace)]
    result=subprocess.run(single,capture_output=True,text=True,cwd=ROOT,timeout=45)
    assert result.returncode==0,result.stderr
    assert not (workspace/'outputs'/'05_r_export').exists()
    assert list((workspace/'snapshots').rglob('r_criteria_dictionary.csv'))
    with connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM stage_runs").fetchone()[0]==1


def test_gis_pending_coordinate_never_promoted_to_verified(tmp_path):
    from au_ree.stages.gis import run as gis_run
    import hashlib
    with sqlite3.connect(':memory:') as db:
        db.row_factory=sqlite3.Row;setup(db)
        db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,latitude,longitude,population_status) VALUES('AU-REE-90001','Test','test',-25,120,'CENSUS')")
        db.execute("INSERT INTO project_coordinates(project_id,latitude,longitude,verification) VALUES('AU-REE-90001',-25,120,'LEGACY_FROZEN_NEEDS_REVIEW')")
        local=tmp_path/'official.geojson'
        local.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[120,-25]},'properties':{'source':'test'}}]}))
        layer={'local_geojson':str(local),'official_source_url':'https://example.gov.au/geojson',
               'expected_sha256':hashlib.sha256(local.read_bytes()).hexdigest(),'mode':'full'}
        cfg={'layers':{name:dict(layer) for name in ['road','rail','power','port']},'radii_km':[25]}
        result=gis_run(db,{'gis':cfg,'root':ROOT,'workspace':tmp_path,'offline':True,'artifacts':{}})
        assert result['status']=='GIS_NOT_RELEASED'
        assert db.execute("SELECT COUNT(*) FROM gis_metrics WHERE status='VERIFIED'").fetchone()[0]==0
