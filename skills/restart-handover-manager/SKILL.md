---
name: restart-handover-manager
description: Reconstruct the current development state from tracking files and recent reports so work can resume in a new Codex session without re-deriving project context from scratch. Use when `development-orchestrator` needs restart or handover context before selecting the next task.
---

# Restart Handover Manager

Resume work from recorded state.

## Goal

Restore restart context from persistent project records so `development-orchestrator` can continue through the single standard workflow entry point.

## Execution owner

Run this skill as: `parent`

- This skill determines the resumed execution path and should stay with the parent.
- For long report history or noisy restart context, the parent may request a restart summary draft from a `sub-agent`, but the resumed path decision stays with the parent.
- When a resumed session is about to re-enter the standard workflow, this skill should make sure the caller re-checks local skill freshness first.
- This skill is not a standalone workflow entry point; call it from `development-orchestrator`.

## Inputs

Before running this skill, gather:

- current `feedback-points/feedback-points.md`
- `phases-status.md`
- `tasks-status.md`
- recent `reports/`

## Read in this order

1. `feedback-points/feedback-points.md`
2. `phases-status.md`
3. `tasks-status.md`
4. recent `reports/`

## Outputs

Produce:

- current overall position
- active or next task
- open dependencies
- latest review or verification state
- immediate next action

Return that result to `development-orchestrator` instead of starting a parallel workflow here.

## Completion condition

This skill is complete only when the resumed next action is explicit and based on recorded project state.

## Large-scope delegation

If restart context is large enough that reconstructing state would require scanning many reports or conflicting records, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded resume-summary pass
3. require a report under `reports/`
4. decide the actual resumed next action in the parent

Use these provisional thresholds as the default trigger:

- recent reports to inspect are 5 or more
- there are contradictions across 2 or more of `feedback-points`, `tasks-status`, `phases-status`, and `reports/`
- open candidate next tasks are 3 or more
- the parent would otherwise need to summarize 4 or more separate evidence sources before restarting

## Rules

- Prefer recorded state over memory.
- Do not assume implementation is complete just because code exists.
- Do not resume into active workflow without re-checking whether `/home/ibis/AI/CodexSkill` is current enough to trust.
- Do not act as a second workflow entry point; resume flows must re-enter through `development-orchestrator`.
- If tracking is stale or contradictory, call `task-consistency-manager` and `progress-sync-manager`.

## Cross-cutting rule

If restart friction itself becomes a repeated pattern, call `feedback-points-manager`.
