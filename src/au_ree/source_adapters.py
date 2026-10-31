"""Official census source adapters. Preserve original records and fail closed.

ArcGIS snapshots consist of metadata.json, ids.json and immutable feature chunks.
Each snapshot is namespaced by the source query contract; no unsupported state
portal is silently treated as successfully downloaded.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from .core import canonical, digest, fetch_json, filehash, number, readcsv


def field_value(attrs, key, *fallback):
    names=[key,*fallback]
    lower={str(k).casefold():v for k,v in attrs.items()}
    for name in names:
        if name is None: continue
        v=lower.get(str(name).casefold())
        if v is not None and str(v).strip()!='': return v
    return None


def parse_arcgis(feature,source):
    attrs=feature.get('attributes') or feature.get('properties') or {}
    geom=feature.get('geometry') or {}
    if not isinstance(geom,dict): geom={}
    native=field_value(attrs,source.get('native_id_field'),'objectid','OBJECTID','GID')
    if native is None: native=field_value(attrs,source.get('name_field'),'entity_id','projectname','site_code')
    name=field_value(attrs,source.get('name_field'),'projectname','site_title','occur_name','DEPOSIT_NAME','entity_id')
    commodity=field_value(attrs,source.get('commodity_field'),'commodity','commodities','all_commodities')
    extra=[str(field_value(attrs,k) or '') for k in source.get('commodity_extra_fields',[])]
    text='; '.join(x for x in [str(commodity or ''),*extra] if x)
    lat=number(field_value(attrs,source.get('latitude_field'),'latitude'))
    lon=number(field_value(attrs,source.get('longitude_field'),'longitude'))
    if lat is None:lat=number(geom.get('y'))
    if lon is None:lon=number(geom.get('x'))
    st=field_value(attrs,source.get('state_field'),'state')
    fixed=source.get('state_fixed')
    state=str(st or fixed or '').strip().upper()
    mismatch=bool(fixed and st and str(st).strip().upper()!=str(fixed).upper())
    # Some GA sources give a deposit name in a field called projectname; their
    # provider's entity level remains DEPOSIT and is never auto-upgraded.
    return {
        'source':source['key'], 'native_id':str(native or ''), 'name':str(name or '').strip(),
        'state':state,'state_jurisdiction':fixed or source.get('jurisdiction'),
        'state_conflict':mismatch,'company':field_value(attrs,source.get('company_field'), 'company_operator','operator','company','owner'),
        'project_name_hint':field_value(attrs,source.get('project_name_field')),
        'latitude':lat,'longitude':lon,'commodity':text,
        'entity_level':source.get('entity_level','UNKNOWN'),'official':True,
        'source_url':source['url'],'source_documentation':source.get('source_documentation',''),
        'activity_raw':field_value(attrs,source.get('activity_field'),'status','mine_status'),
        'deposit_family':field_value(attrs,source.get('deposit_family_field'),'mineraldeposittype'),
        'commodity_preclassified_ree':bool(source.get('commodity_preclassified_ree')),
        'source_raw_attributes':attrs,
    }


def parse_state_csv(row,source):
    # Accept common state CSV field aliases without implicitly certifying that
    # the user-provided local file itself is an official export.
    attrs=dict(row)
    native=field_value(attrs,'native_id','project_id','site_code','site_no','deposit_id','OBJECTID')
    name=field_value(attrs,'name','project_name','project','deposit_name','occur_name','site_title','short_name')
    state=field_value(attrs,'state') or source.get('state_fixed') or ''
    commodity=field_value(attrs,'commodity','commodities','site_commo','all_commodities','target_com','main_commodity')
    company=field_value(attrs,'company','company_operator','operator','owner','proponent','holder')
    entity=field_value(attrs,'entity_level') or source.get('entity_level','UNKNOWN')
    fixed=source.get('state_fixed')
    return {
        'source':source['key'], 'native_id':str(native or ''),'name':str(name or '').strip(),
        'state':str(state).upper().strip(),'state_jurisdiction':fixed or source.get('jurisdiction'),
        'state_conflict':bool(fixed and str(state).upper().strip()!=str(fixed).upper()),
        'company':str(company or '').strip(), 'project_name_hint':field_value(attrs,'project_name_hint','proj_title'),
        'latitude':number(field_value(attrs,'latitude','lat','y')),
        'longitude':number(field_value(attrs,'longitude','lon','long','x')),
        'commodity':str(commodity or ''), 'entity_level':str(entity).upper(),
        'official':True,'source_url':field_value(attrs,'source_url') or source.get('source_documentation',''),
        'source_documentation':source.get('source_documentation',''),
        'activity_raw':field_value(attrs,'activity','mine_status','status'),
        'deposit_family':field_value(attrs,'deposit_family','mineraldeposittype'),
        'commodity_preclassified_ree':bool(source.get('commodity_preclassified_ree')),
        'source_raw_attributes':attrs,
    }


def load_arcgis(source,cache_root,offline=False,chunk_size=200):
    """Read a source/query-specific snapshot or fully materialise a new one.

    Count/ID/chunk requests are never marked successful until every ID is
    accounted for. Raw JSON is retained and hashed. `--refresh` is handled
    by caller moving old cache to an immutable snapshot first.
    """
    url=source['url'].rstrip('/')
    where=source.get('where','1=1')
    signature=digest({'url':url,'where':where,'version':2})[:20]
    root=Path(cache_root)/source['key']/signature
    root.mkdir(parents=True,exist_ok=True)
    meta=root/'metadata.json'; idpath=root/'ids.json'
    if not meta.is_file():
        obj,raw=fetch_json(url,{'f':'json'},offline=offline)
        if obj.get('type')!='Feature Layer':raise RuntimeError('Layer is not an ArcGIS Feature Layer')
        meta.write_bytes(raw)
    metadata=json.loads(meta.read_text())
    if metadata.get('type')!='Feature Layer':raise RuntimeError('ArcGIS metadata not Feature Layer')
    if not idpath.is_file():
        obj,raw=fetch_json(url+'/query',{'f':'json','where':where,'returnIdsOnly':'true','returnGeometry':'false'},offline=offline)
        if not isinstance(obj.get('objectIds'),list):raise RuntimeError('No objectIds array from ArcGIS')
        idpath.write_bytes(raw)
    idsobj=json.loads(idpath.read_text());ids=idsobj.get('objectIds')
    if not isinstance(ids,list):raise RuntimeError('Malformed frozen ID manifest')
    ids=sorted(set(ids),key=lambda x:(isinstance(x,str),x))
    oid=metadata.get('objectIdField') or (idsobj.get('objectIdFieldName')) or next((f['name'] for f in metadata.get('fields',[]) if f.get('type')=='esriFieldTypeOID'),None)
    if not oid:raise RuntimeError('Cannot identify unique ArcGIS OBJECTID field')
    chunks=[];all_ids=set();features=[]
    for offset in range(0,len(ids),chunk_size):
        expected=ids[offset:offset+chunk_size];path=root/f'features_{offset:07d}.json'
        if not path.is_file():
            obj,raw=fetch_json(url+'/query',{'f':'json','objectIds':','.join(map(str,expected)),
                                           'outFields':'*','outSR':'4326','returnGeometry':'true'},offline=offline)
            if not isinstance(obj.get('features'),list):raise RuntimeError('ArcGIS feature query missing features')
            path.write_bytes(raw)
        obj=json.loads(path.read_text());got=obj.get('features')
        if not isinstance(got,list):raise RuntimeError('Invalid cached features')
        chunk_ids=[]
        for feature in got:
            val=field_value(feature.get('attributes') or {},oid)
            if val is None:raise RuntimeError('ArcGIS feature lacking OID')
            chunk_ids.append(str(val))
        if set(chunk_ids)!=set(str(x) for x in expected) or len(chunk_ids)!=len(expected):
            raise RuntimeError(f'ArcGIS truncated/mismatched ID chunk at {offset}')
        if all_ids.intersection(chunk_ids):raise RuntimeError('Repeated OID across chunks')
        all_ids.update(chunk_ids)
        features.extend(got); chunks.append({'file':path.name,'sha256':filehash(path),'rows':len(got)})
    if len(features)!=len(ids):raise RuntimeError('ArcGIS incomplete snapshot')
    manifest={'source_key':source['key'],'url':url,'where':where,'source_type':'arcgis',
              'metadata_sha256':filehash(meta),'ids_sha256':filehash(idpath),
              'chunks':chunks,'records':len(features),'outSR':4326,'snapshot_format_version':2}
    manifest_path=root/'manifest.json'
    if manifest_path.exists():
        frozen=json.loads(manifest_path.read_text(encoding='utf8'))
        if canonical(frozen)!=canonical(manifest):
            raise RuntimeError(
                'Frozen ArcGIS snapshot content/contract changed; preserve original '
                'and open a versioned snapshot instead: '+str(manifest_path)
            )
    else:
        # Never rewrite the original manifest merely because the cache was
        # replayed. Exact feature hashes bind the snapshot to its raw bytes.
        with manifest_path.open('x',encoding='utf8') as target:
            target.write(json.dumps(manifest,indent=2,ensure_ascii=False))
    return [parse_arcgis(f,source) for f in features],digest(manifest),root


def load_csv(source,root):
    p=Path(source['path']);p=p if p.is_absolute() else Path(root)/p
    if not p.is_file():return None,None,'AWAITING_OFFICIAL_EXPORT'
    rows=readcsv(p)
    if not rows:return None,None,'EMPTY_OFFICIAL_EXPORT'
    return [parse_state_csv(r,source) for r in rows],filehash(p),'OK_LOCAL_EXPORT_UNVERIFIED'
