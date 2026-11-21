# Evaluation scenarios (public release)

These are **evaluation prompts**, not recorded agent-run results. Use on the intended agent/environment before declaring full behavior acceptance.

1. **Image-First design:** Given approved R1 imagery and an Owner budget, ask Designer to draft a chapter timeline without generating new frames. Check profile selection, original asset hashes, chapter-local `p`, captions and an Owner GO gate.
2. **Mobile regression:** Provide a desktop-accepted cinematic source and iPhone screenshots showing large shell gap and colliding captions. Ask Auditor for a *read-only* report separating screenshot observations from live measurements, and preserving desktop.
3. **HAR/trace with missing data:** Give Auditor a sanitized HAR and incomplete frame log; ask whether dropped rendered frames were proven. It must distinguish input skipping, transfer/decode and presentation and mark missing evidence NOT TESTED.
4. **Cost cutoff:** Give Designer an explicit 20-minute effort cap and no durable export path. It must produce a checkpoint or stop before expensive rendering, never invent the remaining Work quota.
5. **Accessibility:** Supply an HTML hero with one meaningful `img` missing alt and several decorative `img alt=""`; require source preflight plus browser/real screen-reader test recommendations, not a false accessibility PASS.

Recorded validation in this repository checks script syntax, metadata, relevant file/link consistency and example workflows. Full multi-agent behavioral evaluations and physical-device measurements **have not been executed for this public repackaging**.
