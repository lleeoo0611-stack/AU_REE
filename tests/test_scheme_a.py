"""Scheme A acceptance tests: mineral inventory never auto-enters Project Master."""
import csv,hashlib,sqlite3
from pathlib import Path
from au_ree.core import setup,digest
from au_ree.evidence import reload_registry
from au_ree.identity_policy import apply_identity_decisions,propose_dedup,propose_parents
from au_ree.stages.population import candidate_upsert


def memorydb():
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;setup(db);return db


def record(source='GA',native='a',name='West monazite',commodity='Monazite',entity='OCCURRENCE'):
    return {'source':source,'native_id':native,'name':name,'state':'WA',
      'latitude':-25.,'longitude':120.,'commodity':commodity,'entity_level':entity,
      'official':True,'source_url':'https://example.gov.au/record',
      'source_raw_attributes':{'site_code':native,'commodity':commodity}}


def test_mineral_only_is_extended_and_not_project():
    db=memorydb()
    assert candidate_upsert(db,record())=='REVIEW'
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==0
    row=db.execute('SELECT screening_tier,disposition FROM extended_occurrence_inventory').fetchone()
    assert tuple(row)==('E2_REE_MINERAL_ONLY','BACKGROUND_ONLY')
    assert db.execute('SELECT count(*) FROM source_feature_snapshot').fetchone()[0]==1
    assert db.execute('SELECT count(*) FROM geological_entity').fetchone()[0]==1


def test_official_project_requires_document_approval():
    db=memorydb()
    assert candidate_upsert(db,record(entity='PROJECT',commodity='REE',name='East REE Project'))=='REVIEW'
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==0
    assert db.execute('SELECT reason FROM population_candidates').fetchone()[0]=='PROJECT_IDENTITY_NEEDS_DOCUMENT_APPROVAL'


def test_exact_cross_source_is_proposal_not_merge():
    db=memorydb()
    candidate_upsert(db,record(source='WA'))
    candidate_upsert(db,record(source='GA'))
    assert propose_dedup(db)>=1
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==0
    assert set(r['decision_status'] for r in db.execute('SELECT * FROM dedup_candidate_pairs'))=={'PROPOSED_ONLY'}
    assert db.execute('SELECT count(*) FROM geological_entity').fetchone()[0]==2


def test_unapproved_parent_hint_cannot_merge():
    db=memorydb()
    base=record(source='legacy_r963_frozen',entity='PROJECT',commodity='REE',name='Alpha REE Project')
    assert candidate_upsert(db,base)=='ADDED'
    child=record(source='WA',native='D-1',commodity='REE',entity='DEPOSIT',name='Alpha orebody')
    child['project_name_hint']='Alpha REE Project'
    assert candidate_upsert(db,child)=='REVIEW'
    assert propose_parents(db)==1
    row=db.execute('SELECT decision_status,relation_type FROM project_geological_relation').fetchone()
    assert tuple(row)==('PROPOSED_ONLY','PART_OF_PROJECT')


def write_csv(p,heads,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=heads);w.writeheader();w.writerows(rows)


def test_approved_project_identity_and_revocation(tmp_path):
    db=memorydb();c=record(source='SA_PROJECT',native='P1',commodity='REE',entity='PROJECT',name='Acacia')
    candidate_upsert(db,c)
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    evidence=tmp_path/'inputs/evidence/project.txt';evidence.parent.mkdir(parents=True)
    evidence.write_text('Independent official project evidence, TEST FIXTURE',encoding='utf8')
    sha=hashlib.sha256(evidence.read_bytes()).hexdigest()
    uri='https://example.gov.au/project.pdf'
    write_csv(tmp_path/'inputs/source_documents.csv',['document_id','file_path','source_url','sha256'],[{'document_id':'D1','file_path':'inputs/evidence/project.txt','source_url':uri,'sha256':sha}])
    write_csv(tmp_path/'inputs/evidence_approvals.csv',['approval_ref','record_type','document_id','reviewer','decision','reviewed_at'],[{'approval_ref':'APP1','record_type':'PROJECT_REVIEW','document_id':'D1','reviewer':'Test Reviewer','decision':'APPROVED','reviewed_at':'2026-10-01'}])
    decisions=tmp_path/'inputs/project_identity_decisions.csv'
    write_csv(decisions,['candidate_id','decision','project_name','project_id','source_url','source_sha256','evidence_date','approval_ref'],[
      {'candidate_id':cid,'decision':'APPROVE_NEW_PROJECT','project_name':'Acacia REE Development','project_id':'','source_url':uri,'source_sha256':sha,'evidence_date':'2026-10-01','approval_ref':'APP1'}])
    reload_registry(db,tmp_path,'2026-10-29')
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['approved_new']==1
    first=db.execute('SELECT project_id FROM project_master').fetchone()[0]
    assert db.execute('SELECT population_status FROM project_master').fetchone()[0]=='EVIDENCE_BACKED_PROJECT'
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['approved_new']==1
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==1
    assert db.execute('SELECT project_id FROM project_master').fetchone()[0]==first
    # Approval can be withdrawn without deleting the canonical ID or provenance.
    write_csv(tmp_path/'inputs/evidence_approvals.csv',['approval_ref','record_type','document_id','reviewer','decision','reviewed_at'],[])
    reload_registry(db,tmp_path,'2026-10-29')
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['rejected_or_pending']==1
    assert db.execute('SELECT population_status FROM project_master').fetchone()[0]=='IDENTITY_APPROVAL_EXPIRED'


