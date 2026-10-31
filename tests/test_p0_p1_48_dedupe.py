"""Regression tests: 48 frozen source rows -> 25 provisional parents, no false REO/GIS release."""
import unittest
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p1_48", ROOT / "scripts/audit_p0_p1_48_dedupe.py")
p1 = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(p1)

class Parent48(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.links, cls.groups, cls.resources, cls.stats = p1.build(ROOT)

    def test_deterministic_48_to_25(self):
        self.assertEqual(len(self.links), 48)
        self.assertEqual(len({r["target_id"] for r in self.links}), 48)
        self.assertEqual(len(self.groups), 25)
        self.assertEqual(self.stats["distinct_source_site_name_keys"], 39)
        self.assertEqual(sum(int(x["source_record_count"]) for x in self.groups), 48)
        self.assertEqual(len({x["provisional_group_key"] for x in self.groups}), 25)

    def test_no_auto_merge_approval_or_gis_approval(self):
        self.assertTrue(all(r["identity_approval"] == r["C1_approval"] == "NO" for r in self.links))
        self.assertTrue(all(r["source_point_inside_project_polygon"] == "NOT_TESTED" for r in self.links))
        self.assertTrue(all(r["geometry_polygon_intersection"] == "NOT_PERFORMED" for r in self.groups))
        self.assertTrue(all(r["JORC_TREO_approval"] == r["C1_approval"] == "NO" for r in self.groups))

    def test_multi_deposit_not_duplicated(self):
        n = {r["canonical_parent_candidate"]: int(r["source_record_count"]) for r in self.groups}
        self.assertEqual(n["Redlings Rare Earths Project"], 6)
        self.assertEqual(n["Mt Stirling Project / Yttria Deposit"], 2)
        self.assertEqual(n["Mt Clere Project / Tower Deposit"], 2)
        self.assertEqual(n["Willandra West / Twelve Mile historical HMS area"], 8)

    def test_resource_basis_cutoff_and_nesting(self):
        self.assertEqual(len(self.resources), 12)
        self.assertEqual(dict(Counter(r["grade_basis"] for r in self.resources)), {"TREO": 10, "HM": 2})
        self.assertTrue(all(r["scoreable_TREO_resource_value"] == "NO_NOT_SIGNED_OFF" for r in self.resources))
        m = {r["statement_id"]: r for r in self.resources}
        self.assertTrue(m["P1R-002"]["resource_relationship"].startswith("STRICT_SUBSET_OF_"))
        self.assertEqual(m["P1R-009"]["resource_relationship"], "TOTAL_CHECK_ONLY_NO_SUM_WITH_COMPONENTS")
        self.assertEqual(m["P1R-003"]["scope_name"], "Central Mia prospect")
        self.assertEqual(m["P1R-010"]["grade_basis"], "HM")
        self.assertEqual(m["P1R-012"]["as_of_cutoff_admissibility"], "UNDETERMINED_UNDATED_SOURCE")

    def test_ree_resource_vs_tenement_scope(self):
        byname = {r["canonical_parent_candidate"]: r for r in self.groups}
        self.assertEqual(byname["Fraser Range / Talisker Project (separate Salazar)"]["resource_claim_rows"], 0)
        self.assertEqual(byname["Aileron Niobium–REE Project"]["resource_claim_rows"], 2)
        self.assertEqual(byname["Copi Mineral Sands Project"]["resource_basis_class"], "HM_ONLY_RESOURCE")

    def test_snapshot(self):
        self.assertEqual(p1.read_csv(ROOT / p1.OUT_LINKS), self.links)
        self.assertEqual(p1.read_csv(ROOT / p1.OUT_GROUPS),
                         [{k: str(v) for k, v in r.items()} for r in self.groups])
        self.assertEqual(p1.read_csv(ROOT / p1.OUT_RES), self.resources)

if __name__ == "__main__":
    unittest.main()
