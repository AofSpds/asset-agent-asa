BEGIN;

-- AAA Balanced v1 E4 forward remediation for Independent Validation finding
-- AAA-v1-IV-FND-01-E4-RELEASE-SET-COMPONENT-HASH-BINDING-GAP.
-- Migration 0009 remains immutable historical evidence.
--
-- New release sets use explicit assembly -> exact Decision binding/finalization.
-- A release set is not promotion-eligible until v1_finalize_release_set() has
-- recomputed the canonical component-set SHA256 from actual membership and bound
-- an exact Decision Receipt to that immutable set.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 0009 required an exact Decision reference at row creation, before component
-- membership existed. Successor semantics allow an assembly-only row with NULL
-- here; the exact Decision is bound only in v1_release_set_finalizations.
ALTER TABLE aaa_ops.v1_release_sets
    ALTER COLUMN exact_decision_receipt_ref DROP NOT NULL;

COMMENT ON COLUMN aaa_ops.v1_release_sets.exact_decision_receipt_ref IS
'Legacy 0009 prebinding reference. NULL is allowed for 0010+ assembly-only rows; authoritative exact Decision binding is recorded by v1_release_set_finalizations after component hash verification.';

CREATE TABLE aaa_ops.v1_release_set_finalizations (
    release_set_id text PRIMARY KEY REFERENCES aaa_ops.v1_release_sets(release_set_id) ON DELETE RESTRICT,
    recomputed_component_set_sha256 char(64) NOT NULL CHECK (recomputed_component_set_sha256 ~ '^[0-9a-f]{64}$'),
    component_count integer NOT NULL CHECK (component_count > 0),
    exact_decision_receipt_ref text NOT NULL REFERENCES aaa_ops.v1_decision_receipts(decision_id),
    finalized_at_db timestamptz NOT NULL DEFAULT transaction_timestamp()
);

COMMENT ON TABLE aaa_ops.v1_release_set_finalizations IS
'0010+ immutable finalization receipt. Its presence means actual component membership was canonically hashed, matched the declared release-set hash, and was bound to an exact APPROVE Decision Receipt.';

-- Keep the 0009 insert trigger for legacy rows, but allow 0010+ assembly-only
-- rows to defer Decision binding until finalization.
CREATE OR REPLACE FUNCTION aaa_ops.v1_verify_release_set_decision()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_decision aaa_ops.v1_decision_receipts%ROWTYPE;
BEGIN
    IF NEW.exact_decision_receipt_ref IS NULL THEN
        RETURN NEW;
    END IF;

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

-- Match aaa.core.release_v1.ReleaseComponentRef.canonical_payload() and
-- CompatibleVersionSet.component_set_sha256 exactly:
--   * components sorted by kind, immutable identity, version, content identity
--   * object keys sorted lexicographically
--   * UTF-8 JSON with compact separators
CREATE OR REPLACE FUNCTION aaa_ops.v1_release_component_canonical_json(
    p_component_kind text,
    p_immutable_identity text,
    p_version text,
    p_content_hash_or_git_identity text,
    p_byte_size bigint,
    p_persistent_locator text
)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT
        '{"byte_size":' ||
        CASE WHEN p_byte_size IS NULL THEN 'null' ELSE p_byte_size::text END ||
        ',"component_kind":' || to_json(p_component_kind)::text ||
        ',"content_hash_or_git_identity":' || to_json(p_content_hash_or_git_identity)::text ||
        ',"immutable_identity":' || to_json(p_immutable_identity)::text ||
        ',"persistent_locator":' ||
        CASE WHEN p_persistent_locator IS NULL THEN 'null' ELSE to_json(p_persistent_locator)::text END ||
        ',"version":' || to_json(p_version)::text ||
        '}'
$$;

CREATE OR REPLACE FUNCTION aaa_ops.v1_recompute_release_set_component_sha256(
    p_release_set_id text
)
RETURNS char(64)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_component_count integer;
    v_canonical_payload text;
