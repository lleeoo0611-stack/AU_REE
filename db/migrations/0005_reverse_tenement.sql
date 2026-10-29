-- Read-only tenure / company / project evidence, separate from Project Master approvals.
-- All entities retain original source IDs and source SHA256.
CREATE TABLE IF NOT EXISTS reverse_trace_targets (
 target_id TEXT PRIMARY KEY,
 cohort TEXT NOT NULL CHECK (cohort IN ('LEGACY_86','UNLINKED_E1_401')),
 state TEXT NOT NULL,
 record_name TEXT NOT NULL,
 legacy_project_id TEXT,
 source_candidate_id TEXT,
 latitude REAL,
 longitude REAL,
 coordinate_basis TEXT,
 trace_outcome TEXT NOT NULL,
 reviewed_project_id TEXT,
 review_decision TEXT NOT NULL DEFAULT 'PENDING'
);
CREATE TABLE IF NOT EXISTS reverse_tenement_observations (
 evidence_id TEXT PRIMARY KEY,
 target_id TEXT NOT NULL REFERENCES reverse_trace_targets(target_id),
 source_layer TEXT NOT NULL,
 tenement_number TEXT,
 title_type TEXT,
 title_status TEXT,
 status_class TEXT,
 registered_holder_text TEXT,
 source_url TEXT NOT NULL,
 source_response_sha256 TEXT NOT NULL,
 holder_role TEXT NOT NULL DEFAULT 'TENEMENT_HOLDER_CANDIDATE',
 project_role_verified INTEGER NOT NULL DEFAULT 0 CHECK (project_role_verified IN (0,1))
);
CREATE TABLE IF NOT EXISTS reverse_project_document_evidence (
 evidence_id TEXT PRIMARY KEY,
 target_id TEXT NOT NULL REFERENCES reverse_trace_targets(target_id),
 evidence_type TEXT NOT NULL,
 project_name TEXT,
 source_company_text TEXT,
 ree_materiality_status TEXT,
 official_source_url TEXT NOT NULL,
 identity_decision TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED'
);
CREATE TABLE IF NOT EXISTS reverse_trace_snapshots (
 snapshot_id TEXT PRIMARY KEY,
 source_query_run TEXT,
 input_manifest_sha256 TEXT NOT NULL,
 outcome_manifest_sha256 TEXT NOT NULL,
 as_of_date TEXT NOT NULL,
 project_master_modified INTEGER NOT NULL DEFAULT 0 CHECK (project_master_modified=0)
);
CREATE INDEX IF NOT EXISTS idx_reverse_targets_state_cohort ON reverse_trace_targets(state,cohort);
CREATE INDEX IF NOT EXISTS idx_reverse_tenement_target ON reverse_tenement_observations(target_id);
CREATE INDEX IF NOT EXISTS idx_reverse_project_evidence_target ON reverse_project_document_evidence(target_id);
