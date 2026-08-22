from __future__ import annotations

import csv
import importlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, Sequence

from .admission import ELEVATED_RELEASE_STATES, EXIT_INTEGRITY, M3Top3AdmissionError, price_dataset_identity_hash, verify_price_component_manifest, verify_price_release
from .core import deterministic_id, hash_file, parse_date, parse_datetime, sha256_hex
from .pit_guard import GuardViolation, PITGuard, PITLeakageError


@dataclass(frozen=True)
class UniverseState:
    company_id: str
    security_code: str
    valid_from: date | None
    valid_to: date | None
    operational_member: bool | None
    tradable_eligible: bool | None
    universe_record_id: str
    status: str = "VERIFIED"

    def effective_on(self, d: date) -> bool:
        if self.valid_from and d < self.valid_from:
            return False
        if self.valid_to and d >= self.valid_to:
            return False
        return True


@dataclass(frozen=True)
class EligibilityDecision:
    snapshot_date: date
    snapshot_cutoff_at: str
    universe_release_id: str
    universe_release_revision: int
    denominator_release_id: str
    denominator_release_revision: int
    company_id: str
    security_code: str
    universe_record_id: str
    universe_member_id: str
    eligibility_record_id: str
    eligibility_status: str
    status: str

    def effective_on(self, d: date) -> bool:
        return d == self.snapshot_date


def eligibility_decision_payload(row: EligibilityDecision) -> dict[str, Any]:
    return {
        "snapshot_date": row.snapshot_date.isoformat(),
        "snapshot_cutoff_at": row.snapshot_cutoff_at,
        "universe_release_id": row.universe_release_id,
        "universe_release_revision": row.universe_release_revision,
        "denominator_release_id": row.denominator_release_id,
        "denominator_release_revision": row.denominator_release_revision,
        "company_id": row.company_id,
        "security_code": str(row.security_code).zfill(6),
        "universe_record_id": row.universe_record_id,
        "universe_member_id": row.universe_member_id,
        "eligibility_record_id": row.eligibility_record_id,
        "eligibility_status": row.eligibility_status,
        "status": row.status,
    }


def eligibility_decisions_hash(rows: Sequence[EligibilityDecision]) -> str:
    return sha256_hex(sorted((eligibility_decision_payload(row) for row in rows),key=lambda item:(item["snapshot_date"],item["company_id"],item["security_code"],item["eligibility_record_id"])))


class UniverseProvider(Protocol):
    release_id: str
    release_hash: str
    release_status: str
    authority_status: str
    denominator_release_id: str
    denominator_release_hash: str
    denominator_status: str
    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]: ...
    def expected_states_at(self, snapshot_date: date) -> Sequence[UniverseState]: ...


def universe_state_payload(state: UniverseState) -> dict[str, Any]:
    return {
        "company_id": state.company_id,
        "security_code": str(state.security_code).zfill(6),
        "valid_from": state.valid_from.isoformat() if state.valid_from else None,
        "valid_to": state.valid_to.isoformat() if state.valid_to else None,
        "operational_member": state.operational_member,
        "tradable_eligible": state.tradable_eligible,
        "universe_record_id": state.universe_record_id,
        "status": state.status,
    }


def universe_states_hash(states: Sequence[UniverseState]) -> str:
    payload = sorted(
        (universe_state_payload(state) for state in states),
        key=lambda row: (
            row["company_id"],
            row["security_code"],
            row["valid_from"] or "",
            row["valid_to"] or "",
            row["universe_record_id"],
        ),
    )
    return sha256_hex(payload)


