#!/usr/bin/env python3
"""Read-only triage of Chromium/Chrome JSON traces, including observed Chrome 154.

Only emit aggregate diagnostics. No URL, event args, raw scripts or host data.
Do not interpret tracker snapshots as presented FPS or browser-wide dropped frames.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import json
import math
from pathlib import Path

FRAME_STATES = {'STATE_NO_UPDATE_DESIRED', 'STATE_PRESENTED_ALL',
                'STATE_PRESENTED_PARTIAL', 'STATE_DROPPED'}
STATES_BY_NUMBER = {0: 'STATE_NO_UPDATE_DESIRED', 1: 'STATE_PRESENTED_ALL',
                    2: 'STATE_PRESENTED_PARTIAL', 3: 'STATE_DROPPED'}
TASK_NAMES = {'RunTask', 'ThreadControllerImpl::RunTask'}
DECODE_NAMES = {'Decode Image', 'Decode LazyPixelRef', 'ImageDecodeTask',
                'ImageDecoder::DecodeFrameBufferAtIndex',
                'GpuImageDecodeCache::DecodeImage',
                'GpuImageDecodeTaskImpl::RunOnWorkerThread',
                'ImageController::ProcessNextImageDecodeOnWorkerThread'}
MAIN_NAMES = {'CrRendererMain', 'RendererMain', 'RendererMainThread'}
LEGACY_LANES = {'impl': ('impl-frames-expected', 'impl-frames-produced'),
                'main': ('main-frames-expected', 'main-frames-produced')}
SEQUENCE_LABELS = {
    'MainThreadAnimation', 'CompositorAnimation', 'NativePropertyAnimation',
    'CanvasAnimation', 'JSAnimation', 'RAF', 'WheelScroll', 'TouchScroll',
    'ScrollBarScroll', 'Video', 'MainThreadScroll', 'CompositorScroll',
    'Scroll', 'PinchZoom', 'Universal', 'Custom',
}


def load(path):
    p = Path(path)
    with (gzip.open if p.suffix == '.gz' else open)(p, 'rt', encoding='utf-8-sig') as f:
        data = json.load(f)
    events = data if isinstance(data, list) else data.get('traceEvents') if isinstance(data, dict) else None
    if not isinstance(events, list):
        raise ValueError('trace must be an array or contain traceEvents array')
    return events


def num(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def uint(value):
    return type(value) is int and value >= 0


def metadata(events):
    procs, threads = {}, {}
    for e in events:
        if not isinstance(e, dict) or e.get('ph') != 'M':
            continue
        args = e.get('args')
        if not isinstance(args, dict) or not isinstance(args.get('name'), str):
            continue
        pid, tid = e.get('pid'), e.get('tid')
        if e.get('name') == 'process_name':
            procs[pid] = args['name']
        elif e.get('name') == 'thread_name':
            threads[(pid, tid)] = args['name']
    return procs, threads


def select_main(events, renderer_pid=None, main_tid=None):
    procs, threads = metadata(events)
    candidates = sorted([(p,t) for (p,t), n in threads.items()
                         if n in MAIN_NAMES and 'renderer' in procs.get(p, 'renderer').lower()],
                        key=lambda x: (str(x[0]), str(x[1])))
    if renderer_pid is not None:
        candidates = [(p,t) for p,t in candidates if p == renderer_pid]
    if main_tid is not None:
        if renderer_pid is None:
            return None, 'MAIN_TID_REQUIRES_RENDERER_PID', candidates
        return (renderer_pid, main_tid), 'USER_SELECTED_PID_TID', candidates
    if len(candidates) == 1:
        return candidates[0], 'UNIQUE_RENDERER_MAIN_METADATA', candidates
    if len(candidates) > 1:
        return None, 'AMBIGUOUS_RENDERER_MAIN_THREADS', candidates
    return None, 'RENDERER_MAIN_METADATA_NOT_AVAILABLE', candidates


def frame_state(e):
    args = e.get('args')
    if not isinstance(args, dict):
        return None
    for key in ('frame_reporter', 'chrome_frame_reporter'):
        value = args.get(key)
        if isinstance(value, dict):
            state = value.get('state')
            if type(state) is int:
                return STATES_BY_NUMBER.get(state)
            if isinstance(state, str) and state in FRAME_STATES:
                return state
    return None


def arg_objects(e):
    args = e.get('args')
    if not isinstance(args, dict):
        return []
    out = [args]
    for key in ('data', 'args'):
        child = args.get(key)
        if isinstance(child, dict):
            out.append(child)
            if isinstance(child.get('data'), dict):
                out.append(child['data'])
    return out


def sequence_label(e):
    args = e.get('args')
    value = args.get('name') if isinstance(args, dict) else None
    return value if isinstance(value, str) and value in SEQUENCE_LABELS else 'OTHER_OR_UNAVAILABLE'


def tracker_counters(e):
    """Returns recognized per-event SNAPSHOT; never sum across lanes or sessions."""
    matches = []
    for obj in arg_objects(e):
        if e.get('name') == 'FrameSequenceTrackerV3':
            if not uint(obj.get('expected')):
                continue
            expected = obj['expected']
            dropped = {}
            for k in ('dropped_v4', 'dropped_v3'):
                if k in obj:
                    if not uint(obj[k]) or obj[k] > expected:
                        dropped = {}
                        break
                    dropped[k] = obj[k]
            if not dropped:
                continue
            matches.append({'schema': 'Chromium_FrameSequenceTrackerV3',
                            'expected': expected, **dropped})
        elif e.get('name') == 'FrameSequenceTracker':
            lanes = {}
            for lane,(ek,pk) in LEGACY_LANES.items():
                if ek in obj and pk in obj and uint(obj[ek]) and uint(obj[pk]) and obj[pk] <= obj[ek]:
                    lanes[lane] = {'expected':obj[ek], 'produced': obj[pk],
                                   'not_produced': obj[ek]-obj[pk]}
            if lanes:
                matches.append({'schema': 'Chromium_legacy_2019', 'lanes': lanes})
    return matches[0] if len(matches) == 1 else None


def _async_key(e):
    id2 = e.get('id2')
    ids = id2 if isinstance(id2, dict) else {}
    return (e.get('pid'), e.get('tid'), ids.get('local'), ids.get('global'), e.get('id'))


def summarize(events, long_task_ms=50.0, renderer_pid=None, main_tid=None):
    if not isinstance(events, list) or not num(long_task_ms) or long_task_ms <= 0:
        raise ValueError('invalid trace events or long-task threshold')
    main, main_reason, candidates = select_main(events, renderer_pid, main_tid)
    counts_all, counts_main = Counter(), Counter()
    all_long, scoped_long = 0, 0
    max_main = None
    decode_counts = Counter()
    decode_max = None
    tracker_found, tracker_unknown = [], 0
    tracker_counts = Counter()
    reporter_count, reporter_pairs, reporter_unpaired = 0, 0, 0
    reporter_pending = defaultdict(list)
    reporter_states = []
    # Event timestamps are relative to the browser trace clock; only deltas exported.
    t0 = min((e['ts'] for e in events if isinstance(e, dict) and num(e.get('ts'))), default=None)
    scroll_jank_bool = []
    frame_presented = 0
    for e in events:
        if not isinstance(e, dict):
            continue
        name, ph = e.get('name'), e.get('ph')
        if name in ('FrameSequenceTracker', 'FrameSequenceTrackerV3'):
            tracker_counts[name] += 1
            snap = tracker_counters(e)
            if snap:
                rel = round((e['ts']-t0)/1000, 2) if t0 is not None and num(e.get('ts')) else None
                tracker_found.append({'schema': snap['schema'], 'label':sequence_label(e),
                                      'phase': ph, 'time_from_trace_start_ms': rel,
                                      'counters': snap,
                                      **({'lanes': snap['lanes']} if 'lanes' in snap else {})})
            elif ph != 'e':
                # Async end markers frequently carry no data; that is not unsupported schema.
                tracker_unknown += 1
        if name == 'PipelineReporter':
            reporter_count += 1
            state = frame_state(e)
            key = _async_key(e)
            keyed = any(x is not None for x in key[2:])
            if keyed and ph == 'b':
                reporter_pending[key].append(state)
            elif keyed and ph == 'e':
                if reporter_pending[key]:
                    prior = reporter_pending[key].pop(0)
                    reporter_pairs += 1
                    if state or prior:
                        reporter_states.append(state or prior)
                elif state:
                    reporter_states.append(state)
                    reporter_unpaired += 1
            elif state:
                reporter_states.append(state)
                reporter_unpaired += 1
        if name == 'FramePresented':
            frame_presented += 1
        if name == 'ScrollJankV4':
            # Chrome 154 stores the boolean in args.scroll_jank_v4.is_janky.
            # Only count a payload containing an explicit boolean (usually phase 'b').
            vals = []
            for obj in arg_objects(e):
                candidates = [obj]
                if isinstance(obj.get('scroll_jank_v4'), dict):
                    candidates.append(obj['scroll_jank_v4'])
                for item in candidates:
                    if type(item.get('is_janky')) is bool:
                        vals.append(item['is_janky'])
            if vals:
                scroll_jank_bool.append(vals[0])
        if ph == 'X' and num(e.get('dur')):
            ms = e['dur']/1000
            if name in TASK_NAMES:
                counts_all[name] += 1
                if ms >= long_task_ms:
                    all_long += 1
                if main is not None and (e.get('pid'), e.get('tid')) == main:
                    counts_main[name] += 1
                    max_main = max(max_main or 0, ms)
                    if ms >= long_task_ms:
                        scoped_long += 1
            if name in DECODE_NAMES:
                decode_counts[name] += 1
                decode_max = max(decode_max or 0, ms)
    for pending in reporter_pending.values():
        for state in pending:
            if state:
                reporter_states.append(state)
                reporter_unpaired += 1
    states = Counter(reporter_states)
    known = bool(reporter_states)
    v3_count = sum(item['schema'] == 'Chromium_FrameSequenceTrackerV3' for item in tracker_found)
    legacy_count = sum(item['schema'] == 'Chromium_legacy_2019' for item in tracker_found)
    return {
        'trace_event_count': len(events),
        'renderer_main_thread_selection': main_reason,
        'renderer_main_thread_pid_tid': {'pid':main[0],'tid':main[1]} if main is not None else None,
        'renderer_main_candidate_count': len(candidates),
        'task_names_recognized': sorted(TASK_NAMES),
        'run_task_event_counts_by_name_all_processes': dict(counts_all),
        'run_task_event_counts_by_name_renderer_main': dict(counts_main) if main is not None else None,
        'run_task_event_count_all_processes': sum(counts_all.values()),
        'long_run_task_candidate_count_all_processes_UNATTRIBUTED': all_long,
        'run_task_event_count': sum(counts_main.values()) if main is not None else None,
        'long_run_task_count_at_threshold': scoped_long if main is not None else None,
        'long_run_task_threshold_ms': long_task_ms,
        'long_run_task_max_ms': round(max_main,3) if max_main is not None else (None if main is None else 0),
        'frame_sequence_tracker_event_count': sum(tracker_counts.values()),
        'frame_sequence_tracker_event_counts_by_name': dict(tracker_counts),
        'frame_sequence_tracker_recognized_counter_events': len(tracker_found),
        'frame_sequence_tracker_v3_recognized_snapshots': v3_count,
        'frame_sequence_tracker_legacy_recognized_snapshots': legacy_count,
        'frame_sequence_tracker_unrecognized_format_events_excluding_end': tracker_unknown,
        'frame_sequence_tracker_counters': tracker_found,
        'frame_sequence_tracker_availability': 'RECOGNIZED_SNAPSHOTS' if tracker_found else 'NOT AVAILABLE IN TRACE',
        'frame_sequence_tracker_global_dropped_frames': 'NOT DERIVABLE FROM THESE SNAPSHOTS',
        'frame_sequence_tracker_end_to_end_fps': 'NOT MEASURED',
        'pipeline_reporter_event_count': reporter_count,
        'pipeline_reporter_async_pairs_completed': reporter_pairs,
        'reporter_unpaired_status_events': reporter_unpaired,
        'explicit_frame_state_count': len(reporter_states),
        'frame_state_availability': 'EXPLICIT_PIPELINE_REPORTER_EVENTS' if known else 'NOT AVAILABLE IN TRACE',
        'pipeline_reported_dropped_count': states['STATE_DROPPED'] if known else None,
        'pipeline_reported_partially_presented_count': states['STATE_PRESENTED_PARTIAL'] if known else None,
        'pipeline_reported_fully_presented_count': states['STATE_PRESENTED_ALL'] if known else None,
        'pipeline_reported_no_update_count': states['STATE_NO_UPDATE_DESIRED'] if known else None,
        'frame_presented_event_count_UNATTRIBUTED': frame_presented,
        'scroll_jank_explicit_event_count': len(scroll_jank_bool),
        'scroll_jank_explicit_true_count': sum(scroll_jank_bool) if scroll_jank_bool else None,
        'decode_event_counts_by_name': dict(decode_counts),
        'decode_event_max_duration_ms': round(decode_max,3) if decode_max is not None else None,
        'decode_event_total_duration_ms': 'NOT CALCULATED: nested/overlapping events',
        'end_to_end_fps': 'NOT MEASURED',
        'limitations': [
            'V3 expected/dropped_v3/dropped_v4 are per-event counter snapshots, not total presented frames or FPS.',
            'Snapshots may include time before capture; async begin may not be a final counter.',
            'Do not add V3 tracker sequences: labels, time windows and lanes can overlap.',
            'Renderer main determined by metadata or explicit PID/TID; multiple candidate renderers require disambiguation.',
            'PipelineReporter and FramePresented events can represent distinct surfaces and may duplicate semantic frames.',
            'RunTask durations are not proof of a blocked animation, a LoAF entry, or a lost presented frame.',
            'Decode runs on workers and events can overlap; no global decode latency is inferred.',
            'Absent events / unsupported schema means NOT AVAILABLE rather than zero.',
            'Trace still requires visual review and context from HAR and real scroll coordinates.',
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('trace', help='Local Chrome Performance trace .json or .json.gz')
    p.add_argument('--long-task-ms', type=float, default=50.0)
    p.add_argument('--renderer-pid', type=int, help='Verified renderer PID if multiple renderers are present')
    p.add_argument('--main-tid', type=int, help='Verified thread TID, requires --renderer-pid')
    p.add_argument('--out', help='Optional output JSON path')
    opts = p.parse_args()
    body = json.dumps(summarize(load(opts.trace), opts.long_task_ms,
                                opts.renderer_pid, opts.main_tid), ensure_ascii=False, indent=2)+'\n'
    if opts.out:
        Path(opts.out).write_text(body,encoding='utf-8')
    else:
        print(body, end='')

if __name__ == '__main__':
    main()
