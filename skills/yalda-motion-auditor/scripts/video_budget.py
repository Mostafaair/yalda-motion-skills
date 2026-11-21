#!/usr/bin/env python3
"""Read-only local ffprobe keyframe/video audit; no video seeking benchmarks.

If --ffprobe-json is used, supply data produced by ffprobe -show_frames/-show_streams.
Otherwise ffprobe must be on PATH. Video files are opened locally, never modified.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path


def _num(x):
    try:
        f = float(x)
        return f if math.isfinite(f) and f >= 0 else None
    except (TypeError, ValueError):
        return None


def _p95(xs):
    return sorted(xs)[max(0, math.ceil(.95 * len(xs)) - 1)] if xs else None


def summarize(data, file_bytes=None):
    if not isinstance(data, dict):
        raise ValueError('ffprobe object required')
    streams = [x for x in data.get('streams', []) if isinstance(x, dict) and x.get('codec_type') == 'video']
    if not streams:
        raise ValueError('ffprobe JSON has no video streams')
    stream = streams[0]
    frames = [f for f in data.get('frames', []) if isinstance(f, dict) and
              f.get('media_type', 'video') == 'video']
    key_positions = [i for i, f in enumerate(frames) if str(f.get('key_frame')) == '1']
    distances = [b-a for a, b in zip(key_positions, key_positions[1:])]
    key_times = [_num(frames[i].get('best_effort_timestamp_time', frames[i].get('pts_time')))
                 for i in key_positions]
    time_gaps = [b-a for a, b in zip(key_times, key_times[1:]) if a is not None and b is not None and b >= a]
    return {
        'video_bytes_on_disk': file_bytes,
        'codec_name': stream.get('codec_name'),
        'codec_profile': stream.get('profile'),
        'width': stream.get('width'), 'height': stream.get('height'),
        'reported_avg_frame_rate': stream.get('avg_frame_rate'),
        'reported_r_frame_rate': stream.get('r_frame_rate'),
        'reported_duration_seconds': _num(stream.get('duration')),
        'frame_records_count': len(frames),
        'keyframe_records_count': len(key_positions),
        'keyframe_observation': 'EXTRACTED_FRAMES' if frames else 'NOT AVAILABLE: -show_frames required',
        'max_spacing_between_observed_keyframes_in_frames': max(distances, default=None),
        'p95_spacing_between_observed_keyframes_in_frames': _p95(distances),
        'max_spacing_between_observed_keyframes_seconds': max(time_gaps, default=None),
        'p95_spacing_between_observed_keyframes_seconds': _p95(time_gaps),
        'leading_frames_before_first_observed_keyframe': key_positions[0] if key_positions else None,
        'seeking_latency_ms': 'NOT MEASURED',
        'reversible_scroll_quality': 'NOT TESTED',
        'limitations': [
            'Observed keyframe spacing is not universal GOP size; variable-GOP and variable-FPS streams exist.',
            'Frames list may be incomplete in supplied ffprobe JSON; do not infer uniform seeking from this count.',
            'all-intra, short GOP and normal GOP must be compared at matched content, quality, platform and network.',
            'Keyframes do not prove immediate browser seek, accurate display, range support, or frame presentation.',
        ],
    }


def _ffprobe(path, tool):
    args = [tool, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=codec_type,codec_name,profile,width,height,avg_frame_rate,r_frame_rate,duration:frame=media_type,key_frame,best_effort_timestamp_time,pts_time',
            '-show_streams', '-show_frames', '-of', 'json', str(path)]
    try:
        result = subprocess.run(args, text=True, capture_output=True, check=True, timeout=120)
    except FileNotFoundError as e:
        raise RuntimeError('ffprobe is not installed; use --ffprobe-json or install ffprobe') from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError('ffprobe failed for local file (details withheld)') from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError('ffprobe timed out') from e
    return json.loads(result.stdout)


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('video', nargs='?', help='Local video file, if --ffprobe-json is omitted')
    a.add_argument('--ffprobe-json', help='Existing local ffprobe JSON; no ffprobe execution')
    a.add_argument('--ffprobe', default='ffprobe', help='ffprobe executable path/name')
    a.add_argument('--out')
    x = a.parse_args()
    if not x.video and not x.ffprobe_json:
        a.error('local video or --ffprobe-json required')
    file_path = Path(x.video) if x.video else None
    if file_path and not file_path.is_file():
        a.error('video must be a local existing file')
    data = json.loads(Path(x.ffprobe_json).read_text('utf-8-sig')) if x.ffprobe_json else _ffprobe(file_path, x.ffprobe)
    report = summarize(data, file_path.stat().st_size if file_path else None)
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if x.out:
        Path(x.out).write_text(output, encoding='utf-8')
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
