import copy
import hashlib
import json
import unittest
from dataclasses import replace
from datetime import datetime, timezone

from tools.m3top3 import finance_page100_pilot as page100
from tools.m3top3 import source_admission as sa


NOW = "2026-08-29T01:00:00+00:00"
PILOT_CLOCK = lambda: datetime(2026, 8, 29, 1, tzinfo=timezone.utc)


def finance_body(bas_dt, page_no=1, total=0, items=None, page_size=10):
    if items is None:
        items = []
    return json.dumps(
        {
            "response": {
                "header": {
                    "resultCode": "00",
                    "resultMsg": "NORMAL SERVICE.",
                },
                "body": {
                    "numOfRows": str(page_size),
                    "pageNo": str(page_no),
                    "totalCount": str(total),
                    "items": {"item": items},
                },
            }
        },
        separators=(",", ":"),
    ).encode()


def response(body, status=200):
    return page100.TransportResponse(
        body=body,
        http_status=status,
        safe_headers={"content-type": "application/json"},
        acquired_at_utc=NOW,
    )


class FakeCheckpointStore:
    def __init__(self, *, fail_raw_once=False):
        self.value = None
        self.token = None
        self.cas_calls = 0
        self.fail_raw_once = fail_raw_once
        self.failed = False

    def load(self):
        return copy.deepcopy(self.value), self.token

    def compare_and_swap(self, value, expected_token):
        self.cas_calls += 1
        attempts = value.get("attempts", [])
        if (
            self.fail_raw_once
            and not self.failed
            and attempts
            and attempts[-1].get("state") == "RAW_SEALED_BEFORE_PARSE"
        ):
            self.failed = True
            raise sa.CheckpointConflictError("injected raw/checkpoint gap")
        if expected_token != self.token:
            raise sa.CheckpointConflictError("fake checkpoint conflict")
        self.value = copy.deepcopy(dict(value))
        self.token = f'"etag-{self.cas_calls}"'
        return self.token


class FakeCustody:
    def __init__(self, bindings, historical):
        self.bindings = bindings
        self.historical = historical
        self.objects = {}
        self.claim_payload = None
        self.events = []

    def read_historical(self, binding):
        self.events.append(("historical-read", binding.object_key, binding.version_id))
        if (
            binding.object_key != self.bindings.predecessor.page_one.object_key
            or binding.version_id
            != self.bindings.predecessor.page_one.version_id
        ):
            return None
        return self.historical

    def acquire_execution_claim(self, claim):
        payload = sa.canonical_json_bytes(dict(claim))
        self.events.append(("claim", page100.execution_claim_object_key(self.bindings)))
        if self.claim_payload is not None and self.claim_payload != payload:
            raise sa.CheckpointConflictError("quota-day-global writer conflict")
        self.claim_payload = payload
        return page100.ExecutionClaimEvidence(
            object_key=page100.execution_claim_object_key(self.bindings),
            content_sha256=hashlib.sha256(payload).hexdigest(),
            version_id="claim-version",
            etag='"claim-etag"',
            server_side_encryption="AES256",
            write_precondition="IF_NONE_MATCH_STAR",
            writer_id=claim["writer_id"],
        )

    def read_existing(self, object_key, version_id=None):
        self.events.append(("read", object_key))
        sealed = self.objects.get(object_key)
        if sealed is not None and version_id is not None:
            if sealed.version_id != version_id:
                raise page100.RemoteCustodyError("fake version shift")
        return sealed

    def find_existing_by_prefix(self, object_prefix):
        self.events.append(("find", object_prefix))
        matches = [
            value for key, value in self.objects.items()
            if key.startswith(object_prefix)
        ]
        if len(matches) > 1:
            raise page100.RemoteCustodyError("multiple current objects")
        return matches[0] if matches else None

    def seal_and_readback(self, object_key, body, metadata):
        self.events.append(("seal", object_key))
        digest = hashlib.sha256(body).hexdigest()
        if metadata["sha256"] != digest:
            raise AssertionError("digest mismatch")
        sealed = page100.SealedEntity(
            body=body,
            object_key=object_key,
            storage_locator=(
                "s3://semi-data-plane-aofspds-20260815/" + object_key
            ),
            entity_sha256=digest,
            entity_bytes=len(body),
            readback_sha256=digest,
            readback_bytes=len(body),
            version_id=f"current-version-{len(self.objects) + 1}",
            etag=f'"{digest[:16]}"',
            server_side_encryption="AES256",
            write_precondition="IF_NONE_MATCH_STAR",
            http_status=int(metadata["http-status"]),
            acquired_at_utc=metadata["acquired-at-utc"],
        )
        prior = self.objects.get(object_key)
        if prior is not None and prior.body != body:
            raise page100.RemoteCustodyError("exclusive create conflict")
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
                raise AssertionError("provider called before durable reservation")
        self.calls.append(params)
        return self.handler(params, len(self.calls))


