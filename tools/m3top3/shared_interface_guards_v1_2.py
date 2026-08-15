from __future__ import annotations

import json
from collections.abc import Iterator, Mapping as ABCMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .contracts_v1 import MODEL_VERSION
from .core import parse_datetime, sha256_hex
from .shared_interface_guards_v1 import SharedInterfaceGuardError
from .shared_interface_guards_v1_1 import (
    FEATURE_INPUT_REGISTRY_RELEASE_ID,
    FEATURE_INPUT_REGISTRY_SHA256,
    F02_COMPATIBILITY_NOTE_PATH,
    REFRESH_REGISTRY_RELEASE_ID,
    REFRESH_REGISTRY_SHA256,
    REPO_ROOT,
    FeatureInputRegistry,
    typed_governance_object_hash,
    validate_consumed_value_provenance_v1_1,
    verify_shared_asset_bindings,
)

GUARD_IMPLEMENTATION_VERSION = "M3TOP3-SHARED-INTERFACE-GUARDS-v1.2-CONTROL-FIX_WORKING"

EVIDENCE_AUTHORITY_PATH = "control/shared/M3TOP3-EVIDENCE-RESOLVER-AUTHORITY_v1.0_WORKING.json"
NUMERIC_RULE_AUTHORITY_PATH = "control/shared/M3TOP3-F08-NUMERIC-RULE-AUTHORITY_v1.0_WORKING.json"
RECORD_LEVEL_POLICY_PATH = "control/shared/M3TOP3-RECORD-LEVEL-BINDING-POLICY_v1.0_WORKING.json"

EVIDENCE_AUTHORITY_RELEASE_ID = "M3TOP3-EVIDENCE-RESOLVER-AUTHORITY_v1.0_WORKING"
NUMERIC_RULE_AUTHORITY_RELEASE_ID = "M3TOP3-F08-NUMERIC-RULE-AUTHORITY_v1.0_WORKING"
RECORD_LEVEL_POLICY_RELEASE_ID = "M3TOP3-RECORD-LEVEL-BINDING-POLICY_v1.0_WORKING"


@dataclass(frozen=True)
class BoundControlFixAsset:
    path: str
    sha256: str
    byte_size: int
    git_blob_sha: str


BOUND_CONTROL_FIX_ASSETS = (
    BoundControlFixAsset(
        EVIDENCE_AUTHORITY_PATH,
        "b2e00077f1239b43c6328c0d009df1bae4110e9ffc6d6840d02f67380399ea8f",
        711,
        "3c8442373354f74ce1a351bc0872551f76ab6e5e",
    ),
    BoundControlFixAsset(
        NUMERIC_RULE_AUTHORITY_PATH,
        "3b7200eb92f5e9b162035b1cd92f775f3b80039eb679af09e59343209586b2d7",
        744,
        "5b56f7944a1c0935a9bd296771bd542682c31c09",
    ),
    BoundControlFixAsset(
        RECORD_LEVEL_POLICY_PATH,
        "8f05200e1937761e172995d23f1a344de4d8102cb22fc46782f99f8f1f7fa749",
        1690,
        "fa793a9518eb9cf4eea169aa130702781a0ac9bc",
    ),
)
BOUND_CONTROL_FIX_ASSET_BY_PATH = {a.path: a for a in BOUND_CONTROL_FIX_ASSETS}

EVIDENCE_AUTHORITY_SHA256 = BOUND_CONTROL_FIX_ASSET_BY_PATH[EVIDENCE_AUTHORITY_PATH].sha256
NUMERIC_RULE_AUTHORITY_SHA256 = BOUND_CONTROL_FIX_ASSET_BY_PATH[NUMERIC_RULE_AUTHORITY_PATH].sha256
RECORD_LEVEL_POLICY_SHA256 = BOUND_CONTROL_FIX_ASSET_BY_PATH[RECORD_LEVEL_POLICY_PATH].sha256


def _git_blob_sha(data: bytes) -> str:
    import hashlib

    prefix = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(prefix + data).hexdigest()


