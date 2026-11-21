# Browser validation protocol

## Priority matrix
- Browsers: Chrome desktop + Chrome Android + Safari iOS + Firefox desktop; record exact versions and capabilities, not broad compatibility claims.
- Viewports: representative CSS widths 390, 768, 1366, 1920 as historical suggestions; record DPR and actual display refresh; one weaker real device.
- Network: cold cache, warm cache, constrained network (record throttle settings), error/offline and return-to-tab; disable and re-enable DevTools throttling consistently.
- Input: wheel slow/fast, trackpad, touchscreen, sudden reverse, direct jump via anchor/history, refresh at mid-scroll, resize/orientation/address bar.
- States: posters visible immediately, initial movement, four hard historical transitions, end exit, reduced motion alternative.

## Evidence capture
1. Export Network HAR (careful: may include private headers, cookies, tokens; sanitize). Inspect waterfall queueing, request priority, response bytes and cache behavior.
2. Capture Chrome Performance trace including Frames / GPU / screenshots / main thread; note recorder overhead. Mark red/yellow/green frames from trace, distinguish compositor and JS.
3. Record target/ready/shown telemetry in **an authorized isolated debug build** or via read-only inspection if possible. Never add instrumentation to source without GO.
4. For video, record `seeking`/`seeked` and `requestVideoFrameCallback` metadata: mediaTime, presentedFrames, processingDuration. Note callbacks are not strict real-time proof of display.
5. Screen-record user-perceived frame skip, preferably physical camera/real device when browser trace unclear. Attach short clip and reproduction steps.
6. Report p95 or max only when sample size, methodology, comparator and evidence are specified. Do not invent a universal acceptable fps number.

## Tool limitations
- Playwright screenshots: static snapshots may deliberately disable CSS animations; passing does NOT prove smooth actual playback. Use screenshot diff for reference visual states only.
- Playwright Trace Viewer: useful for actions/DOM/screenshots but not an equivalent substitute for Chrome compositor timeline.
- `requestAnimationFrame` counts application callback opportunities; not actual GPU presented frames.
- `PerformanceResourceTiming.transferSize=0` may mean local cache **or** cross-origin data unavailable without `Timing-Allow-Origin`; do not call it zero network cost without checking.
- LCP measures initial content; it is not equivalent to first scrub-ready frame, particularly with canvas.
- Simulator emulation cannot establish physical Safari/Android GPU/decoder behavior.

## No-pass rule
No acceptance PASS for (a) frame presentation without trace/video evidence; (b) mobile usability without real device or explicit constrained sign-off; (c) scientific truth without engineering source; (d) 'no frame drops' only from JavaScript data.


## v0.1.2 mandatory distinction
- `capture_scroll_paths.mjs` collects Playwright HAR, screenshots and a sampled input trail. It is **not Chrome Performance tracing** and does not measure dropped GPU frames. Do not label the Playwright HAR `cold` without evidence.
- Chrome DevTools MCP `performance_start_trace` with `autoStop:false` plus `performance_stop_trace` can capture a raw performance trace; record the gesture between start and stop. If the MCP is unavailable, use Chrome DevTools Performance UI manually. Source: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md
- A plain browser screenshot/screencast is not automatically a continuous-frame or scientific geometry pass. Real-device iOS decode and Safari seek remain separate gates. See `browser-evidence-matrix.md`.
