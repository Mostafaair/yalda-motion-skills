---
name: yalda-motion-designer
description: Design or revise cinematic, scroll-driven engineering/product heroes using the YALDA Image-First Hybrid method, editable Visual Timeline keyframes, common-rail motion, readable caption relay, bounded scroll momentum, media budgets, and recoverable checkpoints. Use for visual storyboard, motion architecture and explicitly authorized implementation; never deploy without owner approval.
compatibility: Python 3.10+ for bundled validation scripts; browser/Playwright optional for actual visual QA.
metadata:
  version: "0.5.0"
---
# YALDA Motion Designer

Design cinematic scroll narratives without sacrificing approved imagery or engineering meaning. This is an **Agent Skill**, not a renderer, web application, or entitlement to change a site.

## Authority and source fidelity
1. Identify owner, exact asset/source version (prefer SHA-256), visual reference, device targets, and authorization scope. Without explicit authorization, output a **design or audit plan only**; never modify/deploy host code, SEO configuration, APIs, licensing, or production content.
2. **Choose a profile** before making media: `IMAGE-FIRST-HYBRID` reuses approved images and independent composited layers; optional `3D-SOURCE-CONTINUITY` requires an approved reproducible model/camera/geometry and new source proof. Do not impose six Blender frames on an image-first project. See [profile guide](references/profile-selection-and-r4-image-first.md) and [visual proof](references/visual-source-proof.md).
3. Engineering contours in promotional images are *conceptual unless verified against calculations*. Do not infer field values, patch identifiers, or SAFE API success from colors or screenshots. See [scientific integrity](references/scientific-integrity.md).

## Build the scroll narrative
1. Define named chapters, their visual start/end states, and accepted transition anchors. Save scene-source hashes and a motion contract before expensive iteration.
2. For Visual Timeline v1, use stable element IDs and **chapter-local progress** `p ∈ [0,1]`. A keyframe holds `p`, `posX`, `posY`, `opacity`, `scale`; choose `linear` or `smoothstep`. Distinguish `stage`, `workspace`, and `foundation` coordinate spaces. Never invent unsupported JSON fields. Read [Visual Timeline contract](references/visual-timeline-v1-contract.md).
3. Compose initial/final software windows with one **common vertical rail**, ensuring synchronized window speed, nonoverlap and measurable foundation containment. Do not repair trajectories using z-index/clipping tricks. Read [common rail](references/common-rail-and-chapter-choreography.md).
4. Keep editable HTML captions attached to their scene element and synchronized with the engineering event. Design **entry → readable hold → exit**, with a continuous but **noncolliding** relay. Opacity alone does not prove legibility. Read [caption relay](references/caption-relay-owner-contract.md) and [text overlays](references/text-overlay-contract.md).
5. Optional momentum is a **bounded smoothing of `displayProgress` toward scroll-derived `targetProgress`**, not synthetic chapter autoplay. Reverse immediately, settle exactly, bypass on reduced-motion/direct editing/touch where appropriate. Read [momentum](references/bounded-scroll-momentum.md).
6. Adapt mobile composition separately; do not simply shrink a desktop window. Protect accepted desktop imagery and local chapter mapping.

## Budgets, loading and quality gates
- Obtain **Owner-approved** total frame/byte/time limits *before* new media production; apply aggregate size across responsive tiers. Never invent the platform's remaining Work quota. See [media budget](references/owner-media-budget-contract.md), [work budget](references/work-budget-control.md), and [loading/frame gaps](references/frame-skipping-and-media-budget.md).
- For substantial work, checkpoint **after meaningful phases**, SHA-256 each snapshot, and ensure the owner can really retrieve it; local files alone may vanish. See [checkpoint protocol](references/long-run-checkpoints.md).
- Preserve image bytes; media readiness, `img.decode`, poster/fallback, reverse scroll, frame cadence, no horizontal overflow, caption collisions, alt/semantics and `prefers-reduced-motion` need browser checks. See [browser evidence](references/browser-evidence-matrix.md), [semantic hero](references/hero-semantic-seo-geo-and-alt.md) and [embed/staging](references/hero-embed-staging-and-outer-shell.md).
- Distinguish **source test**, **numeric test**, **local browser**, **hosted browser**, and **real device**. Never convert a lower evidence tier into a live/physical-device PASS.

## Use packaged scripts when relevant
Execute scripts explicitly from this skill's `scripts/` folder; optional `--report`/`--out` outputs require authorized workspaces:
- `validate_visual_timeline.py`, `validate_text_overlays.py`, `audit_caption_coverage.py`, `audit_hero_html.py`, `audit_scroll_momentum.py` — structural/log preflights, *not* visual acceptance.
- `media_budget_contract.py`, `configure_owner_budget.py` — planned/actual media caps; `work_budget_guard.py`, `checkpoint_manager.py` — local budget/recovery ledgers.
- `validate_six_frame_proof.py` — **only for explicitly approved 3D-source profile**, not image-first.
- Examples in `assets/` are **SYNTHETIC or NOT OWNER APPROVED**, never deployment defaults.

## Delivery
Provide source identity/hash, selected profile, scene/element timeline, before/after images when authorized, mobile and desktop evidence, measured versus inferred findings, budget/checkpoint receipt, accessible content and a table of `PASS / FAIL / NOT TESTED / BLOCKED`. Stop at the authorized gate; deployment requires separate explicit approval.