BEGIN
    SELECT
        count(*)::integer,
        '[' || string_agg(
            aaa_ops.v1_release_component_canonical_json(
                component_kind,
                immutable_identity,
                version,
                content_hash_or_git_identity,
                byte_size,
                persistent_locator
            ),
            ',' ORDER BY component_kind, immutable_identity, version, content_hash_or_git_identity
        ) || ']'
    INTO v_component_count, v_canonical_payload
    FROM aaa_ops.v1_release_set_components
    WHERE release_set_id = p_release_set_id;

    IF v_component_count = 0 THEN
        RAISE EXCEPTION 'RELEASE_SET_REQUIRES_COMPONENTS';
    END IF;

    RETURN encode(digest(convert_to(v_canonical_payload, 'UTF8'), 'sha256'), 'hex');
END;
$$;

-- Serialize component insertion with finalization on the parent release-set row.
-- After a finalization receipt exists, any new membership is rejected.
CREATE OR REPLACE FUNCTION aaa_ops.v1_guard_release_component_insert()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM 1
    FROM aaa_ops.v1_release_sets
    WHERE release_set_id = NEW.release_set_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'RELEASE_SET_NOT_FOUND';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM aaa_ops.v1_release_set_finalizations
        WHERE release_set_id = NEW.release_set_id
    ) THEN
        RAISE EXCEPTION 'RELEASE_SET_MEMBERSHIP_FINALIZED';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_v1_release_component_insert_guard
BEFORE INSERT ON aaa_ops.v1_release_set_components
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_guard_release_component_insert();

CREATE TRIGGER trg_v1_release_set_finalization_immutable
BEFORE UPDATE OR DELETE ON aaa_ops.v1_release_set_finalizations
FOR EACH ROW EXECUTE FUNCTION aaa_ops.v1_reject_release_set_mutation();

CREATE OR REPLACE FUNCTION aaa_ops.v1_finalize_release_set(
    p_release_set_id text,
    p_exact_decision_receipt_ref text
)
RETURNS char(64)
LANGUAGE plpgsql
AS $$
DECLARE
    v_release aaa_ops.v1_release_sets%ROWTYPE;
    v_decision aaa_ops.v1_decision_receipts%ROWTYPE;
    v_existing aaa_ops.v1_release_set_finalizations%ROWTYPE;
    v_recomputed char(64);
    v_component_count integer;
BEGIN
    SELECT * INTO STRICT v_release
    FROM aaa_ops.v1_release_sets
    WHERE release_set_id = p_release_set_id
    FOR UPDATE;

    SELECT * INTO v_existing
    FROM aaa_ops.v1_release_set_finalizations
    WHERE release_set_id = p_release_set_id;

    IF FOUND THEN
        v_recomputed := aaa_ops.v1_recompute_release_set_component_sha256(p_release_set_id);
        IF v_recomputed <> v_existing.recomputed_component_set_sha256
           OR v_existing.recomputed_component_set_sha256 <> v_release.component_set_sha256
           OR v_existing.exact_decision_receipt_ref <> p_exact_decision_receipt_ref THEN
            RAISE EXCEPTION 'RELEASE_SET_FINALIZATION_IDEMPOTENCY_MISMATCH';
        END IF;
        RETURN v_existing.recomputed_component_set_sha256;
    END IF;

    v_recomputed := aaa_ops.v1_recompute_release_set_component_sha256(p_release_set_id);

    SELECT count(*)::integer INTO v_component_count
    FROM aaa_ops.v1_release_set_components
    WHERE release_set_id = p_release_set_id;

    IF v_recomputed <> v_release.component_set_sha256 THEN
        RAISE EXCEPTION 'RELEASE_SET_COMPONENT_HASH_MISMATCH';
    END IF;

    SELECT * INTO STRICT v_decision
    FROM aaa_ops.v1_decision_receipts
    WHERE decision_id = p_exact_decision_receipt_ref;

    IF v_decision.decision <> 'APPROVE'
       OR v_decision.target_kind <> 'RELEASE_SET'
       OR v_decision.exact_target_identity <> v_release.release_set_id
       OR v_decision.target_content_sha256 IS DISTINCT FROM v_recomputed THEN
        RAISE EXCEPTION 'RELEASE_SET_FINALIZATION_DECISION_MISMATCH';
    END IF;

    -- Legacy 0009 rows may already carry a prebinding Decision reference.
    -- If present, it must agree with the final exact Decision binding.
    IF v_release.exact_decision_receipt_ref IS NOT NULL
       AND v_release.exact_decision_receipt_ref <> p_exact_decision_receipt_ref THEN
        RAISE EXCEPTION 'RELEASE_SET_LEGACY_DECISION_PREBINDING_MISMATCH';
    END IF;

    INSERT INTO aaa_ops.v1_release_set_finalizations(
        release_set_id,
        recomputed_component_set_sha256,
        component_count,
        exact_decision_receipt_ref
    ) VALUES (
        p_release_set_id,
        v_recomputed,
        v_component_count,
        p_exact_decision_receipt_ref
    );

    RETURN v_recomputed;
