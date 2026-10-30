"""Package a portable, verified DB snapshot and evidence extracts; no network."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path
from redact_release_outputs import redact_text_copy

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--snapshot-id',required=True);v=a.parse_args()
    root=Path(v.root).resolve();full=root/'reproducibility/snapshots'/v.snapshot_id
    stage=root/'reproducibility/portable'/v.snapshot_id
    if stage.exists():raise FileExistsError(stage)
    stage.mkdir(parents=True);portable=stage/'portable_snapshot';portable.mkdir()
    shutil.copytree(full/'tables',portable/'tables');shutil.copy2(full/'schema.json',portable/'schema.json')
    m=json.loads((full/'manifest.json').read_text());m['derived_from_full_manifest_sha256']=digest(full/'manifest.json');m['snapshot_id']+='-portable'
    external=[]
    for item in m['provenance_artifacts']:
        if not item.get('snapshot_file'):continue
        source=full/item['snapshot_file']
        if item['path'].endswith(('.zip','.sqlite')):
            external.append({'path':item['path'],'sha256':item.get('sha256'),'size_bytes':item.get('size_bytes')})
            item['available_at_full_release']=item['available'];item['available']=False;item.pop('snapshot_file',None)
        elif source.is_file():
            dest=portable/item['snapshot_file'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
            if redact_text_copy(dest):
                item['original_sha256']=item['sha256'];item['sha256']=digest(dest);item['size_bytes']=dest.stat().st_size;item['credential_query_redacted']=True
    m['external_source_archives_not_bundled']=external
    m['portable_scope']='All DB tables/schema plus included evidence extracts are self-contained and hash-verified. Original government acquisition ZIP archives remain in the full local snapshot and are listed by hash; this portable package rebuilds the reviewed database, not the original internet acquisition.'
    (portable/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    for folder in ['deliverable','research_20261029']:
        shutil.copytree(root/folder,stage/folder)
    for f in (root/'reproducibility').glob('*.py'):
        dest=stage/'reproducibility'/f.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(f,dest)
    shutil.copy2(root/'build_editable_workbook.py',stage/'reproducibility/build_editable_workbook.py')
    workpack=stage/'workpack_scripts';workpack.mkdir()
    for name in ['build_definition_review.py','build_complete_proposal_workpack.py','reproduce_86_401_cohorts.py','enrich_candidate_evidence.py','complete_487_source_review.py','build_row_level_trace_bundle.py','build_editable_workbook.py']:
        shutil.copy2(root/name,workpack/name)
    shutil.copy2(root/'deliverable/FULL_TRACE_REVIEW_20261030.md',stage/'README.md')
    manifest={str(f.relative_to(stage)).replace('\\','/'):{'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(stage.rglob('*')) if f.is_file()}
    (stage/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=root/'reproducibility'/('AU_REE_'+v.snapshot_id+'_portable.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(stage.rglob('*')):
            if not f.is_file():continue
            info=zipfile.ZipInfo(str(f.relative_to(stage)).replace('\\','/'),date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,f.read_bytes())
    print(json.dumps({'archive':str(archive),'sha256':digest(archive),'bytes':archive.stat().st_size,'files':len(manifest)+1}))
    slim=root/'reproducibility'/('AU_REE_'+v.snapshot_id+'_snapshot.zip')
    checks={}
    with zipfile.ZipFile(slim,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(stage.rglob('*')):
            if not f.is_file():continue
            name=str(f.relative_to(stage)).replace('\\','/')
            if not name.startswith(('portable_snapshot/','reproducibility/','workpack_scripts/')):continue
            content=f.read_bytes();info=zipfile.ZipInfo(name,date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content)
            checks[name]={'sha256':digest(f),'bytes':len(content)}
        readme='''# Portable reviewed database snapshot

Rebuild without network or external Python packages:

python reproducibility/build_census_database.py rebuild --snapshot-dir portable_snapshot --output census_review.sqlite
python reproducibility/build_census_database.py verify --snapshot-dir portable_snapshot --database census_review.sqlite

The editable workbook is portable_snapshot/evidence/deliverable/AU_REE_487_pre_MCDA_five_definition_review.xlsx.
Frozen search/extract evidence is under portable_snapshot/evidence/research_20261029/.
The snapshot manifest lists the original acquisition ZIP hashes which are retained in the full local release but not bundled here. All database tables and included evidence are self-contained and verified; replay of original government acquisition requires those original archives. Workpack scripts are supplied for use in the original expanded workpack.

This is a pre-MCDA census review. Candidate relations remain provisional; missing source evidence and incomplete legal rights chains remain HOLD/open. See the accompanying GitHub report for counts and limitations.
'''
        z.writestr('README.md',readme);z.writestr('PACKAGE_MANIFEST.json',json.dumps(checks,indent=2)+'\n')
    print(json.dumps({'snapshot_archive':str(slim),'sha256':digest(slim),'bytes':slim.stat().st_size}))
if __name__=='__main__':main()
