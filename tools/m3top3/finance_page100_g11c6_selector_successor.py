#!/usr/bin/env python3
"""Fail-closed core and focused PRECHECK for the Finance Page100 G11C6 successor.

This file intentionally contains no provider client, quota writer, or S3 writer.
It provides the deterministic selector/projection core, strict governance-bundle
validation, and a focused three-session STS-probe PRECHECK CLI.  ``--mode live`` imports and invokes
only the separately reviewed, exact-hash-bound custody adapter after a fresh LIVE
activation and focused PRECHECK PASS receipt have both been verified.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


GENERATION_TIMESTAMP = "20260901155700"
GENERATION_ID = f"FINANCE-PAGE100-G11C6-{GENERATION_TIMESTAMP}"
RUNTIME_LOCK_ID = f"PMO-FINANCE-PAGE100-G11C6-{GENERATION_TIMESTAMP}"
PILOT_RUN_ID = f"FINANCE-PAGE100-PILOT-G11C6-{GENERATION_TIMESTAMP}"
PREPARATION_ID = f"FINANCE-PAGE100-G11C6-PREPARATION-{GENERATION_TIMESTAMP}"
PRECHECK_ACT_ID = f"FINANCE-PAGE100-PRECHECK-ACT-G11C6-{GENERATION_TIMESTAMP}"
LIVE_ACT_ID = f"FINANCE-PAGE100-LIVE-ACT-G11C6-{GENERATION_TIMESTAMP}"
LATCH_EVENT_ID = f"FINANCE-PAGE100-LATCH-G11C6-{GENERATION_TIMESTAMP}"
OWNER_APPROVAL_COMMIT = "884e1fadebda480f4c38d172eab083cbdbf031b2"
AUTHORITY_COMMIT = "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
GOVERNED_CORRECTION_HEAD = AUTHORITY_COMMIT
GOVERNED_CORRECTION_TREE = "572bf2ab23a7d761de8160e6828f8b074618391b"
ACTIVATION_BASE_HEAD_COMMIT = "d0061e9005a74817563588990064af4260ab2bd9"
ACTIVATION_BASE_TREE = "7ba82af78770b8fdcfb914ab080bd280f017918f"
OWNER_DECISION_V1_1_GIT_BLOB = "1a20b86b784c1c69b407a432e08fb476c60b496d"
OWNER_DECISION_V1_1_SHA256 = (
    "9efa622791a036c870ff4cded87bc4123cfae8089382c90a9ee2e804955ec6dd"
)

SELECTOR_ALGORITHM = "SHA256_OF_UTF8_ISSUCMPY_KSD_CUSTNO"
TARGET_CUSTODY_SHA256 = (
    "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
)
SEALED_SEED_PROJECTION_SHA256 = (
    "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
)
PREDECESSOR_CHECKPOINT_SHA256 = (
    "42a76559083f18e2482f89de59af4d6dd842c07595089e9eea5f1716369e4f39"
)

PRIMARY_DATES = (
    "20240102", "20240131", "20240329", "20240628", "20240808",
    "20240809", "20240812", "20240930", "20241231", "20250115",
    "20250331", "20250630", "20251231", "20260115", "20260331",
    "20260630", "20260814",
)
PRIMARY_DATES_SHA256 = "920b118d7d7abaa10f69e93169698ed380db7162ac3c5024756a07702a7065f6"
OWNER_CAP_SPEC_SHA256 = "073bb0e5f31f7fb6dea105412dc0b0e5097980653c8947fb6113486622c19d36"
EXECUTION_TOKEN_SHA256 = "93d58b33cb86a41142174f3a22a2cd27948f9283fa77c1a04037cdff6f8bd13b"
PREDECESSOR_FAILURE_RECEIPT_GIT_BLOB = "00bd90fa57062e438bcddfdcc36be9a5694ef3d9"
PREDECESSOR_FAILURE_RECEIPT_SHA256 = (
    "0577dbbacefa40e60e402dcfb37dd0a85c621952ac29314b56a8481d5e2087d6"
)
PREDECESSOR_FAILURE_PAYLOAD_SHA256 = (
    "bb9d490db07755ddb1da399c4a454abf08679abaeeaae99db5ff58895dec18df"
)
PREDECESSOR_G11C1_PREPARATION_COMMIT = "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09"
PREDECESSOR_G11C1_PREPARATION_TREE = "f35d2bdd68138d527bc8603472311c0ca032988e"
PREDECESSOR_G11C1_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C1_PREPARATION_AUDIT_TERMINAL_RECEIPT_"
    "20260901130250_v1.0.json"
)
PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256 = (
    "737a2dbd844e2fccf4e53fae88ba34cb68a994138a666dbf221e64fd8acd03c1"
)
PREDECESSOR_G11C1_TERMINAL_RECEIPT_GIT_BLOB = (
    "8dbde6505e5cb0b130cd96e8495cd7f2d63703f7"
)
PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "a41f3fa41413ed89a30a84867624b3ea52de5813903da033dd48ac023fdc15df"
)
PREDECESSOR_G11C1_TERMINAL_RECEIPT_BYTES = 11695
PREDECESSOR_G11C1_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C1-20260901123521",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C1-20260901123521",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C1-20260901123521",),
    "consumed_precheck_act_ids": ("FINANCE-PAGE100-PRECHECK-ACT-G11C1-20260901123521",),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C1-20260901123521",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C1-20260901123521",),
}
PREDECESSOR_G11C2_PREPARATION_COMMIT = "203a11baf838955b69a5cc4b7509aff38dbf271b"
PREDECESSOR_G11C2_PREPARATION_TREE = "c5cc0148f3887eeb360761b0105b85a8fbc96cf2"
PREDECESSOR_G11C2_PRECHECK_ACTIVATION_COMMIT = (
    "117e701f0bd3ce25d40132169ac5267d306c24c2"
)
PREDECESSOR_G11C2_PRECHECK_ACTIVATION_TREE = (
    "e0f6faa56fa485f075cdc974af787352c184870a"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C2_ELIGIBLE_SUCCESSOR_"
    "PRECHECK_TERMINAL_RECEIPT_33469887723_v1.0.json"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "72e2465b1d09853c7baf5b4710c44778c63a3851"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_APPEND_TREE = (
    "0c75cca28985afc555a03d541b5409d22ea74eae"
)
PREDECESSOR_G11C2_PRECHECK_EXECUTION_HEAD_SHA = (
    "117e701f0bd3ce25d40132169ac5267d306c24c2"
)
PREDECESSOR_G11C2_PRECHECK_EXECUTION_HEAD_TREE_SHA = (
    "e0f6faa56fa485f075cdc974af787352c184870a"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_SHA256 = (
    "633cbf782a54076f3a8ba30854383c232724afeed1f8da02f637d489b5d08cb8"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_GIT_BLOB = (
    "f6f2bae314852dbb55d82305d0376a1a543d44b1"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "a476879a9b75ea05c23c241dbd6a5b72a0ed99dbd41ab35c746e25ad0115ea85"
)
PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_BYTES = 30932
PREDECESSOR_G11C2_PRECHECK_RUN_ID = 33469887723
PREDECESSOR_G11C2_PRECHECK_JOB_ID = 99737317645
PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT = 1
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_COMMIT = (
    "5f400498c0890d756b3d5cbe6ede7ec6d2292450"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_TREE = (
    "b5e5eb8c2d08feaa99e83185ee1ef0eaf8e90004"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C2_PRE_LIVE_FROZEN_CONTRACT_AUDIT_"
    "TERMINAL_RECEIPT_20260901130250_v1.0.json"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_SHA256 = (
    "b7e03464f1f2c53a7446901b88ccb2aa481f940c272970f24cccbb5be1523df6"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_GIT_BLOB = (
    "46dc2cf1c7f422786f4365b94782cb8982a6bdb2"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256 = (
    "d94c512c53a2b83c4d8aae0fc54b0558d9d79f00ca699b684189d9831c5f990a"
)
PREDECESSOR_G11C2_INVALIDATION_RECEIPT_BYTES = 16182
PREDECESSOR_G11C2_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C2-20260901130250",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C2-20260901130250",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C2-20260901130250",),
    "consumed_precheck_act_ids": (
        "FINANCE-PAGE100-PRECHECK-ACT-G11C2-20260901130250",
    ),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C2-20260901130250",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C2-20260901130250",),
}
PREDECESSOR_G11C3_PRECHECK_RUN_ID = 33472741288
PREDECESSOR_G11C3_LIVE_RUN_ID = 33473465774
PREDECESSOR_G11C3_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C3-20260901134119",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C3-20260901134119",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C3-20260901134119",),
    "consumed_precheck_act_ids": (
        "FINANCE-PAGE100-PRECHECK-ACT-G11C3-20260901134119",
    ),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C3-20260901134119",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C3-20260901134119",),
}
PREDECESSOR_G11C3_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "8b6cfcb03904e58c5ffabb3ff3c10cb5d6850444"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_APPEND_TREE = (
    "27af43d2d49476ce552e5c59010bac93c890c194"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C3_ELIGIBLE_SUCCESSOR_"
    "LIVE_TERMINAL_RECEIPT_33473465774_v1.0.json"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_SHA256 = (
    "846a915b72f428db2155d316eb075aafa05840b5a277e3e9f2c4a54092dc6c3f"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_GIT_BLOB = (
    "9ccc1ac5a381dea3a9ba18fdabb357330fc35a42"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "ee49c0b5fe739dd9830250e84659780fbefc7e902021200b7ce0c2b334c5630c"
)
PREDECESSOR_G11C3_TERMINAL_RECEIPT_BYTES = 10375
PREDECESSOR_G11C4_PRECHECK_RUN_ID = 33477019917
PREDECESSOR_G11C4_PRECHECK_JOB_ID = 99758300336
PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT = 1
PREDECESSOR_G11C4_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C4-20260901143300",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C4-20260901143300",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C4-20260901143300",),
    "consumed_preparation_ids": (
        "FINANCE-PAGE100-G11C4-PREPARATION-20260901143300",
    ),
    "consumed_precheck_act_ids": (
        "FINANCE-PAGE100-PRECHECK-ACT-G11C4-20260901143300",
    ),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C4-20260901143300",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C4-20260901143300",),
}
PREDECESSOR_G11C4_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "6e4660cfbb1730dcaeaa2908c9e1a38de012a920"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_APPEND_TREE = (
    "3e4a53a6df8ac7fa4f500c51a951ae9c900476d8"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C4_ELIGIBLE_SUCCESSOR_"
    "PRECHECK_TERMINAL_RECEIPT_33477019917_v1.0.json"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_SHA256 = (
    "427fd336552939115a7e4a4ada49dedf74b0dbc5340bc691d1e9c457fcb301ab"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_GIT_BLOB = (
    "7839bde0f67cea9762dd30d2c063add07b36aca9"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "88d6816dbb9ca4f2f1ae91aa82c32bcbcdd5ed119420ff2aa5819a7cb3d847eb"
)
PREDECESSOR_G11C4_TERMINAL_RECEIPT_BYTES = 25645
PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_SHA = (
    "4015867bedf55784584f901bc3afb5e0ca62dc95"
)
PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_TREE_SHA = (
    "9df8503c01a90ed45d76346f43507cd20fee9365"
)
PREDECESSOR_G11C5_PRECHECK_RUN_ID = 33479444941
PREDECESSOR_G11C5_PRECHECK_JOB_ID = 99765558713
PREDECESSOR_G11C5_PRECHECK_RUN_ATTEMPT = 1
PREDECESSOR_G11C5_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C5-20260901152200",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C5-20260901152200",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C5-20260901152200",),
    "consumed_preparation_ids": (
        "FINANCE-PAGE100-G11C5-PREPARATION-20260901152200",
    ),
    "consumed_precheck_act_ids": (
        "FINANCE-PAGE100-PRECHECK-ACT-G11C5-20260901152200",
    ),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C5-20260901152200",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C5-20260901152200",),
}
PREDECESSOR_G11C5_PREPARATION_COMMIT = (
    "b73db818d27c80e4ef1b4c5c7b0506691be33920"
)
PREDECESSOR_G11C5_PREPARATION_TREE = (
    "ffab50ec73ab0f29674d82f2d72110a8923a766f"
)
PREDECESSOR_G11C5_PRECHECK_ACTIVATION_COMMIT = (
    "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
)
PREDECESSOR_G11C5_PRECHECK_ACTIVATION_TREE = (
    "53d13cccc42aae8f4b21adebee3ed71190ba1954"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "d0061e9005a74817563588990064af4260ab2bd9"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_TREE = (
    "7ba82af78770b8fdcfb914ab080bd280f017918f"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C5_ELIGIBLE_SUCCESSOR_"
    "PRECHECK_TERMINAL_RECEIPT_33479444941_v1.0.json"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256 = (
    "c518d4ac79b6e7735eae9fe3a799ae7ea29dd4c357508ddd4c85e2d09711b30e"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_GIT_BLOB = (
    "a3d29884a44ca4dac88b9d47bf2447fe24aa0b08"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "332d15f75b2f7843046f0eb5d8983fdb3791cef3fa6155803828e1d74008049f"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_BYTES = 50220
PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_SHA = (
    "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
)
PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_TREE_SHA = (
    "53d13cccc42aae8f4b21adebee3ed71190ba1954"
)
PREDECESSOR_G11C5_TERMINAL_STATE = (
    "TERMINAL_FAIL_CLOSED_G11C5_PRECHECK_EXECUTION_PASS_RECEIPT_SCHEMA_"
    "GENERATOR_NO_RERUN_CONTRACT_MISMATCH_C4_RUN_33477019917_OMITTED_BY_"
    "FROZEN_SCHEMA_LIVE_CLOSED_CURRENT_GENERATION_NO_RERUN"
)
AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = 2048

SEED_BASE_DATE = "20240131"
SEED_SOURCE_ROWS = 40
SEED_ELIGIBLE_ROWS = 35
SEED_EXCLUDED_ROWS = 5
SEED_MISSING_ROWS = 0
SEED_EXCLUDED_GLOBAL_ROW_ORDINALS = (36, 37, 38, 39, 40)
FIRST_NEW_PAGE = 5

EFFECTIVE_ACQUISITION_CEILING = 1700
INHERITED_G10_ACQUISITIONS = 4
G11_ACQUISITION_CEILING = 1696
EFFECTIVE_ATTEMPT_CEILING = 2000
INHERITED_G10_ATTEMPTS = 4
G11_ATTEMPT_CEILING = 1996
ATTEMPTS_PER_PAGE_CEILING = 2

AUTHORITY_FILENAME = (
    "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_AUTHORITY_v1.0.json"
)
PLAN_FILENAME = "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PLAN_v1.0.json"
SEED_FILENAME = (
    "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0.json"
)
MANIFEST_FILENAME = (
    "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_MANIFEST_v1.0.json"
)

AUTHORITY_SCHEMA = "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_AUTHORITY_v1.0"
PLAN_SCHEMA = "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PLAN_v1.0"
SEED_SCHEMA = "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0"
MANIFEST_SCHEMA = "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_MANIFEST_v1.0"

LIVE_ADAPTER_GATE_BLOCKED = "BLOCKED_MISSING_EXECUTABLE_CUSTODY_ADAPTERS"
LIVE_ADAPTER_GATE_READY = "READY"
LIVE_ADAPTER_REPO_PATH = "tools/m3top3/finance_page100_g11c6_live_adapter.py"
LIVE_ADAPTER_INTERFACE_VERSION = "M3TOP3_FINANCE_CA_PAGE100_G11C6_LIVE_ADAPTER_v1.0"
LIVE_ADAPTER_FACTORY_SYMBOL = "create_sealed_g11c6_custody_adapter"
LIVE_ADAPTER_TEST_REPO_PATH = "tools/m3top3/tests/test_finance_page100_g11c6_live_adapter.py"
REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
QUOTA_DAY_KST = "2026-09-01"
LIVE_HEAD_MARKER = "BOUND_BY_GITHUB_EVENT_AFTER"
LIVE_TREE_MARKER = "BOUND_BY_CHECKED_OUT_HEAD_TREE"
EXECUTION_CLAIM_KEY = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_writer_claims/"
    "quota_day_kst=2026-09-01/execution-claim.json"
)
G11_CONTROL_PREFIX = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_control/"
    f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
)
G11_RAW_PREFIX = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
    f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
)
G11_CHECKPOINT_KEY = G11_CONTROL_PREFIX + "checkpoint.json"
G11_TERMINAL_RECEIPT_KEY = G11_CONTROL_PREFIX + "terminal-receipt.json"
EX_CONFIG = 78

SEED_SELECTOR_POLICY = "SEALED_FIVE_OCCURRENCES_EXCLUDE"
FUTURE_SELECTOR_POLICY = "RAW_CUSTODY_THEN_FAIL_CLOSED_PENDING_OWNER_DECISION"
REQUIRED_NO_RERUN_RUNS = (
    33272691259,  # G10 PRECHECK
    33273146915,  # G10 LIVE
    33401871715,  # S2 PRECHECK
    33403101817,  # S2 LIVE
    33414615913,  # S3 PRECHECK
    33414695818,  # S3 APPLY
    33465583987,  # consumed G11 PRECHECK
    33466306591,  # consumed G11 LIVE pre-credential failure
    33469887723,  # consumed G11C2 PRECHECK; G11C2 invalidated before LIVE
    33472741288,  # consumed G11C3 focused PRECHECK
    33473465774,  # consumed G11C3 LIVE; credentials not issued, runner not started
    33477019917,  # consumed G11C4 PRECHECK; first OIDC AssumeRole denied
    33479444941,  # consumed G11C5 PRECHECK; execution PASS, receipt contract failed
)
HISTORICAL_SUCCESSOR_NAMESPACE_MARKERS = (
    "FINANCE-PAGE100-G11-",
    "PMO-FINANCE-PAGE100-G11-",
    "FINANCE-PAGE100-G11C1-",
    "PMO-FINANCE-PAGE100-G11C1-",
    "FINANCE-PAGE100-G11C2-",
    "PMO-FINANCE-PAGE100-G11C2-",
    "FINANCE-PAGE100-G11C3-",
    "PMO-FINANCE-PAGE100-G11C3-",
    "FINANCE-PAGE100-G11C4-",
    "PMO-FINANCE-PAGE100-G11C4-",
    "FINANCE-PAGE100-G11C5-",
    "PMO-FINANCE-PAGE100-G11C5-",
)
LIVE_PRE_MUTATION_PHASES = (
    "RUNTIME_KST_DATE_EQUALITY_GATE",
    "FIVE_EXACT_PREDECESSOR_GET_OBJECT_VERSION_READS",
    "THREE_BOUNDED_LIST_BUCKET_VERSIONS_READS",
    "RUNTIME_KST_DATE_RECHECK",
    "EXECUTION_CLAIM_IF_NONE_MATCH_CREATE",
    "FRESH_CHECKPOINT_QUOTA_PROVIDER",
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")

ZERO_EFFECTS: dict[str, int] = {
    "provider_calls": 0,
    "quota_reservations": 0,
    "aws_calls": 0,
    "s3_calls": 0,
    "repository_writes": 0,
    "remote_custody_mutations": 0,
    "g10_runs": 0,
    "g11_live_runs": 0,
    "normalization_actions": 0,
    "pit_actions": 0,
    "promotion_actions": 0,
    "release_actions": 0,
    "production_actions": 0,
}

STS_POLICY_PROBE_COUNT = 3
OIDC_STS_POLICY_PACKING_PROBES: tuple[dict[str, Any], ...] = (
    {
        "probe_ordinal": 1,
        "role": "CHECKPOINT_READ",
        "policy_role": "checkpoint_read_session_policy",
        "outcome": "SUCCESS",
        "sts_attempts": 1,
        "sts_successes": 1,
        "credentials_issued": 1,
    },
    {
        "probe_ordinal": 2,
        "role": "RAW_READ",
        "policy_role": "raw_four_read_session_policy",
        "outcome": "SUCCESS",
        "sts_attempts": 1,
        "sts_successes": 1,
        "credentials_issued": 1,
    },
    {
        "probe_ordinal": 3,
        "role": "FINAL_LIST_WRITE",
        "policy_role": "final_list_write_session_policy",
        "outcome": "SUCCESS",
        "sts_attempts": 1,
        "sts_successes": 1,
        "credentials_issued": 1,
    },
)
PRECHECK_STS_PROBE_EFFECTS: dict[str, int] = {
    **ZERO_EFFECTS,
    # Each pinned configure-aws-credentials action performs one
    # AssumeRoleWithWebIdentity and one validation GetCallerIdentity call.
    "aws_calls": 6,
    "sts_calls": 6,
    "sts_assume_role_attempts": 3,
    "sts_sessions_assumed": 3,
    "sts_get_caller_identity_calls": 3,
    "credentials_issued": 3,
}

# This is the exact pre-entry output surface consumed by the LIVE workflow.
# Its three configure-aws-credentials sessions already exist before the runner
# starts.  Once adapter execution begins the adapter's observed ledger is
# preserved, including an ambiguity flag on any unreconciled effect.
LIVE_PRE_ENTRY_EFFECTS: dict[str, int | bool] = {
    "primary_acquisitions": 0,
    "network_attempts": 0,
    "provider_calls": 0,
    "quota_reservations": 0,
    "raw_writes": 0,
    "checkpoint_writes": 0,
    "execution_claim_writes": 0,
    "terminal_receipt_writes": 0,
    "terminal_receipt_put_attempts": 0,
    "s3_get_calls": 0,
    "s3_put_calls": 0,
    "s3_delete_calls": 0,
    "s3_copy_calls": 0,
    "s3_tagging_mutation_calls": 0,
    "s3_other_calls": 0,
    "company_master_mutations": 0,
    "universe_mutations": 0,
    "company_master_or_universe_mutations": 0,
    "repository_writes": 0,
    "repository_mutations_by_workflow": 0,
    "github_actions_artifacts_uploaded": 0,
    "normalization_actions": 0,
    "pit_actions": 0,
    "promotion_actions": 0,
    "release_actions": 0,
    "production_actions": 0,
    "ambiguous_side_effects": False,
    "finance_provider_api_calls": 0,
    "provider_quota_reservations": 0,
    "raw_objects_written": 0,
    "quota_ledger_appends": 0,
    "raw_index_appends": 0,
    "aws_calls": 6,
    "sts_calls": 6,
    "sts_assume_role_attempts": 3,
    "sts_sessions_assumed": 3,
    "sts_get_caller_identity_calls": 3,
    "credentials_issued": 3,
    "s3_calls": 0,
    "s3_get_attempts": 0,
    "s3_put_attempts": 0,
    "s3_other_read_calls": 0,
    "successful_put_mutations": 0,
    "unconfirmed_or_failed_put_attempts": 0,
    "remote_custody_mutations": 0,
    "effects_reconciled": True,
    "effective_primary_acquisitions": INHERITED_G10_ACQUISITIONS,
    "effective_network_attempts": INHERITED_G10_ATTEMPTS,
}


class GateError(RuntimeError):
    """A deterministic control-gate failure."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class MissingCustodyError(GateError):
    pass


