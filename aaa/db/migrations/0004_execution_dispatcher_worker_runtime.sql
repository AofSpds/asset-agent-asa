BEGIN;

ALTER TABLE aaa_ops.work_order_refs
    ADD COLUMN IF NOT EXISTS approval_state text NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN IF NOT EXISTS approval_identity text,
    ADD COLUMN IF NOT EXISTS approval_git_identity text;

CREATE TABLE IF NOT EXISTS aaa_ops.execution_profiles (
    execution_profile_id text PRIMARY KEY,
    version text NOT NULL,
    git_identity text NOT NULL,
    profile_sha256 char(64) NOT NULL CHECK (profile_sha256 ~ '^[0-9a-f]{64}$'),
    allowed_personas text[] NOT NULL,
    required_capability text NOT NULL,
    minimum_permission_level integer NOT NULL CHECK (minimum_permission_level >= 0),
    timeout_seconds integer NOT NULL CHECK (timeout_seconds > 0),
    network_policy text NOT NULL,
    filesystem_policy text NOT NULL,
    metadata_jsonb jsonb NOT NULL DEFAULT '{}'::jsonb,
    registered_at_db timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE TABLE IF NOT EXISTS aaa_ops.workers (
    worker_id text PRIMARY KEY,
    worker_type text NOT NULL,
    runtime_version text NOT NULL,
    host_identity text NOT NULL,
    capabilities text[] NOT NULL,
    authorized_personas text[] NOT NULL,
    permission_level integer NOT NULL CHECK (permission_level >= 0),
    max_concurrency integer NOT NULL CHECK (max_concurrency > 0),
    enabled boolean NOT NULL DEFAULT false,
    last_seen_at timestamptz,
    registered_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    metadata_jsonb jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS aaa_ops.execution_tasks (
    task_id text PRIMARY KEY,
    run_id text NOT NULL UNIQUE REFERENCES aaa_ops.runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    execution_profile_id text NOT NULL REFERENCES aaa_ops.execution_profiles(execution_profile_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    execution_profile_sha256 char(64) NOT NULL CHECK (execution_profile_sha256 ~ '^[0-9a-f]{64}$'),
    exact_target_commit char(40) NOT NULL CHECK (exact_target_commit ~ '^[0-9a-f]{40}$'),
    required_persona text NOT NULL,
    required_capability text NOT NULL,
    required_permission_level integer NOT NULL CHECK (required_permission_level >= 0),
    state text NOT NULL CHECK (state IN ('AVAILABLE', 'CLAIMED', 'ACKNOWLEDGED', 'RUNNING', 'TERMINAL')),
    retry_of_run_id text REFERENCES aaa_ops.runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    claimed_by text REFERENCES aaa_ops.workers(worker_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    lease_epoch bigint,
    materialized_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    claimed_at_db timestamptz,
    acknowledged_at_db timestamptz,
    started_at_db timestamptz,
    terminal_result_id text,
    metadata_jsonb jsonb NOT NULL DEFAULT '{}'::jsonb,
    CHECK ((claimed_by IS NULL AND lease_epoch IS NULL) OR (claimed_by IS NOT NULL AND lease_epoch IS NOT NULL)),
    CHECK (retry_of_run_id IS NULL OR retry_of_run_id <> run_id)
);

CREATE OR REPLACE FUNCTION aaa_ops.materialize_execution_task(
    p_task_id text,
    p_run_id text,
    p_execution_profile_id text,
    p_execution_profile_sha256 char(64),
    p_exact_target_commit char(40),
    p_required_capability text,
    p_required_permission_level integer,
    p_retry_of_run_id text DEFAULT NULL
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    v_run aaa_ops.runs%ROWTYPE;
    v_profile aaa_ops.execution_profiles%ROWTYPE;
    v_wo aaa_ops.work_order_refs%ROWTYPE;
    v_existing aaa_ops.execution_tasks%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_run FROM aaa_ops.runs WHERE run_id = p_run_id;
    SELECT * INTO STRICT v_wo FROM aaa_ops.work_order_refs WHERE work_order_id = v_run.work_order_id;
    SELECT * INTO STRICT v_profile FROM aaa_ops.execution_profiles WHERE execution_profile_id = p_execution_profile_id;

    IF v_wo.approval_state NOT IN ('OWNER_APPROVED_READY_FOR_EXECUTION', 'OWNER_APPROVED_FOR_BOUNDED_ENGINEERING') THEN
        RAISE EXCEPTION 'WORK_ORDER_NOT_APPROVED_FOR_EXECUTION';
    END IF;
    IF v_run.state <> 'DISPATCHED_AWAITING_ACK' THEN
        RAISE EXCEPTION 'RUN_NOT_DISPATCHED_AWAITING_ACK';
    END IF;
    IF v_run.exact_target_commit <> p_exact_target_commit THEN
        RAISE EXCEPTION 'EXACT_TARGET_MISMATCH';
    END IF;
    IF v_profile.profile_sha256 <> p_execution_profile_sha256 THEN
        RAISE EXCEPTION 'EXECUTION_PROFILE_SHA256_MISMATCH';
    END IF;
    IF NOT (v_run.responsible_persona = ANY(v_profile.allowed_personas)) THEN
        RAISE EXCEPTION 'PROFILE_PERSONA_NOT_ALLOWED';
    END IF;
    IF v_profile.required_capability <> p_required_capability THEN
        RAISE EXCEPTION 'PROFILE_CAPABILITY_MISMATCH';
    END IF;
    IF v_profile.minimum_permission_level <> p_required_permission_level THEN
        RAISE EXCEPTION 'PROFILE_PERMISSION_MISMATCH';
    END IF;

    SELECT * INTO v_existing FROM aaa_ops.execution_tasks WHERE run_id = p_run_id;
    IF FOUND THEN
        IF v_existing.task_id = p_task_id
           AND v_existing.execution_profile_id = p_execution_profile_id
           AND v_existing.execution_profile_sha256 = p_execution_profile_sha256
           AND v_existing.exact_target_commit = p_exact_target_commit
           AND v_existing.required_persona = v_run.responsible_persona
           AND v_existing.required_capability = p_required_capability
           AND v_existing.required_permission_level = p_required_permission_level
           AND v_existing.retry_of_run_id IS NOT DISTINCT FROM p_retry_of_run_id THEN
            RETURN v_existing.task_id;
        END IF;
        RAISE EXCEPTION 'RUN_TASK_IDEMPOTENCY_MISMATCH';
    END IF;

    INSERT INTO aaa_ops.execution_tasks (
        task_id, run_id, execution_profile_id, execution_profile_sha256,
        exact_target_commit, required_persona, required_capability,
        required_permission_level, state, retry_of_run_id
    ) VALUES (
        p_task_id, p_run_id, p_execution_profile_id, p_execution_profile_sha256,
        p_exact_target_commit, v_run.responsible_persona, p_required_capability,
        p_required_permission_level, 'AVAILABLE', p_retry_of_run_id
    );

    RETURN p_task_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.claim_next_execution_task(
    p_worker_id text,
    p_ttl_seconds integer
)
RETURNS TABLE (
    task_id text,
    run_id text,
    lease_epoch bigint,
    execution_profile_id text,
    execution_profile_sha256 char(64),
    exact_target_commit char(40),
    work_order_id text,
    responsible_persona text,
    required_capability text,
    required_permission_level integer
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_worker aaa_ops.workers%ROWTYPE;
    v_task aaa_ops.execution_tasks%ROWTYPE;
    v_run aaa_ops.runs%ROWTYPE;
    v_next_epoch bigint;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT * INTO STRICT v_worker
    FROM aaa_ops.workers
    WHERE worker_id = p_worker_id
    FOR UPDATE;

    IF NOT v_worker.enabled THEN
        RAISE EXCEPTION 'WORKER_DISABLED';
    END IF;

    SELECT t.* INTO v_task
    FROM aaa_ops.execution_tasks t
    JOIN aaa_ops.runs r ON r.run_id = t.run_id
    WHERE t.state = 'AVAILABLE'
      AND r.state = 'DISPATCHED_AWAITING_ACK'
      AND t.required_capability = ANY(v_worker.capabilities)
      AND t.required_persona = ANY(v_worker.authorized_personas)
      AND t.required_permission_level <= v_worker.permission_level
    ORDER BY t.materialized_at_db, t.task_id
    FOR UPDATE OF t SKIP LOCKED
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    SELECT * INTO STRICT v_run
    FROM aaa_ops.runs AS r
    WHERE r.run_id = v_task.run_id
    FOR UPDATE;

    IF v_run.lease_expires_at IS NOT NULL
       AND v_run.lease_expires_at > transaction_timestamp()
       AND v_run.lease_owner IS DISTINCT FROM p_worker_id THEN
        RAISE EXCEPTION 'LEASE_ALREADY_HELD';
    END IF;

    v_next_epoch := v_run.lease_epoch + 1;

    IF (
        SELECT count(*)
        FROM aaa_ops.execution_tasks
        WHERE claimed_by = p_worker_id
          AND state IN ('CLAIMED', 'ACKNOWLEDGED', 'RUNNING')
    ) >= v_worker.max_concurrency THEN
        RAISE EXCEPTION 'WORKER_MAX_CONCURRENCY_REACHED';
    END IF;

    UPDATE aaa_ops.runs AS r
    SET lease_owner = p_worker_id,
        lease_epoch = v_next_epoch,
        lease_expires_at = transaction_timestamp() + make_interval(secs => p_ttl_seconds),
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE r.run_id = v_task.run_id;

    UPDATE aaa_ops.execution_tasks AS t
    SET state = 'CLAIMED',
        claimed_by = p_worker_id,
        lease_epoch = v_next_epoch,
        claimed_at_db = transaction_timestamp()
    WHERE t.task_id = v_task.task_id;

    UPDATE aaa_ops.workers
    SET last_seen_at = transaction_timestamp()
    WHERE worker_id = p_worker_id;

    task_id := v_task.task_id;
    run_id := v_task.run_id;
    lease_epoch := v_next_epoch;
    execution_profile_id := v_task.execution_profile_id;
    execution_profile_sha256 := v_task.execution_profile_sha256;
    exact_target_commit := v_task.exact_target_commit;
    work_order_id := v_run.work_order_id;
    responsible_persona := v_run.responsible_persona;
    required_capability := v_task.required_capability;
    required_permission_level := v_task.required_permission_level;
    RETURN NEXT;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.ack_execution_task(
    p_task_id text,
    p_worker_id text,
    p_lease_epoch bigint
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_task aaa_ops.execution_tasks%ROWTYPE;
    v_run aaa_ops.runs%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_task FROM aaa_ops.execution_tasks WHERE task_id = p_task_id FOR UPDATE;
    SELECT * INTO STRICT v_run FROM aaa_ops.runs WHERE run_id = v_task.run_id FOR UPDATE;

    IF v_task.state <> 'CLAIMED'
       OR v_task.claimed_by IS DISTINCT FROM p_worker_id
       OR v_task.lease_epoch IS DISTINCT FROM p_lease_epoch THEN
        RAISE EXCEPTION 'TASK_CLAIM_IDENTITY_MISMATCH';
    END IF;
    IF v_run.state <> 'DISPATCHED_AWAITING_ACK'
       OR v_run.lease_owner IS DISTINCT FROM p_worker_id
       OR v_run.lease_epoch <> p_lease_epoch
       OR v_run.lease_expires_at IS NULL
       OR v_run.lease_expires_at < transaction_timestamp() THEN
        RAISE EXCEPTION 'STALE_OR_INVALID_LEASE';
    END IF;

    UPDATE aaa_ops.execution_tasks
    SET state = 'ACKNOWLEDGED',
        acknowledged_at_db = transaction_timestamp()
    WHERE task_id = p_task_id;

    UPDATE aaa_ops.workers SET last_seen_at = transaction_timestamp() WHERE worker_id = p_worker_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.start_execution_task(
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
    v_run aaa_ops.runs%ROWTYPE;
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT * INTO STRICT v_task FROM aaa_ops.execution_tasks WHERE task_id = p_task_id FOR UPDATE;
    SELECT * INTO STRICT v_run FROM aaa_ops.runs WHERE run_id = v_task.run_id FOR UPDATE;

    IF v_task.state <> 'ACKNOWLEDGED'
       OR v_task.claimed_by IS DISTINCT FROM p_worker_id
       OR v_task.lease_epoch IS DISTINCT FROM p_lease_epoch
       OR v_task.acknowledged_at_db IS NULL THEN
        RAISE EXCEPTION 'TASK_NOT_ACKNOWLEDGED_BY_CURRENT_LEASE';
    END IF;
    IF v_run.state <> 'DISPATCHED_AWAITING_ACK'
       OR v_run.lease_owner IS DISTINCT FROM p_worker_id
       OR v_run.lease_epoch <> p_lease_epoch
       OR v_run.lease_expires_at IS NULL
       OR v_run.lease_expires_at < transaction_timestamp() THEN
        RAISE EXCEPTION 'STALE_OR_INVALID_LEASE';
    END IF;

    UPDATE aaa_ops.runs
    SET state = 'RUNNING_CONFIRMED',
        started_at = transaction_timestamp(),
        last_heartbeat_at = transaction_timestamp(),
        lease_expires_at = transaction_timestamp() + make_interval(secs => p_ttl_seconds),
        row_version = row_version + 1,
        updated_at_db = transaction_timestamp()
    WHERE run_id = v_task.run_id;

    UPDATE aaa_ops.execution_tasks
    SET state = 'RUNNING',
        started_at_db = transaction_timestamp()
    WHERE task_id = p_task_id;

    UPDATE aaa_ops.workers SET last_seen_at = transaction_timestamp() WHERE worker_id = p_worker_id;
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
    SELECT * INTO STRICT v_task FROM aaa_ops.execution_tasks WHERE task_id = p_task_id;
    IF v_task.state <> 'RUNNING'
       OR v_task.claimed_by IS DISTINCT FROM p_worker_id
       OR v_task.lease_epoch IS DISTINCT FROM p_lease_epoch THEN
        RAISE EXCEPTION 'TASK_NOT_RUNNING_UNDER_CURRENT_LEASE';
    END IF;

    PERFORM aaa_ops.heartbeat_run(v_task.run_id, p_worker_id, p_lease_epoch, p_ttl_seconds);
    UPDATE aaa_ops.workers SET last_seen_at = transaction_timestamp() WHERE worker_id = p_worker_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.complete_execution_task_atomic(
    p_task_id text,
    p_worker_id text,
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
    v_task aaa_ops.execution_tasks%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_task
    FROM aaa_ops.execution_tasks
    WHERE task_id = p_task_id
    FOR UPDATE;

    IF v_task.state <> 'RUNNING'
       OR v_task.claimed_by IS DISTINCT FROM p_worker_id
       OR v_task.lease_epoch IS DISTINCT FROM p_lease_epoch THEN
        RAISE EXCEPTION 'TASK_NOT_RUNNING_UNDER_CURRENT_LEASE';
    END IF;

    PERFORM aaa_ops.complete_run_atomic(
        v_task.run_id, p_worker_id, p_lease_epoch,
        p_result_id, p_verdict, p_artifact_locator,
        p_artifact_sha256, p_artifact_byte_size, p_metadata_jsonb
    );

    UPDATE aaa_ops.execution_tasks
    SET state = 'TERMINAL',
        terminal_result_id = p_result_id
    WHERE task_id = p_task_id;

    UPDATE aaa_ops.workers SET last_seen_at = transaction_timestamp() WHERE worker_id = p_worker_id;

    RETURN p_result_id;
END;
$$;

CREATE OR REPLACE VIEW aaa_ops.execution_task_projection AS
SELECT
    t.*,
    rp.effective_state AS run_effective_state,
    CASE
        WHEN t.state = 'RUNNING' AND rp.effective_state = 'STALE_UNKNOWN' THEN 'STALE_UNKNOWN'
        ELSE t.state
    END AS effective_task_state,
    rp.last_heartbeat_at,
    rp.lease_expires_at
FROM aaa_ops.execution_tasks t
JOIN aaa_ops.run_projection rp ON rp.run_id = t.run_id;

COMMIT;
