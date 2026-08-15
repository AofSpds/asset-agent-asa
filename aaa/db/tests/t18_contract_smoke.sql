\set ON_ERROR_STOP on

INSERT INTO aaa_ops.work_order_refs (
    work_order_id, git_repository, git_path, git_commit_or_blob_identity, content_sha256
) VALUES (
    'WO-T18-SMOKE',
    'AofSpds/asset-agent-asa',
    'control/workorders/WO-T18-SMOKE.yaml',
    repeat('a', 40),
    repeat('b', 64)
);

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state, stale_after_seconds
) VALUES (
    'RUN-T18-SMOKE',
    'T18',
    'WO-T18-SMOKE',
    'SEMI-CONTROL-ARCHITECT',
    'ENGINEERING_IMPLEMENTATION',
    'AofSpds/asset-agent-asa',
    repeat('c', 40),
    'aaa-t18-operational-db-v0.1',
    'DISPATCHED_AWAITING_ACK',
    7200
);

DO $$
DECLARE
    observed_epoch bigint;
    observed_effective_state text;
BEGIN
    observed_epoch := aaa_ops.start_run_with_lease('RUN-T18-SMOKE', 'worker-a', 600);
    IF observed_epoch <> 1 THEN
        RAISE EXCEPTION 'UNEXPECTED_INITIAL_LEASE_EPOCH:%', observed_epoch;
    END IF;
    SELECT effective_state INTO STRICT observed_effective_state
    FROM aaa_ops.run_projection
    WHERE run_id='RUN-T18-SMOKE';
    IF observed_effective_state <> 'RUNNING_CONFIRMED' THEN
        RAISE EXCEPTION 'RUN_DID_NOT_PROJECT_RUNNING_CONFIRMED:%', observed_effective_state;
    END IF;
END;
$$;

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_run('RUN-T18-SMOKE', 'worker-a', 0, 600);
        RAISE EXCEPTION 'EXPECTED_STALE_FENCING_REJECTION';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE '%STALE_OR_INVALID_LEASE%' THEN
                RAISE;
            END IF;
    END;
END;
$$;

SELECT aaa_ops.heartbeat_run('RUN-T18-SMOKE', 'worker-a', 1, 600);

INSERT INTO aaa_ops.run_events (
    event_id, run_id, sequence_number, event_type, actor_identity,
    idempotency_key, payload_jsonb, payload_sha256
) VALUES (
    'EV-T18-SMOKE-1',
    'RUN-T18-SMOKE',
    1,
    'HEARTBEAT',
    'worker-a',
    'IDEMP-T18-SMOKE-1',
    '{"source":"postgres-smoke"}'::jsonb,
    repeat('d', 64)
);

DO $$
BEGIN
    BEGIN
        UPDATE aaa_ops.run_events SET event_type='MUTATED' WHERE event_id='EV-T18-SMOKE-1';
        RAISE EXCEPTION 'EXPECTED_APPEND_ONLY_REJECTION';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE '%RUN_EVENTS_APPEND_ONLY%' THEN
                RAISE;
            END IF;
    END;
END;
$$;

BEGIN;
INSERT INTO aaa_ops.results (
    result_id, run_id, work_order_id, verdict, artifact_locator,
    artifact_sha256, artifact_byte_size, repository, exact_target_commit, metadata_jsonb
) VALUES (
    'RESULT-T18-SMOKE',
    'RUN-T18-SMOKE',
    'WO-T18-SMOKE',
    'PASS',
    's3://example/noncanonical/t18-smoke.json',
    repeat('e', 64),
    123,
    'AofSpds/asset-agent-asa',
    repeat('c', 40),
    '{"canonical":false}'::jsonb
);
UPDATE aaa_ops.runs
SET state='COMPLETED_PASS',
    terminal_result_id='RESULT-T18-SMOKE',
    lease_owner=NULL,
    lease_expires_at=NULL,
    row_version=row_version+1,
    updated_at_db=transaction_timestamp()
WHERE run_id='RUN-T18-SMOKE';
COMMIT;

DO $$
DECLARE
    observed_state text;
    observed_verdict text;
BEGIN
    SELECT state INTO STRICT observed_state FROM aaa_ops.runs WHERE run_id='RUN-T18-SMOKE';
    SELECT verdict INTO STRICT observed_verdict FROM aaa_ops.results WHERE result_id='RESULT-T18-SMOKE';
    IF observed_state <> 'COMPLETED_PASS' THEN
        RAISE EXCEPTION 'TERMINAL_TRANSITION_FAILED:%', observed_state;
    END IF;
    IF observed_verdict <> 'PASS' THEN
        RAISE EXCEPTION 'RESULT_BINDING_FAILED:%', observed_verdict;
    END IF;
END;
$$;

DO $$
DECLARE
    rejected boolean := false;
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_run('RUN-T18-SMOKE', 'worker-a', 1, 600);
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%STALE_OR_INVALID_LEASE%' THEN
                rejected := true;
            ELSE
                RAISE;
            END IF;
    END;
    IF NOT rejected THEN
        RAISE EXCEPTION 'TERMINAL_RUN_ACCEPTED_HEARTBEAT';
    END IF;
