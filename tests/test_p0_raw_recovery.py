"""P0 original raw recovery must preserve every source identity and Gate."""
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p0_raw", ROOT / "scripts" / "validate_p0_raw_recovery.py")
assert spec and spec.loader
M = module_from_spec(spec)
spec.loader.exec_module(M)


def test_original_source_provenance_targets():
    scope, missing, sa = M.validate_registry(ROOT)
    assert len(scope) == 272
    assert len(missing) == 23
    assert len(sa) == 10
    assert len({x["target_id"] for x in scope}) == 272
    assert Counter(x["raw_feature_cardinality"] for x in scope) == {"1": 272}
    assert all(x["project_parent_approved"] == "NO" for x in scope)


def test_two_distinct_nature_of_original_recovery():
    _, missing, sa = M.validate_registry(ROOT)
    assert sum("ORIGINAL_GA" in x["recovery_kind"] for x in missing) == 7
    assert sum("LEGACY_ORIGINAL_ROW_AND_ID_RECOVERED" == x["recovery_kind"] for x in missing) == 16
    assert all(x["project_parent_approval"] == "NO" for x in missing)
    # Archived Legacy UUID is real within the historical census, but not a government ID.
    assert all(x["original_source_native_id_status"] ==
               "ORIGINAL_LEGACY_PROJECT_ID_EXACT_MATCH"
               for x in missing if x["source_category"] == "LEGACY")
    assert Counter(x["mineral_deposit_no"] for x in sa) == {"3000": 4, "11849": 6}
    assert len({x["source_feature_key"] for x in sa}) == 10
    assert len({x["source_objectid"] for x in sa}) == 10


def test_provider_parent_is_not_registered_project_parent():
    scope, _, _ = M.validate_registry(ROOT)
    assert Counter(x["native_parent_key_type"] for x in scope) == {
        "NO_PROJECT_PARENT_KEY_IN_NATIVE_RECORD": 268,
        "GEOLOGICAL_GROUP_NAME_ONLY": 2,
        "GEOLOGICAL_PARENT_ID_ONLY": 2,
    }
    assert {x["source_name"] for x in scope
            if x["native_parent_key_type"] !=
            "NO_PROJECT_PARENT_KEY_IN_NATIVE_RECORD"} == {
        "MILO", "FLORENCE BORE SOUTH, TARGET 1",
        "Livingstone Creek A", "Leach Scrub",
    }


def test_archived_raw_if_present():
    path = os.environ.get("AU_REE_RAW_ARCHIVE_ROOT")
    if path:
        scope, missing, sa = M.validate_registry(ROOT)
        result = M.verify_archive(Path(path), scope, missing, sa)
        assert result["scoped_targets_verified"] == 272
        assert result["ga_originals_verified"] == 7
        assert result["sa_duplicate_feature_ids_verified"] == 10
