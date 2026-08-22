from __future__ import annotations

import json
import inspect
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from .core import aggregate_hash, canonical_json_bytes, deterministic_id, hash_file, sha256_hex


EXIT_BLOCKED = 2
EXIT_INTEGRITY = 3
EXIT_AUTHORITY = 4
OFFICIAL_EXECUTION_ENABLED = False
PRICE_CANONICAL_VALIDATION_ENABLED = False
ALLOWED_PRICE_SEMANTICS = frozenset({"RAW_IMMUTABLE", "PRICE_CANONICAL"})
ADMITTED_RELEASE_STATUSES = frozenset({"VERIFIED", "DIAGNOSTIC_VERIFIED"})
DIAGNOSTIC_LINEAGE_STATE = "DIAGNOSTIC_EXACT_BYTES"
ELEVATED_RELEASE_STATES = frozenset({"RELEASED", "FROZEN", "CANONICAL", "OFFICIAL"})
REQUIRED_LINEAGE_DOMAINS = (
    "UNIVERSE_RELEASE",
    "DENOMINATOR_ELIGIBILITY_RELEASE",
    "FEATURE_SOURCE_RELEASE",
    "PRICE_RELEASE",
    "CORPORATE_ACTION_RELEASE",
    "TRADING_CALENDAR_RELEASE",
    "WINDOW_REGISTRY_RELEASE",
    "SCORER_RELEASE",
)
MODEL_INPUT_DATASET_DOMAINS = (
    "UNIVERSE_RELEASE",
    "DENOMINATOR_ELIGIBILITY_RELEASE",
    "FEATURE_SOURCE_RELEASE",
    "PRICE_RELEASE",
    "TRADING_CALENDAR_RELEASE",
)
OUTCOME_DATASET_DOMAINS = (
    "PRICE_RELEASE",
    "CORPORATE_ACTION_RELEASE",
    "TRADING_CALENDAR_RELEASE",
    "WINDOW_REGISTRY_RELEASE",
)
RELEASE_REF_FIELDS = (
    "domain",
    "release_id",
    "release_version",
    "release_revision",
    "artifact_id",
    "artifact_sha256",
    "byte_size",
    "manifest_sha256",
    "component_set_digest",
    "semantic_role",
    "state",
    "as_of_date",
)

RELEASE_MANIFEST_IDENTITY_FIELDS = (
    "domain",
    "release_id",
    "release_version",
    "release_revision",
    "artifact_id",
    "artifact_sha256",
    "byte_size",
    "component_set_digest",
    "semantic_role",
    "state",
    "as_of_date",
)
ALLOWED_PHYSICAL_ALIAS_DOMAINS = frozenset(
    {
        "PRICE_RELEASE",
        "CORPORATE_ACTION_RELEASE",
        "TRADING_CALENDAR_RELEASE",
    }
)
ALLOWED_PHYSICAL_ALIAS_GROUP = "PRICE_CA_CALENDAR_SHARED_BYTES"


