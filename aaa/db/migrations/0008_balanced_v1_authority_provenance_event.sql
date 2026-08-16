BEGIN;

-- AAA Balanced v1 E3 successor authority / provenance / operational-event semantics.
-- Forward-only amendment for E2 finding: dependency_lock_refs becomes an explicit
-- execution-material part of successor Logical Run state. Migration 0007 remains immutable.
-- PostgreSQL remains NON-AUTHORITATIVE until a separate Project Owner cutover.

ALTER TABLE aaa_ops.v1_logical_runs
    ADD COLUMN dependency_lock_refs jsonb NOT NULL DEFAULT '[]'::jsonb;

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
        NEW.configuration_sha256, NEW.dependency_lock_refs, NEW.material_input_refs,
        NEW.schema_family_version_refs, NEW.semantic_generation
    ) IS DISTINCT FROM ROW(
        OLD.project_namespace, OLD.process_id, OLD.work_order_ref,
        OLD.responsible_persona, OLD.executor_role, OLD.repository_identity,
        OLD.exact_target_commit, OLD.exact_execution_spec_hash,
        OLD.execution_profile_ref, OLD.execution_profile_sha256,
        OLD.configuration_sha256, OLD.dependency_lock_refs, OLD.material_input_refs,
        OLD.schema_family_version_refs, OLD.semantic_generation
    ) THEN
        RAISE EXCEPTION 'LOGICAL_RUN_EXECUTION_SPEC_IMMUTABLE';
    END IF;
    NEW.updated_at_db := transaction_timestamp();
    RETURN NEW;
END;
$$;

