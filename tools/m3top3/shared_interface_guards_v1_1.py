from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .contracts_v1 import FEATURE_SCHEMA_VERSION, MODEL_VERSION
from .core import canonical_json_bytes, parse_datetime, sha256_hex
from .features_v1 import FEATURE_IDS
from .shared_interface_guards_v1 import SharedInterfaceGuardError

GUARD_IMPLEMENTATION_VERSION = "M3TOP3-SHARED-INTERFACE-GUARDS-v1.1-WIRING_WORKING"

REPO_ROOT = Path(__file__).resolve().parents[2]

FEATURE_INPUT_REGISTRY_PATH = "control/shared/M3TOP3-FEATURE-INPUT-REGISTRY_v1.0_WORKING.yaml"
PIT_CONTRACT_PATH = "control/shared/M3TOP3-PIT-CONSUMED-PROVENANCE-CONTRACT_v1.0_WORKING.yaml"
REFRESH_REGISTRY_PATH = "control/shared/M3TOP3-REFRESH-RULE-REGISTRY_v1.0_WORKING.yaml"
COVERAGE_POLICY_PATH = "control/shared/M3TOP3-COVERAGE-RELEASE-POLICY_v1.0_WORKING.yaml"
RECONCILED_DECISION_PATH = "control/shared/M3TOP3-v1-SHARED-PREFLIGHT-INTERFACE-RECONCILED-DECISION_v1.0_WORKING.yaml"
F02_COMPATIBILITY_NOTE_PATH = "control/core_b/M3TOP3-v1-IMPLEMENTATION-COMPATIBILITY-NOTE_v1.0.1_WORKING.yaml"


@dataclass(frozen=True)
class BoundAsset:
    path: str
    sha256: str
    byte_size: int
    git_blob_sha: str


BOUND_SHARED_ASSETS = (
    BoundAsset(RECONCILED_DECISION_PATH, "7d8d000c467b8b3cd4e3f16c1eef060a8d70fceabab2f66161fde08d54e9f1a4", 6420, "eb50f06d49c3c52b86d8c16290f350635de2537b"),
    BoundAsset(FEATURE_INPUT_REGISTRY_PATH, "63edde7d91aafa4691b7a31ee7304b9972e064347a55b9d891b19634b199df37", 4843, "5faa4d5739bf9ecb0c11d16f6d7d697ff3983977"),
    BoundAsset(PIT_CONTRACT_PATH, "22e80dbf80e1bfb9ae25ab8f56a7fd56463fc8c8bd92a67489a6a9601455354f", 3302, "b7a00087f9b9985d6d5523bf6524361e5ae620fe"),
    BoundAsset(REFRESH_REGISTRY_PATH, "e44b67e4f3854cfcd2c9f5fd7924192bc0c5491bfcdd496acbae8b4dd318cd64", 3715, "bced062f75b44915f61d8d54dafe8bab9713029d"),
    BoundAsset(COVERAGE_POLICY_PATH, "076bd1b7acee061f9c0d57e4dda802b6beb533fcd4b323eafa39760ad98b1f97", 3178, "0532eb3b921438538fa4cca908832cf5a770ca84"),
    BoundAsset(F02_COMPATIBILITY_NOTE_PATH, "dfd98712a4982eef5a4b07fec5d376f0eefed0c1861e14d3a20ddb22c87fb656", 1141, "685d5aa1ea2ac5c63a3c70898a9576955b1d22fc"),
)
BOUND_ASSET_BY_PATH = {a.path: a for a in BOUND_SHARED_ASSETS}

FEATURE_INPUT_REGISTRY_SHA256 = BOUND_ASSET_BY_PATH[FEATURE_INPUT_REGISTRY_PATH].sha256
REFRESH_REGISTRY_SHA256 = BOUND_ASSET_BY_PATH[REFRESH_REGISTRY_PATH].sha256
FEATURE_INPUT_REGISTRY_RELEASE_ID = "M3TOP3-FEATURE-INPUT-REGISTRY_v1.0_WORKING"
REFRESH_REGISTRY_RELEASE_ID = "M3TOP3-REFRESH-RULE-REGISTRY_v1.0_WORKING"
PIT_SCOPE_CONTRACT_ID = FEATURE_INPUT_REGISTRY_RELEASE_ID

