from __future__ import annotations

import csv
import json
import inspect
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from tools.m3top3.backtest import ValidationRunner
from tools.m3top3.admission import DIAGNOSTIC_LINEAGE_STATE, REQUIRED_LINEAGE_DOMAINS, M3Top3AdmissionError, admit_execution_lineage_bundle, canonical_component_set_digest, eligibility_record_identity, eligibility_set_digest, synthetic_fixture_lineage, universe_member_identity, universe_member_set_digest
from tools.m3top3.core import aggregate_hash, canonical_json_bytes, hash_file, sha256_hex
from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine
from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
from tools.m3top3.providers import CsvPriceProvider, EligibilityDecision, InMemoryFeatureProvider, JsonlFeatureProvider, JsonlUniverseProvider, StaticUniverseProvider, UniverseState, eligibility_decisions_hash, universe_states_hash
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore


def business_dates(start: date = date(2025, 1, 2), count: int = 20) -> list[date]:
    values: list[date] = []
    cursor = start
    while len(values) < count:
        if cursor.weekday() < 5:
            values.append(cursor)
        cursor += timedelta(days=1)
    return values


def write_price_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "date", "code", "open", "high", "low", "close", "volume",
        "corporate_action_flag", "adjustment_factor", "corporate_action_evidence_id",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_universe_lineage_manifest(
    root: Path,
    universe_path: Path,
    snapshot_dates: list[date],
    release_id: str = "U",
    universe_release_revision: int = 0,
    denominator_release_revision: int = 0,
    cutoff_local_time: str = "23:59:59",
    eligibility_status_by_company: dict[str, str] | None = None,
) -> tuple[Path, Path, str]:
    raw_rows = [json.loads(line) for line in universe_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    states = [
        UniverseState(
            str(row["company_id"]),
            str(row["security_code"]),
            date.fromisoformat(row["valid_from"]) if row.get("valid_from") else None,
            date.fromisoformat(row["valid_to"]) if row.get("valid_to") else None,
            row.get("operational_member"),
            row.get("tradable_eligible"),
            str(row["universe_record_id"]),
            str(row.get("status", "VERIFIED")),
        )
        for row in raw_rows
    ]
    denominator_release_id=f"{release_id}:DENOMINATOR"
    denominator_rows=[]; denominator_states=[]
    for snapshot_date in snapshot_dates:
        cutoff=f"{snapshot_date.isoformat()}T{cutoff_local_time}+09:00"
        for state in states:
            if not state.effective_on(snapshot_date): continue
            member_id=universe_member_identity(state)
            eligibility_status=(eligibility_status_by_company or {}).get(state.company_id)
            if eligibility_status is None:
                eligibility_status="ELIGIBLE" if state.operational_member is True and state.tradable_eligible is True else "INELIGIBLE" if state.operational_member is False or state.tradable_eligible is False else "UNRESOLVED"
            if eligibility_status not in {"ELIGIBLE","INELIGIBLE","UNRESOLVED"}:
                raise ValueError(f"unsupported test eligibility status: {eligibility_status}")
            record_id=eligibility_record_identity(state,snapshot_date,denominator_release_id,universe_release_revision,denominator_release_revision,cutoff,eligibility_status)
            row={"schema_version":"m3top3-denominator-eligibility-v1","snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":cutoff,"universe_release_id":release_id,"universe_release_revision":universe_release_revision,"denominator_release_id":denominator_release_id,"denominator_release_revision":denominator_release_revision,"company_id":state.company_id,"security_code":str(state.security_code).zfill(6),"universe_record_id":state.universe_record_id,"universe_member_id":member_id,"eligibility_record_id":record_id,"eligibility_status":eligibility_status,"status":state.status}
            denominator_rows.append(row)
            denominator_states.append(EligibilityDecision(snapshot_date,cutoff,release_id,universe_release_revision,denominator_release_id,denominator_release_revision,state.company_id,str(state.security_code).zfill(6),state.universe_record_id,member_id,record_id,eligibility_status,state.status))
    denominator_path = root / "denominator.jsonl"
    denominator_path.write_text("".join(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n" for row in denominator_rows),encoding="utf-8")
    slices = []
    for snapshot_date in snapshot_dates:
        effective = [state for state in states if state.effective_on(snapshot_date)]
        member_ids = sorted(universe_member_identity(state) for state in effective)
        decisions=[row for row in denominator_states if row.snapshot_date==snapshot_date]
        eligible_ids=sorted(row.universe_member_id for row in decisions if row.eligibility_status=="ELIGIBLE")
        ineligible_ids=sorted(row.universe_member_id for row in decisions if row.eligibility_status=="INELIGIBLE")
        eligible_record_ids=sorted(row.eligibility_record_id for row in decisions if row.eligibility_status=="ELIGIBLE")
        ineligible_record_ids=sorted(row.eligibility_record_id for row in decisions if row.eligibility_status=="INELIGIBLE")
        universe_digest=universe_member_set_digest(effective)
        eligible_digest=eligibility_set_digest(decisions,"ELIGIBLE")
        ineligible_digest=eligibility_set_digest(decisions,"INELIGIBLE")
        partition_digest=sha256_hex({"universe_member_set_digest":universe_digest,"eligible_set_digest":eligible_digest,"ineligible_set_digest":ineligible_digest,"universe_count":len(member_ids),"eligible_count":len(eligible_ids),"ineligible_count":len(ineligible_ids)})
        slices.append(
            {
                "snapshot_date": snapshot_date.isoformat(),
                "snapshot_cutoff_at": f"{snapshot_date.isoformat()}T{cutoff_local_time}+09:00",
                "universe_release_revision": universe_release_revision,
                "denominator_release_revision": denominator_release_revision,
                "release_partition": f"release://{release_id}/{snapshot_date.isoformat()}",
                "denominator_partition": f"denominator://{release_id}/{snapshot_date.isoformat()}",
                "release_row_count": len(member_ids),
                "denominator_row_count": len(member_ids),
                "eligible_row_count": len(eligible_ids),
                "ineligible_row_count": len(ineligible_ids),
                "release_identity_hash": aggregate_hash(member_ids),
                "denominator_identity_hash": aggregate_hash(member_ids),
                "universe_member_set_digest": universe_digest,
                "eligible_identity_hash": aggregate_hash(eligible_ids),
                "ineligible_identity_hash": aggregate_hash(ineligible_ids),
                "eligible_set_digest": eligible_digest,
                "ineligible_set_digest": ineligible_digest,
                "denominator_partition_digest": partition_digest,
            }
        )
    state_hash = universe_states_hash(states)
    universe_expectation={
        "schema_version":"m3top3-universe-expectation-v1",
        "binding_mode":"EXTERNALLY_SUPPLIED_INDEPENDENT_BINDING",
        "expectation_source_id":f"{release_id}:UNIVERSE_EXPECTATION_SOURCE",
        "authority_or_evidence_receipt_ref":f"{release_id}:UNIVERSE_EXPECTATION_RECEIPT",
        "release_id":release_id,
        "release_version":"test-v1",
        "release_revision":universe_release_revision,
        "source_sha256":hash_file(universe_path),
        "slices":[{"snapshot_date":row["snapshot_date"],"snapshot_cutoff_at":row["snapshot_cutoff_at"],"universe_count":row["release_row_count"],"universe_member_set_digest":row["universe_member_set_digest"]} for row in slices],
    }
    denominator_expectation={
        "schema_version":"m3top3-denominator-expectation-v1",
        "binding_mode":"EXTERNALLY_SUPPLIED_INDEPENDENT_BINDING",
        "expectation_source_id":f"{release_id}:DENOMINATOR_EXPECTATION_SOURCE",
        "authority_or_evidence_receipt_ref":f"{release_id}:DENOMINATOR_EXPECTATION_RECEIPT",
        "release_id":denominator_release_id,
        "release_version":"test-v1",
        "release_revision":denominator_release_revision,
        "universe_release_id":release_id,
        "universe_release_revision":universe_release_revision,
        "source_sha256":hash_file(denominator_path),
        "slices":[{"snapshot_date":row["snapshot_date"],"snapshot_cutoff_at":row["snapshot_cutoff_at"],"universe_count":row["denominator_row_count"],"eligible_count":row["eligible_row_count"],"ineligible_count":row["ineligible_row_count"],"universe_member_set_digest":row["universe_member_set_digest"],"eligible_set_digest":row["eligible_set_digest"],"ineligible_set_digest":row["ineligible_set_digest"],"denominator_partition_digest":row["denominator_partition_digest"]} for row in slices],
    }
    universe_expectation_path=root/"universe-expectation.json"; universe_expectation_path.write_bytes(canonical_json_bytes(universe_expectation)+b"\n")
    denominator_expectation_path=root/"denominator-expectation.json"; denominator_expectation_path.write_bytes(canonical_json_bytes(denominator_expectation)+b"\n")
    manifest = {
        "manifest_version": "m3top3-universe-lineage-v1",
        "hash_algorithm": "SHA256",
        "authority_status": "DIAGNOSTIC",
        "release": {
            "release_id": release_id,
            "release_version": "test-v1",
            "release_revision": universe_release_revision,
            "logical_locator": f"release://{release_id}",
            "source_sha256": hash_file(universe_path),
            "status": "DIAGNOSTIC_VERIFIED",
            "state_hash": state_hash,
            "expectation_manifest_path":str(universe_expectation_path.resolve()),
            "expectation_manifest_sha256":hash_file(universe_expectation_path),
            "expectation_source_id":universe_expectation["expectation_source_id"],
            "authority_or_evidence_receipt_ref":universe_expectation["authority_or_evidence_receipt_ref"],
        },
        "denominator": {
            "release_id": denominator_release_id,
            "release_version": "test-v1",
            "release_revision": denominator_release_revision,
            "logical_locator": f"denominator://{release_id}",
            "source_sha256": hash_file(denominator_path),
            "status": "DIAGNOSTIC_VERIFIED",
            "state_hash": eligibility_decisions_hash(denominator_states),
            "expectation_manifest_path":str(denominator_expectation_path.resolve()),
            "expectation_manifest_sha256":hash_file(denominator_expectation_path),
            "expectation_source_id":denominator_expectation["expectation_source_id"],
            "authority_or_evidence_receipt_ref":denominator_expectation["authority_or_evidence_receipt_ref"],
        },
        "slices": slices,
    }
    manifest_path = root / "universe-lineage.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return denominator_path, manifest_path, hash_file(manifest_path)


def external_expectation_kwargs(lineage_manifest_path: Path) -> dict[str, Any]:
    """Return the two independently supplied expectation anchors for tests.

    Production callers receive these values as separate configuration inputs;
    this helper merely keeps exact-byte fixtures readable.
    """

    value=json.loads(lineage_manifest_path.read_text(encoding="utf-8"))
    universe=value["release"]
    denominator=value["denominator"]
    return {
        "universe_expectation_manifest_path":universe["expectation_manifest_path"],
        "universe_expectation_manifest_hash":universe["expectation_manifest_sha256"],
        "denominator_expectation_manifest_path":denominator["expectation_manifest_path"],
        "denominator_expectation_manifest_hash":denominator["expectation_manifest_sha256"],
    }


def standard_price_rows(dates: list[date] | None = None, code: str = "005930") -> list[dict[str, Any]]:
    dates = dates or business_dates()
    return [
        {
            "date": d.isoformat(), "code": code, "open": 100 + i,
            "high": 103 + i, "low": 98 + i, "close": 101 + i,
            "volume": 1000 + i,
        }
        for i, d in enumerate(dates)
    ]


def price_provider(root: Path, rows: list[dict[str, Any]] | None = None, **kwargs: Any) -> CsvPriceProvider:
    path = root / f"price-{len(list(root.glob('price-*.csv')))}.csv"
    write_price_csv(path, rows or standard_price_rows())
    kwargs.setdefault("dataset_hash", hash_file(path))
    return CsvPriceProvider(path, **kwargs)


def ready_builder(root: Path, feature_rows: list[dict[str, Any]] | None = None):
    dates = business_dates()
    price = price_provider(root, standard_price_rows(dates))
    universe = StaticUniverseProvider(
        [UniverseState("C1", "005930", date(2020, 1, 1), None, True, True, "U1")],
        "U-TEST", "DIAGNOSTIC",
    )
    if feature_rows is None:
        feature_rows = [{
            "company_id": "C1", "feature_id": "diagnostic_score", "value": "9",
            "publication_at": "2025-01-02T10:00:00+09:00",
        }]
    builder = SnapshotBuilder(universe, InMemoryFeatureProvider(feature_rows), price, SnapshotBuildConfig())
    return dates, price, builder


def materialize_ready_snapshot(root: Path):
    dates, price, builder = ready_builder(root)
    snapshot_root = root / "snapshots"
    built = builder.build(dates[0])
    SnapshotStore(snapshot_root).write(built, {"generator_version": "test-v1"})
    return snapshot_root / dates[0].isoformat(), dates, price, built


def synthetic_bound_lineage(universe, features, price):
    """Test-only lineage bridge for downstream Jsonl provider regressions.

    CLI/canonical admission never calls this helper.  It deliberately keeps
    the artifact marked synthetic/non-release-eligible while binding the
    already independently verified provider release and denominator hashes.
    """
    fixture = StaticUniverseProvider(
        list(universe._rows),
        universe.release_id,
        "DIAGNOSTIC",
        denominator_states=list(universe._rows),
        release_hash=universe.release_hash,
        release_status=universe.release_status,
        denominator_release_id=universe.denominator_release_id,
        denominator_release_hash=universe.denominator_release_hash,
        denominator_status=universe.denominator_status,
    )
    return synthetic_fixture_lineage(fixture, features, price)


def write_execution_lineage_bundle(root: Path, domain_specs: dict[str, dict[str, Any]], *, bundle_name: str = "execution-lineage.json"):
    """Materialize a complete exact eight-domain diagnostic lineage bundle."""
    if set(domain_specs)!=set(REQUIRED_LINEAGE_DOMAINS):
        raise ValueError(f"domain specs must equal required domains: {sorted(set(REQUIRED_LINEAGE_DOMAINS)-set(domain_specs))}")
    releases=[]
    for domain in REQUIRED_LINEAGE_DOMAINS:
        spec=dict(domain_specs[domain]); artifact=Path(spec["artifact_path"])
        release_id=str(spec.get("release_id",domain)); role=str(spec.get("semantic_role",domain))
        raw_components=spec.get("components") or [{"component_id":f"{release_id}:component:0001","logical_name":artifact.name,"semantic_role":role,"path":str(artifact)}]
        components=[]
        for raw in raw_components:
            path=Path(raw["path"])
            components.append({"component_id":str(raw["component_id"]),"logical_name":str(raw["logical_name"]),"semantic_role":str(raw["semantic_role"]),"path":str(path.resolve()),"artifact_sha256":hash_file(path),"byte_size":path.stat().st_size})
        digest=canonical_component_set_digest(components)
        manifest_components=[{key:component[key] for key in ("component_id","logical_name","semantic_role","artifact_sha256","byte_size")} for component in components]
        as_of_date=str(spec.get("as_of_date","1970-01-01"))
        artifact_id=str(spec.get("artifact_id",f"{release_id}:artifact"))
        artifact_sha256=hash_file(artifact)
        artifact_byte_size=artifact.stat().st_size
        manifest={"schema_version":"m3top3-release-manifest-v1","domain":domain,"release_id":release_id,"release_version":str(spec.get("release_version","test-v1")),"release_revision":int(spec.get("release_revision",0)),"as_of_date":as_of_date,"artifact_id":artifact_id,"artifact_sha256":artifact_sha256,"byte_size":artifact_byte_size,"component_set_digest":digest,"semantic_role":role,"state":DIAGNOSTIC_LINEAGE_STATE,"components":manifest_components}
        if spec.get("physical_alias_allowed") is True:
            manifest["physical_alias_allowed"]=True
            manifest["physical_alias_group_id"]=str(spec["physical_alias_group_id"])
            manifest["physical_alias_roles"]=sorted(str(value) for value in spec["physical_alias_roles"])
        manifest_path=root/f"{domain.lower()}-release-manifest.json"
        manifest_path.write_bytes(canonical_json_bytes(manifest)+b"\n")
        release={"domain":domain,"release_id":release_id,"release_version":manifest["release_version"],"release_revision":manifest["release_revision"],"as_of_date":as_of_date,"artifact_id":artifact_id,"artifact_path":str(artifact.resolve()),"artifact_sha256":artifact_sha256,"byte_size":artifact_byte_size,"manifest_path":str(manifest_path.resolve()),"manifest_sha256":hash_file(manifest_path),"component_set_digest":digest,"semantic_role":role,"state":DIAGNOSTIC_LINEAGE_STATE,"components":components}
        if spec.get("physical_alias_allowed") is True:
            release["physical_alias_allowed"]=True
            release["physical_alias_group_id"]=str(spec["physical_alias_group_id"])
            release["physical_alias_roles"]=sorted(str(value) for value in spec["physical_alias_roles"])
        releases.append(release)
    bundle={"schema_version":"m3top3-execution-lineage-v1","state":DIAGNOSTIC_LINEAGE_STATE,"official_golden":False,"full_replay":False,"releases":releases}
    bundle_path=root/bundle_name; bundle_path.write_bytes(canonical_json_bytes(bundle)+b"\n")
    bundle_hash=hash_file(bundle_path)
    return bundle_path,bundle_hash,admit_execution_lineage_bundle(bundle_path,bundle_hash)


class CountingScorer(DiagnosticFixtureScorer):
    def __init__(self, score: str = "9"):
        self.calls = 0
        self.score_value = score

    def score(self, model_input):
        self.calls += 1
        copied = dict(model_input)
        copied["feature_values"] = dict(copied.get("feature_values", {}))
        copied["feature_values"]["diagnostic_score"] = self.score_value
        return super().score(copied)


def diagnostic_runner(price: CsvPriceProvider, dates: list[date], scorer=None, tie_policy: str = "COMPANY_ID_ASC_DIAGNOSTIC", execution_lineage=None):
    scorer = scorer or CountingScorer()
    window_identity=None
    if execution_lineage is not None and not execution_lineage.get("synthetic_only"):
        window_ref=next(release for release in execution_lineage["portable_releases"] if release["domain"]=="WINDOW_REGISTRY_RELEASE")
        window_identity={key:window_ref[key] for key in ("release_id","artifact_sha256","release_revision")}
    windows = ExplicitWindowResolver({dates[0].isoformat(): dates[5].isoformat()}, "test-window-v1")
    config_bytes,receipt=diagnostic_scorer_admission(scorer)
    return ValidationRunner(scorer, RankingEngine(tie_policy), OutcomeBuilder(price, windows), execution_mode="DIAGNOSTIC",scorer_config_bytes=config_bytes,diagnostic_scorer_identity=receipt,execution_lineage=execution_lineage,window_release_identity=window_identity), scorer


def diagnostic_scorer_admission(scorer):
    artifact=Path(inspect.getsourcefile(scorer.__class__) or inspect.getfile(scorer.__class__)).resolve()
    config_bytes=canonical_json_bytes({"model_id":scorer.model_id,"model_version":scorer.model_version,"model_schema_version":scorer.model_schema_version,"feature_set_version":scorer.feature_set_version,"fixture_behavior":"COUNTING_SCORER_RUNTIME_NONDETERMINISM_PROBE"})
    scorer.config_hash=sha256_hex(config_bytes)
    receipt={"state":"DIAGNOSTIC_EXACT_BYTES","scorer_plugin":f"{scorer.__class__.__module__}:{scorer.__class__.__qualname__}","scorer_artifact_path":str(artifact),"scorer_artifact_sha256":hash_file(artifact),"scorer_artifact_byte_size":artifact.stat().st_size,"config_sha256":sha256_hex(config_bytes),"config_byte_size":len(config_bytes),"model_id":scorer.model_id,"model_version":scorer.model_version,"model_schema_version":scorer.model_schema_version,"feature_set_version":scorer.feature_set_version}
    return config_bytes,receipt


def materialize_external_fixture(
    root: Path,
    states: list[UniverseState] | None = None,
    *,
    independent_expectation_states: list[UniverseState] | None = None,
    eligibility_status_by_company: dict[str, str] | None = None,
    universe_release_revision: int = 0,
    denominator_release_revision: int = 0,
    cutoff_local_time: str = "23:59:59",
):
    dates=business_dates(count=30)
    if states is not None and independent_expectation_states is None:
        raise M3Top3AdmissionError(
            "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
            "a custom live Universe fixture cannot generate its own external expectation authority",
            exit_code=4,
        )
    if states is not None and independent_expectation_states is not None and any(
        live is expected for live in states for expected in independent_expectation_states
    ):
        raise M3Top3AdmissionError(
            "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
            "live Universe rows cannot also serve as the purported independent expectation evidence",
            exit_code=4,
        )
    states=states or [
        UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1","DIAGNOSTIC_VERIFIED"),
        UniverseState("C2","000660",date(2020,1,1),None,True,True,"U2","DIAGNOSTIC_VERIFIED"),
        UniverseState("C3","035420",date(2020,1,1),None,True,True,"U3","DIAGNOSTIC_VERIFIED"),
        UniverseState("C4","051910",date(2020,1,1),None,True,False,"U4","DIAGNOSTIC_VERIFIED"),
    ]
    if independent_expectation_states is not None:
        expected_keys={(row.company_id,str(row.security_code).zfill(6)) for row in independent_expectation_states}
        live_keys={(row.company_id,str(row.security_code).zfill(6)) for row in states}
        if expected_keys!=live_keys:
            raise M3Top3AdmissionError(
                "UNIVERSE_SET_DIGEST_MISMATCH",
                "custom live fixture differs from its separately supplied expectation population",
                exit_code=3,
            )
    universe_path=root/"universe.jsonl"
    universe_path.write_text("".join(json.dumps({"company_id":state.company_id,"security_code":str(state.security_code).zfill(6),"valid_from":state.valid_from.isoformat() if state.valid_from else None,"valid_to":state.valid_to.isoformat() if state.valid_to else None,"operational_member":state.operational_member,"tradable_eligible":state.tradable_eligible,"universe_record_id":state.universe_record_id,"status":state.status},sort_keys=True,separators=(",",":"))+"\n" for state in states),encoding="utf-8")
    denominator_path,universe_manifest,universe_manifest_hash=write_universe_lineage_manifest(
        root,universe_path,[dates[0]],"U-EXTERNAL",
        universe_release_revision=universe_release_revision,
        denominator_release_revision=denominator_release_revision,
        cutoff_local_time=cutoff_local_time,
        eligibility_status_by_company=eligibility_status_by_company,
    )
    feature_path=root/"features.jsonl"
    feature_path.write_text("".join(json.dumps({"company_id":state.company_id,"feature_id":"diagnostic_score","value":str(10-index),"publication_at":f"{dates[0].isoformat()}T10:00:00+09:00"},sort_keys=True,separators=(",",":"))+"\n" for index,state in enumerate(states)),encoding="utf-8")
    price=price_provider(root,standard_price_rows(dates),dataset_id="P-EXTERNAL")
    window_path=root/"window-registry.json"; window_path.write_bytes(canonical_json_bytes({"protocol_version":"test-window-v1","window_end_by_snapshot_date":{dates[0].isoformat():dates[5].isoformat()}})+b"\n")
    scorer=CountingScorer(); scorer_config_bytes,scorer_receipt=diagnostic_scorer_admission(scorer)
    scorer_config_path=root/"scorer-config.json"; scorer_config_path.write_bytes(scorer_config_bytes)
    alias={"artifact_path":price.path,"physical_alias_allowed":True,"physical_alias_group_id":"PRICE_CA_CALENDAR_SHARED_BYTES","physical_alias_roles":["PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE"]}
    specs={
        "UNIVERSE_RELEASE":{
            "release_id":"U-EXTERNAL","artifact_path":universe_path,"semantic_role":"UNIVERSE_MEMBERSHIP",
            "release_revision":universe_release_revision,
            "components":[
                {"component_id":"U-EXTERNAL:ROWS","logical_name":"universe.jsonl","semantic_role":"UNIVERSE_MEMBERSHIP_ROWS","path":universe_path},
                {"component_id":"U-EXTERNAL:EXPECTATION","logical_name":"universe-expectation.json","semantic_role":"UNIVERSE_EXPECTATION_MANIFEST","path":root/"universe-expectation.json"},
                {"component_id":"U-EXTERNAL:LINEAGE","logical_name":"universe-lineage.json","semantic_role":"UNIVERSE_LINEAGE_MANIFEST","path":universe_manifest},
            ],
        },
        "DENOMINATOR_ELIGIBILITY_RELEASE":{
            "release_id":"U-EXTERNAL:DENOMINATOR","artifact_path":denominator_path,"semantic_role":"ELIGIBILITY_DENOMINATOR",
            "release_revision":denominator_release_revision,
            "components":[
                {"component_id":"U-EXTERNAL:DENOMINATOR:ROWS","logical_name":"denominator.jsonl","semantic_role":"DENOMINATOR_ELIGIBILITY_ROWS","path":denominator_path},
                {"component_id":"U-EXTERNAL:DENOMINATOR:EXPECTATION","logical_name":"denominator-expectation.json","semantic_role":"DENOMINATOR_EXPECTATION_MANIFEST","path":root/"denominator-expectation.json"},
            ],
        },
        "FEATURE_SOURCE_RELEASE":{"release_id":"TEST-FEATURES","artifact_path":feature_path,"semantic_role":"PIT_FEATURE_SOURCE"},
        "PRICE_RELEASE":{"release_id":price.dataset_id,"semantic_role":"RAW_PRICE",**alias},
        "CORPORATE_ACTION_RELEASE":{"release_id":f"{price.dataset_id}:CA","semantic_role":"CA_EVIDENCE",**alias},
        "TRADING_CALENDAR_RELEASE":{"release_id":f"{price.dataset_id}:CALENDAR","semantic_role":"TRADING_CALENDAR",**alias},
        "WINDOW_REGISTRY_RELEASE":{"release_id":"WINDOW-TEST-V1","artifact_path":window_path,"semantic_role":"OUTCOME_WINDOW_REGISTRY"},
        "SCORER_RELEASE":{"release_id":"SCORER-DIAGNOSTIC-EXACT","artifact_path":Path(scorer_receipt["scorer_artifact_path"]),"semantic_role":"DIAGNOSTIC_SCORER"},
    }
    bundle_path,bundle_hash,lineage=write_execution_lineage_bundle(root,specs)
    universe=JsonlUniverseProvider(
        universe_path,"U-EXTERNAL","DIAGNOSTIC",
        denominator_path=denominator_path,
        lineage_manifest_path=universe_manifest,
        lineage_manifest_hash=universe_manifest_hash,
        **external_expectation_kwargs(universe_manifest),
    )
    features=JsonlFeatureProvider(feature_path,"TEST-FEATURES")
    builder=SnapshotBuilder(universe,features,price,SnapshotBuildConfig(cutoff_local_time=cutoff_local_time),execution_lineage=lineage)
    built=builder.build(dates[0]); snapshot_root=root/"snapshots"; SnapshotStore(snapshot_root).write(built,{})
    return {"dates":dates,"states":states,"universe_path":universe_path,"denominator_path":denominator_path,"universe_manifest":universe_manifest,"features_path":feature_path,"price":price,"window_path":window_path,"scorer":scorer,"scorer_config_bytes":scorer_config_bytes,"scorer_config_path":scorer_config_path,"scorer_receipt":scorer_receipt,"bundle_path":bundle_path,"bundle_hash":bundle_hash,"lineage":lineage,"snapshot_dir":snapshot_root/dates[0].isoformat(),"built":built}
