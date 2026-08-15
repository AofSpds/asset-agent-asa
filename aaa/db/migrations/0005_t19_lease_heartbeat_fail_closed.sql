BEGIN;

-- T19 P0 remediation successor migration.
-- Do not rewrite frozen 0001/0004 bytes; override affected functions here.

CREATE OR REPLACE FUNCTION aaa_ops.heartbeat_run(
    p_run_id text,
    p_lease_owner text,
    p_lease_epoch bigint,
    p_ttl_seconds integer
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    changed integer;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    UPDATE aaa_ops.runs
    SET last_heartbeat_at = transaction_timestamp(),
        lease_expires_at = transaction_timestamp() + make_interval(secs => p_ttl_seconds),
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE run_id = p_run_id
      AND state = 'RUNNING_CONFIRMED'
      AND lease_owner = p_lease_owner
      AND lease_epoch = p_lease_epoch
      AND started_at IS NOT NULL
      AND started_at <= transaction_timestamp()
      AND lease_expires_at IS NOT NULL
      AND lease_expires_at >= transaction_timestamp();

    GET DIAGNOSTICS changed = ROW_COUNT;
    IF changed <> 1 THEN
        RAISE EXCEPTION 'STALE_OR_INVALID_LEASE';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.heartbeat_execution_task(
    p_task_id text,
    p_worker_id text,
    p_lease_epoch bigint,
    p_ttl_seconds integer
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_task aaa_ops.execution_tasks%ROWTYPE;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT * INTO STRICT v_task
    FROM aaa_ops.execution_tasks
    WHERE task_id = p_task_id
    FOR UPDATE;

    IF v_task.state <> 'RUNNING'
       OR v_task.claimed_by IS DISTINCT FROM p_worker_id
       OR v_task.lease_epoch IS DISTINCT FROM p_lease_epoch THEN
        RAISE EXCEPTION 'TASK_NOT_RUNNING_UNDER_CURRENT_LEASE';
    END IF;

    -- heartbeat_run is the authoritative run-lease fence and now requires
    -- the pre-existing lease to still be current before renewal.
    PERFORM aaa_ops.heartbeat_run(
        v_task.run_id,
        p_worker_id,
        p_lease_epoch,
        p_ttl_seconds
    );

    UPDATE aaa_ops.workers
    SET last_seen_at = transaction_timestamp()
    WHERE worker_id = p_worker_id;
END;
$$;

COMMIT;
