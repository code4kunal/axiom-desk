-- every recorded output, written once; as-of reads filter on knowledge_ts (epoch seconds)
CREATE TABLE emissions (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  instrument TEXT NOT NULL,
  knowledge_ts REAL NOT NULL,
  event_ts REAL NOT NULL,
  version TEXT NOT NULL,
  payload TEXT NOT NULL
);

CREATE INDEX emissions_as_of ON emissions (tenant_id, kind, instrument, knowledge_ts);

CREATE TRIGGER emissions_no_update BEFORE UPDATE ON emissions
BEGIN
  SELECT RAISE(ABORT, 'emissions are append-only');
END;

CREATE TRIGGER emissions_no_delete BEFORE DELETE ON emissions
BEGIN
  SELECT RAISE(ABORT, 'emissions are append-only');
END;
