import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from tools.m3top3 import finance_live_pilot as live
from tools.m3top3 import source_admission as sa


NOW = "2026-08-29T11:00:00+00:00"
PILOT_CLOCK = lambda: datetime(2026, 8, 29, 11, tzinfo=timezone.utc)
WRITER_ID = "github-run:33129999999"
WORKFLOW_ENV = {
    "GITHUB_REPOSITORY": live.AUTHORIZED_GITHUB_REPOSITORY,
    "GITHUB_REF": live.AUTHORIZED_GITHUB_REF,
    "GITHUB_SHA": "1" * 40,
    "GITHUB_ACTOR": live.AUTHORIZED_GITHUB_ACTOR,
    "GITHUB_TRIGGERING_ACTOR": live.AUTHORIZED_GITHUB_ACTOR,
    "GITHUB_RUN_ID": WRITER_ID.split(":", 1)[1],
    "GITHUB_RUN_ATTEMPT": "1",
}


def finance_body(bas_dt, page_no=1, total=0, items=None, page_size=10):
    if items is None:
        items = []
    value = {
        "response": {
            "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
            "body": {
                "numOfRows": str(page_size),
                "pageNo": str(page_no),
                "totalCount": str(total),
                "items": {"item": items},
            },
        }
    }
    return json.dumps(value, separators=(",", ":")).encode()


def response(body, status=200):
    return live.TransportResponse(
        body=body,
        http_status=status,
        safe_headers={"content-type": "application/json"},
        acquired_at_utc=NOW,
    )


class FakeCheckpointStore:
    def __init__(self, fail_once_at=None):
        self.value = None
        self.token = None
        self.cas_calls = 0
        self.fail_once_at = fail_once_at
        self.failed = False
        self.history = []

    def load(self):
        return copy.deepcopy(self.value), self.token

    def compare_and_swap(self, value, expected_token):
        self.cas_calls += 1
        if (
            self.fail_once_at == self.cas_calls
            and not self.failed
        ):
            self.failed = True
            raise sa.CheckpointConflictError("injected CAS crash")
        if expected_token != self.token:
            raise sa.CheckpointConflictError("fake CAS conflict")
        self.value = copy.deepcopy(dict(value))
        self.token = f'"etag-{self.cas_calls}"'
        self.history.append(copy.deepcopy(self.value))
        return self.token


class FakeCustody:
    def __init__(self):
        self.objects = {}
        self.events = []
        self.claim_payload = None

    def acquire_execution_claim(self, claim):
        payload = sa.canonical_json_bytes(dict(claim))
        self.events.append(("claim", claim["writer_id"]))
        if self.claim_payload is not None and self.claim_payload != payload:
            raise sa.CheckpointConflictError("fake single-writer conflict")
        self.claim_payload = payload
        return live.ExecutionClaimEvidence(
            object_key=live.execution_claim_object_key(),
            content_sha256=hashlib.sha256(payload).hexdigest(),
            version_id="claim-version-1",
            etag='"claim-etag-1"',
            server_side_encryption="AES256",
            write_precondition="IF_NONE_MATCH_STAR",
            writer_id=claim["writer_id"],
        )

    def read_existing(self, object_key, version_id=None):
        self.events.append(("read", object_key))
        sealed = self.objects.get(object_key)
        if sealed is not None and version_id is not None:
            if sealed.version_id != version_id:
                raise live.RemoteCustodyError("fake version mismatch")
        return sealed

    def find_existing_by_prefix(self, object_prefix):
        self.events.append(("find", object_prefix))
        matches = [
            value for key, value in self.objects.items()
            if key.startswith(object_prefix)
        ]
        if len(matches) > 1:
            raise live.RemoteCustodyError("multiple fake raw entities")
        return matches[0] if matches else None

    def seal_and_readback(self, object_key, body, metadata):
        self.events.append(("seal", object_key))
        digest = hashlib.sha256(body).hexdigest()
        if metadata["sha256"] != digest:
            raise AssertionError("draft digest mismatch")
        sealed = live.SealedEntity(
            body=body,
            object_key=object_key,
            storage_locator=f"s3://semi-data-plane-aofspds-20260815/{object_key}",
            entity_sha256=digest,
            entity_bytes=len(body),
            readback_sha256=digest,
            readback_bytes=len(body),
            version_id=f"version-{len(self.objects) + 1}",
            etag=f'"{digest[:16]}"',
            server_side_encryption="AES256",
            write_precondition="IF_NONE_MATCH_STAR",
            http_status=int(metadata["http-status"]),
            acquired_at_utc=metadata["acquired-at-utc"],
        )
        prior = self.objects.get(object_key)
        if prior is not None and prior.body != body:
            raise live.RemoteCustodyError("exclusive object mismatch")
        self.objects[object_key] = sealed
        return sealed


class FakeTransport:
    def __init__(self, handler, checkpoint=None):
        self.handler = handler
        self.checkpoint = checkpoint
        self.calls = []

    def fetch_once(self, params):
        params = dict(params)
        if self.checkpoint is not None:
            latest = self.checkpoint.value["attempts"][-1]
            if latest["state"] != "RESERVED_WRITE_AHEAD":
                raise AssertionError("transport called before durable reservation")
        self.calls.append(params)
        return self.handler(params, len(self.calls))


