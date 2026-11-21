# R4 — Common rail, narrative synchronization and event contract

## Accepted entry/exit intent vs measured gates
**Entry**: initial SAFE and YALDA windows translate upward together, equal speed, constant visible gap. YALDA enters from below, never slides behind SAFE. No whole-shell fade or z-order flip. The foundation begins transfer BEFORE YALDA fully fits; completes exactly when its **entire transformed bounding box** can fit in the usable YALDA workspace and in the intended visible screen. The Nov 18 Owner accepted local Chapter 00 p≈0.52 placement; it is a regression anchor for that baseline, not a hardcoded universal constant on resized devices. Freeze baseline SHA before changing it.

Checks at samples and near boundaries:
- `deltaShellY = yalda.top - safe.top`; compare against `safe.renderedHeight + gapPx` across p. Both windows must have matching displacement between any two p samples; assert gap nonnegative and no shell overlap.
- `destinationBBox ⊆ (YALDA workspace ∩ viewport)` at the agreed landing event; model can be anchored to YALDA after arrival. Avoid mixing the apparent SVG/Safe model outline top with the entire image box; report definition of the geometric anchor.
- If a new editor p row changes SAFE's rail, transfer completion and target bounding box must be recomputed from **current geometry**, not an independent stale fixed `.52` timer. Do not make the causal constraint circular: report `fitCrossing`, `entryEnd` and their discrepancy before changing either.
- Stage and shell positions should be sampled as transformed `getBoundingClientRect()` with fixed viewport dimensions, not just JSON value columns.

**Internal YALDA**: from accepted entry landing forward, narrative flows chapter01→02→03→04→05→06. Avoid dead p spans. Owner's current source chapters (00–07) may be split/merged only with GO; internal sequence must finish before the top of model reaches viewport top.

**Exit**: foundation top touches calibrated top threshold (the most recent Work baseline uses `exitTopPx=0`, historically 24px was a proposed visual threshold). This triggers departure toward a **new** lower SAFE window. Output rail shares speed with YALDA, and `lowerSafe.top - yalda.top` should remain constant once coupled. For Nov 18 R4 refinement reference, reported visible gap was ~50px desktop/~62px compact; re-measure the active build. No new SAFE until the trigger; verify it is readable on entry and the model/patchs transfer is conceptual unless actual API proof exists.

## Chapter events / visual flow
- Ch00: raw 2D SAFE → YALDA, two shells at original R1 fidelity, one foundation, anchored after fit.
- Ch01: 2D→3D using R1 image identity. Previous double footprint is an OPEN **regression candidate**, not a current fact without screenshot.
- Ch02: load groups emerge, original nine R1 groups intact; no stress until Chapter03.
- Ch03: zoom main foundation and drift upward as bubbles grow (a prior accepted prototype used +16% scale); aim continuous center/scale at Ch02 boundary.
- Ch04: zoom back to reveal N2/N3/N4; conceptual main central field grows/warmens, visual +25% **not a physical calculation**. Prior Owner requested approximately 20% longer scroll span for Ch04 (as a design target).
- Ch05: fade neighbors/neighbor fields; refocus main concrete slab; progressively wipe/reveal aligned patch colors and then springs. Previous left-side patch protrusion is a regression candidate; check registration (image alignment and visible mask).
- Ch06: model rotates/flattens into 2D plan; never show two displaced slabs simultaneously.
- Ch07: YALDA to second SAFE, when top-of-model trigger is met, handoff starts without waiting zone. Caption follows transfer down.

## Scroll-length allocation vs animation speed
- Distinguish `chapter.localP`, `chapter.scrollSpanPx`, `globalHeroP` and **actual wall time**. User scrolling controls time; giving Ch04/05 +20% more scroll distance improves reading opportunity but does not guarantee seconds of reading for a fast scroller. Avoid autonomously continuing if the user stops. Do not change the original accepted entry geometry to rescale downstream chapters.
- A floating headline must have ENTRY / HOLD / EXIT ranges explicit in local p. When chapters are rescaled, local caption p ranges remain stable. Cross-chapter captions retain identity and do not flash/reload at chapter boundary.
- Smoothstep for opacity/scale; linear for continuous rails or align slopes across boundaries to prevent stopping every new keyframe.
- Remove dead zones and abrupt discontinuities; test at `p=0.9999`, `1.0`, next chapter `0.0`, `0.0001`.

## Correctness first; no new physics
Even if the stress field is conceptually visually intensified, do not claim quantitative soil stress, Boussinesq solution, Ks or load redistribution without verified numerical models. Mark CONCEPTUAL / UNVERIFIED rather than hiding in tiny text.
