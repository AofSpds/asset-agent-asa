BEGIN;

-- AAA Balanced v1 E2 successor execution semantics.
-- This migration adds new successor entities only. It does not rewrite or reinterpret
-- legacy aaa_ops.runs / aaa_ops.execution_tasks or migrations 0001-0006.
-- PostgreSQL remains NON-AUTHORITATIVE until a separate Project Owner cutover.

CREATE TABLE aaa_ops.v1_logical_runs (
    run_id text PRIMARY KEY,
    project_namespace text NOT NULL,
    process_id text NOT NULL,
    work_order_ref text NOT NULL,
    responsible_persona text NOT NULL,
    executor_role text NOT NULL,
    repository_identity text NOT NULL,
    exact_target_commit char(40) NOT NULL CHECK (exact_target_commit ~ '^[0-9a-f]{40}$'),
    exact_execution_spec_hash char(64) NOT NULL CHECK (exact_execution_spec_hash ~ '^[0-9a-f]{64}$'),
    execution_profile_ref text NOT NULL,
    execution_profile_sha256 char(64) NOT NULL CHECK (execution_profile_sha256 ~ '^[0-9a-f]{64}$'),
    configuration_sha256 char(64) NOT NULL CHECK (configuration_sha256 ~ '^[0-9a-f]{64}$'),
    material_input_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    schema_family_version_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    logical_status text NOT NULL DEFAULT 'READY_NOT_DISPATCHED' CHECK (
        logical_status IN (
            'READY_NOT_DISPATCHED','DISPATCHED','ACTIVE','BLOCKED',
            'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
            'CANCELLED','SUPERSEDED'
        )
    ),
    semantic_generation text NOT NULL DEFAULT 'BALANCED_V1' CHECK (semantic_generation = 'BALANCED_V1'),
    final_disposition_ref text,
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    updated_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (btrim(project_namespace) <> ''),
    CHECK (btrim(process_id) <> ''),
    CHECK (btrim(work_order_ref) <> ''),
    CHECK (btrim(responsible_persona) <> ''),
    CHECK (btrim(executor_role) <> ''),
    CHECK (btrim(repository_identity) <> ''),
    CHECK (btrim(execution_profile_ref) <> '')
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_logical_run_spec_immutable()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF ROW(
        NEW.project_namespace, NEW.process_id, NEW.work_order_ref,
        NEW.responsible_persona, NEW.executor_role, NEW.repository_identity,
        NEW.exact_target_commit, NEW.exact_execution_spec_hash,
        NEW.execution_profile_ref, NEW.execution_profile_sha256,
        NEW.configuration_sha256, NEW.material_input_refs,
        NEW.schema_family_version_refs, NEW.semantic_generation
    ) IS DISTINCT FROM ROW(
        OLD.project_namespace, OLD.process_id, OLD.work_order_ref,
        OLD.responsible_persona, OLD.executor_role, OLD.repository_identity,
        OLD.exact_target_commit, OLD.exact_execution_spec_hash,
        OLD.execution_profile_ref, OLD.execution_profile_sha256,
        OLD.configuration_sha256, OLD.material_input_refs,
        OLD.schema_family_version_refs, OLD.semantic_generation
    ) THEN
        RAISE EXCEPTION 'LOGICAL_RUN_EXECUTION_SPEC_IMMUTABLE';
    END IF;
    NEW.updated_at_db := transaction_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_logical_run_spec_immutable
BEFORE UPDATE ON aaa_ops.v1_logical_runs
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_logical_run_spec_immutable();

CREATE TABLE aaa_ops.v1_run_attempts (
    run_attempt_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES aaa_ops.v1_logical_runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    attempt_ordinal integer NOT NULL CHECK (attempt_ordinal >= 1),
    exact_execution_spec_hash char(64) NOT NULL CHECK (exact_execution_spec_hash ~ '^[0-9a-f]{64}$'),
    execution_task_id text NOT NULL UNIQUE,
    attempt_state text NOT NULL DEFAULT 'CREATED' CHECK (
        attempt_state IN (
            'CREATED','CLAIMED','ACKNOWLEDGED','RUNNING_CONFIRMED','STALE_UNKNOWN',
            'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
            'CANCELLED','TIMED_OUT','INFRASTRUCTURE_FAILED','CONTRACT_FAILED'
        )
    ),
    retry_of_attempt_id text,
    retry_reason_code text,
    retry_authorization_ref text,
    worker_id text,
    lease_epoch bigint NOT NULL DEFAULT 0 CHECK (lease_epoch >= 0),
    claimed_at_db timestamptz,
    acknowledged_at_db timestamptz,
    started_at_db timestamptz,
    last_heartbeat_at_db timestamptz,
    lease_expires_at_db timestamptz,
    timeout_at_db timestamptz,
    terminal_receipt_ref text UNIQUE,
    terminal_result_ref text,
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    updated_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    UNIQUE (run_id, attempt_ordinal),
    UNIQUE (run_id, run_attempt_id),
    CONSTRAINT v1_retry_same_run_fk
      FOREIGN KEY (run_id, retry_of_attempt_id)
      REFERENCES aaa_ops.v1_run_attempts(run_id, run_attempt_id)
      DEFERRABLE INITIALLY DEFERRED,
    CHECK (
        (attempt_ordinal = 1 AND retry_of_attempt_id IS NULL AND retry_reason_code IS NULL AND retry_authorization_ref IS NULL)
        OR
        (attempt_ordinal > 1 AND retry_of_attempt_id IS NOT NULL AND btrim(retry_reason_code) <> '' AND btrim(retry_authorization_ref) <> '')
    ),
    CHECK (
        attempt_state <> 'RUNNING_CONFIRMED'
        OR (started_at_db IS NOT NULL AND last_heartbeat_at_db IS NOT NULL AND lease_expires_at_db IS NOT NULL)
    ),
    CHECK (
        attempt_state NOT IN (
            'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
            'CANCELLED','TIMED_OUT','INFRASTRUCTURE_FAILED','CONTRACT_FAILED'
        )
        OR terminal_receipt_ref IS NOT NULL
    ),
    CHECK (
        attempt_state IN (
            'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
            'CANCELLED','TIMED_OUT','INFRASTRUCTURE_FAILED','CONTRACT_FAILED'
        )
        OR terminal_receipt_ref IS NULL
    )
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_attempt_identity_guard()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_run_hash char(64);
    v_prev_ordinal integer;
BEGIN
    SELECT exact_execution_spec_hash INTO STRICT v_run_hash
    FROM aaa_ops.v1_logical_runs WHERE run_id = NEW.run_id;
    IF NEW.exact_execution_spec_hash <> v_run_hash THEN
        RAISE EXCEPTION 'ATTEMPT_EXECUTION_SPEC_HASH_MISMATCH_NEW_LOGICAL_RUN_REQUIRED';
    END IF;
    IF NEW.retry_of_attempt_id IS NOT NULL THEN
        SELECT attempt_ordinal INTO STRICT v_prev_ordinal
        FROM aaa_ops.v1_run_attempts
        WHERE run_id = NEW.run_id AND run_attempt_id = NEW.retry_of_attempt_id;
        IF v_prev_ordinal >= NEW.attempt_ordinal THEN
            RAISE EXCEPTION 'RETRY_MUST_REFERENCE_EARLIER_ATTEMPT';
        END IF;
    END IF;
    IF TG_OP = 'UPDATE' THEN
        IF ROW(
            NEW.run_id, NEW.attempt_ordinal, NEW.exact_execution_spec_hash,
            NEW.execution_task_id, NEW.retry_of_attempt_id,
            NEW.retry_reason_code, NEW.retry_authorization_ref
        ) IS DISTINCT FROM ROW(
            OLD.run_id, OLD.attempt_ordinal, OLD.exact_execution_spec_hash,
            OLD.execution_task_id, OLD.retry_of_attempt_id,
            OLD.retry_reason_code, OLD.retry_authorization_ref
        ) THEN
            RAISE EXCEPTION 'RUN_ATTEMPT_IDENTITY_AND_RETRY_LINEAGE_IMMUTABLE';
        END IF;
    END IF;
    NEW.updated_at_db := transaction_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_attempt_identity_guard
BEFORE INSERT OR UPDATE ON aaa_ops.v1_run_attempts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_attempt_identity_guard();

CREATE TABLE aaa_ops.v1_execution_tasks (
    task_id text PRIMARY KEY,
    run_attempt_id text NOT NULL UNIQUE REFERENCES aaa_ops.v1_run_attempts(run_attempt_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    run_id text NOT NULL,
    exact_execution_spec_hash char(64) NOT NULL CHECK (exact_execution_spec_hash ~ '^[0-9a-f]{64}$'),
    execution_profile_ref text NOT NULL,
    execution_profile_sha256 char(64) NOT NULL CHECK (execution_profile_sha256 ~ '^[0-9a-f]{64}$'),
    exact_target_commit char(40) NOT NULL CHECK (exact_target_commit ~ '^[0-9a-f]{40}$'),
    task_state text NOT NULL DEFAULT 'AVAILABLE' CHECK (task_state IN ('AVAILABLE','CLAIMED','ACKNOWLEDGED','RUNNING','TERMINAL')),
    claimed_by text,
    lease_epoch bigint NOT NULL DEFAULT 0 CHECK (lease_epoch >= 0),
    materialized_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    UNIQUE (run_id, run_attempt_id),
    CONSTRAINT v1_task_same_run_attempt_fk
      FOREIGN KEY (run_id, run_attempt_id)
      REFERENCES aaa_ops.v1_run_attempts(run_id, run_attempt_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
);

ALTER TABLE aaa_ops.v1_run_attempts
    ADD CONSTRAINT v1_attempt_task_fk
    FOREIGN KEY (execution_task_id)
    REFERENCES aaa_ops.v1_execution_tasks(task_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE aaa_ops.v1_attempt_termination_receipts (
    attempt_termination_id text PRIMARY KEY,
    run_id text NOT NULL,
    run_attempt_id text NOT NULL UNIQUE,
    termination_class text NOT NULL CHECK (
        termination_class IN (
            'BUSINESS_PASS','BUSINESS_FAIL','BUSINESS_PASS_WITH_FINDINGS',
            'VALIDATION_FAIL','VALIDATION_WITH_FINDINGS','APPLICATION_FAILURE',
            'INPUT_INTEGRITY_FAILURE','EXECUTION_CONTRACT_VIOLATION',
            'SECURITY_POLICY_DENIAL','INFRASTRUCTURE_TRANSIENT','INFRASTRUCTURE_PERMANENT',
            'STALE_LEASE','TIMEOUT','CANCELLED_BY_AUTHORITY','SUPERSEDED','UNKNOWN_FAIL_CLOSED'
        )
    ),
    retryable_disposition text NOT NULL CHECK (
        retryable_disposition IN (
            'RETRYABLE_IF_POLICY_ALLOWS','RETRYABLE_IF_POLICY_ALLOWS_NEW_ATTEMPT',
            'NOT_RETRYABLE','NOT_EXECUTION_RETRY','REQUIRES_NEW_LOGICAL_RUN'
        )
    ),
    actor_ref text NOT NULL CHECK (btrim(actor_ref) <> ''),
    authority_ref text NOT NULL CHECK (btrim(authority_ref) <> ''),
    terminal_result_ref text,
    failure_reason text,
    terminated_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT v1_termination_attempt_fk
      FOREIGN KEY (run_id, run_attempt_id)
      REFERENCES aaa_ops.v1_run_attempts(run_id, run_attempt_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE aaa_ops.v1_logical_run_final_dispositions (
    final_disposition_id text PRIMARY KEY,
    run_id text NOT NULL UNIQUE REFERENCES aaa_ops.v1_logical_runs(run_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    final_status text NOT NULL CHECK (
        final_status IN ('COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS','CANCELLED','SUPERSEDED')
    ),
    selected_attempt_ref text,
    decision_ref text,
    authority_ref text NOT NULL CHECK (btrim(authority_ref) <> ''),
    actor_ref text NOT NULL CHECK (btrim(actor_ref) <> ''),
    decided_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (
        (final_status IN ('COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS') AND selected_attempt_ref IS NOT NULL)
        OR
        (final_status IN ('CANCELLED','SUPERSEDED') AND decision_ref IS NOT NULL)
    )
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_reject_receipt_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'BALANCED_V1_RECEIPT_APPEND_ONLY_IMMUTABLE';
END;
$$;

CREATE TRIGGER trg_v1_attempt_termination_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_attempt_termination_receipts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_receipt_mutation();

CREATE TRIGGER trg_v1_final_disposition_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_logical_run_final_dispositions
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_receipt_mutation();

CREATE OR REPLACE FUNCTION aaa_ops.v1_materialize_run_attempt(
    p_run_id text,
    p_run_attempt_id text,
    p_execution_task_id text,
    p_attempt_ordinal integer,
    p_retry_of_attempt_id text DEFAULT NULL,
    p_retry_reason_code text DEFAULT NULL,
    p_retry_authorization_ref text DEFAULT NULL,
    p_timeout_at timestamptz DEFAULT NULL
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    v_run aaa_ops.v1_logical_runs%ROWTYPE;
    v_expected_ordinal integer;
BEGIN
    SELECT * INTO STRICT v_run
    FROM aaa_ops.v1_logical_runs
    WHERE run_id = p_run_id
    FOR UPDATE;

    IF v_run.logical_status IN (
        'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS','CANCELLED','SUPERSEDED'
    ) THEN
        RAISE EXCEPTION 'LOGICAL_RUN_ALREADY_TERMINAL';
    END IF;

    SELECT COALESCE(max(attempt_ordinal), 0) + 1 INTO v_expected_ordinal
    FROM aaa_ops.v1_run_attempts
    WHERE run_id = p_run_id;

    IF p_attempt_ordinal <> v_expected_ordinal THEN
        RAISE EXCEPTION 'ATTEMPT_ORDINAL_MUST_BE_NEXT_CONTIGUOUS';
    END IF;

    IF p_attempt_ordinal = 1 AND p_retry_of_attempt_id IS NOT NULL THEN
        RAISE EXCEPTION 'FIRST_ATTEMPT_CANNOT_BE_RETRY';
    END IF;

    IF p_attempt_ordinal > 1 AND (
        p_retry_of_attempt_id IS NULL
        OR NULLIF(btrim(p_retry_reason_code), '') IS NULL
        OR NULLIF(btrim(p_retry_authorization_ref), '') IS NULL
    ) THEN
        RAISE EXCEPTION 'RETRY_LINEAGE_AND_AUTHORIZATION_REQUIRED';
    END IF;

    INSERT INTO aaa_ops.v1_run_attempts (
        run_attempt_id, run_id, attempt_ordinal, exact_execution_spec_hash,
        execution_task_id, attempt_state, retry_of_attempt_id, retry_reason_code,
        retry_authorization_ref, timeout_at_db
    ) VALUES (
        p_run_attempt_id, p_run_id, p_attempt_ordinal, v_run.exact_execution_spec_hash,
        p_execution_task_id, 'CREATED', p_retry_of_attempt_id, p_retry_reason_code,
        p_retry_authorization_ref, p_timeout_at
    );

    INSERT INTO aaa_ops.v1_execution_tasks (
        task_id, run_attempt_id, run_id, exact_execution_spec_hash,
        execution_profile_ref, execution_profile_sha256, exact_target_commit, task_state
    ) VALUES (
        p_execution_task_id, p_run_attempt_id, p_run_id, v_run.exact_execution_spec_hash,
        v_run.execution_profile_ref, v_run.execution_profile_sha256, v_run.exact_target_commit, 'AVAILABLE'
    );

    UPDATE aaa_ops.v1_logical_runs
    SET logical_status = CASE WHEN logical_status = 'READY_NOT_DISPATCHED' THEN 'DISPATCHED' ELSE logical_status END
    WHERE run_id = p_run_id;

    RETURN p_run_attempt_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_claim_run_attempt(
    p_execution_task_id text,
    p_worker_id text,
    p_ttl_seconds integer
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_task aaa_ops.v1_execution_tasks%ROWTYPE;
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_epoch bigint;
BEGIN
    IF NULLIF(btrim(p_worker_id), '') IS NULL THEN
        RAISE EXCEPTION 'WORKER_ID_REQUIRED';
    END IF;
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;

    SELECT * INTO STRICT v_task
    FROM aaa_ops.v1_execution_tasks
    WHERE task_id = p_execution_task_id
    FOR UPDATE;
    SELECT * INTO STRICT v_attempt
    FROM aaa_ops.v1_run_attempts
    WHERE run_attempt_id = v_task.run_attempt_id
    FOR UPDATE;

    IF v_task.task_state <> 'AVAILABLE' OR v_attempt.attempt_state <> 'CREATED' THEN
        RAISE EXCEPTION 'ATTEMPT_NOT_AVAILABLE_FOR_CLAIM';
    END IF;

    v_epoch := v_attempt.lease_epoch + 1;

    UPDATE aaa_ops.v1_run_attempts
    SET attempt_state = 'CLAIMED',
        worker_id = p_worker_id,
        lease_epoch = v_epoch,
        claimed_at_db = transaction_timestamp(),
        lease_expires_at_db = transaction_timestamp() + make_interval(secs => p_ttl_seconds)
    WHERE run_attempt_id = v_attempt.run_attempt_id;

    UPDATE aaa_ops.v1_execution_tasks
    SET task_state = 'CLAIMED', claimed_by = p_worker_id, lease_epoch = v_epoch
    WHERE task_id = p_execution_task_id;

    RETURN v_epoch;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_ack_run_attempt(
    p_execution_task_id text,
    p_worker_id text,
    p_lease_epoch bigint
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_task aaa_ops.v1_execution_tasks%ROWTYPE;
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_task FROM aaa_ops.v1_execution_tasks WHERE task_id = p_execution_task_id FOR UPDATE;
    SELECT * INTO STRICT v_attempt FROM aaa_ops.v1_run_attempts WHERE run_attempt_id = v_task.run_attempt_id FOR UPDATE;

    IF v_task.task_state <> 'CLAIMED'
       OR v_attempt.attempt_state <> 'CLAIMED'
       OR v_attempt.worker_id IS DISTINCT FROM p_worker_id
       OR v_attempt.lease_epoch <> p_lease_epoch
       OR v_attempt.lease_expires_at_db IS NULL
       OR v_attempt.lease_expires_at_db < transaction_timestamp() THEN
        RAISE EXCEPTION 'ACK_REQUIRES_CURRENT_CLAIM_AND_UNEXPIRED_LEASE';
    END IF;

    UPDATE aaa_ops.v1_run_attempts
    SET attempt_state = 'ACKNOWLEDGED', acknowledged_at_db = transaction_timestamp()
    WHERE run_attempt_id = v_attempt.run_attempt_id;
    UPDATE aaa_ops.v1_execution_tasks SET task_state = 'ACKNOWLEDGED' WHERE task_id = p_execution_task_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_start_run_attempt(
    p_execution_task_id text,
    p_worker_id text,
    p_lease_epoch bigint
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_task aaa_ops.v1_execution_tasks%ROWTYPE;
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_now timestamptz := transaction_timestamp();
BEGIN
    SELECT * INTO STRICT v_task FROM aaa_ops.v1_execution_tasks WHERE task_id = p_execution_task_id FOR UPDATE;
    SELECT * INTO STRICT v_attempt FROM aaa_ops.v1_run_attempts WHERE run_attempt_id = v_task.run_attempt_id FOR UPDATE;

    IF v_task.task_state <> 'ACKNOWLEDGED'
       OR v_attempt.attempt_state <> 'ACKNOWLEDGED'
       OR v_attempt.worker_id IS DISTINCT FROM p_worker_id
       OR v_attempt.lease_epoch <> p_lease_epoch
       OR v_attempt.lease_expires_at_db IS NULL
       OR v_attempt.lease_expires_at_db < v_now THEN
        RAISE EXCEPTION 'START_REQUIRES_ACK_AND_CURRENT_UNEXPIRED_LEASE';
    END IF;

    UPDATE aaa_ops.v1_run_attempts
    SET attempt_state = 'RUNNING_CONFIRMED',
        started_at_db = v_now,
        last_heartbeat_at_db = v_now
    WHERE run_attempt_id = v_attempt.run_attempt_id;
    UPDATE aaa_ops.v1_execution_tasks SET task_state = 'RUNNING' WHERE task_id = p_execution_task_id;
    UPDATE aaa_ops.v1_logical_runs SET logical_status = 'ACTIVE' WHERE run_id = v_attempt.run_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_heartbeat_run_attempt(
    p_run_attempt_id text,
    p_worker_id text,
    p_lease_epoch bigint,
    p_ttl_seconds integer
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_now timestamptz := transaction_timestamp();
BEGIN
    IF p_ttl_seconds < 60 THEN
        RAISE EXCEPTION 'LEASE_TTL_TOO_SMALL';
    END IF;
    SELECT * INTO STRICT v_attempt
    FROM aaa_ops.v1_run_attempts
    WHERE run_attempt_id = p_run_attempt_id
    FOR UPDATE;

    IF v_attempt.attempt_state <> 'RUNNING_CONFIRMED'
       OR v_attempt.worker_id IS DISTINCT FROM p_worker_id
       OR v_attempt.lease_epoch <> p_lease_epoch
       OR v_attempt.lease_expires_at_db IS NULL
       OR v_attempt.lease_expires_at_db < v_now THEN
        RAISE EXCEPTION 'HEARTBEAT_REQUIRES_CURRENT_UNEXPIRED_ATTEMPT_LEASE';
    END IF;

    UPDATE aaa_ops.v1_run_attempts
    SET last_heartbeat_at_db = v_now,
        lease_expires_at_db = v_now + make_interval(secs => p_ttl_seconds)
    WHERE run_attempt_id = p_run_attempt_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_terminate_run_attempt(
    p_attempt_termination_id text,
    p_run_attempt_id text,
    p_worker_id text,
    p_lease_epoch bigint,
    p_terminal_state text,
    p_termination_class text,
    p_retryable_disposition text,
    p_actor_ref text,
    p_authority_ref text,
    p_terminal_result_ref text DEFAULT NULL,
    p_failure_reason text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_task aaa_ops.v1_execution_tasks%ROWTYPE;
    v_now timestamptz := transaction_timestamp();
BEGIN
    IF p_terminal_state NOT IN (
        'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
        'INFRASTRUCTURE_FAILED','CONTRACT_FAILED'
    ) THEN
        RAISE EXCEPTION 'WORKER_TERMINATION_STATE_NOT_ALLOWED_BY_THIS_FUNCTION';
    END IF;

    SELECT * INTO STRICT v_attempt
    FROM aaa_ops.v1_run_attempts
    WHERE run_attempt_id = p_run_attempt_id
    FOR UPDATE;
    SELECT * INTO STRICT v_task
    FROM aaa_ops.v1_execution_tasks
    WHERE run_attempt_id = p_run_attempt_id
    FOR UPDATE;

    IF v_attempt.attempt_state <> 'RUNNING_CONFIRMED'
       OR v_attempt.worker_id IS DISTINCT FROM p_worker_id
       OR v_attempt.lease_epoch <> p_lease_epoch
       OR v_attempt.lease_expires_at_db IS NULL
       OR v_attempt.lease_expires_at_db < v_now THEN
        RAISE EXCEPTION 'TERMINATION_REQUIRES_CURRENT_UNEXPIRED_ATTEMPT_LEASE';
    END IF;

    IF p_terminal_state IN ('COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS')
       AND NULLIF(btrim(p_terminal_result_ref), '') IS NULL THEN
        RAISE EXCEPTION 'BUSINESS_OR_VALIDATION_TERMINAL_STATE_REQUIRES_RESULT';
    END IF;

    INSERT INTO aaa_ops.v1_attempt_termination_receipts (
        attempt_termination_id, run_id, run_attempt_id, termination_class,
        retryable_disposition, actor_ref, authority_ref, terminal_result_ref,
        failure_reason, terminated_at_db
    ) VALUES (
        p_attempt_termination_id, v_attempt.run_id, p_run_attempt_id, p_termination_class,
        p_retryable_disposition, p_actor_ref, p_authority_ref, p_terminal_result_ref,
        p_failure_reason, v_now
    );

    UPDATE aaa_ops.v1_run_attempts
    SET attempt_state = p_terminal_state,
        terminal_receipt_ref = p_attempt_termination_id,
        terminal_result_ref = p_terminal_result_ref
    WHERE run_attempt_id = p_run_attempt_id;

    UPDATE aaa_ops.v1_execution_tasks
    SET task_state = 'TERMINAL'
    WHERE task_id = v_task.task_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_timeout_run_attempt(
    p_attempt_termination_id text,
    p_run_attempt_id text,
    p_actor_ref text,
    p_authority_ref text,
    p_retryable_disposition text DEFAULT 'RETRYABLE_IF_POLICY_ALLOWS'
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_task aaa_ops.v1_execution_tasks%ROWTYPE;
    v_now timestamptz := transaction_timestamp();
BEGIN
    SELECT * INTO STRICT v_attempt
    FROM aaa_ops.v1_run_attempts
    WHERE run_attempt_id = p_run_attempt_id
    FOR UPDATE;
    SELECT * INTO STRICT v_task
    FROM aaa_ops.v1_execution_tasks
    WHERE run_attempt_id = p_run_attempt_id
    FOR UPDATE;

    IF v_attempt.attempt_state IN (
        'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS',
        'CANCELLED','TIMED_OUT','INFRASTRUCTURE_FAILED','CONTRACT_FAILED'
    ) THEN
        RAISE EXCEPTION 'ATTEMPT_ALREADY_TERMINAL';
    END IF;
    IF v_attempt.timeout_at_db IS NULL OR v_attempt.timeout_at_db > v_now THEN
        RAISE EXCEPTION 'TIMEOUT_NOT_YET_EFFECTIVE';
    END IF;

    INSERT INTO aaa_ops.v1_attempt_termination_receipts (
        attempt_termination_id, run_id, run_attempt_id, termination_class,
        retryable_disposition, actor_ref, authority_ref, terminated_at_db
    ) VALUES (
        p_attempt_termination_id, v_attempt.run_id, p_run_attempt_id, 'TIMEOUT',
        p_retryable_disposition, p_actor_ref, p_authority_ref, v_now
    );

    UPDATE aaa_ops.v1_run_attempts
    SET attempt_state = 'TIMED_OUT', terminal_receipt_ref = p_attempt_termination_id
    WHERE run_attempt_id = p_run_attempt_id;
    UPDATE aaa_ops.v1_execution_tasks SET task_state = 'TERMINAL' WHERE task_id = v_task.task_id;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_finalize_logical_run(
    p_final_disposition_id text,
    p_run_id text,
    p_final_status text,
    p_actor_ref text,
    p_authority_ref text,
    p_selected_attempt_ref text DEFAULT NULL,
    p_decision_ref text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_run aaa_ops.v1_logical_runs%ROWTYPE;
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_expected_attempt_state text;
BEGIN
    SELECT * INTO STRICT v_run
    FROM aaa_ops.v1_logical_runs
    WHERE run_id = p_run_id
    FOR UPDATE;

    IF v_run.logical_status IN (
        'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS','CANCELLED','SUPERSEDED'
    ) OR v_run.final_disposition_ref IS NOT NULL THEN
        RAISE EXCEPTION 'LOGICAL_RUN_ALREADY_TERMINAL';
    END IF;

    IF p_final_status IN ('COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS') THEN
        IF p_selected_attempt_ref IS NULL THEN
            RAISE EXCEPTION 'COMPLETED_LOGICAL_RUN_REQUIRES_SELECTED_ATTEMPT';
        END IF;
        SELECT * INTO STRICT v_attempt
        FROM aaa_ops.v1_run_attempts
        WHERE run_id = p_run_id AND run_attempt_id = p_selected_attempt_ref;
        v_expected_attempt_state := p_final_status;
        IF v_attempt.attempt_state <> v_expected_attempt_state THEN
            RAISE EXCEPTION 'SELECTED_ATTEMPT_TERMINAL_STATE_MISMATCH';
        END IF;
        IF v_attempt.terminal_result_ref IS NULL THEN
            RAISE EXCEPTION 'SELECTED_COMPLETED_ATTEMPT_REQUIRES_RESULT';
        END IF;
    ELSIF p_final_status IN ('CANCELLED','SUPERSEDED') THEN
        IF NULLIF(btrim(p_decision_ref), '') IS NULL THEN
            RAISE EXCEPTION 'CANCEL_OR_SUPERSEDE_REQUIRES_DECISION_REF';
        END IF;
    ELSE
        RAISE EXCEPTION 'INVALID_LOGICAL_RUN_FINAL_STATUS';
    END IF;

    INSERT INTO aaa_ops.v1_logical_run_final_dispositions (
        final_disposition_id, run_id, final_status, selected_attempt_ref,
        decision_ref, authority_ref, actor_ref
    ) VALUES (
        p_final_disposition_id, p_run_id, p_final_status, p_selected_attempt_ref,
        p_decision_ref, p_authority_ref, p_actor_ref
    );

    UPDATE aaa_ops.v1_logical_runs
    SET logical_status = p_final_status, final_disposition_ref = p_final_disposition_id
    WHERE run_id = p_run_id;
END;
$$;

COMMENT ON TABLE aaa_ops.v1_logical_runs IS
'Balanced-v1 Logical Run successor mirror; legacy aaa_ops.runs remains historical and PostgreSQL remains non-authoritative.';
COMMENT ON TABLE aaa_ops.v1_run_attempts IS
'Balanced-v1 concrete execution realizations. No rows are synthesized for legacy T17/T18/T19 runs.';
COMMENT ON TABLE aaa_ops.v1_execution_tasks IS
'One queue materialization per Balanced-v1 RunAttempt; task mechanics are distinct from execution semantics.';
COMMENT ON TABLE aaa_ops.v1_attempt_termination_receipts IS
'Append-only immutable terminal evidence for one Balanced-v1 RunAttempt.';
COMMENT ON TABLE aaa_ops.v1_logical_run_final_dispositions IS
'Append-only immutable final disposition required before a Balanced-v1 Logical Run becomes terminal.';

COMMIT;