CREATE TABLE aaa_ops.v1_decision_receipts (
    decision_id text PRIMARY KEY,
    decision_type text NOT NULL CHECK (btrim(decision_type) <> ''),
    target_kind text NOT NULL CHECK (
        target_kind IN (
            'GIT_COMMIT','CONTENT_SHA256','RELEASE_SET',
            'ARTIFACT_IDENTITY','SHARED_CONTRACT_RECONCILIATION'
        )
    ),
    exact_target_identity text NOT NULL CHECK (
        btrim(exact_target_identity) <> ''
        AND lower(exact_target_identity) NOT IN ('latest','head','current','main','master')
        AND lower(exact_target_identity) NOT LIKE 'refs/heads/%'
    ),
    target_content_sha256 char(64) CHECK (
        target_content_sha256 IS NULL OR target_content_sha256 ~ '^[0-9a-f]{64}$'
    ),
    actor_type text NOT NULL CHECK (
        actor_type IN ('HUMAN_OWNER','PERSONA_INSTANCE','WORKER','SERVICE','CI_JOB','VALIDATOR_RUNTIME')
    ),
    actor_identity text NOT NULL CHECK (btrim(actor_identity) <> ''),
    authority_role text NOT NULL CHECK (btrim(authority_role) <> ''),
    authority_identity text NOT NULL CHECK (btrim(authority_identity) <> ''),
    authority_scope text NOT NULL CHECK (btrim(authority_scope) <> ''),
    authority_source_ref text NOT NULL CHECK (btrim(authority_source_ref) <> ''),
    decision text NOT NULL CHECK (decision IN ('APPROVE','DENY','REVOKE','SUPERSEDE')),
    rationale_ref text,
    prerequisite_receipt_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    supersedes_decision_ref text,
    revokes_decision_ref text,
    decided_at timestamptz NOT NULL,
    recorded_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT v1_decision_git_target_shape CHECK (
        target_kind <> 'GIT_COMMIT' OR exact_target_identity ~ '^[0-9a-f]{40}$'
    ),
    CONSTRAINT v1_decision_sha_target_shape CHECK (
        target_kind <> 'CONTENT_SHA256' OR exact_target_identity ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT v1_decision_revoke_rule CHECK (
        (decision = 'REVOKE' AND revokes_decision_ref IS NOT NULL AND supersedes_decision_ref IS NULL)
        OR
        (decision = 'SUPERSEDE' AND supersedes_decision_ref IS NOT NULL AND revokes_decision_ref IS NULL)
        OR
        (decision IN ('APPROVE','DENY') AND supersedes_decision_ref IS NULL AND revokes_decision_ref IS NULL)
    ),
    CONSTRAINT v1_decision_supersedes_fk
      FOREIGN KEY (supersedes_decision_ref)
      REFERENCES aaa_ops.v1_decision_receipts(decision_id)
      DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT v1_decision_revokes_fk
      FOREIGN KEY (revokes_decision_ref)
      REFERENCES aaa_ops.v1_decision_receipts(decision_id)
      DEFERRABLE INITIALLY DEFERRED
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_reject_append_only_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'BALANCED_V1_APPEND_ONLY_RECORD_IMMUTABLE';
END;
$$;

CREATE TRIGGER trg_v1_decision_receipt_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_decision_receipts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_append_only_mutation();

CREATE TABLE aaa_ops.v1_execution_provenance_receipts (
    provenance_receipt_id text PRIMARY KEY,
    run_id text NOT NULL,
    run_attempt_id text NOT NULL UNIQUE,
    repository_identity text NOT NULL CHECK (btrim(repository_identity) <> ''),
    exact_commit_sha char(40) NOT NULL CHECK (exact_commit_sha ~ '^[0-9a-f]{40}$'),
    git_tree_sha char(40) NOT NULL CHECK (git_tree_sha ~ '^[0-9a-f]{40}$'),
    working_tree_clean boolean NOT NULL CHECK (working_tree_clean),
    execution_profile_id text NOT NULL CHECK (btrim(execution_profile_id) <> ''),
    execution_profile_version text NOT NULL CHECK (btrim(execution_profile_version) <> ''),
    execution_profile_sha256 char(64) NOT NULL CHECK (execution_profile_sha256 ~ '^[0-9a-f]{64}$'),
    dependency_lock_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    configuration_sha256 char(64) NOT NULL CHECK (configuration_sha256 ~ '^[0-9a-f]{64}$'),
    material_input_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    runtime_identity text NOT NULL CHECK (btrim(runtime_identity) <> ''),
    verified_by_actor_type text NOT NULL CHECK (
        verified_by_actor_type IN ('HUMAN_OWNER','PERSONA_INSTANCE','WORKER','SERVICE','CI_JOB','VALIDATOR_RUNTIME')
    ),
    verified_by_actor_identity text NOT NULL CHECK (btrim(verified_by_actor_identity) <> ''),
    verified_at timestamptz NOT NULL,
    recorded_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT v1_provenance_attempt_fk
      FOREIGN KEY (run_id, run_attempt_id)
      REFERENCES aaa_ops.v1_run_attempts(run_id, run_attempt_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_verify_execution_provenance()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_run aaa_ops.v1_logical_runs%ROWTYPE;
    v_attempt aaa_ops.v1_run_attempts%ROWTYPE;
    v_run_dependencies jsonb;
    v_prov_dependencies jsonb;
    v_run_inputs jsonb;
    v_prov_inputs jsonb;
BEGIN
    SELECT * INTO STRICT v_run
    FROM aaa_ops.v1_logical_runs
    WHERE run_id = NEW.run_id;

    SELECT * INTO STRICT v_attempt
    FROM aaa_ops.v1_run_attempts
    WHERE run_id = NEW.run_id AND run_attempt_id = NEW.run_attempt_id;

    IF v_attempt.exact_execution_spec_hash <> v_run.exact_execution_spec_hash THEN
        RAISE EXCEPTION 'PROVENANCE_ATTEMPT_SPEC_HASH_MISMATCH';
    END IF;
    IF NEW.repository_identity <> v_run.repository_identity THEN
        RAISE EXCEPTION 'PROVENANCE_REPOSITORY_IDENTITY_MISMATCH';
    END IF;
    IF NEW.exact_commit_sha <> v_run.exact_target_commit THEN
        RAISE EXCEPTION 'PROVENANCE_EXACT_COMMIT_MISMATCH';
    END IF;
    IF NEW.execution_profile_id <> v_run.execution_profile_ref
       OR NEW.execution_profile_sha256 <> v_run.execution_profile_sha256 THEN
        RAISE EXCEPTION 'PROVENANCE_EXECUTION_PROFILE_MISMATCH';
    END IF;
    IF NEW.configuration_sha256 <> v_run.configuration_sha256 THEN
        RAISE EXCEPTION 'PROVENANCE_CONFIGURATION_MISMATCH';
    END IF;

    SELECT COALESCE(jsonb_agg(x ORDER BY x->>'identity', x->>'sha256'), '[]'::jsonb)
      INTO v_run_dependencies
    FROM jsonb_array_elements(v_run.dependency_lock_refs) AS x;

    SELECT COALESCE(jsonb_agg(x ORDER BY x->>'identity', x->>'sha256'), '[]'::jsonb)
      INTO v_prov_dependencies
    FROM jsonb_array_elements(NEW.dependency_lock_refs) AS x;

    IF v_run_dependencies IS DISTINCT FROM v_prov_dependencies THEN
        RAISE EXCEPTION 'PROVENANCE_DEPENDENCY_LOCK_MISMATCH';
    END IF;

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'project_namespace', x->>'project_namespace',
                'entity_family', x->>'entity_family',
                'local_id', x->>'local_id'
            )
            ORDER BY x->>'project_namespace', x->>'entity_family', x->>'local_id'
        ),
        '[]'::jsonb
    ) INTO v_run_inputs
    FROM jsonb_array_elements(v_run.material_input_refs) AS x;

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'project_namespace', x->'identity'->>'project_namespace',
                'entity_family', x->'identity'->>'entity_family',
                'local_id', x->'identity'->>'local_id'
            )
            ORDER BY
                x->'identity'->>'project_namespace',
                x->'identity'->>'entity_family',
                x->'identity'->>'local_id'
        ),
        '[]'::jsonb
    ) INTO v_prov_inputs
    FROM jsonb_array_elements(NEW.material_input_refs) AS x;

    IF v_run_inputs IS DISTINCT FROM v_prov_inputs THEN
        RAISE EXCEPTION 'PROVENANCE_MATERIAL_INPUT_IDENTITY_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_execution_provenance_verify
