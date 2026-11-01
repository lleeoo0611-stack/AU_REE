"""Reproducible, incremental, one-stage-at-a-time Australian REE research pipeline."""
from __future__ import annotations
import argparse,json,os,shutil,sqlite3,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone
from contextlib import closing
from . import __version__
from .core import ROOT, STAGES,canonical,config,connect,digest,filehash,setup,utc,writecsv
from .stages import RUNNERS

CONFIGS={'population':'sources.json','criteria':'criteria.json','gis':'gis.json','eligibility':'eligibility.json','r_export':'r_analysis.json'}
EXTRAS={'population':['inputs/legacy_r963_census.csv','inputs/legacy_r974_frozen_alternatives.csv','inputs/project_reviews.csv','inputs/project_identity_decisions.csv','inputs/source_documents.csv','inputs/evidence_approvals.csv'],
        'criteria':['inputs/legacy_r968_observations.csv','inputs/verified_observations.csv','inputs/source_documents.csv','inputs/evidence_approvals.csv'],
        'gis':['inputs/source_documents.csv','inputs/evidence_approvals.csv'],'eligibility':[],'r_export':['R/run_mcda.R']}

def cfgs():return {s:config(name) for s,name in CONFIGS.items()}

def own_fingerprint(stage,db,cfg,root,workspace,offline,source_keys=None):
    k=STAGES.index(stage)
    upstream=db.execute('SELECT fingerprint FROM stage_runs WHERE stage=?',(STAGES[k-1],)).fetchone() if k else None
    module=Path(__file__).parent/'stages'/(stage+'.py')
    paths={p:filehash(root/p) if (root/p).exists() else None for p in EXTRAS[stage]}
    if stage in ('population','criteria','gis'):
        from .evidence import _archive_path
        docs=root/'inputs'/'source_documents.csv'
        if docs.exists():
            import csv
            with docs.open(encoding='utf-8-sig',newline='') as handle:
                for item in csv.DictReader(handle):
                    relative=item.get('file_path','')
                    archive=_archive_path(root,relative)
                    paths[f'evidence_archive_{item.get("document_id", "")}']=filehash(archive) if archive is not None and archive.is_file() else 'MISSING'
    if stage=='population':
        for source in cfg['population']['sources']:
            if source.get('type')=='csv' and source.get('enabled'):
                value=Path(source['path'])
                path=value if value.is_absolute() else root/value
                paths[f"state_input_{source['key']}"]=filehash(path) if path.exists() else 'MISSING'
        cache=workspace/'cache'/'census'
        paths['cached_source_blobs']=digest([(str(p.relative_to(cache)),filehash(p)) for p in sorted(cache.rglob('*.json'))]) if cache.exists() else ''
    if stage=='gis':
        row=db.execute('SELECT group_concat(project_id || criterion || ifnull(source_sha256,"") || ifnull(geometry_sha256,""),"|") AS s FROM (SELECT project_id,criterion,source_sha256,geometry_sha256 FROM gis_metrics ORDER BY project_id,criterion)').fetchone()
        paths['gis_materialized_layer_hashes']=digest(row['s'] or '')
        for key,v in cfg['gis']['layers'].items():
            loc=v.get('local_geojson');p=Path(loc) if loc else None
            if p: p=(root/p) if not p.is_absolute() else p
            paths[key+'_local_geojson']=filehash(p) if p and p.exists() else None
    return digest({'stage':stage,'schema':'AU_REE_SCHEME_A_V1_0_4','upstream':upstream['fingerprint'] if upstream else None,
                   'config':cfg[stage],'paths':paths,'module_sha256':filehash(module),
                   'shared_core_sha256':filehash(Path(__file__).parent/'core.py'),
                   'source_adapters_sha256':filehash(Path(__file__).parent/'source_adapters.py') if stage=='population' else None,
                   'identity_policy_sha256':filehash(Path(__file__).parent/'identity_policy.py') if stage=='population' else None,
                   'offline':bool(offline),'selected_sources':sorted(source_keys or []),'runner_version':__version__})

