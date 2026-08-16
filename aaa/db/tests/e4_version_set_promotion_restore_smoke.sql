\set ON_ERROR_STOP on

BEGIN;

-- 0010+ successor semantics: assemble component membership first, then bind an
-- exact Decision Receipt by finalizing the canonical component-set hash.
INSERT INTO aaa_ops.v1_release_sets(
    release_set_id, component_set_sha256, compatibility_declaration_ref, exact_decision_receipt_ref
) VALUES
    ('RELEASE-OLD','f6ecabbe7d5c06e1986c0ed84ef1fb5878b8ffcd6ae1aa280b047f2188c23919','COMPAT-E4-OLD',NULL),
    ('RELEASE-NEW','43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27','COMPAT-E4-NEW',NULL),
    ('RELEASE-UNVERIFIED','4ef9c561fdccca82b008f087adb67f94cbcaa3ab7946aeb4848acd5533a399f8','COMPAT-E4-UNVERIFIED',NULL);

INSERT INTO aaa_ops.v1_release_set_components(
    release_set_id, component_kind, immutable_identity, version,
    content_hash_or_git_identity, byte_size, persistent_locator, verified
) VALUES
    ('RELEASE-OLD','MODEL','MODEL-OLD','v1',repeat('a',64),100,'s3://immutable/model-old',true),
    ('RELEASE-NEW','MODEL','MODEL-NEW','v2',repeat('b',64),120,'s3://immutable/model-new',true),
    ('RELEASE-NEW','SHARED_CONTRACT','SHARED-CONTRACT','v0.7',repeat('c',40),4096,'git:shared-contract-v0.7',true),
    ('RELEASE-UNVERIFIED','MODEL','MODEL-UNVERIFIED','v3',repeat('d',64),130,'s3://staging/model-unverified',false);

-- Cross-language canonical hashing must match aaa.core.release_v1 exactly.
DO $$
BEGIN
    IF aaa_ops.v1_recompute_release_set_component_sha256('RELEASE-OLD')
       <> 'f6ecabbe7d5c06e1986c0ed84ef1fb5878b8ffcd6ae1aa280b047f2188c23919' THEN
        RAISE EXCEPTION 'OLD_CANONICAL_COMPONENT_HASH_MISMATCH';
    END IF;
    IF aaa_ops.v1_recompute_release_set_component_sha256('RELEASE-NEW')
       <> '43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27' THEN
        RAISE EXCEPTION 'NEW_CANONICAL_COMPONENT_HASH_MISMATCH';
    END IF;
    IF aaa_ops.v1_recompute_release_set_component_sha256('RELEASE-UNVERIFIED')
       <> '4ef9c561fdccca82b008f087adb67f94cbcaa3ab7946aeb4848acd5533a399f8' THEN
        RAISE EXCEPTION 'UNVERIFIED_CANONICAL_COMPONENT_HASH_MISMATCH';
    END IF;
END $$;