class MissingIdentityError(GateError):
    pass


class NonTargetIdentityConflictError(GateError):
    pass


class FutureSelectorObservationError(GateError):
    pass


def _fail(code: str, detail: str) -> None:
    raise GateError(code, detail)


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        _fail(code, detail)


def _require_exact(actual: Any, expected: Any, field_name: str) -> None:
    _require(actual == expected, "EXACT_BINDING_MISMATCH", f"{field_name} must equal {expected!r}")


def _require_hex64(value: Any, field_name: str) -> str:
    _require(isinstance(value, str) and HEX64.fullmatch(value) is not None,
             "INVALID_SHA256", f"{field_name} must be lowercase SHA-256 hex")
    return value


def canonical_json_lf_bytes(value: Any) -> bytes:
    """Canonical JSON form used for deterministic hash-only projections."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1_file(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def load_json_document(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError("INVALID_JSON_DOCUMENT", f"{path}: {exc}") from exc
    _require(isinstance(value, dict), "INVALID_JSON_DOCUMENT", f"{path} must contain one object")
    return value


def validate_predecessor_ineligible_preparation_binding(
    document: Mapping[str, Any], label: str,
) -> None:
    """Seal the G11C1 preparation that never became eligible for activation."""

    binding = document.get("predecessor_ineligible_preparation_binding")
    _require(isinstance(binding, Mapping), "INELIGIBLE_PREPARATION_BINDING_MISSING",
             f"{label}.predecessor_ineligible_preparation_binding is required")
    for key, expected in {
        "preparation_commit": PREDECESSOR_G11C1_PREPARATION_COMMIT,
        "preparation_tree": PREDECESSOR_G11C1_PREPARATION_TREE,
        "activation_created": False,
        "precheck_activation_created": False,
        "live_activation_created": False,
        "precheck_run_created": False,
        "live_run_created": False,
        "reuse_authorized": False,
        "terminal_receipt_path": PREDECESSOR_G11C1_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob": PREDECESSOR_G11C1_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": PREDECESSOR_G11C1_TERMINAL_RECEIPT_BYTES,
    }.items():
        _require_exact(binding.get(key), expected,
                       f"{label}.predecessor_ineligible_preparation_binding.{key}")


def validate_consumed_g11c1_identities(no_rerun: Mapping[str, Any], label: str) -> None:
    """Require every never-activated G11C1 identity to remain permanently consumed."""

    for field_name, expected_values in PREDECESSOR_G11C1_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        _require(
            isinstance(observed, list) and all(value in observed for value in expected_values),
            "G11C1_IDENTITY_NO_RERUN_BINDING_MISSING",
            f"{label}.{field_name} must include all ineligible G11C1 identities",
        )


def predecessor_invalidated_g11c2_binding() -> dict[str, Any]:
    """Return the exact terminal binding for G11C2, invalidated before LIVE."""

    return {
        "generation_id": "FINANCE-PAGE100-G11C2-20260901130250",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C2-20260901130250",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C2-20260901130250",
        "preparation_id": "FINANCE-PAGE100-G11C2-PREPARATION-20260901130250",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C2-20260901130250",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C2-20260901130250",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C2-20260901130250",
        "preparation_commit": PREDECESSOR_G11C2_PREPARATION_COMMIT,
        "preparation_tree": PREDECESSOR_G11C2_PREPARATION_TREE,
        "precheck_activation_commit": PREDECESSOR_G11C2_PRECHECK_ACTIVATION_COMMIT,
        "precheck_activation_tree": PREDECESSOR_G11C2_PRECHECK_ACTIVATION_TREE,
        "precheck_terminal_receipt_path":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_PATH,
        "precheck_terminal_receipt_append_commit":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_APPEND_COMMIT,
        "precheck_terminal_receipt_append_tree":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_APPEND_TREE,
        "precheck_execution_head_sha": PREDECESSOR_G11C2_PRECHECK_EXECUTION_HEAD_SHA,
        "precheck_execution_head_tree_sha":
            PREDECESSOR_G11C2_PRECHECK_EXECUTION_HEAD_TREE_SHA,
        "precheck_terminal_receipt_sha256":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_SHA256,
        "precheck_terminal_receipt_git_blob":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_GIT_BLOB,
        "precheck_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "precheck_terminal_receipt_bytes":
            PREDECESSOR_G11C2_PRECHECK_TERMINAL_RECEIPT_BYTES,
        "precheck_run_id": PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "precheck_job_id": PREDECESSOR_G11C2_PRECHECK_JOB_ID,
        "precheck_run_attempt": PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT,
        "precheck_result": "PASS",
        "terminal_checkpoint_commit": PREDECESSOR_G11C2_INVALIDATION_RECEIPT_COMMIT,
        "terminal_checkpoint_tree": PREDECESSOR_G11C2_INVALIDATION_RECEIPT_TREE,
        "terminal_receipt_path": PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C2_INVALIDATION_RECEIPT_SHA256,
        "terminal_receipt_git_blob":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": PREDECESSOR_G11C2_INVALIDATION_RECEIPT_BYTES,
        "precheck_activation_created": True,
        "precheck_run_created": True,
        "live_activation_created": False,
        "live_run_created": False,
        "reuse_authorized": False,
    }


def validate_predecessor_invalidated_g11c2_binding(
    document: Mapping[str, Any], label: str,
) -> None:
    binding = document.get("predecessor_invalidated_g11c2_binding")
    _require(isinstance(binding, Mapping), "G11C2_INVALIDATION_BINDING_MISSING",
             f"{label}.predecessor_invalidated_g11c2_binding is required")
    _require_exact(
        dict(binding), predecessor_invalidated_g11c2_binding(),
        f"{label}.predecessor_invalidated_g11c2_binding",
    )


def predecessor_terminal_g11c3_binding() -> dict[str, Any]:
    """Return the exact G11C3 LIVE packed-policy failure terminal binding."""

    return {
        "generation_id": "FINANCE-PAGE100-G11C3-20260901134119",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C3-20260901134119",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C3-20260901134119",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C3-20260901134119",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C3-20260901134119",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C3-20260901134119",
        "terminal_receipt_append_commit":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": PREDECESSOR_G11C3_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C3_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob": PREDECESSOR_G11C3_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": PREDECESSOR_G11C3_TERMINAL_RECEIPT_BYTES,
        "precheck_run_id": PREDECESSOR_G11C3_PRECHECK_RUN_ID,
        "live_run_id": PREDECESSOR_G11C3_LIVE_RUN_ID,
        "credentials_issued": False,
        "runner_started": False,
        "reuse_authorized": False,
    }


def validate_predecessor_terminal_g11c3_binding(
    document: Mapping[str, Any], label: str,
) -> None:
    binding = document.get("predecessor_terminal_g11c3_binding")
    _require(isinstance(binding, Mapping), "G11C3_TERMINAL_BINDING_MISSING",
             f"{label}.predecessor_terminal_g11c3_binding is required")
    _require_exact(
        dict(binding), predecessor_terminal_g11c3_binding(),
        f"{label}.predecessor_terminal_g11c3_binding",
    )


def predecessor_terminal_g11c4_binding() -> dict[str, Any]:
    """Return the exact first-probe OIDC-denial G11C4 PRECHECK binding."""

    return {
        "generation_id": "FINANCE-PAGE100-G11C4-20260901143300",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C4-20260901143300",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C4-20260901143300",
        "preparation_id": "FINANCE-PAGE100-G11C4-PREPARATION-20260901143300",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C4-20260901143300",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C4-20260901143300",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C4-20260901143300",
        "terminal_receipt_append_commit":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": PREDECESSOR_G11C4_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C4_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob": PREDECESSOR_G11C4_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": PREDECESSOR_G11C4_TERMINAL_RECEIPT_BYTES,
        "precheck_run_id": PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "precheck_job_id": PREDECESSOR_G11C4_PRECHECK_JOB_ID,
        "execution_head_sha": PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_SHA,
        "execution_tree_sha":
            PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_TREE_SHA,
        "run_attempt": PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT,
        "result": "FAIL_CLOSED",
        "terminal_state": (
            "TERMINAL_FAIL_CLOSED_FOCUSED_G11C4_PRECHECK_PROBE_1_CHECKPOINT_"
            "READ_STS_ASSUME_ROLE_WITH_WEB_IDENTITY_NOT_AUTHORIZED_ONE_STS_"
            "ATTEMPT_ZERO_CREDENTIALS_ZERO_DOWNSTREAM_EFFECT_NO_RERUN_LIVE_CLOSED"
        ),
        "entry_gate": "FAIL_CLOSED_PRECHECK_PROBE_1_STS_AUTHORIZATION_FAILURE",
        "oidc_token_requests": 1,
        "aws_calls": 1,
        "sts_calls": 1,
        "sts_assume_role_attempts": 1,
        "sts_assume_role_successes": 0,
        "sts_sessions_assumed": 0,
        "sts_get_caller_identity_calls": 0,
        "credentials_issued": 0,
        "probe_2_started": False,
        "probe_3_started": False,
        "runner_started": False,
        "s3_calls": 0,
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_custody_mutations": 0,
        "repository_mutations_by_workflow": 0,
        "all_downstream_effects_zero": True,
        "live_execution_started": False,
        "same_run_retry_authorized": False,
        "reuse_authorized": False,
    }


def validate_predecessor_terminal_g11c4_binding(
    document: Mapping[str, Any], label: str,
) -> None:
    binding = document.get("predecessor_terminal_g11c4_binding")
    _require(isinstance(binding, Mapping), "G11C4_TERMINAL_BINDING_MISSING",
             f"{label}.predecessor_terminal_g11c4_binding is required")
    _require_exact(
        dict(binding), predecessor_terminal_g11c4_binding(),
        f"{label}.predecessor_terminal_g11c4_binding",
    )


def predecessor_terminal_g11c5_binding() -> dict[str, Any]:
    """Return the exact terminal G11C5 PRECHECK contract-failure binding."""

    return {
        "generation_id": "FINANCE-PAGE100-G11C5-20260901152200",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C5-20260901152200",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C5-20260901152200",
        "preparation_id": "FINANCE-PAGE100-G11C5-PREPARATION-20260901152200",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C5-20260901152200",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C5-20260901152200",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C5-20260901152200",
        "preparation_commit": PREDECESSOR_G11C5_PREPARATION_COMMIT,
        "preparation_tree": PREDECESSOR_G11C5_PREPARATION_TREE,
        "precheck_activation_commit": PREDECESSOR_G11C5_PRECHECK_ACTIVATION_COMMIT,
        "precheck_activation_tree": PREDECESSOR_G11C5_PRECHECK_ACTIVATION_TREE,
        "terminal_receipt_append_commit":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": PREDECESSOR_G11C5_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob": PREDECESSOR_G11C5_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": PREDECESSOR_G11C5_TERMINAL_RECEIPT_BYTES,
        "execution_head_sha": PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_SHA,
        "execution_tree_sha": PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_TREE_SHA,
        "precheck_run_id": PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "precheck_job_id": PREDECESSOR_G11C5_PRECHECK_JOB_ID,
        "run_attempt": PREDECESSOR_G11C5_PRECHECK_RUN_ATTEMPT,
        "precheck_execution_result": "PASS",
        "result": "FAIL_CLOSED",
        "terminal_state": PREDECESSOR_G11C5_TERMINAL_STATE,
        "terminal_receipt_contract_valid": False,
        "defect": (
            "FROZEN_SCHEMA_REQUIRED_NO_RERUN_CONST_OMITS_CONSUMED_"
            "G11C4_PRECHECK_RUN_33477019917"
        ),
        "oidc_token_requests": 3,
        "aws_calls": 6,
        "sts_calls": 6,
        "sts_assume_role_attempts": 3,
        "sts_sessions_assumed": 3,
        "sts_get_caller_identity_calls": 3,
        "credentials_issued": 3,
        "s3_calls": 0,
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_custody_mutations": 0,
        "repository_mutations_by_workflow": 0,
        "effects_reconciled": True,
        "ambiguous_side_effects": False,
        "all_downstream_effects_zero": True,
        "live_execution_started": False,
        "same_run_retry_authorized": False,
        "reuse_authorized": False,
    }


def validate_predecessor_terminal_g11c5_binding(
    document: Mapping[str, Any], label: str,
) -> None:
    binding = document.get("predecessor_terminal_g11c5_binding")
    _require(isinstance(binding, Mapping), "G11C5_TERMINAL_BINDING_MISSING",
             f"{label}.predecessor_terminal_g11c5_binding is required")
    _require_exact(
        dict(binding), predecessor_terminal_g11c5_binding(),
        f"{label}.predecessor_terminal_g11c5_binding",
    )


def validate_consumed_predecessor_identities(
    no_rerun: Mapping[str, Any], label: str,
) -> None:
    """Require every G11C1 through G11C5 identity/execution to remain consumed."""

    _require_exact(no_rerun.get("consumed_github_runs"),
                   list(REQUIRED_NO_RERUN_RUNS),
                   f"{label}.consumed_github_runs")
    validate_consumed_g11c1_identities(no_rerun, label)
    for field_name, expected_values in PREDECESSOR_G11C2_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        _require(
            isinstance(observed, list) and all(value in observed for value in expected_values),
            "G11C2_IDENTITY_NO_RERUN_BINDING_MISSING",
            f"{label}.{field_name} must include all invalidated G11C2 identities",
        )
    for key, expected in {
        "g11c2_precheck_run_id": PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "g11c2_precheck_run_attempt": PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT,
        "g11c2_precheck_rerun_authorized": False,
        "g11c2_live_run_exists": False,
        "g11c2_activation_reuse_authorized": False,
        "g11c2_generation_reuse_authorized": False,
    }.items():
        _require_exact(no_rerun.get(key), expected, f"{label}.{key}")
    for field_name, expected_values in PREDECESSOR_G11C5_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        _require(
            isinstance(observed, list) and all(value in observed for value in expected_values),
            "G11C5_IDENTITY_NO_RERUN_BINDING_MISSING",
            f"{label}.{field_name} must include all terminal G11C5 identities",
        )
    for key, expected in {
        "g11c5_precheck_run_id": PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "g11c5_precheck_run_attempt": PREDECESSOR_G11C5_PRECHECK_RUN_ATTEMPT,
        "g11c5_precheck_rerun_authorized": False,
        "g11c5_precheck_execution_result": "PASS",
        "g11c5_terminal_receipt_result": "FAIL_CLOSED",
        "g11c5_terminal_receipt_contract_valid": False,
        "g11c5_live_run_exists": False,
        "g11c5_credentials_issued": 3,
        "g11c5_runner_started": True,
        "g11c5_live_execution_started": False,
        "g11c5_activation_reuse_authorized": False,
        "g11c5_generation_reuse_authorized": False,
    }.items():
        _require_exact(no_rerun.get(key), expected, f"{label}.{key}")
    for field_name, expected_values in PREDECESSOR_G11C4_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        _require(
            isinstance(observed, list) and all(value in observed for value in expected_values),
            "G11C4_IDENTITY_NO_RERUN_BINDING_MISSING",
            f"{label}.{field_name} must include all terminal G11C4 identities",
        )
    for key, expected in {
        "g11c4_precheck_run_id": PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "g11c4_precheck_run_attempt": PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT,
        "g11c4_precheck_rerun_authorized": False,
        "g11c4_credentials_issued": 0,
        "g11c4_runner_started": False,
        "g11c4_activation_reuse_authorized": False,
        "g11c4_generation_reuse_authorized": False,
    }.items():
        _require_exact(no_rerun.get(key), expected, f"{label}.{key}")
    for field_name, expected_values in PREDECESSOR_G11C3_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        _require(
            isinstance(observed, list) and all(value in observed for value in expected_values),
            "G11C3_IDENTITY_NO_RERUN_BINDING_MISSING",
            f"{label}.{field_name} must include all terminal G11C3 identities",
        )
    for key, expected in {
        "g11c3_precheck_run_id": PREDECESSOR_G11C3_PRECHECK_RUN_ID,
        "g11c3_precheck_run_attempt": 1,
        "g11c3_live_run_id": PREDECESSOR_G11C3_LIVE_RUN_ID,
        "g11c3_live_run_attempt": 1,
        "g11c3_credentials_issued": False,
        "g11c3_runner_started": False,
        "g11c3_activation_reuse_authorized": False,
        "g11c3_generation_reuse_authorized": False,
    }.items():
        _require_exact(no_rerun.get(key), expected, f"{label}.{key}")


def validate_plan_seed_material_binding(
    plan: Mapping[str, Any], seed_path: Path,
) -> None:
    """Bind the plan cursor to the exact seed bytes supplied to PRECHECK/LIVE."""

    resume = plan.get("resume_and_seed_contract")
    _require(isinstance(resume, Mapping), "INVALID_PLAN",
             "plan.resume_and_seed_contract is required")
    _require_exact(resume.get("checkpoint_seed_path"),
                   f"control/m3top3/public-data-source-admission/v1.0/{SEED_FILENAME}",
                   "plan.resume_and_seed_contract.checkpoint_seed_path")
    _require_exact(resume.get("checkpoint_seed_sha256"), sha256_file(seed_path),
                   "plan.resume_and_seed_contract.checkpoint_seed_sha256")
    _require_exact(resume.get("checkpoint_seed_git_blob"), git_blob_sha1_file(seed_path),
                   "plan.resume_and_seed_contract.checkpoint_seed_git_blob")


def expected_live_session_policy() -> dict[str, Any]:
    bucket_arn = "arn:aws:s3:::semi-data-plane-aofspds-20260815"
    source_arn = bucket_arn + "/raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1"
    g10_runtime = "PMO-FINANCE-PAGE100-G10-20260830044522"
    g10_pilot = "FINANCE-PAGE100-PILOT-G10-20260830044522"
    fresh_suffix = f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/*"
    claim = "_writer_claims/quota_day_kst=2026-09-01/execution-claim.json"
    return {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "s3:ListBucketVersions",
                "Resource": bucket_arn,
                "Condition": {"StringLike": {"s3:prefix": [
                    f"raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_*/{fresh_suffix}",
                    f"raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/{claim}",
                ]}},
            },
            {
                "Effect": "Allow",
                "Action": "s3:GetObjectVersion",
                "Resource": (
                    f"{source_arn}/_pilot_generation/runtime_lock_id={g10_runtime}/"
                    f"pilot_run_id={g10_pilot}/*"
                ),
                "Condition": {"StringEquals": {"s3:VersionId": [
                    "VdsI_D_jNujHIb9ff8loyRWtuAW737RI",
                    "30whtf2xTpWQYXPmr.Kt5RBnK1Y_YDI4",
                    "1dHYBfs4hg1tM7S6TckyUngOmfwWKZc2",
                    "iBxAq9V.V7eA_doOM39JcVt_gtzAHskI",
                ]}},
            },
            {
                "Effect": "Allow",
                "Action": "s3:GetObjectVersion",
                "Resource": (
                    f"{source_arn}/_pilot_control/runtime_lock_id={g10_runtime}/"
                    f"pilot_run_id={g10_pilot}/checkpoint.json"
                ),
                "Condition": {"StringEquals": {
                    "s3:VersionId": "r3eu2mkgFklGzpZPyKq5xXrt50wa6JgU",
                }},
            },
            {
                "Effect": "Allow",
                "Action": ["s3:PutObject", "s3:GetObject", "s3:GetObjectVersion"],
                "Resource": [
                    f"{source_arn}/_pilot_generation/{fresh_suffix}",
                    f"{source_arn}/_pilot_control/{fresh_suffix}",
                    f"{source_arn}/{claim}",
                ],
            },
        ],
    }


def expected_split_session_policies() -> dict[str, dict[str, Any]]:
    """Partition the former union without broadening any permission."""

    statements = expected_live_session_policy()["Statement"]
    return {
        "checkpoint_read_session_policy": {"Statement": [statements[2]]},
        "raw_four_read_session_policy": {"Statement": [statements[1]]},
        "final_list_write_session_policy": {
            "Statement": [statements[0], statements[3]],
        },
    }


def validate_live_session_policy_for_aws(
    path: Path, role: str | None = None,
) -> int:
    """Validate the compact ASCII policy emitted to configure-aws-credentials."""

    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise GateError("LIVE_SESSION_POLICY_NON_ASCII", str(path)) from exc
    source_text = text.strip()
    _require(bool(source_text), "LIVE_SESSION_POLICY_EMPTY", str(path))
    try:
        parsed = json.loads(source_text)
    except json.JSONDecodeError as exc:
        raise GateError("LIVE_SESSION_POLICY_INVALID_JSON", str(path)) from exc
    _require(isinstance(parsed, dict), "LIVE_SESSION_POLICY_INVALID_JSON",
             "LIVE session policy must contain one JSON object")
    _require("Version" not in parsed, "LIVE_SESSION_POLICY_VERSION_MUST_BE_OMITTED",
             "G11C6 inline policy must use the permission-equivalent default version")
    _require("${" not in source_text, "LIVE_SESSION_POLICY_VARIABLE_FORBIDDEN",
             "G11C6 inline policy may not contain policy variables")
    expected = (
        expected_live_session_policy()
        if role is None
        else expected_split_session_policies().get(role)
    )
    _require(expected is not None, "LIVE_SESSION_POLICY_ROLE_INVALID", str(role))
    _require_exact(parsed, expected, f"LIVE session policy semantics for {role or 'union'}")
    as_passed_to_aws = json.dumps(
        parsed, ensure_ascii=True, separators=(",", ":"),
    )
    _require(as_passed_to_aws.isascii(), "LIVE_SESSION_POLICY_NON_ASCII", str(path))
    _require(len(as_passed_to_aws) <= AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING,
             "LIVE_SESSION_POLICY_EXCEEDS_AWS_ASCII_CHARACTER_LIMIT",
             f"{len(as_passed_to_aws)}>{AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING}")
    return len(as_passed_to_aws)


@dataclass(frozen=True)
class HashedSourceRow:
    """Provider-neutral row supplied by a separately governed custody adapter.

    The adapter must derive ``custody_key_sha256`` from the exact UTF-8 bytes of
    ISSUCMPY_KSD_CUSTNO and must derive ``observed_identity_sha256`` with the
    already-governed G10/S2 identity algorithm.  This core performs no semantic
    normalization.
    """

    bas_dt: str
    page_no: int
    page_item_ordinal: int
    global_row_ordinal: int
    custody_key_sha256: str | None
    observed_identity_sha256: str | None

    @classmethod
    def from_document(cls, value: Mapping[str, Any]) -> "HashedSourceRow":
        return cls(
            bas_dt=value.get("basDt"),
            page_no=value.get("page_no"),
            page_item_ordinal=value.get("page_item_ordinal"),
            global_row_ordinal=value.get("global_row_ordinal"),
            custody_key_sha256=value.get("custody_key_sha256"),
            observed_identity_sha256=value.get("observed_identity_sha256"),
        )


@dataclass(frozen=True)
class SealedRawReference:
    key: str
    version_id: str
    sha256: str

    def validate(self) -> None:
        _require(bool(self.key), "RAW_NOT_SEALED", "raw key is absent")
        _require(bool(self.version_id), "RAW_NOT_SEALED", "raw VersionId is absent")
        _require_hex64(self.sha256, "raw.sha256")


@dataclass
class ProjectionState:
    source_rows: int = 0
    eligible_rows: int = 0
    excluded_rows: int = 0
    missing_rows: int = 0
    identity_map: dict[str, str] = field(default_factory=dict)
    eligible_descriptors: list[dict[str, Any]] = field(default_factory=list)
    excluded_global_row_ordinals: list[int] = field(default_factory=list)

    def copy(self) -> "ProjectionState":
        return ProjectionState(
            source_rows=self.source_rows,
            eligible_rows=self.eligible_rows,
            excluded_rows=self.excluded_rows,
            missing_rows=self.missing_rows,
            identity_map=dict(self.identity_map),
            eligible_descriptors=[dict(row) for row in self.eligible_descriptors],
            excluded_global_row_ordinals=list(self.excluded_global_row_ordinals),
        )

    @property
    def eligible_projection_sha256(self) -> str:
        return sha256_bytes(canonical_json_lf_bytes(self.eligible_descriptors))

    def assert_invariants(self) -> None:
        _require(
            self.source_rows == self.eligible_rows + self.excluded_rows + self.missing_rows,
            "PROJECTION_ACCOUNTING_MISMATCH",
            "source_rows must equal eligible_rows + excluded_rows + missing_rows",
        )
        _require(
            TARGET_CUSTODY_SHA256 not in self.identity_map,
            "SELECTOR_LEFT_ELIGIBLE",
            "target selector digest entered the eligible identity map",
        )


@dataclass(frozen=True)
class PageClassification:
    source_rows: int
    eligible_rows: int
    excluded_rows: int
    missing_rows: int
    eligible_global_row_ordinals: tuple[int, ...]
    excluded_global_row_ordinals: tuple[int, ...]
    raw_ref: SealedRawReference | None


def _validate_hashed_row(row: HashedSourceRow, expected_ordinal: int) -> None:
    _require(isinstance(row.bas_dt, str) and re.fullmatch(r"[0-9]{8}", row.bas_dt) is not None,
             "INVALID_SOURCE_ROW", "basDt must be YYYYMMDD digits")
    _require(isinstance(row.page_no, int) and row.page_no >= 1,
             "INVALID_SOURCE_ROW", "page_no must be positive")
    _require(isinstance(row.page_item_ordinal, int) and row.page_item_ordinal >= 1,
             "INVALID_SOURCE_ROW", "page_item_ordinal must be positive")
    _require_exact(row.global_row_ordinal, expected_ordinal, "global_row_ordinal")


def project_hashed_rows(
    rows: Iterable[HashedSourceRow],
    state: ProjectionState | None = None,
    *,
    selector_sha256: str = TARGET_CUSTODY_SHA256,
    raw_ref: SealedRawReference | None = None,
    require_sealed_raw: bool = False,
    selector_policy: str = FUTURE_SELECTOR_POLICY,
) -> tuple[ProjectionState, PageClassification]:
    """Apply the sealed seed rule or the forward-only OA-F01 stop rule.

    Only the already sealed occurrences 36--40 may be excluded.  A selector
    observation in newly acquired data is neither eligible nor excluded: after
    the page has been raw-custodied it raises a terminal pending-Owner gate.
    """

    _require_hex64(selector_sha256, "selector_sha256")
    _require(selector_policy in (SEED_SELECTOR_POLICY, FUTURE_SELECTOR_POLICY),
             "INVALID_SELECTOR_POLICY", "unrecognized selector continuation policy")
    if require_sealed_raw:
        _require(raw_ref is not None, "RAW_NOT_SEALED", "classification requires a sealed raw reference")
        raw_ref.validate()

    next_state = (state or ProjectionState()).copy()
    start_source = next_state.source_rows
    start_eligible = next_state.eligible_rows
    start_excluded = next_state.excluded_rows
    start_missing = next_state.missing_rows
    eligible_ordinals: list[int] = []
    excluded_ordinals: list[int] = []

    for row in rows:
        expected_ordinal = next_state.source_rows + 1
        _validate_hashed_row(row, expected_ordinal)
        next_state.source_rows += 1

        if row.custody_key_sha256 is None:
            next_state.missing_rows += 1
            raise MissingCustodyError(
                "MISSING_CUSTODY_FAIL_CLOSED",
                f"global row {row.global_row_ordinal} has no custody digest",
            )
        _require_hex64(row.custody_key_sha256, "custody_key_sha256")

        # OA-F01: exclusion authority is limited to the five sealed S3 rows.
        # Future selector observations require raw custody and then a terminal
        # Owner-decision stop; they are never automatically classified.
        if row.custody_key_sha256 == selector_sha256:
            if selector_policy == FUTURE_SELECTOR_POLICY:
                _require(require_sealed_raw and raw_ref is not None,
                         "RAW_NOT_SEALED",
                         "future selector observation must be raw-custodied before stop")
                raise FutureSelectorObservationError(
                    "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION",
                    f"global row {row.global_row_ordinal} matched selector after raw custody",
                )
            _require(
                row.global_row_ordinal in SEED_EXCLUDED_GLOBAL_ROW_ORDINALS,
                "SEALED_SELECTOR_SCOPE_VIOLATION",
                "seed exclusion is authorized only for ordinals 36 through 40",
            )
            next_state.excluded_rows += 1
            next_state.excluded_global_row_ordinals.append(row.global_row_ordinal)
            excluded_ordinals.append(row.global_row_ordinal)
            continue

        if row.observed_identity_sha256 is None:
            next_state.missing_rows += 1
            raise MissingIdentityError(
                "MISSING_NON_TARGET_IDENTITY_FAIL_CLOSED",
                f"global row {row.global_row_ordinal} has no non-target identity digest",
            )
        _require_hex64(row.observed_identity_sha256, "observed_identity_sha256")

        prior = next_state.identity_map.get(row.custody_key_sha256)
        if prior is not None and prior != row.observed_identity_sha256:
            raise NonTargetIdentityConflictError(
                "NON_TARGET_IDENTITY_CONFLICT_FAIL_CLOSED",
                f"global row {row.global_row_ordinal} conflicts with admitted custody digest",
            )
        next_state.identity_map[row.custody_key_sha256] = row.observed_identity_sha256
        next_state.eligible_rows += 1
        eligible_ordinals.append(row.global_row_ordinal)
        next_state.eligible_descriptors.append(
            {
                "basDt": row.bas_dt,
                "custody_key_sha256": row.custody_key_sha256,
                "global_row_ordinal": row.global_row_ordinal,
                "observed_identity_sha256": row.observed_identity_sha256,
                "page_item_ordinal": row.page_item_ordinal,
                "page_no": row.page_no,
            }
        )

    next_state.assert_invariants()
    page = PageClassification(
        source_rows=next_state.source_rows - start_source,
        eligible_rows=next_state.eligible_rows - start_eligible,
        excluded_rows=next_state.excluded_rows - start_excluded,
        missing_rows=next_state.missing_rows - start_missing,
        eligible_global_row_ordinals=tuple(eligible_ordinals),
        excluded_global_row_ordinals=tuple(excluded_ordinals),
        raw_ref=raw_ref,
    )
    return next_state, page


@dataclass(frozen=True)
class BudgetState:
    g11_acquisitions: int = 0
    g11_attempts: int = 0

    @property
    def effective_acquisitions(self) -> int:
        return INHERITED_G10_ACQUISITIONS + self.g11_acquisitions

    @property
    def effective_attempts(self) -> int:
        return INHERITED_G10_ATTEMPTS + self.g11_attempts

    @property
    def remaining_acquisitions(self) -> int:
        return G11_ACQUISITION_CEILING - self.g11_acquisitions

    @property
    def remaining_attempts(self) -> int:
        return G11_ATTEMPT_CEILING - self.g11_attempts

    def reserve_attempt(self, *, new_unique_acquisition: bool, page_attempt: int) -> "BudgetState":
        _require(1 <= page_attempt <= ATTEMPTS_PER_PAGE_CEILING,
                 "ATTEMPTS_PER_PAGE_CEILING", "page attempt exceeds the exact ceiling of 2")
        acquisitions = self.g11_acquisitions + int(new_unique_acquisition)
        attempts = self.g11_attempts + 1
        _require(acquisitions <= G11_ACQUISITION_CEILING,
                 "ACQUISITION_CEILING", "G11 would exceed 1696 new acquisitions")
        _require(attempts <= G11_ATTEMPT_CEILING,
                 "ATTEMPT_CEILING", "G11 would exceed 1996 new attempts")
        result = replace(self, g11_acquisitions=acquisitions, g11_attempts=attempts)
        _require(result.effective_acquisitions <= EFFECTIVE_ACQUISITION_CEILING,
                 "EFFECTIVE_ACQUISITION_CEILING", "effective acquisitions would exceed 1700")
        _require(result.effective_attempts <= EFFECTIVE_ATTEMPT_CEILING,
                 "EFFECTIVE_ATTEMPT_CEILING", "effective attempts would exceed 2000")
        return result


@dataclass(frozen=True)
class LiveAdapterBinding:
    path: Path
    repo_path: str
    sha256: str
    git_blob: str
    factory_symbol: str
    interface_version: str


def _literal_assignments(tree: ast.Module) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value_node = node.value
        if value_node is None:
            continue
        try:
            literal = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = literal
    return values


def validate_live_adapter_interface(
    adapter_path: Path,
    *,
    factory_symbol: str,
    interface_version: str,
) -> None:
    """Zero-effect AST validation; PRECHECK never imports executable code."""

    try:
        source = adapter_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(adapter_path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise GateError("LIVE_ADAPTER_PARSE_FAILED", adapter_path.name) from exc
    literals = _literal_assignments(tree)
    _require_exact(literals.get("ADAPTER_INTERFACE_VERSION"), interface_version,
                   "adapter.ADAPTER_INTERFACE_VERSION")
    _require_exact(literals.get("FACTORY_SYMBOL"), factory_symbol,
                   "adapter.FACTORY_SYMBOL")

    factory = next(
        (node for node in tree.body
         if isinstance(node, ast.FunctionDef) and node.name == factory_symbol),
        None,
    )
    _require(factory is not None, "LIVE_ADAPTER_INTERFACE_MISSING",
             f"top-level factory {factory_symbol} is absent")
    required_factory_args = {
        "authority_path", "plan_path", "seed_path", "manifest_path",
        "owner_decision_path", "live_activation_path", "precheck_receipt_path",
    }
    actual_args = {
        arg.arg for arg in (
            list(factory.args.posonlyargs)
            + list(factory.args.args)
            + list(factory.args.kwonlyargs)
        )
    }
    _require(required_factory_args <= actual_args,
             "LIVE_ADAPTER_FACTORY_SIGNATURE_MISMATCH",
             "factory lacks one or more governed path arguments")
    adapter_class = next(
        (node for node in tree.body
         if isinstance(node, ast.ClassDef) and node.name == "G11LiveAdapter"),
        None,
    )
    _require(adapter_class is not None and any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run"
        for node in adapter_class.body
    ), "LIVE_ADAPTER_INTERFACE_MISSING", "G11LiveAdapter.run is absent")


def load_sealed_live_adapter_factory(adapter_path: Path, expected_sha256: str) -> Any:
    """Import the already hash-checked adapter with dataclass-safe registration."""

    _require_exact(sha256_file(adapter_path), expected_sha256,
                   "runtime live adapter sha256")
    module_name = f"_m3top3_g11c6_live_adapter_{expected_sha256}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, adapter_path)
        _require(spec is not None and spec.loader is not None,
                 "LIVE_ADAPTER_IMPORT_FAILED", adapter_path.name)
        module = importlib.util.module_from_spec(spec)
        # dataclasses consult sys.modules during class decoration.
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise
        _require_exact(getattr(module, "ADAPTER_INTERFACE_VERSION", None),
                       LIVE_ADAPTER_INTERFACE_VERSION,
                       "runtime adapter interface version")
        _require_exact(getattr(module, "FACTORY_SYMBOL", None),
                       LIVE_ADAPTER_FACTORY_SYMBOL, "runtime adapter factory symbol")
        factory = getattr(module, LIVE_ADAPTER_FACTORY_SYMBOL, None)
        _require(callable(factory), "LIVE_ADAPTER_FACTORY_MISSING",
                 LIVE_ADAPTER_FACTORY_SYMBOL)
        factory_parameters = inspect.signature(factory).parameters
        for name in (
            "authority_path", "plan_path", "seed_path", "manifest_path",
            "owner_decision_path", "live_activation_path", "precheck_receipt_path",
            "deadline_monotonic", "live_head_sha", "live_head_tree",
        ):
            _require(name in factory_parameters,
                     "LIVE_ADAPTER_FACTORY_SIGNATURE_MISMATCH", name)
        return factory
    except GateError:
        raise
    except Exception as exc:
        raise GateError("LIVE_ADAPTER_IMPORT_FAILED", type(exc).__name__) from None


def validate_live_adapter_manifest(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
    supplied_path: Path | None = None,
) -> LiveAdapterBinding:
    _require_exact(manifest.get("live_adapter_gate"), LIVE_ADAPTER_GATE_READY,
                   "manifest.live_adapter_gate")
    adapter = manifest.get("live_adapter")
    safe = manifest.get("safe_executable_adapter")
    files = manifest.get("files")
    _require(isinstance(adapter, Mapping), "INVALID_MANIFEST", "manifest.live_adapter is required")
    _require(isinstance(safe, Mapping), "INVALID_MANIFEST",
             "manifest.safe_executable_adapter is required")
    _require(isinstance(files, Mapping) and isinstance(files.get("live_adapter"), Mapping),
             "INVALID_MANIFEST", "manifest.files.live_adapter is required")
    file_binding = files["live_adapter"]

    for field_name in ("executable", "sealed", "ready"):
        _require_exact(adapter.get(field_name), True, f"manifest.live_adapter.{field_name}")
    _require_exact(safe.get("ready"), True, "manifest.safe_executable_adapter.ready")

    repo_path = adapter.get("path")
    _require_exact(repo_path, LIVE_ADAPTER_REPO_PATH, "manifest.live_adapter.path")
    _require_exact(file_binding.get("path"), repo_path, "manifest.files.live_adapter.path")
    _require_exact(file_binding.get("filename"), Path(repo_path).name,
                   "manifest.files.live_adapter.filename")
    adapter_path = (repo_root / repo_path).resolve()
    try:
        adapter_path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise GateError("MANIFEST_PATH_ESCAPE", repo_path) from exc
    _require(adapter_path.is_file(), "LIVE_ADAPTER_FILE_MISSING", str(adapter_path))
    if supplied_path is not None:
        _require_exact(supplied_path.resolve(), adapter_path, "supplied live adapter path")

    observed_sha = sha256_file(adapter_path)
    observed_blob = git_blob_sha1_file(adapter_path)
    _require_exact(file_binding.get("sha256"), observed_sha,
                   "manifest.files.live_adapter.sha256")
    _require_exact(file_binding.get("git_blob"), observed_blob,
                   "manifest.files.live_adapter.git_blob")
    _require_exact(adapter.get("sha256"), observed_sha, "manifest.live_adapter.sha256")
    _require_exact(adapter.get("git_blob"), observed_blob, "manifest.live_adapter.git_blob")

    factory_symbol = safe.get("factory_symbol")
    interface_version = safe.get("interface_version")
    _require_exact(factory_symbol, LIVE_ADAPTER_FACTORY_SYMBOL,
                   "manifest.safe_executable_adapter.factory_symbol")
    _require_exact(interface_version, LIVE_ADAPTER_INTERFACE_VERSION,
                   "manifest.safe_executable_adapter.interface_version")
    safe_expected = {
        "path": repo_path,
        "sha256": observed_sha,
        "git_blob": observed_blob,
    }
    for key, value in safe_expected.items():
        _require_exact(safe.get(key), value, f"manifest.safe_executable_adapter.{key}")
    _require_exact(adapter.get("factory_symbol"), factory_symbol,
                   "manifest.live_adapter.factory_symbol")
    _require_exact(adapter.get("interface_version"), interface_version,
                   "manifest.live_adapter.interface_version")

    validate_live_adapter_interface(
        adapter_path,
        factory_symbol=factory_symbol,
        interface_version=interface_version,
    )
    return LiveAdapterBinding(
        path=adapter_path,
        repo_path=repo_path,
        sha256=observed_sha,
        git_blob=observed_blob,
        factory_symbol=factory_symbol,
        interface_version=interface_version,
    )


def validate_g11_object_key(key: str) -> None:
    """Reject writes outside the fresh G11C6 namespace or historical namespaces."""

    _require(isinstance(key, str) and bool(key), "INVALID_G11_OBJECT_KEY", "object key is empty")
    _require("G11C6" in key and GENERATION_TIMESTAMP in key,
             "INVALID_G11_OBJECT_KEY", "key is not bound to the fresh G11C6 generation")
    for forbidden in (
        "G10", "S2", "S3", "PMO-FINANCE-PAGE100-G10",
        "/G11/", "/G11C1/", "/G11C2/", *HISTORICAL_SUCCESSOR_NAMESPACE_MARKERS,
    ):
        _require(forbidden not in key, "HISTORICAL_NAMESPACE_WRITE_FORBIDDEN",
                 f"key contains historical namespace marker {forbidden}")


def validate_active_c6_prefixes(raw_prefix: Any, control_prefix: Any) -> None:
    """Reject any G11 through G11C5 namespace as the active G11C6 route."""

    for label, observed, expected in (
        ("raw", raw_prefix, G11_RAW_PREFIX),
        ("control", control_prefix, G11_CONTROL_PREFIX),
    ):
        _require(isinstance(observed, str) and observed,
                 "ACTIVE_PREFIX_INVALID", f"{label} prefix is absent")
        for marker in HISTORICAL_SUCCESSOR_NAMESPACE_MARKERS:
            _require(marker not in observed, "HISTORICAL_ACTIVE_PREFIX_FORBIDDEN",
                     f"{label} prefix contains {marker}")
        _require_exact(observed, expected, f"authority.custody_boundary.g11_{label}_prefix")


def validate_authority_document(document: Mapping[str, Any]) -> None:
    _require_exact(document.get("artifact"), AUTHORITY_SCHEMA, "authority.artifact")
    _require_exact(document.get("schema_version"), 1, "authority.schema_version")
    _require_exact(document.get("generation_timestamp"), GENERATION_TIMESTAMP,
                   "authority.generation_timestamp")
    _require_exact(document.get("authority_commit"), AUTHORITY_COMMIT,
                   "authority.authority_commit")
    owner = document.get("owner_authority_binding")
    _require(isinstance(owner, Mapping), "INVALID_AUTHORITY",
             "authority.owner_authority_binding is required")
    _require_exact(owner.get("commit"), OWNER_APPROVAL_COMMIT,
                   "authority.owner_authority_binding.commit")
    _require(str(owner.get("governing_forward_only_receipt_path", "")).endswith(
                 "G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1.json"),
             "INVALID_AUTHORITY", "governing forward-only decision receipt v1.1 is required")
    governing_bindings = {
        "governing_forward_only_receipt_commit": GOVERNED_CORRECTION_HEAD,
        "governing_forward_only_receipt_git_blob": OWNER_DECISION_V1_1_GIT_BLOB,
        "governing_forward_only_receipt_sha256": OWNER_DECISION_V1_1_SHA256,
    }
    for field_name, expected_value in governing_bindings.items():
        value = owner.get(field_name)
        _require(isinstance(value, str) and value and not value.startswith("__"),
                 "UNSEALED_AUTHORITY_PLACEHOLDER", f"authority.{field_name} is not sealed")
        _require_exact(value, expected_value, f"authority.{field_name}")

    validate_predecessor_ineligible_preparation_binding(document, "authority")
    validate_predecessor_invalidated_g11c2_binding(document, "authority")
    validate_predecessor_terminal_g11c3_binding(document, "authority")
    validate_predecessor_terminal_g11c4_binding(document, "authority")
    validate_predecessor_terminal_g11c5_binding(document, "authority")

    identity = document.get("fresh_identity")
    _require(isinstance(identity, Mapping), "INVALID_AUTHORITY", "authority.fresh_identity is required")
    _require_exact(identity.get("generation_id"), GENERATION_ID,
                   "authority.fresh_identity.generation_id")
    identity_expected = {
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "preparation_id": PREPARATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
    }
    for key, value in identity_expected.items():
        _require_exact(identity.get(key), value, f"authority.fresh_identity.{key}")
    _require_hex64(identity.get("owner_cap_spec_sha256"),
                   "authority.fresh_identity.owner_cap_spec_sha256")
    _require_hex64(identity.get("execution_token_sha256"),
                   "authority.fresh_identity.execution_token_sha256")
    _require_exact(identity.get("identity_reuse_authorized"), False,
                   "authority.fresh_identity.identity_reuse_authorized")

    owner_cap_spec = document.get("owner_cap_spec")
    token_material = document.get("execution_token_material")
    _require_exact(owner_cap_spec, expected_owner_cap_spec(), "authority.owner_cap_spec")
    _require_exact(token_material, expected_execution_token_material(),
                   "authority.execution_token_material")
    _require_exact(document.get("owner_cap_spec_canonicalization"),
                   "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
                   "authority.owner_cap_spec_canonicalization")
    _require_exact(document.get("execution_token_material_canonicalization"),
                   "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
                   "authority.execution_token_material_canonicalization")
    derived_owner_cap = sha256_bytes(canonical_json_lf_bytes(owner_cap_spec))
    derived_token = sha256_bytes(canonical_json_lf_bytes(token_material))
    _require_exact(derived_owner_cap, OWNER_CAP_SPEC_SHA256,
                   "derived owner_cap_spec_sha256")
    _require_exact(derived_token, EXECUTION_TOKEN_SHA256,
                   "derived execution_token_sha256")
    _require_exact(document.get("owner_cap_spec_sha256"), derived_owner_cap,
                   "authority.owner_cap_spec_sha256")
    _require_exact(document.get("execution_token_sha256"), derived_token,
                   "authority.execution_token_sha256")

    route = document.get("authorized_route")
    _require(isinstance(route, Mapping), "INVALID_AUTHORITY", "authority.authorized_route is required")
    _require_exact(route.get("route"),
                   "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_AT_20240131_PAGE_5",
                   "authority.authorized_route.route")
    _require_exact(
        route.get("one_fresh_exact_three_sts_probe_precheck_authorized"), True,
        "authority.authorized_route.one_fresh_exact_three_sts_probe_precheck_authorized",
    )
    _require_exact(route.get("github_run_attempt_required"), 1,
                   "authority.authorized_route.github_run_attempt_required")

    seed = document.get("sealed_s3_projection_binding")
    _require(isinstance(seed, Mapping), "INVALID_AUTHORITY",
             "authority.sealed_s3_projection_binding is required")
    seed_expected = {
        "bas_dt": SEED_BASE_DATE,
        "source_rows": SEED_SOURCE_ROWS,
        "eligible_rows": SEED_ELIGIBLE_ROWS,
        "excluded_rows_at_sealed_seed": SEED_EXCLUDED_ROWS,
        "missing_rows": SEED_MISSING_ROWS,
        "excluded_global_row_ordinals": list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
        "sealed_eligible_projection_sha256": SEALED_SEED_PROJECTION_SHA256,
        "selector_algorithm": SELECTOR_ALGORITHM,
        "selector_custody_key_sha256": TARGET_CUSTODY_SHA256,
        "selector_match_left_eligible": False,
        "raw_source_rows_mutated": False,
    }
    for key, value in seed_expected.items():
        _require_exact(seed.get(key), value, f"authority.sealed_s3_projection_binding.{key}")

    continuation = document.get("selector_continuation_semantics")
    _require(isinstance(continuation, Mapping), "INVALID_AUTHORITY",
             "authority.selector_continuation_semantics is required")
    continuation_expected = {
        "s3_exclusion_authority_scope":
            "SEALED_FIVE_OCCURRENCES_AT_GLOBAL_ROW_ORDINALS_36_THROUGH_40_ONLY",
        "exact_selector_auto_exclusion_applies_to_future_pages": False,
        "future_same_selector_rows_raw_custodied_before_parse": True,
        "future_same_selector_rows_excluded_from_eligible_projection": False,
        "future_selector_observation_after_raw_custody":
            "FAIL_CLOSED_PENDING_OWNER_DECISION",
        "checkpoint_advance_past_future_selector_observation": False,
        "sealed_excluded_count_without_new_owner_decision": SEED_EXCLUDED_ROWS,
    }
    for key, value in continuation_expected.items():
        _require_exact(continuation.get(key), value,
                       f"authority.selector_continuation_semantics.{key}")

    anchor = document.get("exact_resume_anchor")
    _require(isinstance(anchor, Mapping), "INVALID_AUTHORITY",
             "authority.exact_resume_anchor is required")
    _require_exact(anchor.get("g10_checkpoint_sha256"), PREDECESSOR_CHECKPOINT_SHA256,
                   "authority.exact_resume_anchor.g10_checkpoint_sha256")
    _require_exact(anchor.get("resume_bas_dt"), SEED_BASE_DATE,
                   "authority.exact_resume_anchor.resume_bas_dt")
    _require_exact(anchor.get("next_page"), FIRST_NEW_PAGE,
                   "authority.exact_resume_anchor.next_page")
    _require_exact(anchor.get("reacquire_completed_date_or_first_four_current_date_pages"), False,
                   "authority.exact_resume_anchor.reacquire_completed_date_or_first_four_current_date_pages")

    budget = document.get("finance_bounds")
    _require(isinstance(budget, Mapping), "INVALID_AUTHORITY", "authority.finance_bounds is required")
    authority_budget = {
        "aggregate_max_primary_page_acquisitions": EFFECTIVE_ACQUISITION_CEILING,
        "aggregate_max_network_attempts_total": EFFECTIVE_ATTEMPT_CEILING,
        "max_attempts_per_logical_page": ATTEMPTS_PER_PAGE_CEILING,
        "g10_spent_primary_acquisitions": INHERITED_G10_ACQUISITIONS,
        "g10_spent_network_attempts": INHERITED_G10_ATTEMPTS,
        "maximum_new_g11_primary_acquisitions": G11_ACQUISITION_CEILING,
        "maximum_new_g11_network_attempts": G11_ATTEMPT_CEILING,
    }
    for key, value in authority_budget.items():
        _require_exact(budget.get(key), value, f"authority.finance_bounds.{key}")

    custody = document.get("custody_boundary")
    _require(isinstance(custody, Mapping), "INVALID_AUTHORITY",
             "authority.custody_boundary is required")
    validate_active_c6_prefixes(
        custody.get("g11_raw_prefix"), custody.get("g11_control_prefix")
    )
    _require_exact(custody.get("execution_claim_key"), EXECUTION_CLAIM_KEY,
                   "authority.custody_boundary.execution_claim_key")
    _require_exact(custody.get("predecessor_objects_immutable"), True,
                   "authority.custody_boundary.predecessor_objects_immutable")

    _require_exact(
        document.get("adapter_execution_order_binding"),
        expected_adapter_execution_order(),
        "authority.adapter_execution_order_binding",
    )
    _require_exact(document.get("live_pre_mutation_order"),
                   expected_live_pre_mutation_order(),
                   "authority.live_pre_mutation_order")

    no_rerun = document.get("no_rerun")
    _require(isinstance(no_rerun, Mapping), "INVALID_AUTHORITY", "authority.no_rerun is required")
    consumed = no_rerun.get("consumed_github_runs")
    _require_exact(consumed, list(REQUIRED_NO_RERUN_RUNS),
                   "authority.no_rerun.consumed_github_runs")
    validate_consumed_predecessor_identities(no_rerun, "authority.no_rerun")

    entry_gate = document.get("entry_gate")
    _require(isinstance(entry_gate, Mapping), "INVALID_AUTHORITY",
             "authority.entry_gate is required")
    _require_exact(entry_gate.get("live_session_policy_ascii_and_size_ceiling_verified"),
                   True,
                   "authority.entry_gate.live_session_policy_ascii_and_size_ceiling_verified")

    claims = document.get("claim_ceiling")
    _require(isinstance(claims, Mapping), "INVALID_AUTHORITY", "authority.claim_ceiling is required")
    _require_exact(claims.get("source_admission_verdict"), "NOT_ADMITTED",
                   "authority.claim_ceiling.source_admission_verdict")
    for key in ("issuer_identity_resolved", "normalization", "pit", "promotion", "release", "production"):
        _require_exact(claims.get(key), False, f"authority.claim_ceiling.{key}")


def _validate_budget_mapping(budget: Mapping[str, Any], label: str) -> None:
    expected = {
        "effective_acquisition_ceiling": EFFECTIVE_ACQUISITION_CEILING,
        "inherited_g10_acquisitions": INHERITED_G10_ACQUISITIONS,
        "g11_acquisition_ceiling": G11_ACQUISITION_CEILING,
        "effective_attempt_ceiling": EFFECTIVE_ATTEMPT_CEILING,
        "inherited_g10_attempts": INHERITED_G10_ATTEMPTS,
        "g11_attempt_ceiling": G11_ATTEMPT_CEILING,
        "attempts_per_page_ceiling": ATTEMPTS_PER_PAGE_CEILING,
    }
    for key, value in expected.items():
        _require_exact(budget.get(key), value, f"{label}.{key}")


def expected_adapter_execution_order() -> dict[str, Any]:
    return {
        "fixed_quota_day_kst": QUOTA_DAY_KST,
        "runtime_kst_date_equality_required_before_any_mutation": True,
        "exact_pre_mutation_order": list(LIVE_PRE_MUTATION_PHASES),
        "runtime_kst_date_recheck_immediately_before_claim": True,
        "exact_predecessor_get_object_version_reads": 5,
        "ordered_read_roles": [
            "CHECKPOINT", "RAW_PAGE_1", "RAW_PAGE_2", "RAW_PAGE_3", "RAW_PAGE_4",
        ],
        "exact_live_list_bucket_versions_calls": 3,
        "ordered_list_targets": [
            "FRESH_G11_GENERATION_PREFIX",
            "FRESH_G11_CONTROL_PREFIX",
            "EXACT_2026_09_01_EXECUTION_CLAIM_KEY",
        ],
        "all_three_lists_complete_before_execution_claim": True,
        "precheck_performs_runtime_s3_reads": False,
        "precheck_oidc_sts_policy_packing_probe_count": STS_POLICY_PROBE_COUNT,
        "precheck_oidc_sts_policy_packing_probe_roles": [
            item["role"] for item in OIDC_STS_POLICY_PACKING_PROBES
        ],
        "live_head_object_calls": 0,
        "live_predecessor_unversioned_get_object_calls": 0,
        "fresh_g11_or_claim_unversioned_get_object_use":
            "UNCERTAIN_WRITE_RECONCILIATION_ONLY",
        "all_reads_complete_before_execution_claim": True,
        "execution_claim_create_precondition": "If-None-Match:*",
        "execution_claim_created_before_provider_quota_or_other_write": True,
        "provider_quota_and_other_writes_before_claim": False,
    }


def expected_live_pre_mutation_order() -> list[str]:
    return [
        "VERIFY_RUNTIME_ASIA_SEOUL_QUOTA_DAY_EQUALS_2026_09_01",
        "GET_AND_VERIFY_EXACT_G10_CHECKPOINT_OBJECT_VERSION",
        "GET_AND_VERIFY_EXACT_G10_RAW_PAGE_1_OBJECT_VERSION",
        "GET_AND_VERIFY_EXACT_G10_RAW_PAGE_2_OBJECT_VERSION",
        "GET_AND_VERIFY_EXACT_G10_RAW_PAGE_3_OBJECT_VERSION",
        "GET_AND_VERIFY_EXACT_G10_RAW_PAGE_4_OBJECT_VERSION",
        "LIST_EXACT_FRESH_G11_GENERATION_PREFIX_VERSIONS_ONCE_AND_REQUIRE_EMPTY",
        "LIST_EXACT_FRESH_G11_CONTROL_PREFIX_VERSIONS_ONCE_AND_REQUIRE_EMPTY",
        "LIST_EXACT_2026_09_01_EXECUTION_CLAIM_KEY_VERSIONS_ONCE_AND_REQUIRE_EMPTY",
        "ONLY_AFTER_ALL_FIVE_READS_PASS_CREATE_EXECUTION_CLAIM_WITH_IF_NONE_MATCH_STAR",
        "ONLY_AFTER_CLAIM_PASS_CREATE_FRESH_G11_CHECKPOINT_OR_RESERVE_QUOTA_OR_CALL_PROVIDER",
    ]


def expected_live_seed_verification_actions() -> list[str]:
    return [
        "VERIFY_RUNTIME_ASIA_SEOUL_QUOTA_DAY_EQUALS_FIXED_2026_09_01",
        "GET_EXACT_G10_CHECKPOINT_VERSION_ONCE",
        "VERIFY_G10_CHECKPOINT_VERSION_SHA256_BYTES_REVISION_AND_ETAG",
        "GET_EACH_OF_THE_FOUR_EXACT_G10_RAW_PAGE_VERSIONS_ONCE",
        "VERIFY_ALL_FOUR_RAW_PAGE_KEYS_VERSION_IDS_SHA256_BYTES_ETAGS_AND_AES256_BINDINGS",
        "VERIFY_EXACT_FIVE_OBJECT_VECTOR_AND_18730_RAW_BYTE_AGGREGATE",
        "PERFORM_EXACTLY_THREE_BOUNDED_LISTBUCKETVERSIONS_CALLS_FOR_FRESH_G11_GENERATION_PREFIX_CONTROL_PREFIX_AND_EXACT_2026_09_01_EXECUTION_CLAIM_KEY",
        "REQUIRE_ALL_THREE_LIST_RESULTS_EMPTY_OF_VERSIONS_AND_DELETE_MARKERS",
        "COMPLETE_ALL_THREE_LISTS_ALL_FIVE_GET_OBJECT_VERSION_READS_AND_DATE_EQUALITY_GATE_BEFORE_EXECUTION_CLAIM_QUOTA_RESERVATION_PROVIDER_CALL_OR_ANY_S3_WRITE",
        "DO_NOT_USE_HEAD_OR_UNVERSIONED_GET_FOR_ANY_PREDECESSOR_OBJECT",
        "TRANSFORM_IN_MEMORY_BY_REMOVING_ONLY_THE_SEALED_SELECTOR_IDENTITY_ENTRY",
        "PRESERVE_RAW_AND_PAGINATION_COUNTS_AT_40_AND_SET_ELIGIBLE_BASELINE_TO_35",
        "PRESERVE_COMPLETED_20240102_AND_20240131_PAGES_1_THROUGH_4_WITHOUT_REACQUISITION",
    ]


def expected_owner_cap_spec() -> dict[str, Any]:
    return {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_OWNER_CAP_SPEC_v1.0",
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "activation_base_tree": ACTIVATION_BASE_TREE,
        "standing_authority_issue": 49,
        "standing_authority_comment_id": 5464265547,
        "predecessor_failure_receipt_sha256": PREDECESSOR_FAILURE_RECEIPT_SHA256,
        "predecessor_failure_payload_sha256": PREDECESSOR_FAILURE_PAYLOAD_SHA256,
        "predecessor_failure_run_id": 33466306591,
        "predecessor_g11c1_ineligible_preparation_commit":
            PREDECESSOR_G11C1_PREPARATION_COMMIT,
        "predecessor_g11c1_ineligible_preparation_tree":
            PREDECESSOR_G11C1_PREPARATION_TREE,
        "predecessor_g11c1_terminal_receipt_sha256":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c1_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c2_preparation_commit":
            PREDECESSOR_G11C2_PREPARATION_COMMIT,
        "predecessor_g11c2_preparation_tree": PREDECESSOR_G11C2_PREPARATION_TREE,
        "predecessor_g11c2_invalidation_receipt_sha256":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_SHA256,
        "predecessor_g11c2_invalidation_receipt_payload_sha256":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c2_precheck_run_id": PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "predecessor_g11c3_terminal_receipt_sha256":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c3_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c3_precheck_run_id": PREDECESSOR_G11C3_PRECHECK_RUN_ID,
        "predecessor_g11c3_live_run_id": PREDECESSOR_G11C3_LIVE_RUN_ID,
        "predecessor_g11c4_terminal_receipt_sha256":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c4_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c4_precheck_run_id": PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "predecessor_g11c4_precheck_job_id": PREDECESSOR_G11C4_PRECHECK_JOB_ID,
        "predecessor_g11c5_terminal_receipt_sha256":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c5_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c5_precheck_run_id": PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "predecessor_g11c5_precheck_job_id": PREDECESSOR_G11C5_PRECHECK_JOB_ID,
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "preparation_id": PREPARATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "source_id": "M3TOP3-FINANCE-STOCK-RIGHTS-v1",
        "operation": "getRighExerReasSche_V2",
        "quota_day_kst": "2026-09-01",
        "ordered_primary_dates": list(PRIMARY_DATES),
        "ordered_primary_dates_sha256": PRIMARY_DATES_SHA256,
        "request_page_size": 10,
        "max_pages_per_date": 100,
        "aggregate_max_primary_page_acquisitions": EFFECTIVE_ACQUISITION_CEILING,
        "aggregate_max_network_attempts_total": EFFECTIVE_ATTEMPT_CEILING,
        "max_attempts_per_logical_page": ATTEMPTS_PER_PAGE_CEILING,
        "g10_spent_primary_acquisitions": INHERITED_G10_ACQUISITIONS,
        "g10_spent_network_attempts": INHERITED_G10_ATTEMPTS,
        "maximum_new_g11c6_primary_acquisitions": G11_ACQUISITION_CEILING,
        "maximum_new_g11c6_network_attempts": G11_ATTEMPT_CEILING,
        "reused_completed_dates": ["20240102"],
        "reused_partial_pages": {"20240131": [1, 2, 3, 4]},
        "max_fresh_predecessor_page_revalidations": 0,
        "predecessor_live_run_id": 33273146915,
        "predecessor_rerun_authorized": False,
        "resume_bas_dt": SEED_BASE_DATE,
        "resume_page": FIRST_NEW_PAGE,
        "sealed_eligible_rows": SEED_ELIGIBLE_ROWS,
        "sealed_excluded_rows": SEED_EXCLUDED_ROWS,
        "sealed_projection_sha256": SEALED_SEED_PROJECTION_SHA256,
        "sealed_excluded_ordinals": list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
        "future_selector_disposition":
            "RAW_CUSTODY_FIRST_THEN_FAIL_CLOSED_PENDING_OWNER_DECISION",
        "future_selector_auto_exclusion_authorized": False,
    }


def expected_execution_token_material() -> dict[str, Any]:
    return {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_EXECUTION_TOKEN_MATERIAL_v1.0",
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "preparation_id": PREPARATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "activation_base_tree": ACTIVATION_BASE_TREE,
        "predecessor_failure_receipt_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_PAGE100_G11_ELIGIBLE_SUCCESSOR_"
            "LIVE_TERMINAL_RECEIPT_33466306591_v1.0.json"
        ),
        "predecessor_failure_receipt_git_blob": PREDECESSOR_FAILURE_RECEIPT_GIT_BLOB,
        "predecessor_failure_receipt_sha256": PREDECESSOR_FAILURE_RECEIPT_SHA256,
        "predecessor_failure_payload_sha256": PREDECESSOR_FAILURE_PAYLOAD_SHA256,
        "predecessor_g11c1_ineligible_preparation_commit":
            PREDECESSOR_G11C1_PREPARATION_COMMIT,
        "predecessor_g11c1_ineligible_preparation_tree":
            PREDECESSOR_G11C1_PREPARATION_TREE,
        "predecessor_g11c1_terminal_receipt_path":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_PATH,
        "predecessor_g11c1_terminal_receipt_git_blob":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_GIT_BLOB,
        "predecessor_g11c1_terminal_receipt_sha256":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c1_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c2_preparation_commit":
            PREDECESSOR_G11C2_PREPARATION_COMMIT,
        "predecessor_g11c2_preparation_tree": PREDECESSOR_G11C2_PREPARATION_TREE,
        "predecessor_g11c2_invalidation_receipt_path":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PATH,
        "predecessor_g11c2_invalidation_receipt_git_blob":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_GIT_BLOB,
        "predecessor_g11c2_invalidation_receipt_sha256":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_SHA256,
        "predecessor_g11c2_invalidation_receipt_payload_sha256":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c2_invalidation_receipt_bytes":
            PREDECESSOR_G11C2_INVALIDATION_RECEIPT_BYTES,
        "predecessor_g11c2_precheck_run_id": PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "predecessor_g11c3_terminal_receipt_path":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_PATH,
        "predecessor_g11c3_terminal_receipt_git_blob":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_GIT_BLOB,
        "predecessor_g11c3_terminal_receipt_sha256":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c3_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c3_terminal_receipt_bytes":
            PREDECESSOR_G11C3_TERMINAL_RECEIPT_BYTES,
        "predecessor_g11c3_precheck_run_id": PREDECESSOR_G11C3_PRECHECK_RUN_ID,
        "predecessor_g11c3_live_run_id": PREDECESSOR_G11C3_LIVE_RUN_ID,
        "predecessor_g11c4_terminal_receipt_path":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_PATH,
        "predecessor_g11c4_terminal_receipt_git_blob":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_GIT_BLOB,
        "predecessor_g11c4_terminal_receipt_sha256":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c4_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c4_terminal_receipt_bytes":
            PREDECESSOR_G11C4_TERMINAL_RECEIPT_BYTES,
        "predecessor_g11c4_precheck_run_id": PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "predecessor_g11c4_precheck_job_id": PREDECESSOR_G11C4_PRECHECK_JOB_ID,
        "predecessor_g11c4_execution_head_sha":
            PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_SHA,
        "predecessor_g11c4_execution_head_tree_sha":
            PREDECESSOR_G11C4_PRECHECK_EXECUTION_HEAD_TREE_SHA,
        "predecessor_g11c5_terminal_receipt_path":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_PATH,
        "predecessor_g11c5_terminal_receipt_git_blob":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_GIT_BLOB,
        "predecessor_g11c5_terminal_receipt_sha256":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c5_terminal_receipt_payload_sha256":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c5_terminal_receipt_bytes":
            PREDECESSOR_G11C5_TERMINAL_RECEIPT_BYTES,
        "predecessor_g11c5_precheck_run_id": PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "predecessor_g11c5_precheck_job_id": PREDECESSOR_G11C5_PRECHECK_JOB_ID,
        "predecessor_g11c5_execution_head_sha":
            PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_SHA,
        "predecessor_g11c5_execution_head_tree_sha":
            PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_TREE_SHA,
        "standing_authority_issue": 49,
        "standing_authority_comment_id": 5464265547,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "branch": "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828",
        "route": (
            "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_AT_"
            "20240131_PAGE_5"
        ),
        "one_shot": True,
        "github_run_attempt_required": 1,
        "same_run_retry_authorized": False,
        "same_activation_reuse_authorized": False,
        "same_latch_reuse_authorized": False,
        "identity_reuse_authorized": False,
    }


def validate_plan_document(document: Mapping[str, Any]) -> None:
    _require_exact(document.get("artifact"), PLAN_SCHEMA, "plan.artifact")
    _require_exact(document.get("schema_version"), 1, "plan.schema_version")
    _require_exact(document.get("generation_timestamp"), GENERATION_TIMESTAMP,
                   "plan.generation_timestamp")
    _require_exact(document.get("authority_commit"), AUTHORITY_COMMIT,
                   "plan.authority_commit")
    _require_exact(document.get("generation_id"), GENERATION_ID, "plan.generation_id")
    authority = document.get("authority")
    _require(isinstance(authority, Mapping), "INVALID_PLAN", "plan.authority is required")
    _require_exact(authority.get("owner_authority_commit"), OWNER_APPROVAL_COMMIT,
                   "plan.authority.owner_authority_commit")
    identity = document.get("identity")
    _require(isinstance(identity, Mapping), "INVALID_PLAN", "plan.identity is required")
    plan_identity_expected = {
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "preparation_id": PREPARATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
    }
    for key, value in plan_identity_expected.items():
        _require_exact(identity.get(key), value, f"plan.identity.{key}")

    validate_predecessor_ineligible_preparation_binding(document, "plan")
    validate_predecessor_invalidated_g11c2_binding(document, "plan")
    validate_predecessor_terminal_g11c3_binding(document, "plan")
    validate_predecessor_terminal_g11c4_binding(document, "plan")
    validate_predecessor_terminal_g11c5_binding(document, "plan")
    plan_no_rerun = document.get("no_rerun")
    _require(isinstance(plan_no_rerun, Mapping), "INVALID_PLAN",
             "plan.no_rerun is required")
    validate_consumed_predecessor_identities(plan_no_rerun, "plan.no_rerun")

    resume = document.get("resume_and_seed_contract")
    _require(isinstance(resume, Mapping), "INVALID_PLAN",
             "plan.resume_and_seed_contract is required")
    _require_exact(resume.get("predecessor_checkpoint_sha256"), PREDECESSOR_CHECKPOINT_SHA256,
                   "plan.resume_and_seed_contract.predecessor_checkpoint_sha256")
    _require_exact(resume.get("start_bas_dt"), SEED_BASE_DATE,
                   "plan.resume_and_seed_contract.start_bas_dt")
    _require_exact(resume.get("start_page"), FIRST_NEW_PAGE,
                   "plan.resume_and_seed_contract.start_page")

    budget = document.get("budget_contract")
    _require(isinstance(budget, Mapping), "INVALID_PLAN", "plan.budget_contract is required")
    plan_budget = {
        "aggregate_primary_acquisition_ceiling": EFFECTIVE_ACQUISITION_CEILING,
        "aggregate_network_attempt_ceiling": EFFECTIVE_ATTEMPT_CEILING,
        "g10_spent_primary_acquisitions": INHERITED_G10_ACQUISITIONS,
        "g10_spent_network_attempts": INHERITED_G10_ATTEMPTS,
        "g11_primary_acquisition_ceiling": G11_ACQUISITION_CEILING,
        "g11_network_attempt_ceiling": G11_ATTEMPT_CEILING,
        "max_attempts_per_logical_page": ATTEMPTS_PER_PAGE_CEILING,
        "historical_predecessor_nine_calls_recounted": False,
    }
    for key, value in plan_budget.items():
        _require_exact(budget.get(key), value, f"plan.budget_contract.{key}")

    phases = document.get("ordered_phases")
    _require(isinstance(phases, list), "INVALID_PLAN", "plan.ordered_phases is required")
    precheck_phase = next((phase for phase in phases if phase.get("phase") == "PRECHECK"), None)
    _require(isinstance(precheck_phase, Mapping), "INVALID_PLAN", "PRECHECK phase is required")
    _require_exact(
        precheck_phase.get("allowed_effects"),
        "EXACT_THREE_OIDC_STS_POLICY_PACKING_PROBES_ONLY_ZERO_DOWNSTREAM_EFFECT",
        "plan PRECHECK allowed_effects",
    )
    for key, value in {
        "sts_policy_probe_count": 3,
        "aws_calls": 6,
        "sts_calls": 6,
        "sts_assume_role_attempts": 3,
        "sts_sessions_assumed": 3,
        "sts_get_caller_identity_calls": 3,
        "credentials_issued": 3,
    }.items():
        _require_exact(precheck_phase.get(key), value, f"plan PRECHECK {key}")
    for key in (
        "provider_calls", "quota_reservations", "s3_calls",
        "s3_get_object_version_calls", "s3_bucket_metadata_calls",
        "raw_writes", "s3_put_delete_copy", "repository_mutations_by_workflow",
        "remote_custody_mutations",
    ):
        _require_exact(precheck_phase.get(key), 0, f"plan PRECHECK {key}")

    seed_read_phase = next(
        (phase for phase in phases
         if phase.get("phase") == "LIVE_READ_ONLY_SEED_VERIFICATION_BEFORE_ANY_MUTATION"),
        None,
    )
    _require(isinstance(seed_read_phase, Mapping), "INVALID_PLAN",
             "LIVE read-only seed verification phase is required")
    _require_exact(seed_read_phase.get("s3_get_object_version_calls"), 5,
                   "plan LIVE seed read count")
    _require_exact(seed_read_phase.get("s3_list_bucket_versions_calls"), 3,
                   "plan LIVE namespace-list read count")
    _require_exact(seed_read_phase.get("s3_head_object_calls"), 0,
                   "plan LIVE HeadObject count")
    _require_exact(seed_read_phase.get("predecessor_unversioned_get_object_calls"), 0,
                   "plan LIVE predecessor unversioned GetObject count")
    for key in (
        "g10_checkpoint_mutations", "execution_claim_writes", "quota_reservations",
        "provider_calls", "s3_writes",
    ):
        _require_exact(seed_read_phase.get(key), 0, f"plan LIVE seed phase {key}")
    _require_exact(seed_read_phase.get("actions"),
                   expected_live_seed_verification_actions(),
                   "plan LIVE seed/date/list pre-mutation actions")

    first_mutation_phase = next(
        (phase for phase in phases
         if phase.get("phase") == "LIVE_FIRST_MUTATION_AND_CHECKPOINT_INITIALIZATION"),
        None,
    )
    _require(isinstance(first_mutation_phase, Mapping), "INVALID_PLAN",
             "LIVE first mutation phase is required")
    first_actions = first_mutation_phase.get("actions")
    _require(isinstance(first_actions, list) and first_actions and
             first_actions[0] == "CREATE_EXACT_2026_09_01_EXECUTION_CLAIM_ONCE_WITH_IF_NONE_MATCH_STAR",
             "INVALID_PLAN", "execution claim must be the first LIVE mutation")

    live_phase = next((phase for phase in phases if phase.get("phase") == "BOUNDED_LIVE_DATA_GENERATION"), None)
    _require(isinstance(live_phase, Mapping), "INVALID_PLAN", "bounded LIVE phase is required")
    _require_exact(live_phase.get("start"), "bas_dt=20240131,pageNo=5", "plan LIVE start")
    order = live_phase.get("per_logical_page_order")
    _require(isinstance(order, list) and
             "IF_SELECTOR_IS_OBSERVED_ON_PAGE_5_OR_LATER_AFTER_RAW_CUSTODY_FAIL_CLOSED_PENDING_OWNER_DECISION_WITHOUT_AUTO_EXCLUSION_OR_CHECKPOINT_ADVANCE" in order,
             "INVALID_PLAN", "OA-F01 future selector stop is absent from per-page order")


def _projection_summary(document: Mapping[str, Any]) -> Mapping[str, Any]:
    projection = document.get("projection")
    _require(isinstance(projection, Mapping), "INVALID_SEED", "seed.projection is required")
    return projection


def validate_seed_document(document: Mapping[str, Any]) -> str:
    """Validate the sealed 40-row seed; recompute it when hash-only rows are present."""

    artifact = document.get("artifact", document.get("schema"))
    _require_exact(artifact, SEED_SCHEMA, "seed.artifact")
    _require_exact(document.get("schema_version", 1), 1, "seed.schema_version")
    authority_commit = document.get("authority_commit")
    if authority_commit is None and isinstance(document.get("authority"), Mapping):
        authority_commit = document["authority"].get("owner_authority_commit")
    _require_exact(authority_commit, AUTHORITY_COMMIT, "seed authority commit")
    _require_exact(document.get("generation_timestamp"), GENERATION_TIMESTAMP,
                   "seed.generation_timestamp")
    _require_exact(document.get("bas_dt", document.get("resume_bas_dt")), SEED_BASE_DATE,
                   "seed.bas_dt")
    _require_exact(document.get("next_page", document.get("start_page")), FIRST_NEW_PAGE,
                   "seed.next_page")
    validate_predecessor_ineligible_preparation_binding(document, "seed")
    validate_predecessor_invalidated_g11c2_binding(document, "seed")
    validate_predecessor_terminal_g11c3_binding(document, "seed")
    validate_predecessor_terminal_g11c4_binding(document, "seed")
    validate_predecessor_terminal_g11c5_binding(document, "seed")
    seed_no_rerun = document.get("no_rerun")
    _require(isinstance(seed_no_rerun, Mapping), "INVALID_SEED",
             "seed.no_rerun is required")
    validate_consumed_predecessor_identities(seed_no_rerun, "seed.no_rerun")
    predecessor = document.get("predecessor")
    _require(isinstance(predecessor, Mapping), "INVALID_SEED", "seed.predecessor is required")
    _require_exact(predecessor.get("checkpoint_sha256"), PREDECESSOR_CHECKPOINT_SHA256,
                   "seed.predecessor.checkpoint_sha256")
    _require_exact(predecessor.get("validated_raw_pages"), [1, 2, 3, 4],
                   "seed.predecessor.validated_raw_pages")
    projection = _projection_summary(document)
    expected = {
        "selector_algorithm": SELECTOR_ALGORITHM,
        "selector_sha256": TARGET_CUSTODY_SHA256,
        "eligible_projection_sha256": SEALED_SEED_PROJECTION_SHA256,
        "source_rows": SEED_SOURCE_ROWS,
        "eligible_rows": SEED_ELIGIBLE_ROWS,
        "excluded_rows": SEED_EXCLUDED_ROWS,
        "missing_rows": SEED_MISSING_ROWS,
        "excluded_global_row_ordinals": list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
        "selector_match_left_eligible": False,
    }
    for key, value in expected.items():
        _require_exact(projection.get(key), value, f"seed.projection.{key}")

    raw_rows = document.get("source_descriptors")
    if raw_rows is None:
        _require_exact(document.get("evidence_mode"), "SEALED_S2_S3_RECEIPT_REUSE",
                       "seed.evidence_mode")
        _require_exact(document.get("deterministic_recheck_at_live"), True,
                       "seed.deterministic_recheck_at_live")
        return "SEALED_RECEIPT_REUSE"

    _require(isinstance(raw_rows, list) and len(raw_rows) == SEED_SOURCE_ROWS,
             "INVALID_SEED", "source_descriptors must contain exactly 40 hash-only rows")
    state, _ = project_hashed_rows(
        (HashedSourceRow.from_document(row) for row in raw_rows),
        selector_policy=SEED_SELECTOR_POLICY,
    )
    _require_exact(state.source_rows, SEED_SOURCE_ROWS, "recomputed.source_rows")
    _require_exact(state.eligible_rows, SEED_ELIGIBLE_ROWS, "recomputed.eligible_rows")
    _require_exact(state.excluded_rows, SEED_EXCLUDED_ROWS, "recomputed.excluded_rows")
    _require_exact(state.missing_rows, SEED_MISSING_ROWS, "recomputed.missing_rows")
    _require_exact(state.excluded_global_row_ordinals,
                   list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
                   "recomputed.excluded_global_row_ordinals")
    _require_exact(state.eligible_projection_sha256, SEALED_SEED_PROJECTION_SHA256,
                   "recomputed.eligible_projection_sha256")
    return "RECOMPUTED_HASH_ONLY_SOURCE"


def _manifest_file_binding(
    manifest: Mapping[str, Any],
    role: str,
    path: Path,
    expected_filename: str | None = None,
) -> None:
    files = manifest.get("files")
    _require(isinstance(files, Mapping), "INVALID_MANIFEST", "manifest.files is required")
    binding = files.get(role)
    _require(isinstance(binding, Mapping), "INVALID_MANIFEST", f"manifest.files.{role} is required")
    expected_name = binding.get("filename")
    _require(isinstance(expected_name, str) and expected_name == path.name,
             "MANIFEST_FILENAME_MISMATCH", f"{role} filename does not match supplied path")
    if expected_filename is not None:
        _require_exact(expected_name, expected_filename, f"manifest.files.{role}.filename")
    _require_exact(sha256_file(path), binding.get("sha256"), f"manifest.files.{role}.sha256")
    _require_exact(git_blob_sha1_file(path), binding.get("git_blob"),
                   f"manifest.files.{role}.git_blob")


def validate_manifest_document(
    document: Mapping[str, Any],
    *,
    authority_path: Path,
    plan_path: Path,
    seed_path: Path,
    runner_path: Path,
    pytest_path: Path,
    live_adapter_path: Path | None = None,
    live_session_policy_path: Path | None = None,
) -> LiveAdapterBinding:
    artifact = document.get("artifact", document.get("schema"))
    _require_exact(artifact, MANIFEST_SCHEMA, "manifest.artifact")
    _require_exact(document.get("schema_version", 1), 1, "manifest.schema_version")
    _require_exact(document.get("generation_timestamp", GENERATION_TIMESTAMP),
                   GENERATION_TIMESTAMP, "manifest.generation_timestamp")
    _require_exact(document.get("authority_commit"), AUTHORITY_COMMIT,
                   "manifest.authority_commit")
    _require_exact(document.get("generation_id"), GENERATION_ID, "manifest.generation_id")
    sealed_scope = document.get("sealed_scope_summary")
    _require(isinstance(sealed_scope, Mapping), "INVALID_MANIFEST",
             "manifest.sealed_scope_summary is required")
    _require_exact(sealed_scope.get("owner_cap_spec_sha256"), OWNER_CAP_SPEC_SHA256,
                   "manifest.sealed_scope_summary.owner_cap_spec_sha256")
    _require_exact(sealed_scope.get("execution_token_sha256"), EXECUTION_TOKEN_SHA256,
                   "manifest.sealed_scope_summary.execution_token_sha256")
    _require_exact(sealed_scope.get("fixed_quota_day_kst"), QUOTA_DAY_KST,
                   "manifest.sealed_scope_summary.fixed_quota_day_kst")
    _require_exact(
        document.get("adapter_execution_order_binding"),
        expected_adapter_execution_order(),
        "manifest.adapter_execution_order_binding",
    )
    explicit_deferred = document.get("preparation_commit_binding")
    preparation = document.get("preparation_binding")
    if explicit_deferred is not None:
        _require_exact(explicit_deferred, "DEFERRED_TO_ACTIVATION",
                       "manifest.preparation_commit_binding")
    else:
        _require(isinstance(preparation, Mapping), "INVALID_MANIFEST",
                 "deferred preparation binding is required")
        _require_exact(preparation.get("preparation_commit"), "BOUND_BY_LATER_ACTIVATION",
                       "manifest.preparation_binding.preparation_commit")
        _require_exact(preparation.get("preparation_tree"), "BOUND_BY_LATER_ACTIVATION",
                       "manifest.preparation_binding.preparation_tree")

    owner = document.get("owner_decision_binding")
    if owner is not None:
        _require(isinstance(owner, Mapping), "INVALID_MANIFEST",
                 "manifest.owner_decision_binding must be an object")
        manifest_owner_expected = {
            "governing_forward_only_receipt_commit": GOVERNED_CORRECTION_HEAD,
            "governing_forward_only_receipt_tree": GOVERNED_CORRECTION_TREE,
            "governing_forward_only_receipt_git_blob": OWNER_DECISION_V1_1_GIT_BLOB,
            "governing_forward_only_receipt_sha256": OWNER_DECISION_V1_1_SHA256,
        }
        for key, value in manifest_owner_expected.items():
            _require_exact(owner.get(key), value, f"manifest.owner_decision_binding.{key}")
    _manifest_file_binding(document, "authority", authority_path, AUTHORITY_FILENAME)
    _manifest_file_binding(document, "plan", plan_path, PLAN_FILENAME)
    _manifest_file_binding(document, "seed", seed_path, SEED_FILENAME)
    _manifest_file_binding(document, "runner", runner_path)
    _manifest_file_binding(document, "tests", pytest_path)
    files_for_tests = document.get("files")
    _require(isinstance(files_for_tests, Mapping) and
             isinstance(files_for_tests.get("adapter_tests"), Mapping),
             "INVALID_MANIFEST", "manifest.files.adapter_tests is required")
    split_policy_roles = tuple(expected_split_session_policies())
    for policy_role in split_policy_roles:
        _require(isinstance(files_for_tests.get(policy_role), Mapping),
                 "INVALID_MANIFEST", f"manifest.files.{policy_role} is required")

    # Verify every additional manifest material that has a repository-relative
    # path.  The manifest itself is intentionally not self-hashed; activation
    # later binds the preparation commit/tree plus the manifest hash.
    repo_root = runner_path.resolve().parents[2]
    files = document.get("files")
    assert isinstance(files, Mapping)  # established by _manifest_file_binding
    for role, binding in files.items():
        _require(isinstance(binding, Mapping), "INVALID_MANIFEST",
                 f"manifest.files.{role} must be an object")
        repo_path = binding.get("path")
        if repo_path is None:
            continue
        _require(isinstance(repo_path, str) and repo_path and not Path(repo_path).is_absolute(),
                 "INVALID_MANIFEST_PATH", f"manifest.files.{role}.path is invalid")
        if role == "checkpoint_read_session_policy" and live_session_policy_path is not None:
            bound_path = live_session_policy_path.resolve()
        else:
            bound_path = (repo_root / repo_path).resolve()
            try:
                bound_path.relative_to(repo_root)
            except ValueError as exc:
                raise GateError("MANIFEST_PATH_ESCAPE", f"manifest.files.{role}.path escapes root") from exc
        _require(bound_path.is_file(), "MANIFEST_FILE_MISSING", f"{role}: {bound_path}")
        _require_exact(bound_path.name, binding.get("filename"),
                       f"manifest.files.{role}.filename")
        _require_exact(sha256_file(bound_path), binding.get("sha256"),
                       f"manifest.files.{role}.sha256")
        _require_exact(git_blob_sha1_file(bound_path), binding.get("git_blob"),
                       f"manifest.files.{role}.git_blob")

    for policy_role in split_policy_roles:
        live_policy_binding = files.get(policy_role)
        assert isinstance(live_policy_binding, Mapping)
        live_policy_repo_path = live_policy_binding.get("path")
        _require(isinstance(live_policy_repo_path, str) and live_policy_repo_path,
                 "INVALID_MANIFEST_PATH", f"manifest.files.{policy_role}.path")
        resolved_live_policy = (
            live_session_policy_path.resolve()
            if policy_role == "checkpoint_read_session_policy"
            and live_session_policy_path is not None
            else (repo_root / live_policy_repo_path).resolve()
        )
        validate_live_session_policy_for_aws(resolved_live_policy, policy_role)

    return validate_live_adapter_manifest(
        document,
        repo_root=repo_root,
        supplied_path=live_adapter_path,
    )


def validate_bundle(
    *,
    authority_path: Path,
    plan_path: Path,
    seed_path: Path,
    manifest_path: Path,
    pytest_path: Path,
    live_adapter_path: Path | None = None,
    live_session_policy_path: Path | None = None,
) -> dict[str, Any]:
    _require_exact(authority_path.name, AUTHORITY_FILENAME, "authority filename")
    _require_exact(plan_path.name, PLAN_FILENAME, "plan filename")
    _require_exact(seed_path.name, SEED_FILENAME, "seed filename")
    _require_exact(manifest_path.name, MANIFEST_FILENAME, "manifest filename")

    authority = load_json_document(authority_path)
    plan = load_json_document(plan_path)
    seed = load_json_document(seed_path)
    manifest = load_json_document(manifest_path)
    validate_authority_document(authority)
    validate_plan_document(plan)
    validate_plan_seed_material_binding(plan, seed_path)
    seed_validation = validate_seed_document(seed)
    adapter_binding = validate_manifest_document(
        manifest,
        authority_path=authority_path,
        plan_path=plan_path,
        seed_path=seed_path,
        runner_path=Path(__file__).resolve(),
        pytest_path=pytest_path,
        live_adapter_path=live_adapter_path,
        live_session_policy_path=live_session_policy_path,
    )
    authority_adapter = authority.get("safe_executable_adapter")
    manifest_adapter = manifest.get("safe_executable_adapter")
    _require(isinstance(authority_adapter, Mapping), "INVALID_AUTHORITY",
             "authority.safe_executable_adapter is required")
    _require_exact(authority_adapter, manifest_adapter,
                   "authority.safe_executable_adapter")
    authority_entry_gate = authority.get("entry_gate")
    _require(isinstance(authority_entry_gate, Mapping), "INVALID_AUTHORITY",
             "authority.entry_gate is required")
    _require_exact(authority_entry_gate.get("live_adapter_gate"), LIVE_ADAPTER_GATE_READY,
                   "authority.entry_gate.live_adapter_gate")
    return {
        "generation_timestamp": GENERATION_TIMESTAMP,
        "generation_id": GENERATION_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "governed_correction_head": GOVERNED_CORRECTION_HEAD,
        "governed_correction_tree": GOVERNED_CORRECTION_TREE,
        "owner_decision_v1_1_git_blob": OWNER_DECISION_V1_1_GIT_BLOB,
        "owner_decision_v1_1_sha256": OWNER_DECISION_V1_1_SHA256,
        "seed_validation": seed_validation,
        "first_new_page": FIRST_NEW_PAGE,
        "inherited_g10_acquisitions": INHERITED_G10_ACQUISITIONS,
        "remaining_g11_acquisitions": G11_ACQUISITION_CEILING,
        "inherited_g10_attempts": INHERITED_G10_ATTEMPTS,
        "remaining_g11_attempts": G11_ATTEMPT_CEILING,
        "live_adapter_gate": LIVE_ADAPTER_GATE_READY,
        "live_session_policy_ascii_and_size_ceiling_verified": True,
        "live_adapter": {
            "path": adapter_binding.repo_path,
            "sha256": adapter_binding.sha256,
            "git_blob": adapter_binding.git_blob,
            "factory_symbol": adapter_binding.factory_symbol,
            "interface_version": adapter_binding.interface_version,
        },
    }


def _run_stdlib_test(test_path: Path, role: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(test_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise GateError("FOCUSED_TESTS_FAILED", f"{role}: {completed.stdout[-3500:]}")
    return {
        "status": "PASS",
        "role": role,
        "test_file": test_path.name,
        "test_sha256": sha256_file(test_path),
        "test_runtime": "PYTHON_STDLIB_SELF_CONTAINED",
        "output_tail": completed.stdout[-1000:],
    }


def run_focused_tests(pytest_path: Path, adapter_test_path: Path) -> dict[str, Any]:
    """Run both sealed stdlib suites; no network package installation is allowed."""

    core = _run_stdlib_test(pytest_path, "SELECTOR_SUCCESSOR_CORE")
    adapter = _run_stdlib_test(adapter_test_path, "SEALED_LIVE_ADAPTER")
    return {
        "status": "PASS",
        "pytest_file": pytest_path.name,
        "pytest_sha256": sha256_file(pytest_path),
        "adapter_test_file": adapter_test_path.name,
        "adapter_test_sha256": sha256_file(adapter_test_path),
        "test_runtime": "PYTHON_STDLIB_SELF_CONTAINED",
        "core": core,
        "adapter": adapter,
    }


def _resolve_manifest_role_path(
    manifest_path: Path,
    role: str,
    *,
    supplied_path: Path | None = None,
) -> Path:
    manifest = load_json_document(manifest_path)
    files = manifest.get("files")
    binding = files.get(role) if isinstance(files, Mapping) else None
    _require(isinstance(binding, Mapping), "INVALID_MANIFEST",
             f"manifest.files.{role} is required")
    repo_path = binding.get("path")
    _require(isinstance(repo_path, str) and repo_path and not Path(repo_path).is_absolute(),
             "INVALID_MANIFEST_PATH", f"manifest.files.{role}.path")
    repo_root = Path(__file__).resolve().parents[2]
    resolved = (repo_root / repo_path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise GateError("MANIFEST_PATH_ESCAPE", repo_path) from exc
    _require(resolved.is_file(), "MANIFEST_FILE_MISSING", f"{role}: {resolved}")
    if supplied_path is not None:
        _require_exact(supplied_path.resolve(), resolved, f"supplied {role} path")
    _require_exact(sha256_file(resolved), binding.get("sha256"),
                   f"manifest.files.{role}.sha256")
    _require_exact(git_blob_sha1_file(resolved), binding.get("git_blob"),
                   f"manifest.files.{role}.git_blob")
    return resolved


def _validate_zero_precheck_receipt(receipt: Mapping[str, Any]) -> str:
    artifact = str(receipt.get("artifact") or "")
    match = re.fullmatch(
        r"M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_"
        r"PRECHECK_TERMINAL_RECEIPT_([0-9]+)_v1\.0",
        artifact,
    )
    _require(match is not None, "PRECHECK_RECEIPT_ARTIFACT_MISMATCH", artifact)
    run_id = match.group(1)
    _require_exact(receipt.get("result"), "PASS", "precheck receipt result")
    _require_exact(
        receipt.get("terminal_state"),
        "TERMINAL_PASS_FOCUSED_G11C6_PRECHECK_EXACT_3_OIDC_STS_POLICY_PACKING_"
        "PROBES_SUCCESS_ZERO_DOWNSTREAM_MUTATION_LIVE_NOT_AUTHORIZED",
        "precheck receipt terminal_state",
    )
    for key, value in {
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "act_id": PRECHECK_ACT_ID,
        "github_run_attempt": 1,
    }.items():
        _require_exact(receipt.get(key), value, f"precheck receipt {key}")
    execution = receipt.get("execution_binding")
    _require(isinstance(execution, Mapping), "INVALID_PRECHECK_RECEIPT",
             "execution_binding is required")
    _require_exact(str(execution.get("run_id")), run_id, "precheck execution run_id")
    _require_exact(execution.get("run_attempt"), 1, "precheck execution run_attempt")
    _require_exact(execution.get("forced"), False, "precheck execution forced")
    runner_result = receipt.get("runner_result")
    live_gate = receipt.get("live_adapter_gate")
    terminal = receipt.get("terminal")
    _require(isinstance(runner_result, Mapping) and isinstance(live_gate, Mapping) and
             isinstance(terminal, Mapping), "INVALID_PRECHECK_RECEIPT",
             "runner_result, live_adapter_gate, and terminal are required")
    _require_exact(runner_result.get("verdict"), "PASS", "precheck runner verdict")
    _require_exact(runner_result.get("entry_gate"), "FOCUSED_PRECHECK_PASS",
                   "precheck runner entry_gate")
    _require_exact(runner_result.get("live_adapter_gate"), LIVE_ADAPTER_GATE_READY,
                   "precheck runner live_adapter_gate")
    _require_exact(runner_result.get("sts_policy_probe_count"), STS_POLICY_PROBE_COUNT,
                   "precheck runner sts_policy_probe_count")
    _require_exact(runner_result.get("effects"), PRECHECK_STS_PROBE_EFFECTS,
                   "precheck runner effects")
    runner_observations = runner_result.get("observations")
    _require(isinstance(runner_observations, Mapping), "INVALID_PRECHECK_RECEIPT",
             "runner_result.observations is required")
    _require_exact(runner_observations.get("future_selector_policy"), FUTURE_SELECTOR_POLICY,
                   "precheck runner observations.future_selector_policy")
    _require_exact(runner_observations.get("sealed_exclusion_scope"),
                   list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
                   "precheck runner observations.sealed_exclusion_scope")
    _require_exact(runner_observations.get("required_no_rerun_runs"),
                   list(REQUIRED_NO_RERUN_RUNS),
                   "precheck runner observations.required_no_rerun_runs")
    _require_exact(runner_observations.get("live_pre_mutation_order"),
                   list(LIVE_PRE_MUTATION_PHASES),
                   "precheck runner observations.live_pre_mutation_order")
    _require_exact(
        runner_observations.get("active_prefix_rejection_regressions"),
        ["G11", "G11C1", "G11C2", "G11C3", "G11C4", "G11C5"],
        "precheck runner observations.active_prefix_rejection_regressions",
    )
    _require_exact(
        runner_observations.get("sts_policy_probe_count"),
        STS_POLICY_PROBE_COUNT,
        "precheck runner observations.sts_policy_probe_count",
    )
    _require_exact(
        runner_observations.get("sts_policy_probe_count_verified"),
        STS_POLICY_PROBE_COUNT,
        "precheck runner observations.sts_policy_probe_count_verified",
    )
    _require_exact(
        runner_observations.get("sts_policy_probe_roles"),
        [item["role"] for item in OIDC_STS_POLICY_PACKING_PROBES],
        "precheck runner observations.sts_policy_probe_roles",
    )
    _require_exact(
        runner_observations.get("oidc_sts_policy_packing_probes"),
        [dict(item) for item in OIDC_STS_POLICY_PACKING_PROBES],
        "precheck runner observations.oidc_sts_policy_packing_probes",
    )
    _require_exact(
        runner_observations.get("live_session_policy_ascii_and_size_ceiling_verified"),
        True,
        "precheck runner observations.live_session_policy_ascii_and_size_ceiling_verified",
    )
    _require_exact(live_gate.get("runner_reported_readiness"), LIVE_ADAPTER_GATE_READY,
                   "precheck live adapter readiness")
    _require_exact(terminal.get("result"), "PASS", "precheck terminal result")
    _require_exact(terminal.get("live_authorized"), False,
                   "precheck must not self-authorize LIVE")

    observed = receipt.get("observed_effects")
    _require(isinstance(observed, Mapping), "INVALID_PRECHECK_RECEIPT",
             "observed_effects is required")
    _require_exact(observed.get("effects_reconciled"), True,
                   "precheck observed effects_reconciled")
    _require_exact(observed.get("ambiguous_side_effects"), False,
                   "precheck observed ambiguous_side_effects")
    for key in (
        "aws_calls", "sts_calls", "sts_assume_role_attempts",
        "sts_sessions_assumed", "sts_get_caller_identity_calls",
        "credentials_issued",
    ):
        _require_exact(observed.get(key), PRECHECK_STS_PROBE_EFFECTS[key],
                       f"precheck observed_effects.{key}")
    for key in (
        "s3_calls", "provider_calls", "finance_provider_api_calls",
        "quota_reservations", "provider_quota_reservations", "raw_writes",
        "s3_put_delete_copy", "repository_mutations_by_workflow",
        "remote_custody_mutations", "normalization_actions", "pit_actions",
        "promotion_actions", "release_actions", "production_actions",
    ):
        _require_exact(observed.get(key), 0, f"precheck observed_effects.{key}")
    reconciled = receipt.get("effect_reconciliation")
    _require(isinstance(reconciled, Mapping), "INVALID_PRECHECK_RECEIPT",
             "effect_reconciliation is required")
    for key in (
        "aws_calls", "sts_calls", "sts_assume_role_attempts",
        "sts_sessions_assumed", "sts_get_caller_identity_calls",
        "credentials_issued",
    ):
        _require_exact(reconciled.get(key), PRECHECK_STS_PROBE_EFFECTS[key],
                       f"precheck effect_reconciliation.{key}")
    for key in (
        "provider_calls", "quota_reservations", "raw_writes", "s3_put_delete_copy",
        "repository_mutations_by_workflow", "remote_custody_mutations", "s3_calls",
    ):
        _require_exact(reconciled.get(key), 0, f"precheck effect_reconciliation.{key}")
    _require_exact(reconciled.get("all_mutation_effects_zero"), True,
                   "precheck all_mutation_effects_zero")
    _require_exact(reconciled.get("effects_reconciled"), True,
                   "precheck effects_reconciled")
    _require_exact(reconciled.get("ambiguous_side_effects"), False,
                   "precheck ambiguous_side_effects")
    return run_id


def validate_runtime_live_head_binding(
    activation: Mapping[str, Any],
    *,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Resolve non-self-referential activation markers from GitHub runtime facts."""

    activation_binding = activation.get("activation_binding")
    _require(isinstance(activation_binding, Mapping), "INVALID_LIVE_ACTIVATION",
             "activation_binding is required")
    _require_exact(activation_binding.get("live_activation_commit"), LIVE_HEAD_MARKER,
                   "live activation commit marker")
    _require_exact(activation_binding.get("live_activation_tree"), LIVE_TREE_MARKER,
                   "live activation tree marker")
    _require_exact(activation_binding.get("expected_branch_head_at_dispatch"),
                   LIVE_HEAD_MARKER, "live expected branch head marker")
    env = os.environ if environment is None else environment
    head_sha = env.get("G11C6_LIVE_HEAD_SHA", "")
    tree_sha = env.get("G11C6_LIVE_HEAD_TREE", "")
    _require(isinstance(head_sha, str) and HEX40.fullmatch(head_sha) is not None,
             "LIVE_RUNTIME_HEAD_INVALID", "G11C6_LIVE_HEAD_SHA")
    _require(isinstance(tree_sha, str) and HEX40.fullmatch(tree_sha) is not None,
             "LIVE_RUNTIME_TREE_INVALID", "G11C6_LIVE_HEAD_TREE")
    _require_exact(env.get("GITHUB_SHA"), head_sha, "GITHUB_SHA/G11C6_LIVE_HEAD_SHA")
    run_id = env.get("GITHUB_RUN_ID", "")
    run_attempt = env.get("GITHUB_RUN_ATTEMPT", "")
    _require(isinstance(run_id, str) and run_id.isdigit(),
             "GITHUB_RUNTIME_IDENTITY_MISSING", "GITHUB_RUN_ID")
    _require_exact(run_attempt, "1", "GITHUB_RUN_ATTEMPT")
    return {
        "repository": REPOSITORY,
        "branch": BRANCH,
        "github_run_id": int(run_id),
        "github_run_attempt": 1,
        "head_sha": head_sha,
        "tree_sha": tree_sha,
    }


