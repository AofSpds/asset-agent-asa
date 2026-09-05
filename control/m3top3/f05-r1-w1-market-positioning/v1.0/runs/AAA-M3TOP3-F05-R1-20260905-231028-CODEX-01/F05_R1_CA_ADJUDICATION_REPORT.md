# F05-R1 corporate-action adjudication report

Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
Cutoff: `2024-08-09`
Status: `PASS — OFFICIAL EVIDENCE CLOSED`
Adjustment factor: `NOT_INFERRED / NOT_MATERIALIZED`

Exact downloaded response-byte custody and SHA-256 values are recorded in `F05_R1_OFFICIAL_CA_SOURCE_CUSTODY.json` under `evidence/official-ca/`.

## Decision

The W1 corporate-action boundaries for GST and Exicon are closed with issuer or KRX evidence published no later than the cutoff. F05 may therefore use the bound daily `ChangesRatio` field as a KRX reference/base-price-aware market-price change and must not use adjacent raw-close ratios at these boundaries.

This adjudication establishes event identity, dates, KRX base-price treatment, and listed-share-count effects. It does not create a series-wide adjustment factor, add dividend reinvestment, or claim that a pre-cutoff heuristic is corporate-action truth.

## GST — KRX:083450

### Bonus issue and ex-right base reset

- The issuer announced on 2024-06-11 that it would issue 9,300,515 ordinary shares, allotting one new share per share held, with a 2024-06-27 record date and expected 2024-07-24 listing. Source: [GST issuer notice](https://www.gst-in.com/cn/board/board.php?bbsid=ir&idx=66&pg=3).
- KRX identified an ex-right for bonus issuance effective 2024-06-26 and set the ordinary-share base price to KRW 21,700 for code A083450. Source: [KRX ex-right notice 20240625001437](https://kind.krx.co.kr/external/2024/06/25/000508/20240625001437/70766.htm).
- The bound row on 2024-06-26 is Close 21,600, Changes -100, and ChangesRatio -0.46 percentage points. This agrees with the KRX base-price meaning. The adjacent raw closes 43,300 and 21,600 are not on the same basis, so `21,600 / 43,300 - 1` is forbidden.

Disposition: `OFFICIAL_CA_CONFIRMED__BONUS_ISSUE_EX_RIGHT_BASE_RESET`.

### New-share listing and Stocks boundary

- KRX recorded 9,300,515 additional ordinary shares, 18,618,260 total listed shares after the addition, and a listing date of 2024-07-24. Source: [KRX additional-listing notice 20240724001584](https://kind.krx.co.kr/external/2024/07/24/000527/20240724001584/70791.htm).
- The bound `Stocks` field changes from 9,317,745 on 2024-07-23 to 18,618,260 on 2024-07-24, exactly matching the official post-list total.
- This is the listed-share-count effect of the same bonus issue, not a second inferred return adjustment.

Disposition: `OFFICIAL_LISTING_CONFIRMED__SAME_BONUS_ISSUE_SHARE_COUNT_EFFECT`.

## Exicon — KRX:092870

### Rights issue and ex-right base reset

- Exicon's filing records 2,202,000 new ordinary shares, 10,848,797 pre-issue shares, shareholder allocation followed by a public offering of unsubscribed shares, a 2024-06-04 record date, 0.2137779189 new shares per old share, and an expected 2024-07-31 listing. Source: [KRX filing 20240709000202](https://kind.krx.co.kr/external/2024/07/09/000130/20240709000202/11306.htm).
- KRX acceptance number `20240531001190`, titled `권리락(유상증자)`, gives a KRW 19,470 base price and an ex-right effective date of 2024-06-03. Source: [KRX disclosure viewer 20240531001190](https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=20240531001190&docno=&viewerhost=&viewport=).
- The bound 2024-06-03 row is Close 20,400, Changes +930, and ChangesRatio +4.78 percentage points, which is consistent with the official KRW 19,470 base. A raw close-to-close return from 2024-05-31 is not admissible for this interval.

Disposition: `OFFICIAL_CA_CONFIRMED__RIGHTS_ISSUE_EX_RIGHT_BASE_RESET`.

### New-share listing and Stocks boundary

- KRX recorded 2,202,000 additional ordinary shares, 13,050,797 total listed shares after the addition, an issue price of KRW 15,130, and a listing date of 2024-07-31. Source: [KRX additional-listing notice 20240726001822](https://kind.krx.co.kr/external/2024/07/26/000831/20240726001822/70791.htm).
- The bound `Stocks` field changes from 10,848,797 on 2024-07-30 to 13,050,797 on 2024-07-31, exactly matching the official total. The 2024-07-31 bound daily turnover must therefore use `814,284 / 13,050,797`.
- The economic ex-right reset occurred on 2024-06-03; the 2024-07-31 share-count change is not an invented second adjustment.

Disposition: `OFFICIAL_LISTING_CONFIRMED__RIGHTS_ISSUE_SHARE_COUNT_EFFECT`.

## KRX semantic basis

KRX describes the ordinary base price as the prior close in the usual case and provides separate theoretical base-price treatment for paid or bonus issues, including tick rounding. These rules explain why the daily change field can remain economically comparable at an ex-right boundary while adjacent raw closes cannot. Sources: [KRX base-price overview](https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T2.jsp), [KRX ex-right reference-price formula](https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T3.jsp), and [KRX base-price adjustment cases](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T6.jsp).

## PIT and exclusions

- All operative issuer/KRX records above were public before or on 2024-07-31, earlier than the 2024-08-09 cutoff.
- A 2025 GST annual report may corroborate the later narrative but is excluded from the PIT decision and from every economic input.
- No current-universe substitution, post-cutoff price, outcome, MFE/MAE, or future ranking was read or used.
- No CA factor was estimated. No cash-dividend total-return series was constructed.

## Gate result

`P3_CA_GATE = PASS_PENDING_INDEPENDENT_RECEIPT`

Both required issuers are evidence-closed under the approved policy. No Owner decision is required.
