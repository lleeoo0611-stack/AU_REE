"""V2 retains verified alternatives without cross-project release blocking."""
import csv
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from au_ree.core import connect, setup
from au_ree.stages.eligibility import run
from scripts.run_mcda_pipeline import run as rank, PANELS

ROOT=Path(__file__).resolve().parents[1]

def test_complete_core_survives_another_projects_missing_gis_and_optional_values(tmp_path):
    db=connect(tmp_path/'fixture.sqlite');setup(db)
    criteria=json.loads((ROOT/'config/criteria.json').read_text())['criteria']
    for c in criteria:
        db.execute('INSERT INTO criteria(code,domain,direction,basis) VALUES(?,?,?,?)',
                   (c['code'],c['domain'],c['direction'],c['basis']))
    db.execute("INSERT INTO source_documents(document_id,file_path,source_url,hash_status,checked_at) VALUES('d','test','test','test','now')")
    db.execute("INSERT INTO evidence_approvals(approval_ref,record_type,document_id,status) VALUES('a','OBSERVATION','d','APPROVED')")
    for pid in ('A','B','C'):
        db.execute("INSERT INTO project_master(project_id,canonical_name,normalized_name,country,latitude,longitude,activity,lifecycle,ree_role,population_status) VALUES(?,?,?,'Australia',-25,120,'ACTIVE','PFS','REE_PRIMARY','TEST')",(pid,pid,pid))
        db.execute("INSERT INTO project_coordinates(project_id,verification) VALUES(?,'VERIFIED')",(pid,))
        db.execute("INSERT INTO approved_project_reviews VALUES(?,'a','test')",(pid,))
        db.execute("INSERT INTO observations(obs_id,project_id,variable,text_value,verification) VALUES(?,?,'resource_standard','JORC 2012','VERIFIED')",(pid,pid))
        db.execute("INSERT INTO evidence_links VALUES('OBSERVATION',?,'a')",(pid,))
        for c in criteria:
            # Leave commercial and NORM unknown in every project.
            if c['code'] in ('T2','C1','C2','C3','S1'):continue
            db.execute("INSERT INTO criterion_values(project_id,criterion,value,basis,quality) VALUES(?,?,1,?,'VERIFIED')",(pid,c['code'],c['basis']))
    ctx={'root':ROOT,'eligibility':json.loads((ROOT/'config/eligibility.json').read_text()),'artifacts':{}}
    # Isolate release policy. These mocks do not represent evidence approvals.
    with patch('au_ree.stages.eligibility.independently_approved_project',return_value=True),patch('au_ree.stages.eligibility._gis_complete',side_effect=lambda db,pid:pid!='C'):
        run(db,ctx)
    assert [r['project_id'] for r in ctx['artifacts']['matrix_CORE_BASELINE_V2.csv'][0]]==['A','B']
    assert len(ctx['artifacts']['matrix_RESOURCE_EXTENDED_V2.csv'][0])==2
    assert ctx['artifacts']['matrix_FULL_PANEL_V2.csv'][0]==[]
    assert ctx['artifacts']['matrix_STRATEGIC_EXTENDED_V2.csv'][0]==[]
    # Legacy cohort still obeys historical release requirements.
    assert ctx['artifacts']['matrix_G0_BASELINE.csv'][0]==[]
    db.close()

def test_empty_panels_skip_without_r_and_preserve_run_manifest(tmp_path):
    stages=tmp_path/'work'/'outputs'
    elig=stages/'04_eligibility';params=stages/'05_r_export'
    elig.mkdir(parents=True);params.mkdir()
    (params/'r_criteria_dictionary.csv').write_text('criterion,direction\nT1,MIN\n')
    (params/'r_weights.csv').write_text('perspective,criterion,weight\n')
    (elig/'mcda_eligibility_long.csv').write_text('project_id,scenario,point_ready\n')
    for panel in PANELS:
        (elig/f'matrix_{panel}.csv').write_text('project_id,project_name\n')
    out=tmp_path/'result'
    result=rank(tmp_path/'work',out,rscript='R_NOT_INSTALLED')
    assert len(result['panels'])==4
    assert all(r['status']=='INSUFFICIENT_VERIFIED_CASES' for r in result['panels'])
    assert (out/'manifest.json').exists()
    assert len(result['inputs'])==10
    with pytest.raises(FileExistsError):rank(tmp_path/'work',out)