def verify_control_fix_asset_bindings(repo_root: str | Path = REPO_ROOT) -> dict[str, dict[str, Any]]:
    import hashlib

    root = Path(repo_root)
    result: dict[str, dict[str, Any]] = {}
    for asset in BOUND_CONTROL_FIX_ASSETS:
        path = root / asset.path
        if not path.is_file():
            raise SharedInterfaceGuardError(f"control-fix bound asset missing: {asset.path}")
        data = path.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        byte_size = len(data)
        blob = _git_blob_sha(data)
        if sha256 != asset.sha256:
            raise SharedInterfaceGuardError(f"control-fix asset SHA256 mismatch: {asset.path}")
        if byte_size != asset.byte_size:
            raise SharedInterfaceGuardError(f"control-fix asset byte-size mismatch: {asset.path}")
        if blob != asset.git_blob_sha:
            raise SharedInterfaceGuardError(f"control-fix asset Git-blob mismatch: {asset.path}")
        result[asset.path] = {
            "sha256": sha256,
            "byte_size": byte_size,
            "git_blob_sha": blob,
            "status": "PASS",
        }
    return result


def _read_bound_json(path: str, repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    import hashlib

    asset = BOUND_CONTROL_FIX_ASSET_BY_PATH[path]
    data = (Path(repo_root) / path).read_bytes()
    if hashlib.sha256(data).hexdigest() != asset.sha256:
        raise SharedInterfaceGuardError(f"control-fix bound asset SHA256 mismatch: {path}")
    if len(data) != asset.byte_size or _git_blob_sha(data) != asset.git_blob_sha:
        raise SharedInterfaceGuardError(f"control-fix bound asset physical identity mismatch: {path}")
    obj = json.loads(data.decode("utf-8"))
    if not isinstance(obj, dict):
        raise SharedInterfaceGuardError(f"control-fix bound asset must decode to object: {path}")
    return obj


def _is_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text.lower())


def evidence_resolver_release_hash(
    release_id: str,
    version: str,
    persistent_locator: str,
    objects: Mapping[str, Mapping[str, Any]],
) -> str:
    return sha256_hex(
        {
            "release_id": release_id,
            "version": version,
            "persistent_locator": persistent_locator,
            "objects": objects,
        }
    )


