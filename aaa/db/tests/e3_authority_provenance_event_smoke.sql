\set ON_ERROR_STOP on

BEGIN;

INSERT INTO aaa_ops.v1_logical_runs (
    run_id, project_namespace, process_id, work_order_ref, responsible_persona,
    executor_role, repository_identity, exact_target_commit, exact_execution_spec_hash,
    execution_profile_ref, execution_profile_sha256, configuration_sha256,
    dependency_lock_refs, material_input_refs, schema_family_version_refs
) VALUES (
    'RUN-V1-E3-SMOKE', 'SEMICONDUCTOR_RESEARCH', 'E3-SMOKE', 'WO-E3-SMOKE',
    'SEMI-CONTROL-ARCHITECT', 'BOUNDED_ENGINEERING_IMPLEMENTATION',
    'github-repo-id:1334403184', repeat('a', 40), repeat('b', 64),
    'PROFILE-E3-v1', repeat('c', 64), repeat('d', 64),
    jsonb_build_array(jsonb_build_object('identity','requirements.lock','sha256',repeat('1',64))),
    jsonb_build_array(jsonb_build_object('project_namespace','SEMICONDUCTOR_RESEARCH','entity_family','DATASET','local_id','DATA-1')),
    '[]'::jsonb
);

SELECT aaa_ops.v1_materialize_run_attempt(
    'RUN-V1-E3-SMOKE', 'ATT-E3-1', 'TASK-E3-1', 1, NULL, NULL, NULL, NULL
);

-- E2 bounded finding remediation: dependency locks are execution-material and immutable on one Logical Run.
DO $$
BEGIN
    BEGIN
        UPDATE aaa_ops.v1_logical_runs
        SET dependency_lock_refs = jsonb_build_array(jsonb_build_object('identity','requirements.lock','sha256',repeat('2',64)))
        WHERE run_id='RUN-V1-E3-SMOKE';
        RAISE EXCEPTION 'DEPENDENCY_LOCK_MUTATION_ACCEPTED_ON_SAME_LOGICAL_RUN';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'DEPENDENCY_LOCK_MUTATION_ACCEPTED_ON_SAME_LOGICAL_RUN' THEN RAISE; END IF;
    END;
END $$;

-- Exact-target Decision Receipt: actor and authority are independently recorded.
INSERT INTO aaa_ops.v1_decision_receipts (
    decision_id, decision_type, target_kind, exact_target_identity,
    actor_type, actor_identity, authority_role, authority_identity,
    authority_scope, authority_source_ref, decision, decided_at
) VALUES (
    'DEC-E3-X', 'ARCHITECTURE_EXACT_FREEZE', 'GIT_COMMIT', repeat('a',40),
    'PERSONA_INSTANCE', 'SEMI-CONTROL-ARCHITECT',
    'PROJECT_OWNER', 'PROJECT_OWNER', 'ARCHITECTURE_EXACT_FREEZE', 'OWNER-AUTHORITY-MATRIX',
    'APPROVE', transaction_timestamp()
);

DO $$
BEGIN
    IF (SELECT actor_identity = authority_identity FROM aaa_ops.v1_decision_receipts WHERE decision_id='DEC-E3-X') THEN
        RAISE EXCEPTION 'TEST_REQUIRES_DISTINCT_ACTOR_AND_AUTHORITY_IDENTITIES';
    END IF;
    BEGIN
        INSERT INTO aaa_ops.v1_decision_receipts (
            decision_id, decision_type, target_kind, exact_target_identity,
            actor_type, actor_identity, authority_role, authority_identity,
            authority_scope, authority_source_ref, decision, decided_at
        ) VALUES (
            'DEC-E3-FLOAT', 'RELEASE', 'ARTIFACT_IDENTITY', 'refs/heads/main',
            'HUMAN_OWNER','OWNER','PROJECT_OWNER','OWNER','RELEASE','OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp()
        );
        RAISE EXCEPTION 'FLOATING_TARGET_ACCEPTED';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        UPDATE aaa_ops.v1_decision_receipts SET decision='DENY' WHERE decision_id='DEC-E3-X';
        RAISE EXCEPTION 'DECISION_RECEIPT_MUTABLE';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'DECISION_RECEIPT_MUTABLE' THEN RAISE; END IF;
    END;
END $$;

INSERT INTO aaa_ops.v1_decision_receipts (
    decision_id, decision_type, target_kind, exact_target_identity,
    actor_type, actor_identity, authority_role, authority_identity,
    authority_scope, authority_source_ref, decision, revokes_decision_ref, decided_at
) VALUES (
    'DEC-E3-X-REVOKE', 'ARCHITECTURE_EXACT_FREEZE', 'GIT_COMMIT', repeat('a',40),
    'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER',
    'ARCHITECTURE_EXACT_FREEZE','OWNER-AUTHORITY-MATRIX','REVOKE','DEC-E3-X',transaction_timestamp()
);

