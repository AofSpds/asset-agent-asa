# G3 predecessor standalone-manifest identity recovery

- Execution authority: `AAA-PMO-ORCHESTRATOR`
- Successor lease: `aaa-pmo-m3top3-successor-resume-20260826-0034`
- Observation time: `2026-08-26T00:42:17+09:00`
- Gate effect: `NONE / G3 REMAINS OPEN`
- Validation claim: `NONE`

## Exact authority recovered

GitHub Issue #54 fixes the predecessor standalone component-manifest expected
SHA-256 as:

`56d36d51e9f7b8870aa75cc41ee241603f6cf7446cb2386187c6ebcbb88b73c4`

The identified upstream workbook is:

- file: `U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx`
- observed SHA-256: `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda`
- sheet: `Price_Manifest` (OOXML `xl/worksheets/sheet10.xml`)
- record: row 2, `record_type=MANIFEST`,
  `price_dataset_id=SEMI-PRICE-MARCAP-KRX-2024-2026_v1`,
  `component=INTERFACE_MANIFEST`

The same row contains both:

- `expected_SHA256=56d36...73c4`; and
- `actual_SHA256=NOT_RECOMPUTED_NO_MANIFEST_FILE`.

Its notes state that standalone manifest bytes were not attached. No manifest
filename, byte length, content bytes, or manifest-object locator is supplied by
that row. Its source-path field points only to the stable component locators
listed in the component rows below.

## Read-only recovery search

The successor performed a bounded read-only search across:

1. the recovered prior PMO surface under
   `/workspace/scratch/577256efb437`;
2. the current successor workspace under
   `/workspace/scratch/f56b716343a6`;
3. all accessible files under `/workspace` smaller than 5 MiB, using exact
   SHA-256 matching; and
4. the GitHub repository code index using the exact expected digest.

Results:

- exact SHA-256 byte match: `0`;
- GitHub code-index match: `0`;
- exact predecessor standalone-manifest bytes: `NOT_FOUND`;
- legacy import manifest observed SHA-256:
  `ca8f117a83cd3da800a2a2b5e0ebdca3c89ff658ff3fd21b5083e4aae9ab98ce`;
- legacy import manifest disposition: `MISMATCH_NOT_SUBSTITUTED`.

## Disposition

The predecessor digest is recovered as a workbook-declared expected identity,
not as a rehashable standalone manifest artifact. The workbook itself records
that no manifest file was available for recomputation. Therefore:

- `PREDECESSOR_STANDALONE_MANIFEST_EXPECTED_IDENTITY = RECOVERED_AS_DECLARATION`;
- `PREDECESSOR_STANDALONE_MANIFEST_BYTES = NOT_FOUND`;
- `PREDECESSOR_STANDALONE_MANIFEST_BYTE_IDENTITY = NOT_PROVEN`;
- `CUSTODIAN_EXHAUSTION = NOT_PROVEN`;
- `MULTI_YEAR_CUTOVER = NOT_AUTHORIZED`;
- `G3 = DEPENDENCY_BLOCKED / NOT_CLOSED`.

The recovered range-complete 2026 component through 2026-08-14 has a different
byte identity from the older workbook component row. A new forward recovery
manifest may preserve the current bytes, but it must not impersonate or replace
the unrecovered predecessor standalone manifest.

