"""Acceptance and adversarial tests for frozen source documentary dispositions."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("closeout", ROOT / "scripts/closeout_p2_p3_p4.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DocumentaryCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.details, cls.summary = mod.build()
        cls.base, cls.targets, _, _ = mod.scope()

    def test_exact_immutable_partition(self):
        self.assertEqual(Counter(x["priority"] for x in self.rows), {"P2": 28, "P3": 216, "P4": 95})
        self.assertEqual({x["target_id"] for x in self.rows}, set(self.targets))
        self.assertEqual(len(self.rows), 339)
        self.assertEqual(len({x["case_id"] for x in self.rows if x["priority"] == "P2"}), 27)
        self.assertTrue(all(x["baseline_entity_type"] == "OCCURRENCE" for x in self.rows if x["priority"] == "P4"))

    def test_government_and_legacy_scope_separate(self):
        self.assertEqual(sum(x["target_id"].startswith("LEGACY:") for x in self.rows), 52)
        self.assertEqual(sum(not x["source_key"] for x in self.rows), 22)
        self.assertTrue(all(x["source_inspection"] == "LEGACY_UUID_ROW_VERIFIED_NOT_GOVERNMENT_ID"
                            for x in self.rows if not x["source_key"]))
        self.assertEqual(sum(x["source_inspection"] == "ORIGINAL_GOVERNMENT_FEATURE_CONTENT_INSPECTED" for x in self.rows), 317)
        self.assertTrue(all(x["C1_admitted"] == "NO" and x["Project_approval"] == "UNCHANGED_HOLD"
                            and not x["original_technical_document_sha256"]
                            and x["technical_primary_fulltext_verified_this_run"] == "NO" for x in self.rows))

    def test_raw_recovery_supersedes_stale_round2_only_in_new_output(self):
        ga = [x for x in self.rows if x["source_name"] in {"Gascoyne", "Rodds Peninsula", "Inskip Point",
              "Round Hill Head/Deepwater", "Thunderbird", "Wild Cattle Island-Hummock Hill", "Hat Head"}
              and x["source_key"] == "GA_AIMR_REE_2026"]
        self.assertEqual(len(ga), 7)
        self.assertTrue(all(x["source_id_disposition"] == "EXACT_NATIVE_FEATURE_RETAINED" for x in ga))

    def test_sa_multiple_features_not_collapsed_or_counted_as_projects(self):
        sa = [x for x in self.details if x["source_key"] == "SA_CRITICAL_REE" and x["source_native_id"] in {"3000", "11849"}]
        self.assertEqual(sorted(x["native_feature_count"] for x in sa), ["4", "6"])
        for x in sa:
            altered = copy.deepcopy(x["selected_source"])
            altered["features"] = altered["features"][:1]
            with self.assertRaisesRegex(ValueError, "cardinality"):
                mod.validate_selected(altered, self.base[x["target_id"]])

    def test_wrong_native_and_legacy_ids_rejected(self):
        for x in [self.details[0], next(x for x in self.details if x["target_id"].startswith("LEGACY:"))]:
            altered = copy.deepcopy(x["selected_source"])
            if x["target_id"].startswith("LEGACY:"):
                altered["legacy_original_row"]["project_id"] = "wrong"
            else:
                key = mod.ARC.get(x["source_key"]) or mod.WFS.get(x["source_key"]) or "MINERAL_DEPOSIT_NO"
                altered["features"][0]["attributes"][key] = "wrong"
            with self.assertRaises(ValueError):
                mod.validate_selected(altered, self.base[x["target_id"]])

    def test_same_name_is_not_project_identity(self):
        peers = [x for x in self.rows if json.loads(x["same_state_exact_name_target_ids_json"])]
        self.assertTrue(peers)
        self.assertTrue(all(x["duplicate_disposition"] == "REVIEW_ONLY_NO_NAME_OR_PROXIMITY_MERGE" for x in peers))

    def test_native_url_not_misrepresented_as_external_document(self):
        events = [{"record": {"official_source_url": "https://official.invalid/native"}}]
        self.assertEqual(mod.classify("P4", {}, events), "C0_NATIVE_RECORD_REVIEW_COMPLETE_PROJECT_UNRESOLVED")
        events.append({"record": {"source_document_url": "https://official.invalid/report.pdf"}})
        self.assertEqual(mod.classify("P4", {}, events), "HOLD_DOCUMENT_POINTER_REQUIRES_PRIMARY_SCOPE_REVIEW")

    def test_complete_history_and_reopen_conditions(self):
        for x in self.details:
            self.assertTrue(x["documentary_history"])
            self.assertEqual(x["documentary_history"][0]["path"], mod.R2)
            self.assertTrue(x["remaining_gap_and_reopen_condition"])
            self.assertEqual(x["evidence_sufficient_for_project_approval"], "NO")
        self.assertEqual(self.summary["counts"]["new_technical_primary_fulltext_verifications"], 0)

    def test_reproduction(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts/closeout_p2_p3_p4.py"), "--check"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_changed_selection_bytes_fail_before_reading_review_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for rel in (mod.BASE, mod.P1, mod.P2, mod.SNAP, mod.MANIFEST):
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / rel).read_bytes())
            with (root / mod.SNAP).open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(ValueError, "checksum"):
                mod.build(root)


if __name__ == "__main__":
    unittest.main()
