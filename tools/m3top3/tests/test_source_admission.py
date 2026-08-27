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


if __name__ == "__main__":
    unittest.main()
