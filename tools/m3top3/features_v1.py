from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Any, Iterable
from .core import parse_date, parse_datetime
from .contracts_v1 import FEATURE_SCHEMA_VERSION
from .window_mapping_v11 import add_calendar_months

FEATURE_IDS=("F01_COMMERCIAL_CONVERSION_MOMENTUM","F02_NUMERIC_BUSINESS_INFLECTION","F03_FORWARD_REVISION_MOMENTUM","F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION","F05_MARKET_POSITIONING_BALANCE","F06_CONVERSION_RUNWAY","F07_BETA_TRANSMISSION_ALIGNMENT","F08_EVIDENCE_RELIABILITY","F09_EXECUTION_THESIS_SAFETY")
AXIS_BY_FEATURE={FEATURE_IDS[0]:"Business_Momentum",FEATURE_IDS[1]:"Business_Momentum",FEATURE_IDS[2]:"Expectation_Surprise",FEATURE_IDS[3]:"Expectation_Surprise",FEATURE_IDS[4]:"Market_Positioning",FEATURE_IDS[5]:"Forward_Runway",FEATURE_IDS[6]:"Forward_Runway",FEATURE_IDS[7]:"Reliability_Risk",FEATURE_IDS[8]:"Reliability_Risk"}
COMM={"NONE":0,"CONCRETE_CATALYST_PRE_COMMERCIAL":25,"QUALIFICATION_ACCEPTANCE_OR_FIRST_VOLUME_ORDER":60,"SHIPMENT_OR_BACKLOG_CONVERSION":80,"REPEAT_ORDER_OR_MULTIPLE_INDEPENDENT_COMMERCIAL_CONFIRMATIONS":100}
GUIDE={"UP":80,"UNCHANGED":50,"DOWN":20}; QS={"MATERIALLY_ABOVE":90,"ABOVE":75,"INLINE":50,"BELOW":25,"MATERIALLY_BELOW":10}
BETA={"NOT_ACTIVE":0,"PRE_ACTIVATION":25,"APPROACHING_RELEVANT_PHASE":50,"ACTIVE_RELEVANT_PHASE":75,"ACTIVE_WITH_DIRECT_CUSTOMER_CONFIRMATION":100}
EVI={"VERIFIED_HIGH":100,"VERIFIED_MEDIUM":85,"PARTIAL":65,"NOT_FOUND":50,"STALE":40,"CONFLICT":25}
SAFE={"NONE":100,"LOW":80,"MODERATE":60,"HIGH":35,"CRITICAL":10}; RISK_ORDER={"NONE":0,"LOW":1,"MODERATE":2,"HIGH":3,"CRITICAL":4}
MISSING={"MISSING","UNKNOWN","REVIEW_REQUIRED","NOT_FOUND"}

def D(v): return v if isinstance(v,Decimal) else Decimal(str(v))
def clip(v): return min(Decimal(100),max(Decimal(0),D(v)))
def med(v):
    s=sorted(v); n=len(s)
    return s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2
def qtile(s,q):
    if len(s)==1:return s[0]
    p=D(q)*D(len(s)-1); lo=int(p); hi=min(lo+1,len(s)-1); f=p-D(lo)
    return s[lo]*(1-f)+s[hi]*f
def robust_pct(vals):
    if not vals:return {}
    s=sorted(vals.values()); lo,hi=qtile(s,".05"),qtile(s,".95")
    w={k:min(hi,max(lo,v)) for k,v in vals.items()}
    if len(w)==1:return {next(iter(w)):D(50)}
    ordered=sorted(w.items(),key=lambda x:(x[1],x[0])); out={}; i=0; n=len(ordered)
    while i<n:
        j=i+1
        while j<n and ordered[j][1]==ordered[i][1]:j+=1
        p=D(100)*(D(i)+D(j-1))/D(2*(n-1))
        for k,_ in ordered[i:j]:out[k]=p
        i=j
    return out
def raw(r,f): return r.get("feature_raw_inputs",{}).get(f)
def groups(x):
    if not x:return ()
    g=x.get("event_group_ids") or ([x["event_group_id"]] if x.get("event_group_id") else [])
    return tuple(sorted({str(v) for v in g if v}))
def refs(x):
    if not x:return ()
    g=x.get("source_lineage_refs") or ([x["source_lineage_ref"]] if x.get("source_lineage_ref") else [])
    return tuple(sorted({str(v) for v in g if v}))
