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
    with pytest.raises(RuntimeError,match='Frozen ArcGIS snapshot component SHA256 mismatch'):
        load_arcgis(fake_source(),tmp_path,offline=True,chunk_size=1)



def test_arcgis_frozen_manifest_blocks_same_oid_content_mutation(monkeypatch,tmp_path):
    mock_http(monkeypatch)
    _,frozen_digest,directory=load_arcgis(fake_source(),tmp_path,chunk_size=1)
    original_manifest=(directory/'manifest.json').read_bytes()
    chunk=directory/'features_0000000.json'
    obj=json.loads(chunk.read_text(encoding='utf8'))
    obj['features'][0]['attributes']['site_title']='different geological source record'
    chunk.write_text(json.dumps(obj),encoding='utf8')
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',
                        lambda *args,**kwargs: (_ for _ in ()).throw(RuntimeError('NO_NETWORK')))
    with pytest.raises(RuntimeError,match='Frozen ArcGIS snapshot component SHA256 mismatch'):
        load_arcgis(fake_source(),tmp_path,offline=True,chunk_size=1)
    assert (directory/'manifest.json').read_bytes()==original_manifest
    assert frozen_digest!=None


def test_arcgis_frozen_manifest_blocks_source_metadata_rewrite(monkeypatch,tmp_path):
    mock_http(monkeypatch)
    _,_,directory=load_arcgis(fake_source(),tmp_path,chunk_size=1)
    original=(directory/'manifest.json').read_bytes()
    meta=directory/'metadata.json'
    modified=json.loads(meta.read_text(encoding='utf8'))
    modified['description']='changed after frozen source'
    meta.write_text(json.dumps(modified),encoding='utf8')
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',
                        lambda *args,**kwargs: (_ for _ in ()).throw(RuntimeError('NO_NETWORK')))
    with pytest.raises(RuntimeError,match='Frozen ArcGIS snapshot component SHA256 mismatch'):
        load_arcgis(fake_source(),tmp_path,offline=True,chunk_size=1)
    assert (directory/'manifest.json').read_bytes()==original


def test_arcgis_frozen_snapshot_missing_raw_chunk_cannot_be_refetched(monkeypatch,tmp_path):
    calls=mock_http(monkeypatch)
    _,_,directory=load_arcgis(fake_source(),tmp_path,chunk_size=1)
    frozen_manifest=(directory/'manifest.json').read_bytes()
    chunk=directory/'features_0000000.json'
    chunk.unlink()
    attempted=[]
    def unexpected_http(*args,**kwargs):
        attempted.append(args)
        raise AssertionError('frozen source must not fetch missing original bytes')
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',unexpected_http)
    with pytest.raises(RuntimeError,match='Frozen ArcGIS snapshot missing component'):
        load_arcgis(fake_source(),tmp_path,offline=False,chunk_size=1)
    assert not chunk.exists()
    assert not attempted
    assert (directory/'manifest.json').read_bytes()==frozen_manifest
    assert len(calls)==4


def test_arcgis_frozen_snapshot_missing_metadata_cannot_be_refetched(monkeypatch,tmp_path):
    mock_http(monkeypatch)
    _,_,directory=load_arcgis(fake_source(),tmp_path,chunk_size=1)
    frozen_manifest=(directory/'manifest.json').read_bytes()
    (directory/'metadata.json').unlink()
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',
                        lambda *a,**k: (_ for _ in ()).throw(AssertionError('unapproved refetch')))
    with pytest.raises(RuntimeError,match='Frozen ArcGIS snapshot missing component'):
        load_arcgis(fake_source(),tmp_path,offline=False,chunk_size=1)
    assert (directory/'manifest.json').read_bytes()==frozen_manifest
    assert not (directory/'metadata.json').exists()


def test_arcgis_duplicate_object_ids_not_silently_deduplicated(monkeypatch,tmp_path):
    mock_http(monkeypatch)
    from au_ree import source_adapters
    original_fetch=source_adapters.fetch_json
    def invalid_ids(url,params=None,offline=False):
        if params and params.get('returnIdsOnly')=='true':
            raw=json.dumps({'objectIds':[1,1], 'objectIdFieldName':'oid'}).encode()
            return json.loads(raw),raw
        return original_fetch(url,params,offline)
    monkeypatch.setattr('au_ree.source_adapters.fetch_json',invalid_ids)
    with pytest.raises(RuntimeError,match='Duplicate OIDs'):
        load_arcgis(fake_source(),tmp_path,chunk_size=1)
    assert not list(tmp_path.rglob('manifest.json'))


def _source_ingest_fixture(tmp_path):
    source={'key':'FROZEN_WA_CSV','type':'csv','enabled':True,
            'source_documentation':'https://example.gov.au/frozen-source'}
    def row(native):
        return {'source':'FROZEN_WA_CSV','native_id':native,
                'name':f'Synthetic REE deposit {native}','state':'WA','latitude':-25.1,
                'longitude':120.3,'commodity':'REE','entity_level':'DEPOSIT',
                'official':True,'source_url':source['source_documentation'],
                'source_raw_attributes':{'native_id':native,'commodity':'REE'}}
    ctx={'root':tmp_path,'workspace':tmp_path/'workspace','offline':False,
         'criteria':{'freeze_date':'2026-10-29'},
         'sources':{'as_of':'2026-10-29','sources':[source]},
         'hash_file':lambda _: '0'*64}
    return source,ctx,row


