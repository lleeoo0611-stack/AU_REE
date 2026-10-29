"""03: Official GIS ArcGIS REST / attested local GeoJSON, distances and evidence.
Checkpoint-per-project; incomplete queries never produce a certified distance.
"""
from __future__ import annotations
import json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
from ..evidence import verify
from ..core import utc,digest,filehash,event,fetch_json,number,writecsv

TRANSFORMER=Transformer.from_crs('EPSG:4326','EPSG:3577',always_xy=True)
MAP={'road':'I1','rail':'I2','power':'I3','port':'I4'}

def jsonshape(feat):
    g=feat.get('geometry') or {}
    if 'x' in g:return {'type':'Point','coordinates':[g['x'],g['y']]}
    if 'paths' in g:return {'type':'MultiLineString','coordinates':g['paths']}
    if 'rings' in g:return {'type':'Polygon','coordinates':g['rings']}
    if 'type' in g:return g
    return None

def official_full_features(url,cache,offline):
    """Small authoritative point layer: complete object-ID chunk retrieval, resuming."""
    from ..core import arcgis_features
    feats,sha=arcgis_features(url,cache,offline=offline,chunk_size=200)
    return feats,sha

def official_features(url,lat,lon,radii,cache,offline,where_clause="1=1"):
    cache=Path(cache);cache.parent.mkdir(parents=True,exist_ok=True)
    if cache.exists():
        saved=json.loads(cache.read_text())
        if saved['url']==url and saved['lat']==lat and saved['lon']==lon and saved.get('where_clause')==where_clause and saved.get('completed'):
            return saved['features'],saved['radius_km'],filehash(cache),'REUSED_VERIFIED_CACHE'
    url=url.rstrip('/')
    for radius in radii:
        geo=json.dumps({'x':lon,'y':lat,'spatialReference':{'wkid':4326}})
        base={'f':'json','where':where_clause,'geometry':geo,'geometryType':'esriGeometryPoint','inSR':4326,
              'spatialRel':'esriSpatialRelIntersects','distance':radius,'units':'esriSRUnit_Kilometer'}
        probe,_=fetch_json(url+'/query',{**base,'returnCountOnly':'true','returnGeometry':'false'},offline=offline)
        if not probe.get('count'):continue
        ids,_=fetch_json(url+'/query',{**base,'returnIdsOnly':'true','returnGeometry':'false'},offline=offline)
        oid=ids.get('objectIds') or []
        features=[]
        for i in range(0,len(oid),200):
            vals,_=fetch_json(url+'/query',{'f':'json','objectIds':','.join(map(str,oid[i:i+200])),
                                      'outFields':'*','returnGeometry':'true','outSR':4326},offline=offline)
            features.extend(vals.get('features') or [])
        if len(features)!=len(oid):raise RuntimeError('ArcGIS partial response; cache refused')
        if not features:raise RuntimeError('Query found count but returned zero geometry features')
        saved={'url':url,'lat':lat,'lon':lon,'where_clause':where_clause,'completed':True,'radius_km':radius,'features':features}
        tmp=cache.with_suffix('.tmp');tmp.write_text(json.dumps(saved,ensure_ascii=False));tmp.replace(cache)
        return features,radius,filehash(cache),'OK'
    raise RuntimeError('NO_OFFICIAL_FEATURE_WITHIN_MAX_SEARCH_RADIUS')

def nearest(lat,lon,features):
    p=transform(TRANSFORMER.transform,shape({'type':'Point','coordinates':[lon,lat]}))
    best=None;selected=None
    for f in features:
        g=jsonshape(f)
        if not g:continue
        try:
            geom=transform(TRANSFORMER.transform,shape(g))
            dist=p.distance(geom)/1000.0
        except Exception:continue
        if best is None or dist<best:best,selected=dist,g
    if best is None:raise RuntimeError('No valid geometries')
    return best,digest(selected)