-- Dirty provenance is rejected structurally.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_execution_provenance_receipts (
            provenance_receipt_id, run_id, run_attempt_id, repository_identity,
            exact_commit_sha, git_tree_sha, working_tree_clean,
            execution_profile_id, execution_profile_version, execution_profile_sha256,
            dependency_lock_refs, configuration_sha256, material_input_refs,
            runtime_identity, verified_by_actor_type, verified_by_actor_identity, verified_at
        ) VALUES (
            'PROV-E3-DIRTY','RUN-V1-E3-SMOKE','ATT-E3-1','github-repo-id:1334403184',
            repeat('a',40),repeat('f',40),false,
            'PROFILE-E3-v1','v1',repeat('c',64),
            jsonb_build_array(jsonb_build_object('identity','requirements.lock','sha256',repeat('1',64))),
            repeat('d',64),
            jsonb_build_array(jsonb_build_object('identity',jsonb_build_object('project_namespace','SEMICONDUCTOR_RESEARCH','entity_family','DATASET','local_id','DATA-1'))),
            'python-3.12','CI_JOB','CI-E3',transaction_timestamp()
        );
        RAISE EXCEPTION 'DIRTY_PROVENANCE_ACCEPTED';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END $$;

-- Mismatched dependency lock is rejected by mechanical verification.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_execution_provenance_receipts (
            provenance_receipt_id, run_id, run_attempt_id, repository_identity,
            exact_commit_sha, git_tree_sha, working_tree_clean,
            execution_profile_id, execution_profile_version, execution_profile_sha256,
            dependency_lock_refs, configuration_sha256, material_input_refs,
            runtime_identity, verified_by_actor_type, verified_by_actor_identity, verified_at
        ) VALUES (
            'PROV-E3-BAD-LOCK','RUN-V1-E3-SMOKE','ATT-E3-1','github-repo-id:1334403184',
            repeat('a',40),repeat('f',40),true,
            'PROFILE-E3-v1','v1',repeat('c',64),
            jsonb_build_array(jsonb_build_object('identity','requirements.lock','sha256',repeat('2',64))),
            repeat('d',64),
            jsonb_build_array(jsonb_build_object('identity',jsonb_build_object('project_namespace','SEMICONDUCTOR_RESEARCH','entity_family','DATASET','local_id','DATA-1'))),
            'python-3.12','CI_JOB','CI-E3',transaction_timestamp()
        );
        RAISE EXCEPTION 'MISMATCHED_DEPENDENCY_LOCK_PROVENANCE_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'MISMATCHED_DEPENDENCY_LOCK_PROVENANCE_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

INSERT INTO aaa_ops.v1_execution_provenance_receipts (
    provenance_receipt_id, run_id, run_attempt_id, repository_identity,
    exact_commit_sha, git_tree_sha, working_tree_clean,
    execution_profile_id, execution_profile_version, execution_profile_sha256,
    dependency_lock_refs, configuration_sha256, material_input_refs,
    runtime_identity, verified_by_actor_type, verified_by_actor_identity, verified_at
) VALUES (
    'PROV-E3-GOOD','RUN-V1-E3-SMOKE','ATT-E3-1','github-repo-id:1334403184',
    repeat('a',40),repeat('f',40),true,
    'PROFILE-E3-v1','v1',repeat('c',64),
    jsonb_build_array(jsonb_build_object('identity','requirements.lock','sha256',repeat('1',64))),
    repeat('d',64),
    jsonb_build_array(jsonb_build_object('identity',jsonb_build_object('project_namespace','SEMICONDUCTOR_RESEARCH','entity_family','DATASET','local_id','DATA-1'),'content_sha256',repeat('e',64))),
    'python-3.12','CI_JOB','CI-E3',transaction_timestamp()
);

-- Operational Event identity: exact reappend is idempotent; changed payload under same identity fails closed.
SELECT aaa_ops.v1_append_operational_event(
    'OP-EVT-1','SEMICONDUCTOR_RESEARCH','RUN_LIFECYCLE','RUN_CREATED','OP-EVT-v1',
    'LOGICAL_RUN','RUN-V1-E3-SMOKE',1,'2026-08-16T09:00:00+00',
    'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
    'BOUNDED_ENGINEERING','DEC-E3-X','producer-a','idem-same',repeat('a',64),NULL,NULL,'CORR-1'
);
DO $$
DECLARE
    v_reappend boolean;
