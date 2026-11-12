CREATE TABLE runs (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  as_of TEXT NOT NULL,
  published_at REAL NOT NULL,
  payload TEXT NOT NULL,
  sources TEXT NOT NULL
);

CREATE INDEX runs_kind_published ON runs (kind, published_at);

CREATE TRIGGER runs_no_update BEFORE UPDATE ON runs
BEGIN
  SELECT RAISE(ABORT, 'runs are immutable');
END;

CREATE TRIGGER runs_no_delete BEFORE DELETE ON runs
BEGIN
  SELECT RAISE(ABORT, 'runs are immutable');
END;

-- licence scopes a tenant's data contracts allow it to receive; 'public' needs no row
CREATE TABLE tenant_entitlements (
  tenant_id TEXT NOT NULL,
  scope TEXT NOT NULL,
  PRIMARY KEY (tenant_id, scope)
);
