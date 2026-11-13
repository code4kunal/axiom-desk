CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  submitted_by TEXT NOT NULL,
  kind TEXT NOT NULL,
  params TEXT NOT NULL,
  state TEXT NOT NULL,
  total INTEGER NOT NULL,
  cancel_requested INTEGER NOT NULL DEFAULT 0,
  created_at REAL NOT NULL
);

CREATE INDEX jobs_owner_state ON jobs (tenant_id, user_id, state);
CREATE INDEX jobs_state_created ON jobs (state, created_at);

-- one row per finished step: the checkpoint a restarted worker resumes from
CREATE TABLE job_steps (
  job_id TEXT NOT NULL REFERENCES jobs (id),
  step INTEGER NOT NULL,
  result TEXT NOT NULL,
  PRIMARY KEY (job_id, step)
);
