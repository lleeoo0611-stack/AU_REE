"""P0 P1 review: all 73 immutable IDs evidence-scoped and held from C1."""
from collections import Counter
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p1_73", ROOT / "scripts/audit_p0_p1_73_resolution.py")
p1 = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(p1)

class P1Resolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.cases, cls.stats = p1.build(ROOT)

    def test_exact_73_targets_44_cases(self):
        self.assertEqual(len(self.sources), 73)
        self.assertEqual(len({x["target_id"] for x in self.sources}), 73)
        self.assertEqual(len(self.cases), 44)
        self.assertEqual(len({x["case_id"] for x in self.cases}), 44)
        self.assertEqual(sum(int(x["source_row_count"]) for x in self.cases), 73)
        self.assertEqual(self.stats["source_count_by_category"],
                         {"IDENTITY_SCOPE_HOLD": 21, "INDEX_PRIMARY_PENDING": 4,
                          "PARENT_CANDIDATE": 48})

    def test_no_false_reo_gis_release(self):
        self.assertTrue(all(x["C1_approved"] == "NO" for x in self.sources))
        self.assertTrue(all(x["source_point_polygon_tested"] == "NO" for x in self.sources))
        self.assertTrue(all(x["independent_JORC_REO_approved"] == "NO" for x in self.sources))
        self.assertEqual(self.stats["official_polygon_source_row_intersections_tested"], 0)
        self.assertEqual(self.stats["C1_admissions"], 0)

    def test_benmara_and_korella_resource_basis(self):
        named = {x["case_id"]: x for x in self.cases}
        self.assertEqual(named["P1X-0004"]["resource_basis_evidence"], "V2O5_MRE_NOT_TREO_MRE")
        self.assertEqual(named["P1G-0005"]["REE_role_evidence"],
                         "JORC_YTTRIUM_OXIDE_RESOURCE_CLAIM")
        self.assertEqual(named["P1G-0008"]["resource_basis_evidence"],
                         "THM_JORC_WITH_NO_TREO_MRE")
        self.assertEqual(named["P1X-0008"]["source_row_count"], 2)

    def test_index_not_falsely_approved(self):
        index = [x for x in self.sources if x["p1_source_category"] == "INDEX_PRIMARY_PENDING"]
        self.assertEqual(len(index), 4)
        self.assertEqual({x["source_name"] for x in index},
                         {"Hassell Beach", "Hopelands East", "Witchcliffe"})
        self.assertTrue(all(x["documentary_verdict"] ==
            "REPORT_INDEX_FOUND__OFFICIAL_PDF_NOT_RETRIEVED" for x in index))

    def test_snapshot_reproducibility(self):
        self.assertEqual(p1.read_csv(ROOT, p1.OUT_SOURCES),
                         [{k: str(v) for k, v in x.items()} for x in self.sources])
        self.assertEqual(p1.read_csv(ROOT, p1.OUT_CASES),
                         [{k: str(v) for k, v in x.items()} for x in self.cases])

if __name__ == "__main__":
    unittest.main()
