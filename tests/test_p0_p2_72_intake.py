"""P2 Census 72-source intake regression: stable source keys and no C1 admission."""
from __future__ import annotations
import unittest
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p2_72", ROOT / "scripts/audit_p0_p2_72_intake.py")
assert spec and spec.loader
p2 = module_from_spec(spec)
spec.loader.exec_module(p2)

class P2Intake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.cases, cls.stats = p2.build(ROOT)

    def test_immutable_priority_partition_and_overlap(self):
        self.assertEqual(len(self.sources), 72)
        self.assertEqual(len({x["target_id"] for x in self.sources}), 72)
        self.assertEqual(self.stats["original_census_rows"], 487)
        self.assertEqual(self.stats["prior_p1_73_exact_target_overlaps"], 0)
        self.assertTrue(all(x["prior_p1_target_overlap"] == "NO" for x in self.sources))
        self.assertEqual(self.stats["original_p2_action_counts"], {
            "CHECK_REE_RESOURCE_AND_COMPLETED_STUDY": 37,
            "ESTABLISH_DISTINCT_PROJECT_IDENTITY_AND_SOURCE_LINK": 25,
            "REVIEW_REE_ROLE_AND_INDEPENDENT_PROJECT_ID": 9,
            "VERIFY_CURRENT_ACTIVE_STATUS": 1
        })

    def test_cases_are_review_groups_not_approved_projects(self):
        self.assertEqual(len(self.cases), 47)
        self.assertEqual(sum(int(x["source_rows"]) for x in self.cases), 72)
        self.assertEqual(self.stats["p2_reviewed_group_cases"], 22)
        self.assertEqual(self.stats["p2_unlinked_source_cases"], 25)
        self.assertEqual(sum(x["case_type"] == "ONE_UNLINKED_SOURCE_ROW"
                             for x in self.cases), 25)
        self.assertTrue(all(x["source_group_evidence_only"] == "YES"
                            for x in self.cases))

    def test_seven_documentary_leads_are_only_case_context(self):
        self.assertEqual(self.stats["distinct_case_documentary_leads"], 7)
        self.assertEqual(self.stats["p2_case_documentary_leads"], 7)
        self.assertEqual(self.stats["source_rows_with_new_document_context"], 22)
        self.assertEqual(self.stats["document_progress_counts"], {
            "INHERITED_REVIEW_GROUP_DOCUMENT_CONTEXT__UNAPPROVED": 27,
            "INHERITED_TRACE_OR_SOURCE_LEAD_ONLY": 23,
            "NEW_ISSUER_OR_GOV_DOCUMENT_LOCATED__CASE_SCOPE_ONLY": 22
        })
        byid = {x["new_document_lead_id"]: x for x in self.cases
                if x["new_document_lead_id"]}
        self.assertEqual(byid["P2D-001"]["resource_grade_basis"], "TREO")
        self.assertEqual(byid["P2D-002"]["resource_grade_basis"], "TREOY")
        self.assertIn("MULTIDEPOSIT_TOTAL_DO_NOT_ALLOCATE",
                      byid["P2D-003"]["resource_nonaddition_rule"])
        self.assertIn("STUDY_PLAN_ONLY", byid["P2D-004"]["resource_nonaddition_rule"])
        self.assertIn("HISTORICAL_NONREE_RESOURCE",
                      byid["P2D-005"]["resource_nonaddition_rule"])

    def test_no_jurisdiction_point_project_or_scoring_promotion(self):
        self.assertTrue(all(x["verified_Project_polygon"] == "NO" for x in self.sources))
        self.assertTrue(all(x["independent_project_approved"] == "NO" and
                            x["independent_JORC_REO_approved"] == "NO" and
                            x["C1_approved"] == "NO" for x in self.sources))
        self.assertEqual(self.stats["c1_approved"], 0)
        self.assertEqual(self.stats["project_footprints_approved"], 0)
        self.assertEqual(self.stats["stage_gate"],
                         "P2_INTAKE_COMPLETE_TARGETED_PRIMARY_LEADS_ADDED_NOT_CASE_CLOSED")
        self.assertTrue(all(not x["reviewer_signature"] for x in self.sources))

    def test_frozen_csv_and_summary_rebuild(self):
        self.assertEqual(p2.read(ROOT, p2.OUT_SOURCE), self.sources)
        self.assertEqual(p2.read(ROOT, p2.OUT_CASE), [
            {k: str(r[k]) for k in p2.CASE_FIELDS} for r in self.cases
        ])
        self.assertEqual(self.stats["frozen_as_of"], "2026-10-29")

if __name__ == "__main__":
    unittest.main()
