"""Evidence-content and convergence acceptance tests, including public replay."""
import copy
import csv
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("final_evidence", ROOT / "scripts/close_p234_evidence_status.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FinalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "work").mkdir(exist_ok=True)
        cls.rows, cls.nine, cls.summary = mod.build()
        cls.byid = {r["target_id"]: r for r in cls.rows}
        cls.byname = {r["source_name"]: r for r in cls.nine}
        cls.docs, _ = mod.documents(ROOT)

    def public_copy(self, root):
        paths = [mod.base.PRIOR, mod.PRIOR, mod.NINE, mod.INPUT, mod.RULES, mod.ACCESS, mod.WEB,
                 mod.SEALED, *mod.MANIFESTS, *mod.APPROVALS]
        for rel in paths:
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)

    def test_exact_339_sources_and_priorities_not_project_count(self):
        original = mod.base.read(ROOT / mod.base.PRIOR)
        self.assertEqual({r["target_id"] for r in self.rows}, {r["target_id"] for r in original})
        self.assertEqual(len(self.rows), 339)
        self.assertEqual(Counter(r["priority"] for r in self.rows), {"P2": 28, "P3": 216, "P4": 95})
        self.assertEqual(self.summary["P2_provisional_case_count"], 27)
        self.assertEqual(sum(self.summary["terminal_evidence_status_counts"].values()), 339)

    def test_nine_original_replacement_and_web_counts_are_distinct(self):
        self.assertEqual({r["target_id"] for r in self.nine}, {r["target_id"] for r in mod.base.read(ROOT / mod.NINE)})
        for key, value in [("new_batch_archived_original_content_targets", 8),
                           ("new_batch_nominated_original_targets_archived", 5),
                           ("new_batch_replacement_primary_targets_original_pointer_unarchived", 3),
                           ("new_batch_web_only_targets_original_bytes_unavailable", 1),
                           ("all_144_archived_original_content_targets", 143)]:
            self.assertEqual(self.summary[key], value)
        self.assertEqual(sum(r["nominated_pointer_access_status"] != "NOMINATED_ORIGINAL_BYTES_ARCHIVED" for r in self.nine), 4)

    def test_yellowband_actual_original_and_mineral_basis(self):
        r = self.byname["Yellowband Plain"]
        self.assertEqual(r["document_id"], "DOC-35df3a91e30e")
        self.assertEqual(r["original_total_pdf_pages"], "141")
        self.assertEqual(r["pdf_pages_or_html_sections"], "1,76,77")
        self.assertTrue(r["original_document_sha256"])
        self.assertIn("mineral-composition", r["documentary_finding"])
        self.assertIn("DOC-93f4b7e9c9f4", r["supporting_content_verification_json"])
        self.assertIn("NOT_BULK_ORE", r["REE_resource_basis"])

    def test_scaddan_access_observation_never_invents_original(self):
        r = self.byname["Scaddan"]
        self.assertEqual(r["original_document_sha256"], "")
        self.assertEqual(r["original_archive_path"], "")
        self.assertEqual(r["batch_work_disposition"], "CLASSIFIED_EXTERNAL_ORIGINAL_ACCESS_HOLD")
        checks = self.summary["Scaddan_external_access_checks"]
        self.assertEqual(checks["publisher_dns_at_retrieval"], "NXDOMAIN")
        self.assertEqual(checks["exact_available_snapshot_count"], 0)
        self.assertIn("not proof", checks["limit"])

    def test_scope_transfer_limits_in_new_originals(self):
        self.assertIn("OFFSHORE", self.byname["Naracoopa"]["documentary_finding"])
        self.assertIn("ONSHORE_OFFSHORE", self.byname["Naracoopa"]["terminal_documentary_disposition"])
        self.assertIn("not a negative REE", self.byname["Rubble Flats"]["documentary_finding"])
        self.assertIn("not place Rubble Flats inside", self.byname["Rubble Flats"]["documentary_finding"])
        self.assertIn("corrects the earlier map-only", self.byname["Stronach"]["documentary_finding"])

    def test_quantum_exact_original_preserves_two_ids_and_vintage_conflict(self):
        q = [r for r in self.nine if r["source_name"] == "Quantum"]
        self.assertEqual(len(q), 2)
        self.assertEqual(len({r["target_id"] for r in q}), 2)
        self.assertTrue(all(r["document_id"] == "DOC-edbbf85f0220" for r in q))
        self.assertIn("600 km", q[0]["documentary_finding"])
        self.assertIn("February 2026", q[0]["documentary_finding"])
        self.assertIn("not an MRE", q[0]["documentary_finding"])

    def test_all_sources_have_status_evidence_gap_and_paused_approval(self):
        for r in self.rows:
            self.assertTrue(r["current_documentary_finding"] and r["current_remaining_gap_and_reopen_condition"])
            self.assertEqual(r["source_review_classification_complete"], "YES")
            self.assertEqual(r["original_technical_fulltext_complete_claimed"], "NO")
            self.assertEqual(r["Project_approval"], "UNCHANGED_HOLD")
            self.assertEqual(r["C1_admitted"], "NO")
            self.assertFalse(r["independent_approval_signature"])
            self.assertEqual(r["C1_13_gate_MCDA"], "PAUSED_BY_USER")
        self.assertFalse(self.summary["all_technical_originals_complete"])
        self.assertEqual(self.summary["formal_approvals_changed"], 0)

    def test_native_only_and_inherited_desk_are_not_new_fulltext(self):
        counts = self.summary["content_access_status_counts"]
        self.assertEqual(counts["NATIVE_FEATURE_CONTENT_ONLY_NOT_TECHNICAL_DOCUMENT_REVIEW"], 167)
        self.assertEqual(counts["INHERITED_P2_DESK_REVIEW_NOT_REVERIFIED_FULLTEXT"], 28)
        previous = mod.base.unique(mod.base.read(ROOT / mod.base.PRIOR))
        for r in self.rows:
            if r["target_id"] not in {x["target_id"] for x in mod.base.read(ROOT / mod.PRIOR)}:
                self.assertEqual(r["current_documentary_disposition"], previous[r["target_id"]]["terminal_documentary_disposition"])

    def test_public_checkout_exact_replay_without_original_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            self.public_copy(root)
            rows, nine, summary = mod.build(root)
            self.assertEqual((rows, nine, summary), (self.rows, self.nine, self.summary))
            with self.assertRaisesRegex(ValueError, "Required original bytes absent"):
                mod.review_nine(root, require_originals=True)

    def test_original_sha_and_page_binding_mutations_rejected(self):
        r = copy.deepcopy(self.byname["Yellowband Plain"])
        doc = copy.deepcopy(self.docs[r["document_id"]])
        doc["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA256"):
            mod.base.verify_document(doc, r)
        doc = self.docs[r["document_id"]]
        r["pdf_pages_or_html_sections"] = "9999"
        with self.assertRaisesRegex(ValueError, "exceeds"):
            mod.base.verify_document(doc, r)
        r["pdf_pages_or_html_sections"] = "1"
        r["verification_anchor"] = "THIS_IS_NOT_AN_ORIGINAL_RESOURCE_STATEMENT"
        with self.assertRaisesRegex(ValueError, "anchor absent"):
            mod.base.verify_document(doc, r)

    def test_unmapped_outcome_cannot_silently_classify(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            self.public_copy(root)
            path = root / mod.RULES
            rules = json.loads(path.read_text(encoding="utf-8"))
            del rules["rules"][self.rows[0]["current_documentary_disposition"]]
            path.write_text(json.dumps(rules), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unmapped"):
                mod.build(root)

    def test_id_and_approval_mutations_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            self.public_copy(root)
            path = root / mod.INPUT
            rows = mod.base.read(path)
            original = rows[0]["target_id"]
            rows[0]["target_id"] = "INVENTED-SOURCE"
            path.write_bytes(mod.base.csv_bytes(rows))
            with self.assertRaisesRegex(ValueError, "IDs drifted"):
                mod.read_nine(root)
            rows[0]["target_id"] = original
            rows[0]["C1_admitted"] = "YES"
            path.write_bytes(mod.base.csv_bytes(rows))
            with self.assertRaisesRegex(ValueError, "Paused approval"):
                mod.read_nine(root)

    def test_external_response_bytes_and_interpretation_cannot_change(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            self.public_copy(root)
            path = root / mod.ACCESS
            checks = json.loads(path.read_text(encoding="utf-8"))
            checks[0]["response_utf8"] = "{}"
            path.write_text(json.dumps(checks), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "response SHA"):
                mod.access_checks(root, self.docs)

    def test_public_release_removes_inherited_credential_query_parameters(self):
        self.assertEqual(len(self.summary["public_redaction_target_ids"]), 2)
        self.assertFalse(mod.redaction.PATTERN.search(json.dumps(self.rows)))
        for separator in ["", " ", "\n", "\r\n"]:
            value = "https://example.invalid/report?" + separator + "access_token=dummy_secret&x=1"
            self.assertNotIn("dummy_secret", mod.redaction.clean(value))
            self.assertIn("x=1", mod.redaction.clean(value))

    def test_output_reproduction(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts/close_p234_evidence_status.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
