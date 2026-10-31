"""Fail closed if frozen 412-source audit or 13 C1 gates drift."""
import csv
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_p0_412_gate_continuation.py"
AUDIT = ROOT / "docs/audits"


def read(name):
    with (AUDIT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class CensusContinuationTest(unittest.TestCase):
    def test_exact_source_denominators_and_no_overlap(self):
        base = read("2026-10-31_census_487_batch_review.csv")
        hold = {r["target_id"] for r in base if r["original_inclusion_gate"] == "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"}
        p1 = {r["target_id"] for r in read("2026-10-31_p1_73_source_resolution.csv")}
        p2 = {r["target_id"] for r in read("2026-10-31_p2_28_public_terminal_desk_review.csv")}
        rows = read("2026-10-31_p3_p4_311_provenance_audit.csv")
        tail = {r["target_id"] for r in rows}
        self.assertEqual((len(hold), len(p1), len(p2), len(tail)), (412, 73, 28, 311))
        self.assertEqual(len(p1 | p2 | tail), 412)
        self.assertFalse(p1 & p2 or p1 & tail or p2 & tail)
        self.assertEqual(sum(r["priority"] == "P3" for r in rows), 216)
        self.assertEqual(sum(r["priority"] == "P4" for r in rows), 95)
        self.assertTrue(all(r["C1_gate"] == "NO" for r in rows))

    def test_c1_fail_closed(self):
        rows = read("2026-10-31_c1_13_independent_gate_readiness.csv")
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(int(r["source_target_count"]) for r in rows), 22)
        self.assertTrue(all(not r["original_primary_pdf_sha256"] and not r["independent_reviewer_signature"] for r in rows))
        self.assertTrue(all(r["C1_admitted"] == "NO" and r["final_JORC_approval"] == "NO" for r in rows))

    def test_p2_27_provisional_cases(self):
        rows = read("2026-10-31_p2_28_identity_crosswalk.csv")
        self.assertEqual(len(rows), 28)
        self.assertEqual(len({r["case_id"] for r in rows}), 27)
        self.assertEqual(sum(r["source_identity_crosswalk"].startswith("LEGACY_UUID") for r in rows), 22)
        self.assertTrue(all(r["C1_gate"] == "NO" for r in rows))

    def test_reproducible(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
