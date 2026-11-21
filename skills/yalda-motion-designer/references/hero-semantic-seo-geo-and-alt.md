# v0.4.1 — Hero-specific semantics, image alt, SEO / GEO, and truthful scientific language

## Scope separation
This document governs ONLY the embeddable YALDA R4 hero. The main YALDA site has separate canonical/www/sitemap/hreflang and Windows/API license/handoff concerns handled by the main-site advisory Work. **Do not mutate `PUBLIC_BASE_URL`, operational API endpoints, redirect rules, canonical/hreflang/og:url/schema, sitemap or site editor** while working on R4 unless Owner separately approves a main-site source patch. No `www` bulk string replacement.

Relevant verified public guidance (consult current originals when implementing):
- Google Images alt: https://developers.google.com/search/docs/appearance/google-images
- W3C meaningful/decorative images: https://www.w3.org/WAI/tutorials/images/
- Google JavaScript lazy loading: https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading
- Google AI/search optimization: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
No SEO/GEO ranking promise; no keyword-stuffed alt or invented scientific validation.

## Each image's role determines accessible treatment
- Standalone meaningful `<img>`: nonempty localized image-specific `alt`; lead poster/primary scene includes one strong descriptive alt; do not recite the full product story inside each alt.
- Repeated crossfade/compositing layers (foundation masks, atlas, intermediary WebP, spring overlay): use `alt=""` and appropriate decorative semantics (`aria-hidden="true"` on wrappers if appropriate). Repeated images must not each announce the same scene.
- Functional image/link: label the ACTION, not merely decorative content.
- CSS background has no HTML `alt`; if it conveys meaning add semantic HTML/text equivalent, not a fake `alt` CSS property.
- SVG model: describe through `<title>`/appropriate accessible name when an actual informational image, not on redundant internal paths. Invisible preloads/decode test images are decorative.
- Every `<img>` has an explicit `alt` attribute, but empty is CORRECT for decorative. Retain no-js static visual + adjacent readable explanation for crawlers and users who cannot play motion.

## Asset descriptions — source-aligned candidate mappings, verify names/hash/current role
- `assets/safe-r1.webp`: `CSI SAFE foundation modeling workspace in the YALDA Soil Studio soil-foundation interaction workflow.`
- `assets/yalda-r1.webp`: `YALDA Soil Studio workspace for soil–foundation interaction and soil response visualization.`
- `assets/r1-foundation-cutout.webp`: `Three-dimensional concrete foundation with openings used in the conceptual YALDA Soil Studio SSI visualization.`
- `assets/r1-flow/stress.webp`: `Conceptual stress contours beneath the primary loaded foundation in YALDA Soil Studio.`
- `assets/r1-flow/settlement.webp`: `Layered conceptual soil response beneath a loaded foundation.`
- `assets/r1-flow/neighbors.webp`: `Main foundation with adjacent foundation geometry and surrounding soil-interaction fields.`
- `assets/r1-flow/interaction.webp`: `Conceptual intensified soil stress field around a foundation affected by neighboring foundations.`
- `assets/r1-flow/patches.webp`: `Color-coded patches on a foundation for patch-based soil spring representation.`
- `assets/r1-flow/springs.webp`: `Color-coded foundation patches and spring elements under the slab.`
- `assets/r1-flow/plan.webp`: `Two-dimensional colored foundation patch plan for conceptual spring mapping to CSI SAFE.`

These describe *content*, NOT engineering provenance. Some of these files are layers and should actually use `alt=""` if the scene already has one meaningful summary. The accessible hero description belongs in semantic HTML; NEVER force all asset alts to be nonempty.

## Approved initial semantic companion content (FA/EN; editorial, not scientific validation)
EN: `YALDA Soil Studio presents a visual workflow for soil–structure interaction (SSI) and soil–foundation interaction. Explore bringing foundation geometry from CSI SAFE into YALDA Soil Studio, selecting a reference load combination, visualizing conceptual soil response and adjacent foundation effects, generating patch-based soil spring representations, and mapping springs back to CSI SAFE.`

FA: `نرم‌افزار YALDA Soil Studio یک گردش‌کار تصویری برای اندرکنش خاک و سازه (SSI) و اندرکنش خاک و فونداسیون ارائه می‌دهد. این نمایش مفهومی، ورود هندسهٔ پی از CSI SAFE، انتخاب ترکیب بار مرجع، نمایش پاسخ خاک و اثر پی‌های مجاور، ایجاد پچ‌ها و نمایش فنرهای بستر و بازنگاشت آن‌ها به CSI SAFE را معرفی می‌کند.`

Keep content meaningfully visible near the hero (not hidden SEO spam); `SSI` expands to `Soil–Structure Interaction`, NOT `Soil–Foundation Interaction`. Product terms where accurate: `YALDA Soil Studio`, `SSI`, `soil-foundation interaction`, `subgrade modulus`, `soil springs`, `adjacent foundation effects`, `CSI SAFE integration`. Do not insert all terms into every alt or caption. A visual demo does not prove live computation or API success.

## Four-page localization and shared-canonical discipline
Targets: `/fa/`, `/en/`, `/fa/products/soil-studio/`, `/en/products/soil-studio/` at canonical `https://yaldaeng.ir` if main site approves this origin. This is a **main-site decision** and R4 must NOT change canonical meta or redirect behavior itself.
- The component should not inject a second `<h1>`, canonical, alternate hreflang, og:url, title, site-level schema, robots directives, or sitemap entries; host page owns them.
- Keep semantic copy in host-appropriate heading/body structure and language; FA descriptions Persian, EN descriptions English. Owner-approved 7 cinematic captions are English; do not invent final FA caption translations without approval.
- `SoftwareApplication` structured data can be prepared as integration notes only; avoid duplicate entities and fabricated prices, ratings, compatibility, capabilities or test outcomes. Site team owns actual JSON-LD merge.
- Canonical www and operational application communication are unrelated. Never adjust Windows/API handoff, license/orders, payment, admin or notifications in a hero-only patch.

## Validation
Use `scripts/audit_hero_html.py` on assembled local HTML as an initial syntax check (presence of alt on all img, risks), then visually/semantically inspect actual DOM, non-JS fallback, ARIA, FA/EN content, duplicate headings/schema with *real host wrapper* and indexed-content behavior. Script alone cannot verify descriptive accuracy or SEO rankings. Use actual Search Console/Bing only when authorized and available.
