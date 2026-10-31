"""Original-byte, page/content, scope and immutable-source acceptance tests."""
import copy
import importlib.util
import json
import subprocess
import tempfile
import shutil
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("primary_scope", ROOT / "scripts/review_p234_144_primary_scope.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PrimaryScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "work").mkdir(exist_ok=True)
        cls.rows, cls.updated, cls.summary = mod.build()
        cls.byname = {x["source_name"].casefold(): x for x in cls.rows}
        cls.documents = {}
        for path in mod.MANIFESTS:
            for d in json.loads((ROOT / path).read_text(encoding="utf-8")):
                if "archive_path" in d:
                    cls.documents[d["document_id"]] = d

    def test_fixed_144_ids_and_339_update(self):
        self.assertEqual(len(self.rows), 144)
        self.assertEqual(Counter(x["priority"] for x in self.rows), {"P3": 118, "P4": 26})
        self.assertEqual({x["target_id"] for x in self.rows}, {x["target_id"] for x in mod.read(ROOT / mod.FROZEN)})
        self.assertEqual(len(self.updated), 339)
        self.assertEqual(len({x["target_id"] for x in self.updated}), 339)
        self.assertTrue(all(x["current_disposition"] == x["prior_disposition"] for x in self.updated if x["new_original_content_review"] == "NOT_IN_144_BATCH"))

    def test_no_claim_that_access_or_fulltext_is_complete(self):
        self.assertEqual(self.summary["original_content_reviewed_targets"], 143)
        self.assertEqual(self.summary["no_original_content_access_blocked_targets"], 1)
        self.assertEqual(self.summary["alternative_originals_with_nominated_pointer_still_unarchived"], 7)
        self.assertFalse(self.summary["all_technical_originals_complete"])
        self.assertTrue(all(x["all_pages_human_fulltext_read_claimed"].startswith("NO_") for x in self.rows))

    def test_byte_hash_mutation_cannot_pass(self):
        row = self.byname["elaine dorothy"]
        doc = copy.deepcopy(self.documents[row["document_id"]])
        doc["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA256"):
            mod.verify_document(doc, row)

    def test_wrong_page_and_absent_claim_anchor_fail(self):
        row = copy.deepcopy(self.byname["elaine dorothy"])
        doc = self.documents[row["document_id"]]
        row["pdf_pages_or_html_sections"] = "9999"
        with self.assertRaisesRegex(ValueError, "exceeds"):
            mod.verify_document(doc, row)
        row["pdf_pages_or_html_sections"] = "1"
        row["verification_anchor"] = "THIS_NONEXISTENT_PROJECT_IS_APPROVED"
        with self.assertRaisesRegex(ValueError, "anchor absent"):
            mod.verify_document(doc, row)

    def test_spa_shell_is_not_document_content(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            path = root / mod.SNAP / "empty.html"
            path.parent.mkdir(parents=True)
            payload = b'<html><body><app-root></app-root><script>DSpace</script></body></html>'
            path.write_bytes(payload)
            doc = {"archive_path": path.relative_to(root).as_posix(), "sha256": mod.sha(payload), "format": "html"}
            row = copy.deepcopy(self.byname["stromberg"])
            row.update(document_id="EMPTY-SPA", pdf_pages_or_html_sections="HTML", verification_anchor="DSpace")
            with self.assertRaisesRegex(ValueError, "anchor absent"):
                mod.verify_document(doc, row, root=root)

    def test_kalkaroo_west_uses_correct_government_id(self):
        row = self.byname["kalkaroo west"]
        self.assertEqual(row["source_native_id"], "9629")
        self.assertEqual(row["expected_government_record_id"], "9629")
        self.assertIn("8455", row["documentary_finding"])
        altered = copy.deepcopy(row)
        altered["expected_government_record_id"] = "8455"
        with self.assertRaisesRegex(ValueError, "Wrong government"):
            mod.verify_document(self.documents[row["document_id"]], altered)

    def test_project_and_commodity_transfer_rejections(self):
        for name in ("holsteins", "stromberg", "charley creek", "benmara north"):
            self.assertEqual(self.byname[name]["terminal_documentary_disposition"], "CITED_DOCUMENT_SCOPE_TRANSFER_REJECTED")
        self.assertEqual(self.byname["browns range"]["terminal_documentary_disposition"], "CROSS_STATE_RESOURCE_TRANSFER_REJECTED")
        self.assertIn("230 Mt", self.byname["newmont"]["documentary_finding"])
        self.assertEqual(self.byname["glenmorangie"]["terminal_documentary_disposition"], "CROSS_PROJECT_RESOURCE_TRANSFER_REJECTED")

    def test_no_project_or_c1_approval_and_no_signature(self):
        self.assertTrue(all(x["C1_admitted"] == "NO" and not x["independent_approval_signature"]
                            and x["Project_approval"] == "UNCHANGED_HOLD" for x in self.rows))
        self.assertEqual(self.summary["formal_approvals_changed"], 0)
        self.assertTrue(all(x["C1_and_13_case_gate_and_MCDA"] == "PAUSED_BY_USER" for x in self.rows))

    def test_geometry_comparison_is_not_identity_approval(self):
        self.assertEqual(self.summary["coordinate_comparisons"], 61)
        self.assertGreater(float(self.byname["byfield"]["frozen_to_document_point_distance_km"]), 6)
        self.assertGreater(float(self.byname["cooljarloo"]["frozen_to_document_point_distance_km"]), 6)
        self.assertTrue(all("NOT_APPROVED" in x["coordinate_comparison_limit"] for x in self.rows))

    def test_original_table_coordinate_text_cannot_be_invented(self):
        row = copy.deepcopy(self.byname["byfield"])
        row["table_context"] = "Byfield QLD 999.000 -999.000"
        with self.assertRaisesRegex(ValueError, "Table row"):
            mod.verify_document(self.documents[row["document_id"]], row)

    def test_public_checkout_reproduces_without_restricted_originals(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            for rel in [mod.FROZEN, mod.PRIOR, mod.INPUT, mod.WEB, mod.SEALED, *mod.MANIFESTS]:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            rows, updated, summary = mod.build(root)
            self.assertEqual(rows, self.rows)
            self.assertEqual(updated, self.updated)
            self.assertEqual(summary, self.summary)

    def test_new_originals_and_web_only_limit(self):
        self.assertEqual(self.summary["original_bytes_reviewed_targets"], 142)
        self.assertEqual(self.summary["web_only_original_content_targets"], 1)
        self.assertEqual(self.byname["alluvial flats"]["document_id"], "DOC-5ab766d5fc77")
        self.assertIn("89 Mt", self.byname["alluvial flats"]["documentary_finding"])
        self.assertFalse(self.byname["scaddan"]["original_document_sha256"])
        self.assertEqual(self.byname["yellowband plain"]["original_content_review_completed"], "NO_ACCESS_BLOCKED")

    def test_synthetic_pdf_byte_and_page_guards_without_private_archive(self):
        from pypdf import PdfWriter
        with tempfile.TemporaryDirectory(dir=ROOT / "work") as temp:
            root = Path(temp)
            path = root / mod.SNAP / "synthetic.pdf"
            path.parent.mkdir(parents=True)
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            with path.open("wb") as stream:
                writer.write(stream)
            doc = {"archive_path": path.relative_to(root).as_posix(), "sha256": mod.sha(path.read_bytes()), "format": "pdf"}
            row = copy.deepcopy(self.byname["elaine dorothy"])
            row["pdf_pages_or_html_sections"] = "2"
            with self.assertRaisesRegex(ValueError, "exceeds"):
                mod.verify_document(doc, row, root=root)
            row["pdf_pages_or_html_sections"] = "1"
            with self.assertRaisesRegex(ValueError, "anchor absent"):
                mod.verify_document(doc, row, root=root)
            doc["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "SHA256"):
                mod.verify_document(doc, row, root=root)

    def test_reproduction(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts/review_p234_144_primary_scope.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
