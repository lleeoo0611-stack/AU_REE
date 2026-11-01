"""Acceptance tests for accepted C0 two-tier policy and strict C1/C2 cohorts."""
import unittest
import json
from unittest.mock import patch
from scripts import build_c0_freeze_c1_c2_v1 as cohort_module
from collections import Counter
from scripts.build_c0_freeze_c1_c2_v1 import (
    build, read_rows, OUT_C0, OUT_COHORT, OUT_P1, OUT_SUM,
    signed_freeze, gates_with_signatures
)
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
    def test_signed_gate_decisions_can_pass_after_cutoff_without_early_release(self):
        """Synthetic approvals test valid decisions; they do not sign real Project evidence."""
        meta = {
            "verified_project_id": "SYNTHETIC-PROJECT", "project_identity_scope": "Synthetic mine",
            "project_footprint_ref": "SYNTHETIC-FOOTPRINT", "ree_product_role_ref": "SYNTHETIC-ROLE",
            "resource_statement_id": "SYNTHETIC-MRE", "resource_basis": "TREO",
            "original_jorc_ref": "SYNTHETIC-JORC", "approved_study_document_id": "SYNTHETIC-STUDY",
            "study_published_asof": "2026-10-01", "approved_panel_version": "SYNTHETIC-PANEL",
            "approved_gis_evidence_id": "SYNTHETIC-GIS"
        }
        def sign(cohort, gate):
            return {
                "gate_id": gate, "cohort": cohort, "decision_status": "PASS",
                "source_asof": "2026-10-29", "reason_code": "SYNTHETIC_FIXTURE",
                "document_id": "SYNTHETIC-DOC",
                "original_sha256_or_html_ref": "SYNTHETIC-ARCHIVE-REF",
                "reviewer_id": "Synthetic Fixture Reviewer", "reviewed_at": "2026-11-01",
                "approval_ref": "SYNTHETIC-APP"
            }
        decisions = [sign("C2", g) for g in ("ID", "ROLE")]
        decisions += [sign("C1", g) for g in ("ID", "ROLE", "WINDOW", "JORC", "PANEL", "GIS_RELEASE")]
        status = gates_with_signatures(decisions, self.projects[0], meta)
        self.assertTrue(all(status[g, "C1"] == "PASS" for g in
                            ("ID", "ROLE", "WINDOW", "JORC", "PANEL", "GIS_RELEASE")))
        self.assertEqual(status["ID", "C2"], "PASS")
        self.assertEqual(status["ROLE", "C2"], "PASS")
        # Publication date after the cutoff must still fail even for a later signed review.
        with self.assertRaisesRegex(ValueError, "published after source cutoff"):
            gates_with_signatures(decisions, self.projects[0],
                                  {**meta, "study_published_asof": "2026-10-30"})

    def test_synthetic_signoffs_flow_through_cohort_builder(self):
        group = next(p for p in self.projects
                     if p["screening_class"] == "STUDY_DOCUMENTED_PRE_FID_SCREEN")
        gid = group["review_group_id"]
        metadata = {
            "review_group_id": gid,
            "verified_project_id": "SYNTHETIC-VERIFIED-PROJECT",
            "project_identity_scope": "Synthetic separate Project scope",
            "project_footprint_ref": "SYNTHETIC-FOOTPRINT",
            "ree_product_role_ref": "SYNTHETIC-REE-ROLE",
            "resource_statement_id": "SYNTHETIC-RESOURCE",
            "resource_basis": "TREO", "original_jorc_ref": "SYNTHETIC-JORC",
            "approved_study_document_id": "SYNTHETIC-STUDY",
            "study_published_asof": "2026-10-01",
            "approved_panel_version": "SYNTHETIC-PANEL",
            "approved_gis_evidence_id": "SYNTHETIC-GIS"
        }
        def signed(cohort, gate):
            return {
                "review_group_id": gid, "cohort": cohort, "gate_id": gate,
                "decision_status": "PASS", "reason_code": "SYNTHETIC_TEST",
                "document_id": "SYNTHETIC-DOC", "original_sha256_or_html_ref": "SYNTHETIC-HASH",
                "source_asof": "2026-10-29", "reviewer_id": "Synthetic Reviewer",
                "reviewed_at": "2026-11-01", "approval_ref": "SYNTHETIC-SIGNOFF"
            }
        signed_rows = ([signed("C2", g) for g in ("ID", "ROLE")] +
                       [signed("C1", g) for g in ("ID", "ROLE", "WINDOW",
                                                 "JORC", "PANEL", "GIS_RELEASE")])
        original_read = cohort_module.read_rows
        def read_fixture(path):
            if path == cohort_module.GATE_APPROVAL:
                return signed_rows
            if path == cohort_module.PROJ_METADATA:
                return [metadata]
            return original_read(path)
        with patch.object(cohort_module, "read_rows", side_effect=read_fixture):
            _, projects, _, summary = cohort_module.build()
        updated = next(p for p in projects if p["review_group_id"] == gid)
        self.assertEqual(updated["C1_release_status"], "C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES")
        self.assertEqual(updated["C2_project_id_approved"], "YES")
        self.assertEqual(summary["approved_C1_cohort_projects"], 1)
        self.assertEqual(summary["approved_C2_cohort_projects"], 1)

    def test_output_rebuild_is_identical(self):
        self.assertEqual(read_rows(OUT_C0),self.c0)
        self.assertEqual(read_rows(OUT_COHORT),self.projects)
        self.assertEqual(read_rows(OUT_P1),self.p1)
        with OUT_SUM.open(encoding="utf-8") as fp:
            self.assertEqual(json.load(fp),self.summary)
if __name__=="__main__":
    unittest.main()
