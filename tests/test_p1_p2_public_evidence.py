"""P1 31 outstanding source review and P2 28 scoped documentary case closeout."""
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("public_closure",ROOT/"scripts/audit_p1_p2_public_evidence.py")
p=module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(p)

class TestP1P2PublicReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1,cls.p2,cls.stats=p.build(ROOT)

    def test_p1_remaining_count(self):
        self.assertEqual(len(self.p1),31)
        self.assertEqual(len({x["target_id"] for x in self.p1}),31)
        self.assertEqual(len({x["case_id"] for x in self.p1}),19)
        self.assertEqual(self.stats["P1_remaining_source_tracks"],{
            "GEO_IDENTITY_CONFLICT":4,
            "POSITIVE_REE_OR_PROJECT_LEAD":22,
            "WAMEX_OFFICIAL_PRIMARY_ACCESS":5})
        self.assertEqual(self.stats["P1_WAMEX_unique_reports_indexed"],4)
        self.assertEqual(self.stats["P1_WAMEX_official_pdf_originals_archived"],0)

    def test_p2_all_28_fixed_census(self):
        self.assertEqual(len(self.p2),28)
        self.assertEqual(len({x["target_id"] for x in self.p2}),28)
        self.assertEqual(len({x["case_id"] for x in self.p2}),27)
        self.assertEqual(self.stats["HOLD_source_total"],412)
        self.assertEqual(self.stats["P3_source_rows_unchanged"],216)
        self.assertEqual(self.stats["P4_source_rows_unchanged"],95)
        self.assertEqual(self.stats["P2_case_documentary_verdict_counts"],p.P2_VERDICTS)

    def test_p1_p2_target_ids_disjoint(self):
        self.assertFalse({x["target_id"] for x in self.p1}&
                         {x["target_id"] for x in self.p2})

    def test_ree_grade_basis_and_historical_resource_gates(self):
        by={x["case_id"]:x for x in self.p2}
        self.assertIn("NO_MRE",by["P2G-0003"]["REE_or_resource_basis"])
        self.assertIn("MRE",by["P2G-0009"]["REE_or_resource_basis"])
        self.assertIn("HM_RESOURCE_NOT_REO_JORC",by["P2G-0023"]["REE_or_resource_basis"])
        self.assertEqual(by["P2G-0016"]["scoped_documentary_verdict"],
                         "PRIMARY_DRILL_NEGATIVE_FOR_TESTED_REE_TARGET")
        self.assertEqual(by["P2G-0013"]["scoped_documentary_verdict"],
                         "DOCUMENTED_HISTORIC_SITE_OUTSIDE_CURRENT_PREFID")

    def test_no_auto_promotion_no_fictitious_original_sha(self):
        for x in self.p1+self.p2:
            self.assertEqual(x["C1_admitted"],"NO")
            self.assertFalse(x["reviewer_signature"])
            for col in ("ID_gate","ROLE_gate","WINDOW_gate","JORC_gate","PANEL_gate",
                        "GIS_release_gate"):
                self.assertTrue(x[col].startswith("HOLD_"))
        self.assertTrue(all(not x["official_WAMEX_original_PDF_sha256"]
                            for x in self.p1))
        self.assertTrue(all(not x["original_pdf_SHA256_if_archived"]
                            for x in self.p2))

    def test_snapshot_roundtrip(self):
        self.assertEqual(p.read(ROOT,p.P1_OUT),self.p1)
        self.assertEqual(p.read(ROOT,p.P2_OUT),self.p2)
        import json
        self.assertEqual(json.loads((ROOT/p.SUMMARY).read_text(encoding="utf-8")),
                         self.stats)

if __name__=="__main__":
    unittest.main()
