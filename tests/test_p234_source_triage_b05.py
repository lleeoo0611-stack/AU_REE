"""B05 regression: identity-safe grouping, non-release and reproducibility."""
import csv
import unittest
from collections import Counter
from scripts.build_p234_source_triage_b05 import generate, read_csv, TRIAGE, GROUPS, QUEUE, SUMMARY
import json

class SourceTriageB05Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.groups, cls.queue, cls.summary = generate()

    def test_preserve_all_339_ids_and_priority_levels(self):
        self.assertEqual(len(self.rows), 339)
        self.assertEqual(len({r["target_id"] for r in self.rows}), 339)
        self.assertEqual(Counter(r["priority"] for r in self.rows), {"P2":28, "P3":216, "P4":95})

    def test_source_evidence_levels_are_disjoint(self):
        self.assertEqual(Counter(r["source_review_status"] for r in self.rows), {
            "ARCHIVED_RELEVANT_PAGES":143, "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY":32,
            "WEB_CACHED_TEXT_ONLY":1, "INHERITED_DESK_NO_NEW_ORIGINAL":12,
            "NATIVE_FEATURE_ONLY":151,
        })

    def test_native_locator_crosswalk_retains_all_ids(self):
        self.assertEqual(len(self.groups),100)
        self.assertEqual(sum(int(g["member_source_count"]) for g in self.groups),151)
        self.assertEqual(sum(int(g["member_source_count"])>1 for g in self.groups),51)
        self.assertEqual(sum("|" in g["source_keys"] for g in self.groups),30)
        self.assertTrue(all(g["name_disagreement"]=="NO" and g["coordinate_over_1km"]=="NO"
                            and g["same_native_id_is_approved_project_merge"]=="NO" for g in self.groups))

    def test_open_queue_is_112_units_and_closure_not_approved(self):
        self.assertEqual(len(self.queue),112)
        self.assertEqual(Counter(g["unit_type"] for g in self.queue),
                         {"P2_INDIVIDUAL_SOURCE":12, "P34_SHARED_NATIVE_LOCATOR":100})
        self.assertTrue(all(x["closure_decision"]=="NOT_APPROVED" for x in self.queue))
        self.assertEqual(self.summary["proposed_source_scope_closure_candidates"],119)
        self.assertEqual(self.summary["formally_frozen_source_rows"],0)

    def test_c1_and_pdf_gate_never_autopromoted(self):
        self.assertTrue(all(r["C1_eligibility_status"]=="NOT_ADMITTED_SIX_GATES_UNAPPROVED"
                            and r["source_scope_human_signed"]=="NO"
                            and r["technical_original_fulltext_verified"]=="NO"
                            and r["original_document_newly_archived"]=="NO" for r in self.rows))

    def test_published_derived_csv_json_match_generation(self):
        self.assertEqual(read_csv(TRIAGE), self.rows)
        self.assertEqual(read_csv(GROUPS), self.groups)
        self.assertEqual(read_csv(QUEUE), self.queue)
        with SUMMARY.open(encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), self.summary)

if __name__ == "__main__":
    unittest.main()
