BEGIN;

ALTER TABLE aaa_ops.runs
    ADD COLUMN IF NOT EXISTS canonical_output boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS source_json_path text,
    ADD COLUMN IF NOT EXISTS source_json_sha256 char(64),
    ADD COLUMN IF NOT EXISTS source_json_byte_size bigint;

ALTER TABLE aaa_ops.runs
    DROP CONSTRAINT IF EXISTS runs_source_json_sha256_check;
ALTER TABLE aaa_ops.runs
    ADD CONSTRAINT runs_source_json_sha256_check
    CHECK (source_json_sha256 IS NULL OR source_json_sha256 ~ '^[0-9a-f]{64}$');

ALTER TABLE aaa_ops.runs
    DROP CONSTRAINT IF EXISTS runs_source_json_byte_size_check;
ALTER TABLE aaa_ops.runs
    ADD CONSTRAINT runs_source_json_byte_size_check
    CHECK (source_json_byte_size IS NULL OR source_json_byte_size >= 0);

CREATE UNIQUE INDEX IF NOT EXISTS runs_source_json_path_unique
    ON aaa_ops.runs(source_json_path)
    WHERE source_json_path IS NOT NULL;

CREATE OR REPLACE VIEW aaa_ops.run_projection AS
SELECT
    r.*,
    CASE
        WHEN r.state = 'RUNNING_CONFIRMED'
             AND (
                 r.started_at IS NULL
                 OR r.last_heartbeat_at IS NULL
                 OR r.started_at > transaction_timestamp()
                 OR r.last_heartbeat_at > transaction_timestamp()
                 OR r.last_heartbeat_at + make_interval(secs => r.stale_after_seconds) < transaction_timestamp()
                 OR r.lease_expires_at IS NULL
                 OR r.lease_expires_at < transaction_timestamp()
             )
        THEN 'STALE_UNKNOWN'
        ELSE r.state
    END AS effective_state
FROM aaa_ops.runs r;

COMMIT;
