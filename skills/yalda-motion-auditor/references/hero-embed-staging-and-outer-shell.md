# v0.4.1 — R4 CSS-only outer shell + embeddable mid-page component + staging readiness

## Immutable source visuals / visual-polish scope
R1 application chrome/screenshots and R4 WebP/SVG-derived technical imagery MUST remain byte-for-byte unchanged in this mission. Never rerender, recolor, brighten, filter, blur, add metallic gleams to, crop into replacement assets, recompress, regenerate models, or fabricate SAFE UI. Preserve hashes of old assets; only allow new files for HTML/CSS/JS/text/metadata and minimally necessary nonimage configuration when Owner GO permits.

Metallic visual treatment is **ONLY** on surrounding hero root, not inside image pixels or the software workspace. Prefer scoped CSS gradients on external root `background: #05080c` with graphite `#10171e`, restrained dark-blue `#19232b`, low-contrast edge highlight, subtle corner sheen; avoid massive `backdrop-filter`/heavy blur and image overlays. A viewer must identify the original R1 frame colors and materials unchanged.

## Embeddability, not another full-page microsite
Targets are middle of `/fa/`, `/en/`, `/fa/products/soil-studio/`, `/en/products/soil-studio/`. Need native component mount, not replacing the host `<html>`, `<body>`, H1, navigation or existing CSS. Avoid global CSS selectors (`body`, `h1`, `img`, `*` without scope) and global `window.onscroll` replacement. Keep host scrolling native; isolate event handlers; use idempotent `mount(root, {locale, assetBase, ...})` / `destroy()` contract (or tested equivalent). Support repeated mount/unmount and >1 instance if claimed. CSS stage dimensions must be computed **relative to component viewport/sticky area**, not assumed document origin 0. Native scroll plus local chapter progress mapping must work for a module placed below the fold.

Host owns SEO canonical, hreflang, sitemap, robots, JSON-LD and site API. Hero owns HTML captions, image alt/fallback and scoped visual background. Do not change operational routes, license intent handoff or billing. Asset URLs: base path explicit, avoid hardcoding www/staging/absolute preview paths; ensure .mjs served correct JS MIME when used. Offline poster/no-JS fallback needs visible product content. Avoid multiple h1 or hidden keyword stuffing.

## Integration QA gates
1. Isolated local component (with true WebP paths, source hash, CSS/JS) passes source/visual checks.
2. Render same bundle inside **four representative host wrappers** (FA/EN home/product); verify header, navigation, other site CSS, forms, scroll, footer, content length, LCP/CLS and iframe-free semantics.
3. Desktop, emulated mobile and physical phone are distinct evidence levels. Native wheel/trackpad/touch, reduced motion, keyboard, scrollbar, resize, JS-disabled fallback, direct timeline scrub and reversibility.
4. Verify blank frame avoidance, image readiness/decode/prefetch budget, R1 hash parity, timing/caption legibility, reduced motion and browser performance (measured, not guessed).
5. Host-level *staging* acceptance (only after separate GO for deploy) must test real URLs, actual MIME for `.mjs`, 200/404/403, robots/WAF constraints, cache headers, SEO tags, canonical conflicts, scroll at mid-page, mobile and rollback. Passing an `about:blank`/`file:` Chromium QA is NOT staged readiness proof.
6. Produce staging-ready ZIP, checksum, file-level diff, rollback, append-only integration instructions, and source manifest. `STAGING_READY_LOCAL` is distinct from `STAGING_HOST_VERIFIED` and `OWNER_APPROVED`. No deployment without explicit Owner GO.

## Owner gates / version policy
An existing Work run on v0.4.0 does not retroactively acquire v0.4.1 requirements or permission to modify the main site. Treat 0.4.1 as backwards-compatible skills guidance for NEXT authorized review or next Work iteration. If site package delivered before this addon, audit the gaps as open and propose only a new minimal scoped GO. Never corrupt the in-flight source package with a different unapproved baseline.
