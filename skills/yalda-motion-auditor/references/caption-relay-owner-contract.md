# v0.4.1 — Owner-approved continuous caption relay (R4, 2026-11-19)

**Scope and priority:** This reference overrides the *wording and choreography examples only* in v0.4.0 `cinematic-text-and-typography.md`. It does not change R4 Visual Timeline JSON v1 schema or authorize source edits. Obtain exact current source hash and latest Owner GO before doing any Work.

## Exact Owner-approved English captions (not alternative copy)
| Stage | Exact text | Attachment and choreography |
|---|---|---|
| 00 | `Bring Your SAFE Foundation into YALDA Soil Studio` | Anchored to moving foundation, above model; enter from right and travel downward WITH foundation; exit left as foundation lands in YALDA. Owner accepted chapter00 local p=0.52 placement, DO NOT MOVE FOUNDATION to fix a caption. |
| 01→03 | `Choose the Reference Load Combination` | One stable caption ID across 01 and 02, continuing into 03; from left, readable during 2D→3D and load arrows; exits left from mid-03. Avoid a blank Chapter 01. |
| 04 | `Apply Adjacent Load Effects` | Owner-indicated open scene zone, small→large→hold→small, in sync with neighboring pads and stress contours. |
| 05 | `Generate Patch-Based Springs` | small→large→hold→small; overlap with end of 04; avoid colored patch/spring geometry. |
| 06 | `Converting the 3D Response...` | Exactly this text INCLUDING three periods; joins 05 to 06, restrained translation/fade during flattening, not an unrelated new scene. |
| 07 | `Remap Springs to CSI SAFE` | Follows foundation transfer downward; enter before 06 completely disappears. |
| Final in SAFE | `Spring Mapping Complete` | Appears inside final SAFE composition after handoff; remains readable at exact endpoint; on reverse returns to 07 caption. This is a CONCEPTUAL screen caption, never a claim of successful live API write. |

No spontaneous copy substitutions or invented Persian translations. English copy is approved; FA translated cinematic headings require separate Owner acceptance. FA/EN semantic descriptions can be localized by authorized site integration.

## Relay contract — zero meaningful captionless hero intervals
- Start with a readable caption in the first meaningful composition; stop with the final caption still readable at the settled end. Never create a long no-caption Chapter 01 or Chapter 06.
- Drive all captions from the SAME effective scene progress (`displayProgress` for normal playback, exact owner QA value when scrubbing); do NOT use wall-clock timers that advance while scroll is stopped.
- Next caption begins while predecessor remains visible; use a bounded overlap and ensure no readable blackout. Owner-requested uninterrupted guidance means visual coverage **while the hero is onscreen**, not that unrelated portions of the host page should display captions.
- For pass/fail, sample the FULL global hero progress densely, including .999/next .001 chapter boundaries and responsive layouts. Opacity alone is insufficient. Check rendered text rectangle within viewport and hero, actual occlusion by model/UI, contrast, clipping, and absence of duplicate readable headings.
- Suggested numerical *preflight* thresholds only: steady readable caption effective alpha >= .65; brief handoff >= .30, but BOTH must have meaningful visible glyphs in actual Chromium. These thresholds are not a substitute for visual/accessibility review. Do not manufacture PASS by placing text offscreen, behind foundation, or with aria-hidden.
- Different chapter spans may change. Keep local chapter p, global timeline mapping and scroll allocation distinct. Preserve existing accepted +~20% distance in 04/05; do not multiply that extension again without Owner GO.

## Attachment/ownership rules
- `foundation`-bound headline: its Y follows foundation's actual projected position, even during SAFE→YALDA bridging; no double-counting common rail. Offset above footprint is visually verified; moving model must not erase text during reading.
- `stage` caption near scene window: offset follows chosen window/rail explicitly and respects frame movement. Do not accidentally pin to browser viewport.
- Cross-chapter stable text IDs should survive chapter boundaries without jumps/duplicate DOM nodes. JSON v1 has only stage/workspace/foundation spaces; owner-approved code integration must implement any special parent anchoring, not claim that unsupported `parent` JSON fields work.
- Reversibility: same p/viewport gives same caption text, bbox, opacity, scale and anchor; rapid direction changes must not leave stale captions.

## Typography, readability, and legal font gate
- Frameless headline, high contrast and consistent Semibold styling; refrain from overlays covering SAFE menus, YALDA inspector, stress field, patch colors, foundation openings. Add subtle shadow to characters only if needed; no colored card boxes.
- Apple SF Pro Display may be used only on systems where installed/available under applicable terms. Do NOT distribute downloaded Apple font binaries in a public web bundle without a suitable license. Licensed Inter Semibold is a practical fallback; check actual computed font and glyph rendering on target devices.
- English headings have approved exact copy; preserve punctuation, capitalization and `YALDA Soil Studio`/`CSI SAFE` spelling.
- Reduced-motion mode: show coherent semantic static caption/text rather than a blank overlay. Screen readers should not repeatedly announce transient DOM changes; use readable non-animated description outside decorative visual layers.

## Evidence and blocker protocol
Produce caption coverage trace (visual samples + bbox + opacity + occlusion), per-caption entry/hold/exit contact sheet at desktop and mobile, reverse-scroll run, contrast/readability checks, no-gap coverage report and final SAFE view. `scripts/audit_caption_coverage.py` is a *data-level preflight* only. Label source, quantitative, browser, physical-device and Owner findings separately.
