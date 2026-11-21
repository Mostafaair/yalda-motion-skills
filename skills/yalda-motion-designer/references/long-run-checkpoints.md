> **v0.4.0 efficiency:** checkpoint per meaningful and expensive phase, NOT per individual Keyframe, edit, screenshot or frame; snapshots must remain Owner-accessible, verifiable, scoped to approved budget. For short read-only audits package once at completion if no long-running risk.

# Long-horizon checkpoint and recovery contract — v0.3.0

## Provenance: copy the PATTERN, not source code

## Owner rule / WORK LIMIT INCIDENT
A Work usage reset/context cutoff may happen without warning. Neither this Skill nor a local snapshot can guarantee restoration if the environment is discarded. **Every expensive phase must yield an Owner-accessible portable ZIP, hash and resume note.** A generated ZIP inside a Work container is only `LOCAL_CHECKPOINT_ONLY`; Owner-accessible delivery is a separate, observable step.

## Required procedure BEFORE work
1. Lock exact Owner GO, source baseline SHA-256 and excluded paths. Choose an isolated writable workspace (not R1/R2/production). Set a human-readable `run_id` (e.g. `r3-6frame-20261110`).
2. Define small milestones with one verifiable deliverable each. Before costly work, save a plan, status and source inventory; do not wait until the final ZIP.
3. Run `python scripts/checkpoint_manager.py init --workdir WORKSPACE --run-id RUN-ID` from the Auditor or Designer package. Reuse existing state on resume; NEVER reset or overwrite previous checkpoints.
4. To make a checkpoint, save current source/results/tests/report files inside WORKSPACE, then run:
   `python scripts/checkpoint_manager.py save --workdir WORKSPACE --phase-id geometry-locked --label PARTIAL --include src --include reports/geometry.json --note 'Geometry source indexed, visual QA pending'`
   The snapshot tool rejects links/traversal, writes a self-contained ZIP plus SHA-256 and an atomic `.yalda-motion-state/progress.json`.
5. `python scripts/checkpoint_manager.py verify --workdir WORKSPACE` must PASS. **Immediately make checkpoint ZIP available to Owner** via a supported conversation attachment or Library file, include SHA-256 and `progress/resume` summary; verify its accessibility. `receipt` can record an external reference but is always `REPORTED_UNVERIFIED` until independently observed. Do not mark durable if owner did not get a valid file.
6. Repeat after EACH phase and EACH expensive shard (e.g., a critical frame or renderer change), before any context compaction/change, before high-cost batch rendering, and whenever interrupted. If export is unavailable, STOP rather than risking further uncheckpointed work.
7. On resumption read `progress.json` and checkpoint manifest, run `verify`, restore in a NEW empty directory using `restore --number N --to RESTORE_DIR`, re-validate dependencies and previous pass gates. Never infer status from scattered filenames; never re-run costly phases already proven complete.

## Mandatory state report at each checkpoint
- owner GO/scope, latest known source ZIP and SHA-256, phase done/next, actual files and verification, tests PASS/FAIL/NOT TESTED, budget ledger status, unresolved blockers, required Owner decisions.
- **external_delivery_status** must distinguish `LOCAL_ONLY`, `REPORTED_NOT_VERIFIED`, `OWNER_ACCESSIBLE_VERIFIED`. The last is a human/evidence statement, never reported by the checkpoint script.
- If no trustworthy external copy, the process remains **RECOVERY_UNVERIFIED**. Do not promise that Work session state will be retained.

## Limits of scope
Scripts create snapshots only under `.yalda-motion-state/` in an explicitly chosen workspace; they do not modify product source, auto-upload, deploy, create a Git remote, or grant write access. Never copy secrets/log credentials into ZIP: pre-screen selected paths; protect user privacy. Checkpoint archives may contain proprietary code. Any upload/deployment still needs authorized destination and Owner GO.
