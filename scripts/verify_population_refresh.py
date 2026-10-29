#!/usr/bin/env python3
"""Fail CI when requested official ArcGIS source fetches did not finish.

The output distinguishes an unverified acquired candidate from an approved
research observation; it never modifies the approval registry.
"""
from __future__ import annotations
import argparse,json,sqlite3
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--db',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--source-key',action='append')
    args=ap.parse_args()
    con=sqlite3.connect(args.db);con.row_factory=sqlite3.Row
    sources=[dict(x) for x in con.execute('SELECT source_key,source_type,fetch_status,record_count,raw_sha256,error FROM source_registry ORDER BY source_key')]
    selected=set(args.source_key or [])
    live=[x for x in sources if x['source_type']=='arcgis' and (not selected or x['source_key'] in selected)]
    failures=[x for x in live if x['fetch_status']!='CACHED_OR_FETCHED_UNVERIFIED']
    population=con.execute('SELECT COUNT(*) FROM project_master').fetchone()[0]
    candidates=con.execute('SELECT COUNT(*) FROM population_candidates').fetchone()[0]
    decision_counts={r[0]:r[1] for r in con.execute('SELECT decision,COUNT(*) FROM population_candidates GROUP BY decision')}
    validated=con.execute("SELECT COUNT(*) FROM project_coordinates WHERE verification='VERIFIED'").fetchone()[0]
    summary={'population_count':population,'candidates_count':candidates,'verified_coordinates':validated,
             'candidate_decisions':decision_counts,'official_arcgis_sources_checked':len(live),
             'official_arcgis_sources_failed':len(failures),'sources':sources,
             'status':'PASS' if not failures and live else 'BLOCKED_NO_LIVE_DATA' if not live else 'FAILED_SOURCE_FETCH'}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='sources'},ensure_ascii=False))
    if failures:raise SystemExit(2)
    if not live:raise SystemExit(3)
if __name__=='__main__':main()