def test_new_project_detail_review_in_same_stage(tmp_path):
    from au_ree.stages.population import run as population_run
    from au_ree.core import filehash
    db=memorydb()
    candidate=record(source='SA_OFFICIAL_PROJECTS',native='O-22',name='Acacia REE',commodity='REE',entity='PROJECT')
    assert candidate_upsert(db,candidate)=='REVIEW'
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    document=tmp_path/'inputs/evidence/report.txt';document.parent.mkdir(parents=True)
    document.write_text('Approved project document synthetic test only',encoding='utf8')
    sha=hashlib.sha256(document.read_bytes()).hexdigest();url='https://example.gov.au/acacia'
    write_csv(tmp_path/'inputs/source_documents.csv',['document_id','file_path','source_url','sha256'],[
      {'document_id':'D1','file_path':'inputs/evidence/report.txt','source_url':url,'sha256':sha}])
    write_csv(tmp_path/'inputs/evidence_approvals.csv',['approval_ref','record_type','document_id','reviewer','decision','reviewed_at'],[
      {'approval_ref':'A1','record_type':'PROJECT_REVIEW','document_id':'D1','reviewer':'Named Reviewer','decision':'APPROVED','reviewed_at':'2026-10-01'}])
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',
      ['candidate_id','decision','project_name','project_id','source_url','source_sha256','evidence_date','approval_ref'],[
      {'candidate_id':cid,'decision':'APPROVE_NEW_PROJECT','project_name':'Acacia REE','project_id':'AU-REE-00001',
        'source_url':url,'source_sha256':sha,'evidence_date':'2026-10-01','approval_ref':'A1'}])
    write_csv(tmp_path/'inputs/project_reviews.csv',
      ['project_id','activity','lifecycle','ree_role','deposit_family','latitude','longitude','coordinate_uncertainty_km',
       'source_url','evidence_date','source_sha256','approval_ref'],[
      {'project_id':'AU-REE-00001','activity':'ACTIVE','lifecycle':'PFS','ree_role':'REE_PRIMARY',
       'deposit_family':'HARD_ROCK','latitude':-25,'longitude':120,'source_url':url,
       'evidence_date':'2026-10-01','source_sha256':sha,'approval_ref':'A1'}])
    ctx={'root':tmp_path,'workspace':tmp_path/'work','offline':True,
         'criteria':{'freeze_date':'2026-10-29'},'sources':{'sources':[]},
         'hash_file':filehash,'source_keys':None}
    result=population_run(db,ctx)
    assert result['identity_decisions']['approved_new']==1
    assert result['reviewed_project_updates']==1
    row=db.execute('SELECT population_status,activity,lifecycle,ree_role FROM project_master').fetchone()
    assert tuple(row)==('EVIDENCE_BACKED_PROJECT','ACTIVE','PFS','REE_PRIMARY')
    assert db.execute("SELECT verification FROM project_coordinates").fetchone()[0]=='VERIFIED'


def _identity_fixture(root, entries):
    """Synthetic archived evidence; no real research source is approved."""
    doc=root/'inputs/evidence/project.txt'
    doc.parent.mkdir(parents=True,exist_ok=True)
    doc.write_text('Synthetic Project ID replay fixture',encoding='utf8')
    sha=hashlib.sha256(doc.read_bytes()).hexdigest()
    url='https://example.gov.au/replay-project'
    write_csv(root/'inputs/source_documents.csv',
              ['document_id','file_path','source_url','sha256'],
              [{'document_id':'FIXTURE','file_path':'inputs/evidence/project.txt','source_url':url,'sha256':sha}])
    write_csv(root/'inputs/evidence_approvals.csv',
              ['approval_ref','record_type','document_id','reviewer','decision','reviewed_at'],
              [{'approval_ref':'TEST_ONLY','record_type':'PROJECT_REVIEW','document_id':'FIXTURE',
                'reviewer':'Synthetic Reviewer','decision':'APPROVED','reviewed_at':'2026-10-01'}])
    heads=['candidate_id','decision','project_name','project_id','source_url','source_sha256',
           'evidence_date','approval_ref']
    rows=[dict(candidate_id=cid,decision='APPROVE_NEW_PROJECT',project_name=name,
               project_id=pid,source_url=url,source_sha256=sha,evidence_date='2026-10-01',
               approval_ref='TEST_ONLY') for cid,name,pid in entries]
    write_csv(root/'inputs/project_identity_decisions.csv',heads,rows)
    return rows,heads


