-- Two verdicts of one version can be saved within a second (verdict, then the challenged one); the timestamp
-- cannot order them, so each gets the next number for its version.
ALTER TABLE verdicts ADD COLUMN seq INTEGER NOT NULL DEFAULT 0;
