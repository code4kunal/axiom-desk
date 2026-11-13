-- sessions and pending sign-ins are keyed by the SHA-256 of the token or handle, never the raw value
CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  -- the ID token's auth_time; NULL when the provider sent none, which never counts as recent
  authenticated_at REAL,
  expires_at REAL NOT NULL
);

CREATE TABLE pending_logins (
  handle_hash TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  nonce TEXT NOT NULL,
  verifier TEXT NOT NULL,
  expires_at REAL NOT NULL
);
