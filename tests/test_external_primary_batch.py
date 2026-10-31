import csv
import unittest
from pathlib import Path
from scripts.check_external_primary_batch import validate, ROOT, BATCH, TRACKER

class ExternalPrimaryBatchTests(unittest.TestCase):
    def test_complete_lineage_and_paused_gate(self):
        validate()

    def test_scaddan_conflict_and_byte_hold(self):
        with BATCH.open(encoding="utf-8-sig", newline="") as f:
            rows = {r["target_id"]: r for r in csv.DictReader(f)}
        item = rows["E1:C-c1e7aa1538298437b0bdec"]
        self.assertIn("fine-grained secondary phosphates", item["technical_finding"])
        self.assertIn("ion-adsorption", item["technical_finding"])
        self.assertEqual(item["original_bytes_archived"], "NO")
        self.assertEqual(item["original_byte_sha256"], "")
        self.assertEqual(item["formal_C1_or_MCDA_change"], "NO")

    def test_p2_recheck_is_not_claimed_for_unread_sources(self):
        with TRACKER.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(sum("NEW_DIRECT_GOVERNMENT" in r["review_2026_10_31"] for r in rows), 3)
        self.assertEqual(sum("PENDING" in r["review_2026_10_31"] for r in rows), 25)

if __name__ == "__main__":
    unittest.main()
