# Video route / GOP / reversal — v0.1.2

`video_budget.py` can inspect *local* media using `ffprobe`, or an already generated ffprobe JSON with `--ffprobe-json`. It outputs reported codec/rates, frame/keyframe counts and observed spacing, and says **NOT MEASURED** for seek latency.

```
python scripts/video_budget.py ./hero.mp4
python scripts/video_budget.py --ffprobe-json ./ffprobe.json
```

Video decision variants for identical source content: (1) normal inter-frame GOP, (2) shorter GOP, (3) all-intra GOP=1. Test bytes, cold poster, server Range requests, first seek after load, reversal, fast direct jump and mobile Safari. Record compatible browsers and decoding delays; avoid a blanket rule 'keyframe every N'.

`ScrollyVideo.js` upstream uses WebCodecs/playbackRate/currentTime fallback as available. This is **published implementation**, not a verified result for YALDA. Negative `playbackRate` is not a portable reverse solution. Source: https://github.com/dkaoster/scrolly-video ; reference for ffprobe: https://www.ffmpeg.org/ffprobe.html

Explicitly compare with bounded image sequence and progressive tiers; never select video solely because output bytes are smaller. No source change to YALDA without Owner GO.