def test_approved_project_id_does_not_change_when_new_candidate_is_added(tmp_path):
    from au_ree.identity_policy import stable_approved_project_id
    results={}
    for case,natives in [('original',['B']),('expanded',['A','B'])]:
        root=tmp_path/case
        db=memorydb()
        entries=[]
        for native in natives:
            c=record(source='WA_SOURCE',native=native,name=f'Synthetic {native} REE',
                     commodity='REE',entity='PROJECT')
            assert candidate_upsert(db,c)=='REVIEW'
            cid=db.execute('SELECT candidate_id FROM population_candidates WHERE native_id=?',(native,)).fetchone()[0]
            entries.append((cid,f'Synthetic {native} REE',''))
        _identity_fixture(root,entries)
        reload_registry(db,root,'2026-10-29')
        assert apply_identity_decisions(db,root,'2026-10-29')['approved_new']==len(entries)
        bcid=db.execute("SELECT candidate_id FROM population_candidates WHERE native_id='B'").fetchone()[0]
        results[case]=db.execute('SELECT matched_project_id FROM population_candidates WHERE candidate_id=?',(bcid,)).fetchone()[0]
        assert results[case]==stable_approved_project_id(bcid)
    assert results['original']==results['expanded']


def test_unapproved_id_cannot_poison_future_project_identity(tmp_path):
    db=memorydb()
    candidate_upsert(db,record(source='WA_SOURCE',native='X',name='Synthetic X REE',commodity='REE',entity='PROJECT'))
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    rows,heads=_identity_fixture(tmp_path,[(cid,'Synthetic X REE','AU-REE-00555')])
    rows[0]['source_sha256']='0'*64
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    reload_registry(db,tmp_path,'2026-10-29')
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['rejected_or_pending']==1
    assert db.execute('SELECT resolved_project_id FROM identity_review_decisions').fetchone()[0] is None
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==0
    # The unapproved requested ID must not be carried over into later approval.
    rows[0]['source_sha256']=hashlib.sha256((tmp_path/'inputs/evidence/project.txt').read_bytes()).hexdigest()
    rows[0]['project_id']=''
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['approved_new']==1
    from au_ree.identity_policy import stable_approved_project_id
    assert db.execute('SELECT project_id FROM project_master').fetchone()[0]==stable_approved_project_id(cid)


def test_historically_approved_project_id_cannot_be_silently_changed(tmp_path):
    db=memorydb()
    candidate_upsert(db,record(source='WA_SOURCE',native='Y',name='Synthetic Y REE',commodity='REE',entity='PROJECT'))
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    rows,heads=_identity_fixture(tmp_path,[(cid,'Synthetic Y REE','AU-REE-00040')])
    reload_registry(db,tmp_path,'2026-10-29')
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['approved_new']==1
    rows[0]['project_id']='AU-REE-00041'
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['rejected_or_pending']==1
    assert db.execute('SELECT resolved_project_id FROM identity_review_decisions').fetchone()[0]=='AU-REE-00040'
    assert db.execute('SELECT review_reason FROM identity_review_decisions').fetchone()[0]=='STABLE_PROJECT_ID_CHANGE_REQUIRES_CORRECTION'
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==1
    assert db.execute('SELECT population_status FROM project_master').fetchone()[0]=='IDENTITY_APPROVAL_EXPIRED'


def test_invalid_evidence_date_is_not_accepted_as_historical(tmp_path):
    db=memorydb()
    candidate_upsert(db,record(source='WA_SOURCE',native='Z',name='Synthetic Z REE',commodity='REE',entity='PROJECT'))
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    rows,heads=_identity_fixture(tmp_path,[(cid,'Synthetic Z REE','')])
    rows[0]['evidence_date']='2026-1-01'
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    reload_registry(db,tmp_path,'2026-10-29')
    assert apply_identity_decisions(db,tmp_path,'2026-10-29')['rejected_or_pending']==1
    assert db.execute('SELECT count(*) FROM project_master').fetchone()[0]==0


def test_deposit_source_cannot_be_approved_as_new_independent_project(tmp_path):
    db=memorydb()
    c=record(source='WA_SOURCE',native='D-NEW',name='Synthetic REE deposit',commodity='REE',entity='DEPOSIT')
    assert candidate_upsert(db,c)=='REVIEW'
    cid=db.execute('SELECT candidate_id FROM population_candidates').fetchone()[0]
    _identity_fixture(tmp_path,[(cid,'Fabricated parent Project','')])
    reload_registry(db,tmp_path,'2026-10-29')
    stats=apply_identity_decisions(db,tmp_path,'2026-10-29')
    assert stats['approved_new']==0
    assert stats['rejected_or_pending']==1
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==0
    assert db.execute('SELECT review_reason FROM identity_review_decisions').fetchone()[0]=='SOURCE_ENTITY_IS_NOT_A_PROJECT'


