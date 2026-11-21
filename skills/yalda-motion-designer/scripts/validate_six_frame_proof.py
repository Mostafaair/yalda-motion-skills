#!/usr/bin/env python3
"""Strict *structural* six-frame evidence preflight; not a rendered-scene verifier.

Six native independently named PNG outputs with camera/object provenance;
SUCCESS does NOT prove that the renderer actually generated the files, nor
visual fidelity or scientific mapping to SAFE.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
EXPECTED={'A1':0.0,'A2':0.5,'A3':1.0,'C1':0.0,'C2':0.5,'C3':1.0}
PNG_MAGIC=b'\x89PNG\r\n\x1a\n'

def relpath(base,value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value:return None
    p=Path(value)
    if p.is_absolute() or any(v in ('..','.') for v in p.parts):return None
    file=base/p
    if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(base.resolve()):return None
    return file

def validate(manifest,root):
    base=Path(root)
    m=json.loads(Path(manifest).read_text('utf-8'))
    errs=[];seen=set();seen_sha=set();seen_paths=set();ids_by_stage={}
    scene=relpath(base,m.get('scene_source'))
    render=relpath(base,m.get('renderer_source'))
    if not scene:errs.append('Missing or unsafe common scene source')
    if not render:errs.append('Missing or unsafe renderer source')
    if not isinstance(m.get('render_command'),str) or not m['render_command'].strip():
        errs.append('Missing deterministic render_command')
    frames=m.get('frames',[])
    if not isinstance(frames,list) or len(frames)!=6:
        errs.append('Expected exactly six individual frame records')
        frames=frames if isinstance(frames,list) else []
    for item in frames:
        if not isinstance(item,dict):errs.append('Invalid frame entry');continue
        k=item.get('id')
        if k not in EXPECTED or k in seen:errs.append(f'Unexpected or duplicate ID {k}');continue
        seen.add(k)
        if item.get('p')!=EXPECTED[k]:errs.append(f'Wrong p for {k}')
        camera=item.get('camera')
        if (not isinstance(camera,dict) or
            camera.get('projection') not in ('perspective','orthographic') or
            any(not isinstance(camera.get(key),list) or len(camera.get(key))!=3 or
                any(isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n)
                    for n in camera.get(key,[])) for key in ('position','rotation'))):
            errs.append(f'Missing or malformed camera data {k}')
        objs=item.get('stable_object_ids')
        if not isinstance(objs,list) or not objs or not all(isinstance(x,str) and x for x in objs):
            errs.append(f'Missing stable object IDs {k}')
        else:ids_by_stage[k]=set(objs)
        if item.get('file') in seen_paths:errs.append(f'Duplicate image path {k}')
        seen_paths.add(item.get('file'))
        f=relpath(base,item.get('file'))
        if not f or f.suffix.lower()!='.png':errs.append(f'Missing/invalid native PNG {k}');continue
        data=f.read_bytes()
        if not data.startswith(PNG_MAGIC):errs.append(f'Invalid PNG signature {k}')
        sha=hashlib.sha256(data).hexdigest()
        if sha in seen_sha:errs.append(f'Identical frame file bytes for {k}')
        seen_sha.add(sha)
        if item.get('sha256')!=sha:errs.append(f'Invalid frame checksum {k}')
    if set(EXPECTED)!=seen:errs.append('Missing one or more required proof IDs')
    for group in (('A1','A2','A3'),('C1','C2','C3')):
        if all(k in ids_by_stage for k in group) and not set.intersection(*(ids_by_stage[k] for k in group)):
            errs.append(f'No stable common object ID across {group}')
    if m.get('actual_safe_mapping_status') not in ('VERIFIED','UNVERIFIED','CONCEPTUAL'):
        errs.append('Scientific status must be explicitly declared')
    if m.get('source_claim') not in ('RENDERED_FROM_COMMON_SCENE','CONCEPTUAL_RECONSTRUCTION'):
        errs.append('Missing scene provenance declaration')
    return {'status':'FAIL' if errs else 'STRUCTURAL_PASS_NOT_RENDER_VERIFICATION',
            'errors':errs,'frames_found':len(seen),
            'owner_visual_acceptance':'NOT_TESTED',
            'camera_geometry_continuity':'NOT_TESTED',
            'actual_SAFE_mapping':'NOT_TESTED_UNLESS_INDEPENDENTLY_VERIFIED',
            'note':'A valid manifest cannot prove rendered origin, continuity or scientific truth.'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',required=True);p.add_argument('--root',required=True);a=p.parse_args(argv)
    try:out=validate(a.manifest,a.root)
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as e:out={'status':'FAIL','errors':[str(e)]}
    print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['status']!='FAIL' else 1
if __name__=='__main__':sys.exit(main())
