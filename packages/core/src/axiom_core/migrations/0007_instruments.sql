CREATE TABLE instruments (
  instrument_id TEXT PRIMARY KEY,
  asset_class TEXT NOT NULL,
  kind TEXT NOT NULL,
  exchange TEXT NOT NULL,
  name TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE TABLE instrument_identifiers (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  identifier_type TEXT NOT NULL,
  value TEXT NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_instrument_identifiers_lookup
  ON instrument_identifiers (identifier_type, value, effective_from);

CREATE TABLE instrument_roles (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  role TEXT NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_instrument_roles_lookup
  ON instrument_roles (instrument_id, effective_from);

CREATE TABLE instrument_tracks (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  tracked_instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  effective_from DATE NOT NULL,
  effective_to DATE,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_instrument_tracks_lookup
  ON instrument_tracks (tracked_instrument_id, effective_from);
