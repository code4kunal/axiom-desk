CREATE TABLE contracts (
  contract_id TEXT PRIMARY KEY,
  underlying_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  option_type TEXT,
  strike TEXT,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_contracts_underlying ON contracts (underlying_id);

CREATE TABLE contract_expiries (
  contract_id TEXT NOT NULL REFERENCES contracts(contract_id),
  expiry_date DATE NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_contract_expiries_lookup
  ON contract_expiries (contract_id, effective_from);

CREATE TABLE contract_lots (
  contract_id TEXT NOT NULL REFERENCES contracts(contract_id),
  lot_size INTEGER NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL
);

CREATE INDEX idx_contract_lots_lookup
  ON contract_lots (contract_id, effective_from);

CREATE TABLE ban_list_days (
  exchange TEXT NOT NULL,
  list_date DATE NOT NULL,
  published_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL,
  PRIMARY KEY (exchange, list_date)
);

CREATE TABLE ban_list (
  exchange TEXT NOT NULL,
  list_date DATE NOT NULL,
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  source TEXT NOT NULL,
  licence_scope TEXT NOT NULL,
  PRIMARY KEY (exchange, list_date, instrument_id),
  FOREIGN KEY (exchange, list_date) REFERENCES ban_list_days(exchange, list_date)
);

CREATE INDEX idx_ban_list_lookup
  ON ban_list (exchange, list_date, instrument_id);
