"""Project P0/P1 73 final desk dispositions, preserving six-gate C1 prohibition."""
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p1_closeout", ROOT / "scripts/audit_p0_p1_closeout.py")
x = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(x)

class CloseoutP1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.stats = x.build(ROOT)

    def test_seventy_three_immutable_census_rows(self):
        self.assertEqual(len(self.rows), 73)
        self.assertEqual(len({a["target_id"] for a in self.rows}), 73)
        self.assertEqual(len({a["case_id"] for a in self.rows}), 44)
        self.assertTrue(all(len(a["native_chunk_sha256"]) == 64 for a in self.rows))

    def test_all_dispositions_accounted(self):
        self.assertEqual(self.stats["source_dispositions"], {
            "C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION": 2,
            "C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED": 5,
            "C0_NO_PROJECT_SCOPED_REE_PRODUCT_PROOF": 40,
            "C0_POSITIVE_PROJECT_OR_REE_LEAD": 22,
            "C0_UNRESOLVED_NATIVE_IDENTITY_CONFLICT": 4
        })
        self.assertEqual(self.stats["positive_cases_gate_reviewed"], 13)

    def test_no_project_or_c1_promotion(self):
        self.assertTrue(all(a["independent_C1_admission"] == "NO" and
                            a["census_cohort"] == "C0_ONLY_NOT_ADMITTED"
                            for a in self.rows))
        self.assertTrue(all(a["legal_project_footprint_verified"] ==
                            "NO_NOT_PERFORMED" for a in self.rows))
        self.assertTrue(all(a["human_reviewer_signature"] == "" for a in self.rows))
        self.assertFalse(self.stats["CI_validated"])

    def test_benmara_wemen_wamex_and_positive_gates(self):
        idx = {a["case_id"]: a for a in self.rows}
        self.assertEqual(idx["P1X-0004"]["p1_evidence_disposition"],
                         "C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION")
        self.assertEqual(idx["P1G-0009"]["documented_stage"],
                         "POST_FID_PRODUCTION_CEASED_2004")
        self.assertEqual(idx["P1X-0018"]["p1_evidence_disposition"],
                         "C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED")
        self.assertEqual(idx["P1G-0021"]["WINDOW_gate"],
                         "HOLD_NO_COMPLETE_ECONOMIC_STUDY_ASOF")

    def test_reproducible_snapshot(self):
        self.assertEqual(x.read(ROOT / x.OUT), self.rows)

if __name__ == "__main__":
    unittest.main()