def validate_precheck_pass_role_binding(
    binding: Mapping[str, Any], receipt: Mapping[str, Any],
) -> None:
    """Keep durable receipt-append lineage distinct from PRECHECK execution lineage."""

    execution = receipt.get("execution_binding")
    _require(isinstance(execution, Mapping), "INVALID_PRECHECK_RECEIPT",
             "execution_binding is required")
    expected_execution_head = execution.get("head_sha")
    expected_execution_tree = execution.get("tree_sha")
    _require(isinstance(expected_execution_head, str) and
             HEX40.fullmatch(expected_execution_head) is not None,
             "PRECHECK_EXECUTION_HEAD_INVALID", "execution_binding.head_sha")
    _require(isinstance(expected_execution_tree, str) and
             HEX40.fullmatch(expected_execution_tree) is not None,
             "PRECHECK_EXECUTION_TREE_INVALID", "execution_binding.tree_sha")
    receipt_append_commit = binding.get("receipt_append_commit")
    receipt_append_tree = binding.get("receipt_append_tree")
    _require(isinstance(receipt_append_commit, str) and
             HEX40.fullmatch(receipt_append_commit) is not None,
             "PRECHECK_RECEIPT_APPEND_COMMIT_INVALID", "receipt_append_commit")
    _require(isinstance(receipt_append_tree, str) and
             HEX40.fullmatch(receipt_append_tree) is not None,
             "PRECHECK_RECEIPT_APPEND_TREE_INVALID", "receipt_append_tree")
    _require_exact(binding.get("execution_head_sha"), expected_execution_head,
                   "precheck_pass_binding.execution_head_sha")
    _require_exact(binding.get("execution_head_tree_sha"), expected_execution_tree,
                   "precheck_pass_binding.execution_head_tree_sha")
    _require(
        (receipt_append_commit, receipt_append_tree) !=
        (expected_execution_head, expected_execution_tree),
        "PRECHECK_LINEAGE_ROLES_COLLAPSED",
        "receipt append and internal execution lineages must remain distinct",
    )
    _require("commit" not in binding and "tree" not in binding,
             "AMBIGUOUS_PRECHECK_LINEAGE_FIELDS_FORBIDDEN",
             "legacy commit/tree fields collapse distinct PRECHECK roles")


