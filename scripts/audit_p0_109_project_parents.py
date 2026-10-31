#!/usr/bin/env python3
"""Re-audit all 109 frozen C0 sources lacking an independent Project parent.

Grounding: source-native 2026-10-29 features; 156 review snapshot; an
independently curated historical government/issuer/CSIRO document register.
Do not treat same names, resource TONNAGE, or heavy-mineral assemblages
as a REO resource, a Project approval, or a current pre-FID alternative.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE="docs/audits/2026-10-31_156_project_parent_evidence_review.csv"
RAW="data/source_snapshots/2026-10-29_272_native_features.jsonl"
ALL="docs/audits/2026-10-31_487_evidence_round2_review.csv"
LEADS="inputs/source_review_20261031/round5_109_documented_project_deposit_leads.csv"
OUTPUT="docs/audits/2026-10-31_109_project_evidence_review.csv"
GAPS="docs/audits/2026-10-31_109_project_evidence_gaps.csv"
SUMMARY="docs/audits/2026-10-31_109_project_evidence_summary.json"

COLUMNS=[
    "target_id","state","source_name","source_key","source_native_id",
    "source_native_entity","source_native_status","native_commodity",
    "native_major_commodity","native_deposit_type","native_resource_information",
    "native_lat","native_lon","source_native_feature_locator",
    "source_original_chunk_sha256","source_document_uri",
    "same_state_name_count_487","other_same_state_name_source_ids",
    "same_name_nearest_native_distance_km","same_name_is_project_proof",
    "document_evidence_class","parent_project_candidate",
    "project_parent_claim_status","external_document_title",
    "external_document_url","external_document_date",
    "external_document_locator","REE_resource_role",
    "scope_and_time_qualification","new_document_evidence_available",
    "independent_project_identity_approved","source_boundary_verified",
    "JORC_REO_approved","C1_approved","next_document_requirement",
]

def read(root,relative):
    with (root/relative).open(encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def unique(rows,key,label):
    out={}
    for x in rows:
        v=x[key]
        if not v or v in out:
            raise ValueError(f"{label} duplicated/missing {key} {v}")
        out[v]=x
    return out

def attr(obj,*keys):
    for key in keys:
        val=obj.get(key)
        if val is not None and str(val).strip() and str(val).strip().lower() not in ("none","null","nan"):
            return str(val).strip()
    return ""

def coords(a):
    try:
        lat=attr(a,"latitude","LATITUDE_GDA2020","LATITUDE_GDA94","LATITUDE")
        lon=attr(a,"longitude","LONGITUDE_GDA2020","LONGITUDE_GDA94","LONGITUDE")
        lat,lon=float(lat),float(lon)
        return (lat,lon) if (-44<=lat<=-10 and 110<=lon<=155) else None
    except (ValueError,TypeError):
        return None

def distance_km(a,b):
    radius=6371.0088
    x1,y1=a
    x2,y2=b
    dlat=math.radians(x2-x1)
    dlon=math.radians(y2-y1)
    d=math.sin(dlat/2)**2+math.cos(math.radians(x1))*math.cos(math.radians(x2))*math.sin(dlon/2)**2
    return 2*radius*math.asin(min(1,math.sqrt(d)))

def source_description(x,attrs):
    key=x["source_key"]
    if key.startswith("SA_"):
        ent=attr(attrs,"DEPOSIT_CLASS","MINDEP_CLASS_CODE")
        status=attr(attrs,"DEPOSIT_STATUS","STATUS_TYPE_VALUE")
        comm=attr(attrs,"COMMODITIES","DEPOSIT_COMMODITIES")
        major=attr(attrs,"MAJOR_COMMODITY_CODE")
        typ=attr(attrs,"DEPOSIT_CLASS","MINDEP_CLASS_CODE")
        resource=attr(attrs,"DEPOSIT_SUMMARY","SUMMARY_DESCRIPTION")[:550]
        uri="https://minerals.sarig.sa.gov.au/"
    elif key=="STATE_TAS_MRT":
        ent=attr(attrs,"DEPOSIT_TYPE","TYPE")
        status=attr(attrs,"OPERATIONAL_STATUS")
        comm=attr(attrs,"COMMODITIES")
        major=attr(attrs,"COMMODITY_CATEGORY")
        typ=attr(attrs,"DEPOSIT_TYPE")
        resource=attr(attrs,"RESOURCES")
        uri=attr(attrs,"DETAILS")
    elif key=="STATE_QLD_MINOCC":
        ent=attr(attrs,"occurrence_type","site_type","TYPE")
        status=attr(attrs,"status","STATUS")
        comm=attr(attrs,"commodities","COMMODITIES")
        major=attr(attrs,"commodity","COMMODITY")
        typ=ent
        resource=""
        uri=attr(attrs,"url","URL")
    else:
        ent=attr(attrs,"currentstatus","status","TYPE")
        status=ent
        comm=attr(attrs,"commodity","commodities")
        major=attr(attrs,"mineraldeposittype")
        typ=major
        resource=attr(attrs,"size_","resource")
        uri=attr(attrs,"source","source_url")
        if "https://" in uri:
            uri=uri[uri.index("https://"):]
    return ent,status,comm,major,typ,resource,uri

def build(root=ROOT):
    reviewed=read(root,BASE)
    target=[x for x in reviewed if x["parent_review_result"]=="NO_INDEPENDENT_PROJECT_PARENT_DOCUMENT_FOUND"]
    native=unique([json.loads(line) for line in (root/RAW).read_text(encoding="utf-8").splitlines()
                   if line],"target_id","frozen native features")
    allrows=read(root,ALL)
    leads=read(root,LEADS)
    if len(reviewed)!=156 or len(target)!=109 or len(native)!=272 or len(allrows)!=487 or len(leads)!=31:
        raise ValueError("Frozen source population or dated evidence register changed")

    known_names=defaultdict(list)
    for x in allrows:
        known_names[(x["state"],x["name"].casefold().strip())].append(x["target_id"])
    leads_by_key=unique([{**x,"lookup":x["state"]+"|"+x["source_name"].casefold().strip()}
                         for x in leads], "lookup","new external evidence")
    targetkeys={x["state"]+"|"+x["source_name"].casefold().strip() for x in target}
    if set(leads_by_key)-targetkeys:
        raise ValueError("New documentary evidence names must match frozen target names in the same state")
    result=[]
    source_count=Counter()
    by_status=Counter()
    states=Counter()
    by_doc=Counter()
    duplicate_state_name_rows=0
    coordinate_comparable=0
    coordinate_near_1km=0
    coordinate_conflicts=[]
    for x in target:
        tid=x["target_id"]
        src=native.get(tid)
        if not src or src["source_key"]!=x["source_key"] or src["native_id"]!=x["source_native_id"]:
            raise ValueError(f"Source native evidence not matched: {tid}")
        attrs=src["source_attributes"]
        ent,status,comm,major,typ,resource,uri=source_description(x,attrs)
        pos=coords(attrs)
        dupids=sorted(k for k in known_names[(x["state"],x["source_name"].casefold().strip())] if k!=tid)
        dupdist=[]
        for other in dupids:
            o=native.get(other)
            q=coords(o["source_attributes"]) if o else None
            if pos and q:
                dupdist.append(distance_km(pos,q))
        match=leads_by_key.get(x["state"]+"|"+x["source_name"].casefold().strip())
        if match:
            claim=match["evidence_claim_grade"]
            if claim in ("ISSUER_EXPLICIT_DEPOSIT_WITHIN_PROJECT","ISSUER_EXPLICIT_TARGET_WITHIN_PROJECT",
                         "GOV_EXPLICIT_NORTH_SOUTH_DEPOSITS_IN_PROJECT","ISSUER_EXPLICIT_SITE_PROJECT"):
                grade="DOCUMENTED_HISTORICAL_PARENT_CANDIDATE"
            elif claim=="HISTORICAL_GROUPED_DEPOSIT_PARENT_CANDIDATE":
                grade="HISTORICAL_GROUP_PARENT_CANDIDATE"
            elif claim in ("HISTORICAL_TENEMENT_NOT_PROJECT_PARENT","HISTORICAL_ALTERNATE_SPELLING_HOLD",
                           "PARTIAL_SITE_NAME_BOUNDARY_HOLD","REGIONAL_NAME_NO_PARENT_HOLD"):
                grade="SCOPE_OR_TENEMENT_ONLY_HOLD"
            else:
                grade="INDEPENDENT_DEPOSIT_DOCUMENT_NO_PROJECT_PARENT"
            newdoc="YES"
            parent=match["candidate_parent"]
            docclass=claim
            dtitle=match["document_title"]
            durl=match["document_url"]
            date=match["published_date"]
            locator=match["original_document_locator"]
            role=match["REE_resource_role"]
            qualification=match["scope_caveat"]
            next_action=("Check historical Project/Deposit boundary plus current operator, "
                         "REE recoverable product and original JORC statement")
            if grade=="SCOPE_OR_TENEMENT_ONLY_HOLD":
                next_action="Verify source-feature location inside project and distinguish tenement from Project"
            if grade=="INDEPENDENT_DEPOSIT_DOCUMENT_NO_PROJECT_PARENT":
                next_action="Keep independently documented geological deposit in C0; locate actual Project scope separately"
        else:
            newdoc="NO"
            parent=dtitle=durl=date=locator=role=qualification=""
            docclass="NO_ADDITIONAL_EXTERNAL_PROJECT_DOCUMENT"
            if x["source_key"].startswith("SA_") and (major.upper() not in ("REE","REO","RARE EARTHS")):
                grade="NATIVE_MULTICOMMODITY_NONPRIMARY_REE_DEPOSIT"
                next_action="Find project and extractable REE evidence; do not treat Cu/U/Au resource as REO"
            elif x["source_key"]=="STATE_TAS_MRT":
                grade="NATIVE_TAS_GEOLOGICAL_RECORD_ONLY"
                next_action="Obtain MRT historical report for deposit ID and independent Project evidence"
            elif x["source_key"]=="STATE_QLD_MINOCC":
                grade="NATIVE_QLD_GEOLOGICAL_RECORD_ONLY"
                next_action="Obtain QLD mineral occurrence original technical report and project tenure"
            elif "heavy mineral sands" in (major+" "+typ).casefold():
                grade="NATIVE_HMS_DEPOSIT_WITHOUT_PROJECT_EVIDENCE"
                next_action="Locate deposit-to-mining project source; do not conflate THM and TREO"
            elif "clay" in (major+" "+typ).casefold():
                grade="NATIVE_CLAY_REE_DEPOSIT_WITHOUT_PROJECT_EVIDENCE"
                next_action="Locate clay REE development Project, source-scoped resource and ownership"
            else:
                grade="NATIVE_REE_DEPOSIT_WITHOUT_PROJECT_EVIDENCE"
                next_action="Locate published Project parent boundary and REE development evidence"
        # Quarantine same-state names with conflicting government source coordinates.
        spatial_conflict=bool(dupdist and min(dupdist)>10.0)
        if spatial_conflict:
            grade="SPATIAL_IDENTITY_CONFLICT_PARENT_WITHHELD"
            next_action=("Resolve same-name original source points and historic project "
                         "polygon; no name-only parent merge")
            qualification=(qualification+"; " if qualification else "")+(
                "Official same-name features differ by more than 10 km")
        r=dict(zip(COLUMNS,[
            tid,x["state"],x["source_name"],x["source_key"],x["source_native_id"],
            ent,status,comm,major,typ,resource,
            str(pos[0]) if pos else "",str(pos[1]) if pos else "",
            src["source_feature_locator"],src["original_chunk_sha256"],uri,
            str(len(dupids)+1),";".join(dupids),
            f"{min(dupdist):.3f}" if dupdist else "","NO",
            docclass,parent,grade,dtitle,durl,date,locator,role,qualification,newdoc,
            "NO","NO","NO","NO",next_action
        ]))
        if len(r)!=len(COLUMNS):
            raise AssertionError("Column mapping error")
        result.append(r)
        by_status[grade]+=1
        by_doc[docclass]+=1
        states[x["state"]]+=1
        source_count[x["source_key"]]+=1
        if dupids:duplicate_state_name_rows+=1
        if dupdist:
            coordinate_comparable+=1
            if min(dupdist)<=1:coordinate_near_1km+=1
            if min(dupdist)>10.0:
                coordinate_conflicts.append({
                    "target_id":tid,"state":x["state"],"source_name":x["source_name"],
                    "nearest_source_distance_km":round(min(dupdist),3),
                    "other_source_target_ids":dupids
                })
    if len(result)!=109 or len({x["target_id"] for x in result})!=109 or any(
        x["C1_approved"]!="NO" or x["independent_project_identity_approved"]!="NO" or
        x["JORC_REO_approved"]!="NO" for x in result):
        raise AssertionError("Target count or C1 release gate violation")
    leads_reached=sum(x["new_document_evidence_available"]=="YES" for x in result)
    if sum(by_status.values())!=109 or leads_reached<31:
        raise ValueError(f"Lead coverage regression {leads_reached}")
    stats={
        "review_date":"2026-10-31",
        "source_frozen_as_of":"2026-10-29",
        "unit":"source-target rows, never independent unique mining Projects",
        "source_target_count":109,"unique_ids":109,
        "new_document_register_unique_names":len(leads),
        "new_document_target_rows":leads_reached,
        "documented_parent_source_rows":(
            by_status["DOCUMENTED_HISTORICAL_PARENT_CANDIDATE"]+
            by_status["HISTORICAL_GROUP_PARENT_CANDIDATE"]),
        "scope_or_tenement_holds":(
            by_status["SCOPE_OR_TENEMENT_ONLY_HOLD"]+
            by_status["SPATIAL_IDENTITY_CONFLICT_PARENT_WITHHELD"]),
        "spatial_identity_conflicts_withheld":by_status["SPATIAL_IDENTITY_CONFLICT_PARENT_WITHHELD"],
        "same_state_name_rows":duplicate_state_name_rows,
        "same_state_name_coordinate_comparable_rows":coordinate_comparable,
        "same_name_near_1km_rows":coordinate_near_1km,
        "same_name_over_10km_identity_conflicts":coordinate_conflicts,
        "independent_deposit_document_no_parent":by_status["INDEPENDENT_DEPOSIT_DOCUMENT_NO_PROJECT_PARENT"],
        "without_new_external_document":109-leads_reached,
        "project_ID_signoffs":0,"JORC_REO_signoffs":0,"C1_release_count":0,
        "state_distribution":dict(states),
        "original_source_counts":dict(source_count),
        "evidence_class_counts":dict(by_status),
        "external_claim_type_counts":dict(by_doc),
        "input_sha256":{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in (BASE,RAW,ALL,LEADS)},
        "decision_note":"Historic resources are HM not TREO; document links are independent leads, not PDF byte archives or independent Project boundary/JORC approval. Exact same state/name is not a confirmed Project parent.",
    }
    return result,stats

def save(root=ROOT):
    data,stats=build(root)
    output=root/OUTPUT
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
        w.writeheader();w.writerows(data)
    with (root/GAPS).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
        w.writeheader()
        w.writerows(x for x in data if x["project_parent_claim_status"] not in (
            "DOCUMENTED_HISTORICAL_PARENT_CANDIDATE","HISTORICAL_GROUP_PARENT_CANDIDATE"))
    (root/SUMMARY).write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False))
    return stats

if __name__=="__main__":
    save()
