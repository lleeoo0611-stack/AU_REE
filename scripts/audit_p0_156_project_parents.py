#!/usr/bin/env python3
"""Audit all 156 unresolved Project parents from frozen source-native evidence.

Read-only baseline; keep all 272 parent audit rows and source IDs unchanged.
Government/issuer source discovery is a distinct, curated review input.
An EXACT same-name document is still only a candidate Project relationship
until geometry, time, REE product and independent signoff agree.
"""
from __future__ import annotations
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = "docs/audits/2026-10-31_272_project_parent_evidence_queue.csv"
RAW = "data/source_snapshots/2026-10-29_272_native_features.jsonl"
CENSUS = "docs/audits/2026-10-31_487_evidence_round2_review.csv"
LEADS = "inputs/source_review_20261031/round4_156_official_parent_documents.csv"
OUTPUT = "docs/audits/2026-10-31_156_project_parent_evidence_review.csv"
GAPS = "docs/audits/2026-10-31_156_project_parent_gaps.csv"
REPORT = "docs/audits/2026-10-31_156_project_parent_evidence_summary.json"
COLS = [
    "target_id","state","source_name","source_key","source_native_id",
    "original_entity_type","raw_snapshot_feature_id","original_raw_sha256",
    "official_source_locator","official_source_url","official_raw_entity_type",
    "official_operational_status","official_commodity_text","official_major_commodity",
    "official_ree_resource_disclosure","source_level_ree_role","within_state_same_name_count",
    "other_record_ids_same_name","name_cross_source_is_parent_evidence",
    "parent_review_result","parent_project_candidate","new_document_grade",
    "new_document_url","new_document_date","new_document_locator",
    "project_claim_supported","source_boundary_verified","original_JORC_approved",
    "project_id_approved","C1_approved","next_review_action"
]

def csvrows(root,rel):
    with (root/rel).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def stable_sha(root,path):
    return hashlib.sha256((root/path).read_bytes()).hexdigest()

def choose_attr(attrs,*names):
    for name in names:
        x=attrs.get(name)
        if x is not None and str(x).strip() and str(x).strip().lower() not in ("none","null"):
            return str(x).strip()
    return ""

def unique(rows,key,label):
    out={}
    for row in rows:
        k=row[key]
        if not k or k in out:
            raise ValueError(f"{label}: missing/duplicate {key} {k}")
        out[k]=row
    return out

