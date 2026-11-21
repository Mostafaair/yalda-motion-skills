#!/usr/bin/env python3
"""YALDA independent, read-only-to-project checkpoint helper.

Writes only to the explicit --workdir/.yalda-motion-state directory; snapshots
approved relative source/evidence paths, never mutates the source files.
Atomic state records and ZIP snapshots allow local resume. EXTERNAL persistence
is never inferred from local output: report it separately to Owner.

Patterns adapted from Anthropic triage SKILL checkpointing; independent code.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile

STATE_DIR = '.yalda-motion-state'
PROGRESS = 'progress.json'
UTC = dt.timezone.utc


def now():
    return dt.datetime.now(UTC).isoformat(timespec='seconds')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require_safe_rel(value):
    # Strictly portable path names; forbid drive roots, hidden state, traversal,
    # source changes through symlinks, and Windows alternate streams.
    if not isinstance(value,str) or not value or '\\' in value or '\x00' in value or ':' in value:
        raise ValueError('Unsafe relative path')
    p=Path(value)
    if p.is_absolute() or any(x in ('.','..','') for x in p.parts) or STATE_DIR in p.parts:
        raise ValueError('Unsafe relative path')
    return p


def atomic_write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix='._yalda_')
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def atomic_json(path, obj):
    atomic_write(path,(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8'))


def locate(workdir):
    root=Path(workdir).resolve(strict=True)
    if not root.is_dir():raise ValueError('Workdir must be a directory')
    return root, root/STATE_DIR


def read_state(state):
    p=state/PROGRESS
    if not p.is_file():raise ValueError('No checkpoint state; run init')
    obj=json.loads(p.read_text('utf-8'))
    if obj.get('schema') != 1 or not isinstance(obj.get('checkpoints'),list):
        raise ValueError('Invalid progress schema')
    return obj


def init(workdir,run_id):
    root,state=locate(workdir)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{2,79}',run_id):
        raise ValueError('Invalid run id')
    if (state/PROGRESS).exists():
        raise ValueError('Run already exists: resume it; never silently reset')
    obj={'schema':1,'run_id':run_id,'created_utc':now(), 'status':'running','checkpoints':[],
         'external_persistence':'NOT_VERIFIED','last_saved_utc':None}
    atomic_json(state/PROGRESS,obj)
    return obj


def enumerate_files(root,items):
    files={}
    for raw in items:
        rel=require_safe_rel(raw)
        path=root/rel
        if not path.exists():raise ValueError(f'Missing source: {rel}')
        if path.is_symlink():raise ValueError(f'Symlink forbidden: {rel}')
        candidates=[path] if path.is_file() else sorted(path.rglob('*'))
        for p in candidates:
            if p.is_symlink():raise ValueError(f'Symlink forbidden: {p}')
            if not p.is_file():continue
            rp=p.relative_to(root)
            if STATE_DIR in rp.parts:raise ValueError('State cannot be included')
            if not p.resolve().is_relative_to(root):raise ValueError('Outside workdir')
            files[rp.as_posix()]=p
    if not files:raise ValueError('No files selected')
    return files


def save(workdir,phase_id,include,note='',label='PARTIAL'):
    root,state=locate(workdir);s=read_state(state)
    if s['status']!='running':raise ValueError('Run already complete')
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{1,50}',phase_id):raise ValueError('Invalid phase ID')
    if label not in ('PARTIAL','GATE_PASS','BLOCKED'):
        raise ValueError('Invalid checkpoint label')
    files=enumerate_files(root,include)
    entries=[]
    for rel,p in sorted(files.items()):
        b=p.read_bytes()
        entries.append({'path':rel,'sha256':digest(b),'bytes':len(b),'data':b})
    number=len(s['checkpoints'])+1
    archive=f'YALDA_CP_{number:03d}_{phase_id}.zip'
    meta={'schema':1,'run_id':s['run_id'],'checkpoint_number':number,'phase_id':phase_id,
          'state':label,'note':note,'created_utc':now(),
          'artifacts':[{'path':e['path'],'sha256':e['sha256'],'bytes':e['bytes']} for e in entries],
          'external_persistence':'NOT_VERIFIED'}
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        z.writestr('CHECKPOINT.json',json.dumps(meta,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        for e in entries:z.writestr('files/'+e['path'],e['data'])
    dest=state/'checkpoints'/archive
    if dest.exists():raise ValueError('Refusing overwrite existing checkpoint')
    raw=b.getvalue();atomic_write(dest,raw)
    s['checkpoints'].append({'number':number,'phase_id':phase_id,'state':label,
                             'archive':str(Path('checkpoints')/archive),
                             'archive_sha256':digest(raw),'artifact_count':len(entries),
                             'external_persistence':'NOT_VERIFIED','external_reference':None,
                             'saved_utc':meta['created_utc']})
    s['last_saved_utc']=now()
    atomic_json(state/PROGRESS,s)
    return {'status':'LOCAL_CHECKPOINT_ONLY','archive':str(dest),'sha256':digest(raw),
            'checkpoint_number':number,'files':len(entries),'external_persistence':'NOT_VERIFIED',
            'next':'Deliver this ZIP and hash to Owner/Library; verify user-accessible copy before costly continuation.'}


def verify(workdir,number=None):
    _,state=locate(workdir);s=read_state(state)
    cps=s['checkpoints'] if number is None else [c for c in s['checkpoints'] if c['number']==number]
    if not cps:raise ValueError('No checkpoints selected')
    issues=[]
    for c in cps:
        p=state/require_safe_rel(c['archive'])
        if not p.is_file():issues.append(f"{c['number']}: archive missing");continue
        data=p.read_bytes()
        if digest(data)!=c['archive_sha256']:issues.append(f"{c['number']}: archive SHA mismatch");continue
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.testzip() is not None:issues.append(f"{c['number']}: CRC failure");continue
                meta=json.loads(z.read('CHECKPOINT.json'))
                if meta['checkpoint_number']!=c['number'] or meta['run_id']!=s['run_id']:
                    issues.append(f"{c['number']}: metadata mismatch")
                names=set(z.namelist())
                expected={'CHECKPOINT.json'}
                for a in meta['artifacts']:
                    rel=require_safe_rel(a['path']).as_posix();member='files/'+rel
                    expected.add(member)
                    if member not in names:issues.append(f"{c['number']}: missing {member}");continue
                    b=z.read(member)
                    if len(b)!=a['bytes'] or digest(b)!=a['sha256']:
                        issues.append(f"{c['number']}: bad hash {member}")
                if names!=expected:issues.append(f"{c['number']}: unlisted member(s)")
        except (KeyError,ValueError,zipfile.BadZipFile) as e:issues.append(f"{c['number']}: invalid ZIP {e}")
    return {'status':'PASS_LOCAL_INTEGRITY' if not issues else 'FAIL',
            'checked':len(cps),'errors':issues,
            'external_persistence':'NOT_PROVED_BY_THIS_TOOL'}


def receipt(workdir,number,external_reference):
    _,state=locate(workdir);s=read_state(state)
    c=next((x for x in s['checkpoints'] if x['number']==number),None)
    if not c:raise ValueError('Unknown checkpoint')
    if not isinstance(external_reference,str) or len(external_reference)<8:
        raise ValueError('External reference required')
    # This is NOT independent proof of access; labeling is intentionally conservative.
    c['external_persistence']='REPORTED_UNVERIFIED'
    c['external_reference']=external_reference
    atomic_json(state/PROGRESS,s)
    return {'status':'REPORTED_UNVERIFIED','note':'Owner must confirm the ZIP can actually be retrieved.'}


def restore(workdir,number,to):
    _,state=locate(workdir);s=read_state(state)
    c=next((x for x in s['checkpoints'] if x['number']==number),None)
    if not c:raise ValueError('Unknown checkpoint')
    result=verify(workdir,number)
    if result['status']!='PASS_LOCAL_INTEGRITY':raise ValueError('Cannot restore invalid checkpoint')
    target=Path(to)
    if target.exists() and any(target.iterdir()):raise ValueError('Restore target must be empty')
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(state/c['archive']) as z:
        meta=json.loads(z.read('CHECKPOINT.json'))
        for a in meta['artifacts']:
            rel=require_safe_rel(a['path']);p=target/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            atomic_write(p,z.read('files/'+rel.as_posix()))
    return {'status':'RESTORED_IN_NEW_LOCATION','destination':str(target),'artifact_count':len(meta['artifacts']),
            'note':'Source snapshot only; browser QA and Owner approvals must be reverified.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='cmd',required=True)
    for cmd in ('init','save','verify','status','receipt','restore'):
        p=sub.add_parser(cmd);p.add_argument('--workdir',required=True)
        if cmd=='init':p.add_argument('--run-id',required=True)
        if cmd=='save':
            p.add_argument('--phase-id',required=True);p.add_argument('--include',action='append',required=True)
            p.add_argument('--note',default='');p.add_argument('--label',default='PARTIAL')
        if cmd in ('verify','receipt','restore'):p.add_argument('--number',type=int,required=(cmd!='verify'))
        if cmd=='receipt':p.add_argument('--external-reference',required=True)
        if cmd=='restore':p.add_argument('--to',required=True)
    a=parser.parse_args(argv)
    try:
        if a.cmd=='init':out=init(a.workdir,a.run_id)
        elif a.cmd=='save':out=save(a.workdir,a.phase_id,a.include,a.note,a.label)
        elif a.cmd=='verify':out=verify(a.workdir,a.number)
        elif a.cmd=='receipt':out=receipt(a.workdir,a.number,a.external_reference)
        elif a.cmd=='restore':out=restore(a.workdir,a.number,a.to)
        else:
            _,state=locate(a.workdir);out=read_state(state)
        print(json.dumps(out,ensure_ascii=False,indent=2))
        return 1 if isinstance(out,dict) and out.get('status')=='FAIL' else 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
        print(json.dumps({'status':'FAIL','error':str(e)},ensure_ascii=False));return 2

if __name__=='__main__':sys.exit(main())
