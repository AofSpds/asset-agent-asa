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

SELECT aaa_ops.start_run_with_lease('RUN-T18-SMOKE', 'worker-a', 600) AS lease_epoch \gset
\if :lease_epoch != 1
  \echo 'unexpected lease epoch'
  \quit 41
\endif

SELECT effective_state FROM aaa_ops.run_projection WHERE run_id='RUN-T18-SMOKE' \gset
\if :'effective_state' != 'RUNNING_CONFIRMED'
  \echo 'run did not project RUNNING_CONFIRMED'
  \quit 42
\endif

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_run('RUN-T18-SMOKE', 'worker-a', 0, 600);
        RAISE EXCEPTION 'expected stale fencing rejection';
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
        RAISE EXCEPTION 'expected append-only rejection';
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

SELECT state FROM aaa_ops.runs WHERE run_id='RUN-T18-SMOKE' \gset
\if :'state' != 'COMPLETED_PASS'
  \echo 'terminal transition failed'
  \quit 43
\endif

SELECT verdict FROM aaa_ops.results WHERE result_id='RESULT-T18-SMOKE' \gset
\if :'verdict' != 'PASS'
  \echo 'result binding failed'
  \quit 44
\endif

DO $$
DECLARE
    failed boolean := false;
BEGIN
    BEGIN
        PERFORM aaa_ops.heartbeat_run('RUN-T18-SMOKE', 'worker-a', 1, 600);
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%STALE_OR_INVALID_LEASE%' THEN
                failed := true;
            ELSE
                RAISE;
            END IF;
    END;
    IF NOT failed THEN
        RAISE EXCEPTION 'terminal run accepted heartbeat';
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

SELECT count(*) AS experiment_links
FROM aaa_ops.experiment_runs
WHERE experiment_id='EXP-T18-SMOKE'
  AND run_id='RUN-T18-SMOKE' \gset
\if :experiment_links != 1
  \echo 'experiment/run linkage failed'
  \quit 45
\endif

SELECT count(*) AS snapshot_count
FROM aaa_ops.snapshot_refs
WHERE snapshot_id='SNAPSHOT-T18-SMOKE' \gset
\if :snapshot_count != 1
  \echo 'snapshot metadata linkage failed'
  \quit 46
\endif

SELECT 'T18_POSTGRES_SMOKE_PASS' AS result;
