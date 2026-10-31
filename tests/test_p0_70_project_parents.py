"""Regression gates for immutable 70 original-only Project source evidence records."""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import csv
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("p0_70",ROOT/"scripts/audit_p0_70_project_parents.py")
module=module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class Audit70(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.stats=module.build(ROOT)

    def test_complete_frozen_population(self):
        self.assertEqual(len(self.rows),70)
        self.assertEqual(len({r["target_id"] for r in self.rows}),70)
        self.assertEqual(sum(self.stats["by_state"].values()),70)
        self.assertEqual(self.stats["curated_external_source_names"],25)
        self.assertTrue(all(x["source_native_feature_locator"] and
                            len(x["source_original_chunk_sha256"])==64 for x in self.rows))

    def test_project_ree_jorc_nonpromotion(self):
        for x in self.rows:
            self.assertEqual(x["project_scope_approved"],"NO")
            self.assertEqual(x["ree_product_verified"],"NO")
            self.assertEqual(x["JORC_TREO_approved"],"NO")
            self.assertEqual(x["C1_approved"],"NO")
            self.assertEqual(x["independent_external_primary_bytes_archived"],"NO")
        self.assertEqual(self.stats["all_C1_approvals"],0)

    def test_duplicate_stay_distinct_and_Tower_documented(self):
        byname={}
        for r in self.rows:
            byname.setdefault((r["state"],r["source_name"]),[]).append(r)
        tower=byname[("WA","Tower")]
        self.assertEqual(len(tower),2)
        self.assertEqual(len({x["target_id"] for x in tower}),2)
        self.assertTrue(all(x["round6_evidence_grade"]==
                 "HISTORICAL_PROJECT_PARENT_DOCUMENT_CANDIDATE" for x in tower))
        benmara=byname[("NT","Benmara South")]
        self.assertEqual(len(benmara),2)
        self.assertTrue(all(x["round6_evidence_grade"]==
                 "PROJECT_OR_JURISDICTION_IDENTITY_HOLD" for x in benmara))
        self.assertEqual(len(byname[("WA","Hassell Beach")]),2)

    def test_sa_border_and_resource_semantics(self):
        target=[x for x in self.rows if x["source_name"]=="WINGELLINA"]
        self.assertEqual(len(target),2)
        self.assertTrue(all(x["state"]=="SA" and
                   x["state_geometry_flag"]==
                   "SA_TAGGED_SOURCE_WEST_OF_129E_NEAR_WA_BORDER_REVIEW" for x in target))
        self.assertEqual(self.stats["cross_state_coordinate_flagged"],2)
        self.assertTrue(all(x["round6_evidence_grade"]=="CROSS_STATE_SOURCE_COORDINATE_HOLD"
                            for x in target))
        mount=[x for x in self.rows if x["source_name"]=="Mount Gee"]
        self.assertEqual(mount[0]["round6_evidence_grade"],
                         "EXTERNAL_GEOLOGICAL_OR_NON_REE_CONTEXT_ONLY")
        self.assertEqual(mount[0]["JORC_TREO_approved"],"NO")

    def test_output_snapshot_regression(self):
        path=ROOT/module.OUT
        if not path.exists():
            self.skipTest("Generated in the publication workflow")
        with path.open(encoding="utf-8",newline="") as f:
            self.assertEqual(list(csv.DictReader(f)),self.rows)

if __name__=="__main__":
    unittest.main()
