"""Supervised parent/child pipeline: C1 default and evidence-only P2-P4."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.run_research_pipeline import build_plan, execute, read_manifest

class ParentPipelineTest(unittest.TestCase):
    def test_all_profile_defaults_to_c1_and_skips_p234_without_event(self):
        plan=build_plan("all","check")
        self.assertEqual([x["name"] for x in plan],
                         ["c0_cohort","c1_stage1","p234_event_router"])
        self.assertEqual(plan[-1]["action"],"SKIP_NO_NEW_EVIDENCE")
        self.assertEqual(len([x for x in plan if x["action"]=="EXECUTE"]),2)
        self.assertNotIn("run_mcda.R",str(plan))
    def test_p234_explicit_profile_has_no_repeated_searches(self):
        summary=execute("p234","check",dry_run=True)
        self.assertEqual(summary["stages"][0]["action"],"SKIP_NO_NEW_EVIDENCE")
    def test_write_mode_invokes_correct_child_commands_without_uncontrolled_shell(self):
        plan=build_plan("c1","write")
        self.assertEqual(len(plan),2)
        self.assertTrue(all(p["command"][-1]=="--write" for p in plan))
    def test_new_evidence_event_triggers_router(self):
        cfg=read_manifest()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            file=root/cfg["stages"]["p234_event_router"]["trigger_input"]
            file.parent.mkdir(parents=True)
            file.write_text("event_id,target_id\nEV-P234-TEST01,example\n",encoding="utf-8")
            decision=root/cfg["stages"]["p234_event_router"]["review_decisions_input"]
            decision.parent.mkdir(parents=True)
            decision.write_text("event_id,review_status\n",encoding="utf-8")
            script=root/cfg["stages"]["p234_event_router"]["script"]
            script.parent.mkdir(parents=True)
            script.touch()
            plan=build_plan("p234","check",root=root,manifest=cfg)
            self.assertEqual(plan[0]["action"],"EXECUTE")
            self.assertEqual(plan[0]["command"][-1],"--check")
            decision.write_text("event_id,review_status\nEV-P234-TEST01,SOURCE_SCOPE_REVIEWED\n",encoding="utf-8")
            second=build_plan("p234","check",root=root,manifest=cfg)
            self.assertEqual(second[0]["action"],"SKIP_NO_NEW_EVIDENCE")
    def test_zero_external_approvals_and_unknown_profile_rejected(self):
        self.assertEqual(execute("all","check",dry_run=True)["C1_automatic_admissions"],0)
        with self.assertRaises(ValueError):
            build_plan("automatic-live-ree-mcda","write")

if __name__=="__main__":
    unittest.main()
