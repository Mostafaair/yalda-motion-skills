#!/usr/bin/env python3
"""Validate the actual R4 Visual Timeline v1 JSON structure (never render or edit source).

PASS is SCHEMA_ONLY. Real position, clipping, camera, CSS and Owner visual approval
require real browser evidence. Standard library only.
"""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from pathlib import Path

FIELDS = {"p", "posX", "posY", "opacity", "scale"}
SPACES = {"stage", "workspace", "foundation"}
CHAPTERS = {f"{n:02d}" for n in range(8)}
METHODS = {"linear", "smoothstep"}
RAIL_NAMES = {"gap", "compactGap", "entryStart", "entryMid", "entryEnd", "exitTopPx", "exitGapPx", "compactExitGapPx"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,49}$")


def numeric(x):
    return type(x) in (float, int) and math.isfinite(x)


def smoothstep(x):
    return x*x*(3-2*x)


def interpolate(keys, progress, method):
    # Mirror the runtime validator: sorted p and bounded numeric presentation values.
    keys = sorted(({**k, "posX": min(10000,max(-10000,k["posX"])),
                    "posY": min(10000,max(-10000,k["posY"])),
                    "opacity": min(1,max(0,k["opacity"])),
                    "scale": min(4,max(.05,k["scale"]))} for k in keys), key=lambda k:k["p"])
    p = min(1.0, max(0.0, progress))
    if p <= keys[0]["p"]:
        return {k: keys[0][k] for k in FIELDS if k != "p"}
    if p >= keys[-1]["p"]:
        return {k: keys[-1][k] for k in FIELDS if k != "p"}
    for a, b in zip(keys, keys[1:]):
        if a["p"] <= p <= b["p"]:
            x = (p-a["p"])/(b["p"]-a["p"])
            t = smoothstep(x) if method == "smoothstep" else x
            return {k: a[k]+(b[k]-a[k])*t for k in FIELDS if k != "p"}
    raise AssertionError("unreachable")


