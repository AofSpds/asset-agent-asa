# Mechanical probe replay results

Run locally with the standard-library-only `03_microprobes.py`; all assertions passed.

```text
d1_ahck {'histories': [((0, 0), (1, 1)), ((1, 1), (0, 0))], "a'=b'": 'NECESSARY', "a'=1": 'OPEN'}
d2_crf {'linearizations': [('alpha', 'beta', 'gamma'), ('alpha', 'gamma', 'beta')], 'frontier': ['e', 'f'], 'concurrent': ['beta', 'gamma']}
d3_oppc {'composite_traces': [0], 'one_only_component': 'DEADLOCK'}
d4_lpcw {'pairwise_solution_counts': [2, 2, 2], 'global_solution_count': 0, 'result': 'OBSTRUCTED'}
d5_pgk {'A_out_degree': 2, 'D_in_degree': 2, 'conserved_weight': 10, 'classification': ['FISSION', 'MERGE']}
d6_cpa {'mu=-1': [(0.0, 'stable')], 'mu=1': [(0.0, 'unstable'), (-1.0, 'stable'), (1.0, 'stable')], 'result': 'BIFURCATION'}
d7_cge {'survivors_after_0': 2, 'survivors_after_01': 1, 'next_prediction': '0'}
d8_dsrm {'warm@v1': True, 'warm@v2': False, 'label_without_temperature@v2': 'UNDEFINED'}
d9_itw {'orbit': [(0, 1), (1, 0)], 'weight=1': 'INVARIANT', 'left=1': 'OPEN', 'single_bit_flip': 'NOT_ADMITTED@v1'}
```

These are bounded semantics checks, not empirical validation.
