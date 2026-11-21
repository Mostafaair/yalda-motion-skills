#!/usr/bin/env python3
"""Validate declarative YALDA scroll overlay/caption contract. No browser or site modification."""
import argparse,json,math,re,sys
from pathlib import Path
SCHEMA='yalda.motion-overlays.v1'
MODES={'below_media','within_stage_fixed','floating_scroll','scene_anchored'}
BAD_MARKUP=re.compile(r'<\s*/?\s*[a-z!]|\bon\w+\s*=|javascript\s*:',re.I)

def validate(doc):
    errors=[];warnings=[]
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:return {'status':'FAIL','errors':['Incorrect schema']}
    overlays=doc.get('overlays')
    if not isinstance(overlays,list):return {'status':'FAIL','errors':['overlays must be list']}
    if doc.get('owner_approved_text') is True and not isinstance(doc.get('owner_text_approval_id'),str):
        errors.append('Owner-approved text requires an owner_text_approval_id')
    seen=set()
    for j,c in enumerate(overlays):
        if not isinstance(c,dict):errors.append(f'Overlay {j} not object');continue
        prefix=f'overlay[{j}]';id=c.get('id')
        if not isinstance(id,str) or not id or id in seen:errors.append(f'{prefix}: missing/duplicate id')
        seen.add(id)
        mode=c.get('mode');loc=c.get('placement',{});tm=c.get('interval',{})
        if mode not in MODES:errors.append(f'{prefix}: unsupported mode');continue
        if not isinstance(tm,dict):errors.append(f'{prefix}: invalid interval');continue
        s,e=tm.get('p_start'),tm.get('p_end')
        if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (s,e)) or not (0<=s<e<=1):
            errors.append(f'{prefix}: invalid p_start/p_end')
        content=c.get('text')
        if not isinstance(content,dict) or any(not isinstance(content.get(lang),str) or not content[lang].strip() for lang in ('fa','en')):
            errors.append(f'{prefix}: both fa and en visible text required')
        else:
            if any(BAD_MARKUP.search(content[k]) for k in ('fa','en')):
                errors.append(f'{prefix}: text must be plain text (render via textContent, not innerHTML)')
            if max(len(content[k]) for k in ('fa','en'))>700:
                warnings.append(f'{prefix}: long overlay; manual mobile readability review')
        if not isinstance(loc,dict):errors.append(f'{prefix}: placement must be object');continue
        if mode=='scene_anchored':
            if not isinstance(loc.get('model_anchor_id'),str) or not loc['model_anchor_id'].strip():
                errors.append(f'{prefix}: scene anchor model id required for shared camera projection')
            if loc.get('coordinate_space')!='scene_world':
                errors.append(f'{prefix}: anchored overlay must share scene_world projection')
        elif mode=='floating_scroll':
            factor=loc.get('parallax_factor',0)
            if not isinstance(factor,(int,float)) or isinstance(factor,bool) or not math.isfinite(factor) or not -.5<=factor<=.5:
                errors.append(f'{prefix}: parallax_factor must be [-0.5, 0.5]')
        if mode=='below_media' and loc.get('layout')!='normal_document_flow':
            errors.append(f'{prefix}: below_media requires reserved normal document flow')
        if mode=='within_stage_fixed' and loc.get('coordinate_space')!='story_stage':
            errors.append(f'{prefix}: within_stage_fixed must be anchored to story_stage, not whole viewport')
        if c.get('required_information') is True and c.get('reduced_motion_behavior')=='hidden':
            errors.append(f'{prefix}: required information cannot disappear in reduced motion')
        if c.get('reduced_motion_behavior') not in ('static','visible','hidden'):
            errors.append(f'{prefix}: invalid reduced_motion_behavior')
        if c.get('html_layer') is not True:
            errors.append(f'{prefix}: overlay must be real HTML text, not rasterized into frames')
    return {'status':'FAIL' if errors else 'PASS','overlay_count':len(overlays),'errors':errors,'warnings':warnings,
            'owner_text_gate':'APPROVED_STRUCTURAL_ONLY' if doc.get('owner_approved_text') is True and not errors else 'HOLD_OWNER_APPROVAL',
            'limits':'Structural only: readability, overlap, RTL, source/render alignment and screen reader behavior require browser QA'}

def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('contract');a.add_argument('--out');x=a.parse_args(argv)
    try:r=validate(json.loads(Path(x.contract).read_text('utf-8-sig')))
    except (ValueError,OSError,TypeError) as e:r={'status':'FAIL','errors':[str(e)]}
    out=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if x.out:Path(x.out).write_text(out,'utf-8')
    else:print(out,end='')
    return 0 if r['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())
