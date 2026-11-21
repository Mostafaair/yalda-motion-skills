# Test matrix — evidence required, no false PASS

| Test | Desktop Chrome | Desktop Firefox | iOS Safari | Android Chrome | Evidence |
|---|---|---|---|---|---|
| Cold cache poster and first usable movement | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | Network waterfall + screen recording |
| 3G/4G constrained transfer (record exact shaping) | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | HAR and resource counts |
| Slow scroll; stage C0/C1 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | landmark frames |
| Fast scroll jump | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | target/ready/shown + trace |
| Reverse immediately after jump | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | target/ready/shown + video |
| Cache warm; mid-page refresh/history | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | recording |
| Missing frame / decode error | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | fault test + nonblank fallback |
| Resize, orientation, address bar | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | recording + p-state comparison |
| Reduced motion + keyboard | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | accessibility inspection |
| Compositor frame presentation | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | Perf trace/physical evidence |
| Scientific IDs/colors/contours | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | model/patch export + screenshots |
