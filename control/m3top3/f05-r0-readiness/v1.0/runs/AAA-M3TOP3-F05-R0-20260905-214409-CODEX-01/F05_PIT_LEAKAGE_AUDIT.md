# F05 PIT and outcome-leakage audit

- Run ID: `AAA-M3TOP3-F05-R0-20260905-214409-CODEX-01`
- W1 snapshot cutoff: `2024-08-09T23:59:59+09:00`
- Audit disposition: `NO_PROHIBITED_ECONOMIC_VALUE_ADMITTED`
- Scope: F05-R0 readiness evidence only; this is not a scoring or validation verdict.

| Firewall item | Observed handling | Disposition |
|---|---|---|
| Market observation bound | The economic-data scan was predicate-filtered to `Date <= 2024-08-09`; all 57 last observations are exactly 2024-08-09. | CONFORMING |
| Entry-date data | No 2024-08-12 entry price was read or used. Population metadata may identify the entry date, but it supplied no economic value. | NOT_ADMITTED |
| Outcome/evaluation data | No W1 outcome or evaluation price, return, high, close, rank, or winner label was read or used. | NOT_ADMITTED |
| Rank column | The Parquet `Rank` column was not loaded into the economic analysis. | NOT_ADMITTED |
| Future annual Parquet data | 2025 and 2026 file bytes were used only for exact size/hash identity readback; no economic column was loaded. | HASH_ONLY |
| Post-cutoff model/control artifacts | Later documents and code were read only to establish provenance and whether an earlier governed definition exists. | PROVENANCE_ONLY |
| Post-cutoff CA records | Two 2026 CA register entries were inspected only to establish register scope/status and were excluded from all 2024 mapping. | SCOPE_PROOF_ONLY |
| Heuristic discontinuities | Derived only from pre-cutoff raw Close, Stocks, Volume, and Amount observations in the bounded 61-date window. | PRE_CUTOFF_ONLY |
| Feature/score/output | No F05 input, score, ranking, seal, or Top3 output was materialized. | NOT_CREATED |

## Data-access boundary

For economic analysis, the 2024 Parquet scanner loaded only Date, Code, Name, Open, High, Low, Close, Volume, Amount, and Stocks, predicate-filtered to the exact 57 codes and cutoff. It never loaded Rank. The common 21- and 61-date windows end on the cutoff and are availability diagnostics, not formula definitions.

An initially redundant recovery copy of the same bound 2024 object was downloaded after a recursive local search did not surface the direct path. Its byte count and SHA256 exactly matched the bound object. The direct `Downloads` copy was then located and was the only copy used for economic computation. The redundant copy introduced no new provider, credential, paid source, budget, or economic identity and was removed during closeout.

No post-cutoff fact was used to relabel, adjust, or reinterpret a pre-cutoff price. In particular, the lack of a governed 2024 CA record was not converted into a claim of CA absence.
