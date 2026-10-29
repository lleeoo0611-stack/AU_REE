-- Scheme A identity and geological-entity schema, additive migration
    CREATE TABLE IF NOT EXISTS source_feature_snapshot(candidate_id TEXT NOT NULL,source_key TEXT NOT NULL,native_id TEXT,
      record_sha256 TEXT NOT NULL,source_manifest_sha256 TEXT,source_url TEXT,observed_at TEXT NOT NULL,
      PRIMARY KEY(candidate_id,record_sha256));
    CREATE TABLE IF NOT EXISTS geological_entity(entity_id TEXT PRIMARY KEY,canonical_name TEXT NOT NULL,state TEXT,
      latitude REAL,longitude REAL,entity_level TEXT NOT NULL,screening_tier TEXT NOT NULL,
      identity_status TEXT NOT NULL,first_seen TEXT,last_seen TEXT);
    CREATE TABLE IF NOT EXISTS geological_entity_source(entity_id TEXT NOT NULL,candidate_id TEXT PRIMARY KEY,
      source_key TEXT NOT NULL,native_id TEXT,record_sha256 TEXT NOT NULL,
      FOREIGN KEY(entity_id) REFERENCES geological_entity(entity_id),
      FOREIGN KEY(candidate_id) REFERENCES population_candidates(candidate_id));
    CREATE TABLE IF NOT EXISTS extended_occurrence_inventory(candidate_id TEXT PRIMARY KEY,entity_id TEXT NOT NULL,
      screening_tier TEXT NOT NULL,disposition TEXT NOT NULL,source_sha256 TEXT,updated_at TEXT NOT NULL,
      FOREIGN KEY(candidate_id) REFERENCES population_candidates(candidate_id),
      FOREIGN KEY(entity_id) REFERENCES geological_entity(entity_id));
    CREATE TABLE IF NOT EXISTS project_geological_relation(project_id TEXT NOT NULL,entity_id TEXT NOT NULL,
      relation_type TEXT NOT NULL,decision_status TEXT NOT NULL,source_ref TEXT,approval_ref TEXT,updated_at TEXT,
      PRIMARY KEY(project_id,entity_id), FOREIGN KEY(project_id) REFERENCES project_master(project_id),
      FOREIGN KEY(entity_id) REFERENCES geological_entity(entity_id));
    CREATE TABLE IF NOT EXISTS identity_review_decisions(candidate_id TEXT PRIMARY KEY,review_decision TEXT NOT NULL,
      approval_ref TEXT,source_url TEXT,source_sha256 TEXT,review_status TEXT NOT NULL,
      resolved_project_id TEXT,review_reason TEXT,reviewed_at TEXT,
      FOREIGN KEY(candidate_id) REFERENCES population_candidates(candidate_id));
    CREATE TABLE IF NOT EXISTS dedup_candidate_pairs(pair_id TEXT PRIMARY KEY,candidate_a TEXT NOT NULL,
      candidate_b TEXT NOT NULL,rule TEXT NOT NULL,distance_km REAL,decision_status TEXT NOT NULL,
      updated_at TEXT NOT NULL,FOREIGN KEY(candidate_a) REFERENCES population_candidates(candidate_id),
      FOREIGN KEY(candidate_b) REFERENCES population_candidates(candidate_id));
    CREATE INDEX IF NOT EXISTS idx_geological_source ON geological_entity_source(source_key,native_id);
    CREATE INDEX IF NOT EXISTS idx_geological_state ON geological_entity(state,screening_tier);
    CREATE INDEX IF NOT EXISTS idx_identity_review_status ON identity_review_decisions(review_status);