def _read_universe_states(path: Path) -> list[UniverseState]:
    rows: list[UniverseState] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise TypeError("universe row must be an object")
            required = {
                "company_id",
                "security_code",
                "valid_from",
                "valid_to",
                "operational_member",
                "tradable_eligible",
                "universe_record_id",
                "status",
            }
            if required - set(row):
                raise KeyError(f"missing universe fields: {sorted(required - set(row))}")
            company_id = row["company_id"]
            security_code = str(row["security_code"]).strip()
            universe_record_id = row["universe_record_id"]
            status = row["status"]
            if (
                not isinstance(company_id, str)
                or not company_id.strip()
                or not security_code.isdigit()
                or len(security_code) != 6
                or not isinstance(universe_record_id, str)
                or not universe_record_id.strip()
                or not isinstance(status, str)
                or not status.strip()
                or row["operational_member"] not in {True, False, None}
                or row["tradable_eligible"] not in {True, False, None}
            ):
                raise TypeError("universe row identity, status, or eligibility fields are malformed")
            rows.append(
                UniverseState(
                    company_id,
                    security_code,
                    parse_date(row["valid_from"]) if row.get("valid_from") else None,
                    parse_date(row["valid_to"]) if row.get("valid_to") else None,
                    row.get("operational_member"),
                    row.get("tradable_eligible"),
                    universe_record_id,
                    status,
                )
            )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            "universe JSONL is unreadable or malformed",
            {"path": str(path), "line": locals().get("line_number"), "cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    return rows


def _read_eligibility_decisions(path: Path) -> list[EligibilityDecision]:
    rows: list[EligibilityDecision] = []
    required = {
        "schema_version","snapshot_date","snapshot_cutoff_at","universe_release_id",
        "universe_release_revision","denominator_release_id","denominator_release_revision",
        "company_id","security_code","universe_record_id","universe_member_id",
        "eligibility_record_id","eligibility_status","status",
    }
    try:
        for line_number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if not line.strip(): continue
            row=json.loads(line)
            if not isinstance(row,dict): raise TypeError("denominator row must be an object")
            missing=required-set(row)
            if missing: raise KeyError(f"missing denominator fields: {sorted(missing)}")
            code=str(row["security_code"]).strip()
            if row["schema_version"]!="m3top3-denominator-eligibility-v1" or not code.isdigit() or len(code)!=6:
                raise TypeError("denominator schema or security code is invalid")
            if row["eligibility_status"] not in {"ELIGIBLE","INELIGIBLE","UNRESOLVED"} or row["status"] not in {"VERIFIED","DIAGNOSTIC_VERIFIED","PARTIAL","UNVERIFIED","UNKNOWN"}:
                raise TypeError("denominator status is invalid")
            if any(not isinstance(row[field],str) or not row[field] for field in ("snapshot_cutoff_at","universe_release_id","denominator_release_id","company_id","universe_record_id","universe_member_id","eligibility_record_id")):
                raise TypeError("denominator identity is invalid")
            if any(not isinstance(row[field],int) or isinstance(row[field],bool) or row[field]<0 for field in ("universe_release_revision","denominator_release_revision")):
                raise TypeError("denominator revisions are invalid")
            parsed_snapshot=parse_date(row["snapshot_date"])
            cutoff=parse_datetime(row["snapshot_cutoff_at"])
            if cutoff.date()!=parsed_snapshot:
                raise ValueError("denominator cutoff/date differ")
            rows.append(EligibilityDecision(parsed_snapshot,row["snapshot_cutoff_at"],row["universe_release_id"],row["universe_release_revision"],row["denominator_release_id"],row["denominator_release_revision"],row["company_id"],code.zfill(6),row["universe_record_id"],row["universe_member_id"],row["eligibility_record_id"],row["eligibility_status"],row["status"]))
    except (OSError,UnicodeError,json.JSONDecodeError,KeyError,TypeError,ValueError) as exc:
        raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY","denominator eligibility JSONL is unreadable or malformed",{"path":str(path),"line":locals().get("line_number"),"cause":type(exc).__name__},EXIT_INTEGRITY) from exc
    keys=[(row.company_id,row.snapshot_date,row.denominator_release_revision) for row in rows]
    if len(keys)!=len(set(keys)):
        raise M3Top3AdmissionError("DUPLICATE_DENOMINATOR_KEY","denominator has more than one decision per company/date/revision",exit_code=EXIT_INTEGRITY)
    return rows


class JsonlUniverseProvider:
    def __init__(
        self,
        path: str | Path,
        release_id: str,
        authority_status: str,
        *,
        release_hash: str | None = None,
        release_status: str | None = None,
        denominator_path: str | Path | None = None,
        denominator_release_id: str | None = None,
        denominator_release_hash: str | None = None,
        denominator_status: str | None = None,
        lineage_manifest_path: str | Path | None = None,
        lineage_manifest_hash: str | None = None,
        universe_expectation_manifest_path: str | Path | None = None,
        universe_expectation_manifest_hash: str | None = None,
        denominator_expectation_manifest_path: str | Path | None = None,
        denominator_expectation_manifest_hash: str | None = None,
    ):
        if (
            lineage_manifest_path is None
            or lineage_manifest_hash is None
            or denominator_path is None
            or universe_expectation_manifest_path is None
            or universe_expectation_manifest_hash is None
            or denominator_expectation_manifest_path is None
            or denominator_expectation_manifest_hash is None
        ):
            raise M3Top3AdmissionError(
                "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
                "JSONL universe admission requires externally supplied exact U and denominator expectation manifests",
                exit_code=4,
            )
        self.path = Path(path)
        self.authority_status = authority_status
        self.lineage_manifest_path = Path(lineage_manifest_path)
        self.lineage_manifest_hash = lineage_manifest_hash
        try:
            manifest_bytes = self.lineage_manifest_path.read_bytes()
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "universe lineage manifest is unreadable or malformed",
                {"path": str(self.lineage_manifest_path), "cause": type(exc).__name__},
                EXIT_INTEGRITY,
            ) from exc
        if not isinstance(manifest, dict) or hash_file(self.lineage_manifest_path) != lineage_manifest_hash:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "universe lineage manifest bytes differ from the configured exact hash",
                exit_code=EXIT_INTEGRITY,
            )
        release = manifest.get("release")
        denominator = manifest.get("denominator")
        slices = manifest.get("slices")
        required_binding = {"release_id", "release_version", "release_revision", "logical_locator", "source_sha256", "status", "state_hash", "expectation_manifest_path", "expectation_manifest_sha256", "expectation_source_id", "authority_or_evidence_receipt_ref"}
        if (
            manifest.get("manifest_version") != "m3top3-universe-lineage-v1"
            or manifest.get("hash_algorithm") != "SHA256"
            or not isinstance(manifest.get("authority_status"), str)
            or not manifest.get("authority_status")
            or not isinstance(release, dict)
            or not isinstance(denominator, dict)
            or required_binding - set(release)
            or required_binding - set(denominator)
            or not isinstance(slices, list)
            or not slices
            or any(not isinstance(item, dict) for item in slices)
        ):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "universe lineage manifest schema/version is incomplete",
                exit_code=EXIT_INTEGRITY,
            )
        manifest_authority=manifest.get("authority_status")
        if manifest_authority!="DIAGNOSTIC":
            code="RELEASE_AUTHORITY_ADMISSION_DENIED" if manifest_authority in ELEVATED_RELEASE_STATES else "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE"
            raise M3Top3AdmissionError(code,"external Universe lineage authority must equal DIAGNOSTIC in this bounded phase",{"authority_status":manifest_authority},4)
        if authority_status!="DIAGNOSTIC":
            code="RELEASE_AUTHORITY_ADMISSION_DENIED" if authority_status in ELEVATED_RELEASE_STATES else "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE"
            raise M3Top3AdmissionError(code,"configured external Universe authority exceeds the exact diagnostic ceiling",{"authority_status":authority_status},4)
        if manifest_authority != authority_status:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "configured universe authority status differs from the independent lineage manifest",
                {"configured": authority_status, "manifest": manifest.get("authority_status")},
                EXIT_INTEGRITY,
            )
        expectation_paths=[Path(universe_expectation_manifest_path).resolve(),Path(denominator_expectation_manifest_path).resolve()]
        expectation_hashes=[universe_expectation_manifest_hash,denominator_expectation_manifest_hash]
        declared_expectation_paths=[Path(binding["expectation_manifest_path"]).resolve() for binding in (release,denominator)]
        declared_expectation_hashes=[binding["expectation_manifest_sha256"] for binding in (release,denominator)]
        if expectation_paths!=declared_expectation_paths or expectation_hashes!=declared_expectation_hashes:
            raise M3Top3AdmissionError(
                "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
                "externally supplied U/denominator expectation anchors differ from the lineage manifest",
                exit_code=4,
            )
        expectation_sources=[binding["expectation_source_id"] for binding in (release,denominator)]
        expectation_receipts=[binding["authority_or_evidence_receipt_ref"] for binding in (release,denominator)]
        if len(set(map(str,expectation_paths)))!=2 or len(set(expectation_hashes))!=2 or len(set(expectation_sources))!=2 or len(set(expectation_receipts))!=2 or any(not isinstance(value,str) or not value for value in expectation_hashes+expectation_sources+expectation_receipts):
            raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","Universe and denominator require distinct external expectation manifests, sources, and evidence receipts",exit_code=4)
        expectation_values=[]
        for path,expected_hash in zip(expectation_paths,expectation_hashes):
            try:
                raw=path.read_bytes(); value=json.loads(raw.decode("utf-8"))
            except (OSError,UnicodeError,json.JSONDecodeError) as exc:
                raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external expectation manifest is unavailable or malformed",{"path":str(path)},4) from exc
            if not isinstance(value,dict) or hash_file(path)!=expected_hash or value.get("binding_mode")!="EXTERNALLY_SUPPLIED_INDEPENDENT_BINDING":
                raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external expectation manifest is not independently exact-byte bound",{"path":str(path)},4)
            expectation_values.append(value)
        universe_expectation,denominator_expectation=expectation_values
        if universe_expectation.get("schema_version")!="m3top3-universe-expectation-v1" or denominator_expectation.get("schema_version")!="m3top3-denominator-expectation-v1" or universe_expectation.get("expectation_source_id")!=expectation_sources[0] or denominator_expectation.get("expectation_source_id")!=expectation_sources[1] or universe_expectation.get("authority_or_evidence_receipt_ref")!=expectation_receipts[0] or denominator_expectation.get("authority_or_evidence_receipt_ref")!=expectation_receipts[1]:
            raise M3Top3AdmissionError("SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED","external expectation manifests do not match their independent bindings",exit_code=4)
        for binding_name,binding in (("release",release),("denominator",denominator)):
            if not isinstance(binding.get("release_version"),str) or not binding["release_version"] or not isinstance(binding.get("release_revision"),int) or isinstance(binding.get("release_revision"),bool) or binding["release_revision"]<0:
                raise M3Top3AdmissionError("RELEASE_REVISION_MISMATCH",f"{binding_name} version/revision is invalid",exit_code=EXIT_INTEGRITY)
        if release.get("release_id") != release_id:
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "configured universe release ID differs from the independent lineage manifest",
                {"configured": release_id, "manifest": release.get("release_id")},
                EXIT_INTEGRITY,
            )
        if release_hash is not None and release_hash != release.get("source_sha256"):
            raise M3Top3AdmissionError("UNIVERSE_RELEASE_HASH_MISMATCH", "configured universe release hash differs from the lineage manifest", exit_code=EXIT_INTEGRITY)
        if release_status is not None and release_status != release.get("status"):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", "configured universe release status differs from the lineage manifest", exit_code=EXIT_INTEGRITY)
        if denominator_release_id is not None and denominator_release_id != denominator.get("release_id"):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", "configured denominator release ID differs from the lineage manifest", exit_code=EXIT_INTEGRITY)
        if denominator_release_hash is not None and denominator_release_hash != denominator.get("source_sha256"):
            raise M3Top3AdmissionError("DENOMINATOR_RELEASE_HASH_MISMATCH", "configured denominator hash differs from the lineage manifest", exit_code=EXIT_INTEGRITY)
        if denominator_status is not None and denominator_status != denominator.get("status"):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", "configured denominator status differs from the lineage manifest", exit_code=EXIT_INTEGRITY)
        if not all(isinstance(binding.get("logical_locator"), str) and binding["logical_locator"] for binding in (release, denominator)):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", "release and denominator logical locators must be non-empty", exit_code=EXIT_INTEGRITY)
        if release.get("release_id") == denominator.get("release_id") or release.get("logical_locator") == denominator.get("logical_locator"):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "release and denominator must have distinct governed identities and logical locators",
                exit_code=EXIT_INTEGRITY,
            )
        self._lineage_manifest = manifest
        self.universe_expectation_manifest_path=expectation_paths[0]
        self.universe_expectation_manifest_hash=expectation_hashes[0]
        self._universe_expectation_manifest=universe_expectation
        self.denominator_expectation_manifest_path=expectation_paths[1]
        self.denominator_expectation_manifest_hash=expectation_hashes[1]
        self._denominator_expectation_manifest=denominator_expectation
        self._lineage_slices = {str(item.get("snapshot_date")): item for item in slices if item.get("snapshot_date")}
        if len(self._lineage_slices) != len(slices):
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", "lineage manifest slice dates must be present and unique", exit_code=EXIT_INTEGRITY)
        self.release_id = release_id
        self.release_version = str(release["release_version"])
        self.release_revision = int(release["release_revision"])
        self.release_status = str(release["status"])
        self._rows = _read_universe_states(self.path)
        self.actual_release_hash = hash_file(self.path)
        self.release_hash = str(release["source_sha256"])
        self.release_state_hash = universe_states_hash(self._rows)
        self.denominator_path = Path(denominator_path)
        if self.denominator_path.resolve() == self.path.resolve():
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
                "JSONL universe rows cannot self-certify the independent denominator",
                exit_code=EXIT_INTEGRITY,
            )
        self._denominator_rows = _read_eligibility_decisions(self.denominator_path)
        self.actual_denominator_release_hash = hash_file(self.denominator_path)
        self.denominator_release_id = str(denominator["release_id"])
        self.denominator_release_version = str(denominator["release_version"])
        self.denominator_release_revision = int(denominator["release_revision"])
        self.denominator_release_hash = str(denominator["source_sha256"])
        self.denominator_status = str(denominator["status"])
        self.denominator_state_hash = eligibility_decisions_hash(self._denominator_rows)
        self.denominator_schema_version = "m3top3-denominator-eligibility-v1"
        self.release_source_kind = "JSONL_EXACT_BYTES"
        self.lineage_manifest_kind = "EXACT_EXTERNAL_MANIFEST"
        if universe_expectation.get("release_id")!=self.release_id or universe_expectation.get("release_version")!=self.release_version or universe_expectation.get("release_revision")!=self.release_revision or universe_expectation.get("source_sha256")!=self.release_hash or denominator_expectation.get("release_id")!=self.denominator_release_id or denominator_expectation.get("release_version")!=self.denominator_release_version or denominator_expectation.get("release_revision")!=self.denominator_release_revision or denominator_expectation.get("universe_release_id")!=self.release_id or denominator_expectation.get("universe_release_revision")!=self.release_revision or denominator_expectation.get("source_sha256")!=self.denominator_release_hash:
            raise M3Top3AdmissionError("UNIVERSE_LINEAGE_MANIFEST_MISMATCH","external expectation manifest release tuples differ from exact live release bindings",exit_code=EXIT_INTEGRITY)
        if self.release_state_hash != release.get("state_hash") or self.denominator_state_hash != denominator.get("state_hash"):
            raise M3Top3AdmissionError(
                "UNIVERSE_LINEAGE_MANIFEST_MISMATCH",
                "parsed release/denominator state hashes differ from the lineage manifest",
                {"release_state_hash": self.release_state_hash, "denominator_state_hash": self.denominator_state_hash},
                EXIT_INTEGRITY,
            )

    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]:
        return [r for r in self._rows if r.effective_on(snapshot_date)]

    def expected_states_at(self, snapshot_date: date) -> Sequence[EligibilityDecision]:
        return [r for r in self._denominator_rows if r.effective_on(snapshot_date)]