def bindings():
    return live.ExecutionBindings(
        authority_sha256="a" * 64,
        plan_sha256="b" * 64,
        latch_execution_material_sha256="c" * 64,
        runner_sha256="d" * 64,
        source_admission_sha256=live.EXPECTED_SOURCE_ADMISSION_SHA256,
        checkpoint_template_sha256="e" * 64,
        baseline_quota_ledger_sha256="f" * 64,
        baseline_raw_index_sha256="9" * 64,
        github_repository=live.AUTHORIZED_GITHUB_REPOSITORY,
        github_ref=live.AUTHORIZED_GITHUB_REF,
        github_sha=WORKFLOW_ENV["GITHUB_SHA"],
        github_actor=live.AUTHORIZED_GITHUB_ACTOR,
        github_triggering_actor=live.AUTHORIZED_GITHUB_ACTOR,
        github_run_id=int(WORKFLOW_ENV["GITHUB_RUN_ID"]),
        github_run_attempt=int(WORKFLOW_ENV["GITHUB_RUN_ATTEMPT"]),
    )


def empty_handler(params, _ordinal):
    return response(finance_body(params["basDt"], int(params["pageNo"])))


class FinanceLivePilotTests(unittest.TestCase):
    def run_empty(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(empty_handler, checkpoint)
        report = live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=transport,
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=("fixture-secret",),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        return report, checkpoint, custody, transport

    def test_owner_cap_hash_and_deterministic_keys_are_exact(self):
        self.assertEqual(
            hashlib.sha256(
                sa.canonical_json_bytes(live.OWNER_CAP_MATERIAL)
            ).hexdigest(),
            live.OWNER_CAP_SPEC_SHA256,
        )
        prefix = live.deterministic_raw_object_prefix(
            live.PRIMARY_DATES[0], 1, 1
        )
        digest = hashlib.sha256(b"fixture").hexdigest()
        key = live.canonical_raw_object_key(prefix, digest)
        self.assertTrue(
            key.startswith(
                "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
            )
        )
        self.assertIn("quota_day_kst=2026-08-29/", key)
        self.assertIn(
            f"request_id={live.deterministic_request_id('20240102', 1)}/",
            key,
        )
        self.assertIn("attempt=1/", key)
        self.assertTrue(key.endswith(f"sha256={digest}.entity"))
        self.assertNotIn("serviceKey", key)
        self.assertEqual(
            live.checkpoint_object_key(),
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
            "_pilot_control/runtime_lock_id="
            f"{live.RUNTIME_LOCK_ID}/pilot_run_id={live.PILOT_RUN_ID}/"
            "checkpoint.json",
        )

    def test_baseline_quota_binding_is_stable_after_pilot_mirror_append(self):
        rows = []
        for provider, count in (("FINANCE", 5), ("KSD", 2)):
            for ordinal in range(1, count + 1):
                operation = (
                    sa.FINANCE_OPERATION
                    if provider == "FINANCE"
                    else {
                        1: "getIssucoCustnoByShortIsin",
                        2: "getIssucoBasicInfo",
                    }[ordinal]
                )
                rows.append(
                    {
                        "event": "QUOTA_SLOT_SPENT",
                        "provider": provider,
                        "ordinal": ordinal,
                        "operation": operation,
                        "quota_day_kst": live.HISTORICAL_BASELINE_QUOTA_DAY_KST,
                    }
                )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quota.jsonl"
            governed_bytes = (
                b"".join(sa.canonical_json_bytes(row) for row in rows) + b"\n"
            )
            path.write_bytes(governed_bytes)
            first_sha, first_rows = live._read_baseline_quota_ledger(path)
            self.assertEqual(
                first_sha, hashlib.sha256(governed_bytes).hexdigest()
            )
            path.write_bytes(
                path.read_bytes()
                + sa.canonical_json_bytes(
                    {
                        "event": "QUOTA_SLOT_SPENT",
                        "provider": "FINANCE",
                        "ordinal": 1,
                        "operation": sa.FINANCE_OPERATION,
                        "quota_day_kst": live.PILOT_QUOTA_DAY_KST,
                        "pilot_run_id": live.PILOT_RUN_ID,
                    }
                )
            )
            resumed_sha, resumed_rows = live._read_baseline_quota_ledger(path)
        self.assertEqual(first_sha, resumed_sha)
        self.assertEqual(first_rows, resumed_rows)
        self.assertTrue(
            all(
                row["quota_day_kst"] == live.HISTORICAL_BASELINE_QUOTA_DAY_KST
                for row in resumed_rows
            )
        )

        root = Path(__file__).resolve().parents[3]
        governed_quota = (
            root / "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_PUBLIC_DATA_API_QUOTA_LEDGER_v1.0.jsonl"
        )
        self.assertEqual(
            live._governed_baseline_jsonl_sha256(governed_quota),
            "aa1d73613a3ba737837b368ad0b15f0504f0bf35d56f5a81558093b4cc03f607",
        )
        self.assertEqual(
            len(live._read_baseline_quota_ledger(governed_quota)[1]), 7
        )
        governed_raw = (
            root / "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_RAW_CUSTODY_INDEX_v1.0.jsonl"
        )
        self.assertEqual(
            live._governed_baseline_jsonl_sha256(governed_raw),
            hashlib.sha256(governed_raw.read_bytes()).hexdigest(),
        )

    def test_empty_17_date_run_reserves_before_transport_and_stops(self):
        report, checkpoint, custody, transport = self.run_empty()
        self.assertEqual(report["state"], "STOP_NO_PROMOTION_ZERO_DENSITY")
        self.assertEqual(report["completed_date_count"], 17)
        self.assertEqual(len(transport.calls), 17)
        self.assertEqual(checkpoint.value["quota_reservations"], 17)
        self.assertEqual(checkpoint.value["unique_page_slots"][0], "20240102:1")
        self.assertEqual(
            [row["provider_quota_ordinal"] for row in checkpoint.value["attempts"]],
            list(range(1, len(live.PRIMARY_DATES) + 1)),
        )
        self.assertTrue(
            all(row["run_attempt"] == 1 for row in checkpoint.value["attempts"])
        )
        self.assertEqual(len(custody.objects), 17)
        self.assertEqual(checkpoint.value["state"], "COMPLETE")
        self.assertEqual(report["normalization_records_created"], 0)
        self.assertFalse(report["automatic_promotion_performed"])
        self.assertEqual(report["quota"]["quota_day_kst"], "2026-08-29")
        self.assertEqual(report["quota"]["pre_pilot_finance_ordinal"], 0)
        self.assertEqual(report["quota"]["historical_baseline_quota_day_kst"], "2026-08-28")
        self.assertEqual(report["quota"]["historical_baseline_finance_last_ordinal"], 5)
        self.assertEqual(report["quota"]["provider_finance_last_ordinal"], 17)
        raw = sa.canonical_json_bytes(checkpoint.value)
        self.assertNotIn(b"serviceKey", raw)
        self.assertNotIn(b"https://apis.data.go.kr", raw)
        self.assertTrue(
            all(
                row["credential_bearing_endpoint_material_absent"] is True
                for row in checkpoint.value["raw_index"]
            )
        )

    def test_density_event_identity_and_duplicate_telemetry(self):
        item = {
            "basDt": live.PRIMARY_DATES[0],
            "issuCmpyKsdCustNo": "000001",
            "crno": "1101110000011",
            "stckIssuCmpyNm": "Fixture Issuer",
            "rgtExertRcd": "OPAQUE-A",
            "rgtExertRcdNm": "Opaque Event A",
        }

        def handler(params, _ordinal):
            bas_dt = params["basDt"]
            items = [item, dict(item)] if bas_dt == live.PRIMARY_DATES[0] else []
            return response(
                finance_body(
                    bas_dt,
                    int(params["pageNo"]),
                    total=len(items),
                    items=items,
                )
            )

        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        report = live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=FakeTransport(handler, checkpoint),
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(report["dates_with_rows"], 1)
        self.assertEqual(report["total_items"], 2)
        self.assertEqual(report["event_code_counts_opaque"], {"OPAQUE-A": 2})
        self.assertEqual(report["date_echo"]["match_rows"], 2)
        self.assertEqual(report["issuer_identity"]["match_rows"], 2)
        self.assertEqual(report["duplicates"]["exact_duplicate_items"], 1)
        self.assertEqual(report["duplicates"]["ratio_numerator"], 1)
        self.assertEqual(report["duplicates"]["ratio_denominator"], 2)
        self.assertEqual(
            report["external_u127_identity_match"]["state"], "NOT_EVALUATED"
        )
        self.assertEqual(
            report["event_code_name_pairs_opaque"],
            [{"code": "OPAQUE-A", "name": "Opaque Event A", "count": 2}],
        )
        self.assertEqual(
            report["historical_acquisition_promotion"]["decision"],
            "RECOMMEND_SEPARATE_BOUNDED_RAW_HISTORICAL_AUTHORITY",
        )
        quarantined = copy.deepcopy(checkpoint.value)
        quarantined["issuer_identity_conflicts"] = 1
        quarantined_report = live._build_report(quarantined, checkpoint.token)
        self.assertEqual(
            quarantined_report["historical_acquisition_promotion"]["decision"],
            "HOLD_NO_PROMOTION_QUARANTINED",
        )
        blocked = copy.deepcopy(checkpoint.value)
        blocked["state"] = "BLOCKED"
        blocked_report = live._build_report(blocked, checkpoint.token)
        self.assertEqual(
            blocked_report["historical_acquisition_promotion"]["decision"],
            "STOP_NO_PROMOTION_PILOT_BLOCKED",
        )

    def test_response_bearing_429_is_custodied_before_retry(self):
        def handler(params, ordinal):
            if ordinal == 1:
                return response(b"rate limited", status=429)
            return empty_handler(params, ordinal)

        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        report = live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=FakeTransport(handler, checkpoint),
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(report["quota"]["pilot_reservations"], 18)
        self.assertEqual(report["http_status_counts"]["429"], 1)
        self.assertEqual(report["http_status_counts"]["200"], 17)
        self.assertEqual(len(custody.objects), 18)
        self.assertEqual(
            checkpoint.value["attempts"][0]["state"],
            "RETRYABLE_HTTP_ENTITY_CUSTODIED",
        )

    def test_timeout_spends_reservation_then_retries_without_raw_entity(self):
        def handler(params, ordinal):
            if ordinal == 1:
                raise live.NoEntityTransportError("fixture timeout")
            return empty_handler(params, ordinal)

        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        report = live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=FakeTransport(handler, checkpoint),
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(report["quota"]["pilot_reservations"], 18)
        self.assertEqual(report["quota"]["no_entity_attempts"], 1)
        self.assertEqual(len(custody.objects), 17)
        self.assertEqual(
            checkpoint.value["attempts"][0]["state"],
            "NO_RESPONSE_ENTITY_RESERVATION_SPENT",
        )

    def test_malformed_200_is_custodied_before_parse_block(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(
            lambda _params, _ordinal: response(b"{malformed"), checkpoint
        )
        with self.assertRaises(sa.SourceProtocolError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(custody.objects), 1)
        self.assertEqual(len(checkpoint.value["raw_index"]), 1)
        self.assertEqual(checkpoint.value["state"], "BLOCKED")
        self.assertEqual(
            checkpoint.value["attempts"][0]["state"],
            "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY",
        )

    def test_secret_leak_is_rejected_before_custody(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(
            lambda _params, _ordinal: response(b'{"echo":"topsecret"}'),
            checkpoint,
        )
        with self.assertRaises(sa.CredentialContractError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=("topsecret",),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(custody.objects), 0)
        self.assertEqual(checkpoint.value["quota_reservations"], 1)
        self.assertEqual(checkpoint.value["state"], "BLOCKED")

    def test_page_ceiling_fails_after_page_one_custody_without_page_two(self):
        items = [
            {"basDt": live.PRIMARY_DATES[0], "row": index}
            for index in range(10)
        ]

        def handler(params, _ordinal):
            return response(
                finance_body(
                    params["basDt"],
                    int(params["pageNo"]),
                    total=101,
                    items=items,
                )
            )

        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(handler, checkpoint)
        with self.assertRaises(sa.QuotaBoundaryError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(len(custody.objects), 1)
        self.assertEqual(checkpoint.value["quota_reservations"], 1)

    def test_custody_before_checkpoint_crash_reconciles_without_refetch(self):
        checkpoint = FakeCheckpointStore(fail_once_at=4)
        custody = FakeCustody()
        first_transport = FakeTransport(empty_handler, checkpoint)
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=first_transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(first_transport.calls), 1)
        self.assertEqual(len(custody.objects), 1)
        self.assertEqual(
            checkpoint.value["attempts"][0]["state"],
            "RESERVED_WRITE_AHEAD",
        )

        second_transport = FakeTransport(empty_handler, checkpoint)
        report = live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=second_transport,
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(report["state"], "STOP_NO_PROMOTION_ZERO_DENSITY")
        self.assertEqual(len(second_transport.calls), 16)
        self.assertTrue(
            checkpoint.value["raw_index"][0][
                "reconciled_after_custody_before_checkpoint_gap"
            ]
        )
        self.assertEqual(checkpoint.value["quota_reservations"], 17)

    def test_resume_revalidates_page_one_and_blocks_shift_before_page_two(self):
        class FailPageTwoReservation(FakeCheckpointStore):
            def compare_and_swap(self, value, expected_token):
                attempts = value.get("attempts", [])
                if (
                    not self.failed
                    and attempts
                    and attempts[-1].get("page_no") == 2
                    and attempts[-1].get("state") == "RESERVED_WRITE_AHEAD"
                ):
                    self.failed = True
                    raise sa.CheckpointConflictError("crash before page two")
                return super().compare_and_swap(value, expected_token)

        original_items = [
            {"basDt": live.PRIMARY_DATES[0], "row": index}
            for index in range(10)
        ]
        checkpoint = FailPageTwoReservation()
        custody = FakeCustody()
        first_transport = FakeTransport(
            lambda params, _ordinal: response(
                finance_body(
                    params["basDt"], 1, total=11, items=original_items
                )
            ),
            checkpoint,
        )
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=first_transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(first_transport.calls), 1)
        self.assertEqual(
            len(checkpoint.value["current_date"]["validated_pages"]), 1
        )

        shifted = [dict(row) for row in original_items]
        shifted[0]["row"] = 999
        second_transport = FakeTransport(
            lambda params, _ordinal: response(
                finance_body(params["basDt"], 1, total=11, items=shifted)
            ),
            checkpoint,
        )
        with self.assertRaises(sa.SourceProtocolError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=second_transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(second_transport.calls), 1)
        self.assertEqual(checkpoint.value["state"], "BLOCKED")

    def test_two_retryable_entities_exhaust_exact_page_attempt_cap(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(
            lambda _params, _ordinal: response(b"busy", status=503),
            checkpoint,
        )
        with self.assertRaises(sa.SourceTransportError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(checkpoint.value["quota_reservations"], 2)
        self.assertEqual(len(custody.objects), 2)

    def test_single_writer_claim_precedes_provider_and_conflict_blocks(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()

        def handler(params, ordinal):
            self.assertIsNotNone(custody.claim_payload)
            self.assertEqual(
                checkpoint.value["execution_claim"]["writer_id"], WRITER_ID
            )
            return empty_handler(params, ordinal)

        live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=FakeTransport(handler, checkpoint),
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(custody.events[0], ("claim", WRITER_ID))
        original_claim = custody.claim_payload
        rerun_transport = FakeTransport(empty_handler)
        live.run_finance_live_pilot(
            live.LivePilotSpec(),
            replace(bindings(), github_run_attempt=2),
            transport=rerun_transport,
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(custody.claim_payload, original_claim)
        self.assertEqual(rerun_transport.calls, [])
        blocked_transport = FakeTransport(empty_handler)
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                replace(bindings(), github_sha="2" * 40),
                transport=blocked_transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(blocked_transport.calls, [])

    def test_wrong_kst_quota_day_fails_before_claim_or_provider(self):
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(empty_handler)
        with self.assertRaises(sa.QuotaBoundaryError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=lambda: datetime(2026, 8, 29, 16, tzinfo=timezone.utc),
                sleep_fn=lambda _: None,
            )
        self.assertEqual(custody.events, [])
        self.assertEqual(transport.calls, [])

        class RollingClock:
            def __init__(self):
                self.calls = 0

            def __call__(self):
                self.calls += 1
                hour = 11 if self.calls <= 6 else 16
                return datetime(2026, 8, 29, hour, tzinfo=timezone.utc)

        checkpoint = FakeCheckpointStore()
        custody = FakeCustody()
        transport = FakeTransport(empty_handler, checkpoint)
        with self.assertRaises(sa.QuotaBoundaryError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(), transport=transport,
                custody=custody, claim_store=custody,
                checkpoint_store=checkpoint, writer_id=WRITER_ID,
                secrets=(), clock=RollingClock(), sleep_fn=lambda _: None,
            )
        self.assertEqual(checkpoint.value["quota_reservations"], 1)
        self.assertEqual(len(checkpoint.value["attempts"]), 1)
        self.assertEqual(transport.calls, [])

    def test_parsed_200_checkpoint_crash_reuses_sealed_body(self):
        class CrashBeforeValidatedPage(FakeCheckpointStore):
            def compare_and_swap(self, value, expected_token):
                current = value.get("current_date")
                if (
                    not self.failed
                    and isinstance(current, dict)
                    and current.get("validated_pages")
                ):
                    self.failed = True
                    raise sa.CheckpointConflictError("crash after PARSED_200 CAS")
                return super().compare_and_swap(value, expected_token)

        checkpoint = CrashBeforeValidatedPage()
        custody = FakeCustody()
        first_transport = FakeTransport(empty_handler, checkpoint)
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(),
                bindings(),
                transport=first_transport,
                custody=custody,
                claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=WRITER_ID,
                secrets=(),
                clock=PILOT_CLOCK,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(checkpoint.value["attempts"][0]["state"], "PARSED_200")
        second_transport = FakeTransport(empty_handler, checkpoint)
        live.run_finance_live_pilot(
            live.LivePilotSpec(),
            bindings(),
            transport=second_transport,
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=WRITER_ID,
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(len(second_transport.calls), 16)
        self.assertEqual(checkpoint.value["quota_reservations"], 17)

    def test_raw_put_then_transient_readback_failure_is_reconciled(self):
        class FailReadbackOnce(FakeCustody):
            def __init__(self):
                super().__init__()
                self.failed = False

            def seal_and_readback(self, object_key, body, metadata):
                sealed = super().seal_and_readback(object_key, body, metadata)
                if not self.failed:
                    self.failed = True
                    raise live.RemoteCustodyError("injected readback outage")
                return sealed

        checkpoint = FakeCheckpointStore()
        custody = FailReadbackOnce()
        first_transport = FakeTransport(empty_handler, checkpoint)
        with self.assertRaises(live.RemoteCustodyError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(), transport=first_transport,
                custody=custody, claim_store=custody,
                checkpoint_store=checkpoint, writer_id=WRITER_ID,
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(checkpoint.value["state"], "IN_PROGRESS")
        self.assertEqual(
            checkpoint.value["attempts"][0]["state"], "RESERVED_WRITE_AHEAD"
        )
        second_transport = FakeTransport(empty_handler, checkpoint)
        second_bindings = replace(bindings(), github_run_attempt=2)
        live.run_finance_live_pilot(
            live.LivePilotSpec(), second_bindings, transport=second_transport,
            custody=custody, claim_store=custody,
            checkpoint_store=checkpoint, writer_id=WRITER_ID,
            secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
        )
        self.assertEqual(len(second_transport.calls), 16)
        self.assertTrue(
            checkpoint.value["raw_index"][0][
                "reconciled_after_custody_before_checkpoint_gap"
            ]
        )
        self.assertEqual(checkpoint.value["observed_github_run_attempts"], [1, 2])
        self.assertEqual(checkpoint.value["attempts"][0]["run_attempt"], 1)
        self.assertTrue(
            all(
                row["run_attempt"] == 2
                for row in checkpoint.value["attempts"][1:]
            )
        )
        quota_rows = live._quota_rows_from_checkpoint([], checkpoint.value)
        self.assertEqual(quota_rows[0]["run_attempt"], 1)
        self.assertTrue(all(row["run_attempt"] in {1, 2} for row in quota_rows))

    def test_corrupt_checkpoint_and_terminal_state_never_refetch(self):
        report, checkpoint, custody, _ = self.run_empty()
        self.assertEqual(report["completed_date_count"], 17)
        checkpoint.value["quota_reservations"] += 1
        transport = FakeTransport(empty_handler)
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(), transport=transport,
                custody=custody, claim_store=custody,
                checkpoint_store=checkpoint, writer_id=WRITER_ID,
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(transport.calls, [])

        _, forged, forged_custody, _ = self.run_empty()
        forged.value.update(
            {
                "attempts": [],
                "raw_index": [],
                "unique_page_slots": [],
                "observed_github_run_attempts": [],
                "quota_reservations": 0,
                "network_attempts_started_conservative": 0,
                "response_entities_received": 0,
                "remote_raw_custody_writes_or_reconciliations": 0,
                "raw_entity_bytes": 0,
                "http_status_counts": {},
            }
        )
        forged_transport = FakeTransport(empty_handler)
        with self.assertRaises(sa.CheckpointConflictError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(), transport=forged_transport,
                custody=forged_custody, claim_store=forged_custody,
                checkpoint_store=forged, writer_id=WRITER_ID,
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(forged_transport.calls, [])

        malformed_checkpoint = FakeCheckpointStore()
        malformed_custody = FakeCustody()
        with self.assertRaises(sa.SourceProtocolError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(),
                transport=FakeTransport(
                    lambda _params, _ordinal: response(b"{bad"),
                    malformed_checkpoint,
                ),
                custody=malformed_custody, claim_store=malformed_custody,
                checkpoint_store=malformed_checkpoint, writer_id=WRITER_ID,
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        malformed_checkpoint.value["state"] = "IN_PROGRESS"
        terminal_transport = FakeTransport(empty_handler)
        with self.assertRaises(sa.SourceProtocolError):
            live.run_finance_live_pilot(
                live.LivePilotSpec(), bindings(), transport=terminal_transport,
                custody=malformed_custody, claim_store=malformed_custody,
                checkpoint_store=malformed_checkpoint, writer_id=WRITER_ID,
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(terminal_transport.calls, [])

    def test_strict_duplicate_json_and_identity_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_bytes(b'{"state":"ARMED","state":"STAGED"}')
            with self.assertRaises(live.AuthorityBindingError):
                live._load_json(path)

        class FixtureResponse:
            status = 200
            headers = {"Content-Type": "application/json"}

            def getcode(self):
                return 200

            def read(self):
                return finance_body("20240102")

        class FixtureOpener:
            request = None

            def open(self, request, timeout):
                self.request = request
                return FixtureResponse()

        opener = FixtureOpener()
        transport = live.UrlLibFinanceTransport(
            "fixture-secret", opener=opener
        )
        transport.fetch_once(sa.finance_request_params("20240102", 1, 10))
        self.assertEqual(opener.request.get_header("Accept-encoding"), "identity")

    def test_cli_rejects_staged_latch_and_accepts_exact_armed_material(self):
        root = Path(__file__).resolve().parents[3]
        control = root / "control/m3top3/public-data-source-admission/v1.0"
        authority_source = control / "M3TOP3_PUBLIC_DATA_API_SOURCE_ADMISSION_CONTRACT_v1.0.json"
        plan_source = control / "M3TOP3_PUBLIC_DATA_API_SOURCE_ADMISSION_PLAN_v1.0.json"
        staged = control / "M3TOP3_FINANCE_CA_LIVE_PILOT_LATCH_v1.0.json"
        checkpoint_source = control / "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0.json"
        with self.assertRaises(live.AuthorityBindingError):
            live.validate_cli_materials(
                authority_path=authority_source,
                plan_path=plan_source,
                latch_path=staged,
                checkpoint_path=checkpoint_source,
            )

        authority_doc = json.loads(authority_source.read_text())
        current = authority_doc["current_runtime_authority"]
        current.update(
            {
                "state": "ACTIVE_FINANCE_ONLY_LIVE_PILOT",
                "provider_api_network_calls_entry_gate": "OPEN",
                "provider_api_network_calls_authorized": True,
                "provider_api_network_calls_permitted_now": True,
                "provider_api_network_attempt_budget": live.MAX_NETWORK_ATTEMPTS_TOTAL,
                "quota_reservation_authorized": True,
                "provider_workflow_dispatch_authorized": True,
                "live_multi_page_provider_run_authorized": True,
                "remote_raw_custody_write_authorized": True,
                "remote_raw_custody_writes_permitted_now": True,
            }
        )
        live_authority = authority_doc["finance_live_pilot_authority"]
        live_authority["authority_state"] = "GRANTED_ENTRY_GATE_OPEN"
        live_authority["live_entry_gate"]["state"] = "OPEN"
        plan_doc = json.loads(plan_source.read_text())
        plan_doc["state"] = "LIVE_ARMED_EXECUTABLE"
        plan_doc["execution_gate"].update(
            {
                "state": "OPEN",
                "execution_armed": True,
                "plan_executable": True,
                "provider_api_calls_permitted_now": True,
                "remote_s3_writes_permitted_now": True,
            }
        )
        plan_doc["durable_custody_plan"]["state"] = "READY_FOR_LIVE_ARMED"
        latch = json.loads(staged.read_text())
        latch["state"] = "ARMED"
        latch["mode"] = "LIVE_ARMED"
        latch["finance_spec"].update(
            {
                "pilot_quota_day_kst": live.PILOT_QUOTA_DAY_KST,
                "historical_baseline_quota_day_kst": live.HISTORICAL_BASELINE_QUOTA_DAY_KST,
                "current_day_finance_ordinal_base": live.PILOT_FINANCE_ORDINAL_BASE,
                "current_day_next_finance_ordinal": live.PILOT_FINANCE_ORDINAL_BASE + 1,
                "historical_baseline_rows_preserved": 7,
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            authority = directory_path / "authority.json"
            plan = directory_path / "plan.json"
            checkpoint = directory_path / "checkpoint.json"
            latch_path = Path(directory) / "latch.json"
            authority.write_bytes(sa.canonical_json_bytes(authority_doc))
            plan.write_bytes(sa.canonical_json_bytes(plan_doc))
            checkpoint.write_bytes(checkpoint_source.read_bytes())
            authority_sha = hashlib.sha256(authority.read_bytes()).hexdigest()
            plan_sha = hashlib.sha256(plan.read_bytes()).hexdigest()
            runner_sha = hashlib.sha256(Path(live.__file__).read_bytes()).hexdigest()
            source_sha = hashlib.sha256(Path(sa.__file__).read_bytes()).hexdigest()
            checkpoint_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            latch["execution_material"] = {
                "runtime_lock_id": live.RUNTIME_LOCK_ID,
                "pilot_run_id": live.PILOT_RUN_ID,
                "authority_sha256": authority_sha,
                "plan_sha256": plan_sha,
                "runner_sha256": runner_sha,
                "source_admission_sha256": source_sha,
                "checkpoint_template_sha256": checkpoint_sha,
                "owner_cap_spec_sha256": live.OWNER_CAP_SPEC_SHA256,
                "execution_token_sha256": live.EXPECTED_EXECUTION_TOKEN_SHA256,
                "pilot_quota_day_kst": live.PILOT_QUOTA_DAY_KST,
                "historical_baseline_quota_day_kst": live.HISTORICAL_BASELINE_QUOTA_DAY_KST,
                "current_day_finance_ordinal_base": live.PILOT_FINANCE_ORDINAL_BASE,
                "current_day_next_finance_ordinal": live.PILOT_FINANCE_ORDINAL_BASE + 1,
                "historical_baseline_rows_preserved": 7,
            }
            latch["execution_material_sha256"] = hashlib.sha256(
                sa.canonical_json_bytes(latch["execution_material"])
            ).hexdigest()
            latch["authority_bindings"].update(
                {
                    "bindings_finalized": True,
                    "authority_sha256": authority_sha,
                    "plan_sha256": plan_sha,
                    "runner_sha256": runner_sha,
                    "source_admission_sha256": source_sha,
                    "checkpoint_seed_sha256": checkpoint_sha,
                    "workflow_sha256": "1" * 64,
                }
            )
            latch_path.write_bytes(sa.canonical_json_bytes(latch))
            with mock.patch.object(
                live, "EXPECTED_AUTHORITY_SHA256", authority_sha
            ):
                spec, observed = live.validate_cli_materials(
                    authority_path=authority,
                    plan_path=plan,
                    latch_path=latch_path,
                    checkpoint_path=checkpoint,
                    environment=WORKFLOW_ENV,
                )
                bad_identity = dict(WORKFLOW_ENV)
                bad_identity["GITHUB_RUN_ATTEMPT"] = "0"
                with self.assertRaises(live.AuthorityBindingError):
                    live.validate_cli_materials(
                        authority_path=authority,
                        plan_path=plan,
                        latch_path=latch_path,
                        checkpoint_path=checkpoint,
                        environment=bad_identity,
                    )
        self.assertEqual(spec.ordered_dates, live.PRIMARY_DATES)
        self.assertEqual(observed.authority_sha256, authority_sha)
        self.assertEqual(observed.source_admission_sha256, source_sha)

    def test_s3_cli_adapter_uses_conditional_cas_and_exact_prefix(self):
        objects = {}
        metadata = {}
        calls = []
        version = [0]

        def runner(command):
            command = list(command)
            calls.append(command)
            operation = command[2]
            if operation == "get-object":
                key = command[command.index("--key") + 1]
                if key not in objects:
                    return subprocess.CompletedProcess(
                        command, 1, "", "NoSuchKey"
                    )
                Path(command[-1]).write_bytes(objects[key])
                return subprocess.CompletedProcess(
                    command,
                    0,
                    json.dumps(metadata[key]),
                    "",
                )
            if operation == "put-object":
                key = command[command.index("--key") + 1]
                if "--if-none-match" in command and key in objects:
                    return subprocess.CompletedProcess(
                        command, 1, "", "PreconditionFailed 412"
                    )
                if "--if-match" in command:
                    expected = command[command.index("--if-match") + 1]
                    if key not in metadata or metadata[key]["ETag"] != expected:
                        return subprocess.CompletedProcess(
                            command, 1, "", "PreconditionFailed 412"
                        )
                body_path = Path(command[command.index("--body") + 1])
                version[0] += 1
                objects[key] = body_path.read_bytes()
                user_metadata = {}
                if "--metadata" in command:
                    text = command[command.index("--metadata") + 1]
                    user_metadata = dict(
                        pair.split("=", 1) for pair in text.split(",")
                    )
                metadata[key] = {
                    "ETag": f'"etag-{version[0]}"',
                    "VersionId": f"v-{version[0]}",
                    "ServerSideEncryption": "AES256",
                    "Metadata": user_metadata,
                }
                return subprocess.CompletedProcess(
                    command,
                    0,
                    json.dumps(metadata[key]),
                    "",
                )
            if operation == "list-objects-v2":
                prefix = command[command.index("--prefix") + 1]
                return subprocess.CompletedProcess(
                    command,
                    0,
                    json.dumps(
                        {
                            "Contents": [
                                {"Key": key}
                                for key in sorted(objects)
                                if key.startswith(prefix)
                            ]
                        }
                    ),
                    "",
                )
            raise AssertionError(operation)

        store = live.S3CliObjectStore(command_runner=runner)
        self.assertEqual(store.load(), (None, None))
        first = {"state": "ONE"}
        first_token = store.compare_and_swap(first, None)
        second_token = store.compare_and_swap({"state": "TWO"}, first_token)
        self.assertNotEqual(first_token, second_token)
        put_calls = [call for call in calls if call[2] == "put-object"]
        self.assertIn("--if-none-match", put_calls[0])
        self.assertIn("--if-match", put_calls[1])
        self.assertEqual(
            put_calls[0][put_calls[0].index("--key") + 1],
            live.checkpoint_object_key(),
        )

        claim = live._execution_claim_material(bindings(), WRITER_ID)
        claim_evidence = store.acquire_execution_claim(claim)
        self.assertEqual(
            claim_evidence.object_key, live.execution_claim_object_key()
        )
        self.assertEqual(claim_evidence.writer_id, WRITER_ID)
        self.assertEqual(store.acquire_execution_claim(claim), claim_evidence)

        body = b'{"fixture":true}'
        digest = hashlib.sha256(body).hexdigest()
        prefix = live.deterministic_raw_object_prefix("20240102", 1, 1)
        key = live.canonical_raw_object_key(prefix, digest)
        sealed = store.seal_and_readback(
            key,
            body,
            {
                "sha256": digest,
                "http-status": "200",
                "acquired-at-utc": NOW,
                "request-id": live.deterministic_request_id("20240102", 1),
                "bas-dt": "20240102",
                "page-no": "1",
                "attempt": "1",
                "runtime-lock-id": live.RUNTIME_LOCK_ID,
                "pilot-run-id": live.PILOT_RUN_ID,
                "quota-day-kst": live.PILOT_QUOTA_DAY_KST,
            },
        )
        self.assertEqual(sealed.body, body)
        self.assertEqual(sealed.server_side_encryption, "AES256")
        self.assertTrue(sealed.version_id)
        self.assertEqual(store.find_existing_by_prefix(prefix), sealed)
        base_metadata = {
            "sha256": digest,
            "http-status": "200",
            "acquired-at-utc": NOW,
            "request-id": live.deterministic_request_id("20240102", 1),
            "bas-dt": "20240102",
            "page-no": "1",
            "attempt": "1",
            "runtime-lock-id": live.RUNTIME_LOCK_ID,
            "pilot-run-id": live.PILOT_RUN_ID,
            "quota-day-kst": live.PILOT_QUOTA_DAY_KST,
        }
        for field, changed in (
            ("http-status", "201"),
            ("acquired-at-utc", "2026-08-29T11:00:01+00:00"),
        ):
            conflicting = dict(base_metadata)
            conflicting[field] = changed
            with self.assertRaises(live.RemoteCustodyError):
                store.seal_and_readback(key, body, conflicting)
        with self.assertRaises(live.RemoteCustodyError):
            live.S3CliObjectStore(
                prefix="s3://semi-data-plane-aofspds-20260815/other/"
            )


if __name__ == "__main__":
    unittest.main()
