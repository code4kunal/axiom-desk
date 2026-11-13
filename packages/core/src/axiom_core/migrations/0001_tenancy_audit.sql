CREATE TABLE books (
  tenant_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  PRIMARY KEY (tenant_id, book_id)
);

-- book_id '' means the role applies tenant-wide
CREATE TABLE role_assignments (
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  book_id TEXT NOT NULL DEFAULT '',
  PRIMARY KEY (tenant_id, user_id, role, book_id)
);

CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  at REAL NOT NULL,
  kind TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL,
  verdict TEXT NOT NULL,
  ids TEXT NOT NULL
);
