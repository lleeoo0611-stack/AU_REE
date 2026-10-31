"""P2-P4 event gate tests: no event means skip; new events cannot cause C1."""
import unittest
from scripts.route_p234_new_evidence_v1 import generate, rows, BASE, OUTPUT, SUMMARY
import json

class EvidenceTriggerTest(unittest.TestCase):
    def test_empty_event_is_idempotent_and_no_c1_promotion(self):
        items,summary=generate()
        self.assertEqual(items,[])
        self.assertEqual(summary["trigger_state"],"SKIP_NO_NEW_EVIDENCE")
        self.assertEqual(summary["C1_automatic_promotions"],0)
        self.assertEqual(rows(OUTPUT),[])
        self.assertEqual(json.loads(SUMMARY.read_text(encoding="utf-8")),summary)
    def test_real_event_creates_review_only(self):
        original=next(x for x in rows(BASE) if x["priority"]=="P3")
        row={"event_id":"EV-P234-TEST01","target_id":original["target_id"],
             "source_key":original["source_key"],"source_native_id":original["source_native_id"],
             "source_snapshot":"2026-10-29","evidence_doc_id":"TEST-NTGS-123",
             "official_url":"https://example.gov.au/technical.pdf",
             "published_date":"2026-10-20","original_sha256":"",
             "original_bytes_archived":"NO","section_locator":"Section 4, Table 1",
             "claim_type":"RESOURCE_JORC_REO","submission_reason":"New original document was found"}
        items,summary=generate(events=[row],decisions=[])
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["C1_admitted"],"NO")
        self.assertEqual(items[0]["review_status"],"NEW_SOURCE_SCOPE_REVIEW_REQUIRED")
        self.assertEqual(items[0]["temporal_scope"],"WITHIN_FROZEN_SOURCE_DATE")
        row["published_date"]="2026-11-01"
        items,summary=generate(events=[row],decisions=[])
        self.assertEqual(items[0]["temporal_scope"],"POST_2026_10_29_NEW_VERSION_ONLY")
        self.assertEqual(summary["post_snapshot_events"],1)
    def test_dedup_and_invalid_original_hash_fail_closed(self):
        original=next(x for x in rows(BASE) if x["priority"]=="P4")
        row={"event_id":"EV-P234-TEST02","target_id":original["target_id"],
             "source_key":original["source_key"],"source_native_id":original["source_native_id"],
             "source_snapshot":"2026-10-29","evidence_doc_id":"REPORT-TEST",
             "official_url":"https://gov.example.gov.au/report.html","published_date":"2026-10-02",
             "original_sha256":"","original_bytes_archived":"YES","section_locator":"p3",
             "claim_type":"PROJECT_IDENTITY","submission_reason":"New report"}
        with self.assertRaises(ValueError):
            generate(events=[row],decisions=[])
        row["original_bytes_archived"]="NO"
        with self.assertRaises(ValueError):
            generate(events=[row,row],decisions=[])

if __name__=="__main__":
    unittest.main()
