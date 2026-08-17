\set ON_ERROR_STOP on

DO $$
DECLARE
    first_id text;
    retry_id text;
    event_count bigint;
    mismatch_rejected boolean := false;
BEGIN
    first_id := aaa_ops.append_run_event_idempotent(
        'EV-T18-IDEMPOTENT-1',
        'RUN-T18-CONCURRENCY',
        1,
        'LEASE_TEST',
        'worker-a',
        'IDEMP-T18-EXACT-RETRY-1',
        '{"attempt":1,"kind":"exact-retry"}'::jsonb,
        repeat('9', 64)
    );
    retry_id := aaa_ops.append_run_event_idempotent(
        'EV-T18-IDEMPOTENT-1',
        'RUN-T18-CONCURRENCY',
        1,
        'LEASE_TEST',
        'worker-a',
        'IDEMP-T18-EXACT-RETRY-1',
        '{"attempt":1,"kind":"exact-retry"}'::jsonb,
        repeat('9', 64)
    );
    IF first_id <> 'EV-T18-IDEMPOTENT-1' OR retry_id <> first_id THEN
        RAISE EXCEPTION 'EXACT_RETRY_DID_NOT_RETURN_EXISTING_EVENT';
    END IF;
    SELECT count(*) INTO event_count
    FROM aaa_ops.run_events
    WHERE idempotency_key='IDEMP-T18-EXACT-RETRY-1';
    IF event_count <> 1 THEN
        RAISE EXCEPTION 'EXACT_RETRY_CREATED_DUPLICATE:%', event_count;
    END IF;

    BEGIN
        PERFORM aaa_ops.append_run_event_idempotent(
            'EV-T18-IDEMPOTENT-1',
            'RUN-T18-CONCURRENCY',
            1,
            'LEASE_TEST',
            'worker-a',
            'IDEMP-T18-EXACT-RETRY-1',
            '{"attempt":2,"kind":"drift"}'::jsonb,
            repeat('a', 64)
        );
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%IDEMPOTENCY_KEY_REUSE_MISMATCH%' THEN
                mismatch_rejected := true;
            ELSE
                RAISE;
            END IF;
    END;
    IF NOT mismatch_rejected THEN
        RAISE EXCEPTION 'IDEMPOTENCY_DRIFT_WAS_ACCEPTED';
    END IF;
END;
$$;

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state, stale_after_seconds
) VALUES (
    'RUN-T18-ATOMIC', 'T18', 'WO-T18-SMOKE', 'SEMI-CONTROL-ARCHITECT',
    'ENGINEERING_IMPLEMENTATION', 'AofSpds/asset-agent-asa', repeat('5',40),
    'aaa-t18-operational-db-v0.1', 'DISPATCHED_AWAITING_ACK', 7200
);

DO $$
DECLARE
    observed_epoch bigint;
    result_identity text;
    observed_state text;
    observed_result_id text;
    observed_verdict text;
BEGIN
    observed_epoch := aaa_ops.start_run_with_lease('RUN-T18-ATOMIC', 'atomic-worker', 600);
    IF observed_epoch <> 1 THEN
        RAISE EXCEPTION 'ATOMIC_RUN_BAD_EPOCH:%', observed_epoch;
    END IF;
    result_identity := aaa_ops.complete_run_atomic(
        'RUN-T18-ATOMIC',
        'atomic-worker',
        1,
        'RESULT-T18-ATOMIC',
        'PASS_WITH_FINDINGS',
        's3://example/noncanonical/t18-atomic.json',
        repeat('6',64),
        789,
        '{"test":"atomic-completion"}'::jsonb
    );
    IF result_identity <> 'RESULT-T18-ATOMIC' THEN
        RAISE EXCEPTION 'ATOMIC_COMPLETION_RETURN_ID_MISMATCH:%', result_identity;
    END IF;
    SELECT state, terminal_result_id INTO STRICT observed_state, observed_result_id
    FROM aaa_ops.runs WHERE run_id='RUN-T18-ATOMIC';
    SELECT verdict INTO STRICT observed_verdict
    FROM aaa_ops.results WHERE result_id='RESULT-T18-ATOMIC';
    IF observed_state <> 'COMPLETED_WITH_FINDINGS'
       OR observed_result_id <> 'RESULT-T18-ATOMIC'
       OR observed_verdict <> 'PASS_WITH_FINDINGS' THEN
        RAISE EXCEPTION 'ATOMIC_COMPLETION_BINDING_MISMATCH:%:%:%', observed_state, observed_result_id, observed_verdict;
    END IF;
END;
$$;

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state, stale_after_seconds
) VALUES (
    'RUN-T18-ATOMIC-FAIL', 'T18', 'WO-T18-SMOKE', 'SEMI-CONTROL-ARCHITECT',
    'ENGINEERING_IMPLEMENTATION', 'AofSpds/asset-agent-asa', repeat('7',40),
    'aaa-t18-operational-db-v0.1', 'DISPATCHED_AWAITING_ACK', 7200
);

DO $$
DECLARE
    observed_epoch bigint;
    failed boolean := false;
    observed_state text;
    observed_result_id text;
BEGIN
    observed_epoch := aaa_ops.start_run_with_lease('RUN-T18-ATOMIC-FAIL', 'atomic-worker-fail', 600);
    IF observed_epoch <> 1 THEN
        RAISE EXCEPTION 'ATOMIC_FAIL_RUN_BAD_EPOCH:%', observed_epoch;
    END IF;

    BEGIN
        PERFORM aaa_ops.complete_run_atomic(
            'RUN-T18-ATOMIC-FAIL',
            'atomic-worker-fail',
            1,
            'RESULT-T18-ATOMIC',
            'PASS',
            's3://example/noncanonical/should-not-bind.json',
            repeat('8',64),
            111,
            '{"test":"forced-result-id-conflict"}'::jsonb
        );
    EXCEPTION
        WHEN unique_violation THEN
            failed := true;
    END;
    IF NOT failed THEN
        RAISE EXCEPTION 'ATOMIC_FAILURE_INJECTION_DID_NOT_FAIL';
    END IF;

    SELECT state, terminal_result_id INTO STRICT observed_state, observed_result_id
    FROM aaa_ops.runs WHERE run_id='RUN-T18-ATOMIC-FAIL';
    IF observed_state <> 'RUNNING_CONFIRMED' OR observed_result_id IS NOT NULL THEN
        RAISE EXCEPTION 'ATOMIC_FAILURE_LEFT_PARTIAL_TERMINAL_STATE:%:%', observed_state, observed_result_id;
    END IF;

    PERFORM aaa_ops.heartbeat_run('RUN-T18-ATOMIC-FAIL', 'atomic-worker-fail', 1, 600);
END;
$$;

SELECT 'T18_IDEMPOTENT_ATOMIC_SMOKE_PASS' AS result;
