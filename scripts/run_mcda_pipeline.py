#!/usr/bin/env python3
"""Run fixed-panel R MCDA from canonical verified stage exports, independently per panel."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANELS = ('CORE_BASELINE_V2','RESOURCE_EXTENDED_V2','STRATEGIC_EXTENDED_V2','FULL_PANEL_V2')

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(workspace, out, *, reps=1000, seed=20261029, rscript='Rscript'):
    workspace, out = Path(workspace).resolve(), Path(out).resolve()
    source = workspace/'outputs'
    settings = json.loads((ROOT/'config/eligibility.json').read_text())
    matrices = source/'04_eligibility'
    parameters = source/'05_r_export'
    dictionary, weights = parameters/'r_criteria_dictionary.csv', parameters/'r_weights.csv'
    # Missing canonical stages are an actionable failure, never an empty success.
    for path in (dictionary,weights, matrices/'mcda_eligibility_long.csv'):
        if not path.is_file():
            raise FileNotFoundError(f'Build canonical stages through r_export first: {path}')
    eligibility = {(r['project_id'],r['scenario']):r for r in rows(matrices/'mcda_eligibility_long.csv')}
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        raise FileExistsError('Use a new output directory to preserve prior run provenance: '+str(out))
    results = []
    panel_data = {}
    inputs = [dictionary,weights,matrices/'mcda_eligibility_long.csv',ROOT/'R/run_mcda.R',ROOT/'config/eligibility.json',ROOT/'config/r_analysis.json']
    with tempfile.TemporaryDirectory(prefix='mcda-',dir=out.parent) as td:
        stage = Path(td)
        for panel in PANELS:
            path = matrices/f'matrix_{panel}.csv'
            inputs.append(path)
            data = rows(path)
            panel_data[panel] = data
            cols = settings['scenarios'][panel]['criteria']
            if len({r['project_id'] for r in data})!=len(data):
                raise ValueError('Duplicate project identity in '+panel)
            if any(not all(c in r and math.isfinite(float(r[c])) for c in cols) for r in data):
                raise ValueError('Missing or non-finite fixed-panel criterion in '+panel)
            if any(eligibility.get((r['project_id'],panel),{}).get('point_ready')!='1' for r in data):
                raise ValueError('Matrix contains a project without canonical point-ready eligibility')
            result = {'panel':panel,'n':len(data),'criteria':cols}
            if len(data)<settings['minimum_subset_size']:
                result['status']='INSUFFICIENT_VERIFIED_CASES'
            else:
                cmd=[rscript,str(ROOT/'R/run_mcda.R'),'--input',str(path),'--criteria',str(dictionary),
                     '--weights',str(weights),'--illustrative','--perspective','development_driven',
                     '--seed',str(seed),'--reps',str(reps),'--out',str(stage/panel)]
                try:
                    proc=subprocess.run(cmd,capture_output=True,text=True,check=False)
                except OSError as exc:
                    proc=subprocess.CompletedProcess(cmd,127,'',str(exc))
                (stage/f'{panel}.log').write_text(proc.stdout+proc.stderr)
                result['status']='COMPLETED_ASSUMED_WEIGHTS' if proc.returncode==0 else 'R_FAILED'
                result['command']=cmd
                result['exit_code']=proc.returncode
            results.append(result)
        # Paired reruns isolate added criteria from changes in candidate membership.
        for panel in PANELS[1:]:
            ids={r['project_id'] for r in panel_data[panel]}
            common=[r for r in panel_data[PANELS[0]] if r['project_id'] in ids]
            if len(common)<settings['minimum_subset_size']:
                continue
            paired=stage/f'CORE_ON_{panel}'
            paired.mkdir()
            path=paired/'matrix.csv'
            columns=['project_id','project_name',*settings['scenarios'][PANELS[0]]['criteria']]
            with path.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore')
                writer.writeheader();writer.writerows(common)
            cmd=[rscript,str(ROOT/'R/run_mcda.R'),'--input',str(path),'--criteria',str(dictionary),
                 '--weights',str(weights),'--illustrative','--perspective','development_driven',
                 '--seed',str(seed),'--reps',str(reps),'--out',str(paired)]
            try:
                proc=subprocess.run(cmd,capture_output=True,text=True,check=False)
            except OSError as exc:
                proc=subprocess.CompletedProcess(cmd,127,'',str(exc))
            (paired/'run.log').write_text(proc.stdout+proc.stderr)
            results.append({'panel':'CORE_ON_'+panel,'n':len(common),'criteria':columns[2:],
                            'status':'COMPLETED_ASSUMED_WEIGHTS' if proc.returncode==0 else 'R_FAILED',
                            'exit_code':proc.returncode})
        manifest={'schema_version':'2.0','seed':seed,'reps':reps,'panels':results,
                  'weight_status':'ILLUSTRATIVE_SCENARIO_ASSUMPTIONS_NOT_ELICITED_AHP',
                  'data_snapshot':settings['snapshot_date'],
                  'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'git_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
                  'inputs':{str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):sha(p) for p in inputs}}
        (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        shutil.move(str(stage),str(out))
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',type=Path,default=ROOT/'work')
    p.add_argument('--out',type=Path,default=ROOT/'work'/'r_mcda'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    p.add_argument('--plan',action='store_true',help='Inspect canonical matrix sizes without writing or running R')
    p.add_argument('--reps',type=int,default=1000)
    p.add_argument('--seed',type=int,default=20261029)
    a=p.parse_args()
    if a.plan:
        print(json.dumps({panel:len(rows(a.workspace/'outputs'/'04_eligibility'/f'matrix_{panel}.csv')) for panel in PANELS},indent=2))
        return 0
    manifest=run(a.workspace,a.out,reps=a.reps,seed=a.seed)
    print(json.dumps(manifest['panels'],indent=2))
    return int(any(x['status']=='R_FAILED' for x in manifest['panels']))

if __name__=='__main__':
    raise SystemExit(main())