BEGIN
    SELECT aaa_ops.v1_append_operational_event(
        'OP-EVT-1','SEMICONDUCTOR_RESEARCH','RUN_LIFECYCLE','RUN_CREATED','OP-EVT-v1',
        'LOGICAL_RUN','RUN-V1-E3-SMOKE',1,'2026-08-16T09:00:00+00',
        'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
        'BOUNDED_ENGINEERING','DEC-E3-X','producer-a','idem-same',repeat('a',64),NULL,NULL,'CORR-1'
    ) INTO v_reappend;
    IF v_reappend THEN RAISE EXCEPTION 'EXACT_REAPPEND_WAS_NOT_IDEMPOTENT'; END IF;

    BEGIN
        PERFORM aaa_ops.v1_append_operational_event(
            'OP-EVT-1','SEMICONDUCTOR_RESEARCH','RUN_LIFECYCLE','RUN_CREATED','OP-EVT-v1',
            'LOGICAL_RUN','RUN-V1-E3-SMOKE',1,'2026-08-16T09:00:00+00',
            'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
            'BOUNDED_ENGINEERING','DEC-E3-X','producer-a','idem-same',repeat('b',64),NULL,NULL,'CORR-1'
        );
        RAISE EXCEPTION 'EVENT_IDENTITY_COLLISION_DIFFERENT_PAYLOAD_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'EVENT_IDENTITY_COLLISION_DIFFERENT_PAYLOAD_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

-- Same idempotency key is allowed across a different producer scope.
SELECT aaa_ops.v1_append_operational_event(
    'OP-EVT-2','SEMICONDUCTOR_RESEARCH','RUN_LIFECYCLE','RUN_UPDATED','OP-EVT-v1',
    'LOGICAL_RUN','RUN-V1-E3-SMOKE',2,'2026-08-16T09:01:00+00',
    'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
    'BOUNDED_ENGINEERING','DEC-E3-X','producer-b','idem-same',repeat('c',64),NULL,'OP-EVT-1','CORR-1'
);

-- Same scoped idempotency key and duplicate aggregate sequence both fail closed.
DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.v1_append_operational_event(
            'OP-EVT-3','SEMICONDUCTOR_RESEARCH','RUN_LIFECYCLE','RUN_UPDATED','OP-EVT-v1',
            'LOGICAL_RUN','RUN-V1-E3-SMOKE',3,'2026-08-16T09:02:00+00',
            'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
            'BOUNDED_ENGINEERING','DEC-E3-X','producer-a','idem-same',repeat('d',64),NULL,NULL,'CORR-1'
        );
        RAISE EXCEPTION 'SAME_SCOPED_IDEMPOTENCY_KEY_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'SAME_SCOPED_IDEMPOTENCY_KEY_ACCEPTED' THEN RAISE; END IF;
    END;
    BEGIN
        PERFORM aaa_ops.v1_append_operational_event(
            'OP-EVT-4','SEMICONDUCTOR_RESEARCH','RESULT','RESULT_WRITTEN','OP-EVT-v1',
            'LOGICAL_RUN','RUN-V1-E3-SMOKE',2,'2026-08-16T09:03:00+00',
            'SERVICE','AAA-SERVICE','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT',
            'BOUNDED_ENGINEERING','DEC-E3-X','producer-c','idem-result',repeat('e',64),NULL,NULL,'CORR-1'
        );
        RAISE EXCEPTION 'DUPLICATE_AGGREGATE_SEQUENCE_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'DUPLICATE_AGGREGATE_SEQUENCE_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

-- Economic Event is not an Operational Event family.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_operational_events(
            operational_event_id, project_namespace, event_family, event_type, event_schema_version,
            aggregate_entity_family, aggregate_local_id, sequence_number, observed_at,
            actor_type, actor_identity, authority_role, authority_identity, authority_scope,
            authority_source_ref, producer_or_actor_scope, idempotency_scope_key, payload_sha256
        ) VALUES (
            'OP-EVT-ECON','SEMICONDUCTOR_RESEARCH','ECONOMIC_EVENT','MILESTONE','OP-EVT-v1',
            'ECONOMIC_EVENT','ECON-1',1,transaction_timestamp(),
            'SERVICE','AAA','SEMI_CONTROL_ARCHITECT','SEMI-CONTROL-ARCHITECT','CONTROL','AUTH',
            'producer-econ','idem-econ',repeat('f',64)
        );
        RAISE EXCEPTION 'ECONOMIC_EVENT_ACCEPTED_AS_OPERATIONAL_EVENT';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END $$;

ROLLBACK;
