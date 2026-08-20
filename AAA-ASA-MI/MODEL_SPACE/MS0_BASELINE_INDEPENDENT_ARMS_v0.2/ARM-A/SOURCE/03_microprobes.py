"""Deterministic micro-probes for ARM-A deep proposals. Standard library only."""

from itertools import product, permutations


def d1_ahck():
    histories = []
    for a, b, ap, bp in product((0, 1), repeat=4):
        if b == a and ap == 1 - a and bp == ap:
            histories.append(((a, b), (ap, bp)))
    assert histories == [((0, 0), (1, 1)), ((1, 1), (0, 0))]
    assert all(ap == bp for _, (ap, bp) in histories)
    assert {ap for _, (ap, _) in histories} == {0, 1}
    return {"histories": histories, "a'=b'": "NECESSARY", "a'=1": "OPEN"}


def d2_crf():
    events = ("alpha", "beta", "gamma")
    valid = [p for p in permutations(events) if p.index("alpha") < p.index("beta") and p.index("alpha") < p.index("gamma")]
    assert valid == [("alpha", "beta", "gamma"), ("alpha", "gamma", "beta")]
    return {"linearizations": valid, "frontier": ["e", "f"], "concurrent": ["beta", "gamma"]}


def d3_oppc():
    sender = {0, 1}
    receiver_accepts = {0}
    composite = sender & receiver_accepts
    assert composite == {0}
    assert ({1} & receiver_accepts) == set()
    return {"composite_traces": sorted(composite), "one_only_component": "DEADLOCK"}


def d4_lpcw():
    assignments = list(product((0, 1), repeat=3))
    pxy = {v for v in assignments if v[0] == v[1]}
    pyz = {v for v in assignments if v[1] != v[2]}
    pxz = {v for v in assignments if v[0] == v[2]}
    pair_sizes = [len(pxy & pyz), len(pxy & pxz), len(pyz & pxz)]
    triple = pxy & pyz & pxz
    assert all(n > 0 for n in pair_sizes) and not triple
    return {"pairwise_solution_counts": pair_sizes, "global_solution_count": 0, "result": "OBSTRUCTED"}


def d5_pgk():
    first = {("A", "B"): 6, ("A", "C"): 4}
    second = {("B", "D"): 6, ("C", "D"): 4}
    assert sum(first.values()) == 10 == sum(second.values())
    return {"A_out_degree": 2, "D_in_degree": 2, "conserved_weight": 10, "classification": ["FISSION", "MERGE"]}


def d6_cpa():
    def equilibria(mu):
        roots = [0.0]
        if mu > 0:
            roots.extend([-mu ** 0.5, mu ** 0.5])
        return [(round(x, 6), "stable" if mu - 3 * x * x < 0 else "unstable") for x in roots]
    before = equilibria(-1)
    after = equilibria(1)
    assert before == [(0.0, "stable")]
    assert after == [(0.0, "unstable"), (-1.0, "stable"), (1.0, "stable")]
    return {"mu=-1": before, "mu=1": after, "result": "BIFURCATION"}


def d7_cge():
    g_alt = "010101"
    g_copy = "000000"
    after_0 = [g for g in (g_alt, g_copy) if g.startswith("0")]
    after_01 = [g for g in (g_alt, g_copy) if g.startswith("01")]
    assert len(after_0) == 2 and after_01 == [g_alt]
    return {"survivors_after_0": 2, "survivors_after_01": 1, "next_prediction": g_alt[2]}


def d8_dsrm():
    temp = 21
    historical = temp >= 20
    currentized = temp >= 22
    assert historical is True and currentized is False
    return {"warm@v1": historical, "warm@v2": currentized, "label_without_temperature@v2": "UNDEFINED"}


def d9_itw():
    start = (0, 1)
    identity = lambda pair: pair
    swap = lambda pair: (pair[1], pair[0])
    orbit = {identity(start), swap(start)}
    assert orbit == {(0, 1), (1, 0)}
    assert {sum(pair) for pair in orbit} == {1}
    assert {pair[0] for pair in orbit} == {0, 1}
    return {"orbit": sorted(orbit), "weight=1": "INVARIANT", "left=1": "OPEN", "single_bit_flip": "NOT_ADMITTED@v1"}


if __name__ == "__main__":
    probes = [d1_ahck, d2_crf, d3_oppc, d4_lpcw, d5_pgk, d6_cpa, d7_cge, d8_dsrm, d9_itw]
    for probe in probes:
        print(probe.__name__, probe())
