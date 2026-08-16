\set ON_ERROR_STOP on

BEGIN;

INSERT INTO aaa_ops.v1_logical_runs (
    run_id, project_namespace, process_id, work_order_ref, responsible_persona,
    executor_role, repository_identity, exact_target_commit, exact_execution_spec_hash,
    execution_profile_ref, execution_profile_sha256, configuration_sha256,
    material_input_refs, schema_family_version_refs
) VALUES (
    'RUN-V1-E2-SMOKE', 'SEMICONDUCTOR_RESEARCH', 'E2-SMOKE', 'WO-E2-SMOKE',
    'SEMI-CONTROL-ARCHITECT', 'BOUNDED_ENGINEERING_IMPLEMENTATION',
    'github-repo-id:1334403184', repeat('a', 40), repeat('b', 64),
    'PROFILE-E2-SMOKE', repeat('c', 64), repeat('d', 64),
    '[]'::jsonb, '[]'::jsonb
);

-- First Attempt and task are materialized atomically. Dispatch/task availability is not running.
SELECT aaa_ops.v1_materialize_run_attempt(
    'RUN-V1-E2-SMOKE', 'ATT-E2-1', 'TASK-E2-1', 1, NULL, NULL, NULL,
    transaction_timestamp() - interval '1 second'
);

