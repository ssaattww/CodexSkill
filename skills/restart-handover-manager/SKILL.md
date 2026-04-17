---
name: restart-handover-manager
description: Reconstruct the current development state from tracking files and recent reports so work can resume in a new Codex session without re-deriving project context from scratch. Use when restarting after interruption, opening a new chat/session, handing work over, or resuming development from existing tasks, phases, reports, and feedback records.
---

# Restart Handover Manager

Resume work from recorded state.

## Goal

Restore the next actionable task from persistent project records.

## Read in this order

1. `feedback-points.md`
2. `phases-status.md`
3. `tasks-status.md`
4. recent `reports/`

## Required outputs

Produce:

- current overall position
- active or next task
- open dependencies
- latest review or verification state
- immediate next action

## Rules

- Prefer recorded state over memory.
- Do not assume implementation is complete just because code exists.
- If tracking is stale or contradictory, call `task-consistency-manager` and `progress-sync-manager`.

## Cross-cutting rule

If restart friction itself becomes a repeated pattern, call `feedback-points-manager`.