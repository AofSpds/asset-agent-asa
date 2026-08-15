-- T19 software execution-plane contract smoke.
-- All identities are synthetic and noncanonical.

INSERT INTO aaa_ops.work_order_refs (
    work_order_id, git_repository, git_path, git_commit_or_blob_identity,
    approval_state, approval_identity, approval_git_identity
) VALUES
('WO-T19-APPROVED', 'AofSpds/asset-agent-asa', 'synthetic/approved', 't19-approved',
 'OWNER_APPROVED_READY_FOR_EXECUTION', 'PROJECT_OWNER', 'synthetic-owner-approval'),
('WO-T19-UNAPPROVED', 'AofSpds/asset-agent-asa', 'synthetic/unapproved', 't19-unapproved',
 'UNKNOWN', NULL, NULL)
ON CONFLICT (work_order_id) DO NOTHING;

INSERT INTO aaa_ops.execution_profiles (
    execution_profile_id, version, git_identity, profile_sha256,
    allowed_personas, required_capability, minimum_permission_level,
    timeout_seconds, network_policy, filesystem_policy
) VALUES (
    'AAA_VALIDATION_EXACT_GIT_V0_1', 'v0.1', 'synthetic-profile-git',
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    ARRAY['SEMI-VALIDATION-AUDITOR'], 'INDEPENDENT_VALIDATION', 1,
    900, 'DENY', 'READ_ONLY_EXACT_CHECKOUT'
)
ON CONFLICT (execution_profile_id) DO NOTHING;

INSERT INTO aaa_ops.workers (
    worker_id, worker_type, runtime_version, host_identity,
    capabilities, authorized_personas, permission_level,
    max_concurrency, enabled
) VALUES
('worker-a', 'CI_VALIDATION_WORKER', 'v0.1', 'ci-a',
 ARRAY['INDEPENDENT_VALIDATION'], ARRAY['SEMI-VALIDATION-AUDITOR'], 1, 1, true),
('worker-b', 'CI_VALIDATION_WORKER', 'v0.1', 'ci-b',
 ARRAY['INDEPENDENT_VALIDATION'], ARRAY['SEMI-VALIDATION-AUDITOR'], 1, 1, true),
('worker-no-cap', 'DETERMINISTIC_LOCAL_WORKER', 'v0.1', 'ci-no-cap',
 ARRAY['OTHER'], ARRAY['SEMI-VALIDATION-AUDITOR'], 1, 1, true)
ON CONFLICT (worker_id) DO NOTHING;

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state, stale_after_seconds
) VALUES
('RUN-T19-MAIN', 'T19-SYNTHETIC', 'WO-T19-APPROVED',
 'SEMI-VALIDATION-AUDITOR', 'INDEPENDENT_VALIDATION',
 'AofSpds/asset-agent-asa', '1111111111111111111111111111111111111111',
 'synthetic-t19', 'DISPATCHED_AWAITING_ACK', 300),
('RUN-T19-UNAPPROVED', 'T19-SYNTHETIC', 'WO-T19-UNAPPROVED',
 'SEMI-VALIDATION-AUDITOR', 'INDEPENDENT_VALIDATION',
 'AofSpds/asset-agent-asa', '2222222222222222222222222222222222222222',
 'synthetic-t19', 'DISPATCHED_AWAITING_ACK', 300),
('RUN-T19-CONCURRENCY', 'T19-SYNTHETIC', 'WO-T19-APPROVED',
 'SEMI-VALIDATION-AUDITOR', 'INDEPENDENT_VALIDATION',
 'AofSpds/asset-agent-asa', '3333333333333333333333333333333333333333',
 'synthetic-t19', 'DISPATCHED_AWAITING_ACK', 300)
ON CONFLICT (run_id) DO NOTHING;

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.materialize_execution_task(
            'TASK-T19-UNAPPROVED', 'RUN-T19-UNAPPROVED',
            'AAA_VALIDATION_EXACT_GIT_V0_1',
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            '2222222222222222222222222222222222222222',
            'INDEPENDENT_VALIDATION', 1, NULL
        );
        RAISE EXCEPTION 'EXPECTED_UNAPPROVED_WORK_ORDER_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_UNAPPROVED_WORK_ORDER_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%WORK_ORDER_NOT_APPROVED_FOR_EXECUTION%' THEN
            RAISE;
        END IF;
    END;
END
$$;

SELECT aaa_ops.materialize_execution_task(
    'TASK-T19-MAIN', 'RUN-T19-MAIN',
    'AAA_VALIDATION_EXACT_GIT_V0_1',
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    '1111111111111111111111111111111111111111',
    'INDEPENDENT_VALIDATION', 1, NULL
);

SELECT aaa_ops.materialize_execution_task(
    'TASK-T19-MAIN', 'RUN-T19-MAIN',
    'AAA_VALIDATION_EXACT_GIT_V0_1',
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    '1111111111111111111111111111111111111111',
    'INDEPENDENT_VALIDATION', 1, NULL
);

