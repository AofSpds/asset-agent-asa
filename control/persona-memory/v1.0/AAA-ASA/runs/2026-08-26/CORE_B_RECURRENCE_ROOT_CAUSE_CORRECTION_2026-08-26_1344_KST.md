# Core-B recurrence root-cause correction

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
TIME_KST = 2026-08-26 13:44 KST
AUTHORITY_SOT = FALSE
CLASS = OWNER_OBSERVATION_AND_ASA_RUNTIME_CORRECTION

## Owner observation

Owner reports that the Core-B issue has already been removed multiple times and asks why it keeps recurring.

## Exact current-state diagnosis

- `Core B` as a domain label is intentionally retained in the Shared Contract for model/feature/scorer/ranking scientific authority. It is not itself the stale object to remove.
- The recurring blocker is the obsolete short-name active Persona pair still present in the effective Organization v1.3 current projections:
  - `AAA-MODEL-ARCHITECT`
  - `AAA-MODEL-VALIDATOR`
- Project Instructions, Shared Contract, selector registry, and memory index instead resolve the intended long-name pair:
  - `AAA-MODEL-VALIDATION-DESIGN-ARCHITECT`
  - `AAA-MODEL-DESIGN-VALIDATOR`
- The v1.4 successor candidate has already been authored on `aaa-core-b-authority-coherence-successor-v1.0-20260826` and a D1 exact target has been frozen on `aaa-core-b-authority-coherence-d1-validation-receipts-20260826`.
- The active persistent-locator branch has not yet been cut over from Organization v1.3 to v1.4. Therefore every authority-first bootstrap correctly redetects the same conflict.

## ASA correction

Do not restart Core-B discovery, reauthor another successor, or send another full remediation packet.

The only remaining route is:

1. continue from existing D1 frozen target;
2. complete bounded fresh CTLV P0 L1;
3. complete bounded IVA P0 L2 on the same exact target;
4. obtain exact Owner cutover approval;
5. atomically activate Organization v1.4 through the persistent-locator CAS plan;
6. run MOD/MODV fresh bootstrap regression;
7. release the Core-B routing hold;
8. resume the Common Guard rollout with narrow A0 currentization only.

Historical v1.3 and old Persona strings remain as immutable evidence but must cease resolving as current after cutover.

## Exact refs

- active Organization v1.3 current state blob: `cad42e60efea2eb67bb663b5ff889277c028e66c`
- active routing v1.3 blob: `ca48540479b3c25ef4c8573a457d12a53e576246`
- active pair activation v1.3 blob: `3579860fd20e497161e13a9ccc8fa0c7fac0db61`
- v1.4 successor head: `a1c65d0e500c34fe849badf452f84907f6d53554`
- D1 frozen target head: `85321a798bc82912f28fe061450e047257bbea4d`

## Claim ceiling

This note creates no authority, validation PASS, cutover, model semantic change, M3Top3 gate transition, Release, or Production authority.