def build(root=ROOT):
    allrows=csvrows(root,QUEUE)
    source=unique([json.loads(x) for x in (root/RAW).read_text(encoding="utf-8").splitlines()
                   if x], "target_id", "raw native")
    census=csvrows(root,CENSUS)
    leads=csvrows(root,LEADS)
    if len(allrows)!=272 or len(source)!=272 or len(census)!=487 or len(leads)!=11:
        raise ValueError("Frozen evidence corpus changed; use a new dated audit")

    targets=[x for x in allrows if x["evidence_review_status"]=="PROJECT_PARENT_UNLOCATED"]
    if len(targets)!=156 or len({x["target_id"] for x in targets})!=156:
        raise ValueError("Expected 156 unique unresolved source target IDs")
    names=defaultdict(list)
    for x in census:
        names[(x["state"],x["name"].casefold().strip())].append(x["target_id"])
    lead_idx=unique([{**x,"lookup":(x["state"]+"|"+x["source_name"].casefold().strip())}
                     for x in leads], "lookup","official parent document")
    records=[]
    hist=Counter()
    native_hist=Counter()
    by_state=Counter()
    for x in targets:
        target=x["target_id"]
        native=source[target]
        attrs=native["source_attributes"]
        if x["native_feature_exact"]!="YES" or native["source_key"]!=x["source_key"] or native["native_id"]!=x["source_native_id"]:
            raise ValueError(f"Raw feature identity mismatch for {target}")
        state=x["state"]
        name=x["source_name"]
        lead=lead_idx.get(state+"|"+name.casefold().strip())
        source_kind=x["source_key"]
        if source_kind=="STATE_WA_MINDEX":
            entity=choose_attr(attrs,"site_type_","site_sub_t")
            stage=choose_attr(attrs,"site_stage")
            commodity=choose_attr(attrs,"site_commo","target_com")
            main=choose_attr(attrs,"commodity")
            url=choose_attr(attrs,"web_link")
        elif source_kind=="STATE_TAS_MRT":
            entity=choose_attr(attrs,"DEPOSIT_TYPE")
            stage=choose_attr(attrs,"OPERATIONAL_STATUS")
            commodity=choose_attr(attrs,"COMMODITIES")
            main=choose_attr(attrs,"COMMODITY_CATEGORY")
            url=choose_attr(attrs,"DETAILS")
        elif source_kind.startswith("SA_"):
            entity=choose_attr(attrs,"DEPOSIT_CLASS","MINDEP_CLASS_CODE")
            stage=choose_attr(attrs,"DEPOSIT_STATUS","STATUS_TYPE_VALUE")
            commodity=choose_attr(attrs,"COMMODITIES","DEPOSIT_COMMODITIES","DEPOSIT_COMMODITY_CODES")
            main=choose_attr(attrs,"MAJOR_COMMODITY_CODE")
            url=choose_attr(attrs,"MAIN_REFERENCE")
            # MAIN_REFERENCE may be a document number such as 'Env 9278', not a URL.
            url=url if url.startswith(("http://","https://")) else ""
        else:
            entity=choose_attr(attrs,"currentstatus","status","deposit_type","TYPE")
            stage=choose_attr(attrs,"currentstatus","status")
            commodity=choose_attr(attrs,"commodity","commodities")
            main=choose_attr(attrs,"mineraldeposittype")
            url=choose_attr(attrs,"source")
            url=url[url.index("https://"):] if "https://" in url else ""
        source_ree=("REE_PRIMARY_UNVERIFIED" if source_kind.startswith("GA_")
                    else "REE_IN_SOURCE_COMMODITY_METADATA")
        if source_kind.startswith("SA_") and main.upper() not in ("REE","REO","RARE EARTHS"):
            source_ree="REE_ASSOCIATED_NONPRIMARY_IN_NATIVE_COMMODITY"
        if source_kind=="STATE_WA_MINDEX" and entity in ("Occurrence","Target","Infrastructure","Prospect"):
            source_ree="GEOLOGICAL_SITE_WITH_REE_COMMODITY_NOT_INDEPENDENT_PROJECT"
        if source_kind=="STATE_TAS_MRT" and str(attrs.get("RESOURCES","")).upper()=="N":
            source_ree="TAS_SOURCE_RESOURCE_FLAG_N"
        matches=names[(state,name.casefold().strip())]
        others=sorted(z for z in matches if z!=target)
        relation="NO_INDEPENDENT_PROJECT_PARENT_DOCUMENT_FOUND"
        parent=grade=docurl=docdate=locator=""
        claim="NO"
        nextstep=("Locate published title + boundary + Project report and explain REE role; "
                  "retain geological source record in C0")
        if lead is not None:
            parent=lead["candidate_parent_project"]
            grade=lead["claim_grade"]
            docurl=lead["source_url"]
            docdate=lead["source_publication_or_status_date"]
            locator=lead["document_locator_and_supported_claim"]
            if grade in ("SIMILAR_NAME_BOUNDARY_UNVERIFIED","REGIONAL_GENERIC_NAME_SCOPE_UNVERIFIED"):
                relation="NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED"
                nextstep="Verify same deposit boundary; a similar name cannot establish parentage"
            else:
                relation="DOCUMENTED_NAMED_PROJECT_CANDIDATE_NOT_APPROVED"
                claim="PROJECT_NAME_SUPPORTED_BOUNDARY_UNCHECKED"
                nextstep=("Independently check source point inside documented Project boundary, "
                          "date of rights and whether REE is an actual recoverable product")
        elif source_kind=="STATE_WA_MINDEX" and entity in ("Infrastructure","Target","Occurrence","Prospect"):
            relation="OFFICIAL_NONPROJECT_SITE_TYPE_PARENT_UNLOCATED"
            nextstep="Keep source as site/prospect/target; obtain separate project/tenure evidence"
        elif source_kind=="STATE_TAS_MRT" and stage in ("Prospect","Mineral occurrence","Not worked"):
            relation="OFFICIAL_GEOLOGICAL_SITE_PARENT_UNLOCATED"
        else:
            relation="NO_INDEPENDENT_PROJECT_PARENT_DOCUMENT_FOUND"
        if not native["original_chunk_sha256"] or not native["source_relative_path"]:
            raise ValueError(f"Source provenance missing for {target}")
        rec=dict(zip(COLS,[
            target,state,name,source_kind,x["source_native_id"],x["original_entity_type"],
            native["source_feature_locator"],native["original_chunk_sha256"],
            native["source_relative_path"],url,entity,stage,commodity,main,
            str(attrs.get("RESOURCES","")) if source_kind=="STATE_TAS_MRT" else "",
            source_ree,str(len(matches)),";".join(others),"NO",
            relation,parent,grade,docurl,docdate,locator,claim,
            "NO","NO","NO","NO",nextstep
        ]))
        records.append(rec)
        hist[relation]+=1
        native_hist[source_ree]+=1
        by_state[state]+=1
    if len(records)!=156 or any(x["C1_approved"]!="NO" or x["project_id_approved"]!="NO" or x["source_boundary_verified"]!="NO" for x in records):
        raise AssertionError("Approval/target population invariant failed")
    expected={
        "DOCUMENTED_NAMED_PROJECT_CANDIDATE_NOT_APPROVED":8,
        "NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED":3,
    }
    for k,v in expected.items():
        if hist[k]!=v:raise ValueError(f"Document lead sentinel {k}: {hist[k]} expected {v}")
    stats={
        "review_date":"2026-10-31",
        "source_cutoff":"2026-10-29",
        "research_unit":"156 previously unresolved source-target IDs, not 156 unique REE Projects",
        "input_target_count":156,
        "unique_id_count":len({x["target_id"] for x in records}),
        "new_official_or_issuer_document_leads":len(leads),
        "named_project_document_candidates":hist["DOCUMENTED_NAMED_PROJECT_CANDIDATE_NOT_APPROVED"],
        "named_project_scope_holds":hist["NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED"],
        "remaining_without_new_parent_document":156-len(leads),
        "remaining_without_verified_project_boundary":156,
        "project_identity_approvals":0,"C1_approvals":0,
        "cross_source_same_state_name_rows":sum(int(x["within_state_same_name_count"])>1 for x in records),
        "by_state":dict(by_state),
        "review_result_counts":dict(hist),
        "native_ree_role_counts":dict(native_hist),
        "input_sha256":{
            QUEUE:stable_sha(root,QUEUE),RAW:stable_sha(root,RAW),
            CENSUS:stable_sha(root,CENSUS),LEADS:stable_sha(root,LEADS)
        },
        "policy":"Government site/deposit is C0 evidence, not a verified independent Project. Same state+name does not prove identity; dated official named Project is a candidate only pending Project boundary, REE product, stage/JORC and approval."
    }
    return records,stats

def output(root=ROOT):
    rows,stats=build(root)
    p=root/OUTPUT
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLS,lineterminator="\n");w.writeheader();w.writerows(rows)
    with (root/GAPS).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLS,lineterminator="\n");w.writeheader()
        w.writerows(r for r in rows if r["project_claim_supported"]=="NO")
    (root/REPORT).write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False))
    return stats

if __name__=="__main__":
    output()
