#!/usr/bin/env python3
"""Read-only sampled app frame log analyzer. NOT a compositor dropped-frame counter."""
import argparse,json,math
from pathlib import Path
FIELDS=('t_ms','target_index','shown_index','target_ready','blank')
def p95(v):return sorted(v)[max(0,math.ceil(.95*len(v))-1)] if v else None
def load_samples(path):
    out=[];last=-1
    for n,line in enumerate(Path(path).read_text('utf8').splitlines(),1):
        if not line.strip() or line.startswith('#'):continue
        s=json.loads(line)
        if not isinstance(s,dict) or any(k not in s for k in FIELDS):raise ValueError(f'line {n}: missing sample field')
        t=s['t_ms']
        if type(t) not in (int,float) or not math.isfinite(t) or t<0 or t<=last:raise ValueError(f'line {n}: non-monotonic/invalid time')
        if any(type(s[k]) is not int for k in ('target_index','shown_index')) or s['target_index']<0 or s['shown_index']< -1:raise ValueError(f'line {n}: invalid index')
        if any(type(s[k]) is not bool for k in ('target_ready','blank')):raise ValueError(f'line {n}: invalid boolean')
        out.append(s);last=t
    if not out:raise ValueError('no samples')
    return out
def summarize(samples,gap_threshold_ms=50):
    if gap_threshold_ms<=0:raise ValueError('gap threshold must be positive')
    t_jumps=[];s_jumps=[];intervals=[];target_changes=[];runs=[];runstart=samples[0]['t_ms']
    for a,b in zip(samples,samples[1:]):
        dt=b['t_ms']-a['t_ms'];intervals.append(dt)
        td=b['target_index']-a['target_index'];sd=b['shown_index']-a['shown_index']
        if td:target_changes.append(td)
        if abs(td)>1:t_jumps.append({'t_ms':b['t_ms'],'from':a['target_index'],'to':b['target_index'],'delta':td})
        if a['shown_index']>=0 and b['shown_index']>=0 and abs(sd)>1:s_jumps.append({'t_ms':b['t_ms'],'from':a['shown_index'],'to':b['shown_index'],'delta':sd,'sample_gap_ms':dt})
        if sd:runs.append(a['t_ms']-runstart);runstart=b['t_ms']
    runs.append(samples[-1]['t_ms']-runstart)
    n=len(samples)
    mismatch=[abs(x['target_index']-x['shown_index']) for x in samples if x['shown_index']>=0]
    return {'sample_count':n,'time_span_ms':samples[-1]['t_ms']-samples[0]['t_ms'],
      'input_target_jumps_over_one_index':len(t_jumps),'input_target_jumps_examples':t_jumps[:30],
      'sampled_shown_jumps_over_one_index':len(s_jumps),'sampled_shown_jumps_examples':s_jumps[:30],
      'max_abs_sampled_shown_jump':max([abs(x['delta']) for x in s_jumps],default=0),
      'max_inter_sample_gap_ms':max(intervals,default=None),'p95_inter_sample_gap_ms_nearest_rank':p95(intervals),
      'inter_sample_gap_threshold_ms':gap_threshold_ms,'inter_sample_gaps_over_threshold_count':sum(x>gap_threshold_ms for x in intervals),
      'target_direction_reversals_observed':sum(a*b<0 for a,b in zip(target_changes,target_changes[1:])),
      'max_contiguous_same_shown_sample_span_ms_lower_bound':max(runs),
      'target_not_ready_sample_count':sum(not x['target_ready'] for x in samples),
      'target_not_ready_sample_percent':round(100*sum(not x['target_ready'] for x in samples)/n,2),
      'shown_not_equal_target_sample_count':sum(x['shown_index']!=x['target_index'] for x in samples),
      'ready_target_not_shown_sample_count':sum(x['target_ready'] and x['shown_index']!=x['target_index'] for x in samples),
      'blank_samples':sum(x['blank'] for x in samples),'no_shown_frame_samples':sum(x['shown_index']==-1 for x in samples),
      'p95_abs_target_shown_index_gap_nearest_rank':p95(mismatch),
      'actual_browser_dropped_frames':'NOT MEASURED','actual_browser_presented_frames':'NOT MEASURED',
      'limitations':['A sampled shown-index jump does not establish GPU frame drops.',
                     'A long inter-sample gap does not prove an equally long main-thread block.',
                     'Fast scroll can intentionally skip intermediate indices.',
                     'Observed same-index run is a lower bound, not a continuous video measurement.']}
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('log');a.add_argument('--gap-threshold-ms',type=float,default=50);a.add_argument('--out');x=a.parse_args()
    text=json.dumps(summarize(load_samples(x.log),x.gap_threshold_ms),ensure_ascii=False,indent=2)+'\n'
    if x.out:Path(x.out).write_text(text,encoding='utf8')
    else:print(text,end='')
if __name__=='__main__':main()
