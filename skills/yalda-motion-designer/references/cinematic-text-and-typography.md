# R4 — Cinematic text / HTML captions, not UI labels

## Visual type system
- Captions are HTML, not embedded into WebP. Cinematic, frameless, bold, high-contrast and semibold typographic styling; visual anchor must follow moving scene/rail, not inadvertently fixed to browser viewport. Text-safe zones cannot obscure foundation openings, load arrows, intense stress cores, important patch colors, UI menus or inspector. **No rectangular card/border/background panel** unless Owner overrides.
- Owner requested **SF Pro Display Semibold appearance**. Apple SF Pro license should be consulted; downloaded Apple font binaries are **not automatically licensed for public web hosting or redistribution**. Prefer system font where legally provided and a licensed webfont such as Inter SemiBold otherwise. Do not package Apple font binaries in Skill ZIP or website. Log `getComputedStyle().fontFamily` *and* visually verify fallback rather than assuming CSS naming proves actual glyph font.
- Desktop suggested headline size around 42–54 CSS px and mobile ~26–34px, adjusted via `clamp`, responsive lines and reading width. Use a subtle text-shadow for contrast, never glowing blobs that defeat clarity. Semantic text with heading/p elements, ARIA only as needed, RTL/LTR support, respect reduced motion.

## Exact proposed content and choreography — Owner-editable, not mandatory finished copy
- Chapter00 `Import Foundation from CSI SAFE`: from outside RIGHT → near SAFE/YALDA seam while both shells translate in common rail → outside LEFT; keep its relative Y tied to shell rail. Prior proposed local spans `enter .08–.22`, `hold .22–.48`, `exit .48–.68`.
- Chapter02 through early Chapter03 `Select Reference Load Combination`: from LEFT, hold across chapter boundary as nine load groups emerge, exit LEFT during Chapter03 `.50–.82`. Stable ID; no blink at chapter boundary.
- Chapter04 `Apply Adjacent Load Effects`: pop **small→large→hold→small**, not a fixed panel; centered in Owner-marked empty region under neighbors. Prior proposed `grow .08–.28`, `hold .28–.62`, `shrink .62–.92`, scale ~.65→1→.65.
- Chapter05 `Generate Soil Patches & Springs` (preferred; alternate `Calculate Patch Springs`): same grow/hold/shrink, after Ch04 caption has receded, with patches then spring visibility. Prior proposed `grow .10–.28`, `hold .28–.64`, `shrink .64–.90`.
- Chapter07 `Transfer Springs to SAFE` (alternate `Apply Springs to SAFE` if Owner product vocabulary requires): upper region, attached to visual handoff, travels downward with model, fades before final SAFE state.

These **wordings and p ranges are recommendations for Owner review**. Check owner-approved strings and current source before modifying. Captions need a documented source of truth and cross-chapter persistence. Do not mistake a static `text.content` field plus p track for automatically supporting parent-relative anchoring; verify the implementation.

## Readability and actual exit direction
- For LEFT entry, prove `element.right <= stage.left` at first invisible position, then center inside intended text-safe zone during hold, then `element.right <= stage.left` again. For RIGHT entry, prove `element.left >= stage.right` both outside points. `opacity:0` while still geometrically inside is **not** sufficient proof of a genuine side entry/exit.
- For scale caption, record actual bounding rect and CSS transform origin. Avoid shrinking about the incorrect window corner, offscreen anchors, large blur or fade that makes text unreadable. Hold duration is **scroll distance**, not guaranteed seconds: test slow/medium/fast scrolling and if needed increase chapter scroll allocation without forced autoscroll.
- Contrast test against moving bright SAFE screenshot and dark YALDA frame. Handle overlap, long translated strings and mobile overflow; use actual screenshots at entry/hold/exit.

## Caption audit gates
For each caption: ID, chapter(s), exact copy, direction/scale style, anchor parent, logical coordinates, CSS pixel box, p ranges, reading distance in scroll pixels, screenshot at three phases (desktop/compact), reduced-motion static fallback, source/owner status. Text animation shares effective scroll progress; do not let timers expire when user pauses. Do not claim a font is embedded or licensed without evidence.
