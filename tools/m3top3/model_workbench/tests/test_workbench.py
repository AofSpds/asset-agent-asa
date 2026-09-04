from __future__ import annotations

import copy
import itertools
import json
import unittest
from collections import UserDict
from decimal import localcontext
from pathlib import Path
from types import MappingProxyType

from tools.m3top3.core import canonical_json_bytes, sha256_hex
from tools.m3top3.model_workbench import (
    FIXTURE_CLASS,
    LOCAL_FORBIDDEN_OUTCOME_FIELDS,
    WORKBENCH_SCHEMA_VERSION,
    EligibilityState,
    EvidenceState,
    FailClosedSetConstructor,
    ForwardModelWorkbench,
    IdentityCandidateRecall,
    OpportunityTailRanker,
    SetConstructionResult,
    WorkbenchContractError,
    WorkbenchInvariantError,
    run_workbench,
    validate_and_parse_envelope,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "synthetic_candidates_v0_1.json"
)


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def traces_by_id(result: dict) -> dict[str, dict]:
    return {item["candidate_id"]: item for item in result["candidate_traces"]}


def raw_identity(result: dict) -> list[tuple[str, int, str]]:
    return [
        (item["candidate_id"], item["raw_rank"], item["raw_score"])
        for item in result["raw_ranking"]
    ]


def selected_identity(result: dict) -> list[tuple[str, int, int]]:
    return [
        (item["candidate_id"], item["set_position"], item["raw_rank"])
        for item in result["selected_set"]
    ]


class TamperingSetConstructor:
    def __init__(self, mutate) -> None:
        self._mutate = mutate

    def construct(self, assessed, policy) -> SetConstructionResult:
        valid = FailClosedSetConstructor().construct(assessed, policy)
        selected = [copy.deepcopy(dict(item)) for item in valid.selected_set]
        decisions = [copy.deepcopy(dict(item)) for item in valid.decision_log]
        dispositions = copy.deepcopy(dict(valid.dispositions))
        self._mutate(selected, decisions, dispositions)
        return SetConstructionResult(
            selected_set=tuple(selected),
            decision_log=tuple(decisions),
            dispositions=dispositions,
        )


class ModelWorkbenchAuthorSelfCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_fixture()
        self.engine = ForwardModelWorkbench()

    def test_01_public_contract_import_and_parse(self) -> None:
        parsed = validate_and_parse_envelope(self.fixture)
        self.assertEqual(parsed.workbench_schema_version, WORKBENCH_SCHEMA_VERSION)
        self.assertEqual(parsed.fixture_class, FIXTURE_CLASS)
        self.assertFalse(parsed.official_outcome_data)
        self.assertEqual(len(parsed.candidates), 6)
        self.assertEqual(
            [state.value for state in EvidenceState],
            ["VERIFIED", "UNKNOWN", "NOT_FOUND", "PARTIAL", "CONFLICT", "STALE"],
        )
        self.assertEqual(
            [state.value for state in EligibilityState], ["TRUE", "FALSE", "UNKNOWN"]
        )

    def test_02_fixture_provenance_and_required_coverage(self) -> None:
        provenance = self.fixture["fixture_provenance"]
        self.assertEqual(provenance["provenance_class"], "HAND_AUTHORED_SYNTHETIC_DEV_ONLY")
        self.assertIs(provenance["contains_real_market_data"], False)
        self.assertIs(provenance["contains_official_w1_w8_data"], False)
        self.assertIs(provenance["contains_outcome_labels"], False)
        self.assertEqual(provenance["source_refs"], [])
        evidence_states = {
            candidate[axis]["evidence_state"]
            for candidate in self.fixture["candidates"]
            for axis in ("opportunity", "confidence", "risk")
        }
        eligibility_states = {
            candidate["eligibility"]["state"]
            for candidate in self.fixture["candidates"]
        }
        self.assertEqual(evidence_states, {state.value for state in EvidenceState})
        self.assertEqual(eligibility_states, {state.value for state in EligibilityState})
        self.assertTrue(any("metadata" in row for row in self.fixture["candidates"]))

    def test_03_success_output_and_no_silent_loss_accounting(self) -> None:
        result = self.engine.run(self.fixture)
        self.assertEqual(result["guard_state"], "PASS")
        self.assertEqual(
            result["accounting"],
            {
                "input_rows": 6,
                "terminal_trace_rows": 6,
                "ranked_rows": 5,
                "unranked_rows": 1,
                "selected_rows": 2,
                "skipped_rows": 3,
                "input_terminal_identity_match": True,
            },
        )
        self.assertEqual(
            {row["candidate_id"] for row in self.fixture["candidates"]},
            {row["candidate_id"] for row in result["candidate_traces"]},
        )
        selected = {row["candidate_id"] for row in result["selected_set"]}
        self.assertTrue(
            all(
                row["candidate_id"] in selected or row["reason_codes"]
                for row in result["candidate_traces"]
            )
        )

    def test_04_raw_rank_exact_decimal_tie_and_total_key(self) -> None:
        result = self.engine.run(self.fixture)
        self.assertEqual(
            [row["candidate_id"] for row in result["raw_ranking"]],
            [
                "candidate-alpha",
                "candidate-bravo",
                "candidate-charlie",
                "candidate-delta",
                "candidate-echo",
            ],
        )
        bravo, charlie = result["raw_ranking"][1:3]
        self.assertEqual(bravo["raw_score"], "9")
        self.assertEqual(bravo["tie_group"], charlie["tie_group"])
        self.assertLess(bravo["tie_break_key"][1], charlie["tie_break_key"][1])
        self.assertEqual([row["raw_rank"] for row in result["raw_ranking"]], list(range(1, 6)))

    def test_05_set_log_reconstructs_skip_substitution_and_unfilled(self) -> None:
        result = self.engine.run(self.fixture)
        self.assertEqual(
            selected_identity(result),
            [("candidate-bravo", 1, 2), ("candidate-echo", 2, 5)],
        )
        actions = [row["action"] for row in result["set_decision_log"]]
        self.assertEqual(
            actions,
            ["SKIPPED", "SUBSTITUTED", "SKIPPED", "SKIPPED", "SUBSTITUTED", "UNFILLED"],
        )
        alpha_skip = result["set_decision_log"][0]
        bravo_substitution = result["set_decision_log"][1]
        self.assertEqual(alpha_skip["replacement_candidate_id"], "candidate-bravo")
        self.assertEqual(
            bravo_substitution["substitutes_for_candidate_ids"], ["candidate-alpha"]
        )
        self.assertEqual(result["set_decision_log"][-1]["slot"], 3)
        self.assertEqual(result["set_decision_log"][-1]["candidate_id"], None)

    def test_06_result_digest_and_deterministic_repetition_three_of_three(self) -> None:
        results = [self.engine.run(copy.deepcopy(self.fixture)) for _ in range(3)]
        byte_results = [canonical_json_bytes(result) for result in results]
        self.assertEqual(byte_results[0], byte_results[1])
        self.assertEqual(byte_results[1], byte_results[2])
        self.assertEqual(len({result["result_digest"] for result in results}), 1)
        without_digest = dict(results[0])
        digest = without_digest.pop("result_digest")
        self.assertEqual(digest, sha256_hex(without_digest))

    def test_07_all_candidate_permutations_are_byte_invariant(self) -> None:
        baseline = canonical_json_bytes(self.engine.run(self.fixture))
        candidates = self.fixture["candidates"]
        for permutation in itertools.permutations(candidates):
            permuted = copy.deepcopy(self.fixture)
            permuted["candidates"] = list(permutation)
            self.assertEqual(canonical_json_bytes(self.engine.run(permuted)), baseline)

    def test_08_confidence_mutation_changes_set_not_raw_rank(self) -> None:
        baseline = self.engine.run(self.fixture)
        mutated = copy.deepcopy(self.fixture)
        bravo = mutated["candidates"][1]
        bravo["confidence"].update(
            {
                "evidence_state": "CONFLICT",
                "value": None,
                "evidence_refs": ["synthetic-confidence-a", "synthetic-confidence-b"],
                "reason_codes": ["SYNTHETIC_CONFIDENCE_CONFLICT"],
            }
        )
        changed = self.engine.run(mutated)
        self.assertEqual(raw_identity(changed), raw_identity(baseline))
        self.assertNotEqual(selected_identity(changed), selected_identity(baseline))

    def test_09_risk_mutation_changes_set_not_raw_rank(self) -> None:
        baseline = self.engine.run(self.fixture)
        mutated = copy.deepcopy(self.fixture)
        bravo = mutated["candidates"][1]
        bravo["risk"].update(
            {
                "evidence_state": "STALE",
                "value": "0.2",
                "reason_codes": ["SYNTHETIC_RISK_BECAME_STALE"],
            }
        )
        changed = self.engine.run(mutated)
        self.assertEqual(raw_identity(changed), raw_identity(baseline))
        self.assertNotEqual(selected_identity(changed), selected_identity(baseline))

    def test_10_eligibility_mutation_changes_set_not_raw_rank(self) -> None:
        baseline = self.engine.run(self.fixture)
        mutated = copy.deepcopy(self.fixture)
        mutated["candidates"][0]["eligibility"] = {
            "state": "TRUE",
            "reason_codes": [],
        }
        changed = self.engine.run(mutated)
        self.assertEqual(raw_identity(changed), raw_identity(baseline))
        self.assertNotEqual(selected_identity(changed), selected_identity(baseline))

    def test_11_irrelevant_metadata_cannot_change_rank_set_config_or_run_id(self) -> None:
        baseline = self.engine.run(self.fixture)
        mutated = copy.deepcopy(self.fixture)
        mutated["candidates"][1]["metadata"]["new_irrelevant"] = {
            "list": [3, 2, 1],
            "flag": True,
        }
        changed = self.engine.run(mutated)
        self.assertEqual(raw_identity(changed), raw_identity(baseline))
        self.assertEqual(selected_identity(changed), selected_identity(baseline))
        self.assertEqual(changed["config_digest"], baseline["config_digest"])
        self.assertEqual(changed["workbench_run_id"], baseline["workbench_run_id"])
        self.assertNotEqual(changed["input_digest"], baseline["input_digest"])
        self.assertNotEqual(changed["result_digest"], baseline["result_digest"])

    def test_12_all_evidence_states_and_null_values_survive_terminal_trace(self) -> None:
        result = self.engine.run(self.fixture)
        actual = {
            trace[axis]["evidence_state"]
            for trace in result["candidate_traces"]
            for axis in ("opportunity", "confidence", "risk")
        }
        self.assertEqual(actual, {state.value for state in EvidenceState})
        foxtrot = traces_by_id(result)["candidate-foxtrot"]
        self.assertEqual(foxtrot["opportunity"]["evidence_state"], "UNKNOWN")
        self.assertIsNone(foxtrot["opportunity"]["value"])
        self.assertEqual(foxtrot["confidence"]["evidence_state"], "NOT_FOUND")
        self.assertIsNone(foxtrot["confidence"]["value"])
        self.assertEqual(foxtrot["risk"]["evidence_state"], "CONFLICT")
        self.assertIsNone(foxtrot["risk"]["value"])

    def test_13_not_found_null_zero_and_false_remain_distinct(self) -> None:
        mutated = copy.deepcopy(self.fixture)
        foxtrot = mutated["candidates"][-1]
        foxtrot["opportunity"] = {
            "evidence_state": "VERIFIED",
            "value": "0",
            "publication_at": "2026-01-30T14:00:00+09:00",
            "evidence_refs": ["synthetic-zero-opportunity"],
        }
        foxtrot["eligibility"] = {
            "state": "FALSE",
            "reason_codes": ["SYNTHETIC_FALSE_ELIGIBILITY"],
        }
        result = self.engine.run(mutated)
        trace = traces_by_id(result)["candidate-foxtrot"]
        self.assertEqual(trace["opportunity"]["value"], "0")
        self.assertEqual(trace["opportunity"]["evidence_state"], "VERIFIED")
        self.assertIsNone(trace["confidence"]["value"])
        self.assertEqual(trace["confidence"]["evidence_state"], "NOT_FOUND")
        self.assertEqual(trace["eligibility"]["state"], "FALSE")

    def test_14_unknown_keys_fail_each_positive_shape_surface(self) -> None:
        cases = []
        envelope = copy.deepcopy(self.fixture)
        envelope["extra"] = 1
        cases.append(envelope)
        provenance = copy.deepcopy(self.fixture)
        provenance["fixture_provenance"]["extra"] = 1
        cases.append(provenance)
        policy = copy.deepcopy(self.fixture)
        policy["set_policy"]["extra"] = 1
        cases.append(policy)
        candidate = copy.deepcopy(self.fixture)
        candidate["candidates"][0]["extra"] = 1
        cases.append(candidate)
        eligibility = copy.deepcopy(self.fixture)
        eligibility["candidates"][0]["eligibility"]["extra"] = 1
        cases.append(eligibility)
        axis = copy.deepcopy(self.fixture)
        axis["candidates"][0]["opportunity"]["extra"] = 1
        cases.append(axis)
        for case in cases:
            with self.subTest(surface=len(case)):
                with self.assertRaises(WorkbenchContractError) as caught:
                    self.engine.run(case)
                self.assertIn("UNKNOWN_KEY", {v.code for v in caught.exception.violations})

    def test_15_missing_keys_wrong_shapes_and_duplicate_identities_fail_closed(self) -> None:
        cases: list[tuple[dict, str]] = []
        missing = copy.deepcopy(self.fixture)
        del missing["candidates"][0]["risk"]
        cases.append((missing, "MISSING_REQUIRED_KEY"))
        wrong_shape = copy.deepcopy(self.fixture)
        wrong_shape["candidates"][0]["opportunity"] = []
        cases.append((wrong_shape, "EXPECTED_MAPPING"))
        duplicate_candidate = copy.deepcopy(self.fixture)
        duplicate_candidate["candidates"][1]["candidate_id"] = "candidate-alpha"
        cases.append((duplicate_candidate, "DUPLICATE_CANDIDATE_ID"))
        duplicate_pit = copy.deepcopy(self.fixture)
        duplicate_pit["candidates"][1]["pit_snapshot_id"] = "synthetic-pit-alpha"
        cases.append((duplicate_pit, "DUPLICATE_PIT_SNAPSHOT_ID"))
        for case, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(WorkbenchContractError) as caught:
                    self.engine.run(case)
                self.assertIn(code, {v.code for v in caught.exception.violations})

    def test_16_noncanonical_and_binary_float_axis_values_fail(self) -> None:
        invalid_values = [1.25, "1.0", "01", "+1", "1e2", "NaN", "Infinity", "-0"]
        for invalid in invalid_values:
            mutated = copy.deepcopy(self.fixture)
            mutated["candidates"][0]["opportunity"]["value"] = invalid
            with self.subTest(value=invalid):
                with self.assertRaises(WorkbenchContractError) as caught:
                    self.engine.run(mutated)
                self.assertIn(
                    "NONCANONICAL_DECIMAL",
                    {violation.code for violation in caught.exception.violations},
                )

    def test_17_evidence_state_value_matrix_fails_invalid_combinations(self) -> None:
        invalid = [
            ("VERIFIED", None, "VERIFIED_VALUE_REQUIRED"),
            ("UNKNOWN", "1", "STATE_REQUIRES_NULL_VALUE"),
            ("NOT_FOUND", "1", "STATE_REQUIRES_NULL_VALUE"),
            ("CONFLICT", "1", "STATE_REQUIRES_NULL_VALUE"),
        ]
        for state, value, code in invalid:
            mutated = copy.deepcopy(self.fixture)
            mutated["candidates"][0]["opportunity"]["evidence_state"] = state
            mutated["candidates"][0]["opportunity"]["value"] = value
            with self.subTest(state=state):
                with self.assertRaises(WorkbenchContractError) as caught:
                    self.engine.run(mutated)
                self.assertIn(code, {v.code for v in caught.exception.violations})

    def test_18_every_local_denylist_field_fails_at_top_map_and_nested_list(self) -> None:
        for forbidden in sorted(LOCAL_FORBIDDEN_OUTCOME_FIELDS):
            variants = []
            top = copy.deepcopy(self.fixture)
            top[forbidden] = "prohibited"
            variants.append(top)
            nested_map = copy.deepcopy(self.fixture)
            nested_map["candidates"][1]["metadata"][forbidden] = "prohibited"
            variants.append(nested_map)
            nested_list = copy.deepcopy(self.fixture)
            nested_list["candidates"][1]["metadata"]["nested"]["items"] = [
                {forbidden: "prohibited"}
            ]
            variants.append(nested_list)
            for variant in variants:
                with self.subTest(field=forbidden):
                    with self.assertRaises(WorkbenchContractError) as caught:
                        self.engine.run(variant)
                    self.assertIn(
                        "OUTCOME_FIELD_FORBIDDEN",
                        {violation.code for violation in caught.exception.violations},
                    )

    def test_19_existing_pit_guard_forbidden_field_is_reused(self) -> None:
        mutated = copy.deepcopy(self.fixture)
        mutated["candidates"][1]["metadata"]["future_close"] = 1
        with self.assertRaises(WorkbenchContractError) as caught:
            self.engine.run(mutated)
        self.assertIn(
            "PIT_GUARD_FUTURE_FIELD_IN_MODEL_INPUT",
            {violation.code for violation in caught.exception.violations},
        )

    def test_20_pit_cutoff_and_timezone_awareness_fail_before_stages(self) -> None:
        after_cutoff = copy.deepcopy(self.fixture)
        after_cutoff["candidates"][0]["opportunity"]["publication_at"] = (
            "2026-02-01T00:00:00+09:00"
        )
        with self.assertRaises(WorkbenchContractError) as caught:
            self.engine.run(after_cutoff)
        self.assertTrue(
            {"PIT_PUBLICATION_AFTER_CUTOFF", "PIT_GUARD_PIT_PUBLICATION_AFTER_CUTOFF"}
            & {violation.code for violation in caught.exception.violations}
        )

        naive = copy.deepcopy(self.fixture)
        naive["candidates"][0]["opportunity"]["publication_at"] = "2026-01-30T09:00:00"
        with self.assertRaises(WorkbenchContractError) as caught_naive:
            self.engine.run(naive)
        self.assertIn(
            "INVALID_TIMEZONE_AWARE_DATETIME",
            {violation.code for violation in caught_naive.exception.violations},
        )

    def test_21_guard_failure_occurs_before_recall(self) -> None:
        class SpyRecall:
            def __init__(self) -> None:
                self.calls = 0

            def recall(self, candidates):
                self.calls += 1
                return ()

        spy = SpyRecall()
        engine = ForwardModelWorkbench(recall=spy)
        mutated = copy.deepcopy(self.fixture)
        mutated["candidates"][1]["metadata"]["target_label"] = "prohibited"
        with self.assertRaises(WorkbenchContractError):
            engine.run(mutated)
        self.assertEqual(spy.calls, 0)

    def test_22_declared_set_policy_is_exact_and_fail_closed(self) -> None:
        mutations = [
            ("eligibility_required", "UNKNOWN"),
            ("allowed_confidence_states", ["VERIFIED", "PARTIAL"]),
            ("allowed_risk_states", []),
            ("opportunity_state_required_for_raw_rank", "PARTIAL"),
            ("set_size", 0),
            ("set_size", True),
        ]
        for key, value in mutations:
            mutated = copy.deepcopy(self.fixture)
            mutated["set_policy"][key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(WorkbenchContractError):
                    self.engine.run(mutated)

    def test_23_declared_set_lists_are_normalized_and_duplicates_rejected(self) -> None:
        reversed_refs = copy.deepcopy(self.fixture)
        reversed_refs["candidates"][-1]["risk"]["evidence_refs"].reverse()
        self.assertEqual(
            canonical_json_bytes(self.engine.run(reversed_refs)),
            canonical_json_bytes(self.engine.run(self.fixture)),
        )
        duplicate = copy.deepcopy(self.fixture)
        duplicate["candidates"][-1]["risk"]["evidence_refs"] = ["same", "same"]
        with self.assertRaises(WorkbenchContractError) as caught:
            self.engine.run(duplicate)
        self.assertIn(
            "DUPLICATE_LIST_ITEM", {violation.code for violation in caught.exception.violations}
        )

    def test_24_contract_violations_are_sorted_deterministically(self) -> None:
        mutated = copy.deepcopy(self.fixture)
        mutated["z_unknown"] = 1
        mutated["a_unknown"] = 1
        mutated["candidates"][0]["opportunity"]["value"] = "1.0"
        with self.assertRaises(WorkbenchContractError) as first:
            self.engine.run(mutated)
        with self.assertRaises(WorkbenchContractError) as second:
            self.engine.run(copy.deepcopy(mutated))
        first_values = [v.as_dict() for v in first.exception.violations]
        second_values = [v.as_dict() for v in second.exception.violations]
        self.assertEqual(first_values, second_values)
        sort_keys = [violation.sort_key() for violation in first.exception.violations]
        self.assertEqual(sort_keys, sorted(sort_keys))

    def test_25_terminal_trace_exposes_five_separate_surfaces(self) -> None:
        result = run_workbench(self.fixture)
        for trace in result["candidate_traces"]:
            self.assertTrue(
                {"opportunity", "confidence", "risk", "eligibility", "set_policy"}
                <= set(trace)
            )
            self.assertIn(
                trace["recall_disposition"], {"RECALLED_IDENTITY_PRESERVED"}
            )
            self.assertIn(trace["rankability_disposition"], {"RANKED", "UNRANKED"})
            self.assertIn(
                trace["set_disposition"],
                {"SELECTED", "SKIPPED", "NOT_SCANNED_CAPACITY_REACHED", "UNRANKED"},
            )

    def test_26_security_code_leading_zeroes_are_preserved(self) -> None:
        result = self.engine.run(self.fixture)
        self.assertEqual(
            [trace["security_code"] for trace in result["candidate_traces"]],
            ["000001", "000002", "000003", "000004", "000005", "000006"],
        )

    def test_27_public_ranker_owns_verified_rule_and_rejects_old_policy_arg(self) -> None:
        parsed = validate_and_parse_envelope(self.fixture)
        recalled = IdentityCandidateRecall().recall(parsed.candidates)
        ranker = OpportunityTailRanker()

        ranked, reasons = ranker.rank(recalled)

        self.assertEqual(len(ranked), 5)
        self.assertEqual([item.raw_rank for item in ranked], [1, 2, 3, 4, 5])
        self.assertEqual(
            reasons["candidate-foxtrot"],
            ("OPPORTUNITY_STATE_UNKNOWN_NOT_VERIFIED",),
        )
        with self.assertRaises(TypeError):
            ranker.rank(recalled, parsed.set_policy)  # type: ignore[call-arg]

        baseline = self.engine.run(self.fixture)
        policy_mutations = {
            "policy_id": "M3TOP3-SYNTHETIC-SET-v0.1-ALTERNATE-ID",
            "set_size": 1,
        }
        for key, value in policy_mutations.items():
            with self.subTest(policy_field=key):
                mutated = copy.deepcopy(self.fixture)
                mutated["set_policy"][key] = value
                self.assertEqual(
                    self.engine.run(mutated)["raw_ranking"],
                    baseline["raw_ranking"],
                )

    def test_28_malicious_set_stage_outputs_fail_closed_before_projection(self) -> None:
        def selected_rank_only(selected, _decisions, _dispositions) -> None:
            selected[0]["raw_rank"] = 999

        def selected_and_log_rank(selected, decisions, _dispositions) -> None:
            candidate_id = selected[0]["candidate_id"]
            selected[0]["raw_rank"] = 999
            next(
                row for row in decisions if row["candidate_id"] == candidate_id
            )["raw_rank"] = 999

        def duplicate_selection(selected, _decisions, _dispositions) -> None:
            duplicate = copy.deepcopy(selected[0])
            duplicate["set_position"] = len(selected) + 1
            selected.append(duplicate)

        def contradictory_slot(_selected, decisions, _dispositions) -> None:
            next(
                row
                for row in decisions
                if row["action"] in {"SELECTED", "SUBSTITUTED"}
            )["slot"] = 2

        def contradictory_disposition(_selected, _decisions, dispositions) -> None:
            dispositions["candidate-bravo"]["set_disposition"] = "SKIPPED"

        def mutated_identity(selected, _decisions, _dispositions) -> None:
            selected[0]["company_id"] = "synthetic-company-mutated"

        def unranked_identity(selected, _decisions, _dispositions) -> None:
            selected[0]["candidate_id"] = "candidate-foxtrot"

        def missing_disposition(_selected, _decisions, dispositions) -> None:
            del dispositions["candidate-delta"]

        def unhashable_action(_selected, decisions, _dispositions) -> None:
            decisions[0]["action"] = []

        cases = {
            "selected_raw_rank_999": selected_rank_only,
            "selected_and_log_raw_rank_999": selected_and_log_rank,
            "duplicate_selection": duplicate_selection,
            "decision_slot_contradiction": contradictory_slot,
            "disposition_contradiction": contradictory_disposition,
            "identity_mutation": mutated_identity,
            "unranked_identity": unranked_identity,
            "missing_disposition": missing_disposition,
            "unhashable_invalid_action": unhashable_action,
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                engine = ForwardModelWorkbench(
                    set_constructor=TamperingSetConstructor(mutate)
                )
                with self.assertRaises(WorkbenchInvariantError):
                    engine.run(copy.deepcopy(self.fixture))

        def add_harmless_diagnostics(selected, decisions, dispositions) -> None:
            selected[0]["delegate_diagnostic"] = {"state": "observed"}
            decisions[0]["delegate_diagnostic"] = ["observed"]
            dispositions["candidate-alpha"]["delegate_diagnostic"] = True

        diagnostic_result = ForwardModelWorkbench(
            set_constructor=TamperingSetConstructor(add_harmless_diagnostics)
        ).run(copy.deepcopy(self.fixture))
        self.assertEqual(
            selected_identity(diagnostic_result),
            selected_identity(self.engine.run(self.fixture)),
        )
        self.assertEqual(
            diagnostic_result["selected_set"][0]["delegate_diagnostic"],
            {"state": "observed"},
        )

    def test_29_canonical_pit_guard_cannot_be_replaced_by_noop_extension(self) -> None:
        def contains_only_plain_containers(value) -> bool:
            if isinstance(value, dict):
                return type(value) is dict and all(
                    contains_only_plain_containers(item) for item in value.values()
                )
            if isinstance(value, list):
                return type(value) is list and all(
                    contains_only_plain_containers(item) for item in value
                )
            return True

        class NoOpGuard:
            def __init__(self) -> None:
                self.calls = 0
                self.saw_only_plain_containers = True

            def assert_model_inputs(self, records, _cutoff_at) -> None:
                self.calls += 1
                self.saw_only_plain_containers &= contains_only_plain_containers(
                    records
                )

        extension = NoOpGuard()
        mutated = copy.deepcopy(self.fixture)
        mutated["candidates"][1]["metadata"]["future_close"] = 1
        with self.assertRaises(WorkbenchContractError) as caught:
            ForwardModelWorkbench(pit_guard=extension).run(mutated)
        self.assertIn(
            "PIT_GUARD_FUTURE_FIELD_IN_MODEL_INPUT",
            {violation.code for violation in caught.exception.violations},
        )
        self.assertEqual(extension.calls, len(self.fixture["candidates"]))
        self.assertTrue(extension.saw_only_plain_containers)

    def test_30_mapping_implementations_are_deep_normalized_for_pit_guard(self) -> None:
        forbidden_containers = [
            UserDict({"future_close": 1}),
            MappingProxyType({"future_close": 1}),
        ]
        for wrapped in forbidden_containers:
            with self.subTest(forbidden_type=type(wrapped).__name__):
                mutated = copy.deepcopy(self.fixture)
                mutated["candidates"][1]["metadata"]["wrapped_mapping"] = wrapped
                with self.assertRaises(WorkbenchContractError) as caught:
                    self.engine.run(mutated)
                self.assertIn(
                    "PIT_GUARD_FUTURE_FIELD_IN_MODEL_INPUT",
                    {violation.code for violation in caught.exception.violations},
                )

        safe_mappings = [
            UserDict({"safe_value": [1, {"label": "ok"}]}),
            MappingProxyType({"safe_value": [1, {"label": "ok"}]}),
        ]
        for wrapped in safe_mappings:
            with self.subTest(safe_type=type(wrapped).__name__):
                wrapped_fixture = copy.deepcopy(self.fixture)
                wrapped_fixture["candidates"][1]["metadata"][
                    "wrapped_mapping"
                ] = wrapped
                plain_fixture = copy.deepcopy(self.fixture)
                plain_fixture["candidates"][1]["metadata"]["wrapped_mapping"] = {
                    "safe_value": [1, {"label": "ok"}]
                }
                self.assertEqual(
                    canonical_json_bytes(self.engine.run(wrapped_fixture)),
                    canonical_json_bytes(self.engine.run(plain_fixture)),
                )

    def test_31_decimal_context_cannot_change_order_ties_or_digest(self) -> None:
        mutated = copy.deepcopy(self.fixture)
        values = {
            "candidate-alpha": "10000000000000000000000000001",
            "candidate-bravo": "10000000000000000000000000002",
            "candidate-charlie": "10000000000000000000000000002",
            "candidate-delta": "-1",
            "candidate-echo": "0",
        }
        for candidate in mutated["candidates"]:
            if candidate["candidate_id"] in values:
                candidate["opportunity"]["value"] = values[candidate["candidate_id"]]

        with localcontext() as context:
            context.prec = 28
            precision_28 = self.engine.run(copy.deepcopy(mutated))
        with localcontext() as context:
            context.prec = 60
            precision_60 = self.engine.run(copy.deepcopy(mutated))

        self.assertEqual(
            canonical_json_bytes(precision_28), canonical_json_bytes(precision_60)
        )
        self.assertEqual(precision_28["result_digest"], precision_60["result_digest"])
        self.assertEqual(
            [row["candidate_id"] for row in precision_28["raw_ranking"]],
            [
                "candidate-bravo",
                "candidate-charlie",
                "candidate-alpha",
                "candidate-echo",
                "candidate-delta",
            ],
        )
        by_id = {row["candidate_id"]: row for row in precision_28["raw_ranking"]}
        self.assertEqual(
            by_id["candidate-bravo"]["tie_break_key"][0],
            "-10000000000000000000000000002",
        )
        self.assertEqual(
            by_id["candidate-bravo"]["tie_group"],
            by_id["candidate-charlie"]["tie_group"],
        )
        self.assertEqual(by_id["candidate-echo"]["tie_break_key"][0], "0")
        self.assertEqual(by_id["candidate-delta"]["tie_break_key"][0], "1")


if __name__ == "__main__":
    unittest.main()
