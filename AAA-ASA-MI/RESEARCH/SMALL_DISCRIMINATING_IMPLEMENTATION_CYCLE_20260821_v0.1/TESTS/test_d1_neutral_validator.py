import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).parents[1] / "TOOLS" / "d1_neutral_validator.py"
spec = importlib.util.spec_from_file_location("d1_neutral_validator", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIXTURE = {
    "fixture_id": "AAA-ASA-MI-D1-PROMISE-ORIGIN-v0.1",
    "variants": [{"id": v} for v in ["D1-A", "D1-B", "D1-C", "D1-D", "D1-E"]],
}
FIELDS = (
    "BEHAVIOR_RELATION",
    "MEMORY_CONTENT_RELATION",
    "PROMISE_ORIGIN_STATUS",
    "DESCENT_STATUS",
    "COMMITMENT_OR_OBLIGATION_STATUS",
    "CONTINUATION_STATUS",
    "AUTHORITY_STATUS",
    "SAME_PERSONA_STATUS",
    "UNKNOWN_NOT_PROVEN_OUT_OF_SCOPE",
    "DECISION_DEPENDENCIES",
    "CHANGED_INPUT_CAUSING_OUTPUT_DELTA",
)


def make_result(vid):
    result = {k: {"native": "UNSPECIFIED"} for k in FIELDS[:8]}
    result.update(
        {
            "UNKNOWN_NOT_PROVEN_OUT_OF_SCOPE": [],
            "DECISION_DEPENDENCIES": [],
            "CHANGED_INPUT_CAUSING_OUTPUT_DELTA": [],
            "variant_id": vid,
            "EVIDENCE_MODE": "EXECUTABLE_REPLAY",
        }
    )
    if vid == "D1-B":
        result["PROMISE_ORIGIN_STATUS"] = {"native": "NOT_PROVEN"}
    if vid == "D1-E":
        result["AUTHORITY_STATUS"] = {"X": "GRANTED", "Y": "REVOKED"}
    return result


class NeutralValidatorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.fixture_path = self.dir / "fixture.json"
        raw = json.dumps(FIXTURE, separators=(",", ":")).encode()
        self.fixture_path.write_bytes(raw)
        self.digest = hashlib.sha256(raw).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def write_output(self, mutate=None):
        out = {
            "adapter_id": "neutral-test",
            "candidate_position": "A1",
            "candidate_exact_sha256": "0" * 64,
            "fixture_id": FIXTURE["fixture_id"],
            "fixture_sha256": self.digest,
            "candidate_semantics_unchanged": True,
            "variant_results": [
                make_result(v) for v in ["D1-A", "D1-B", "D1-C", "D1-D", "D1-E"]
            ],
        }
        if mutate:
            mutate(out)
        path = self.dir / "out.json"
        path.write_text(json.dumps(out), encoding="utf-8")
        return path

    def test_accepts_neutral_well_formed_output(self):
        receipt = mod.validate(self.fixture_path, self.write_output())
        self.assertEqual(receipt["validator_state"], "PASS_NEUTRAL_STRUCTURAL_CONTROLS")

    def test_rejects_fixture_digest_mismatch(self):
        path = self.write_output(lambda o: o.__setitem__("fixture_sha256", "1" * 64))
        with self.assertRaises(mod.ValidationError):
            mod.validate(self.fixture_path, path)

    def test_rejects_missing_variant(self):
        path = self.write_output(lambda o: o["variant_results"].pop())
        with self.assertRaises(mod.ValidationError):
            mod.validate(self.fixture_path, path)

    def test_rejects_d1b_not_proven_to_false(self):
        def mutate(out):
            for result in out["variant_results"]:
                if result["variant_id"] == "D1-B":
                    result["PROMISE_ORIGIN_STATUS"] = {"native": "FALSE"}

        with self.assertRaises(mod.ValidationError):
            mod.validate(self.fixture_path, self.write_output(mutate))

    def test_rejects_bare_boolean_axis(self):
        def mutate(out):
            out["variant_results"][0]["BEHAVIOR_RELATION"] = True

        with self.assertRaises(mod.ValidationError):
            mod.validate(self.fixture_path, self.write_output(mutate))


if __name__ == "__main__":
    unittest.main()