def item(bas_dt, number):
    return {
        "basDt": bas_dt,
        "issuCmpyKsdCustNo": f"{number:06d}",
        "crno": f"110111{number:07d}",
        "stckIssuCmpyNm": f"Issuer {number}",
        "rgtExertRcd": "01",
        "rgtExertRcdNm": "Fixture",
    }


def predecessor_fixture(*, total=1, first_items=None):
    if first_items is None:
        first_items = [item("20240131", 1)] if total else []
    body = finance_body("20240131", 1, total, first_items)
    digest = hashlib.sha256(body).hexdigest()
    request_id = page100.deterministic_request_id("20240131", 1)
    old_key = (
        page100.RAW_KEY_PREFIX
        + f"{sa.FINANCE_OPERATION}/quota_day_kst=2026-08-29/"
        + f"request_id={request_id}/attempt=1/sha256={digest}.entity"
    )
    page_binding = page100.HistoricalPageOneBinding(
        object_key=old_key,
        version_id="historical-version-1",
        entity_sha256=digest,
        entity_bytes=len(body),
        server_side_encryption="AES256",
    )

    attempts = []
    raw_index = []
    for page_no in range(1, 9):
        page_digest = f"{page_no:064x}"
        page_key = f"old/20240102/page={page_no}/sha256={page_digest}.entity"
        attempts.append({
            "basDt": "20240102",
            "page_no": page_no,
            "attempt": 1,
            "state": "PARSED_200",
            "github_run_id": page100.PREDECESSOR_WORKFLOW_RUN_ID,
        })
        raw_index.append({
            "basDt": "20240102",
            "page_no": page_no,
            "attempt": 1,
            "s3_object_key": page_key,
            "s3_version_id": f"historical-20240102-{page_no}",
            "entity_sha256": page_digest,
            "entity_bytes": 100,
            "server_side_encryption": "AES256",
            "http_status": 200,
        })
    attempts.append({
        "basDt": "20240131",
        "page_no": 1,
        "attempt": 1,
        "state": "PARSED_200",
        "github_run_id": page100.PREDECESSOR_WORKFLOW_RUN_ID,
    })
    raw_index.append({
        "basDt": "20240131",
        "page_no": 1,
        "attempt": 1,
        "s3_object_key": old_key,
        "s3_version_id": page_binding.version_id,
        "entity_sha256": digest,
        "entity_bytes": len(body),
        "server_side_encryption": "AES256",
        "http_status": 200,
    })
    checkpoint = {
        "runtime_lock_id": page100.PREDECESSOR_RUNTIME_LOCK_ID,
        "pilot_run_id": page100.PREDECESSOR_PILOT_RUN_ID,
        "state": "BLOCKED",
        "last_error_class": "QuotaBoundaryError",
        "completed_dates": ["20240102"],
        "next_date_index": 1,
        "date_results": [{
            "basDt": "20240102",
            "state": "DATE_COMPLETE",
            "page_count": 8,
            "item_count": 76,
            "total_count": 76,
            "page_1_identity": "a" * 64,
            "resume_page_1_revalidations": 0,
            "valid_empty": False,
        }],
        "attempts": attempts,
        "raw_index": raw_index,
        "event_code_counts": {},
        "event_code_name_counts": {},
        "date_echo_match_rows": 0,
        "issuer_identity_rows_checked": 0,
        "issuer_identity_match_rows": 0,
        "issuer_identity_conflicts": 0,
        "issuer_identity_missing_rows": 0,
        "issuer_identity_hashes": {},
        "seen_item_sha256": [],
        "exact_duplicate_items": 0,
    }
    checkpoint_bytes = sa.canonical_json_bytes(checkpoint)
    raw_bytes = b"".join(sa.canonical_json_bytes(row) for row in raw_index)
    quota_bytes = sa.canonical_json_bytes({
        "event": "QUOTA_SLOT_SPENT",
        "provider": "FINANCE",
        "pilot_run_id": page100.PREDECESSOR_PILOT_RUN_ID,
        "ordinal": 9,
    })
    predecessor = page100.PredecessorBinding(
        checkpoint_sha256=hashlib.sha256(checkpoint_bytes).hexdigest(),
        raw_index_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        quota_ledger_sha256=hashlib.sha256(quota_bytes).hexdigest(),
        page_one=page_binding,
    )
    bindings = page100.SuccessorBindings(
        github_run_id=40000000000,
        predecessor=predecessor,
    )
    historical = page100.SealedEntity(
        body=body,
        object_key=old_key,
        storage_locator="s3://semi-data-plane-aofspds-20260815/" + old_key,
        entity_sha256=digest,
        entity_bytes=len(body),
        readback_sha256=digest,
        readback_bytes=len(body),
        version_id=page_binding.version_id,
        etag='"historical-etag"',
        server_side_encryption="AES256",
        write_precondition="IF_NONE_MATCH_STAR",
        http_status=200,
        acquired_at_utc=NOW,
    )
    bundle = page100.PredecessorBundle(
        checkpoint_bytes=checkpoint_bytes,
        raw_index_bytes=raw_bytes,
        quota_ledger_bytes=quota_bytes,
    )
    return bindings, bundle, historical, body


