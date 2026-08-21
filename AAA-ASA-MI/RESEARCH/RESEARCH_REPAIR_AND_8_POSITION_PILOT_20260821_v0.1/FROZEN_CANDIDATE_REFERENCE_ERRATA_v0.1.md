# Frozen Candidate Reference Errata v0.1

STATE = `POST_EVALUATION_CROSSWALK / CANDIDATE_BYTES_UNCHANGED / NO_SCIENTIFIC_CHANGE`

Static QA after final research-foundation traceability edits found portable-path and line-range drift in the frozen A1/A2 provenance headers. Their evaluated bytes, blind transformations, receipts, and hashes are intentionally not rewritten. This crosswalk corrects references only; it changes no assumption, model, consequence, test, profile, gate, or qualification.

| Frozen location | Preserved text/problem | Portable successor reference |
|---|---|---|
| `CANDIDATES/TRACK_A_A1.md:11` | scratch-oriented `deliverables/...` research root | Repository root is `AAA-ASA-MI/RESEARCH/RESEARCH_REPAIR_AND_8_POSITION_PILOT_20260821_v0.1/`. |
| `CANDIDATES/TRACK_A_A1.md:13,19` | `working/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md` | `INSTRUMENTS/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md`; cited purpose remains lines 5–11. |
| `CANDIDATES/TRACK_A_A1.md:20-21` | `02_RESEARCH_FOUNDATION_MAP.md:39-48` shifted when the traceability ledger was inserted | P0, historical-version, and non-closure assumptions are now `02_RESEARCH_FOUNDATION_MAP.md:55-64`. |
| `CANDIDATES/TRACK_A_A2.md:11` | scratch-oriented `deliverables/...` research root | Repository root is `AAA-ASA-MI/RESEARCH/RESEARCH_REPAIR_AND_8_POSITION_PILOT_20260821_v0.1/`. |
| `CANDIDATES/TRACK_A_A2.md:13,19` | `working/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md` | `INSTRUMENTS/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md`; cited purpose remains lines 5–11. |
| `CANDIDATES/TRACK_A_A2.md:20` | foundation-map ranges shifted | Identity/memory/relation/event/global-account questions and alternatives are now `02_RESEARCH_FOUNDATION_MAP.md:43-53,75-83`; `04_CONCEPT_AND_ASSUMPTION_MAP.md:9-18` remains the concept-map cross-reference. |
| `CANDIDATES/TRACK_A_A2.md:21` | foundation-map ranges shifted | terminology/two-job cautions are now `02_RESEARCH_FOUNDATION_MAP.md:75-83,95-103`; `03_OWNER_INTENT_INTERPRETATION_MATRIX.md:21-24` remains the provenance cross-reference. |

The same immutable evaluated candidate files remain canonical for this pilot. Any future candidate revision must receive a new version, hash, blind transformation, and evaluation receipt rather than replacing these bytes.
