#!/usr/bin/env python3
"""Offline HAR 1.2 timing/media timeline (never emits request URLs or headers)."""
import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

IMG = {'.png', '.webp', '.jpg', '.jpeg', '.gif', '.avif', '.svg', '.bmp'}
VID = {'.mp4', '.webm', '.mov', '.m4v'}


def num(v):
    return type(v) in (int, float) and math.isfinite(v) and v >= 0


def p95(v):
    return sorted(v)[max(0, math.ceil(.95 * len(v)) - 1)] if v else None


def kind(e):
    resp = e.get('response') or {}
    cont = resp.get('content') or {}
    mt = str(cont.get('mimeType', '')).lower() if isinstance(cont, dict) else ''
    req = e.get('request') or {}
    url = req.get('url', '') if isinstance(req, dict) else ''
    try:
        ext = Path(urlsplit(str(url)).path).suffix.lower()
    except ValueError:
        ext = ''
    if mt.startswith('image/') or ext in IMG:
        return 'image'
    if mt.startswith('video/') or ext in VID:
        return 'video'
    if 'javascript' in mt or ext in ('.js', '.mjs'):
        return 'javascript'
    if mt.startswith('text/css') or ext == '.css':
        return 'css'
    if mt.startswith('font/') or ext in ('.woff', '.woff2', '.ttf'):
        return 'font'
    if mt.startswith('text/html') or ext == '.html':
        return 'html'
    return 'other'


def _datetime_ms(raw):
    if not isinstance(raw, str):
        return None
    try:
        dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc).timestamp() * 1000
    except (ValueError, OverflowError):
        return None


def _timeline(records):
    if not records:
        return {'status': 'NOT AVAILABLE IN HAR', 'request_with_valid_start_and_duration': 0,
                'maximum_concurrent_requests': None, 'relative_first_request_start_ms': None,
                'relative_last_request_start_ms': None}
    # Double-count prevention for touching intervals: end before start at same millisecond.
    origin = min(x['start'] for x in records)
    marks = []
    for row in records:
        marks.extend(((row['start'], +1), (row['end'], -1)))
    active = peak = 0
    for _, delta in sorted(marks, key=lambda x: (x[0], x[1])):
        if delta == -1:
            active = max(0, active - 1)
        else:
            active += 1
            peak = max(peak, active)
    return {'status': 'HAR_START_AND_DURATION_ONLY',
            'request_with_valid_start_and_duration': len(records),
            'maximum_concurrent_requests': peak,
            'relative_first_request_start_ms': 0.0,
            'relative_last_request_start_ms': round(max(x['start'] for x in records) - origin, 3),
            'relative_last_request_complete_ms': round(max(x['end'] for x in records) - origin, 3)}


def _media_timeline(records, origin):
    if not records or origin is None:
        return {'status': 'NOT AVAILABLE IN HAR', 'valid_media_requests': len(records),
                'first_media_start_relative_ms': None, 'last_media_start_relative_ms': None,
                'first_media_complete_relative_ms': None, 'last_media_complete_relative_ms': None,
                'p95_gap_between_media_starts_ms': None, 'max_gap_between_media_starts_ms': None,
                'maximum_concurrent_media_requests': None}
    starts = sorted(r['start'] for r in records)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    t = _timeline(records)
    return {'status': 'HAR_START_AND_DURATION_ONLY', 'valid_media_requests': len(records),
            'first_media_start_relative_ms': round(starts[0] - origin, 3),
            'last_media_start_relative_ms': round(starts[-1] - origin, 3),
            'first_media_complete_relative_ms': round(min(x['end'] for x in records) - origin, 3),
            'last_media_complete_relative_ms': round(max(x['end'] for x in records) - origin, 3),
            'p95_gap_between_media_starts_ms': round(p95(gaps), 3) if gaps else None,
            'max_gap_between_media_starts_ms': round(max(gaps), 3) if gaps else None,
            'maximum_concurrent_media_requests': t['maximum_concurrent_requests']}