def test_census_source_ingest_rolls_back_partial_entity_import(monkeypatch,tmp_path):
    """If source row 2 is invalid, row 1 may not survive in any identity table."""
    from au_ree.stages import population
    source,ctx,row=_source_ingest_fixture(tmp_path)
    monkeypatch.setattr(population,'load_csv',
                        lambda src,root:([row('D1'),row('D2')],'a'*64,'OK_LOCAL_EXPORT_UNVERIFIED'))
    original=population.candidate_upsert
    def fail_after_one(db,record):
        if record['native_id']=='D2':
            raise RuntimeError('synthetic invalid second source row')
        return original(db,record)
    monkeypatch.setattr(population,'candidate_upsert',fail_after_one)
    db=memorydb()
    result=population.run(db,ctx)
    assert len(result['source_failures'])==1
    assert 'synthetic invalid second source row' in result['source_failures'][0]['error']
    for table in ('population_candidates','source_feature_snapshot','geological_entity',
                  'geological_entity_source','extended_occurrence_inventory',
                  'project_master'):
        assert db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]==0,table
    registry=db.execute('SELECT raw_sha256,record_count,fetch_status FROM source_registry').fetchone()
    assert registry['raw_sha256'] is None
    assert registry['record_count']==0
    assert registry['fetch_status']=='FETCH_FAILED'
    assert result['counts'].get('REVIEW',0)==0
    db.close()


def test_census_same_cutoff_source_hash_drift_preserves_imported_records(monkeypatch,tmp_path):
    from au_ree.stages import population
    source,ctx,row=_source_ingest_fixture(tmp_path)
    current=['a'*64]
    monkeypatch.setattr(population,'load_csv',
                        lambda src,root:([row('D1')],current[0],'OK_LOCAL_EXPORT_UNVERIFIED'))
    db=memorydb()
    first=population.run(db,ctx)
    assert first['source_failures']==[]
    first_original=db.execute('SELECT original_json FROM population_candidates').fetchone()[0]
    first_sha=db.execute('SELECT record_sha256 FROM source_feature_snapshot').fetchone()[0]
    current[0]='b'*64
    second=population.run(db,ctx)
    assert 'FROZEN_SOURCE_SHA_CHANGED_REVIEW_REQUIRED' in second['source_failures'][0]['error']
    assert db.execute('SELECT raw_sha256 FROM source_registry').fetchone()[0]=='a'*64
    assert db.execute('SELECT original_json FROM population_candidates').fetchone()[0]==first_original
    assert db.execute('SELECT record_sha256 FROM source_feature_snapshot').fetchone()[0]==first_sha
    assert db.execute('SELECT COUNT(*) FROM source_feature_snapshot').fetchone()[0]==1
    assert db.execute('SELECT COUNT(*) FROM geological_entity_source').fetchone()[0]==1
    db.close()


def test_census_same_cutoff_source_url_changed_requires_versioned_source(monkeypatch,tmp_path):
    from au_ree.stages import population
    source,ctx,row=_source_ingest_fixture(tmp_path)
    monkeypatch.setattr(population,'load_csv',
                        lambda src,root:([row('D1')],'a'*64,'OK_LOCAL_EXPORT_UNVERIFIED'))
    db=memorydb()
    assert population.run(db,ctx)['source_failures']==[]
    old_source=db.execute('SELECT source_url,raw_sha256 FROM source_registry').fetchone()
    source['source_documentation']='https://example.gov.au/different-unapproved-source'
    result=population.run(db,ctx)
    assert 'FROZEN_SOURCE_URL_CHANGED_REVIEW_REQUIRED' in result['source_failures'][0]['error']
    after=db.execute('SELECT source_url,raw_sha256 FROM source_registry').fetchone()
    assert tuple(old_source)==tuple(after)
    assert db.execute('SELECT COUNT(*) FROM population_candidates').fetchone()[0]==1
    db.close()


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



def _legacy_project_for_conflict(db,name,native_id,lat=-25.0,lon=121.0):
    record={'source':'legacy_r963_frozen','native_id':native_id,
            'name':name,'state':'WA','company':'Legacy Pty Ltd',
            'latitude':lat,'longitude':lon,'commodity':'REE',
            'entity_level':'PROJECT','official':False}
    assert candidate_upsert(db,record)=='ADDED'
    return db.execute('SELECT project_id FROM project_master WHERE canonical_name=?',(name,)).fetchone()[0]


