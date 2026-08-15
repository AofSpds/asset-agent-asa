BEGIN;

CREATE SCHEMA IF NOT EXISTS aaa_ops;

CREATE TABLE IF NOT EXISTS aaa_ops.work_order_refs (
    work_order_id text PRIMARY KEY,
    git_repository text NOT NULL,
    git_path text NOT NULL,
    git_commit_or_blob_identity text NOT NULL,
    content_sha256 char(64),
    observed_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS aaa_ops.runs (
    run_id text PRIMARY KEY,
    process_id text NOT NULL,
    work_order_id text NOT NULL REFERENCES aaa_ops.work_order_refs(work_order_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    responsible_persona text NOT NULL CHECK (responsible_persona IN (
        'SEMI-CONTROL-ARCHITECT',
        'SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT',
        'SEMI-RESEARCH-ORCHESTRATOR',
        'SEMI-VALIDATION-AUDITOR'
    )),
    executor_role text NOT NULL,
    repository text NOT NULL,
    exact_target_commit char(40) NOT NULL CHECK (exact_target_commit ~ '^[0-9a-f]{40}$'),
    branch_context text NOT NULL,
    state text NOT NULL CHECK (state IN (
        'READY_NOT_DISPATCHED',
        'DISPATCHED_AWAITING_ACK',
        'RUNNING_CONFIRMED',
        'BLOCKED',
        'STALE_UNKNOWN',
        'COMPLETED_PASS',
        'COMPLETED_FAIL',
        'COMPLETED_WITH_FINDINGS'
    )),
    started_at timestamptz,
    last_heartbeat_at timestamptz,
    stale_after_seconds integer NOT NULL CHECK (stale_after_seconds >= 60),
    lease_owner text,
    lease_epoch bigint NOT NULL DEFAULT 0 CHECK (lease_epoch >= 0),
    lease_expires_at timestamptz,
    terminal_result_id text,
    row_version bigint NOT NULL DEFAULT 0 CHECK (row_version >= 0),
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    updated_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (last_heartbeat_at IS NULL OR (started_at IS NOT NULL AND last_heartbeat_at >= started_at)),
    CHECK (
        state <> 'RUNNING_CONFIRMED'
        OR (started_at IS NOT NULL AND last_heartbeat_at IS NOT NULL)
    ),
    CHECK (
        state IN ('COMPLETED_PASS', 'COMPLETED_FAIL', 'COMPLETED_WITH_FINDINGS')
        OR terminal_result_id IS NULL
    )
);

CREATE TABLE IF NOT EXISTS aaa_ops.run_events (
    event_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES aaa_ops.runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    sequence_number bigint NOT NULL CHECK (sequence_number > 0),
    event_type text NOT NULL,
    observed_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    actor_identity text NOT NULL,
    idempotency_key text NOT NULL UNIQUE,
    payload_jsonb jsonb NOT NULL DEFAULT '{}'::jsonb,
    payload_sha256 char(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    prev_event_hash char(64),
    event_hash char(64),
    UNIQUE (run_id, sequence_number),
    CHECK (prev_event_hash IS NULL OR prev_event_hash ~ '^[0-9a-f]{64}$'),
    CHECK (event_hash IS NULL OR event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS aaa_ops.results (
    result_id text PRIMARY KEY,
    run_id text NOT NULL UNIQUE REFERENCES aaa_ops.runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    work_order_id text NOT NULL REFERENCES aaa_ops.work_order_refs(work_order_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    verdict text NOT NULL CHECK (verdict IN ('PASS', 'FAIL', 'PASS_WITH_FINDINGS')),
    artifact_locator text NOT NULL,
    artifact_sha256 char(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    artifact_byte_size bigint NOT NULL CHECK (artifact_byte_size >= 0),
    repository text NOT NULL,
    exact_target_commit char(40) NOT NULL CHECK (exact_target_commit ~ '^[0-9a-f]{40}$'),
    completed_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    metadata_jsonb jsonb NOT NULL DEFAULT '{}'::jsonb
);

ALTER TABLE aaa_ops.runs
    ADD CONSTRAINT runs_terminal_result_fk
    FOREIGN KEY (terminal_result_id)
    REFERENCES aaa_ops.results(result_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE IF NOT EXISTS aaa_ops.experiments (
    experiment_id text PRIMARY KEY,
    experiment_type text NOT NULL,
    model_spec_git_identity text NOT NULL,
    feature_spec_git_identity text NOT NULL,
    dataset_identity text,
    snapshot_identity text,
    configuration_sha256 char(64) NOT NULL CHECK (configuration_sha256 ~ '^[0-9a-f]{64}$'),
    seed_policy jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL,
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE TABLE IF NOT EXISTS aaa_ops.experiment_runs (
    experiment_id text NOT NULL REFERENCES aaa_ops.experiments(experiment_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    run_id text NOT NULL REFERENCES aaa_ops.runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    experiment_role text NOT NULL DEFAULT 'PRIMARY',
    PRIMARY KEY (experiment_id, run_id)
);

CREATE TABLE IF NOT EXISTS aaa_ops.snapshot_refs (
    snapshot_id text PRIMARY KEY,
    pit_cutoff timestamptz NOT NULL,
    artifact_locator text NOT NULL,
    artifact_sha256 char(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    artifact_byte_size bigint NOT NULL CHECK (artifact_byte_size >= 0),
    lineage_identity text NOT NULL,
    source_release_identity text,
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE OR REPLACE FUNCTION aaa_ops.reject_run_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'RUN_EVENTS_APPEND_ONLY';
END;
$$;

DROP TRIGGER IF EXISTS run_events_no_update_delete ON aaa_ops.run_events;
CREATE TRIGGER run_events_no_update_delete
BEFORE UPDATE OR DELETE ON aaa_ops.run_events
FOR EACH ROW EXECUTE FUNCTION aaa_ops.reject_run_event_mutation();

CREATE OR REPLACE FUNCTION aaa_ops.validate_result_identity()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    run_row aaa_ops.runs%ROWTYPE;
BEGIN
    SELECT * INTO STRICT run_row FROM aaa_ops.runs WHERE run_id = NEW.run_id;

    IF run_row.work_order_id <> NEW.work_order_id THEN
        RAISE EXCEPTION 'RESULT_WORK_ORDER_MISMATCH';
    END IF;
    IF run_row.repository <> NEW.repository THEN
        RAISE EXCEPTION 'RESULT_REPOSITORY_MISMATCH';
    END IF;
    IF run_row.exact_target_commit <> NEW.exact_target_commit THEN
        RAISE EXCEPTION 'RESULT_TARGET_MISMATCH';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS results_identity_guard ON aaa_ops.results;
CREATE TRIGGER results_identity_guard
BEFORE INSERT OR UPDATE ON aaa_ops.results
FOR EACH ROW EXECUTE FUNCTION aaa_ops.validate_result_identity();

CREATE OR REPLACE FUNCTION aaa_ops.validate_deferred_terminal_binding()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    run_row aaa_ops.runs%ROWTYPE;
    result_row aaa_ops.results%ROWTYPE;
    expected_verdict text;
BEGIN
    IF TG_TABLE_NAME = 'runs' THEN
        run_row := NEW;
    ELSE
        SELECT * INTO STRICT run_row FROM aaa_ops.runs WHERE run_id = NEW.run_id;
    END IF;

    IF run_row.state IN ('COMPLETED_PASS', 'COMPLETED_FAIL', 'COMPLETED_WITH_FINDINGS') THEN
        IF run_row.terminal_result_id IS NULL THEN
            RAISE EXCEPTION 'TERMINAL_RESULT_REQUIRED';
        END IF;

        SELECT * INTO STRICT result_row
        FROM aaa_ops.results
        WHERE result_id = run_row.terminal_result_id
          AND run_id = run_row.run_id;

        expected_verdict := CASE run_row.state
            WHEN 'COMPLETED_PASS' THEN 'PASS'
            WHEN 'COMPLETED_FAIL' THEN 'FAIL'
            WHEN 'COMPLETED_WITH_FINDINGS' THEN 'PASS_WITH_FINDINGS'
        END;

        IF result_row.verdict <> expected_verdict THEN
            RAISE EXCEPTION 'TERMINAL_STATE_VERDICT_MISMATCH';
        END IF;
        IF result_row.work_order_id <> run_row.work_order_id
           OR result_row.repository <> run_row.repository
           OR result_row.exact_target_commit <> run_row.exact_target_commit THEN
            RAISE EXCEPTION 'TERMINAL_RESULT_REFERENTIAL_MISMATCH';
        END IF;
    ELSIF run_row.terminal_result_id IS NOT NULL THEN
        RAISE EXCEPTION 'NONTERMINAL_RESULT_BINDING_PROHIBITED';
    END IF;

    IF TG_TABLE_NAME = 'results' THEN
        IF run_row.terminal_result_id IS DISTINCT FROM NEW.result_id THEN
            RAISE EXCEPTION 'RESULT_MUST_BE_BOUND_IN_SAME_TRANSACTION';
        END IF;
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS runs_terminal_binding_guard ON aaa_ops.runs;
CREATE CONSTRAINT TRIGGER runs_terminal_binding_guard
AFTER INSERT OR UPDATE OF state, terminal_result_id, work_order_id, repository, exact_target_commit
ON aaa_ops.runs
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION aaa_ops.validate_deferred_terminal_binding();

DROP TRIGGER IF EXISTS results_terminal_binding_guard ON aaa_ops.results;
CREATE CONSTRAINT TRIGGER results_terminal_binding_guard
AFTER INSERT OR UPDATE
ON aaa_ops.results
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION aaa_ops.validate_deferred_terminal_binding();

CREATE OR REPLACE FUNCTION aaa_ops.start_run_with_lease(
    p_run_id text,
    p_lease_owner text,
    p_ttl_seconds integer
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    next_epoch bigint;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT lease_epoch + 1 INTO STRICT next_epoch
    FROM aaa_ops.runs
    WHERE run_id = p_run_id
      AND state IN ('DISPATCHED_AWAITING_ACK', 'READY_NOT_DISPATCHED', 'BLOCKED', 'STALE_UNKNOWN')
    FOR UPDATE;

    UPDATE aaa_ops.runs
    SET state = 'RUNNING_CONFIRMED',
        started_at = transaction_timestamp(),
        last_heartbeat_at = transaction_timestamp(),
        lease_owner = p_lease_owner,
        lease_epoch = next_epoch,
        lease_expires_at = transaction_timestamp() + make_interval(secs => p_ttl_seconds),
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE run_id = p_run_id;

    RETURN next_epoch;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.acquire_run_lease(
    p_run_id text,
    p_lease_owner text,
    p_ttl_seconds integer
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    current_owner text;
    current_epoch bigint;
    current_expiry timestamptz;
    next_epoch bigint;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT lease_owner, lease_epoch, lease_expires_at
    INTO STRICT current_owner, current_epoch, current_expiry
    FROM aaa_ops.runs
    WHERE run_id = p_run_id
      AND state NOT IN ('COMPLETED_PASS', 'COMPLETED_FAIL', 'COMPLETED_WITH_FINDINGS')
    FOR UPDATE;

    IF current_expiry IS NOT NULL
       AND current_expiry > transaction_timestamp()
       AND current_owner IS DISTINCT FROM p_lease_owner THEN
        RAISE EXCEPTION 'LEASE_ALREADY_HELD';
    END IF;

    next_epoch := current_epoch + 1;

    UPDATE aaa_ops.runs
    SET lease_owner = p_lease_owner,
        lease_epoch = next_epoch,
        lease_expires_at = transaction_timestamp() + make_interval(secs => p_ttl_seconds),
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE run_id = p_run_id;

    RETURN next_epoch;
END;
$$;

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
      AND started_at <= transaction_timestamp();

    GET DIAGNOSTICS changed = ROW_COUNT;
    IF changed <> 1 THEN
        RAISE EXCEPTION 'STALE_OR_INVALID_LEASE';
    END IF;
END;
$$;

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
