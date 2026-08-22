# M3TOP3 R-WP4-02 — Fail-Closed Runtime Implementation Receipt

## Control header

| Field | Value |
|---|---|
| Receipt | `AAA-M3TOP3-R-WP4-02-LOCAL-GREEN-20260823-0150` |
| Exact base | `AofSpds/asset-agent-asa@167c1b05e25df658b322cf428c72ce3a4f476544` |
| Candidate | Local isolated implementation staging; Git candidate HEAD pending |
| Verdict | `LOCAL_IMPLEMENTATION_CANDIDATE_GREEN / PAIRED_VALIDATION_PENDING` |
| Model semantics | Preserved; no feature, weight, gate, ranking, or outcome-definition change |
| IVA execution participation | `NONE` |
| Official Golden / Full Replay | `BLOCKED / BLOCKED` |

## Implemented controls

- Central classified admission contract with exits `2/3/4`.
- Strict missing/invalid publication, availability, current-only, future-field, consumed-slice PIT, and cutoff-frozen bundle guards.
- Core B `V-F04` correction: later rows in a longitudinal raw source are deterministically excluded, not used to block every earlier snapshot. Each retrieval emits a deterministic receipt.
- Retrieval receipts are persisted in a separate non-scoreable `retrieval_audit.jsonl`; manifest records its byte hash, row count, content hash, and the snapshot aggregate binds it. Excluded future values and row IDs do not enter `pit_snapshot.jsonl` or `model_input.jsonl`.
- READY/empty-blocker scoring firewall, actual JSONL byte/hash/count/semantic verification, and zero-scorer-call failure behavior.
- Price component-byte, duplicate-key, OHLC, CA evidence/factor, and canonical-release/CA-completeness admission.
- Create-only staged snapshot-directory publication and immutable result storage keyed by `validation_run_id`.
- Lazy ledger directory creation; classified admission failures create no result or ledger path.
- Official/diagnostic scorer separation and exact scorer/config/authority receipt checks.
- CLI accounting and stable exits: success `0`, controlled block `2`, integrity `3`, authority/config `4`.

## Test evidence

| Check | Result |
|---|---:|
| Logical Known-Failure IDs | `33 / 33` |
| Existing infrastructure tests | `25 / 25` |
| Combined executed tests | `80` |
| Failure / error / unexpected skip | `0 / 0 / 0` |
| Targeted guard mutations | `15 / 15 KILLED_RED` |
| Temp-copy mutation isolation | `PASS`; source mutation `FALSE` |
| `compileall` / `py_compile` | `PASS / PASS` |

Commands:

```text
python -m unittest discover -s tools/m3top3/tests -p 'test_*.py' -v
python remediation/r_wp4_failclosed_impl/run_targeted_mutation_checks.py remediation/runtime_checkout
python -m compileall -q tools/m3top3
python -m py_compile tools/m3top3/*.py
```

Observed final suite output: `Ran 80 tests ... OK`.

Observed mutation output: `requested_mutations=15, killed_red=15, survived_or_error=0, status=PASS`.

## Candidate file digests

| File | SHA-256 |
|---|---|
| `tools/m3top3/admission.py` | `91bae32409b4faca67f4e840c4a1d90994ccd941febd544893c0385a93b1f394` |
| `tools/m3top3/pit_guard.py` | `5fa17bb958b852e808757b1636c593ae8fec6e8b9bcd9ec3b26e6822a863e366` |
| `tools/m3top3/providers.py` | `4050608929e5ec7e2574728208b64eedd0d89f24f4f30fd244c78e12cda4ad0a` |
| `tools/m3top3/snapshot.py` | `4550dfa8ba037c1b2daacb14db2292f5330d26bc04eb63216e4710746a9a0ba3` |
| `tools/m3top3/backtest.py` | `94d0dd1a7cccb0a8e695703666ed9a0b3abff8354de0c29f5258204536832adb` |
| `tools/m3top3/ledger.py` | `16bd0ccff0061f325682e45094edb54be4626e402456a389c13d943187d43769` |
| `tools/m3top3/outcome.py` | `0097cbab2373db885538d18083f554136dd347d2863b97aa3f26d728acd9331f` |
| `tools/m3top3/cli_build_snapshots.py` | `547fe9c49e8376235d788b720ec1d3709c09079b1da53af21b2c4db5abd5d35d` |
| `tools/m3top3/cli_run_backtest.py` | `fcbf57d564cc9f855041bcf92375abb374c626081fe369bf5fd4ee235f4dfb7c` |
| `tools/m3top3/configs/snapshot.example.json` | `e260f5d60170318453859f796c652cf80a88aa210e94b0f56e4deb338941117b` |
| `tools/m3top3/configs/backtest.example.json` | `ee7fe5550560aff249ab1e45e7152ed99375c82e68a34d51deb7d0bef783e579` |
| `tools/m3top3/tests/test_infrastructure.py` | `e032f6c107f042f2b8e43dc5e01de2225c5ca48dcbd978c5d1b78f1c8b0e9416` |
| `tools/m3top3/tests/_known_failure_helpers.py` | `92da81e87d0c35875c01a1494644faf9ee536ba19880b777c8820c066f2c2321` |
| `tools/m3top3/tests/test_known_failures_pit.py` | `e7935170b9183d0cbf8da23690565a342ea8ddb2cc517023092069cac0a89684` |
| `tools/m3top3/tests/test_known_failures_snapshot.py` | `72a403083c2bd914d71956fc3f5a03a01541492c81af905b6d5557201f1c2cf0` |
| `tools/m3top3/tests/test_known_failures_integrity.py` | `fb97779fe47b9b3f2c17e06b09e41286ec149dbbc4c4aa9be5473c52818162ce` |
| `tools/m3top3/tests/test_known_failures_price.py` | `0568bdafd4bf562f4a012f15135796f4f9f848b5ea92ec0ba1edf9de2bd5951d` |
| `tools/m3top3/tests/test_known_failures_immutability.py` | `ac68e866b11f7991ea5a8f219e226d422d056ed08dad80190b7c42589f866005` |
| `tools/m3top3/tests/test_known_failures_cli.py` | `73743b1d7062962233d7b2316933a96ea387fa08fa137b5e728660ce54761419` |
| `tools/m3top3/tests/test_known_failures_model_admission.py` | `8dd35227248b691e583c0636c7df18cbd873691acc6f4c3e9526ac6884ac591e` |
| `remediation/r_wp4_failclosed_impl/run_targeted_mutation_checks.py` | `9c00a88b69293fa45958e147882f98b9cc275dbea276681c8bd78b2a3c87137a` |

## Remaining gates

1. Materialize this exact candidate on the assigned isolated Git branch and freeze a candidate HEAD.
2. Re-run the same suite and mutation harness on that exact Git HEAD.
3. Obtain active Core B and engineering paired-validator follow-up receipts on the exact diff/head.
4. Keep `S0_PRE_OUTCOME_BASELINE_CANDIDATE`; do not run Official Golden or Full Replay.

This receipt establishes only a local fail-closed implementation candidate. It does not establish exact v1 identity, predictive power, a validated model, Official Golden readiness, Full Replay readiness, Freeze, Release, Promotion, or Production authority.
