# F05-R1 D1 IVA L2 independent validation journal

- Validator: `root/f05_r1_iva_d1`
- Role / level: `IVA / L2`
- Target revision: `D1`
- Target commit: `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9`
- Target tree: `c98194af223562e440d66c47b57f6696110ced47`
- Bundle: `AAA-M3TOP3-F05-R1-D1-2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9-c98194af223562e440d66c47b57f6696110ced47`
- Recorded: `2026-09-06T01:18:13+09:00`
- Independence: `INDEPENDENT_OF_TARGET_AUTHOR_AND_OTHER_VALIDATORS`
- Verdict: `PASS`
- Findings: `0`
- Assertions: `43,810`

## Independence and custody boundary

I did not read any CTLV, MODV, or ENGV D1 receipt or journal before freezing this verdict. I did not edit any target file, did not invoke the production scoring CLI or score engine, did not create any score artifact, and did not transfer a D0 verdict. The primary numeric validation queried only the governed physical fields from the bound 2024 Parquet and reconstructed the approved calculations with an independent `Decimal` implementation.

All 34 declared target paths matched their D1 Git blob identities and their declared worktree SHA-256/byte counts. Twelve inherited Python files use normal Windows CRLF checkout representation while their Git blobs are LF-normalized; each worktree file normalized exactly to its declared target blob, so this is an expected dual-representation custody fact and not content drift.

## Independent reperformance

The exact 57-company cohort was reconstructed from the frozen R0 binding. For every company, the final 61 sessions ending `2024-08-09` matched the governed grid, yielding 3,477 independently inspected source rows. Every required Open/High/Low/Close, Changes, ChangesRatio, Volume, Amount, and Stocks value passed finite/positive/integral and KRX reference-base consistency checks as applicable.

For all 57 companies I independently recomputed:

- exactly 20 ChangesRatio intervals over 21 observations;
- exactly 60 ChangesRatio intervals over 61 observations;
- daily `Volume / Stocks` for the immediately prior and recent 20-session windows;
- turnover acceleration from those two means;
- all 171 per-company source-slice digests;
- the fixed-order exact-57 equal-weight 20d and 60d benchmarks;
- the canonical merged F02+F05 input hash.

The reconstructed benchmarks were `-0.2124153885346208337758748387981210510982875684105824670798651096` for 20d and `-0.2427557483310895727201166322683066906964043950156641786131060302` for 60d. They matched every one of the 57 bound rows without denominator shrink. The merged input hash independently reproduced `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.

GST's `2024-06-26` KRX base-price row and `2024-07-24` listed-share boundary matched the official custody facts. Exicon's `2024-06-03` KRX base-price row and `2024-07-31` Volume/Stocks boundary also matched. In both cases, the adjacent raw-close ratio materially differed from the approved ChangesRatio return, confirming that a naive raw-close construction would be invalid across the corporate-action reset.

## P01-P07 and N01-N13

Every positive case P01-P07 passed. The in-memory downstream check independently reproduced robust percentile inputs, the unchanged `.50/.30/.20` recognition-velocity weights, saturation, 57 F05 values, and the exact-five persisted F02 identity/score join with five `0.30` and fifty-two `0.20` feature coverage. No score output was persisted.

Every negative case N01-N13 passed. Direct adversarial admission checks rejected raw-close/cash-dividend semantics, wrong issuer, future rows, 56-member denominator, zero/nonintegral turnover inputs, session/cutoff defects, inferred CA factor, source/config drift, percent/fraction confusion, and alias/lineage defects.

For N12, one independently synthesized exact D1 four-role receipt set passed the formal gate. Thirty-one rehashed or structurally altered receipt/report variants were rejected, including D0 transfer, arbitrary validator identity, wrong role/level, author substitution, weak independence assertion, self-pass, edited target, PASS transfer, nonempty findings, target/input drift, malformed receipt ID, descriptor reorder, duplicate path, and aggregate status/provenance mutations. Clean-worktree, create-once output, exact-target ancestry/blob, and receipt-path custody guards remain present. The production score directory remained absent and the recorded production score-call count remained zero.

N13 confirmed the provisional-only claim constant, forced false Top3/Top10 flags, and exact 1..57 / 1..5 rank-domain guards. This validation does not claim official Top3/Top10, performance PASS, OOS validity, release readiness, or an investment recommendation.

## Frozen conclusion

`IVA_L2_D1 = PASS`. There are no findings, no requested correction, no Owner decision boundary, and no authorization transfer. This receipt supports only the exact D1 target and exact input bindings stated above.