def validate_live_activation_and_receipt(
    *,
    activation_path: Path,
    precheck_receipt_path: Path,
    authority_path: Path,
    plan_path: Path,
    seed_path: Path,
    manifest_path: Path,
    owner_decision_path: Path,
    adapter_binding: Mapping[str, Any],
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Runner-side focused gate performed before importing executable adapter code."""

    receipt_raw = precheck_receipt_path.read_bytes()
    receipt = load_json_document(precheck_receipt_path)
    run_id = _validate_zero_precheck_receipt(receipt)
    activation = load_json_document(activation_path)
    _require_exact(activation.get("artifact"),
                   "M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_LIVE_ACTIVATION_v1.0",
                   "live activation artifact")
    _require_exact(activation.get("mode"), "LIVE", "live activation mode")
    _require_exact(activation.get("armed"), True, "live activation armed")
    _require_exact(activation.get("repository"), REPOSITORY, "live activation repository")
    _require_exact(activation.get("branch"), BRANCH, "live activation branch")
    runtime_execution = validate_runtime_live_head_binding(
        activation, environment=environment
    )
    identity = activation.get("identity")
    _require(isinstance(identity, Mapping), "INVALID_LIVE_ACTIVATION", "identity is required")
    for key, value in {
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
    }.items():
        _require_exact(identity.get(key), value, f"live activation identity.{key}")
    _require_exact(activation.get("live_adapter_gate"), LIVE_ADAPTER_GATE_READY,
                   "live activation live_adapter_gate")
    _require_exact(activation.get("safe_executable_adapter"), adapter_binding,
                   "live activation safe_executable_adapter")

    precheck = activation.get("precheck_pass_binding")
    _require(isinstance(precheck, Mapping), "INVALID_LIVE_ACTIVATION",
             "precheck_pass_binding is required")
    _require_exact(precheck.get("required"), True, "live activation precheck required")
    _require_exact(precheck.get("result"), "PASS", "live activation precheck result")
    _require_exact(precheck.get("live_adapter_gate"), LIVE_ADAPTER_GATE_READY,
                   "live activation precheck live_adapter_gate")
    _require_exact(precheck.get("github_run_attempt"), 1,
                   "live activation precheck github_run_attempt")
    _require_exact(str(precheck.get("github_run_id")), run_id,
                   "live activation precheck github_run_id")
    _require_exact(precheck.get("sha256"), sha256_bytes(receipt_raw),
                   "live activation precheck sha256")
    _require_exact(precheck.get("git_blob"), git_blob_sha1_file(precheck_receipt_path),
                   "live activation precheck git_blob")
    validate_precheck_pass_role_binding(precheck, receipt)
    if precheck.get("bytes") is not None:
        _require_exact(precheck.get("bytes"), len(receipt_raw),
                       "live activation precheck bytes")
    bound_path = str(precheck.get("path") or "")
    _require(bool(bound_path) and precheck_receipt_path.as_posix().endswith(bound_path),
             "LIVE_PRECHECK_PATH_MISMATCH", bound_path)

    material = activation.get("material_bindings")
    _require(isinstance(material, Mapping), "INVALID_LIVE_ACTIVATION",
             "material_bindings is required")
    material_paths = {
        "authority": authority_path,
        "plan": plan_path,
        "checkpoint_seed": seed_path,
        "manifest": manifest_path,
        "owner_decision_v1_1": owner_decision_path,
    }
    for role, path in material_paths.items():
        _require_exact(material.get(f"{role}_sha256"), sha256_file(path),
                       f"live activation material_bindings.{role}_sha256")
        if material.get(f"{role}_git_blob") is not None:
            _require_exact(material.get(f"{role}_git_blob"), git_blob_sha1_file(path),
                           f"live activation material_bindings.{role}_git_blob")

    owner_raw = owner_decision_path.read_bytes()
    _require_exact(sha256_bytes(owner_raw), OWNER_DECISION_V1_1_SHA256,
                   "owner decision v1.1 sha256")
    _require_exact(git_blob_sha1_file(owner_decision_path), OWNER_DECISION_V1_1_GIT_BLOB,
                   "owner decision v1.1 git_blob")
    owner = load_json_document(owner_decision_path)
    _require_exact(owner.get("artifact"),
                   "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1",
                   "owner decision v1.1 artifact")
    _require_exact(owner.get("correction_id"), "OA-F01", "owner decision correction_id")

    bounds = activation.get("effect_bounds")
    _require(isinstance(bounds, Mapping), "INVALID_LIVE_ACTIVATION", "effect_bounds required")
    for key, value in {
        "aggregate_max_primary_page_acquisitions": EFFECTIVE_ACQUISITION_CEILING,
        "aggregate_max_network_attempts_total": EFFECTIVE_ATTEMPT_CEILING,
        "g10_spent_primary_acquisitions": INHERITED_G10_ACQUISITIONS,
        "g10_spent_network_attempts": INHERITED_G10_ATTEMPTS,
        "maximum_new_g11_primary_page_acquisitions": G11_ACQUISITION_CEILING,
        "maximum_new_g11_network_attempts": G11_ATTEMPT_CEILING,
        "max_attempts_per_logical_page": ATTEMPTS_PER_PAGE_CEILING,
        "ordered_primary_dates_sha256": PRIMARY_DATES_SHA256,
    }.items():
        _require_exact(bounds.get(key), value, f"live activation effect_bounds.{key}")
    no_rerun = activation.get("no_rerun")
    _require(isinstance(no_rerun, Mapping), "INVALID_LIVE_ACTIVATION", "no_rerun required")
    _require_exact(no_rerun.get("github_run_attempt_required"), 1,
                   "live activation no_rerun.github_run_attempt_required")
    for key in ("same_run_retry_authorized", "same_activation_reuse_authorized", "same_latch_reuse_authorized"):
        _require_exact(no_rerun.get(key), False, f"live activation no_rerun.{key}")
    validate_consumed_predecessor_identities(no_rerun, "live activation no_rerun")
    return {
        "precheck_run_id": run_id,
        "precheck_sha256": sha256_bytes(receipt_raw),
        "execution_binding": runtime_execution,
    }


def _normalize_and_validate_live_result(
    result: Mapping[str, Any], return_code: int,
    *,
    expected_execution_binding: Mapping[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    output = dict(result)
    effects_value = output.get("effects")
    _require(isinstance(effects_value, Mapping), "LIVE_ADAPTER_RESULT_INVALID", "effects absent")
    effects = dict(effects_value)
    effects.setdefault("s3_other_calls", 0)
    output["effects"] = effects
    _require_exact(output.get("schema"),
                   "M3TOP3_FINANCE_CA_PAGE100_G11C6_LIVE_ENTRY_RESULT_v1.0",
                   "live adapter result schema")
    _require(output.get("verdict") in {"PASS", "FAIL_CLOSED"},
             "LIVE_ADAPTER_RESULT_INVALID", "verdict")
    _require_exact(return_code == 0, output.get("verdict") == "PASS",
                   "live adapter result/exit_code consistency")

    integer_keys = (
        "primary_acquisitions", "network_attempts", "provider_calls", "quota_reservations",
        "raw_writes", "checkpoint_writes", "execution_claim_writes", "terminal_receipt_writes",
        "terminal_receipt_put_attempts",
        "s3_get_calls", "s3_put_calls", "s3_delete_calls", "s3_copy_calls",
        "s3_tagging_mutation_calls", "s3_other_calls", "company_master_mutations",
        "universe_mutations", "company_master_or_universe_mutations", "repository_writes",
        "repository_mutations_by_workflow", "github_actions_artifacts_uploaded",
        "normalization_actions", "pit_actions", "promotion_actions", "release_actions",
        "production_actions", "finance_provider_api_calls", "provider_quota_reservations",
        "raw_objects_written", "quota_ledger_appends", "raw_index_appends", "aws_calls",
        "sts_calls", "sts_assume_role_attempts", "sts_sessions_assumed",
        "sts_get_caller_identity_calls", "credentials_issued",
        "s3_calls", "remote_custody_mutations", "effective_primary_acquisitions",
        "effective_network_attempts", "s3_get_attempts", "s3_put_attempts",
        "s3_other_read_calls", "successful_put_mutations",
        "unconfirmed_or_failed_put_attempts",
    )
    for key in integer_keys:
        _require(type(effects.get(key)) is int and effects[key] >= 0,
                 "LIVE_EFFECT_LEDGER_INVALID", key)
    _require(type(effects.get("ambiguous_side_effects")) is bool and
             type(effects.get("effects_reconciled")) is bool,
             "LIVE_EFFECT_LEDGER_INVALID", "reconciliation flags")
    _require(effects["primary_acquisitions"] <= G11_ACQUISITION_CEILING,
             "LIVE_EFFECT_BOUND_EXCEEDED", "primary_acquisitions")
    _require(effects["network_attempts"] <= G11_ATTEMPT_CEILING,
             "LIVE_EFFECT_BOUND_EXCEEDED", "network_attempts")
    _require(effects["primary_acquisitions"] <= effects["network_attempts"] <=
             2 * effects["primary_acquisitions"],
             "LIVE_EFFECT_BOUND_EXCEEDED", "acquisition/attempt relationship")
    _require(effects["provider_calls"] <= effects["network_attempts"] <= G11_ATTEMPT_CEILING,
             "LIVE_EFFECT_BOUND_EXCEEDED", "provider_calls/network_attempts")
    _require_exact(effects["quota_reservations"], effects["network_attempts"],
                   "effects.quota_reservations")
    _require(effects["raw_writes"] <= effects["provider_calls"] and
             effects["raw_writes"] <= G11_ACQUISITION_CEILING,
             "LIVE_EFFECT_BOUND_EXCEEDED", "raw_writes")
    _require(effects["checkpoint_writes"] <= 8003 and
             effects["checkpoint_writes"] <= effects["network_attempts"] * 4 + 19,
             "LIVE_EFFECT_BOUND_EXCEEDED", "checkpoint_writes")
    _require(effects["execution_claim_writes"] <= 1 and
             effects["terminal_receipt_writes"] <= 1,
             "LIVE_EFFECT_BOUND_EXCEEDED", "singleton writes")
    _require(0 <= effects["terminal_receipt_writes"] <=
             effects["terminal_receipt_put_attempts"] <= 1,
             "LIVE_EFFECT_BOUND_EXCEEDED", "terminal receipt attempt/write")
    _require_exact(effects["finance_provider_api_calls"], effects["provider_calls"],
                   "effects.finance_provider_api_calls")
    _require_exact(effects["provider_quota_reservations"], effects["quota_reservations"],
                   "effects.provider_quota_reservations")
    _require_exact(effects["raw_objects_written"], effects["raw_writes"],
                   "effects.raw_objects_written")
    _require_exact(effects["raw_index_appends"], effects["raw_writes"],
                   "effects.raw_index_appends")
    _require_exact(effects["quota_ledger_appends"], 0, "effects.quota_ledger_appends")
    confirmed_mutations = (
        effects["raw_writes"] + effects["checkpoint_writes"] +
        effects["execution_claim_writes"] + effects["terminal_receipt_writes"]
    )
    _require_exact(effects["remote_custody_mutations"], confirmed_mutations,
                   "effects.remote_custody_mutations")
    _require(confirmed_mutations <= effects["s3_put_calls"],
             "LIVE_EFFECT_LEDGER_INVALID", "confirmed mutations exceed PUT attempts")
    _require_exact(effects["s3_get_attempts"], effects["s3_get_calls"],
                   "effects.s3_get_attempts")
    _require_exact(effects["s3_put_attempts"], effects["s3_put_calls"],
                   "effects.s3_put_attempts")
    _require_exact(effects["s3_other_read_calls"], effects["s3_other_calls"],
                   "effects.s3_other_read_calls")
    _require_exact(effects["successful_put_mutations"], confirmed_mutations,
                   "effects.successful_put_mutations")
    _require_exact(effects["unconfirmed_or_failed_put_attempts"],
                   effects["s3_put_calls"] - confirmed_mutations,
                   "effects.unconfirmed_or_failed_put_attempts")
    for key in (
        "s3_delete_calls", "s3_copy_calls", "s3_tagging_mutation_calls",
        "company_master_mutations", "universe_mutations", "company_master_or_universe_mutations",
        "repository_writes", "repository_mutations_by_workflow", "github_actions_artifacts_uploaded",
        "normalization_actions", "pit_actions", "promotion_actions", "release_actions",
        "production_actions",
    ):
        _require_exact(effects[key], 0, f"effects.{key}")
    _require_exact(effects["sts_calls"], PRECHECK_STS_PROBE_EFFECTS["sts_calls"],
                   "effects.sts_calls")
    _require_exact(effects["sts_assume_role_attempts"],
                   PRECHECK_STS_PROBE_EFFECTS["sts_assume_role_attempts"],
                   "effects.sts_assume_role_attempts")
    _require_exact(effects["sts_sessions_assumed"],
                   PRECHECK_STS_PROBE_EFFECTS["sts_sessions_assumed"],
                   "effects.sts_sessions_assumed")
    _require_exact(effects["sts_get_caller_identity_calls"],
                   PRECHECK_STS_PROBE_EFFECTS["sts_get_caller_identity_calls"],
                   "effects.sts_get_caller_identity_calls")
    _require_exact(effects["credentials_issued"],
                   PRECHECK_STS_PROBE_EFFECTS["credentials_issued"],
                   "effects.credentials_issued")
    _require_exact(effects["s3_calls"],
                   effects["s3_get_calls"] + effects["s3_put_calls"] + effects["s3_other_calls"],
                   "effects.s3_calls")
    _require_exact(effects["aws_calls"], effects["sts_calls"] + effects["s3_calls"],
                   "effects.aws_calls")
    _require(effects["s3_other_calls"] <= 3,
             "LIVE_EFFECT_BOUND_EXCEEDED", "s3_other_calls")
    _require_exact(effects["effective_primary_acquisitions"],
                   INHERITED_G10_ACQUISITIONS + effects["primary_acquisitions"],
                   "effects.effective_primary_acquisitions")
    _require_exact(effects["effective_network_attempts"],
                   INHERITED_G10_ATTEMPTS + effects["network_attempts"],
                   "effects.effective_network_attempts")
    _require_exact(effects["effects_reconciled"], not effects["ambiguous_side_effects"],
                   "effects.effects_reconciled")
    reconciliation = output.get("effect_reconciliation")
    _require(isinstance(reconciliation, Mapping), "LIVE_ADAPTER_RESULT_INVALID",
             "effect_reconciliation")
    _require_exact(reconciliation.get("complete"), effects["effects_reconciled"],
                   "effect_reconciliation.complete")
    _require_exact(reconciliation.get("ambiguous_side_effects"),
                   effects["ambiguous_side_effects"],
                   "effect_reconciliation.ambiguous_side_effects")
    entry_gate = output.get("entry_gate")
    _require(entry_gate in {"LIVE_NOT_ENTERED", "LIVE_ENTERED_ONCE"},
             "LIVE_ADAPTER_RESULT_INVALID", "entry_gate")
    if entry_gate == "LIVE_ENTERED_ONCE":
        _require_exact(effects["execution_claim_writes"], 1,
                       "entered effects.execution_claim_writes")
        _require_exact(effects["s3_other_calls"], 3, "entered effects.s3_other_calls")
        _require(effects["s3_get_calls"] >= 5,
                 "LIVE_EFFECT_LEDGER_INVALID", "entered exact predecessor reads")
    else:
        for key in (
            "execution_claim_writes", "provider_calls", "quota_reservations", "raw_writes",
            "checkpoint_writes", "terminal_receipt_writes", "terminal_receipt_put_attempts",
            "remote_custody_mutations",
        ):
            _require_exact(effects[key], 0, f"not-entered effects.{key}")
    if expected_execution_binding is not None:
        execution = output.get("execution_binding")
        _require(isinstance(execution, Mapping), "LIVE_ADAPTER_RESULT_INVALID",
                 "execution_binding")
        for key in (
            "repository", "branch", "github_run_id", "github_run_attempt", "head_sha", "tree_sha",
        ):
            _require_exact(execution.get(key), expected_execution_binding.get(key),
                           f"live result execution_binding.{key}")
        _require(execution.get("head_sha") not in {LIVE_HEAD_MARKER, LIVE_TREE_MARKER} and
                 execution.get("tree_sha") not in {LIVE_HEAD_MARKER, LIVE_TREE_MARKER},
                 "LIVE_ADAPTER_RESULT_INVALID", "execution binding contains activation marker")

    def validate_object_binding(value: Any, label: str) -> Mapping[str, Any]:
        _require(isinstance(value, Mapping), "LIVE_CUSTODY_BINDING_INVALID", label)
        _require(isinstance(value.get("key"), str) and bool(value.get("key")),
                 "LIVE_CUSTODY_BINDING_INVALID", f"{label}.key")
        _require(isinstance(value.get("version_id"), str) and bool(value.get("version_id")),
                 "LIVE_CUSTODY_BINDING_INVALID", f"{label}.version_id")
        _require(isinstance(value.get("etag"), str) and bool(value.get("etag")),
                 "LIVE_CUSTODY_BINDING_INVALID", f"{label}.etag")
        _require_hex64(value.get("sha256"), f"{label}.sha256")
        _require(type(value.get("bytes")) is int and value["bytes"] > 0,
                 "LIVE_CUSTODY_BINDING_INVALID", f"{label}.bytes")
        _require(value.get("content_type") in {"application/json", "application/octet-stream"},
                 "LIVE_CUSTODY_BINDING_INVALID", f"{label}.content_type")
        _require_exact(value.get("server_side_encryption"), "AES256",
                       f"{label}.server_side_encryption")
        return value

    claim_binding = output.get("execution_claim_binding")
    checkpoint_binding = output.get("checkpoint_binding")
    terminal_binding = output.get("terminal_receipt_binding")
    _require(isinstance(terminal_binding, Mapping), "LIVE_CUSTODY_BINDING_INVALID",
             "terminal_receipt_binding")
    _require(type(terminal_binding.get("attempted")) is bool and
             type(terminal_binding.get("confirmed")) is bool and
             type(terminal_binding.get("put_attempts")) is int,
             "LIVE_CUSTODY_BINDING_INVALID", "terminal_receipt_binding fields")
    _require_exact(terminal_binding.get("put_attempts"),
                   effects["terminal_receipt_put_attempts"],
                   "terminal_receipt_binding.put_attempts")
    _require_exact(int(terminal_binding.get("confirmed")),
                   effects["terminal_receipt_writes"],
                   "terminal_receipt_binding.confirmed/write count")
    terminal_object = terminal_binding.get("object")
    if terminal_object is not None:
        validate_object_binding(terminal_object, "terminal_receipt_binding.object")
    if entry_gate == "LIVE_NOT_ENTERED":
        _require_exact(claim_binding, None, "not-entered execution_claim_binding")
        _require_exact(checkpoint_binding, None, "not-entered checkpoint_binding")
        _require_exact(terminal_binding.get("attempted"), False,
                       "not-entered terminal_receipt_binding.attempted")
        _require_exact(terminal_binding.get("put_attempts"), 0,
                       "not-entered terminal_receipt_binding.put_attempts")
        _require_exact(terminal_binding.get("confirmed"), False,
                       "not-entered terminal_receipt_binding.confirmed")
        _require_exact(terminal_object, None, "not-entered terminal receipt object")
    else:
        validate_object_binding(claim_binding, "execution_claim_binding")
        validate_object_binding(checkpoint_binding, "checkpoint_binding")
    if output.get("verdict") == "PASS":
        _require_exact(entry_gate, "LIVE_ENTERED_ONCE", "PASS entry_gate")
        _require_exact(effects["s3_put_calls"], confirmed_mutations,
                       "PASS effects.s3_put_calls")
        _require(effects["s3_get_calls"] >= 5 + confirmed_mutations,
                 "LIVE_EFFECT_LEDGER_INVALID", "PASS readback count")
        _require_exact(effects["terminal_receipt_put_attempts"], 1,
                       "PASS terminal_receipt_put_attempts")
        _require_exact(effects["terminal_receipt_writes"], 1,
                       "PASS terminal_receipt_writes")
        _require_exact(terminal_binding.get("attempted"), True,
                       "PASS terminal_receipt_binding.attempted")
        _require_exact(terminal_binding.get("put_attempts"), 1,
                       "PASS terminal_receipt_binding.put_attempts")
        _require_exact(terminal_binding.get("confirmed"), True,
                       "PASS terminal_receipt_binding.confirmed")
        validate_object_binding(terminal_object, "PASS terminal_receipt_binding.object")
        _require_exact(claim_binding.get("key"), EXECUTION_CLAIM_KEY,
                       "PASS execution_claim_binding.key")
        _require_exact(checkpoint_binding.get("key"), G11_CHECKPOINT_KEY,
                       "PASS checkpoint_binding.key")
        _require_exact(terminal_binding.get("key"), G11_TERMINAL_RECEIPT_KEY,
                       "PASS terminal_receipt_binding.key")
        _require_exact(terminal_object.get("key"), G11_TERMINAL_RECEIPT_KEY,
                       "PASS terminal_receipt_binding.object.key")
    return return_code, output


def _pre_entry_live_failure(code: str, detail: str = "") -> dict[str, Any]:
    return {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_LIVE_ENTRY_RESULT_v1.0",
        "verdict": "FAIL_CLOSED",
        "entry_gate": "LIVE_NOT_ENTERED",
        "live_adapter_gate": LIVE_ADAPTER_GATE_READY,
        "terminal_state": "TERMINAL_FAIL_CLOSED_BEFORE_LIVE_ENTRY",
        "error": {"code": code, "detail": detail},
        "effects": dict(LIVE_PRE_ENTRY_EFFECTS),
        "effect_reconciliation": {"complete": True, "ambiguous_side_effects": False},
        "execution_claim_binding": None,
        "checkpoint_binding": None,
        "terminal_receipt_binding": {
            "key": None,
            "attempted": False,
            "put_attempts": 0,
            "confirmed": False,
            "object": None,
        },
        "claim_ceiling": {
            "source_admission_verdict": "NOT_ADMITTED",
            "issuer_identity_resolved": False,
            "normalization": False,
            "pit": False,
            "promotion": False,
            "release": False,
            "production": False,
        },
        "no_rerun": {
            "same_run_retry_authorized": False,
            "same_activation_reuse_authorized": False,
            "same_latch_reuse_authorized": False,
        },
    }


def _write_output(path: str, value: Mapping[str, Any]) -> None:
    payload = canonical_json_lf_bytes(value).decode("utf-8")
    if path == "-":
        sys.stdout.write(payload)
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise GateError("OUTPUT_ALREADY_EXISTS", str(output)) from exc


def validate_precheck_sts_policy_probe_count(value: Any) -> int:
    """Accept only the workflow proof emitted after all three STS probes pass."""

    _require(type(value) is int, "STS_POLICY_PROBE_WORKFLOW_PROOF_MISSING",
             "precheck.sts_policy_probe_count must be an integer")
    _require_exact(value, STS_POLICY_PROBE_COUNT, "precheck.sts_policy_probe_count")
    return value


def _precheck(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    validate_precheck_sts_policy_probe_count(
        getattr(args, "sts_policy_probe_count", None)
    )
    pytest_path = Path(args.pytest_file).resolve()
    manifest_path = Path(args.manifest).resolve()
    adapter_test_path = _resolve_manifest_role_path(
        manifest_path,
        "adapter_tests",
        supplied_path=(Path(args.adapter_test).resolve() if args.adapter_test else None),
    )
    bundle = validate_bundle(
        authority_path=Path(args.authority).resolve(),
        plan_path=Path(args.plan).resolve(),
        seed_path=Path(args.seed).resolve(),
        manifest_path=manifest_path,
        pytest_path=pytest_path,
        live_adapter_path=(Path(args.live_adapter).resolve() if args.live_adapter else None),
    )
    _require_exact(bundle["live_adapter_gate"], LIVE_ADAPTER_GATE_READY,
                   "precheck.live_adapter_gate")
    tests = run_focused_tests(pytest_path, adapter_test_path)
    return 0, {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_FOCUSED_PRECHECK_RESULT_v1.0",
        "verdict": "PASS",
        "entry_gate": "FOCUSED_PRECHECK_PASS",
        "live_adapter_gate": bundle["live_adapter_gate"],
        "sts_policy_probe_count": STS_POLICY_PROBE_COUNT,
        "bundle": bundle,
        "tests": tests,
        "effects": dict(PRECHECK_STS_PROBE_EFFECTS),
        "observations": {
            "future_selector_policy": FUTURE_SELECTOR_POLICY,
            "sealed_exclusion_scope": list(SEED_EXCLUDED_GLOBAL_ROW_ORDINALS),
            "required_no_rerun_runs": list(REQUIRED_NO_RERUN_RUNS),
            "active_prefix_rejection_regressions": [
                "G11", "G11C1", "G11C2", "G11C3", "G11C4", "G11C5",
            ],
            "sts_policy_probe_count": STS_POLICY_PROBE_COUNT,
            "sts_policy_probe_count_verified": STS_POLICY_PROBE_COUNT,
            "sts_policy_probe_roles": [
                item["role"] for item in OIDC_STS_POLICY_PACKING_PROBES
            ],
            "oidc_sts_policy_packing_probes": [
                dict(item) for item in OIDC_STS_POLICY_PACKING_PROBES
            ],
            "live_pre_mutation_order": list(LIVE_PRE_MUTATION_PHASES),
            "live_session_policy_ascii_and_size_ceiling_verified": True,
        },
    }


def _live(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    required_args = {
        "activation": args.activation,
        "precheck_receipt": args.precheck_receipt,
        "owner_decision": args.owner_decision,
        "live_adapter": args.live_adapter,
    }
    for name, value in required_args.items():
        _require(bool(value), "LIVE_ARGUMENT_REQUIRED", name)
    _require(isinstance(args.self_deadline_seconds, int) and
             1 <= args.self_deadline_seconds <= 18_000,
             "SELF_DEADLINE_BOUND_INVALID", "must be 1..18000 seconds")

    pytest_path = Path(args.pytest_file).resolve()
    authority_path = Path(args.authority).resolve()
    plan_path = Path(args.plan).resolve()
    seed_path = Path(args.seed).resolve()
    manifest_path = Path(args.manifest).resolve()
    activation_path = Path(args.activation).resolve()
    precheck_receipt_path = Path(args.precheck_receipt).resolve()
    owner_decision_path = Path(args.owner_decision).resolve()
    adapter_path = Path(args.live_adapter).resolve()
    bundle = validate_bundle(
        authority_path=authority_path,
        plan_path=plan_path,
        seed_path=seed_path,
        manifest_path=manifest_path,
        pytest_path=pytest_path,
        live_adapter_path=adapter_path,
    )
    manifest = load_json_document(manifest_path)
    adapter_binding = manifest.get("safe_executable_adapter")
    _require(isinstance(adapter_binding, Mapping), "INVALID_MANIFEST",
             "safe_executable_adapter is required")
    live_gate = validate_live_activation_and_receipt(
        activation_path=activation_path,
        precheck_receipt_path=precheck_receipt_path,
        authority_path=authority_path,
        plan_path=plan_path,
        seed_path=seed_path,
        manifest_path=manifest_path,
        owner_decision_path=owner_decision_path,
        adapter_binding=adapter_binding,
    )

    # Executable adapter code is imported only after every runner-side static
    # activation and receipt gate above has passed.
    factory = load_sealed_live_adapter_factory(
        adapter_path, bundle["live_adapter"]["sha256"]
    )

    adapter = None
    run_started = False
    try:
        adapter = factory(
            authority_path=authority_path,
            plan_path=plan_path,
            seed_path=seed_path,
            manifest_path=manifest_path,
            owner_decision_path=owner_decision_path,
            live_activation_path=activation_path,
            precheck_receipt_path=precheck_receipt_path,
            deadline_monotonic=time.monotonic() + args.self_deadline_seconds,
            live_head_sha=live_gate["execution_binding"]["head_sha"],
            live_head_tree=live_gate["execution_binding"]["tree_sha"],
        )
        _require(callable(getattr(adapter, "run", None)),
                 "LIVE_ADAPTER_RUN_MISSING", "run")
        run_started = True
        adapter_return = adapter.run()
        _require(isinstance(adapter_return, tuple) and len(adapter_return) == 2,
                 "LIVE_ADAPTER_RESULT_INVALID", "run must return (exit_code, result)")
        return_code, result = adapter_return
        _require(type(return_code) is int and isinstance(result, Mapping),
                 "LIVE_ADAPTER_RESULT_INVALID", "exit_code/result types")
        try:
            return _normalize_and_validate_live_result(
                result, return_code,
                expected_execution_binding=live_gate["execution_binding"],
            )
        except GateError as exc:
            preserved = dict(result)
            effects = dict(preserved.get("effects") or {})
            effects.setdefault("s3_other_calls", 0)
            effects["ambiguous_side_effects"] = True
            effects["effects_reconciled"] = False
            preserved.update({
                "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_LIVE_ENTRY_RESULT_v1.0",
                "verdict": "FAIL_CLOSED",
                "error": {"code": "LIVE_ADAPTER_RESULT_CONTRACT_FAILED", "detail": exc.code},
                "effects": effects,
                "effect_reconciliation": {"complete": False, "ambiguous_side_effects": True},
                "no_rerun": {
                    "same_run_retry_authorized": False,
                    "same_activation_reuse_authorized": False,
                    "same_latch_reuse_authorized": False,
                },
            })
            return 2, preserved
    except GateError as exc:
        if not run_started:
            raise
        result = _pre_entry_live_failure("UNRECONCILED_LIVE_ADAPTER_EXCEPTION", exc.code)
        result["effects"]["ambiguous_side_effects"] = True
        result["effects"]["effects_reconciled"] = False
        result["effect_reconciliation"] = {"complete": False, "ambiguous_side_effects": True}
        return 2, result
    except Exception as exc:
        # Factory errors occur before external entry because the factory first
        # validates its complete governance bundle.  Any exception escaping a
        # started run is conservatively marked ambiguous; no secret or raw
        # provider exception text is emitted.
        code = getattr(exc, "code", "UNEXPECTED_LIVE_ADAPTER_EXCEPTION")
        safe_code = code if isinstance(code, str) and re.fullmatch(r"[A-Z0-9_]{1,80}", code) else "UNEXPECTED_LIVE_ADAPTER_EXCEPTION"
        result = _pre_entry_live_failure(safe_code)
        result["execution_binding"] = dict(live_gate["execution_binding"])
        if run_started:
            result["error"]["code"] = "UNRECONCILED_LIVE_ADAPTER_EXCEPTION"
            result["effects"]["ambiguous_side_effects"] = True
            result["effects"]["effects_reconciled"] = False
            result["effect_reconciliation"] = {
                "complete": False, "ambiguous_side_effects": True,
            }
        return 2 if run_started else EX_CONFIG, result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("precheck", "live"), required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--pytest-file", required=True)
    parser.add_argument("--live-adapter")
    parser.add_argument("--adapter-test")
    parser.add_argument("--activation", "--live-activation", dest="activation")
    parser.add_argument("--precheck-receipt")
    parser.add_argument("--owner-decision")
    parser.add_argument("--sts-policy-probe-count", type=int)
    parser.add_argument("--self-deadline-seconds", type=int, default=18_000)
    parser.add_argument("--output", default="-")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return_code, result = _precheck(args) if args.mode == "precheck" else _live(args)
    except GateError as exc:
        return_code = EX_CONFIG if args.mode == "live" else 2
        if args.mode == "live":
            result = _pre_entry_live_failure(exc.code, exc.detail)
        else:
            precheck_effects = (
                dict(PRECHECK_STS_PROBE_EFFECTS)
                if args.sts_policy_probe_count == STS_POLICY_PROBE_COUNT
                else dict(ZERO_EFFECTS)
            )
            result = {
                "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C6_GATE_FAILURE_v1.0",
                "verdict": "FAIL_CLOSED",
                "entry_gate": "NOT_PASSED",
                "live_adapter_gate": LIVE_ADAPTER_GATE_BLOCKED,
                "error": {"code": exc.code, "detail": exc.detail},
                "effects": precheck_effects,
            }
    try:
        _write_output(args.output, result)
    except GateError as exc:
        sys.stderr.write(f"{exc}\n")
        return EX_CONFIG
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
