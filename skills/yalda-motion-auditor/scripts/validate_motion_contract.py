#!/usr/bin/env python3
"""Validate declared camera/landmark C0 and optional C1; NOT actual rendered/scientific proof."""
import argparse,json,math
from pathlib import Path
def vector(v,n):return isinstance(v,list) and len(v)==n and all(type(x) in (int,float) and math.isfinite(x) for x in v)
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def validate(data,tolerance=1e-7):
    errors=[];warnings=[];boundaries=[]
    if not isinstance(data,dict):return {'structurally_valid':False,'errors':['Must be object'],'warnings':[], 'science_verified':False}
    for k in ('contract_version','reference_build_sha256','geometry_source','units','coordinate_system','progress','stages','viewport','scene_object_ids','approved_checkpoints','scientific_provenance'):
        if k not in data:errors.append('Missing: '+k)
    sha=data.get('reference_build_sha256')
    good_sha=isinstance(sha,str) and len(sha)==64 and all(c in '0123456789abcdefABCDEF' for c in sha)
    if not good_sha:warnings.append('reference_build_sha256 missing/invalid: draft only')
    viewport=data.get('viewport')
    if not isinstance(viewport,dict) or any(type(viewport.get(k)) not in (int,float) or not math.isfinite(viewport[k]) or viewport[k]<=0 for k in ('width_css_px','height_css_px','dpr')):errors.append('viewport width/height/dpr must be finite positive')
    ids=data.get('scene_object_ids')
    if not isinstance(ids,list) or not ids or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids):errors.append('scene_object_ids must be unique nonempty strings')
    checkpoints=data.get('approved_checkpoints')
    if not isinstance(checkpoints,list) or not checkpoints:errors.append('approved_checkpoints required')
    elif any(not isinstance(x,dict) or x.get('status')!='APPROVED' for x in checkpoints):warnings.append('Approved checkpoints remain UNVERIFIED/DRAFT')
    progress=data.get('progress')
    if not isinstance(progress,dict) or type(progress.get('start')) not in (int,float) or type(progress.get('end')) not in (int,float) or progress['start']!=0 or progress['end']!=1:errors.append('progress must span [0,1]')
    if isinstance(progress,dict) and progress.get('deterministic_reverse') is not True:warnings.append('Reverse determinism not declared')
    tol=data.get('continuity_tolerance_css_px')
    if type(tol) not in (int,float) or not math.isfinite(tol) or tol<0:errors.append('continuity_tolerance_css_px invalid');tol=0
    if data.get('continuity_tolerance_status')!='OWNER_APPROVED':warnings.append('C0 tolerance provisional; not Owner-approved')
    stages=data.get('stages')
    if not isinstance(stages,list) or not stages:errors.append('stages must be nonempty list');stages=[]
    prev=None;names=set()
    for i,st in enumerate(stages):
        if not isinstance(st,dict):errors.append(f'Stage {i}: not object');continue
        for k in ('id','p_start','p_end','start_state_id','end_state_id','camera_path_id','geometry_mapping_id','start_camera','end_camera','start_landmarks_css_px','end_landmarks_css_px'):
            if k not in st:errors.append(f'Stage {i}: missing {k}')
        sid=st.get('id')
        if not isinstance(sid,str) or sid in names or not sid:errors.append(f'Stage {i}: duplicate/invalid ID')
        names.add(sid)
        a,b=st.get('p_start'),st.get('p_end')
        if type(a) not in (int,float) or type(b) not in (int,float) or not math.isfinite(a) or not math.isfinite(b) or not 0<=a<b<=1:errors.append(f'Stage {i}: invalid interval')
        elif i==0 and abs(a)>tolerance:errors.append('First stage must start p0')
        for side in ('start','end'):
            cam=st.get(side+'_camera')
            if not isinstance(cam,dict) or not all(vector(cam.get(k),3) for k in ('position_world','look_at_world')) or cam.get('projection') not in ('perspective','orthographic') or type(cam.get('projection_parameter')) not in (int,float) or not math.isfinite(cam['projection_parameter']) or cam['projection_parameter']<=0 or (cam['projection']=='perspective' and cam['projection_parameter']>=180):errors.append(f'Stage {i}: invalid {side} camera')
            marks=st.get(side+'_landmarks_css_px')
            if not isinstance(marks,dict) or not marks or any(not isinstance(k,str) or not vector(v,2) for k,v in marks.items()):errors.append(f'Stage {i}: invalid {side} landmarks')
            elif isinstance(ids,list) and any(k not in ids for k in marks):errors.append(f'Stage {i}: unknown landmark ID')
        if prev and type(a) in (int,float):
            label=f'{prev.get("id")} → {sid}'
            if type(prev.get('p_end')) in (int,float) and abs(a-prev['p_end'])>tolerance:errors.append('Disjoint interval: '+label)
            if prev.get('end_state_id')!=st.get('start_state_id'):errors.append('State boundary mismatch: '+label)
            bd={'from':prev.get('id'),'to':sid,'landmark_c0_css_px':{},'camera_c0_world':{},'declared_c1_status':'NOT TESTED'}
            l=prev.get('end_landmarks_css_px');r=st.get('start_landmarks_css_px')
            if isinstance(l,dict) and isinstance(r,dict):
                if set(l)!=set(r):errors.append('Landmark identity mismatch: '+label)
                for k in set(l)&set(r):
                    if vector(l[k],2) and vector(r[k],2):
                        d=dist(l[k],r[k]);bd['landmark_c0_css_px'][k]=round(d,6)
                        if d>tol+tolerance:errors.append(f'Landmark C0 exceeds tolerance: {label}/{k} {d:.3f}px')
            lc=prev.get('end_camera');rc=st.get('start_camera')
            if isinstance(lc,dict) and isinstance(rc,dict):
                for k in ('position_world','look_at_world'):
                    if vector(lc.get(k),3) and vector(rc.get(k),3):
                        d=dist(lc[k],rc[k]);bd['camera_c0_world'][k]=round(d,8)
                        if d>tolerance:errors.append('Camera C0 world mismatch: '+label+'/'+k)
                if lc.get('projection')!=rc.get('projection') or lc.get('projection_parameter')!=rc.get('projection_parameter'):errors.append('Camera projection mismatch: '+label)
            v1=prev.get('end_velocity_css_px_per_p');v2=st.get('start_velocity_css_px_per_p')
            if v1 is not None and v2 is not None:
                if not isinstance(v1,dict) or not isinstance(v2,dict) or set(v1)!=set(v2) or any(not vector(v,2) for v in list(v1.values())+list(v2.values())):errors.append('C1 velocity shape mismatch: '+label)
                else:
                    j=max([dist(v1[k],v2[k]) for k in v1],default=0);bd['declared_c1_status']='DECLARED_VELOCITY_COMPARED';bd['max_declared_c1_jump_css_px_per_p']=j
                    vtol=data.get('continuity_velocity_tolerance_css_px_per_p')
                    if type(vtol) not in (int,float) or not math.isfinite(vtol) or vtol<0:warnings.append('Velocity tolerance missing; no C1 PASS')
                    elif j>vtol+tolerance:errors.append('Declared C1 mismatch: '+label)
            boundaries.append(bd)
        prev=st
    if prev and type(prev.get('p_end')) in (int,float) and abs(prev['p_end']-1)>tolerance:errors.append('Last stage must end p1')
    for k in ('geometry_source','units','coordinate_system','scientific_provenance'):
        if not isinstance(data.get(k),str) or not data[k] or 'UNVERIFIED' in data[k].upper():warnings.append(k+': not independently verified')
    return {'structurally_valid':not errors,'errors':errors,'warnings':warnings,'declared_boundary_checks':boundaries,
      'declared_c0_comparison_performed':bool(boundaries),'reference_build_sha256_well_formed':good_sha,'reference_build_verified':False,
      'science_verified':False,'rendered_continuity_measured':False,'acceptance_ready':False,
      'disclaimer':'Declared endpoint consistency only; not observed site motion, scientific verification or actual source hash verification.'}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('contract');ap.add_argument('--out');a=ap.parse_args();r=validate(json.loads(Path(a.contract).read_text('utf8')))
    text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.out:Path(a.out).write_text(text,encoding='utf8')
    else:print(text,end='')
    if not r['structurally_valid']:raise SystemExit(2)
if __name__=='__main__':main()
