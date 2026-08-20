"""Replayable ARM-C micro-probes. Uses only Python's standard library."""

from itertools import combinations, product


def d1_rewrite():
    q, q1, q2 = 10, 4, 6
    invariant = q1 > 0 and q2 > 0 and q1 + q2 == q
    status_domain = {"stable", "unstable"}
    unstable_guard_entailed = status_domain == {"unstable"}
    return invariant and not unstable_guard_entailed


def d2_occurrences():
    events = {"load", "split4_6", "split5_5", "paintY"}
    causes = {"split4_6": {"load"}, "split5_5": {"load"}, "paintY": {"split4_6"}}
    conflict = {frozenset(("split4_6", "split5_5"))}
    def admissible(conf):
        return all(causes.get(e, set()) <= conf for e in conf) and not any(p <= conf for p in conflict)
    configs = [set(c) for n in range(len(events) + 1) for c in combinations(events, n) if admissible(set(c))]
    return ({"load", "split4_6"} in configs and {"load", "split5_5"} in configs and {"load", "split4_6", "split5_5"} not in configs and {"load", "paintY"} not in configs)


def d3_contextual_obstruction():
    bits = (0, 1)
    local_xy = [(x, y) for x, y in product(bits, repeat=2) if x == y]
    local_yz = [(y, z) for y, z in product(bits, repeat=2) if y == z]
    local_zx = [(z, x) for z, x in product(bits, repeat=2) if z != x]
    globals_before = [(x, y, z) for x, y, z in product(bits, repeat=3) if x == y and y == z and z != x]
    globals_after = [(x, y, z) for x, y, z in product(bits, repeat=3) if x == y and y == z and z == x]
    return all(len(s) == 2 for s in (local_xy, local_yz, local_zx)) and not globals_before and len(globals_after) == 2


def d4_hybrid_bounds():
    q0, rate, duration = 10.0, 0.1, 2.0
    reach = (q0 - rate * duration, q0 + rate * duration)
    reset_possible_at_lower_bound = reach[0] <= 9.8 <= reach[1]
    reset_example = (4.0, 5.8)
    conservation = abs(sum(reset_example) - 9.8) < 1e-12
    return reach == (9.8, 10.2) and not (reach[0] <= 9.5 <= reach[1]) and reset_possible_at_lower_bound and conservation


def minimal_cycles(nodes, edges):
    def strongly_connected(subset):
        if len(subset) < 2: return False
        for start in subset:
            seen, stack = {start}, [start]
            while stack:
                here = stack.pop()
                for a, b in edges:
                    if a == here and b in subset and b not in seen:
                        seen.add(b); stack.append(b)
            if seen != subset: return False
        return True
    candidates = [set(c) for n in range(2, len(nodes) + 1) for c in combinations(nodes, n) if strongly_connected(set(c))]
    return [c for c in candidates if not any(d < c for d in candidates)]


def d5_operational_closure():
    nodes = {"a", "b", "c"}
    initial = minimal_cycles(nodes, {("a", "b"), ("b", "a"), ("a", "c")})
    dissolved = minimal_cycles(nodes, {("a", "b"), ("a", "c")})
    merged = minimal_cycles(nodes, {("a", "b"), ("b", "c"), ("c", "a")})
    return initial == [{"a", "b"}] and dissolved == [] and merged == [{"a", "b", "c"}]


def d6_generative_update():
    prior = (0.6, 0.4); likelihood = (0.0, 1.0)
    raw = tuple(p * l for p, l in zip(prior, likelihood)); total = sum(raw)
    posterior = tuple(x / total for x in raw)
    before_change_probability = prior[0]
    after_change_at_2_2 = posterior[0] * 1.0 + posterior[1] * 1.0
    return posterior == (0.0, 1.0) and before_change_probability == 0.6 and after_change_at_2_2 == 1.0


def d7_process_deadlock():
    offers_without_b = {"a"}; q_requires = {"a", "b"}; deadlocked = not q_requires <= offers_without_b
    offers_with_b = {"a", "b"}; enabled_after_composition = q_requires <= offers_with_b
    return deadlocked and enabled_after_composition


def d8_predictive_behavior():
    transitions = {("u", "a"): (0, "u1"), ("v", "a"): (0, "v1"), ("u1", "b"): (1, "u1"), ("v1", "b"): (0, "v1"), ("w", "a"): (0, "w1"), ("w1", "b"): (1, "w1")}
    def trace(state, actions):
        observations=[]
        for action in actions:
            observation,state=transitions[(state,action)]; observations.append(observation)
        return tuple(observations)
    one_step_same = trace("u", ("a",)) == trace("v", ("a",))
    two_step_distinct = trace("u", ("a", "b")) != trace("v", ("a", "b"))
    u_w_same_on_probe_set = all(trace("u", seq) == trace("w", seq) for seq in (("a",), ("a", "b"), ("a", "b", "b")))
    return one_step_same and two_step_distinct and u_w_same_on_probe_set


PROBES = {"D1_WLRF": d1_rewrite, "D2_BOS": d2_occurrences, "D3_CCRA": d3_contextual_obstruction, "D4_HTA": d4_hybrid_bounds, "D5_OCIC": d5_operational_closure, "D6_OGTK": d6_generative_update, "D7_CPIC": d7_process_deadlock, "D8_PPBC": d8_predictive_behavior}

if __name__ == "__main__":
    results = {name: probe() for name, probe in PROBES.items()}
    for name, passed in results.items(): print(f"{name}: {'REPLAYED' if passed else 'MISMATCH'}")
    if not all(results.values()): raise SystemExit(1)
