-- Pre-MCDA census/entity linkage review only; no score, rank, or Project Master mutation.
CREATE TABLE IF NOT EXISTS census_definition_review (
  target_id TEXT PRIMARY KEY,
  cohort TEXT NOT NULL CHECK (cohort IN ('LEGACY_86','UNLINKED_E1_401')),
  state TEXT NOT NULL,
  source_name TEXT NOT NULL,
  legacy_project_id TEXT,
  candidate_id TEXT,
  source_key TEXT,
  source_native_id TEXT,
  latitude REAL,
  longitude REAL,
  coordinates_basis TEXT,
  jurisdiction_check TEXT NOT NULL,
  location_check TEXT NOT NULL,
  project_identity_check TEXT NOT NULL,
  project_linkage_check TEXT NOT NULL,
  canonical_project_candidate TEXT,
  entity_level_assessed TEXT,
  project_lifecycle_check TEXT NOT NULL,
  ree_role_check TEXT NOT NULL,
  definition_screen_status TEXT NOT NULL,
  reviewer_decision TEXT NOT NULL DEFAULT '',
  reviewer_notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS census_project_dedup_candidates (
  candidate_group_key TEXT PRIMARY KEY,
  canonical_project_candidate TEXT NOT NULL,
  candidate_observation_count INTEGER NOT NULL,
  target_ids_preserved TEXT NOT NULL,
  source_names TEXT NOT NULL,
  states TEXT NOT NULL,
  cohorts TEXT NOT NULL,
  open_review TEXT NOT NULL,
  review_decision TEXT NOT NULL DEFAULT 'PENDING'
);
CREATE TABLE IF NOT EXISTS census_tenement_evidence (
  target_id TEXT NOT NULL REFERENCES census_definition_review(target_id),
  dataset TEXT NOT NULL,
  official_title_number TEXT,
  official_holder_text TEXT,
  tenure_status_text TEXT,
  relation_status TEXT NOT NULL,
  source_url TEXT NOT NULL,
  api_response_sha256 TEXT NOT NULL,
  holder_role TEXT NOT NULL DEFAULT 'HOLDER_OR_APPLICANT_CANDIDATE',
  developer_operator_verified INTEGER NOT NULL DEFAULT 0 CHECK (developer_operator_verified IN (0,1)),
  PRIMARY KEY (target_id, dataset, official_title_number)
);
CREATE TABLE IF NOT EXISTS census_source_manifest (
  source_key TEXT PRIMARY KEY,
  source_sha256 TEXT NOT NULL,
  artifact_id TEXT,
  as_of_date TEXT,
  scope_note TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_census_review_state_status ON census_definition_review(state,definition_screen_status);
CREATE INDEX IF NOT EXISTS idx_census_title_target ON census_tenement_evidence(target_id);
