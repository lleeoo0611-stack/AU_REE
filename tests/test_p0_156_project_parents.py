"""P0 156-source Project parent audit: preserve native provenance and approval gates."""
import csv
import json
import unittest
from pathlib import Path
from importlib.util import module_from_spec,spec_from_file_location

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("audit156",ROOT/"scripts/audit_p0_156_project_parents.py")
module=module_from_spec(spec)
spec.loader.exec_module(module)

class Audit156(unittest.TestCase):
    def test_full_frozen_156(self):
        rows,s=module.build(ROOT)
        self.assertEqual(len(rows),156)
        self.assertEqual(len(set(x["target_id"] for x in rows)),156)
        self.assertEqual(sum(s["by_state"].values()),156)
        self.assertTrue(all(x["original_raw_sha256"] and x["official_source_locator"]
                            for x in rows))
    def test_documents_and_no_hasty_parent_approval(self):
        rows,s=module.build(ROOT)
        self.assertEqual(s["named_project_document_candidates"],8)
        self.assertEqual(s["named_project_scope_holds"],3)
        self.assertEqual(s["remaining_without_new_parent_document"],145)
        self.assertEqual(s["remaining_without_verified_project_boundary"],156)
        self.assertTrue(all(x["project_id_approved"]=="NO" and x["C1_approved"]=="NO"
                            and x["original_JORC_approved"]=="NO"
                            and x["source_boundary_verified"]=="NO" for x in rows))
        self.assertTrue(all(x["name_cross_source_is_parent_evidence"]=="NO" for x in rows))
    def test_temporal_and_project_scope_split(self):
        rows,_=module.build(ROOT)
        by_name={x["source_name"]:x for x in rows}
        self.assertEqual(by_name["Mulga Rock"]["parent_review_result"],
                         "DOCUMENTED_NAMED_PROJECT_CANDIDATE_NOT_APPROVED")
        self.assertEqual(by_name["Wim deposits"]["parent_review_result"],
                         "NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED")
        self.assertEqual(by_name["Tutunup West"]["parent_review_result"],
                         "NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED")
        self.assertEqual(by_name["Meenar Plant (Deferred)"]["official_raw_entity_type"],
                         "Infrastructure")
    def test_versioned_output_rebuild(self):
        frozen=ROOT/module.OUTPUT
        if not frozen.exists():
            self.skipTest("Build in P0 artifact workflow before snapshot comparison")
        rows,_=module.build(ROOT)
        with frozen.open(encoding="utf-8",newline="") as f:
            self.assertEqual(list(csv.DictReader(f)),rows)

if __name__=="__main__":
    unittest.main()
