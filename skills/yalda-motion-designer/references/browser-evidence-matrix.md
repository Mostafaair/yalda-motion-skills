# Device/browser/decode/seek evidence gates — v0.1.2

**Status:** Protocol, not proof that these tests were performed.

| Platform | Image element + `decode()` | Canvas `drawImage`/ImageBitmap | Video seek/reverse | Evidence required |
|---|---|---|---|---|
| Chrome Desktop | cold/warm, bounded N | main thread and compositor trace | GOP/keyframe variants | Trace, sanitized HAR, visual capture |
| Firefox Desktop | test separately | identify synchronous canvas stalls | seek and reverse | Performance profiler/manual capture; do NOT label Chrome counters available |
| Safari macOS | test separately | device decode/memory | seek/reverse | Safari Web Inspector capture and recording |
| iPhone Safari | **mandatory real-device gate** | memory pressure, orientation, background/foreground | low-power mode/seek correctness | device, iOS version, memory symptoms and recording |
| Chrome Android | reduced-powered real device | frame sampling and decode | reverse and fallback | device, browser, trace/recording |

## Concurrent image decode
- Bound concurrent `decode()` requests; benchmark multiple caps rather than hardcoding a Safari-wide value.
- A WebKit report (Bug 302801, **RESOLVED INVALID**) described memory pressure when decoding 20 4000x4000 images in parallel, not a universal cap. The engineer explained `decode()` may use natural dimensions rather than subsampled display size. Source: https://bugs.webkit.org/show_bug.cgi?id=302801
- Record decoded frame **dimensions**, in-flight count, working-set policy, eviction and whether the browser killed/reloaded the tab. Browser device memory is not proved by theoretical RGBA bytes.

## LoAF / dropped frames
- Long Animation Frames API is supplemental and currently Chromium-centered. A LoAF with `blockingDuration` is not itself a compositor dropped-frame counter. Firefox and Safari need their own instruments.
- Compare Chromium `FrameSequenceTracker` counters (when present) with DevTools Frames, `PipelineReporter`, renderer Main and user-visible recording. Never sum overlapping main/impl counters.
- For video, `requestVideoFrameCallback()` is useful but not a guarantee of on-time screen presentation. Compare `mediaTime`, `presentedFrames`, seeking/seeked and observed reverse.

## Network tiers, not claims about Iran
Start with three *declared test profiles*; use fixed settings for fair comparisons and record actual measured effective throughput/RTT, media bytes and repeat count. No fixed nationwide 'Iran speed' asserted, and no universal recommended load time without Owner approval.

## Required source evidence
- [WebKit decode report](https://bugs.webkit.org/show_bug.cgi?id=302801) — device-specific observation, NOT standard.
- [Chrome LoAF](https://developer.chrome.com/docs/web-platform/long-animation-frames) — optional API.
- [Chromium jank debugging](https://chromium.googlesource.com/chromium/src/+/main/docs/speed/debug-janks.md) — tracing protocol.
- [ScrollyVideo](https://github.com/dkaoster/scrolly-video) — implementation claims; device testing required.
