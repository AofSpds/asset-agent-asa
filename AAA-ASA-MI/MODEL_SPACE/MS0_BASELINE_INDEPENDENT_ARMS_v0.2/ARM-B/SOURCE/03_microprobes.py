"""Deterministic, dependency-free semantic probes for ARM-B.

Evidence source: only semantics written in 02_deep_proposals.md.
This is not an implementation artifact named 별 and makes no canonical claim.
"""

from __future__ import annotations

from itertools import combinations, product
import json


def probe_d1_ccp():
    device = ({"p": 0, "l": 0}, {"p": 1, "l": 1})
    bright = ({"l": 1},)
    dark = ({"l": 0},)
    def glue(*contexts):
        merged = []
        for selections in product(*contexts):
            out = {}
            compatible = True
            for assignment in selections:
                for key, value in assignment.items():
                    if key in out and out[key] != value:
                        compatible = False
                    out[key] = value
            if compatible and out not in merged:
                merged.append(out)
        return merged
    device_bright = glue(device, bright)
    device_dark = glue(device, dark)
    all_three = glue(device, bright, dark)
    declared_unconstrained_temp = glue(tuple({**a, "temp": t} for a in device for t in (0, 1)), bright)
    assert device_bright == [{"p": 1, "l": 1}]
    assert device_dark == [{"p": 0, "l": 0}]
    assert all_three == []
    assert {a["temp"] for a in declared_unconstrained_temp} == {0, 1}
    return {"device+bright": device_bright, "device+dark": device_dark, "all_contexts": all_three, "temp_values": sorted({a["temp"] for a in declared_unconstrained_temp}), "color_query": "UNDEFINED_OUTSIDE_SIGNATURE"}


def probe_d2_trcc():
    seed = {"nodes": {"s": "stem", "b": "bud"}, "incidence": {("s", "b")}}
    after = {"nodes": {"s": "stem", "b1": "bud", "b2": "bud"}, "incidence": {("s", "b1"), ("s", "b2")}}
    preservation = {"s": "s"}
    inverse = {"nodes": dict(seed["nodes"]), "incidence": set(seed["incidence"])}
    split_write = {"node:b", "incidence:s-b"}; wither_write = {"node:b", "incidence:s-b"}; mark_write = {"mark:s"}
    assert "b" not in preservation
    assert set(after["nodes"]) - set(preservation.values()) == {"b1", "b2"}
    assert split_write & wither_write
    assert not (split_write & mark_write)
    assert inverse == seed
    return {"preserved": preservation, "fresh_successors": ["b1", "b2"], "old_bud_persists": False, "split_wither": "CONFLICT", "split_mark": "COMMUTATIVE_UNDER_DECLARED_WRITE_SETS", "inverse_reconstructs_seed": True}


def probe_d3_ocf():
    events = ("i", "h", "f", "a", "r")
    prerequisites = {"i": set(), "h": {"i"}, "f": set(), "a": {"h"}, "r": set()}
    conflicts = {frozenset(("i", "f"))}
    def valid(chosen):
        chosen = set(chosen)
        if any(not prerequisites[e] <= chosen for e in chosen): return False
        if any(pair <= chosen for pair in conflicts): return False
        return True
    configurations = []
    for n in range(len(events)+1):
        for choice in combinations(events,n):
            if valid(choice): configurations.append(set(choice))
    def enabled(chosen):
        chosen=set(chosen)
        return sorted(e for e in events if e not in chosen and valid(chosen|{e}))
    assert enabled(set()) == ["f","i","r"]
    assert enabled({"i"}) == ["h","r"]
    assert {"i","f"} not in configurations
    assert {"i","h","a","r"} in configurations
    assert not any("f" in c and ("i" in c or "h" in c or "a" in c) for c in configurations)
    return {"configuration_count": len(configurations), "enabled_empty": enabled(set()), "enabled_after_i": enabled({"i"}), "i_and_f_possible": False, "f_prevents_i_lineage": True}


def probe_d4_vtd():
    def reachable_interval(t,x0=0.0,speed_bound=1.0): return (x0-speed_bound*t,x0+speed_bound*t)
    reach_2=reachable_interval(2.0); target_3_possible=reach_2[0] <= 3.0 <= reach_2[1]
    exit_time_for_x_eq_t=0.5; constant_zero_viable=-0.5 <= 0 <= 0.5
    assert reach_2 == (-2.0,2.0); assert not target_3_possible; assert constant_zero_viable
    return {"reachable_at_2": reach_2, "x_eq_3_possible": target_3_possible, "sign_at_2": "UNKNOWN_BOTH_SIGNS_REACHABLE", "x_eq_t_exit_time_from_K": exit_time_for_x_eq_t, "x_eq_0_viable_in_K": constant_zero_viable}


