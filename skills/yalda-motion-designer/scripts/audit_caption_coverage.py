#!/usr/bin/env python3
"""Conservative sampled visual-caption coverage preflight. Not a browser visual PASS.
Input JSONL records:
{"global_p":0.1,"viewport":{"width":1366,"height":768},"captions":[
{"id":"caption_00","opacity":0.8,"rect":{"left":100,"top":100,"right":600,"bottom":170},
 "occluded_fraction":0.0,"visibility":"visible"}]}
"""
import argparse, json, math, sys

def finite(n): return isinstance(n,(float,int)) and not isinstance(n,bool) and math.isfinite(n)

def evaluate(samples,max_gap=0.03,min_alpha=0.30,min_visible=0.25):
    errors=[]; warns=[]; rows=[]; old=None
    for i,s in enumerate(samples):
        p=s.get('global_p')
        if not finite(p) or not 0<=p<=1:
            errors.append(f'sample {i}: invalid global_p');continue
        if old is not None and p <= old:
            errors.append(f'sample {i}: duplicate or unsorted progress')
        if old is not None and p-old > max_gap+1e-9:
            errors.append(f'sample {i}: unsampled gap {p-old:.5f} > {max_gap:.3f}')
        old=p
        vp=s.get('viewport',{})
        w,h=vp.get('width'),vp.get('height')
        if not finite(w) or not finite(h) or w<=0 or h<=0:
            errors.append(f'sample {i}: invalid viewport');continue
        visible=[]; potential=[]
        for cap in s.get('captions',[]):
            a=cap.get('opacity',0);r=cap.get('rect',{})
            if not finite(a) or not 0<=a<=1:
                errors.append(f'sample {i}: invalid caption opacity');continue
            rect=[r.get(k) for k in ('left','top','right','bottom')]
            if not all(finite(v) for v in rect):
                errors.append(f'sample {i}: missing/bad text bounding rect');continue
            left,top,right,bottom=rect
            area=max(0,right-left)*max(0,bottom-top)
            on=max(0,min(w,right)-max(0,left))*max(0,min(h,bottom)-max(0,top))
            frac=on/area if area else 0
            if cap.get('visibility','visible')=='hidden':continue
            occ=cap.get('occluded_fraction',None)
            if occ is None:
                warns.append(f'sample {i}: caption {cap.get("id", "?")} has no occlusion measurement')
                occ=0
            if not finite(occ) or not 0<=occ<=1:
                errors.append(f'sample {i}: invalid occluded_fraction');continue
            if a>=min_alpha and frac >= min_visible and occ<0.5:
                visible.append(cap.get('id','unknown'))
            if a>0 and frac>0:potential.append(cap.get('id','unknown'))
        rows.append({'p':p,'readable_candidates':visible,'visible_candidates':potential})
        if not visible: errors.append(f'sample {i}: no geometrically readable caption at p={p:.5f}')
    if not samples:errors.append('no samples')
    elif rows:
        if rows[0]['p']>max_gap:errors.append('hero start not sampled')
        if rows[-1]['p']<1-max_gap:errors.append('hero endpoint not sampled')
    return {'status':'INCOMPLETE' if errors else 'STRUCTURAL_COVERAGE_PASS_NOT_VISUAL_ACCEPTANCE',
            'sample_count':len(samples),'errors':errors,'warnings':sorted(set(warns)), 'rows':rows,
            'limits':'No browser visual, contrast, shadow, correct text content, accurate occlusion or physical-device PASS is implied.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('jsonl');ap.add_argument('--max-gap',type=float,default=.03);ap.add_argument('--min-alpha',type=float,default=.30)
    a=ap.parse_args()
    with open(a.jsonl,encoding='utf-8') as f: samples=[json.loads(line) for line in f if line.strip()]
    report=evaluate(samples,a.max_gap,a.min_alpha)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if not report['errors'] else 2
if __name__=='__main__':sys.exit(main())
