#!/usr/bin/env python3
"""YALDA task-level advisory budget ledger and fail-closed preflight.

Never claims to read ChatGPT Work's proprietary usage quota. User-entered
budgets and manually provided measurements/estimates are explicit and separate.
Patterns from official Anthropic cost-optimization / task budgets and OpenAI
Skill efficiency evals; independently implemented local Python utility.
"""
import argparse
import datetime as dt
import decimal
import json
import math
from pathlib import Path
import os
import tempfile
import sys

METRICS=('elapsed_minutes','model_tokens','tool_calls','render_jobs','external_cost_usd')
APPROVAL='owner'


def parse_quantity(x,metric):
    if x is None:return None
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<0:
        raise ValueError(f'Invalid nonnegative finite {metric}')
    if metric in ('model_tokens','tool_calls','render_jobs') and int(x)!=x:
        raise ValueError(f'{metric} must be integer')
    return x


def validate_config(conf):
    if conf.get('schema')!=1:raise ValueError('Invalid config schema')
    owner=conf.get('owner')
    if not isinstance(owner,dict):raise ValueError('owner required')
    if owner.get('approved') is True and not owner.get('approval_id'):
        raise ValueError('Owner approval_id required')
    if not isinstance(owner.get('approved'),bool):raise ValueError('Owner approved must be bool')
    limits=conf.get('limits',{})
    if not isinstance(limits,dict):raise ValueError('limits must be object')
    for k in METRICS:parse_quantity(limits.get(k),k)
    if owner.get('approved') is True and all(limits.get(k) is None for k in METRICS):
        raise ValueError('Approved budget must define at least one explicit limit')
    threshold=conf.get('soft_stop_ratio')
    if threshold is not None and (isinstance(threshold,bool) or not isinstance(threshold,(int,float)) or not 0<threshold<1):
        raise ValueError('soft_stop_ratio must be between 0 and 1')
    if conf.get('work_quota_visibility')!='NOT_ACCESSIBLE':
        raise ValueError('Never assert ChatGPT Work quota visibility')
    return conf


def _atomic(path,obj):
    raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix='._budget_')
    try:
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def state_path(workdir):return Path(workdir).resolve()/'.yalda-motion-state'/'budget.json'


def init(workdir,config):
    dst=state_path(workdir)
    if dst.exists():raise ValueError('Budget ledger exists; do not reset usage')
    conf=validate_config(json.loads(Path(config).read_text('utf-8')))
    state={'schema':1,'config':conf,'events':[],'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
           'usage':{k:0 for k in METRICS},'unmeasured':[]}
    _atomic(dst,state)
    return {'status':'READY' if conf['owner']['approved'] else 'DRAFT_UNAPPROVED',
            'ledger':str(dst),'quota':'NOT_ACCESSIBLE'}


def read(workdir):
    p=state_path(workdir)
    if not p.is_file():raise ValueError('No ledger; init first')
    state=json.loads(p.read_text('utf-8'));validate_config(state['config']);return state


def amounts(doc):
    if not isinstance(doc,dict):raise ValueError('Usage file must be object')
    return {k:parse_quantity(doc.get(k),k) for k in METRICS}


def evaluate(state,next_usage=None):
    conf=validate_config(state['config'])
    if not conf['owner']['approved']:
        return {'status':'HOLD_OWNER_BUDGET_UNAPPROVED','quota':'NOT_ACCESSIBLE'}
    estimates=amounts(next_usage or {})
    usage=state['usage'];limits=conf['limits']
    hard=[];soft=[];unknown=[];remaining={}
    for k in METRICS:
        limit=limits.get(k)
        if limit is None:
            remaining[k]=None;continue
        remaining[k]=max(0,limit-usage[k])
        if k in state['unmeasured'] or estimates[k] is None:
            unknown.append(k);continue
        prospective=usage[k]+estimates[k]
        if prospective>limit:
            hard.append(k)
        elif prospective==limit:
            # At exact cap this action may complete, but no follow-up is allowed.
            soft.append(k)
        elif conf.get('soft_stop_ratio') is not None and prospective>=limit*conf['soft_stop_ratio']:
            soft.append(k)
    if hard:status='STOP_HARD_LIMIT'
    elif unknown:status='HOLD_UNMEASURED'
    elif soft:status='CHECKPOINT_AND_REASSESS'
    else:status='PASS_WITHIN_DECLARED_LIMITS'
    return {'status':status,'hard_limit_metrics':hard,'unknown_metrics':unknown,
            'soft_notice_metrics':soft,'remaining_before_next_action':remaining,
            'quota':'NOT_ACCESSIBLE','disclaimer':'Does not measure Work subscription/tool limits or guarantee external persistence'}


def record(workdir,usage_file):
    s=read(workdir);doc=json.loads(Path(usage_file).read_text('utf-8'))
    measured=amounts(doc.get('measured',{}))
    # Declared estimates are not silently added to measured totals.
    estimated=amounts(doc.get('estimated',{}))
    label=doc.get('action')
    if not isinstance(label,str) or not label.strip() or len(label)>160:raise ValueError('action name required')
    for k in METRICS:
        if measured[k] is None:
            if k not in s['unmeasured']:s['unmeasured'].append(k)
        else:
            s['usage'][k]+=measured[k]
    s['events'].append({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                        'action':label,'measured':measured,'estimated_not_counted':estimated,
                        'source':doc.get('source','USER_OR_TOOL_DECLARATION')})
    _atomic(state_path(workdir),s)
    return {'status':'RECORDED','measurements_known_for': [k for k,v in measured.items() if v is not None],
            'unmeasured':s['unmeasured'],'usage':s['usage'],
            'note':'Unknown metrics block proof of compliance; no Work quota is accessible.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    for op in ('init','preflight','record','status'):
        a=sub.add_parser(op);a.add_argument('--workdir',required=True)
        if op=='init':a.add_argument('--config',required=True)
        if op=='preflight':a.add_argument('--next-usage',required=True)
        if op=='record':a.add_argument('--usage',required=True)
    a=p.parse_args(argv)
    try:
        if a.cmd=='init':out=init(a.workdir,a.config)
        elif a.cmd=='preflight':out=evaluate(read(a.workdir),json.loads(Path(a.next_usage).read_text('utf-8')))
        elif a.cmd=='record':out=record(a.workdir,a.usage)
        else:
            s=read(a.workdir);out={'status':'LEDGER_ONLY','used':s['usage'],'unmeasured':s['unmeasured'],
                                  'approval':s['config']['owner'], 'event_count':len(s['events']),
                                  'quota':'NOT_ACCESSIBLE'}
        print(json.dumps(out,ensure_ascii=False,indent=2))
        return 0 if out.get('status') in ('READY','DRAFT_UNAPPROVED','PASS_WITHIN_DECLARED_LIMITS','RECORDED','LEDGER_ONLY') else 3
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as e:
        print(json.dumps({'status':'FAIL','error':str(e)},ensure_ascii=False));return 2

if __name__=='__main__':sys.exit(main())
