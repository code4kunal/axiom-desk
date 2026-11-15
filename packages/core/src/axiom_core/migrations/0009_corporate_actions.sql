CREATE TABLE corporate_actions (
  action_id TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  ex_date DATE NOT NULL,
  from_qty INTEGER,
  to_qty INTEGER,
  amount TEXT,
  published_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL,
  PRIMARY KEY (action_id, recorded_at)
);

CREATE INDEX idx_corporate_actions_lookup
  ON corporate_actions (instrument_id, ex_date);