def empty_or_historical_handler(historical_body):
    def handler(params, _ordinal):
        if params["basDt"] == "20240102":
            raise AssertionError("completed predecessor date was rerun")
        if params["basDt"] == "20240131" and params["pageNo"] == "1":
            return response(historical_body)
        return response(
            finance_body(params["basDt"], int(params["pageNo"]), 0, [])
        )
    return handler


class FinancePage100PilotTests(unittest.TestCase):
    def run_fixture(self, *, total=1, first_items=None):
        bindings, bundle, historical, body = predecessor_fixture(
            total=total, first_items=first_items
        )
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)
        transport = FakeTransport(
            empty_or_historical_handler(body), checkpoint
        )
        report = page100.run_page100_pilot(
            page100.Page100Spec(),
            bindings,
            bundle,
            transport=transport,
            custody=custody,
            claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
            secrets=(),
            clock=PILOT_CLOCK,
            sleep_fn=lambda _: None,
        )
        return report, checkpoint, custody, transport, bindings, bundle

    def test_caps_ids_owner_material_and_global_claim_are_exact(self):
        self.assertEqual(page100.MAX_PAGES_PER_DATE, 100)
        self.assertEqual(page100.MAX_PRIMARY_PAGE_SLOTS, 1700)
        self.assertEqual(page100.MAX_NETWORK_ATTEMPTS_TOTAL, 2000)
        self.assertEqual(page100.MAX_ATTEMPTS_PER_PAGE, 2)
        self.assertEqual(len(page100.PRIMARY_DATES), 17)
        self.assertEqual(
            page100.owner_cap_material()["reused_completed_dates"],
            ["20240102"],
        )
        bindings, *_ = predecessor_fixture()
        self.assertEqual(
            page100.execution_claim_object_key(bindings),
            page100.RAW_KEY_PREFIX
            + "_writer_claims/quota_day_kst=2026-08-29/"
            "execution-claim.json",
        )
        self.assertNotIn(
            bindings.runtime_lock_id,
            page100.execution_claim_object_key(bindings),
        )

    def test_reuses_20240102_and_exact_page_one_once_without_rewrite(self):
        report, checkpoint, custody, transport, bindings, _ = self.run_fixture()
        self.assertEqual(checkpoint.value["state"], "COMPLETE")
        self.assertEqual(checkpoint.value["completed_dates"], list(page100.PRIMARY_DATES))
        self.assertFalse(any(call["basDt"] == "20240102" for call in transport.calls))
        page_one_calls = [
            call for call in transport.calls
            if call["basDt"] == "20240131" and call["pageNo"] == "1"
        ]
        self.assertEqual(len(page_one_calls), 1)
        self.assertEqual(
            checkpoint.value["page_1_revalidation"]["fresh_calls_started"], 1
        )
        self.assertEqual(
            checkpoint.value["inherited_predecessor"]["network_attempts_recounted"], 0
        )
        self.assertEqual(
            checkpoint.value["inherited_predecessor"]["raw_entities_rewritten"], 0
        )
        self.assertEqual(report["reused_completed_dates"], ["20240102"])
        self.assertEqual(report["predecessor_rerun"], False)
        self.assertEqual(report["page_1_fresh_revalidations"], 1)
        current_keys = list(custody.objects)
        self.assertTrue(current_keys)
        expected_namespace = (
            page100.RAW_KEY_PREFIX
            + "_pilot_generation/"
            + f"runtime_lock_id={bindings.runtime_lock_id}/"
            + f"pilot_run_id={bindings.pilot_run_id}/"
        )
        self.assertTrue(all(key.startswith(expected_namespace) for key in current_keys))
        self.assertNotIn(bindings.predecessor.page_one.object_key, custody.objects)

    def test_complete_report_exposes_owner_required_metrics_without_unknown_zero(self):
        report, checkpoint, _, _, _, _ = self.run_fixture()
        self.assertEqual(checkpoint.value["state"], "COMPLETE")
        for key in (
            "completed_date_count", "blocked_date_count", "rows_per_date",
            "pages_per_date", "total_rows", "total_page_acquisitions",
            "total_network_attempts", "total_retries", "raw_bytes_total",
            "s3_raw_object_count",
        ):
            self.assertIn(key, report)
        self.assertEqual(report["completed_date_count"], 17)
        self.assertEqual(report["blocked_date_count"], 0)
        self.assertEqual(set(report["rows_per_date"]), {"min", "p50", "p90", "max"})
        self.assertEqual(set(report["pages_per_date"]), {"min", "p50", "p90", "max"})
        self.assertEqual(
            report["quota"]["remaining_governed_margin"]["external_attempts"],
            "UNKNOWN_NOT_INSTRUMENTED",
        )
        self.assertEqual(
            report["distributions"]["provider_result_code_counts_aggregate"],
            "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR",
        )
        revalidation = report["page_1_revalidation"]
        self.assertTrue(revalidation["raw_digest_match"])
        self.assertTrue(revalidation["page_identity_match"])
        self.assertTrue(revalidation["total_count_match"])
        self.assertTrue(revalidation["all_invariants_pass"])
        verification = report["s3_custody"]["verification"]
        self.assertEqual(
            verification["sha256"]["aggregate_verified_objects"],
            report["s3_raw_object_count"],
        )
        self.assertEqual(
            verification["bytes"]["aggregate_verified_objects"],
            report["s3_raw_object_count"],
        )

    def test_post_reservation_deadline_records_zero_page_one_calls(self):
        bindings, bundle, historical, body = predecessor_fixture()
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)
        transport = FakeTransport(empty_or_historical_handler(body), checkpoint)
        ticks = iter((0.0, 2.0))
        with self.assertRaises(page100.SelfDeadlineExceededError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK,
                deadline_monotonic=1.0,
                monotonic_fn=lambda: next(ticks),
                sleep_fn=lambda _: None,
            )
        self.assertEqual(transport.calls, [])
        self.assertEqual(
            checkpoint.value["page_1_revalidation"]["fresh_calls_started"], 0
        )
        self.assertEqual(checkpoint.value["provider_api_network_attempts"], 0)
        self.assertEqual(checkpoint.value["quota_reservations"], 1)

    def test_underfilled_intermediate_page_blocks_before_next_page(self):
        bindings, bundle, historical, historical_body = predecessor_fixture()
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)

        def handler(params, _ordinal):
            bas_dt = params["basDt"]
            page_no = int(params["pageNo"])
            if bas_dt == "20240131":
                return response(historical_body)
            if bas_dt == "20240329" and page_no == 1:
                rows = [item(bas_dt, n) for n in range(5)]
                return response(finance_body(bas_dt, 1, 15, rows))
            return response(finance_body(bas_dt, page_no, 0, []))

        transport = FakeTransport(handler, checkpoint)
        with self.assertRaises(sa.SourceProtocolError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(checkpoint.value["state"], "BLOCKED")
        self.assertEqual(checkpoint.value["pagination_drift_events"], 1)
        self.assertEqual(
            checkpoint.value["pagination_drift_records"][0]["kind"],
            "UNDERFILLED_INTERMEDIATE_PAGE",
        )
        self.assertFalse(any(
            call["basDt"] == "20240329" and call["pageNo"] == "2"
            for call in transport.calls
        ))

    def test_page_one_raw_checkpoint_gap_reuses_sealed_entity_no_second_call(self):
        bindings, bundle, historical, body = predecessor_fixture()
        checkpoint = FakeCheckpointStore(fail_raw_once=True)
        custody = FakeCustody(bindings, historical)
        first = FakeTransport(empty_or_historical_handler(body), checkpoint)
        with self.assertRaises(sa.CheckpointConflictError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=first, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(
            len([c for c in first.calls if c["basDt"] == "20240131"]), 1
        )
        second = FakeTransport(empty_or_historical_handler(body), checkpoint)
        page100.run_page100_pilot(
            page100.Page100Spec(), bindings, bundle,
            transport=second, custody=custody, claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
            secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
        )
        self.assertFalse(any(
            c["basDt"] == "20240131" and c["pageNo"] == "1"
            for c in second.calls
        ))
        self.assertEqual(
            checkpoint.value["page_1_revalidation"]["fresh_calls_started"], 1
        )

    def test_shifted_page_one_blocks_before_page_two_after_one_call(self):
        bindings, bundle, historical, _ = predecessor_fixture()
        shifted = finance_body(
            "20240131", 1, 1, [item("20240131", 999)]
        )
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)
        transport = FakeTransport(
            lambda _params, _ordinal: response(shifted), checkpoint
        )
        with self.assertRaises(sa.SourceProtocolError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(checkpoint.value["state"], "BLOCKED")
        self.assertEqual(
            checkpoint.value["page_1_revalidation"]["state"],
            "BLOCKED_THREE_WAY_SHIFT",
        )

    def test_page_one_retryable_response_is_not_called_twice(self):
        bindings, bundle, historical, _ = predecessor_fixture()
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)
        transport = FakeTransport(
            lambda _params, _ordinal: response(b"busy", 503), checkpoint
        )
        with self.assertRaises(sa.SourceTransportError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(
            checkpoint.value["page_1_revalidation"]["fresh_calls_started"], 1
        )

    def test_page_cap_boundary_100_passes_and_101_blocks_with_telemetry(self):
        first_items = [item("20240131", n) for n in range(10)]
        bindings, bundle, historical, first_body = predecessor_fixture(
            total=1000, first_items=first_items
        )
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, historical)

        def hundred_pages(params, _ordinal):
            bas_dt = params["basDt"]
            page_no = int(params["pageNo"])
            if bas_dt == "20240131":
                start = (page_no - 1) * 10
                rows = [item(bas_dt, n) for n in range(start, start + 10)]
                return response(finance_body(bas_dt, page_no, 1000, rows))
            return response(finance_body(bas_dt, page_no, 0, []))

        transport = FakeTransport(hundred_pages, checkpoint)
        report = page100.run_page100_pilot(
            page100.Page100Spec(), bindings, bundle,
            transport=transport, custody=custody, claim_store=custody,
            checkpoint_store=checkpoint,
            writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
            secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
        )
        self.assertEqual(
            checkpoint.value["date_results"][1]["page_count"], 100
        )
        self.assertEqual(report["completed_date_count"], 17)

        # A later date can still fail at 101 pages; telemetry is durable before
        # any request for page 2.
        bindings2, bundle2, historical2, body2 = predecessor_fixture()
        checkpoint2 = FakeCheckpointStore()
        custody2 = FakeCustody(bindings2, historical2)

        def over_cap(params, _ordinal):
            if params["basDt"] == "20240131":
                return response(body2)
            rows = [item(params["basDt"], n) for n in range(10)]
            return response(
                finance_body(params["basDt"], 1, 1001, rows)
            )

        transport2 = FakeTransport(over_cap, checkpoint2)
        with self.assertRaises(page100.PageCeilingError) as captured:
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings2, bundle2,
                transport=transport2, custody=custody2,
                claim_store=custody2, checkpoint_store=checkpoint2,
                writer_id=f"github-run:{bindings2.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(captured.exception.telemetry["expected_pages"], 101)
        self.assertTrue(captured.exception.telemetry["blocked_before_page_2"])
        self.assertEqual(
            checkpoint2.value["page_cap_telemetry"]["expected_pages"], 101
        )
        self.assertEqual(checkpoint2.value["state"], "BLOCKED")
        over_date = page100.PRIMARY_DATES[2]
        self.assertFalse(any(
            c["basDt"] == over_date and c["pageNo"] == "2"
            for c in transport2.calls
        ))

    def test_full_predecessor_mirror_bytes_are_preserved(self):
        predecessor_rows = (
            b'{"original":1}\r\n'
            b'{"pilot_run_id":"FINANCE-LIVE-PILOT-20260828192737","old":1}\n'
        )
        current = {"pilot_run_id": page100.PILOT_RUN_ID, "new": 1}
        first = page100.append_current_rows(
            predecessor_rows, page100.PILOT_RUN_ID, [current]
        )
        self.assertTrue(first.startswith(predecessor_rows))
        self.assertEqual(
            page100.pre_current_pilot_bytes(first, page100.PILOT_RUN_ID),
            predecessor_rows,
        )
        second = page100.append_current_rows(
            first, page100.PILOT_RUN_ID,
            [{"pilot_run_id": page100.PILOT_RUN_ID, "new": 2}],
        )
        self.assertTrue(second.startswith(predecessor_rows))
        self.assertEqual(second.count(b"FINANCE-LIVE-PILOT"), 1)
        self.assertEqual(second.count(page100.PILOT_RUN_ID.encode()), 1)

    def test_exact_predecessor_readback_mismatch_blocks_before_provider(self):
        bindings, bundle, historical, body = predecessor_fixture()
        bad_historical = replace(historical, readback_bytes=historical.entity_bytes + 1)
        checkpoint = FakeCheckpointStore()
        custody = FakeCustody(bindings, bad_historical)
        transport = FakeTransport(empty_or_historical_handler(body), checkpoint)
        with self.assertRaises(page100.HistoricalEvidenceError):
            page100.run_page100_pilot(
                page100.Page100Spec(), bindings, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{bindings.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(transport.calls, [])
        self.assertIsNone(checkpoint.value)
        self.assertIsNone(custody.claim_payload)

    def test_quota_day_global_claim_blocks_competing_successor(self):
        _, _, custody, _, bindings, bundle = self.run_fixture()
        competitor = replace(bindings, github_run_id=40000000001)
        checkpoint = FakeCheckpointStore()
        transport = FakeTransport(
            lambda params, ordinal: response(
                finance_body(params["basDt"], int(params["pageNo"]), 0, [])
            ),
            checkpoint,
        )
        with self.assertRaises(sa.CheckpointConflictError):
            page100.run_page100_pilot(
                page100.Page100Spec(), competitor, bundle,
                transport=transport, custody=custody, claim_store=custody,
                checkpoint_store=checkpoint,
                writer_id=f"github-run:{competitor.github_run_id}:attempt:1",
                secrets=(), clock=PILOT_CLOCK, sleep_fn=lambda _: None,
            )
        self.assertEqual(transport.calls, [])
        self.assertIsNone(checkpoint.value)


if __name__ == "__main__":
    unittest.main()
