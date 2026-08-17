BEGIN;

-- AAA Balanced v1 E4 compatible-version-set, promotion, and restore hardening.
-- This is a NON-AUTHORITATIVE shadow implementation. It cannot promote production
-- authority or make PostgreSQL Operational SoT without a separate Owner decision.

CREATE TABLE aaa_ops.v1_release_sets (
    release_set_id text PRIMARY KEY,
    component_set_sha256 char(64) NOT NULL CHECK (component_set_sha256 ~ '^[0-9a-f]{64}$'),
    compatibility_declaration_ref text NOT NULL CHECK (btrim(compatibility_declaration_ref) <> ''),
    exact_decision_receipt_ref text NOT NULL REFERENCES aaa_ops.v1_decision_receipts(decision_id),
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (btrim(release_set_id) <> '' AND lower(release_set_id) NOT IN ('latest','head','current'))
);

CREATE TABLE aaa_ops.v1_release_set_components (
    release_set_id text NOT NULL REFERENCES aaa_ops.v1_release_sets(release_set_id) ON DELETE RESTRICT,
    component_kind text NOT NULL,
    immutable_identity text NOT NULL CHECK (btrim(immutable_identity) <> '' AND lower(immutable_identity) NOT IN ('latest','head','current')),
    version text NOT NULL CHECK (btrim(version) <> '' AND lower(version) NOT IN ('latest','head','current')),
    content_hash_or_git_identity text NOT NULL CHECK (content_hash_or_git_identity ~ '^([0-9a-f]{40}|[0-9a-f]{64})$'),
    byte_size bigint,
    persistent_locator text,
    verified boolean NOT NULL DEFAULT false,
    PRIMARY KEY (release_set_id, component_kind, immutable_identity, version),
    CHECK (byte_size IS NULL OR byte_size >= 0),
    CHECK (
        (byte_size IS NULL AND persistent_locator IS NULL)
        OR
        (byte_size IS NOT NULL AND persistent_locator IS NOT NULL AND btrim(persistent_locator) <> '')
    )
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_verify_release_set_decision()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_decision aaa_ops.v1_decision_receipts%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_decision
    FROM aaa_ops.v1_decision_receipts
    WHERE decision_id = NEW.exact_decision_receipt_ref;

    IF v_decision.decision <> 'APPROVE'
       OR v_decision.target_kind <> 'RELEASE_SET'
       OR v_decision.exact_target_identity <> NEW.release_set_id
       OR v_decision.target_content_sha256 IS DISTINCT FROM NEW.component_set_sha256 THEN
        RAISE EXCEPTION 'RELEASE_SET_DECISION_EXACT_TARGET_MISMATCH';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_release_set_decision
BEFORE INSERT ON aaa_ops.v1_release_sets
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_verify_release_set_decision();

CREATE OR REPLACE FUNCTION aaa_ops.v1_reject_release_set_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'COMPATIBLE_VERSION_SET_APPEND_ONLY_IMMUTABLE';
END;
$$;

CREATE TRIGGER trg_v1_release_set_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_release_sets
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_release_set_mutation();

CREATE TRIGGER trg_v1_release_component_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_release_set_components
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_release_set_mutation();

CREATE TABLE aaa_ops.v1_promotion_receipts (
    promotion_id text PRIMARY KEY,
    promotion_kind text NOT NULL CHECK (btrim(promotion_kind) <> ''),
    release_set_id text NOT NULL REFERENCES aaa_ops.v1_release_sets(release_set_id),
    source_version_set_hash char(64) NOT NULL CHECK (source_version_set_hash ~ '^[0-9a-f]{64}$'),
    decision_receipt_ref text NOT NULL REFERENCES aaa_ops.v1_decision_receipts(decision_id),
    actor_ref text NOT NULL CHECK (btrim(actor_ref) <> ''),
    authority_ref text NOT NULL CHECK (btrim(authority_ref) <> ''),
    status text NOT NULL DEFAULT 'PREPARED' CHECK (
        status IN ('PREPARED','IN_PROGRESS','COMPLETED_VERIFIED','FAILED_NO_PROMOTION','FAILED_PARTIAL_FAIL_CLOSED')
    ),
    failure_reason text,
    recorded_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    completed_at_db timestamptz
);

CREATE TABLE aaa_ops.v1_promotion_destination_receipts (
    promotion_id text NOT NULL REFERENCES aaa_ops.v1_promotion_receipts(promotion_id) ON DELETE RESTRICT,
    destination_store text NOT NULL CHECK (btrim(destination_store) <> ''),
    destination_namespace text NOT NULL CHECK (btrim(destination_namespace) <> ''),
    status text NOT NULL CHECK (status IN ('PENDING','VERIFIED','FAILED')),
    object_identity text,
    content_sha256 char(64) CHECK (content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'),
    byte_size bigint CHECK (byte_size IS NULL OR byte_size >= 0),
    PRIMARY KEY (promotion_id, destination_store, destination_namespace),
    CHECK (
        status <> 'VERIFIED'
        OR (
            object_identity IS NOT NULL AND btrim(object_identity) <> ''
            AND content_sha256 IS NOT NULL
            AND byte_size IS NOT NULL
        )
    )
);

CREATE TABLE aaa_ops.v1_shadow_canonical_pointers (
    pointer_name text PRIMARY KEY,
    release_set_id text NOT NULL REFERENCES aaa_ops.v1_release_sets(release_set_id),
    component_set_sha256 char(64) NOT NULL CHECK (component_set_sha256 ~ '^[0-9a-f]{64}$'),
    promotion_id text NOT NULL REFERENCES aaa_ops.v1_promotion_receipts(promotion_id),
    updated_at_db timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_promotion_target_guard()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_release aaa_ops.v1_release_sets%ROWTYPE;
    v_decision aaa_ops.v1_decision_receipts%ROWTYPE;
BEGIN
    SELECT * INTO STRICT v_release FROM aaa_ops.v1_release_sets WHERE release_set_id = NEW.release_set_id;
    SELECT * INTO STRICT v_decision FROM aaa_ops.v1_decision_receipts WHERE decision_id = NEW.decision_receipt_ref;

    IF NEW.source_version_set_hash <> v_release.component_set_sha256 THEN
        RAISE EXCEPTION 'PROMOTION_SOURCE_VERSION_SET_HASH_MISMATCH';
    END IF;
    IF v_decision.decision <> 'APPROVE'
       OR v_decision.target_kind <> 'RELEASE_SET'
       OR v_decision.exact_target_identity <> v_release.release_set_id
       OR v_decision.target_content_sha256 IS DISTINCT FROM v_release.component_set_sha256 THEN
        RAISE EXCEPTION 'PROMOTION_DECISION_EXACT_TARGET_MISMATCH';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_promotion_target_guard
BEFORE INSERT ON aaa_ops.v1_promotion_receipts
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_promotion_target_guard();

CREATE OR REPLACE FUNCTION aaa_ops.v1_finalize_shadow_promotion(
    p_promotion_id text,
    p_pointer_name text
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    v_promotion aaa_ops.v1_promotion_receipts%ROWTYPE;
    v_release aaa_ops.v1_release_sets%ROWTYPE;
    v_total integer;
    v_verified integer;
    v_failed integer;
    v_pending integer;
    v_unverified_components integer;
    v_status text;
BEGIN
    SELECT * INTO STRICT v_promotion
    FROM aaa_ops.v1_promotion_receipts
    WHERE promotion_id = p_promotion_id
    FOR UPDATE;

    SELECT * INTO STRICT v_release
    FROM aaa_ops.v1_release_sets
    WHERE release_set_id = v_promotion.release_set_id;

    SELECT count(*),
           count(*) FILTER (WHERE status='VERIFIED'),
           count(*) FILTER (WHERE status='FAILED'),
           count(*) FILTER (WHERE status='PENDING')
      INTO v_total, v_verified, v_failed, v_pending
    FROM aaa_ops.v1_promotion_destination_receipts
    WHERE promotion_id = p_promotion_id;

    SELECT count(*) INTO v_unverified_components
    FROM aaa_ops.v1_release_set_components
    WHERE release_set_id = v_release.release_set_id AND NOT verified;

    IF v_total = 0 THEN
        RAISE EXCEPTION 'PROMOTION_REQUIRES_DESTINATION_RECEIPTS';
    ELSIF v_failed > 0 THEN
        v_status := CASE WHEN v_verified > 0 THEN 'FAILED_PARTIAL_FAIL_CLOSED' ELSE 'FAILED_NO_PROMOTION' END;
        UPDATE aaa_ops.v1_promotion_receipts
        SET status=v_status, completed_at_db=transaction_timestamp(),
            failure_reason='DESTINATION_FAILURE'
        WHERE promotion_id=p_promotion_id;
        RETURN v_status;
    ELSIF v_pending > 0 THEN
        UPDATE aaa_ops.v1_promotion_receipts SET status='IN_PROGRESS'
        WHERE promotion_id=p_promotion_id;
        RETURN 'IN_PROGRESS';
    ELSIF v_unverified_components > 0 THEN
        UPDATE aaa_ops.v1_promotion_receipts
        SET status='FAILED_NO_PROMOTION', completed_at_db=transaction_timestamp(),
            failure_reason='UNVERIFIED_RELEASE_COMPONENT'
        WHERE promotion_id=p_promotion_id;
        RETURN 'FAILED_NO_PROMOTION';
    END IF;

    UPDATE aaa_ops.v1_promotion_receipts
    SET status='COMPLETED_VERIFIED', completed_at_db=transaction_timestamp(), failure_reason=NULL
    WHERE promotion_id=p_promotion_id;

    -- NON-AUTHORITATIVE shadow pointer update intentionally occurs LAST.
    INSERT INTO aaa_ops.v1_shadow_canonical_pointers(
        pointer_name, release_set_id, component_set_sha256, promotion_id
    ) VALUES (
        p_pointer_name, v_release.release_set_id, v_release.component_set_sha256, p_promotion_id
    )
    ON CONFLICT (pointer_name) DO UPDATE
    SET release_set_id=EXCLUDED.release_set_id,
        component_set_sha256=EXCLUDED.component_set_sha256,
        promotion_id=EXCLUDED.promotion_id,
        updated_at_db=transaction_timestamp();

    RETURN 'COMPLETED_VERIFIED';
END;
$$;

CREATE TABLE aaa_ops.v1_restore_manifests (
    restore_manifest_id text PRIMARY KEY,
    backup_or_snapshot_identity text NOT NULL CHECK (btrim(backup_or_snapshot_identity) <> ''),
    source_store_kind text NOT NULL CHECK (btrim(source_store_kind) <> ''),
    target_store_kind text NOT NULL CHECK (btrim(target_store_kind) <> ''),
    schema_migration_version_set jsonb NOT NULL,
    immutable_artifact_refs jsonb NOT NULL,
    restore_target_identity text NOT NULL CHECK (btrim(restore_target_identity) <> ''),
    verification_plan_ref text NOT NULL CHECK (btrim(verification_plan_ref) <> ''),
    status text NOT NULL DEFAULT 'PREPARED' CHECK (
        status IN ('PREPARED','RESTORED_UNVERIFIED','RESTORED_VERIFIED','FAILED_FAIL_CLOSED')
    ),
    provider_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    verification_result_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    managed_pitr_rpo_rto_qualification_ref text,
    operational_sot_authorized boolean NOT NULL DEFAULT false CHECK (NOT operational_sot_authorized),
    created_at_db timestamptz NOT NULL DEFAULT transaction_timestamp(),
    restored_at_db timestamptz,
    verified_at_db timestamptz,
    CHECK (jsonb_array_length(schema_migration_version_set) > 0),
    CHECK (jsonb_array_length(immutable_artifact_refs) > 0)
);

CREATE OR REPLACE FUNCTION aaa_ops.v1_restore_semantic_guard()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND ROW(
        NEW.backup_or_snapshot_identity, NEW.source_store_kind, NEW.target_store_kind,
        NEW.schema_migration_version_set, NEW.immutable_artifact_refs,
        NEW.restore_target_identity, NEW.verification_plan_ref
    ) IS DISTINCT FROM ROW(
        OLD.backup_or_snapshot_identity, OLD.source_store_kind, OLD.target_store_kind,
        OLD.schema_migration_version_set, OLD.immutable_artifact_refs,
        OLD.restore_target_identity, OLD.verification_plan_ref
    ) THEN
        RAISE EXCEPTION 'RESTORE_SEMANTIC_IDENTITY_IMMUTABLE';
    END IF;
    IF NEW.status = 'RESTORED_VERIFIED' AND jsonb_array_length(NEW.verification_result_refs) = 0 THEN
        RAISE EXCEPTION 'RESTORED_VERIFIED_REQUIRES_VERIFICATION_EVIDENCE';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_restore_semantic_guard
BEFORE UPDATE ON aaa_ops.v1_restore_manifests
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_restore_semantic_guard();

CREATE OR REPLACE FUNCTION aaa_ops.v1_mark_restore_unverified(
    p_restore_manifest_id text
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE aaa_ops.v1_restore_manifests
    SET status='RESTORED_UNVERIFIED', restored_at_db=transaction_timestamp()
    WHERE restore_manifest_id=p_restore_manifest_id AND status='PREPARED';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'RESTORE_NOT_PREPARED';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_verify_restore(
    p_restore_manifest_id text,
    p_verification_result_refs jsonb
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_verification_result_refs IS NULL
       OR jsonb_typeof(p_verification_result_refs) <> 'array'
       OR jsonb_array_length(p_verification_result_refs) = 0 THEN
        RAISE EXCEPTION 'RESTORE_VERIFICATION_EVIDENCE_REQUIRED';
    END IF;

    UPDATE aaa_ops.v1_restore_manifests
    SET status='RESTORED_VERIFIED',
        verification_result_refs=p_verification_result_refs,
        verified_at_db=transaction_timestamp()
    WHERE restore_manifest_id=p_restore_manifest_id
      AND status='RESTORED_UNVERIFIED';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'RESTORE_MUST_BE_UNVERIFIED_BEFORE_VERIFICATION';
    END IF;
END;
$$;

COMMENT ON TABLE aaa_ops.v1_release_sets IS
'Immutable compatible version sets. Valid components are not compatible unless explicitly declared and exact-decision bound.';
COMMENT ON TABLE aaa_ops.v1_promotion_receipts IS
'Promotion workflow receipts for shadow validation only; completion does not grant production authority.';
COMMENT ON TABLE aaa_ops.v1_shadow_canonical_pointers IS
'NON-AUTHORITATIVE shadow pointer used only to prove pointer-last fail-closed promotion semantics.';
COMMENT ON TABLE aaa_ops.v1_restore_manifests IS
'Provider-neutral restore manifests. RESTORED_VERIFIED does not authorize PostgreSQL Operational SoT.';

COMMIT;
