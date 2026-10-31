"""P2 phase-1: immutable 412 HOLD partition, 28 C0 sources, 27 site keys."""
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p2_28", ROOT / "scripts/audit_p2_28_initial_triage.py")
p2 = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(p2)

class TestP2InitialTriage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.cases, cls.stats = p2.build(ROOT)
        cls.by_case = {x["case_id"]: x for x in cls.cases}

    def test_partition_frozen_412(self):
        self.assertEqual(self.stats["original_hold_412"], 412)
        self.assertEqual(
            (self.stats["closed_prior_P1_source_rows"],
             self.stats["p2_source_rows"],
             self.stats["p3_source_rows_untouched"],
             self.stats["p4_source_rows_untouched"]),
            (73, 28, 216, 95)
        )
        self.assertEqual(len(self.sources), 28)
        self.assertEqual(len({x["target_id"] for x in self.sources}), 28)
        self.assertEqual(len(self.cases), 27)
        self.assertEqual(sum(int(x["source_target_count"]) for x in self.cases), 28)

    def test_source_identity_and_legacy_isolation(self):
        self.assertEqual(sum(x["legacy_or_E1_source"] == "LEGACY_86"
                             for x in self.sources),22)
        self.assertEqual(sum(x["legacy_or_E1_source"] == "UNLINKED_E1_401"
                             for x in self.sources),6)
        self.assertTrue(all(x["original_priority"] == "P2" for x in self.sources))
        self.assertTrue(all(not x["original_coordinate_latitude"] and
                            not x["original_coordinate_longitude"]
                            for x in self.sources
                            if x["legacy_or_E1_source"] == "LEGACY_86"))

    def test_mary_kathleen_mine_vs_tailings_not_merged(self):
        mine = self.by_case["P2G-0012"]
        tail = self.by_case["P2G-0011"]
        self.assertEqual(mine["source_target_count"],2)
        self.assertEqual(tail["source_target_count"],1)
        self.assertEqual(mine["source_entity_type"],"DEPOSIT")
        self.assertEqual(tail["source_entity_type"],"SOURCE_PROJECT_RECORD")
        self.assertNotEqual(mine["project_identity_scope"],tail["project_identity_scope"])

    def test_port_pirie_historic_treatment_not_mining_mre(self):
        x = self.by_case["P2G-0013"]
        self.assertEqual(x["evidence_class"],"SOUTH_AUSTRALIA_OFFICIAL_DEPOSIT_RECORD")
        self.assertTrue(x["evidence_url"].endswith("DEPOSIT_NO=8908"))
        self.assertEqual(x["independent_JORC_REO_approved"],"NO")

    def test_bondi_must_not_inherit_iluka_douglas(self):
        bondi = self.by_case["P2G-0019"]
        douglas = self.by_case["P2G-0021"]
        self.assertIn("DO_NOT_LINK_DOUGLAS",bondi["project_identity_scope"])
        self.assertNotEqual(bondi["case_id"],douglas["case_id"])
        self.assertEqual(douglas["C1_admitted"],"NO")

    def test_source_fidelity_and_no_C1_admission(self):
        self.assertTrue(all(x["C1_admitted"] == x["project_title_or_polygon_approved"] ==
                            x["independent_project_id_approved"] ==
                            x["independent_JORC_REO_approved"] == "NO"
                            for x in self.sources))
        self.assertTrue(all(x["p2_stage_status"] == "PHASE1_DOCUMENTARY_TRIAGE_NOT_FORMAL_SIGNOFF"
                            and not x["reviewer_signed_off"] for x in self.sources))
        self.assertEqual(self.stats["p2_C1_admissions"],0)
        self.assertEqual(self.stats["p1_WAMEX_official_pdfs_outstanding"],4)

    def test_resource_not_claimed_from_oxide_or_exploration(self):
        self.assertEqual(self.by_case["P2G-0014"]["documented_stage"],"EXPLORATION_DRILLING_2024")
        self.assertEqual(self.by_case["P2G-0004"]["documented_stage"],"EXPLORATION_ASOF_2026")
        self.assertTrue(all(x["independent_JORC_REO_approved"] == "NO" for x in self.cases))

    def test_snapshots_roundtrip(self):
        self.assertEqual(p2.read_csv(ROOT, p2.OUT_SOURCES),self.sources)
        self.assertEqual(p2.read_csv(ROOT,p2.OUT_CASES),[
            {k:str(v) for k,v in x.items()} for x in self.cases
        ])

if __name__ == "__main__":
    unittest.main()
