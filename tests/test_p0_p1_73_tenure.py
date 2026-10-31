"""Regression for P1 government-source tenure overlay vs Project boundaries."""
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p1_tenure", ROOT / "scripts/audit_p0_p1_73_tenure.py")
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class P1Tenure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.stats = module.build(ROOT)

    def test_73_rows_and_official_overlap_counts(self):
        self.assertEqual(len(self.rows), 73)
        self.assertEqual(sum(int(x["official_tenement_intersection_count"])
                             for x in self.rows), 204)
        self.assertEqual(self.stats["official_tenure_query_status_counts"],
                         {"TENURE_INTERSECTS_PENDING_COMPANY_VERIFICATION": 60,
                          "NO_OVERLAP_IN_QUERIED_LAYERS": 11,
                          "OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED": 2})

    def test_title_match_does_not_approve_project(self):
        self.assertEqual(self.stats["rows_with_exact_documented_title_number_overlap"], 20)
        self.assertEqual(len(self.stats["distinct_cases_with_exact_title_overlap"]), 12)
        self.assertTrue(all(x["C1_approved"] == "NO" and
                            x["project_or_mine_footprint_intersected"] == "NOT_TESTED"
                            for x in self.rows))

    def test_temporal_conflicts_not_rewritten(self):
        by_case = {}
        for r in self.rows:
            by_case.setdefault(r["case_id"], []).append(r)
        self.assertTrue(all(not x["exact_title_matches"] for x in by_case["P1X-0008"]))
        self.assertTrue(all(x["documented_title_comparison"] !=
                            "DOCUMENTED_TENEMENT_NUMBER_INTERSECTS_SOURCE_POINT"
                            for x in by_case["P1X-0004"]))
        self.assertTrue(all(x["exact_title_matches"] == "E3701311"
                            for x in by_case["P1G-0021"]))

    def test_checked_snapshots_match(self):
        self.assertEqual(module.read(ROOT / module.OUT),
                         [{k: str(v) for k, v in r.items()} for r in self.rows])

if __name__ == "__main__":
    unittest.main()
