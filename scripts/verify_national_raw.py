#!/usr/bin/env python3
"""Fail closed before ANY nationwide REE filtering if a required raw source is missing."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def verify(root):
    root=pathlib.Path(root)
    data=json.loads((root/'national_raw_manifest.json').read_text(encoding='utf-8'))
    errors=[];sources=data.get('sources',{})
    for jurisdiction in ['GA_NATIONAL','WA','QLD','TAS','NSW','VIC','NT','SA']:
        if data.get('jurisdiction_status',{}).get(jurisdiction)!='RAW_COMPLETE':errors.append(f'{jurisdiction}: not complete')
    if data.get('jurisdiction_status',{}).get('ACT')!='NATIONAL_GA_SCOPE_ONLY_NOT_INDEPENDENT_STATE_SURVEY':errors.append('ACT: missing coverage classification')
    required=['GA_AIMR_REE_2026','GA_CRITICAL_DEPOSITS_2025','STATE_WA_MINDEX','STATE_QLD_MINOCC','STATE_TAS_MRT','NSW_METINDEX','VIC_MINSITE','NT_MODAT_WFS','SA_GEODATA','SA_PROJECT_WFS']
    for key in required:
        if key not in sources:errors.append('MISSING_RAW_SOURCE:'+key);continue
        items=sources[key] if isinstance(sources[key],list) else [sources[key]]
        for item in items:
            if item.get('status')!='RAW_COMPLETE':errors.append(key+': missing RAW_COMPLETE')
            if int(item.get('count',-1))<0:errors.append(key+': missing raw row count')
            if item.get('format')=='csv':
                path=root/item['path']
                if not path.is_file() or sha(path)!=item['sha256']:errors.append(key+': bad CSV SHA '+str(path))
                if path.is_file() and item.get('size_bytes') is not None and path.stat().st_size!=item['size_bytes']:errors.append(key+': file length mismatch')
            elif item.get('format')=='geojson':
                chunks=item.get('chunks') or []
                if not chunks or sum(x['count'] for x in chunks)!=item['count']:errors.append(key+': incomplete WFS page counts')
                for x in chunks:
                    p=root/x['path']
                    if not p.is_file() or sha(p)!=x['sha256']:errors.append(key+': bad WFS source chunk '+str(p))
            elif item.get('format')=='arcgis_json':
                path=root/item['cache_path']/'manifest.json'
                if not path.is_file() or sha(path)!=item['manifest_sha256']:errors.append(key+': bad ArcGIS manifest')
                else:
                    m=json.loads(path.read_text())
                    if m['records']!=item['count']:errors.append(key+': raw ArcGIS ID count mismatch')
                    for chunk in m['chunks']:
                        p=path.parent/chunk['file']
                        if not p.is_file() or sha(p)!=chunk['sha256']:errors.append(key+': ArcGIS chunk mismatch '+str(p))
    if data.get('errors'):errors.append('source errors: '+json.dumps(data['errors'],ensure_ascii=False)[:2500])
    if not data.get('complete'):errors.append('national raw manifest is incomplete')
    report={'status':'PASS' if not errors else 'BLOCKED','raw_source_count':len(sources),
            'raw_states_complete':[k for k,v in data.get('jurisdiction_status',{}).items() if v=='RAW_COMPLETE'],
            'ACT':'GA national layer coverage only; no independent mineral-survey file',
            'errors':errors,'no_ree_screening_performed':True}
    (root/'raw_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return not errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=pathlib.Path,default=pathlib.Path('work/national_raw'))
    args=p.parse_args();raise SystemExit(0 if verify(args.raw_dir) else 2)
