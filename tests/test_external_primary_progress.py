import csv
import unittest
from scripts.check_external_primary_progress import validate, BATCH2, INDEX

class ExternalPrimaryProgressTests(unittest.TestCase):
    def test_id_counts_and_evidence_boundaries(self):
        validate()

    def test_pindari_two_sources_never_auto_merge(self):
        with BATCH2.open(encoding="utf-8-sig", newline="") as f:
            data = list(csv.DictReader(f))
        items = [r for r in data if r["source_name"] == "PINDARI"]
        self.assertEqual(len(items), 2)
        self.assertEqual(len({x["target_id"] for x in items}), 2)
        self.assertTrue(all("no scoped reo" in x["resource_basis_review"].lower()
                            or "no published prospect-specific treo" in x["resource_basis_review"].lower() for x in items))

    def test_progress_preserves_unverified_157(self):
        with INDEX.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(sum(r["source_scope_disposition"] ==
            "REQUIRES_EXTERNAL_PRIMARY_TECHNICAL_DOCUMENT" for r in rows), 157)

if __name__ == "__main__":
    unittest.main()