def validate(data):
    failures, warnings, counts = [], [], {"elements": 0, "tracks": 0, "keyframes": 0, "compactTracks": 0}
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("elements"), dict):
        return ["root: expected version=1 and elements object"], warnings, counts
    unknown = set(data) - {"version", "elements", "rail"}
    if unknown:
        warnings.append(f"root: unsupported fields {sorted(unknown)} may be dropped on runtime import/export")
    if not data["elements"]:
        failures.append("elements: empty dictionary")

    def check_keys(keys, where):
        if not isinstance(keys, list) or not keys:
            failures.append(f"{where}: keyframes must be a nonempty list")
            return
        seen = set()
        last = float("-inf")
        for i, key in enumerate(keys):
            tag=f"{where}[{i}]"
            if not isinstance(key, dict) or set(key) != FIELDS or not all(numeric(key.get(k)) for k in FIELDS):
                failures.append(f"{tag}: must contain exactly five finite numeric fields {sorted(FIELDS)}")
                continue
            p=key["p"]
            if not 0 <= p <= 1: failures.append(f"{tag}: p out of [0,1]")
            if p in seen: failures.append(f"{tag}: duplicate p={p}")
            if p < last: warnings.append(f"{where}: unsorted p input (runtime sorts)")
            last=p;seen.add(p)
            if not 0 <= key["opacity"] <= 1: warnings.append(f"{tag}: opacity would be clamped by runtime")
            if not .05 <= key["scale"] <= 4: warnings.append(f"{tag}: scale would be clamped by runtime")
            if abs(key["posX"]) > 10000 or abs(key["posY"]) > 10000: warnings.append(f"{tag}: coordinates would be clamped")
            counts["keyframes"] += 1
    for element_id, item in data["elements"].items():
        counts["elements"] += 1
        if not ID_RE.fullmatch(element_id): failures.append(f"{element_id}: invalid element id")
        if not isinstance(item, dict):
            failures.append(f"{element_id}: element must be object")
            continue
        if not isinstance(item.get("label"), str) or not item["label"].strip() or len(item["label"]) > 100:
            failures.append(f"{element_id}: invalid label")
        if item.get("space") not in SPACES: failures.append(f"{element_id}: unsupported space")
        other = set(item) - {"label", "space", "chapters", "text"}
        if other: warnings.append(f"{element_id}: unknown fields {sorted(other)}")
        if "text" in item:
            txt = item["text"]
            if not (isinstance(txt, dict) and item.get("space") == "stage" and txt.get("lang") in ("en", "fa") and isinstance(txt.get("content"), str) and txt["content"].strip() and len(txt["content"]) <= 240):
                failures.append(f"{element_id}: invalid stage text definition")
            if isinstance(txt,dict) and set(txt)-{"lang","content"}:
                warnings.append(f"{element_id}: unsupported text fields may be dropped")
        chapters = item.get("chapters")
        if not isinstance(chapters, dict) or not chapters:
            failures.append(f"{element_id}: nonempty chapters object required")
            continue
        for chap, track in chapters.items():
            counts["tracks"] += 1
            where=f"{element_id}/chapter-{chap}"
            if chap not in CHAPTERS or not isinstance(track, dict) or track.get("interpolation", "smoothstep") not in METHODS:
                failures.append(f"{where}: invalid chapter/track/interpolation")
                continue
            other=set(track)-{"interpolation", "keyframes", "compact"}
            if other:warnings.append(f"{where}: fields {sorted(other)} not supported by v1 runtime")
            check_keys(track.get("keyframes"), where)
            if "compact" in track:
                counts["compactTracks"] += 1
                check_keys(track["compact"], where+"/compact")
    if "rail" in data:
        rail=data["rail"]
        if not isinstance(rail,dict): failures.append("rail: must be object")
        else:
            for k,v in rail.items():
                if k not in RAIL_NAMES: warnings.append(f"rail.{k}: unknown rail property")
                elif not numeric(v): failures.append(f"rail.{k}: must be finite number")
            for k in ("gap", "compactGap", "exitTopPx", "exitGapPx", "compactExitGapPx"):
                if k in rail and numeric(rail[k]) and rail[k]<0:failures.append(f"rail.{k}: negative prohibited")
            if all(k in rail and numeric(rail[k]) for k in ("entryStart","entryMid","entryEnd")):
                if not (0 <= rail["entryStart"] < rail["entryMid"] < rail["entryEnd"] <= 1):
                    failures.append("rail: must satisfy 0<=entryStart<entryMid<entryEnd<=1")
    # Chapter boundary continuity is a *warning*, not a blanket failure: deliberate scene cuts exist.
    for element_id,item in data["elements"].items():
        if not isinstance(item,dict) or not isinstance(item.get("chapters"),dict):continue
        for n in range(7):
            prev=item["chapters"].get(f"{n:02d}")
            nxt=item["chapters"].get(f"{n+1:02d}")
            if not isinstance(prev,dict) or not isinstance(nxt,dict):continue
            for profile in ["keyframes", "compact"]:
                before = prev.get(profile,prev.get("keyframes"))
                after = nxt.get(profile,nxt.get("keyframes"))
                if not isinstance(before,list) or not isinstance(after,list) or not before or not after:continue
                if any(not isinstance(k,dict) or not all(numeric(k.get(f)) for f in FIELDS) for k in before+after):continue
                a=max(before,key=lambda k:k["p"]);b=min(after,key=lambda k:k["p"])
                deltas={k:round(b[k]-a[k],4) for k in ("posX", "posY", "opacity", "scale")}
                if any(abs(v)>1e-3 for v in deltas.values()):
                    warnings.append(f"boundary {element_id} {n:02d}->{n+1:02d} {profile}: declared pose change {deltas}; verify intentional cut")
    return failures,warnings,counts


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("timeline",type=Path)
    ap.add_argument("--report",type=Path,help="Save JSON report outside protected source")
    ap.add_argument("--fail-on-warnings",action="store_true")
    ap.add_argument("--sample",nargs=3,metavar=("ELEMENT","CHAPTER","P"),help="Raw v1 track sample, not effective common-rail pose")
    ap.add_argument("--compact",action="store_true",help="Use compact keys if present")
    a=ap.parse_args()
    try:
        data=json.loads(a.timeline.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as e:
        print(json.dumps({"status":"FAIL","errors":[str(e)]},ensure_ascii=False,indent=2));return 2
    err,warn,counts=validate(data)
    report={"status":"STRUCTURAL_PASS_NOT_VISUAL_VERIFICATION" if not err else "FAIL","scope":"static R4 timeline v1, no browser or engineering validation","source":str(a.timeline),"counts":counts,"errors":err,"warnings":warn}
    if a.sample and not err:
        name,ch,p=a.sample;p=float(p)
        element=data["elements"].get(name,{})
        track=element.get("chapters",{}).get(ch)
        if track is None:report["errors"].append("unknown element/chapter for sample"); report["status"]="FAIL"
        else: report["sample"]={"element":name,"chapter":ch,"p":p,"compact":a.compact,"raw_track_pose":interpolate(track.get("compact") if a.compact and track.get("compact") else track["keyframes"],p,track.get("interpolation","smoothstep")),"WARNING":"Effective runtime pose may differ when driven by common rail/parent transforms"}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if a.report:a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return 1 if report["errors"] or a.fail_on_warnings and warn else 0

if __name__=="__main__":sys.exit(main())
