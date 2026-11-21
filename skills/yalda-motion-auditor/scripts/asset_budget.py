#!/usr/bin/env python3
"""Read-only image corpus inventory. The RGBA estimate is NOT measured RAM/VRAM.

No network; no writes unless --out is specified. Optional Pillow for dimensions.
"""
import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}
EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def dimensions(path):
    try:
        from PIL import Image
        with Image.open(path) as image:
            return [int(image.width), int(image.height)]
    except Exception:  # Pillow unavailable, unreadable or unsupported format
        return None


def _natural_key(path):
    # Natural ordering of path components; f2 precedes f10. Does not infer frame IDs.
    parts = re.split(r"(\d+)", str(path).replace("\\", "/").lower())
    return tuple((0, int(x)) if x.isdigit() else (1, x) for x in parts)


def _load_manifest(root, manifest_path):
    """Optional explicit sequence ordering via JSON {frames:[relative_path,...]}.

    One entry per image file. Each file must exist inside root; no traversal.
    """
    if manifest_path is None:
        return None
    data = json.loads(Path(manifest_path).read_text('utf-8-sig'))
    names = data.get('frames') if isinstance(data, dict) else None
    if not isinstance(names, list) or not names or any(not isinstance(x, str) or not x for x in names):
        raise ValueError('manifest must contain a non-empty frames list of relative paths')
    if len(names) != len(set(names)):
        raise ValueError('manifest has duplicate paths')
    result = []
    for n in names:
        rel = Path(n)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('manifest contains an unsafe path')
        target = (root / rel).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError('manifest references missing/outside-root file')
        if target.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError('manifest frames must be image files')
        result.append(target)
    return result


