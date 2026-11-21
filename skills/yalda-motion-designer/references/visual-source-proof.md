> **v0.4.0 PROFILE GATE:** This six-render proof applies ONLY to the explicitly authorized `3D-SOURCE-CONTINUITY` production profile. For R4 `IMAGE-FIRST-HYBRID`, preserve R1 images and audit actual layer registration/viewport continuity instead. Do not demand new Blender renders for R4. See `profile-selection-and-r4-image-first.md`.

# R3 visual and geometry proof gates — v0.3.0

Historical incident (not universal current defect): R3 42-frame prototype met byte/count caps but resembled simplified R2; static A/B proofs were edits of R1 screenshots, C was a stacked collage of 09/10/12, not a new single-source 3D render. Treat these as regression candidates for the next build.

## Mandatory pre-mass-render checks
1. Distinguish `approved appearance reference` from `new renderer source` and `engineering source`. R1 screenshot edit/collage cannot PASS unified geometry.
2. Demand native editable scene/scene graph, deterministic renderer invocation, camera/config, reproducible A1/A2/A3 and C1/C2/C3 *independent PNG renders* from shared object IDs and scene transformations, not crossfades, screenshot crops or warps.
3. Verify native R1 material fidelity at matched angles: concrete texture, openings/strip proportions, asymmetric load arrows, translucency of layered iso-surfaces, distinct neighbor footprints/shadows, patch IDs/legend, SAFE representation.
4. Verify transition A and C at p = 0,0.5,1, compare screenshot vs source scene, object position/ID anchors and camera. One phase checkpoint per generated proof; no mass rendering before Owner explicitly approves the proof gate.
5. If actual geometric source/patch-to-SAFE map missing, label reconstructed scene CONCEPTUAL/UNVERIFIED; no fabricated numerical stress, settlement, Ks, patch IDs or SAFE data. Distinguish 'continuous geometry in conceptual renderer' from 'validated numerical model'.
6. Do not collapse distinct image proofs into a collage because of requested number of outputs; deliver separate source-native image files and optional comparison sheets.

Verdicts separately per image/stage: `VISUAL_OWNER_APPROVED`, `SOURCE_REPRODUCIBLE`, `GEOMETRY_CONTINUITY`, `ENGINEERING_MAPPING` with PASS / FAIL / NOT TESTED / BLOCKED. Do not let a pass in one imply others.
