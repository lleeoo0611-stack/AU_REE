"""Shared SQLite, provenance, deterministic stage signatures and network helpers."""
from __future__ import annotations
import csv, hashlib, json, math, os, re, sqlite3, time, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
STAGES = ('population', 'criteria', 'gis', 'eligibility', 'r_export')

def utc(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def canonical(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',',':'))
def digest(x): return hashlib.sha256(x if isinstance(x, bytes) else canonical(x).encode()).hexdigest()
def filehash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def norm(x):
    s=unicodedata.normalize('NFKC',str(x or '')).casefold()
    s=re.sub(r'\bmount\b','mt',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def number(x):
    try:
        if x is None or str(x).strip().lower() in ('','na','nan','none','null'):return None
        value=float(str(x).replace(',',''))
        return value if math.isfinite(value) else None
    except (TypeError,ValueError):return None
def readcsv(path):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(path,rows,columns):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    with open(temp,'w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    os.replace(temp,path)
def config(name):return json.loads((ROOT/'config'/name).read_text(encoding='utf8'))
def connect(path):
    db=sqlite3.connect(path);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA busy_timeout=30000');return db

def setup(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS stage_runs(stage TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, status TEXT NOT NULL, input_hash TEXT NOT NULL, run_time TEXT NOT NULL, summary_json TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS stage_run_history(event_id INTEGER PRIMARY KEY AUTOINCREMENT, stage TEXT, fingerprint TEXT, status TEXT, input_hash TEXT, run_time TEXT, summary_json TEXT);
    CREATE TABLE IF NOT EXISTS source_registry(source_key TEXT PRIMARY KEY, source_url TEXT, source_type TEXT, dataset_date TEXT, fetched_at TEXT, raw_sha256 TEXT, record_count INTEGER, fetch_status TEXT, error TEXT);
    CREATE TABLE IF NOT EXISTS source_documents(document_id TEXT PRIMARY KEY,file_path TEXT NOT NULL,source_url TEXT NOT NULL,declared_sha256 TEXT,actual_sha256 TEXT,hash_status TEXT NOT NULL,checked_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS evidence_approvals(approval_ref TEXT PRIMARY KEY,record_type TEXT NOT NULL,document_id TEXT NOT NULL,reviewer TEXT,decision TEXT,reviewed_at TEXT,status TEXT NOT NULL,notes TEXT,FOREIGN KEY(document_id) REFERENCES source_documents(document_id));
    CREATE TABLE IF NOT EXISTS evidence_links(record_type TEXT NOT NULL, record_id TEXT NOT NULL, approval_ref TEXT NOT NULL, PRIMARY KEY(record_type,record_id));
    CREATE TABLE IF NOT EXISTS approved_project_reviews(project_id TEXT PRIMARY KEY, approval_ref TEXT NOT NULL, source_sha256 TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS gis_release_gates(scenario TEXT PRIMARY KEY,scope TEXT NOT NULL,cohort_size INTEGER NOT NULL,gis_complete INTEGER NOT NULL,status TEXT NOT NULL,cohort_sha256 TEXT NOT NULL,reason TEXT NOT NULL,evaluated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS population_candidates(candidate_id TEXT PRIMARY KEY, source_key TEXT, native_id TEXT, raw_name TEXT, normalized_name TEXT, state TEXT, company TEXT, latitude REAL, longitude REAL, commodity_text TEXT, entity_level TEXT, ree_role TEXT, decision TEXT, matched_project_id TEXT, reason TEXT, source_url TEXT, original_json TEXT, first_seen TEXT, last_seen TEXT);
    CREATE TABLE IF NOT EXISTS project_master(project_id TEXT PRIMARY KEY, canonical_name TEXT NOT NULL, normalized_name TEXT NOT NULL, state TEXT, country TEXT NOT NULL DEFAULT 'Australia', latitude REAL, longitude REAL, activity TEXT, lifecycle TEXT, ree_role TEXT, deposit_family TEXT, population_status TEXT NOT NULL, identity_source TEXT, updated_at TEXT);
    CREATE TABLE IF NOT EXISTS project_coordinates(project_id TEXT PRIMARY KEY,latitude REAL,longitude REAL,quality TEXT,uncertainty_km REAL,source_url TEXT,verification TEXT,updated_at TEXT);
    CREATE TABLE IF NOT EXISTS project_aliases(project_id TEXT NOT NULL, alias TEXT NOT NULL, normalized_alias TEXT NOT NULL, source_key TEXT NOT NULL, native_id TEXT NOT NULL, PRIMARY KEY(project_id,normalized_alias,source_key,native_id));
    CREATE TABLE IF NOT EXISTS legacy_id_map(legacy_id TEXT PRIMARY KEY, project_id TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS criteria(code TEXT PRIMARY KEY, domain TEXT NOT NULL, label TEXT, direction TEXT, unit TEXT, basis TEXT, mandatory INTEGER, description TEXT, config_version TEXT);
    CREATE TABLE IF NOT EXISTS variable_dictionary(code TEXT PRIMARY KEY, domain TEXT, unit TEXT, expected_basis TEXT, source_priority TEXT, provenance_required INTEGER);
    CREATE TABLE IF NOT EXISTS observations(obs_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, variable TEXT NOT NULL, numeric_value REAL, text_value TEXT, unit TEXT, basis TEXT, effective_date TEXT, publication_date TEXT, source_url TEXT, source_title TEXT, source_page TEXT, source_sha256 TEXT, verification TEXT, captured_at TEXT, FOREIGN KEY(project_id) REFERENCES project_master(project_id));
    CREATE TABLE IF NOT EXISTS criterion_values(project_id TEXT NOT NULL, criterion TEXT NOT NULL, value REAL, unit TEXT, basis TEXT, observation_id TEXT, quality TEXT, issue TEXT, PRIMARY KEY(project_id,criterion));
    CREATE TABLE IF NOT EXISTS gis_sources(layer TEXT PRIMARY KEY, source_url TEXT, source_type TEXT, verified INTEGER, fingerprint TEXT, status TEXT, queried_at TEXT);
    CREATE TABLE IF NOT EXISTS gis_project_status(layer TEXT NOT NULL, project_id TEXT NOT NULL, status TEXT NOT NULL, cache_file TEXT, feature_count INTEGER, radius_km REAL, error TEXT, query_hash TEXT, PRIMARY KEY(layer,project_id));
    CREATE TABLE IF NOT EXISTS gis_metrics(project_id TEXT NOT NULL, criterion TEXT NOT NULL, distance_km REAL, method TEXT, source_url TEXT, source_sha256 TEXT, geometry_sha256 TEXT, coordinate_uncertainty_km REAL, status TEXT NOT NULL, computed_at TEXT, PRIMARY KEY(project_id,criterion));
    CREATE TABLE IF NOT EXISTS coverage(project_id TEXT NOT NULL, criterion TEXT NOT NULL, domain TEXT NOT NULL, status TEXT NOT NULL, value REAL, quality TEXT, reason TEXT, PRIMARY KEY(project_id,criterion));
    CREATE TABLE IF NOT EXISTS eligibility(project_id TEXT NOT NULL, scenario TEXT NOT NULL, eligible INTEGER NOT NULL, point_ready INTEGER NOT NULL DEFAULT 0, coverage_fraction REAL NOT NULL, domain_count INTEGER NOT NULL, reasons_json TEXT NOT NULL, evaluated_at TEXT NOT NULL, PRIMARY KEY(project_id,scenario));
    CREATE TABLE IF NOT EXISTS audit_events(id INTEGER PRIMARY KEY AUTOINCREMENT, stage TEXT NOT NULL, entity_id TEXT, kind TEXT NOT NULL, message TEXT, time TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_candidate_name ON population_candidates(normalized_name,state);
    CREATE INDEX IF NOT EXISTS idx_obs_proj ON observations(project_id,variable);
    ''')
    # Scheme A schema migrations are Git-versioned and idempotent.
    db.executescript((ROOT/'db'/'migrations'/'0004_scheme_a.sql').read_text(encoding='utf-8'))
    if 'operator_name' not in {x[1] for x in db.execute('PRAGMA table_info(project_master)')}:
        db.execute('ALTER TABLE project_master ADD COLUMN operator_name TEXT')

def event(db,stage,entity,kind,msg):db.execute('INSERT INTO audit_events(stage,entity_id,kind,message,time) VALUES(?,?,?,?,?)',(stage,entity,kind,msg,utc()))

def fetch_json(url,params=None,timeout=40,retries=3,offline=False):
    if offline:raise RuntimeError('OFFLINE: external API disabled')
    for attempt in range(retries):
        try:
            target=url + (('?' if '?' not in url else '&')+urlencode(params)) if params else url
            req=Request(target,headers={'User-Agent':'Australian-REE-research/1.0 (+open-government-api)','Accept':'application/json'})
            with urlopen(req,timeout=timeout) as response:raw=response.read()
            obj=json.loads(raw)
            if isinstance(obj,dict) and obj.get('error'):raise RuntimeError(str(obj['error']))
            return obj,raw
        except Exception:
            if attempt+1==retries:raise
            time.sleep(min(2**attempt,4))

# Object ID chunking avoids ArcGIS return-transfer truncation.
def arcgis_features(url,cache,offline=False,chunk_size=250):
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    meta=cache/'metadata.json';idsfile=cache/'ids.json'
    if not meta.exists():
        obj,raw=fetch_json(url,{'f':'json'},offline=offline);meta.write_bytes(raw)
    metadata=json.loads(meta.read_text())
    if not idsfile.exists():
        ids,raw=fetch_json(url.rstrip('/')+'/query',{'f':'json','where':'1=1','returnIdsOnly':'true'},offline=offline)
        if not isinstance(ids.get('objectIds'),list):raise RuntimeError('ArcGIS layer has no objectIds')
        idsfile.write_bytes(raw)
    ids=sorted(json.loads(idsfile.read_text())['objectIds'])
    features=[]
    for i in range(0,len(ids),chunk_size):
        batch=ids[i:i+chunk_size];path=cache/f'features_{i:06}.json'
        if path.exists():part=json.loads(path.read_text())
        else:
            part,raw=fetch_json(url.rstrip('/')+'/query',{'f':'json','objectIds':','.join(map(str,batch)),'outFields':'*','outSR':4326,'returnGeometry':'true'},offline=offline)
            path.write_bytes(raw)
        got=part.get('features',[])
        if len(got)!=len(batch):raise RuntimeError(f'ArcGIS feature truncation: {len(got)} != {len(batch)} for offset {i}')
        features.extend(got)
    return features,digest({'metadata':filehash(meta),'ids':filehash(idsfile),'parts':[(p.name,filehash(p)) for p in sorted(cache.glob('features_*.json'))],'features':len(features)})

def australian(lat,lon):return lat is not None and lon is not None and -45<=lat<=-9 and 111<=lon<=155

def stage_input_hash(stage,db,override=None):
    i=STAGES.index(stage)
    previous=db.execute('SELECT fingerprint FROM stage_runs WHERE stage=?',(STAGES[i-1],)).fetchone() if i else None
    return digest({'previous':previous['fingerprint'] if previous else None,'override':override})
