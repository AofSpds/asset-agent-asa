import importlib.util
import hashlib
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "source_admission.py"
SPEC = importlib.util.spec_from_file_location("source_admission", MODULE_PATH)
sa = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = sa
SPEC.loader.exec_module(sa)


SYNTHETIC_SECRET = "A+B/C==syntheticValue12345"


class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json", "Authorization": "must-not-copy"}

    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def getcode(self):
        return self.status


class SequenceOpener:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)

    def open(self, request, timeout):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def finance_body(bas_dt, page_no, page_size, total_count, items, *, result_code="00"):
    return sa.canonical_json_bytes({
        "response": {
            "header": {"resultCode": result_code, "resultMsg": "NORMAL"},
            "body": {
                "items": {"item": items},
                "numOfRows": page_size,
                "pageNo": page_no,
                "totalCount": total_count,
            },
        },
    })


class MemoryCustodySink:
    def __init__(self, trace=None, *, mismatch=False):
        self.trace = trace if trace is not None else []
        self.mismatch = mismatch
        self.entities = {}

    def seal_and_verify(self, body, draft):
        digest = hashlib.sha256(body).hexdigest()
        locator = "memory://offline/" + digest
        self.trace.append(("seal", draft["safe_params"]["basDt"], draft["safe_params"]["pageNo"]))
        prior = self.entities.get(locator)
        if prior is not None and prior != body:
            raise sa.AdmissionError("fixture custody collision")
        self.entities[locator] = body
        return sa.CustodyWriteResult(
            storage_locator=locator,
            entity_bytes=len(body),
            entity_sha256=digest,
            readback_bytes=len(body),
            readback_sha256=("0" * 64 if self.mismatch else digest),
            canonical=False,
        )


class OfflinePilotFixture:
    def __init__(self, pages, checkpoint_path, *, sink=None, records=None):
        self.pages = pages
        self.trace = []
        self.sink = sink or MemoryCustodySink(self.trace)
        self.records = records if records is not None else []
        self.store = sa.JsonCheckpointStore(checkpoint_path)
        self.ordinal = 0
        self.reserve_error = None

    def reserve(self, provider, operation, request_id):
        self.trace.append(("reserve", provider, operation))
        if self.reserve_error is not None:
            raise self.reserve_error
        self.ordinal += 1
        return sa.QuotaReservation(provider, "2026-08-28", self.ordinal, operation)

    def acquire(self, params, reservation):
        key = (params["basDt"], int(params["pageNo"]))
        self.trace.append(("acquire", *key))
        outcome = self.pages[key]
        if isinstance(outcome, Exception):
            raise outcome
        return sa.AcquiredRawEntity(
            body=outcome,
            http_status=200,
            acquired_at_utc="2026-08-28T05:00:00+00:00",
            provider_api_network_attempts=0,
        )

    def leak_scan(self, body):
        self.trace.append(("leak_scan", hashlib.sha256(body).hexdigest()))

    def append_record(self, record):
        self.trace.append(("index", record["safe_params"]["basDt"], record["safe_params"]["pageNo"]))
        if record not in self.records:
            self.records.append(dict(record))

    def run(self, spec):
        return sa.run_finance_historical_pilot(
            spec,
            reserve_attempt=self.reserve,
            acquire_raw_once=self.acquire,
            leak_scan=self.leak_scan,
            custody_sink=self.sink,
            custody_index_append=self.append_record,
            checkpoint_store=self.store,
            clock=lambda: datetime(2026, 8, 28, 5, 0, tzinfo=timezone.utc),
        )


def pilot_spec(dates, *, max_pages=3, max_acquisitions=20, authority="a" * 64):
    return sa.FinancePilotSpec(
        ordered_dates=tuple(dates),
        target_start_date="2024-01-01",
        target_end_date="2026-08-14",
        requested_page_size=2,
        max_pages_per_date=max_pages,
        max_page_acquisitions=max_acquisitions,
        authority_binding_sha256=authority,
    )