@dataclass(frozen=True)
class EvidenceResolverRelease:
    release_id: str
    version: str
    persistent_locator: str
    objects: Mapping[str, Mapping[str, Any]]
    release_content_sha256: str
    test_only: bool = False

    @classmethod
    def synthetic(
        cls,
        objects: Mapping[str, Mapping[str, Any]],
        *,
        release_id: str = "SYNTHETIC-EVIDENCE-RESOLVER-v1",
        version: str = "v1",
        persistent_locator: str = "synthetic://evidence-resolver",
    ) -> "EvidenceResolverRelease":
        normalized = {str(k): dict(v) for k, v in objects.items()}
        return cls(
            release_id=release_id,
            version=version,
            persistent_locator=persistent_locator,
            objects=normalized,
            release_content_sha256=evidence_resolver_release_hash(
                release_id, version, persistent_locator, normalized
            ),
            test_only=True,
        )

    def _verify_internal_release_hash(self) -> None:
        actual = evidence_resolver_release_hash(
            self.release_id, self.version, self.persistent_locator, self.objects
        )
        if not _is_sha256(self.release_content_sha256) or actual != self.release_content_sha256:
            raise SharedInterfaceGuardError("evidence resolver release content hash mismatch")

    def validate_binding(
        self,
        repo_root: str | Path = REPO_ROOT,
        *,
        allow_test_resolver: bool = False,
    ) -> None:
        self._verify_internal_release_hash()
        if not self.persistent_locator:
            raise SharedInterfaceGuardError("evidence resolver persistent locator required")
        if self.test_only:
            if not allow_test_resolver:
                raise SharedInterfaceGuardError("TEST_ONLY evidence resolver prohibited in official path")
            return

        authority = _read_bound_json(EVIDENCE_AUTHORITY_PATH, repo_root)
        if authority.get("authority_release_id") != EVIDENCE_AUTHORITY_RELEASE_ID:
            raise SharedInterfaceGuardError("evidence resolver authority release identity mismatch")
        entries = authority.get("approved_evidence_resolver_releases")
        if not isinstance(entries, list):
            raise SharedInterfaceGuardError("evidence resolver authority approved-release list missing")
        match = next(
            (
                entry
                for entry in entries
                if isinstance(entry, Mapping)
                and entry.get("release_id") == self.release_id
                and entry.get("version") == self.version
            ),
            None,
        )
        if not match:
            raise SharedInterfaceGuardError("evidence resolver release is not persistently approved")
        required = ("content_sha256", "persistent_locator", "authority_identity")
        missing = [field for field in required if not match.get(field)]
        if missing:
            raise SharedInterfaceGuardError(
                f"approved evidence resolver release binding incomplete: {missing}"
            )
        if match["content_sha256"] != self.release_content_sha256:
            raise SharedInterfaceGuardError("approved evidence resolver release hash mismatch")
        if match["persistent_locator"] != self.persistent_locator:
            raise SharedInterfaceGuardError("approved evidence resolver locator mismatch")
        if match["authority_identity"] != EVIDENCE_AUTHORITY_RELEASE_ID:
            raise SharedInterfaceGuardError("approved evidence resolver authority identity mismatch")

    def resolve(self, ref: str, *, cutoff_at: str | None = None) -> Mapping[str, Any]:
        ref = str(ref)
        obj = self.objects.get(ref)
        if not isinstance(obj, Mapping):
            raise SharedInterfaceGuardError(f"immutable evidence reference unresolved: {ref}")
        if obj.get("evidence_ref") not in (None, ref):
            raise SharedInterfaceGuardError(f"evidence object identity mismatch: {ref}")
        if not _is_sha256(obj.get("content_sha256")):
            raise SharedInterfaceGuardError(f"evidence object content SHA256 missing/invalid: {ref}")
        if not obj.get("persistent_locator"):
            raise SharedInterfaceGuardError(f"evidence object persistent locator missing: {ref}")
        lineage = obj.get("source_lineage") or obj.get("source_evidence_lineage")
        if not isinstance(lineage, (list, tuple)) or not lineage:
            raise SharedInterfaceGuardError(f"evidence object source/evidence lineage missing: {ref}")
        support_time = obj.get("publication_at") or obj.get("supported_cutoff_at")
        if not support_time:
            raise SharedInterfaceGuardError(f"evidence object publication/support time missing: {ref}")
        if cutoff_at is not None and parse_datetime(str(support_time)) > parse_datetime(str(cutoff_at)):
            raise SharedInterfaceGuardError(
                f"evidence object publication/support time exceeds snapshot cutoff: {ref}"
            )
        return obj


class EvidenceResolverView(ABCMapping[str, Mapping[str, Any]]):
    def __init__(self, resolver: EvidenceResolverRelease, cutoff_at: str):
        self.resolver = resolver
        self.cutoff_at = cutoff_at

    def __getitem__(self, key: str) -> Mapping[str, Any]:
        return self.resolver.resolve(str(key), cutoff_at=self.cutoff_at)

    def __iter__(self) -> Iterator[str]:
        return iter(self.resolver.objects)

    def __len__(self) -> int:
        return len(self.resolver.objects)

    def __contains__(self, key: object) -> bool:
        try:
            self.resolver.resolve(str(key), cutoff_at=self.cutoff_at)
        except SharedInterfaceGuardError:
            return False
        return True


def numeric_rule_resolver_release_hash(
    release_id: str,
    version: str,
    persistent_locator: str,
    rules: Mapping[str, Mapping[str, Any]],
) -> str:
    return sha256_hex(
        {
            "release_id": release_id,
            "version": version,
            "persistent_locator": persistent_locator,
            "rules": rules,
        }
    )


