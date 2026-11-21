# R4 Visual Timeline v1 — authoritative contract (source-aligned)

## Runtime implementation examined
Derived from R4's `src/motion-timeline.js`, `src/common-rail.js`, `qa/editor.js`, `motion-timeline.json` in the 2026-11-18 Motion Refinement package. This is a **documented observed implementation**, not a new engine and not a claim that current cinematic output is Owner-approved.

### Exact input schema
Root: `{ "version": 1, "elements": { "id": {"label": "...", "space": "stage|workspace|foundation", "chapters": {"00": {"interpolation":"smoothstep|linear", "keyframes":[{"p":0,"posX":500,"posY":500,"opacity":1,"scale":1}], "compact": [ ... optional same objects ] }}, "text": {"lang":"en|fa","content":"..."} (optional **only when space=stage**) } }, "rail": { ... optional } }`.

- IDs match `^[a-z][a-z0-9_]{1,49}$`; stable, human readable, no renaming without migration.
- Chapter IDs currently `00`–`07`; p is **chapter-local** `[0,1]`, not global Hero position. Global chapter routing is a separate mapping; changing a chapter scroll span must not shift local keyframes.
- Each keyframe contains exactly five finite fields: `p`, `posX`, `posY`, `opacity`, `scale`. Sort by p; identical p is invalid. At least one keyframe/track. Opacity `[0,1]`, scale `[0.05,4]`; current runtime clamps X/Y to `[-10000,10000]` rather than rejecting huge values. The audit should call out suspicious extremes even if accepted by runtime.
- `linear`: constant speed between adjacent keys; `smoothstep`: eases to zero velocity at both keys. Do not add a smoothstep at **every** sub-keyframe of a continuously scrolling window, or repeated undesired stops result. A fixed common rail normally uses linear, while fade/reveal may use smoothstep.
- Before the first/after the last keyframe, the runtime holds the endpoint. No time-based autonomous animation is implied.
- `compact` is an optional responsive keyframe array for width ≤600px; when absent, the runtime uses desktop keys; do not mistake emulated mobile viewport for an actual phone test.
- Neutral fallback when element lacks track: `posX=0,posY=0,opacity=1,scale=1` for evaluation; **not necessarily invisible** — require explicit track and visibility control to avoid accidental element display.

### Coordinate spaces, origin and real pixels
- `stage`: origin top-left of 1000×1000 logical stage; shell `posX/Y` refers to its **top-left**. `posY=Y_logical*(stageHeight/1000)` and X similarly. Chapter-specific rail can override a shell's effective Y.
- `workspace`: 1000×1000 logical coordinate **inside the application model viewport**, element coordinates normally refer to foundation **center**. Fit/rendered bounding box matters. Workspaces depend on safe/yalda shell bounding boxes; UI sidebars and bars are excluded.
- `foundation`: 1000×1000 logical coordinate **relative to foundation**, for loads, bubbles, patch/spring layers. These inherit foundation transform. Avoid double-applying YALDA window translation or scale.
- A cross-window transfer must have one visual subject, a documented temporary stage-space bridge, then attachment to the destination workspace with coordinates transformed at handoff. No teleport, duplication, partial disappearance or UI coverage.
- Do NOT compare `posY=500` and a browser screenshot Y-pixel as if they were the same unit. Log logical coordinates, transformed CSS pixels, element bounding boxes and chosen viewport.

### Source of truth / parent-child controls
- One authoritative pose per element/property. A follower such as `yalda_window` may be derived from `safe_window_in` via the **common rail**. The editor must show whether field values are a driven result; edits to a follower must update the authorized driver or relative offset deterministically. An apparently editable control whose value is ignored is a FAIL.
- Shell motion: validate `Y_y(p) − S_y(p) = actual SAFE shell height + approved gap` during entry, and that `dY_y/dp ≈ dS_y/dp` for corresponding steps. Exit likewise YALDA→outgoing SAFE. Never mask bad rail geometry using z-index, opacity or clipping.
- `safe_window_in`, `yalda_window`, `safe_window_out`, `foundation`, `foundation_3d`, `loads`, `stress_field`, `neighbor_pads`, `neighbor_stress`, `patch_surface`, `springs`, `text_*` are current/expected identifiers, but inspect current source instead of assuming they all exist.

### Visual Editor acceptance
- `preview.html?qa=1` must show REAL scene, not disconnected diagram. Select chapter, element, viewport; scrub p; edit X/Y/opacity/scale; add/update/delete keys; see computed value and physical px; compare default/compact; enable guides; JSON Import/Export and Reset.
- Export/import must reproduce poses, `rail` config, responsive tracks and text content. Unsupported fields must fail loudly or be explicitly documented; no silent loss. Browser download may be unavailable, so JSON copy should work and filename/encoding be clear.
- Test sample: `yalda_window` at chapter00 p=.20 (X=0,Y=125), p=.30 (X=100,Y=136), interpolation linear: midpoint p=.25 => X=50,Y=130.5 **only if the current rail driver/overrides allow direct motion**. Distinguish editable/raw vs effective driven pose.
- Editor preview direct slider input bypasses scroll inertia and never alters public display unless the owner exports and explicitly approves integrating the config.

### Cross-chapter identity
- The same caption or foundation can span chapters. Preserve element identity across chapter boundary and match end pose/opacity/scale to next chapter's first pose; if an intended cut exists document it as such.
- The v1 data schema is not a full text storyboard engine. It has only simple stage-space HTML text; cross-chapter persistence and relative-to-rail anchoring require explicit runtime coordination. Do not claim these advanced behaviors solely because the JSON contains a text element.

### Static validation vs visual truth
Use `scripts/validate_visual_timeline.py` for schema/continuity diagnostics. It does **not** calculate real CSS layout, last-presented frame, media readiness, actual editor behavior, text readability or engineering correctness. Real-browser screenshot comparisons and user review remain mandatory.
