---
name: development-orchestrator
description: Orchestrate iterative development work from task selection through design update, test-first execution, Codex delegation, review, progress reflection, commit, and PR creation. Use when resuming development, starting a new issue/task, or continuing implementation across multiple tasks and phases. This skill acts as the parent coordinator and calls specialized child skills rather than performing detailed work itself.
---

# Development Orchestrator

Use this skill as the entry point for implementation work.

Keep this skill thin. Do not embed detailed rules that belong in child skills.

## Goal

Advance one task at a time until it reaches commit and PR creation, then move to the next task.

This is the single workflow entry point for implementation and resume flows.

## Execution owner

Run this skill as: `parent`

- This skill owns task selection, completion flow, and final lifecycle decisions.
- End-of-issue skill-gap reflection is parent work, not sub-agent work.
- This skill owns the start-of-workflow check that repo-local skills are current enough to trust.
- This skill is the only standard workflow entry point; restart and handover should re-enter through this skill.

## Inputs

Before running this skill, confirm:

- current local skill state under `/home/ibis/AI/CodexSkill`
- the user's intended work for this run when it is not already explicit from the request or restart context
- current `tasks-status.md` and `phases-status.md`
- recent `reports/` relevant to the active issue or task
- active `feedback-points/feedback-points.md`
- repository state needed to choose the next task

## Required flow

Follow this sequence:

1. Check whether `/home/ibis/AI/CodexSkill` is already current enough for this run.
2. If the local skill repo is clean and behind its intended source, update it before continuing the workflow.
3. If the local skill repo is dirty, diverged, or otherwise unsafe to auto-update, stop and resolve that explicitly before trusting the workflow.
4. When entering from a resumed or restarted session, call `restart-handover-manager` to reconstruct the current position before selecting the next task.
5. When the intended work for this run is not already explicit, read [references/start-intake-policy.md](references/start-intake-policy.md) and confirm with the user what work should be done before selecting a task.
6. Confirm current state from `tasks-status.md`, `phases-status.md`, recent `reports/`, and `feedback-points/feedback-points.md`.
7. Select exactly one next task.
8. Call `task-consistency-manager`.
9. Call `design-doc-maintainer` if design impact exists.
10. Call `tdd-executor`.
11. Call `codex-delegation-executor` to choose executor and run implementation/verification work.
12. Call `review-enforcer`.
13. Call `progress-sync-manager`.
14. Call `git-workflow-manager`.
15. When an issue or task reaches done, make an explicit parent-side decision: `no skill action needed`, `update an existing skill`, or `propose a new skill`.
16. If the decision is `update an existing skill` or `propose a new skill` and the local skill work should be executed now, call `skill-authoring-wrapper`.
17. Call `feedback-points-manager` when that decision should be recorded as reusable process feedback, when skillization state changed, or when a follow-up issue must be created at commit timing.
18. Return to task confirmation.

## Core rules

- Work on one task at a time.
- Do not start implementation or restart flows from any other standard entry point.
- Do not select a task before clarifying the run target when the user's intended work is still ambiguous.
- Do not treat implementation as complete before commit and PR creation.
- Do not skip task reconciliation, design reflection, review, or progress updates.
- Do not enter the implementation workflow on stale local skills when a safe latest-sync was available at the start.
- Do not skip parent-owned end-of-issue skill-gap reflection when an issue reaches done.
- Do not leave local skill creation or substantial local skill updates floating without an explicit caller; use `development-orchestrator` as the default caller when the need is discovered through normal task completion.
- Do not decide `main agent` vs `sub-agent` for implementation outside `codex-delegation-executor`.
- Treat design-document editing as switchable implementation work under `codex-delegation-executor` with `design-executor`.
- Treat test authoring and code authoring as switchable implementation work under `codex-delegation-executor` with `implementation-executor`.
- Do not downgrade skills that require mandatory `sub-agent` execution.
- When work is delegated to a `sub-agent`, prefer making it read the relevant skill files instead of relying on a paraphrased prompt alone.
- If any future skill remains `どちらでも良い`, resolve that ownership before work starts and batch the user confirmation up front.
- Call `feedback-points-manager` whenever a reusable process problem, repeated instruction, or workflow failure is detected.
- Call `feedback-points-manager` for reusable execution lessons discovered mid-task even when the user did not explicitly ask to register an `FP`.
- Stop and re-plan when work required for the current task is missing from `tasks-status.md`.

## Outputs

After this skill runs, the workflow should have:

- one explicitly selected current task
- a concrete next-step path through the child skills
- evidence of completion or a clear blocking condition for the current cycle

## Completion condition

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
