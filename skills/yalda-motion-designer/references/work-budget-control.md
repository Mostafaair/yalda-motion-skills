> **v0.4.0 R4 cost policy:** favor source reuse, 1-2 targeted browser screenshots per known defect and bounded QA matrices before speculative full renders. Do not turn the R4 image-first profile into an expensive 3D proof mission. Owner budget and user-accessible checkpoint rules unchanged.

# Owner-controlled run-cost and task-budget protocol — v0.3.0

## Source-bound method

## Precise platform limitation
The YALDA Skill **cannot inspect ChatGPT Work's remaining subscription usage, its reset timer, exact token quota, internal model calls or price** unless Work exposes these metrics to the task. Never call wall clock, a self-estimated token counter or tool-call counts *the actual Work quota*. Local budget control is an **advisory gate with manually available measured counters**. No known usage value must be labeled UNKNOWN, never zero.

## Preflight for Work/Agent
1. Freeze Owner GO and milestone list; explicitly list quality gates, source dependencies and stop points. Choose fastest evidence-bearing step, not an expensive render first.
2. Owner supplies optional limits in `assets/owner-work-budget-TEMPLATE.json`; all `null` is DRAFT, **not unlimited and not approved**. No global cost or time threshold is invented. `soft_stop_ratio` is Owner policy, not a platform fact.
3. `python scripts/work_budget_guard.py init --workdir WORKSPACE --config owner-work-budget.json`; never reset usage silently.
4. Before significant model/render/tool work, write the expected *incremental* resources in `next-action.json` and call:
   `python scripts/work_budget_guard.py preflight --workdir WORKSPACE --next-usage next-action.json`.
   `STOP_HARD_LIMIT` blocks the action, `HOLD_UNMEASURED` means cannot prove compliance, `CHECKPOINT_AND_REASSESS` requires a durable checkpoint and Owner decision. Only `PASS_WITHIN_DECLARED_LIMITS` is an advisory pass.
5. After an action, write `usage.json` with `measured` counters and independently labeled `estimated`. Call `record --workdir WORKSPACE --usage usage.json`. Estimates are never silently counted as measured data. If metrics cannot be observed, declare `null`; the tool flags `unmeasured`.
6. Prefer targeted retrieval over repeated whole-codebase reads; reuse hash-verified files, cached trace results and deterministic scripts; do not repeat previously checked source until baseline changes. Limit parallel verification/agent fan-out to scope and available budget. Apply one small correction + focused tests before broader validation.
7. Stop substantive work on limit, loss of source, missing permission, or inability to deliver a checkpoint. Save status, portable evidence and exact next action. Reaching a budget is **NOT completion** and shall not be called PASS.

## Usage/next-action schema
Example file contents (NOT Owner approval):
`{"elapsed_minutes": 8, "model_tokens": null, "tool_calls": 2, "render_jobs": 1, "external_cost_usd": null}`

`usage.json` contains `{"action":"render A2", "measured":{...},"estimated":{...},"source":"observed tool usage / manual estimate"}`. Model tokens, dollars and reset timers remain unmeasured when not exposed. If `soft_stop_ratio` is unset, only declared hard caps can be compared. Simple render-job counts do not substitute for quality evaluation.

## Red-line behaviors
- Do not spend an hour on unexported source without a verified accessible checkpoint.
- Do not write `READY`, `100% budget-safe` or `5h remaining` without actual platform metrics.
- Do not automatically reduce R1 fidelity to fit work cost. Return to Owner with measured tradeoffs.
- Do not silently count unrelated user-level quotas, staging bandwidth or final frame MB as an agent token or dollar budget.
