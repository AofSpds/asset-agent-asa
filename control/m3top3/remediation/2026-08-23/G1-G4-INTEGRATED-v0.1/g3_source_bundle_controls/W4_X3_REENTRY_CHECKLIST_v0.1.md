# W4×3 Non-scoreable Re-entry Checklist v0.1

Re-entry means a second assembly-control attempt only. It does not mean scoring, ranking, returns, Golden or Replay admission.

For each of 케이씨텍 (`281820`), 미래산업 (`025560`) and 삼양엔씨켐 (`482630`):

- [ ] Identity binding source and SHA-256 are present.
- [ ] Eligibility state and decision-source refs are present; unresolved rows remain full-row preserved and unscored.
- [ ] Every source byte is frozen and hashed.
- [ ] Every `publication_at` is timezone-aware and at/before the W4 cutoff.
- [ ] Retrieval actor/time/locator are recorded.
- [ ] Future prices, winners, ranks, returns and current-success state are absent from the bundle.
- [ ] Outcome-blind access sidecar is complete and hash-bound.
- [ ] Raw 2025 price component hash matches `2bfd93c2...559e`.
- [ ] Boundary dates 2025-05-09, 2025-05-12 and 2025-08-08 remain present.
- [ ] Zero-OHL observations are preserved without imputation.
- [ ] 미래산업's 17 W4 zero-OHL rows have evidence-backed Trading Status/CA treatment or remain blocked.
- [ ] Governed CA completeness and Trading Status are not inferred from the raw 18-column file.
- [ ] Independent pre-adjudication outputs are preserved if annotation is attempted.
- [ ] `SCORE_ADMISSION=false`, `RANK_ADMISSION=false`, `OUTCOME_ADMISSION=false` remain locked.
- [ ] IVA has no authoring, retrieval, annotation or adjudication role.

Any unchecked mandatory item ends the row as `FAIL_CLOSED`. Owner action is not required to apply this checklist.