class M3Top3AdmissionError(RuntimeError):
    """A classified, fail-closed admission failure.

    ``code`` and ``exit_code`` are part of the runtime contract.  Callers must
    not downgrade a classified failure to a successful or generic exit.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        exit_code: int = EXIT_BLOCKED,
    ):
        self.code = code
        self.details = details or {}
        self.exit_code = exit_code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class VerifiedSnapshot:
    manifest: dict[str, Any]
    pit_rows: list[dict[str, Any]]
    model_inputs: list[dict[str, Any]]
    retrieval_audits: list[dict[str, Any]]


def _portable_release_ref(release: dict[str, Any]) -> dict[str, Any]:
    """Project an admitted release into path-free row/result lineage."""

    return {field: release[field] for field in RELEASE_REF_FIELDS}


def _read_exact_json_object(path: Path, code: str = "BLOCKED_INPUT_INTEGRITY") -> tuple[bytes, dict[str, Any]]:
    try:
        payload = path.read_bytes()
        value = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise M3Top3AdmissionError(code, "exact JSON artifact is unreadable or malformed", {"path": str(path), "cause": type(exc).__name__}, EXIT_INTEGRITY) from exc
    if not isinstance(value, dict):
        raise M3Top3AdmissionError(code, "exact JSON artifact must contain one object", {"path": str(path)}, EXIT_INTEGRITY)
    return payload, value


def admit_claim_locks(config: dict[str, Any]) -> None:
    if config.get("execution_mode", "DIAGNOSTIC") == "OFFICIAL":
        raise M3Top3AdmissionError("OFFICIAL_MODE_GLOBALLY_BLOCKED", "Official execution remains globally blocked", exit_code=EXIT_AUTHORITY)
    if config.get("official_golden") is True or config.get("full_replay") is True:
        raise M3Top3AdmissionError("OFFICIAL_REPLAY_GLOBALLY_BLOCKED", "Official Golden and Full Replay remain globally blocked", exit_code=EXIT_AUTHORITY)


def verify_execution_accounting(requested:int,*,admitted:int,blocked:int,failed_integrity:int,failed_authority:int,failed_internal:int=0)->None:
    values=(requested,admitted,blocked,failed_integrity,failed_authority,failed_internal)
    if any(not isinstance(value,int) or isinstance(value,bool) or value<0 for value in values) or requested!=admitted+blocked+failed_integrity+failed_authority+failed_internal:
        raise M3Top3AdmissionError("EXECUTION_ACCOUNTING_MISMATCH","requested execution units do not reconcile to terminal categories",{"requested":requested,"admitted":admitted,"blocked":blocked,"failed_integrity":failed_integrity,"failed_authority":failed_authority,"failed_internal":failed_internal},EXIT_BLOCKED)


def require_execution_units(count:int,context:str)->None:
    if not isinstance(count,int) or isinstance(count,bool) or count<=0:
        raise M3Top3AdmissionError("NO_EXECUTION_UNITS",f"{context} contains zero admitted execution units",{"count":count},EXIT_BLOCKED)


def verify_mutation_execution_receipt(
    receipt:dict[str,Any],
    required_mutations:int=50,
    *,
    expected_freeze_manifest_sha256:str,
    expected_source_tree_sha256:str,
    expected_registry_sha256:str,
    expected_mutation_ids:Iterable[str],
)->None:
    """Admit only a complete, zero-survivor mutation execution receipt.

    The mutation worker owns process execution and classification.  This
    production verifier owns the stable gate codes used by PMO/CLI adapters;
    callers cannot replace real execution with a boolean PASS flag.
    """

    if required_mutations != 50:
        raise M3Top3AdmissionError(
            "MUTATION_REGRESSION_INCOMPLETE",
            "final mutation admission requires the governed 50-mutation registry",
            {"required_mutations":required_mutations},
            EXIT_INTEGRITY,
        )

    required_fields={
        "schema_version","requested_mutations","killed_red","survivors",
        "harness_errors","source_mutated","manifest_drift","results","status",
        "readiness","full_registry_executed","iva_participation",
        "registry_sha256","freeze_binding_start","freeze_binding_end",
        "source_tree_before","source_tree_after","killed_ids",
        "survivor_ids","harness_error_ids",
    }
    if (
        not all(_is_sha256(value) for value in (
            expected_freeze_manifest_sha256,expected_source_tree_sha256,expected_registry_sha256,
        ))
        or not isinstance(receipt,dict)
        or required_fields-set(receipt)
    ):
        raise M3Top3AdmissionError(
            "MUTATION_REGRESSION_INCOMPLETE",
            "mutation execution receipt is missing governed accounting fields",
            exit_code=EXIT_INTEGRITY,
        )
    results=receipt.get("results")
    if not isinstance(results,list) or len(results)!=receipt.get("requested_mutations"):
        raise M3Top3AdmissionError(
            "MUTATION_REGRESSION_INCOMPLETE",
            "mutation result rows do not reconcile to requested mutations",
            exit_code=EXIT_INTEGRITY,
        )
    expected_ids=tuple(expected_mutation_ids)
    result_ids=[row.get("mutation_id") for row in results if isinstance(row,dict)]
    if (
        not expected_ids
        or len(expected_ids)!=len(set(expected_ids))
        or len(result_ids)!=len(results)
        or len(result_ids)!=len(set(result_ids))
        or set(result_ids)!=set(expected_ids)
    ):
        raise M3Top3AdmissionError(
            "MUTATION_REGRESSION_INCOMPLETE",
            "mutation result identities do not exactly cover the externally supplied registry selection",
            {"expected":sorted(expected_ids),"actual":sorted(str(value) for value in result_ids)},
            EXIT_INTEGRITY,
        )
    for row in results:
        baseline=row.get("baseline"); mutant=row.get("mutant")
        if not isinstance(baseline,dict) or not isinstance(mutant,dict):
            raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE","mutation row lacks baseline/mutant execution evidence",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
        for phase,run in (("baseline",baseline),("mutant",mutant)):
            required_run={"return_code","timed_out","test_summary","stdout_path","stderr_path","stdout_sha256","stderr_sha256","combined_sha256"}
            if required_run-set(run) or not all(_is_sha256(run.get(field)) for field in ("stdout_sha256","stderr_sha256","combined_sha256")):
                raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE",f"{phase} execution evidence is incomplete",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
            try:
                stdout=Path(run["stdout_path"]).read_bytes(); stderr=Path(run["stderr_path"]).read_bytes()
            except (OSError,TypeError) as exc:
                raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE",f"{phase} transcript bytes are unavailable",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY) from exc
            if sha256_hex(stdout)!=run["stdout_sha256"] or sha256_hex(stderr)!=run["stderr_sha256"] or sha256_hex(stdout+stderr)!=run["combined_sha256"]:
                raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE",f"{phase} transcript hashes differ from live bytes",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
        if baseline.get("timed_out") is not False or baseline.get("return_code")!=0 or baseline.get("test_summary")!="OK":
            raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE","baseline paired tests are not exactly green",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
        mutant_failure_summary=re.fullmatch(r"FAILED \(failures=[1-9][0-9]*\)",str(mutant.get("test_summary","")))
        if row.get("status")=="KILLED_RED" and (mutant.get("timed_out") is not False or mutant.get("return_code")==0 or mutant_failure_summary is None):
            raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE","killed mutation lacks a real assertion-failure execution",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
        if row.get("status")=="SURVIVOR" and (mutant.get("timed_out") is not False or mutant.get("return_code")!=0 or mutant.get("test_summary")!="OK"):
            raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE","survivor classification differs from live mutant execution",{"mutation_id":row.get("mutation_id")},EXIT_INTEGRITY)
    observed_survivors=sum(row.get("status")=="SURVIVOR" for row in results if isinstance(row,dict))
    killed_ids=[row["mutation_id"] for row in results if row.get("status")=="KILLED_RED"]
    survivor_ids=[row["mutation_id"] for row in results if row.get("status")=="SURVIVOR"]
    error_ids=[row["mutation_id"] for row in results if row.get("status")=="HARNESS_ERROR"]
    if (
        receipt.get("killed_ids")!=killed_ids
        or receipt.get("survivor_ids")!=survivor_ids
        or receipt.get("harness_error_ids")!=error_ids
    ):
        raise M3Top3AdmissionError("MUTATION_REGRESSION_INCOMPLETE","mutation category identity lists do not reconcile to result rows",exit_code=EXIT_INTEGRITY)
    if receipt.get("survivors")!=observed_survivors or observed_survivors:
        raise M3Top3AdmissionError(
            "MUTATION_SURVIVOR_PROHIBITED",
            "one or more executed mutations survived their paired production tests",
            {"survivors":observed_survivors},
            EXIT_INTEGRITY,
        )
    start=receipt.get("freeze_binding_start"); end=receipt.get("freeze_binding_end")
    binding_exact=(
        isinstance(start,dict)
        and isinstance(end,dict)
        and start.get("manifest_sha256")==expected_freeze_manifest_sha256
        and end.get("manifest_sha256")==expected_freeze_manifest_sha256
        and start.get("source_tree_sha256")==expected_source_tree_sha256
        and end.get("source_tree_sha256")==expected_source_tree_sha256
        and receipt.get("registry_sha256")==expected_registry_sha256
        and receipt.get("source_tree_before")==expected_source_tree_sha256
        and receipt.get("source_tree_after")==expected_source_tree_sha256
    )
    observed_killed=sum(row.get("status")=="KILLED_RED" for row in results if isinstance(row,dict))
    observed_errors=sum(row.get("status")=="HARNESS_ERROR" for row in results if isinstance(row,dict))
    if (
        receipt.get("schema_version")!="r-wp4-03-mutation-execution-v2"
        or receipt.get("status")!="PASS"
        or receipt.get("readiness")!="GO_FOR_INDEPENDENT_VALIDATION_HANDOFF"
        or receipt.get("full_registry_executed") is not True
        or receipt.get("iva_participation")!="NONE"
        or not binding_exact
        or receipt.get("requested_mutations")!=required_mutations
        or receipt.get("killed_red")!=observed_killed
        or observed_killed!=required_mutations
        or receipt.get("harness_errors")!=observed_errors
        or observed_errors
        or receipt.get("source_mutated") is not False
        or receipt.get("manifest_drift") is not False
    ):
        raise M3Top3AdmissionError(
            "MUTATION_REGRESSION_INCOMPLETE",
            "mutation registry execution is not complete, exact, and source-preserving",
            {
                "required":required_mutations,
                "requested":receipt.get("requested_mutations"),
                "killed":observed_killed,
                "errors":observed_errors,
                "binding_exact":binding_exact,
                "full_registry_executed":receipt.get("full_registry_executed"),
                "status":receipt.get("status"),
            },
            EXIT_INTEGRITY,
        )


def admit_execution_lineage_bundle(path: str | Path | None, expected_sha256: str | None) -> dict[str, Any]:
    """Admit all eight release domains before any scorer import or data read.

    The bundle hash is supplied externally.  Every release manifest and every
    component is independently rehashed.  Operational paths are retained only
    for subsequent live rechecks and are excluded from semantic identities.
    """

    if path is None or not _is_sha256(expected_sha256):
        raise M3Top3AdmissionError("LINEAGE_BUNDLE_REQUIRED", "an external lineage bundle path and SHA256 are required", exit_code=EXIT_INTEGRITY)
    bundle_path = Path(path).resolve()
    payload, bundle = _read_exact_json_object(bundle_path)
    actual_bundle_hash = sha256_hex(payload)
    if actual_bundle_hash != expected_sha256:
        raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "lineage bundle bytes differ from the externally supplied hash", {"declared": expected_sha256, "actual": actual_bundle_hash}, EXIT_INTEGRITY)
    admit_claim_locks(bundle)
    if bundle.get("schema_version") != "m3top3-execution-lineage-v1" or not isinstance(bundle.get("releases"), list):
        raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY", "execution-lineage bundle schema is invalid", exit_code=EXIT_INTEGRITY)
    if bundle.get("state") != DIAGNOSTIC_LINEAGE_STATE:
        state = str(bundle.get("state", ""))
        code = "RELEASE_AUTHORITY_ADMISSION_DENIED" if state in ELEVATED_RELEASE_STATES else "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE"
        raise M3Top3AdmissionError(code, "only exact diagnostic lineage may execute", {"state": state}, EXIT_AUTHORITY)
    releases = bundle["releases"]
    domains = [release.get("domain") for release in releases if isinstance(release, dict)]
    if len(domains) != len(set(domains)):
        raise M3Top3AdmissionError("DUPLICATE_DATASET_REF_DOMAIN", "execution lineage has duplicate release domains", exit_code=EXIT_INTEGRITY)
    missing = sorted(set(REQUIRED_LINEAGE_DOMAINS) - set(domains))
    extra = sorted(set(domains) - set(REQUIRED_LINEAGE_DOMAINS))
    if missing:
        raise M3Top3AdmissionError("LINEAGE_DOMAIN_MISSING", "execution lineage is missing required domains", {"missing": missing}, EXIT_INTEGRITY)
    if extra:
        raise M3Top3AdmissionError("EXTRA_DATASET_REF", "execution lineage has unregistered domains", {"extra": extra}, EXIT_INTEGRITY)
    admitted: list[dict[str, Any]] = []
    path_uses: dict[str, list[dict[str, Any]]] = {}
    for release in releases:
        missing_fields = [field for field in RELEASE_REF_FIELDS if field not in release]
        if missing_fields or not all(isinstance(release.get(field), str) and release.get(field) for field in ("release_id", "release_version", "artifact_id", "semantic_role", "state", "as_of_date")):
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY", "release reference identity is incomplete", {"domain": release.get("domain"), "missing": missing_fields}, EXIT_INTEGRITY)
        if not isinstance(release.get("release_revision"), int) or isinstance(release.get("release_revision"), bool) or release["release_revision"] < 0:
            raise M3Top3AdmissionError("RELEASE_REVISION_MISMATCH", "release revision must be a non-negative integer", {"domain": release["domain"]}, EXIT_INTEGRITY)
        try:
            date.fromisoformat(release["as_of_date"])
        except (TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("RELEASE_TEMPORAL_MISMATCH","release as_of_date must be a valid ISO date",{"domain":release["domain"]},EXIT_INTEGRITY) from exc
        if release.get("state") != DIAGNOSTIC_LINEAGE_STATE:
            state = str(release.get("state", ""))
            code = "RELEASE_AUTHORITY_ADMISSION_DENIED" if state in ELEVATED_RELEASE_STATES else "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE"
            raise M3Top3AdmissionError(code, "release state is not admitted for bounded diagnostics", {"domain": release["domain"], "state": state}, EXIT_AUTHORITY)
        if not _is_sha256(release.get("artifact_sha256")) or not _is_sha256(release.get("manifest_sha256")) or not _is_sha256(release.get("component_set_digest")) or not isinstance(release.get("byte_size"), int):
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY", "release hashes/size are malformed", {"domain": release["domain"]}, EXIT_INTEGRITY)
        manifest_path = release.get("manifest_path")
        artifact_path = release.get("artifact_path")
        components = release.get("components")
        if not isinstance(manifest_path, str) or not isinstance(artifact_path, str) or not isinstance(components, list) or not components:
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY", "release manifest, artifact and component locators are required", {"domain": release["domain"]}, EXIT_INTEGRITY)
        live_manifest, manifest = _read_exact_json_object(Path(manifest_path).resolve())
        if sha256_hex(live_manifest) != release["manifest_sha256"]:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "release-manifest bytes differ from lineage", {"domain": release["domain"]}, EXIT_INTEGRITY)
        manifest_state=str(manifest.get("state", ""))
        if manifest_state!=DIAGNOSTIC_LINEAGE_STATE:
            code="RELEASE_AUTHORITY_ADMISSION_DENIED" if manifest_state in ELEVATED_RELEASE_STATES else "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE"
            raise M3Top3AdmissionError(code,"release manifest state is not admitted for bounded diagnostics",{"domain":release["domain"],"state":manifest_state},EXIT_AUTHORITY)
        manifest_tuple = {field: manifest.get(field) for field in RELEASE_MANIFEST_IDENTITY_FIELDS}
        release_tuple = {field: release.get(field) for field in RELEASE_MANIFEST_IDENTITY_FIELDS}
        if manifest_tuple != release_tuple:
            revision_fields = {"domain", "release_id", "release_version", "release_revision", "as_of_date"}
            if manifest_tuple["component_set_digest"]!=release_tuple["component_set_digest"]:
                code="COMPONENT_SET_DIGEST_MISMATCH"
            else:
                code = "RELEASE_REVISION_MISMATCH" if any(manifest_tuple[field] != release_tuple[field] for field in revision_fields) else "DATASET_REF_IDENTITY_MISMATCH"
            raise M3Top3AdmissionError(code, "bundle and release-manifest governed identities differ", {"domain": release["domain"]}, EXIT_INTEGRITY)
        alias_fields = ("physical_alias_allowed", "physical_alias_group_id", "physical_alias_roles")
        if any(field in release or field in manifest for field in alias_fields) and any(manifest.get(field) != release.get(field) for field in alias_fields):
            raise M3Top3AdmissionError("AMBIGUOUS_COMPONENT_ALIAS", "bundle and release-manifest alias-role declarations differ", {"domain": release["domain"]}, EXIT_INTEGRITY)
        artifact = Path(artifact_path).resolve()
        try:
            artifact_hash = hash_file(artifact); artifact_size = artifact.stat().st_size
        except OSError as exc:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "release artifact bytes are unavailable", {"domain": release["domain"]}, EXIT_INTEGRITY) from exc
        if artifact_hash != release["artifact_sha256"] or artifact_size != release["byte_size"]:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "release artifact hash/size differs from live bytes", {"domain": release["domain"]}, EXIT_INTEGRITY)
        normalized_components: list[dict[str, Any]] = []
        declared_paths: set[str] = set()
        for component in components:
            locator = component.get("path") if isinstance(component, dict) else None
            if not isinstance(locator, str):
                raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY", "component locator is missing", {"domain": release["domain"]}, EXIT_INTEGRITY)
            component_path = Path(locator).resolve(); resolved = str(component_path)
            if resolved in declared_paths:
                raise M3Top3AdmissionError("DUPLICATE_LINEAGE_COMPONENT", "release contains a duplicate component locator", {"domain": release["domain"]}, EXIT_INTEGRITY)
            declared_paths.add(resolved)
            try:
                component_hash = hash_file(component_path); component_size = component_path.stat().st_size
            except OSError as exc:
                raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "component bytes are unavailable", {"domain": release["domain"], "path": resolved}, EXIT_INTEGRITY) from exc
            normalized = dict(component)
            if component_hash != component.get("artifact_sha256", component.get("sha256")) or component_size != component.get("byte_size"):
                raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "component hash/size differs from live bytes", {"domain": release["domain"], "component_id": component.get("component_id")}, EXIT_INTEGRITY)
            normalized["artifact_sha256"] = component_hash; normalized["byte_size"] = component_size; normalized["path"] = resolved
            normalized_components.append(normalized); path_uses.setdefault(resolved, []).append(release)
        calculated_digest = canonical_component_set_digest(normalized_components)
        if calculated_digest != release["component_set_digest"] or manifest.get("component_set_digest") != calculated_digest:
            raise M3Top3AdmissionError("COMPONENT_SET_DIGEST_MISMATCH", "component-set digest differs from exact live identities", {"domain": release["domain"]}, EXIT_INTEGRITY)
        manifest_components=manifest.get("components")
        if not isinstance(manifest_components,list):
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY","release manifest must enumerate the exact registered component set",{"domain":release["domain"]},EXIT_INTEGRITY)
        manifest_digest=canonical_component_set_digest(manifest_components)
        live_semantic=[{key:component.get(key) for key in ("component_id","logical_name","byte_size","artifact_sha256","semantic_role")} for component in normalized_components]
        manifest_semantic=[{key:component.get(key) for key in ("component_id","logical_name","byte_size","artifact_sha256","semantic_role")} for component in manifest_components]
        live_ids={component["component_id"] for component in live_semantic}; declared_ids={component["component_id"] for component in manifest_semantic}
        if declared_ids-live_ids:
            raise M3Top3AdmissionError("EXTRA_LINEAGE_COMPONENT","release manifest declares components absent from live registered inputs",{"domain":release["domain"],"extra":sorted(declared_ids-live_ids)},EXIT_INTEGRITY)
        if live_ids-declared_ids or sorted(live_semantic,key=lambda row:row["component_id"])!=sorted(manifest_semantic,key=lambda row:row["component_id"]):
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH","bundle/live component identities differ from release manifest",{"domain":release["domain"]},EXIT_INTEGRITY)
        if manifest_digest!=calculated_digest:
            raise M3Top3AdmissionError("COMPONENT_SET_DIGEST_MISMATCH","release-manifest component digest differs from live inputs",{"domain":release["domain"]},EXIT_INTEGRITY)
        admitted.append({**release, "artifact_path": str(artifact), "manifest_path": str(Path(manifest_path).resolve()), "components": normalized_components})
    for locator, aliases in path_uses.items():
        if len(aliases) <= 1:
            continue
        domains = frozenset(alias["domain"] for alias in aliases)
        expected_roles = sorted(domains)
        alias_is_explicit = (
            domains.issubset(ALLOWED_PHYSICAL_ALIAS_DOMAINS)
            and len(domains) == len(aliases)
            and all(alias.get("physical_alias_allowed") is True for alias in aliases)
            and all(alias.get("physical_alias_group_id") == ALLOWED_PHYSICAL_ALIAS_GROUP for alias in aliases)
            and all(alias.get("physical_alias_roles") == expected_roles for alias in aliases)
        )
        if not alias_is_explicit:
            raise M3Top3AdmissionError("AMBIGUOUS_COMPONENT_ALIAS", "one physical component is reused outside the exact permitted price/CA/calendar alias roles", {"path": locator, "domains": sorted(domains)}, EXIT_INTEGRITY)
    portable = [_portable_release_ref(release) for release in admitted]
    return {
        "schema_version": "m3top3-execution-lineage-v1",
        "state": DIAGNOSTIC_LINEAGE_STATE,
        "bundle_sha256": actual_bundle_hash,
        "bundle_path": str(bundle_path),
        "lineage_identity_hash": sha256_hex(sorted(portable, key=lambda row: row["domain"])),
        "releases": admitted,
        "portable_releases": sorted(portable, key=lambda row: row["domain"]),
    }


def reverify_execution_lineage(admitted: dict[str, Any]) -> None:
    """Catch mutation after admission and before any lazy parse/query/use."""

    try:
        bundle_path = admitted.get("bundle_path")
        bundle_hash = admitted.get("bundle_sha256")
        if not isinstance(bundle_path, str) or not _is_sha256(bundle_hash) or hash_file(Path(bundle_path)) != bundle_hash:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "execution-lineage bundle drifted after admission", exit_code=EXIT_INTEGRITY)
        for release in admitted.get("releases", []):
            if hash_file(Path(release["manifest_path"])) != release["manifest_sha256"] or hash_file(Path(release["artifact_path"])) != release["artifact_sha256"]:
                raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "release artifact or manifest drifted after admission", {"domain": release["domain"]}, EXIT_INTEGRITY)
            for component in release["components"]:
                path = Path(component["path"])
                if hash_file(path) != component["artifact_sha256"] or path.stat().st_size != component["byte_size"]:
                    raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "release component drifted after admission", {"domain": release["domain"], "component_id": component["component_id"]}, EXIT_INTEGRITY)
    except M3Top3AdmissionError:
        raise
    except (OSError,KeyError,TypeError) as exc:
        raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH","execution-lineage component is missing or unreadable after admission",{"cause":type(exc).__name__},EXIT_INTEGRITY) from exc


def lineage_ref_map(admitted: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {release["domain"]: _portable_release_ref(release) for release in admitted["releases"]}


def verify_lineage_temporal_compatibility(admitted:dict[str,Any],snapshot_date:date)->None:
    for release in admitted.get("portable_releases",[]):
        try:
            as_of=date.fromisoformat(release.get("as_of_date"))
        except (TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("RELEASE_TEMPORAL_MISMATCH","release as_of_date is missing or invalid",{"domain":release.get("domain")},EXIT_INTEGRITY) from exc
        if as_of>snapshot_date:
            raise M3Top3AdmissionError("RELEASE_TEMPORAL_MISMATCH","release vintage is later than the snapshot cutoff date",{"domain":release.get("domain"),"as_of_date":release.get("as_of_date"),"snapshot_date":snapshot_date.isoformat()},EXIT_INTEGRITY)


def synthetic_fixture_lineage(universe: Any, features: Any, price: Any) -> dict[str, Any]:
    """Build an explicitly non-release-eligible lineage for unit fixtures.

    This exception is intentionally unavailable to either CLI and is accepted
    only for the exact in-memory diagnostic provider classes.
    """

    if (
        type(universe).__name__ != "StaticUniverseProvider"
        or type(features).__name__ != "InMemoryFeatureProvider"
        or getattr(universe, "authority_status", None) != "DIAGNOSTIC"
        or getattr(price, "semantics", None) != "RAW_IMMUTABLE"
    ):
        raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED", "self-derived lineage is restricted to explicit in-memory diagnostic fixtures", exit_code=EXIT_AUTHORITY)
    feature_hash = getattr(features, "source_hash", None)
    price_hash = getattr(price, "dataset_hash", None)
    values = {
        "UNIVERSE_RELEASE": (getattr(universe, "release_id", "SYNTH-U"), getattr(universe, "release_hash", None), "SYNTHETIC_UNIVERSE"),
        "DENOMINATOR_ELIGIBILITY_RELEASE": (getattr(universe, "denominator_release_id", "SYNTH-D"), getattr(universe, "denominator_release_hash", None), "SYNTHETIC_DENOMINATOR"),
        "FEATURE_SOURCE_RELEASE": (getattr(features, "source_version", "SYNTH-F"), feature_hash, "SYNTHETIC_FEATURES"),
        "PRICE_RELEASE": (getattr(price, "dataset_id", "SYNTH-P"), price_hash, "SYNTHETIC_PRICE"),
        "CORPORATE_ACTION_RELEASE": (f"{getattr(price, 'dataset_id', 'SYNTH-P')}:CA", price_hash, "SYNTHETIC_CA"),
        "TRADING_CALENDAR_RELEASE": (f"{getattr(price, 'dataset_id', 'SYNTH-P')}:CALENDAR", price_hash, "SYNTHETIC_CALENDAR"),
        "WINDOW_REGISTRY_RELEASE": ("SYNTHETIC-WINDOW-REGISTRY", sha256_hex(b"SYNTHETIC-WINDOW-REGISTRY"), "SYNTHETIC_WINDOW"),
        "SCORER_RELEASE": ("SYNTHETIC-SCORER-RELEASE", sha256_hex(b"SYNTHETIC-SCORER-RELEASE"), "SYNTHETIC_SCORER"),
    }
    releases=[]
    for domain,(release_id,artifact_hash,role) in values.items():
        if not _is_sha256(artifact_hash):
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH", "synthetic fixture exposes an invalid exact hash", {"domain":domain}, EXIT_INTEGRITY)
        component={"component_id":f"{release_id}:component","logical_name":f"{domain.lower()}.fixture","byte_size":0,"artifact_sha256":artifact_hash,"semantic_role":role}
        digest=canonical_component_set_digest([component])
        release={"domain":domain,"release_id":release_id,"release_version":"fixture-v1","release_revision":0,"artifact_id":f"{release_id}:artifact","artifact_sha256":artifact_hash,"byte_size":0,"manifest_sha256":sha256_hex({"domain":domain,"release_id":release_id,"component_set_digest":digest}),"component_set_digest":digest,"semantic_role":role,"state":DIAGNOSTIC_LINEAGE_STATE,"as_of_date":"1970-01-01","components":[component]}
        releases.append(release)
    portable=sorted((_portable_release_ref(release) for release in releases),key=lambda row:row["domain"])
    bundle_hash=sha256_hex({"schema_version":"m3top3-execution-lineage-v1","state":DIAGNOSTIC_LINEAGE_STATE,"synthetic_only":True,"releases":portable})
    return {"schema_version":"m3top3-execution-lineage-v1","state":DIAGNOSTIC_LINEAGE_STATE,"synthetic_only":True,"release_eligible":False,"bundle_sha256":bundle_hash,"bundle_path":None,"lineage_identity_hash":sha256_hex(portable),"releases":releases,"portable_releases":portable}


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def _universe_state_payload(state: Any) -> dict[str, Any]:
    valid_from = getattr(state, "valid_from", None)
    valid_to = getattr(state, "valid_to", None)
    return {
        "company_id": getattr(state, "company_id", None),
        "security_code": str(getattr(state, "security_code", "")).zfill(6),
        "valid_from": valid_from.isoformat() if isinstance(valid_from, date) else None,
        "valid_to": valid_to.isoformat() if isinstance(valid_to, date) else None,
        "operational_member": getattr(state, "operational_member", None),
        "tradable_eligible": getattr(state, "tradable_eligible", None),
        "universe_record_id": getattr(state, "universe_record_id", None),
        "status": getattr(state, "status", None),
    }


def universe_member_identity(state: Any) -> str:
    payload = _universe_state_payload(state)
    membership = {
        "company_id": payload["company_id"],
        "security_code": payload["security_code"],
        "valid_from": payload["valid_from"],
        "valid_to": payload["valid_to"],
        "universe_record_id": payload["universe_record_id"],
    }
    return deterministic_id("universe_member", membership)


def universe_member_set_digest(rows: Iterable[Any]) -> str:
    """Canonical applicable-Universe digest required by contract section 2.3.

    Membership is the company/security binding at the cutoff.  Release record
    IDs and eligibility facts deliberately do not participate in this digest.
    """

    canonical_rows=[]
    for row in rows:
        company_id=row.get("company_id") if isinstance(row,dict) else getattr(row,"company_id",None)
        security_code=(row.get("security_code_at_cutoff",row.get("security_code")) if isinstance(row,dict) else getattr(row,"security_code",None))
        canonical_rows.append({"company_id":company_id,"security_code_at_cutoff":str(security_code or "").zfill(6)})
    return sha256_hex(sorted(canonical_rows,key=lambda item:(str(item["company_id"]),item["security_code_at_cutoff"])))


def eligibility_set_digest(rows: Iterable[Any], status: str) -> str:
    """Canonical eligible/ineligible digest preserving company/security/record."""

    canonical_rows=[]
    for row in rows:
        value=lambda field,default=None: row.get(field,default) if isinstance(row,dict) else getattr(row,field,default)
        if value("eligibility_status")!=status:
            continue
        canonical_rows.append({
            "company_id":value("company_id"),
            "security_code_at_cutoff":str(value("security_code_at_cutoff",value("security_code","")) or "").zfill(6),
            "eligibility_record_id":value("eligibility_record_id"),
        })
    return sha256_hex(sorted(canonical_rows,key=lambda item:(str(item["company_id"]),item["security_code_at_cutoff"],str(item["eligibility_record_id"]))))


def eligibility_record_identity(
    state: Any,
    snapshot_date: date,
    denominator_release_id: str,
    universe_release_revision: int = 0,
    denominator_release_revision: int = 0,
    snapshot_cutoff_at: str | None = None,
    eligibility_status: str | None = None,
) -> str:
    payload = _universe_state_payload(state)
    status = eligibility_status or (
        "ELIGIBLE"
        if payload["operational_member"] is True and payload["tradable_eligible"] is True
        else "INELIGIBLE"
        if payload["operational_member"] is False or payload["tradable_eligible"] is False
        else "UNRESOLVED"
    )
    return deterministic_id(
        "eligibility",
        {
            "denominator_release_id": denominator_release_id,
            "universe_release_revision": universe_release_revision,
            "denominator_release_revision": denominator_release_revision,
            "snapshot_date": snapshot_date.isoformat(),
            "snapshot_cutoff_at": snapshot_cutoff_at or f"{snapshot_date.isoformat()}T23:59:59+09:00",
            "company_id": payload["company_id"],
            "security_code": payload["security_code"],
            "universe_record_id": payload["universe_record_id"],
            "eligibility_status": status,
        },
    )


def _universe_states_hash(states: Iterable[Any]) -> str:
    payload = sorted(
        (_universe_state_payload(state) for state in states),
        key=lambda row: (
            str(row["company_id"]),
            str(row["security_code"]),
            row["valid_from"] or "",
            row["valid_to"] or "",
            str(row["universe_record_id"]),
        ),
    )
    return sha256_hex(payload)


def _eligibility_decision_payload(row: Any) -> dict[str, Any]:
    snapshot_date=getattr(row,"snapshot_date",None)
    return {
        "snapshot_date": snapshot_date.isoformat() if isinstance(snapshot_date,date) else None,
        "snapshot_cutoff_at": getattr(row,"snapshot_cutoff_at",None),
        "universe_release_id": getattr(row,"universe_release_id",None),
        "universe_release_revision": getattr(row,"universe_release_revision",None),
        "denominator_release_id": getattr(row,"denominator_release_id",None),
        "denominator_release_revision": getattr(row,"denominator_release_revision",None),
        "company_id": getattr(row,"company_id",None),
        "security_code": str(getattr(row,"security_code","")).zfill(6),
        "universe_record_id": getattr(row,"universe_record_id",None),
        "universe_member_id": getattr(row,"universe_member_id",None),
        "eligibility_record_id": getattr(row,"eligibility_record_id",None),
        "eligibility_status": getattr(row,"eligibility_status",None),
        "status": getattr(row,"status",None),
    }


def _eligibility_decisions_hash(rows: Iterable[Any]) -> str:
    return sha256_hex(sorted((_eligibility_decision_payload(row) for row in rows),key=lambda item:(item["snapshot_date"] or "",str(item["company_id"]),str(item["security_code"]),str(item["eligibility_record_id"]))))


def _effective_states(states: Iterable[Any], snapshot_date: date) -> list[Any]:
    return [state for state in states if state.effective_on(snapshot_date)]


def _live_release_hash(provider: Any, path_field: str, rows_field: str) -> str:
    path = getattr(provider, path_field, None)
    if path is not None:
        try:
            return hash_file(Path(path))
        except OSError as exc:
            raise M3Top3AdmissionError(
                "UNIVERSE_RELEASE_HASH_MISMATCH",
                "universe or denominator release bytes are unavailable during live verification",
                {"path": str(path), "cause": type(exc).__name__},
                EXIT_INTEGRITY,
            ) from exc
    rows = getattr(provider, rows_field, None)
    if not isinstance(rows, list):
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_INCOMPLETE",
            "universe provider exposes neither exact release bytes nor an in-memory diagnostic release",
            {"rows_field": rows_field},
            EXIT_INTEGRITY,
        )
    return _universe_states_hash(rows)


def verify_universe_release(provider: Any, snapshot_date: date, states: Iterable[Any]) -> dict[str, Any]:
    """Bind an exact universe release to an independent denominator slice.

    The release source and denominator source remain separate even when a
    diagnostic fixture intentionally points both at the same bytes.  This
    makes subset/extra/drift checks explicit without granting canonical or
    Official authority to a self-declared diagnostic input.
    """

    required = (
        "release_id",
        "release_hash",
        "release_status",
        "denominator_release_id",
        "denominator_release_hash",
        "denominator_status",
        "release_state_hash",
        "denominator_state_hash",
    )
    missing = [field for field in required if not getattr(provider, field, None)]
    if missing:
        if "release_hash" in missing:
            raise M3Top3AdmissionError("UNIVERSE_RELEASE_BYTES_REQUIRED","Universe admission requires an independently supplied exact artifact SHA and bytes",{"missing":missing},EXIT_INTEGRITY)
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_INCOMPLETE",
            "universe release and denominator lineage must be complete",
            {"missing": missing},
            EXIT_INTEGRITY,
        )
    lineage_manifest_kind = getattr(provider, "lineage_manifest_kind", None)
    if lineage_manifest_kind not in {"EXACT_EXTERNAL_MANIFEST", "SYNTHETIC_IN_MEMORY_DIAGNOSTIC"}:
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
            "universe provider has no admitted lineage-manifest class",
            exit_code=EXIT_INTEGRITY,
        )
    if lineage_manifest_kind == "EXACT_EXTERNAL_MANIFEST":
        manifest_path = getattr(provider, "lineage_manifest_path", None)
        manifest_hash = getattr(provider, "lineage_manifest_hash", None)
        try:
            live_manifest_hash = hash_file(Path(manifest_path))
            live_manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "lineage manifest is unavailable or malformed during live admission",
                {"cause": type(exc).__name__},
                EXIT_INTEGRITY,
            ) from exc
        if live_manifest_hash != manifest_hash or live_manifest != getattr(provider, "_lineage_manifest", None):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "lineage manifest bytes or parsed content drifted after provider construction",
                {"declared": manifest_hash, "actual": live_manifest_hash},
                EXIT_INTEGRITY,
            )
        for path_attr,hash_attr,cache_attr in (
            ("universe_expectation_manifest_path","universe_expectation_manifest_hash","_universe_expectation_manifest"),
            ("denominator_expectation_manifest_path","denominator_expectation_manifest_hash","_denominator_expectation_manifest"),
        ):
            path=Path(getattr(provider,path_attr,None))
            try:
                live_bytes=path.read_bytes(); live_value=json.loads(live_bytes.decode("utf-8")); live_hash=sha256_hex(live_bytes)
            except (OSError,UnicodeError,json.JSONDecodeError,TypeError) as exc:
                raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","independent expectation manifest is unavailable during live admission",{"manifest":path_attr},EXIT_AUTHORITY) from exc
            if live_hash!=getattr(provider,hash_attr,None) or live_value!=getattr(provider,cache_attr,None):
                raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH","independent expectation manifest drifted after provider construction",{"manifest":path_attr},EXIT_INTEGRITY)
        declared_slice=getattr(provider,"_lineage_slices",{}).get(snapshot_date.isoformat())
        if not isinstance(declared_slice,dict):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_SLICE_NOT_DECLARED","lineage manifest has no slice for the requested snapshot date",{"snapshot_date":snapshot_date.isoformat()},EXIT_BLOCKED)
    if provider.release_status not in ADMITTED_RELEASE_STATUSES:
        raise M3Top3AdmissionError(
            "UNIVERSE_RELEASE_STATUS_UNVERIFIED",
            "partial or unverified universe releases are not scoreable",
            {"status": provider.release_status},
            EXIT_BLOCKED,
        )
    if provider.denominator_status not in ADMITTED_RELEASE_STATUSES:
        raise M3Top3AdmissionError(
            "DENOMINATOR_RELEASE_STATUS_UNVERIFIED",
            "partial or unverified denominator releases are not scoreable",
            {"status": provider.denominator_status},
            EXIT_BLOCKED,
        )
    live_release_hash = _live_release_hash(provider, "path", "_rows")
    if not _is_sha256(provider.release_hash) or provider.release_hash != live_release_hash:
        raise M3Top3AdmissionError(
            "UNIVERSE_RELEASE_HASH_MISMATCH",
            "configured universe release hash differs from live release bytes",
            {"declared": provider.release_hash, "actual": live_release_hash},
            EXIT_INTEGRITY,
        )
    live_denominator_hash = _live_release_hash(provider, "denominator_path", "_denominator_rows")
    if not _is_sha256(provider.denominator_release_hash) or provider.denominator_release_hash != live_denominator_hash:
        raise M3Top3AdmissionError(
            "DENOMINATOR_RELEASE_HASH_MISMATCH",
            "configured denominator release hash differs from live denominator bytes",
            {"declared": provider.denominator_release_hash, "actual": live_denominator_hash},
            EXIT_INTEGRITY,
        )
    all_release_rows = getattr(provider, "_rows", None)
    all_denominator_rows = getattr(provider, "_denominator_rows", None)
    if not isinstance(all_release_rows, list) or not isinstance(all_denominator_rows, list):
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_INCOMPLETE",
            "independent parsed release and denominator rows are required",
            exit_code=EXIT_INTEGRITY,
        )
    live_release_state_hash = _universe_states_hash(all_release_rows)
    external_denominator = getattr(provider,"denominator_schema_version",None)=="m3top3-denominator-eligibility-v1"
    live_denominator_state_hash = _eligibility_decisions_hash(all_denominator_rows) if external_denominator else _universe_states_hash(all_denominator_rows)
    if provider.release_state_hash != live_release_state_hash:
        raise M3Top3AdmissionError(
            "UNIVERSE_RELEASE_STATE_DRIFT",
            "parsed universe state changed after release admission",
            {"declared": provider.release_state_hash, "actual": live_release_state_hash},
            EXIT_INTEGRITY,
        )
    if provider.denominator_state_hash != live_denominator_state_hash:
        raise M3Top3AdmissionError(
            "DENOMINATOR_RELEASE_STATE_DRIFT",
            "parsed denominator state changed after release admission",
            {"declared": provider.denominator_state_hash, "actual": live_denominator_state_hash},
            EXIT_INTEGRITY,
        )

    actual = list(states)
    independently_released = _effective_states(all_release_rows, snapshot_date)
    independently_expected = _effective_states(all_denominator_rows, snapshot_date)

    def identities(rows: list[Any], artifact: str) -> list[str]:
        company_ids: list[str] = []
        security_codes: list[str] = []
        record_ids: list[str] = []
        member_ids: list[str] = []
        for index, state in enumerate(rows):
            payload = _universe_state_payload(state)
            if not all(isinstance(payload[field], str) and payload[field] for field in ("company_id", "security_code", "universe_record_id")):
                raise M3Top3AdmissionError(
                    "UNIVERSE_IDENTITY_INCOMPLETE",
                    f"{artifact} member identity is incomplete",
                    {"row_index": index},
                    EXIT_INTEGRITY,
                )
            if payload["status"] not in ADMITTED_RELEASE_STATUSES:
                raise M3Top3AdmissionError(
                    "UNIVERSE_MEMBER_STATUS_UNVERIFIED",
                    f"{artifact} contains a partial or unverified member row",
                    {"row_index": index, "company_id": payload["company_id"], "status": payload["status"]},
                    EXIT_BLOCKED,
                )
            company_ids.append(payload["company_id"])
            security_codes.append(payload["security_code"])
            record_ids.append(payload["universe_record_id"])
            member_id = universe_member_identity(state)
            member_ids.append(member_id)
        if len(set(company_ids)) != len(company_ids):
            raise M3Top3AdmissionError("DUPLICATE_UNIVERSE_COMPANY_ID",f"{artifact} contains duplicate company identity",{"artifact":artifact},EXIT_INTEGRITY)
        if len(set(security_codes)) != len(security_codes):
            raise M3Top3AdmissionError("DUPLICATE_ACTIVE_SECURITY_CODE",f"{artifact} contains an ambiguous active security binding",{"artifact":artifact},EXIT_INTEGRITY)
        if len(set(record_ids)) != len(record_ids) or len(set(member_ids)) != len(member_ids):
            raise M3Top3AdmissionError("DUPLICATE_UNIVERSE_IDENTITY",f"{artifact} contains duplicate record/member identity",{"artifact":artifact},EXIT_INTEGRITY)
        return sorted(member_ids)

    actual_ids = identities(actual, "universe release slice")
    release_ids = identities(independently_released, "independently parsed universe release slice")
    # Detect interval ambiguity in the complete release after applicable-slice
    # duplicate checks have produced their more specific stable codes.
    by_company: dict[str,list[Any]]={}
    for state in all_release_rows: by_company.setdefault(str(getattr(state,"company_id", "")),[]).append(state)
    for company_id,rows in by_company.items():
        ordered=sorted(rows,key=lambda item:(getattr(item,"valid_from",None) or date.min,getattr(item,"valid_to",None) or date.max))
        for left,right in zip(ordered,ordered[1:]):
            left_end=getattr(left,"valid_to",None) or date.max; right_start=getattr(right,"valid_from",None) or date.min
            if right_start<left_end:
                raise M3Top3AdmissionError("UNIVERSE_EFFECTIVE_INTERVAL_CONFLICT","universe security bindings overlap for one company",{"company_id":company_id},EXIT_INTEGRITY)
    if actual_ids != release_ids:
        raise M3Top3AdmissionError(
            "UNIVERSE_RELEASE_RUNTIME_SLICE_MISMATCH",
            "provider runtime membership slice differs from the independently parsed release rows",
            exit_code=EXIT_INTEGRITY,
        )
    eligibility_records: dict[str, dict[str, Any]] = {}
    eligible_record_ids: list[str] = []
    ineligible_member_ids: list[str] = []
    ineligible_record_ids: list[str] = []
    unresolved_member_ids: list[str] = []
    universe_release_revision=0
    denominator_release_revision=0
    declared_snapshot_cutoff=f"{snapshot_date.isoformat()}T23:59:59+09:00"
    digest_decisions:list[Any]=[]
    external_denominator_missing:list[str]=[]
    if external_denominator:
        universe_revisions={row.universe_release_revision for row in independently_expected}
        denominator_revisions={row.denominator_release_revision for row in independently_expected}
        cutoffs={row.snapshot_cutoff_at for row in independently_expected}
        if len(universe_revisions)!=1 or len(denominator_revisions)!=1 or len(cutoffs)!=1:
            raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","denominator slice has mixed release revisions or cutoffs",exit_code=EXIT_INTEGRITY)
        universe_release_revision=next(iter(universe_revisions))
        denominator_release_revision=next(iter(denominator_revisions))
        declared_snapshot_cutoff=next(iter(cutoffs))
        try:
            parsed_cutoff=datetime.fromisoformat(declared_snapshot_cutoff)
        except (TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","denominator cutoff is invalid",exit_code=EXIT_INTEGRITY) from exc
        if parsed_cutoff.tzinfo is None or parsed_cutoff.utcoffset() is None or parsed_cutoff.date()!=snapshot_date:
            raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","denominator cutoff must be timezone-aware and match snapshot date",exit_code=EXIT_INTEGRITY)
        if universe_release_revision!=getattr(provider,"release_revision",None) or denominator_release_revision!=getattr(provider,"denominator_release_revision",None):
            raise M3Top3AdmissionError("RELEASE_REVISION_MISMATCH","denominator rows differ from independent release revision bindings",exit_code=EXIT_INTEGRITY)
        keys=[(row.universe_release_id,row.universe_release_revision,row.snapshot_date,row.company_id) for row in independently_expected]
        if len(keys)!=len(set(keys)):
            raise M3Top3AdmissionError("DUPLICATE_DENOMINATOR_KEY","denominator has duplicate company/date/revision decisions",exit_code=EXIT_INTEGRITY)
        decision_by_member={row.universe_member_id:row for row in independently_expected}
        if len(decision_by_member)!=len(independently_expected):
            raise M3Top3AdmissionError("DUPLICATE_DENOMINATOR_KEY","denominator has duplicate universe-member decisions",exit_code=EXIT_INTEGRITY)
        eligibility_record_ids=[row.eligibility_record_id for row in independently_expected]
        if len(eligibility_record_ids)!=len(set(eligibility_record_ids)):
            raise M3Top3AdmissionError("DUPLICATE_DENOMINATOR_KEY","denominator has duplicate eligibility-record identities",exit_code=EXIT_INTEGRITY)
        expected_ids=sorted(decision_by_member)
        missing=sorted(set(actual_ids)-set(expected_ids)); extra=sorted(set(expected_ids)-set(actual_ids))
        external_denominator_missing=missing
        if extra: raise M3Top3AdmissionError("DENOMINATOR_MEMBER_EXTRA","denominator includes a member outside Universe",{"extra":extra},EXIT_INTEGRITY)
        actual_by_member={universe_member_identity(row):row for row in independently_released}
        for member_id,row in decision_by_member.items():
            state=actual_by_member[member_id]
            if row.universe_release_id!=provider.release_id or row.denominator_release_id!=provider.denominator_release_id or row.universe_release_revision!=universe_release_revision or row.denominator_release_revision!=denominator_release_revision or row.snapshot_date!=snapshot_date or row.snapshot_cutoff_at!=declared_snapshot_cutoff:
                raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","denominator date/cutoff/release/revision tuple differs from admitted run",{"company_id":row.company_id},EXIT_INTEGRITY)
            if row.company_id!=state.company_id or row.security_code!=str(state.security_code).zfill(6) or row.universe_record_id!=state.universe_record_id:
                raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","denominator decision identity differs from Universe binding",{"company_id":row.company_id},EXIT_INTEGRITY)
            if row.status not in ADMITTED_RELEASE_STATUSES or row.eligibility_status=="UNRESOLVED":
                raise M3Top3AdmissionError("ELIGIBILITY_RELEASE_NOT_COMPLETE","denominator contains a nonterminal eligibility decision",{"company_id":row.company_id,"status":row.status,"eligibility_status":row.eligibility_status},EXIT_BLOCKED)
            eligibility_records[member_id]={"eligibility_record_id":row.eligibility_record_id,"eligibility_status":row.eligibility_status}
        digest_decisions=list(decision_by_member.values())
        expected_eligible_ids=sorted(member_id for member_id,row in decision_by_member.items() if row.eligibility_status=="ELIGIBLE")
    else:
        expected_ids = identities(independently_expected, "denominator slice")
        actual_eligible_ids=sorted(universe_member_identity(state) for state in actual if _universe_state_payload(state)["operational_member"] is True and _universe_state_payload(state)["tradable_eligible"] is True)
        expected_eligible_ids=sorted(universe_member_identity(state) for state in independently_expected if _universe_state_payload(state)["operational_member"] is True and _universe_state_payload(state)["tradable_eligible"] is True)
        missing=sorted(set(expected_ids)-set(actual_ids)); extra=sorted(set(actual_ids)-set(expected_ids))
        if missing or extra:
            raise M3Top3AdmissionError("UNIVERSE_DENOMINATOR_MEMBERSHIP_MISMATCH","universe release slice differs from denominator slice",{"missing":missing,"extra":extra},EXIT_INTEGRITY)
        if actual_eligible_ids != expected_eligible_ids:
            raise M3Top3AdmissionError("UNIVERSE_DENOMINATOR_ELIGIBILITY_MISMATCH","eligible identity set differs from denominator slice",exit_code=EXIT_INTEGRITY)
        expected_by_member = {universe_member_identity(state): state for state in independently_expected}
        for member_id in expected_ids:
            state=expected_by_member[member_id]; payload=_universe_state_payload(state)
            eligibility_status="ELIGIBLE" if payload["operational_member"] is True and payload["tradable_eligible"] is True else "INELIGIBLE" if payload["operational_member"] is False or payload["tradable_eligible"] is False else "UNRESOLVED"
            record_id=eligibility_record_identity(state,snapshot_date,provider.denominator_release_id,universe_release_revision,denominator_release_revision,declared_snapshot_cutoff)
            eligibility_records[member_id]={"eligibility_record_id":record_id,"eligibility_status":eligibility_status}
            digest_decisions.append({"company_id":payload["company_id"],"security_code":payload["security_code"],"eligibility_record_id":record_id,"eligibility_status":eligibility_status})
    if external_denominator_missing:
        raise M3Top3AdmissionError("DENOMINATOR_MEMBER_MISSING","Universe member is missing from denominator decisions",{"missing":external_denominator_missing},EXIT_INTEGRITY)
    for member_id in expected_ids:
        record_id=eligibility_records[member_id]["eligibility_record_id"]
        eligibility_status=eligibility_records[member_id]["eligibility_status"]
        if eligibility_status == "ELIGIBLE":
            eligible_record_ids.append(record_id)
        elif eligibility_status == "INELIGIBLE":
            ineligible_member_ids.append(member_id); ineligible_record_ids.append(record_id)
        else:
            unresolved_member_ids.append(member_id)
    canonical_universe_digest=universe_member_set_digest(independently_released)
    canonical_eligible_digest=eligibility_set_digest(digest_decisions,"ELIGIBLE")
    canonical_ineligible_digest=eligibility_set_digest(digest_decisions,"INELIGIBLE")
    denominator_partition_digest=sha256_hex({
        "universe_member_set_digest":canonical_universe_digest,
        "eligible_set_digest":canonical_eligible_digest,
        "ineligible_set_digest":canonical_ineligible_digest,
        "universe_count":len(expected_ids),
        "eligible_count":len(expected_eligible_ids),
        "ineligible_count":len(ineligible_member_ids),
    })
    release_partition = f"STATIC_RELEASE:{snapshot_date.isoformat()}"
    denominator_partition = f"STATIC_DENOMINATOR:{snapshot_date.isoformat()}"
    if lineage_manifest_kind == "EXACT_EXTERNAL_MANIFEST":
        declared_slice = getattr(provider, "_lineage_slices", {}).get(snapshot_date.isoformat())
        required_slice = {
            "snapshot_date",
            "release_partition",
            "denominator_partition",
            "release_row_count",
            "denominator_row_count",
            "eligible_row_count",
            "ineligible_row_count",
            "release_identity_hash",
            "denominator_identity_hash",
            "universe_member_set_digest",
            "eligible_identity_hash",
            "ineligible_identity_hash",
            "eligible_set_digest",
            "ineligible_set_digest",
            "denominator_partition_digest",
        }
        if external_denominator:
            required_slice.update({"snapshot_cutoff_at","universe_release_revision","denominator_release_revision"})
        if not isinstance(declared_slice, dict) or required_slice - set(declared_slice):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_SLICE_NOT_DECLARED",
                "lineage manifest has no complete slice for the requested snapshot date",
                {"snapshot_date": snapshot_date.isoformat()},
                EXIT_BLOCKED,
            )
        release_partition = declared_slice.get("release_partition")
        denominator_partition = declared_slice.get("denominator_partition")
        if not all(isinstance(value, str) and value for value in (release_partition, denominator_partition)):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "lineage slice partitions must be non-empty logical locators",
                exit_code=EXIT_INTEGRITY,
            )
        expected_slice = {
            "snapshot_date": snapshot_date.isoformat(),
            "release_row_count": len(release_ids),
            "denominator_row_count": len(expected_ids),
            "eligible_row_count": len(expected_eligible_ids),
            "ineligible_row_count": len(ineligible_member_ids),
            "release_identity_hash": aggregate_hash(release_ids),
            "denominator_identity_hash": aggregate_hash(expected_ids),
            "universe_member_set_digest": canonical_universe_digest,
            "eligible_identity_hash": aggregate_hash(expected_eligible_ids),
            "ineligible_identity_hash": aggregate_hash(sorted(ineligible_member_ids)),
            "eligible_set_digest": canonical_eligible_digest,
            "ineligible_set_digest": canonical_ineligible_digest,
            "denominator_partition_digest": denominator_partition_digest,
        }
        if external_denominator:
            expected_slice.update({"snapshot_cutoff_at":declared_snapshot_cutoff,"universe_release_revision":universe_release_revision,"denominator_release_revision":denominator_release_revision})
        declared_comparable = {field: declared_slice.get(field) for field in expected_slice}
        declared_counts=(
            declared_slice.get("release_row_count"),
            declared_slice.get("denominator_row_count"),
            declared_slice.get("eligible_row_count"),
            declared_slice.get("ineligible_row_count"),
        )
        expected_counts=(
            expected_slice["release_row_count"],
            expected_slice["denominator_row_count"],
            expected_slice["eligible_row_count"],
            expected_slice["ineligible_row_count"],
        )
        if declared_counts!=expected_counts or (
            isinstance(declared_slice.get("denominator_row_count"),int)
            and isinstance(declared_slice.get("eligible_row_count"),int)
            and isinstance(declared_slice.get("ineligible_row_count"),int)
            and declared_slice["denominator_row_count"]
            != declared_slice["eligible_row_count"]+declared_slice["ineligible_row_count"]
        ):
            raise M3Top3AdmissionError(
                "DENOMINATOR_COUNT_MISMATCH",
                "declared U/E/I slice counts differ from the exact live releases or do not reconcile",
                {"declared":declared_counts,"actual":expected_counts},
                EXIT_INTEGRITY,
            )
        if declared_slice.get("universe_member_set_digest")!=canonical_universe_digest:
            raise M3Top3AdmissionError("UNIVERSE_SET_DIGEST_MISMATCH","declared Universe company/security digest differs from live applicable release",{"declared":declared_slice.get("universe_member_set_digest"),"actual":canonical_universe_digest},EXIT_INTEGRITY)
        if (
            declared_slice.get("eligible_set_digest")!=canonical_eligible_digest
            or declared_slice.get("ineligible_set_digest")!=canonical_ineligible_digest
            or declared_slice.get("denominator_partition_digest")!=denominator_partition_digest
        ):
            raise M3Top3AdmissionError(
                "ELIGIBLE_SET_DIGEST_MISMATCH",
                "declared eligibility partition digests differ from the exact denominator decisions",
                exit_code=EXIT_INTEGRITY,
            )
        if external_denominator and (
            declared_slice.get("snapshot_cutoff_at")!=declared_snapshot_cutoff
            or declared_slice.get("universe_release_revision")!=universe_release_revision
            or declared_slice.get("denominator_release_revision")!=denominator_release_revision
        ):
            raise M3Top3AdmissionError(
                "DENOMINATOR_LINEAGE_MISMATCH",
                "declared denominator cutoff or revision differs from the exact decision release",
                exit_code=EXIT_INTEGRITY,
            )
        if declared_comparable != expected_slice:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_SLICE_MISMATCH",
                "declared applicable-date counts or identity digests differ from live release/denominator rows",
                {"declared": declared_comparable, "actual": expected_slice},
                EXIT_INTEGRITY,
            )
        universe_expectation_slices={str(item.get("snapshot_date")):item for item in provider._universe_expectation_manifest.get("slices",[]) if isinstance(item,dict)}
        denominator_expectation_slices={str(item.get("snapshot_date")):item for item in provider._denominator_expectation_manifest.get("slices",[]) if isinstance(item,dict)}
        u_expectation=universe_expectation_slices.get(snapshot_date.isoformat()); d_expectation=denominator_expectation_slices.get(snapshot_date.isoformat())
        expected_u={"snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":declared_snapshot_cutoff,"universe_count":len(expected_ids),"universe_member_set_digest":canonical_universe_digest}
        expected_d={"snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":declared_snapshot_cutoff,"universe_count":len(expected_ids),"eligible_count":len(expected_eligible_ids),"ineligible_count":len(ineligible_member_ids),"universe_member_set_digest":canonical_universe_digest,"eligible_set_digest":canonical_eligible_digest,"ineligible_set_digest":canonical_ineligible_digest,"denominator_partition_digest":denominator_partition_digest}
        if not isinstance(u_expectation,dict) or {field:u_expectation.get(field) for field in expected_u}!=expected_u:
            code="UNIVERSE_SET_DIGEST_MISMATCH" if isinstance(u_expectation,dict) and u_expectation.get("universe_member_set_digest")!=canonical_universe_digest else "UNIVERSE_LINEAGE_SLICE_MISMATCH"
            raise M3Top3AdmissionError(code,"independent Universe expectation differs from live applicable membership",exit_code=EXIT_INTEGRITY)
        if not isinstance(d_expectation,dict) or {field:d_expectation.get(field) for field in expected_d}!=expected_d:
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_SLICE_MISMATCH","independent denominator expectation differs from live E/I partition",exit_code=EXIT_INTEGRITY)
        release_binding = provider._lineage_manifest["release"]
        denominator_binding = provider._lineage_manifest["denominator"]
        release_logical_locator = release_binding["logical_locator"]
        denominator_logical_locator = denominator_binding["logical_locator"]
        universe_lineage_manifest_locator=str(Path(provider.lineage_manifest_path).resolve())
        universe_expectation_manifest_locator=str(Path(provider.universe_expectation_manifest_path).resolve())
        denominator_expectation_manifest_locator=str(Path(provider.denominator_expectation_manifest_path).resolve())
    else:
        if getattr(provider, "authority_status", None) != "DIAGNOSTIC":
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
                "synthetic in-memory lineage is restricted to explicit DIAGNOSTIC authority status",
                exit_code=EXIT_AUTHORITY,
            )
        release_logical_locator = f"memory://{provider.release_id}"
        denominator_logical_locator = f"memory://{provider.denominator_release_id}"
        universe_lineage_manifest_locator=None
        universe_expectation_manifest_locator=None
        denominator_expectation_manifest_locator=None
    return {
        "universe_lineage_manifest_kind": lineage_manifest_kind,
        "universe_lineage_manifest_hash": provider.lineage_manifest_hash,
        "universe_release_id": provider.release_id,
        "universe_release_hash": provider.release_hash,
        "universe_release_status": provider.release_status,
        "universe_authority_status": getattr(provider, "authority_status", None),
        "universe_release_state_hash": provider.release_state_hash,
        "universe_release_logical_locator": release_logical_locator,
        "universe_release_partition": release_partition,
        "universe_release_revision": universe_release_revision,
        "denominator_release_id": provider.denominator_release_id,
        "denominator_release_hash": provider.denominator_release_hash,
        "denominator_release_status": provider.denominator_status,
        "denominator_state_hash": provider.denominator_state_hash,
        "denominator_logical_locator": denominator_logical_locator,
        "denominator_partition": denominator_partition,
        "denominator_release_revision": denominator_release_revision,
        "snapshot_cutoff_at": declared_snapshot_cutoff,
        "universe_lineage_manifest_locator": universe_lineage_manifest_locator,
        "universe_expectation_manifest_locator": universe_expectation_manifest_locator,
        "universe_expectation_manifest_hash": getattr(provider,"universe_expectation_manifest_hash",None),
        "denominator_expectation_manifest_locator": denominator_expectation_manifest_locator,
        "denominator_expectation_manifest_hash": getattr(provider,"denominator_expectation_manifest_hash",None),
        "denominator_member_ids": expected_ids,
        "denominator_identity_hash": aggregate_hash(expected_ids),
        "universe_member_set_digest": canonical_universe_digest,
        "denominator_row_count": len(expected_ids),
        "eligible_member_ids": expected_eligible_ids,
        "eligible_identity_hash": aggregate_hash(expected_eligible_ids),
        "eligible_row_count": len(expected_eligible_ids),
        "ineligible_member_ids": sorted(ineligible_member_ids),
        "ineligible_identity_hash": aggregate_hash(sorted(ineligible_member_ids)),
        "ineligible_row_count": len(ineligible_member_ids),
        "eligible_record_ids": sorted(eligible_record_ids),
        "eligible_set_digest": canonical_eligible_digest,
        "ineligible_record_ids": sorted(ineligible_record_ids),
        "ineligible_set_digest": canonical_ineligible_digest,
        "unresolved_member_ids": sorted(unresolved_member_ids),
        "eligibility_records": eligibility_records,
        "denominator_partition_digest": denominator_partition_digest,
    }


def verify_feature_release(provider: Any) -> dict[str, Any]:
    status = getattr(provider, "source_status", None)
    if status not in ADMITTED_RELEASE_STATUSES:
        raise M3Top3AdmissionError(
            "FEATURE_RELEASE_STATUS_UNVERIFIED",
            "partial or unverified feature releases are not scoreable",
            {"status": status},
            EXIT_BLOCKED,
        )
    path = getattr(provider, "path", None)
    try:
        live_hash = hash_file(Path(path)) if path is not None else sha256_hex(getattr(provider, "_rows", None))
    except OSError as exc:
        raise M3Top3AdmissionError(
            "FEATURE_RELEASE_HASH_MISMATCH",
            "feature release bytes are unavailable during live verification",
            {"cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    if not _is_sha256(getattr(provider, "source_hash", None)) or provider.source_hash != live_hash:
        raise M3Top3AdmissionError(
            "FEATURE_RELEASE_HASH_MISMATCH",
            "feature release hash differs from the live source",
            {"declared": getattr(provider, "source_hash", None), "actual": live_hash},
            EXIT_INTEGRITY,
        )
    return {
        "feature_source_version": provider.source_version,
        "feature_source_hash": provider.source_hash,
        "feature_source_status": provider.source_status,
    }


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            f"manifest is unreadable: {path}",
            {"path": str(path), "cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    if not isinstance(value, dict):
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            "manifest must be a JSON object",
            {"path": str(path)},
            EXIT_INTEGRITY,
        )
    return value


def _read_jsonl(path: Path) -> tuple[bytes, list[dict[str, Any]]]:
    try:
        payload = path.read_bytes()
        text = payload.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            f"JSONL input is unreadable: {path}",
            {"path": str(path), "cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                f"malformed JSONL at {path}:{line_number}",
                {"path": str(path), "line": line_number},
                EXIT_INTEGRITY,
            ) from exc
        if not isinstance(row, dict):
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                f"JSONL row must be an object at {path}:{line_number}",
                {"path": str(path), "line": line_number},
                EXIT_INTEGRITY,
            )
        rows.append(row)
    return payload, rows


def _retrieval_semantic_failure(message: str, details: dict[str, Any] | None = None) -> None:
    raise M3Top3AdmissionError(
        "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH",
        message,
        details,
        EXIT_INTEGRITY,
    )


def _verify_retrieval_audit_semantics(
    snapshot_dir: Path,
    manifest: dict[str, Any],
    pit_rows: list[dict[str, Any]],
    model_inputs: list[dict[str, Any]],
    retrieval_audits: list[dict[str, Any]],
    allow_staging: bool = False,
) -> None:
    """Revalidate retrieval receipts independently of declared hashes.

    Hash binding detects byte drift.  This check prevents a self-consistent
    rewrite of the audit bytes and every declared aggregate from turning an
    invalid receipt into an admissible snapshot.
    """

    expected_count = len(pit_rows)
    if len(model_inputs) != expected_count or len(retrieval_audits) != expected_count:
        _retrieval_semantic_failure(
            "READY snapshot requires exactly one PIT row, model input, and retrieval receipt per company slice",
            {
                "pit_rows": len(pit_rows),
                "model_inputs": len(model_inputs),
                "retrieval_audits": len(retrieval_audits),
            },
        )

    manifest_cutoff = manifest.get("snapshot_cutoff_at")
    manifest_date = manifest.get("snapshot_date")
    if not isinstance(manifest_cutoff, str) or not manifest_cutoff:
        _retrieval_semantic_failure("manifest snapshot_cutoff_at must be a non-empty string")
    if not isinstance(manifest_date, str) or not manifest_date:
        _retrieval_semantic_failure("manifest snapshot_date must be a non-empty string")
    try:
        parsed_date = date.fromisoformat(manifest_date)
        parsed_cutoff = datetime.fromisoformat(manifest_cutoff)
    except (TypeError, ValueError) as exc:
        _retrieval_semantic_failure("manifest snapshot date/cutoff is invalid", {"cause": type(exc).__name__})
    if parsed_cutoff.tzinfo is None or parsed_cutoff.utcoffset() is None:
        _retrieval_semantic_failure("manifest snapshot cutoff must be timezone-aware")
    if parsed_cutoff.date() != parsed_date:
        _retrieval_semantic_failure(
            "manifest snapshot date and cutoff calendar date differ",
            {"snapshot_date": manifest_date, "snapshot_cutoff_at": manifest_cutoff},
        )
    key_fields=("company_id","security_code_at_cutoff","snapshot_date","snapshot_cutoff_at","pit_snapshot_id","universe_release_id","universe_release_revision","denominator_release_id","denominator_release_revision","eligibility_record_id")

    def row_keys(rows: list[dict[str, Any]], artifact: str) -> set[tuple[Any,...]]:
        keys: list[tuple[Any,...]] = []
        for index, row in enumerate(rows):
            company_id = row.get("company_id")
            security_code = row.get("security_code_at_cutoff",row.get("security_code"))
            cutoff_at = row.get("snapshot_cutoff_at")
            snapshot_date = row.get("snapshot_date")
            pit_snapshot_id = row.get("pit_snapshot_id")
            if (
                not isinstance(company_id, str)
                or not company_id
                or not isinstance(security_code,str)
                or not security_code
                or not isinstance(cutoff_at, str)
                or cutoff_at != manifest_cutoff
                or snapshot_date != manifest_date
                or not isinstance(pit_snapshot_id, str)
                or not pit_snapshot_id
            ):
                _retrieval_semantic_failure(
                    f"{artifact} company/date/cutoff/PIT identity is invalid",
                    {
                        "artifact": artifact,
                        "row_index": index,
                        "company_id": company_id,
                        "snapshot_date": snapshot_date,
                        "cutoff_at": cutoff_at,
                        "pit_snapshot_id": pit_snapshot_id,
                    },
                )
            normalized={**row,"security_code_at_cutoff":security_code}
            key=tuple(normalized.get(field) for field in key_fields)
            if any(value is None or value=="" for value in key) or not isinstance(normalized.get("universe_release_revision"),int) or not isinstance(normalized.get("denominator_release_revision"),int):
                _retrieval_semantic_failure(f"{artifact} full Universe/release/eligibility key is incomplete",{"artifact":artifact,"row_index":index})
            keys.append(key)
        if len(set(keys)) != len(keys):
            _retrieval_semantic_failure(f"{artifact} contains a duplicate company/date/cutoff/PIT slice", {"artifact": artifact})
        return set(keys)

    pit_keys = row_keys(pit_rows, "pit_snapshot.jsonl")
    model_keys = row_keys(model_inputs, "model_input.jsonl")
    if pit_keys != model_keys:
        _retrieval_semantic_failure(
            "PIT and model-input company/date/cutoff/PIT identities differ",
            {"pit_keys": sorted(pit_keys), "model_keys": sorted(model_keys)},
        )

    # Dataset-reference classification precedes derived PIT-ID verification so
    # a self-consistent reference attack receives the normative REF code.
    top_refs={ref.get("domain"):ref for ref in manifest.get("lineage_releases",[]) if isinstance(ref,dict)}
    for rows,artifact in ((pit_rows,"pit_snapshot.jsonl"),(model_inputs,"model_input.jsonl")):
        for row in rows:
            refs=row.get("dataset_refs")
            if not isinstance(refs,list):
                raise M3Top3AdmissionError("DATASET_REF_DOMAIN_MISSING",f"{artifact} has no dataset refs",{"company_id":row.get("company_id")},EXIT_INTEGRITY)
            domains=[ref.get("domain") for ref in refs if isinstance(ref,dict)]
            if len(domains)!=len(refs) or len(domains)!=len(set(domains)):
                raise M3Top3AdmissionError("DUPLICATE_DATASET_REF_DOMAIN",f"{artifact} has duplicate/malformed dataset refs",{"company_id":row.get("company_id")},EXIT_INTEGRITY)
            missing=sorted(set(MODEL_INPUT_DATASET_DOMAINS)-set(domains)); extra=sorted(set(domains)-set(MODEL_INPUT_DATASET_DOMAINS))
            if missing: raise M3Top3AdmissionError("DATASET_REF_DOMAIN_MISSING",f"{artifact} lacks required dataset refs",{"company_id":row.get("company_id"),"missing":missing},EXIT_INTEGRITY)
            if extra: raise M3Top3AdmissionError("EXTRA_DATASET_REF",f"{artifact} has unregistered dataset refs",{"company_id":row.get("company_id"),"extra":extra},EXIT_INTEGRITY)
            for ref in refs:
                if top_refs.get(ref["domain"])!=ref:
                    raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH",f"{artifact} dataset ref differs from top-level lineage",{"company_id":row.get("company_id"),"domain":ref["domain"]},EXIT_INTEGRITY)

    pit_by_company: dict[tuple[str, str], dict[str, Any]] = {}
    model_by_company: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(pit_rows):
        identity_payload = {
            "company_id": row.get("company_id"),
            "snapshot_cutoff_at": row.get("snapshot_cutoff_at"),
            "snapshot_schema_version": row.get("snapshot_schema_version"),
            "snapshot_revision": row.get("snapshot_revision"),
            "f1_f2_effective_refs": row.get("f1_f2_effective_refs"),
            "f3_observation_refs": row.get("f3_observation_refs"),
            "evidence_refs": row.get("evidence_refs"),
            "dataset_refs": row.get("dataset_refs"),
            "universe_lineage_manifest_hash": row.get("universe_lineage_manifest_hash"),
            "universe_authority_status": row.get("universe_authority_status"),
            "universe_release_id": row.get("universe_release_id"),
            "universe_release_revision": row.get("universe_release_revision"),
            "universe_release_hash": row.get("universe_release_hash"),
            "universe_release_status": row.get("universe_release_status"),
            "denominator_release_id": row.get("denominator_release_id"),
            "denominator_release_revision": row.get("denominator_release_revision"),
            "denominator_release_hash": row.get("denominator_release_hash"),
            "denominator_release_status": row.get("denominator_release_status"),
            "denominator_member_id": row.get("denominator_member_id"),
            "eligibility_record_id": row.get("eligibility_record_id"),
            "eligibility_status": row.get("eligibility_status"),
            "tradability_state_ref": row.get("tradability_state_ref"),
            "retrieval_receipt_id": row.get("retrieval_receipt_id"),
            "retrieval_source_hash": row.get("retrieval_source_hash"),
        }
        if row.get("pit_snapshot_id") != deterministic_id("pit", identity_payload):
            _retrieval_semantic_failure("PIT snapshot ID is not deterministic for its semantic payload", {"row_index": index})
        generator_version = row.get("generator_version")
        if not isinstance(generator_version, str) or not generator_version:
            _retrieval_semantic_failure("PIT row generator_version must be a non-empty string", {"row_index": index})
        expected_capture = deterministic_id(
            "capture",
            {"pit_snapshot_id": row.get("pit_snapshot_id"), "generator_version": generator_version},
        )
        if row.get("capture_run_id") != expected_capture:
            _retrieval_semantic_failure("capture_run_id is not deterministic for PIT/generator identity", {"row_index": index})
        pit_by_company[(row["company_id"], row["snapshot_cutoff_at"])] = row
    for row in model_inputs:
        model_by_company[(row["company_id"], row["snapshot_cutoff_at"])] = row

    required = {
        "retrieval_receipt_id",
        "company_id",
        "cutoff_at",
        "source_version",
        "source_status",
        "source_hash",
        "source_matching_rows",
        "selected_rows",
        "excluded_rows",
        "exclusions",
        "cutoff_frozen_bundle",
    }
    bound_required={"security_code_at_cutoff","snapshot_date","snapshot_cutoff_at","pit_snapshot_id","universe_release_id","universe_release_revision","denominator_release_id","denominator_release_revision","eligibility_record_id","eligibility_status","entry_eligible"}
    audit_keys: list[tuple[Any,...]] = []
    audit_by_key: dict[tuple[Any,...], dict[str, Any]] = {}
    for index, receipt in enumerate(retrieval_audits):
        missing = sorted((required|bound_required) - set(receipt))
        if missing:
            _retrieval_semantic_failure("retrieval receipt is missing required fields", {"row_index": index, "missing": missing})
        company_id = receipt.get("company_id")
        cutoff_at = receipt.get("cutoff_at")
        source_version = receipt.get("source_version")
        source_hash = receipt.get("source_hash")
        receipt_id = receipt.get("retrieval_receipt_id")
        exclusions = receipt.get("exclusions")
        source_status = receipt.get("source_status")
        if not all(isinstance(value, str) and value for value in (company_id, cutoff_at, source_version, source_status, source_hash, receipt_id)):
            _retrieval_semantic_failure("retrieval receipt identity/source fields must be non-empty strings", {"row_index": index})
        if source_status not in ADMITTED_RELEASE_STATUSES:
            _retrieval_semantic_failure("retrieval receipt source status is partial or unverified", {"row_index": index, "status": source_status})
        if cutoff_at != manifest_cutoff:
            _retrieval_semantic_failure(
                "retrieval receipt cutoff differs from the snapshot cutoff",
                {"row_index": index, "receipt_cutoff": cutoff_at, "manifest_cutoff": manifest_cutoff},
            )
        if len(source_hash) != 64 or any(character not in "0123456789abcdef" for character in source_hash.lower()):
            _retrieval_semantic_failure("retrieval receipt source_hash must be a SHA256 hex digest", {"row_index": index})
        counts = [receipt.get(name) for name in ("source_matching_rows", "selected_rows", "excluded_rows")]
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts):
            _retrieval_semantic_failure("retrieval receipt counts must be non-negative integers", {"row_index": index, "counts": counts})
        source_matching_rows, selected_rows, excluded_rows = counts
        if source_matching_rows != selected_rows + excluded_rows:
            _retrieval_semantic_failure(
                "retrieval receipt counts do not reconcile",
                {
                    "row_index": index,
                    "source_matching_rows": source_matching_rows,
                    "selected_rows": selected_rows,
                    "excluded_rows": excluded_rows,
                },
            )
        if not isinstance(exclusions, list) or excluded_rows != len(exclusions):
            _retrieval_semantic_failure(
                "retrieval receipt excluded_rows differs from exclusions length",
                {"row_index": index, "excluded_rows": excluded_rows},
            )
        if not isinstance(receipt.get("cutoff_frozen_bundle"), bool):
            _retrieval_semantic_failure("retrieval receipt cutoff_frozen_bundle must be boolean", {"row_index": index})
        for exclusion_index, exclusion in enumerate(exclusions):
            if not isinstance(exclusion, dict) or not isinstance(exclusion.get("row_id"), str) or not exclusion.get("row_id"):
                _retrieval_semantic_failure("retrieval exclusion requires a non-empty row_id", {"row_index": index, "exclusion_index": exclusion_index})
            codes = exclusion.get("codes")
            if not isinstance(codes, list) or not codes or any(not isinstance(code, str) or not code for code in codes):
                _retrieval_semantic_failure("retrieval exclusion requires non-empty string codes", {"row_index": index, "exclusion_index": exclusion_index})
        payload = {key: receipt[key] for key in required if key != "retrieval_receipt_id"}
        if receipt_id != deterministic_id("retrieval", payload):
            _retrieval_semantic_failure("retrieval receipt ID is not deterministic for its payload", {"row_index": index})
        normalized={**receipt,"security_code_at_cutoff":receipt.get("security_code_at_cutoff")}
        audit_key=tuple(normalized.get(field) for field in key_fields)
        if any(value is None or value=="" for value in audit_key):
            _retrieval_semantic_failure("retrieval receipt full Universe/release/eligibility key is incomplete",{"row_index":index})
        audit_keys.append(audit_key)
        audit_by_key[audit_key] = receipt

    if len(set(audit_keys)) != len(audit_keys) or set(audit_keys) != pit_keys:
        _retrieval_semantic_failure(
            "retrieval receipt full keys are not one-to-one with PIT/model rows",
            {"receipt_keys": sorted(set(audit_keys)), "pit_keys": sorted(pit_keys)},
        )
    for key in sorted(pit_keys):
        company_id=key[0]; cutoff_at=key[3]
        pit_row = pit_by_company[(company_id,cutoff_at)]
        model_row = model_by_company[(company_id,cutoff_at)]
        receipt = audit_by_key[key]
        for row, artifact in ((pit_row, "pit_snapshot.jsonl"), (model_row, "model_input.jsonl")):
            if row.get("retrieval_receipt_id") != receipt["retrieval_receipt_id"] or row.get("retrieval_source_hash") != receipt["source_hash"]:
                _retrieval_semantic_failure(
                    f"{artifact} retrieval lineage differs from the audit receipt",
                    {"company_id": company_id},
                )
        if model_row.get("price_dataset_id") != manifest.get("price_dataset_id") or model_row.get("price_dataset_hash") != manifest.get("price_dataset_hash") or model_row.get("price_source_semantics") != manifest.get("price_source_semantics"):
            _retrieval_semantic_failure("model-input price lineage differs from manifest", {"company_id": company_id})
        if model_row.get("price_release_status") != manifest.get("price_release_status"):
            _retrieval_semantic_failure("model-input price release status differs from manifest", {"company_id": company_id})
        top_refs={ref.get("domain"):ref for ref in manifest.get("lineage_releases",[]) if isinstance(ref,dict)}
        for row,artifact in ((pit_row,"pit_snapshot.jsonl"),(model_row,"model_input.jsonl")):
            refs=row.get("dataset_refs")
            if not isinstance(refs,list):
                raise M3Top3AdmissionError("DATASET_REF_DOMAIN_MISSING",f"{artifact} has no dataset refs",{"company_id":key[0]},EXIT_INTEGRITY)
            domains=[ref.get("domain") for ref in refs if isinstance(ref,dict)]
            if len(domains)!=len(refs) or len(domains)!=len(set(domains)):
                raise M3Top3AdmissionError("DUPLICATE_DATASET_REF_DOMAIN",f"{artifact} has duplicate/malformed dataset refs",{"company_id":key[0]},EXIT_INTEGRITY)
            missing=sorted(set(MODEL_INPUT_DATASET_DOMAINS)-set(domains)); extra=sorted(set(domains)-set(MODEL_INPUT_DATASET_DOMAINS))
            if missing:
                raise M3Top3AdmissionError("DATASET_REF_DOMAIN_MISSING",f"{artifact} lacks required dataset refs",{"company_id":key[0],"missing":missing},EXIT_INTEGRITY)
            if extra:
                raise M3Top3AdmissionError("EXTRA_DATASET_REF",f"{artifact} has unregistered dataset refs",{"company_id":key[0],"extra":extra},EXIT_INTEGRITY)
            for ref in refs:
                expected=top_refs.get(ref["domain"])
                if expected is None or ref!=expected:
                    raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH",f"{artifact} dataset ref differs from top-level lineage",{"company_id":key[0],"domain":ref["domain"]},EXIT_INTEGRITY)
        if pit_row.get("generator_version") != manifest.get("generator_version"):
            _retrieval_semantic_failure("PIT generator version differs from manifest", {"company_id": key[0]})
        if pit_row.get("universe_release_id") != manifest.get("universe_release_id"):
            _retrieval_semantic_failure("PIT universe release differs from manifest", {"company_id": key[0]})
        if (
            pit_row.get("universe_lineage_manifest_hash") != manifest.get("universe_lineage_manifest_hash")
            or pit_row.get("universe_authority_status") != manifest.get("universe_authority_status")
            or pit_row.get("universe_release_hash") != manifest.get("universe_release_hash")
            or pit_row.get("universe_release_revision") != manifest.get("universe_release_revision")
            or pit_row.get("universe_release_status") != manifest.get("universe_release_status")
            or pit_row.get("denominator_release_id") != manifest.get("denominator_release_id")
            or pit_row.get("denominator_release_hash") != manifest.get("denominator_release_hash")
            or pit_row.get("denominator_release_revision") != manifest.get("denominator_release_revision")
            or pit_row.get("denominator_release_status") != manifest.get("denominator_release_status")
        ):
            _retrieval_semantic_failure("PIT universe/denominator lineage differs from manifest", {"company_id": key[0]})
        if (
            model_row.get("universe_lineage_manifest_hash") != manifest.get("universe_lineage_manifest_hash")
            or model_row.get("universe_authority_status") != manifest.get("universe_authority_status")
            or model_row.get("universe_release_id") != manifest.get("universe_release_id")
            or model_row.get("universe_release_revision") != manifest.get("universe_release_revision")
            or model_row.get("universe_release_hash") != manifest.get("universe_release_hash")
            or model_row.get("universe_release_status") != manifest.get("universe_release_status")
            or model_row.get("denominator_release_id") != manifest.get("denominator_release_id")
            or model_row.get("denominator_release_revision") != manifest.get("denominator_release_revision")
            or model_row.get("denominator_release_hash") != manifest.get("denominator_release_hash")
            or model_row.get("denominator_release_status") != manifest.get("denominator_release_status")
        ):
            _retrieval_semantic_failure("model-input universe/denominator lineage differs from manifest", {"company_id": key[0]})
        if receipt.get("source_version") != manifest.get("feature_source_version"):
            raise M3Top3AdmissionError("FEATURE_SOURCE_LINEAGE_MISMATCH","retrieval source version differs from FEATURE_SOURCE_RELEASE",{"company_id":key[0]},EXIT_INTEGRITY)
        if receipt.get("source_hash") != manifest.get("feature_source_hash") or receipt.get("source_status") != manifest.get("feature_source_status"):
            raise M3Top3AdmissionError("FEATURE_SOURCE_LINEAGE_MISMATCH","retrieval source hash/status differs from FEATURE_SOURCE_RELEASE",{"company_id":key[0]},EXIT_INTEGRITY)
        if (
            model_row.get("feature_source_version") != manifest.get("feature_source_version")
            or model_row.get("feature_source_hash") != manifest.get("feature_source_hash")
            or model_row.get("feature_source_status") != manifest.get("feature_source_status")
        ):
            raise M3Top3AdmissionError("FEATURE_SOURCE_LINEAGE_MISMATCH","model input feature lineage differs from FEATURE_SOURCE_RELEASE",{"company_id":key[0]},EXIT_INTEGRITY)
        if model_row.get("reconstruction_version") != manifest.get("reconstruction_version"):
            _retrieval_semantic_failure("model reconstruction version differs from manifest", {"company_id": key[0]})

    expected_receipt_ids = sorted(receipt["retrieval_receipt_id"] for receipt in retrieval_audits)
    expected_source_hashes = sorted({receipt["source_hash"] for receipt in retrieval_audits})
    if manifest.get("retrieval_receipt_ids") != expected_receipt_ids or manifest.get("retrieval_source_hashes") != expected_source_hashes:
        _retrieval_semantic_failure("manifest retrieval lineage does not match audit rows")


def _snapshot_manifest_identity_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "snapshot_date",
        "snapshot_cutoff_at",
        "snapshot_revision",
        "snapshot_content_hash",
        "snapshot_status",
        "blockers",
        "pit_row_count",
        "model_input_row_count",
        "retrieval_audit_row_count",
        "pit_file_sha256",
        "model_input_file_sha256",
        "retrieval_audit_file_sha256",
        "retrieval_audit_content_hash",
        "retrieval_receipt_ids",
        "retrieval_source_hashes",
        "generator_version",
        "universe_lineage_manifest_kind",
        "universe_lineage_manifest_hash",
        "universe_expectation_manifest_hash",
        "denominator_expectation_manifest_hash",
        "universe_release_id",
        "universe_release_revision",
        "universe_release_hash",
        "universe_release_status",
        "universe_authority_status",
        "universe_release_state_hash",
        "universe_release_logical_locator",
        "universe_release_partition",
        "denominator_release_id",
        "denominator_release_revision",
        "denominator_release_hash",
        "denominator_release_status",
        "denominator_state_hash",
        "denominator_logical_locator",
        "denominator_partition",
        "denominator_member_ids",
        "denominator_identity_hash",
        "universe_member_set_digest",
        "denominator_row_count",
        "eligible_member_ids",
        "eligible_identity_hash",
        "eligible_row_count",
        "ineligible_member_ids",
        "ineligible_identity_hash",
        "ineligible_row_count",
        "eligible_record_ids",
        "eligible_set_digest",
        "ineligible_record_ids",
        "ineligible_set_digest",
        "denominator_partition_digest",
        "execution_lineage_bundle_hash",
        "execution_lineage_identity_hash",
        "lineage_bundle_synthetic_only",
        "lineage_releases",
        "feature_source_version",
        "feature_source_hash",
        "feature_source_status",
        "price_dataset_id",
        "price_dataset_hash",
        "price_source_semantics",
        "price_release_status",
        "reconstruction_version",
    )
    return {field: manifest.get(field) for field in fields}


def _verify_full_universe_coverage(
    manifest: dict[str, Any],
    pit_rows: list[dict[str, Any]],
    model_inputs: list[dict[str, Any]],
    retrieval_audits: list[dict[str,Any]]|None=None,
) -> None:
    lineage_kind = manifest.get("universe_lineage_manifest_kind")
    if lineage_kind not in {"EXACT_EXTERNAL_MANIFEST", "SYNTHETIC_IN_MEMORY_DIAGNOSTIC"}:
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
            "READY snapshot has no admitted lineage-manifest class",
            {"kind": lineage_kind},
            EXIT_INTEGRITY,
        )
    if lineage_kind == "SYNTHETIC_IN_MEMORY_DIAGNOSTIC" and manifest.get("universe_authority_status") != "DIAGNOSTIC":
        raise M3Top3AdmissionError(
            "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
            "synthetic lineage cannot be promoted beyond DIAGNOSTIC authority",
            {"authority_status": manifest.get("universe_authority_status")},
            EXIT_AUTHORITY,
        )
    if lineage_kind=="EXACT_EXTERNAL_MANIFEST":
        for field in ("universe_lineage_manifest_locator","universe_expectation_manifest_locator","denominator_expectation_manifest_locator","universe_expectation_manifest_hash","denominator_expectation_manifest_hash"):
            if not isinstance(manifest.get(field),str) or not manifest[field]:
                raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external snapshot omits independent U/D expectation binding",{"field":field},EXIT_AUTHORITY)
        if not _is_sha256(manifest["universe_expectation_manifest_hash"]) or not _is_sha256(manifest["denominator_expectation_manifest_hash"]):
            raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external U/D expectation hashes are malformed",exit_code=EXIT_AUTHORITY)
    for field in (
        "universe_release_id",
        "universe_lineage_manifest_kind",
        "universe_lineage_manifest_hash",
        "universe_release_hash",
        "universe_release_status",
        "universe_authority_status",
        "denominator_release_id",
        "denominator_release_hash",
        "denominator_release_status",
        "denominator_identity_hash",
        "universe_member_set_digest",
        "eligible_identity_hash",
        "feature_source_version",
        "feature_source_hash",
        "feature_source_status",
        "price_dataset_id",
        "price_dataset_hash",
        "price_release_status",
        "universe_release_logical_locator",
        "universe_release_partition",
        "denominator_logical_locator",
        "denominator_partition",
    ):
        if not isinstance(manifest.get(field), str) or not manifest[field]:
            raise M3Top3AdmissionError(
                "SNAPSHOT_LINEAGE_INCOMPLETE",
                "READY snapshot manifest has incomplete dataset/release lineage",
                {"field": field},
                EXIT_INTEGRITY,
            )
    for field in ("universe_release_revision","denominator_release_revision","snapshot_revision"):
        if not isinstance(manifest.get(field),int) or isinstance(manifest.get(field),bool) or manifest[field]<0:
            raise M3Top3AdmissionError("SNAPSHOT_REVISION_MISMATCH","snapshot/release revision is missing or invalid",{"field":field},EXIT_INTEGRITY)
    for field in ("universe_lineage_manifest_hash", "universe_release_hash", "denominator_release_hash", "feature_source_hash", "price_dataset_hash"):
        if not _is_sha256(manifest.get(field)):
            raise M3Top3AdmissionError(
                "SNAPSHOT_LINEAGE_INCOMPLETE",
                "READY snapshot manifest contains a non-SHA256 release identity",
                {"field": field},
                EXIT_INTEGRITY,
            )
    for field in ("universe_release_status", "denominator_release_status", "feature_source_status", "price_release_status"):
        if manifest.get(field) not in ADMITTED_RELEASE_STATUSES:
            raise M3Top3AdmissionError(
                "SNAPSHOT_RELEASE_STATUS_UNVERIFIED",
                "READY snapshot references a partial or unverified release",
                {"field": field, "status": manifest.get(field)},
                EXIT_BLOCKED,
            )
    denominator_member_ids = manifest.get("denominator_member_ids")
    eligible_member_ids = manifest.get("eligible_member_ids")
    ineligible_member_ids = manifest.get("ineligible_member_ids")
    if (
        not isinstance(denominator_member_ids, list)
        or any(not isinstance(item, str) or not item for item in denominator_member_ids)
        or len(set(denominator_member_ids)) != len(denominator_member_ids)
        or denominator_member_ids != sorted(denominator_member_ids)
        or not isinstance(eligible_member_ids, list)
        or any(not isinstance(item, str) or not item for item in eligible_member_ids)
        or len(set(eligible_member_ids)) != len(eligible_member_ids)
        or eligible_member_ids != sorted(eligible_member_ids)
        or not set(eligible_member_ids).issubset(denominator_member_ids)
        or not isinstance(ineligible_member_ids,list)
        or ineligible_member_ids!=sorted(ineligible_member_ids)
        or len(set(ineligible_member_ids))!=len(ineligible_member_ids)
        or set(eligible_member_ids)&set(ineligible_member_ids)
        or set(eligible_member_ids)|set(ineligible_member_ids)!=set(denominator_member_ids)
    ):
        raise M3Top3AdmissionError("DENOMINATOR_COUNT_MISMATCH","manifest U/E/I identity lists are malformed or do not partition U",exit_code=EXIT_INTEGRITY)
    if manifest.get("denominator_row_count")!=len(denominator_member_ids) or manifest.get("eligible_row_count")!=len(eligible_member_ids) or manifest.get("ineligible_row_count")!=len(ineligible_member_ids):
        raise M3Top3AdmissionError("DENOMINATOR_COUNT_MISMATCH","manifest U/E/I counts do not reconcile",exit_code=EXIT_INTEGRITY)
    if manifest.get("denominator_identity_hash")!=aggregate_hash(denominator_member_ids):
        raise M3Top3AdmissionError("UNIVERSE_SET_DIGEST_MISMATCH","manifest Universe member-set digest differs after recomputation",exit_code=EXIT_INTEGRITY)
    if manifest.get("eligible_identity_hash")!=aggregate_hash(eligible_member_ids) or manifest.get("ineligible_identity_hash")!=aggregate_hash(ineligible_member_ids):
        raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","manifest eligible/ineligible member-set digest differs after recomputation",exit_code=EXIT_INTEGRITY)
    pit_member_ids: list[str] = []
    model_member_ids: list[str] = []
    actual_eligible_ids: list[str] = []
    for index, (pit_row, model_row) in enumerate(zip(pit_rows, model_inputs)):
        if pit_row.get("snapshot_date")!=manifest.get("snapshot_date") or model_row.get("snapshot_date")!=manifest.get("snapshot_date") or pit_row.get("snapshot_cutoff_at")!=manifest.get("snapshot_cutoff_at") or model_row.get("snapshot_cutoff_at")!=manifest.get("snapshot_cutoff_at"):
            raise M3Top3AdmissionError("SNAPSHOT_DATE_LINEAGE_MISMATCH","PIT/model date or cutoff differs from snapshot manifest",{"row_index":index},EXIT_INTEGRITY)
        if pit_row.get("snapshot_revision")!=manifest.get("snapshot_revision") or model_row.get("snapshot_revision",0)!=manifest.get("snapshot_revision"):
            raise M3Top3AdmissionError("SNAPSHOT_REVISION_MISMATCH","PIT/model snapshot revision differs from manifest",{"row_index":index},EXIT_INTEGRITY)
        pit_member_id = pit_row.get("denominator_member_id")
        model_member_id = model_row.get("denominator_member_id")
        member_payload = {
            "company_id": model_row.get("company_id"),
            "security_code": model_row.get("security_code"),
            "valid_from": model_row.get("universe_valid_from"),
            "valid_to": model_row.get("universe_valid_to"),
            "universe_record_id": model_row.get("universe_record_id"),
        }
        expected_member_id = deterministic_id("universe_member", member_payload)
        if pit_member_id != model_member_id or model_member_id != expected_member_id:
            raise M3Top3AdmissionError("SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE","PIT/model Universe member identity is missing or inconsistent",{"row_index":index},EXIT_INTEGRITY)
        pit_member_ids.append(pit_member_id)
        model_member_ids.append(model_member_id)
        eligibility = model_row.get("entry_eligible")
        if eligibility not in {"TRUE", "FALSE"}:
            raise M3Top3AdmissionError(
                "SNAPSHOT_RELEASE_STATUS_UNVERIFIED",
                "READY snapshot contains unresolved eligibility",
                {"row_index": index, "eligibility": eligibility},
                EXIT_BLOCKED,
            )
        if eligibility == "TRUE":
            actual_eligible_ids.append(model_member_id)
            expected_status="ELIGIBLE"
        else:
            expected_status="INELIGIBLE"
        if pit_row.get("eligibility_record_id")!=model_row.get("eligibility_record_id") or pit_row.get("eligibility_status")!=expected_status or model_row.get("eligibility_status")!=expected_status:
            raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","snapshot eligibility record/status differs across PIT/model partition",{"row_index":index},EXIT_INTEGRITY)
    if len(pit_rows)!=len(model_inputs) or len(set(pit_member_ids))!=len(pit_member_ids) or len(set(model_member_ids))!=len(model_member_ids):
        raise M3Top3AdmissionError("DUPLICATE_SCOREABLE_SNAPSHOT_KEY","PIT/model snapshot keys are duplicate or not one-to-one",exit_code=EXIT_INTEGRITY)
    actual_members=set(pit_member_ids)|set(model_member_ids); expected_members=set(denominator_member_ids)
    missing=sorted(expected_members-actual_members); extra=sorted(actual_members-expected_members)
    if missing:
        code="TERMINAL_INELIGIBLE_IDENTITY_MISSING" if set(missing).issubset(ineligible_member_ids) else "SNAPSHOT_UNIVERSE_MEMBER_MISSING"
        raise M3Top3AdmissionError(code,"snapshot PIT/model sets omit applicable Universe members",{"missing":missing},EXIT_INTEGRITY)
    if extra:
        raise M3Top3AdmissionError("SNAPSHOT_UNIVERSE_MEMBER_EXTRA","snapshot PIT/model sets contain outside-Universe members",{"extra":extra},EXIT_INTEGRITY)
    if sorted(pit_member_ids)!=denominator_member_ids or sorted(model_member_ids)!=denominator_member_ids:
        raise M3Top3AdmissionError("SNAPSHOT_UNIVERSE_MEMBER_MISSING","PIT/model Universe sets do not reconcile",exit_code=EXIT_INTEGRITY)
    if sorted(actual_eligible_ids)!=eligible_member_ids:
        raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","snapshot eligible set differs from denominator E",exit_code=EXIT_INTEGRITY)
    if retrieval_audits is not None:
        expected_companies=sorted(row.get("company_id") for row in model_inputs)
        audit_companies=[row.get("company_id") for row in retrieval_audits]
        if len(audit_companies)!=len(set(audit_companies)):
            raise M3Top3AdmissionError("DUPLICATE_SCOREABLE_SNAPSHOT_KEY","retrieval audit contains duplicate company/cutoff slice",exit_code=EXIT_INTEGRITY)
        if sorted(audit_companies)!=expected_companies:
            missing_companies=sorted(set(expected_companies)-set(audit_companies)); extra_companies=sorted(set(audit_companies)-set(expected_companies))
            code="SNAPSHOT_UNIVERSE_MEMBER_MISSING" if missing_companies else "SNAPSHOT_UNIVERSE_MEMBER_EXTRA"
            raise M3Top3AdmissionError(code,"retrieval audit set differs from full applicable Universe",{"missing":missing_companies,"extra":extra_companies},EXIT_INTEGRITY)
    eligible_record_ids=sorted(row["eligibility_record_id"] for row in model_inputs if row.get("entry_eligible")=="TRUE")
    ineligible_record_ids=sorted(row["eligibility_record_id"] for row in model_inputs if row.get("entry_eligible")=="FALSE")
    canonical_u=universe_member_set_digest(model_inputs)
    decision_rows=[{"company_id":row.get("company_id"),"security_code":row.get("security_code"),"eligibility_record_id":row.get("eligibility_record_id"),"eligibility_status":row.get("eligibility_status")} for row in model_inputs]
    canonical_e=eligibility_set_digest(decision_rows,"ELIGIBLE"); canonical_i=eligibility_set_digest(decision_rows,"INELIGIBLE")
    if manifest.get("universe_member_set_digest")!=canonical_u:
        raise M3Top3AdmissionError("UNIVERSE_SET_DIGEST_MISMATCH","snapshot canonical company/security Universe digest differs after recomputation",exit_code=EXIT_INTEGRITY)
    partition_digest=sha256_hex({"universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,"universe_count":len(denominator_member_ids),"eligible_count":len(eligible_member_ids),"ineligible_count":len(ineligible_member_ids)})
    if manifest.get("eligible_record_ids")!=eligible_record_ids or manifest.get("ineligible_record_ids")!=ineligible_record_ids or manifest.get("eligible_set_digest")!=canonical_e or manifest.get("ineligible_set_digest")!=canonical_i or manifest.get("denominator_partition_digest")!=partition_digest:
        raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","eligibility partition record sets/digests do not reconcile",exit_code=EXIT_INTEGRITY)


def _verify_external_snapshot_expectation(
    manifest:dict[str,Any],
    admitted:dict[str,Any],
    pit_rows:list[dict[str,Any]],
    model_inputs:list[dict[str,Any]],
    retrieval_audits:list[dict[str,Any]],
)->None:
    """Rebind a stored snapshot to live external U/denominator expectations.

    Snapshot-internal lists and hashes are never allowed to certify their own
    membership.  This verifier reopens the separately supplied expectation
    manifests and the exact U/D artifacts that the execution bundle admitted.
    """

    locator=manifest.get("universe_lineage_manifest_locator")
    expected_hash=manifest.get("universe_lineage_manifest_hash")
    if not isinstance(locator,str) or not locator or not _is_sha256(expected_hash):
        raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external snapshot lacks an exact independent lineage-manifest locator/hash",exit_code=EXIT_AUTHORITY)
    payload,lineage_manifest=_read_exact_json_object(Path(locator).resolve(),"UNIVERSE_LINEAGE_MANIFEST_MISMATCH")
    if sha256_hex(payload)!=expected_hash or lineage_manifest.get("authority_status")!="DIAGNOSTIC":
        raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH","external snapshot lineage manifest differs from exact diagnostic binding",exit_code=EXIT_INTEGRITY)
    release_map={release["domain"]:release for release in admitted.get("releases",[])}
    u_release=release_map.get("UNIVERSE_RELEASE"); d_release=release_map.get("DENOMINATOR_ELIGIBILITY_RELEASE")
    u_binding=lineage_manifest.get("release"); d_binding=lineage_manifest.get("denominator")
    if not all(isinstance(value,dict) for value in (u_release,d_release,u_binding,d_binding)):
        raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external U/D release bindings are incomplete",exit_code=EXIT_AUTHORITY)
    for prefix,binding,release in (("universe",u_binding,u_release),("denominator",d_binding,d_release)):
        if binding.get("release_id")!=release.get("release_id") or binding.get("release_version")!=release.get("release_version") or binding.get("release_revision")!=release.get("release_revision") or binding.get("source_sha256")!=release.get("artifact_sha256"):
            raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH",f"{prefix} expectation release tuple differs from execution lineage",exit_code=EXIT_INTEGRITY)
        manifest_locator=manifest.get(f"{prefix}_expectation_manifest_locator")
        manifest_hash=manifest.get(f"{prefix}_expectation_manifest_hash")
        if manifest_locator!=binding.get("expectation_manifest_path") or manifest_hash!=binding.get("expectation_manifest_sha256") or not _is_sha256(manifest_hash):
            raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",f"{prefix} independent expectation reference is absent or substituted",exit_code=EXIT_AUTHORITY)
    required_external_components=(
        (u_release,"UNIVERSE_LINEAGE_MANIFEST",locator,expected_hash),
        (u_release,"UNIVERSE_EXPECTATION_MANIFEST",manifest["universe_expectation_manifest_locator"],manifest["universe_expectation_manifest_hash"]),
        (d_release,"DENOMINATOR_EXPECTATION_MANIFEST",manifest["denominator_expectation_manifest_locator"],manifest["denominator_expectation_manifest_hash"]),
    )
    for release,semantic_role,component_locator,component_hash in required_external_components:
        matches=[
            component for component in release.get("components",[])
            if component.get("semantic_role")==semantic_role
            and Path(component.get("path","")).resolve()==Path(component_locator).resolve()
            and component.get("artifact_sha256")==component_hash
        ]
        if len(matches)!=1:
            raise M3Top3AdmissionError(
                "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
                "external U/denominator expectation anchor is not an exact registered release component",
                {"domain":release.get("domain"),"semantic_role":semantic_role},
                EXIT_AUTHORITY,
            )
    # Reconstruct the production JSONL provider from exact bundle artifacts and
    # independently hashed manifests.  This reuses the same strict row-schema
    # parser as snapshot creation rather than trusting snapshot projections.
    from .providers import JsonlUniverseProvider
    provider=JsonlUniverseProvider(
        u_release["artifact_path"],u_release["release_id"],"DIAGNOSTIC",
        release_hash=u_release["artifact_sha256"],release_status=u_binding.get("status"),
        denominator_path=d_release["artifact_path"],denominator_release_id=d_release["release_id"],
        denominator_release_hash=d_release["artifact_sha256"],denominator_status=d_binding.get("status"),
        lineage_manifest_path=locator,lineage_manifest_hash=expected_hash,
        universe_expectation_manifest_path=manifest.get("universe_expectation_manifest_locator"),
        universe_expectation_manifest_hash=manifest.get("universe_expectation_manifest_hash"),
        denominator_expectation_manifest_path=manifest.get("denominator_expectation_manifest_locator"),
        denominator_expectation_manifest_hash=manifest.get("denominator_expectation_manifest_hash"),
    )
    try:
        parsed_snapshot_date=date.fromisoformat(manifest.get("snapshot_date"))
    except (TypeError,ValueError) as exc:
        raise M3Top3AdmissionError("SNAPSHOT_DATE_LINEAGE_MISMATCH","snapshot date is invalid",exit_code=EXIT_INTEGRITY) from exc
    live=verify_universe_release(provider,parsed_snapshot_date,provider.states_at(parsed_snapshot_date))
    if u_release.get("release_version")!=provider.release_version or u_release.get("release_revision")!=provider.release_revision or d_release.get("release_version")!=provider.denominator_release_version or d_release.get("release_revision")!=provider.denominator_release_revision:
        raise M3Top3AdmissionError("RELEASE_REVISION_MISMATCH","execution lineage and independent U/D manifests have different versions/revisions",exit_code=EXIT_INTEGRITY)
    live_fields=("universe_release_id","universe_release_revision","universe_release_hash","denominator_release_id","denominator_release_revision","denominator_release_hash","universe_member_set_digest","eligible_set_digest","ineligible_set_digest","denominator_partition_digest","denominator_row_count","eligible_row_count","ineligible_row_count","denominator_member_ids","eligible_member_ids","ineligible_member_ids","eligible_record_ids","ineligible_record_ids")
    if any(manifest.get(field)!=live.get(field) for field in live_fields):
        expected_companies={state.company_id for state in provider.states_at(parsed_snapshot_date)}; actual_companies={row.get("company_id") for row in model_inputs}
        missing=sorted(expected_companies-actual_companies)
        ineligible_companies={state.company_id for state in provider.states_at(parsed_snapshot_date) if live["eligibility_records"][universe_member_identity(state)]["eligibility_status"]=="INELIGIBLE"}
        code="TERMINAL_INELIGIBLE_IDENTITY_MISSING" if missing and set(missing).issubset(ineligible_companies) else "SNAPSHOT_UNIVERSE_MEMBER_MISSING" if missing else "UNIVERSE_SET_DIGEST_MISMATCH"
        raise M3Top3AdmissionError(code,"snapshot U/E/I declarations differ from live independently admitted U/D releases",{"missing_companies":missing},EXIT_INTEGRITY)
    states_by_key={(state.company_id,str(state.security_code).zfill(6)):state for state in provider.states_at(parsed_snapshot_date)}
    for pit_row,model_row,audit_row in zip(pit_rows,model_inputs,retrieval_audits):
        key=(model_row.get("company_id"),str(model_row.get("security_code","")).zfill(6)); state=states_by_key.get(key)
        if state is None:
            raise M3Top3AdmissionError("SNAPSHOT_UNIVERSE_MEMBER_EXTRA","snapshot contains a member outside external Universe release",{"key":key},EXIT_INTEGRITY)
        member_id=universe_member_identity(state); decision=live["eligibility_records"][member_id]; expected_entry="TRUE" if decision["eligibility_status"]=="ELIGIBLE" else "FALSE"
        if model_row.get("universe_record_id")!=state.universe_record_id or pit_row.get("tradability_state_ref")!={"domain":"TRADABILITY_HISTORY","ref_id":state.universe_record_id} or pit_row.get("denominator_member_id")!=member_id or model_row.get("denominator_member_id")!=member_id or any(row.get("eligibility_record_id")!=decision["eligibility_record_id"] or row.get("eligibility_status")!=decision["eligibility_status"] for row in (pit_row,model_row)) or model_row.get("entry_eligible")!=expected_entry:
            raise M3Top3AdmissionError("SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE","snapshot PIT/model/audit row identity differs from external U/denominator record",{"key":key},EXIT_INTEGRITY)
        if audit_row.get("pit_snapshot_id")!=model_row.get("pit_snapshot_id") or audit_row.get("security_code_at_cutoff")!=key[1] or audit_row.get("eligibility_record_id")!=decision["eligibility_record_id"] or audit_row.get("eligibility_status")!=decision["eligibility_status"] or audit_row.get("entry_eligible")!=expected_entry:
            _retrieval_semantic_failure("retrieval audit row identity differs from external U/denominator record",{"key":key})
    _,u_expectation=_read_exact_json_object(Path(manifest["universe_expectation_manifest_locator"]).resolve(),"UNIVERSE_LINEAGE_MANIFEST_MISMATCH")
    _,d_expectation=_read_exact_json_object(Path(manifest["denominator_expectation_manifest_locator"]).resolve(),"UNIVERSE_LINEAGE_MANIFEST_MISMATCH")
    if hash_file(Path(manifest["universe_expectation_manifest_locator"]))!=manifest["universe_expectation_manifest_hash"] or hash_file(Path(manifest["denominator_expectation_manifest_locator"]))!=manifest["denominator_expectation_manifest_hash"]:
        raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH","independent U/D expectation bytes drifted",exit_code=EXIT_INTEGRITY)
    if u_expectation.get("binding_mode")!="EXTERNALLY_SUPPLIED_INDEPENDENT_BINDING" or d_expectation.get("binding_mode")!="EXTERNALLY_SUPPLIED_INDEPENDENT_BINDING" or u_expectation.get("expectation_source_id")==d_expectation.get("expectation_source_id") or u_expectation.get("authority_or_evidence_receipt_ref")==d_expectation.get("authority_or_evidence_receipt_ref"):
        raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","U/D expectations are not distinct external trust bindings",exit_code=EXIT_AUTHORITY)

    _,universe_rows=_read_jsonl(Path(u_release["artifact_path"]))
    _,denominator_rows=_read_jsonl(Path(d_release["artifact_path"]))
    snapshot_date=manifest.get("snapshot_date"); cutoff=manifest.get("snapshot_cutoff_at")
    try:
        parsed_date=date.fromisoformat(snapshot_date)
    except (TypeError,ValueError) as exc:
        raise M3Top3AdmissionError("SNAPSHOT_DATE_LINEAGE_MISMATCH","snapshot date is invalid",exit_code=EXIT_INTEGRITY) from exc
    applicable=[]
    for row in universe_rows:
        try:
            valid_from=date.fromisoformat(row["valid_from"]) if row.get("valid_from") else None
            valid_to=date.fromisoformat(row["valid_to"]) if row.get("valid_to") else None
        except (TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY","external Universe interval is invalid",exit_code=EXIT_INTEGRITY) from exc
        if (valid_from is None or valid_from<=parsed_date) and (valid_to is None or parsed_date<valid_to): applicable.append(row)
    decisions=[row for row in denominator_rows if row.get("snapshot_date")==snapshot_date]
    u_keys=[(row.get("company_id"),str(row.get("security_code","")).zfill(6)) for row in applicable]
    d_keys=[(row.get("company_id"),str(row.get("security_code","")).zfill(6)) for row in decisions]
    if len(u_keys)!=len(set(u_keys)) or len(d_keys)!=len(set(d_keys)):
        raise M3Top3AdmissionError("DUPLICATE_UNIVERSE_IDENTITY","external U/D expectation contains duplicate active company/security identity",exit_code=EXIT_INTEGRITY)
    missing_d=sorted(set(u_keys)-set(d_keys)); extra_d=sorted(set(d_keys)-set(u_keys))
    if missing_d: raise M3Top3AdmissionError("DENOMINATOR_MEMBER_MISSING","external denominator omits applicable Universe members",{"missing":missing_d},EXIT_INTEGRITY)
    if extra_d: raise M3Top3AdmissionError("DENOMINATOR_MEMBER_EXTRA","external denominator contains outside-Universe members",{"extra":extra_d},EXIT_INTEGRITY)
    if any(row.get("eligibility_status") not in {"ELIGIBLE","INELIGIBLE"} for row in decisions):
        raise M3Top3AdmissionError("ELIGIBILITY_RELEASE_NOT_COMPLETE","external denominator contains nonterminal eligibility",exit_code=EXIT_BLOCKED)
    if any(row.get("snapshot_cutoff_at")!=cutoff or row.get("universe_release_id")!=u_release["release_id"] or row.get("universe_release_revision")!=u_release["release_revision"] or row.get("denominator_release_id")!=d_release["release_id"] or row.get("denominator_release_revision")!=d_release["release_revision"] for row in decisions):
        raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","external denominator date/cutoff/release tuple differs from snapshot",exit_code=EXIT_INTEGRITY)
    canonical_u=universe_member_set_digest(applicable); canonical_e=eligibility_set_digest(decisions,"ELIGIBLE"); canonical_i=eligibility_set_digest(decisions,"INELIGIBLE")
    e_count=sum(row.get("eligibility_status")=="ELIGIBLE" for row in decisions); i_count=len(decisions)-e_count
    partition=sha256_hex({"universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,"universe_count":len(applicable),"eligible_count":e_count,"ineligible_count":i_count})
    u_slices={row.get("snapshot_date"):row for row in u_expectation.get("slices",[]) if isinstance(row,dict)}; d_slices={row.get("snapshot_date"):row for row in d_expectation.get("slices",[]) if isinstance(row,dict)}
    u_expected={"snapshot_date":snapshot_date,"snapshot_cutoff_at":cutoff,"universe_count":len(applicable),"universe_member_set_digest":canonical_u}
    d_expected={"snapshot_date":snapshot_date,"snapshot_cutoff_at":cutoff,"universe_count":len(applicable),"eligible_count":e_count,"ineligible_count":i_count,"universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,"denominator_partition_digest":partition}
    if {key:(u_slices.get(snapshot_date) or {}).get(key) for key in u_expected}!=u_expected:
        raise M3Top3AdmissionError("UNIVERSE_SET_DIGEST_MISMATCH","external Universe expectation does not match live applicable bytes",exit_code=EXIT_INTEGRITY)
    if {key:(d_slices.get(snapshot_date) or {}).get(key) for key in d_expected}!=d_expected:
        raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","external denominator expectation does not match live E/I bytes",exit_code=EXIT_INTEGRITY)
    snapshot_expected={"universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,"denominator_partition_digest":partition,"denominator_row_count":len(applicable),"eligible_row_count":e_count,"ineligible_row_count":i_count}
    if any(manifest.get(key)!=value for key,value in snapshot_expected.items()):
        snapshot_keys={(row.get("company_id"),str(row.get("security_code","")).zfill(6)) for row in model_inputs}
        missing=sorted(set(u_keys)-snapshot_keys); missing_i=sorted(key for key in missing if next((row.get("eligibility_status") for row in decisions if (row.get("company_id"),str(row.get("security_code","")).zfill(6))==key),None)=="INELIGIBLE")
        code="TERMINAL_INELIGIBLE_IDENTITY_MISSING" if missing and missing==missing_i else "SNAPSHOT_UNIVERSE_MEMBER_MISSING" if missing else "UNIVERSE_SET_DIGEST_MISMATCH"
        raise M3Top3AdmissionError(code,"snapshot self-declared sets/counts differ from live external U/D expectations",{"missing":missing},EXIT_INTEGRITY)


def verify_snapshot_artifacts(snapshot_dir: str | Path, *, allow_staging: bool = False) -> VerifiedSnapshot:
    """Verify state, actual bytes, row counts, and semantic aggregate.

    Verification occurs before a scorer or output path may be touched.
    """

    snapshot_dir = Path(snapshot_dir)
    manifest = _read_manifest(snapshot_dir / "manifest.json")
    expected_manifest_identity = sha256_hex(_snapshot_manifest_identity_payload(manifest))
    if manifest.get("snapshot_manifest_identity_hash") != expected_manifest_identity:
        raise M3Top3AdmissionError(
            "SNAPSHOT_MANIFEST_IDENTITY_MISMATCH",
            "manifest control identity differs from its declared hash",
            {"expected": expected_manifest_identity, "declared": manifest.get("snapshot_manifest_identity_hash")},
            EXIT_INTEGRITY,
        )
    status = manifest.get("snapshot_status")
    blockers = manifest.get("blockers")
    if not isinstance(blockers, list):
        raise M3Top3AdmissionError(
            "BLOCKED_MANIFEST_STATE_CONTRADICTION_OR_BLOCKED_SNAPSHOT_NOT_READY",
            "manifest blockers must be a list",
            {"snapshot_status": status},
            EXIT_BLOCKED,
        )
    if status == "SNAPSHOT_READY" and blockers:
        raise M3Top3AdmissionError(
            "BLOCKED_MANIFEST_STATE_CONTRADICTION_OR_BLOCKED_SNAPSHOT_NOT_READY",
            "READY snapshot has non-empty blockers",
            {"blockers": blockers},
            EXIT_BLOCKED,
        )
    if status != "SNAPSHOT_READY":
        raise M3Top3AdmissionError(
            "BLOCKED_MANIFEST_STATE_CONTRADICTION_OR_BLOCKED_SNAPSHOT_NOT_READY",
            f"snapshot status is {status!r}",
            {"snapshot_status": status, "blockers": blockers},
            EXIT_BLOCKED,
        )

    bundle_hash=manifest.get("execution_lineage_bundle_hash")
    releases=manifest.get("lineage_releases")
    if not _is_sha256(bundle_hash) or not _is_sha256(manifest.get("execution_lineage_identity_hash")) or not isinstance(releases,list) or len(releases)!=len(REQUIRED_LINEAGE_DOMAINS):
        raise M3Top3AdmissionError("SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE","snapshot manifest does not bind the complete execution-lineage bundle",exit_code=EXIT_INTEGRITY)
    external_admitted=None
    if manifest.get("lineage_bundle_synthetic_only") is True:
        domains=[release.get("domain") for release in releases if isinstance(release,dict)]
        if set(domains)!=set(REQUIRED_LINEAGE_DOMAINS) or len(domains)!=len(set(domains)) or any(release.get("state")!=DIAGNOSTIC_LINEAGE_STATE for release in releases):
            raise M3Top3AdmissionError("SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE","synthetic fixture lineage is incomplete or non-diagnostic",exit_code=EXIT_INTEGRITY)
        if manifest.get("execution_lineage_identity_hash")!=sha256_hex(sorted(releases,key=lambda row:row["domain"])):
            raise M3Top3AdmissionError("SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE","synthetic fixture lineage identity does not reconcile",exit_code=EXIT_INTEGRITY)
    else:
        locator=manifest.get("execution_lineage_bundle_locator")
        admitted=admit_execution_lineage_bundle(locator,bundle_hash)
        external_admitted=admitted
        if admitted["lineage_identity_hash"]!=manifest.get("execution_lineage_identity_hash") or admitted["portable_releases"]!=releases:
            raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH","snapshot lineage differs from independently re-admitted external bundle",exit_code=EXIT_INTEGRITY)
    try:
        lineage_date=date.fromisoformat(manifest.get("snapshot_date"))
    except (TypeError,ValueError) as exc:
        raise M3Top3AdmissionError("SNAPSHOT_DATE_LINEAGE_MISMATCH","snapshot date is missing or invalid",exit_code=EXIT_INTEGRITY) from exc
    canonical_directory = snapshot_dir.name == manifest["snapshot_date"]
    internal_staging_directory = (
        allow_staging
        and snapshot_dir.name.startswith(f".{manifest['snapshot_date']}.")
        and snapshot_dir.name.endswith(".staging")
    )
    if not canonical_directory and not internal_staging_directory:
        try:
            directory_date=date.fromisoformat(snapshot_dir.name)
        except ValueError:
            directory_date=None
        if directory_date is not None:
            raise M3Top3AdmissionError(
                "SNAPSHOT_DATE_LINEAGE_MISMATCH",
                "snapshot directory date differs from the manifest date",
                {"directory":snapshot_dir.name,"snapshot_date":manifest["snapshot_date"]},
                EXIT_INTEGRITY,
            )
        _retrieval_semantic_failure(
            "snapshot directory identity differs from manifest snapshot_date",
            {"directory":snapshot_dir.name,"snapshot_date":manifest["snapshot_date"]},
        )
    verify_lineage_temporal_compatibility(external_admitted if external_admitted is not None else {"portable_releases":releases},lineage_date)

    pit_path = snapshot_dir / "pit_snapshot.jsonl"
    model_path = snapshot_dir / "model_input.jsonl"
    audit_path = snapshot_dir / "retrieval_audit.jsonl"
    pit_bytes, pit_rows = _read_jsonl(pit_path)
    model_bytes, model_inputs = _read_jsonl(model_path)
    audit_bytes, retrieval_audits = _read_jsonl(audit_path)

    actual_pit_hash = sha256_hex(pit_bytes)
    if manifest.get("pit_file_sha256") != actual_pit_hash:
        raise M3Top3AdmissionError(
            "PIT_FILE_HASH_MISMATCH",
            "stored PIT bytes do not match the manifest",
            {"expected": manifest.get("pit_file_sha256"), "actual": actual_pit_hash},
            EXIT_INTEGRITY,
        )
    actual_model_hash = sha256_hex(model_bytes)
    if manifest.get("model_input_file_sha256") != actual_model_hash:
        raise M3Top3AdmissionError(
            "MODEL_INPUT_FILE_HASH_MISMATCH",
            "stored model-input bytes do not match the manifest",
            {"expected": manifest.get("model_input_file_sha256"), "actual": actual_model_hash},
            EXIT_INTEGRITY,
        )
    actual_audit_hash = sha256_hex(audit_bytes)
    if manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:
        raise M3Top3AdmissionError(
            "RETRIEVAL_AUDIT_FILE_HASH_MISMATCH",
            "stored retrieval-audit bytes do not match the manifest",
            {"expected": manifest.get("retrieval_audit_file_sha256"), "actual": actual_audit_hash},
            EXIT_INTEGRITY,
        )

    if manifest.get("pit_row_count") != len(pit_rows):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "PIT row count differs from the manifest",
            {"declared": manifest.get("pit_row_count"), "actual": len(pit_rows), "artifact": "pit_snapshot.jsonl"},
            EXIT_INTEGRITY,
        )
    if manifest.get("model_input_row_count") != len(model_inputs):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "model-input row count differs from the manifest",
            {"declared": manifest.get("model_input_row_count"), "actual": len(model_inputs), "artifact": "model_input.jsonl"},
            EXIT_INTEGRITY,
        )
    if manifest.get("retrieval_audit_row_count") != len(retrieval_audits):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "retrieval-audit row count differs from the manifest",
            {"declared": manifest.get("retrieval_audit_row_count"), "actual": len(retrieval_audits), "artifact": "retrieval_audit.jsonl"},
            EXIT_INTEGRITY,
        )

    audit_content_hash=aggregate_hash([sha256_hex(row) for row in retrieval_audits])
    if manifest.get("retrieval_audit_content_hash") != audit_content_hash:
        raise M3Top3AdmissionError(
            "RETRIEVAL_AUDIT_CONTENT_HASH_MISMATCH",
            "recalculated retrieval-audit aggregate differs from the manifest",
            {"expected": manifest.get("retrieval_audit_content_hash"), "actual": audit_content_hash},
            EXIT_INTEGRITY,
        )

    aggregate = aggregate_hash(
        [sha256_hex(row) for row in pit_rows]
        + [sha256_hex(row) for row in model_inputs]
        + [sha256_hex(row) for row in retrieval_audits]
    )
    if manifest.get("snapshot_content_hash") != aggregate:
        raise M3Top3AdmissionError(
            "SNAPSHOT_CONTENT_HASH_MISMATCH",
            "recalculated semantic aggregate differs from the manifest",
            {"expected": manifest.get("snapshot_content_hash"), "actual": aggregate},
            EXIT_INTEGRITY,
        )
    if external_admitted is not None:
        _verify_external_snapshot_expectation(manifest,external_admitted,pit_rows,model_inputs,retrieval_audits)
    _verify_full_universe_coverage(manifest,pit_rows,model_inputs,retrieval_audits)
    _verify_retrieval_audit_semantics(snapshot_dir, manifest, pit_rows, model_inputs, retrieval_audits, allow_staging)
    return VerifiedSnapshot(manifest, pit_rows, model_inputs, retrieval_audits)


def _placeholder_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _placeholder_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _placeholder_values(nested)
    elif value is None:
        yield "NONE"
    elif isinstance(value, str):
        yield value


def verify_official_scorer(
    scorer: Any,
    config_bytes: bytes,
    receipt: dict[str, Any] | None,
) -> None:
    """Admit an exact scorer/config identity for official-mode execution."""

    if not OFFICIAL_EXECUTION_ENABLED:
        raise M3Top3AdmissionError(
            "OFFICIAL_MODE_GLOBALLY_BLOCKED",
            "no active governed authority registry or cryptographic trust root admits official execution",
            exit_code=EXIT_AUTHORITY,
        )

    if getattr(scorer, "model_id", None) == "DIAGNOSTIC_FIXTURE" or scorer.__class__.__name__.lower().startswith("diagnostic"):
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "diagnostic/test scorers cannot enter official mode",
            exit_code=EXIT_AUTHORITY,
        )
    try:
        config = json.loads(config_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise M3Top3AdmissionError(
            "PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",
            "official scorer config is not canonical JSON",
            exit_code=EXIT_AUTHORITY,
        ) from exc
    placeholders = ("WORKING", "UNRESOLVED", "EXAMPLE", "PLACEHOLDER")
    if any(any(token in item.upper() for token in placeholders) for item in _placeholder_values(config)):
        raise M3Top3AdmissionError(
            "PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",
            "working/example/unresolved values are not admissible in official mode",
            exit_code=EXIT_AUTHORITY,
        )
    required = {
        "model_id",
        "model_version",
        "model_schema_version",
        "feature_set_version",
        "scorer_artifact_sha256",
        "config_sha256",
        "baseline_identity",
        "authority_receipt",
    }
    if not isinstance(receipt, dict) or required - set(receipt) or any(not receipt.get(k) for k in required):
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "complete frozen scorer identity and authority receipt are required",
            {"missing": sorted(required - set(receipt or {}))},
            EXIT_AUTHORITY,
        )
    actual_config_hash = sha256_hex(config_bytes)
    if receipt["config_sha256"] != actual_config_hash or getattr(scorer, "config_hash", None) != actual_config_hash:
        raise M3Top3AdmissionError(
            "SCORER_CONFIG_HASH_MISMATCH",
            "scorer/config identity differs from actual canonical config bytes",
            {"actual": actual_config_hash},
            EXIT_AUTHORITY,
        )
    for attr in ("model_id", "model_version", "model_schema_version", "feature_set_version"):
        if getattr(scorer, attr, None) != receipt[attr]:
            raise M3Top3AdmissionError(
                "OFFICIAL_SCORER_ADMISSION_DENIED",
                f"scorer {attr} differs from the release receipt",
                {"field": attr},
                EXIT_AUTHORITY,
            )
    artifact_path = getattr(scorer, "artifact_path", None)
    if artifact_path is None or hash_file(Path(artifact_path)) != receipt["scorer_artifact_sha256"]:
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "scorer artifact bytes do not match the release receipt",
            exit_code=EXIT_AUTHORITY,
        )


def preflight_diagnostic_scorer(
    receipt: dict[str, Any] | None,
    config_bytes: bytes,
) -> dict[str, Any]:
    """Verify scorer artifact/config exact bytes *before* plugin import."""

    required = {
        "state", "scorer_plugin", "scorer_artifact_path", "scorer_artifact_sha256",
        "scorer_artifact_byte_size", "config_sha256", "config_byte_size",
        "model_id", "model_version", "model_schema_version", "feature_set_version",
    }
    if not isinstance(receipt, dict) or required - set(receipt):
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE", "diagnostic scorer exact identity is incomplete", {"missing": sorted(required - set(receipt or {}))}, EXIT_AUTHORITY)
    if receipt.get("state") != DIAGNOSTIC_LINEAGE_STATE:
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE", "diagnostic scorer state is not exact-byte admitted", {"state": receipt.get("state")}, EXIT_AUTHORITY)
    if sha256_hex(config_bytes) != receipt.get("config_sha256") or len(config_bytes) != receipt.get("config_byte_size"):
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH", "diagnostic scorer config bytes differ from receipt", exit_code=EXIT_AUTHORITY)
    artifact_path = receipt.get("scorer_artifact_path")
    try:
        path = Path(artifact_path).resolve(); artifact_hash = hash_file(path); artifact_size = path.stat().st_size
    except (OSError, TypeError) as exc:
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE", "diagnostic scorer artifact is unavailable", exit_code=EXIT_AUTHORITY) from exc
    if artifact_hash != receipt.get("scorer_artifact_sha256") or artifact_size != receipt.get("scorer_artifact_byte_size"):
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH", "diagnostic scorer artifact bytes differ from receipt", exit_code=EXIT_AUTHORITY)
    for field in ("scorer_plugin", "model_id", "model_version", "model_schema_version", "feature_set_version"):
        if not isinstance(receipt.get(field), str) or not receipt[field]:
            raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE", f"diagnostic scorer {field} is missing", exit_code=EXIT_AUTHORITY)
    identity = {
        "state": DIAGNOSTIC_LINEAGE_STATE,
        "scorer_plugin": receipt["scorer_plugin"],
        "scorer_artifact_sha256": artifact_hash,
        "scorer_artifact_byte_size": artifact_size,
        "config_sha256": receipt["config_sha256"],
        "config_byte_size": receipt["config_byte_size"],
        "model_id": receipt["model_id"],
        "model_version": receipt["model_version"],
        "model_schema_version": receipt["model_schema_version"],
        "feature_set_version": receipt["feature_set_version"],
    }
    return {**identity, "scorer_artifact_path": str(path), "scorer_identity_hash": sha256_hex(identity)}


def preflight_diagnostic_scorer_origin(admitted:dict[str,Any],execution_lineage:dict[str,Any])->None:
    """Resolve a Python scorer locator without importing/executing the module."""

    plugin=admitted.get("scorer_plugin") if isinstance(admitted,dict) else None
    if not isinstance(plugin,str) or plugin.count(":")!=1:
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE","diagnostic scorer plugin locator is malformed",exit_code=EXIT_AUTHORITY)
    module_name,qualname=plugin.split(":",1)
    if not module_name or not qualname or "<locals>" in qualname:
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE","diagnostic scorer module/class identity is malformed",exit_code=EXIT_AUTHORITY)
    parts=module_name.split(".")
    candidates:set[Path]=set()
    for item in sys.path:
        try:
            root=Path(item or ".").resolve()
            module_path=root.joinpath(*parts).with_suffix(".py")
            package_path=root.joinpath(*parts,"__init__.py")
            if module_path.is_file(): candidates.add(module_path.resolve())
            if package_path.is_file(): candidates.add(package_path.resolve())
        except (OSError,TypeError):
            continue
    expected_path=Path(admitted.get("scorer_artifact_path","")).resolve()
    if candidates!={expected_path}:
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","scorer plugin resolves to bytes different from the preflighted artifact",{"plugin":plugin,"resolved":[str(path) for path in sorted(candidates,key=str)],"expected":str(expected_path)},EXIT_AUTHORITY)
    release=next((row for row in execution_lineage.get("releases",[]) if row.get("domain")=="SCORER_RELEASE"),None)
    if not isinstance(release,dict) or Path(release.get("artifact_path","")).resolve()!=expected_path or release.get("artifact_sha256")!=admitted.get("scorer_artifact_sha256") or release.get("byte_size")!=admitted.get("scorer_artifact_byte_size"):
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","preflighted scorer bytes differ from exact SCORER_RELEASE",exit_code=EXIT_AUTHORITY)


def verify_diagnostic_scorer(scorer: Any, admitted: dict[str, Any], config_bytes: bytes) -> dict[str, Any]:
    """Bind the loaded object to the already preflighted exact artifact."""

    if not isinstance(admitted, dict):
        raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE", "diagnostic scorer was not preflighted", exit_code=EXIT_AUTHORITY)
    # Recompute the complete preflight identity even when a caller supplies an
    # object that already contains a scorer_identity_hash.  That hash is never
    # trusted as an admission shortcut.
    admitted=preflight_diagnostic_scorer(admitted,config_bytes)
    try:
        loaded_path=Path(inspect.getsourcefile(scorer.__class__) or inspect.getfile(scorer.__class__)).resolve()
        loaded_hash=hash_file(loaded_path); loaded_size=loaded_path.stat().st_size
    except (OSError,TypeError) as exc:
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","loaded scorer defining module cannot be bound to exact bytes",exit_code=EXIT_AUTHORITY) from exc
    loaded_plugin=f"{scorer.__class__.__module__}:{scorer.__class__.__qualname__}"
    if loaded_plugin!=admitted["scorer_plugin"] or loaded_path!=Path(admitted["scorer_artifact_path"]).resolve() or loaded_hash!=admitted["scorer_artifact_sha256"] or loaded_size!=admitted["scorer_artifact_byte_size"]:
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","loaded scorer class/module bytes differ from the preflighted scorer artifact",{"loaded_plugin":loaded_plugin,"expected_plugin":admitted["scorer_plugin"]},EXIT_AUTHORITY)
    if hash_file(Path(admitted["scorer_artifact_path"])) != admitted["scorer_artifact_sha256"] or sha256_hex(config_bytes) != admitted["config_sha256"]:
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH", "scorer artifact/config drifted after preflight", exit_code=EXIT_AUTHORITY)
    for field in ("model_id", "model_version", "model_schema_version", "feature_set_version"):
        if getattr(scorer, field, None) != admitted[field]:
            raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH", f"loaded scorer {field} differs from exact receipt", {"field": field}, EXIT_AUTHORITY)
    config_hash = getattr(scorer, "config_hash", None)
    if config_hash != admitted["config_sha256"]:
        raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH", "loaded scorer config hash differs from exact config bytes", {"loaded": config_hash, "expected": admitted["config_sha256"]}, EXIT_AUTHORITY)
    return admitted


def verify_price_release(provider: Any, admission_config: dict[str, Any] | None = None) -> None:
    """Re-verify provider byte identity and canonical/CA release admission."""

    semantics = getattr(provider, "semantics", None)
    if semantics not in ALLOWED_PRICE_SEMANTICS:
        raise M3Top3AdmissionError(
            "UNSUPPORTED_PRICE_SEMANTICS",
            "price semantics must match the governed allowlist exactly",
            {"semantics": semantics, "allowed": sorted(ALLOWED_PRICE_SEMANTICS)},
            EXIT_AUTHORITY,
        )
    release_status = getattr(provider, "release_status", None)
    if release_status not in ADMITTED_RELEASE_STATUSES:
        raise M3Top3AdmissionError(
            "PRICE_RELEASE_STATUS_UNVERIFIED",
            "partial or unverified price releases are not admissible",
            {"status": release_status},
            EXIT_BLOCKED,
        )
    raw_paths = getattr(provider, "paths", None)
    if raw_paths is None:
        single_path = getattr(provider, "path", None)
        raw_paths = [single_path] if single_path is not None else []
    paths = [Path(path).resolve() for path in raw_paths]
    if not paths:
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_PATHS_UNAVAILABLE",
            "price provider must expose exact component paths for live byte verification",
            exit_code=EXIT_INTEGRITY,
        )
    try:
        live_component_hashes = {str(path): hash_file(path) for path in paths}
    except OSError as exc:
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_HASH_MISMATCH",
            "price component bytes are unavailable during live verification",
            {"cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    if len(live_component_hashes) == 1:
        cached_components = {
            str(Path(path).resolve()): digest
            for path, digest in getattr(provider, "component_hashes", {}).items()
        }
        actual_hash = next(iter(live_component_hashes.values()))
        cached_match = cached_components == live_component_hashes
    else:
        records = getattr(provider, "component_records", None)
        if not isinstance(records, list) or len(records) != len(paths):
            raise M3Top3AdmissionError(
                "PRICE_COMPONENT_MANIFEST_REQUIRED",
                "multi-component price input has no admitted portable component records",
                exit_code=EXIT_INTEGRITY,
            )
        current_by_path = {str(path): digest for path, digest in live_component_hashes.items()}
        refreshed = []
        cached_match = True
        for record in records:
            locator = str(Path(record.get("path", "")).resolve())
            live_digest = current_by_path.get(locator)
            if live_digest is None or live_digest != record.get("artifact_sha256") or Path(locator).stat().st_size != record.get("byte_size"):
                cached_match = False
            refreshed.append({**record, "path": locator, "artifact_sha256": live_digest})
        actual_hash = price_dataset_identity_hash(getattr(provider, "dataset_id", ""), refreshed)
    if (
        not actual_hash
        or getattr(provider, "dataset_hash", None) != actual_hash
        or getattr(provider, "actual_dataset_hash", None) != actual_hash
        or not cached_match
    ):
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_HASH_MISMATCH",
            "configured price hash differs from actual component bytes",
            {
                "declared": getattr(provider, "dataset_hash", None),
                "cached": getattr(provider, "actual_dataset_hash", None),
                "actual": actual_hash,
            },
            EXIT_INTEGRITY,
        )
    if len(live_component_hashes) > 1:
        verify_price_component_manifest(provider, getattr(provider, "component_manifest", None))
    if semantics != "PRICE_CANONICAL":
        return
    if not PRICE_CANONICAL_VALIDATION_ENABLED:
        raise M3Top3AdmissionError(
            "PRICE_CANONICAL_GLOBALLY_BLOCKED",
            "self-asserted canonical receipts cannot create VALIDATION authority",
            exit_code=EXIT_AUTHORITY,
        )


def canonical_component_set_digest(components: Iterable[dict[str, Any]]) -> str:
    """Return the portable component-set identity required by R-WP4-03.

    A local locator is deliberately *not* part of this payload.  Exact live
    bytes are still rehashed through the locator, but relocating the same
    logical components cannot change the semantic identity.
    """

    normalized: list[dict[str, Any]] = []
    component_ids: list[str] = []
    logical_names: list[str] = []
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                "lineage component must be an object",
                {"row_index": index},
                EXIT_INTEGRITY,
            )
        semantic = {
            "component_id": component.get("component_id"),
            "logical_name": component.get("logical_name"),
            "byte_size": component.get("byte_size"),
            "artifact_sha256": component.get("artifact_sha256", component.get("sha256")),
            "semantic_role": component.get("semantic_role"),
        }
        if (
            not all(isinstance(semantic[field], str) and semantic[field] for field in ("component_id", "logical_name", "semantic_role"))
            or not isinstance(semantic["byte_size"], int)
            or isinstance(semantic["byte_size"], bool)
            or semantic["byte_size"] < 0
            or not _is_sha256(semantic["artifact_sha256"])
        ):
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                "lineage component semantic identity is incomplete",
                {"row_index": index},
                EXIT_INTEGRITY,
            )
        component_ids.append(semantic["component_id"])
        logical_names.append(semantic["logical_name"])
        normalized.append(semantic)
    if len(component_ids) != len(set(component_ids)) or len(logical_names) != len(set(logical_names)):
        raise M3Top3AdmissionError(
            "DUPLICATE_LINEAGE_COMPONENT",
            "component_id and logical_name must each be unique within a release",
            exit_code=EXIT_INTEGRITY,
        )
    return sha256_hex(sorted(normalized, key=lambda row: row["component_id"]))


def price_dataset_identity_hash(dataset_id: str, components: Iterable[dict[str, Any]] | dict[str, Any]) -> str:
    """Path-independent multi-component price identity.

    ``dict[path, sha256]`` remains accepted only as a compatibility helper for
    old callers.  It is normalized with basename logical identities and live
    sizes when available; governed admission itself requires the explicit
    component records checked by :func:`verify_price_component_manifest`.
    """

    if isinstance(components, dict):
        normalized: list[dict[str, Any]] = []
        for index, (locator, value) in enumerate(sorted(components.items()), 1):
            if isinstance(value, dict):
                record = dict(value)
                record.setdefault("path", locator)
            else:
                path = Path(locator)
                record = {
                    "component_id": f"{dataset_id}:component:{index:04d}",
                    "logical_name": path.name,
                    "semantic_role": f"PRICE_COMPONENT_{index:04d}",
                    "byte_size": path.stat().st_size if path.exists() else 0,
                    "artifact_sha256": value,
                    "path": locator,
                }
            normalized.append(record)
    else:
        normalized = [dict(component) for component in components]
    return sha256_hex(
        {
            "manifest_version": "m3top3-price-components-v2",
            "dataset_id": dataset_id,
            "component_set_digest": canonical_component_set_digest(normalized),
        }
    )


def verify_price_component_manifest(provider: Any, manifest: dict[str, Any] | None) -> None:
    paths=[Path(path).resolve() for path in getattr(provider,"paths",[]) or []]
    if len(paths)<=1:
        return
    if not isinstance(manifest,dict):
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_REQUIRED","multi-component price input requires a versioned byte manifest",exit_code=EXIT_INTEGRITY)
    required={"manifest_version","hash_algorithm","dataset_id","dataset_hash","component_set_digest","components"}
    if required-set(manifest) or manifest.get("manifest_version")!="m3top3-price-components-v2" or manifest.get("hash_algorithm")!="SHA256":
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","price component manifest schema/version is invalid",exit_code=EXIT_INTEGRITY)
    declared=manifest.get("components")
    if not isinstance(declared,list) or len(declared)!=len(paths):
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","manifest and live component cardinalities differ",exit_code=EXIT_INTEGRITY)
    by_path: dict[str,dict[str,Any]]={}
    for component in declared:
        if not isinstance(component,dict) or not isinstance(component.get("path"),str):
            raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","every price component requires an operational path locator",exit_code=EXIT_INTEGRITY)
        resolved=str(Path(component["path"]).resolve())
        if resolved in by_path:
            raise M3Top3AdmissionError("DUPLICATE_LINEAGE_COMPONENT","duplicate price component locator",exit_code=EXIT_INTEGRITY)
        by_path[resolved]=component
    if set(by_path)!=set(map(str,paths)):
        raise M3Top3AdmissionError("EXTRA_LINEAGE_COMPONENT","live price components differ from the registered component set",exit_code=EXIT_INTEGRITY)
    records=[]
    for path in paths:
        declared_component=dict(by_path[str(path)])
        try:
            actual_hash=hash_file(path); actual_size=path.stat().st_size
        except OSError as exc:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH","price component bytes are unavailable",{"path":str(path)},EXIT_INTEGRITY) from exc
        if declared_component.get("artifact_sha256",declared_component.get("sha256"))!=actual_hash or declared_component.get("byte_size")!=actual_size:
            raise M3Top3AdmissionError("LINEAGE_COMPONENT_HASH_MISMATCH","price component hash/size differs from live bytes",{"component_id":declared_component.get("component_id")},EXIT_INTEGRITY)
        declared_component["artifact_sha256"]=actual_hash
        declared_component["byte_size"]=actual_size
        declared_component["path"]=str(path)
        records.append(declared_component)
    digest=canonical_component_set_digest(records)
    actual_identity=price_dataset_identity_hash(getattr(provider,"dataset_id",None),records)
    if manifest.get("component_set_digest")!=digest:
        raise M3Top3AdmissionError("COMPONENT_SET_DIGEST_MISMATCH","price component-set digest is forged or stale",exit_code=EXIT_INTEGRITY)
    if manifest.get("dataset_id")!=getattr(provider,"dataset_id",None) or manifest.get("dataset_hash")!=actual_identity or getattr(provider,"dataset_hash",None)!=actual_identity:
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","price dataset identity does not match exact components",{"actual":actual_identity},EXIT_INTEGRITY)
    provider.component_records=records
    provider.component_set_digest=digest
    provider.component_hashes={record["component_id"]:record["artifact_sha256"] for record in records}
    provider.actual_dataset_hash=actual_identity