DO $$
BEGIN
    IF (SELECT state FROM aaa_ops.execution_tasks WHERE task_id='TASK-T19-MAIN') <> 'AVAILABLE' THEN
        RAISE EXCEPTION 'TASK_NOT_AVAILABLE_AFTER_DISPATCH';
    END IF;
    IF (SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') <> 'DISPATCHED_AWAITING_ACK' THEN
        RAISE EXCEPTION 'DISPATCH_MUTATED_RUN_STATE';
    END IF;
    IF (SELECT started_at FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') IS NOT NULL THEN
        RAISE EXCEPTION 'DISPATCH_FABRICATED_START';
    END IF;
END
$$;

DO $$
DECLARE
    c integer;
BEGIN
    SELECT count(*) INTO c FROM aaa_ops.claim_next_execution_task('worker-no-cap', 300);
    IF c <> 0 THEN
        RAISE EXCEPTION 'UNAUTHORIZED_WORKER_CLAIMED_TASK';
    END IF;
END
$$;

SELECT * FROM aaa_ops.claim_next_execution_task('worker-a', 300);

DO $$
BEGIN
    IF (SELECT state FROM aaa_ops.execution_tasks WHERE task_id='TASK-T19-MAIN') <> 'CLAIMED' THEN
        RAISE EXCEPTION 'TASK_NOT_CLAIMED';
    END IF;
    IF (SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') <> 'DISPATCHED_AWAITING_ACK' THEN
        RAISE EXCEPTION 'CLAIM_FALSELY_MARKED_RUNNING';
    END IF;
    IF (SELECT started_at FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') IS NOT NULL THEN
        RAISE EXCEPTION 'CLAIM_FABRICATED_START';
    END IF;
END
$$;

SELECT aaa_ops.ack_execution_task('TASK-T19-MAIN', 'worker-a', 1);

DO $$
BEGIN
    IF (SELECT state FROM aaa_ops.execution_tasks WHERE task_id='TASK-T19-MAIN') <> 'ACKNOWLEDGED' THEN
        RAISE EXCEPTION 'ACK_NOT_RECORDED';
    END IF;
    IF (SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') <> 'DISPATCHED_AWAITING_ACK' THEN
        RAISE EXCEPTION 'ACK_FALSELY_MARKED_RUNNING';
    END IF;
END
$$;

SELECT aaa_ops.start_execution_task('TASK-T19-MAIN', 'worker-a', 1, 300);

DO $$
BEGIN
    IF (SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') <> 'RUNNING_CONFIRMED' THEN
        RAISE EXCEPTION 'START_DID_NOT_CONFIRM_RUNNING';
    END IF;
    IF (SELECT started_at FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') IS NULL
       OR (SELECT last_heartbeat_at FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') IS NULL THEN
        RAISE EXCEPTION 'RUNNING_WITHOUT_TIME_EVIDENCE';
    END IF;
END
$$;

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_execution_task('TASK-T19-MAIN', 'worker-a', 0, 300);
        RAISE EXCEPTION 'EXPECTED_STALE_TOKEN_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_STALE_TOKEN_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%TASK_NOT_RUNNING_UNDER_CURRENT_LEASE%' THEN
            RAISE;
        END IF;
    END;
END
$$;

SELECT aaa_ops.heartbeat_execution_task('TASK-T19-MAIN', 'worker-a', 1, 300);

SELECT aaa_ops.complete_execution_task_atomic(
    'TASK-T19-MAIN', 'worker-a', 1,
    'RESULT-T19-MAIN', 'PASS',
    'synthetic://t19/result-main.json',
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    123,
    '{"synthetic":true}'::jsonb
);

DO $$
BEGIN
    IF (SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T19-MAIN') <> 'COMPLETED_PASS' THEN
        RAISE EXCEPTION 'RUN_NOT_TERMINAL_PASS';
    END IF;
    IF (SELECT state FROM aaa_ops.execution_tasks WHERE task_id='TASK-T19-MAIN') <> 'TERMINAL' THEN
        RAISE EXCEPTION 'TASK_NOT_TERMINAL';
    END IF;
    IF (SELECT terminal_result_id FROM aaa_ops.execution_tasks WHERE task_id='TASK-T19-MAIN') <> 'RESULT-T19-MAIN' THEN
        RAISE EXCEPTION 'TASK_RESULT_NOT_BOUND';
    END IF;
END
$$;

SELECT aaa_ops.materialize_execution_task(
    'TASK-T19-CONCURRENCY', 'RUN-T19-CONCURRENCY',
    'AAA_VALIDATION_EXACT_GIT_V0_1',
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    '3333333333333333333333333333333333333333',
    'INDEPENDENT_VALIDATION', 1, NULL
);
