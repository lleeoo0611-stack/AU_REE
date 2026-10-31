"""109-source Project-parent evidence review; strict science and frozen corpus gates."""
import csv
import unittest
from pathlib import Path
from importlib.util import module_from_spec,spec_from_file_location

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("p0_109",ROOT/"scripts/audit_p0_109_project_parents.py")
mod=module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

class Review109(unittest.TestCase):
    def test_full_source_corpus_preservation(self):
        rows,stats=mod.build(ROOT)
        self.assertEqual(len(rows),109)
        self.assertEqual(len({x["target_id"] for x in rows}),109)
        self.assertEqual(stats["source_target_count"],109)
        self.assertEqual(sum(stats["state_distribution"].values()),109)
        self.assertTrue(all(x["source_original_chunk_sha256"] and
                            x["source_native_feature_locator"] for x in rows))
    def test_new_document_no_approval_or_TREO_inference(self):
        rows,stats=mod.build(ROOT)
        self.assertEqual(stats["new_document_register_unique_names"],31)
        self.assertGreaterEqual(stats["new_document_target_rows"],31)
        self.assertEqual(stats["project_ID_signoffs"],0)
        self.assertEqual(stats["JORC_REO_signoffs"],0)
        self.assertEqual(stats["C1_release_count"],0)
        self.assertTrue(all(x["independent_project_identity_approved"]=="NO" and
                            x["JORC_REO_approved"]=="NO" and
                            x["C1_approved"]=="NO" and
                            x["same_name_is_project_proof"]=="NO" for x in rows))
    def test_distinguish_historical_parent_from_geological_only(self):
        rows,_=mod.build(ROOT)
        byname={}
        for x in rows:byname.setdefault((x["state"],x["source_name"]),[]).append(x)
        self.assertEqual(len(byname[("WA","Yttria")]),2)
        self.assertEqual(len(byname[("WA","Mia")]),2)
        self.assertTrue(all(x["parent_project_candidate"]=="Mt Stirling Project (Yttria REE Deposit)"
                            for x in byname[("WA","Yttria")]))
        self.assertTrue(all(x["project_parent_claim_status"]=="DOCUMENTED_HISTORICAL_PARENT_CANDIDATE"
                            for x in byname[("WA","Happy Valley North")]))
        self.assertEqual(byname[("NSW","Birthday Gift")][0]["project_parent_claim_status"],
                         "HISTORICAL_GROUP_PARENT_CANDIDATE")
        self.assertEqual(byname[("WA","Scott River")][0]["project_parent_claim_status"],
                         "SCOPE_OR_TENEMENT_ONLY_HOLD")
        self.assertTrue(all(x["project_parent_claim_status"]=="INDEPENDENT_DEPOSIT_DOCUMENT_NO_PROJECT_PARENT"
                            for x in byname[("NSW","Gallipoli")]))
    def test_frozen_csv_exact_rerun(self):
        p=ROOT/mod.OUTPUT
        if not p.exists():
            self.skipTest("Publication snapshot generated in P0 evidence workflow")
        rows,_=mod.build(ROOT)
        with p.open(newline="",encoding="utf-8") as f:
            self.assertEqual(list(csv.DictReader(f)),rows)

if __name__=="__main__":
    unittest.main()
