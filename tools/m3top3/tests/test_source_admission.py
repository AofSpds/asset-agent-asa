import importlib.util
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