END;
$$;

-- Promotion receipts are now admissible only for a finalized immutable component set.
CREATE OR REPLACE FUNCTION aaa_ops.v1_promotion_target_guard()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_release aaa_ops.v1_release_sets%ROWTYPE;
    v_finalization aaa_ops.v1_release_set_finalizations%ROWTYPE;
    v_decision aaa_ops.v1_decision_receipts%ROWTYPE;
    v_recomputed char(64);
BEGIN
    SELECT * INTO STRICT v_release
    FROM aaa_ops.v1_release_sets
    WHERE release_set_id = NEW.release_set_id;

    SELECT * INTO v_finalization
    FROM aaa_ops.v1_release_set_finalizations
    WHERE release_set_id = NEW.release_set_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'RELEASE_SET_NOT_FINALIZED';
    END IF;

    v_recomputed := aaa_ops.v1_recompute_release_set_component_sha256(NEW.release_set_id);

    IF v_recomputed <> v_finalization.recomputed_component_set_sha256
       OR v_recomputed <> v_release.component_set_sha256
       OR NEW.source_version_set_hash <> v_recomputed THEN
        RAISE EXCEPTION 'PROMOTION_ACTUAL_RELEASE_SET_HASH_MISMATCH';
    END IF;

    IF NEW.decision_receipt_ref <> v_finalization.exact_decision_receipt_ref THEN
        RAISE EXCEPTION 'PROMOTION_FINALIZED_DECISION_MISMATCH';
    END IF;

    SELECT * INTO STRICT v_decision
    FROM aaa_ops.v1_decision_receipts
    WHERE decision_id = NEW.decision_receipt_ref;

    IF v_decision.decision <> 'APPROVE'
       OR v_decision.target_kind <> 'RELEASE_SET'
       OR v_decision.exact_target_identity <> v_release.release_set_id
       OR v_decision.target_content_sha256 IS DISTINCT FROM v_recomputed THEN
        RAISE EXCEPTION 'PROMOTION_DECISION_EXACT_TARGET_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;

-- Defense in depth: revalidate actual component membership/hash again immediately
-- before any NON-AUTHORITATIVE shadow pointer mutation.
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
    v_finalization aaa_ops.v1_release_set_finalizations%ROWTYPE;
    v_recomputed char(64);
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
    WHERE release_set_id = v_promotion.release_set_id
    FOR SHARE;

    SELECT * INTO STRICT v_finalization
    FROM aaa_ops.v1_release_set_finalizations
    WHERE release_set_id = v_promotion.release_set_id;

    v_recomputed := aaa_ops.v1_recompute_release_set_component_sha256(v_release.release_set_id);

    IF v_recomputed <> v_finalization.recomputed_component_set_sha256
       OR v_recomputed <> v_release.component_set_sha256
       OR v_promotion.source_version_set_hash <> v_recomputed
       OR v_promotion.decision_receipt_ref <> v_finalization.exact_decision_receipt_ref THEN
        RAISE EXCEPTION 'PROMOTION_FINALIZATION_ACTUAL_SET_HASH_MISMATCH';
    END IF;

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

    -- NON-AUTHORITATIVE shadow pointer update remains LAST.
    INSERT INTO aaa_ops.v1_shadow_canonical_pointers(
        pointer_name, release_set_id, component_set_sha256, promotion_id
    ) VALUES (
        p_pointer_name, v_release.release_set_id, v_recomputed, p_promotion_id
    )
    ON CONFLICT (pointer_name) DO UPDATE
    SET release_set_id=EXCLUDED.release_set_id,
        component_set_sha256=EXCLUDED.component_set_sha256,
        promotion_id=EXCLUDED.promotion_id,
        updated_at_db=transaction_timestamp();

    RETURN 'COMPLETED_VERIFIED';
END;
$$;

COMMIT;
