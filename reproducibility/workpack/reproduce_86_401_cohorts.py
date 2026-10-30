#!/usr/bin/env python3
"""Reproduce the recorded 86 + 401 cohort rules and compare to the frozen 487 list.

The rules are reconstructed from the retained 2026-10-29 ChatGPT conversation and
the source ledgers produced by the merged AU_REE PR #4 generator. The fixed 487
target list is used only as a comparison key, not as the selection input.
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import re
import sqlite3
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "reconstructed_from_chatgpt_artifact"
TRACE_TARGETS = ROOT / "trace_artifact" / "inputs" / "reverse_trace_targets_487.csv"
PRESERVED_TARGETS = ROOT / "input_targets_487_preserved.csv"
OUT = ROOT / "deliverable"


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def split_ids(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def load_sqlite_audit() -> None:
    db = OUT / "census_review.sqlite"
    migration = ROOT / "db" / "migrations" / "0008_reproduced_cohort_selection.sql"
    if not db.exists():
        return
    with sqlite3.connect(db) as conn:
        conn.executescript(migration.read_text(encoding="utf-8-sig"))
        conn.execute("DELETE FROM census_cohort_selection_run")
        conn.execute("DELETE FROM census_cohort_selection_decision")
        conn.execute("DELETE FROM census_reconstructed_target_cohort")
        summary = json.loads((OUT / "cohort_reproduction_summary.json").read_text(encoding="utf-8"))
        flat = []
        for section in ("counts", "comparison_to_frozen_target_list", "source_hashes"):
            for key, value in summary[section].items():
                flat.append((f"{section}.{key}", json.dumps(value, ensure_ascii=False), section))
        for cohort, values in summary["state_counts"].items():
            for state, value in values.items():
                flat.append((f"state_counts.{cohort}.{state}", str(value), "state_counts"))
        for i, value in enumerate(summary["limitations"], 1):
            flat.append((f"limitations.{i}", value, "limitations"))
        conn.executemany("INSERT INTO census_cohort_selection_run(metric,value,section) VALUES (?,?,?)", flat)
        for filename, cohort, id_field in (
            ("legacy_203_selection_audit.csv", "LEGACY_203", "project_id"),
            ("source_candidate_selection_audit_1006.csv", "SOURCE_1006", "candidate_id"),
        ):
            for row in read_csv(OUT / filename):
                selected_field = "cohort_86_selected" if cohort == "LEGACY_203" else "cohort_401_selected"
                conn.execute(
                    "INSERT INTO census_cohort_selection_decision(cohort,source_record_id,selected,selection_rule,selection_disposition,payload_json) VALUES (?,?,?,?,?,?)",
                    (cohort, row[id_field], int(row[selected_field] == "YES"), row["cohort_selection_rule"], row["selection_disposition"], json.dumps(row, ensure_ascii=False)),
                )
        for row in read_csv(OUT / "reconstructed_cohort_487.csv"):
            conn.execute(
                "INSERT INTO census_reconstructed_target_cohort(target_id,cohort,candidate_id,legacy_project_id,selection_rule_reproduced,crosswalk_status,provisional_group_ids,payload_json) VALUES (?,?,?,?,?,?,?,?)",
                (row["target_id"], row["cohort"], row.get("candidate_id", ""), row.get("legacy_project_id", ""), int(row["selection_rule_reproduced"] == "YES"), row["crosswalk_status"], row.get("provisional_group_ids", ""), json.dumps(row, ensure_ascii=False)),
            )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    provisional = read_csv(ART / "provisional_project_groups_126.csv")
    legacy = read_csv(ART / "legacy_203_crosswalk_audit.csv")
    all_candidates = read_csv(ART / "all_1006_evidence_decisions.csv")
    e1_unlinked = read_csv(ART / "E1_project_unlinked_review_queue.csv")
    frozen = read_csv(TRACE_TARGETS)
    preserved = read_csv(PRESERVED_TARGETS)

    # Legacy rule: historical 203 records not crosswalked to the 126 provisional
    # groups. Crosswalk keys are supplied by WA parent-code relations, exact SA
    # government project/deposit relations, exact Dubbo, and the documented
    # Nolans Bore -> Nolans alias. No fuzzy-name linkage is used.
    provisional_to_legacy: dict[str, list[str]] = defaultdict(list)
    for p in provisional:
        for project_id in split_ids(p.get("legacy_project_ids", "")):
            provisional_to_legacy[project_id].append(p["provisional_group_id"])
    matched_legacy_ids = set(provisional_to_legacy)
    legacy_by_id = {r["project_id"]: r for r in legacy}
    assert len(legacy) == 203 and len(legacy_by_id) == 203
    assert len(provisional) == 126
    assert len(matched_legacy_ids) == 117, f"Expected recorded 117 crosswalk IDs, got {len(matched_legacy_ids)}"
    legacy_selected = [r for r in legacy if r["project_id"] not in matched_legacy_ids]
    assert len(legacy_selected) == 86

    legacy_audit = []
    for r in legacy:
        group_ids = provisional_to_legacy.get(r["project_id"], [])
        selected = not group_ids
        legacy_audit.append({
            **r,
            "provisional_126_group_ids": ";".join(sorted(group_ids)),
            "cohort_86_selected": "YES" if selected else "NO",
            "cohort_selection_rule": "LEGACY_203_MINUS_IDS_CROSSWALKED_TO_PROVISIONAL_126",
            "selection_disposition": "LEGACY_NONOVERLAP_SELECTED" if selected else "MATCHED_TO_PROVISIONAL_126_NOT_SELECTED",
        })
    write_csv(OUT / "legacy_203_selection_audit.csv", legacy_audit)

    # E1 rule: every source candidate classed E1_DIRECT_REE and E1_MISSING_PROJECT_LINK
    # by the PR #4 stage gate. This yields 401 records: 803 E1 - 399 WA parent-coded
    # site rows - 3 SA government Project rows. E2/E3 remain in extended inventory.
    candidate_by_id = {r["candidate_id"]: r for r in all_candidates}
    unlinked_ids = {r["candidate_id"] for r in e1_unlinked}
    assert len(all_candidates) == 1006 and len(candidate_by_id) == 1006
    assert len(e1_unlinked) == 401 and len(unlinked_ids) == 401
    assert all(candidate_by_id[c]["tier"] == "E1_DIRECT_REE" for c in unlinked_ids)
    assert all(candidate_by_id[c]["decision"] == "E1_MISSING_PROJECT_LINK" for c in unlinked_ids)

    e1_audit = []
    for r in all_candidates:
        selected = r["candidate_id"] in unlinked_ids
        if selected:
            reason = "E1_DIRECT_REE_WITHOUT_OFFICIAL_PROJECT_OR_WA_PARENT_KEY"
        elif r["tier"] != "E1_DIRECT_REE":
            reason = "E2_E3_EXTENDED_GEOLOGICAL_INVENTORY"
        elif r["decision"] == "OFFICIAL_PARENT_PROJECT_CANDIDATE":
            reason = "WA_MINDEX_OFFICIAL_PARENT_CODE_GROUPED"
        elif r["decision"] == "GOVERNMENT_NAMED_PROJECT":
            reason = "SA_OFFICIAL_GOVERNMENT_PROJECT_ROW"
        else:
            reason = "OTHER_STAGE_GATE_DISPOSITION_REVIEW"
        e1_audit.append({
            **r,
            "cohort_401_selected": "YES" if selected else "NO",
            "cohort_selection_rule": "E1_DIRECT_REE_AND_E1_MISSING_PROJECT_LINK",
            "selection_disposition": reason,
        })
    write_csv(OUT / "source_candidate_selection_audit_1006.csv", e1_audit)

    # Compare reconstructed membership against both preserved copies of the fixed
    # list. Retain the original target_id only after the source key independently
    # reproduces cohort membership.
    targets = frozen
    assert len(targets) == 487 and len({r["target_id"] for r in targets}) == 487
    target_legacy_ids = {r["legacy_project_id"] for r in targets if r["cohort"] == "LEGACY_86"}
    expected_legacy_ids = {r["project_id"] for r in legacy_selected}
    target_e1_ids = {r["candidate_id"] for r in targets if r["cohort"] == "UNLINKED_E1_401"}
    expected_e1_ids = unlinked_ids
    assert target_legacy_ids == expected_legacy_ids, (
        f"Legacy membership differs: missing={len(expected_legacy_ids-target_legacy_ids)} extra={len(target_legacy_ids-expected_legacy_ids)}")
    assert target_e1_ids == expected_e1_ids, (
        f"E1 membership differs: missing={len(expected_e1_ids-target_e1_ids)} extra={len(target_e1_ids-expected_e1_ids)}")
    preserved_keys = {(r["target_id"], r["cohort"], r["candidate_id"], r["legacy_project_id"]) for r in preserved}
    frozen_keys = {(r["target_id"], r["cohort"], r["candidate_id"], r["legacy_project_id"]) for r in frozen}
    assert len(preserved) == 487 and preserved_keys == frozen_keys

    reconstructed = []
    target_by_candidate = {r["candidate_id"]: r for r in targets if r["cohort"] == "UNLINKED_E1_401"}
    target_by_legacy = {r["legacy_project_id"]: r for r in targets if r["cohort"] == "LEGACY_86"}
    for r in legacy_selected:
        t = target_by_legacy[r["project_id"]]
        reconstructed.append({
            **t,
            "selection_rule_reproduced": "YES",
            "selection_basis": "LEGACY_203_MINUS_117_IDS_LINKED_TO_PROVISIONAL_126",
            "crosswalk_status": "NO_126_LINK; " + ("HAS_1006_SOURCE_CROSSWALK" if int(r["matched_1006_source_records"]) > 0 else "NO_DIRECT_1006_NAME_OR_PARENT_MATCH"),
            "provisional_group_ids": "",
        })
    for cid in sorted(unlinked_ids):
        t = target_by_candidate[cid]
        c = candidate_by_id[cid]
        # Provisional evidence crosswalks are surfaced as review clues only.
        pids = sorted({p["provisional_group_id"] for p in provisional
                       if cid in split_ids(p.get("source_candidate_ids", ""))
                       or p.get("official_project_code", "") == c.get("wa_project_code", "") and c.get("wa_project_code", "")})
        if not pids:
            alias_key = c.get("external_verified_example_project", "")
            alias_map = {"Koppamurra": "Koppamurra", "Wudinna": "Wudinna", "Nolans": "Nolans", "Dubbo": "Dubbo Project"}
            candidate_names = {alias_map[alias_key]} if alias_key in alias_map else set()
            pids = sorted(p["provisional_group_id"] for p in provisional if p["project_name_candidate"] in candidate_names)
        legacy_candidates = split_ids(c.get("legacy_exact_ids", "")) + split_ids(c.get("legacy_parent_ids", ""))
        reconstructed.append({
            **t,
            "selection_rule_reproduced": "YES",
            "selection_basis": "E1_DIRECT_REE_AND_E1_MISSING_PROJECT_LINK",
            "crosswalk_status": ";".join([
                "SOURCE_RECORD_RETAINED",
                "PROVISIONAL_126_CROSSWALK_CANDIDATE" if pids else "NO_126_CROSSWALK_ESTABLISHED",
                "LEGACY_203_CROSSWALK_CANDIDATE" if legacy_candidates else "NO_EXACT_LEGACY_NAME_OR_WA_PARENT_LINK",
            ]),
            "provisional_group_ids": ";".join(pids),
        })
    reconstructed.sort(key=lambda r: (r["cohort"], r["state"], r["target_id"]))
    assert len(reconstructed) == 487
    write_csv(OUT / "reconstructed_cohort_487.csv", reconstructed)

    # Explain the 86 legacy non-overlap subset more finely: 43 have a direct/parent
    # source crosswalk in the 1006 inventory but no 126 group; 43 have none.
    legacy_nonoverlap_status = Counter(
        "HAS_1006_SOURCE_CROSSWALK" if int(r["matched_1006_source_records"]) > 0 else "NO_1006_SOURCE_CROSSWALK"
        for r in legacy_selected)
    assert legacy_nonoverlap_status == {"HAS_1006_SOURCE_CROSSWALK": 43, "NO_1006_SOURCE_CROSSWALK": 43}
    state_counts = {
        cohort: dict(Counter(r["state"] for r in targets if r["cohort"] == cohort))
        for cohort in ("LEGACY_86", "UNLINKED_E1_401")
    }
    summary = {
        "scope": "reproduce cohort selection only; census/entity review continues; no MCDA",
        "selection_rules": {
            "legacy_86": "The 203-row r963 frozen historical list minus the 117 Project IDs crosswalked to the 126 provisional-group list. Crosswalk basis recorded as WA parent-code/name, exact SA government project row, exact NSW Dubbo, and the documented NT Nolans Bore -> Nolans alias.",
            "unlinked_e1_401": "Among 1,006 candidates, retain tier E1_DIRECT_REE with decision E1_MISSING_PROJECT_LINK. This is 803 E1 minus 399 WA MINEDEX parent-coded site records and 3 SA official Project rows. E2/E3 remain extended geological inventory.",
        },
        "counts": {
            "legacy_203": len(legacy), "provisional_groups_126": len(provisional),
            "legacy_ids_linked_to_126": len(matched_legacy_ids), "legacy_nonoverlap_86": len(legacy_selected),
            "legacy_86_with_1006_source_crosswalk_but_not_126": legacy_nonoverlap_status["HAS_1006_SOURCE_CROSSWALK"],
            "legacy_86_without_1006_source_crosswalk": legacy_nonoverlap_status["NO_1006_SOURCE_CROSSWALK"],
            "national_candidates_1006": len(all_candidates), "E1_records": sum(r["tier"] == "E1_DIRECT_REE" for r in all_candidates),
            "wa_parent_coded_e1_source_records": sum(r["decision"] == "OFFICIAL_PARENT_PROJECT_CANDIDATE" for r in all_candidates),
            "sa_official_project_e1_records": sum(r["decision"] == "GOVERNMENT_NAMED_PROJECT" for r in all_candidates),
            "unlinked_e1_401": len(e1_unlinked), "combined_reconstructed_cohort": len(reconstructed),
        },
        "state_counts": state_counts,
        "comparison_to_frozen_target_list": {
            "legacy_membership_exact": target_legacy_ids == expected_legacy_ids,
            "e1_membership_exact": target_e1_ids == expected_e1_ids,
            "both_487_target_copies_exact": preserved_keys == frozen_keys,
            "all_target_ids_retained": len({r["target_id"] for r in reconstructed}) == 487,
        },
        "source_hashes": {
            "legacy_203_crosswalk_audit.csv": sha(ART / "legacy_203_crosswalk_audit.csv"),
            "provisional_project_groups_126.csv": sha(ART / "provisional_project_groups_126.csv"),
            "all_1006_evidence_decisions.csv": sha(ART / "all_1006_evidence_decisions.csv"),
            "E1_project_unlinked_review_queue.csv": sha(ART / "E1_project_unlinked_review_queue.csv"),
            "fixed_487_targets": sha(TRACE_TARGETS),
            "screening_zip": sha(ROOT / "scheme-a-screening-review.zip"),
            "raw_inventory_zip": sha(ROOT / "national-raw-inventory.zip"),
        },
        "limitations": [
            "Four historical ChatGPT files were regenerated; the earlier sandbox ZIP bytes are unavailable, so this is a reproducible reconstruction rather than a byte-identical restoration.",
            "126 groups are provisional. Membership in the 86+401 research queue does not assert that a row is an independent REE mining project.",
            "The 43 legacy source crosswalks are record/parent clues, not automatic project merges. The other 43 remain unresolved against the 1006 inventory.",
            "Exact membership reproduction establishes the recorded selection rule against the frozen 487 target list; it does not establish completeness of the broader Australian Project Census.",
        ],
    }
    (OUT / "cohort_reproduction_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "REPRODUCED_86_401_SELECTION_RULES.md").write_text(
        "# Reproduced 86 + 401 cohort selection\n\n"
        "## Reconstructed rules\n\n"
        "1. **Legacy 86:** take the 203-row historical r963 list and remove the 117 project IDs crosswalked to the 126 provisional groups. The recorded links comprise 112 WA parent groups, 3 SA official project records, NSW Dubbo, and the documented NT Nolans Bore → Nolans alias. The remaining 86 split into 43 with a 1,006-source crosswalk clue but no 126 group and 43 without a direct 1,006 crosswalk.\n"
        "2. **Unlinked E1 401:** take the 1,006 candidate ledger and select `tier=E1_DIRECT_REE` plus `decision=E1_MISSING_PROJECT_LINK`. This leaves 401 after 399 WA MINEDEX parent-coded records and 3 SA government Project rows are assigned direct source-level structure. The E1 set includes some records that can later be linked to known projects; ‘unlinked’ describes the source-layer linkage state at selection time.\n\n"
        "## Validation\n\n"
        "The reconstructed legacy IDs and E1 candidate IDs match the frozen 487 target list exactly. See `cohort_reproduction_summary.json` for state counts, input hashes, exact set comparisons, and limits. `legacy_203_selection_audit.csv`, `source_candidate_selection_audit_1006.csv`, and `reconstructed_cohort_487.csv` preserve row-level decisions.\n\n"
        "This restores the documented selection logic; it does not prove that the 86+401 set is the complete Australian REE project census or that every selected row is an independent project. No MCDA was run.\n",
        encoding="utf-8")
    load_sqlite_audit()
    print(json.dumps({"counts": summary["counts"], "state_counts": state_counts,
                      "comparison": summary["comparison_to_frozen_target_list"],
                      "legacy86_crosswalk_split": dict(legacy_nonoverlap_status)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
