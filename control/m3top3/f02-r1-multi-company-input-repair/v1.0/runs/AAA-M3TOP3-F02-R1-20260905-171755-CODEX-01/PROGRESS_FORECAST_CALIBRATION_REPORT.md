# PROGRESS_FORECAST_CALIBRATION_REPORT

RUN_ID = AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01  
REPORT_CUTOFF_KST = 2026-09-05T19:37:43.2411131+09:00  
BASELINE_FROZEN = TRUE · REBASE_HISTORY = [] · TOTAL_EWU = 100

## Outcome and clock boundary

Functional terminal is COMPLETE_MULTI_COMPANY_PROVISIONAL: four new issuers plus one cached control, five required validation-role PASS acts and one new durable score/seal. This is not model-development completion or a performance/OOS result. Local persistence and remote transfer are separate: local score payload is committed; remote push was rejected before execution by auto-review because explicit payload/destination transfer approval was absent. No bypass or transfer occurred.

Run start: 2026-09-05T17:17:55.1469424+09:00. Wall to this report cutoff: 139.802 minutes. Final report commit/readback occurs after this document's measurement cutoff and is identified in terminal response. Do not mislabel the document cutoff as the final commit time or infer exact active effort from it.

Original overall forecast is unchanged: P50 planning proxy 125 minutes, conservative planning proxy 240 minutes, LOW confidence. These are not empirically fitted percentiles. To report cutoff, actual wall exceeds P50 by 14.802 minutes (11.84%); it remains below 240 minutes. The four-hour checkpoint is 21:17:55.1469424 KST and was not reached at report cutoff. No timing overrun waived a gate.

## Stage evidence and planned/actual comparison

| Stage | EWU | Original P50 / conservative | Actual start evidence | Actual end evidence | Elapsed interpretation / final disposition |
|---|---:|---|---|---|---|
| P0 | 5 | 5 / 10 min | 17:17:55.1469424 | 17:18:51.2079169; custody commit 17:22:32 | Bootstrap action 56.061 sec; later commit is different event. COMPLETE |
| P1 | 25 | 25 / 45 min | 17:18:51.2079169 dispatch boundary | Material sources 17:45:31.4742731; recovered central close 18:14:40.3012516 | Source evidence window 26m40.266; recovery latency is not source-search active time. COMPLETE_RECOVERED |
| P2 | 15 | 15 / 30 min | Exact active start NOT_INSTRUMENTED; after recovered source shape | Commit 18:26:29; central checkpoint recorded 18:30 | End artifact/commit/recording differ; exact exclusive active wall NOT_INSTRUMENTED. COMPLETE |
| P3 | 25 | 35 / 65 min | 18:24:00 design/delegation boundary, overlapping P2 closure | Material verification 18:42:16.9204973; target commit 18:43:21 | Recorded boundary window 18m16.920; not independent exclusive-stage effort. COMPLETE |
| P4 | 15 | 25 / 50 min | Exact operative candidate commit 18:43:21 | Last PMOV receipt persistence 19:17:19; aggregate freeze 19:25:44.7285839; evidence commit 19:26:18 | Candidate→aggregate 42m23.729; role work/slot waits/aggregation not separately fully instrumented. COMPLETE |
| P5 | 10 | 10 / 20 min | Actual CLI 19:26:31.699448 | CLI 19:26:42.579538; root checks 19:29:42; IVA return 19:30; payload commit 19:31:47 | CLI execution 10.88009 sec, not total verification/persistence effort. COMPLETE |
| P6 | 5 | 10 / 20 min | Completion/readback work after P5 checks; exact exclusive start NOT_INSTRUMENTED | Document cutoff 2026-09-05T19:37:43.2411131+09:00; final commit/readback separately returned | Final local reporting/custody close; remote not performed. COMPLETE_LOCAL with remote approval boundary |

Stage windows overlap and timestamps mix substantive work, saved evidence, aggregation and commit custody. They must not be summed as exclusive active work. P2's 18:30 central checkpoint is not evidence that implementation began only afterward. Missing measurements are retained explicitly rather than backdated.

LAST_MATERIAL_PROGRESS at cutoff = actual five-company score/seal and independent post-score readback complete; report assembled. NEXT_TERMINAL_EVENT = final local report commit/tree/clean status readback. After that event no source, scorer or validation correction work remains. Remote transfer is outside local closure and remains separately blocked.

## Early checkpoints and interruption

