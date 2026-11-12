-- how many times a worker has started this job; a job that keeps failing is given up on
ALTER TABLE jobs ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0;
