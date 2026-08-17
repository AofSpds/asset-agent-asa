BEGIN;

CREATE OR REPLACE FUNCTION aaa_ops.append_run_event_idempotent(
    p_event_id text,
    p_run_id text,
    p_sequence_number bigint,
    p_event_type text,
    p_actor_identity text,
    p_idempotency_key text,
    p_payload_jsonb jsonb,
    p_payload_sha256 char(64),
    p_prev_event_hash char(64) DEFAULT NULL,
    p_event_hash char(64) DEFAULT NULL
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    existing aaa_ops.run_events%ROWTYPE;
BEGIN
    IF p_sequence_number <= 0 THEN
        RAISE EXCEPTION 'INVALID_EVENT_SEQUENCE';
    END IF;
    IF p_payload_sha256 !~ '^[0-9a-f]{64}$' THEN
        RAISE EXCEPTION 'INVALID_EVENT_PAYLOAD_SHA256';
    END IF;

    PERFORM pg_advisory_xact_lock(hashtextextended(p_idempotency_key, 0));

    SELECT * INTO existing
    FROM aaa_ops.run_events
    WHERE idempotency_key = p_idempotency_key;

    IF FOUND THEN
        IF existing.event_id = p_event_id
           AND existing.run_id = p_run_id
           AND existing.sequence_number = p_sequence_number
           AND existing.event_type = p_event_type
           AND existing.actor_identity = p_actor_identity
           AND existing.payload_jsonb = p_payload_jsonb
           AND existing.payload_sha256 = p_payload_sha256
           AND existing.prev_event_hash IS NOT DISTINCT FROM p_prev_event_hash
           AND existing.event_hash IS NOT DISTINCT FROM p_event_hash THEN
            RETURN existing.event_id;
        END IF;
        RAISE EXCEPTION 'IDEMPOTENCY_KEY_REUSE_MISMATCH';
    END IF;

    INSERT INTO aaa_ops.run_events (
        event_id, run_id, sequence_number, event_type, actor_identity,
        idempotency_key, payload_jsonb, payload_sha256, prev_event_hash, event_hash
    ) VALUES (
        p_event_id, p_run_id, p_sequence_number, p_event_type, p_actor_identity,
        p_idempotency_key, p_payload_jsonb, p_payload_sha256, p_prev_event_hash, p_event_hash
    );

    RETURN p_event_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.complete_run_atomic(
    p_run_id text,
    p_lease_owner text,
    p_lease_epoch bigint,
    p_result_id text,
    p_verdict text,
    p_artifact_locator text,
    p_artifact_sha256 char(64),
    p_artifact_byte_size bigint,
    p_metadata_jsonb jsonb DEFAULT '{}'::jsonb
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    run_row aaa_ops.runs%ROWTYPE;
    terminal_state text;
BEGIN
    IF p_verdict NOT IN ('PASS', 'FAIL', 'PASS_WITH_FINDINGS') THEN
        RAISE EXCEPTION 'INVALID_TERMINAL_VERDICT';
    END IF;
    IF p_artifact_sha256 !~ '^[0-9a-f]{64}$' THEN
        RAISE EXCEPTION 'INVALID_RESULT_SHA256';
    END IF;
    IF p_artifact_byte_size < 0 THEN
        RAISE EXCEPTION 'INVALID_RESULT_BYTE_SIZE';
    END IF;

    SELECT * INTO STRICT run_row
    FROM aaa_ops.runs
    WHERE run_id = p_run_id
    FOR UPDATE;

    IF run_row.state <> 'RUNNING_CONFIRMED' THEN
        RAISE EXCEPTION 'RUN_NOT_RUNNING';
    END IF;
    IF run_row.lease_owner IS DISTINCT FROM p_lease_owner
       OR run_row.lease_epoch <> p_lease_epoch
       OR run_row.lease_expires_at IS NULL
       OR run_row.lease_expires_at < transaction_timestamp() THEN
        RAISE EXCEPTION 'STALE_OR_INVALID_LEASE';
    END IF;
    IF run_row.started_at IS NULL
       OR run_row.last_heartbeat_at IS NULL
       OR run_row.started_at > transaction_timestamp()
       OR run_row.last_heartbeat_at > transaction_timestamp() THEN
        RAISE EXCEPTION 'INVALID_RUN_TIME_EVIDENCE';
    END IF;

    terminal_state := CASE p_verdict
        WHEN 'PASS' THEN 'COMPLETED_PASS'
        WHEN 'FAIL' THEN 'COMPLETED_FAIL'
        WHEN 'PASS_WITH_FINDINGS' THEN 'COMPLETED_WITH_FINDINGS'
    END;

    INSERT INTO aaa_ops.results (
        result_id, run_id, work_order_id, verdict, artifact_locator,
        artifact_sha256, artifact_byte_size, repository, exact_target_commit,
        completed_at_db, metadata_jsonb
    ) VALUES (
        p_result_id, run_row.run_id, run_row.work_order_id, p_verdict, p_artifact_locator,
        p_artifact_sha256, p_artifact_byte_size, run_row.repository, run_row.exact_target_commit,
        transaction_timestamp(), p_metadata_jsonb
    );

    UPDATE aaa_ops.runs
    SET state = terminal_state,
        terminal_result_id = p_result_id,
        lease_owner = NULL,
        lease_expires_at = NULL,
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE run_id = run_row.run_id;

    RETURN p_result_id;
END;
$$;

COMMIT;
