BEGIN;

-- AAA Balanced v1 E1 successor foundation.
-- Historical migrations 0001-0005 remain immutable.
-- PostgreSQL remains NON-AUTHORITATIVE until a separate Owner cutover decision.

CREATE TABLE aaa_ops.v1_identity_bindings (
    project_namespace text NOT NULL,
    entity_family text NOT NULL,
    local_id text NOT NULL,
    identity_payload_sha256 text NOT NULL,
    semantic_generation text NOT NULL DEFAULT 'BALANCED_V1',
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (project_namespace, entity_family, local_id),
    CONSTRAINT v1_identity_project_nonempty CHECK (btrim(project_namespace) <> ''),
    CONSTRAINT v1_identity_family_nonempty CHECK (btrim(entity_family) <> ''),
    CONSTRAINT v1_identity_local_nonempty CHECK (btrim(local_id) <> ''),
    CONSTRAINT v1_identity_hash_shape CHECK (identity_payload_sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT v1_identity_generation CHECK (semantic_generation = 'BALANCED_V1')
);

CREATE TABLE aaa_ops.v1_time_evidence (
    time_evidence_id text PRIMARY KEY,
    time_semantic text NOT NULL,
    precision text NOT NULL,
    value_date date,
    value_datetime_tz timestamptz,
    authority_kind text NOT NULL,
    authority_identity text NOT NULL,
    evidence_or_clock_reference text NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT v1_time_evidence_id_nonempty CHECK (btrim(time_evidence_id) <> ''),
    CONSTRAINT v1_time_semantic_enum CHECK (
        time_semantic IN (
            'FACT_OR_EFFECTIVE_TIME',
            'PUBLIC_EVIDENCE_AVAILABLE_TIME',
            'RECORDED_TIME',
            'SNAPSHOT_CUTOFF_TIME',
            'EXECUTION_LIFECYCLE_TIME'
        )
    ),
    CONSTRAINT v1_time_precision_enum CHECK (precision IN ('DATE', 'DATETIME_TZ')),
    CONSTRAINT v1_time_precision_value CHECK (
        (precision = 'DATE' AND value_date IS NOT NULL AND value_datetime_tz IS NULL)
        OR
        (precision = 'DATETIME_TZ' AND value_datetime_tz IS NOT NULL AND value_date IS NULL)
    ),
    CONSTRAINT v1_time_authority_enum CHECK (
        authority_kind IN (
            'SOURCE_EVIDENCE',
            'GOVERNED_OPERATIONAL_STORE_CLOCK',
            'IMMUTABLE_CERTIFICATION',
            'EXTERNAL_GOVERNED_CALENDAR_OR_TIME_SOURCE'
        )
    ),
    CONSTRAINT v1_time_authority_nonempty CHECK (btrim(authority_identity) <> ''),
    CONSTRAINT v1_time_reference_nonempty CHECK (btrim(evidence_or_clock_reference) <> '')
);

CREATE TABLE aaa_ops.v1_schema_family_versions (
    schema_family_id text NOT NULL,
    schema_version text NOT NULL,
    schema_status text NOT NULL,
    compatibility_with_predecessor text NOT NULL,
    reader_policy text NOT NULL,
    spec_sha256 text NOT NULL,
    predecessor_schema_family_id text,
    predecessor_schema_version text,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (schema_family_id, schema_version),
    CONSTRAINT v1_schema_family_nonempty CHECK (btrim(schema_family_id) <> ''),
    CONSTRAINT v1_schema_version_nonempty CHECK (btrim(schema_version) <> '' AND lower(schema_version) <> 'latest'),
    CONSTRAINT v1_schema_status_enum CHECK (schema_status IN ('WORKING', 'CANDIDATE', 'FROZEN', 'DEPRECATED')),
    CONSTRAINT v1_schema_compat_enum CHECK (
        compatibility_with_predecessor IN (
            'NON_BREAKING_ADDITIVE',
            'BREAKING_SUCCESSOR',
            'REVISION_ONLY_NO_SCHEMA_CHANGE',
            'NOT_APPLICABLE_INITIAL'
        )
    ),
    CONSTRAINT v1_schema_reader_policy_enum CHECK (reader_policy IN ('EXACT_VERSION_ONLY', 'DECLARED_COMPATIBLE_SET')),
    CONSTRAINT v1_schema_hash_shape CHECK (spec_sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT v1_schema_predecessor_pair CHECK (
        (predecessor_schema_family_id IS NULL AND predecessor_schema_version IS NULL)
        OR
        (predecessor_schema_family_id IS NOT NULL AND predecessor_schema_version IS NOT NULL)
    ),
    CONSTRAINT v1_schema_initial_predecessor_rule CHECK (
        (compatibility_with_predecessor = 'NOT_APPLICABLE_INITIAL'
         AND predecessor_schema_family_id IS NULL
         AND predecessor_schema_version IS NULL)
        OR
        (compatibility_with_predecessor <> 'NOT_APPLICABLE_INITIAL'
         AND predecessor_schema_family_id IS NOT NULL
         AND predecessor_schema_version IS NOT NULL)
    ),
    CONSTRAINT v1_schema_not_self_predecessor CHECK (
        predecessor_schema_family_id IS NULL
        OR (predecessor_schema_family_id, predecessor_schema_version) <> (schema_family_id, schema_version)
    ),
    CONSTRAINT v1_schema_predecessor_fk
      FOREIGN KEY (predecessor_schema_family_id, predecessor_schema_version)
      REFERENCES aaa_ops.v1_schema_family_versions(schema_family_id, schema_version)
      DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE aaa_ops.v1_schema_compatible_sets (
    compatible_set_id text PRIMARY KEY,
    reader_schema_family_id text NOT NULL,
    reader_schema_version text NOT NULL,
    component_set_sha256 text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT v1_compatible_set_id_nonempty CHECK (btrim(compatible_set_id) <> ''),
    CONSTRAINT v1_compatible_set_hash_shape CHECK (component_set_sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT v1_compatible_set_reader_fk
      FOREIGN KEY (reader_schema_family_id, reader_schema_version)
      REFERENCES aaa_ops.v1_schema_family_versions(schema_family_id, schema_version)
);

CREATE TABLE aaa_ops.v1_schema_compatible_set_members (
    compatible_set_id text NOT NULL,
    member_schema_family_id text NOT NULL,
    member_schema_version text NOT NULL,
    PRIMARY KEY (compatible_set_id, member_schema_family_id, member_schema_version),
    CONSTRAINT v1_compatible_member_set_fk
      FOREIGN KEY (compatible_set_id)
      REFERENCES aaa_ops.v1_schema_compatible_sets(compatible_set_id)
      ON DELETE CASCADE,
    CONSTRAINT v1_compatible_member_schema_fk
      FOREIGN KEY (member_schema_family_id, member_schema_version)
      REFERENCES aaa_ops.v1_schema_family_versions(schema_family_id, schema_version)
);

COMMENT ON TABLE aaa_ops.v1_identity_bindings IS
'Balanced-v1 typed identity mirror. Presence here does not grant canonical authority.';

COMMENT ON TABLE aaa_ops.v1_time_evidence IS
'Balanced-v1 governed time semantics. DATE and DATETIME_TZ precision are structurally distinct.';

COMMENT ON TABLE aaa_ops.v1_schema_family_versions IS
'Balanced-v1 schema family metadata. Compatibility is declared, never inferred.';

COMMENT ON TABLE aaa_ops.v1_schema_compatible_sets IS
'Directional exact compatible-set declaration for one reader schema identity.';

COMMIT;
