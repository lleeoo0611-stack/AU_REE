-- Additive audit tables for reproduced 86 + 401 cohort selection.
-- Selection rows and candidate links remain review evidence, not project approvals.
CREATE TABLE IF NOT EXISTS census_cohort_selection_run (
  metric TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  section TEXT NOT NULL,
  run_timestamp_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS census_cohort_selection_decision (
  cohort TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  selected INTEGER NOT NULL CHECK (selected IN (0,1)),
  selection_rule TEXT NOT NULL,
  selection_disposition TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  PRIMARY KEY (cohort, source_record_id)
);
CREATE TABLE IF NOT EXISTS census_reconstructed_target_cohort (
  target_id TEXT PRIMARY KEY,
  cohort TEXT NOT NULL,
  candidate_id TEXT,
  legacy_project_id TEXT,
  selection_rule_reproduced INTEGER NOT NULL CHECK (selection_rule_reproduced IN (0,1)),
  crosswalk_status TEXT NOT NULL,
  provisional_group_ids TEXT NOT NULL DEFAULT '',
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_census_cohort_selected ON census_cohort_selection_decision(cohort, selected);

