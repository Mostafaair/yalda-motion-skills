# HAR and Chrome Performance trace — v0.1.3, read-only

## Capture
1. Record exact staging revision/URL, timestamp, browser version, viewport/DPR, hardware, refresh rate and cache state. Do not use admin, OTP, payment or any authenticated page.
2. For Chromium collect a **Chrome Performance trace** in DevTools / Chrome DevTools MCP with start **before** the specific scroll and stop **after**. A Playwright Trace Viewer trace is not the same format as Chrome Performance trace.
3. Export sanitized DevTools HAR, inspect before sharing: removing cookies/authorization headers does not necessarily remove URL query secrets. Do not put secret-bearing unredacted traces or HARs in the Skill ZIP.
4. Optional `capture_scroll_paths.mjs` uses separate Playwright context, collects deterministic *input descriptions*, a screenshot, and HAR. It **does not** record raw Chrome Performance trace; wheel events and browser execution still vary. Requires locally installed Node.js + Playwright; script was syntax-checked but not exercised with Playwright in v0.1.2.
5. Before declaring `cold`/`warm` explicitly log DevTools cache setting, profile and run order. Cold/warm is NOT inferred from HAR.

## Offline commands
```
python scripts/analyze_har.py network.har --cache-state cold
python scripts/analyze_chrome_trace.py chrome-trace.json.gz
python scripts/analyze_chrome_trace.py chrome-trace.json --renderer-pid 12345
python scripts/analyze_chrome_trace.py chrome-trace.json --renderer-pid 12345 --main-tid 6789
python scripts/analyze_frame_log.py frame-log.jsonl
```

## Trace attribution and schema
- Both `RunTask` (legacy) and **`ThreadControllerImpl::RunTask` (observed Chrome 154)** are counted as renderer-main only when a unique thread metadata `(pid,tid)` names `CrRendererMain`/`RendererMain`, **or** explicit PID/TID are supplied. Multiple candidate renderer mains require a user-verified PID. The all-process count is deliberately named `UNATTRIBUTED` and must not be used as a YALDA main-thread result.
- **Chrome 154** `FrameSequenceTrackerV3` uses `args.args.data.expected`, `dropped_v3` and `dropped_v4` with the label in `args.name`; these are **per-event snapshots**, not a count of actually displayed YALDA frames or end-to-end FPS. Do not add overlapping `CanvasAnimation`, `JSAnimation`, `MainThreadAnimation` and compositor sequences, and do not assume the `ph=b` payload represents a completed interval. Async `ph=e` events without data are ordinary end markers, not format errors.
- `FrameSequenceTracker` (older traces): source-grounded legacy keys `impl-frames-expected/produced` and `main-frames-expected/produced` are recognized in `args` or `args.data` if valid and unambiguous. Each result is **one lane in one sequence report**; don't add impl and main or overlapping sequences. Unknown schema returns `NOT AVAILABLE IN TRACE` not zero.
- `PipelineReporter` explicit state counts can include unrelated surfaces and need manual DevTools Frames correlation. Async B/E pairing is best-effort and can be version-dependent.
- Chrome 154 decode names include `GpuImageDecodeCache::DecodeImage`, `GpuImageDecodeTaskImpl::RunOnWorkerThread` and `ImageController::ProcessNextImageDecodeOnWorkerThread`; they are **separate overlapping operations**, not additive decode time.
- `ScrollJankV4` explicit `args.scroll_jank_v4.is_janky` status is reported independently from canvas/image presentation. A false value does not prove a smooth hero.
- Decode events may nest and overlap, so time totals are not added. Trace event timing is typically microseconds; `RunTask≥50ms` is a threshold candidate, not LoAF or proof of a dropped presented frame.
- Chromium primary source: https://chromium.googlesource.com/chromium/src/+/main/docs/speed/debug-janks.md ; tracker source: https://chromium.googlesource.com/chromium/src/+/a108d811e91a6e66e1b807a1ced3f6807709e65b/cc/metrics/frame_sequence_tracker.cc

## HAR timing
- HAR 1.2 `startedDateTime` + `time` produce a **request interval**; concurrency is overlap of these intervals, not number of TCP connections nor simultaneous Decode jobs.
- Report network first/last **request start and completion**, plus images/video relative to the earliest logged request. This is NOT first **decoded**, usable or presented frame.
- Missing/invalid timestamps => missing timeline observations; present quantities are partial. `response.bodySize=-1` is unknown, not zero and not wire transfer bytes. `blocked` is network-related queue timing.
- Output excludes URLs/domains/headers, but inputs can still contain secrets. Source: https://github.com/ahmadnassri/har-spec/blob/master/versions/1.2.md

## Evidence status
Never declare a current YALDA frame-dropping cause from synthetic fixtures. If actual trace schema is unsupported, report unsupported keys/status and compare with manual Chrome Frames / Performance. Keep hypotheses ranked alongside their discriminating next measurements.

## Verified evidence (8 November 2026, user-provided R1/R2 archive)
- Input `YALDA_HERO_EVIDENCE.zip` SHA-256 `88e8262000e09960a1566e2489d883fa2a877604bb66208cdbd647ff866e211f`; collected Chrome 154 on Windows 10, 1366×900. Raw evidence **not redistributed in this Skill**.
- On real trace, v0.1.3 recognizes Renderer Main complete-event `ThreadControllerImpl::RunTask`: R1=4,831, R2=1,937; maximum duration R1=28.237ms, R2=23.206ms. One run per version; not directly comparable performance rates.
- Explicit `ScrollJankV4` boolean: R1=28 reported values, 0 true; R2=28 reported values, 0 true. This does **not** measure image-sequence frame jumps.
- V3 recognized counter-bearing snapshots: R1=8; R2=22. Example snapshots R1 `MainThreadAnimation` expected=869, dropped_v4=433; R2 `CanvasAnimation` expected=5, dropped_v4=4. Do not convert these to global drop percentages.
- `GpuImageDecodeCache::DecodeImage` complete events: R1=14; R2=7. These do not establish full decode costs or main-thread blocking.
- See `VALIDATION_REAL_20261108_FA.json` and `EVIDENCE_RECHECK_20261108_FA.md` in package root for rerun status and limitations.
