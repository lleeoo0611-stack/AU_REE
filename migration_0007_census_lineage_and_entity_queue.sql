-- Additive extensions to migration 0006. These are source and review ledgers only.
-- No project master mutation, ranking, or scoring is performed.
CREATE TABLE IF NOT EXISTS census_reconstructed_candidate_ledger (
  candidate_id TEXT PRIMARY KEY,
  source_key TEXT NOT NULL,
  native_id TEXT,
  state TEXT NOT NULL,
  source_name TEXT NOT NULL,
  tier TEXT,
  cohort_membership TEXT NOT NULL DEFAULT 'NOT_IN_FIXED_487',
  original_selection_reason TEXT NOT NULL DEFAULT 'NOT_RECOVERED',
  evidence_decision TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
  raw_record_sha256 TEXT
);
CREATE TABLE IF NOT EXISTS census_exact_name_cluster_candidates (
  cluster_key TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  member_count INTEGER NOT NULL,
  member_ids TEXT NOT NULL,
  candidate_only INTEGER NOT NULL DEFAULT 1 CHECK (candidate_only=1),
  reviewer_decision TEXT NOT NULL DEFAULT 'PENDING'
);
CREATE TABLE IF NOT EXISTS census_legacy_exact_crosswalk_review (
  target_id TEXT PRIMARY KEY,
  legacy_project_id TEXT NOT NULL,
  exact_match_count INTEGER NOT NULL,
  candidate_source_ids TEXT NOT NULL,
  match_status TEXT NOT NULL,
  match_basis TEXT NOT NULL DEFAULT 'EXACT_NORMALIZED_STATE_NAME_ONLY',
  reviewer_decision TEXT NOT NULL DEFAULT 'PENDING'
);
CREATE TABLE IF NOT EXISTS census_company_entity_resolution_queue (
  target_id TEXT PRIMARY KEY REFERENCES census_definition_review(target_id),
  holder_or_applicant_text TEXT,
  developer_text TEXT,
  operator_text TEXT,
  legal_entity_name TEXT,
  acn TEXT,
  asx_ticker TEXT,
  historical_name TEXT,
  effective_from TEXT,
  effective_to TEXT,
  transfer_or_name_change_basis TEXT,
  primary_source_url TEXT,
  primary_source_sha256 TEXT,
  resolution_status TEXT NOT NULL DEFAULT 'PENDING_PRIMARY_SOURCE_REVIEW',
  reviewer_decision TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS census_state_source_coverage (
  jurisdiction TEXT PRIMARY KEY,
  survey_source_status TEXT NOT NULL,
  tenure_source_status TEXT NOT NULL,
  source_url TEXT,
  snapshot_date TEXT,
  coverage_limit TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS census_missing_upstream_inputs (
  file_name TEXT PRIMARY KEY,
  expected_role TEXT NOT NULL,
  recovery_status TEXT NOT NULL,
  reconstruction_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS census_five_condition_rules (
  condition_number INTEGER PRIMARY KEY CHECK (condition_number BETWEEN 1 AND 5),
  condition_name TEXT NOT NULL,
  pass_rule TEXT NOT NULL,
  hold_rule TEXT NOT NULL,
  required_evidence TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_census_candidate_state_name ON census_exact_name_cluster_candidates(state,normalized_name);
CREATE INDEX IF NOT EXISTS idx_census_company_status ON census_company_entity_resolution_queue(resolution_status);