def test_conflicting_native_id_never_falls_back_to_matching_project_name():
    db=memorydb()
    a=_legacy_project_for_conflict(db,'Alpha REE Project','LEGACY-A')
    b=_legacy_project_for_conflict(db,'Beta REE Project','LEGACY-B',lat=-27,lon=123)
    for pid in (a,b):
        db.execute('INSERT INTO project_aliases VALUES(?,?,?,?,?)',
                   (pid,'Old survey name','old survey name','WA_SOURCE','NATIVE-42'))
    official={'source':'WA_SOURCE','native_id':'NATIVE-42',
              'name':'Alpha REE Project','state':'WA','latitude':-25.0,
              'longitude':121.0,'commodity':'REE','entity_level':'PROJECT',
              'official':True}
    assert candidate_upsert(db,official)=='REVIEW'
    row=db.execute("SELECT decision,reason,matched_project_id FROM population_candidates WHERE source_key='WA_SOURCE'").fetchone()
    assert row['reason']=='REVIEW_NATIVE_ID_CONFLICT'
    assert row['matched_project_id'] is None
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==2
    db.close()


def test_exact_project_name_disagrees_with_curated_alias_is_review():
    db=memorydb()
    a=_legacy_project_for_conflict(db,'Alpha REE Project','LEGACY-A')
    b=_legacy_project_for_conflict(db,'Beta REE Project','LEGACY-B',lat=-27,lon=123)
    db.execute('INSERT INTO project_aliases VALUES(?,?,?,?,?)',
               (b,'Alpha REE Project','alpha ree project','CURATED','OLD-B'))
    official={'source':'WA_SOURCE','native_id':'NATIVE-43',
              'name':'Alpha REE Project','state':'WA','latitude':-25,
              'longitude':121,'commodity':'REE','entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,official)=='REVIEW'
    result=db.execute("SELECT reason,matched_project_id FROM population_candidates WHERE source_key='WA_SOURCE'").fetchone()
    assert result['reason']=='REVIEW_CONFLICTING_IDENTITY_EVIDENCE'
    assert result['matched_project_id'] is None
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==2
    db.close()


def test_native_id_same_as_other_project_name_stays_unresolved():
    db=memorydb()
    a=_legacy_project_for_conflict(db,'Alpha REE Project','LEGACY-A')
    b=_legacy_project_for_conflict(db,'Beta REE Project','LEGACY-B',lat=-27,lon=123)
    db.execute('INSERT INTO project_aliases VALUES(?,?,?,?,?)',
               (b,'Old Beta Project','old beta project','WA_SOURCE','NATIVE-44'))
    official={'source':'WA_SOURCE','native_id':'NATIVE-44',
              'name':'Alpha REE Project','state':'WA','latitude':-25,
              'longitude':121,'commodity':'REE','entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,official)=='REVIEW'
    record=db.execute("SELECT reason,matched_project_id FROM population_candidates WHERE source_key='WA_SOURCE'").fetchone()
    assert record['reason']=='REVIEW_CONFLICTING_IDENTITY_EVIDENCE'
    assert record['matched_project_id'] is None
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==2
    db.close()


def test_native_id_state_conflict_remains_review_and_not_linked():
    db=memorydb()
    pid=_legacy_project_for_conflict(db,'Alpha REE Project','LEGACY-A')
    db.execute('INSERT INTO project_aliases VALUES(?,?,?,?,?)',
               (pid,'Source name','source name','GA_SOURCE','NATIVE-5'))
    official={'source':'GA_SOURCE','native_id':'NATIVE-5','name':'Different QLD REE Project',
              'state':'QLD','latitude':-22,'longitude':146,'commodity':'REE',
              'entity_level':'PROJECT','official':True}
    assert candidate_upsert(db,official)=='REVIEW'
    record=db.execute("SELECT reason,matched_project_id FROM population_candidates WHERE source_key='GA_SOURCE'").fetchone()
    assert record['reason']=='REVIEW_NATIVE_ID_STATE_CONFLICT'
    assert record['matched_project_id'] is None
    db.close()


def test_geological_deposit_records_preserve_conflicting_source_native_id():
    db=memorydb()
    a=_legacy_project_for_conflict(db,'Alpha REE Project','LEGACY-A')
    b=_legacy_project_for_conflict(db,'Beta REE Project','LEGACY-B',lat=-27,lon=123)
    for pid in (a,b):
        db.execute('INSERT INTO project_aliases VALUES(?,?,?,?,?)',
                   (pid,'Other name','other name','GA_SOURCE','NATIVE-6'))
    deposit={'source':'GA_SOURCE','native_id':'NATIVE-6','name':'Alpha REE Project',
             'state':'WA','latitude':-25,'longitude':121,'commodity':'REE',
             'entity_level':'DEPOSIT','official':True}
    assert candidate_upsert(db,deposit)=='REVIEW'
    record=db.execute("SELECT entity_level,reason,matched_project_id FROM population_candidates WHERE source_key='GA_SOURCE'").fetchone()
    assert record['entity_level']=='DEPOSIT'
    assert record['reason']=='REVIEW_NATIVE_ID_CONFLICT'
    assert record['matched_project_id'] is None
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==2
    db.close()


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