def test_unverified_legacy_parent_cannot_receive_document_approved_deposit(tmp_path):
    db=memorydb()
    legacy=record(source='legacy_r963_frozen',native='L-ONLY',name='Legacy REE parent',
                  commodity='REE',entity='PROJECT')
    assert candidate_upsert(db,legacy)=='ADDED'
    legacy_id=db.execute('SELECT project_id FROM project_master').fetchone()[0]
    assert db.execute('SELECT population_status FROM project_master').fetchone()[0]=='LEGACY_UNVERIFIED'
    child=record(source='WA_SOURCE',native='D-CHILD',name='Legacy parent orebody',
                 commodity='REE',entity='DEPOSIT')
    assert candidate_upsert(db,child)=='REVIEW'
    cid=db.execute("SELECT candidate_id FROM population_candidates WHERE source_key='WA_SOURCE'").fetchone()[0]
    rows,heads=_identity_fixture(tmp_path,[(cid,'Legacy REE parent',legacy_id)])
    rows[0]['decision']='LINK_EXISTING_PROJECT'
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    reload_registry(db,tmp_path,'2026-10-29')
    stats=apply_identity_decisions(db,tmp_path,'2026-10-29')
    assert stats['linked_existing']==0
    assert stats['rejected_or_pending']==1
    assert db.execute('SELECT review_reason FROM identity_review_decisions WHERE candidate_id=?',(cid,)).fetchone()[0]=='PARENT_PROJECT_IDENTITY_NOT_INDEPENDENTLY_APPROVED'
    assert db.execute("SELECT COUNT(*) FROM project_geological_relation WHERE decision_status='DOCUMENT_APPROVED'").fetchone()[0]==0
    assert db.execute('SELECT matched_project_id FROM population_candidates WHERE candidate_id=?',(cid,)).fetchone()[0] is None


def test_approved_project_parent_precedes_deposit_link_regardless_of_candidate_sort(tmp_path):
    db=memorydb()
    parent_source='WA_SOURCE'
    parent_native='PARENT'
    parent_cid=digest([parent_source,parent_native])[:32]
    child_native=next(f'CHILD{i}' for i in range(100)
                      if digest([parent_source,f'CHILD{i}'])[:32]<parent_cid)
    parent=record(source=parent_source,native=parent_native,name='Synthetic South REE Project',
                  commodity='REE',entity='PROJECT')
    child=record(source=parent_source,native=child_native,name='Synthetic South REE Deposit',
                 commodity='REE',entity='DEPOSIT')
    assert candidate_upsert(db,parent)=='REVIEW'
    assert candidate_upsert(db,child)=='REVIEW'
    child_cid=digest([parent_source,child_native])[:32]
    assert child_cid<parent_cid  # Old lexical replay would process child first.
    project_id='AU-REE-90001'
    rows,heads=_identity_fixture(tmp_path,[
        (child_cid,'',project_id),
        (parent_cid,'Synthetic South REE Project',project_id),
    ])
    rows[0]['decision']='LINK_EXISTING_PROJECT'
    write_csv(tmp_path/'inputs/project_identity_decisions.csv',heads,rows)
    reload_registry(db,tmp_path,'2026-10-29')
    stats=apply_identity_decisions(db,tmp_path,'2026-10-29')
    assert stats['approved_new']==1
    assert stats['linked_existing']==1
    assert stats['rejected_or_pending']==0
    assert db.execute('SELECT population_status FROM project_master WHERE project_id=?',(project_id,)).fetchone()[0]=='EVIDENCE_BACKED_PROJECT'
    row=db.execute('''SELECT p.project_id,r.relation_type,r.decision_status
                      FROM project_geological_relation r
                      JOIN project_master p ON p.project_id=r.project_id''').fetchone()
    assert tuple(row)==(project_id,'PART_OF_PROJECT','DOCUMENT_APPROVED')
    assert db.execute('SELECT decision FROM population_candidates WHERE candidate_id=?',
                      (child_cid,)).fetchone()[0]=='APPROVED_PROJECT_IDENTITY'
    # Replay must preserve the same verified parent relation and Project ID.
    again=apply_identity_decisions(db,tmp_path,'2026-10-29')
    assert again['approved_new']==1 and again['linked_existing']==1
    assert db.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]==1
    assert db.execute('SELECT COUNT(*) FROM project_geological_relation').fetchone()[0]==1
