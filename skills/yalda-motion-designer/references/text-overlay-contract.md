> **v0.4.0 R4 SCOPE:** The current R4 `motion-timeline.json` v1 supports three actual element coordinate spaces and optional stage-space HTML `text` objects. The four historical overlay *concepts* in this document remain useful for design, but parent-relative captions across chapters require explicit browser runtime attachment and testing. See `visual-timeline-v1-contract.md` and `cinematic-text-and-typography.md`.

# Editable text captions, fixed and scroll-floating descriptions — Motion Overlay Contract

## Owner-facing content controls
Text content is **Owner-authored/approved**, not auto-invented promotional copy. Offer separate Persian/English strings per overlay, id, purpose, start/end normalized p, anchor, text width, alignment, visual design, reduced-motion version, responsive placement and enabled flag in a standalone JSON. Do not bake captions into 180/340 image frames: use accessible, selectable semantic HTML text under one canonical p timeline. Do not mistake media `<track>`/WebVTT (time-based captions for a `<video>` media element) for a deterministic scroll-bound narrative overlay.

## Modes (all in the same scrollytelling section)
1. `below_media`: **normal flow under scene/image**. Reserve vertical space to prevent overlap, let text wrap and remain readable at 200% zoom and 320 CSS px viewport. Do not absolute-position below and accidentally overlay the next section.
2. `within_stage_fixed`: pinned relative to the **story/stage**, not indefinitely fixed to whole viewport. Has p_start/end visibility. Pinned identity survives model animation; should leave with section.
3. `floating_scroll`: parallax or translate/opacity based only on the canonical p, reversible and deterministic; no perpetual bobbing, hover-only reveal or independent time tween.
4. `scene_anchored`: anchored to a **named world/scene object** (e.g. N2, patch ID) and projected using the *same* camera transform/model units as media; cannot be inferred from a flat screenshot. If 3D projection or consistent scene anchor unavailable, mark BLOCKED or use ordinary story/stage caption, never fake scientific association.

## Rendering/a11y/quality
- Text must be separate, semantic HTML (`<p>`, `<figcaption>` etc.) or equivalent with plain `textContent`, never unsanitized `innerHTML`; no baked screenshots and no duplicate hidden/visible content that confuses screen readers. Source localization FA `dir=rtl` and EN `dir=ltr`, logical CSS properties and real font fallback. Preserve accepted YALDA menu strings and software UI.
- Avoid covering key model features/SAFE transfer. Apply safe insets and max readable widths. Test iPhone/mobile, desktop, zoom 200%, 320 CSS px reflow, RTL mixed technical notation (Ks, SAFE, N2), contrast/visibility over stress colors, long text, disabled JS and failed media. Provide static informative alternative when `prefers-reduced-motion` is on; essential information must never disappear.
- `opacity`/`transform` are candidates for compositor-friendly transitions; pin/fixed elements and multiple stacking contexts may still cause paint/layout and occlusion. Test with browser trace. One p timeline; no wheel interception. If CSS scroll-driven effects chosen, feature-detect and provide supported fallback, test Safari and Firefox.
- Keep editorial captions optional by default. Previously approved requirement forbidding unrequested slogans or frame numbers remains. Enabling description mode needs Owner text approval; sample copy is NOT final.

## Validator
`python scripts/validate_text_overlays.py assets/text-overlays-EXAMPLE-NOT-APPROVED.json` checks schema, interval, languages, anchors, plain text/no HTML injection, reduced-motion validity and HTML-layer contract. A PASS is **structural only**; not a screenshot pass or guarantee of no overlap. A user can edit the JSON and validate it before Work integrates it.

## Sources
- MDN scroll-driven timelines: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations/Timelines
- Google Chrome scrollytelling: https://developer.chrome.com/docs/modern-web-guidance/guides/ui-behaviors/scrollytelling
- MDN CSS position/sticky: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position
- W3C WCAG Resize Text / Reflow: https://www.w3.org/WAI/WCAG21/Understanding/resize-text and https://www.w3.org/WAI/WCAG21/Understanding/reflow
- MDN time-based video track distinction: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/track

## Visibility synchronization with actual media readiness
Stage-specific captions and scientific callouts must not assert a new model state while `shown_p` belongs to an older scene stage. Compare target_p, ready/shown_p, stage_id and chosen fallback. Either hold the previous matching caption until the correctly corresponding frame is shown, or use an explicit neutral loading caption that is not a scientific claim. Never silently pair new narrative text with arbitrary stale frame; do not blank out all essential text. Keep a nonanimated full transcript/overview accessible outside visually transient layers so key information remains discoverable in read-only and reduced-motion experiences.
