# Motion Contract schema v0.1.1

The JSON template is **synthetic**, not actual YALDA geometry. `scripts/validate_motion_contract.py` checks numerical *declared* C0 of landmarks in CSS px at declared viewport/DPR and camera position/look-at/projection in world units; optional declared C1 uses velocities `end_velocity_css_px_per_p` and `start_velocity_css_px_per_p` plus explicit `continuity_velocity_tolerance_css_px_per_p`.

Required keys: `contract_version`, `reference_build_sha256`, `geometry_source`, `units`, `coordinate_system`, `scientific_provenance`, `viewport`, `scene_object_ids`, `approved_checkpoints`, `continuity_tolerance_css_px`, `progress`, `stages`. Each stage has p interval, start/end state IDs, camera/geometry IDs, numeric start/end cameras and per-side landmarks.

Adjacent stage endpoints must meet with common object IDs. Camera projections must match at boundaries unless a named Owner-approved intentional cut has a separate test. Tolerances are **provisional** until Owner approval. The program does not verify actual SHA contents, engineering physics, camera interpolation or browser rendering. `structurally_valid=true` never means science/visual acceptance.

Historic YALDA hard transitions 03→04, 05→06, 07→08, 09→10 and 11 storyline stages are regression candidates from 2026-11-04, not automatically present defects. Preserve foundation openings, N2/N3/N4, patch IDs, physical quantity and SAFE mapping. Native vertical page flow and deterministic reverse are required design targets.
