"""C1 first-pass must preserve original source scope and independent six gates."""
import unittest
from collections import Counter
from scripts.review_c1_stage1_v1 import generate,read,OUT,SUMMARY
import json

class C1Stage1Test(unittest.TestCase):
    def test_c1_documentary_review(self):
        rows,summary=generate()
        self.assertEqual(len(rows),39)
        self.assertEqual(len({r["review_group_id"] for r in rows}),39)
        self.assertEqual(summary["documentary_scope_rechecked"],7)
        self.assertEqual(summary["independent_C1_admitted"],0)
        self.assertEqual(sum(r["primary_review_level"].startswith("SCOPED") for r in rows),7)
        self.assertTrue(all(r["approved_C1_gate_count"]=="0" and r["source_project_identity_signed"]=="NO"
                            and r["independent_C1_release"]=="NO" for r in rows))
        self.assertEqual(Counter(r["screening_class"] for r in rows)["OUTSIDE_PRE_FID_CONFIRMED"],2)
    def test_safeguards_for_thm_and_a_study_in_progress(self):
        rows,_=generate()
        b=next(x for x in rows if x["project_name"]=="Bungalally Mineral Sands Project")
        self.assertEqual(b["study_evidence_status"],"SCOPING_STAGE_ONLY_COMPLETION_NOT_PROVEN")
        self.assertEqual(b["REE_resource_evidence_status"],"JORC_THM_NO_SAME_SCOPE_TREO")
        j=next(x for x in rows if x["project_name"]=="Jupiter REE Project within Brothers")
        self.assertIn("TREO_RESOURCE_REPORTED",j["REE_resource_evidence_status"])
        self.assertEqual(j["independent_C1_release"],"NO")
    def test_rebuild_matches_checked_in_outputs(self):
        rows,summary=generate()
        self.assertEqual(read(OUT),rows)
        self.assertEqual(json.loads(SUMMARY.read_text(encoding="utf-8")),summary)

if __name__=="__main__":
    unittest.main()
