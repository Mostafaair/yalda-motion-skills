# Symptom / competing hypothesis / first discriminator

| Symptom | First measurement | Possible causes | Test distinguishing them |
|---|---|---|---|
| 1→6 image jump | target/shown indices and p timestamp | intentional fast scrolling; missing decoded frame; scheduler stale | if target jumps and ready true, input skipping is plausible; if target stable and shown delayed, inspect readiness / trace |
| 400ms without log sample | sampled time gap, `RunTask`, LoAF, visibility | blocked main thread; hidden tab; sparse logging; decode workload | sample gap alone proves no underlying cause |
| Slow first poster | sanitized HAR, priority, image decode status | poster lazy loaded, heavy asset, request competition, TTFB | distinguish timing phases and verify real first-usable visual |
| Broken reverse | request/decode order, cache window and p | sequential prefetch, stale queue, memory eviction, video seek | reverse repeatedly under cold/throttled network |
| Smooth but worse R2 image | same-p screenshots, pixel dimensions, loss settings | resampling, chroma artifacts, geometry mismatch | compare contours/openings/patch colors and crop |
| Video late | seeking/seeked, keyframes, `mediaTime` callback | seek backlog, large GOP, range fetch | compare seek coalescing and encode variants on actual devices |

Test order, **not a claim of root cause:** unbounded eager loading → target readiness → priority/eviction → competing smoothing → decode/compositor. Always confirm current source/build.
