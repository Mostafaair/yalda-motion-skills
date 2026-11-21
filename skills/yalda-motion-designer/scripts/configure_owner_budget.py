#!/usr/bin/env python3
"""Create NEW Owner budget config from template (never patch YALDA site or source)."""
import argparse,json,sys
from pathlib import Path
from media_budget_contract import validate_config,plan

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--template',required=True,help='Existing owner-media-budget-TEMPLATE.json')
    ap.add_argument('--total-frames',required=True,type=int)
    ap.add_argument('--total-mb',required=True,type=float)
    ap.add_argument('--count-policy',choices=['maximum','exact'],default='maximum')
    ap.add_argument('--approval-id',help='Only when Owner explicitly approves these exact limits')
    ap.add_argument('--out',required=True,help='NEW file outside the template; refuses overwrite')
    z=ap.parse_args(argv)
    try:
        src=Path(z.template).resolve();out=Path(z.out).resolve()
        if out==src or out.exists():raise ValueError('Output must be a new file; overwrite is prohibited')
        obj=json.loads(src.read_text('utf-8-sig'))
        obj['budget']['max_total_frames']=z.total_frames
        obj['budget']['max_total_mb']=z.total_mb
        obj['budget']['count_policy']=z.count_policy
        if z.approval_id:
            obj['owner']['approved']=True
            obj['owner']['approval_id']=z.approval_id
        else:
            obj['owner']['approved']=False
            obj['owner']['approval_id']=None
        # Never infer per-tier caps from a global Owner limit; accept None and propose split.
        validate_config(obj)
        preview=plan(obj)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
        print(json.dumps({'config_saved_to':str(out),'plan':preview},ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'FAIL','error':str(e)}),file=sys.stderr)
        return 2
if __name__=='__main__':sys.exit(main())