_MISSING_STATES = {"MISSING", "UNKNOWN", "REVIEW_REQUIRED", "NOT_FOUND"}
_F08_GOVERNANCE_SUFFIXES = (
    ".freshness_penalty",
    ".refresh_rule_id",
    ".refresh_code",
    ".evaluated_freshness_state",
    ".supported_cutoff_ref",
    ".supported_cutoff_at",
    ".evaluated_for_snapshot_cutoff_at",
    ".as_of_at",
    ".evaluation_run_at",
)
_MODEL_GOVERNANCE_SUFFIXES = (
    ".change_mode",
    ".operator_id",
    ".derivation_id",
    ".derivation_version",
)


def _git_blob_sha(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(prefix + data).hexdigest()


def verify_shared_asset_bindings(repo_root: str | Path = REPO_ROOT) -> dict[str, dict[str, Any]]:
    root = Path(repo_root)
    result: dict[str, dict[str, Any]] = {}
    for asset in BOUND_SHARED_ASSETS:
        p = root / asset.path
        if not p.is_file():
            raise SharedInterfaceGuardError(f"bound shared asset missing: {asset.path}")
        data = p.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        blob = _git_blob_sha(data)
        size = len(data)
        if sha != asset.sha256:
            raise SharedInterfaceGuardError(f"shared asset SHA256 mismatch: {asset.path}")
        if size != asset.byte_size:
            raise SharedInterfaceGuardError(f"shared asset byte-size mismatch: {asset.path}")
        if blob != asset.git_blob_sha:
            raise SharedInterfaceGuardError(f"shared asset Git-blob mismatch: {asset.path}")
        result[asset.path] = {"sha256": sha, "byte_size": size, "git_blob_sha": blob, "status": "PASS"}
    return result


def _read_verified_text(path: str, repo_root: str | Path = REPO_ROOT) -> str:
    asset = BOUND_ASSET_BY_PATH[path]
    p = Path(repo_root) / path
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != asset.sha256 or len(data) != asset.byte_size or _git_blob_sha(data) != asset.git_blob_sha:
        raise SharedInterfaceGuardError(f"bound asset identity mismatch: {path}")
    return data.decode("utf-8")


def _parse_top_level_list(text: str, key: str) -> tuple[str, ...]:
    lines = text.splitlines()
    out: list[str] = []
    active = False
    for line in lines:
        if line == f"{key}:":
            active = True
            continue
        if not active:
            continue
        if line.startswith("- "):
            out.append(line[2:].strip())
            continue
        if line and not line.startswith(" "):
            break
    return tuple(out)


def _parse_feature_consumed_paths(text: str) -> dict[str, tuple[str, ...]]:
    lines = text.splitlines()
    out: dict[str, list[str]] = {}
    in_features = False
    current: str | None = None
    in_paths = False
    for line in lines:
        if line == "features:":
            in_features = True
            continue
        if not in_features:
            continue
        if line and not line.startswith(" "):
            break
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current = line.strip()[:-1]
            if current in FEATURE_IDS:
                out.setdefault(current, [])
            else:
                current = None
            in_paths = False
            continue
        if current is None:
            continue
        if line.strip() == "consumed_paths:":
            in_paths = True
            continue
        if in_paths and line.startswith("    - "):
            out[current].append(line.strip()[2:].strip())
            continue
        if in_paths and line.startswith("    ") and not line.startswith("    - "):
            in_paths = False
    missing = [fid for fid in FEATURE_IDS if fid not in out]
    if missing:
        raise SharedInterfaceGuardError(f"feature registry missing feature definitions: {missing}")
    return {k: tuple(v) for k, v in out.items()}


@dataclass(frozen=True)
class FeatureInputRegistry:
    release_id: str
    content_sha256: str
    feature_paths: Mapping[str, tuple[str, ...]]
    cross_cutting_paths: tuple[str, ...]
    record_level_paths: tuple[str, ...]

    @classmethod
    def load(cls, repo_root: str | Path = REPO_ROOT) -> "FeatureInputRegistry":
        text = _read_verified_text(FEATURE_INPUT_REGISTRY_PATH, repo_root)
        if "bound_model_version: M3TOP3-v1.0" not in text:
            raise SharedInterfaceGuardError("feature registry model binding mismatch")
        if f"bound_feature_schema_version: {FEATURE_SCHEMA_VERSION}" not in text:
            raise SharedInterfaceGuardError("feature registry feature-schema binding mismatch")
        return cls(
            release_id=FEATURE_INPUT_REGISTRY_RELEASE_ID,
            content_sha256=FEATURE_INPUT_REGISTRY_SHA256,
            feature_paths=_parse_feature_consumed_paths(text),
            cross_cutting_paths=_parse_top_level_list(text, "cross_cutting_feature_paths"),
            record_level_paths=_parse_top_level_list(text, "record_level_consumed_paths"),
        )

    def resolve_feature_paths(self, feature_id: str, block: Mapping[str, Any]) -> tuple[str, ...]:
        if feature_id not in self.feature_paths:
            raise SharedInterfaceGuardError(f"unknown feature_id for authoritative scope: {feature_id}")
        patterns = tuple(self.cross_cutting_paths) + tuple(self.feature_paths[feature_id])
        concrete: list[str] = []
        for pattern in patterns:
            concrete.extend(_expand_path_pattern(block, pattern))
        return tuple(sorted(dict.fromkeys(concrete)))


def _expand_path_pattern(root: Any, pattern: str) -> list[str]:
    optional = pattern.endswith("?")
    if optional:
        pattern = pattern[:-1]
    tokens = pattern.split(".") if pattern else []
    out: list[str] = []

    def walk(obj: Any, idx: int, prefix: str) -> None:
        if idx >= len(tokens):
            out.append(prefix)
            return
        token = tokens[idx]
        if token == "*":
            if not isinstance(obj, Mapping):
                return
            for key in sorted(obj, key=lambda v: str(v)):
                p = f"{prefix}.{key}" if prefix else str(key)
                walk(obj[key], idx + 1, p)
            return
        if token.endswith("[]"):
            key = token[:-2]
            if not isinstance(obj, Mapping) or key not in obj or not isinstance(obj[key], list):
                return
            for pos, item in enumerate(obj[key]):
                p = f"{prefix}.{key}[{pos}]" if prefix else f"{key}[{pos}]"
                walk(item, idx + 1, p)
            return
        if not isinstance(obj, Mapping) or token not in obj:
            return
        p = f"{prefix}.{token}" if prefix else token
        walk(obj[token], idx + 1, p)

    walk(root, 0, "")
    return out


def _get_concrete_path(root: Any, path: str) -> Any:
    obj = root
    for token in path.split("."):
        if "[" in token and token.endswith("]"):
            key, pos = token[:-1].split("[", 1)
            if key:
                obj = obj[key]
            obj = obj[int(pos)]
        else:
            obj = obj[token]
    return obj


def _requires_historical_evidence(feature_id: str, path: str) -> bool:
    if any(path.endswith(suffix) for suffix in _MODEL_GOVERNANCE_SUFFIXES):
        return False
    if feature_id == "F08_EVIDENCE_RELIABILITY" and any(path.endswith(suffix) for suffix in _F08_GOVERNANCE_SUFFIXES):
        return False
    return True


def _resolve_immutable_ref(provenance: Mapping[str, Any], resolver: Mapping[str, Any], *, context: str) -> str:
    ref = (
        provenance.get("immutable_evidence_ref")
        or provenance.get("immutable_support_ref")
        or provenance.get("supported_cutoff_ref")
    )
    if not ref:
        raise SharedInterfaceGuardError(f"{context}: immutable evidence/support reference required")
    ref = str(ref)
    if ref not in resolver:
        raise SharedInterfaceGuardError(f"{context}: immutable evidence/support reference unresolved: {ref}")
    return ref


def _assert_historical_provenance(
    provenance: Mapping[str, Any],
    cutoff_at: str,
    evidence_resolver: Mapping[str, Any],
    *,
    context: str,
) -> None:
    if not isinstance(provenance, Mapping):
        raise SharedInterfaceGuardError(f"{context}: provenance object required")
    _resolve_immutable_ref(provenance, evidence_resolver, context=context)
    timestamp = provenance.get("publication_at") or provenance.get("supported_cutoff_at")
    if not timestamp:
        raise SharedInterfaceGuardError(f"{context}: publication_at or supported_cutoff_at required")
    if parse_datetime(timestamp) > parse_datetime(cutoff_at):
        raise SharedInterfaceGuardError(f"{context}: provenance timestamp exceeds snapshot cutoff")


def _feature_business_payload(block: Mapping[str, Any]) -> dict[str, Any]:
    excluded = {"consumed_fields", "consumed_value_provenance", "whole_block_certification"}
    return {k: v for k, v in block.items() if k not in excluded}


def whole_block_payload_hash(block: Mapping[str, Any]) -> str:
    return sha256_hex(_feature_business_payload(block))


def certification_content_hash(certification: Mapping[str, Any]) -> str:
    payload = {k: v for k, v in certification.items() if k != "certification_content_hash"}
    return sha256_hex(payload)


def _validate_block_certification(
    feature_id: str,
    block: Mapping[str, Any],
    authoritative_paths: tuple[str, ...],
    cutoff_at: str,
    certification_resolver: Mapping[str, str],
    evidence_resolver: Mapping[str, Any],
    registry: FeatureInputRegistry,
) -> None:
    cert = block.get("whole_block_certification")
    if not isinstance(cert, Mapping):
        raise SharedInterfaceGuardError(f"{feature_id}: whole_block_certification object required")
    required = (
        "certification_id", "certification_version", "certification_content_hash", "feature_id",
        "applicable_model_version", "applicable_feature_schema_version", "feature_block_hash",
        "authoritative_scope_contract_id", "authoritative_scope_contract_hash", "certified_scope",
        "supported_cutoff_at", "immutable_evidence_refs", "persistent_locator",
    )
    missing = [k for k in required if not cert.get(k)]
    if missing:
        raise SharedInterfaceGuardError(f"{feature_id}: block certification missing fields: {missing}")
    if cert["feature_id"] != feature_id:
        raise SharedInterfaceGuardError(f"{feature_id}: certification feature_id mismatch")
    if cert["applicable_model_version"] != MODEL_VERSION or cert["applicable_feature_schema_version"] != FEATURE_SCHEMA_VERSION:
        raise SharedInterfaceGuardError(f"{feature_id}: certification model/schema applicability mismatch")
    if cert["feature_block_hash"] != whole_block_payload_hash(block):
        raise SharedInterfaceGuardError(f"{feature_id}: certification feature_block_hash mismatch")
    if cert["authoritative_scope_contract_id"] != registry.release_id or cert["authoritative_scope_contract_hash"] != registry.content_sha256:
        raise SharedInterfaceGuardError(f"{feature_id}: certification scope-contract identity mismatch")
    certified_scope = set(str(v) for v in cert["certified_scope"])
    if not set(authoritative_paths).issubset(certified_scope):
        raise SharedInterfaceGuardError(f"{feature_id}: certification scope does not cover authoritative consumed paths")
    if parse_datetime(cert["supported_cutoff_at"]) > parse_datetime(cutoff_at):
        raise SharedInterfaceGuardError(f"{feature_id}: certification supported_cutoff_at exceeds snapshot cutoff")
    cert_id = str(cert["certification_id"])
    expected_hash = certification_resolver.get(cert_id)
    actual_hash = certification_content_hash(cert)
    if not expected_hash or expected_hash != actual_hash or cert["certification_content_hash"] != actual_hash:
        raise SharedInterfaceGuardError(f"{feature_id}: immutable certification identity/hash unresolved or mismatched")
    refs = cert.get("immutable_evidence_refs")
    if not isinstance(refs, list) or not refs:
        raise SharedInterfaceGuardError(f"{feature_id}: certification immutable evidence/source lineage required")
    for ref in refs:
        if str(ref) not in evidence_resolver:
            raise SharedInterfaceGuardError(f"{feature_id}: certification evidence reference unresolved: {ref}")


def _validate_f02_aggregate_governance(
    block: Mapping[str, Any],
    cutoff_at: str,
    provenance_map: Mapping[str, Any],
    evidence_resolver: Mapping[str, Any],
    *,
    block_certified: bool,
) -> None:
    for metric, spec in (block.get("metric_changes") or {}).items():
        if not isinstance(spec, Mapping) or spec.get("value") is None:
            continue
        for field in ("operator_id", "derivation_id", "derivation_version"):
            if not spec.get(field):
                raise SharedInterfaceGuardError(f"F02 metric_changes[{metric!r}] missing governed {field}")
        if block_certified:
            continue
        path = f"metric_changes.{metric}.value"
        prov = provenance_map.get(path)
        if not isinstance(prov, Mapping):
            raise SharedInterfaceGuardError(f"F02 {path}: aggregate provenance required")
        if str(prov.get("operator_id") or "") != str(spec.get("operator_id")):
            raise SharedInterfaceGuardError(f"F02 {path}: operator_id provenance mismatch")
        if str(prov.get("derivation_id") or "") != str(spec.get("derivation_id")):
            raise SharedInterfaceGuardError(f"F02 {path}: derivation_id provenance mismatch")
        if str(prov.get("derivation_version") or "") != str(spec.get("derivation_version")):
            raise SharedInterfaceGuardError(f"F02 {path}: derivation_version provenance mismatch")
        upstream_refs = prov.get("upstream_evidence_refs")
        upstream_cutoff = prov.get("upstream_supported_cutoff_at")
        upstream_lineage = prov.get("upstream_lineage_ref")
        if not isinstance(upstream_refs, list) or not upstream_refs or not upstream_cutoff or not upstream_lineage:
            raise SharedInterfaceGuardError(f"F02 {path}: PIT-certified upstream lineage incomplete")
        for ref in upstream_refs:
            if str(ref) not in evidence_resolver:
                raise SharedInterfaceGuardError(f"F02 {path}: upstream evidence reference unresolved: {ref}")
        if parse_datetime(upstream_cutoff) > parse_datetime(cutoff_at):
            raise SharedInterfaceGuardError(f"F02 {path}: upstream supported cutoff exceeds snapshot cutoff")


def validate_consumed_value_provenance_v1_1(
    record: Mapping[str, Any],
    *,
    evidence_resolver: Mapping[str, Any],
    certification_resolver: Mapping[str, str] | None = None,
    repo_root: str | Path = REPO_ROOT,
) -> dict[str, tuple[str, ...]]:
    registry = FeatureInputRegistry.load(repo_root)
    cutoff = str(record["snapshot_cutoff_at"])
    cert_resolver = certification_resolver or {}
    resolved: dict[str, tuple[str, ...]] = {}

    for feature_id, block in (record.get("feature_raw_inputs") or {}).items():
        if feature_id not in FEATURE_IDS or not isinstance(block, Mapping):
            continue
        authoritative_paths = registry.resolve_feature_paths(feature_id, block)
        resolved[feature_id] = authoritative_paths
        cert = block.get("whole_block_certification")
        provenance_map = block.get("consumed_value_provenance") or {}
        if cert is not None:
            _validate_block_certification(
                feature_id, block, authoritative_paths, cutoff, cert_resolver, evidence_resolver, registry
            )
            block_certified = True
        else:
            block_certified = False
            if not isinstance(provenance_map, Mapping):
                raise SharedInterfaceGuardError(f"{feature_id}: consumed_value_provenance mapping required")
            for path in authoritative_paths:
                if not _requires_historical_evidence(feature_id, path):
                    continue
                if path not in provenance_map:
                    raise SharedInterfaceGuardError(f"{feature_id}.{path}: missing authoritative consumed-value provenance")
                _assert_historical_provenance(
                    provenance_map[path], cutoff, evidence_resolver, context=f"{feature_id}.{path}"
                )
        if feature_id == "F02_NUMERIC_BUSINESS_INFLECTION":
            _validate_f02_aggregate_governance(
                block, cutoff, provenance_map, evidence_resolver, block_certified=block_certified
            )

    gate = record.get("hard_risk_gate") or {}
    if gate.get("state") and gate.get("state") != "NONE":
        for field in ("event_group_id", "evidence_status", "reason"):
            if not gate.get(field):
                raise SharedInterfaceGuardError(f"hard_risk_gate: {field} required for non-NONE state")
        _assert_historical_provenance(
            gate.get("pit_provenance") or {}, cutoff, evidence_resolver, context="hard_risk_gate"
        )
    return resolved


def typed_governance_object_hash(rule: Mapping[str, Any]) -> str:
    payload = {k: v for k, v in rule.items() if k != "governance_object_sha256"}
    return sha256_hex(payload)


def validate_f08_freshness_provenance_v1_1(
    record: Mapping[str, Any],
    *,
    typed_refresh_rules: Mapping[str, Mapping[str, Any]] | None = None,
    evidence_resolver: Mapping[str, Any] | None = None,
    repo_root: str | Path = REPO_ROOT,
) -> None:
    _read_verified_text(REFRESH_REGISTRY_PATH, repo_root)
    rules = typed_refresh_rules or {}
    evidence_refs = evidence_resolver or {}
    cutoff = str(record["snapshot_cutoff_at"])
    f08 = (record.get("feature_raw_inputs") or {}).get("F08_EVIDENCE_RELIABILITY") or {}
    for target, evidence in (f08.get("feature_evidence") or {}).items():
        try:
            penalty = float(evidence.get("freshness_penalty", 0) or 0)
        except Exception as exc:
            raise SharedInterfaceGuardError(f"F08 {target}: invalid freshness_penalty") from exc
        if penalty <= 0:
            continue
        rule_id = str(evidence.get("refresh_rule_id") or "")
        if not rule_id or rule_id not in rules:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh governance rule unresolved")
        rule = rules[rule_id]
        if rule.get("registry_release_id") != REFRESH_REGISTRY_RELEASE_ID or rule.get("registry_sha256") != REFRESH_REGISTRY_SHA256:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh registry identity/hash mismatch")
        if rule.get("refresh_rule_id") != rule_id or rule.get("rule_status") != "ACTIVE":
            raise SharedInterfaceGuardError(f"F08 {target}: refresh rule inactive or identity mismatch")
        if rule.get("effective_model_version") != MODEL_VERSION:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh rule model-version mismatch")
        scope = rule.get("applicable_scope")
        if scope != "*" and target not in (scope if isinstance(scope, list) else [scope]):
            raise SharedInterfaceGuardError(f"F08 {target}: refresh rule scope mismatch")
        evidence_class = evidence.get("source_or_evidence_class")
        allowed_class = rule.get("applicable_source_or_evidence_class")
        if allowed_class not in (None, "*") and evidence_class != allowed_class:
            raise SharedInterfaceGuardError(f"F08 {target}: refresh source/evidence-class mismatch")
        if not rule.get("freshness_determination_method") or not rule.get("stale_state_method"):
            raise SharedInterfaceGuardError(f"F08 {target}: refresh rule definition incomplete")
        if rule.get("penalty_value") is None or float(rule["penalty_value"]) != penalty:
            raise SharedInterfaceGuardError(f"F08 {target}: positive penalty not bound to governed numeric rule")
        expected_rule_hash = str(rule.get("governance_object_sha256") or "")
        if not expected_rule_hash or expected_rule_hash != typed_governance_object_hash(rule):
            raise SharedInterfaceGuardError(f"F08 {target}: typed refresh governance object hash mismatch")

        support_ref = evidence.get("supported_cutoff_ref") or evidence.get("immutable_evidence_ref")
        if not support_ref or str(support_ref) not in evidence_refs:
            raise SharedInterfaceGuardError(f"F08 {target}: historical freshness support reference unresolved")
        as_of = (
            evidence.get("supported_cutoff_at")
            or evidence.get("evaluated_for_snapshot_cutoff_at")
            or evidence.get("as_of_at")
        )
        if not as_of:
            raise SharedInterfaceGuardError(f"F08 {target}: historical freshness support time required")
        if parse_datetime(as_of) > parse_datetime(cutoff):
            raise SharedInterfaceGuardError(f"F08 {target}: historical freshness support time exceeds snapshot cutoff")
        # evaluation_run_at / computed_at are intentionally not compared with the historical cutoff.