def summarize(data, cache_state='unknown'):
    if cache_state not in ('cold', 'warm', 'unknown'):
        raise ValueError('cache state must be declared cold, warm or unknown')
    if not isinstance(data, dict) or not isinstance(data.get('log'), dict) or not isinstance(data['log'].get('entries'), list):
        raise ValueError('invalid HAR log.entries')
    entries = data['log']['entries']
    kinds = Counter()
    statuses = Counter()
    priorities = Counter()
    headers = Counter()
    dur, blocked, wait, receive, sizes = [], [], [], [], []
    unknown_size = unknown_time = errors = sensitive = 0
    records, media, images, video = [], [], [], []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            raise ValueError(f'entry {i} invalid')
        resp, req, timing = e.get('response') or {}, e.get('request') or {}, e.get('timings') or {}
        if not isinstance(resp, dict) or not isinstance(req, dict) or not isinstance(timing, dict):
            raise ValueError(f'entry {i} invalid objects')
        k = kind(e)
        kinds[k] += 1
        status = resp.get('status', 'unknown')
        statuses[str(status)] += 1
        if type(status) is int and status >= 400:
            errors += 1
        size = resp.get('bodySize')
        if num(size):
            sizes.append(size)
        else:
            unknown_size += 1
        if num(e.get('time')):
            dur.append(e['time'])
        for key, arr in (('blocked', blocked), ('wait', wait), ('receive', receive)):
            if num(timing.get(key)):
                arr.append(timing[key])
        priorities[str(e.get('_priority', 'not_recorded'))] += 1
        for h in resp.get('headers') or []:
            if not isinstance(h, dict):
                continue
            nm = str(h.get('name', '')).lower()
            if nm in ('cache-control', 'etag', 'last-modified', 'expires', 'age', 'vary'):
                headers[nm] += 1
            if nm in ('authorization', 'set-cookie'):
                sensitive += 1
        for h in req.get('headers') or []:
            if isinstance(h, dict) and str(h.get('name', '')).lower() in ('cookie', 'authorization', 'proxy-authorization'):
                sensitive += 1
        ts = _datetime_ms(e.get('startedDateTime'))
        if ts is not None and num(e.get('time')):
            row = {'start': ts, 'end': ts + e['time']}
            records.append(row)
            if k in ('image', 'video'):
                media.append(row)
            if k == 'image':
                images.append(row)
            if k == 'video':
                video.append(row)
        else:
            unknown_time += 1
    origin = min((x['start'] for x in records), default=None)
    return {
        'entry_count': len(entries), 'cache_test_condition_declared': cache_state,
        'requests_by_category': dict(sorted(kinds.items())), 'status_counts': dict(sorted(statuses.items())),
        'http_error_entry_count': errors,
        'response_body_known_bytes_sum': sum(sizes), 'response_body_unknown_size_entries': unknown_size,
        'body_bytes_are_complete': unknown_size == 0,
        'entry_duration_ms_p95_nearest_rank': p95(dur), 'entry_duration_ms_max': max(dur, default=None),
        'blocked_ms_p95_nearest_rank': p95(blocked), 'blocked_ms_max': max(blocked, default=None),
        'blocked_timing_reported_entries': len(blocked),
        'wait_ms_p95_nearest_rank': p95(wait), 'receive_ms_p95_nearest_rank': p95(receive),
        'optional_priority_counts': dict(sorted(priorities.items())),
        'cache_related_response_header_occurrences': dict(headers),
        'sensitive_headers_detected_count': sensitive,
        'timing_missing_or_invalid_entries': unknown_time,
        'all_requests_timeline': _timeline(records),
        'media_requests_timeline': _media_timeline(media, origin),
        'image_requests_timeline': _media_timeline(images, origin),
        'video_requests_timeline': _media_timeline(video, origin),
        'safety_note': 'No URL/hostname/header values are emitted. Input HAR may still contain secrets; sanitize before sharing.',
        'limitations': [
            'Concurrency counts overlap of HAR request intervals, not browser socket/HTTP2 concurrency or simultaneous image decode.',
            'HAR entries may omit timestamps/time; timeline is partial when timing_missing_or_invalid_entries > 0.',
            'First image completion in HAR is network-complete, NOT first usable/decoded/displayed image.',
            'HAR bodySize is not guaranteed wire transfer bytes; -1 means unknown, not zero.',
            'Cold/warm is a declared test condition, not inferred from response headers.',
            'blocked is network-connection timing; not JS task queue proof.',
            'No image decode, GPU dropped frames, memory or user-visible presentation measured.',
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('har')
    ap.add_argument('--cache-state', choices=('cold', 'warm', 'unknown'), default='unknown')
    ap.add_argument('--out')
    a = ap.parse_args()
    result = json.dumps(summarize(json.loads(Path(a.har).read_text('utf-8-sig')), a.cache_state),
                        ensure_ascii=False, indent=2) + '\n'
    if a.out:
        Path(a.out).write_text(result, encoding='utf-8')
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
