"""Acceptance tests for accepted C0 two-tier policy and strict C1/C2 cohorts."""
import unittest
import csv
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch
from scripts import build_c0_freeze_c1_c2_v1 as cohort_module
from collections import Counter
from scripts.build_c0_freeze_c1_c2_v1 import (
    build, read_rows, OUT_C0, OUT_COHORT, OUT_P1, OUT_SUM,
    signed_freeze, gates_with_signatures
)
def approved_fixture(root, group):
    """All evidence and approvals are synthetic and isolated from repository inputs."""
    from au_ree.core import setup
    from au_ree.evidence import reload_registry
    from au_ree.identity_policy import apply_identity_decisions
    from au_ree.stages.population import candidate_upsert

    def write_csv(path, fields, records):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer=csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    db=sqlite3.connect(":memory:")
    db.row_factory=sqlite3.Row
    setup(db)
    candidate={
        "source": "SYNTHETIC_ISSUER", "native_id": "SYNTH-C0-1",
        "name": group["project_name"], "state": group["state"],
        "commodity": "REE", "entity_level": "PROJECT",
        "official": True, "source_url": "https://example.gov.au/identity",
    }
    assert candidate_upsert(db, candidate) == "REVIEW"
    cid=db.execute("SELECT candidate_id FROM population_candidates").fetchone()[0]
    specs={
        "IDENTITY":("PROJECT_REVIEW",b"Synthetic issuer Project scope"),
        "OTHER":("PROJECT_REVIEW",b"Synthetic source-backed REE statement"),
        "GIS":("GIS_LAYER",b"Synthetic official GIS release"),
    }
    docs={}
    for label, (_,content) in specs.items():
        path=root/"inputs"/"evidence"/(label.lower()+".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        docs[label]={
            "document_id":"SYNTH-DOC-"+label,
            "file_path":path.relative_to(root).as_posix(),
            "source_url":"https://example.gov.au/"+label.lower(),
            "sha256":hashlib.sha256(content).hexdigest(),
        }
    write_csv(root/"inputs/source_documents.csv",
              ["document_id","file_path","source_url","sha256"],list(docs.values()))
    gate_labels={"ID":"IDENTITY", "ROLE":"OTHER", "WINDOW":"OTHER",
                 "JORC":"OTHER", "PANEL":"OTHER", "GIS_RELEASE":"GIS"}
    approvals=[]
    for gate,label in gate_labels.items():
        typ=("GIS_LAYER" if gate=="GIS_RELEASE" else
             "OBSERVATION" if gate in ("WINDOW","JORC") else
             "PROJECT_REVIEW")
        approvals.append({
            "approval_ref":"SYNTH-APP-"+gate,"record_type":typ,
            "document_id":docs[label]["document_id"],
            "reviewer":"Synthetic Fixture Reviewer","decision":"APPROVED",
            "reviewed_at":"2026-11-01",
        })
    write_csv(root/"inputs/evidence_approvals.csv",
              ["approval_ref","record_type","document_id","reviewer","decision","reviewed_at"],approvals)
    write_csv(root/"inputs/project_identity_decisions.csv",
              ["candidate_id","decision","project_name","project_id","source_url",
               "source_sha256","evidence_date","approval_ref"],[{
                "candidate_id":cid,"decision":"APPROVE_NEW_PROJECT",
                "project_name":group["project_name"],"project_id":"",
                "source_url":docs["IDENTITY"]["source_url"],
                "source_sha256":docs["IDENTITY"]["sha256"],
                "evidence_date":"2026-10-01","approval_ref":"SYNTH-APP-ID",
              }])
    reload_registry(db,root,"2026-10-29")
    assert apply_identity_decisions(db,root,"2026-10-29")["approved_new"] == 1
    project_id=db.execute("SELECT project_id FROM project_master WHERE population_status='EVIDENCE_BACKED_PROJECT'").fetchone()[0]
    db.commit()  # SQLite backup requires a committed source; never wait on an open write transaction.
    metadata={
        "review_group_id":group["review_group_id"],
        "verified_project_id":project_id,
        "project_identity_scope":"Synthetic distinct mining Project",
        "project_footprint_ref":"SYNTHETIC-FOOTPRINT",
        "ree_product_role_ref":"SYNTHETIC-REE-ROLE",
        "resource_statement_id":"SYNTHETIC-MRE",
        "resource_basis":"TREO","original_jorc_ref":"SYNTHETIC-JORC",
        "approved_study_document_id":"SYNTHETIC-PFS",
        "study_published_asof":"2026-10-01",
        "approved_panel_version":"SYNTHETIC-PANEL",
        "approved_gis_evidence_id":"SYNTHETIC-GIS",
    }
    def signed(cohort,gate):
        label=gate_labels[gate]
        return {
            "review_group_id":group["review_group_id"],
            "cohort":cohort,"gate_id":gate,"decision_status":"PASS",
            "reason_code":"SYNTHETIC_TEST",
            "document_id":docs[label]["document_id"],
            "original_sha256_or_html_ref":docs[label]["sha256"],
            "source_asof":"2026-10-29",
            "reviewer_id":"Synthetic Fixture Reviewer",
            "reviewed_at":"2026-11-01",
            "approval_ref":"SYNTH-APP-"+gate,
        }
    decisions=[signed("C2",g) for g in ("ID","ROLE")]
    decisions += [signed("C1",g) for g in ("ID","ROLE","WINDOW","JORC","PANEL","GIS_RELEASE")]
    return db,metadata,decisions,docs

class CohortFreezePolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c0,cls.projects,cls.p1,cls.summary=build()
    def test_exact_source_universe_and_f1_f2(self):
        self.assertEqual(len(self.c0),339)
        self.assertEqual(len({x["target_id"] for x in self.c0}),339)
        self.assertEqual(Counter(x["priority"] for x in self.c0),{"P2":28,"P3":216,"P4":95})
        self.assertEqual(self.summary["proposed_F1_candidates"],119)
        self.assertEqual(self.summary["proposed_F2_native_search_pause_prechecks"],151)
        self.assertEqual(self.summary["F2_with_b06_known_unresolved_locator_lead"],6)
        self.assertTrue(all(x["C1_admitted"]=="NO" for x in self.c0))
    def test_p1_cases_are_not_thirteen_auto_new_projects(self):
        self.assertEqual(len(self.p1),13)
        self.assertEqual(self.summary["P1_distinct_project_additions_approved"],0)
        self.assertTrue(all(x["unique_project_counted_as_new"]=="NO" for x in self.p1))
    def test_provisional_c2_candidates_not_admitted(self):
        self.assertEqual(len(self.projects),39)
        self.assertEqual(sum(x["C2_identity_review_candidate"]=="YES" for x in self.projects),28)
        self.assertEqual(self.summary["approved_C1_cohort_projects"],
                         sum(x["C1_release_status"]=="C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"
                             for x in self.projects))
        self.assertEqual(self.summary["approved_C2_cohort_projects"],
                         sum(x["C2_project_id_approved"]=="YES" for x in self.projects))
        self.assertTrue(all(x["C1_release_status"]!="C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"
                            or x["C2_project_id_approved"]=="YES" for x in self.projects))
    def test_f2_known_locator_cannot_be_paused_even_with_signature(self):
        row=next(x for x in self.c0 if x["proposed_route"].startswith("F2") and x["related_source_locator_ref"])
        d={"freeze_class":"F2_NATIVE_SEARCH_PAUSED","reviewer_id":"human","approved_at":"2026-10-31",
           "source_snapshot_sha256":row["selected_feature_sha256"],
           "evidence_document_ref":"NEGATIVE_SOURCE_SEARCH_LOG:test","page_or_section":"section 1",
           "scope_decision":"NATIVE_ONLY","reopen_trigger":"NEW_ORIGINAL",
           "rule_version":"C0_F1F2_COHORT_C1C2_V1_20261031","approval_ref":"review-1"}
        with self.assertRaises(ValueError):
            signed_freeze(row,d)
    def test_f1_requires_real_human_signature(self):
        row=next(x for x in self.c0 if x["proposed_route"].startswith("F1"))
        with self.assertRaises((ValueError,KeyError)):
            signed_freeze(row,{"freeze_class":"F1_SOURCE_SCOPE_FROZEN"})
    def test_c1_c2_gate_cannot_pass_without_project_metadata_or_review(self):
        group=self.projects[0]
        d={"gate_id":"JORC","cohort":"C1","decision_status":"PASS","source_asof":"2026-10-29",
           "reason_code":"SOURCE_REPORTED","document_id":"ref",
           "original_sha256_or_html_ref":"not-signed-resource","reviewer_id":"human",
           "reviewed_at":"2026-10-31","approval_ref":"approval-not-verified"}
        with self.assertRaises(ValueError):
            gates_with_signatures([d],group,None)
    def test_unsigned_gate_rows_do_not_count_as_approved(self):
        """Complete-looking strings must not bypass archived approvals or Project identity."""
        group=next(x for x in self.projects if x["screening_class"]=="STUDY_DOCUMENTED_PRE_FID_SCREEN")
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            db,meta,decisions,_=approved_fixture(root,group)
            with self.assertRaisesRegex(ValueError,"signed PASS has no independently"):
                gates_with_signatures(decisions,group,meta)
            with self.assertRaisesRegex(ValueError,"source record missing"):
                gates_with_signatures([{**decisions[0],"approval_ref":"FAKE-APPROVAL"}],
                                      group,meta,approval_db=db,approval_root=root)
            db.close()

    def test_source_cutoff_and_future_signatures_are_distinct(self):
        group=next(x for x in self.projects if x["screening_class"]=="STUDY_DOCUMENTED_PRE_FID_SCREEN")
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            db,meta,decisions,_=approved_fixture(root,group)
            status=gates_with_signatures(decisions,group,meta,
                                          approval_db=db,approval_root=root)
            self.assertEqual(status["ID","C2"],"PASS")
            self.assertTrue(all(status[gate,"C1"]=="PASS" for gate in
                                ("ID","ROLE","WINDOW","JORC","PANEL","GIS_RELEASE")))
            with self.assertRaisesRegex(ValueError,"published after source cutoff"):
                gates_with_signatures(decisions,group,
                                      {**meta,"study_published_asof":"2026-10-30"},
                                      approval_db=db,approval_root=root)
            with self.assertRaisesRegex(ValueError,"future-dated reviewer signature"):
                gates_with_signatures([{**decisions[0],"reviewed_at":"2099-01-01"}]+decisions[1:],
                                      group,meta,approval_db=db,approval_root=root)
            db.close()

    def test_authenticated_signed_cohort_and_document_tampering(self):
        group=next(x for x in self.projects if x["screening_class"]=="STUDY_DOCUMENTED_PRE_FID_SCREEN")
        gid=group["review_group_id"]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            db,meta,decisions,docs=approved_fixture(root,group)
            source_read=cohort_module.read_rows
            def read_fixture(path):
                if path==cohort_module.GATE_APPROVAL:
                    return decisions
                if path==cohort_module.PROJ_METADATA:
                    return [meta]
                return source_read(path)
            with patch.object(cohort_module,"read_rows",side_effect=read_fixture):
                _,projects,_,summary=cohort_module.build(identity_db=db,approval_root=root)
                approved=next(r for r in projects if r["review_group_id"]==gid)
                self.assertEqual(approved["C1_release_status"],
                                 "C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES")
                self.assertEqual(approved["C2_project_id_approved"],"YES")
                self.assertEqual(summary["approved_C1_cohort_projects"],1)
                self.assertEqual(summary["approved_C2_cohort_projects"],1)
                # Last-mile original bytes are rechecked on each build.
                original=root/docs["IDENTITY"]["file_path"]
                original.write_bytes(b"modified after independent approval")
                with self.assertRaisesRegex(ValueError,"source record missing"):
                    cohort_module.build(identity_db=db,approval_root=root)
                original.write_bytes(b"Synthetic issuer Project scope")
                # A source reviewer revocation must invalidate the signed gate.
                approval_file=root/"inputs/evidence_approvals.csv"
                lines=list(csv.DictReader(approval_file.open(encoding="utf-8")))
                for row in lines:
                    if row["approval_ref"]=="SYNTH-APP-ID":
                        row["decision"]="REVOKED"
                with approval_file.open("w",encoding="utf-8",newline="") as handle:
                    writer=csv.DictWriter(handle,fieldnames=list(lines[0]))
                    writer.writeheader();writer.writerows(lines)
                with self.assertRaisesRegex(ValueError,"source record missing"):
                    cohort_module.build(identity_db=db,approval_root=root)
            db.close()

    def test_signed_c2_identity_reaches_integrated_sqlite_and_is_revocable(self):
        """Synthetic original bytes -> signed identity -> C2 -> Structural -> Census SQLite."""
        import argparse
        import copy
        from scripts import build_structural_round01 as structural
        from reproducibility import build_census_database as census_db
        gid="PRJ-42437b4a11115372"  # Existing Copi ID+ROLE documentary-ready group.
        review_group=next(g for g in self.projects if g["review_group_id"]==gid)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            db,metadata,decisions,_=approved_fixture(root,review_group)
            canonical=root/"canonical_identity.sqlite"
            dest=sqlite3.connect(canonical)
            db.backup(dest)
            dest.close()
            db.close()
            signed=[d for d in decisions if d["cohort"]=="C2"]
            signed_input=root/"inputs/review_decisions/c1_c2_project_gate_signoffs_v1.csv"
            signed_input.parent.mkdir(parents=True,exist_ok=True)
            with signed_input.open("w",encoding="utf-8",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=list(signed[0]))
                writer.writeheader();writer.writerows(signed)
            original_read=cohort_module.read_rows
            def signed_read(path):
                if path==cohort_module.GATE_APPROVAL: return signed
                if path==cohort_module.PROJ_METADATA: return [metadata]
                return original_read(path)
            with patch.object(cohort_module,"read_rows",side_effect=signed_read):
                _,projects,_,summary=cohort_module.build(
                    identity_db=canonical,approval_root=root)
                self.assertEqual(summary["approved_C2_cohort_projects"],1)
                audits=root/"audits"
                audits.mkdir()
                (audits/"2026-10-31_c1_c2_project_review_39.csv").write_text(
                    cohort_module.csv_text(projects),encoding="utf-8")
                reviewdir=audits/"structural_round01"
                reviewdir.mkdir()
                structural_read=structural.read_csv
                def structural_input(path):
                    if path==structural.BASE:
                        return copy.deepcopy(projects)
                    if path.name=="c1_c2_project_gate_signoffs_v1.csv":
                        return signed
                    if path.name=="c1_c2_project_identity_metadata_v1.csv":
                        return [metadata]
                    return structural_read(path)
                with patch.object(structural,"read_csv",side_effect=structural_input):
                    outputs,structsum=structural.build(
                        identity_db=canonical,approval_root=root)
                    self.assertEqual(structsum["C2_approved"],1)
                    for name,content in outputs.items():
                        if name.endswith(".csv"):
                            (reviewdir/name).write_text(content,encoding="utf-8")
                args=argparse.Namespace(
                    csv_dir=cohort_module.ROOT/"outputs",review_dir=reviewdir,
                    output=root/"integrated.sqlite",as_of_date="2026-10-29",
                    identity_db=canonical,approval_root=root,overwrite=False)
                census_db.csv_build(args)
                with sqlite3.connect(args.output) as built:
                    row=built.execute("""SELECT verified_independent_project_id
                        FROM identity_crosswalk WHERE review_group_id=?""",(gid,)).fetchone()
                    self.assertEqual(row[0],metadata["verified_project_id"])
                manifest=json.loads(Path(str(args.output)+".manifest.json").read_text())
                self.assertEqual(manifest["census_relation_check"]
                                 ["independently_approved_projects"],1)
                baseline_sha=hashlib.sha256(args.output.read_bytes()).hexdigest()
                # Even a *partial* gate signoff must agree with the official
                # signed cohort before the existing SQLite can be replaced.
                cohort_csv=audits/"2026-10-31_c1_c2_project_review_39.csv"
                baseline_csv=cohort_csv.read_bytes()
                altered=list(csv.DictReader(cohort_csv.open(encoding="utf-8")))
                next(r for r in altered if r["review_group_id"]==gid)["JORC_gate"] = (
                    "PASS_FORGED_PARTIAL_GATE")
                with cohort_csv.open("w",encoding="utf-8",newline="") as handle:
                    writer=csv.DictWriter(handle,fieldnames=list(altered[0]))
                    writer.writeheader();writer.writerows(altered)
                args.overwrite=True
                with self.assertRaisesRegex(ValueError,"Signed cohort CSV must be rebuilt"):
                    census_db.csv_build(args)
                self.assertEqual(hashlib.sha256(args.output.read_bytes()).hexdigest(),
                                 baseline_sha)
                cohort_csv.write_bytes(baseline_csv)
                # A detached or revoked signature cannot replace a validated SQLite release.
                approval_file=root/"inputs/evidence_approvals.csv"
                records=list(csv.DictReader(approval_file.open(encoding="utf-8")))
                next(x for x in records if x["approval_ref"]=="SYNTH-APP-ID")["decision"]="REVOKED"
                with approval_file.open("w",encoding="utf-8",newline="") as handle:
                    writer=csv.DictWriter(handle,fieldnames=list(records[0]))
                    writer.writeheader();writer.writerows(records)
                args.overwrite=True
                with self.assertRaisesRegex(ValueError,"source record missing"):
                    census_db.csv_build(args)
                self.assertEqual(hashlib.sha256(args.output.read_bytes()).hexdigest(),
                                 baseline_sha)

    def test_output_rebuild_is_identical(self):
        self.assertEqual(read_rows(OUT_C0),self.c0)
        self.assertEqual(read_rows(OUT_COHORT),self.projects)
        self.assertEqual(read_rows(OUT_P1),self.p1)
        with OUT_SUM.open(encoding="utf-8") as fp:
            self.assertEqual(json.load(fp),self.summary)
if __name__=="__main__":
    unittest.main()