BEFORE INSERT ON aaa_ops.v1_execution_provenance_receipts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_verify_execution_provenance();

CREATE TRIGGER trg_v1_execution_provenance_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_execution_provenance_receipts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_append_only_mutation();

CREATE TABLE aaa_ops.v1_operational_events (
    operational_event_id text NOT NULL,
    project_namespace text NOT NULL,
    event_family text NOT NULL CHECK (
        event_family IN (
            'RUN_LIFECYCLE','ATTEMPT_LIFECYCLE','DISPATCH','LEASE',
            'RESULT','DECISION','PROMOTION','RESTORE'
        )
    ),
    event_type text NOT NULL CHECK (btrim(event_type) <> ''),
    event_schema_version text NOT NULL CHECK (
        btrim(event_schema_version) <> '' AND lower(event_schema_version) <> 'latest'
    ),
    aggregate_entity_family text NOT NULL CHECK (btrim(aggregate_entity_family) <> ''),
    aggregate_local_id text NOT NULL CHECK (btrim(aggregate_local_id) <> ''),
    sequence_number bigint NOT NULL CHECK (sequence_number >= 1),
    observed_at timestamptz NOT NULL,
    actor_type text NOT NULL CHECK (
        actor_type IN ('HUMAN_OWNER','PERSONA_INSTANCE','WORKER','SERVICE','CI_JOB','VALIDATOR_RUNTIME')
    ),
    actor_identity text NOT NULL CHECK (btrim(actor_identity) <> ''),
    authority_role text NOT NULL CHECK (btrim(authority_role) <> ''),
    authority_identity text NOT NULL CHECK (btrim(authority_identity) <> ''),
    authority_scope text NOT NULL CHECK (btrim(authority_scope) <> ''),
    authority_source_ref text NOT NULL CHECK (btrim(authority_source_ref) <> ''),
    producer_or_actor_scope text NOT NULL CHECK (btrim(producer_or_actor_scope) <> ''),
    idempotency_scope_key text NOT NULL CHECK (btrim(idempotency_scope_key) <> ''),
    payload_sha256 char(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    decision_receipt_ref text REFERENCES aaa_ops.v1_decision_receipts(decision_id),
    causation_event_ref text,
    correlation_id text,
    recorded_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (project_namespace, event_family, operational_event_id),
    UNIQUE (project_namespace, producer_or_actor_scope, event_family, idempotency_scope_key),
    UNIQUE (project_namespace, aggregate_entity_family, aggregate_local_id, sequence_number)
);

CREATE TRIGGER trg_v1_operational_event_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_operational_events
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_append_only_mutation();

CREATE OR REPLACE FUNCTION aaa_ops.v1_append_operational_event(
    p_operational_event_id text,
    p_project_namespace text,
    p_event_family text,
    p_event_type text,
    p_event_schema_version text,
    p_aggregate_entity_family text,
    p_aggregate_local_id text,
    p_sequence_number bigint,
    p_observed_at timestamptz,
    p_actor_type text,
    p_actor_identity text,
    p_authority_role text,
    p_authority_identity text,
    p_authority_scope text,
    p_authority_source_ref text,
    p_producer_or_actor_scope text,
    p_idempotency_scope_key text,
    p_payload_sha256 text,
    p_decision_receipt_ref text DEFAULT NULL,
    p_causation_event_ref text DEFAULT NULL,
    p_correlation_id text DEFAULT NULL
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    v_existing aaa_ops.v1_operational_events%ROWTYPE;
BEGIN
    SELECT * INTO v_existing
    FROM aaa_ops.v1_operational_events
    WHERE project_namespace = p_project_namespace
      AND event_family = p_event_family
      AND operational_event_id = p_operational_event_id;

    IF FOUND THEN
        IF ROW(
            v_existing.event_type, v_existing.event_schema_version,
            v_existing.aggregate_entity_family, v_existing.aggregate_local_id,
            v_existing.sequence_number, v_existing.observed_at,
            v_existing.actor_type, v_existing.actor_identity,
            v_existing.authority_role, v_existing.authority_identity,
            v_existing.authority_scope, v_existing.authority_source_ref,
            v_existing.producer_or_actor_scope, v_existing.idempotency_scope_key,
            v_existing.payload_sha256, v_existing.decision_receipt_ref,
            v_existing.causation_event_ref, v_existing.correlation_id
        ) IS NOT DISTINCT FROM ROW(
            p_event_type, p_event_schema_version,
            p_aggregate_entity_family, p_aggregate_local_id,
            p_sequence_number, p_observed_at,
            p_actor_type, p_actor_identity,
            p_authority_role, p_authority_identity,
            p_authority_scope, p_authority_source_ref,
            p_producer_or_actor_scope, p_idempotency_scope_key,
            p_payload_sha256::char(64), p_decision_receipt_ref,
            p_causation_event_ref, p_correlation_id
        ) THEN
            RETURN false;
        END IF;
        RAISE EXCEPTION 'OPERATIONAL_EVENT_IDENTITY_COLLISION_DIFFERENT_PAYLOAD_OR_MEANING';
    END IF;

    INSERT INTO aaa_ops.v1_operational_events (
        operational_event_id, project_namespace, event_family, event_type,
        event_schema_version, aggregate_entity_family, aggregate_local_id,
        sequence_number, observed_at, actor_type, actor_identity,
        authority_role, authority_identity, authority_scope, authority_source_ref,
        producer_or_actor_scope, idempotency_scope_key, payload_sha256,
        decision_receipt_ref, causation_event_ref, correlation_id
    ) VALUES (
        p_operational_event_id, p_project_namespace, p_event_family, p_event_type,
        p_event_schema_version, p_aggregate_entity_family, p_aggregate_local_id,
        p_sequence_number, p_observed_at, p_actor_type, p_actor_identity,
        p_authority_role, p_authority_identity, p_authority_scope, p_authority_source_ref,
        p_producer_or_actor_scope, p_idempotency_scope_key, p_payload_sha256::char(64),
        p_decision_receipt_ref, p_causation_event_ref, p_correlation_id
    );

    RETURN true;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'OPERATIONAL_EVENT_SCOPED_IDEMPOTENCY_OR_SEQUENCE_COLLISION';
END;
$$;

COMMENT ON TABLE aaa_ops.v1_decision_receipts IS
'Append-only exact-target authority evidence. Actor capability does not create authority.';
COMMENT ON TABLE aaa_ops.v1_execution_provenance_receipts IS
'Execution-source provenance bound to Balanced-v1 Logical Run/Attempt; distinct from historical PIT evidence provenance.';
COMMENT ON TABLE aaa_ops.v1_operational_events IS
'Operational audit/provenance events only. Not economic events and not an Event Sourcing sole-state model.';

COMMIT;