def ensure_database(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with closing(connect(path)) as db, db:setup(db)

def run_one(stage,args,allcfg,force=False):
    root=ROOT;dbpath=args.db;workspace=args.workspace;ensure_database(dbpath)
    with closing(connect(dbpath)) as db, db:
        setup(db)
        idx=STAGES.index(stage)
        if idx:
            check=db.execute('SELECT status FROM stage_runs WHERE stage=?',(STAGES[idx-1],)).fetchone()
            if not check:raise RuntimeError(f'Prerequisite {STAGES[idx-1]} missing; use --through {stage}')
        expected=own_fingerprint(stage,db,allcfg,root,workspace,args.offline,getattr(args,"source_keys",None))
        prior=db.execute('SELECT fingerprint,status FROM stage_runs WHERE stage=?',(stage,)).fetchone()
        if prior and prior['fingerprint']==expected and not force:
            print(f'{stage:12s} REUSED {prior["status"]}')
            return {'reused':True,'status':prior['status']}
    if stage=='population' and args.refresh and not args.offline:
        cache=workspace/'cache'/'census'
        selected=getattr(args,'source_keys',None)
        if selected:
            for key in selected:
                target=cache/key
                if target.exists():
                    archive=workspace/'snapshots'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')/'census_raw_cache'/key
                    archive.parent.mkdir(parents=True,exist_ok=True)
                    shutil.move(str(target),str(archive))
        elif cache.exists():
            archive=workspace/'snapshots'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')/'census_raw_cache'
            archive.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(cache),str(archive))
    if stage=='gis' and args.refresh and not args.offline:
        cache=workspace/'cache'/'gis'
        if cache.exists():
            archive=workspace/'snapshots'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')/'gis_raw_cache'
            archive.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(cache),str(archive))
    with tempfile.TemporaryDirectory(prefix='.stage-'+stage+'-',dir=workspace) as temp:
        staged=Path(temp)/'candidate.sqlite';artifacts={}
        with closing(connect(dbpath)) as source, closing(connect(staged)) as dest, dest:source.backup(dest)
        with closing(connect(staged)) as db, db:
            setup(db);db.execute('BEGIN')
            context={'root':root,'workspace':workspace,'offline':args.offline,'artifacts':artifacts,
                     'hash_file':filehash, 'source_keys':getattr(args,'source_keys',None), 'sources':allcfg['population'], 'criteria':allcfg['criteria'], 'gis':allcfg['gis'], 'eligibility':allcfg['eligibility'], 'r_analysis':allcfg['r_export']}
            result=RUNNERS[stage](db,context)
            signature=own_fingerprint(stage,db,allcfg,root,workspace,args.offline,getattr(args,"source_keys",None))
            db.execute('''INSERT OR REPLACE INTO stage_runs(stage,fingerprint,status,input_hash,run_time,summary_json) VALUES(?,?,?,?,?,?)''',
                       (stage,signature,result['status'],digest(result),utc(),canonical(result)))
            db.execute('INSERT INTO stage_run_history(stage,fingerprint,status,input_hash,run_time,summary_json) VALUES(?,?,?,?,?,?)',(stage,signature,result['status'],digest(result),utc(),canonical(result)))
            for s in STAGES[STAGES.index(stage)+1:]:db.execute('DELETE FROM stage_runs WHERE stage=?',(s,))
            db.commit()
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('SQLite integrity_check FAILED')
            if db.execute('PRAGMA foreign_key_check').fetchall():raise RuntimeError('SQLite FK check FAILED')
        # Prepare every published output in a private staging directory before
        # replacing the canonical database. A formatting/export error cannot
        # mark an incomplete stage as completed.
        prepared=Path(temp)/'published';prepared.mkdir()
        for name,(rows,cols) in artifacts.items():writecsv(prepared/name,rows,cols)
        manifest={'stage':stage,'version':__version__,'fingerprint':signature,'result':result,
                  'stage_code_sha256':filehash(Path(__file__).parent/'stages'/(stage+'.py')),
                  'snapshot_time':utc(),'offline':args.offline}
        (prepared/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
        if stage=='population':
            with closing(connect(staged)) as db, db:
                writecsv(prepared/'population_master.csv',[dict(x) for x in db.execute('SELECT * FROM project_master ORDER BY project_id')],[x[1] for x in db.execute('PRAGMA table_info(project_master)')])
                writecsv(prepared/'population_review_queue.csv',[dict(x) for x in db.execute("SELECT * FROM population_candidates WHERE decision IN ('REVIEW','EXCLUDED') ORDER BY source_key,raw_name")],[x[1] for x in db.execute('PRAGMA table_info(population_candidates)')])
                writecsv(prepared/'population_source_registry.csv',[dict(x) for x in db.execute('SELECT * FROM source_registry ORDER BY source_key')],[x[1] for x in db.execute('PRAGMA table_info(source_registry)')])
                for tbl,filename,sort in (
                    ('source_feature_snapshot','population_raw_feature_index.csv','source_key,candidate_id'),
                    ('geological_entity','geological_entities.csv','state,canonical_name'),
                    ('geological_entity_source','geological_entity_provenance.csv','source_key,native_id'),
                    ('extended_occurrence_inventory','extended_occurrence_inventory.csv','screening_tier,candidate_id'),
                    ('project_geological_relation','project_deposit_relations.csv','project_id,entity_id'),
                    ('dedup_candidate_pairs','dedup_candidate_pairs.csv','candidate_a,candidate_b'),
                    ('identity_review_decisions','project_identity_decisions_audit.csv','candidate_id'),
                ):
                    writecsv(prepared/filename,[dict(row) for row in db.execute(f'SELECT * FROM {tbl} ORDER BY {sort}')],
                             [x[1] for x in db.execute(f'PRAGMA table_info({tbl})')])
                candidates=[dict(x) for x in db.execute('SELECT candidate_id,source_key,native_id,raw_name,state,company,entity_level,decision,matched_project_id,reason,source_url,original_json FROM population_candidates ORDER BY source_key,raw_name')]
                audit=[];duplicates=[]
                for c in candidates:
                    original=json.loads(c.pop('original_json') or '{}')
                    checks=original.get('normalisation') or {}
                    row={**c,'operator_check':checks.get('company_validation','NOT_REPORTED'),
                        'state_check':checks.get('state_validation','REQUIRES_REVIEW'),
                        'project_name_hint':original.get('project_name_hint','')}
                    audit.append(row)
                    suggestions=checks.get('possible_duplicates') or []
                    if suggestions:
                        duplicates.append({**row,'nearby_projects_json':json.dumps(suggestions,ensure_ascii=False)})
                auditcols=['candidate_id','source_key','native_id','raw_name','state','company','entity_level','decision','matched_project_id','reason','source_url','operator_check','state_check','project_name_hint']
                writecsv(prepared/'population_identity_audit.csv',audit,auditcols)
                writecsv(prepared/'population_duplicate_review.csv',duplicates,auditcols+['nearby_projects_json'])
                # Two agencies can describe the same deposit/occurrence without
                # either having legal evidence of a project-level identity.
                # Report duplicates across source candidates but do not delete.
                from collections import defaultdict
                cross=defaultdict(list)
                for c in candidates:
                    if c['decision']!='EXCLUDED' and c['raw_name'] and c['state']:
                        from .core import norm as norm_name
                        cross[(norm_name(c['raw_name']),c['state'])].append(c)
                rows_cross=[]
                for (name,state),group in sorted(cross.items()):
                    for i,a in enumerate(group):
                        for b in group[i+1:]:
                            if a['source_key']==b['source_key']:continue
                            rows_cross.append({'candidate_a':a['candidate_id'],'candidate_b':b['candidate_id'],
                                               'source_a':a['source_key'],'source_b':b['source_key'],
                                               'normalized_name':name,'state':state,
                                               'operator_a':a['company'],'operator_b':b['company'],
                                               'operator_conflict':bool(a['company'] and b['company'] and norm_name(a['company'])!=norm_name(b['company'])),
                                               'review_action':'CHECK_ENTITY_IDENTITY_AND_PARENT_PROJECT'})
                writecsv(prepared/'population_cross_source_duplicates.csv',rows_cross,
                         ['candidate_a','candidate_b','source_a','source_b','normalized_name','state',
                          'operator_a','operator_b','operator_conflict','review_action'])


        # Archive stale downstream exports and the previous version of this
        # stage; a refreshed census/criterion/GIS run must not leave old R
        # matrices available in the active outputs directory.
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        for ix, later in enumerate(STAGES[STAGES.index(stage)+1:],start=STAGES.index(stage)+2):
            obsolete=workspace/'outputs'/f'{ix:02}_{later}'
            if obsolete.exists():
                archive=workspace/'snapshots'/stamp/obsolete.name
                archive.parent.mkdir(parents=True,exist_ok=True)
                shutil.move(str(obsolete),str(archive))
        target=workspace/'outputs'/f'{STAGES.index(stage)+1:02}_{stage}'
        if target.exists():
            archive=workspace/'snapshots'/stamp/target.name
            archive.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(target),str(archive))
        os.replace(staged,dbpath)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(prepared),str(target))
    print(f'{stage:12s} {result["status"]}; summary: {json.dumps(result,ensure_ascii=False)[:380]}')
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description='Australian rare-earth research five-stage pipeline')
    p.add_argument('command',choices=['plan','run','status'])
    sel=p.add_mutually_exclusive_group()
    sel.add_argument('--stage',choices=STAGES)
    sel.add_argument('--through',choices=STAGES)
    p.add_argument('--db',type=Path,default=ROOT/'work'/'research.sqlite')
    p.add_argument('--workspace',type=Path,default=ROOT/'work')
    p.add_argument('--offline',action='store_true',help='Use frozen/locally cached sources only; no network requests')
    p.add_argument('--force',action='store_true',help='Recalculate selected stage even if fingerprint is equal')
    p.add_argument('--refresh',action='store_true',help='Refresh online source snapshots rather than cache reuse')
    p.add_argument('--source-key',action='append',dest='source_keys',help='Only fetch named population source(s), repeatable; stage population only')
    a=p.parse_args(argv);a.db=a.db.resolve();a.workspace=a.workspace.resolve();a.workspace.mkdir(parents=True,exist_ok=True)
    if a.command=='plan':
        if not a.stage and not a.through:a.through='r_export'
        end=STAGES.index(a.stage or a.through)
        for i,s in enumerate(STAGES[:end+1]):print(f'{i+1}. {s} (config/{CONFIGS[s]})')
        return 0
    if a.command=='status':
        if not a.db.exists():print('No SQLite database yet');return 0
        with closing(connect(a.db)) as db, db:
            setup(db)
            for stage in STAGES:
                record=db.execute('SELECT status,run_time FROM stage_runs WHERE stage=?',(stage,)).fetchone()
                print(f'{stage:12s} {record["status"] if record else "PENDING"} {record["run_time"] if record else ""}')
        return 0
    if not a.stage and not a.through:p.error('run requires --stage or --through')
    allcfg=cfgs()
    if a.source_keys:
        known={x['key'] for x in allcfg['population']['sources']}
        unknown=set(a.source_keys)-known
        if unknown:p.error('Unknown source key(s): '+', '.join(sorted(unknown)))
        if a.stage not in (None,'population') and not (a.through and a.through in STAGES):p.error('--source-key only valid for population and --through runs')
    targets=[a.stage] if a.stage else STAGES[:STAGES.index(a.through)+1]
    try:
        for s in targets:run_one(s,a,allcfg,force=a.force or a.refresh)
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