DO $$
BEGIN
    IF (SELECT attempt_state FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') <> 'CREATED' THEN
        RAISE EXCEPTION 'MATERIALIZATION_FALSELY_MARKED_ATTEMPT_RUNNING';
    END IF;
    IF (SELECT task_state FROM aaa_ops.v1_execution_tasks WHERE task_id='TASK-E2-1') <> 'AVAILABLE' THEN
        RAISE EXCEPTION 'TASK_NOT_AVAILABLE_AFTER_MATERIALIZATION';
    END IF;
END $$;

-- Attempt ordinal must be contiguous and unique within Logical Run.
DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.v1_materialize_run_attempt(
            'RUN-V1-E2-SMOKE', 'ATT-E2-BAD-ORDINAL', 'TASK-E2-BAD-ORDINAL', 3,
            'ATT-E2-1', 'RETRY', 'AUTH-RETRY'
        );
        RAISE EXCEPTION 'NONCONTIGUOUS_ATTEMPT_ORDINAL_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'NONCONTIGUOUS_ATTEMPT_ORDINAL_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

-- Claim does not imply ACK or start.
SELECT aaa_ops.v1_claim_run_attempt('TASK-E2-1', 'worker-e2', 300);
DO $$
BEGIN
    IF (SELECT attempt_state FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') <> 'CLAIMED' THEN
        RAISE EXCEPTION 'CLAIM_STATE_WRONG';
    END IF;
    IF (SELECT started_at_db FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') IS NOT NULL THEN
        RAISE EXCEPTION 'CLAIM_FABRICATED_START';
    END IF;
END $$;

SELECT aaa_ops.v1_ack_run_attempt('TASK-E2-1', 'worker-e2', 1);
DO $$
BEGIN
    IF (SELECT attempt_state FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') <> 'ACKNOWLEDGED' THEN
        RAISE EXCEPTION 'ACK_STATE_WRONG';
    END IF;
    IF (SELECT started_at_db FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') IS NOT NULL THEN
        RAISE EXCEPTION 'ACK_FABRICATED_START';
    END IF;
END $$;

SELECT aaa_ops.v1_start_run_attempt('TASK-E2-1', 'worker-e2', 1);
DO $$
BEGIN
    IF (SELECT attempt_state FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') <> 'RUNNING_CONFIRMED' THEN
        RAISE EXCEPTION 'START_DID_NOT_CONFIRM_RUNNING';
    END IF;
    IF (SELECT started_at_db IS NULL OR last_heartbeat_at_db IS NULL FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') THEN
        RAISE EXCEPTION 'RUNNING_MISSING_START_OR_HEARTBEAT';
    END IF;
END $$;

-- Expired same-epoch lease may not heartbeat or worker-terminalize.
UPDATE aaa_ops.v1_run_attempts
SET lease_expires_at_db = transaction_timestamp() - interval '1 second'
WHERE run_attempt_id='ATT-E2-1';

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.v1_heartbeat_run_attempt('ATT-E2-1', 'worker-e2', 1, 300);
        RAISE EXCEPTION 'EXPIRED_LEASE_HEARTBEAT_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPIRED_LEASE_HEARTBEAT_ACCEPTED' THEN RAISE; END IF;
    END;
    BEGIN
        PERFORM aaa_ops.v1_terminate_run_attempt(
            'TERM-E2-BAD', 'ATT-E2-1', 'worker-e2', 1,
            'COMPLETED_PASS', 'BUSINESS_PASS', 'NOT_EXECUTION_RETRY',
            'WORKER-E2', 'AUTH-E2', 'RESULT-E2-BAD'
        );
        RAISE EXCEPTION 'EXPIRED_LEASE_TERMINATION_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPIRED_LEASE_TERMINATION_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

-- Governed timeout terminates the Attempt but not the Logical Run.
SELECT aaa_ops.v1_timeout_run_attempt(
    'TERM-E2-TIMEOUT-1', 'ATT-E2-1', 'TIMER-SERVICE', 'AUTH-TIMEOUT',
    'RETRYABLE_IF_POLICY_ALLOWS'
);
DO $$
BEGIN
    IF (SELECT attempt_state FROM aaa_ops.v1_run_attempts WHERE run_attempt_id='ATT-E2-1') <> 'TIMED_OUT' THEN
        RAISE EXCEPTION 'TIMEOUT_DID_NOT_TERMINATE_ATTEMPT';
    END IF;
    IF (SELECT logical_status FROM aaa_ops.v1_logical_runs WHERE run_id='RUN-V1-E2-SMOKE') IN (
        'COMPLETED_PASS','COMPLETED_FAIL','COMPLETED_WITH_FINDINGS','CANCELLED','SUPERSEDED'
    ) THEN
        RAISE EXCEPTION 'RETRYABLE_TIMEOUT_FALSELY_TERMINALIZED_LOGICAL_RUN';
    END IF;
END $$;

-- Same immutable Logical Run gets a new retry Attempt with exact lineage.
SELECT aaa_ops.v1_materialize_run_attempt(
    'RUN-V1-E2-SMOKE', 'ATT-E2-2', 'TASK-E2-2', 2,
    'ATT-E2-1', 'TIMEOUT_RETRY', 'AUTH-RETRY-1'
);

-- Direct attempt with a changed execution-spec hash must fail closed, representing a new Logical Run instead.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_run_attempts(
            run_attempt_id, run_id, attempt_ordinal, exact_execution_spec_hash,
            execution_task_id, retry_of_attempt_id, retry_reason_code, retry_authorization_ref
        ) VALUES (
            'ATT-E2-WRONG-SPEC', 'RUN-V1-E2-SMOKE', 3, repeat('e', 64),
            'TASK-E2-WRONG-SPEC', 'ATT-E2-2', 'CHANGED_SPEC', 'AUTH-RETRY-2'
        );
        RAISE EXCEPTION 'CHANGED_SPEC_ACCEPTED_AS_SAME_LOGICAL_RUN';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'CHANGED_SPEC_ACCEPTED_AS_SAME_LOGICAL_RUN' THEN RAISE; END IF;
    END;
END $$;

SELECT aaa_ops.v1_claim_run_attempt('TASK-E2-2', 'worker-e2', 300);
SELECT aaa_ops.v1_ack_run_attempt('TASK-E2-2', 'worker-e2', 1);
SELECT aaa_ops.v1_start_run_attempt('TASK-E2-2', 'worker-e2', 1);
SELECT aaa_ops.v1_terminate_run_attempt(
    'TERM-E2-PASS-2', 'ATT-E2-2', 'worker-e2', 1,
    'COMPLETED_PASS', 'BUSINESS_PASS', 'NOT_EXECUTION_RETRY',
    'WORKER-E2', 'AUTH-E2', 'RESULT-E2-SMOKE'
);

-- Logical Run remains nonterminal until a separate immutable Final Disposition Receipt selects the terminal Attempt.
DO $$
BEGIN
    IF (SELECT logical_status FROM aaa_ops.v1_logical_runs WHERE run_id='RUN-V1-E2-SMOKE') = 'COMPLETED_PASS' THEN
        RAISE EXCEPTION 'ATTEMPT_PASS_FALSELY_TERMINALIZED_LOGICAL_RUN';
    END IF;
END $$;

SELECT aaa_ops.v1_finalize_logical_run(
    'FINAL-E2-PASS', 'RUN-V1-E2-SMOKE', 'COMPLETED_PASS',
    'CONTROL-ACTOR', 'CONTROL-AUTHORITY', 'ATT-E2-2', NULL
);

DO $$
BEGIN
    IF (SELECT logical_status FROM aaa_ops.v1_logical_runs WHERE run_id='RUN-V1-E2-SMOKE') <> 'COMPLETED_PASS' THEN
        RAISE EXCEPTION 'FINAL_DISPOSITION_DID_NOT_TERMINALIZE_LOGICAL_RUN';
    END IF;
    IF (SELECT final_disposition_ref FROM aaa_ops.v1_logical_runs WHERE run_id='RUN-V1-E2-SMOKE') <> 'FINAL-E2-PASS' THEN
        RAISE EXCEPTION 'FINAL_DISPOSITION_REF_MISSING';
    END IF;
END $$;

-- Receipts are append-only immutable.
DO $$
BEGIN
    BEGIN
        UPDATE aaa_ops.v1_attempt_termination_receipts
        SET failure_reason='MUTATED'
        WHERE attempt_termination_id='TERM-E2-PASS-2';
        RAISE EXCEPTION 'ATTEMPT_TERMINATION_RECEIPT_MUTABLE';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'ATTEMPT_TERMINATION_RECEIPT_MUTABLE' THEN RAISE; END IF;
    END;
    BEGIN
        DELETE FROM aaa_ops.v1_logical_run_final_dispositions
        WHERE final_disposition_id='FINAL-E2-PASS';
        RAISE EXCEPTION 'FINAL_DISPOSITION_RECEIPT_MUTABLE';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'FINAL_DISPOSITION_RECEIPT_MUTABLE' THEN RAISE; END IF;
    END;
END $$;

-- E2 migration is additive: legacy runs remain legacy and no successor Attempt is synthesized for them.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM aaa_ops.v1_run_attempts a
        JOIN aaa_ops.runs legacy ON legacy.run_id = a.run_id
    ) THEN
        RAISE EXCEPTION 'LEGACY_RUN_WAS_SYNTHESIZED_INTO_BALANCED_V1_ATTEMPT';
    END IF;
END $$;

ROLLBACK;