@dataclass(frozen=True)
class NumericRuleResolverRelease:
    release_id: str
    version: str
    persistent_locator: str
    rules: Mapping[str, Mapping[str, Any]]
    release_content_sha256: str
    test_only: bool = False

    @classmethod
    def synthetic(
        cls,
        rules: Mapping[str, Mapping[str, Any]],
        *,
        release_id: str = "SYNTHETIC-F08-NUMERIC-RULE-RESOLVER-v1",
        version: str = "v1",
        persistent_locator: str = "synthetic://f08-numeric-rule-resolver",
    ) -> "NumericRuleResolverRelease":
        normalized = {str(k): dict(v) for k, v in rules.items()}
        return cls(
            release_id=release_id,
            version=version,
            persistent_locator=persistent_locator,
            rules=normalized,
            release_content_sha256=numeric_rule_resolver_release_hash(
                release_id, version, persistent_locator, normalized
            ),
            test_only=True,
        )

    def _verify_internal_release_hash(self) -> None:
        actual = numeric_rule_resolver_release_hash(
            self.release_id, self.version, self.persistent_locator, self.rules
        )
        if not _is_sha256(self.release_content_sha256) or actual != self.release_content_sha256:
            raise SharedInterfaceGuardError("numeric rule resolver release content hash mismatch")

    def validate_binding(
        self,
        repo_root: str | Path = REPO_ROOT,
        *,
        allow_test_resolver: bool = False,
    ) -> None:
        self._verify_internal_release_hash()
        if not self.persistent_locator:
            raise SharedInterfaceGuardError("numeric rule resolver persistent locator required")
        if self.test_only:
            if not allow_test_resolver:
                raise SharedInterfaceGuardError("TEST_ONLY numeric-rule resolver prohibited in official path")
            return

        authority = _read_bound_json(NUMERIC_RULE_AUTHORITY_PATH, repo_root)
        if authority.get("authority_release_id") != NUMERIC_RULE_AUTHORITY_RELEASE_ID:
            raise SharedInterfaceGuardError("numeric-rule authority release identity mismatch")
        entries = authority.get("approved_numeric_rule_resolver_releases")
        if not isinstance(entries, list):
            raise SharedInterfaceGuardError("numeric-rule authority approved-release list missing")
        match = next(
            (
                entry
                for entry in entries
                if isinstance(entry, Mapping)
                and entry.get("release_id") == self.release_id
                and entry.get("version") == self.version
            ),
            None,
        )
        if not match:
            raise SharedInterfaceGuardError("numeric rule resolver release is not persistently approved")
        required = ("content_sha256", "persistent_locator", "authority_identity")
        missing = [field for field in required if not match.get(field)]
        if missing:
            raise SharedInterfaceGuardError(
                f"approved numeric rule resolver binding incomplete: {missing}"
            )
        if match["content_sha256"] != self.release_content_sha256:
            raise SharedInterfaceGuardError("approved numeric rule resolver release hash mismatch")
        if match["persistent_locator"] != self.persistent_locator:
            raise SharedInterfaceGuardError("approved numeric rule resolver locator mismatch")
        if match["authority_identity"] != NUMERIC_RULE_AUTHORITY_RELEASE_ID:
            raise SharedInterfaceGuardError("approved numeric rule resolver authority identity mismatch")

    def resolve_rule(self, rule_id: str) -> Mapping[str, Any]:
        rule = self.rules.get(str(rule_id))
        if not isinstance(rule, Mapping):
            raise SharedInterfaceGuardError(f"numeric freshness rule unresolved: {rule_id}")
        if rule.get("refresh_rule_id") != rule_id:
            raise SharedInterfaceGuardError(f"numeric freshness rule identity mismatch: {rule_id}")
        expected_hash = str(rule.get("governance_object_sha256") or "")
        if not expected_hash or expected_hash != typed_governance_object_hash(rule):
            raise SharedInterfaceGuardError(
                f"numeric freshness governance object hash mismatch: {rule_id}"
            )
        return rule


@dataclass(frozen=True)
class RecordLevelBindingPolicy:
    release_id: str
    content_sha256: str
    classifications: Mapping[str, str]

    @classmethod
    def load(cls, repo_root: str | Path = REPO_ROOT) -> "RecordLevelBindingPolicy":
        obj = _read_bound_json(RECORD_LEVEL_POLICY_PATH, repo_root)
        if obj.get("policy_release_id") != RECORD_LEVEL_POLICY_RELEASE_ID:
            raise SharedInterfaceGuardError("record-level policy release identity mismatch")
        if obj.get("model_version") != MODEL_VERSION:
            raise SharedInterfaceGuardError("record-level policy model version mismatch")
        if obj.get("feature_input_registry_release_id") != FEATURE_INPUT_REGISTRY_RELEASE_ID:
            raise SharedInterfaceGuardError("record-level policy feature registry binding mismatch")
        classifications = obj.get("classifications")
        if not isinstance(classifications, Mapping):
            raise SharedInterfaceGuardError("record-level policy classifications missing")
        registry = FeatureInputRegistry.load(repo_root)
        required_paths = {p[:-1] if p.endswith("?") else p for p in registry.record_level_paths}
        missing = sorted(required_paths - set(classifications))
        if missing:
            raise SharedInterfaceGuardError(
                f"record-level policy missing Feature Input Registry paths: {missing}"
            )
        return cls(
            release_id=RECORD_LEVEL_POLICY_RELEASE_ID,
            content_sha256=RECORD_LEVEL_POLICY_SHA256,
            classifications={str(k): str(v) for k, v in classifications.items()},
        )