class StaticUniverseProvider:
    def __init__(
        self,
        states: Sequence[UniverseState],
        release_id: str = "TEST-U",
        authority_status: str = "DIAGNOSTIC",
        *,
        denominator_states: Sequence[UniverseState] | None = None,
        release_hash: str | None = None,
        release_status: str = "DIAGNOSTIC_VERIFIED",
        denominator_release_id: str | None = None,
        denominator_release_hash: str | None = None,
        denominator_status: str = "DIAGNOSTIC_VERIFIED",
    ):
        self._rows = list(states)
        self._denominator_rows = list(states if denominator_states is None else denominator_states)
        self.release_id = release_id
        self.release_version = "synthetic-fixture-v1"
        self.release_revision = 0
        self.authority_status = authority_status
        self.release_status = release_status
        self.actual_release_hash = universe_states_hash(self._rows)
        self.release_hash = release_hash or self.actual_release_hash
        self.release_state_hash = self.actual_release_hash
        self.denominator_release_id = denominator_release_id or f"{release_id}:DENOMINATOR"
        self.denominator_release_version = "synthetic-fixture-v1"
        self.denominator_release_revision = 0
        self.actual_denominator_release_hash = universe_states_hash(self._denominator_rows)
        self.denominator_release_hash = denominator_release_hash or self.actual_denominator_release_hash
        self.denominator_status = denominator_status
        self.denominator_state_hash = self.actual_denominator_release_hash
        self.release_source_kind = "IN_MEMORY_DIAGNOSTIC"
        self.lineage_manifest_kind = "SYNTHETIC_IN_MEMORY_DIAGNOSTIC"
        self.lineage_manifest_hash = sha256_hex(
            {
                "kind": self.lineage_manifest_kind,
                "authority_status": self.authority_status,
                "release_id": self.release_id,
                "release_hash": self.release_hash,
                "release_status": self.release_status,
                "denominator_release_id": self.denominator_release_id,
                "denominator_release_hash": self.denominator_release_hash,
                "denominator_status": self.denominator_status,
            }
        )
        self.path = None
        self.denominator_path = None

    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]:
        return [r for r in self._rows if r.effective_on(snapshot_date)]

    def expected_states_at(self, snapshot_date: date) -> Sequence[UniverseState]:
        return [r for r in self._denominator_rows if r.effective_on(snapshot_date)]


