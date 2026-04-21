---
name: feedback-points-manager
description: Maintain feedback-points.md as a cross-cutting record of reusable workflow lessons, repeated process failures, skill adoption status, and skillization candidates. Use from any skill whenever a new process-related instruction appears, a repeated point reoccurs, a workflow problem is discovered, or a decision must be made about whether a repeated point should become a skill.
---

# Feedback Points Manager

Maintain `<repo-root>/feedback-points/feedback-points.md` as the system of record for reusable workflow lessons.

## Goal

Capture process-level feedback, detect repetition, and route skill-improvement follow-up into issues so the active FP ledger does not remain the long-term execution queue and is empty again by commit timing.

## Execution owner

Run this skill as: `parent`

- This skill governs feedback records and skillization decisions.
- Parent agents may call it after issue completion, but issue-completion reflection itself is not owned here.

## Inputs

Before running this skill, gather:

- candidate process lesson or repeated workflow problem
- current active `feedback-points/feedback-points.md`
- any existing duplicate group or related skill context
- whether the trigger came from explicit user instruction, parent judgment, or sub-agent proposal

The canonical files live in the real repository root, not inside the symlinked `skills/` tree:

- active: `<repo-root>/feedback-points/feedback-points.md`
- backlog: `<repo-root>/feedback-points/feedback-points-backlog.md`

If either file must be created from scratch, include a top-of-file rule stating that it may be updated only through `feedback-points-manager` or `feedback-points-sanitizer`.

## This skill is cross-cutting

Allow any other skill to call this skill.

Typical callers include:

- `development-orchestrator`
- `task-consistency-manager`
- `design-doc-maintainer`
- `codex-delegation-executor`
- `review-enforcer`
- `progress-sync-manager`
- `git-workflow-manager`
- `execution-cost-stabilizer`

## Run this skill

Run this skill when:

- a new process instruction appears
- a known process problem happens again
- workflow mistakes keep recurring
- a point seems reusable across repositories
- you need to decide if a point should become a skill or a skill update
- you need to decide whether to recommend a new skill or update an existing one
- a reusable execution lesson is discovered during work even if the user did not explicitly label it as an `FP`
- an in-flight adjustment to tools, patch sizing, sequencing, or delegation proved necessary to keep execution stable
- a commit-ready skill/process improvement needs a tracked follow-up issue before the loop can be considered handed off

## Scope filter

Record workflow and development-method points, not issue-specific feature design details.

Good examples:

- delegation policy
- TDD policy
- review policy
- progress update policy
- task sizing policy
- Git workflow policy
- restart or handover policy

Do not keep one-off feature specifications here if they belong in design docs, reports, tasks, or phases.

## Read only what you need

Read in this order:

1. active `feedback-points/feedback-points.md`
2. `feedback-points/feedback-points-backlog.md` only if needed
3. related `tasks-status.md` and `phases-status.md` only if needed for context

Open only one reference unless the situation clearly spans multiple decisions:

- Need table columns, allowed statuses, or legacy cleanup:
  - [references/feedback-format-and-cleanup.md](references/feedback-format-and-cleanup.md)
- Need duplicate-group decision, threshold, or "skillize vs not":
  - [references/skillization-policy.md](references/skillization-policy.md)
- Need issue creation flow, routing target, or required run output:
  - [references/skillization-operations.md](references/skillization-operations.md)
- Need category naming or duplicate-group naming:
  - [references/canonical-feedback-taxonomy.md](references/canonical-feedback-taxonomy.md)

If the answer is obvious from the active row and current skill context, do not open any reference.

If the active file is visibly noisy, mixed with issue-specific content, or hard to classify, call `feedback-points-sanitizer` first.

Before writing to `feedback-points/feedback-points.md`, get a pre-write classification review when the point is new, materially rewritten, ambiguous, or potentially duplicative. Prefer an independent sub-agent pass via `feedback-points-sanitizer` when available. Only write directly when reusable-process classification is obvious.

Treat the classification as parent-direct only when the reusable-process nature is obvious. For non-obvious cases, request a classification pass from `feedback-points-sanitizer` first.

Keep this skill as the parent governance point for skillization decisions. Use sub-agents for narrow classification, comparison, or review work when helpful, but keep the final proposal vs implementation decision in the main agent.

When writing or updating a feedback-point row, always record `記録起点` so the user can distinguish explicitly requested entries from parent-originated entries.

If the user says `〜べきです`, treat that statement as an explicit `指摘` by default, not as optional advice. Route it through this skill immediately unless it is clearly non-process content.

When a skill-improvement loop has been committed or otherwise reached the point where follow-up should be tracked externally, create the corresponding issue, preserve the full FP content in that issue, and remove the active row from `feedback-points/feedback-points.md`.

## Required output after each run

After running this skill, leave clear evidence in chat or report:

- whether a new point was added or merged
- recorded `記録起点`
- duplicate group decision
- skillization status decision and reason
- related skill update/new-skill decision
- `次アクション対応`
- issue creation result (issue URL/number, or draft file path)
- whether the active FP row was removed or moved to backlog after issue creation

## Outputs

After this skill runs, there should be:

- an added, merged, updated, or explicitly skipped feedback-point decision
- an explicit `記録起点`
- duplicate-group and skillization status rationale
- clear evidence of `次アクション対応`
- no stale active FP row for a point that has already been handed off to an issue
- no active FP row left behind at commit timing for points already reflected or handed off

## Completion condition

This skill is complete only when the feedback-point decision and its rationale are recorded in chat, report, or the feedback ledger, and any commit-ready skill/process point has been removed from the active FP ledger.

## Strong rules

- Always make an explicit skillization decision for repeated process points.
- Keep process feedback and feature specifications separated.
- Keep the active feedback records current when recurrence status changes.
- Do not wait for an explicit `FP` request when a reusable process lesson is already clear from the work itself.
- Do not register a new or updated feedback-point without making its origin visible to the user through `記録起点`.
- When the user states `〜べきです`, do not defer classification or wait for an explicit `FP` request; treat it as a process finding immediately unless clearly out of scope.
- When a feedback-point materially affects an existing skill, consider updating that skill even if the current thresholds or wording already exist.
- When a follow-up issue has been created for a skill-improvement point, preserve the FP content in the issue body and remove that point from the active FP ledger.
- By the time related work is committed, active `feedback-points.md` should be empty again unless a truly not-yet-handoffable point was created in the same run and cannot yet be issue-tracked.
