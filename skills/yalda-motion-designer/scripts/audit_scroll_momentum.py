#!/usr/bin/env python3
"""Read-only post-hoc metrics for R4 target/display progress logs.

Input JSONL fields: t_ms, targetProgress, displayProgress; optionally inputActive,
chapter, mode, viewport. Never interprets synthetic logs as real browser measurements.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path


def analyze(records, epsilon=0.001, max_lag=None, max_settle_ms=None):
    errors=[];warnings=[]
    for i, r in enumerate(records):
        if not isinstance(r,dict) or any(type(r.get(k)) not in (int,float) or not math.isfinite(r.get(k)) for k in ("t_ms","targetProgress","displayProgress")):
            errors.append(f"row {i}: finite t_ms, targetProgress and displayProgress required")
            continue
        if i and r["t_ms"]<=records[i-1].get("t_ms",float("-inf")):
            errors.append(f"row {i}: timestamps must strictly increase")
        for key in ("targetProgress","displayProgress"):
            if not -.000001 <= r[key] <= 1.000001:errors.append(f"row {i}: {key} out of [0,1]")
    if errors:return {"status":"FAIL","errors":errors,"warnings":warnings,"scope":"log-only, no browser presentation proof"}
    lag=[abs(r["targetProgress"]-r["displayProgress"]) for r in records]
    # A fixed-target overshoot is a sign the visual pose passed its actual target.
    overshoot=[];away=[];reversals=[]
    settle_segments=[]
    for i in range(1,len(records)):
        a,b=records[i-1],records[i]
        prev_gap=a["targetProgress"]-a["displayProgress"]
        curr_gap=b["targetProgress"]-b["displayProgress"]
        target_same=abs(b["targetProgress"]-a["targetProgress"])<1e-9
        if target_same and prev_gap*curr_gap < -1e-8:
            overshoot.append(i)
        if target_same and abs(curr_gap)>abs(prev_gap)+1e-6:
            away.append(i)
        if i>=2:
            prev_delta=records[i-1]["targetProgress"]-records[i-2]["targetProgress"]
            curr_delta=b["targetProgress"]-a["targetProgress"]
            if prev_delta*curr_delta < -1e-8:reversals.append(i)
    start=None
    for i,r in enumerate(records):
        is_idle=r.get("inputActive") is False
        if is_idle and (i==0 or records[i-1].get("inputActive") is not False):start=i
        if start is not None and (not is_idle or i==len(records)-1):
            end=i if is_idle else i-1
            if end>=start:
                target=records[start]["targetProgress"]
                stable=all(abs(records[j]["targetProgress"]-target)<1e-9 for j in range(start,end+1))
                found=next((j for j in range(start,end+1) if abs(records[j]["displayProgress"]-target)<=epsilon),None) if stable else None
                settle_segments.append({"start_ms":records[start]["t_ms"],"end_ms":records[end]["t_ms"],"settled":found is not None,"settle_ms":round(records[found]["t_ms"]-records[start]["t_ms"],3) if found is not None else None,"target_stationary":stable})
            start=None
    if overshoot:warnings.append(f"{len(overshoot)} fixed-target overshoot crossings")
    if away:warnings.append(f"{len(away)} fixed-target movements away from actual target")
    if max_lag is not None and max(lag,default=0)>max_lag:warnings.append("lag exceeds configured threshold")
    if max_settle_ms is not None and any(x["settle_ms"] is not None and x["settle_ms"]>max_settle_ms for x in settle_segments):warnings.append("measured settle time exceeds configured threshold")
    if any(not x["settled"] and x["target_stationary"] for x in settle_segments):warnings.append("some idle intervals did not settle within the supplied log")
    return {"status":"LOG_ANALYSIS_ONLY" if not errors else "FAIL", "scope":"Only supplied samples; actual presentation/FPS/accessibility NOT VERIFIED", "samples":len(records),"max_abs_lag_p":round(max(lag,default=0),6),"mean_abs_lag_p":round(sum(lag)/len(lag),6) if lag else 0,"overshoot_sample_indices":overshoot,"movement_away_sample_indices":away,"direction_reversal_sample_indices":reversals,"idle_intervals":settle_segments,"warnings":warnings,"errors":errors}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("log",type=Path)
    p.add_argument("--max-lag",type=float,default=None)
    p.add_argument("--max-settle-ms",type=float,default=None)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    try:
        rows=[json.loads(line) for line in a.log.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError,ValueError,UnicodeError) as exc:
        print(json.dumps({"status":"FAIL","errors":[str(exc)]}));return 2
    report=analyze(rows,max_lag=a.max_lag,max_settle_ms=a.max_settle_ms)
    output=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    print(output,end="")
    if a.report:a.report.write_text(output,encoding="utf-8")
    return 2 if report["errors"] else 0

if __name__=="__main__":sys.exit(main())