class PITFeatureProvider(Protocol):
    source_version: str
    source_status: str
    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]: ...


class JsonlFeatureProvider:
    def __init__(self, path: str | Path, source_version: str, cutoff_frozen_bundle: bool = False, source_status: str = "DIAGNOSTIC_VERIFIED"):
        self.path = Path(path); self.source_version = source_version; self.source_status=source_status; self.cutoff_frozen_bundle=cutoff_frozen_bundle; self._rows = []; self.retrieval_receipts=[]; self.last_retrieval_receipt=None
        try:
            for line_number,line in enumerate(self.path.read_text(encoding="utf-8").splitlines(),1):
                if line.strip():
                    row=json.loads(line)
                    if not isinstance(row,dict): raise TypeError("feature row must be an object")
                    self._rows.append(row)
            self.source_hash=hash_file(self.path)
        except (OSError,UnicodeError,json.JSONDecodeError,TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY","feature JSONL is unreadable or malformed",{"path":str(self.path),"line":locals().get("line_number"),"cause":type(exc).__name__},EXIT_INTEGRITY) from exc

    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        return _select_feature_rows(self,company_id,cutoff_at)


class InMemoryFeatureProvider:
    def __init__(self, rows: Sequence[dict[str, Any]], source_version: str = "TEST-FEATURES", cutoff_frozen_bundle: bool = False, source_status: str = "DIAGNOSTIC_VERIFIED"):
        self._rows=[dict(r) for r in rows]; self.source_version=source_version; self.source_status=source_status; self.cutoff_frozen_bundle=cutoff_frozen_bundle; self.source_hash=sha256_hex(self._rows); self.retrieval_receipts=[]; self.last_retrieval_receipt=None
    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        return _select_feature_rows(self,company_id,cutoff_at)


_AS_OF_EXCLUSION_CODES={"PIT_PUBLICATION_AFTER_CUTOFF","PIT_EFFECTIVE_AFTER_CUTOFF","POST_SNAPSHOT_CA_KNOWLEDGE"}


def _select_feature_rows(provider: Any, company_id: str, cutoff_at: datetime) -> list[dict[str, Any]]:
    """Select an as-of slice and emit a deterministic raw-source exclusion receipt.

    Longitudinal stores may contain later rows.  Those rows are excluded and
    audited; the consumed slice is independently re-guarded.  A declared
    cutoff-frozen bundle treats any future row as an integrity violation.
    """
    guard=PITGuard(); selected=[]; exclusions=[]; matching=0
    for index,r in enumerate(provider._rows):
        if str(r.get("company_id")) != company_id: continue
        matching+=1
        violations=guard.validate_model_input(r,cutoff_at)
        hard=[v for v in violations if v.code not in _AS_OF_EXCLUSION_CODES]
        future=[v for v in violations if v.code in _AS_OF_EXCLUSION_CODES]
        if hard: raise PITLeakageError(hard+future)
        row_id=str(r.get("feature_record_id") or r.get("evidence_id") or r.get("event_record_id") or deterministic_id("feature_row",{"source_hash":provider.source_hash,"index":index,"row":r}))
        if future:
            if provider.cutoff_frozen_bundle: raise PITLeakageError(future)
            exclusions.append({"row_id":row_id,"codes":sorted({v.code for v in future})}); continue
        valid_to=r.get("valid_to")
        if valid_to:
            try: expired=parse_datetime(valid_to)<=cutoff_at
            except (ValueError,TypeError) as exc: raise PITLeakageError([GuardViolation("INVALID_EFFECTIVE_DATETIME","valid_to must be a timezone-aware datetime","valid_to")]) from exc
            if expired:
                exclusions.append({"row_id":row_id,"codes":["OUTSIDE_VALIDITY_INTERVAL"]}); continue
        selected.append(dict(r))
    guard.assert_model_inputs(selected,cutoff_at)
    receipt_payload={"company_id":company_id,"cutoff_at":cutoff_at.isoformat(),"source_version":provider.source_version,"source_status":provider.source_status,"source_hash":provider.source_hash,"source_matching_rows":matching,"selected_rows":len(selected),"excluded_rows":len(exclusions),"exclusions":exclusions,"cutoff_frozen_bundle":provider.cutoff_frozen_bundle}
    receipt={**receipt_payload,"retrieval_receipt_id":deterministic_id("retrieval",receipt_payload)}
    provider.last_retrieval_receipt=receipt; provider.retrieval_receipts.append(receipt)
    return selected


@dataclass(frozen=True)
class PriceRow:
    date: date
    code: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None = None
    marcap: Decimal | None = None
    stocks: int | None = None
    corporate_action_flag: bool | None = None
    adjustment_factor: Decimal | None = None
    corporate_action_evidence_id: str | None = None


class PriceProvider(Protocol):
    dataset_id: str
    dataset_hash: str
    semantics: str
    def trading_dates(self, start: date, end: date) -> list[date]: ...
    def row(self, code: str, trading_date: date) -> PriceRow | None: ...
    def rows(self, code: str, start: date, end: date) -> list[PriceRow]: ...


class CsvPriceProvider:
    def __init__(self, path: str | Path, dataset_id: str = "TEST-PRICE", dataset_hash: str = "TEST", semantics: str = "RAW_IMMUTABLE", admission_config: dict[str, Any] | None = None):
        self.path=Path(path); self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; self.canonical_release=admission_config; self.release_status=(admission_config or {}).get("release_status","DIAGNOSTIC_VERIFIED"); rows=[]
        self.component_hashes={str(self.path):hash_file(self.path)}; self.actual_dataset_hash=self.component_hashes[str(self.path)]
        seen:set[tuple[str,date]]=set()
        with self.path.open("r", encoding="utf-8", newline="") as f:
            for line_number,r in enumerate(csv.DictReader(f),2):
                row=PriceRow(parse_date(r["date"]), str(r["code"]).zfill(6), Decimal(str(r["open"])), Decimal(str(r["high"])), Decimal(str(r["low"])), Decimal(str(r["close"])), int(r["volume"]) if r.get("volume") else None, Decimal(str(r["marcap"])) if r.get("marcap") else None, int(r["stocks"]) if r.get("stocks") else None, (r.get("corporate_action_flag", "").lower()=="true") if r.get("corporate_action_flag") else None, Decimal(str(r["adjustment_factor"])) if r.get("adjustment_factor") else None, str(r["corporate_action_evidence_id"]) if r.get("corporate_action_evidence_id") else None)
                key=(row.code,row.date)
                if key in seen:
                    raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {key}",{"line":line_number,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
                seen.add(key); _validate_price_row(row,{"line":line_number,"path":str(self.path)}); rows.append(row)
        self._rows=rows; self._by_key={(r.code,r.date):r for r in rows}; self._dates=sorted({r.date for r in rows}); verify_price_release(self,admission_config)
    def trading_dates(self,start:date,end:date)->list[date]: verify_price_release(self); return [d for d in self._dates if start<=d<=end]
    def row(self,code:str,trading_date:date)->PriceRow|None: verify_price_release(self); return self._by_key.get((str(code).zfill(6),trading_date))
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        verify_price_release(self); code=str(code).zfill(6); return [r for r in self._rows if r.code==code and start<=r.date<=end]


class DuckDBParquetPriceProvider:
    """Optional production adapter for RAW marcap or PRICE-CANONICAL parquet."""
    def __init__(self, paths: Sequence[str | Path], dataset_id: str, dataset_hash: str, semantics: str = "RAW_IMMUTABLE", admission_config: dict[str, Any] | None = None, component_manifest: dict[str, Any] | None = None):
        try: duckdb=importlib.import_module("duckdb")
        except ImportError as exc: raise RuntimeError("DuckDBParquetPriceProvider requires the optional 'duckdb' package") from exc
        self._duckdb=duckdb; self.paths=[str(Path(p).resolve()) for p in paths]; self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; self.canonical_release=admission_config; self.release_status=(admission_config or {}).get("release_status","DIAGNOSTIC_VERIFIED"); self.component_manifest=component_manifest
        self.component_hashes={p:hash_file(Path(p)) for p in self.paths}; self.actual_dataset_hash=next(iter(self.component_hashes.values())) if len(self.component_hashes)==1 else None
        verify_price_component_manifest(self,component_manifest)
        verify_price_release(self,admission_config)
        self._con=duckdb.connect()
        list_sql="["+",".join(repr(p) for p in self.paths)+"]"; self._source_sql=f"read_parquet({list_sql}, union_by_name=true)"
        cols={r[0].lower():r[0] for r in self._con.execute(f"DESCRIBE SELECT * FROM {self._source_sql}").fetchall()}; required={"date","code","open","high","low","close"}; missing=required-set(cols)
        if missing: raise ValueError(f"price parquet missing required columns: {sorted(missing)}")
        self._cols=cols
        duplicate=self._con.execute(f"SELECT LPAD(CAST({self._c('code')} AS VARCHAR),6,'0'), CAST({self._c('date')} AS DATE), COUNT(*) n FROM {self._source_sql} GROUP BY 1,2 HAVING n>1 LIMIT 1").fetchone()
        if duplicate: raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {(duplicate[0],duplicate[1])}",{"code":duplicate[0],"date":str(duplicate[1]),"count":duplicate[2]},EXIT_INTEGRITY)
        invalid=self._con.execute(f"SELECT CAST({self._c('date')} AS DATE), LPAD(CAST({self._c('code')} AS VARCHAR),6,'0'), {self._c('open')}, {self._c('high')}, {self._c('low')}, {self._c('close')} FROM {self._source_sql} WHERE {self._c('open')}<=0 OR {self._c('high')}<=0 OR {self._c('low')}<=0 OR {self._c('close')}<=0 OR {self._c('high')}<GREATEST({self._c('open')},{self._c('close')}) OR {self._c('low')}>LEAST({self._c('open')},{self._c('close')}) OR {self._c('low')}>{self._c('high')} LIMIT 1").fetchone()
        if invalid: raise M3Top3AdmissionError("INVALID_OHLC",f"invalid OHLC row {(invalid[1],invalid[0])}",{"code":invalid[1],"date":str(invalid[0])},EXIT_INTEGRITY)
        ca_columns={"corporate_action_flag","adjustment_factor","corporate_action_evidence_id"}
        if self.semantics=="PRICE_CANONICAL" and not ca_columns.issubset(self._cols):
            raise M3Top3AdmissionError("PRICE_CANONICAL_CA_INCOMPLETE","canonical parquet lacks required CA flag/factor/evidence columns",{"missing":sorted(ca_columns-set(self._cols))},4)
        if "corporate_action_flag" in self._cols:
            if not {"adjustment_factor","corporate_action_evidence_id"}.issubset(self._cols):
                flagged=self._con.execute(f"SELECT CAST({self._c('date')} AS DATE), LPAD(CAST({self._c('code')} AS VARCHAR),6,'0') FROM {self._source_sql} WHERE CAST({self._c('corporate_action_flag')} AS BOOLEAN)=TRUE LIMIT 1").fetchone()
                if flagged: raise M3Top3AdmissionError("CA_EVIDENCE_INCOMPLETE","flagged parquet CA row lacks factor/evidence schema",{"date":str(flagged[0]),"code":flagged[1]},EXIT_INTEGRITY)
            else:
                invalid_ca=self._con.execute(f"SELECT CAST({self._c('date')} AS DATE), LPAD(CAST({self._c('code')} AS VARCHAR),6,'0'), {self._c('adjustment_factor')}, CAST({self._c('corporate_action_evidence_id')} AS VARCHAR) FROM {self._source_sql} WHERE CAST({self._c('corporate_action_flag')} AS BOOLEAN)=TRUE AND ({self._c('adjustment_factor')} IS NULL OR {self._c('adjustment_factor')}<=0 OR {self._c('corporate_action_evidence_id')} IS NULL OR TRIM(CAST({self._c('corporate_action_evidence_id')} AS VARCHAR))='') LIMIT 1").fetchone()
                if invalid_ca:
                    code="INVALID_ADJUSTMENT_FACTOR" if invalid_ca[2] is not None and Decimal(str(invalid_ca[2]))<=0 else "CA_EVIDENCE_INCOMPLETE"
                    raise M3Top3AdmissionError(code,"invalid parquet corporate-action evidence/factor",{"date":str(invalid_ca[0]),"code":invalid_ca[1]},EXIT_INTEGRITY)
        verify_price_release(self,admission_config)
    def _c(self,lower:str)->str: return '"'+self._cols[lower].replace('"','""')+'"'
    def trading_dates(self,start:date,end:date)->list[date]:
        verify_price_release(self)
        q=f"SELECT DISTINCT CAST({self._c('date')} AS DATE) d FROM {self._source_sql} WHERE CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY d"; return [r[0] for r in self._con.execute(q,[start,end]).fetchall()]
    def row(self,code:str,trading_date:date)->PriceRow|None:
        verify_price_release(self)
        q=f"SELECT {self._select_columns()} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE)=?"; rows=self._con.execute(q,[str(code).zfill(6),trading_date]).fetchall()
        if len(rows)>1: raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {(code,trading_date)}",exit_code=EXIT_INTEGRITY)
        row=rows[0] if rows else None
        return None if not row else self._price_row(row)
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        verify_price_release(self)
        q=f"SELECT {self._select_columns()} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY 1"; out=[]
        for row in self._con.execute(q,[str(code).zfill(6),start,end]).fetchall(): out.append(self._price_row(row))
        return out
    def _select_columns(self)->str:
        flag=f"CAST({self._c('corporate_action_flag')} AS BOOLEAN)" if "corporate_action_flag" in self._cols else "NULL"
        factor=self._c("adjustment_factor") if "adjustment_factor" in self._cols else "NULL"
        evidence=f"CAST({self._c('corporate_action_evidence_id')} AS VARCHAR)" if "corporate_action_evidence_id" in self._cols else "NULL"
        return f"CAST({self._c('date')} AS DATE), CAST({self._c('code')} AS VARCHAR), {self._c('open')}, {self._c('high')}, {self._c('low')}, {self._c('close')}, {flag}, {factor}, {evidence}"
    def _price_row(self,row)->PriceRow:
        result=PriceRow(row[0],str(row[1]).zfill(6),*(Decimal(str(x)) for x in row[2:6]),corporate_action_flag=bool(row[6]) if row[6] is not None else None,adjustment_factor=Decimal(str(row[7])) if row[7] is not None else None,corporate_action_evidence_id=str(row[8]) if row[8] is not None else None)
        _validate_price_row(result,{"provider":"DuckDBParquetPriceProvider","code":result.code,"date":result.date.isoformat()}); return result


def _validate_price_row(row: PriceRow, locator: dict[str, Any]) -> None:
    prices=(row.open,row.high,row.low,row.close)
    if any(value <= 0 for value in prices) or row.high < max(row.open,row.close) or row.low > min(row.open,row.close) or row.low > row.high:
        raise M3Top3AdmissionError("INVALID_OHLC",f"invalid OHLC for {row.code} on {row.date}",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
    if row.corporate_action_flag:
        if row.adjustment_factor is None:
            raise M3Top3AdmissionError("CA_EVIDENCE_INCOMPLETE","corporate-action row is missing an adjustment factor",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
        if row.adjustment_factor <= 0:
            raise M3Top3AdmissionError("INVALID_ADJUSTMENT_FACTOR","adjustment factor must be positive",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
        if not row.corporate_action_evidence_id:
            raise M3Top3AdmissionError("CA_EVIDENCE_INCOMPLETE","corporate-action row is missing evidence",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
