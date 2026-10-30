"""Repository layout checks: keep the canonical and frozen-workpack entrypoints available."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKPACK = ROOT / "reproducibility" / "workpack"


def test_repository_root_is_an_entrypoint_not_a_script_dump():
    for old in (
        "build_definition_review.py",
        "build_complete_proposal_workpack.py",
        "build_editable_workbook.py",
        "build_row_level_trace_bundle.py",
        "complete_487_source_review.py",
        "enrich_candidate_evidence.py",
        "reproduce_86_401_cohorts.py",
        "migration_0007_census_lineage_and_entity_queue.sql",
        "migration_0008_reproduced_cohort_selection.sql",
        "migration_0009_project_evidence_and_admission_gate.sql",
    ):
        assert not (ROOT / old).exists(), old


def test_workpack_runner_references_existing_entrypoints():
    runner = ROOT / "reproducibility" / "rebuild_all.py"
    content = runner.read_text(encoding="utf-8")
    ast.parse(content, filename=str(runner))
    script_paths = set(re.findall(r'root / "([^"]+\.py)"', content))
    expected = {
        "scripts/build_487_definition_review.py",
        "scripts/build_487_complete_proposal_workpack.py",
        "scripts/build_487_editable_workbook.py",
        "reproducibility/workpack/reproduce_86_401_cohorts.py",
        "reproducibility/workpack/enrich_candidate_evidence.py",
        "reproducibility/workpack/complete_487_source_review.py",
        "reproducibility/workpack/build_row_level_trace_bundle.py",
    }
    assert script_paths == expected
    for relative in script_paths:
        path = ROOT / relative
        assert path.is_file(), relative
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_workpack_uses_canonical_sql_migrations():
    paths = (
        ("reproduce_86_401_cohorts.py", "0008_reproduced_cohort_selection.sql"),
        ("enrich_candidate_evidence.py", "0009_project_evidence_and_admission_gate.sql"),
    )
    for script, migration in paths:
        code = (WORKPACK / script).read_text(encoding="utf-8")
        assert f'"{migration}"' in code
        assert (ROOT / "db" / "migrations" / migration).is_file()
    assert (ROOT / "db" / "migrations" / "0007_census_lineage_and_entity_queue.sql").is_file()


def test_documentation_entrypoints():
    for relative in (
        "README.md",
        "docs/README.md",
        "docs/RUNBOOK.md",
        "docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md",
        "reproducibility/workpack/README.md",
        "outputs/README.md",
        "CENSUS_RELEASE.md",
    ):
        assert (ROOT / relative).is_file(), relative
