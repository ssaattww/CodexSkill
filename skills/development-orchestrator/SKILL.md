---
name: development-orchestrator
description: Orchestrate iterative development work through a persistent one-task routine, from task selection through design update, test-first execution, Codex delegation, review, skill/tool reflection, progress synchronization, commit, and PR creation. Use when resuming development, starting a new issue/task, or continuing implementation across multiple tasks and phases. This skill acts as the parent coordinator and calls specialized child skills rather than performing detailed work itself.
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
- This skill owns the persistent task routine state and decides when each routine step is complete.
- End-of-issue skill-gap and tool-automation reflection are parent work, not sub-agent work.
- This skill owns the start-of-workflow check that repo-local skills are current enough to trust.
- This skill is the only standard workflow entry point; restart and handover should re-enter through this skill.

## Inputs

Before running this skill, confirm:

- current local skill state under `/home/ibis/AI/CodexSkill`
- repo root `AGENTS.md` exists and explicitly says both of the following:
  - always confirm whether a relevant skill already exists while working
  - when unsure, suspect skill insufficiency before improvising
- active task routine state from `scripts/task_routine.py status`
- the user's intended work for this run when it is not already explicit from the request or restart context
- current `tasks-status.md` and `phases-status.md`
- recent `reports/` relevant to the active issue or task
- active `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`
- repository state needed to choose the next task

## Required flow

Follow this sequence:

1. Check whether `/home/ibis/AI/CodexSkill` is already current enough for this run.
2. Check `AGENTS.md` before trusting the workflow entry. If either required instruction is missing, notify the user explicitly before selecting a task.
3. If the local skill repo is clean and behind its intended source, update it before continuing the workflow.
4. If the local skill repo is dirty, diverged, or otherwise unsafe to auto-update, stop and resolve that explicitly before trusting the workflow.
5. Read the task routine state with `scripts/task_routine.py status`.
6. When entering from a resumed or restarted session, call `restart-handover-manager` and reconcile its result with the active routine before selecting the next task.
7. When the intended work for this run is not already explicit, read [references/start-intake-policy.md](references/start-intake-policy.md) and confirm with the user what work should be done before selecting a task.
8. Confirm current state from `tasks-status.md`, `phases-status.md`, recent `reports/`, and `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`.
9. Start exactly one task routine when none is active, then select exactly one next task.
10. Record evidence for `intake`, `skill_scan`, `task_definition`, and `plan` before repository mutation begins.
11. Call `task-consistency-manager`.
12. Call `design-doc-maintainer` if design impact exists.
13. Call `tdd-executor`.
14. Call `codex-delegation-executor` to choose executor and run implementation/verification work.
15. Call `review-enforcer`.
16. Record one explicit skill decision: `none`, `update-existing`, or `propose-new`.
17. When the skill decision is `update-existing` and the change is internal, reversible, low-risk, and within an existing skill's ownership, execute it now through `skill-authoring-wrapper`. Recommend a new skill to the user before creating it.
18. Record one explicit tool decision: `none`, `update-existing`, `create-internal`, or `propose-external`. Create or update an internal helper now when it automates deterministic repeated agent output within the current skill ownership and remains reversible and low-risk.
19. Call `feedback-points-manager` when reusable process feedback, duplicate tracking, skillization state, or follow-up issue handling is required.
20. Call `progress-sync-manager`.
21. Call `git-workflow-manager` only after review, both reflections, feedback disposition, and progress synchronization have routine evidence.
22. Archive or close the completed routine, then return to task confirmation.

## Core rules

- Work on one task at a time.
- Do not mutate a repository without an active task routine.
- Do not advance a routine step without evidence or an explicit not-applicable reason.
- Do not use GitHub Issue lookup as the only runtime trigger; issues and feedback points are history and duplicate-tracking records, while the local routine state owns the next executable step.
- Do not start implementation or restart flows from any other standard entry point.
- Do not select a task before clarifying the run target when the user's intended work is still ambiguous.
- Do not treat implementation as complete before commit and PR creation.
- Do not skip task reconciliation, design reflection, review, skill reflection, tool reflection, feedback disposition, or progress updates.
- Do not enter the implementation workflow on stale local skills when a safe latest-sync was available at the start.
- Do not trust the workflow entry until `AGENTS.md` is present and contains the required skill-first constraints, or the user has been explicitly notified that it does not.
- Do not leave local skill creation or substantial local skill updates floating without an explicit caller; use `development-orchestrator` as the default caller when the need is discovered through normal task completion.
- Do not decide `main agent` vs `sub-agent` for implementation outside `codex-delegation-executor`.
- Treat design-document editing as switchable implementation work under `codex-delegation-executor` with `design-executor`.
- Treat test authoring and code authoring as switchable implementation work under `codex-delegation-executor` with `implementation-executor`.
- Do not downgrade skills that require mandatory `sub-agent` execution.
- When work is delegated to a `sub-agent`, prefer making it read the relevant skill files instead of relying on a paraphrased prompt alone.
- Do not make delegated `sub-agent` tasks re-enter this workflow entry skill unless the parent explicitly delegated orchestration analysis itself.
- If any future skill remains `どちらでも良い`, resolve that ownership before work starts and batch the user confirmation up front.
- Call `feedback-points-manager` whenever a reusable process problem, repeated instruction, or workflow failure is detected.
- Call `feedback-points-manager` for reusable execution lessons discovered mid-task even when the user did not explicitly ask to register an `FP`.
- Stop and re-plan when work required for the current task is missing from `tasks-status.md`.

## Outputs

After this skill runs, the workflow should have:

- one explicitly selected current task and active routine
- a concrete next-step path through the child skills
- evidence for every completed or skipped routine step
- explicit skill and tool automation decisions
- evidence of completion or a clear paused, aborted, or blocking condition for the current cycle

## Completion condition

A task cycle is complete only when all of the following are true:

- implementation is done
- tests have been run
- review has been completed
- reports have been written
- skill reflection has an evidence-backed decision
- tool reflection has an evidence-backed decision
- feedback and duplicate tracking have an explicit disposition
- progress files have been updated
- commit has been created
- PR has been created
- the routine has been archived or closed

## What this skill must not do

- Do not contain detailed TDD instructions.
- Do not contain detailed Git instructions.
- Do not contain detailed review criteria.
- Do not directly replace child skills.
- Do not bypass `codex-delegation-executor` when executable work needs an owner decision.
