# R4 — Bounded cinematic scroll momentum (optional; do not hijack page scroll)

## Owner intent
Fast wheel/trackpad input should feel like pushing cinematic imagery: visual content smoothly catches up through intermediate states. Slow scroll must be precise. Momentum must **never invent progress beyond actual scroll target** or autoplay extra chapters. Reversal should change direction promptly and a paused scroll should finish at the exact target. This is a visual tracking filter, **not** mandatory native wheel interception, content scrolling physics, random frames or smooth-scroll polyfill.

## Data model and single rendering clock
- `targetProgress`: derived solely from actual document scrolling, normalized against current measured scroll geometry; updated for layout/resizes.
- `displayProgress`: filtered position used by **all** shells, foundation, images, text, exit trigger, and other effects. No double smoothing on children. All meaningful geometry invariants must use consistent progress and current layout; define triggers in a stable geometric or target-progress mapping so filtered lag cannot create a broken handoff.
- For direct QA timeline scrubbing, keyboard seeking, browser restoration and `prefers-reduced-motion: reduce`, optionally set `displayProgress=targetProgress` immediately.

## One possible bounded filter (not mandated code)
`alpha = 1 - exp(-deltaTime / tau)`; `display += (target - display)*alpha` with `tau` chosen from measured input speed. Since `alpha∈[0,1]`, display cannot overshoot target for a fixed target. Use `requestAnimationFrame` delta time, not per-frame magic numbers. Near the target, snap exactly on convergence threshold with no accumulating fractional drift. Do not force constant velocity; avoid changing tau so aggressively that animation jerks when switching speed bands.

### Preliminary tuning for browser experiments, not Owner-approved constants
slow: tau ~40–80ms; normal: ~90–150ms; fast: ~150–240ms; after wheel release: ideally visually settled within ~300–350ms. These are **hypotheses to tune**, not guaranteed measured performance. Clamp maximal chapter-progress lag and large jumps; avoid seconds-long catch-up or slow-moving text after a fast scroll.

### Explicit invariants
- At rest and after settling: `displayProgress == targetProgress` within a documented epsilon; never exceed global scroll bounds.
- While target is fixed and filter is active, next display is between previous display and target; no overshoot.
- Direction reverse: previous positive momentum immediately yields to new target direction, no synthetic forward steps; if user drags scrollbar, jump/short-circuit lag to maintain accurate position.
- No independent caption timers: reading hold is tied to scene p; freeze scroll = freeze caption after settle.
- Do not run another smoothing layer in CSS transition, GSAP scrub, wheel library or child animation unless its combined lag is explicitly measured/approved.
- Touch/mobile usually already has native inertia. Avoid stacking full virtual-scroll interpolation. Reduced motion disables additional inertia/large travel; provide readable static text.

## Why "push several frames ahead" must be scoped
Browser-native scroll velocity can travel farther than one wheel event because of native momentum. The visual filter may traverse several states **up to** that actual scroll position and settle; it must not automatically leap an unrequested chapter. If Owner later wants true page-physics overshoot or snap-to-chapter that advances beyond actual scroll, require a separate GO and a dedicated safety/UX analysis.

## QA and evidence
Record (timestamp, actualScrollPx, targetProgress, displayProgress, mode, viewport, reducedMotion). A sample JS log alone does not prove display at compositor level; combine with DevTools/Chrome capture, screenshots and actual user interaction.
- Slow, medium, fast; rapid stop; immediate reverse; pointer wheel/trackpad; keyboard; scrollbar drag; touch emulation and real touch if available; resize; direct QA slider; reduced-motion.
- For every case: maximum lag in p and projected CSS px; settle time; target overshoot; reverse delay; jank/long frames; screenshot alignment of shell/model/caption; decoding/cache readiness. Label unsupported measurements NOT TESTED.
- Use `scripts/audit_scroll_momentum.py` on a log with the exact format in `assets/r4-motion-sample-SYNTHETIC.jsonl`. The script is strictly post-hoc and cannot assert real browser performance from synthetic fixture.

## References
- MDN Scroll-driven animation timelines https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations/Timelines
- GSAP ScrollTrigger API https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- W3C animation from interactions https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions
- Chrome guidance on transform/opacity https://developer.chrome.com/docs/modern-web-guidance/guides/ui-behaviors/scroll-entry-exit-effects
