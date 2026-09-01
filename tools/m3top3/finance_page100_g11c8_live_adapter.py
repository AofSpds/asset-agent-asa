#!/usr/bin/env python3
"""Least-privilege LIVE adapter for the governed Finance Page100 G11C8 route.

The adapter is intentionally append-only and fail-closed.  Its first five S3
object reads are the exact G10 checkpoint version followed by the four exact
G10 raw versions.  Only after all five bodies, metadata, pagination invariants,
and the sealed 35-row hash-only projection have been revalidated may it create
the fresh execution claim and G11C8 checkpoint or call the Finance provider.

The public factory is ``create_sealed_g11c8_custody_adapter``.  Tests may inject
an object store and provider; the production defaults use only the Python
standard library and the AWS CLI.  No clear issuer identity value is emitted in
checkpoints, terminal receipts, local output, logs, or exceptions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence


# Forward-only governance binding.  AUTHORITY_COMMIT remains the historical
# contextual approval commit; GOVERNED_CORRECTION_HEAD is the controlling
# corrected receipt commit.
AUTHORITY_COMMIT = "884e1fadebda480f4c38d172eab083cbdbf031b2"
GOVERNED_CORRECTION_HEAD = "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
GOVERNED_CORRECTION_TREE = "572bf2ab23a7d761de8160e6828f8b074618391b"
OWNER_DECISION_V1_1_GIT_BLOB = "1a20b86b784c1c69b407a432e08fb476c60b496d"
OWNER_DECISION_V1_1_SHA256 = (
    "9efa622791a036c870ff4cded87bc4123cfae8089382c90a9ee2e804955ec6dd"
)
OWNER_CAP_SPEC_SHA256 = "82713faf7265f7e5f9c48fbef6dd7407714a23a050600b816a5d4b7a104d2f9b"
EXECUTION_TOKEN_SHA256 = "4daea206f046bf8ace279ed0fa39edbd0ac79a4f0c98b698f55798077aba6306"
ACTIVATION_BASE_HEAD_COMMIT = "0b21f3ffde00ea7f6705811954c729e35103a8db"
ACTIVATION_BASE_TREE = "283ccf856dd34559a1fe8848808615ab4a3ba9ce"
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
    "consumed_preparation_ids": ("FINANCE-PAGE100-G11C5-PREPARATION-20260901152200",),
    "consumed_precheck_act_ids": ("FINANCE-PAGE100-PRECHECK-ACT-G11C5-20260901152200",),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C5-20260901152200",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C5-20260901152200",),
}
PREDECESSOR_G11C5_PREPARATION_COMMIT = "b73db818d27c80e4ef1b4c5c7b0506691be33920"
PREDECESSOR_G11C5_PREPARATION_TREE = "ffab50ec73ab0f29674d82f2d72110a8923a766f"
PREDECESSOR_G11C5_PRECHECK_ACTIVATION_COMMIT = "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
PREDECESSOR_G11C5_PRECHECK_ACTIVATION_TREE = "53d13cccc42aae8f4b21adebee3ed71190ba1954"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT = "d0061e9005a74817563588990064af4260ab2bd9"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_TREE = "7ba82af78770b8fdcfb914ab080bd280f017918f"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C5_ELIGIBLE_SUCCESSOR_"
    "PRECHECK_TERMINAL_RECEIPT_33479444941_v1.0.json"
)
PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256 = "c518d4ac79b6e7735eae9fe3a799ae7ea29dd4c357508ddd4c85e2d09711b30e"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_GIT_BLOB = "a3d29884a44ca4dac88b9d47bf2447fe24aa0b08"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256 = "332d15f75b2f7843046f0eb5d8983fdb3791cef3fa6155803828e1d74008049f"
PREDECESSOR_G11C5_TERMINAL_RECEIPT_BYTES = 50220
PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_SHA = "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
PREDECESSOR_G11C5_PRECHECK_EXECUTION_HEAD_TREE_SHA = "53d13cccc42aae8f4b21adebee3ed71190ba1954"
PREDECESSOR_G11C5_TERMINAL_STATE = (
    "TERMINAL_FAIL_CLOSED_G11C5_PRECHECK_EXECUTION_PASS_RECEIPT_SCHEMA_"
    "GENERATOR_NO_RERUN_CONTRACT_MISMATCH_C4_RUN_33477019917_OMITTED_BY_"
    "FROZEN_SCHEMA_LIVE_CLOSED_CURRENT_GENERATION_NO_RERUN"
)
PREDECESSOR_G11C6_BINDING: dict[str, Any] = {'generation_id': 'FINANCE-PAGE100-G11C6-20260901155700',
 'runtime_lock_id': 'PMO-FINANCE-PAGE100-G11C6-20260901155700',
 'pilot_run_id': 'FINANCE-PAGE100-PILOT-G11C6-20260901155700',
 'preparation_id': 'FINANCE-PAGE100-G11C6-PREPARATION-20260901155700',
 'precheck_act_id': 'FINANCE-PAGE100-PRECHECK-ACT-G11C6-20260901155700',
 'live_act_id': 'FINANCE-PAGE100-LIVE-ACT-G11C6-20260901155700',
 'latch_event_id': 'FINANCE-PAGE100-LATCH-G11C6-20260901155700',
 'preparation_commit': '1a7588c3c5cc25d378f8edcad4f89c04cf1ba773',
 'preparation_tree': '5e4fe175e926401b3814c6509958d2d39e782434',
 'preparation_parent_commit': 'd0061e9005a74817563588990064af4260ab2bd9',
 'preparation_parent_tree': '7ba82af78770b8fdcfb914ab080bd280f017918f',
 'preparation_expected_commit_message': 'Prepare M3Top3 Finance page100 G11C6 eligible successor '
                                        '20260901155700 v1.0',
 'preparation_actual_commit_message': 'Prepare M3Top3 Finance Page100 G11C6 eligible successor '
                                      '20260901155700 v1.0',
 'preparation_message_case_sensitive_equal': False,
 'precheck_activation_commit': 'a08938730b95843125b18950abc27af1d48839ba',
 'precheck_activation_tree': '8ac1f1d29c82c0b240559b758cabde22c4ca93d1',
 'precheck_activation_path': 'control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PRECHECK_ACTIVATION_v1.0.json',
 'precheck_activation_git_blob': '85ecbc94a5dc125ef979d7a9925dcd50a73f871a',
 'precheck_activation_sha256': '3a845af5bffee4dcbea399e7635d402bf2403494f84dc7899a2a2f031a018282',
 'precheck_activation_bytes': 50757,
 'terminal_receipt_append_commit': '56f2a2fc109da0167010dce64c3697d5051636d3',
 'terminal_receipt_append_tree': 'a868ca84f516dc43f30329c267e3209f940ce2bf',
 'terminal_receipt_path': 'control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_RECEIPT_33484842311_v1.0.json',
 'terminal_receipt_git_blob': '08583e511d62cde662b668fa78cfe4f1a4787572',
 'terminal_receipt_sha256': 'd1d4ed8edbc670990b2eea1c13f9681f17f1a1ae0771fb062c20900346a22867',
 'terminal_receipt_payload_sha256': '50581e61f50e9526ecc945900fd545047761c7ecfe95e18ee49717c3037734ce',
 'terminal_receipt_bytes': 44284,
 'execution_head_sha': 'a08938730b95843125b18950abc27af1d48839ba',
 'execution_tree_sha': '8ac1f1d29c82c0b240559b758cabde22c4ca93d1',
 'precheck_run_id': 33484842311,
 'precheck_job_id': 99782407546,
 'run_attempt': 1,
 'workflow_conclusion': 'failure',
 'result': 'FAIL_CLOSED',
 'terminal_state': 'TERMINAL_FAIL_CLOSED_G11C6_PRECHECK_PRE_OIDC_PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH_EXPECTED_page100_ACTUAL_Page100_ZERO_EXTERNAL_EFFECT_NO_RERUN_LIVE_CLOSED',
 'entry_gate': 'FAIL_CLOSED_PRE_OIDC_PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH',
 'defect_code': 'PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH',
 'defect_class': 'SEMANTIC_QUOTA_CUSTODY_NEUTRAL_ZERO_EXTERNAL_EFFECT_CONTROL_DEFECT',
 'runner_started': False,
 'oidc_token_requests': 0,
 'aws_calls': 0,
 'sts_calls': 0,
 'sts_assume_role_attempts': 0,
 'sts_assume_role_successes': 0,
 'sts_sessions_assumed': 0,
 'sts_get_caller_identity_calls': 0,
 'credentials_issued': 0,
 's3_calls': 0,
 'provider_calls': 0,
 'provider_network_attempts': 0,
 'quota_reservations': 0,
 'remote_custody_mutations': 0,
 'repository_mutations_by_workflow': 0,
 'github_actions_artifacts_uploaded': 0,
 'effects_reconciled': True,
 'ambiguous_side_effects': False,
 'all_effects_zero': True,
 'all_downstream_effects_zero': True,
 'live_execution_started': False,
 'same_run_retry_authorized': False,
 'reuse_authorized': False}
PREDECESSOR_G11C6_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C6-20260901155700",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C6-20260901155700",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C6-20260901155700",),
    "consumed_preparation_ids": ("FINANCE-PAGE100-G11C6-PREPARATION-20260901155700",),
    "consumed_precheck_act_ids": ("FINANCE-PAGE100-PRECHECK-ACT-G11C6-20260901155700",),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C6-20260901155700",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C6-20260901155700",),
}
PREDECESSOR_G11C7_BINDING_CANONICAL_SHA256 = (
    "a93c61efbdcedc1d870052a3adac3bd5d8cff375f10c8794531cdd8c2fbf1d10"
)
PREDECESSOR_G11C7_IDENTITIES = {
    "consumed_generation_ids": ("FINANCE-PAGE100-G11C7-20260901171500",),
    "consumed_runtime_lock_ids": ("PMO-FINANCE-PAGE100-G11C7-20260901171500",),
    "consumed_pilot_run_ids": ("FINANCE-PAGE100-PILOT-G11C7-20260901171500",),
    "consumed_preparation_ids": ("FINANCE-PAGE100-G11C7-PREPARATION-20260901171500",),
    "consumed_precheck_act_ids": ("FINANCE-PAGE100-PRECHECK-ACT-G11C7-20260901171500",),
    "consumed_live_act_ids": ("FINANCE-PAGE100-LIVE-ACT-G11C7-20260901171500",),
    "consumed_latch_event_ids": ("FINANCE-PAGE100-LATCH-G11C7-20260901171500",),
}

AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = 2048

GENERATION_TIMESTAMP = "20260901184500"
GENERATION_ID = f"FINANCE-PAGE100-G11C8-{GENERATION_TIMESTAMP}"
RUNTIME_LOCK_ID = f"PMO-FINANCE-PAGE100-G11C8-{GENERATION_TIMESTAMP}"
PILOT_RUN_ID = f"FINANCE-PAGE100-PILOT-G11C8-{GENERATION_TIMESTAMP}"
PREPARATION_ID = f"FINANCE-PAGE100-G11C8-PREPARATION-{GENERATION_TIMESTAMP}"
PRECHECK_ACT_ID = f"FINANCE-PAGE100-PRECHECK-ACT-G11C8-{GENERATION_TIMESTAMP}"
LIVE_ACT_ID = f"FINANCE-PAGE100-LIVE-ACT-G11C8-{GENERATION_TIMESTAMP}"
LATCH_EVENT_ID = f"FINANCE-PAGE100-LATCH-G11C8-{GENERATION_TIMESTAMP}"
REQUIRED_NO_RERUN_RUNS = (
    33272691259,  # G10 PRECHECK
    33273146915,  # G10 LIVE
    33401871715,  # S2 PRECHECK
    33403101817,  # S2 LIVE
    33414615913,  # S3 PRECHECK
    33414695818,  # S3 APPLY
    33465583987,  # consumed G11 PRECHECK
    33466306591,  # consumed G11 LIVE fail-closed control defect
    33469887723,  # consumed G11C2 PRECHECK; G11C2 invalidated before LIVE
    33472741288,  # consumed G11C3 focused PRECHECK
    33473465774,  # consumed G11C3 LIVE; credentials/runner were never entered
    33477019917,  # consumed G11C4 PRECHECK; first OIDC AssumeRole denied
    33479444941,  # consumed G11C5 PRECHECK; receipt contract terminal failure
    33484842311,  # consumed G11C6 PRECHECK; pre-OIDC message-case failure
    33490803554,  # consumed G11C7 PRECHECK; focused PASS, receipt durably closed
    33492771321,  # consumed G11C7 LIVE; pre-credential shallow-history failure
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
    "FINANCE-PAGE100-G11C6-",
    "PMO-FINANCE-PAGE100-G11C6-",
    "FINANCE-PAGE100-G11C7-",
    "PMO-FINANCE-PAGE100-G11C7-",
)
PRECHECK_STS_EFFECTS = {
    "aws_calls": 6,
    "sts_calls": 6,
    "sts_assume_role_attempts": 3,
    "sts_sessions_assumed": 3,
    "sts_get_caller_identity_calls": 3,
    "credentials_issued": 3,
}
PRECHECK_STS_PROBES = [
    {
        "probe_ordinal": ordinal,
        "role": role,
        "policy_role": policy_role,
        "outcome": "SUCCESS",
        "sts_attempts": 1,
        "sts_successes": 1,
        "credentials_issued": 1,
    }
    for ordinal, (role, policy_role) in enumerate((
        ("CHECKPOINT_READ", "checkpoint_read_session_policy"),
        ("RAW_READ", "raw_four_read_session_policy"),
        ("FINAL_LIST_WRITE", "final_list_write_session_policy"),
    ), 1)
]

REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
SOURCE_ID = "M3TOP3-FINANCE-STOCK-RIGHTS-v1"
OPERATION = "getRighExerReasSche_V2"
FINANCE_URL = (
    "https://apis.data.go.kr/1160100/GetStocRighScheService_V2/"
    "getRighExerReasSche_V2"
)
PRIMARY_DATES = (
    "20240102", "20240131", "20240329", "20240628", "20240808",
    "20240809", "20240812", "20240930", "20241231", "20250115",
    "20250331", "20250630", "20251231", "20260115", "20260331",
    "20260630", "20260814",
)
PRIMARY_DATES_SHA256 = (
    "920b118d7d7abaa10f69e93169698ed380db7162ac3c5024756a07702a7065f6"
)
REQUEST_PAGE_SIZE = 10
MAX_PAGES_PER_DATE = 100
EFFECTIVE_ACQUISITION_CEILING = 1700
INHERITED_G10_ACQUISITIONS = 4
G11C8_ACQUISITION_CEILING = 1696
EFFECTIVE_NETWORK_ATTEMPT_CEILING = 2000
INHERITED_G10_ATTEMPTS = 4
G11C8_NETWORK_ATTEMPT_CEILING = 1996
MAX_ATTEMPTS_PER_LOGICAL_PAGE = 2
# A page attempt uses at most four checkpoint writes (reservation, durable call
# marker, raw-reference persistence, and classification/status), plus the
# initial seed, at most 17 date closures, and terminal/block transitions.
CHECKPOINT_WRITE_CEILING = 8_003
EXECUTION_CLAIM_WRITE_CEILING = 1
TERMINAL_RECEIPT_WRITE_CEILING = 1

SEED_BASE_DATE = "20240131"
FIRST_NEW_PAGE = 5
SEED_TOTAL_COUNT = 275
SEED_EXPECTED_PAGES = 28
SEED_SOURCE_ROWS = 40
SEED_ELIGIBLE_ROWS = 35
SEED_EXCLUDED_ROWS = 5
SEED_EXCLUDED_ORDINALS = (36, 37, 38, 39, 40)
TARGET_CUSTODY_SHA256 = (
    "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
)
TARGET_FROZEN_IDENTITY_SHA256 = (
    "d95a27a7c79ae4bda4c8170db30f2d4bc395faff904b55dbcbaeb10e3f6f9c21"
)
TARGET_OBSERVED_IDENTITY_SHA256 = (
    "d1d37a0df09e0aa73c1dd350b4a8be2b62172dfcca27bf8dede4a925bdeacb03"
)
SEALED_ELIGIBLE_PROJECTION_SHA256 = (
    "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
)
G10_CLEAR_IDENTITY_MAP_SHA256 = (
    "ddd4379158a6cbb3c1073754c6b531bfb0fbaa0792ff04a2c88396a6b5c07851"
)

AWS_ACCOUNT = "956315449338"
AWS_REGION = "ap-northeast-2"
BUCKET = "semi-data-plane-aofspds-20260815"
SOURCE_PREFIX = f"raw/public-data-api/{SOURCE_ID}/"
G11C8_RAW_PREFIX = (
    SOURCE_PREFIX + "_pilot_generation/"
    f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
)
G11C8_CONTROL_PREFIX = (
    SOURCE_PREFIX + "_pilot_control/"
    f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
)
G11C8_CHECKPOINT_KEY = G11C8_CONTROL_PREFIX + "checkpoint.json"
G11C8_TERMINAL_RECEIPT_KEY = G11C8_CONTROL_PREFIX + "terminal-receipt.json"
QUOTA_DAY_KST = "2026-09-01"
EXECUTION_CLAIM_KEY = (
    SOURCE_PREFIX + f"_writer_claims/quota_day_kst={QUOTA_DAY_KST}/"
    "execution-claim.json"
)

CHECKPOINT_ARTIFACT = "M3TOP3_FINANCE_CA_PAGE100_G11C8_CHECKPOINT_v1.0"
TERMINAL_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_LIVE_TERMINAL_v1.0"
)
LIVE_ADAPTER_PATH = "tools/m3top3/finance_page100_g11c8_live_adapter.py"
FACTORY_SYMBOL = "create_sealed_g11c8_custody_adapter"
ADAPTER_INTERFACE_VERSION = "M3TOP3_FINANCE_CA_PAGE100_G11C8_LIVE_ADAPTER_v1.0"
EX_CONFIG = 78

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ASCII_DATE = re.compile(r"^[0-9]{8}$")
ASCII_CUSTODY = re.compile(r"^[0-9]+$")
FORBIDDEN_CLEAR_KEYS = frozenset(
    {"issuCmpyKsdCustNo", "crno", "stckIssuCmpyNm"}
)
KST = timezone(timedelta(hours=9))


class LiveAdapterError(RuntimeError):
    """A sanitized, deterministic, fail-closed LIVE error."""

    def __init__(self, code: str, detail: str = "") -> None:
        safe_detail = detail if re.fullmatch(r"[A-Za-z0-9_.:/= -]{0,240}", detail) else ""
        super().__init__(code + (f": {safe_detail}" if safe_detail else ""))
        self.code = code
        self.detail = safe_detail


class GovernanceError(LiveAdapterError):
    pass


class SeedBindingError(LiveAdapterError):
    pass


class CustodyError(LiveAdapterError):
    pass


class AmbiguousSideEffectError(CustodyError):
    pass


class ConditionalWriteConflict(CustodyError):
    """A proven failed S3 precondition with no mutation by this request."""


class ProviderError(LiveAdapterError):
    pass


class PaginationDriftError(LiveAdapterError):
    pass


class FutureSelectorError(LiveAdapterError):
    pass


class IdentityConflictError(LiveAdapterError):
    pass


class MissingIdentityError(LiveAdapterError):
    pass


class BudgetError(LiveAdapterError):
    pass


def require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise LiveAdapterError(code, detail)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha(value: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(value)).encode("ascii") + b"\0" + value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def strict_json_bytes(value: bytes, code: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value, object_pairs_hook=_strict_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveAdapterError(code) from exc
    if not isinstance(parsed, dict):
        raise LiveAdapterError(code)
    return parsed


def read_json_file(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise GovernanceError(code, path.name) from exc
    return strict_json_bytes(raw, code), raw


def _walk_scalars(value: Any) -> Sequence[Any]:
    scalars: list[Any] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            if any(key in FORBIDDEN_CLEAR_KEYS for key in current):
                raise LiveAdapterError("CLEAR_ISSUER_KEY_IN_OUTPUT")
            stack.extend(current.values())
        elif isinstance(current, (list, tuple)):
            stack.extend(current)
        else:
            scalars.append(current)
    return scalars


def assert_hash_only_output(value: Any, sensitive_values: set[str] | None = None) -> None:
    sensitive = sensitive_values or set()
    for scalar in _walk_scalars(value):
        if isinstance(scalar, str) and scalar in sensitive:
            raise LiveAdapterError("CLEAR_ISSUER_VALUE_IN_OUTPUT")


def _nested(value: Mapping[str, Any], *path: str) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            raise GovernanceError("MISSING_GOVERNED_FIELD", ".".join(path))
        current = current[key]
    return current


def _exact(value: Any, expected: Any, code: str) -> None:
    if value != expected:
        raise GovernanceError(code)


def _validate_active_c7_prefixes(raw_prefix: Any, control_prefix: Any) -> None:
    """Reject any historical namespace before accepting exact G11C8 prefixes."""

    for observed, expected in (
        (raw_prefix, G11C8_RAW_PREFIX),
        (control_prefix, G11C8_CONTROL_PREFIX),
    ):
        if not isinstance(observed, str) or not observed:
            raise GovernanceError("AUTHORITY_CUSTODY_BOUNDARY_MISMATCH")
        if any(marker in observed for marker in HISTORICAL_SUCCESSOR_NAMESPACE_MARKERS):
            raise GovernanceError("HISTORICAL_ACTIVE_PREFIX_FORBIDDEN")
        _exact(observed, expected, "AUTHORITY_CUSTODY_BOUNDARY_MISMATCH")


def _validate_predecessor_ineligible_preparation_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_ineligible_preparation_binding")
    for field_name, expected in {
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
        _exact(binding.get(field_name), expected, code)


def _validate_consumed_g11c1_identities(
    no_rerun: Mapping[str, Any], code: str,
) -> None:
    for field_name, expected_values in PREDECESSOR_G11C1_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)


def _predecessor_invalidated_g11c2_binding() -> dict[str, Any]:
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


def _validate_predecessor_invalidated_g11c2_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_invalidated_g11c2_binding")
    _exact(dict(binding), _predecessor_invalidated_g11c2_binding(), code)


def _predecessor_terminal_g11c3_binding() -> dict[str, Any]:
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


def _validate_predecessor_terminal_g11c3_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_terminal_g11c3_binding")
    _exact(dict(binding), _predecessor_terminal_g11c3_binding(), code)


def _predecessor_terminal_g11c4_binding() -> dict[str, Any]:
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


def _validate_predecessor_terminal_g11c4_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_terminal_g11c4_binding")
    _exact(dict(binding), _predecessor_terminal_g11c4_binding(), code)


def _predecessor_terminal_g11c5_binding() -> dict[str, Any]:
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
        "terminal_receipt_append_commit": PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree": PREDECESSOR_G11C5_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": PREDECESSOR_G11C5_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": PREDECESSOR_G11C5_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob": PREDECESSOR_G11C5_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256": PREDECESSOR_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256,
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
        "defect": "FROZEN_SCHEMA_REQUIRED_NO_RERUN_CONST_OMITS_CONSUMED_G11C4_PRECHECK_RUN_33477019917",
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


def _validate_predecessor_terminal_g11c5_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_terminal_g11c5_binding")
    _exact(dict(binding), _predecessor_terminal_g11c5_binding(), code)



def _predecessor_terminal_g11c6_binding() -> dict[str, Any]:
    return dict(PREDECESSOR_G11C6_BINDING)


def _validate_predecessor_terminal_g11c6_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_terminal_g11c6_binding")
    _exact(dict(binding), _predecessor_terminal_g11c6_binding(), code)


def _validate_predecessor_terminal_g11c7_binding(
    document: Mapping[str, Any], code: str,
) -> None:
    binding = _nested(document, "predecessor_terminal_g11c7_binding")
    _exact(
        sha256_bytes(canonical_json_bytes(dict(binding))),
        PREDECESSOR_G11C7_BINDING_CANONICAL_SHA256,
        code,
    )

def _validate_consumed_predecessor_identities(
    no_rerun: Mapping[str, Any], code: str,
) -> None:
    _exact(no_rerun.get("consumed_github_runs"), list(REQUIRED_NO_RERUN_RUNS), code)
    for field_name, expected_values in PREDECESSOR_G11C6_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
        "g11c6_precheck_run_id": 33484842311,
        "g11c6_precheck_job_id": 99782407546,
        "g11c6_precheck_run_attempt": 1,
        "g11c6_precheck_rerun_authorized": False,
        "g11c6_precheck_execution_result": "NOT_RUN_PRE_OIDC",
        "g11c6_terminal_receipt_result": "FAIL_CLOSED",
        "g11c6_terminal_receipt_contract_valid": True,
        "g11c6_live_run_exists": False,
        "g11c6_credentials_issued": 0,
        "g11c6_runner_started": False,
        "g11c6_live_execution_started": False,
        "g11c6_activation_reuse_authorized": False,
        "g11c6_generation_reuse_authorized": False,
        "g11c6_runtime_lock_reuse_authorized": False,
        "g11c6_pilot_run_id_reuse_authorized": False,
        "g11c6_precheck_act_id_reuse_authorized": False,
        "g11c6_live_act_id_reuse_authorized": False,
        "g11c6_latch_event_id_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(field_name), expected, code)
    for field_name, expected_values in PREDECESSOR_G11C7_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
        "consumed_g11c7_precheck_run": 33490803554,
        "consumed_g11c7_live_run": 33492771321,
        "g11c7_precheck_run_id": 33490803554,
        "g11c7_precheck_job_id": 99801574441,
        "g11c7_precheck_run_attempt": 1,
        "g11c7_precheck_execution_result": "PASS",
        "g11c7_live_run_id": 33492771321,
        "g11c7_live_job_id": 99807892677,
        "g11c7_live_run_attempt": 1,
        "g11c7_live_execution_result": "FAIL_CLOSED_PRE_CREDENTIAL",
        "g11c7_terminal_receipt_contract_valid": True,
        "g11c7_precheck_credentials_issued": 3,
        "g11c7_live_credentials_issued": 0,
        "g11c7_live_runner_started": False,
        "g11c7_live_execution_started": False,
        "g11c7_precheck_rerun_authorized": False,
        "g11c7_live_rerun_authorized": False,
        "g11c7_activation_reuse_authorized": False,
        "g11c7_generation_reuse_authorized": False,
        "g11c7_runtime_lock_reuse_authorized": False,
        "g11c7_pilot_run_id_reuse_authorized": False,
        "g11c7_precheck_act_id_reuse_authorized": False,
        "g11c7_live_act_id_reuse_authorized": False,
        "g11c7_latch_event_id_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(field_name), expected, code)
    _validate_consumed_g11c1_identities(no_rerun, code)
    for field_name, expected_values in PREDECESSOR_G11C2_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
        "g11c2_precheck_run_id": PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "g11c2_precheck_run_attempt": PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT,
        "g11c2_precheck_rerun_authorized": False,
        "g11c2_live_run_exists": False,
        "g11c2_activation_reuse_authorized": False,
        "g11c2_generation_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(field_name), expected, code)
    for field_name, expected_values in PREDECESSOR_G11C5_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
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
        _exact(no_rerun.get(field_name), expected, code)
    for field_name, expected_values in PREDECESSOR_G11C4_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
        "g11c4_precheck_run_id": PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "g11c4_precheck_run_attempt": PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT,
        "g11c4_precheck_rerun_authorized": False,
        "g11c4_credentials_issued": 0,
        "g11c4_runner_started": False,
        "g11c4_activation_reuse_authorized": False,
        "g11c4_generation_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(field_name), expected, code)
    for field_name, expected_values in PREDECESSOR_G11C3_IDENTITIES.items():
        observed = no_rerun.get(field_name)
        if not isinstance(observed, list) or not all(
            value in observed for value in expected_values
        ):
            raise GovernanceError(code)
    for field_name, expected in {
        "g11c3_precheck_run_id": PREDECESSOR_G11C3_PRECHECK_RUN_ID,
        "g11c3_precheck_run_attempt": 1,
        "g11c3_live_run_id": PREDECESSOR_G11C3_LIVE_RUN_ID,
        "g11c3_live_run_attempt": 1,
        "g11c3_credentials_issued": False,
        "g11c3_runner_started": False,
        "g11c3_activation_reuse_authorized": False,
        "g11c3_generation_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(field_name), expected, code)


def _validate_precheck_pass_role_binding(
    binding: Mapping[str, Any], receipt: Mapping[str, Any],
) -> None:
    """Keep PRECHECK receipt persistence distinct from its execution head/tree."""

    execution = _nested(receipt, "execution_binding")
    execution_head = execution.get("head_sha")
    execution_tree = execution.get("tree_sha")
    if not isinstance(execution_head, str) or HEX40.fullmatch(execution_head) is None:
        raise GovernanceError("PRECHECK_EXECUTION_HEAD_INVALID")
    if not isinstance(execution_tree, str) or HEX40.fullmatch(execution_tree) is None:
        raise GovernanceError("PRECHECK_EXECUTION_TREE_INVALID")
    append_commit = binding.get("receipt_append_commit")
    append_tree = binding.get("receipt_append_tree")
    if not isinstance(append_commit, str) or HEX40.fullmatch(append_commit) is None:
        raise GovernanceError("PRECHECK_RECEIPT_APPEND_COMMIT_INVALID")
    if not isinstance(append_tree, str) or HEX40.fullmatch(append_tree) is None:
        raise GovernanceError("PRECHECK_RECEIPT_APPEND_TREE_INVALID")
    _exact(binding.get("execution_head_sha"), execution_head,
           "ACTIVATION_PRECHECK_EXECUTION_HEAD_MISMATCH")
    _exact(binding.get("execution_head_tree_sha"), execution_tree,
           "ACTIVATION_PRECHECK_EXECUTION_TREE_MISMATCH")
    if (append_commit, append_tree) == (execution_head, execution_tree):
        raise GovernanceError("PRECHECK_LINEAGE_ROLES_COLLAPSED")
    if "commit" in binding or "tree" in binding:
        raise GovernanceError("AMBIGUOUS_PRECHECK_LINEAGE_FIELDS_FORBIDDEN")


def _validate_plan_seed_material_binding(
    plan: Mapping[str, Any], seed_path: Path, seed_raw: bytes,
) -> None:
    resume = _nested(plan, "resume_and_seed_contract")
    _exact(
        resume.get("checkpoint_seed_path"),
        "control/m3top3/public-data-source-admission/v1.0/"
        "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0.json",
        "PLAN_SEED_PATH_MISMATCH",
    )
    _exact(resume.get("checkpoint_seed_sha256"), sha256_bytes(seed_raw),
           "PLAN_SEED_SHA256_MISMATCH")
    _exact(resume.get("checkpoint_seed_git_blob"), git_blob_sha(seed_raw),
           "PLAN_SEED_GIT_BLOB_MISMATCH")
    _exact(seed_path.name,
           "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0.json",
           "SEED_FILENAME_MISMATCH")


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
    """Validate the compact ASCII inline policy actually supplied to STS."""

    try:
        raw = path.read_bytes()
        source_text = raw.decode("ascii").strip()
    except (OSError, UnicodeDecodeError) as exc:
        raise GovernanceError("LIVE_SESSION_POLICY_NON_ASCII") from exc
    if not source_text:
        raise GovernanceError("LIVE_SESSION_POLICY_EMPTY")
    policy = strict_json_bytes(source_text.encode("ascii"),
                               "LIVE_SESSION_POLICY_INVALID_JSON")
    if "Version" in policy:
        raise GovernanceError("LIVE_SESSION_POLICY_VERSION_MUST_BE_OMITTED")
    if "${" in source_text:
        raise GovernanceError("LIVE_SESSION_POLICY_VARIABLE_FORBIDDEN")
    expected = (
        expected_live_session_policy()
        if role is None
        else expected_split_session_policies().get(role)
    )
    if expected is None:
        raise GovernanceError("LIVE_SESSION_POLICY_ROLE_INVALID")
    _exact(policy, expected,
           "LIVE_SESSION_POLICY_SEMANTICS_MISMATCH")
    compact = json.dumps(policy, ensure_ascii=True, separators=(",", ":"))
    if not compact.isascii():
        raise GovernanceError("LIVE_SESSION_POLICY_NON_ASCII")
    if len(compact) > AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING:
        raise GovernanceError("LIVE_SESSION_POLICY_EXCEEDS_AWS_ASCII_CHARACTER_LIMIT")
    return len(compact)


@dataclass(frozen=True)
class ObjectBinding:
    key: str
    version_id: str
    sha256: str
    bytes: int
    etag: str
    content_type: str
    server_side_encryption: str = "AES256"
    page_no: int | None = None


G10_CHECKPOINT_BINDING = ObjectBinding(
    key=(
        SOURCE_PREFIX + "_pilot_control/"
        "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
        "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/checkpoint.json"
    ),
    version_id="r3eu2mkgFklGzpZPyKq5xXrt50wa6JgU",
    sha256="42a76559083f18e2482f89de59af4d6dd842c07595089e9eea5f1716369e4f39",
    bytes=66359,
    etag='"5d1c1a7bb50329b2d4608552b483a37d"',
    content_type="application/json",
)

G10_RAW_BINDINGS = (
    ObjectBinding(
        key=(SOURCE_PREFIX + "_pilot_generation/runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
             "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/getRighExerReasSche_V2/"
             "quota_day_kst=2026-08-30/request_id=2336abe1c81d4c86f90fef6575e204d0455367d4d5e8ed6cce103a752f0330da/"
             "attempt=1/sha256=2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309.entity"),
        version_id="VdsI_D_jNujHIb9ff8loyRWtuAW737RI",
        sha256="2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309",
        bytes=4642, etag='"f53c31679b7985d17c59e9bed7006f04"',
        content_type="application/octet-stream", page_no=1,
    ),
    ObjectBinding(
        key=(SOURCE_PREFIX + "_pilot_generation/runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
             "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/getRighExerReasSche_V2/"
             "quota_day_kst=2026-08-30/request_id=dea3a2edfa78a4ebe2f912d2a8d8fa90456e960ad4cdbb832e501c91dd71d41c/"
             "attempt=1/sha256=385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9.entity"),
        version_id="30whtf2xTpWQYXPmr.Kt5RBnK1Y_YDI4",
        sha256="385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9",
        bytes=4697, etag='"823c7254b8a0e943bae650b8664377e2"',
        content_type="application/octet-stream", page_no=2,
    ),
    ObjectBinding(
        key=(SOURCE_PREFIX + "_pilot_generation/runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
             "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/getRighExerReasSche_V2/"
             "quota_day_kst=2026-08-30/request_id=eb594842fb4aa2c9a131efbb7b64f4bb72f3678315fa352224132355bd0be1de/"
             "attempt=1/sha256=ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9.entity"),
        version_id="1dHYBfs4hg1tM7S6TckyUngOmfwWKZc2",
        sha256="ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9",
        bytes=4570, etag='"014d58859ef7ba4c4104827af266e9d1"',
        content_type="application/octet-stream", page_no=3,
    ),
    ObjectBinding(
        key=(SOURCE_PREFIX + "_pilot_generation/runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
             "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/getRighExerReasSche_V2/"
             "quota_day_kst=2026-08-30/request_id=75494b2b71aeb1dcfd52e2cba2198e933fef2ad271c900328085da375dd9989c/"
             "attempt=1/sha256=8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1.entity"),
        version_id="iBxAq9V.V7eA_doOM39JcVt_gtzAHskI",
        sha256="8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1",
        bytes=4821, etag='"dad1ca1dbe6f1c5bbedf80967f9b3d61"',
        content_type="application/octet-stream", page_no=4,
    ),
)


@dataclass(frozen=True)
class LiveContract:
    correction_head: str = GOVERNED_CORRECTION_HEAD
    correction_tree: str = GOVERNED_CORRECTION_TREE
    owner_blob: str = OWNER_DECISION_V1_1_GIT_BLOB
    owner_sha256: str = OWNER_DECISION_V1_1_SHA256
    primary_dates: tuple[str, ...] = PRIMARY_DATES
    checkpoint_binding: ObjectBinding = G10_CHECKPOINT_BINDING
    raw_bindings: tuple[ObjectBinding, ...] = G10_RAW_BINDINGS
    seed_base_date: str = SEED_BASE_DATE
    first_new_page: int = FIRST_NEW_PAGE
    seed_total_count: int = SEED_TOTAL_COUNT
    seed_expected_pages: int = SEED_EXPECTED_PAGES
    seed_source_rows: int = SEED_SOURCE_ROWS
    seed_eligible_rows: int = SEED_ELIGIBLE_ROWS
    seed_excluded_rows: int = SEED_EXCLUDED_ROWS
    excluded_ordinals: tuple[int, ...] = SEED_EXCLUDED_ORDINALS
    selector_sha256: str = TARGET_CUSTODY_SHA256
    frozen_identity_sha256: str = TARGET_FROZEN_IDENTITY_SHA256
    observed_identity_sha256: str = TARGET_OBSERVED_IDENTITY_SHA256
    eligible_projection_sha256: str = SEALED_ELIGIBLE_PROJECTION_SHA256
    g10_identity_map_sha256: str = G10_CLEAR_IDENTITY_MAP_SHA256
    request_page_size: int = REQUEST_PAGE_SIZE
    max_pages_per_date: int = MAX_PAGES_PER_DATE
    g11_acquisition_ceiling: int = G11C8_ACQUISITION_CEILING
    g11_attempt_ceiling: int = G11C8_NETWORK_ATTEMPT_CEILING
    attempts_per_page: int = MAX_ATTEMPTS_PER_LOGICAL_PAGE


PRODUCTION_CONTRACT = LiveContract()


@dataclass(frozen=True)
class VersionedObject:
    key: str
    version_id: str
    etag: str
    body: bytes
    content_type: str
    server_side_encryption: str
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.body)


@dataclass(frozen=True)
class ProviderResponse:
    body: bytes
    http_status: int
    socket_opened_at_utc: str
    response_received_at_utc: str
    safe_headers: Mapping[str, str] = field(default_factory=dict)


class ObjectStore(Protocol):
    def exact_read(self, binding: ObjectBinding) -> VersionedObject: ...

    def pre_mutation_gate(self) -> None: ...

    def create_once(
        self, key: str, body: bytes, *, content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject: ...

    def compare_and_swap(
        self, key: str, body: bytes, *, expected_etag: str,
        content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject: ...


class FinanceProvider(Protocol):
    def fetch_once(self, params: Mapping[str, str]) -> ProviderResponse: ...


@dataclass
class EffectLedger:
    primary_acquisitions: int = 0
    network_attempts: int = 0
    provider_calls: int = 0
    quota_reservations: int = 0
    raw_writes: int = 0
    checkpoint_writes: int = 0
    execution_claim_writes: int = 0
    terminal_receipt_writes: int = 0
    terminal_receipt_put_attempts: int = 0
    s3_get_calls: int = 0
    s3_put_calls: int = 0
    s3_other_calls: int = 0
    s3_delete_calls: int = 0
    s3_copy_calls: int = 0
    s3_tagging_mutation_calls: int = 0
    company_master_mutations: int = 0
    universe_mutations: int = 0
    company_master_or_universe_mutations: int = 0
    repository_writes: int = 0
    repository_mutations_by_workflow: int = 0
    github_actions_artifacts_uploaded: int = 0
    normalization_actions: int = 0
    pit_actions: int = 0
    promotion_actions: int = 0
    release_actions: int = 0
    production_actions: int = 0
    ambiguous_side_effects: bool = False

    def output(self) -> dict[str, Any]:
        confirmed_mutations = (
            self.raw_writes + self.checkpoint_writes
            + self.execution_claim_writes + self.terminal_receipt_writes
        )
        result = dict(self.__dict__)
        result.update({
            "sts_calls": PRECHECK_STS_EFFECTS["sts_calls"],
            "sts_assume_role_attempts": PRECHECK_STS_EFFECTS[
                "sts_assume_role_attempts"
            ],
            "sts_sessions_assumed": PRECHECK_STS_EFFECTS["sts_sessions_assumed"],
            "sts_get_caller_identity_calls": PRECHECK_STS_EFFECTS[
                "sts_get_caller_identity_calls"
            ],
            "credentials_issued": PRECHECK_STS_EFFECTS["credentials_issued"],
            "finance_provider_api_calls": self.provider_calls,
            "provider_quota_reservations": self.quota_reservations,
            "raw_objects_written": self.raw_writes,
            "quota_ledger_appends": 0,
            "raw_index_appends": self.raw_writes,
            "aws_calls": (
                PRECHECK_STS_EFFECTS["aws_calls"]
                + self.s3_get_calls + self.s3_put_calls + self.s3_other_calls
            ),
            "s3_calls": (
                self.s3_get_calls + self.s3_put_calls + self.s3_other_calls
            ),
            "s3_get_attempts": self.s3_get_calls,
            "s3_put_attempts": self.s3_put_calls,
            "s3_other_read_calls": self.s3_other_calls,
            "successful_put_mutations": confirmed_mutations,
            "unconfirmed_or_failed_put_attempts": max(
                0, self.s3_put_calls - confirmed_mutations
            ),
            "remote_custody_mutations": confirmed_mutations,
            "effects_reconciled": not self.ambiguous_side_effects,
            "effective_primary_acquisitions": (
                INHERITED_G10_ACQUISITIONS + self.primary_acquisitions
            ),
            "effective_network_attempts": (
                INHERITED_G10_ATTEMPTS + self.network_attempts
            ),
        })
        return result


@dataclass(frozen=True)
class GovernanceBundle:
    documents: Mapping[str, Mapping[str, Any]]
    raw: Mapping[str, bytes]
    sha256: Mapping[str, str]
    paths: Mapping[str, Path]
    github_run_id: int
    github_run_attempt: int
    live_head_sha: str
    live_head_tree: str


@dataclass(frozen=True)
class SeedState:
    checkpoint: Mapping[str, Any]
    sensitive_values: frozenset[str]


def _validate_production_contract(contract: LiveContract) -> None:
    if contract is not PRODUCTION_CONTRACT and contract != PRODUCTION_CONTRACT:
        return
    _exact(contract.correction_head, GOVERNED_CORRECTION_HEAD, "CORRECTION_HEAD_SHIFT")
    _exact(contract.owner_blob, OWNER_DECISION_V1_1_GIT_BLOB, "OWNER_BLOB_SHIFT")
    _exact(contract.owner_sha256, OWNER_DECISION_V1_1_SHA256, "OWNER_SHA_SHIFT")
    _exact(contract.primary_dates, PRIMARY_DATES, "DATE_VECTOR_SHIFT")
    _exact(sha256_bytes(canonical_json_bytes(list(contract.primary_dates))),
           PRIMARY_DATES_SHA256, "DATE_VECTOR_DIGEST_SHIFT")
    _exact(contract.first_new_page, 5, "FIRST_NEW_PAGE_SHIFT")
    _exact(contract.g11_acquisition_ceiling, 1696, "ACQUISITION_BOUND_SHIFT")
    _exact(contract.g11_attempt_ceiling, 1996, "ATTEMPT_BOUND_SHIFT")
    _exact(contract.attempts_per_page, 2, "PER_PAGE_ATTEMPT_BOUND_SHIFT")


def validate_governance_bundle(
    *, authority_path: Path, plan_path: Path, seed_path: Path,
    manifest_path: Path, owner_decision_path: Path,
    live_activation_path: Path, precheck_receipt_path: Path,
    adapter_path: Path | None = None,
    live_head_sha: str | None = None,
    live_head_tree: str | None = None,
) -> GovernanceBundle:
    paths = {
        "authority": authority_path,
        "plan": plan_path,
        "seed": seed_path,
        "manifest": manifest_path,
        "owner_decision": owner_decision_path,
        "live_activation": live_activation_path,
        "precheck_receipt": precheck_receipt_path,
    }
    documents: dict[str, Mapping[str, Any]] = {}
    raw: dict[str, bytes] = {}
    hashes: dict[str, str] = {}
    for role, path in paths.items():
        document, body = read_json_file(path, "INVALID_GOVERNED_JSON")
        documents[role] = document
        raw[role] = body
        hashes[role] = sha256_bytes(body)

    owner = documents["owner_decision"]
    _exact(hashes["owner_decision"], OWNER_DECISION_V1_1_SHA256,
           "OWNER_DECISION_SHA256_MISMATCH")
    _exact(git_blob_sha(raw["owner_decision"]), OWNER_DECISION_V1_1_GIT_BLOB,
           "OWNER_DECISION_BLOB_MISMATCH")
    _exact(owner.get("artifact"),
           "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1",
           "OWNER_DECISION_ARTIFACT_MISMATCH")
    _exact(owner.get("correction_id"), "OA-F01", "OWNER_CORRECTION_MISMATCH")
    _exact(_nested(owner, "selector_continuation_semantics", "sealed_exclusion_scope"),
           [36, 37, 38, 39, 40], "SEALED_EXCLUSION_SCOPE_SHIFT")
    _exact(_nested(owner, "selector_continuation_semantics", "future_selector_match"),
           "RAW_CUSTODY_THEN_FAIL_CLOSED", "FUTURE_SELECTOR_POLICY_SHIFT")
    _exact(_nested(owner, "selector_continuation_semantics", "future_selector_match_auto_excluded"),
           False, "FUTURE_SELECTOR_AUTO_EXCLUSION_FORBIDDEN")

    authority = documents["authority"]
    _exact(authority.get("artifact"),
           "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_AUTHORITY_v1.0",
           "AUTHORITY_ARTIFACT_MISMATCH")
    binding = _nested(authority, "owner_authority_binding")
    _exact(binding.get("governing_forward_only_receipt_commit"),
           GOVERNED_CORRECTION_HEAD, "AUTHORITY_CORRECTION_COMMIT_MISMATCH")
    _exact(binding.get("governing_forward_only_receipt_git_blob"),
           OWNER_DECISION_V1_1_GIT_BLOB, "AUTHORITY_OWNER_BLOB_MISMATCH")
    _exact(binding.get("governing_forward_only_receipt_sha256"),
           OWNER_DECISION_V1_1_SHA256, "AUTHORITY_OWNER_SHA_MISMATCH")
    _exact(authority.get("authority_base_commit"), ACTIVATION_BASE_HEAD_COMMIT,
           "AUTHORITY_BASE_COMMIT_MISMATCH")
    _exact(authority.get("authority_base_tree"), ACTIVATION_BASE_TREE,
           "AUTHORITY_BASE_TREE_MISMATCH")
    _validate_predecessor_ineligible_preparation_binding(
        authority, "AUTHORITY_INELIGIBLE_PREPARATION_MISMATCH"
    )
    _validate_predecessor_invalidated_g11c2_binding(
        authority, "AUTHORITY_G11C2_INVALIDATION_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c3_binding(
        authority, "AUTHORITY_G11C3_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c4_binding(
        authority, "AUTHORITY_G11C4_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c5_binding(
        authority, "AUTHORITY_G11C5_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c6_binding(
        authority, "AUTHORITY_G11C6_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c7_binding(
        authority, "AUTHORITY_G11C7_TERMINAL_BINDING_MISMATCH"
    )
    _exact(_nested(authority, "fresh_identity", "generation_id"), GENERATION_ID,
           "AUTHORITY_GENERATION_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "runtime_lock_id"), RUNTIME_LOCK_ID,
           "AUTHORITY_RUNTIME_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "pilot_run_id"), PILOT_RUN_ID,
           "AUTHORITY_PILOT_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "preparation_id"), PREPARATION_ID,
           "AUTHORITY_PREPARATION_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "precheck_act_id"), PRECHECK_ACT_ID,
           "AUTHORITY_PRECHECK_ACT_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "live_act_id"), LIVE_ACT_ID,
           "AUTHORITY_LIVE_ACT_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "latch_event_id"), LATCH_EVENT_ID,
           "AUTHORITY_LATCH_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "execution_token_sha256"),
           EXECUTION_TOKEN_SHA256, "AUTHORITY_EXECUTION_TOKEN_MISMATCH")
    _exact(_nested(authority, "fresh_identity", "owner_cap_spec_sha256"),
           OWNER_CAP_SPEC_SHA256, "AUTHORITY_OWNER_CAP_MISMATCH")
    _exact(authority.get("execution_token_sha256"), EXECUTION_TOKEN_SHA256,
           "AUTHORITY_TOP_LEVEL_EXECUTION_TOKEN_MISMATCH")
    _exact(authority.get("owner_cap_spec_sha256"), OWNER_CAP_SPEC_SHA256,
           "AUTHORITY_TOP_LEVEL_OWNER_CAP_MISMATCH")
    _exact(_nested(authority, "entry_gate", "live_adapter_gate"), "READY",
           "AUTHORITY_ADAPTER_GATE_NOT_READY")
    _exact(
        _nested(
            authority, "entry_gate",
            "live_session_policy_ascii_and_size_ceiling_verified",
        ),
        True,
        "AUTHORITY_LIVE_POLICY_SIZE_GATE_NOT_VERIFIED",
    )
    _exact(_nested(authority, "authorized_route", "route"),
           "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_AT_20240131_PAGE_5",
           "AUTHORITY_ROUTE_MISMATCH")
    finance = _nested(authority, "finance_bounds")
    for key, expected in {
        "ordered_primary_dates": list(PRIMARY_DATES),
        "request_page_size": 10,
        "max_pages_per_date": 100,
        "aggregate_max_primary_page_acquisitions": 1700,
        "aggregate_max_network_attempts_total": 2000,
        "max_attempts_per_logical_page": 2,
        "g10_spent_primary_acquisitions": 4,
        "g10_spent_network_attempts": 4,
        "maximum_new_g11_primary_acquisitions": 1696,
        "maximum_new_g11_network_attempts": 1996,
    }.items():
        _exact(finance.get(key), expected, "AUTHORITY_FINANCE_BOUND_MISMATCH")
    custody = _nested(authority, "custody_boundary")
    _validate_active_c7_prefixes(
        custody.get("g11_raw_prefix"), custody.get("g11_control_prefix")
    )
    for key, expected in {
        "aws_account": AWS_ACCOUNT, "region": AWS_REGION, "bucket": BUCKET,
        "execution_claim_key": EXECUTION_CLAIM_KEY,
        "delete_authority": False, "copy_authority": False,
        "predecessor_objects_immutable": True,
    }.items():
        _exact(custody.get(key), expected, "AUTHORITY_CUSTODY_BOUNDARY_MISMATCH")
    authority_no_rerun = _nested(authority, "no_rerun")
    _validate_consumed_predecessor_identities(
        authority_no_rerun, "AUTHORITY_PREDECESSOR_IDENTITY_LINEAGE_INCOMPLETE"
    )

    plan = documents["plan"]
    _exact(plan.get("artifact"),
           "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_PLAN_v1.0",
           "PLAN_ARTIFACT_MISMATCH")
    _validate_predecessor_ineligible_preparation_binding(
        plan, "PLAN_INELIGIBLE_PREPARATION_MISMATCH"
    )
    _validate_predecessor_invalidated_g11c2_binding(
        plan, "PLAN_G11C2_INVALIDATION_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c3_binding(
        plan, "PLAN_G11C3_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c4_binding(
        plan, "PLAN_G11C4_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c5_binding(
        plan, "PLAN_G11C5_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c6_binding(
        plan, "PLAN_G11C6_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c7_binding(
        plan, "PLAN_G11C7_TERMINAL_BINDING_MISMATCH"
    )
    _validate_consumed_predecessor_identities(
        _nested(plan, "no_rerun"), "PLAN_PREDECESSOR_IDENTITY_LINEAGE_INCOMPLETE"
    )
    plan_identity = _nested(plan, "identity")
    for field_name, expected in {
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "preparation_id": PREPARATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
    }.items():
        _exact(plan_identity.get(field_name), expected, "PLAN_FRESH_IDENTITY_MISMATCH")
    _validate_plan_seed_material_binding(plan, seed_path, raw["seed"])
    _exact(_nested(plan, "entry", "bas_dt"), SEED_BASE_DATE, "PLAN_ENTRY_DATE_MISMATCH")
    _exact(_nested(plan, "entry", "first_new_page"), FIRST_NEW_PAGE,
           "PLAN_ENTRY_PAGE_MISMATCH")
    _exact(_nested(plan, "entry", "provider_replay_pages"), [],
           "PLAN_REPLAY_FORBIDDEN")
    _exact(_nested(plan, "selector", "future_matches_excluded"), False,
           "PLAN_AUTO_EXCLUSION_FORBIDDEN")
    _exact(_nested(plan, "selector", "future_match_disposition"),
           "RAW_CUSTODY_FIRST_THEN_FAIL_CLOSED_PENDING_OWNER_DECISION",
           "PLAN_SELECTOR_DISPOSITION_MISMATCH")

    seed = documents["seed"]
    _exact(seed.get("artifact"),
           "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0",
           "SEED_ARTIFACT_MISMATCH")
    _validate_predecessor_ineligible_preparation_binding(
        seed, "SEED_INELIGIBLE_PREPARATION_MISMATCH"
    )
    _validate_predecessor_invalidated_g11c2_binding(
        seed, "SEED_G11C2_INVALIDATION_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c3_binding(
        seed, "SEED_G11C3_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c4_binding(
        seed, "SEED_G11C4_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c5_binding(
        seed, "SEED_G11C5_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c6_binding(
        seed, "SEED_G11C6_TERMINAL_BINDING_MISMATCH"
    )
    _validate_predecessor_terminal_g11c7_binding(
        seed, "SEED_G11C7_TERMINAL_BINDING_MISMATCH"
    )
    _validate_consumed_predecessor_identities(
        _nested(seed, "no_rerun"), "SEED_PREDECESSOR_IDENTITY_LINEAGE_INCOMPLETE"
    )
    _exact(seed.get("bas_dt"), SEED_BASE_DATE, "SEED_DATE_MISMATCH")
    _exact(seed.get("next_page"), FIRST_NEW_PAGE, "SEED_PAGE_MISMATCH")
    predecessor = _nested(seed, "predecessor_checkpoint")
    for key, expected in {
        "key": G10_CHECKPOINT_BINDING.key,
        "version_id": G10_CHECKPOINT_BINDING.version_id,
        "sha256": G10_CHECKPOINT_BINDING.sha256,
        "bytes": G10_CHECKPOINT_BINDING.bytes,
        "revision": 27,
        "etag": G10_CHECKPOINT_BINDING.etag,
        "mutation_authorized": False,
    }.items():
        _exact(predecessor.get(key), expected, "SEED_PREDECESSOR_MISMATCH")
    projection = _nested(seed, "projection")
    for key, expected in {
        "selector_sha256": TARGET_CUSTODY_SHA256,
        "eligible_projection_sha256": SEALED_ELIGIBLE_PROJECTION_SHA256,
        "source_rows": 40, "eligible_rows": 35, "excluded_rows": 5,
        "missing_rows": 0, "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
        "future_match_auto_exclusion_authorized": False,
    }.items():
        _exact(projection.get(key), expected, "SEED_PROJECTION_MISMATCH")

    manifest = documents["manifest"]
    adapter_file = (adapter_path or Path(__file__)).resolve()
    adapter_sha = sha256_file(adapter_file)
    adapter_blob = git_blob_sha(adapter_file.read_bytes())
    _exact(manifest.get("live_adapter_gate"), "READY",
           "MANIFEST_ADAPTER_GATE_NOT_READY")
    live_adapter = _nested(manifest, "live_adapter")
    for key, expected in {
        "executable": True, "sealed": True, "ready": True,
        "path": LIVE_ADAPTER_PATH, "sha256": adapter_sha,
        "git_blob": adapter_blob,
        "factory_symbol": FACTORY_SYMBOL,
    }.items():
        _exact(live_adapter.get(key), expected, "MANIFEST_ADAPTER_NOT_SEALED")
    for binding_name, adapter_binding in {
        "manifest": _nested(manifest, "safe_executable_adapter"),
        "authority": _nested(authority, "safe_executable_adapter"),
    }.items():
        for key, expected in {
            "ready": True, "path": LIVE_ADAPTER_PATH,
            "sha256": adapter_sha, "git_blob": adapter_blob,
            "factory_symbol": FACTORY_SYMBOL,
        }.items():
            _exact(
                adapter_binding.get(key), expected,
                f"{binding_name.upper()}_SAFE_ADAPTER_NOT_SEALED",
            )
    manifest_files = _nested(manifest, "files")
    repo_root = Path(__file__).resolve().parents[2]
    for policy_role in expected_split_session_policies():
        live_policy_binding = _nested(manifest_files, policy_role)
        live_policy_repo_path = live_policy_binding.get("path")
        if (
            not isinstance(live_policy_repo_path, str)
            or not live_policy_repo_path
            or Path(live_policy_repo_path).is_absolute()
        ):
            raise GovernanceError("MANIFEST_LIVE_SESSION_POLICY_PATH_INVALID")
        live_policy_path = (repo_root / live_policy_repo_path).resolve()
        try:
            live_policy_path.relative_to(repo_root)
        except ValueError as exc:
            raise GovernanceError("MANIFEST_LIVE_SESSION_POLICY_PATH_INVALID") from exc
        try:
            live_policy_raw = live_policy_path.read_bytes()
        except OSError as exc:
            raise GovernanceError("MANIFEST_LIVE_SESSION_POLICY_MISSING") from exc
        _exact(live_policy_binding.get("sha256"), sha256_bytes(live_policy_raw),
               "MANIFEST_LIVE_SESSION_POLICY_SHA_MISMATCH")
        _exact(live_policy_binding.get("git_blob"), git_blob_sha(live_policy_raw),
               "MANIFEST_LIVE_SESSION_POLICY_BLOB_MISMATCH")
        validate_live_session_policy_for_aws(live_policy_path, policy_role)

    precheck = documents["precheck_receipt"]
    artifact_id = precheck.get("artifact")
    artifact_match = re.fullmatch(
        r"M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_"
        r"PRECHECK_TERMINAL_RECEIPT_([0-9]+)_v1\.0",
        str(artifact_id or ""),
    )
    if artifact_match is None:
        raise GovernanceError("PRECHECK_RECEIPT_ARTIFACT_MISMATCH")
    precheck_run_id = artifact_match.group(1)
    _exact((precheck.get("artifact_identity") or {}).get("artifact_id"), artifact_id,
           "PRECHECK_ARTIFACT_IDENTITY_MISMATCH")
    _exact(str(precheck.get("github_run_id")), precheck_run_id,
           "PRECHECK_TOP_LEVEL_RUN_ID_MISMATCH")
    _exact(str(_nested(precheck, "execution_binding", "run_id")), precheck_run_id,
           "PRECHECK_EXECUTION_RUN_ID_MISMATCH")
    _exact(_nested(precheck, "terminal", "result"), "PASS", "PRECHECK_NOT_PASS")
    _exact(_nested(precheck, "terminal", "live_authorized"), False,
           "PRECHECK_MUST_NOT_SELF_AUTHORIZE_LIVE")
    _exact(_nested(precheck, "live_adapter_gate", "runner_reported_readiness"),
           "READY", "PRECHECK_ADAPTER_NOT_READY")
    _exact(_nested(precheck, "runner_result", "live_adapter_gate"),
           "READY", "PRECHECK_RUNNER_ADAPTER_NOT_READY")
    _exact(precheck.get("terminal_state"),
           "TERMINAL_PASS_FOCUSED_G11C8_PRECHECK_EXACT_3_OIDC_STS_POLICY_"
           "PACKING_PROBES_SUCCESS_ZERO_DOWNSTREAM_MUTATION_LIVE_NOT_AUTHORIZED",
           "PRECHECK_TERMINAL_STATE_MISMATCH")
    runner_result = _nested(precheck, "runner_result")
    _exact(runner_result.get("sts_policy_probe_count"), 3,
           "PRECHECK_STS_POLICY_PROBE_COUNT_MISMATCH")
    for key, expected in PRECHECK_STS_EFFECTS.items():
        _exact(_nested(runner_result, "effects").get(key), expected,
               "PRECHECK_RUNNER_STS_EFFECT_MISMATCH")
    observations = _nested(runner_result, "observations")
    _exact(observations.get("sts_policy_probe_count"), 3,
           "PRECHECK_STS_POLICY_PROBE_COUNT_MISMATCH")
    _exact(observations.get("sts_policy_probe_count_verified"), 3,
           "PRECHECK_STS_POLICY_PROBE_COUNT_MISMATCH")
    _exact(observations.get("sts_policy_probe_roles"),
           [probe["role"] for probe in PRECHECK_STS_PROBES],
           "PRECHECK_STS_POLICY_PROBE_ROLE_MISMATCH")
    _exact(observations.get("oidc_sts_policy_packing_probes"), PRECHECK_STS_PROBES,
           "PRECHECK_STS_POLICY_PROBE_OBSERVATION_MISMATCH")
    _exact(_nested(precheck, "execution_binding", "run_attempt"), 1,
           "PRECHECK_RUN_ATTEMPT_MISMATCH")
    _exact(_nested(precheck, "execution_binding", "forced"), False,
           "PRECHECK_FORCED_RUN_FORBIDDEN")
    observed = _nested(precheck, "observed_effects")
    _exact(observed.get("effects_reconciled"), True, "PRECHECK_EFFECTS_UNRECONCILED")
    _exact(observed.get("ambiguous_side_effects"), False, "PRECHECK_EFFECTS_AMBIGUOUS")
    for key, expected in PRECHECK_STS_EFFECTS.items():
        _exact(observed.get(key), expected, "PRECHECK_STS_EFFECT_MISMATCH")
    for key in (
        "s3_calls", "provider_calls", "finance_provider_api_calls",
        "quota_reservations", "provider_quota_reservations", "raw_writes",
        "s3_put_delete_copy", "repository_mutations_by_workflow",
        "remote_custody_mutations", "normalization_actions", "pit_actions",
        "promotion_actions", "release_actions", "production_actions",
    ):
        _exact(observed.get(key), 0, "PRECHECK_DOWNSTREAM_EFFECT_NONZERO")

    activation = documents["live_activation"]
    _exact(activation.get("artifact"),
           "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_LIVE_ACTIVATION_v1.0",
           "LIVE_ACTIVATION_ARTIFACT_MISMATCH")
    _exact(activation.get("mode"), "LIVE", "LIVE_MODE_MISMATCH")
    _exact(activation.get("armed"), True, "LIVE_NOT_ARMED")
    activation_binding = _nested(activation, "activation_binding")
    for key, expected in {
        "live_activation_commit": "BOUND_BY_GITHUB_EVENT_AFTER",
        "live_activation_tree": "BOUND_BY_CHECKED_OUT_HEAD_TREE",
        "expected_branch_head_at_dispatch": "BOUND_BY_GITHUB_EVENT_AFTER",
    }.items():
        _exact(activation_binding.get(key), expected,
               "LIVE_ACTIVATION_SELF_REFERENCE_FORBIDDEN")
    identity = _nested(activation, "identity")
    for key, expected in {
        "generation_id": GENERATION_ID, "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID, "act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
    }.items():
        _exact(identity.get(key), expected, "LIVE_IDENTITY_MISMATCH")
    _exact(activation.get("live_adapter_gate"), "READY", "ACTIVATION_ADAPTER_NOT_READY")
    safe_activation_adapter = _nested(activation, "safe_executable_adapter")
    for key, expected in {
        "ready": True, "path": LIVE_ADAPTER_PATH,
        "sha256": adapter_sha, "git_blob": adapter_blob,
        "factory_symbol": FACTORY_SYMBOL,
    }.items():
        _exact(safe_activation_adapter.get(key), expected,
               "ACTIVATION_SAFE_ADAPTER_NOT_SEALED")
    precheck_binding = _nested(activation, "precheck_pass_binding")
    _exact(precheck_binding.get("sha256"),
           hashes["precheck_receipt"], "ACTIVATION_PRECHECK_SHA_MISMATCH")
    _exact(precheck_binding.get("git_blob"), git_blob_sha(raw["precheck_receipt"]),
           "ACTIVATION_PRECHECK_BLOB_MISMATCH")
    _exact(precheck_binding.get("bytes"), len(raw["precheck_receipt"]),
           "ACTIVATION_PRECHECK_BYTES_MISMATCH")
    _validate_precheck_pass_role_binding(precheck_binding, precheck)
    _exact(str(precheck_binding.get("github_run_id")), precheck_run_id,
           "ACTIVATION_PRECHECK_RUN_ID_MISMATCH")
    _exact(precheck_binding.get("github_run_attempt"), 1,
           "ACTIVATION_PRECHECK_RUN_ATTEMPT_MISMATCH")
    _exact(str(precheck_binding.get("github_job_id")),
           str(precheck.get("github_job_id")),
           "ACTIVATION_PRECHECK_JOB_ID_MISMATCH")
    bound_precheck_path = str(precheck_binding.get("path") or "")
    if not bound_precheck_path or not precheck_receipt_path.as_posix().endswith(
        bound_precheck_path
    ):
        raise GovernanceError("ACTIVATION_PRECHECK_PATH_MISMATCH")
    _exact(precheck_binding.get("result"), "PASS",
           "ACTIVATION_PRECHECK_RESULT_MISMATCH")
    no_rerun = _nested(activation, "no_rerun")
    for key, expected in {
        "github_run_attempt_required": 1, "same_run_retry_authorized": False,
        "same_activation_reuse_authorized": False,
        "same_latch_reuse_authorized": False,
    }.items():
        _exact(no_rerun.get(key), expected, "LIVE_NO_RERUN_MISMATCH")
    consumed_runs = no_rerun.get("consumed_github_runs")
    if (
        not isinstance(consumed_runs, list)
        or not all(run_id in consumed_runs for run_id in REQUIRED_NO_RERUN_RUNS)
    ):
        raise GovernanceError("LIVE_NO_RERUN_LINEAGE_INCOMPLETE")
    _validate_consumed_predecessor_identities(
        no_rerun, "LIVE_PREDECESSOR_IDENTITY_LINEAGE_INCOMPLETE"
    )
    material = _nested(activation, "material_bindings")
    material_names = {
        "authority": ("authority", "authority_sha256"),
        "plan": ("plan", "plan_sha256"),
        "seed": ("seed", "seed_sha256", "checkpoint_seed_sha256"),
        "manifest": ("manifest", "manifest_sha256"),
        "owner_decision": (
            "owner_decision", "owner_decision_sha256",
            "owner_decision_v1_1_sha256",
        ),
    }
    for role, aliases in material_names.items():
        role_binding = material.get(role)
        observed_hash = role_binding.get("sha256") if isinstance(
            role_binding, Mapping
        ) else None
        for alias in aliases:
            if observed_hash is not None:
                break
            candidate = material.get(alias)
            if isinstance(candidate, str):
                observed_hash = candidate
        _exact(observed_hash, hashes[role], "LIVE_MATERIAL_HASH_MISMATCH")

    run_id_text = os.environ.get("GITHUB_RUN_ID", "")
    run_attempt_text = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if not run_id_text.isdigit() or not run_attempt_text.isdigit():
        raise GovernanceError("GITHUB_RUNTIME_IDENTITY_MISSING")
    run_id, run_attempt = int(run_id_text), int(run_attempt_text)
    _exact(run_attempt, 1, "GITHUB_RUN_ATTEMPT_MUST_BE_ONE")
    actual_head = live_head_sha or os.environ.get("G11C8_LIVE_HEAD_SHA", "")
    actual_tree = live_head_tree or os.environ.get("G11C8_LIVE_HEAD_TREE", "")
    if not isinstance(actual_head, str) or not HEX40.fullmatch(actual_head):
        raise GovernanceError("LIVE_RUNTIME_HEAD_INVALID")
    if not isinstance(actual_tree, str) or not HEX40.fullmatch(actual_tree):
        raise GovernanceError("LIVE_RUNTIME_TREE_INVALID")
    _exact(os.environ.get("G11C8_LIVE_HEAD_SHA"), actual_head,
           "LIVE_RUNTIME_HEAD_ENV_MISMATCH")
    _exact(os.environ.get("G11C8_LIVE_HEAD_TREE"), actual_tree,
           "LIVE_RUNTIME_TREE_ENV_MISMATCH")
    for env_name, expected in {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": f"refs/heads/{BRANCH}",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_ACTOR": "AofSpds",
        "GITHUB_TRIGGERING_ACTOR": "AofSpds",
        "GITHUB_SHA": actual_head,
    }.items():
        _exact(os.environ.get(env_name), expected, "GITHUB_RUNTIME_BINDING_MISMATCH")

    return GovernanceBundle(
        documents=documents, raw=raw, sha256=hashes, paths=paths,
        github_run_id=run_id, github_run_attempt=run_attempt,
        live_head_sha=actual_head, live_head_tree=actual_tree,
    )


def _find_first(value: Any, names: tuple[str, ...]) -> Any:
    if isinstance(value, Mapping):
        for name in names:
            if name in value and not isinstance(value[name], (Mapping, list)):
                return value[name]
        for child in value.values():
            found = _find_first(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_first(child, names)
            if found is not None:
                return found
    return None


def _find_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        if "item" in value:
            item = value["item"]
            if item in (None, ""):
                return []
            if isinstance(item, Mapping):
                return [dict(item)]
            if isinstance(item, list) and all(isinstance(row, Mapping) for row in item):
                return [dict(row) for row in item]
            raise PaginationDriftError("ITEM_SHAPE_INVALID")
        for child in value.values():
            result = _find_items(child)
            if result:
                return result
    elif isinstance(value, list):
        for child in value:
            result = _find_items(child)
            if result:
                return result
    return []


def _xml_value(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return (element.text or "").strip()
    result: dict[str, Any] = {}
    for child in children:
        key = child.tag.rsplit("}", 1)[-1]
        value = _xml_value(child)
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result


def parse_entity(body: bytes) -> Any:
    if not isinstance(body, bytes) or not 0 < len(body) <= 2_000_000:
        raise PaginationDriftError("ENTITY_SIZE_INVALID")
    payload = body.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if payload.startswith((b"{", b"[")):
        try:
            return json.loads(payload.decode("utf-8"), object_pairs_hook=_strict_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise PaginationDriftError("ENTITY_JSON_INVALID") from exc
    if payload.startswith(b"<"):
        if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
            raise PaginationDriftError("ENTITY_XML_DTD_FORBIDDEN")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise PaginationDriftError("ENTITY_XML_INVALID") from exc
        return {root.tag.rsplit("}", 1)[-1]: _xml_value(root)}
    raise PaginationDriftError("ENTITY_FORMAT_INVALID")


def _wire_uint(value: Any, code: str) -> int:
    text = str(value) if value is not None else ""
    if not re.fullmatch(r"[0-9]+", text):
        raise PaginationDriftError(code)
    return int(text)


def parse_finance_page(
    body: bytes, *, expected_bas_dt: str, expected_page_no: int,
    expected_page_size: int,
) -> dict[str, Any]:
    parsed = parse_entity(body)
    if _find_first(parsed, ("resultCode",)) != "00":
        raise PaginationDriftError("FINANCE_RESULT_CODE_NOT_00")
    page_no = _wire_uint(_find_first(parsed, ("pageNo",)), "PAGE_NUMBER_INVALID")
    page_size = _wire_uint(_find_first(parsed, ("numOfRows",)), "PAGE_SIZE_INVALID")
    total_count = _wire_uint(
        _find_first(parsed, ("totalCount", "totalCnt")), "TOTAL_COUNT_INVALID"
    )
    if page_no != expected_page_no:
        raise PaginationDriftError("PAGE_NUMBER_DRIFT")
    if page_size != expected_page_size:
        raise PaginationDriftError("PAGE_SIZE_DRIFT")
    items = _find_items(parsed)
    if len(items) > expected_page_size:
        raise PaginationDriftError("PAGE_ITEM_CEILING_EXCEEDED")
    for item in items:
        if str(_find_first(item, ("basDt",)) or "") != expected_bas_dt:
            raise PaginationDriftError("ITEM_BASE_DATE_DRIFT")
    return {
        "page_no": page_no, "page_size": page_size,
        "total_count": total_count, "items": items,
    }


def identity_digest(item: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes({
        "crno": str(item.get("crno") or ""),
        "issuCmpyKsdCustNo": str(item.get("issuCmpyKsdCustNo") or ""),
        "stckIssuCmpyNm": str(item.get("stckIssuCmpyNm") or ""),
    }))


def request_params(bas_dt: str, page_no: int) -> dict[str, str]:
    if not ASCII_DATE.fullmatch(bas_dt) or page_no < 1:
        raise LiveAdapterError("INVALID_REQUEST_CURSOR")
    return {
        "basDt": bas_dt, "issuCmpyKsdCustNo": "",
        "numOfRows": str(REQUEST_PAGE_SIZE), "pageNo": str(page_no),
        "resultType": "json", "stckIssuCmpyNm": "",
    }


def request_id(bas_dt: str, page_no: int) -> str:
    params = request_params(bas_dt, page_no)
    return sha256_bytes(canonical_json_bytes({
        "source_id": SOURCE_ID, "endpoint": FINANCE_URL, "operation": OPERATION,
        "params": {key: params[key] for key in sorted(params)},
    }))


def raw_prefix(bas_dt: str, page_no: int, attempt: int) -> str:
    if attempt not in (1, 2):
        raise BudgetError("PER_PAGE_ATTEMPT_CEILING")
    return (
        G11C8_RAW_PREFIX + f"{OPERATION}/quota_day_kst={QUOTA_DAY_KST}/"
        f"request_id={request_id(bas_dt, page_no)}/attempt={attempt}/"
    )


def _validate_object(value: VersionedObject, binding: ObjectBinding) -> None:
    if (
        value.key != binding.key
        or value.version_id != binding.version_id
        or value.etag != binding.etag
        or value.sha256 != binding.sha256
        or len(value.body) != binding.bytes
        or value.content_type != binding.content_type
        or value.server_side_encryption != binding.server_side_encryption
    ):
        raise SeedBindingError("EXACT_OBJECT_VERSION_BINDING_MISMATCH")


def _validate_g10_checkpoint(
    body: bytes, contract: LiveContract,
) -> tuple[dict[str, Any], dict[str, str]]:
    checkpoint = strict_json_bytes(body, "G10_CHECKPOINT_JSON_INVALID")
    if (
        checkpoint.get("artifact") != "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_v1.0"
        or checkpoint.get("checkpoint_revision") != 27
        or checkpoint.get("state") != "BLOCKED"
        or checkpoint.get("runtime_lock_id") != "PMO-FINANCE-PAGE100-G10-20260830044522"
        or checkpoint.get("pilot_run_id") != "FINANCE-PAGE100-PILOT-G10-20260830044522"
        or checkpoint.get("completed_dates") != ["20240102"]
        or checkpoint.get("next_date_index") != 1
        or checkpoint.get("provider_api_network_attempts") != 4
        or checkpoint.get("quota_reservations") != 4
        or checkpoint.get("remote_raw_custody_writes") != 4
        or checkpoint.get("issuer_identity_rows_checked") != 40
        or checkpoint.get("issuer_identity_match_rows") != 38
        or checkpoint.get("issuer_identity_conflicts") != 2
        or checkpoint.get("issuer_identity_missing_rows") != 0
    ):
        raise SeedBindingError("G10_CHECKPOINT_TERMINAL_SHAPE_MISMATCH")
    attempts = checkpoint.get("attempts")
    raw_index = checkpoint.get("raw_index")
    identities = checkpoint.get("issuer_identity_hashes")
    if (
        not isinstance(attempts, list) or len(attempts) != 4
        or not isinstance(raw_index, list) or len(raw_index) != 4
        or not isinstance(identities, Mapping) or len(identities) != 17
        or sha256_bytes(canonical_json_bytes(dict(identities)))
           != contract.g10_identity_map_sha256
    ):
        raise SeedBindingError("G10_CHECKPOINT_SEED_COLLECTION_MISMATCH")
    for ordinal, (attempt, raw, binding) in enumerate(
        zip(attempts, raw_index, contract.raw_bindings), 1
    ):
        if (
            attempt.get("basDt") != contract.seed_base_date
            or attempt.get("page_no") != ordinal
            or attempt.get("attempt") != 1
            or raw.get("basDt") != contract.seed_base_date
            or raw.get("page_no") != ordinal
            or raw.get("attempt") != 1
            or raw.get("s3_object_key") != binding.key
            or raw.get("s3_version_id") != binding.version_id
            or raw.get("entity_sha256") != binding.sha256
            or raw.get("entity_bytes") != binding.bytes
        ):
            raise SeedBindingError("G10_CHECKPOINT_RAW_JOIN_MISMATCH")
    hash_map: dict[str, str] = {}
    for clear_custody, digest in identities.items():
        if (
            not isinstance(clear_custody, str) or not ASCII_CUSTODY.fullmatch(clear_custody)
            or not isinstance(digest, str) or not HEX64.fullmatch(digest)
        ):
            raise SeedBindingError("G10_IDENTITY_MAP_INVALID")
        custody_hash = sha256_bytes(clear_custody.encode("utf-8"))
        if custody_hash in hash_map:
            raise SeedBindingError("CUSTODY_DIGEST_COLLISION")
        hash_map[custody_hash] = digest
    if hash_map.get(contract.selector_sha256) != contract.frozen_identity_sha256:
        raise SeedBindingError("TARGET_FROZEN_IDENTITY_BINDING_MISMATCH")
    del hash_map[contract.selector_sha256]
    if len(hash_map) != 16:
        raise SeedBindingError("FILTERED_IDENTITY_MAP_COUNT_MISMATCH")
    return checkpoint, hash_map


def recover_seed(
    store: ObjectStore,
    contract: LiveContract,
    *,
    on_exact_read: Callable[[], None] | None = None,
) -> SeedState:
    """Perform the exact five read-only predecessor reads and build the seed."""

    if on_exact_read is not None:
        on_exact_read()
    checkpoint_object = store.exact_read(contract.checkpoint_binding)
    _validate_object(checkpoint_object, contract.checkpoint_binding)
    raw_objects: list[VersionedObject] = []
    for binding in contract.raw_bindings:
        if on_exact_read is not None:
            on_exact_read()
        observed = store.exact_read(binding)
        _validate_object(observed, binding)
        raw_objects.append(observed)

    predecessor, filtered_map = _validate_g10_checkpoint(
        checkpoint_object.body, contract
    )
    pages: list[dict[str, Any]] = []
    sensitive_values: set[str] = set()
    eligible_descriptors: list[dict[str, Any]] = []
    target_ordinals: list[int] = []
    target_identity_vector: list[str] = []
    global_ordinal = 0
    page_fingerprints: list[str] = []
    for page_no, obj in enumerate(raw_objects, 1):
        page = parse_finance_page(
            obj.body, expected_bas_dt=contract.seed_base_date,
            expected_page_no=page_no,
            expected_page_size=contract.request_page_size,
        )
        if (
            page["total_count"] != contract.seed_total_count
            or len(page["items"]) != contract.request_page_size
        ):
            raise SeedBindingError("G10_RAW_PAGINATION_SEED_MISMATCH")
        pages.append(page)
        fingerprint = sha256_bytes(canonical_json_bytes(page["items"]))
        if fingerprint in page_fingerprints:
            raise SeedBindingError("G10_RAW_REPEATED_PAGE")
        page_fingerprints.append(fingerprint)
        for page_item_ordinal, item in enumerate(page["items"], 1):
            global_ordinal += 1
            values: dict[str, str] = {}
            for key in FORBIDDEN_CLEAR_KEYS:
                value = item.get(key)
                if not isinstance(value, str):
                    raise SeedBindingError("G10_IDENTITY_FIELD_TYPE_INVALID")
                values[key] = value
                if value:
                    sensitive_values.add(value)
            custody = values["issuCmpyKsdCustNo"]
            if not custody or custody != custody.strip() or not ASCII_CUSTODY.fullmatch(custody):
                raise SeedBindingError("G10_CUSTODY_FORMAT_INVALID")
            custody_hash = sha256_bytes(custody.encode("utf-8"))
            identity_hash = identity_digest(item)
            descriptor = {
                "basDt": contract.seed_base_date,
                "custody_key_sha256": custody_hash,
                "global_row_ordinal": global_ordinal,
                "observed_identity_sha256": identity_hash,
                "page_item_ordinal": page_item_ordinal,
                "page_no": page_no,
            }
            if custody_hash == contract.selector_sha256:
                target_ordinals.append(global_ordinal)
                target_identity_vector.append(identity_hash)
            else:
                if filtered_map.get(custody_hash) != identity_hash:
                    raise SeedBindingError("NON_TARGET_SEED_IDENTITY_MISMATCH")
                eligible_descriptors.append(descriptor)

    if (
        global_ordinal != contract.seed_source_rows
        or target_ordinals != list(contract.excluded_ordinals)
        or target_identity_vector != [
            contract.frozen_identity_sha256,
            contract.observed_identity_sha256,
            contract.frozen_identity_sha256,
            contract.observed_identity_sha256,
            contract.frozen_identity_sha256,
        ]
        or len(eligible_descriptors) != contract.seed_eligible_rows
        or sha256_bytes(canonical_json_bytes(eligible_descriptors))
           != contract.eligible_projection_sha256
    ):
        raise SeedBindingError("SEALED_35_ROW_PROJECTION_MISMATCH")

    inherited_refs = [
        {
            "page_no": binding.page_no, "key": binding.key,
            "version_id": binding.version_id, "sha256": binding.sha256,
            "bytes": binding.bytes, "etag": binding.etag,
        }
        for binding in contract.raw_bindings
    ]
    checkpoint: dict[str, Any] = {
        "artifact": CHECKPOINT_ARTIFACT,
        "schema_version": 1,
        "checkpoint_revision": 0,
        "state": "IN_PROGRESS",
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "governed_correction_commit": contract.correction_head,
        "owner_decision_git_blob": contract.owner_blob,
        "owner_decision_sha256": contract.owner_sha256,
        "ordered_dates": list(contract.primary_dates),
        "request_page_size": contract.request_page_size,
        "max_pages_per_date": contract.max_pages_per_date,
        "budget": {
            "inherited_g10_acquisitions": INHERITED_G10_ACQUISITIONS,
            "inherited_g10_attempts": INHERITED_G10_ATTEMPTS,
            "g11_primary_acquisitions": 0,
            "g11_network_attempts": 0,
            "g11_provider_calls": 0,
            "g11_quota_reservations": 0,
            "g11_raw_writes": 0,
            "g11_primary_acquisition_ceiling": contract.g11_acquisition_ceiling,
            "g11_network_attempt_ceiling": contract.g11_attempt_ceiling,
            "max_attempts_per_logical_page": contract.attempts_per_page,
        },
        "execution_claim": None,
        "completed_dates": [contract.primary_dates[0]],
        "next_date_index": 1,
        "date_results": [{
            "basDt": contract.primary_dates[0], "state": "INHERITED_COMPLETE",
            "page_count": 8, "item_count": 76, "total_count": 76,
        }],
        "current_date": {
            "basDt": contract.seed_base_date,
            "total_count": contract.seed_total_count,
            "page_size": contract.request_page_size,
            "expected_pages": contract.seed_expected_pages,
            "validated_pages": inherited_refs,
            "page_fingerprints": page_fingerprints,
            "cumulative_item_count": contract.seed_source_rows,
            "next_page": contract.first_new_page,
        },
        "projection": {
            "source_rows": contract.seed_source_rows,
            "eligible_rows": contract.seed_eligible_rows,
            "excluded_rows": contract.seed_excluded_rows,
            "missing_rows": 0,
            "conflict_rows": 0,
            "excluded_global_row_ordinals": list(contract.excluded_ordinals),
            "future_selector_observed": False,
            "eligible_descriptors": eligible_descriptors,
            "eligible_projection_sha256": contract.eligible_projection_sha256,
            "identity_hashes_by_custody_sha256": dict(sorted(filtered_map.items())),
        },
        "inherited_g10": {
            "checkpoint": {
                "key": contract.checkpoint_binding.key,
                "version_id": contract.checkpoint_binding.version_id,
                "sha256": contract.checkpoint_binding.sha256,
                "bytes": contract.checkpoint_binding.bytes,
                "etag": contract.checkpoint_binding.etag,
                "revision": 27,
            },
            "raw_pages": inherited_refs,
            "predecessor_mutated": False,
            "reacquired_pages": [],
        },
        "attempts": [],
        "raw_index": [],
        "unique_page_slots": [],
        "terminal": None,
    }
    assert_hash_only_output(checkpoint, sensitive_values)
    return SeedState(checkpoint=checkpoint, sensitive_values=frozenset(sensitive_values))


CHECKPOINT_READ_ROLE = "CHECKPOINT_READ"
RAW_READ_ROLE = "RAW_READ"
FINAL_LIST_WRITE_ROLE = "FINAL_LIST_WRITE"
AWS_CREDENTIAL_ROLES = (
    CHECKPOINT_READ_ROLE, RAW_READ_ROLE, FINAL_LIST_WRITE_ROLE,
)
LIVE_AWS_CREDENTIAL_ENV = {
    CHECKPOINT_READ_ROLE: (
        "G11C8_CHECKPOINT_READ_AWS_ACCESS_KEY_ID",
        "G11C8_CHECKPOINT_READ_AWS_SECRET_ACCESS_KEY",
        "G11C8_CHECKPOINT_READ_AWS_SESSION_TOKEN",
    ),
    RAW_READ_ROLE: (
        "G11C8_RAW_FOUR_READ_AWS_ACCESS_KEY_ID",
        "G11C8_RAW_FOUR_READ_AWS_SECRET_ACCESS_KEY",
        "G11C8_RAW_FOUR_READ_AWS_SESSION_TOKEN",
    ),
    FINAL_LIST_WRITE_ROLE: (
        "G11C8_FINAL_LIST_WRITE_AWS_ACCESS_KEY_ID",
        "G11C8_FINAL_LIST_WRITE_AWS_SECRET_ACCESS_KEY",
        "G11C8_FINAL_LIST_WRITE_AWS_SESSION_TOKEN",
    ),
}
AMBIENT_AWS_CREDENTIAL_ENV_NAMES = frozenset({
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "AWS_SECURITY_TOKEN", "AWS_PROFILE", "AWS_DEFAULT_PROFILE",
    "AWS_SHARED_CREDENTIALS_FILE", "AWS_CONFIG_FILE",
    "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_ROLE_ARN", "AWS_ROLE_SESSION_NAME",
    "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "AWS_CONTAINER_CREDENTIALS_FULL_URI",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN", "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE",
})


@dataclass(frozen=True)
class AwsSessionCredentials:
    access_key_id: str
    secret_access_key: str
    session_token: str

    def __post_init__(self) -> None:
        values = (self.access_key_id, self.secret_access_key, self.session_token)
        if any(not value or value != value.strip() for value in values):
            raise GovernanceError("LIVE_AWS_CREDENTIAL_BUNDLE_INVALID")


def load_live_credential_bundles(
    environment: Mapping[str, str] | None = None,
) -> dict[str, AwsSessionCredentials]:
    """Load exactly three complete workflow-issued bundles, never ambient AWS auth."""

    env = os.environ if environment is None else environment
    bundles: dict[str, AwsSessionCredentials] = {}
    missing: list[str] = []
    for role in AWS_CREDENTIAL_ROLES:
        names = LIVE_AWS_CREDENTIAL_ENV[role]
        values = tuple(env.get(name, "") for name in names)
        missing.extend(name for name, value in zip(names, values) if not value)
        if all(values):
            bundles[role] = AwsSessionCredentials(*values)
    if missing or len(bundles) != 3:
        raise GovernanceError("G11C8_EXACT_THREE_CREDENTIAL_BUNDLES_REQUIRED")
    fingerprints = {
        sha256_bytes("\0".join((item.access_key_id, item.secret_access_key,
                                 item.session_token)).encode("utf-8"))
        for item in bundles.values()
    }
    if len(fingerprints) != 3:
        raise GovernanceError("G11C8_CREDENTIAL_BUNDLES_MUST_BE_DISTINCT")
    for field_name in ("access_key_id", "secret_access_key", "session_token"):
        if len({getattr(item, field_name) for item in bundles.values()}) != 3:
            raise GovernanceError("G11C8_CREDENTIAL_BUNDLES_MUST_BE_DISTINCT")
    return bundles


class AwsCliS3ObjectStore:
    """One role-bound AWS CLI client; cross-phase operations are impossible."""

    def __init__(
        self, *, credential_role: str, credentials: AwsSessionCredentials,
        exact_read_bindings: Sequence[ObjectBinding] = (),
        bucket: str = BUCKET, region: str = AWS_REGION,
        command_runner: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        if bucket != BUCKET or region != AWS_REGION:
            raise GovernanceError("AWS_CUSTODY_SCOPE_SHIFT")
        if credential_role not in AWS_CREDENTIAL_ROLES:
            raise GovernanceError("AWS_CREDENTIAL_ROLE_INVALID")
        if not isinstance(credentials, AwsSessionCredentials):
            raise GovernanceError("EXPLICIT_AWS_SESSION_CREDENTIALS_REQUIRED")
        if credential_role == CHECKPOINT_READ_ROLE and len(exact_read_bindings) != 1:
            raise GovernanceError("CHECKPOINT_READ_BINDING_COUNT_INVALID")
        if credential_role == RAW_READ_ROLE and len(exact_read_bindings) != 4:
            raise GovernanceError("RAW_READ_BINDING_COUNT_INVALID")
        if credential_role == FINAL_LIST_WRITE_ROLE and exact_read_bindings:
            raise GovernanceError("FINAL_ROLE_PREDECESSOR_BINDINGS_FORBIDDEN")
        self.bucket = bucket
        self.region = region
        self.credential_role = credential_role
        self.credentials = credentials
        self.exact_read_bindings = tuple(exact_read_bindings)
        self._exact_read_index = 0
        self._final_gate_complete = False
        self.command_runner = command_runner or self._default_runner
        self.api_calls: dict[str, int] = {"get": 0, "put": 0, "other": 0}

    def _command_environment(
        self, environment: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        source = os.environ if environment is None else environment
        command_env = {
            key: value for key, value in source.items()
            if key not in AMBIENT_AWS_CREDENTIAL_ENV_NAMES
            and key not in {
                name for names in LIVE_AWS_CREDENTIAL_ENV.values() for name in names
            }
            and key != "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY"
        }
        command_env.update({
            "AWS_ACCESS_KEY_ID": self.credentials.access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.credentials.secret_access_key,
            "AWS_SESSION_TOKEN": self.credentials.session_token,
            "AWS_REGION": self.region,
            "AWS_DEFAULT_REGION": self.region,
            "AWS_PAGER": "",
            "AWS_MAX_ATTEMPTS": "1",
            "AWS_EC2_METADATA_DISABLED": "true",
        })
        return command_env

    def _default_runner(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command), check=False, capture_output=True, text=True,
            timeout=30.0, env=self._command_environment(),
        )

    def _base(self, operation: str) -> list[str]:
        return [
            "aws", "s3api", operation, "--bucket", self.bucket,
            "--region", self.region, "--no-cli-pager", "--output", "json",
        ]

    def _run(self, command: Sequence[str], code: str) -> dict[str, Any]:
        operation = command[2] if len(command) > 2 else ""
        category = (
            "get" if operation == "get-object"
            else "put" if operation == "put-object"
            else "other"
        )
        self.api_calls[category] += 1
        try:
            completed = self.command_runner(command)
        except (OSError, subprocess.SubprocessError) as exc:
            raise CustodyError(code) from exc
        if completed.returncode != 0:
            # S3 conditional failures are known non-mutations, not uncertain
            # transport outcomes.  Do not perform an unversioned reconciliation
            # read for claim contention or checkpoint CAS contention.
            stderr = completed.stderr or ""
            if operation == "put-object" and any(
                token in stderr
                for token in ("PreconditionFailed", "ConditionalRequestConflict")
            ):
                raise ConditionalWriteConflict(code)
            raise CustodyError(code)
        try:
            value = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise CustodyError("AWS_CLI_JSON_INVALID") from exc
        if not isinstance(value, dict):
            raise CustodyError("AWS_CLI_JSON_INVALID")
        return value

    def _get(self, key: str, version_id: str | None) -> VersionedObject:
        with tempfile.NamedTemporaryFile(prefix="g11-s3-get-", delete=False) as handle:
            target = Path(handle.name)
        try:
            command = self._base("get-object") + ["--key", key]
            if version_id is not None:
                command += ["--version-id", version_id]
            command.append(str(target))
            metadata = self._run(command, "S3_EXACT_READ_FAILED")
            try:
                body = target.read_bytes()
            except OSError as exc:
                raise CustodyError("S3_GET_BODY_READ_FAILED") from exc
        finally:
            target.unlink(missing_ok=True)
        user = metadata.get("Metadata") or {}
        if not isinstance(user, Mapping):
            raise CustodyError("S3_METADATA_INVALID")
        return VersionedObject(
            key=key,
            version_id=str(metadata.get("VersionId") or ""),
            etag=str(metadata.get("ETag") or ""),
            body=body,
            content_type=str(metadata.get("ContentType") or ""),
            server_side_encryption=str(metadata.get("ServerSideEncryption") or ""),
            metadata={str(k): str(v) for k, v in user.items()},
        )

    def exact_read(self, binding: ObjectBinding) -> VersionedObject:
        if self.credential_role == FINAL_LIST_WRITE_ROLE:
            raise GovernanceError("FINAL_ROLE_PREDECESSOR_READ_FORBIDDEN")
        if self._exact_read_index >= len(self.exact_read_bindings):
            raise GovernanceError("ROLE_EXACT_READ_CEILING_EXCEEDED")
        expected = self.exact_read_bindings[self._exact_read_index]
        if binding != expected:
            raise GovernanceError("ROLE_EXACT_READ_ORDER_OR_SCOPE_MISMATCH")
        if not binding.version_id:
            raise CustodyError("EXACT_VERSION_REQUIRED")
        observed = self._get(binding.key, binding.version_id)
        self._exact_read_index += 1
        return observed

    def pre_mutation_gate(self) -> None:
        """Prove the three fresh namespaces empty immediately before mutation.

        Bucket region and Enabled versioning remain sealed-evidence reuse; LIVE
        calls neither bucket metadata operation.  These are the only three
        policy-bounded ListObjectVersions reads.  The following conditional
        claim independently protects against a list/create TOCTOU race.
        """

        if self.credential_role != FINAL_LIST_WRITE_ROLE:
            raise GovernanceError("READ_ROLE_LIST_OR_WRITE_FORBIDDEN")
        if self._final_gate_complete:
            raise GovernanceError("FINAL_LIST_GATE_REUSE_FORBIDDEN")
        if (
            self.bucket != BUCKET or self.region != AWS_REGION
            or not G11C8_RAW_PREFIX.startswith(SOURCE_PREFIX)
            or not G11C8_CONTROL_PREFIX.startswith(SOURCE_PREFIX)
            or not EXECUTION_CLAIM_KEY.startswith(SOURCE_PREFIX)
        ):
            raise GovernanceError("STATIC_CUSTODY_SCOPE_MISMATCH")
        for prefix in (G11C8_RAW_PREFIX, G11C8_CONTROL_PREFIX, EXECUTION_CLAIM_KEY):
            query = (
                "{IsTruncated:IsTruncated,Prefix:Prefix,MaxKeys:MaxKeys,"
                "Versions:Versions || `[]`,DeleteMarkers:DeleteMarkers || `[]`}"
            )
            listing = self._run(
                self._base("list-object-versions")
                + ["--prefix", prefix, "--max-keys", "2", "--query", query],
                "FRESH_NAMESPACE_LIST_FAILED",
            )
            versions = listing.get("Versions")
            markers = listing.get("DeleteMarkers")
            if (
                set(listing) != {
                    "IsTruncated", "Prefix", "MaxKeys", "Versions", "DeleteMarkers"
                }
                or listing.get("IsTruncated") is not False
                or listing.get("Prefix") != prefix
                or listing.get("MaxKeys") != 2
                or not isinstance(versions, list) or not isinstance(markers, list)
                or versions or markers
            ):
                raise GovernanceError("FRESH_G11C8_IDENTITY_ALREADY_CONSUMED")
        self._final_gate_complete = True

    def _put(
        self, key: str, body: bytes, *, content_type: str,
        metadata: Mapping[str, str], precondition: Sequence[str], code: str,
    ) -> VersionedObject:
        safe_metadata = {str(k): str(v) for k, v in metadata.items()}
        with tempfile.NamedTemporaryFile(prefix="g11-s3-put-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            command = self._base("put-object") + [
                "--key", key, "--body", str(target),
                "--content-type", content_type,
                "--server-side-encryption", "AES256",
                *precondition,
                "--metadata", ",".join(
                    f"{name}={safe_metadata[name]}" for name in sorted(safe_metadata)
                ),
            ]
            try:
                result = self._run(command, code)
                version_id = str(result.get("VersionId") or "")
                if not version_id:
                    raise AmbiguousSideEffectError("S3_WRITE_VERSION_ID_MISSING")
                observed = self._get(key, version_id)
            except ConditionalWriteConflict:
                raise
            except CustodyError as write_error:
                # One readback resolves an uncertain CLI return without issuing a
                # second write.  The per-process nonce in metadata prevents a
                # prior activation from being adopted.
                try:
                    observed = self._get(key, None)
                except CustodyError as read_error:
                    raise AmbiguousSideEffectError("S3_WRITE_EFFECT_AMBIGUOUS") from read_error
                if (
                    observed.body != body or observed.content_type != content_type
                    or dict(observed.metadata) != safe_metadata
                ):
                    raise AmbiguousSideEffectError(
                        "S3_WRITE_EFFECT_AMBIGUOUS_MISMATCH"
                    ) from write_error
            if (
                observed.body != body or observed.content_type != content_type
                or observed.server_side_encryption != "AES256"
                or dict(observed.metadata) != safe_metadata
                or not observed.version_id or not observed.etag
            ):
                raise AmbiguousSideEffectError("S3_WRITE_READBACK_MISMATCH")
            return observed
        finally:
            target.unlink(missing_ok=True)

    def create_once(
        self, key: str, body: bytes, *, content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject:
        if self.credential_role != FINAL_LIST_WRITE_ROLE or not self._final_gate_complete:
            raise GovernanceError("FINAL_WRITE_PHASE_NOT_OPEN")
        if not (
            key == EXECUTION_CLAIM_KEY
            or key.startswith(G11C8_RAW_PREFIX)
            or key.startswith(G11C8_CONTROL_PREFIX)
        ):
            raise CustodyError("APPEND_ONLY_NAMESPACE_ESCAPE")
        return self._put(
            key, body, content_type=content_type, metadata=metadata,
            precondition=("--if-none-match", "*"), code="S3_CONDITIONAL_CREATE_FAILED",
        )

    def compare_and_swap(
        self, key: str, body: bytes, *, expected_etag: str,
        content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject:
        if self.credential_role != FINAL_LIST_WRITE_ROLE or not self._final_gate_complete:
            raise GovernanceError("FINAL_WRITE_PHASE_NOT_OPEN")
        if key != G11C8_CHECKPOINT_KEY or not expected_etag:
            raise CustodyError("CHECKPOINT_CAS_SCOPE_INVALID")
        return self._put(
            key, body, content_type=content_type, metadata=metadata,
            precondition=("--if-match", expected_etag), code="CHECKPOINT_CAS_FAILED",
        )


class PhaseSeparatedS3ObjectStore:
    """One-way checkpoint -> raw -> final handoff across three clients."""

    def __init__(
        self, *, checkpoint_client: AwsCliS3ObjectStore,
        raw_client: AwsCliS3ObjectStore, final_client: AwsCliS3ObjectStore,
        checkpoint_binding: ObjectBinding, raw_bindings: Sequence[ObjectBinding],
    ) -> None:
        if (
            checkpoint_client is raw_client or checkpoint_client is final_client
            or raw_client is final_client
            or checkpoint_client.credential_role != CHECKPOINT_READ_ROLE
            or raw_client.credential_role != RAW_READ_ROLE
            or final_client.credential_role != FINAL_LIST_WRITE_ROLE
            or tuple(checkpoint_client.exact_read_bindings) != (checkpoint_binding,)
            or tuple(raw_client.exact_read_bindings) != tuple(raw_bindings)
            or len(raw_bindings) != 4
        ):
            raise GovernanceError("G11C8_PHASE_CLIENT_BINDING_INVALID")
        self.checkpoint_client = checkpoint_client
        self.raw_client = raw_client
        self.final_client = final_client
        self.checkpoint_binding = checkpoint_binding
        self.raw_bindings = tuple(raw_bindings)
        self._read_index = 0
        self._final_open = False

    @property
    def api_calls(self) -> dict[str, int]:
        return {
            category: sum(client.api_calls[category] for client in (
                self.checkpoint_client, self.raw_client, self.final_client
            ))
            for category in ("get", "put", "other")
        }

    def exact_read(self, binding: ObjectBinding) -> VersionedObject:
        expected = (self.checkpoint_binding, *self.raw_bindings)
        if self._final_open or self._read_index >= len(expected) or binding != expected[self._read_index]:
            raise GovernanceError("G11C8_ONE_WAY_READ_PHASE_VIOLATION")
        client = self.checkpoint_client if self._read_index == 0 else self.raw_client
        observed = client.exact_read(binding)
        self._read_index += 1
        return observed

    def pre_mutation_gate(self) -> None:
        if self._read_index != 5 or self._final_open:
            raise GovernanceError("G11C8_FINAL_PHASE_HANDOFF_INVALID")
        self.final_client.pre_mutation_gate()
        self._final_open = True

    def create_once(
        self, key: str, body: bytes, *, content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject:
        if not self._final_open:
            raise GovernanceError("G11C8_FINAL_PHASE_NOT_OPEN")
        return self.final_client.create_once(
            key, body, content_type=content_type, metadata=metadata,
        )

    def compare_and_swap(
        self, key: str, body: bytes, *, expected_etag: str,
        content_type: str, metadata: Mapping[str, str]
    ) -> VersionedObject:
        if not self._final_open:
            raise GovernanceError("G11C8_FINAL_PHASE_NOT_OPEN")
        return self.final_client.compare_and_swap(
            key, body, expected_etag=expected_etag,
            content_type=content_type, metadata=metadata,
        )


class BoundedFinanceProvider:
    MAX_ENTITY_BYTES = 2_000_000

    def __init__(
        self, service_key: str, *, timeout_seconds: float = 20.0,
        opener: Any | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        monotonic_fn: Callable[[], float] = time.monotonic,
        deadline_monotonic: float | None = None,
    ) -> None:
        if (
            not service_key or service_key != service_key.strip()
            or any(ch.isspace() for ch in service_key)
            or re.search(r"%[0-9A-Fa-f]{2}", service_key)
        ):
            raise GovernanceError("FINANCE_SERVICE_KEY_FORMAT_INVALID")
        if not 0 < timeout_seconds <= 20:
            raise GovernanceError("PROVIDER_TIMEOUT_BOUND_INVALID")
        self._service_key = service_key
        self.timeout_seconds = timeout_seconds
        self.opener = opener or urllib.request.build_opener(_NoRedirect())
        self.clock = clock
        self.monotonic_fn = monotonic_fn
        self.deadline_monotonic = deadline_monotonic

    def _read(self, stream: Any) -> bytes:
        chunks: list[bytes] = []
        size = 0
        while True:
            if self.deadline_monotonic is not None and self.monotonic_fn() >= self.deadline_monotonic:
                raise ProviderError("LIVE_SELF_DEADLINE_REACHED")
            chunk = stream.read(min(65_536, self.MAX_ENTITY_BYTES + 1 - size))
            if not isinstance(chunk, bytes):
                raise ProviderError("PROVIDER_ENTITY_NON_BYTES")
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            size += len(chunk)
            if size > self.MAX_ENTITY_BYTES:
                raise ProviderError("PROVIDER_ENTITY_TOO_LARGE")

    def fetch_once(self, params: Mapping[str, str]) -> ProviderResponse:
        now_value = self.clock()
        if not isinstance(now_value, datetime) or now_value.tzinfo is None:
            raise GovernanceError("CLOCK_MUST_BE_TIMEZONE_AWARE")
        now = now_value.astimezone(timezone.utc)
        if now.astimezone(KST).date().isoformat() != QUOTA_DAY_KST:
            raise BudgetError("FROZEN_KST_QUOTA_DAY_CLOSED")
        if self.deadline_monotonic is not None and self.monotonic_fn() >= self.deadline_monotonic:
            raise ProviderError("LIVE_SELF_DEADLINE_REACHED")
        clean = {str(k): str(v) for k, v in params.items() if k != "serviceKey"}
        clean["serviceKey"] = self._service_key
        url = FINANCE_URL + "?" + urllib.parse.urlencode(clean, doseq=False)
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json", "Accept-Encoding": "identity",
                "User-Agent": "AAA-M3Top3-Finance-Page100-G11C8/1.0",
            },
        )
        socket_opened = now.isoformat()
        try:
            response = self.opener.open(request, timeout=self.timeout_seconds)
            status = int(getattr(response, "status", response.getcode()))
            body = self._read(response)
            headers = response.headers
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            body = self._read(exc)
            headers = exc.headers
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError("PROVIDER_NO_RESPONSE_ENTITY") from exc
        encoded = {
            self._service_key.encode("utf-8"),
            urllib.parse.quote(self._service_key, safe="").encode("ascii"),
            urllib.parse.quote_plus(self._service_key, safe="").encode("ascii"),
        }
        if any(secret and secret in body for secret in encoded):
            raise ProviderError("SECRET_BEARING_RESPONSE_REJECTED")
        received_value = self.clock()
        if not isinstance(received_value, datetime) or received_value.tzinfo is None:
            raise GovernanceError("CLOCK_MUST_BE_TIMEZONE_AWARE")
        received = received_value.astimezone(timezone.utc).isoformat()
        safe_headers = {
            str(k).lower(): str(v) for k, v in headers.items()
            if str(k).lower() in {"content-type", "content-length", "date", "etag", "last-modified"}
        }
        return ProviderResponse(
            body=body, http_status=status, socket_opened_at_utc=socket_opened,
            response_received_at_utc=received, safe_headers=safe_headers,
        )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


class G11LiveAdapter:
    def __init__(
        self, *, contract: LiveContract, governance: GovernanceBundle | None,
        store: ObjectStore, provider: FinanceProvider,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        monotonic_fn: Callable[[], float] = time.monotonic,
        deadline_monotonic: float | None = None,
        invocation_nonce: str | None = None,
    ) -> None:
        _validate_production_contract(contract)
        self.contract = contract
        self.governance = governance
        self.store = store
        self.provider = provider
        self.clock = clock
        self.monotonic_fn = monotonic_fn
        self.deadline_monotonic = deadline_monotonic
        nonce = invocation_nonce or secrets.token_hex(32)
        if not HEX64.fullmatch(nonce):
            raise GovernanceError("INVOCATION_NONCE_INVALID")
        self.invocation_nonce_sha256 = sha256_bytes(nonce.encode("ascii"))
        self.effects = EffectLedger()
        self.checkpoint: dict[str, Any] | None = None
        self.checkpoint_object: VersionedObject | None = None
        self.claim_object: VersionedObject | None = None
        self.terminal_receipt_object: VersionedObject | None = None
        self.terminal_receipt_attempted = False
        self.sensitive_values: set[str] = set()

    def _now(self) -> str:
        value = self.clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise GovernanceError("CLOCK_MUST_BE_TIMEZONE_AWARE")
        return value.astimezone(timezone.utc).isoformat()

    def _kst_day(self) -> str:
        value = self.clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise GovernanceError("CLOCK_MUST_BE_TIMEZONE_AWARE")
        return value.astimezone(KST).date().isoformat()

    def _deadline_guard(self) -> None:
        if self.deadline_monotonic is not None and self.monotonic_fn() >= self.deadline_monotonic:
            raise ProviderError("LIVE_SELF_DEADLINE_REACHED")

    def _metadata(self, artifact: str, revision: int | None = None) -> dict[str, str]:
        value = {
            "artifact": artifact,
            "generation-id": GENERATION_ID,
            "runtime-lock-id": RUNTIME_LOCK_ID,
            "pilot-run-id": PILOT_RUN_ID,
            "execution-nonce-sha256": self.invocation_nonce_sha256,
        }
        if revision is not None:
            value["checkpoint-revision"] = str(revision)
        return value

    def _save_checkpoint(self, *, initial: bool = False) -> None:
        assert self.checkpoint is not None
        if self.effects.checkpoint_writes >= CHECKPOINT_WRITE_CEILING:
            raise BudgetError("G11C8_CHECKPOINT_WRITE_CEILING")
        if not initial:
            self.checkpoint["checkpoint_revision"] += 1
        self.checkpoint["updated_at_utc"] = self._now()
        self._assert_checkpoint()
        body = canonical_json_bytes(self.checkpoint)
        assert_hash_only_output(self.checkpoint, self.sensitive_values)
        metadata = self._metadata(
            CHECKPOINT_ARTIFACT, int(self.checkpoint["checkpoint_revision"])
        )
        metadata["sha256"] = sha256_bytes(body)
        self.effects.s3_put_calls += 1
        if initial:
            observed = self.store.create_once(
                G11C8_CHECKPOINT_KEY, body, content_type="application/json", metadata=metadata
            )
        else:
            if self.checkpoint_object is None:
                raise CustodyError("CHECKPOINT_CAS_TOKEN_MISSING")
            observed = self.store.compare_and_swap(
                G11C8_CHECKPOINT_KEY, body, expected_etag=self.checkpoint_object.etag,
                content_type="application/json", metadata=metadata,
            )
        if observed.body != body or observed.sha256 != metadata["sha256"]:
            raise AmbiguousSideEffectError("CHECKPOINT_READBACK_MISMATCH")
        self.checkpoint_object = observed
        self.effects.checkpoint_writes += 1

    def _assert_checkpoint(self) -> None:
        assert self.checkpoint is not None
        checkpoint = self.checkpoint
        if (
            checkpoint.get("artifact") != CHECKPOINT_ARTIFACT
            or checkpoint.get("generation_id") != GENERATION_ID
            or checkpoint.get("runtime_lock_id") != RUNTIME_LOCK_ID
            or checkpoint.get("pilot_run_id") != PILOT_RUN_ID
            or checkpoint.get("governed_correction_commit") != self.contract.correction_head
            or checkpoint.get("state") not in {"IN_PROGRESS", "BLOCKED", "COMPLETE"}
            or checkpoint.get("ordered_dates") != list(self.contract.primary_dates)
        ):
            raise CustodyError("G11C8_CHECKPOINT_BINDING_MISMATCH")
        budget = checkpoint.get("budget")
        attempts = checkpoint.get("attempts")
        raw_index = checkpoint.get("raw_index")
        slots = checkpoint.get("unique_page_slots")
        projection = checkpoint.get("projection")
        if not all(isinstance(v, list) for v in (attempts, raw_index, slots)):
            raise CustodyError("G11C8_CHECKPOINT_COLLECTION_INVALID")
        if not isinstance(budget, Mapping) or not isinstance(projection, Mapping):
            raise CustodyError("G11C8_CHECKPOINT_MAPPING_INVALID")
        if (
            budget.get("g11_primary_acquisitions") != len(slots)
            or budget.get("g11_network_attempts") != len(attempts)
            or budget.get("g11_quota_reservations") != len(attempts)
            or budget.get("g11_provider_calls")
               != sum(row.get("provider_call_started") is True for row in attempts)
            or budget.get("g11_raw_writes") != len(raw_index)
            or len(slots) > self.contract.g11_acquisition_ceiling
            or len(attempts) > self.contract.g11_attempt_ceiling
            or len(raw_index) > self.contract.g11_acquisition_ceiling
        ):
            raise CustodyError("G11C8_CHECKPOINT_COUNTER_MISMATCH")
        if (
            projection.get("source_rows")
            != projection.get("eligible_rows") + projection.get("excluded_rows")
               + projection.get("missing_rows")
            or projection.get("excluded_rows") != self.contract.seed_excluded_rows
            or projection.get("excluded_global_row_ordinals")
               != list(self.contract.excluded_ordinals)
            or projection.get("missing_rows") != 0
            or projection.get("conflict_rows") != 0
            or self.contract.selector_sha256
               in projection.get("identity_hashes_by_custody_sha256", {})
        ):
            raise CustodyError("G11C8_PROJECTION_ACCOUNTING_MISMATCH")

    def _claim(self) -> None:
        if self.effects.execution_claim_writes >= EXECUTION_CLAIM_WRITE_CEILING:
            raise BudgetError("G11C8_EXECUTION_CLAIM_WRITE_CEILING")
        if self.governance is None:
            run_id, run_attempt = 1, 1
            activation_sha = "0" * 64
        else:
            run_id = self.governance.github_run_id
            run_attempt = self.governance.github_run_attempt
            activation_sha = self.governance.sha256["live_activation"]
        claim = {
            "artifact": "M3TOP3_FINANCE_PAGE100_G11C8_EXECUTION_CLAIM_v1.0",
            "state": "SINGLE_WRITER_CLAIMED",
            "generation_id": GENERATION_ID,
            "runtime_lock_id": RUNTIME_LOCK_ID,
            "pilot_run_id": PILOT_RUN_ID,
            "live_act_id": LIVE_ACT_ID,
            "latch_event_id": LATCH_EVENT_ID,
            "github_run_id": run_id,
            "github_run_attempt": run_attempt,
            "governed_correction_commit": self.contract.correction_head,
            "live_activation_sha256": activation_sha,
            "execution_nonce_sha256": self.invocation_nonce_sha256,
            "quota_day_kst": QUOTA_DAY_KST,
            "same_run_retry_authorized": False,
            "same_activation_reuse_authorized": False,
        }
        body = canonical_json_bytes(claim)
        metadata = self._metadata(claim["artifact"])
        metadata["sha256"] = sha256_bytes(body)
        self.effects.s3_put_calls += 1
        observed = self.store.create_once(
            EXECUTION_CLAIM_KEY, body, content_type="application/json", metadata=metadata
        )
        if observed.body != body:
            raise AmbiguousSideEffectError("EXECUTION_CLAIM_READBACK_MISMATCH")
        self.claim_object = observed
        self.effects.execution_claim_writes += 1

    def _initialize(self) -> None:
        # The fixed KST quota day is a freshness gate for this one generation.
        # A stale runtime performs neither predecessor reads nor any mutation.
        if self._kst_day() != QUOTA_DAY_KST:
            raise BudgetError("FROZEN_KST_QUOTA_DAY_CLOSED")

        def count_exact_read() -> None:
            self.effects.s3_get_calls += 1

        seed = recover_seed(
            self.store, self.contract, on_exact_read=count_exact_read
        )
        self.sensitive_values.update(seed.sensitive_values)
        self.checkpoint = copy.deepcopy(dict(seed.checkpoint))
        # The first five S3 commands are necessarily the exact predecessor
        # checkpoint + four raw GetObjectVersion reads.  Only after their
        # content and metadata validate may these three read-only namespace
        # checks run; no claim/provider/write precedes them.
        self.store.pre_mutation_gate()
        # Re-check immediately before the first mutation so a quota-day
        # boundary crossed during the eight read-only gates cannot create a
        # stale-day claim.
        if self._kst_day() != QUOTA_DAY_KST:
            raise BudgetError("FROZEN_KST_QUOTA_DAY_CLOSED_BEFORE_CLAIM")
        self._claim()
        assert self.claim_object is not None
        self.checkpoint["execution_claim"] = {
            "key": self.claim_object.key,
            "version_id": self.claim_object.version_id,
            "etag": self.claim_object.etag,
            "sha256": self.claim_object.sha256,
        }
        self._save_checkpoint(initial=True)

    def _reserve(self, bas_dt: str, page_no: int) -> dict[str, Any]:
        assert self.checkpoint is not None
        self._deadline_guard()
        if self._kst_day() != QUOTA_DAY_KST:
            raise BudgetError("FROZEN_KST_QUOTA_DAY_CLOSED")
        slot = f"{bas_dt}:{page_no}"
        attempts = [
            row for row in self.checkpoint["attempts"]
            if row.get("basDt") == bas_dt and row.get("page_no") == page_no
        ]
        if len(attempts) >= self.contract.attempts_per_page:
            raise BudgetError("PER_PAGE_ATTEMPT_CEILING")
        if len(self.checkpoint["attempts"]) >= self.contract.g11_attempt_ceiling:
            raise BudgetError("G11C8_NETWORK_ATTEMPT_CEILING")
        if slot not in self.checkpoint["unique_page_slots"]:
            if len(self.checkpoint["unique_page_slots"]) >= self.contract.g11_acquisition_ceiling:
                raise BudgetError("G11C8_ACQUISITION_CEILING")
            self.checkpoint["unique_page_slots"].append(slot)
            self.effects.primary_acquisitions += 1
        attempt_no = len(attempts) + 1
        record = {
            "basDt": bas_dt, "page_no": page_no, "attempt": attempt_no,
            "request_id": request_id(bas_dt, page_no),
            "raw_object_prefix": raw_prefix(bas_dt, page_no, attempt_no),
            "state": "RESERVED_WRITE_AHEAD",
            "reserved_at_utc": self._now(),
            "provider_call_started": False,
            "response_entity_received": False,
        }
        self.checkpoint["attempts"].append(record)
        budget = self.checkpoint["budget"]
        budget["g11_primary_acquisitions"] = len(self.checkpoint["unique_page_slots"])
        budget["g11_network_attempts"] = len(self.checkpoint["attempts"])
        budget["g11_quota_reservations"] = len(self.checkpoint["attempts"])
        self.effects.network_attempts += 1
        self.effects.quota_reservations += 1
        self._save_checkpoint()
        return record

    def _call_and_custody(
        self, bas_dt: str, page_no: int, record: dict[str, Any]
    ) -> tuple[ProviderResponse, VersionedObject]:
        assert self.checkpoint is not None and self.claim_object is not None
        if self.effects.raw_writes >= self.contract.g11_acquisition_ceiling:
            raise BudgetError("G11C8_RAW_WRITE_CEILING")
        record["provider_call_started"] = True
        record["provider_call_started_at_utc"] = self._now()
        record["execution_claim_version_id"] = self.claim_object.version_id
        self.checkpoint["budget"]["g11_provider_calls"] += 1
        self.effects.provider_calls += 1
        self._save_checkpoint()
        response = self.provider.fetch_once(request_params(bas_dt, page_no))
        digest = sha256_bytes(response.body)
        key = record["raw_object_prefix"] + f"sha256={digest}.entity"
        metadata = {
            "sha256": digest,
            "http-status": str(response.http_status),
            "request-id": record["request_id"],
            "bas-dt": bas_dt,
            "page-no": str(page_no),
            "attempt": str(record["attempt"]),
            "generation-id": GENERATION_ID,
            "runtime-lock-id": RUNTIME_LOCK_ID,
            "pilot-run-id": PILOT_RUN_ID,
            "quota-day-kst": QUOTA_DAY_KST,
            "provider-call-started-at-utc": record["provider_call_started_at_utc"],
            "socket-opened-at-utc": response.socket_opened_at_utc,
            "response-received-at-utc": response.response_received_at_utc,
            "execution-claim-version-id": self.claim_object.version_id,
            "execution-nonce-sha256": self.invocation_nonce_sha256,
        }
        self.effects.s3_put_calls += 1
        sealed = self.store.create_once(
            key, response.body, content_type="application/octet-stream", metadata=metadata
        )
        if sealed.body != response.body or sealed.sha256 != digest:
            raise AmbiguousSideEffectError("RAW_CUSTODY_READBACK_MISMATCH")
        self.effects.raw_writes += 1
        record.update({
            "state": "RAW_SEALED_BEFORE_PARSE",
            "response_entity_received": True,
            "http_status": response.http_status,
            "entity_sha256": digest,
            "entity_bytes": len(response.body),
            "s3_object_key": key,
            "s3_version_id": sealed.version_id,
            "s3_etag": sealed.etag,
            "socket_opened_at_utc": response.socket_opened_at_utc,
            "response_received_at_utc": response.response_received_at_utc,
        })
        self.checkpoint["raw_index"].append({
            "basDt": bas_dt, "page_no": page_no, "attempt": record["attempt"],
            "s3_object_key": key, "s3_version_id": sealed.version_id,
            "s3_etag": sealed.etag, "entity_sha256": digest,
            "entity_bytes": len(response.body), "http_status": response.http_status,
        })
        self.checkpoint["budget"]["g11_raw_writes"] = len(self.checkpoint["raw_index"])
        self._save_checkpoint()
        return response, sealed

    def _classify_page(
        self, bas_dt: str, page_no: int, sealed: VersionedObject,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str], set[str]]:
        assert self.checkpoint is not None
        current = self.checkpoint["current_date"]
        page = parse_finance_page(
            sealed.body, expected_bas_dt=bas_dt, expected_page_no=page_no,
            expected_page_size=self.contract.request_page_size,
        )
        total = page["total_count"]
        expected_pages = max(1, math.ceil(total / self.contract.request_page_size))
        if expected_pages > self.contract.max_pages_per_date:
            raise PaginationDriftError("PAGE_CEILING_EXCEEDED")
        if page_no == 1:
            if current["validated_pages"]:
                raise PaginationDriftError("PAGE_ONE_AFTER_VALIDATED_PAGE")
            current["total_count"] = total
            current["page_size"] = self.contract.request_page_size
            current["expected_pages"] = expected_pages
        elif (
            total != current["total_count"]
            or self.contract.request_page_size != current["page_size"]
            or expected_pages != current["expected_pages"]
        ):
            raise PaginationDriftError("PAGINATION_SNAPSHOT_DRIFT")
        items = page["items"]
        cumulative = int(current["cumulative_item_count"]) + len(items)
        if cumulative > total:
            raise PaginationDriftError("PAGINATION_COUNT_EXCEEDED")
        if not items and cumulative < total:
            raise PaginationDriftError("EMPTY_INTERMEDIATE_PAGE")
        if page_no < expected_pages and len(items) != self.contract.request_page_size:
            raise PaginationDriftError("UNDERFILLED_INTERMEDIATE_PAGE")
        fingerprint = sha256_bytes(canonical_json_bytes(items))
        if items and fingerprint in current["page_fingerprints"]:
            raise PaginationDriftError("REPEATED_WHOLE_PAGE")

        projection = self.checkpoint["projection"]
        identities = dict(projection["identity_hashes_by_custody_sha256"])
        descriptors = list(projection["eligible_descriptors"])
        page_sensitive: set[str] = set()
        new_descriptors: list[dict[str, Any]] = []
        start_ordinal = int(projection["source_rows"])
        for page_item_ordinal, item in enumerate(items, 1):
            fields: dict[str, str] = {}
            for key in FORBIDDEN_CLEAR_KEYS:
                value = item.get(key)
                if not isinstance(value, str):
                    raise MissingIdentityError("IDENTITY_FIELD_TYPE_INVALID")
                fields[key] = value
                if value:
                    page_sensitive.add(value)
            custody = fields["issuCmpyKsdCustNo"]
            if not custody or custody != custody.strip() or not ASCII_CUSTODY.fullmatch(custody):
                raise MissingIdentityError("CUSTODY_MISSING_BLANK_OR_MALFORMED")
            if (
                not fields["crno"] or fields["crno"] != fields["crno"].strip()
                or not fields["stckIssuCmpyNm"]
                or fields["stckIssuCmpyNm"] != fields["stckIssuCmpyNm"].strip()
            ):
                raise MissingIdentityError("NON_TARGET_IDENTITY_MISSING_OR_BLANK")
            custody_hash = sha256_bytes(custody.encode("utf-8"))
            observed_identity = identity_digest(item)
            global_ordinal = start_ordinal + page_item_ordinal
            if custody_hash == self.contract.selector_sha256:
                raise FutureSelectorError(
                    "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION",
                    f"basDt={bas_dt} page={page_no} ordinal={global_ordinal}",
                )
            prior = identities.get(custody_hash)
            if prior is not None and prior != observed_identity:
                raise IdentityConflictError(
                    "NON_TARGET_IDENTITY_CONFLICT",
                    f"basDt={bas_dt} page={page_no} ordinal={global_ordinal}",
                )
            identities[custody_hash] = observed_identity
            descriptor = {
                "basDt": bas_dt, "custody_key_sha256": custody_hash,
                "global_row_ordinal": global_ordinal,
                "observed_identity_sha256": observed_identity,
                "page_item_ordinal": page_item_ordinal, "page_no": page_no,
            }
            descriptors.append(descriptor)
            new_descriptors.append(descriptor)
        return page, new_descriptors, identities, page_sensitive

    def _advance_page(
        self, page: Mapping[str, Any], descriptors: list[dict[str, Any]],
        identities: Mapping[str, str], sensitive: set[str], sealed: VersionedObject,
    ) -> None:
        assert self.checkpoint is not None
        current = self.checkpoint["current_date"]
        projection = self.checkpoint["projection"]
        items = page["items"]
        page_no = int(page["page_no"])
        cumulative = int(current["cumulative_item_count"]) + len(items)
        fingerprint = sha256_bytes(canonical_json_bytes(items))
        if items:
            current["page_fingerprints"].append(fingerprint)
        current["cumulative_item_count"] = cumulative
        current["validated_pages"].append({
            "page_no": page_no, "item_count": len(items),
            "cumulative_item_count": cumulative,
            "page_fingerprint_sha256": fingerprint,
            "entity_sha256": sealed.sha256, "s3_version_id": sealed.version_id,
        })
        current["next_page"] = page_no + 1
        projection["source_rows"] += len(items)
        projection["eligible_rows"] += len(descriptors)
        projection["eligible_descriptors"].extend(descriptors)
        projection["eligible_projection_sha256"] = sha256_bytes(
            canonical_json_bytes(projection["eligible_descriptors"])
        )
        projection["identity_hashes_by_custody_sha256"] = dict(sorted(identities.items()))
        self.sensitive_values.update(sensitive)
        assert_hash_only_output(self.checkpoint, self.sensitive_values)
        self._save_checkpoint()

    def _finish_date_if_complete(self) -> None:
        assert self.checkpoint is not None
        current = self.checkpoint["current_date"]
        if current["next_page"] <= current["expected_pages"]:
            return
        if current["cumulative_item_count"] != current["total_count"]:
            raise PaginationDriftError("PAGINATION_TOTAL_DID_NOT_CLOSE")
        self.checkpoint["date_results"].append({
            "basDt": current["basDt"], "state": "DATE_COMPLETE",
            "page_count": len(current["validated_pages"]),
            "item_count": current["cumulative_item_count"],
            "total_count": current["total_count"],
        })
        self.checkpoint["completed_dates"].append(current["basDt"])
        self.checkpoint["next_date_index"] += 1
        if self.checkpoint["next_date_index"] < len(self.contract.primary_dates):
            next_date = self.contract.primary_dates[self.checkpoint["next_date_index"]]
            self.checkpoint["current_date"] = {
                "basDt": next_date, "total_count": None,
                "page_size": None, "expected_pages": None,
                "validated_pages": [], "page_fingerprints": [],
                "cumulative_item_count": 0, "next_page": 1,
            }
        else:
            self.checkpoint["current_date"] = None
        self._save_checkpoint()

    def _acquire_page(self, bas_dt: str, page_no: int) -> None:
        last_error: LiveAdapterError | None = None
        for attempt_no in range(1, self.contract.attempts_per_page + 1):
            record = self._reserve(bas_dt, page_no)
            try:
                response, sealed = self._call_and_custody(bas_dt, page_no, record)
            except ProviderError as exc:
                record["state"] = "NO_RESPONSE_ENTITY_RESERVATION_SPENT"
                self._save_checkpoint()
                last_error = exc
                if attempt_no < self.contract.attempts_per_page:
                    continue
                raise
            try:
                socket_time = datetime.fromisoformat(
                    response.socket_opened_at_utc.replace("Z", "+00:00")
                )
                response_time = datetime.fromisoformat(
                    response.response_received_at_utc.replace("Z", "+00:00")
                )
                if socket_time.tzinfo is None or response_time.tzinfo is None:
                    raise ValueError("timezone required")
                socket_day = socket_time.astimezone(KST).date().isoformat()
                response_day = response_time.astimezone(KST).date().isoformat()
            except (TypeError, ValueError) as exc:
                raise ProviderError("PROVIDER_RESPONSE_TIMING_INVALID") from exc
            if socket_day != QUOTA_DAY_KST or response_day != QUOTA_DAY_KST:
                # The entity is already conditionally raw-custodied and its
                # reference is already CAS-persisted.  No parse/projection/cursor
                # advance is allowed after the fixed quota day boundary.
                record["state"] = "RESPONSE_QUOTA_DAY_CROSSED_AFTER_RAW_CUSTODY"
                self._save_checkpoint()
                raise BudgetError("RESPONSE_CROSSED_FROZEN_KST_QUOTA_DAY")
            if response.http_status == 429 or 500 <= response.http_status <= 599:
                record["state"] = "RETRYABLE_HTTP_ENTITY_CUSTODIED"
                self._save_checkpoint()
                last_error = ProviderError("RETRYABLE_HTTP_ENTITY_EXHAUSTED")
                if attempt_no < self.contract.attempts_per_page:
                    continue
                raise last_error
            if response.http_status != 200:
                record["state"] = "NONRETRYABLE_HTTP_ENTITY_CUSTODIED"
                self._save_checkpoint()
                raise ProviderError("NONSUCCESS_HTTP_ENTITY_CUSTODIED")
            page, descriptors, identities, sensitive = self._classify_page(
                bas_dt, page_no, sealed
            )
            record["state"] = "PARSED_AND_ELIGIBLE"
            self._advance_page(page, descriptors, identities, sensitive, sealed)
            return
        if last_error is not None:
            raise last_error

    def _block(self, error: LiveAdapterError) -> None:
        if self.checkpoint is None or self.checkpoint_object is None:
            return
        self.checkpoint["state"] = "BLOCKED"
        self.checkpoint["terminal"] = {
            "verdict": "FAIL_CLOSED", "error_code": error.code,
            "cursor_advanced_past_failure": False,
            "future_selector_auto_excluded": False,
        }
        if isinstance(error, FutureSelectorError):
            self.checkpoint["projection"]["future_selector_observed"] = True
        self._save_checkpoint()

    def _result(self, verdict: str, error: LiveAdapterError | None = None) -> dict[str, Any]:
        checkpoint = self.checkpoint or {}
        current = checkpoint.get("current_date") or {}
        projection = checkpoint.get("projection") or {}
        effects = self.effects.output()
        observed_api_calls = getattr(self.store, "api_calls", None)
        if isinstance(observed_api_calls, Mapping):
            s3_gets = int(observed_api_calls.get("get", 0))
            s3_puts = int(observed_api_calls.get("put", 0))
            s3_other = int(observed_api_calls.get("other", 0))
            effects["s3_get_calls"] = s3_gets
            effects["s3_put_calls"] = s3_puts
            effects["s3_other_calls"] = s3_other
            effects["s3_calls"] = s3_gets + s3_puts + s3_other
            effects["aws_calls"] = (
                PRECHECK_STS_EFFECTS["aws_calls"] + effects["s3_calls"]
            )
            effects["s3_get_attempts"] = s3_gets
            effects["s3_put_attempts"] = s3_puts
            effects["s3_other_read_calls"] = s3_other
            confirmed = int(effects["remote_custody_mutations"])
            effects["successful_put_mutations"] = confirmed
            effects["unconfirmed_or_failed_put_attempts"] = max(
                0, s3_puts - confirmed
            )
        if self.governance is None:
            execution_binding = {
                "repository": REPOSITORY, "branch": BRANCH,
                "github_run_id": 1, "github_run_attempt": 1,
                "github_job": "injected-test",
                "head_sha": self.contract.correction_head,
                "tree_sha": self.contract.correction_tree,
            }
            material_bindings: dict[str, Any] = {}
            receipt_bindings: dict[str, Any] = {}
        else:
            execution_binding = {
                "repository": REPOSITORY, "branch": BRANCH,
                "github_run_id": self.governance.github_run_id,
                "github_run_attempt": self.governance.github_run_attempt,
                "github_job": os.environ.get("GITHUB_JOB", ""),
                "head_sha": self.governance.live_head_sha,
                "tree_sha": self.governance.live_head_tree,
            }
            material_bindings = {
                role: {
                    "sha256": self.governance.sha256[role],
                    "git_blob": git_blob_sha(self.governance.raw[role]),
                    "bytes": len(self.governance.raw[role]),
                }
                for role in (
                    "authority", "plan", "seed", "manifest", "owner_decision"
                )
            }
            receipt_bindings = {
                "live_activation": {
                    "sha256": self.governance.sha256["live_activation"],
                    "git_blob": git_blob_sha(
                        self.governance.raw["live_activation"]
                    ),
                    "bytes": len(self.governance.raw["live_activation"]),
                },
                "precheck_receipt": {
                    "sha256": self.governance.sha256["precheck_receipt"],
                    "git_blob": git_blob_sha(
                        self.governance.raw["precheck_receipt"]
                    ),
                    "bytes": len(self.governance.raw["precheck_receipt"]),
                },
            }

        def object_binding(value: VersionedObject | None) -> dict[str, Any] | None:
            if value is None:
                return None
            return {
                "key": value.key, "version_id": value.version_id,
                "etag": value.etag, "sha256": value.sha256,
                "bytes": len(value.body), "content_type": value.content_type,
                "server_side_encryption": value.server_side_encryption,
            }

        result = {
            "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C8_LIVE_ENTRY_RESULT_v1.0",
            "verdict": verdict,
            "entry_gate": "LIVE_ENTERED_ONCE" if self.claim_object else "LIVE_NOT_ENTERED",
            "live_adapter_gate": "READY",
            "generation_id": GENERATION_ID,
            "runtime_lock_id": RUNTIME_LOCK_ID,
            "pilot_run_id": PILOT_RUN_ID,
            "governed_correction_commit": self.contract.correction_head,
            "terminal_state": (
                "TERMINAL_PASS_BOUNDED_G11C8_DATA_GENERATION_SOURCE_NOT_ADMITTED"
                if verdict == "PASS" else "TERMINAL_FAIL_CLOSED_NO_RERUN"
            ),
            "execution_binding": execution_binding,
            "material_bindings": material_bindings,
            "receipt_bindings": receipt_bindings,
            "execution_claim_binding": object_binding(self.claim_object),
            "checkpoint_binding": object_binding(self.checkpoint_object),
            "terminal_receipt_binding": {
                "key": G11C8_TERMINAL_RECEIPT_KEY,
                "attempted": self.terminal_receipt_attempted,
                "put_attempts": self.effects.terminal_receipt_put_attempts,
                "confirmed": self.terminal_receipt_object is not None,
                "object": object_binding(self.terminal_receipt_object),
            },
            "effects": effects,
            "effect_reconciliation": {
                "complete": not self.effects.ambiguous_side_effects,
                "ambiguous_side_effects": self.effects.ambiguous_side_effects,
            },
            "projection": {
                "source_rows": projection.get("source_rows", 0),
                "eligible_rows": projection.get("eligible_rows", 0),
                "excluded_rows": projection.get("excluded_rows", 0),
                "missing_rows": projection.get("missing_rows", 0),
                "conflict_rows": projection.get("conflict_rows", 0),
                "eligible_projection_sha256": projection.get("eligible_projection_sha256"),
                "future_selector_observed": projection.get("future_selector_observed", False),
                "future_selector_auto_excluded": False,
            },
            "next_resume_cursor": {
                "basDt": current.get("basDt"), "page_no": current.get("next_page"),
            },
            "claim_ceiling": {
                "source_admission_verdict": "NOT_ADMITTED",
                "issuer_identity_resolved": False,
                "normalization": False, "pit": False, "promotion": False,
                "release": False, "production": False,
            },
            "no_rerun": {
                "same_run_retry_authorized": False,
                "same_activation_reuse_authorized": False,
                "same_latch_reuse_authorized": False,
            },
        }
        if error is not None:
            result["error"] = {"code": error.code, "detail": error.detail}
        assert_hash_only_output(result, self.sensitive_values)
        return result

    def _terminalize(self, result: Mapping[str, Any]) -> VersionedObject | None:
        if self.claim_object is None:
            return None
        if self.terminal_receipt_attempted:
            return None
        if self.effects.terminal_receipt_put_attempts >= TERMINAL_RECEIPT_WRITE_CEILING:
            raise BudgetError("G11C8_TERMINAL_RECEIPT_WRITE_CEILING")
        receipt = {
            "artifact": TERMINAL_ARTIFACT,
            "schema_version": 1,
            "generation_id": GENERATION_ID,
            "runtime_lock_id": RUNTIME_LOCK_ID,
            "pilot_run_id": PILOT_RUN_ID,
            "governed_correction_commit": self.contract.correction_head,
            "verdict": result["verdict"],
            "terminal_state": result["terminal_state"],
            "execution_binding": result["execution_binding"],
            "material_bindings": result["material_bindings"],
            "receipt_bindings": result["receipt_bindings"],
            "pre_terminal_result_sha256": sha256_bytes(canonical_json_bytes(result)),
            "effects_before_terminal_receipt": result["effects"],
            "terminal_receipt_write_expected": 1,
            "projection": result["projection"],
            "next_resume_cursor": result["next_resume_cursor"],
            "claim_ceiling": result["claim_ceiling"],
            "no_rerun": result["no_rerun"],
        }
        if "error" in result:
            receipt["error"] = result["error"]
        assert_hash_only_output(receipt, self.sensitive_values)
        body = canonical_json_bytes(receipt)
        metadata = self._metadata(TERMINAL_ARTIFACT)
        metadata["sha256"] = sha256_bytes(body)
        # Consume the one-shot terminal identity before calling S3.  Any known
        # failure or uncertain return is terminal and must never cause a second
        # PutObject attempt in this process/run.
        self.terminal_receipt_attempted = True
        self.effects.terminal_receipt_put_attempts += 1
        self.effects.s3_put_calls += 1
        observed = self.store.create_once(
            G11C8_TERMINAL_RECEIPT_KEY, body,
            content_type="application/json", metadata=metadata,
        )
        if observed.body != body:
            raise AmbiguousSideEffectError("TERMINAL_RECEIPT_READBACK_MISMATCH")
        self.terminal_receipt_object = observed
        self.effects.terminal_receipt_writes += 1
        return observed

    def _fail_result(self, exc: LiveAdapterError) -> tuple[int, dict[str, Any]]:
        if isinstance(exc, AmbiguousSideEffectError):
            self.effects.ambiguous_side_effects = True
            # Owner-reserved ambiguity boundary: once an effect is uncertain,
            # issue no checkpoint, terminal receipt, or other S3 mutation.
            return 2, self._result("FAIL_CLOSED", exc)
        try:
            self._block(exc)
        except LiveAdapterError as block_error:
            if isinstance(block_error, AmbiguousSideEffectError):
                self.effects.ambiguous_side_effects = True
                return 2, self._result("FAIL_CLOSED", block_error)
        result = self._result("FAIL_CLOSED", exc)
        try:
            self._terminalize(result)
            result = self._result("FAIL_CLOSED", exc)
        except LiveAdapterError as terminal_error:
            if isinstance(terminal_error, AmbiguousSideEffectError):
                self.effects.ambiguous_side_effects = True
            result = self._result("FAIL_CLOSED", exc)
        return 2, result

    def run(self) -> tuple[int, dict[str, Any]]:
        try:
            self._initialize()
            assert self.checkpoint is not None
            while self.checkpoint["next_date_index"] < len(self.contract.primary_dates):
                self._deadline_guard()
                current = self.checkpoint["current_date"]
                bas_dt = current["basDt"]
                page_no = int(current["next_page"])
                # The governed seed makes this assertion the first provider cursor.
                if not self.checkpoint["attempts"] and (
                    bas_dt != self.contract.seed_base_date
                    or page_no != self.contract.first_new_page
                ):
                    raise SeedBindingError("FIRST_PROVIDER_CURSOR_MISMATCH")
                self._acquire_page(bas_dt, page_no)
                self._finish_date_if_complete()
            self.checkpoint["state"] = "COMPLETE"
            self.checkpoint["terminal"] = {
                "verdict": "PASS", "source_admission_verdict": "NOT_ADMITTED"
            }
            self._save_checkpoint()
            result = self._result("PASS")
            self._terminalize(result)
            result = self._result("PASS")
            return 0, result
        except LiveAdapterError as exc:
            return self._fail_result(exc)
        except Exception as unexpected:
            # After external entry, even an unforeseen implementation/runtime
            # exception is converted to a sanitized terminal fail-closed result.
            # The exception text is never emitted because it could contain a
            # provider or subprocess value.
            return self._fail_result(
                LiveAdapterError(
                    "UNEXPECTED_INTERNAL_ERROR", type(unexpected).__name__
                )
            )


def create_sealed_g11c8_custody_adapter(
    *, authority_path: Path, plan_path: Path, seed_path: Path,
    manifest_path: Path, owner_decision_path: Path,
    live_activation_path: Path, precheck_receipt_path: Path,
    service_key: str | None = None,
    object_store: ObjectStore | None = None,
    provider: FinanceProvider | None = None,
    contract: LiveContract = PRODUCTION_CONTRACT,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic_fn: Callable[[], float] = time.monotonic,
    deadline_monotonic: float | None = None,
    invocation_nonce: str | None = None,
    live_head_sha: str | None = None,
    live_head_tree: str | None = None,
) -> G11LiveAdapter:
    """Stable factory used by the LIVE workflow and focused injected tests."""

    governance = validate_governance_bundle(
        authority_path=authority_path, plan_path=plan_path, seed_path=seed_path,
        manifest_path=manifest_path, owner_decision_path=owner_decision_path,
        live_activation_path=live_activation_path,
        precheck_receipt_path=precheck_receipt_path,
        live_head_sha=live_head_sha, live_head_tree=live_head_tree,
    )
    if object_store is None:
        bundles = load_live_credential_bundles()
        checkpoint_client = AwsCliS3ObjectStore(
            credential_role=CHECKPOINT_READ_ROLE,
            credentials=bundles[CHECKPOINT_READ_ROLE],
            exact_read_bindings=(contract.checkpoint_binding,),
        )
        raw_client = AwsCliS3ObjectStore(
            credential_role=RAW_READ_ROLE,
            credentials=bundles[RAW_READ_ROLE],
            exact_read_bindings=contract.raw_bindings,
        )
        final_client = AwsCliS3ObjectStore(
            credential_role=FINAL_LIST_WRITE_ROLE,
            credentials=bundles[FINAL_LIST_WRITE_ROLE],
        )
        store: ObjectStore = PhaseSeparatedS3ObjectStore(
            checkpoint_client=checkpoint_client,
            raw_client=raw_client,
            final_client=final_client,
            checkpoint_binding=contract.checkpoint_binding,
            raw_bindings=contract.raw_bindings,
        )
    else:
        store = object_store
    if provider is None:
        secret = service_key or os.environ.get(
            "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY", ""
        )
        provider = BoundedFinanceProvider(
            secret, clock=clock, monotonic_fn=monotonic_fn,
            deadline_monotonic=deadline_monotonic,
        )
    return G11LiveAdapter(
        contract=contract, governance=governance, store=store, provider=provider,
        clock=clock, monotonic_fn=monotonic_fn,
        deadline_monotonic=deadline_monotonic,
        invocation_nonce=invocation_nonce,
    )


class _LiveAdapterEntrypoint:
    """Runner-facing compatibility facade with a one-shot execute contract."""

    interface_version = ADAPTER_INTERFACE_VERSION

    def execute(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        required_paths = {
            "authority_path", "plan_path", "seed_path", "manifest_path",
            "owner_decision_path", "live_activation_path", "precheck_receipt_path",
        }
        if not isinstance(request, Mapping) or any(
            not isinstance(request.get(name), (str, Path)) for name in required_paths
        ):
            result = _pre_entry_failure_result(
                GovernanceError("LIVE_ADAPTER_REQUEST_INVALID"), adapter_ready=True
            )
            result["adapter_interface_version"] = ADAPTER_INTERFACE_VERSION
            result["exit_code"] = EX_CONFIG
            return result
        try:
            adapter = create_sealed_g11c8_custody_adapter(
                authority_path=Path(request["authority_path"]),
                plan_path=Path(request["plan_path"]),
                seed_path=Path(request["seed_path"]),
                manifest_path=Path(request["manifest_path"]),
                owner_decision_path=Path(request["owner_decision_path"]),
                live_activation_path=Path(request["live_activation_path"]),
                precheck_receipt_path=Path(request["precheck_receipt_path"]),
                service_key=request.get("service_key"),
                object_store=request.get("object_store"),
                provider=request.get("provider"),
                contract=request.get("contract", PRODUCTION_CONTRACT),
                clock=request.get("clock", lambda: datetime.now(timezone.utc)),
                monotonic_fn=request.get("monotonic_fn", time.monotonic),
                deadline_monotonic=request.get("deadline_monotonic"),
                invocation_nonce=request.get("invocation_nonce"),
                live_head_sha=request.get("live_head_sha"),
                live_head_tree=request.get("live_head_tree"),
            )
            return_code, result = adapter.run()
        except LiveAdapterError as exc:
            return_code = EX_CONFIG
            result = _pre_entry_failure_result(exc, adapter_ready=False)
        except Exception as unexpected:
            return_code = EX_CONFIG
            result = _pre_entry_failure_result(
                LiveAdapterError(
                    "UNEXPECTED_PRE_ENTRY_ERROR", type(unexpected).__name__
                ),
                adapter_ready=False,
            )
        output = dict(result)
        output["adapter_interface_version"] = ADAPTER_INTERFACE_VERSION
        output["exit_code"] = return_code
        return output


def build_live_adapter() -> _LiveAdapterEntrypoint:
    """Return the exact one-shot runner interface validated by PRECHECK."""

    return _LiveAdapterEntrypoint()


def _pre_entry_failure_result(
    error: LiveAdapterError, *, adapter_ready: bool,
) -> dict[str, Any]:
    """Return one complete sanitized envelope for every pre-entry failure."""

    effects = EffectLedger().output()
    return {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C8_LIVE_ENTRY_RESULT_v1.0",
        "verdict": "FAIL_CLOSED",
        "entry_gate": "LIVE_NOT_ENTERED",
        "live_adapter_gate": "READY" if adapter_ready else "NOT_READY",
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "governed_correction_commit": GOVERNED_CORRECTION_HEAD,
        "terminal_state": "TERMINAL_FAIL_CLOSED_BEFORE_LIVE_ENTRY",
        "error": {"code": error.code, "detail": error.detail},
        "effects": effects,
        "effect_reconciliation": {
            "complete": True, "ambiguous_side_effects": False,
        },
        "projection": {
            "source_rows": 0, "eligible_rows": 0, "excluded_rows": 0,
            "missing_rows": 0, "conflict_rows": 0,
            "eligible_projection_sha256": None,
            "future_selector_observed": False,
            "future_selector_auto_excluded": False,
        },
        "next_resume_cursor": {"basDt": None, "page_no": None},
        "execution_claim_binding": None,
        "checkpoint_binding": None,
        "terminal_receipt_binding": {
            "key": G11C8_TERMINAL_RECEIPT_KEY,
            "attempted": False, "put_attempts": 0,
            "confirmed": False, "object": None,
        },
        "claim_ceiling": {
            "source_admission_verdict": "NOT_ADMITTED",
            "issuer_identity_resolved": False,
            "normalization": False, "pit": False, "promotion": False,
            "release": False, "production": False,
        },
        "no_rerun": {
            "same_run_retry_authorized": False,
            "same_activation_reuse_authorized": False,
            "same_latch_reuse_authorized": False,
        },
    }


def _write_output(path: str, value: Mapping[str, Any]) -> None:
    body = canonical_json_bytes(value)
    if path == "-":
        sys.stdout.buffer.write(body)
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise GovernanceError("OUTPUT_ALREADY_EXISTS", target.name) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("live",), default="live")
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--owner-decision", type=Path, required=True)
    parser.add_argument("--live-activation", type=Path, required=True)
    parser.add_argument("--precheck-receipt", type=Path, required=True)
    parser.add_argument("--output", default="-")
    parser.add_argument("--self-deadline-seconds", type=int, default=0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    deadline = None
    if args.self_deadline_seconds:
        if not 1 <= args.self_deadline_seconds <= 18_000:
            result = _pre_entry_failure_result(
                GovernanceError("SELF_DEADLINE_BOUND_INVALID"), adapter_ready=True
            )
            _write_output(args.output, result)
            return EX_CONFIG
        deadline = time.monotonic() + args.self_deadline_seconds
    try:
        adapter = create_sealed_g11c8_custody_adapter(
            authority_path=args.authority, plan_path=args.plan,
            seed_path=args.seed, manifest_path=args.manifest,
            owner_decision_path=args.owner_decision,
            live_activation_path=args.live_activation,
            precheck_receipt_path=args.precheck_receipt,
            deadline_monotonic=deadline,
        )
        return_code, result = adapter.run()
    except LiveAdapterError as exc:
        result = _pre_entry_failure_result(exc, adapter_ready=False)
        return_code = EX_CONFIG
    except Exception as unexpected:
        result = _pre_entry_failure_result(
            LiveAdapterError(
                "UNEXPECTED_PRE_ENTRY_ERROR", type(unexpected).__name__
            ),
            adapter_ready=False,
        )
        return_code = EX_CONFIG
    _write_output(args.output, result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
