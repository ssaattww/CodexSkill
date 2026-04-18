---
name: development-orchestrator
description: Orchestrate iterative development work from task selection through design update, test-first execution, Codex delegation, review, progress reflection, commit, and PR creation. Use when resuming development, starting a new issue/task, or continuing implementation across multiple tasks and phases. This skill acts as the parent coordinator and calls specialized child skills rather than performing detailed work itself.
---

# Development Orchestrator

Use this skill as the entry point for implementation work.

Keep this skill thin. Do not embed detailed rules that belong in child skills.

## Goal

Advance one task at a time until it reaches commit and PR creation, then move to the next task.

## Execution owner

Run this skill as: `parent`

- This skill owns task selection, completion flow, and final lifecycle decisions.
- End-of-issue skill-gap reflection is parent work, not sub-agent work.

## Required flow

Follow this sequence:

1. Confirm current state from `tasks-status.md`, `phases-status.md`, recent `reports/`, and `feedback-points/feedback-points.md`.
2. Select exactly one next task.
3. Call `task-consistency-manager`.
4. Call `design-doc-maintainer` if design impact exists.
5. Call `tdd-executor`.
6. Call `codex-delegation-executor` to choose executor and run implementation/verification work.
7. Call `review-enforcer`.
8. Call `progress-sync-manager`.
9. Call `git-workflow-manager`.
10. When an issue or task reaches done, make an explicit parent-side decision: `no skill action needed`, `update an existing skill`, or `propose a new skill`.
11. Call `feedback-points-manager` only if that decision should be recorded as reusable process feedback or a skillization record.
12. Return to task confirmation.

## Core rules

- Work on one task at a time.
- Do not treat implementation as complete before commit and PR creation.
- Do not skip task reconciliation, design reflection, review, or progress updates.
- Do not skip parent-owned end-of-issue skill-gap reflection when an issue reaches done.
- Do not decide `main agent` vs `sub-agent` for implementation outside `codex-delegation-executor`.
- Treat design-document editing as switchable implementation work under `codex-delegation-executor` with `design-executor`.
- Treat test authoring and code authoring as switchable implementation work under `codex-delegation-executor` with `implementation-executor`.
- Do not downgrade skills that require mandatory `sub-agent` execution.
- When work is delegated to a `sub-agent`, prefer making it read the relevant skill files instead of relying on a paraphrased prompt alone.
- If any future skill remains `どちらでも良い`, resolve that ownership before work starts and batch the user confirmation up front.
- Call `feedback-points-manager` whenever a reusable process problem, repeated instruction, or workflow failure is detected.
- Stop and re-plan when work required for the current task is missing from `tasks-status.md`.

## Completion condition for one cycle

A task cycle is complete only when all of the following are true:

- implementation is done
- tests have been run
- review has been completed
- reports have been written
- progress files have been updated
- commit has been created
- PR has been created
- end-of-issue skill candidate decision has been made

## What this skill must not do

- Do not contain detailed TDD instructions.
- Do not contain detailed Git instructions.
- Do not contain detailed review criteria.
- Do not directly replace child skills.
- Do not bypass `codex-delegation-executor` when executable work needs an owner decision.