def explicit(x):
    if x and x.get("availability_state") in MISSING:return x["availability_state"],x.get("missing_reason")
    return None

@dataclass
class FV:
    feature_id:str; axis_id:str; score:Decimal|None; availability_state:str; missing_reason:str|None; event_group_ids:tuple[str,...]; source_lineage_refs:tuple[str,...]; trace:dict[str,Any]
    def dict(self):
        d=asdict(self); d["score"]=None if self.score is None else str(self.score); d["event_group_ids"]=list(self.event_group_ids); d["source_lineage_refs"]=list(self.source_lineage_refs); return d
def na(fid,x,state="NOT_FOUND",reason=None):return FV(fid,AXIS_BY_FEATURE[fid],None,state,reason or state,groups(x),refs(x),{})
def ok(fid,x,score,trace):return FV(fid,AXIS_BY_FEATURE[fid],clip(score),"AVAILABLE",None,groups(x),refs(x),trace)

class FeatureEngineV1:
    version=FEATURE_SCHEMA_VERSION
    def __init__(self,weights):self.w={k:D(v) for k,v in weights.items() if k in FEATURE_IDS}
    def f01(self,r):
        f=FEATURE_IDS[0]; x=raw(r,f); e=explicit(x)
        if not x:return na(f,x)
        if e:return na(f,x,*e)
        st=x.get("commercial_state")
        if st not in COMM:return na(f,x,"REVIEW_REQUIRED","commercial_state absent/invalid")
        if x.get("latest_positive_transition_at"):
            days=(parse_datetime(r["snapshot_cutoff_at"]).date()-parse_datetime(x["latest_positive_transition_at"]).date()).days
            if days<0:return na(f,x,"REVIEW_REQUIRED","transition after cutoff")
            rec=100 if days<=30 else 75 if days<=60 else 50 if days<=90 else 25
        elif st=="NONE":days=None;rec=0
        else:return na(f,x,"REVIEW_REQUIRED","positive state without transition timestamp")
        return ok(f,x,D(".75")*D(COMM[st])+D(".25")*D(rec),{"commercial_state":st,"recency_days":days})
    def f02(self,rows):
        f=FEATURE_IDS[1]; mm={}
        for r in rows:
            x=raw(r,f)
            if r["eligibility_state"]!="ELIGIBLE" or not x or explicit(x):continue
            changes=x.get("metric_changes")
            if isinstance(changes,dict):
                for m,v in changes.items():
                    if v is not None:mm.setdefault(m,{})[r["company_id"]]=D(v)
            for m,p in (x.get("metric_pairs") or {}).items():
                if not isinstance(p,dict) or p.get("current") is None or p.get("prior") is None:continue
                c,pr=D(p["current"]),D(p["prior"]); mode=p.get("change_mode","RELATIVE")
                if mode=="ABSOLUTE":v=c-pr
                elif mode=="RELATIVE" and pr!=0:v=(c-pr)/abs(pr)
                else:continue
                mm.setdefault(m,{})[r["company_id"]]=v
        pp={m:robust_pct(v) for m,v in mm.items()}; out={}
        for r in rows:
            x=raw(r,f); e=explicit(x); vals=[p[r["company_id"]] for p in pp.values() if r["company_id"] in p]
            out[r["company_id"]]=na(f,x,*e) if e else (ok(f,x,med(vals),{"metric_percentiles":[str(v) for v in vals]}) if vals else na(f,x,"NOT_FOUND","no valid realized metric"))
        return out
    def f03(self,rows):
        f=FEATURE_IDS[2]; mm={}
        for r in rows:
            x=raw(r,f) or {}
            if r["eligibility_state"]!="ELIGIBLE" or explicit(x):continue
            for m,v in (x.get("revision_pcts") or {}).items():
                if v is not None:mm.setdefault(m,{})[r["company_id"]]=D(v)
        pp={m:robust_pct(v) for m,v in mm.items()}; out={}
        for r in rows:
            x=raw(r,f); e=explicit(x)
            if e:out[r["company_id"]]=na(f,x,*e);continue
            vals=[p[r["company_id"]] for p in pp.values() if r["company_id"] in p]
            if vals:out[r["company_id"]]=ok(f,x,sum(vals,D(0))/D(len(vals)),{"revision_percentiles":[str(v) for v in vals]})
            elif x and x.get("official_guidance_change") in GUIDE:out[r["company_id"]]=ok(f,x,GUIDE[x["official_guidance_change"]],{"guidance":x["official_guidance_change"]})
            else:out[r["company_id"]]=na(f,x,"NOT_FOUND","no valid revision or guidance")
        return out
    def f04(self,rows):
        f=FEATURE_IDS[3]; nums={}
        for r in rows:
            x=raw(r,f) or {}
            if r["eligibility_state"]!="ELIGIBLE" or explicit(x) or not x.get("independent_pre_event_baseline"):continue
            if x.get("observed") is not None and x.get("prior_expectation") is not None:
                o,p=D(x["observed"]),D(x["prior_expectation"]); nums[r["company_id"]]=(o-p)/max(abs(p),D(x.get("epsilon","1e-12")))
        pp=robust_pct(nums);out={}
        for r in rows:
            x=raw(r,f);e=explicit(x);cid=r["company_id"]
            if e:out[cid]=na(f,x,*e)
            elif not x or not x.get("independent_pre_event_baseline"):out[cid]=na(f,x,"NOT_FOUND","no independent pre-event baseline")
            elif cid in pp:out[cid]=ok(f,x,pp[cid],{"numeric_surprise_percentile":str(pp[cid])})
            elif x.get("qualitative_surprise") in QS:out[cid]=ok(f,x,QS[x["qualitative_surprise"]],{"qualitative_surprise":x["qualitative_surprise"]})
            else:out[cid]=na(f,x,"NOT_FOUND","no measurable surprise")
        return out
    def f05(self,rows):
        f=FEATURE_IDS[4];a={};b={};c={}
        for r in rows:
            x=raw(r,f) or {};cid=r["company_id"]
            if r["eligibility_state"]!="ELIGIBLE" or explicit(x):continue
            if x.get("trailing_20d_total_return") is not None and x.get("universe_20d_equal_weight_return") is not None:a[cid]=D(x["trailing_20d_total_return"])-D(x["universe_20d_equal_weight_return"])
            if x.get("trailing_60d_total_return") is not None and x.get("universe_60d_equal_weight_return") is not None:b[cid]=D(x["trailing_60d_total_return"])-D(x["universe_60d_equal_weight_return"])
            if x.get("turnover_acceleration") is not None:c[cid]=D(x["turnover_acceleration"])
        pa,pb,pc=robust_pct(a),robust_pct(b),robust_pct(c);out={}
        for r in rows:
            x=raw(r,f);e=explicit(x);cid=r["company_id"]
            if e:out[cid]=na(f,x,*e);continue
            if not x or cid not in pa or cid not in pb or cid not in pc:out[cid]=na(f,x,"NOT_FOUND","required market components incomplete");continue
            v=D(".5")*pa[cid]+D(".3")*pb[cid]+D(".2")*pc[cid];p=max(D(0),v-D(85))
            if x.get("valuation_percentile") is not None:p+=D(".5")*max(D(0),D(x["valuation_percentile"])-D(90))
            if x.get("diffusion_percentile") is not None:p+=D(".5")*max(D(0),D(x["diffusion_percentile"])-D(90))
            p=min(D(30),p);out[cid]=ok(f,x,v-p,{"recognition_velocity":str(v),"saturation_penalty":str(p)})
        return out
    def f06(self,r):
        f=FEATURE_IDS[5];x=raw(r,f);e=explicit(x)
        if not x:return na(f,x)
        if e:return na(f,x,*e)
        if not x.get("retrieval_complete"):return na(f,x,"NOT_FOUND","runway retrieval incomplete")
        a=parse_date(r["window_anchor_date"]);end=add_calendar_months(a,3);ms=[m for m in x.get("milestones",[]) if m.get("date") and a<parse_date(m["date"])<=end]
        if not ms:return ok(f,x,20,{"milestones_in_horizon":0})
        ver=[m for m in ms if m.get("verified") and m.get("source_tier") in {"S1","S2","S3"}];supplier=all(m.get("supplier_only",False) for m in ms)
        s=100 if len(ver)>=2 and x.get("sequential_conversion_steps") else 90 if len(ver)>=2 else 70 if len(ver)==1 else 40
        if supplier:s=min(s,70)
        return ok(f,x,s,{"milestones_in_horizon":len(ms),"verified_count":len(ver),"supplier_only":supplier})
    def f07(self,r):
        f=FEATURE_IDS[6];x=raw(r,f);e=explicit(x)
        if not x:return na(f,x)
        if e:return na(f,x,*e)
        st=x.get("activation_alignment");return ok(f,x,BETA[st],{"activation_alignment":st}) if st in BETA else na(f,x,"NOT_FOUND","PIT-supported beta stage unavailable")
    def f09(self,r,gated):
        f=FEATURE_IDS[8];x=raw(r,f);e=explicit(x)
        if not x:return na(f,x)
        if e:return na(f,x,*e)
        if not x.get("assessment_complete"):return na(f,x,"NOT_FOUND","risk assessment incomplete")
        ev=[z for z in x.get("risk_events",[]) if z.get("event_group_id") not in gated];sv=[z.get("severity") for z in ev if z.get("severity") in RISK_ORDER];s=max(sv,key=lambda z:RISK_ORDER[z]) if sv else "NONE"
        v=ok(f,x,SAFE[s],{"severity":s,"excluded_hard_gate_groups":sorted(gated)});v.event_group_ids=tuple(sorted({str(z.get("event_group_id")) for z in ev if z.get("event_group_id")}));return v
    def f08(self,r,fmap):
        f=FEATURE_IDS[7];x=raw(r,f);e=explicit(x)
        if not x:return na(f,x)
        if e:return na(f,x,*e)
        num=D(0);den=D(0);tr={}
        for target,ev in (x.get("feature_evidence") or {}).items():
            if target==f or target not in self.w or (target in fmap and fmap[target].score is None):continue
            st=ev.get("evidence_status")
            if st not in EVI:continue
            pen=min(D(20),max(D(0),D(ev.get("freshness_penalty",0))));sup=clip(D(EVI[st])-pen);w=self.w[target];num+=w*sup;den+=w;tr[target]={"status":st,"freshness_penalty":str(pen),"support":str(sup)}
        return ok(f,x,num/den,{"feature_evidence":tr,"weighted_evidence_weight":str(den)}) if den else na(f,x,"NOT_FOUND","no scored-feature evidence support")
    @staticmethod
    def dedupe(fmap,inputs):
        claimed={};audit=[]
        for f in [FEATURE_IDS[i] for i in (0,1,2,3,4,5,6,8)]:
            v=fmap[f]
            if v.score is None:continue
            x=inputs.get(f,{})
            indep=bool(x.get("independent_overlap")) or (f==FEATURE_IDS[3] and bool(x.get("independent_pre_event_baseline")))
            col=[(g,claimed[g]) for g in v.event_group_ids if g in claimed]
            if col and not indep:v.score=None;v.availability_state="NA_FOR_OVERLAP";v.missing_reason="economic event already credited to primary feature";audit.append({"feature_id":f,"action":"SUPPRESSED","collisions":col});continue
            for g in v.event_group_ids:claimed.setdefault(g,f)
            if col:audit.append({"feature_id":f,"action":"INDEPENDENCE_EXCEPTION","collisions":col})
        return audit
    def compute_snapshot(self,records:Iterable[dict[str,Any]],hard_gate_groups=None):
        rows=list(records);hard_gate_groups=hard_gate_groups or {};a=self.f02(rows);b=self.f03(rows);c=self.f04(rows);d=self.f05(rows);out={}
        for r in rows:
            cid=r["company_id"]
            if r["eligibility_state"]!="ELIGIBLE":out[cid]={"features":{},"anti_double_count_audit":[]};continue
            m={FEATURE_IDS[0]:self.f01(r),FEATURE_IDS[1]:a[cid],FEATURE_IDS[2]:b[cid],FEATURE_IDS[3]:c[cid],FEATURE_IDS[4]:d[cid],FEATURE_IDS[5]:self.f06(r),FEATURE_IDS[6]:self.f07(r),FEATURE_IDS[8]:self.f09(r,hard_gate_groups.get(cid,set()))}
            au=self.dedupe(m,r.get("feature_raw_inputs",{}));m[FEATURE_IDS[7]]=self.f08(r,m);out[cid]={"features":{k:v.dict() for k,v in m.items()},"anti_double_count_audit":au}
        return out
