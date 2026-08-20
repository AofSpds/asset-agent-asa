# New-candidate deduplication audit

This audit prevents full-sweep observations from becoming count inflation. A candidate is **new** only when no v0.1 object preserves the material source claim. A bad v0.1 statement is repaired through a successor correction, not counted again as new. A source position that is merely suppressed is recovered in interpretation but remains the same object.

| Sweep candidate | Disposition | v0.2 result | Reason |
|---|---|---|---|
| V02-SRC-0001 | GENUINELY_NEW | V02-LIVE-NEW-0001 | C-06's limiting prose was outside the v0.1 record block. |
| V02-SRC-0002 | EXISTING_NEEDS_CORRECTION | correction for CX-LIVE-PLANNING-0017 | ASA-MI-REC-010's code block already contains the cognitive-cost condition; v0.1 used metadata as its statement. |
| V02-SRC-0003 | GENUINELY_NEW | V02-LIVE-NEW-0002 | The register-wide prior-art interpretation rule was not objectized. |
| V02-SRC-0004 | GENUINELY_NEW | V02-LIVE-NEW-0003 | The P-006 scope boundary was outside the extracted code block. |
| V02-SRC-0005 | GENUINELY_NEW | V02-LIVE-NEW-0004 | The per-dimension status classification rule was omitted. |
| V02-SRC-0006 | SPLIT_TO_AVOID_BUNDLING | V02-LIVE-NEW-0005 and V02-LIVE-NEW-0006 | The source contains two independent negative distinctions. |
| V02-SRC-0007 | GENUINELY_NEW_AFTER_SPLIT | V02-LIVE-NEW-0005 | Zero-specific unknown semantics were not preserved by `UNKNOWN != FALSE`. |
| V02-SRC-0008 | GENUINELY_NEW_AFTER_SPLIT | V02-LIVE-NEW-0006 | Observation status and existence status are distinct. |
| V02-SRC-0009 | DUPLICATE_OF_V02-SRC-0003 | no additional object | The broader prior-art rule already includes reference-found versus method-adopted. |
| V02-SRC-0010 | EXISTING_ACCURATE | CX-SRC-SRC-WP2-0007 | v0.1 already preserves `Protocol standardizes definability, not the definition`. |
| V02-SRC-0011 | EXISTING_SUPPRESSED | CX-SRC-META-0016 | PL-007 exists; recovery changes review priority, not identity. |
| V02-SRC-0012 | EXISTING_SUPPRESSED | CX-SRC-META-0017 | PL-008 exists. |
| V02-SRC-0013 | EXISTING_SUPPRESSED | CX-SRC-META-0018 | PL-009 exists. |
| V02-SRC-0014 | EXISTING_SUPPRESSED | CX-SRC-META-0019 | PL-010 exists. |
| V02-SRC-0015 | EXISTING_SUPPRESSED | CX-SRC-META-0011 | PL-002 exists. |
| V02-SRC-0016 | EXISTING_SUPPRESSED | CX-SRC-META-0012 | PL-003 exists. |
| V02-SRC-0017 | EXISTING_SUPPRESSED | CX-SRC-META-0013 | PL-004 exists. |
| V02-SRC-0018 | EXISTING_SUPPRESSED | CX-SRC-META-0014 | PL-005 exists. |
| V02-SRC-0019 | EXISTING_SUPPRESSED | CX-SRC-META-0015 | PL-006 exists. |

Result of the first 19 labels: six genuinely new live-source objects, one existing-object correction, nine recovered-but-existing objects, two exact/covered duplicates, and one already accurate object. A later full narrative-prose residual reread added two genuinely new live-source scope/method boundaries (`V02-LIVE-NEW-0007` and `0008`) and one existing-object correction (`CX-LIVE-WORLDVIEW-0002`). The layer-B historical normalized corpus yielded no genuinely new object beyond v0.1; its empty JSONL is intentional. `RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED` still applies to layer-B claims.
