\set ON_ERROR_STOP on

BEGIN;

-- Typed identity: same raw local_id across different entity families is allowed
-- because the canonical tuple is typed. Same tuple with conflicting payload fails closed.
INSERT INTO aaa_ops.v1_identity_bindings(
    project_namespace, entity_family, local_id, identity_payload_sha256
) VALUES
    ('SEMICONDUCTOR_RESEARCH', 'LOGICAL_RUN', 'ID-001', repeat('a', 64)),
    ('SEMICONDUCTOR_RESEARCH', 'ECONOMIC_EVENT', 'ID-001', repeat('b', 64));

DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_identity_bindings(
            project_namespace, entity_family, local_id, identity_payload_sha256
        ) VALUES ('SEMICONDUCTOR_RESEARCH', 'LOGICAL_RUN', 'ID-001', repeat('c', 64));
        RAISE EXCEPTION 'DUPLICATE_TYPED_IDENTITY_DID_NOT_FAIL';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;
END $$;

-- DATE precision is physically distinct from DATETIME_TZ; no intraday timestamp can
-- be inserted under DATE precision.
INSERT INTO aaa_ops.v1_time_evidence(
    time_evidence_id, time_semantic, precision, value_date,
    authority_kind, authority_identity, evidence_or_clock_reference
) VALUES (
    'TIME-E1-DATE-001', 'PUBLIC_EVIDENCE_AVAILABLE_TIME', 'DATE', DATE '2026-08-16',
    'IMMUTABLE_CERTIFICATION', 'PIT-CERTIFIER', 'CERT-001'
);

DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_time_evidence(
            time_evidence_id, time_semantic, precision, value_date, value_datetime_tz,
            authority_kind, authority_identity, evidence_or_clock_reference
        ) VALUES (
            'TIME-E1-BAD-001', 'PUBLIC_EVIDENCE_AVAILABLE_TIME', 'DATE', DATE '2026-08-16', now(),
            'SOURCE_EVIDENCE', 'SOURCE-1', 'EVIDENCE-1'
        );
        RAISE EXCEPTION 'DATE_PRECISION_ACCEPTED_INTRADAY_TIMESTAMP';
    EXCEPTION WHEN check_violation THEN
        NULL;
    END;
END $$;

-- Schema-family identities are exact; floating latest and implicit compatibility are rejected.
INSERT INTO aaa_ops.v1_schema_family_versions(
    schema_family_id, schema_version, schema_status,
    compatibility_with_predecessor, reader_policy, spec_sha256
) VALUES (
    'MODEL_INPUT_SCHEMA', 'MIS-v1.0', 'FROZEN',
    'NOT_APPLICABLE_INITIAL', 'EXACT_VERSION_ONLY', repeat('d', 64)
);

INSERT INTO aaa_ops.v1_schema_family_versions(
    schema_family_id, schema_version, schema_status,
    compatibility_with_predecessor, reader_policy, spec_sha256,
    predecessor_schema_family_id, predecessor_schema_version
) VALUES (
    'MODEL_INPUT_SCHEMA', 'MIS-v1.1', 'WORKING',
    'NON_BREAKING_ADDITIVE', 'DECLARED_COMPATIBLE_SET', repeat('e', 64),
    'MODEL_INPUT_SCHEMA', 'MIS-v1.0'
);

DO $$
BEGIN
    BEGIN
        INSERT INTO aaa_ops.v1_schema_family_versions(
            schema_family_id, schema_version, schema_status,
            compatibility_with_predecessor, reader_policy, spec_sha256
        ) VALUES (
            'MODEL_INPUT_SCHEMA', 'latest', 'WORKING',
            'NOT_APPLICABLE_INITIAL', 'EXACT_VERSION_ONLY', repeat('f', 64)
        );
        RAISE EXCEPTION 'FLOATING_LATEST_SCHEMA_VERSION_ACCEPTED';
    EXCEPTION WHEN check_violation THEN
        NULL;
    END;
END $$;

INSERT INTO aaa_ops.v1_schema_compatible_sets(
    compatible_set_id, reader_schema_family_id, reader_schema_version, component_set_sha256
) VALUES (
    'COMPAT-MIS-v1.1', 'MODEL_INPUT_SCHEMA', 'MIS-v1.1', repeat('1', 64)
);

INSERT INTO aaa_ops.v1_schema_compatible_set_members(
    compatible_set_id, member_schema_family_id, member_schema_version
) VALUES
    ('COMPAT-MIS-v1.1', 'MODEL_INPUT_SCHEMA', 'MIS-v1.0'),
    ('COMPAT-MIS-v1.1', 'MODEL_INPUT_SCHEMA', 'MIS-v1.1');

DO $$
DECLARE
    reverse_count integer;
BEGIN
    SELECT count(*) INTO reverse_count
    FROM aaa_ops.v1_schema_compatible_sets s
    JOIN aaa_ops.v1_schema_compatible_set_members m USING (compatible_set_id)
    WHERE s.reader_schema_family_id = 'MODEL_INPUT_SCHEMA'
      AND s.reader_schema_version = 'MIS-v1.0'
      AND m.member_schema_family_id = 'MODEL_INPUT_SCHEMA'
      AND m.member_schema_version = 'MIS-v1.1';
    IF reverse_count <> 0 THEN
        RAISE EXCEPTION 'COMPATIBILITY_WAS_IMPLICITLY_MADE_SYMMETRIC';
    END IF;
END $$;

-- PostgreSQL remains a non-authoritative mirror; E1 adds successor foundation only.
DO $$
BEGIN
    IF obj_description('aaa_ops.v1_identity_bindings'::regclass) NOT LIKE '%does not grant canonical authority%' THEN
        RAISE EXCEPTION 'IDENTITY_TABLE_AUTHORITY_BOUNDARY_COMMENT_MISSING';
    END IF;
END $$;

ROLLBACK;
