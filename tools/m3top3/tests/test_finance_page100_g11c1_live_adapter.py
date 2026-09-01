"""Focused, zero-network tests for the G11C1 append-only LIVE adapter."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ADAPTER_PATH = Path(__file__).resolve().parents[1] / "finance_page100_g11c1_live_adapter.py"
SPEC = importlib.util.spec_from_file_location("g11c1_live_adapter_under_test", ADAPTER_PATH)
assert SPEC is not None and SPEC.loader is not None
g11 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = g11
SPEC.loader.exec_module(g11)

FIXED_NOW = datetime(2026, 9, 1, 3, 0, 0, tzinfo=timezone.utc)
FIXED_TIME = FIXED_NOW.isoformat()


def _entity(page_no: int, total_count: int, items: list[dict[str, str]]) -> bytes:
    return g11.canonical_json_bytes({
        "response": {
            "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
            "body": {
                "pageNo": str(page_no),
                "numOfRows": "10",
                "totalCount": str(total_count),
                "items": {"item": items},
            },
        },
    })


def _item(custody: str, crno: str, name: str) -> dict[str, str]:
    return {
        "basDt": "20240131",
        "issuCmpyKsdCustNo": custody,
        "crno": crno,
        "stckIssuCmpyNm": name,
    }


def _versioned(binding: Any, body: bytes | None = None) -> Any:
    return g11.VersionedObject(
        key=binding.key,
        version_id=binding.version_id,
        etag=binding.etag,
        body=binding.body if body is None and hasattr(binding, "body") else (body or b""),
        content_type=binding.content_type,
        server_side_encryption=binding.server_side_encryption,
        metadata={},
    )


@dataclass
class SyntheticSeed:
    contract: Any
    objects: dict[tuple[str, str], Any]
    stable_items: dict[str, dict[str, str]]
    target_custody: str


def _synthetic_seed() -> SyntheticSeed:
    stable_items = {
        str(1000 + ordinal): _item(
            str(1000 + ordinal), f"CRNO-{ordinal:02d}", f"Issuer-{ordinal:02d}"
        )
        for ordinal in range(1, 17)
    }
    target_custody = "9999"
    target_frozen = _item(target_custody, "TARGET-CRNO-A", "Target-A")
    target_observed = _item(target_custody, "TARGET-CRNO-B", "Target-B")

    rows: list[dict[str, str]] = []
    for ordinal in range(1, 36):
        rows.append(copy.deepcopy(stable_items[str(1000 + ((ordinal - 1) % 16) + 1)]))
    rows.extend([
        target_frozen, target_observed, target_frozen,
        target_observed, target_frozen,
    ])

    raw_bodies = [
        _entity(page_no, 41, rows[(page_no - 1) * 10:page_no * 10])
        for page_no in range(1, 5)
    ]
    raw_bindings = tuple(
        g11.ObjectBinding(
            key=f"seed/raw/page-{page_no}.entity",
            version_id=f"raw-version-{page_no}",
            sha256=g11.sha256_bytes(body),
            bytes=len(body),
            etag=f'"raw-etag-{page_no}"',
            content_type="application/octet-stream",
            page_no=page_no,
        )
        for page_no, body in enumerate(raw_bodies, 1)
    )

    identities = {
        custody: g11.identity_digest(item)
        for custody, item in stable_items.items()
    }
    identities[target_custody] = g11.identity_digest(target_frozen)
    attempts = [
        {"basDt": "20240131", "page_no": page_no, "attempt": 1}
        for page_no in range(1, 5)
    ]
    raw_index = [
        {
            "basDt": "20240131", "page_no": page_no, "attempt": 1,
            "s3_object_key": binding.key,
            "s3_version_id": binding.version_id,
            "entity_sha256": binding.sha256,
            "entity_bytes": binding.bytes,
        }
        for page_no, binding in enumerate(raw_bindings, 1)
    ]
    checkpoint = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_v1.0",
        "checkpoint_revision": 27,
        "state": "BLOCKED",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G10-20260830044522",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G10-20260830044522",
        "completed_dates": ["20240102"],
        "next_date_index": 1,
        "provider_api_network_attempts": 4,
        "quota_reservations": 4,
        "remote_raw_custody_writes": 4,
        "issuer_identity_rows_checked": 40,
        "issuer_identity_match_rows": 38,
        "issuer_identity_conflicts": 2,
        "issuer_identity_missing_rows": 0,
        "attempts": attempts,
        "raw_index": raw_index,
        "issuer_identity_hashes": identities,
    }
    checkpoint_body = g11.canonical_json_bytes(checkpoint)
    checkpoint_binding = g11.ObjectBinding(
        key="seed/control/checkpoint.json",
        version_id="checkpoint-version",
        sha256=g11.sha256_bytes(checkpoint_body),
        bytes=len(checkpoint_body),
        etag='"checkpoint-etag"',
        content_type="application/json",
    )

    descriptors = []
    for ordinal, item in enumerate(rows, 1):
        custody_hash = g11.sha256_bytes(item["issuCmpyKsdCustNo"].encode("utf-8"))
        if item["issuCmpyKsdCustNo"] == target_custody:
            continue
        descriptors.append({
            "basDt": "20240131",
            "custody_key_sha256": custody_hash,
            "global_row_ordinal": ordinal,
            "observed_identity_sha256": g11.identity_digest(item),
            "page_item_ordinal": ((ordinal - 1) % 10) + 1,
            "page_no": ((ordinal - 1) // 10) + 1,
        })

    contract = g11.LiveContract(
        correction_head="1" * 40,
        correction_tree="2" * 40,
        owner_blob="3" * 40,
        owner_sha256="4" * 64,
        primary_dates=("20240102", "20240131"),
        checkpoint_binding=checkpoint_binding,
        raw_bindings=raw_bindings,
        seed_base_date="20240131",
        first_new_page=5,
        seed_total_count=41,
        seed_expected_pages=5,
        seed_source_rows=40,
        seed_eligible_rows=35,
        seed_excluded_rows=5,
        excluded_ordinals=(36, 37, 38, 39, 40),
        selector_sha256=g11.sha256_bytes(target_custody.encode("utf-8")),
        frozen_identity_sha256=g11.identity_digest(target_frozen),
        observed_identity_sha256=g11.identity_digest(target_observed),
        eligible_projection_sha256=g11.sha256_bytes(
            g11.canonical_json_bytes(descriptors)
        ),
        g10_identity_map_sha256=g11.sha256_bytes(
            g11.canonical_json_bytes(identities)
        ),
        request_page_size=10,
        max_pages_per_date=100,
        g11_acquisition_ceiling=10,
        g11_attempt_ceiling=20,
        attempts_per_page=2,
    )
    objects = {
        (checkpoint_binding.key, checkpoint_binding.version_id): g11.VersionedObject(
            key=checkpoint_binding.key,
            version_id=checkpoint_binding.version_id,
            etag=checkpoint_binding.etag,
            body=checkpoint_body,
            content_type=checkpoint_binding.content_type,
            server_side_encryption="AES256",
            metadata={},
        )
    }
    for binding, body in zip(raw_bindings, raw_bodies):
        objects[(binding.key, binding.version_id)] = g11.VersionedObject(
            key=binding.key, version_id=binding.version_id, etag=binding.etag,
            body=body, content_type=binding.content_type,
            server_side_encryption="AES256", metadata={},
        )
    return SyntheticSeed(contract, objects, stable_items, target_custody)


class FakeStore:
    def __init__(
        self, objects: Mapping[tuple[str, str], Any], *,
        exact_mismatch: bool = False,
        claim_error: Exception | None = None,
        fail_raw_ambiguous: bool = False,
        terminal_error: Exception | None = None,
        fail_block_checkpoint_ambiguous: bool = False,
    ) -> None:
        self.objects = dict(objects)
        self.exact_mismatch = exact_mismatch
        self.claim_error = claim_error
        self.fail_raw_ambiguous = fail_raw_ambiguous
        self.terminal_error = terminal_error
        self.fail_block_checkpoint_ambiguous = fail_block_checkpoint_ambiguous
        self.actions: list[tuple[str, str]] = []
        self.current: dict[str, Any] = {}
        self.api_calls = {"get": 0, "put": 0, "other": 0}
        self._counter = 0

    def exact_read(self, binding: Any) -> Any:
        self.actions.append(("exact_read", binding.key))
        self.api_calls["get"] += 1
        observed = self.objects[(binding.key, binding.version_id)]
        if self.exact_mismatch:
            self.exact_mismatch = False
            return g11.VersionedObject(
                key=observed.key, version_id=observed.version_id,
                etag=observed.etag, body=observed.body + b"x",
                content_type=observed.content_type,
                server_side_encryption=observed.server_side_encryption,
                metadata=observed.metadata,
            )
        return observed

    def pre_mutation_gate(self) -> None:
        self.actions.append(("pre_mutation_gate", "three-bounded-lists"))
        self.api_calls["other"] += 3

    def _write(
        self, operation: str, key: str, body: bytes,
        content_type: str, metadata: Mapping[str, str],
    ) -> Any:
        self.actions.append((operation, key))
        self.api_calls["put"] += 1
        if key == g11.EXECUTION_CLAIM_KEY and self.claim_error is not None:
            raise self.claim_error
        if self.fail_raw_ambiguous and key.startswith(g11.G11C1_RAW_PREFIX):
            raise g11.AmbiguousSideEffectError("S3_WRITE_EFFECT_AMBIGUOUS")
        if key == g11.G11C1_TERMINAL_RECEIPT_KEY and self.terminal_error is not None:
            raise self.terminal_error
        if (
            self.fail_block_checkpoint_ambiguous
            and key == g11.G11C1_CHECKPOINT_KEY
            and json.loads(body).get("state") == "BLOCKED"
        ):
            raise g11.AmbiguousSideEffectError("CHECKPOINT_WRITE_EFFECT_AMBIGUOUS")
        self._counter += 1
        observed = g11.VersionedObject(
            key=key, version_id=f"new-version-{self._counter}",
            etag=f'"new-etag-{self._counter}"', body=body,
            content_type=content_type, server_side_encryption="AES256",
            metadata=dict(metadata),
        )
        self.current[key] = observed
        # The production adapter performs an exact readback after every put.
        self.api_calls["get"] += 1
        return observed

    def create_once(
        self, key: str, body: bytes, *, content_type: str,
        metadata: Mapping[str, str],
    ) -> Any:
        if key in self.current:
            self.api_calls["put"] += 1
            raise g11.CustodyError("S3_CONDITIONAL_CREATE_FAILED")
        return self._write("create_once", key, body, content_type, metadata)

    def compare_and_swap(
        self, key: str, body: bytes, *, expected_etag: str,
        content_type: str, metadata: Mapping[str, str],
    ) -> Any:
        if key not in self.current or self.current[key].etag != expected_etag:
            self.api_calls["put"] += 1
            raise g11.CustodyError("CHECKPOINT_CAS_FAILED")
        return self._write("compare_and_swap", key, body, content_type, metadata)


class FakeProvider:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, str]] = []

    def fetch_once(self, params: Mapping[str, str]) -> Any:
        self.calls.append(dict(params))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _response(body: bytes, status: int = 200, *, received: str = FIXED_TIME) -> Any:
    return g11.ProviderResponse(
        body=body, http_status=status,
        socket_opened_at_utc=FIXED_TIME,
        response_received_at_utc=received,
        safe_headers={"content-type": "application/json"},
    )


def _adapter(seed: SyntheticSeed, store: FakeStore, provider: FakeProvider, **kwargs: Any) -> Any:
    return g11.G11LiveAdapter(
        contract=kwargs.pop("contract", seed.contract), governance=None,
        store=store, provider=provider,
        clock=kwargs.pop("clock", lambda: FIXED_NOW),
        invocation_nonce="a" * 64,
        **kwargs,
    )


def test_success_starts_page_five_after_exact_reads_and_namespace_gate() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    page_five = _entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])])
    provider = FakeProvider([_response(page_five)])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 0
    assert result["verdict"] == "PASS"
    assert provider.calls == [{
        "basDt": "20240131", "issuCmpyKsdCustNo": "", "numOfRows": "10",
        "pageNo": "5", "resultType": "json", "stckIssuCmpyNm": "",
    }]
    assert [kind for kind, _ in store.actions[:6]] == [
        "exact_read", "exact_read", "exact_read", "exact_read", "exact_read",
        "pre_mutation_gate",
    ]
    assert store.actions[6] == ("create_once", g11.EXECUTION_CLAIM_KEY)
    assert result["projection"]["source_rows"] == 41
    assert result["projection"]["eligible_rows"] == 36
    assert result["projection"]["excluded_rows"] == 5
    effects = result["effects"]
    assert effects["primary_acquisitions"] == 1
    assert effects["network_attempts"] == 1
    assert effects["raw_writes"] == 1
    assert effects["execution_claim_writes"] == 1
    assert effects["terminal_receipt_writes"] == 1
    assert effects["s3_other_calls"] == 3
    assert effects["company_master_or_universe_mutations"] == 0
    assert effects["repository_mutations_by_workflow"] == 0
    assert effects["github_actions_artifacts_uploaded"] == 0
    assert result["execution_claim_binding"]["key"] == g11.EXECUTION_CLAIM_KEY
    assert result["checkpoint_binding"]["key"] == g11.G11C1_CHECKPOINT_KEY
    terminal = result["terminal_receipt_binding"]
    assert terminal["attempted"] is True
    assert terminal["put_attempts"] == 1
    assert terminal["confirmed"] is True
    assert terminal["object"]["key"] == g11.G11C1_TERMINAL_RECEIPT_KEY
    assert terminal["object"]["sha256"] == g11.sha256_bytes(
        store.current[g11.G11C1_TERMINAL_RECEIPT_KEY].body
    )
    assert terminal["object"]["server_side_encryption"] == "AES256"
    serialized = json.dumps(result, ensure_ascii=False)
    assert "Issuer-01" not in serialized
    assert g11.FORBIDDEN_CLEAR_KEYS.isdisjoint(set(result))


def test_stale_kst_day_has_no_reads_provider_calls_or_writes() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    provider = FakeProvider([])
    stale = datetime(2026, 9, 2, 0, 0, tzinfo=timezone.utc)

    exit_code, result = _adapter(seed, store, provider, clock=lambda: stale).run()

    assert exit_code == 2
    assert result["error"]["code"] == "FROZEN_KST_QUOTA_DAY_CLOSED"
    assert store.actions == []
    assert provider.calls == []
    assert result["effects"]["aws_calls"] == 0
    assert result["effects"]["remote_custody_mutations"] == 0


def test_naive_runtime_clock_fails_before_any_effect() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    provider = FakeProvider([])

    exit_code, result = _adapter(
        seed, store, provider,
        clock=lambda: datetime(2026, 9, 1, 3, 0, 0),
    ).run()

    assert exit_code == 2
    assert result["error"]["code"] == "CLOCK_MUST_BE_TIMEZONE_AWARE"
    assert store.actions == []
    assert provider.calls == []


def test_kst_day_crossing_during_read_gates_stops_before_claim() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    provider = FakeProvider([])
    times = iter([
        FIXED_NOW,
        datetime(2026, 9, 1, 15, 1, tzinfo=timezone.utc),
    ])

    exit_code, result = _adapter(
        seed, store, provider, clock=lambda: next(times),
    ).run()

    assert exit_code == 2
    assert result["error"]["code"] == "FROZEN_KST_QUOTA_DAY_CLOSED_BEFORE_CLAIM"
    assert [kind for kind, _ in store.actions] == [
        "exact_read", "exact_read", "exact_read", "exact_read", "exact_read",
        "pre_mutation_gate",
    ]
    assert provider.calls == []
    assert result["effects"]["execution_claim_writes"] == 0
    assert result["effects"]["remote_custody_mutations"] == 0


def test_exact_predecessor_mismatch_fails_before_gate_or_mutation() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects, exact_mismatch=True)
    provider = FakeProvider([])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "EXACT_OBJECT_VERSION_BINDING_MISMATCH"
    assert [kind for kind, _ in store.actions] == ["exact_read"]
    assert provider.calls == []
    assert result["effects"]["execution_claim_writes"] == 0


def test_claim_contention_is_unambiguous_and_precedes_provider() -> None:
    seed = _synthetic_seed()
    store = FakeStore(
        seed.objects,
        claim_error=g11.CustodyError("S3_CONDITIONAL_CREATE_FAILED"),
    )
    provider = FakeProvider([])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "S3_CONDITIONAL_CREATE_FAILED"
    assert provider.calls == []
    assert result["effects"]["execution_claim_writes"] == 0
    assert result["effect_reconciliation"] == {
        "complete": True, "ambiguous_side_effects": False,
    }


def test_future_selector_is_raw_custodied_then_stops_without_cursor_advance() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    target = _item(seed.target_custody, "TARGET-CRNO-A", "Target-A")
    provider = FakeProvider([_response(_entity(5, 41, [target]))])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION"
    assert result["effects"]["provider_calls"] == 1
    assert result["effects"]["raw_writes"] == 1
    assert result["next_resume_cursor"] == {"basDt": "20240131", "page_no": 5}
    assert result["projection"]["source_rows"] == 40
    assert result["projection"]["excluded_rows"] == 5
    assert result["projection"]["future_selector_observed"] is True
    assert result["projection"]["future_selector_auto_excluded"] is False
    assert any(
        kind == "create_once" and key.startswith(g11.G11C1_RAW_PREFIX)
        for kind, key in store.actions
    )


def test_page_semantic_failures_occur_after_raw_custody() -> None:
    cases = [
        (_entity(5, 42, [_item("1001", "CRNO-01", "Issuer-01")]),
         "PAGINATION_SNAPSHOT_DRIFT"),
        (_entity(5, 41, [_item("1001", "DIFFERENT", "Issuer-01")]),
         "NON_TARGET_IDENTITY_CONFLICT"),
        (_entity(5, 41, [_item("1001", "CRNO-01", "")]),
         "NON_TARGET_IDENTITY_MISSING_OR_BLANK"),
    ]
    for body, error_code in cases:
        seed = _synthetic_seed()
        store = FakeStore(seed.objects)
        provider = FakeProvider([_response(body)])

        exit_code, result = _adapter(seed, store, provider).run()

        assert exit_code == 2
        assert result["error"]["code"] == error_code
        assert result["effects"]["raw_writes"] == 1
        assert result["next_resume_cursor"]["page_no"] == 5


def test_response_crossing_kst_is_raw_custodied_before_fail_closed() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects)
    page_five = _entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])])
    next_kst_day = datetime(2026, 9, 1, 15, 1, tzinfo=timezone.utc).isoformat()
    provider = FakeProvider([_response(page_five, received=next_kst_day)])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "RESPONSE_CROSSED_FROZEN_KST_QUOTA_DAY"
    assert result["effects"]["raw_writes"] == 1
    assert result["next_resume_cursor"]["page_no"] == 5


def test_raw_write_ceiling_stops_retry_before_second_provider_call() -> None:
    seed = _synthetic_seed()
    contract = replace(seed.contract, g11_acquisition_ceiling=1)
    store = FakeStore(seed.objects)
    retry = _response(_entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])]), 500)
    provider = FakeProvider([retry, retry])

    exit_code, result = _adapter(seed, store, provider, contract=contract).run()

    assert exit_code == 2
    assert result["error"]["code"] == "G11C1_RAW_WRITE_CEILING"
    assert len(provider.calls) == 1
    assert result["effects"]["raw_writes"] == 1
    assert result["effects"]["network_attempts"] == 2


def test_ambiguous_raw_write_marks_effect_reconciliation_incomplete() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects, fail_raw_ambiguous=True)
    page_five = _entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])])
    provider = FakeProvider([_response(page_five)])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "S3_WRITE_EFFECT_AMBIGUOUS"
    assert result["effect_reconciliation"] == {
        "complete": False, "ambiguous_side_effects": True,
    }
    assert result["effects"]["effects_reconciled"] is False
    assert result["effects"]["ambiguous_side_effects"] is True
    assert result["effects"]["terminal_receipt_put_attempts"] == 0
    assert store.actions[-1][1].startswith(g11.G11C1_RAW_PREFIX)


def test_known_terminal_put_failure_is_attempted_only_once() -> None:
    seed = _synthetic_seed()
    store = FakeStore(
        seed.objects,
        terminal_error=g11.ConditionalWriteConflict(
            "S3_CONDITIONAL_CREATE_FAILED"
        ),
    )
    page_five = _entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])])
    provider = FakeProvider([_response(page_five)])

    exit_code, result = _adapter(seed, store, provider).run()

    terminal_actions = [
        action for action in store.actions if action[1] == g11.G11C1_TERMINAL_RECEIPT_KEY
    ]
    assert exit_code == 2
    assert result["error"]["code"] == "S3_CONDITIONAL_CREATE_FAILED"
    assert len(terminal_actions) == 1
    assert result["effects"]["terminal_receipt_put_attempts"] == 1
    assert result["effects"]["terminal_receipt_writes"] == 0
    assert result["terminal_receipt_binding"] == {
        "key": g11.G11C1_TERMINAL_RECEIPT_KEY,
        "attempted": True, "put_attempts": 1,
        "confirmed": False, "object": None,
    }
    assert result["effect_reconciliation"]["complete"] is True


def test_ambiguous_terminal_put_causes_no_follow_on_mutation_or_retry() -> None:
    seed = _synthetic_seed()
    store = FakeStore(
        seed.objects,
        terminal_error=g11.AmbiguousSideEffectError("S3_WRITE_EFFECT_AMBIGUOUS"),
    )
    page_five = _entity(5, 41, [copy.deepcopy(seed.stable_items["1001"])])
    provider = FakeProvider([_response(page_five)])

    exit_code, result = _adapter(seed, store, provider).run()

    terminal_positions = [
        index for index, action in enumerate(store.actions)
        if action[1] == g11.G11C1_TERMINAL_RECEIPT_KEY
    ]
    assert exit_code == 2
    assert terminal_positions == [len(store.actions) - 1]
    assert result["effects"]["terminal_receipt_put_attempts"] == 1
    assert result["effects"]["terminal_receipt_writes"] == 0
    assert result["terminal_receipt_binding"]["confirmed"] is False
    assert result["effect_reconciliation"]["complete"] is False
    assert result["effect_reconciliation"]["ambiguous_side_effects"] is True


def test_ambiguous_block_checkpoint_stops_before_terminal_receipt() -> None:
    seed = _synthetic_seed()
    store = FakeStore(seed.objects, fail_block_checkpoint_ambiguous=True)
    target = _item(seed.target_custody, "TARGET-CRNO-A", "Target-A")
    provider = FakeProvider([_response(_entity(5, 41, [target]))])

    exit_code, result = _adapter(seed, store, provider).run()

    assert exit_code == 2
    assert result["error"]["code"] == "CHECKPOINT_WRITE_EFFECT_AMBIGUOUS"
    assert result["effect_reconciliation"]["complete"] is False
    assert result["effects"]["terminal_receipt_put_attempts"] == 0
    assert all(key != g11.G11C1_TERMINAL_RECEIPT_KEY for _, key in store.actions)
    assert store.actions[-1][1] == g11.G11C1_CHECKPOINT_KEY


def test_public_runner_interface_is_stable() -> None:
    entrypoint = g11.build_live_adapter()
    assert g11.ADAPTER_INTERFACE_VERSION == (
        "M3TOP3_FINANCE_CA_PAGE100_G11C1_LIVE_ADAPTER_v1.0"
    )
    assert g11.FACTORY_SYMBOL == "create_sealed_g11c1_custody_adapter"
    assert entrypoint.interface_version == g11.ADAPTER_INTERFACE_VERSION
    assert callable(entrypoint.execute)
    rejected = entrypoint.execute({})
    assert rejected["exit_code"] == g11.EX_CONFIG
    assert rejected["verdict"] == "FAIL_CLOSED"
    assert rejected["entry_gate"] == "LIVE_NOT_ENTERED"
    assert rejected["effects"]["effects_reconciled"] is True
    assert rejected["effect_reconciliation"]["complete"] is True
    assert rejected["no_rerun"] == {
        "same_run_retry_authorized": False,
        "same_activation_reuse_authorized": False,
        "same_latch_reuse_authorized": False,
    }


def test_consumed_g11_runs_are_in_successor_no_rerun_lineage() -> None:
    assert 33465583987 in g11.REQUIRED_NO_RERUN_RUNS
    assert 33466306591 in g11.REQUIRED_NO_RERUN_RUNS
    assert g11.OWNER_CAP_SPEC_SHA256 == (
        "5eae2419731d045b6dbaa8795a42c430d0efc42b54f897a1618b09c4573ccde2"
    )
    assert g11.EXECUTION_TOKEN_SHA256 == (
        "a9bd3a1bfacd0a04e9ab76b80aa4ec3f795258251fdc30b37409ca5a8c56fec6"
    )


def test_terminal_execution_binding_uses_validated_runtime_head_and_tree() -> None:
    seed = _synthetic_seed()
    roles = (
        "authority", "plan", "seed", "manifest", "owner_decision",
        "live_activation", "precheck_receipt",
    )
    raw = {role: g11.canonical_json_bytes({"role": role}) for role in roles}
    governance = g11.GovernanceBundle(
        documents={role: {} for role in roles}, raw=raw,
        sha256={role: g11.sha256_bytes(raw[role]) for role in roles},
        paths={role: Path(f"{role}.json") for role in roles},
        github_run_id=123456, github_run_attempt=1,
        live_head_sha="a" * 40, live_head_tree="b" * 40,
    )
    adapter = g11.G11LiveAdapter(
        contract=seed.contract, governance=governance,
        store=FakeStore(seed.objects), provider=FakeProvider([]),
        clock=lambda: FIXED_NOW, invocation_nonce="a" * 64,
    )

    result = adapter._result("FAIL_CLOSED")

    assert result["execution_binding"]["head_sha"] == "a" * 40
    assert result["execution_binding"]["tree_sha"] == "b" * 40
    assert "BOUND_BY_" not in json.dumps(result, sort_keys=True)


def test_proven_s3_precondition_failure_is_not_marked_ambiguous() -> None:
    def conflict(command: Any) -> Any:
        return subprocess.CompletedProcess(
            command, 1, "",
            "An error occurred (PreconditionFailed) when calling PutObject: 412",
        )

    store = g11.AwsCliS3ObjectStore(command_runner=conflict)
    try:
        store.create_once(
            g11.EXECUTION_CLAIM_KEY, b"{}\n",
            content_type="application/json", metadata={"sha256": "0" * 64},
        )
    except g11.ConditionalWriteConflict as exc:
        assert exc.code == "S3_CONDITIONAL_CREATE_FAILED"
    else:
        raise AssertionError("expected a proven conditional write conflict")
    assert store.api_calls == {"get": 0, "put": 1, "other": 0}


def test_namespace_list_gate_requires_exact_empty_nontruncated_shape() -> None:
    def valid_payload(prefix: str) -> dict[str, Any]:
        return {
            "IsTruncated": False, "Prefix": prefix, "MaxKeys": 2,
            "Versions": [], "DeleteMarkers": [],
        }

    seen: list[str] = []

    def valid_runner(command: Any) -> Any:
        prefix = command[command.index("--prefix") + 1]
        seen.append(prefix)
        return subprocess.CompletedProcess(
            command, 0, json.dumps(valid_payload(prefix)), "",
        )

    valid_store = g11.AwsCliS3ObjectStore(command_runner=valid_runner)
    valid_store.pre_mutation_gate()
    assert seen == [g11.G11C1_RAW_PREFIX, g11.G11C1_CONTROL_PREFIX, g11.EXECUTION_CLAIM_KEY]
    assert valid_store.api_calls == {"get": 0, "put": 0, "other": 3}

    malformed_payloads = [
        {},
        {"Prefix": g11.G11C1_RAW_PREFIX, "MaxKeys": 2,
         "Versions": [], "DeleteMarkers": []},
        {**valid_payload(g11.G11C1_RAW_PREFIX), "Prefix": "wrong/"},
        {**valid_payload(g11.G11C1_RAW_PREFIX), "IsTruncated": "false"},
        {**valid_payload(g11.G11C1_RAW_PREFIX), "IsTruncated": True},
        {**valid_payload(g11.G11C1_RAW_PREFIX), "Versions": [{}]},
        {**valid_payload(g11.G11C1_RAW_PREFIX), "DeleteMarkers": [{}]},
    ]
    for payload in malformed_payloads:
        def malformed_runner(command: Any, payload: Any = payload) -> Any:
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        store = g11.AwsCliS3ObjectStore(command_runner=malformed_runner)
        try:
            store.pre_mutation_gate()
        except g11.GovernanceError as exc:
            assert exc.code == "FRESH_G11C1_IDENTITY_ALREADY_CONSUMED"
        else:
            raise AssertionError("malformed namespace listing must fail closed")
        assert store.api_calls == {"get": 0, "put": 0, "other": 1}


def test_aws_subprocess_environment_strips_finance_secret() -> None:
    captured: dict[str, Any] = {}
    original_run = subprocess.run
    original_secret = os.environ.get("DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY")

    def fake_run(command: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, "{}", "")

    try:
        os.environ["DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY"] = "secret-value"
        subprocess.run = fake_run  # type: ignore[assignment]
        g11.AwsCliS3ObjectStore._default_runner(["aws", "s3api", "noop"])
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
        if original_secret is None:
            os.environ.pop("DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY", None)
        else:
            os.environ["DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY"] = original_secret
    assert "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY" not in captured["env"]
    assert captured["env"]["AWS_MAX_ATTEMPTS"] == "1"


def _run_direct() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"{len(tests)} focused adapter tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_direct())
