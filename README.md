# YALDA Motion Skills

**Two portable Agent Skills for source-faithful cinematic scrolling and evidence-based motion QA.**

- `yalda-motion-designer`: plan/implement explicitly authorized scroll stories using Image-First Hybrid, JSON Visual Timeline, common-rail windows, caption relay, bounded momentum and budgeted checkpoints.
- `yalda-motion-auditor`: independently audit motion/geometry, image integrity, media loading, frames, accessibility, mobile readability, browser performance and reproducibility. **Read-only by default.**

## Install

This repository follows the [Agent Skills specification](https://agentskills.io/specification). Copy **each skill folder separately**, retaining its `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/` directories, into a skill directory supported by your agent environment. For Codex-based environments, consult your product's current skill-loading documentation. An agent must explicitly **read** the relevant `SKILL.md` and references; merely attaching a ZIP does not prove skill usage.

```text
skills/
  yalda-motion-designer/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
  yalda-motion-auditor/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
```

## Quick checks

Scripts use Python 3.10+ and the Python standard library, except optional external tooling like `ffprobe` for video metadata. They analyze files locally and do **not** auto-deploy or create imagery.

```bash
python skills/yalda-motion-auditor/scripts/validate_visual_timeline.py --help
python skills/yalda-motion-auditor/scripts/audit_caption_coverage.py --help
python skills/yalda-motion-auditor/scripts/analyze_har.py --help
python -m unittest discover -s tests -q
```

## What makes this different?

1. **Immutable image sources**, instead of automatically replacing accepted engineering graphics.
2. **Visual Timeline v1** with stable IDs, local chapter `p`, `posX`, `posY`, `opacity`, `scale`, and `stage / workspace / foundation` coordinate spaces.
3. **Common-rail choreography** so multiple software windows translate coherently.
4. **Caption handoff with real readability checks**, not opacity-only PASS.
5. **Bounded inertia** to the actual scroll position, reversible under direction changes.
6. **Evidence tiers**: source check ≠ local browser ≠ live hosting ≠ physical phone.
7. **Checkpoint/cost safety**: a local checkpoint is not a durable owner-accessible delivery.

**This repository contains no proprietary R1 images, website/application source, secret credentials, downloadable Apple fonts or production server configuration.** Example JSON and browser logs in `assets/` are marked as synthetic or not owner-approved.

## Publication and license status

The public-source license is **not yet selected by the Owner**. This repository is technically organized for public review and GitHub upload, but publishing does **not** automatically grant permission to reuse or redistribute its contents. Before advertising it as open source, choose and add a suitable LICENSE, and review provenance of the original source and references. See [PUBLICATION_CHECKLIST.md](PUBLICATION_CHECKLIST.md). No license has been invented on the Owner's behalf.

## Documentation

- [راهنمای فارسی](README.fa.md)
- [Technical Persian article for the YALDA site](docs/article-fa.md) · [CMS HTML fragment](docs/article-fa.html) · [SEO metadata draft](docs/article-seo.json)
- [Clean-up and standards audit](docs/PUBLIC_RELEASE_AUDIT_FA.md)
- [Evaluation scenarios](docs/evaluation-scenarios.md)

## Caveats

The Skills are *methodology, scripts and QA contracts*, not an SSI solver, SAFE API adapter, rendering engine or claim of certified engineering accuracy. Scientific field visualizations must disclose whether their data are conceptual or independently verified. Any source change or deployment is subject to the asset Owner's explicit approval.
