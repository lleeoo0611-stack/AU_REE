"""Independent, file-byte-verified evidence approvals (never trust an input VERIFIED flag).

Approval requires: separately curated source_documents.csv and evidence_approvals.csv,
actual archived bytes matching SHA-256, a named reviewer, explicit APPROVED
status and a valid actual review date. The source cutoff is checked against
source evidence dates by its consumer, not against reviewer sign-off time.
A checksum alone establishes byte identity, not the reliability or authorship of a publication.
"""
from __future__ import annotations
import re
from datetime import date
from pathlib import Path
from .core import filehash,readcsv,utc,event

HEX64 = re.compile(r'^[0-9a-fA-F]{64}$')
VALID_TYPES = {'OBSERVATION','PROJECT_REVIEW','GIS_LAYER'}


def _day(text):
    try:return date.fromisoformat(str(text).strip())
    except (ValueError,TypeError):return None


def _archive_path(root,raw):
    """Allow only approved local evidence archives; never accept arbitrary paths."""
    if not raw:
        return None
    rel = str(raw).replace('\\', '/')
    allowed = ('inputs/evidence/', 'work/structural_round01/originals/')
    if not any(rel.startswith(prefix) for prefix in allowed):
        return None
    root = Path(root).resolve()
    p = (root / rel).resolve()
    for prefix in allowed:
        archive = (root / prefix).resolve()
        if rel.startswith(prefix) and p.is_relative_to(archive):
            return p
    return None


def reload_registry(db,root,as_of):
    db.execute('DELETE FROM evidence_approvals')
    db.execute('DELETE FROM source_documents')
    docpath=Path(root)/'inputs'/'source_documents.csv'
    apprpath=Path(root)/'inputs'/'evidence_approvals.csv'
    docs=readcsv(docpath) if docpath.exists() else []
    approvals=readcsv(apprpath) if apprpath.exists() else []
    for row in docs:
        did=(row.get('document_id') or '').strip()
        if not did:continue
        rel=(row.get('file_path') or '').strip()
        p=_archive_path(root,rel)
        expected=(row.get('sha256') or '').strip().lower()
        actual=filehash(p) if p is not None and p.is_file() else ''
        uri=(row.get('source_url') or '').strip()
        if not p or not p.is_file():status='ARCHIVE_MISSING_OR_UNSAFE'
        elif not HEX64.fullmatch(expected):status='INVALID_DECLARED_SHA256'
        elif actual != expected:status='HASH_MISMATCH'
        elif not uri.startswith('https://'):status='SOURCE_URL_MISSING'
        else:status='HASH_MATCH_REVIEW_REQUIRED'
        db.execute('''INSERT INTO source_documents(document_id,file_path,source_url,declared_sha256,actual_sha256,hash_status,checked_at)
                      VALUES(?,?,?,?,?,?,?)''',(did,rel,uri,expected,actual,status,utc()))
        if status!='HASH_MATCH_REVIEW_REQUIRED':event(db,'evidence',did,status,rel)
    for row in approvals:
        ref=(row.get('approval_ref') or '').strip()
        typ=(row.get('record_type') or '').strip().upper()
        did=(row.get('document_id') or '').strip()
        who=(row.get('reviewer') or '').strip()
        decision=(row.get('decision') or '').strip().upper()
        dt=(row.get('reviewed_at') or '').strip()
        if not ref:continue
        d=db.execute('SELECT * FROM source_documents WHERE document_id=?',(did,)).fetchone()
        valid=(typ in VALID_TYPES and decision=='APPROVED' and bool(who)
               and _day(dt) is not None and _day(as_of) is not None
               and d is not None and d['hash_status']=='HASH_MATCH_REVIEW_REQUIRED')
        status='APPROVED' if valid else 'NOT_APPROVED'
        db.execute('''INSERT INTO evidence_approvals(approval_ref,record_type,document_id,reviewer,decision,reviewed_at,status,notes)
                      VALUES(?,?,?,?,?,?,?,?)''',(ref,typ,did,who,decision,dt,status,(row.get('notes') or '')[:1000]))
        if status!='APPROVED':event(db,'evidence',ref,'APPROVAL_NOT_ACCEPTED',f'{typ}:{did}:{decision}')
    return {'documents':len(docs),'hash_matched':db.execute("SELECT count(*) FROM source_documents WHERE hash_status='HASH_MATCH_REVIEW_REQUIRED'").fetchone()[0],
            'approved':db.execute("SELECT count(*) FROM evidence_approvals WHERE status='APPROVED'").fetchone()[0]}


def verify(db,approval_ref,record_type,source_url,sha256,archive_path=None,*,root=None):
    """Require independent approval and, when root is given, current archived bytes.

    The cached approval registry is not a substitute for a last-mile SHA-256
    check; a report can be modified or deleted after reload_registry().
    """
    if not approval_ref or not source_url or not HEX64.fullmatch(str(sha256 or '')):
        return False
    row=db.execute('''SELECT a.status,a.record_type,d.file_path,d.source_url,d.actual_sha256,d.hash_status
        FROM evidence_approvals a JOIN source_documents d ON d.document_id=a.document_id
        WHERE a.approval_ref=?''',(approval_ref,)).fetchone()
    approved=bool(row and row['status']=='APPROVED' and row['record_type']==record_type
                  and row['hash_status']=='HASH_MATCH_REVIEW_REQUIRED'
                  and source_url==row['source_url'] and sha256.lower()==row['actual_sha256']
                  and (archive_path is None or archive_path==row['file_path']))
    if not approved:
        return False
    if root is not None:
        archived=_archive_path(root,row['file_path'])
        if archived is None or not archived.is_file():
            return False
        if filehash(archived)!=row['actual_sha256']:
            return False
    return True
