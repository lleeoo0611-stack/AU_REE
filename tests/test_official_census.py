"""Live API structure is tested with synthetic server responses, not fake research data."""
import json, sqlite3
from pathlib import Path
import pytest
from au_ree.core import setup, connect
from au_ree.stages.population import candidate_upsert
from au_ree.source_adapters import load_arcgis, parse_arcgis, parse_state_csv, load_csv


def memorydb():
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;setup(db);return db


def fake_source(entity='DEPOSIT'):
    return {'key':'TEST_WA','type':'arcgis','url':'https://example.gov.au/arcgis/MapServer/0',
            'name_field':'site_title','native_id_field':'site_code','commodity_field':'site_commo',
            'project_name_field':'proj_title','state_fixed':'WA','jurisdiction':'WA',
            'entity_level':entity,'official':True,'where':'1=1'}


def mock_http(monkeypatch, feature_names=('REE Field A','REE Field B')):
    calls=[]
    def fake(url,params=None,offline=False):
        calls.append((url,params))
        if url.endswith('/0'):
            val={'type':'Feature Layer','objectIdField':'oid','fields':[{'name':'oid','type':'esriFieldTypeOID'}]}
        elif params.get('returnIdsOnly')=='true':
            val={'objectIds':list(range(1,len(feature_names)+1)),'objectIdFieldName':'oid'}
        else:
            val={'features':[{'attributes':{'oid':int(i),'site_code':f'WA{i}','site_title':feature_names[int(i)-1],
                'site_commo':'rare earth elements','proj_title':'Area Alpha','latitude':-25.1,'longitude':120.3},
                'geometry':{'x':120.3,'y':-25.1}} for i in params['objectIds'].split(',')]}
        return val,json.dumps(val).encode()
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',fake)
    return calls


def test_wa_layer_profile_fields_and_project_hint():
    source=fake_source()
    item=parse_arcgis({'attributes':{'site_code':'S-1','site_title':'Lynx','site_commo':'REE','proj_title':'Lynx Project',
                                    'latitude':-25.,'longitude':120.}},source)
    assert item['name']=='Lynx'
    assert item['project_name_hint']=='Lynx Project'
    assert item['state']=='WA'
    assert item['entity_level']=='DEPOSIT'


def test_arcgis_snapshot_offline_resume(monkeypatch,tmp_path):
    calls=mock_http(monkeypatch)
    rows,checksum,directory=load_arcgis(fake_source(),tmp_path,offline=False,chunk_size=1)
    assert len(rows)==2 and len(checksum)==64
    assert len(calls)==4  # metadata, IDs, 2 chunk queries
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',lambda *a,**k:(_ for _ in ()).throw(RuntimeError('NO_NETWORK')))
    copy,other,_=load_arcgis(fake_source(),tmp_path,offline=True,chunk_size=1)
    assert copy==rows and checksum==other
    # An incomplete cached chunk must be rejected rather than passed as complete.
    f=directory/'features_0000000.json'
    f.write_text(json.dumps({'features':[]}))
    with pytest.raises(RuntimeError,match='truncated/mismatched'):
        load_arcgis(fake_source(),tmp_path,offline=True,chunk_size=1)


def test_ga_deposit_exact_project_name_not_merged():
    db=memorydb()
    project={'source':'OFFICIAL_PROJECT','native_id':'p1','name':'Test Rare Earth Project','state':'WA',
             'latitude':-25.2,'longitude':121.,'commodity':'REE','entity_level':'PROJECT','official':True,
             'source_url':'https://example.gov.au/p','company':'Example Pty Ltd'}
    assert candidate_upsert(db,project)=='REVIEW'
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==0
    assert candidate_upsert(db,{**project,'source':'legacy_r963_frozen','native_id':'legacy'})=='ADDED'
    same={'source':'GA','native_id':'d1','name':project['name'],'state':'WA','latitude':-25.2,'longitude':121.,
          'commodity':'REE','entity_level':'DEPOSIT','official':True,'source_url':'https://example.gov.au/d'}
    assert candidate_upsert(db,same)=='REVIEW'
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==1
    row=db.execute("SELECT decision,reason,matched_project_id FROM population_candidates WHERE source_key='GA'").fetchone()
    assert row['reason'].startswith('DEPOSIT_POSSIBLE_PARENT_')
    assert row['matched_project_id'] is not None
    db.close()


def test_same_project_company_conflict_requires_review():
    db=memorydb();c={'source':'ONE','native_id':'1','name':'Cedar REE Project','state':'WA','company':'A Pty Ltd',
                      'latitude':-25.,'longitude':121.,'commodity':'REE','entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,{**c,'source':'legacy_r963_frozen'})=='ADDED'
    assert candidate_upsert(db,{**c,'source':'TWO','native_id':'2','company':'B Pty Ltd'})=='REVIEW'
    assert db.execute('SELECT operator_name FROM project_master').fetchone()[0]=='A Pty Ltd'
    assert db.execute("SELECT reason FROM population_candidates WHERE source_key='TWO'").fetchone()[0]=='COMPANY_OPERATOR_CONFLICT'


def test_state_mismatch_is_rejected_for_automatic_inclusion():
    db=memorydb();c={'source':'WA','native_id':'99','name':'Out of jurisdiction','state':'QLD','state_jurisdiction':'WA',
                      'latitude':-21,'longitude':146,'commodity':'REE','entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,c)=='REVIEW'
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==0


def test_nearby_different_names_are_reviewed_not_auto_merged():
    db=memorydb();c={'source':'ONE','native_id':'1','name':'Cedar REE Project','state':'WA','latitude':-25.0,
                      'longitude':121.0,'commodity':'REE','entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,{**c,'source':'legacy_r963_frozen'})=='ADDED'
    assert candidate_upsert(db,{**c,'source':'TWO','native_id':'2','name':'Cedar South Project','latitude':-25.01})=='REVIEW'
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==1
    assert db.execute("SELECT reason FROM population_candidates WHERE source_key='TWO'").fetchone()[0]=='NEARBY_PROJECT_POSSIBLE_DUPLICATE'


def test_csv_state_source_pending_is_explicit(tmp_path):
    source={'type':'csv','key':'STATE_NT','path':'inputs/state_exports/nt.csv','state_fixed':'NT'}
    rows,sha,status=load_csv(source,tmp_path)
    assert rows is None and status=='AWAITING_OFFICIAL_EXPORT'


def test_state_csv_case_insensitive_mapping():
    x=parse_state_csv({'Project Name':'Cedar','Longitude':123,'Latitude':-27,'Owner':'Owner Ltd',
                       'Commodity':'Rare Earth Elements','Entity_Level':'PROJECT'},
                      {'key':'STATE_WA','entity_level':'DEPOSIT','state_fixed':'WA','source_documentation':'https://example.gov.au'})
    assert x['company']=='Owner Ltd' and x['state']=='WA' and x['entity_level']=='PROJECT'
