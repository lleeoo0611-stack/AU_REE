from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_national_raw import verify
from acquire_national_raw import S3_KEYS,fetch_wfs

def test_stored_all_sa_csv_classes():
    assert set(S3_KEYS)=={
      'sarig_md_details_exp.csv','sarig_md_commodity_exp.csv',
      'sarig_md_mineralogy_exp.csv','sarig_md_reference_exp.csv'}

def test_gate_fails_on_partial_jurisdiction(tmp_path):
    (tmp_path/'national_raw_manifest.json').write_text(json.dumps({'sources':{},'complete':False,'jurisdiction_status':{'SA':'RAW_INCOMPLETE'}}))
    assert verify(tmp_path) is False
    assert json.loads((tmp_path/'raw_validation.json').read_text())['status']=='BLOCKED'

def test_wfs_raw_does_not_filter_by_commodity(monkeypatch,tmp_path):
    import acquire_national_raw as module
    class Response:
        content=b'{"type":"FeatureCollection","numberMatched":2,"features":[{"id":"a","properties":{"commodity":"gold"}},{"id":"b","properties":{"commodity":"REE"}}]}'
        def json(self):return json.loads(self.content)
    monkeypatch.setattr(module,'get',lambda *args,**kwargs:Response())
    m=fetch_wfs(tmp_path,('X','NSW','https://example.invalid','foo:bar'))
    assert m['count']==2
    assert m['chunks'][0]['count']==2
    raw=json.loads((tmp_path/m['chunks'][0]['path']).read_text())
    assert raw['features'][0]['properties']['commodity']=='gold'

def test_wfs_fails_closed_on_partial_data(monkeypatch,tmp_path):
    import pytest,acquire_national_raw as module
    class Response:
        content=b'{"type":"FeatureCollection","numberMatched":2000,"features":[]}'
        def json(self):return json.loads(self.content)
    monkeypatch.setattr(module,'get',lambda *args,**kwargs:Response())
    with pytest.raises(RuntimeError,match='incomplete'):
        fetch_wfs(tmp_path,('X','NT','https://example.invalid','foo:bar'))
