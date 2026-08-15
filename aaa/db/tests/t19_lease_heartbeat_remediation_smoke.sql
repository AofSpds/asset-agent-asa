-- T19 P0 remediation adversarial smoke.
-- Synthetic/noncanonical only. Requires migrations 0001-0005 and t19_execution_runtime_smoke fixtures.

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state,
    started_at, last_heartbeat_at, stale_after_seconds,
    lease_owner, lease_epoch, lease_expires_at
) VALUES (
    'RUN-T19-EXPIRED-LEASE', 'T19-SYNTHETIC-REMEDIATION', 'WO-T19-APPROVED',
    'SEMI-VALIDATION-AUDITOR', 'INDEPENDENT_VALIDATION',
    'AofSpds/asset-agent-asa', '4444444444444444444444444444444444444444',
    'synthetic-t19-remediation', 'RUNNING_CONFIRMED',
    transaction_timestamp() - interval '10 minutes',
    transaction_timestamp() - interval '6 minutes',
    300,
    'worker-a', 7, transaction_timestamp() - interval '1 second'
)
ON CONFLICT (run_id) DO NOTHING;

INSERT INTO aaa_ops.execution_tasks (
    task_id, run_id, execution_profile_id, execution_profile_sha256,
    exact_target_commit, required_persona, required_capability,
    required_permission_level, state, claimed_by, lease_epoch,
    claimed_at_db, acknowledged_at_db, started_at_db
) VALUES (
    'TASK-T19-EXPIRED-LEASE', 'RUN-T19-EXPIRED-LEASE',
    'AAA_VALIDATION_EXACT_GIT_V0_1',
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    '4444444444444444444444444444444444444444',
    'SEMI-VALIDATION-AUDITOR', 'INDEPENDENT_VALIDATION', 1,
    'RUNNING', 'worker-a', 7,
    transaction_timestamp() - interval '10 minutes',
    transaction_timestamp() - interval '10 minutes',
    transaction_timestamp() - interval '10 minutes'
)
ON CONFLICT (task_id) DO NOTHING;

DO $$
BEGIN
    IF (SELECT effective_state FROM aaa_ops.run_projection WHERE run_id='RUN-T19-EXPIRED-LEASE') <> 'STALE_UNKNOWN' THEN
        RAISE EXCEPTION 'EXPIRED_LEASE_NOT_PROJECTED_STALE_UNKNOWN';
    END IF;

    BEGIN
        PERFORM aaa_ops.heartbeat_execution_task('TASK-T19-EXPIRED-LEASE', 'worker-a', 7, 300);
        RAISE EXCEPTION 'EXPECTED_EXPIRED_SAME_EPOCH_HEARTBEAT_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_EXPIRED_SAME_EPOCH_HEARTBEAT_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%STALE_OR_INVALID_LEASE%' THEN
            RAISE;
        END IF;
    END;

    IF (SELECT lease_epoch FROM aaa_ops.runs WHERE run_id='RUN-T19-EXPIRED-LEASE') <> 7 THEN
        RAISE EXCEPTION 'EXPIRED_HEARTBEAT_CHANGED_EPOCH';
    END IF;
    IF (SELECT lease_expires_at FROM aaa_ops.runs WHERE run_id='RUN-T19-EXPIRED-LEASE') >= transaction_timestamp() THEN
        RAISE EXCEPTION 'EXPIRED_HEARTBEAT_RESURRECTED_LEASE';
    END IF;
    IF (SELECT effective_state FROM aaa_ops.run_projection WHERE run_id='RUN-T19-EXPIRED-LEASE') <> 'STALE_UNKNOWN' THEN
        RAISE EXCEPTION 'STALE_UNKNOWN_SELF_REVIVED';
    END IF;
END
$$;

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.complete_execution_task_atomic(
            'TASK-T19-EXPIRED-LEASE', 'worker-a', 7,
            'RESULT-T19-EXPIRED-ILLEGAL', 'PASS',
            'synthetic://t19/expired-illegal.json',
            'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
            1, '{"synthetic":true}'::jsonb
        );
        RAISE EXCEPTION 'EXPECTED_EXPIRED_LEASE_TERMINAL_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_EXPIRED_LEASE_TERMINAL_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%STALE_OR_INVALID_LEASE%' THEN
            RAISE;
        END IF;
    END;
END
$$;

DO $$
DECLARE
    next_epoch bigint;
BEGIN
    next_epoch := aaa_ops.acquire_run_lease('RUN-T19-EXPIRED-LEASE', 'worker-b', 300);
    IF next_epoch <> 8 THEN
        RAISE EXCEPTION 'TAKEOVER_DID_NOT_INCREMENT_EPOCH';
    END IF;
    IF (SELECT lease_owner FROM aaa_ops.runs WHERE run_id='RUN-T19-EXPIRED-LEASE') <> 'worker-b' THEN
        RAISE EXCEPTION 'TAKEOVER_OWNER_NOT_REBOUND';
    END IF;
END
$$;

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_execution_task('TASK-T19-EXPIRED-LEASE', 'worker-a', 7, 300);
        RAISE EXCEPTION 'EXPECTED_OLD_EPOCH_HEARTBEAT_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_OLD_EPOCH_HEARTBEAT_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%STALE_OR_INVALID_LEASE%' THEN
            RAISE;
        END IF;
    END;

    BEGIN
        PERFORM aaa_ops.complete_execution_task_atomic(
            'TASK-T19-EXPIRED-LEASE', 'worker-a', 7,
            'RESULT-T19-OLD-EPOCH-ILLEGAL', 'PASS',
            'synthetic://t19/old-epoch-illegal.json',
            'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',
            1, '{"synthetic":true}'::jsonb
        );
        RAISE EXCEPTION 'EXPECTED_OLD_EPOCH_TERMINAL_REJECTION';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EXPECTED_OLD_EPOCH_TERMINAL_REJECTION' THEN
            RAISE;
        END IF;
        IF SQLERRM NOT LIKE '%STALE_OR_INVALID_LEASE%' THEN
            RAISE;
        END IF;
    END;
END
$$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM aaa_ops.results WHERE result_id IN ('RESULT-T19-EXPIRED-ILLEGAL','RESULT-T19-OLD-EPOCH-ILLEGAL')) THEN
        RAISE EXCEPTION 'STALE_AUTHORITY_CREATED_TERMINAL_RESULT';
    END IF;
END
$$;