- First source locator 17:28:34.7925142, elapsed 10m39.646 from run start: approximate 15-minute first-return target met.
- Required 30-minute checkpoint due 17:47:55.1469424 was not durably recorded then. At 18:14:40.3012516 it was documented late from recovered evidence, lateness 26m45.154. Target NOT_MET; not backdated.
- First executable input materialization: 18:35:50.3101487, elapsed 77m55.163. The earlier source locator/raw-byte completion is not this input event.
- Owner reported PC/browser restart. Same run/branch/root and 13-file management state retained. Four newly acquired raw files and cached control hashes matched. No durable source evidence loss detected; unrecorded/unsaved UI state cannot be proven recovered.
- Repeat source actions after recovery: 0. Completed queries and exact evidence were reused; runtime recovery did not create authority to restart F02-R1.
- Restart duration, active time and blocked/wait time: NOT_INSTRUMENTED. No claimed measured time saving from reuse.

## Counters and costs

| Metric | Observed | Limit / interpretation |
|---|---:|---|
| Charged unique source actions | 33 | 48 total; queries/opens/fetches/retries, not HTTP total |
| Per issuer actions | 10 / 5 / 9 / 9 | 003160 / 025560 / 031980 / 036200; each ≤12 |
| Cached control new source actions | 0 | 005290 cache only |
| Worker source ledger records | 37 | 33 charged + 4 control records |
| Action classes | 19 query + 4 open + 8 fetch + 2 fetch-retry | Sum 33; retry=true appears on 6 records, a separate dimension |
| Newly saved source files | 4 | ≤8 total and 1 per issuer ≤2 |
| Newly saved raw bytes | 4,774,865 | ≤20,000,000 |
| HTTP requests | NOT_INSTRUMENTED | 2 direct successful requests observed; 2 sandbox attempts recorded zero; internal total for 29 actions unknown |
| Browser interactions | 0 | No UI source retrieval during continuation |
| Source human assistance | 0 | Owner-directed runtime recovery is operational direction, not manual source selection |
| New R1 score calls | 1 | No rerun; CLI 10.88009 sec |
| Estimated numeric input leaves | 0 | 20 observed values + 20 derived control leaves |
| Source companies / leaves | 5 / 40 | Leaves are not extra companies |
| Fresh distinct affected + legacy suite methods | 31 + 13 = 44 | Overlapping focused runs not added as unique tests |
| P3 known affected recheck | 3 methods / 8.944 sec | Lower-bound observed revalidation event, not all rework |
| Total active / wait / rework / CRU / token cost | NOT_INSTRUMENTED | No conversion from actions/bytes/tests into CRU |
| Planned CRU / token price | NOT_CALIBRATED | No invented dollar or token estimate |
| Remote push transfer | 0 | Rejected before command execution; no payload transmitted |

The governance Git readback had one sandbox connection failure followed by an allowed read-only escalated call. It is not source discovery and does not increment KIND action counts. Remote push was separately denied by auto-review; no retry or indirect workaround was made.

## Rework, findings and forecast history

Known pre-P4 events: corrected P2 SHA transcription reference (underlying classification unchanged), tightened exact cover/header cells, reran affected three tests for 8.944 seconds, normalized only the two changed integration files to repository LF before bundle freeze. P4 formal correction cycle: none required; zero operative target changes after cdfebb. Five nonblocking reviewer observations (three unique themes) were carried into reports. P5 readback initially compared canonical semantic hashes to raw formatted-file hashes; the read-only assertion was corrected to the existing canonical contract, without code/input/output changes or rescoring. Total duration of these activities is unknown, not zero.

Immutable Git history retains original forecasts and intermediate reports: P3 ETA 40–80 minutes at 18:42; P4 20–50 minutes at 18:57; P4 aggregate 10–25 minutes at 19:25; P5 close 5–15 minutes at 19:29. They were conditional forecasts, not retroactive baseline replacements. The final report elapsed time includes runtime interruption, reviewer slot/aggregation latency and final documentation; their separate contributions cannot be quantified from available telemetry.

## Calibration judgment and next boundary

The reusable functional result is exact admission across multiple actual source layouts, with native units, publication/period/cell custody and create-once validation-gated sealing. Source-stage elapsed about 26m40 is near its 25-minute planning proxy, but one interrupted observation is insufficient to recalibrate statistical P50/P90 or claim efficiency gains. Overall 125-minute proxy was optimistic for this run. Preserve 240-minute conservative proxy as historical plan, not a future guarantee.

For any separately authorized successor, instrument exclusive active/wait/rework spans and schedule the 30-minute checkpoint before long validation/aggregation work. This is a recommendation, not new implementation or scheduled automation. Do not reopen sources, outcomes, features, windows, providers or budgets. If remote preservation is desired, request explicit approval for the existing task branch and existing origin payload transfer; no additional approval is needed to use the completed local artifacts.
