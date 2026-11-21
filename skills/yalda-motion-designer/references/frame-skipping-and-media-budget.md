# Frame skipping, media budgets and image readiness

## Mandatory first diagnosis
Use precise labels:
- `content_gap`: discrete source images have different model/camera geometry; no credible intermediate position.
- `input_sampling`: the scroll target jumps from frame i to j between observed input samples; skipping unseen indices may be normal and does **not** demonstrate a dropped rendered frame.
- `not_ready`: desired image isn't available to draw because transfer/decode/queue failed or lagged; detect by `target_ready=false` at a sampled target.
- `scheduler_stale`: a ready target is available yet the application remains behind due to queued outdated work / smoothing / update design; requires scheduling logs to attribute cause.
- `presentation_delay`: frame was scheduled/drawn but browser missed its presentation deadline; confirm with browser performance Frames or external video, not JavaScript counters alone.
- `unknown`: unresolved if available evidence cannot distinguish mechanisms.

## Request → ready → shown → presented state machine
1. Determine `p = clamp((scrollY-start)/(end-start),0,1)` as the **target state** (more complex maps permitted if deterministic).
2. Target selection: frame index or video timestamp. A change from i to j may be an intentional input jump.
3. Image fetch request: track request start/completion/error and resource path; separate cache-cold from warm; cancellation/coalescing does not guarantee an already started network transfer or decoder is instantly stopped.
4. Image Decode: `img.decode()` fulfills once image is decoded; distinguish from `load`. If `createImageBitmap`, close bitmaps on eviction. Handle rejected promises, stale generation tokens and tab/resize transitions.
5. Drawing/DOM update: only draw a ready image. If target missing, preserve last valid state or choose a documented nearby fallback; no empty frame. `shown` is **program-selected**, not proof of compositor presentation.
6. Presented: verify with performance trace, visual recording and/or video frame callback if video architecture. Be explicit if no such proof.

## Adaptive scheduler — desired policy, NOT implementation claim
- One canonical p; latest target supersedes stale requests. Coalesce repeated requests.
- A bounded number of active fetches/decode tasks and decoded working-set; values **measured/tuned per device**, not universal. Never enqueue the entire corpus as equally urgent.
- Initial hero poster has a dedicated early discovery path; minimal essential media only initially.
- Prefetch a small window around p, favor the current travel direction, retain a smaller reserve behind for immediate reverse. At direction reversal re-prioritize future requests; don't assume changing `fetchPriority` after request initiation actually reprioritizes it.
- Candidate tiers: mobile/low-resource, standard desktop, high-DPR desktop; compare quality and byte counts, do not choose from `deviceMemory` alone, since availability varies and may be privacy-rounded.
- Recompute demand after resize/orientation and preserve p/scene identity during tier change.
- Evict distant decoded images by bounded budget; release `ImageBitmap` with `close()` when used; retained pixel memory isn't simply file bytes.
- Avoid double smoothed delay (numeric GSAP scrub plus custom LERP plus smooth-scroll).
- If target missing, fallback policy must be deterministic and reverse-safe. Never snap arbitrarily to a future frame that changes scientific scene state.

## Budget worksheet (conceptual, tune via benchmark)
For N independent encoded images of size b_i bytes and dimensions w_i × h_i:
- `transfer_bytes = Σ b_i` for the selected variant/corpus (not necessarily actual network bytes, affected by cache and headers).
- `decoded_rgba_upper_bound_bytes = Σ 4 × w_i × h_i` if **all** frame pixels resident as 8-bit RGBA; GPU textures/copies, color depth and browser policies may differ. This is **not measured RAM**.
- `working_set_bytes ≈ Σ_{i∈active decoded set}4×w_i×h_i` as a planning estimate; prove it with device tracing/telemetry where available.
- `asset_bytes_per_scroll_window` and `decode_jobs_per_second` must be estimated under the **fastest requested user interaction**, not an autoplay fps assumption.
- `p` step spacing for frame i should respect maximum projected model/camera displacement; frame count is driven by content derivative and target quality, not by an arbitrary 30fps×seconds formula.
- Keep separate: encoded bytes, cache residency, decoded CPU memory, GPU texture memory, actual presented frames.

**Example only:** 240 frames × 150 KB ≈36 MB encoded; at 1600×1000 px, all decoded as RGBA ≈1.43 GiB. This is arithmetic, not YALDA runtime measurement.

## Visual quality gates
- Compare reference raster and proposed compressed outputs at **same crop and scale** for hard edges: foundation outlines/openings, fine isolines, labels, patch borders, color gradients, alpha and thin arrows.
- Use multiple image variants and explicit line/text QA; lossy may produce ringing or chroma bleed while lossless may be too heavy. Never assert AVIF or WebP is always superior.
- Prefer separating consistent UI frame/labels from model media if alignment and fidelity can be proven, reducing repeated pixels per encoded frame.
- A sprite sheet can reduce request count but may increase memory, delay partial use and still fail random access; only compare experimentally.
- Optimize sequential image vs seekable video vs selective 3D after confirming identical approved source, content and crop.

## Minimal frame sample schema
Each line is a JSON object captured at a *sampled client tick*, not a compositor frame:
```
{"t_ms":0,"target_index":0,"shown_index":0,"target_ready":true,"blank":false}
{"t_ms":16,"target_index":5,"shown_index":0,"target_ready":false,"blank":false}
{"t_ms":32,"target_index":5,"shown_index":5,"target_ready":true,"blank":false}
```
Rules: monotonic time, nonnegative target, shown>=-1 (`-1`=nothing), booleans for readiness/blank. Index gaps are not automatically browser frame drops. Real recording requires an authorized observational adapter to the source application or controlled browser test; don't silently change deployed JS.

Use `scripts/analyze_frame_log.py`. Results: number of intentional index jumps, percentage of not-ready samples, number of stale shown samples, blank samples, mismatch and longest shown-index hold. **No inferred GPU FPS**.

## Required experiments
- Cold cache, measured throttled networks, warm cache, rapid forward, slow forward, sudden reverse, direct jump, tab hide/return, resize, mobile DPR, offline/error 404, reduced motion.
- Record resource priority, waterfall queueing, download, decode readiness, visible target mapping and browser frames/traces.
- Collect 3+ repeated passes if comparing performance, and report variance; number of passes is a **proposed methodology**, not vendor standard.
- Record separate first usable hero/initial poster time vs LCP; canvas-only visual readiness may not be captured by a single Web Vital.
- Evaluate direction-reversal target lag in p units and landmark displacement, not frame indices alone.

## Production gate
P0: no unbounded eager frame burst; no blank/invalid state under recoverable missing frame; no unmeasured performance claim; no unexplained rapid-reverse artifact in required environments; physical model continuity preserved. If any criterion untested, mark NOT TESTED and block claiming production-ready.


## v0.1.1 additions
- See `open-source-patterns.md` for progressive layered coverage, constrained low-res sheets and latest-target video seeking as **experiment alternatives**.
- `analyze_frame_log.py` now records shown-index jumps, max/p95 inter-sample gaps, reversals and a conservative sampled hold lower bound. Old `max_shown_index_hold_ms_observed` was removed because it misclassified unsampled gaps.
- `asset_budget.py --window 8 --tier-mode first-folder` adds an illustrative lexicographic per-tier sliding-window estimate (not actual runtime cache occupancy).
- `analyze_har.py` and `analyze_chrome_trace.py` handle available offline evidence; missing trace frame states are *not* zero drops. See `trace-har-playbook.md`.
