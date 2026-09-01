"""Focused, zero-network tests for the G11C7 append-only LIVE adapter."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ADAPTER_PATH = Path(__file__).resolve().parents[1] / "finance_page100_g11c7_live_adapter.py"
SPEC = importlib.util.spec_from_file_location("g11c7_live_adapter_under_test", ADAPTER_PATH)
assert SPEC is not None and SPEC.loader is not None
g11 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = g11
SPEC.loader.exec_module(g11)

FIXED_NOW = datetime(2026, 9, 1, 3, 0, 0, tzinfo=timezone.utc)
FIXED_TIME = FIXED_NOW.isoformat()


def _credentials(tag: str) -> Any:
    return g11.AwsSessionCredentials(
        f"AKIA-{tag}", f"secret-{tag}", f"token-{tag}",
    )


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
        if self.fail_raw_ambiguous and key.startswith(g11.G11C7_RAW_PREFIX):
            raise g11.AmbiguousSideEffectError("S3_WRITE_EFFECT_AMBIGUOUS")
        if key == g11.G11C7_TERMINAL_RECEIPT_KEY and self.terminal_error is not None:
            raise self.terminal_error
        if (
            self.fail_block_checkpoint_ambiguous
            and key == g11.G11C7_CHECKPOINT_KEY
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


def _assert_three_session_effects(effects: Mapping[str, Any]) -> None:
    assert effects["sts_calls"] == 6
    assert effects["sts_assume_role_attempts"] == 3
    assert effects["sts_sessions_assumed"] == 3
    assert effects["sts_get_caller_identity_calls"] == 3
    assert effects["credentials_issued"] == 3
    assert effects["aws_calls"] == 6 + effects["s3_calls"]


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
    assert effects["s3_calls"] == sum(store.api_calls.values())
    _assert_three_session_effects(effects)
    assert effects["company_master_or_universe_mutations"] == 0
    assert effects["repository_mutations_by_workflow"] == 0
    assert effects["github_actions_artifacts_uploaded"] == 0
    assert result["execution_claim_binding"]["key"] == g11.EXECUTION_CLAIM_KEY
    assert result["checkpoint_binding"]["key"] == g11.G11C7_CHECKPOINT_KEY
    terminal = result["terminal_receipt_binding"]
    assert terminal["attempted"] is True
    assert terminal["put_attempts"] == 1
    assert terminal["confirmed"] is True
    assert terminal["object"]["key"] == g11.G11C7_TERMINAL_RECEIPT_KEY
    assert terminal["object"]["sha256"] == g11.sha256_bytes(
        store.current[g11.G11C7_TERMINAL_RECEIPT_KEY].body
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
    assert result["effects"]["s3_calls"] == 0
    _assert_three_session_effects(result["effects"])
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
        kind == "create_once" and key.startswith(g11.G11C7_RAW_PREFIX)
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
    assert result["error"]["code"] == "G11C7_RAW_WRITE_CEILING"
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
    assert store.actions[-1][1].startswith(g11.G11C7_RAW_PREFIX)


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
        action for action in store.actions if action[1] == g11.G11C7_TERMINAL_RECEIPT_KEY
    ]
    assert exit_code == 2
    assert result["error"]["code"] == "S3_CONDITIONAL_CREATE_FAILED"
    assert len(terminal_actions) == 1
    assert result["effects"]["terminal_receipt_put_attempts"] == 1
    assert result["effects"]["terminal_receipt_writes"] == 0
    assert result["terminal_receipt_binding"] == {
        "key": g11.G11C7_TERMINAL_RECEIPT_KEY,
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
        if action[1] == g11.G11C7_TERMINAL_RECEIPT_KEY
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
    assert all(key != g11.G11C7_TERMINAL_RECEIPT_KEY for _, key in store.actions)
    assert store.actions[-1][1] == g11.G11C7_CHECKPOINT_KEY


def test_public_runner_interface_is_stable() -> None:
    entrypoint = g11.build_live_adapter()
    assert g11.ADAPTER_INTERFACE_VERSION == (
        "M3TOP3_FINANCE_CA_PAGE100_G11C7_LIVE_ADAPTER_v1.0"
    )
    assert g11.FACTORY_SYMBOL == "create_sealed_g11c7_custody_adapter"
    assert entrypoint.interface_version == g11.ADAPTER_INTERFACE_VERSION
    assert callable(entrypoint.execute)
    rejected = entrypoint.execute({})
    assert rejected["exit_code"] == g11.EX_CONFIG
    assert rejected["verdict"] == "FAIL_CLOSED"
    assert rejected["entry_gate"] == "LIVE_NOT_ENTERED"
    assert rejected["effects"]["s3_calls"] == 0
    _assert_three_session_effects(rejected["effects"])
    assert rejected["effects"]["effects_reconciled"] is True
    assert rejected["effect_reconciliation"]["complete"] is True
    assert rejected["no_rerun"] == {
        "same_run_retry_authorized": False,
        "same_activation_reuse_authorized": False,
        "same_latch_reuse_authorized": False,
    }


def test_consumed_g11_through_g11c6_are_in_successor_no_rerun_lineage() -> None:
    assert g11.REQUIRED_NO_RERUN_RUNS == (
        33272691259, 33273146915, 33401871715, 33403101817,
        33414615913, 33414695818, 33465583987, 33466306591,
        33469887723, 33472741288, 33473465774, 33477019917,
        33479444941, 33484842311,
    )
    assert g11.OWNER_CAP_SPEC_SHA256 == "6bf86c75cc675ff5b72739e52155317505cc5dda32e9d61fa04a7392a8041aa6"
    assert g11.EXECUTION_TOKEN_SHA256 == "4213f2a26fe8f1557e35c2150ef20aab777adb609e6977c5d0e7291f2d76c89c"
    assert g11.PREDECESSOR_G11C1_PREPARATION_COMMIT == (
        "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09"
    )
    assert "FINANCE-PAGE100-G11C1-20260901123521" in (
        g11.PREDECESSOR_G11C1_IDENTITIES["consumed_generation_ids"]
    )
    assert "FINANCE-PAGE100-G11C2-20260901130250" in (
        g11.PREDECESSOR_G11C2_IDENTITIES["consumed_generation_ids"]
    )
    assert g11.PREDECESSOR_G11C2_INVALIDATION_RECEIPT_SHA256 == (
        "b7e03464f1f2c53a7446901b88ccb2aa481f940c272970f24cccbb5be1523df6"
    )
    assert "FINANCE-PAGE100-G11C3-20260901134119" in (
        g11.PREDECESSOR_G11C3_IDENTITIES["consumed_generation_ids"]
    )
    assert g11._predecessor_terminal_g11c3_binding()["credentials_issued"] is False
    assert g11._predecessor_terminal_g11c3_binding()["runner_started"] is False
    assert "FINANCE-PAGE100-G11C4-20260901143300" in (
        g11.PREDECESSOR_G11C4_IDENTITIES["consumed_generation_ids"]
    )
    assert "FINANCE-PAGE100-G11C4-PREPARATION-20260901143300" in (
        g11.PREDECESSOR_G11C4_IDENTITIES["consumed_preparation_ids"]
    )
    c4_terminal = g11._predecessor_terminal_g11c4_binding()
    assert set(c4_terminal) == {
        "generation_id", "runtime_lock_id", "pilot_run_id", "preparation_id",
        "precheck_act_id", "live_act_id", "latch_event_id",
        "terminal_receipt_append_commit", "terminal_receipt_append_tree",
        "terminal_receipt_path", "terminal_receipt_git_blob",
        "terminal_receipt_sha256", "terminal_receipt_payload_sha256",
        "terminal_receipt_bytes", "execution_head_sha", "execution_tree_sha",
        "precheck_run_id", "precheck_job_id", "run_attempt", "result",
        "terminal_state", "entry_gate", "oidc_token_requests", "aws_calls",
        "sts_calls", "sts_assume_role_attempts", "sts_assume_role_successes",
        "sts_sessions_assumed", "sts_get_caller_identity_calls",
        "credentials_issued", "probe_2_started", "probe_3_started",
        "runner_started", "s3_calls", "provider_calls", "quota_reservations",
        "remote_custody_mutations", "repository_mutations_by_workflow",
        "all_downstream_effects_zero", "live_execution_started",
        "same_run_retry_authorized", "reuse_authorized",
    }
    assert c4_terminal["entry_gate"] == (
        "FAIL_CLOSED_PRECHECK_PROBE_1_STS_AUTHORIZATION_FAILURE"
    )
    assert c4_terminal["aws_calls"] == 1
    assert c4_terminal["sts_assume_role_successes"] == 0
    assert c4_terminal["credentials_issued"] == 0
    assert c4_terminal["probe_2_started"] is False
    assert c4_terminal["probe_3_started"] is False
    assert c4_terminal["runner_started"] is False
    assert c4_terminal["all_downstream_effects_zero"] is True
    assert c4_terminal["live_execution_started"] is False
    assert c4_terminal["same_run_retry_authorized"] is False
    c5_terminal = g11._predecessor_terminal_g11c5_binding()
    assert c5_terminal["terminal_receipt_append_commit"] == (
        "d0061e9005a74817563588990064af4260ab2bd9"
    )
    assert c5_terminal["terminal_receipt_append_tree"] == (
        "7ba82af78770b8fdcfb914ab080bd280f017918f"
    )
    assert c5_terminal["terminal_receipt_git_blob"] == (
        "a3d29884a44ca4dac88b9d47bf2447fe24aa0b08"
    )
    assert c5_terminal["terminal_receipt_sha256"] == (
        "c518d4ac79b6e7735eae9fe3a799ae7ea29dd4c357508ddd4c85e2d09711b30e"
    )
    assert c5_terminal["terminal_receipt_payload_sha256"] == (
        "332d15f75b2f7843046f0eb5d8983fdb3791cef3fa6155803828e1d74008049f"
    )
    assert c5_terminal["terminal_receipt_bytes"] == 50220
    assert c5_terminal["precheck_run_id"] == 33479444941
    assert c5_terminal["precheck_job_id"] == 99765558713
    assert c5_terminal["execution_head_sha"] == (
        "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
    )
    assert c5_terminal["execution_tree_sha"] == (
        "53d13cccc42aae8f4b21adebee3ed71190ba1954"
    )
    assert c5_terminal["precheck_execution_result"] == "PASS"
    assert c5_terminal["result"] == "FAIL_CLOSED"
    assert c5_terminal["terminal_receipt_contract_valid"] is False
    assert c5_terminal["credentials_issued"] == 3
    assert "runner_started" not in c5_terminal
    c6_terminal = g11._predecessor_terminal_g11c6_binding()
    assert c6_terminal == g11.PREDECESSOR_G11C6_BINDING
    assert c6_terminal["terminal_receipt_append_commit"] == (
        "56f2a2fc109da0167010dce64c3697d5051636d3"
    )
    assert c6_terminal["terminal_receipt_append_tree"] == (
        "a868ca84f516dc43f30329c267e3209f940ce2bf"
    )
    assert c6_terminal["terminal_receipt_git_blob"] == (
        "08583e511d62cde662b668fa78cfe4f1a4787572"
    )
    assert c6_terminal["terminal_receipt_sha256"] == (
        "d1d4ed8edbc670990b2eea1c13f9681f17f1a1ae0771fb062c20900346a22867"
    )
    assert c6_terminal["terminal_receipt_payload_sha256"] == (
        "50581e61f50e9526ecc945900fd545047761c7ecfe95e18ee49717c3037734ce"
    )
    assert c6_terminal["terminal_receipt_bytes"] == 44284
    assert c6_terminal["precheck_run_id"] == 33484842311
    assert c6_terminal["precheck_job_id"] == 99782407546
    assert c6_terminal["execution_head_sha"] == (
        "a08938730b95843125b18950abc27af1d48839ba"
    )
    assert c6_terminal["execution_tree_sha"] == (
        "8ac1f1d29c82c0b240559b758cabde22c4ca93d1"
    )
    assert c6_terminal["runner_started"] is False
    assert c6_terminal["credentials_issued"] == 0
    assert c6_terminal["all_effects_zero"] is True
    authority_path = (
        Path(__file__).resolve().parents[3]
        / "control/m3top3/public-data-source-admission/v1.0"
        / "M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_AUTHORITY_v1.0.json"
    )
    authority_no_rerun = json.loads(
        authority_path.read_text(encoding="utf-8")
    )["no_rerun"]
    g11._validate_consumed_predecessor_identities(
        authority_no_rerun, "TEST_G11C6_NO_RERUN_LINEAGE_MISMATCH"
    )
    assert authority_no_rerun["g11c6_precheck_job_id"] == 99782407546
    for field_name in (
        "g11c6_runtime_lock_reuse_authorized",
        "g11c6_pilot_run_id_reuse_authorized",
        "g11c6_precheck_act_id_reuse_authorized",
        "g11c6_live_act_id_reuse_authorized",
        "g11c6_latch_event_id_reuse_authorized",
    ):
        assert authority_no_rerun[field_name] is False
    assert g11.ACTIVATION_BASE_HEAD_COMMIT == (
        "56f2a2fc109da0167010dce64c3697d5051636d3"
    )
    assert g11.ACTIVATION_BASE_TREE == "a868ca84f516dc43f30329c267e3209f940ce2bf"


def test_live_session_policy_exact_semantics_ascii_and_size_gate() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        policy_path = Path(temporary_directory) / "live-policy.json"
        policies = g11.expected_split_session_policies()
        for role, policy in policies.items():
            policy_path.write_text(
                json.dumps(policy, sort_keys=True) + "\n", encoding="ascii",
            )
            exact_length = g11.validate_live_session_policy_for_aws(policy_path, role)
            assert exact_length <= 2048

        forbidden_version = copy.deepcopy(policies["checkpoint_read_session_policy"])
        forbidden_version["Version"] = "2012-10-17"
        policy_path.write_text(
            json.dumps(forbidden_version, sort_keys=True) + "\n", encoding="ascii"
        )
        try:
            g11.validate_live_session_policy_for_aws(
                policy_path, "checkpoint_read_session_policy"
            )
        except g11.GovernanceError as exc:
            assert exc.code == "LIVE_SESSION_POLICY_VERSION_MUST_BE_OMITTED"
        else:
            raise AssertionError("Version-bearing G11C7 policy must fail closed")


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
        if command[2] == "list-object-versions":
            prefix = command[command.index("--prefix") + 1]
            return subprocess.CompletedProcess(command, 0, json.dumps({
                "IsTruncated": False, "Prefix": prefix, "MaxKeys": 2,
                "Versions": [], "DeleteMarkers": [],
            }), "")
        return subprocess.CompletedProcess(
            command, 1, "",
            "An error occurred (PreconditionFailed) when calling PutObject: 412",
        )

    store = g11.AwsCliS3ObjectStore(
        credential_role=g11.FINAL_LIST_WRITE_ROLE,
        credentials=_credentials("final-conflict"), command_runner=conflict,
    )
    store.pre_mutation_gate()
    try:
        store.create_once(
            g11.EXECUTION_CLAIM_KEY, b"{}\n",
            content_type="application/json", metadata={"sha256": "0" * 64},
        )
    except g11.ConditionalWriteConflict as exc:
        assert exc.code == "S3_CONDITIONAL_CREATE_FAILED"
    else:
        raise AssertionError("expected a proven conditional write conflict")
    assert store.api_calls == {"get": 0, "put": 1, "other": 3}


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

    valid_store = g11.AwsCliS3ObjectStore(
        credential_role=g11.FINAL_LIST_WRITE_ROLE,
        credentials=_credentials("final-valid"), command_runner=valid_runner,
    )
    valid_store.pre_mutation_gate()
    assert seen == [g11.G11C7_RAW_PREFIX, g11.G11C7_CONTROL_PREFIX, g11.EXECUTION_CLAIM_KEY]
    assert valid_store.api_calls == {"get": 0, "put": 0, "other": 3}

    malformed_payloads = [
        {},
        {"Prefix": g11.G11C7_RAW_PREFIX, "MaxKeys": 2,
         "Versions": [], "DeleteMarkers": []},
        {**valid_payload(g11.G11C7_RAW_PREFIX), "Prefix": "wrong/"},
        {**valid_payload(g11.G11C7_RAW_PREFIX), "IsTruncated": "false"},
        {**valid_payload(g11.G11C7_RAW_PREFIX), "IsTruncated": True},
        {**valid_payload(g11.G11C7_RAW_PREFIX), "Versions": [{}]},
        {**valid_payload(g11.G11C7_RAW_PREFIX), "DeleteMarkers": [{}]},
    ]
    for payload in malformed_payloads:
        def malformed_runner(command: Any, payload: Any = payload) -> Any:
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        store = g11.AwsCliS3ObjectStore(
            credential_role=g11.FINAL_LIST_WRITE_ROLE,
            credentials=_credentials("final-malformed"), command_runner=malformed_runner,
        )
        try:
            store.pre_mutation_gate()
        except g11.GovernanceError as exc:
            assert exc.code == "FRESH_G11C7_IDENTITY_ALREADY_CONSUMED"
        else:
            raise AssertionError("malformed namespace listing must fail closed")
        assert store.api_calls == {"get": 0, "put": 0, "other": 1}


def test_authority_active_prefix_gate_rejects_g11_through_g11c6() -> None:
    g11._validate_active_c7_prefixes(g11.G11C7_RAW_PREFIX, g11.G11C7_CONTROL_PREFIX)
    for historical in ("G11", "G11C1", "G11C2", "G11C3", "G11C4", "G11C5", "G11C6"):
        old_raw = g11.G11C7_RAW_PREFIX.replace("G11C7", historical)
        old_control = g11.G11C7_CONTROL_PREFIX.replace("G11C7", historical)
        try:
            g11._validate_active_c7_prefixes(old_raw, g11.G11C7_CONTROL_PREFIX)
        except g11.GovernanceError as exc:
            assert exc.code == "HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"
        else:
            raise AssertionError(f"{historical} raw prefix must fail closed")
        try:
            g11._validate_active_c7_prefixes(g11.G11C7_RAW_PREFIX, old_control)
        except g11.GovernanceError as exc:
            assert exc.code == "HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"
        else:
            raise AssertionError(f"{historical} control prefix must fail closed")


def test_precheck_receipt_append_and_execution_roles_are_distinct() -> None:
    receipt = {"execution_binding": {"head_sha": "a" * 40, "tree_sha": "b" * 40}}
    binding = {
        "receipt_append_commit": "c" * 40,
        "receipt_append_tree": "d" * 40,
        "execution_head_sha": "a" * 40,
        "execution_head_tree_sha": "b" * 40,
    }
    g11._validate_precheck_pass_role_binding(binding, receipt)

    collapsed = dict(binding)
    collapsed.update({"receipt_append_commit": "a" * 40, "receipt_append_tree": "b" * 40})
    try:
        g11._validate_precheck_pass_role_binding(collapsed, receipt)
    except g11.GovernanceError as exc:
        assert exc.code == "PRECHECK_LINEAGE_ROLES_COLLAPSED"
    else:
        raise AssertionError("collapsed PRECHECK roles must fail closed")

    legacy = {**binding, "commit": "c" * 40, "tree": "d" * 40}
    try:
        g11._validate_precheck_pass_role_binding(legacy, receipt)
    except g11.GovernanceError as exc:
        assert exc.code == "AMBIGUOUS_PRECHECK_LINEAGE_FIELDS_FORBIDDEN"
    else:
        raise AssertionError("legacy ambiguous PRECHECK commit/tree must fail closed")


def test_live_credentials_require_all_nine_and_never_fall_back_to_ambient() -> None:
    assert "CONFIGURED_AWS_ACCOUNT_ID" not in ADAPTER_PATH.read_text(encoding="utf-8")
    ambient = {
        "AWS_ACCESS_KEY_ID": "ambient-access",
        "AWS_SECRET_ACCESS_KEY": "ambient-secret",
        "AWS_SESSION_TOKEN": "ambient-token",
        "AWS_PROFILE": "ambient-profile",
        "AWS_WEB_IDENTITY_TOKEN_FILE": "/tmp/ambient-token",
        "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY": "finance-secret",
    }
    try:
        g11.load_live_credential_bundles(ambient)
    except g11.GovernanceError as exc:
        assert exc.code == "G11C7_EXACT_THREE_CREDENTIAL_BUNDLES_REQUIRED"
    else:
        raise AssertionError("ambient AWS credentials must never satisfy LIVE")

    exact = dict(ambient)
    for ordinal, role in enumerate(g11.AWS_CREDENTIAL_ROLES, 1):
        for suffix, name in zip(("access", "secret", "token"),
                                g11.LIVE_AWS_CREDENTIAL_ENV[role]):
            exact[name] = f"role-{ordinal}-{suffix}"
    bundles = g11.load_live_credential_bundles(exact)
    assert tuple(bundles) == g11.AWS_CREDENTIAL_ROLES
    assert len({bundle.access_key_id for bundle in bundles.values()}) == 3

    aliased = dict(exact)
    aliased[g11.LIVE_AWS_CREDENTIAL_ENV[g11.RAW_READ_ROLE][0]] = (
        aliased[g11.LIVE_AWS_CREDENTIAL_ENV[g11.CHECKPOINT_READ_ROLE][0]]
    )
    try:
        g11.load_live_credential_bundles(aliased)
    except g11.GovernanceError as exc:
        assert exc.code == "G11C7_CREDENTIAL_BUNDLES_MUST_BE_DISTINCT"
    else:
        raise AssertionError("credential components may not alias across roles")

    store = g11.AwsCliS3ObjectStore(
        credential_role=g11.CHECKPOINT_READ_ROLE,
        credentials=bundles[g11.CHECKPOINT_READ_ROLE],
        exact_read_bindings=(g11.PRODUCTION_CONTRACT.checkpoint_binding,),
    )
    command_env = store._command_environment(exact)
    assert command_env["AWS_ACCESS_KEY_ID"] == "role-1-access"
    assert command_env["AWS_SECRET_ACCESS_KEY"] == "role-1-secret"
    assert command_env["AWS_SESSION_TOKEN"] == "role-1-token"
    assert command_env["AWS_EC2_METADATA_DISABLED"] == "true"
    assert "AWS_PROFILE" not in command_env
    assert "AWS_WEB_IDENTITY_TOKEN_FILE" not in command_env
    assert "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY" not in command_env
    assert not any(name in command_env for names in g11.LIVE_AWS_CREDENTIAL_ENV.values()
                   for name in names)


def test_three_clients_route_exact_reads_and_one_way_final_handoff() -> None:
    seed = _synthetic_seed()

    class RecordingClient:
        def __init__(self, role: str, bindings: tuple[Any, ...]) -> None:
            self.credential_role = role
            self.exact_read_bindings = bindings
            self.api_calls = {"get": 0, "put": 0, "other": 0}
            self.actions: list[str] = []

        def exact_read(self, binding: Any) -> Any:
            self.actions.append(f"read:{binding.key}")
            self.api_calls["get"] += 1
            return seed.objects[(binding.key, binding.version_id)]

        def pre_mutation_gate(self) -> None:
            self.actions.append("three-lists")
            self.api_calls["other"] += 3

        def create_once(self, key: str, body: bytes, **_: Any) -> Any:
            self.actions.append(f"create:{key}")
            self.api_calls["put"] += 1
            return g11.VersionedObject(
                key=key, version_id="fresh-version", etag='"fresh-etag"',
                body=body, content_type="application/json",
                server_side_encryption="AES256", metadata={},
            )

        def compare_and_swap(self, key: str, body: bytes, **kwargs: Any) -> Any:
            return self.create_once(key, body, **kwargs)

    checkpoint = RecordingClient(
        g11.CHECKPOINT_READ_ROLE, (seed.contract.checkpoint_binding,)
    )
    raw = RecordingClient(g11.RAW_READ_ROLE, tuple(seed.contract.raw_bindings))
    final = RecordingClient(g11.FINAL_LIST_WRITE_ROLE, ())
    store = g11.PhaseSeparatedS3ObjectStore(
        checkpoint_client=checkpoint, raw_client=raw, final_client=final,
        checkpoint_binding=seed.contract.checkpoint_binding,
        raw_bindings=seed.contract.raw_bindings,
    )
    store.exact_read(seed.contract.checkpoint_binding)
    for binding in seed.contract.raw_bindings:
        store.exact_read(binding)
    store.pre_mutation_gate()
    store.create_once(
        g11.EXECUTION_CLAIM_KEY, b"{}\n", content_type="application/json",
        metadata={},
    )
    assert len(checkpoint.actions) == 1
    assert len(raw.actions) == 4
    assert final.actions == ["three-lists", f"create:{g11.EXECUTION_CLAIM_KEY}"]
    assert store.api_calls == {"get": 5, "put": 1, "other": 3}

    unopened = g11.PhaseSeparatedS3ObjectStore(
        checkpoint_client=RecordingClient(
            g11.CHECKPOINT_READ_ROLE, (seed.contract.checkpoint_binding,)
        ),
        raw_client=RecordingClient(g11.RAW_READ_ROLE, tuple(seed.contract.raw_bindings)),
        final_client=RecordingClient(g11.FINAL_LIST_WRITE_ROLE, ()),
        checkpoint_binding=seed.contract.checkpoint_binding,
        raw_bindings=seed.contract.raw_bindings,
    )
    for operation in (
        lambda: unopened.exact_read(seed.contract.raw_bindings[0]),
        unopened.pre_mutation_gate,
        lambda: unopened.create_once(
            g11.EXECUTION_CLAIM_KEY, b"{}\n",
            content_type="application/json", metadata={},
        ),
    ):
        try:
            operation()
        except g11.GovernanceError:
            pass
        else:
            raise AssertionError("cross-phase or out-of-order call must fail closed")


def test_role_clients_reject_cross_phase_operations_before_aws() -> None:
    contract = g11.PRODUCTION_CONTRACT
    final = g11.AwsCliS3ObjectStore(
        credential_role=g11.FINAL_LIST_WRITE_ROLE,
        credentials=_credentials("final-role"),
    )
    try:
        final.exact_read(contract.checkpoint_binding)
    except g11.GovernanceError as exc:
        assert exc.code == "FINAL_ROLE_PREDECESSOR_READ_FORBIDDEN"
    else:
        raise AssertionError("final client must reject predecessor reads")

    checkpoint = g11.AwsCliS3ObjectStore(
        credential_role=g11.CHECKPOINT_READ_ROLE,
        credentials=_credentials("checkpoint-role"),
        exact_read_bindings=(contract.checkpoint_binding,),
    )
    try:
        checkpoint.create_once(
            g11.EXECUTION_CLAIM_KEY, b"{}\n",
            content_type="application/json", metadata={},
        )
    except g11.GovernanceError as exc:
        assert exc.code == "FINAL_WRITE_PHASE_NOT_OPEN"
    else:
        raise AssertionError("checkpoint client must reject writes")


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