def run(db,ctx):
    cfg=ctx['gis'];projects=[dict(r) for r in db.execute('''SELECT p.project_id,p.latitude,p.longitude,c.verification AS coordinate_verification FROM project_master p LEFT JOIN project_coordinates c ON c.project_id=p.project_id WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL''')]
    outcomes={}; outrows=[]
    for layer,criterion in MAP.items():
        entry=cfg['layers'][layer];url=entry.get('arcgis_layer_url');local=entry.get('local_geojson')
        mode=entry.get('mode','nearby');source_url=url or entry.get('official_source_url')
        # HTTPS confirms transport only, not independent research approval.
        # Online materialisation can be cached but never silently promoted to VERIFIED.
        verified=False
        features_all=None;layer_hash=None
        if local:
            path=Path(local);path=ctx['root']/path if not path.is_absolute() else path
            relative=str(path.resolve().relative_to(ctx['root'].resolve())) if path.exists() and path.resolve().is_relative_to(ctx['root'].resolve()) else ''
            if (path.exists() and filehash(path)==entry.get('expected_sha256')
                and verify(db,entry.get('approval_ref'),'GIS_LAYER',entry.get('official_source_url'),entry.get('expected_sha256'),relative)):
                data=json.loads(path.read_text(encoding='utf8'));features_all=data.get('features') or []
                verified=True;layer_hash=filehash(path)
                # Authorized local copy is provenance-verified by an exact checksum.
            else:verified=False
        if verified and features_all is None and url and mode=='full':
            try:features_all,layer_hash=official_full_features(url,ctx['workspace']/'cache'/'gis'/layer/'full',ctx['offline'])
            except Exception as ex:
                verified=False;event(db,'gis',layer,'FULL_LAYER_DOWNLOAD_FAIL',str(ex))
        status='APPROVED_ARCHIVED_LAYER' if verified else ('GIS_LAYER_APPROVAL_PENDING' if local else 'OFFICIAL_REMOTE_NOT_ARCHIVED_OR_APPROVED')
        db.execute('INSERT OR REPLACE INTO gis_sources(layer,source_url,source_type,verified,fingerprint,status,queried_at) VALUES(?,?,?,?,?,?,?)',
                   (layer,source_url,'local_geojson' if local else 'arcgis_rest',int(verified),layer_hash,status,utc()))
        good=0;failed=0
        for pr in projects:
            pid=pr['project_id'];lat=pr['latitude'];lon=pr['longitude'];rad=None
            distance=None;geosha=None;sourcehash=layer_hash;method='EPSG3577_SHAPELY_NEAREST';result='NOT_CONFIGURED';err='';feats=[];cache_file=''
            if pr.get('coordinate_verification')!='VERIFIED':
                result='COORDINATE_REVIEW_PENDING'
            elif verified:
                try:
                    if features_all is not None:feats=features_all
                    else:
                        if not url:raise RuntimeError('Local layer failed verification')
                        cached=ctx['workspace']/'cache'/'gis'/layer/(digest([pid,url,lat,lon,entry.get('where_clause','1=1')])[:24]+'.json')
                        feats,rad,sourcehash,_=official_features(url,lat,lon,cfg['radii_km'],cached,ctx['offline'],entry.get('where_clause','1=1'));cache_file=str(cached)
                    distance,geosha=nearest(lat,lon,feats)
                    result='VERIFIED';good+=1
                except Exception as ex:
                    err=str(ex);result='FAILED_QUERY';failed+=1
                    event(db,'gis',pid,'GIS_QUERY_FAILED',f'{layer}: {err[:400]}')
            db.execute('''INSERT OR REPLACE INTO gis_project_status(layer,project_id,status,cache_file,feature_count,radius_km,error,query_hash) VALUES(?,?,?,?,?,?,?,?)''',
                       (layer,pid,result,cache_file,len(feats),rad,err,digest([pid,layer,source_url,lat,lon])))
            cr=db.execute('SELECT uncertainty_km,verification FROM project_coordinates WHERE project_id=?',(pid,)).fetchone()
            uncertainty=cr['uncertainty_km'] if cr else None
            db.execute('''INSERT OR REPLACE INTO gis_metrics(project_id,criterion,distance_km,method,source_url,source_sha256,geometry_sha256,coordinate_uncertainty_km,status,computed_at) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                       (pid,criterion,distance,method,source_url,sourcehash,geosha,uncertainty,result,utc()))
            db.execute('''INSERT OR REPLACE INTO criterion_values(project_id,criterion,value,unit,basis,observation_id,quality,issue) VALUES(?,?,?,?,?,?,?,?)''',
                       (pid,criterion,distance if result=='VERIFIED' else None,'km','OFFICIAL_GIS',None,'VERIFIED' if result=='VERIFIED' else 'NOT_SCORED',result if result!='VERIFIED' else ''))
            outrows.append({'project_id':pid,'criterion':criterion,'distance_km':distance,'status':result,'source_url':source_url,'source_sha256':sourcehash})
        outcomes[layer]={'complete':good,'attempted':len(projects),'failed':failed,'source':status}
    ctx['artifacts']['gis_source_registry.csv']=([dict(x) for x in db.execute('SELECT * FROM gis_sources ORDER BY layer')],
        ['layer','source_url','source_type','verified','fingerprint','status','queried_at'])
    ctx['artifacts']['gis_project_status.csv']=([dict(x) for x in db.execute('SELECT * FROM gis_project_status ORDER BY project_id,layer')],
        ['layer','project_id','status','cache_file','feature_count','radius_km','error','query_hash'])
    ctx['artifacts']['gis_metrics.csv']=(outrows,['project_id','criterion','distance_km','status','source_url','source_sha256'])
    return {'projects_with_coordinates':len(projects),'layers':outcomes,'status':'GIS_COMPLETE' if projects and all(v['complete']==len(projects) for v in outcomes.values()) else 'GIS_NOT_RELEASED'}
