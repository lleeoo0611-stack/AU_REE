"""P0 P1 73-row Project-parent/source evidence no-promotion tests."""
import unittest
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p0_p1", ROOT / "scripts/audit_p0_p1_parent_identity.py")
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class P1Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.summary = module.build(ROOT)

    def test_fixed_frozen_target_set(self):
        self.assertEqual(len(self.rows), 73)
        self.assertEqual(len({r["target_id"] for r in self.rows}), 73)
        self.assertEqual(dict(Counter(x["p1_category"] for x in self.rows)),
            {"PARENT_CANDIDATE": 48, "INDEX_PRIMARY_PENDING": 4, "IDENTITY_SCOPE_HOLD": 21})
        self.assertTrue(all(len(x["native_chunk_sha256"]) == 64 for x in self.rows))

    def test_no_fabricated_admission_or_jurisdiction(self):
        for r in self.rows:
            self.assertEqual(r["original_project_identity_approved"], "NO")
            self.assertEqual(r["original_JORC_REO_approved"], "NO")
            self.assertEqual(r["original_C1_approved"], "NO")
            self.assertEqual(r["external_primary_bytes_archived"], "NO")

    def test_ambergate_not_auto_merged(self):
        am = [r for r in self.rows if r["state"] == "WA" and r["source_name"] == "Ambergate"]
        self.assertEqual(len(am), 2)
        self.assertEqual(len({r["target_id"] for r in am}), 2)
        self.assertTrue(all(x["p1_category"] == "IDENTITY_SCOPE_HOLD" for x in am))
        self.assertTrue(all(x["original_state_or_spatial_issue"].startswith("SAME_NAME") for x in am))

    def test_historic_index_is_not_original_pdf(self):
        index = [r for r in self.rows if r["p1_category"] == "INDEX_PRIMARY_PENDING"]
        self.assertEqual(len(index), 4)
        self.assertEqual({x["source_name"] for x in index}, {"Hopelands East", "Hassell Beach", "Witchcliffe"})
        self.assertTrue(all(x["new_p1_review_level"].startswith("SECONDARY_") for x in index))

    def test_manual_claims_have_original_target_ids(self):
        checks = [r for r in self.rows if not r["new_p1_review_level"].startswith("NOT_YET")]
        self.assertEqual(len(checks), 14)
        self.assertEqual(len([x for x in checks if x["source_name"] == "Tower"]), 2)
        self.assertEqual(len([x for x in checks if x["source_name"] == "WINGELLINA"]), 2)

    def test_committed_snapshot_matches_rebuild(self):
        self.assertEqual(module.read(ROOT / module.OUT), self.rows)

if __name__ == "__main__":
    unittest.main()
