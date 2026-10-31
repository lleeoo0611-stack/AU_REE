"""B06 regression: cause classification, evidence scopes and immutable C1 gates."""
import unittest
from collections import Counter
from scripts.build_p234_reason_classification_b06 import generate, rows, OUT, SUMMARY
import json

class B06AuditRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.summary = generate()
    def test_all_original_339_rows_still_present(self):
        self.assertEqual(len(self.records), 339)
        self.assertEqual(len({x["target_id"] for x in self.records}),339)
        self.assertEqual(Counter(x["priority"] for x in self.records),{"P2":28,"P3":216,"P4":95})
    def test_manual_reviews_and_workqueue(self):
        self.assertEqual(self.summary["new_P2_bounded_primary_text"],4)
        self.assertEqual(self.summary["P2_source_scoped_text_total"],20)
        self.assertEqual(self.summary["P2_remaining_desk_only"],8)
        self.assertEqual(self.summary["P3_remaining_native"],87)
        self.assertEqual(self.summary["P4_remaining_native"],64)
        self.assertEqual(self.summary["remaining_priority_work_units"],108)
        self.assertEqual(self.summary["related_locator_rows"],8)
    def test_elaine_historic_resource_corrected_only_in_overlay(self):
        cases=[x for x in self.records if x["source_name"]=="Elaine Dorothy" and x["priority"]=="P2"]
        self.assertEqual(len(cases),1)
        self.assertIn("HISTORIC_2010_JORC_INFERRED_83000T_3200PPM_TREO",cases[0]["resource_basis_annotation"])
        self.assertEqual(cases[0]["C1_admitted"],"NO")
    def test_bells_homonym_holds_separate_sites(self):
        bell=[x for x in self.records if x["source_name"]=="Bells Monazite" and x["priority"]=="P2"]
        self.assertEqual(len(bell),1)
        self.assertIn("HOMONYM_BELLS_MONAZITE",bell[0]["resource_basis_annotation"]+
                      bell[0]["new_bounded_finding"]+bell[0]["cross_source_consistency_issue"])
    def test_never_claim_pdf_freeze_project_or_C1_approval(self):
        self.assertTrue(all(x["source_snapshot"]=="2026-10-29" and x["original_pdf_bytes_new"]=="NO"
                            and x["source_freeze_approval"]==x["identity_approval"]==
                            x["C1_admitted"]=="NO" for x in self.records))
        self.assertEqual(self.summary["original_C0_close_candidate_count"],119)
        self.assertEqual(self.summary["formally_frozen_sources"],0)
    def test_derived_csv_and_json_same_as_builder(self):
        self.assertEqual(rows(OUT), self.records)
        with SUMMARY.open(encoding="utf-8") as file:
            self.assertEqual(json.load(file),self.summary)

if __name__=="__main__":
    unittest.main()