def _read_record_path(record: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    obj: Any = record
    for token in path.split("."):
        if not isinstance(obj, Mapping) or token not in obj:
            return False, None
        obj = obj[token]
    return True, obj


def _validate_policy_binding(
    path: str,
    binding: Mapping[str, Any] | None,
    classification: str,
    policy: RecordLevelBindingPolicy,
    *,
    expected_type: str,
) -> None:
    if not isinstance(binding, Mapping):
        raise SharedInterfaceGuardError(f"record-level {path}: explicit binding required")
    if binding.get("binding_type") != expected_type:
        raise SharedInterfaceGuardError(
            f"record-level {path}: binding_type must be {expected_type}"
        )
    if binding.get("policy_release_id") != policy.release_id:
        raise SharedInterfaceGuardError(f"record-level {path}: policy release identity mismatch")
    if binding.get("policy_sha256") != policy.content_sha256:
        raise SharedInterfaceGuardError(f"record-level {path}: policy SHA256 mismatch")
    if binding.get("classification") != classification:
        raise SharedInterfaceGuardError(f"record-level {path}: classification mismatch")


def _validate_historical_record_binding(
    path: str,
    value: Any,
    binding: Mapping[str, Any] | None,
    classification: str,
    policy: RecordLevelBindingPolicy,
    resolver: EvidenceResolverRelease,
    cutoff_at: str,
) -> None:
    if not isinstance(binding, Mapping):
        raise SharedInterfaceGuardError(f"record-level {path}: governed historical binding required")
    if binding.get("binding_type") not in ("GOVERNED_EVIDENCE", "GOVERNED_RELEASE_EVIDENCE"):
        raise SharedInterfaceGuardError(f"record-level {path}: governed binding_type required")
    if binding.get("policy_release_id") != policy.release_id or binding.get(
        "policy_sha256"
    ) != policy.content_sha256:
        raise SharedInterfaceGuardError(f"record-level {path}: governing policy identity mismatch")
    if binding.get("classification") != classification:
        raise SharedInterfaceGuardError(f"record-level {path}: classification mismatch")
    if "value" not in binding or binding.get("value") != value:
        raise SharedInterfaceGuardError(f"record-level {path}: bound value mismatch")
    effective_at = binding.get("effective_at")
    if not effective_at:
        raise SharedInterfaceGuardError(f"record-level {path}: effective_at required")
    if parse_datetime(str(effective_at)) > parse_datetime(str(cutoff_at)):
        raise SharedInterfaceGuardError(f"record-level {path}: effective_at exceeds snapshot cutoff")
    ref = binding.get("immutable_evidence_ref") or binding.get("governed_release_ref")
    if not ref:
        raise SharedInterfaceGuardError(f"record-level {path}: immutable evidence/release reference required")
    resolver.resolve(str(ref), cutoff_at=cutoff_at)


def validate_record_level_consumed_scope_v1_2(
    record: Mapping[str, Any],
    *,
    record_level_bindings: Mapping[str, Mapping[str, Any]],
    evidence_resolver: EvidenceResolverRelease,
    repo_root: str | Path = REPO_ROOT,
    allow_test_resolver: bool = False,
) -> tuple[str, ...]:
    policy = RecordLevelBindingPolicy.load(repo_root)
    registry = FeatureInputRegistry.load(repo_root)
    evidence_resolver.validate_binding(repo_root, allow_test_resolver=allow_test_resolver)
    cutoff = str(record["snapshot_cutoff_at"])
    processed: list[str] = []
    gate_state = str((record.get("hard_risk_gate") or {}).get("state") or "NONE")

    for pattern in registry.record_level_paths:
        optional = pattern.endswith("?")
        path = pattern[:-1] if optional else pattern
        present, value = _read_record_path(record, path)
        if not present:
            if optional:
                continue
            raise SharedInterfaceGuardError(f"record-level consumed path missing: {path}")
        classification = policy.classifications.get(path)
        if not classification:
            raise SharedInterfaceGuardError(f"record-level path lacks explicit classification: {path}")
        binding = record_level_bindings.get(path)

        if classification == "CONTROL_IDENTITY_EXEMPT_WITH_EXPLICIT_POLICY_BINDING":
            _validate_policy_binding(
                path,
                binding,
                classification,
                policy,
                expected_type="EXPLICIT_CONTROL_IDENTITY_EXEMPTION",
            )
        elif classification == "HISTORICAL_GOVERNED_BINDING_REQUIRED":
            _validate_historical_record_binding(
                path, value, binding, classification, policy, evidence_resolver, cutoff
            )
        elif classification == "CONDITIONAL_HISTORICAL_BINDING_REQUIRED_WHEN_NON_NONE":
            if gate_state != "NONE":
                _validate_historical_record_binding(
                    path, value, binding, classification, policy, evidence_resolver, cutoff
                )
            else:
                _validate_policy_binding(
                    path,
                    binding,
                    classification,
                    policy,
                    expected_type="EXPLICIT_CONDITIONAL_EXEMPTION",
                )
        else:
            raise SharedInterfaceGuardError(
                f"record-level path has unsupported classification {classification!r}: {path}"
            )
        processed.append(path)

    return tuple(processed)


def validate_consumed_value_provenance_v1_2(
    record: Mapping[str, Any],
    *,
    evidence_resolver: EvidenceResolverRelease,
    record_level_bindings: Mapping[str, Mapping[str, Any]],
    certification_resolver: Mapping[str, str] | None = None,
    repo_root: str | Path = REPO_ROOT,
    allow_test_resolver: bool = False,
) -> dict[str, Any]:
    if not isinstance(evidence_resolver, EvidenceResolverRelease):
        raise SharedInterfaceGuardError(
            "governed EvidenceResolverRelease required; caller-supplied mapping is not authority"
        )
    evidence_resolver.validate_binding(repo_root, allow_test_resolver=allow_test_resolver)
    cutoff = str(record["snapshot_cutoff_at"])
    record_paths = validate_record_level_consumed_scope_v1_2(
        record,
        record_level_bindings=record_level_bindings,
        evidence_resolver=evidence_resolver,
        repo_root=repo_root,
        allow_test_resolver=allow_test_resolver,
    )
    feature_scopes = validate_consumed_value_provenance_v1_1(
        record,
        evidence_resolver=EvidenceResolverView(evidence_resolver, cutoff),
        certification_resolver=certification_resolver,
        repo_root=repo_root,
    )
    return {
        "record_level_paths": record_paths,
        "feature_scopes": feature_scopes,
        "evidence_resolver_release_id": evidence_resolver.release_id,
        "evidence_resolver_release_sha256": evidence_resolver.release_content_sha256,
    }


def validate_f08_freshness_provenance_v1_2(
    record: Mapping[str, Any],
    *,
    evidence_resolver: EvidenceResolverRelease,
    numeric_rule_resolver: NumericRuleResolverRelease | None = None,
    repo_root: str | Path = REPO_ROOT,
    allow_test_resolver: bool = False,
) -> None:
    evidence_resolver.validate_binding(repo_root, allow_test_resolver=allow_test_resolver)
    cutoff = str(record["snapshot_cutoff_at"])
    f08 = (record.get("feature_raw_inputs") or {}).get("F08_EVIDENCE_RELIABILITY") or {}
    for target, evidence in (f08.get("feature_evidence") or {}).items():
        try:
            penalty = float(evidence.get("freshness_penalty", 0) or 0)
        except Exception as exc:
            raise SharedInterfaceGuardError(f"F08 {target}: invalid freshness_penalty") from exc
        if penalty <= 0:
            continue

        if numeric_rule_resolver is None:
            raise SharedInterfaceGuardError(
                f"F08 {target}: positive freshness penalty requires approved numeric-rule resolver"
            )
        if not isinstance(numeric_rule_resolver, NumericRuleResolverRelease):
            raise SharedInterfaceGuardError(
                f"F08 {target}: caller-created numeric-rule mapping is not authority"
            )
        numeric_rule_resolver.validate_binding(
            repo_root, allow_test_resolver=allow_test_resolver
        )

        rule_id = str(evidence.get("refresh_rule_id") or "")
        if not rule_id:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh_rule_id required")
        rule = numeric_rule_resolver.resolve_rule(rule_id)
        if rule.get("registry_release_id") != REFRESH_REGISTRY_RELEASE_ID:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh registry release mismatch")
        if rule.get("registry_sha256") != REFRESH_REGISTRY_SHA256:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh registry SHA256 mismatch")
        if rule.get("rule_status") != "ACTIVE":
            raise SharedInterfaceGuardError(f"F08 {target}: numeric freshness rule inactive")
        if rule.get("effective_model_version") != MODEL_VERSION:
            raise SharedInterfaceGuardError(f"F08 {target}: numeric freshness rule model mismatch")
        scope = rule.get("applicable_scope")
        if scope != "*" and target not in (scope if isinstance(scope, list) else [scope]):
            raise SharedInterfaceGuardError(f"F08 {target}: numeric freshness rule scope mismatch")
        allowed_class = rule.get("applicable_source_or_evidence_class")
        actual_class = evidence.get("source_or_evidence_class")
        if allowed_class not in (None, "*") and actual_class != allowed_class:
            raise SharedInterfaceGuardError(f"F08 {target}: source/evidence class mismatch")
        if not rule.get("freshness_determination_method") or not rule.get("stale_state_method"):
            raise SharedInterfaceGuardError(f"F08 {target}: numeric freshness rule incomplete")
        if rule.get("penalty_value") is None or float(rule["penalty_value"]) != penalty:
            raise SharedInterfaceGuardError(
                f"F08 {target}: positive penalty not equal to approved numeric rule"
            )

        support_ref = evidence.get("supported_cutoff_ref") or evidence.get(
            "immutable_evidence_ref"
        )
        if not support_ref:
            raise SharedInterfaceGuardError(
                f"F08 {target}: historical freshness support reference required"
            )
        evidence_resolver.resolve(str(support_ref), cutoff_at=cutoff)

        as_of = (
            evidence.get("supported_cutoff_at")
            or evidence.get("evaluated_for_snapshot_cutoff_at")
            or evidence.get("as_of_at")
        )
        if not as_of:
            raise SharedInterfaceGuardError(
                f"F08 {target}: historical freshness support time required"
            )
        if parse_datetime(str(as_of)) > parse_datetime(cutoff):
            raise SharedInterfaceGuardError(
                f"F08 {target}: historical freshness support time exceeds snapshot cutoff"
            )
        # evaluation_run_at/computed_at are execution timestamps and intentionally may be later.


def official_positive_f08_numeric_rules_available(
    repo_root: str | Path = REPO_ROOT,
) -> bool:
    authority = _read_bound_json(NUMERIC_RULE_AUTHORITY_PATH, repo_root)
    entries = authority.get("approved_numeric_rule_resolver_releases")
    return isinstance(entries, list) and len(entries) > 0


__all__ = [
    "BOUND_CONTROL_FIX_ASSETS",
    "EVIDENCE_AUTHORITY_PATH",
    "EVIDENCE_AUTHORITY_RELEASE_ID",
    "EVIDENCE_AUTHORITY_SHA256",
    "F02_COMPATIBILITY_NOTE_PATH",
    "GUARD_IMPLEMENTATION_VERSION",
    "NUMERIC_RULE_AUTHORITY_PATH",
    "NUMERIC_RULE_AUTHORITY_RELEASE_ID",
    "NUMERIC_RULE_AUTHORITY_SHA256",
    "RECORD_LEVEL_POLICY_PATH",
    "RECORD_LEVEL_POLICY_RELEASE_ID",
    "RECORD_LEVEL_POLICY_SHA256",
    "EvidenceResolverRelease",
    "NumericRuleResolverRelease",
    "RecordLevelBindingPolicy",
    "evidence_resolver_release_hash",
    "numeric_rule_resolver_release_hash",
    "official_positive_f08_numeric_rules_available",
    "validate_consumed_value_provenance_v1_2",
    "validate_f08_freshness_provenance_v1_2",
    "validate_record_level_consumed_scope_v1_2",
    "verify_control_fix_asset_bindings",
    "verify_shared_asset_bindings",
]