def probe_d5_gpe():
    def alt(n): return "".join("0" if i%2==0 else "1" for i in range(n))
    def zero_tail(n):
        fixed="010"; return (fixed+"0"*n)[:n]
    programs={"alt":alt,"zero_tail":zero_tail}
    def survivors(observed): return {name:fn for name,fn in programs.items() if fn(len(observed))==observed}
    s3=survivors("010"); predictions3={name:fn(4)[3] for name,fn in s3.items()}; s4=survivors("0101")
    assert predictions3 == {"alt":"1","zero_tail":"0"}; assert set(s4)=={"alt"}
    return {"survivors_after_010": sorted(s3), "next_predictions": predictions3, "survivors_after_0101": sorted(s4), "unallocated_hypothesis_mass_allowed": True}


def probe_d6_oiba():
    not_rel={(0,1),(1,0)}
    def compose(left,right): return {(x,z) for x,y1 in left for y2,z in right if y1==y2}
    double_not=compose(not_rel,not_rel); feedback_fixed_points={x for x,y in not_rel if x==y}
    assert double_not == {(0,0),(1,1)}; assert feedback_fixed_points==set()
    return {"NOT_then_NOT": sorted(double_not), "NOT_feedback_fixed_points": sorted(feedback_fixed_points), "feedback_status": "EMPTY_BEHAVIOR"}


def probe_d7_irow():
    profiles_v1={"u":{"T1":0},"v":{"T1":0}}; profiles_v2={"u":{"T1":0,"T2":0},"v":{"T1":0,"T2":1}}
    def classes(profiles,repertoire):
        buckets={}
        for candidate,profile in profiles.items(): buckets.setdefault(tuple(profile[t] for t in repertoire),[]).append(candidate)
        return sorted(sorted(group) for group in buckets.values())
    v1_classes=classes(profiles_v1,("T1",)); v2_classes=classes(profiles_v2,("T1","T2"))
    assert v1_classes == [["u","v"]]; assert v2_classes == [["u"],["v"]]
    return {"classes_under_T1": v1_classes, "classes_under_T1_T2": v2_classes, "historical_equivalence_rewritten": False, "distinguishing_test": "T2"}


def probe_d8_rcn():
    edges_base={("a","b"),("b","a"),("b","c")}
    def mutually_reachable_component(edges,members):
        adjacency={m:set() for m in members}
        for src,dst in edges:
            if src in members and dst in members: adjacency[src].add(dst)
        def reaches(src,dst):
            frontier,seen=[src],{src}
            while frontier:
                at=frontier.pop()
                if at==dst: return True
                for nxt in adjacency[at]:
                    if nxt not in seen: seen.add(nxt); frontier.append(nxt)
            return False
        return all(reaches(a,b) for a in members for b in members)
    ab_closed=mutually_reachable_component(edges_base,{"a","b"}); abc_closed=mutually_reachable_component(edges_base,{"a","b","c"}); after_removing_t2=mutually_reachable_component({("a","b"),("b","c")},{"a","b"}); after_t4=mutually_reachable_component(edges_base|{("c","a")},{"a","b","c"})
    assert ab_closed and not abc_closed and not after_removing_t2 and after_t4
    return {"minimal_regenerative_component":["a","b"], "c_is_constitutive_before_t4": abc_closed, "closure_after_removing_t2": after_removing_t2, "abc_closure_after_t4": after_t4}


def probe_d9_ptl():
    split_cost=abs(-1-0)+abs(1-0)+0.2; birth_death_cost=3+3+3; high_penalty_split_cost=abs(-1-0)+abs(1-0)+7.1
    assert split_cost==2.2; assert split_cost<birth_death_cost; assert high_penalty_split_cost>birth_death_cost
    return {"split_cost": split_cost, "delete_plus_births_cost": birth_death_cost, "selected_low_penalty":"SPLIT", "selected_split_penalty_7.1":"DELETE_AND_TWO_BIRTHS", "identity_claim":"NOT_MADE"}


def main():
    results={"D1_CCP":probe_d1_ccp(),"D2_TRCC":probe_d2_trcc(),"D3_OCF":probe_d3_ocf(),"D4_VTD":probe_d4_vtd(),"D5_GPE":probe_d5_gpe(),"D6_OIBA":probe_d6_oiba(),"D7_IROW":probe_d7_irow(),"D8_RCN":probe_d8_rcn(),"D9_PTL":probe_d9_ptl()}
    print(json.dumps(results,ensure_ascii=False,indent=2,sort_keys=True))

if __name__ == "__main__": main()
