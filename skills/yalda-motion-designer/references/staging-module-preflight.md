# Staging web module delivery and browser QA gates — v0.3.0

Observed historical R3 test: `.mjs` was served as `application/octet-stream` and browser showed just two initial posters. After Owner's scoped `.htaccess` fix, it ran. This is a **regression candidate** for future deployments, not an assertion about present site state.

Before saying `ready-to-deploy` for approved staging candidate: verify intended `index.html` is full sequence or explicitly 2-transition proof; all `.mjs`, `.js`, JSON, image and CSS assets exist and paths are correct; real browser Network and Console, MIME (`text/javascript` for modules), CORS/caching, errors, startup/reduced motion, both scroll directions, safe fallback; source hash parity; responsive mobile. A local static-file PASS does not prove server MIME.

No test QA URL, files, or server configuration may be changed without a specific Owner GO. Staging test is read-only; actual deployment separate GO. When server access is blocked, `NOT TESTED`, not success. Ask for browser evidence ZIP or use authorized read-only capture.