END;
$$;

DO $$
DECLARE
    rejected boolean := false;
BEGIN
    BEGIN
        INSERT INTO aaa_ops.runs (
            run_id, process_id, work_order_id, responsible_persona, executor_role,
            repository, exact_target_commit, branch_context, state,
            started_at, last_heartbeat_at, stale_after_seconds
        ) VALUES (
            'RUN-T18-BAD-TIME', 'T18', 'WO-T18-SMOKE', 'SEMI-CONTROL-ARCHITECT',
            'ENGINEERING_IMPLEMENTATION', 'AofSpds/asset-agent-asa', repeat('7',40),
            'aaa-t18-operational-db-v0.1', 'RUNNING_CONFIRMED',
            transaction_timestamp(), transaction_timestamp() - interval '1 minute', 7200
        );
    EXCEPTION
        WHEN check_violation THEN
            rejected := true;
    END;
    IF NOT rejected THEN
        RAISE EXCEPTION 'HEARTBEAT_BEFORE_START_WAS_ACCEPTED';
    END IF;
END;
$$;

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state,
    started_at, last_heartbeat_at, stale_after_seconds,
    lease_owner, lease_epoch, lease_expires_at
) VALUES (
    'RUN-T18-FUTURE-TIME', 'T18', 'WO-T18-SMOKE', 'SEMI-CONTROL-ARCHITECT',
    'ENGINEERING_IMPLEMENTATION', 'AofSpds/asset-agent-asa', repeat('8',40),
    'aaa-t18-operational-db-v0.1', 'RUNNING_CONFIRMED',
    transaction_timestamp() + interval '1 day',
    transaction_timestamp() + interval '1 day 1 minute',
    7200, 'future-worker', 1, transaction_timestamp() + interval '1 day 10 minutes'
);

DO $$
DECLARE
    observed text;
BEGIN
    SELECT effective_state INTO STRICT observed
    FROM aaa_ops.run_projection
    WHERE run_id='RUN-T18-FUTURE-TIME';
    IF observed <> 'STALE_UNKNOWN' THEN
        RAISE EXCEPTION 'FUTURE_TIME_FALSE_RUNNING:%', observed;
    END IF;
END;
$$;

INSERT INTO aaa_ops.snapshot_refs (
    snapshot_id, pit_cutoff, artifact_locator, artifact_sha256,
    artifact_byte_size, lineage_identity, source_release_identity
) VALUES (
    'SNAPSHOT-T18-SMOKE',
    '2026-08-16T06:00:00+09:00'::timestamptz,
    's3://example/noncanonical/snapshot-t18-smoke.parquet',
    repeat('f', 64),
    456,
    'LINEAGE-T18-SMOKE',
    'RELEASE-NONCANONICAL'
);

INSERT INTO aaa_ops.experiments (
    experiment_id, experiment_type, model_spec_git_identity,
    feature_spec_git_identity, dataset_identity, snapshot_identity,
    configuration_sha256, seed_policy, status
) VALUES (
    'EXP-T18-SMOKE',
    'BACKTEST',
    repeat('1', 40),
    repeat('2', 40),
    'DATASET-T18-SMOKE',
    'SNAPSHOT-T18-SMOKE',
    repeat('3', 64),
    '{"kind":"fixed","seed":7}'::jsonb,
    'ENGINEERING_ONLY'
);

INSERT INTO aaa_ops.experiment_runs (
    experiment_id, run_id, experiment_role
) VALUES (
    'EXP-T18-SMOKE',
    'RUN-T18-SMOKE',
    'PRIMARY'
);

INSERT INTO aaa_ops.runs (
    run_id, process_id, work_order_id, responsible_persona, executor_role,
    repository, exact_target_commit, branch_context, state, stale_after_seconds
) VALUES (
    'RUN-T18-CONCURRENCY',
    'T18',
    'WO-T18-SMOKE',
    'SEMI-CONTROL-ARCHITECT',
    'ENGINEERING_IMPLEMENTATION',
    'AofSpds/asset-agent-asa',
    repeat('4', 40),
    'aaa-t18-operational-db-v0.1',
    'DISPATCHED_AWAITING_ACK',
    7200
);

DO $$
DECLARE
    observed_experiment_links bigint;
    observed_snapshot_count bigint;
BEGIN
    SELECT count(*) INTO observed_experiment_links
    FROM aaa_ops.experiment_runs
    WHERE experiment_id='EXP-T18-SMOKE' AND run_id='RUN-T18-SMOKE';
    SELECT count(*) INTO observed_snapshot_count
    FROM aaa_ops.snapshot_refs
    WHERE snapshot_id='SNAPSHOT-T18-SMOKE';
    IF observed_experiment_links <> 1 THEN
        RAISE EXCEPTION 'EXPERIMENT_RUN_LINKAGE_FAILED:%', observed_experiment_links;
    END IF;
    IF observed_snapshot_count <> 1 THEN
        RAISE EXCEPTION 'SNAPSHOT_METADATA_LINKAGE_FAILED:%', observed_snapshot_count;
    END IF;
END;
$$;

SELECT 'T18_POSTGRES_SMOKE_PASS' AS result;
