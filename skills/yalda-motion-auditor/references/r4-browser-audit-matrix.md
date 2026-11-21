# R4 — Visual Timeline and Image-First Hybrid: read-only browser QA

## Evidence levels
1. Source inspection and static JSON schema: **structural only**.
2. Node or Python numeric checks: **mathematical only**.
3. In-memory Chromium execution with exact packaged HTML/CSS/JS/asset bytes: **visual + DOM for that artificial environment**; not hosting/network verification.
4. Real hosted URL on actual target: loading/MIME, response headers, decode latency, ready/target/shown alignment, browser performance and interaction on that host.
5. Actual mobile device: touch momentum, readability, font fallback, composition stability. Desktop mobile emulation does not prove physical mobile PASS.
No mixing levels: Work reported "Chromium passed" should specify URL/mode, images and screen coordinates.

## Required benchmark grid
- Browser sizes: 1366×768, 390×844; additional aspect ratios where practical. Emulated touch and real phone separate.
- Chapters local p: 0, .01, .1, .25, .50, .52 when relevant, .75, .99, 1; chapter boundary p≈.9999/next≈.0001; visually chosen intermediate states in stress, neighbor, patch and 3D-to-plan transitions.
- Test forward, reverse, sudden jump, resize at p, reduced motion, no animation/offline fallback, slow and fast scroll and both native and editor navigation.
- Source and origin hash in all screenshots; compare pixels with exact original assets and record any derived image transformations (crop, alpha, edit, recolor, outline).

## P0 conditions to fail
- Any simultaneous shell blackout, shell overlap hidden by clipping, independent rail velocities when synchronized motion required, z-index flip or teleportation.
- Foundation not fully inside target model workspace at Owner-approved landing; unexpected duplicated/fragmented/floating slab or UI occlusion.
- 2D→3D or 3D→plan double geometry, misregistered patch wipe, SAFE UI fabricated as actual software, false engineering claim.
- Parent/child drift when changing rail, p or viewport; scene-relative caption detached from shell; unknown text direction, clipped headline or early exit; blank render or media fallback from unrelated stage.
- Reverse scroll renders a different settled state at same p+viewport; invalid/duplicate keyframe accepted as valid; JSON round trip loses responsive tracks or rail config.
- Unbounded or uncontrolled inertia, overshoot, long lag, lag after reversing, reduced-motion ignored, UI interactions delayed.

## P1 / still blocking final aesthetic acceptance
- Title falls over patch colors, sidebars or important stress cores; mobile headline cut off; unresolved font license; unreadable hold.
- Large empty gap to lower SAFE or out-of-frame handoff; visible hard edge, unmatched alpha/matte; different position due to untested viewport.
- FPS/long tasks, decode latency, network failures, MIME `.mjs` type, accessibility and performance unmeasured.

## Browser capture checklist
Each evidence record must include: file hash, environment/browser version, viewport/scale, chapter and local p, real scroll px, target/display p if momentum enabled, bounding boxes of shell/workspace/foundation/captions, resource state, measured/asserted/assumed distinctions, screenshot path, console/network errors and known NOT TESTED areas.

## PASS discipline
- `validate_visual_timeline.py`: schema and declared continuity **only**, no visual PASS.
- `audit_scroll_momentum.py`: log metrics **only**, no actual presentation proof.
- Browser screenshots + DOM measurements: supports visible overlap, registration and placement at selected p only, not smooth FPS over the full timeline.
- HAR/Trace/Performance: needed for frame skip, decode latency and browser jank; preserve historical findings as regression candidates.
- Owner sign-off: aesthetic/production acceptance cannot be inferred from numerical PASS.
