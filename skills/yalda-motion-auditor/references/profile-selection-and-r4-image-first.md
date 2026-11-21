# v0.4.0 — Choose the rendering profile BEFORE design/audit

## Protocol scope
This is a required decision for **both** Designer and Auditor. Name the profile and source hash in each report:

- **R4-IMAGE-FIRST-HYBRID (current YALDA official hero):** 12 approved R1 WebP images and authentic SAFE/YALDA application chrome are immutable source references; compositing, independent model layers, protected UI regions, CSS/JS keyframe tracks, source-preserving crop/atlas/masks, carefully controlled reveal, zoom, pan, viewport anchoring and HTML typography are appropriate. **DO NOT demand six Blender-generated frames** or a newly reconstructed 3D world to accept an image-first sequence. Acceptance is visual continuity, source fidelity, scene correctness and browser evidence. Never claim original images are engineering computation proof.
- **3D-SOURCE-CONTINUITY (optional only with explicitly selected Owner GO):** a reproducible scene/camera/patch mapping and six-frame intermediate-render evidence is mandatory. Existing `visual-source-proof.md` and `validate_six_frame_proof.py` apply only here and remain available for future 3D missions.
- **VIDEO/IMAGE-SEQUENCE:** apply existing image/video frame, codec, decoding, frame-fallback and media-budget protocols. Do not silently convert a 12-image hybrid into hundreds of frames.

If the task mixes profiles, label each element/transition and its evidence independently. A technical PASS in one profile is not permission to change another profile or deploy.

## R1→R4 provenance and image-first policy
- Root reference: `08_YALDA_HERO_STAGING_20261104.zip`. Inventory and independently hash each of 12 original keyframes and source code (`src/hero.js`, `src/hero.css`, `hero-section.html` where present). The historically recorded 12-image encoded budget is ~13.944 decimal MB; recompute actual bytes from the owner-supplied archive rather than treating history as a measurement of the current build.
- Preserve native application UI/menus/inspector and pixel fidelity. Split **shell** / **model viewport** / **transient transfer layer** / **loads, stress and neighbor effects** / **patch, spring, planar output** / **HTML captions**. Keep source files byte-identical. Every derivative gets its own provenance and hash.
- Valid R4 motion may be image-layer crossfade, camera-like scaling, reveal, selective matte, scene-space translation and layer compositing. Using masks to reveal original source content is acceptable; **using whole-shell opacity, z-index flips or clip-path to conceal an incorrect layout is not**.
- Never allow dissimilar 2D and 3D footprint geometry to show as double slabs during crossfade. Use source-image registration/one-dominant-source transition or explicit conceptual staging. No false physical equivalence, patch assignment or real SAFE API success.
- Original approved visual fidelity and provenance outrank artificial 3D reproducibility or arbitrary frame count. If 2D↔3D or patch↔plan cannot be registered, classify VISUAL HOLD and preserve the good images.

## Canonical chapter inventory — conceptual narrative, not pre-approval
00: raw 2D foundation in SAFE → YALDA; chapter-00 landing at local p≈0.52 is **Owner-accepted** for the Nov 18 R4 baseline only. 01: 2D→3D (historically misregistered, regression candidate). 02: asymmetric load groups (nine original R1 groups). 03: zoom and soil-stress field. 04: zoom-out, neighbors and central field intensification (visual/conceptual, not measured numerical change). 05: concrete→colored patches→springs. 06: perspective→plan, no duplicate geometry. 07: transfer to outgoing SAFE. Chapter IDs and future edits are Owner-controlled; do not infer completion from their presence in source.

## Owner governance and retention
- A chapter is accepted ONLY if Owner explicitly accepts it. Keep source and cinematic acceptance separate.
- No R1/R2/R3 replacement, staging, production, future chapter production or changes to license/payment/site source without their own Owner GO.
- Preserve v0.3.0 checkpoint, work-budget and media-budget tools. Owner-accessible ZIP+SHA is required before expensive next phase, not just an unshared temporary path. No implicit Work quota access.
