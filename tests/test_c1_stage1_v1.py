"""C1 first-pass must preserve original source scope and independent six gates."""
import unittest
from collections import Counter
from unittest.mock import patch
from scripts import review_c1_stage1_v1 as review_module
from scripts.review_c1_stage1_v1 import generate,read,OUT,SUMMARY
import json

class C1Stage1Test(unittest.TestCase):
    def test_c1_documentary_review(self):
        rows,summary=generate()
        self.assertEqual(len(rows),39)
        self.assertEqual(len({r["review_group_id"] for r in rows}),39)
        self.assertEqual(summary["documentary_scope_rechecked"],7)
        self.assertEqual(summary["independent_C1_admitted"],
                         sum(r["independent_C1_release"]=="YES" for r in rows))
        self.assertEqual(sum(r["primary_review_level"].startswith("SCOPED") for r in rows),7)
        self.assertEqual(summary["independent_C2_admitted"],
                         sum(r["source_project_identity_signed"]=="YES" for r in rows))
        self.assertEqual(Counter(r["screening_class"] for r in rows)["OUTSIDE_PRE_FID_CONFIRMED"],2)
    def test_safeguards_for_thm_and_a_study_in_progress(self):
        rows,_=generate()
        b=next(x for x in rows if x["project_name"]=="Bungalally Mineral Sands Project")
        self.assertEqual(b["study_evidence_status"],"SCOPING_STAGE_ONLY_COMPLETION_NOT_PROVEN")
        self.assertEqual(b["REE_resource_evidence_status"],"JORC_THM_NO_SAME_SCOPE_TREO")
        j=next(x for x in rows if x["project_name"]=="Jupiter REE Project within Brothers")
        self.assertIn("TREO_RESOURCE_REPORTED",j["REE_resource_evidence_status"])
        self.assertEqual(j["independent_C1_release"],"NO")
    def test_signed_review_can_progress_without_invalidating_historical_source_checks(self):
        groups = read(review_module.INPUT)
        checks = read(review_module.REVIEWS)
        updated = [dict(group) for group in groups]
        group = updated[0]
        group["C2_project_id_approved"] = "YES"
        group["C2_release_status"] = "C2_VERIFIED_PROJECT_ID_AND_REE_ROLE_ADMITTED"
        group["C1_release_status"] = "C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"
        for gate in ("ID", "ROLE", "WINDOW", "JORC", "PANEL", "GIS_RELEASE"):
            group[gate+"_gate"] = "PASS_SYNTHETIC_UNIT_TEST"
        with patch.object(review_module, "read", side_effect=[updated, checks]):
            rows, summary = generate()
        row = next(r for r in rows if r["review_group_id"] == group["review_group_id"])
        self.assertEqual(row["approved_C1_gate_count"], "6")
        self.assertEqual(row["independent_C1_release"], "YES")
        self.assertEqual(row["source_project_identity_signed"], "YES")
        self.assertEqual(summary["independent_C1_admitted"], 1)
        self.assertEqual(summary["independent_C2_admitted"], 1)

    def test_rebuild_matches_checked_in_outputs(self):
        rows,summary=generate()
        self.assertEqual(read(OUT),rows)
        self.assertEqual(json.loads(SUMMARY.read_text(encoding="utf-8")),summary)

if __name__=="__main__":
    unittest.main()
