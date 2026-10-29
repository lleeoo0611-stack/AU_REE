-- Source-backed candidate evidence and explicit pre-MCDA admission gate.
-- A candidate disposition is a review state, not an automatic census decision.
CREATE TABLE IF NOT EXISTS census_project_candidate_evidence (
  candidate_group_key TEXT PRIMARY KEY,
  canonical_project_unit TEXT NOT NULL,
  project_identity_status TEXT NOT NULL,
  ree_role_status TEXT NOT NULL,
  stage_status TEXT NOT NULL,
  inclusion_gate TEXT NOT NULL CHECK (inclusion_gate IN ('INCLUDE_CANDIDATE','HOLD','EXCLUDE')),
  evidence_urls TEXT NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS census_project_inclusion_gate (
  target_id TEXT PRIMARY KEY,
  cohort TEXT NOT NULL,
  state TEXT NOT NULL,
  candidate_group_key TEXT NOT NULL DEFAULT '',
  inclusion_gate TEXT NOT NULL CHECK (inclusion_gate IN ('INCLUDE_CANDIDATE','HOLD','EXCLUDE')),
  dedup_relation TEXT NOT NULL,
  evidence_urls TEXT NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS census_project_inclusion_gate_rules (
  rule_id TEXT PRIMARY KEY,
  minimum_threshold TEXT NOT NULL,
  effect TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_census_project_gate_status ON census_project_inclusion_gate(inclusion_gate,state);