-- Exact release-set decisions are created after membership assembly.
INSERT INTO aaa_ops.v1_decision_receipts (
    decision_id, decision_type, target_kind, exact_target_identity, target_content_sha256,
    actor_type, actor_identity, authority_role, authority_identity, authority_scope,
    authority_source_ref, decision, decided_at
) VALUES
    ('DEC-E4-OLD','RELEASE','RELEASE_SET','RELEASE-OLD','f6ecabbe7d5c06e1986c0ed84ef1fb5878b8ffcd6ae1aa280b047f2188c23919',
     'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER','RELEASE','OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp()),
    ('DEC-E4-NEW','RELEASE','RELEASE_SET','RELEASE-NEW','43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27',
     'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER','RELEASE','OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp()),
    ('DEC-E4-UNVERIFIED','RELEASE','RELEASE_SET','RELEASE-UNVERIFIED','4ef9c561fdccca82b008f087adb67f94cbcaa3ab7946aeb4848acd5533a399f8',
     'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER','RELEASE','OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp());

SELECT aaa_ops.v1_finalize_release_set('RELEASE-OLD','DEC-E4-OLD');
SELECT aaa_ops.v1_finalize_release_set('RELEASE-NEW','DEC-E4-NEW');
SELECT aaa_ops.v1_finalize_release_set('RELEASE-UNVERIFIED','DEC-E4-UNVERIFIED');

-- Finalization is idempotent only for the exact same immutable set and decision.
DO $$
BEGIN
    IF aaa_ops.v1_finalize_release_set('RELEASE-NEW','DEC-E4-NEW')
       <> '43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27' THEN
        RAISE EXCEPTION 'FINALIZATION_IDEMPOTENCY_FAILED';
    END IF;
END $$;

-- Floating latest is prohibited.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_release_set_components(
            release_set_id, component_kind, immutable_identity, version,
            content_hash_or_git_identity, verified
        ) VALUES ('RELEASE-NEW','SCHEMA','SCHEMA-X','latest',repeat('e',64),true);
        RAISE EXCEPTION 'FLOATING_LATEST_COMPONENT_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'FLOATING_LATEST_COMPONENT_ACCEPTED' THEN RAISE; END IF;
    END;
END $$;

-- Adversarial 1: arbitrary stored hash + different actual components must reject.
INSERT INTO aaa_ops.v1_release_sets(
    release_set_id, component_set_sha256, compatibility_declaration_ref, exact_decision_receipt_ref
) VALUES ('RELEASE-BADHASH',repeat('9',64),'COMPAT-E4-BADHASH',NULL);

INSERT INTO aaa_ops.v1_release_set_components(
    release_set_id, component_kind, immutable_identity, version,
    content_hash_or_git_identity, byte_size, persistent_locator, verified
) VALUES ('RELEASE-BADHASH','MODEL','MODEL-BADHASH','v1',repeat('e',64),50,'s3://immutable/model-badhash',true);

INSERT INTO aaa_ops.v1_decision_receipts (
    decision_id, decision_type, target_kind, exact_target_identity, target_content_sha256,
    actor_type, actor_identity, authority_role, authority_identity, authority_scope,
    authority_source_ref, decision, decided_at
) VALUES (
    'DEC-E4-BADHASH','RELEASE','RELEASE_SET','RELEASE-BADHASH',repeat('9',64),
    'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER','RELEASE',
    'OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp()
);

DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.v1_finalize_release_set('RELEASE-BADHASH','DEC-E4-BADHASH');
        RAISE EXCEPTION 'ARBITRARY_STORED_HASH_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'ARBITRARY_STORED_HASH_ACCEPTED' THEN RAISE; END IF;
        IF SQLERRM <> 'RELEASE_SET_COMPONENT_HASH_MISMATCH' THEN RAISE; END IF;
    END;
END $$;

-- Adversarial 2/3/4: once exact Decision binding/finalization occurs, membership
-- is frozen; material change cannot reuse the stale Decision.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_release_set_components(
            release_set_id, component_kind, immutable_identity, version,
            content_hash_or_git_identity, byte_size, persistent_locator, verified
        ) VALUES (
            'RELEASE-NEW','SCHEMA','SCHEMA-AFTER-DECISION','v1',
            repeat('f',64),25,'s3://immutable/schema-after-decision',true
        );
        RAISE EXCEPTION 'POST_DECISION_COMPONENT_INSERT_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'POST_DECISION_COMPONENT_INSERT_ACCEPTED' THEN RAISE; END IF;
        IF SQLERRM <> 'RELEASE_SET_MEMBERSHIP_FINALIZED' THEN RAISE; END IF;
    END;
END $$;

-- A stale Decision hash cannot survive a pre-finalization material membership change.
INSERT INTO aaa_ops.v1_release_sets(
    release_set_id, component_set_sha256, compatibility_declaration_ref, exact_decision_receipt_ref
) VALUES (
    'RELEASE-STALE',
    '517562b28676a1556ed1ef9f13373a9af8b157c4bcfc04af5c294f77fd37c5be',
    'COMPAT-E4-STALE',
    NULL
);
INSERT INTO aaa_ops.v1_release_set_components(
    release_set_id, component_kind, immutable_identity, version,
    content_hash_or_git_identity, byte_size, persistent_locator, verified
) VALUES
    ('RELEASE-STALE','MODEL','MODEL-STALE','v1',repeat('e',64),50,'s3://immutable/model-stale',true),
    ('RELEASE-STALE','SCHEMA','SCHEMA-STALE','v1',repeat('f',64),25,'s3://immutable/schema-stale',true);
INSERT INTO aaa_ops.v1_decision_receipts (
    decision_id, decision_type, target_kind, exact_target_identity, target_content_sha256,
    actor_type, actor_identity, authority_role, authority_identity, authority_scope,
    authority_source_ref, decision, decided_at
) VALUES (
    'DEC-E4-STALE','RELEASE','RELEASE_SET','RELEASE-STALE',
    '517562b28676a1556ed1ef9f13373a9af8b157c4bcfc04af5c294f77fd37c5be',
    'HUMAN_OWNER','PROJECT_OWNER','PROJECT_OWNER','PROJECT_OWNER','RELEASE',
    'OWNER-AUTHORITY-MATRIX','APPROVE',transaction_timestamp()
);
DO $$
BEGIN
    BEGIN
        PERFORM aaa_ops.v1_finalize_release_set('RELEASE-STALE','DEC-E4-STALE');
        RAISE EXCEPTION 'STALE_DECISION_REUSE_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'STALE_DECISION_REUSE_ACCEPTED' THEN RAISE; END IF;
        IF SQLERRM <> 'RELEASE_SET_COMPONENT_HASH_MISMATCH' THEN RAISE; END IF;
    END;
END $$;

-- Promotion of a release set that failed finalization is prohibited and cannot
-- mutate the shadow pointer.
DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_promotion_receipts(
            promotion_id, promotion_kind, release_set_id, source_version_set_hash,
            decision_receipt_ref, actor_ref, authority_ref
        ) VALUES (
            'PROMO-BADHASH','SHADOW_PROMOTION','RELEASE-BADHASH',repeat('9',64),
            'DEC-E4-BADHASH','ACTOR-E4','AUTH-E4'
        );
        RAISE EXCEPTION 'UNFINALIZED_MISMATCHED_SET_PROMOTION_ACCEPTED';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'UNFINALIZED_MISMATCHED_SET_PROMOTION_ACCEPTED' THEN RAISE; END IF;
        IF SQLERRM <> 'RELEASE_SET_NOT_FINALIZED' THEN RAISE; END IF;
    END;
END $$;

-- Establish an OLD non-authoritative shadow pointer through a fully verified promotion.
INSERT INTO aaa_ops.v1_promotion_receipts(
    promotion_id, promotion_kind, release_set_id, source_version_set_hash,
    decision_receipt_ref, actor_ref, authority_ref
) VALUES (
    'PROMO-OLD','SHADOW_PROMOTION','RELEASE-OLD',
    'f6ecabbe7d5c06e1986c0ed84ef1fb5878b8ffcd6ae1aa280b047f2188c23919',
    'DEC-E4-OLD','ACTOR-E4','AUTH-E4'
);
INSERT INTO aaa_ops.v1_promotion_destination_receipts(
    promotion_id,destination_store,destination_namespace,status,object_identity,content_sha256,byte_size
) VALUES ('PROMO-OLD','S3','shadow','VERIFIED','OBJ-OLD',repeat('a',64),100);
DO $$
DECLARE v text;
BEGIN
    SELECT aaa_ops.v1_finalize_shadow_promotion('PROMO-OLD','CURRENT-RELEASE') INTO v;
    IF v <> 'COMPLETED_VERIFIED' THEN RAISE EXCEPTION 'OLD_PROMOTION_NOT_VERIFIED'; END IF;
    IF (SELECT release_set_id FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE') <> 'RELEASE-OLD' THEN
        RAISE EXCEPTION 'OLD_POINTER_NOT_ESTABLISHED';
    END IF;
END $$;

-- Adversarial 5: mismatched actual-set/stored-hash promotion leaves pointer unchanged.
DO $$
BEGIN
    IF (SELECT release_set_id FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE') <> 'RELEASE-OLD' THEN
        RAISE EXCEPTION 'BADHASH_ATTEMPT_CHANGED_POINTER';
    END IF;
END $$;

-- Partial multi-store promotion must fail closed and leave the pointer unchanged.
INSERT INTO aaa_ops.v1_promotion_receipts(
    promotion_id, promotion_kind, release_set_id, source_version_set_hash,
    decision_receipt_ref, actor_ref, authority_ref
) VALUES (
    'PROMO-NEW-PARTIAL','SHADOW_PROMOTION','RELEASE-NEW',
    '43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27',
    'DEC-E4-NEW','ACTOR-E4','AUTH-E4'
);
INSERT INTO aaa_ops.v1_promotion_destination_receipts(
    promotion_id,destination_store,destination_namespace,status,object_identity,content_sha256,byte_size
) VALUES
    ('PROMO-NEW-PARTIAL','S3','shadow','VERIFIED','OBJ-NEW-S3',repeat('b',64),120),
    ('PROMO-NEW-PARTIAL','GIT','shadow','FAILED',NULL,NULL,NULL);
DO $$
DECLARE v text;
BEGIN
    SELECT aaa_ops.v1_finalize_shadow_promotion('PROMO-NEW-PARTIAL','CURRENT-RELEASE') INTO v;
    IF v <> 'FAILED_PARTIAL_FAIL_CLOSED' THEN RAISE EXCEPTION 'PARTIAL_PROMOTION_DID_NOT_FAIL_CLOSED'; END IF;
    IF (SELECT release_set_id FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE') <> 'RELEASE-OLD' THEN
        RAISE EXCEPTION 'PARTIAL_PROMOTION_CHANGED_POINTER';
    END IF;
END $$;

-- All destinations verified, but an unverified component still cannot promote.
INSERT INTO aaa_ops.v1_promotion_receipts(
    promotion_id, promotion_kind, release_set_id, source_version_set_hash,
    decision_receipt_ref, actor_ref, authority_ref
) VALUES (
    'PROMO-UNVERIFIED','SHADOW_PROMOTION','RELEASE-UNVERIFIED',
    '4ef9c561fdccca82b008f087adb67f94cbcaa3ab7946aeb4848acd5533a399f8',
    'DEC-E4-UNVERIFIED','ACTOR-E4','AUTH-E4'
);
INSERT INTO aaa_ops.v1_promotion_destination_receipts(
    promotion_id,destination_store,destination_namespace,status,object_identity,content_sha256,byte_size
) VALUES ('PROMO-UNVERIFIED','S3','shadow','VERIFIED','OBJ-U',repeat('d',64),130);
DO $$
DECLARE v text;
BEGIN
    SELECT aaa_ops.v1_finalize_shadow_promotion('PROMO-UNVERIFIED','CURRENT-RELEASE') INTO v;
    IF v <> 'FAILED_NO_PROMOTION' THEN RAISE EXCEPTION 'UNVERIFIED_COMPONENT_PROMOTED'; END IF;
    IF (SELECT release_set_id FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE') <> 'RELEASE-OLD' THEN
        RAISE EXCEPTION 'UNVERIFIED_COMPONENT_CHANGED_POINTER';
    END IF;
END $$;

-- Fully verified NEW promotion updates the NON-AUTHORITATIVE shadow pointer only after verification.
INSERT INTO aaa_ops.v1_promotion_receipts(
    promotion_id, promotion_kind, release_set_id, source_version_set_hash,
    decision_receipt_ref, actor_ref, authority_ref
) VALUES (
    'PROMO-NEW-GOOD','SHADOW_PROMOTION','RELEASE-NEW',
    '43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27',
    'DEC-E4-NEW','ACTOR-E4','AUTH-E4'
);
INSERT INTO aaa_ops.v1_promotion_destination_receipts(
    promotion_id,destination_store,destination_namespace,status,object_identity,content_sha256,byte_size
) VALUES
    ('PROMO-NEW-GOOD','S3','shadow','VERIFIED','OBJ-NEW-S3',repeat('b',64),120),
    ('PROMO-NEW-GOOD','GIT','shadow','VERIFIED','OBJ-NEW-GIT',repeat('c',64),4096);
DO $$
DECLARE v text;
BEGIN
    SELECT aaa_ops.v1_finalize_shadow_promotion('PROMO-NEW-GOOD','CURRENT-RELEASE') INTO v;
    IF v <> 'COMPLETED_VERIFIED' THEN RAISE EXCEPTION 'FULL_PROMOTION_NOT_COMPLETED'; END IF;
    IF (SELECT release_set_id FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE') <> 'RELEASE-NEW' THEN
        RAISE EXCEPTION 'VERIFIED_PROMOTION_DID_NOT_UPDATE_SHADOW_POINTER';
    END IF;
    IF (SELECT component_set_sha256 FROM aaa_ops.v1_shadow_canonical_pointers WHERE pointer_name='CURRENT-RELEASE')
       <> '43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27' THEN
        RAISE EXCEPTION 'VERIFIED_PROMOTION_POINTER_HASH_MISMATCH';
    END IF;
END $$;

-- Restore lifecycle: creation != verification != Operational SoT authority.
INSERT INTO aaa_ops.v1_restore_manifests(
    restore_manifest_id, backup_or_snapshot_identity, source_store_kind, target_store_kind,
    schema_migration_version_set, immutable_artifact_refs, restore_target_identity,
    verification_plan_ref, provider_metadata
) VALUES (
    'RESTORE-E4-1','BACKUP-E4-1','POSTGRESQL_BACKUP','POSTGRESQL',
    '["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]'::jsonb,
    '[{"immutable_identity":"ART-E4-1","sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","byte_size":1234,"persistent_locator":"s3://immutable/art-e4-1"}]'::jsonb,
    'PG-RESTORE-E4-1','VERIFY-PLAN-E4-1','{"provider":"local-docker"}'::jsonb
);
DO $$
BEGIN
    IF (SELECT status FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') <> 'PREPARED' THEN
        RAISE EXCEPTION 'RESTORE_NOT_PREPARED';
    END IF;
    IF (SELECT operational_sot_authorized FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') THEN
        RAISE EXCEPTION 'RESTORE_CREATION_AUTHORIZED_SOT';
    END IF;
END $$;

SELECT aaa_ops.v1_mark_restore_unverified('RESTORE-E4-1');
DO $$
BEGIN
    IF (SELECT status FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') <> 'RESTORED_UNVERIFIED' THEN
        RAISE EXCEPTION 'RESTORE_NOT_UNVERIFIED_AFTER_RESTORE';
    END IF;
    BEGIN
        UPDATE aaa_ops.v1_restore_manifests SET operational_sot_authorized=true WHERE restore_manifest_id='RESTORE-E4-1';
        RAISE EXCEPTION 'UNVERIFIED_RESTORE_AUTHORIZED_SOT';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END $$;

SELECT aaa_ops.v1_verify_restore('RESTORE-E4-1','["VERIFY-RESULT-E4-1"]'::jsonb);
DO $$
BEGIN
    IF (SELECT status FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') <> 'RESTORED_VERIFIED' THEN
        RAISE EXCEPTION 'RESTORE_VERIFICATION_FAILED';
    END IF;
    IF (SELECT operational_sot_authorized FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') THEN
        RAISE EXCEPTION 'VERIFIED_RESTORE_AUTO_AUTHORIZED_SOT';
    END IF;
    IF (SELECT managed_pitr_rpo_rto_qualification_ref FROM aaa_ops.v1_restore_manifests WHERE restore_manifest_id='RESTORE-E4-1') IS NOT NULL THEN
        RAISE EXCEPTION 'LOCAL_RESTORE_FABRICATED_MANAGED_QUALIFICATION';
    END IF;
    BEGIN
        UPDATE aaa_ops.v1_restore_manifests SET restore_target_identity='MUTATED' WHERE restore_manifest_id='RESTORE-E4-1';
        RAISE EXCEPTION 'RESTORE_SEMANTIC_IDENTITY_MUTABLE';
    EXCEPTION WHEN OTHERS THEN
        IF SQLERRM = 'RESTORE_SEMANTIC_IDENTITY_MUTABLE' THEN RAISE; END IF;
    END;
END $$;

-- PostgreSQL/shadow pointers remain explicitly non-authoritative.
DO $$
BEGIN
    IF obj_description('aaa_ops.v1_shadow_canonical_pointers'::regclass) NOT LIKE '%NON-AUTHORITATIVE%' THEN
        RAISE EXCEPTION 'SHADOW_POINTER_AUTHORITY_BOUNDARY_COMMENT_MISSING';
    END IF;
    IF obj_description('aaa_ops.v1_restore_manifests'::regclass) NOT LIKE '%does not authorize PostgreSQL Operational SoT%' THEN
        RAISE EXCEPTION 'RESTORE_AUTHORITY_BOUNDARY_COMMENT_MISSING';
    END IF;
END $$;

ROLLBACK;
