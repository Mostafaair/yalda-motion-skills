#!/usr/bin/env python3
"""Owner-configured media/frame cap planning and strict inventory validation.

Read-only against YALDA source/media. Writes a separate JSON report ONLY if --out.
Does NOT render, encode, optimize, fetch, or mutate source files. Disk bytes != network bytes.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
from decimal import Decimal, InvalidOperation
from collections import defaultdict

IMAGE_TYPES = {'.png','.jpg','.jpeg','.webp','.avif'}
SCHEMA='yalda.media-budget.v1'


def positive_int(x, name):
    if isinstance(x, bool) or not isinstance(x,int) or x<1:
        raise ValueError(f'{name}: expected positive integer')
    return x


def bytes_mb(x, name):
    if isinstance(x,bool) or isinstance(x,(list,dict)) or x is None:
        raise ValueError(f'{name}: expected positive decimal MB')
    try: v=Decimal(str(x))
    except InvalidOperation: raise ValueError(f'{name}: invalid MB')
    if not v.is_finite() or v<=0: raise ValueError(f'{name}: expected finite positive MB')
    result=int(v*Decimal(1_000_000))
    if result<1:raise ValueError(f'{name}: cap rounds to zero bytes')
    return result


def allocate(total, capacities, weights, minima):
    """Deterministic capped proportional allocation with guaranteed minima."""
    if total<sum(minima) or total>sum(capacities):
        raise ValueError('Frame budget infeasible for required minima and per-tier/per-stage caps')
    if any(v<mn for v,mn in zip(capacities,minima)):
        raise ValueError('Individual frame cap below stage minima')
    res=list(minima)
    remaining=total-sum(res)
    while remaining:
        eligible=[i for i,v in enumerate(res) if v<capacities[i]]
        if not eligible: raise ValueError('No eligible capacity for frame budget')
        denom=sum(weights[i] for i in eligible)
        shares=[(remaining*weights[i]/denom,i) for i in eligible]
        big=[(math.floor(v),i) for v,i in shares]
        taken=0
        for v,i in big:
            n=min(v,capacities[i]-res[i]);res[i]+=n;taken+=n
        remaining-=taken
        if remaining and taken==0:
            # Largest fractional remainder; stable by original index on tie.
            order=sorted(shares,key=lambda z:(-(z[0]-math.floor(z[0])),z[1]))
            for _,i in order:
                if remaining and res[i]<capacities[i]: res[i]+=1;remaining-=1
        elif remaining and taken>0:
            # Fast fill in a deterministic order to avoid roundoff stalling.
            pass
    return res


def validate_config(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:
        raise ValueError('Wrong budget schema')
    owner=doc.get('owner',{})
    if not isinstance(owner,dict) or type(owner.get('approved')) is not bool:
        raise ValueError('owner.approved must be boolean')
    if owner['approved'] and (not isinstance(owner.get('approval_id'),str) or not owner['approval_id'].strip()):
        raise ValueError('Owner approved=True requires nonempty approval_id')
    b=doc.get('budget',{})
    if b.get('scope')!='all_frame_files_all_tiers':
        raise ValueError('Scope MUST be all_frame_files_all_tiers, not bytes per device')
    if b.get('size_unit')!='MB_decimal_1000000':
        raise ValueError('Size unit must explicitly be MB_decimal_1000000')
    policy=b.get('count_policy')
    if policy not in ('maximum','exact'):
        raise ValueError('count_policy must be maximum or exact')
    if b.get('max_total_frames') is None or b.get('max_total_mb') is None:
        if owner['approved']: raise ValueError('Owner-approved budget cannot have empty frame or byte limits')
        return {'configured':False,'approved':False,'reason':'DRAFT_REQUIRES_OWNER_INPUT'}
    n=positive_int(b.get('max_total_frames'),'max_total_frames')
    cap_bytes=bytes_mb(b.get('max_total_mb'),'max_total_mb')
    tiers=doc.get('tiers',[])
    stages=doc.get('stages',[])
    if not isinstance(tiers,list) or not tiers or not isinstance(stages,list) or not stages:
        raise ValueError('Need nonempty tiers and stages')
    ids=[x.get('id') for x in tiers]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise ValueError('Tier IDs invalid or duplicate')
    sids=[x.get('id') for x in stages]
    if any(not isinstance(i,str) or not i for i in sids) or len(set(sids))!=len(sids):
        raise ValueError('Stage IDs invalid or duplicate')
    for t in tiers:
        if t.get('max_frames') is not None:positive_int(t.get('max_frames'),'tier.max_frames')
        if not isinstance(t.get('weight'),(int,float)) or t['weight']<=0 or not math.isfinite(t['weight']):
            raise ValueError('tier weight must be finite positive')
        if t.get('max_total_mb') is not None: bytes_mb(t['max_total_mb'],'tier.max_total_mb')
    last=0.0
    for j,s in enumerate(stages):
        v=s.get('p_range')
        if not isinstance(v,list) or len(v)!=2 or not all(isinstance(a,(float,int)) and not isinstance(a,bool) and math.isfinite(a) for a in v):
            raise ValueError('p_range must be numeric [start,end]')
        if not 0<=v[0]<v[1]<=1 or (j and v[0]<last-1e-9):
            raise ValueError('Stage p_ranges must be ordered and non-overlapping')
        if j == 0 and abs(v[0])>1e-8: raise ValueError('Stages must cover p=0')
        if j and abs(v[0]-prev_end)>1e-8: raise ValueError('Gaps between stages: declare an explicit hold stage')
        last=v[1];prev_end=v[1]
        positive_int(s.get('min_frames_per_tier'),'stage.min_frames_per_tier')
        if not isinstance(s.get('weight'),(int,float)) or s['weight']<=0 or not math.isfinite(s['weight']):
            raise ValueError('stage weight must be positive')
    if abs(last-1.0)>1e-8:raise ValueError('Stages must cover p=1')
    if sum(s['min_frames_per_tier'] for s in stages)*len(tiers)>n:
        raise ValueError('Budget smaller than mandatory stage minima across all tiers')
    return {'configured':True,'approved':owner['approved'],'global_max_frames':n,'global_max_bytes':cap_bytes,'count_policy':policy,'tiers':tiers,'stages':stages}


def plan(doc):
    conf=validate_config(doc)
    if not conf['configured']:
        return {'status':'DRAFT','reason':conf['reason'],'owner_approved':False,'measured':False}
    tiers=conf['tiers'];stages=conf['stages'];n=conf['global_max_frames']
    minimum=sum(s['min_frames_per_tier'] for s in stages)
    # A MAXIMUM is a cap, not a requirement to use every available slot.
    # EXACT must be feasible in full.
    capacities=[t['max_frames'] if t.get('max_frames') is not None else n for t in tiers]
    planned_n=min(n,sum(capacities)) if conf['count_policy']=='maximum' else n
    tier_counts=allocate(planned_n,capacities,[t['weight'] for t in tiers],[minimum]*len(tiers))
    tier_plans={}
    for t,c in zip(tiers,tier_counts):
        stage_counts=allocate(c,[c]*len(stages),[s['weight'] for s in stages],[s['min_frames_per_tier'] for s in stages])
        tier_plans[t['id']]={'planned_frames':c,'stage_counts':dict(zip([s['id'] for s in stages],stage_counts)),
                             'tier_max_bytes':bytes_mb(t['max_total_mb'],'tier.max_total_mb') if t.get('max_total_mb') is not None else None}
    return {'status':'PLAN_ONLY_NOT_MEASURED' if conf['approved'] else 'DRAFT_UNAPPROVED',
            'owner_approved':conf['approved'],'count_policy':conf['count_policy'],'scope':'ALL tiers counted together',
            'max_total_frames':n,'max_encoded_frame_bytes':conf['global_max_bytes'],
            'planned_frame_count':sum(tier_counts), 'global_average_bytes_per_frame_if_full_budget':conf['global_max_bytes']//n,
            'tier_plans':tier_plans,'measured':False,
            'caveat':'Planning is not render/encoding. Cannot promise fidelity or budget without actual assets; fail closed if constraints conflict.'}


def inspect_inventory(doc, root, manifest):
    conf=validate_config(doc)
    if not conf['configured']: raise ValueError('Owner budget is not configured')
    root=Path(root).resolve()
    if not root.is_dir(): raise ValueError('frames_root missing')
    data=json.loads(Path(manifest).read_text('utf-8-sig'))
    if not isinstance(data,dict) or not isinstance(data.get('frames'),list):
        raise ValueError('manifest must have frames array')
    tiers={x['id']:x for x in conf['tiers']}
    stages={x['id']:x for x in conf['stages']}
    seen=set();actual_count=defaultdict(int);actual_bytes=defaultdict(int);stage_count=defaultdict(int)
    p_by_tier=defaultdict(list); errors=[]
    for f in data['frames']:
        if not isinstance(f,dict): errors.append('Non-object frame');continue
        fn=f.get('file');t=f.get('tier');s=f.get('stage');p=f.get('p')
        if not isinstance(fn,str) or not fn or '\\' in fn or fn.startswith(('/','\\')) or '..' in Path(fn).parts:
            errors.append(f'Unsafe frame path {fn!r}');continue
        given_path=root/fn
        path=given_path.resolve()
        if not path.is_relative_to(root) or path.suffix.lower() not in IMAGE_TYPES or not path.is_file() or given_path.is_symlink():
            errors.append(f'Frame missing/unsafe/unsupported: {fn}');continue
        if path in seen: errors.append(f'Duplicate frame: {fn}');continue
        seen.add(path)
        if t not in tiers or s not in stages:
            errors.append(f'Unknown tier/stage for {fn}');continue
        if not isinstance(p,(int,float)) or isinstance(p,bool) or not math.isfinite(p) or not (stages[s]['p_range'][0]-1e-8<=p<=stages[s]['p_range'][1]+1e-8):
            errors.append(f'Invalid progress/stage for {fn}');continue
        sz=path.stat().st_size
        actual_count[t]+=1; actual_bytes[t]+=sz;stage_count[(t,s)]+=1;p_by_tier[t].append(p)
    all_files={p.resolve() for p in root.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_TYPES}
    extra=all_files-seen
    if extra: errors.append(f'{len(extra)} unlisted frame files in root: {sorted(str(p.relative_to(root)) for p in extra)[:4]}')
    for t,ps in p_by_tier.items():
        if any(a>b for a,b in zip(ps,ps[1:])):
            errors.append(f'Nonmonotonic manifest p order for tier {t}')
    for t,x in tiers.items():
        if x.get('max_frames') is not None and actual_count[t]>x['max_frames']: errors.append(f'Tier {t} exceeds frame cap')
        if x.get('max_total_mb') is not None and actual_bytes[t]>bytes_mb(x['max_total_mb'],'tier.max_total_mb'):
            errors.append(f'Tier {t} exceeds byte cap')
        for s,y in stages.items():
            if stage_count[(t,s)]<y['min_frames_per_tier']:
                errors.append(f'{t}/{s}: fewer frames than mandatory minimum')
    total_count=sum(actual_count.values());total_bytes=sum(actual_bytes.values())
    if total_count>conf['global_max_frames']:errors.append('Global total frame count exceeded')
    if conf['count_policy']=='exact' and total_count!=conf['global_max_frames']:
        errors.append('Exact frame count not satisfied')
    if total_bytes>conf['global_max_bytes']:errors.append('Global total frame byte cap exceeded')
    if not conf['approved']: errors.append('Owner budget not approved')
    return {'status':'FAIL' if errors else 'PASS','owner_approved':conf['approved'],
            'actual_all_tiers_frames':total_count,'actual_all_tiers_encoded_bytes_on_disk':total_bytes,
            'max_total_frames':conf['global_max_frames'],'max_frame_bytes':conf['global_max_bytes'],
            'tier_counts':dict(actual_count),'tier_encoded_bytes':dict(actual_bytes),
            'stage_counts':{f'{t}/{s}':n for (t,s),n in sorted(stage_count.items())},
            'errors':errors,'not_measured':['network transfer','decode latency','CPU/GPU memory','visual quality','presented FPS','scientific consistency'],
            'scope':'all_frame_files_all_tiers','measured':'encoded files on disk only'}


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--config',required=True)
    a.add_argument('--frames-root',help='Read-only directory containing all rendered frame files')
    a.add_argument('--manifest',help='JSON containing explicit frame file, tier, stage, p entries')
    a.add_argument('--out',help='Write report JSON to separate path, NOT to source root')
    x=a.parse_args(argv)
    cfg=json.loads(Path(x.config).read_text('utf-8-sig'))
    try:
        if bool(x.frames_root)!=bool(x.manifest):raise ValueError('Provide BOTH --frames-root and --manifest, or neither')
        result=inspect_inventory(cfg,x.frames_root,x.manifest) if x.manifest else plan(cfg)
    except (ValueError,OSError,KeyError,TypeError) as e:
        result={'status':'FAIL','errors':[str(e)]}
    output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if x.out:Path(x.out).write_text(output,'utf-8')
    else:print(output,end='')
    return 0 if result['status'] in ('PASS','PLAN_ONLY_NOT_MEASURED','DRAFT','DRAFT_UNAPPROVED') else 2

if __name__=='__main__':sys.exit(main())