class SourceAdmissionTests(unittest.TestCase):
    def test_decoded_secret_contract(self):
        self.assertEqual(sa.validate_decoded_secret("S", SYNTHETIC_SECRET), SYNTHETIC_SECRET)
        opaque_hex_key = "a1" * 32
        self.assertEqual(sa.validate_decoded_secret("S", opaque_hex_key), opaque_hex_key)
        for value in (None, "", "  ", "abc defghijklmnopqrstuvwxyz", "ABC%2BDEF012345678901234"):
            with self.subTest(value=value):
                with self.assertRaises(sa.CredentialContractError):
                    sa.validate_decoded_secret("S", value)

    def test_data_go_kr_ksd_identity_and_market_alias(self):
        self.assertEqual(sa.KSD_SOURCE_ID, "M3TOP3-KSD-CORP-DATA-GO-KR-v1")
        self.assertEqual(sa.KSD_BASE_URL, "https://apis.data.go.kr/B552481/CorpSvc")
        self.assertIn("listNm", sa.KSD_MARKET_NAME_FIELDS)

    def test_exactly_once_query_encoding(self):
        url = sa.encoded_query("https://example.invalid/op", {"a": "x", "serviceKey": "ignored"}, SYNTHETIC_SECRET)
        self.assertIn("serviceKey=A%2BB%2FC%3D%3DsyntheticValue12345", url)
        self.assertNotIn("%252B", url)
        parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        self.assertEqual(parsed["serviceKey"], [SYNTHETIC_SECRET])

    def test_json_duplicate_key_rejected(self):
        with self.assertRaises(sa.SourceProtocolError):
            sa.parse_entity_bytes(b'{"a":1,"a":2}')

    def test_unsafe_xml_rejected(self):
        with self.assertRaises(sa.SourceProtocolError):
            sa.parse_entity_bytes(b'<!DOCTYPE x [<!ENTITY y "z">]><x>&y;</x>')

    def test_finance_valid_empty(self):
        parsed = sa.parse_entity_bytes(b'{"response":{"header":{"resultCode":"00"},"body":{"totalCount":0,"items":{}}}}')
        result = sa.classify_provider("FINANCE", parsed)
        self.assertEqual(result["state"], "VALID_EMPTY")
        self.assertEqual(result["total_count"], 0)

    def test_ksd_nodata_and_schema_error(self):
        nodata = sa.parse_entity_bytes(b'<response><header><resultCode>3</resultCode></header></response>')
        self.assertEqual(sa.classify_provider("KSD", nodata)["state"], "NODATA")
        schema = sa.parse_entity_bytes(b'<response><header><resultCode>11</resultCode></header></response>')
        with self.assertRaises(sa.SourceProtocolError):
            sa.classify_provider("KSD", schema)

    def test_single_item_xml_shape(self):
        parsed = sa.parse_entity_bytes(b'<response><header><resultCode>00</resultCode></header><body><items><item><issucoCustno>6069</issucoCustno></item></items></body></response>')
        result = sa.classify_provider("KSD", parsed)
        self.assertEqual(result["items"][0]["issucoCustno"], "6069")

    def test_quota_boundary_and_kst_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = sa.QuotaLedger(Path(tmp) / "quota.jsonl", now=lambda: datetime(2026, 8, 27, 16, 1, tzinfo=timezone.utc))
            original = sa.QUOTA_CAPS["KSD"]
            sa.QUOTA_CAPS["KSD"] = 2
            try:
                self.assertEqual(ledger.reserve("KSD", "a", "r1").quota_day_kst, "2026-08-28")
                ledger.reserve("KSD", "b", "r2")
                with self.assertRaises(sa.QuotaBoundaryError):
                    ledger.reserve("KSD", "c", "r3")
            finally:
                sa.QUOTA_CAPS["KSD"] = original

    def test_each_retry_consumes_quota_and_error_is_sanitized(self):
        body = b'{"response":{"header":{"resultCode":"00"},"body":{"totalCount":0}}}'
        opener = SequenceOpener([urllib.error.URLError("contains-url-like-details"), FakeResponse(body)])
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "quota.jsonl"
            ledger = sa.QuotaLedger(ledger_path)
            received, receipt = sa.fetch_entity(
                provider="FINANCE",
                source_id="S",
                endpoint="https://example.invalid/op",
                operation="op",
                params={"pageNo": 1},
                secret=SYNTHETIC_SECRET,
                ledger=ledger,
                opener=opener,
                sleep_fn=lambda _: None,
            )
            self.assertEqual(received, body)
            self.assertEqual(receipt["attempt"], 2)
            self.assertEqual(len(ledger_path.read_text(encoding="utf-8").splitlines()), 2)
            self.assertNotIn("authorization", json.dumps(receipt).lower())

    def test_secret_echo_rejected_before_custody(self):
        opener = SequenceOpener([FakeResponse(("prefix" + SYNTHETIC_SECRET).encode())])
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(sa.CredentialContractError) as caught:
                sa.fetch_entity(
                    provider="FINANCE",
                    source_id="S",
                    endpoint="https://example.invalid/op",
                    operation="op",
                    params={},
                    secret=SYNTHETIC_SECRET,
                    ledger=sa.QuotaLedger(Path(tmp) / "quota.jsonl"),
                    opener=opener,
                )
            self.assertNotIn(SYNTHETIC_SECRET, str(caught.exception))

    def test_request_id_excludes_secret_and_preserves_omitted_vs_empty(self):
        a = sa.canonical_request_id("S", "https://x.invalid", "op", {"filter": ""})
        b = sa.canonical_request_id("S", "https://x.invalid", "op", {})
        self.assertNotEqual(a, b)
        self.assertEqual(a, sa.canonical_request_id("S", "https://x.invalid", "op", {"filter": ""}))


    def test_pagination_snapshot_complete_and_resume_stable(self):
        pages = [
            {"page_no": 1, "page_size": 2, "total_count": 3, "items": [{"id": 1}, {"id": 2}]},
            {"page_no": 2, "page_size": 2, "total_count": 3, "items": [{"id": 3}]},
        ]
        snapshot = sa.validate_pagination_snapshot(pages)
        self.assertEqual(snapshot["state"], "DATE_COMPLETE")
        self.assertEqual(snapshot["item_count"], 3)
        sa.assert_resume_page_1(snapshot, pages[0])

    def test_pagination_snapshot_rejects_protocol_drift(self):
        cases = [
            [{"page_no": 2, "page_size": 2, "total_count": 1, "items": [{"id": 1}]}],
            [{"page_no": 1, "page_size": 2, "total_count": 3, "items": [{"id": 1}]}, {"page_no": 2, "page_size": 2, "total_count": 4, "items": [{"id": 2}]}],
            [{"page_no": 1, "page_size": 2, "total_count": 3, "items": [{"id": 1}, {"id": 2}]}, {"page_no": 2, "page_size": 2, "total_count": 3, "items": []}],
            [{"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]}, {"page_no": 2, "page_size": 1, "total_count": 2, "items": [{"id": 1}]}],
        ]
        for pages in cases:
            with self.subTest(pages=pages):
                with self.assertRaises(sa.SourceProtocolError):
                    sa.validate_pagination_snapshot(pages)

    def test_resume_page_1_shift_rejected(self):
        page = {"page_no": 1, "page_size": 2, "total_count": 1, "items": [{"id": 1}]}
        snapshot = sa.validate_pagination_snapshot([page])
        shifted = {**page, "total_count": 2}
        with self.assertRaises(sa.SourceProtocolError):
            sa.assert_resume_page_1(snapshot, shifted)

    def test_bounded_collector_closes_complete_snapshot_from_returned_page_size(self):
        pages = {
            1: {"page_no": 1, "page_size": 2, "total_count": 3, "items": [{"id": 1}, {"id": 2}]},
            2: {"page_no": 2, "page_size": 2, "total_count": 3, "items": [{"id": 3}]},
        }
        requested = []

        def fetch_page(page_no):
            requested.append(page_no)
            return pages[page_no]

        result = sa.collect_bounded_pagination_snapshot(fetch_page, max_pages=2)
        self.assertEqual(requested, [1, 2])
        self.assertEqual(result["state"], "DATE_COMPLETE")
        self.assertEqual(result["snapshot"]["item_count"], 3)
        self.assertFalse(result["resumed"])

    def test_bounded_collector_rejects_each_contract_pagination_drift(self):
        cases = {
            "boolean_page_number": [
                {"page_no": True, "page_size": 1, "total_count": 1, "items": [{"id": 1}]},
            ],
            "boolean_total_count": [
                {"page_no": 1, "page_size": 1, "total_count": True, "items": [{"id": 1}]},
            ],
            "boolean_page_size": [
                {"page_no": 1, "page_size": True, "total_count": 1, "items": [{"id": 1}]},
            ],
            "echoed_page_number": [
                {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
                {"page_no": 3, "page_size": 1, "total_count": 2, "items": [{"id": 2}]},
            ],
            "total_count_shift": [
                {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
                {"page_no": 2, "page_size": 1, "total_count": 3, "items": [{"id": 2}]},
            ],
            "page_size_shift": [
                {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
                {"page_no": 2, "page_size": 2, "total_count": 2, "items": [{"id": 2}]},
            ],
            "empty_intermediate_page": [
                {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
                {"page_no": 2, "page_size": 1, "total_count": 2, "items": []},
            ],
            "repeated_whole_page": [
                {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
                {"page_no": 2, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
            ],
            "date_complete_item_count": [
                {"page_no": 1, "page_size": 2, "total_count": 3, "items": [{"id": 1}]},
                {"page_no": 2, "page_size": 2, "total_count": 3, "items": [{"id": 2}]},
            ],
        }
        for name, rows in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(sa.SourceProtocolError):
                    sa.collect_bounded_pagination_snapshot(lambda page_no: rows[page_no - 1], max_pages=2)

    def test_bounded_collector_enforces_frozen_page_ceiling_before_page_two(self):
        requested = []

        def fetch_page(page_no):
            requested.append(page_no)
            return {"page_no": page_no, "page_size": 2, "total_count": 5, "items": [{"id": 1}, {"id": 2}]}

        with self.assertRaises(sa.QuotaBoundaryError):
            sa.collect_bounded_pagination_snapshot(fetch_page, max_pages=2)
        self.assertEqual(requested, [1])

    def test_bounded_collector_quarantines_page_two_before_page_three(self):
        page_1 = {"page_no": 1, "page_size": 1, "total_count": 3, "items": [{"id": 1}]}
        page_3 = {"page_no": 3, "page_size": 1, "total_count": 3, "items": [{"id": 3}]}
        drift_cases = {
            "echoed_page_number": {"page_no": 3, "page_size": 1, "total_count": 3, "items": [{"id": 2}]},
            "total_count_shift": {"page_no": 2, "page_size": 1, "total_count": 4, "items": [{"id": 2}]},
            "page_size_shift": {"page_no": 2, "page_size": 2, "total_count": 3, "items": [{"id": 2}]},
            "empty_intermediate_page": {"page_no": 2, "page_size": 1, "total_count": 3, "items": []},
            "repeated_whole_page": {"page_no": 2, "page_size": 1, "total_count": 3, "items": [{"id": 1}]},
        }
        for name, page_2 in drift_cases.items():
            requested = []
            pages = {1: page_1, 2: page_2, 3: page_3}

            def fetch_page(page_no):
                requested.append(page_no)
                return pages[page_no]

            with self.subTest(name=name):
                with self.assertRaises(sa.SourceProtocolError):
                    sa.collect_bounded_pagination_snapshot(fetch_page, max_pages=3)
                self.assertEqual(requested, [1, 2])

    def test_bounded_collector_resume_revalidates_page_one_before_page_two(self):
        original_pages = [
            {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
            {"page_no": 2, "page_size": 1, "total_count": 2, "items": [{"id": 2}]},
        ]
        prior = sa.validate_pagination_snapshot(original_pages)
        stable = sa.collect_bounded_pagination_snapshot(
            lambda page_no: original_pages[page_no - 1], max_pages=2, resume_snapshot=prior
        )
        self.assertTrue(stable["resumed"])

        requested = []

        def shifted_fetch(page_no):
            requested.append(page_no)
            if page_no == 1:
                return {**original_pages[0], "items": [{"id": 99}]}
            return original_pages[page_no - 1]

        with self.assertRaises(sa.SourceProtocolError):
            sa.collect_bounded_pagination_snapshot(
                shifted_fetch, max_pages=2, resume_snapshot=prior
            )
        self.assertEqual(requested, [1])

    def test_finance_pilot_date_plan_is_exact_and_never_expanded(self):
        dates = ("20240101", "20240229", "20260814")
        self.assertEqual(
            sa.validate_finance_pilot_dates(
                dates, start_date="2024-01-01", end_date="2026-08-14"
            ),
            dates,
        )
        params = sa.finance_request_params("20240229", 1, 10)
        self.assertEqual(params["pageNo"], "1")
        self.assertEqual(params["numOfRows"], "10")
        self.assertEqual(params["issuCmpyKsdCustNo"], "")
        self.assertNotIn("serviceKey", params)
        invalid = [
            (),
            ("20240101", "20240101"),
            ("20240201", "20240101"),
            ("20240230",),
            ("20230814",),
            ("20260815",),
        ]
        for plan in invalid:
            with self.subTest(plan=plan):
                with self.assertRaises(sa.SourceProtocolError):
                    sa.validate_finance_pilot_dates(
                        plan, start_date="2024-01-01", end_date="2026-08-14"
                    )

    def test_finance_entity_to_page_has_strict_wire_contract(self):
        body = finance_body(
            "20240102", 1, 2, 1, [{"basDt": "20240102", "id": 1}]
        )
        page = sa.finance_entity_to_page(
            body, expected_bas_dt="20240102", expected_page_no=1
        )
        self.assertEqual(page["page_size"], 2)
        self.assertEqual(page["total_count"], 1)
        missing_code = sa.canonical_json_bytes({
            "response": {
                "body": {
                    "items": {"item": []}, "numOfRows": 2, "pageNo": 1, "totalCount": 0,
                }
            }
        })
        boolean_total = sa.canonical_json_bytes({
            "response": {
                "header": {"resultCode": "00"},
                "body": {
                    "items": {"item": []}, "numOfRows": 2, "pageNo": 1, "totalCount": True,
                },
            }
        })
        wrong_date = finance_body(
            "20240102", 1, 2, 1, [{"basDt": "20240103", "id": 1}]
        )
        noncanonical_success_codes = (
            finance_body("20240102", 1, 2, 0, [], result_code="000"),
            finance_body("20240102", 1, 2, 0, [], result_code=0),
        )
        cases = [
            (missing_code, "20240102", 1),
            (boolean_total, "20240102", 1),
            (body, "20240102", 2),
            (wrong_date, "20240102", 1),
            *((candidate, "20240102", 1) for candidate in noncanonical_success_codes),
        ]
        for candidate, bas_dt, page_no in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(sa.SourceProtocolError):
                    sa.finance_entity_to_page(
                        candidate, expected_bas_dt=bas_dt, expected_page_no=page_no
                    )

    def test_pagination_public_page_one_identity_and_validated_hook(self):
        pages = {
            1: {"page_no": 1, "page_size": 1, "total_count": 2, "items": [{"id": 1}]},
            2: {"page_no": 2, "page_size": 1, "total_count": 2, "items": [{"id": 2}]},
        }
        observed = []
        result = sa.collect_bounded_pagination_snapshot(
            lambda page_no: pages[page_no],
            max_pages=2,
            on_page_validated=lambda page_no, page, count: observed.append((page_no, count)),
        )
        self.assertEqual(observed, [(1, 1), (2, 2)])
        self.assertEqual(
            result["snapshot"]["page_1_identity"],
            sa.pagination_page_1_identity(pages[1]),
        )

    def test_finance_pilot_mixed_dates_is_custody_first_and_deterministic(self):
        pages = {
            ("20240102", 1): finance_body(
                "20240102", 1, 2, 3,
                [{"basDt": "20240102", "id": 1}, {"basDt": "20240102", "id": 2}],
            ),
            ("20240102", 2): finance_body(
                "20240102", 2, 2, 3, [{"basDt": "20240102", "id": 3}],
            ),
            ("20240103", 1): finance_body("20240103", 1, 2, 0, []),
        }
        with tempfile.TemporaryDirectory() as tmp:
            fixture = OfflinePilotFixture(pages, Path(tmp) / "checkpoint.json")
            result = fixture.run(pilot_spec(("20240102", "20240103")))
            self.assertEqual(result["state"], "OFFLINE_FIXTURE_COMPLETE_NO_PROMOTION")
            self.assertEqual(result["completed_dates"], ["20240102", "20240103"])
            self.assertEqual(result["page_acquisitions"], 3)
            self.assertEqual(len(fixture.records), 3)
            required = {
                "source_id", "operation", "safe_params", "request_id", "attempt",
                "quota_day_kst", "http_status", "entity_bytes", "entity_sha256",
                "acquired_at_utc", "storage_locator",
            }
            self.assertTrue(all(set(record) == required for record in fixture.records))
            self.assertTrue(all("serviceKey" not in record["safe_params"] for record in fixture.records))
            effect_names = [row[0] for row in fixture.trace[:5]]
            self.assertEqual(effect_names, ["reserve", "acquire", "leak_scan", "seal", "index"])
            loaded, digest = fixture.store.load()
            self.assertEqual(digest, result["checkpoint_sha256"])
            self.assertEqual(loaded["current_date"], None)
            self.assertEqual(loaded["provider_api_network_attempts"], 0)

    def test_finance_pilot_valid_empty_uses_one_attempt_and_stops_no_promotion(self):
        pages = {("20240810", 1): finance_body("20240810", 1, 10, 0, [])}
        with tempfile.TemporaryDirectory() as tmp:
            spec = sa.FinancePilotSpec(
                ordered_dates=("20240810",),
                target_start_date="2024-01-01",
                target_end_date="2026-08-14",
                requested_page_size=10,
                max_pages_per_date=1,
                max_page_acquisitions=1,
                authority_binding_sha256="a" * 64,
            )
            fixture = OfflinePilotFixture(pages, Path(tmp) / "checkpoint.json")
            result = fixture.run(spec)
            self.assertEqual(result["state"], "STOP_NO_PROMOTION")
            self.assertEqual([row[:3] for row in fixture.trace if row[0] == "acquire"], [("acquire", "20240810", 1)])
            self.assertEqual(len(fixture.records), 1)

    def test_finance_pilot_quota_denial_precedes_fetch_and_custody(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = OfflinePilotFixture({}, Path(tmp) / "checkpoint.json")
            fixture.reserve_error = sa.QuotaBoundaryError("fixture quota boundary")
            with self.assertRaises(sa.QuotaBoundaryError):
                fixture.run(pilot_spec(("20240102",)))
            self.assertFalse(any(row[0] == "acquire" for row in fixture.trace))
            self.assertEqual(fixture.records, [])
            self.assertEqual(fixture.sink.entities, {})

    def test_finance_pilot_page_ceiling_stops_before_page_two(self):
        pages = {
            ("20240102", 1): finance_body(
                "20240102", 1, 2, 5,
                [{"basDt": "20240102", "id": 1}, {"basDt": "20240102", "id": 2}],
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            fixture = OfflinePilotFixture(pages, Path(tmp) / "checkpoint.json")
            with self.assertRaises(sa.QuotaBoundaryError):
                fixture.run(pilot_spec(("20240102",), max_pages=2))
            self.assertEqual(
                [row for row in fixture.trace if row[0] == "acquire"],
                [("acquire", "20240102", 1)],
            )
            self.assertEqual(len(fixture.records), 1)
            checkpoint, _ = fixture.store.load()
            self.assertEqual(checkpoint["current_date"]["state"], "BLOCKED")
            self.assertRegex(checkpoint["current_date"]["page_1_identity"], r"^[0-9a-f]{64}$")

    def test_finance_pilot_pagination_drift_preserves_raw_and_stops_later_pages(self):
        pages = {
            ("20240102", 1): finance_body(
                "20240102", 1, 1, 3, [{"basDt": "20240102", "id": 1}],
            ),
            ("20240102", 2): finance_body(
                "20240102", 2, 1, 4, [{"basDt": "20240102", "id": 2}],
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            fixture = OfflinePilotFixture(pages, Path(tmp) / "checkpoint.json")
            with self.assertRaises(sa.SourceProtocolError):
                fixture.run(pilot_spec(("20240102",), max_pages=4))
            self.assertEqual(
                [row for row in fixture.trace if row[0] == "acquire"],
                [("acquire", "20240102", 1), ("acquire", "20240102", 2)],
            )
            self.assertEqual(len(fixture.records), 2)
            checkpoint, _ = fixture.store.load()
            self.assertEqual(len(checkpoint["current_date"]["validated_pages"]), 1)

    def test_finance_pilot_resume_revalidates_page_one_then_completes(self):
        page_1 = finance_body(
            "20240102", 1, 1, 2, [{"basDt": "20240102", "id": 1}],
        )
        page_2 = finance_body(
            "20240102", 2, 1, 2, [{"basDt": "20240102", "id": 2}],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            records = []
            sink = MemoryCustodySink()
            first = OfflinePilotFixture(
                {
                    ("20240102", 1): page_1,
                    ("20240102", 2): sa.SourceTransportError("fixture stop"),
                },
                path,
                sink=sink,
                records=records,
            )
            spec = pilot_spec(("20240102",), max_acquisitions=4)
            with self.assertRaises(sa.SourceTransportError):
                first.run(spec)
            second = OfflinePilotFixture(
                {("20240102", 1): page_1, ("20240102", 2): page_2},
                path,
                sink=sink,
                records=records,
            )
            result = second.run(spec)
            self.assertEqual(result["completed_dates"], ["20240102"])
            self.assertEqual(
                [row for row in second.trace if row[0] == "acquire"],
                [("acquire", "20240102", 1), ("acquire", "20240102", 2)],
            )
            self.assertEqual(result["page_acquisitions"], 3)
            self.assertEqual(len(records), 2)

    def test_finance_pilot_completed_prefix_resume_has_no_side_effects(self):
        pages = {("20240102", 1): finance_body("20240102", 1, 2, 0, [])}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            spec = pilot_spec(("20240102",), max_pages=1)
            first = OfflinePilotFixture(pages, path)
            original = first.run(spec)
            second = OfflinePilotFixture({}, path)
            resumed = second.run(spec)
            self.assertEqual(second.trace, [])
            self.assertEqual(resumed["completed_dates"], original["completed_dates"])
            self.assertEqual(resumed["date_results"], original["date_results"])
            self.assertEqual(resumed["checkpoint_sha256"], original["checkpoint_sha256"])

    def test_finance_pilot_checkpoint_failure_never_silently_advances(self):
        pages = {("20240102", 1): finance_body("20240102", 1, 2, 0, [])}

        class FailOnFifthCas:
            def __init__(self, inner):
                self.inner = inner
                self.calls = 0

            def load(self):
                return self.inner.load()

            def compare_and_swap(self, value, expected_sha256):
                self.calls += 1
                if self.calls == 5:
                    raise sa.CheckpointConflictError("injected checkpoint failure")
                return self.inner.compare_and_swap(value, expected_sha256)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            spec = pilot_spec(("20240102",), max_pages=1, max_acquisitions=3)
            first = OfflinePilotFixture(pages, path)
            failing_store = FailOnFifthCas(first.store)
            with self.assertRaises(sa.CheckpointConflictError):
                sa.run_finance_historical_pilot(
                    spec,
                    reserve_attempt=first.reserve,
                    acquire_raw_once=first.acquire,
                    leak_scan=first.leak_scan,
                    custody_sink=first.sink,
                    custody_index_append=first.append_record,
                    checkpoint_store=failing_store,
                    clock=lambda: datetime(2026, 8, 28, 5, 0, tzinfo=timezone.utc),
                )
            checkpoint, _ = first.store.load()
            self.assertEqual(checkpoint["completed_dates"], [])
            self.assertEqual(checkpoint["next_date_index"], 0)
            self.assertIsNotNone(checkpoint["current_date"])
            resumed = OfflinePilotFixture(pages, path, sink=first.sink, records=first.records)
            result = resumed.run(spec)
            self.assertEqual(result["completed_dates"], ["20240102"])

    def test_finance_pilot_resume_page_one_shift_quarantines_before_page_two(self):
        original = finance_body(
            "20240102", 1, 1, 2, [{"basDt": "20240102", "id": 1}],
        )
        shifted = finance_body(
            "20240102", 1, 1, 2, [{"basDt": "20240102", "id": 99}],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            spec = pilot_spec(("20240102",), max_acquisitions=4)
            first = OfflinePilotFixture(
                {
                    ("20240102", 1): original,
                    ("20240102", 2): sa.SourceTransportError("fixture stop"),
                },
                path,
            )
            with self.assertRaises(sa.SourceTransportError):
                first.run(spec)
            second = OfflinePilotFixture(
                {
                    ("20240102", 1): shifted,
                    ("20240102", 2): finance_body(
                        "20240102", 2, 1, 2, [{"basDt": "20240102", "id": 2}],
                    ),
                },
                path,
            )
            with self.assertRaises(sa.SourceProtocolError):
                second.run(spec)
            self.assertEqual(
                [row for row in second.trace if row[0] == "acquire"],
                [("acquire", "20240102", 1)],
            )

    def test_finance_checkpoint_binding_and_cas_conflicts_have_zero_side_effects(self):
        pages = {("20240102", 1): finance_body("20240102", 1, 2, 0, [])}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            first = OfflinePilotFixture(pages, path)
            first.run(pilot_spec(("20240102",), max_pages=1))
            second = OfflinePilotFixture({}, path)
            with self.assertRaises(sa.CheckpointConflictError):
                second.run(pilot_spec(("20240102",), max_pages=2))
            self.assertEqual(second.trace, [])
            loaded, current_sha = second.store.load()
            with self.assertRaises(sa.CheckpointConflictError):
                second.store.compare_and_swap(loaded, "0" * 64)
            _, after_sha = second.store.load()
            self.assertEqual(after_sha, current_sha)

    def test_finance_pilot_rejects_custody_mismatch_before_parse_or_index(self):
        pages = {("20240102", 1): finance_body("20240102", 1, 2, 0, [])}
        with tempfile.TemporaryDirectory() as tmp:
            sink = MemoryCustodySink(mismatch=True)
            fixture = OfflinePilotFixture(
                pages, Path(tmp) / "checkpoint.json", sink=sink
            )
            with self.assertRaises(sa.SourceProtocolError):
                fixture.run(pilot_spec(("20240102",)))
            self.assertEqual(fixture.records, [])
            checkpoint, _ = fixture.store.load()
            self.assertEqual(checkpoint["page_acquisitions"], 0)

    def test_finance_pilot_has_no_ambient_network_path(self):
        pages = {("20240810", 1): finance_body("20240810", 1, 2, 0, [])}
        with tempfile.TemporaryDirectory() as tmp:
            fixture = OfflinePilotFixture(pages, Path(tmp) / "checkpoint.json")
            with mock.patch.object(
                sa.urllib.request, "build_opener", side_effect=AssertionError("ambient network")
            ):
                result = fixture.run(pilot_spec(("20240810",), max_pages=1))
            self.assertEqual(result["provider_api_network_attempts"], 0)
            self.assertEqual(result["remote_raw_custody_writes"], 0)
            self.assertFalse(result["bulk_acquisition_authorized"])


if __name__ == "__main__":
    unittest.main()