def summarize(root, details=False, effective_mbps=None, window=None, tier_mode="none", manifest=None):
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    if window is not None and (type(window) is not int or window <= 0):
        raise ValueError("window must be positive integer")
    if tier_mode not in ("none", "first-folder"):
        raise ValueError("tier_mode must be none or first-folder")
    files = sorted((p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS), key=lambda p: _natural_key(p.relative_to(root)))
    ordered_frames = _load_manifest(root, manifest)
    if ordered_frames is not None:
        existing = set(p.resolve() for p in files if p.suffix.lower() in IMAGE_EXTENSIONS)
        if set(ordered_frames) != existing:
            raise ValueError('manifest must list every image exactly once; no unseen image files')
    rows = []
    for p in files:
        media_kind = "video" if p.suffix.lower() in VIDEO_EXTENSIONS else "image"
        width_height = dimensions(p) if media_kind == "image" else None
        bytes_on_disk = p.stat().st_size
        rel = p.relative_to(root)
        tier = rel.parts[0] if tier_mode == "first-folder" and len(rel.parts) > 1 else "root_or_all"
        row = {
            "tier": tier,
            "file": str(rel),
            "extension": p.suffix.lower(),
            "media_kind": media_kind,
            "encoded_bytes_on_disk": bytes_on_disk,
            "dimensions": width_height,
            "estimated_rgba_bytes": (4 * width_height[0] * width_height[1]) if width_height else None,
        }
        rows.append(row)
    if ordered_frames is not None:
        rank = {str(p.relative_to(root)): i for i, p in enumerate(ordered_frames)}
        rows.sort(key=lambda r: ((0,rank[r['file']]) if r['media_kind']=='image' else (1, _natural_key(r['file']))))
    sizes = sorted(r["encoded_bytes_on_disk"] for r in rows)
    images = [r for r in rows if r["media_kind"] == "image"]
    videos = [r for r in rows if r["media_kind"] == "video"]
    known = [r for r in images if r["dimensions"] is not None]
    est_rgba = sum(r["estimated_rgba_bytes"] for r in known)
    def pct(p):
        return sizes[math.ceil(p * len(sizes))-1] if sizes else None
    summary = {
        "source_root": str(root.resolve()),
        "tier_mode": tier_mode,
        "frame_order_mode": "explicit_complete_manifest" if ordered_frames is not None else "natural_filename_sort_NOT_verified_frame_order",
        "file_count": len(rows),
        "image_file_count": len(images),
        "video_file_count": len(videos),
        "video_encoded_bytes_on_disk": sum(r["encoded_bytes_on_disk"] for r in videos),
        "video_decoding_requirements": "NOT EVALUATED: use ffprobe/codec manifest and actual video seek trace",
        "counts_by_extension": dict(sorted(Counter(r["extension"] for r in rows).items())),
        "total_encoded_bytes_on_disk": sum(sizes),
        "largest_file_bytes": sizes[-1] if sizes else None,
        "median_file_bytes_nearest_rank": pct(0.5),
        "p95_file_bytes_nearest_rank": pct(0.95),
        "dimensions_known_count": len(known),
        "dimensions_unknown_image_count": len(images) - len(known),
        "estimated_rgba_bytes_known_images_if_all_decoded": est_rgba,
        "estimated_rgba_mib_known_images_if_all_decoded": round(est_rgba/1048576, 2),
        "image_estimate_complete": len(known) == len(images),
        "disclaimer": "Encoded on-disk bytes are not measured network transfer; theoretical 4 bytes/pixel for known frames if all resident is NOT observed browser RAM or VRAM, ignores texture/copies/format and browser reclamation.",
        "web_budgets": "No universal maximum frame count, MB, concurrency or fps is asserted; Owner must approve device/network budget and compare trace evidence.",
    }
    tiers = {}
    for name in sorted({r["tier"] for r in rows}):
        group = [r for r in rows if r["tier"] == name]
        images_in_tier = [r for r in group if r["media_kind"] == "image"]
        data = {
            "file_count": len(group), "image_count": len(images_in_tier),
            "encoded_bytes_on_disk": sum(r["encoded_bytes_on_disk"] for r in group),
            "theoretical_all_known_images_rgba_bytes": sum(r["estimated_rgba_bytes"] or 0 for r in images_in_tier),
            "unknown_image_dimensions_count": sum(r["estimated_rgba_bytes"] is None for r in images_in_tier)
        }
        if window is not None:
            w = min(window, len(images_in_tier))
            segments = [images_in_tier[i:i+w] for i in range(len(images_in_tier)-w+1)] if w else []
            data["sliding_window"] = {
                "window_count": len(segments),
                "max_encoded_window_bytes": max((sum(r["encoded_bytes_on_disk"] for r in seg) for seg in segments), default=0),
                "max_theoretical_rgba_window_bytes_for_known_dimensions": max((sum(r["estimated_rgba_bytes"] or 0 for r in seg) for seg in segments), default=0),
                "max_unknown_dimensions_in_window": max((sum(r["estimated_rgba_bytes"] is None for r in seg) for seg in segments), default=0),
            }
        tiers[name] = data
    summary["tiers"] = tiers
    if window is not None:
        summary["window_images_requested"] = window
        summary["window_definition"] = "Contiguous images per tier in explicit manifest order if provided, otherwise natural filename sort; NOT measured decoded RAM/cache residency"
    if effective_mbps is not None:
        if effective_mbps <= 0 or not math.isfinite(effective_mbps):
            raise ValueError("effective_mbps must be positive and finite")
        summary["optimistic_full_corpus_transfer_seconds_at_assumed_effective_mbps"] = round(8*sum(sizes)/(effective_mbps*1_000_000), 3)
        summary["transfer_estimate_caveat"] = "Arithmetic minimum at supplied EFFECTIVE throughput, assuming full corpus request and ignoring request/RTT/queueing/decode/cache overhead; NOT a measured loading time."
    if details:
        summary["files"] = rows
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", help="Local directory containing media (read-only)")
    ap.add_argument("--details", action="store_true", help="Include each file in JSON")
    ap.add_argument("--window", type=int, help="Hypothetical contiguous N-image window")
    ap.add_argument("--tier-mode", choices=["none", "first-folder"], default="none")
    ap.add_argument("--manifest", help="Optional JSON {frames: [relative_path,...]} listing ALL images in approved playback order")
    ap.add_argument("--effective-mbps", type=float, help="Optional assumed EFFECTIVE throughput for an optimistic full-corpus transfer-time calculation; not a benchmark")
    ap.add_argument("--out", help="Optional output JSON path; otherwise print to stdout")
    args = ap.parse_args()
    result = summarize(args.root, args.details, args.effective_mbps, args.window, args.tier_mode, args.manifest)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
