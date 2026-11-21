# Owner-controlled motion-frame count and byte budgets — HARD CONTRACT (v0.2.0)

## Why
User must choose (a) **global aggregate frame count**, exact or maximum; (b) **global aggregate encoded on-disk bytes of all frame images**, in decimal MB (1 MB=1,000,000 bytes). Includes *every* responsive frame tier — desktop, mobile, HiDPI, etc. Never describe a 180-frame global budget as 180 desktop + 180 mobile. Report other bytes separately: HTML/CSS/JS, poster, shell, fonts/subtitles, video alternatives and deploy ZIP. Distinguish encoded bytes, actual network transfers, and decoded RAM/VRAM.

## Input before any media generation
1. Ask Owner or read **explicitly approved** `owner-media-budget.json`: `count_policy=maximum|exact`, `max_total_frames`, `max_total_mb`, per-tier caps/weights (or Owner authorization to propose split), stage minima, essential checkpoints and approval reference.
2. Do NOT invent final values or treat an example file as approved. Empty template = DRAFT, not execution permission. If Owner has not chosen values, draft alternatives and STOP at the budget decision gate.
3. Compute feasibility: sum of stage minima across all tiers ≤ total frame cap, aggregate tier caps ≥ requested frame allocation, per-tier byte limits consistent with global limit, preserved mandatory milestone frames, approved reference appearance.
4. **Density by motion complexity:** estimate screen-space motion/landmark displacement, curvature/change in camera motion, stage length and semantic checkpoints. Allocate unevenly; avoid naïve every-Nth downsampling of R2's nonuniform `p` positions and avoid requiring uniform FPS per scroll section. Keep known scientific steps, adjacent positions, patch continuity and SAFE handoff.
5. Choose candidate compression/size for frames on representative scenes using same crop and visual master. Fit quality to budget via (a) less waste/duplicate rendered output, (b) reallocation of samples, (c) responsive dimensions, (d) WebP/AVIF/other candidates, (e) hybrid video fallback only after random seek tests. **Never silently degrade scientific geometry/patch IDs, approved outlines or color semantics.**
6. If constraints can't all be met: `INFEASIBLE`, list which constraints conflict, present measured tradeoffs and STOP for Owner decision. Never exceed budget and simply label success; never quietly raise cap.

## Executable checks
- `scripts/media_budget_contract.py --config <config>` → PLAN_ONLY_NOT_MEASURED or DRAFT; deterministic tier/stage allocations, byte allowance.
- `scripts/media_budget_contract.py --config <approved> --frames-root <all_frame_images_only> --manifest <inventory.json>` → PASS or FAIL for count and encoded on-disk frame bytes; the manifest MUST list every file in `frames-root`, with explicit tier/stage/p. Use forward slashes for relative paths. Unlisted frames, duplicate entries, unknown stage, nonmonotonic p, over caps or unapproved contract all FAIL.
- No tool in this package renders/encodes frames. Asset size checks are NOT proof of quality, latency, visual presentation, browser memory or internet bandwidth.
- Global aggregate includes mobile and desktop even if only one is downloaded in a user session; provide independent per-device transfer measurements in addition.
- Work must deliver actual `frame-inventory.json`, config snapshot, PASS result and source reference hashes for acceptance. No Owner GO for site source/deploy is implied by changing this config.

## Acceptance
Hard count/bytes verified; important stage endpoints and scientific landmarks manually inspected; gap and reverse tests at cold/warm cache on representative browser/device; clarity/typography/contours near full viewport and mobile; bounded concurrency and decode working-set supported by trace; no use of stale-frame fallback across stages; screen p ↔ frame p measured. Record global, per-tier, media-extras, compressed/delivered and decoded working-set metrics SEPARATELY. Owner signoff required.

## User-friendly input without manually editing JSON
Run `scripts/configure_owner_budget.py --template assets/owner-media-budget-TEMPLATE.json --total-frames <OwnerN> --total-mb <OwnerMB> --count-policy maximum --out ./owner-media-budget.json`. This writes a **new** config, never overwrites the template, and does **not** mark it Owner-approved. Add `--approval-id <explicit Owner decision reference>` only with real Owner authorization. The Owner may use exact mode instead. The tier split and p ranges are initial planning inputs, not final approved science; inspect the plan and QA the actual stage allocation. Work can also create the same JSON after asking the Owner conversationally.

## If Work chooses video rather than image sequence
This v0.2.0 strict validator counts **individual encoded image frame files only**. It must NOT claim that an MP4 with 0 image files satisfies a user's frame-count/MB budget. A video candidate must be labeled `ALTERNATIVE_NOT_COVERED_BY_FRAME_IMAGE_GATE`, and its total codec/container bytes plus encoded frame count and seek behavior must be separately measured with `video_budget.py`/ffprobe and browser QA. To use video as the final method, request explicit Owner confirmation of how frame count and global video media byte cap are defined, then add/validate a video-specific release gate rather than silently repurposing the image inventory check.
