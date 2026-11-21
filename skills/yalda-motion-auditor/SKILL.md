---
name: yalda-motion-auditor
description: Perform evidence-based, read-only audits of cinematic scroll-driven heroes including YALDA Visual Timeline, common-rail geometry, caption collisions, image fidelity, loading/decoding, frame skipping, bounded momentum, accessibility, mobile composition and browser performance. Use when checking a source archive, live staging URL, render trace, HAR, or regression; distinguish measured failures from hypotheses and require owner approval for any change.
compatibility: Python 3.10+ for analysis scripts; optional ffprobe for video metadata; browser QA needs a separately available browser.
metadata:
  version: "0.5.0"
---
# YALDA Motion Auditor

**Default mode: STRICT READ-ONLY.** Never modify project source, re-render imagery, upload, deploy, change API/SEO settings, or use admin/payment endpoints without explicit Owner GO. Audit artifacts belong in a separate workspace. Historical defects are regression hypotheses, **not current facts**.

## Evidence levels (never conflate)
1. **Source/static**: code, manifests, assets, hash, timeline schema. Structural evidence only.
2. **Numeric/replay**: repeatable keyframe/interpolation assertions. Mathematical evidence only.
3. **Local browser**: pixels/DOM/console for an extracted exact package. Not live-host evidence.
4. **Hosted browser**: actual URL, HTTP/MIME/cache and browser behavior. Not a physical phone.
5. **Real device**: native scroll, typography and touch observation on actual hardware.

## Audit sequence
1. Record exact build ZIP, URL, SHA-256, revision, approved reference, device/browser, cache, date and granted scope. Treat unknown data as **NOT TESTED**, not PASS.
2. Choose rendering profile: image-first source reuse, 3D-source continuity or frame/video. Do not demand 3D scene proof for the image-first profile. Read [profiles](references/profile-selection-and-r4-image-first.md) and [scientific integrity](references/scientific-integrity.md).
3. Validate Visual Timeline chapter-local progress, ID/space/compact tracks, coordinates and interpolation, using `scripts/validate_visual_timeline.py`. Verify **rendered** SAFE/YALDA common-rail positions, nonoverlap, model containment and reverse transitions separately in the browser. Read [timeline](references/visual-timeline-v1-contract.md), [rail](references/common-rail-and-chapter-choreography.md).
4. Inspect each caption's actual bounding box, glyph collision, clipped text, opacity, event alignment, scene anchoring, responsive font and continuous readable coverage. An opacity threshold alone never proves readability. Read [caption relay](references/caption-relay-owner-contract.md) and [typography](references/cinematic-text-and-typography.md).
5. Measure media loading and decode readiness: `requested -> fetched -> decoded -> shown -> presented` is not one step. Distinguish input index sampling from absent media, stale scheduling and missed compositor frames. Browser FPS cannot be inferred from `requestAnimationFrame` counts. See [media gaps](references/frame-skipping-and-media-budget.md), [browser test](references/browser-test-protocol.md), [HAR/trace](references/trace-har-playbook.md).
6. Check scroll reversibility, adaptive momentum target/display lag, rapid direction reversal, resize, reduced-motion, poster fallback, touch/mobile, accessibility alt and HTML semantics, CPU/decode latency and long frames where evidence exists. See [momentum](references/bounded-scroll-momentum.md), [R4 matrix](references/r4-browser-audit-matrix.md), [SEO/accessibility](references/hero-semantic-seo-geo-and-alt.md).
7. Confirm original media hashes and engineering interpretation; distinguish conceptual stress contours from numerically validated SSI results. Check patch/plan registration and no R1 image degradation.
8. Identify minimal reproduction steps and **separate measured findings from hypotheses**. Rate severity and likely root cause, list explicit unavailable evidence. See [acceptance gates](references/acceptance-gates.md) and [evidence governance](references/evidence-and-governance.md).

## Tools
- `analyze_har.py`, `analyze_chrome_trace.py`, `analyze_frame_log.py`, `asset_budget.py`, `video_budget.py` (optional `ffprobe`) — offline analysis; never fabricate missing network/performance data.
- `validate_visual_timeline.py`, `audit_caption_coverage.py`, `audit_hero_html.py`, `audit_scroll_momentum.py`, `validate_motion_contract.py`, `validate_text_overlays.py` — static/log-based only.
- `media_budget_contract.py`, `work_budget_guard.py`, `checkpoint_manager.py` — controlled media/cost/checkpoint checks. Never claim direct access to Work quota.
- Fixture data in `assets/` is explicitly synthetic and MUST NOT be cited as site observations.

## Deliver and stop
Report `PASS / FAIL / NOT TESTED / BLOCKED` per criterion, exact affected source/hash, relevant actual browser screenshots/logs, reproducible steps, proposed **read-only** corrective plan, risks, and Owner decision gate. Preserve the accepted desktop baseline when a mobile-only problem is under audit. Separate GO needed for edits and deployment.
