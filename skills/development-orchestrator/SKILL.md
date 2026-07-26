---
name: development-orchestrator
description: Orchestrate iterative development work from task selection through design update, project-defined implementation and validation, Codex delegation, review, progress reflection, commit, and PR creation. Use when resuming development, starting a new issue or task, or continuing implementation across multiple tasks and phases. This Skill acts as the parent coordinator and calls specialized child Skills rather than performing detailed work itself.
---

# Development Orchestrator

## Goal

Advance one task at a time through the target project's required development lifecycle until commit and PR creation.

This is the single standard entry point for implementation and resume flows.

## Shared contracts

Follow the [Common Work Contract](../../shared/workflow/common-work-contract.md) for authority, state discovery, target identity, validation evidence, report separation, and merge boundary.

The target repository owns its development method and testing order. This orchestrator must not impose TDD when the target repository does not require it.

## Execution owner

Run this Skill as: `parent`.

- This Skill owns task selection, lifecycle routing, and final workflow decisions.
- End-of-Issue Skill-gap reflection is parent work, not sub-agent work.
- This Skill owns the start-of-workflow check that repository-local Skills are current enough to trust.
- Restart and handover flows re-enter through this Skill.

## Inputs

Before running this Skill, establish:

- current local Skill state under `/home/ibis/AI/CodexSkill`,
- repository-root `AGENTS.md` and its Skill-first constraints,
- the user's intended work when it is not already explicit,
- the target repository's development and testing policy,
- the user-confirmed model for implementation sub-agent work when delegation may occur,
- current `tasks-status.md` and `phases-status.md`,
- recent relevant `reports/`,
- active `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`,
- repository state needed to select one task.

## Required flow

1. Check whether `/home/ibis/AI/CodexSkill` is current enough for this run.
2. Check `AGENTS.md` before trusting the workflow entry. If either required Skill-first instruction is missing, notify the user explicitly before selecting a task.
3. If the local Skill repository is clean and behind its intended source, update it before continuing.
4. If it is dirty, diverged, or unsafe to update automatically, stop and resolve that state explicitly before trusting the workflow.
5. For a resumed or restarted session, call `restart-handover-manager` to reconstruct the current position.
6. At the first applicable user confirmation, confirm the implementation sub-agent model. When the intended work is not explicit, also read [start intake policy](references/start-intake-policy.md) and establish the work target.
7. Confirm state from task tracking, phase tracking, relevant reports, feedback points, repository evidence, and the target project's development policy.
8. Select exactly one next task.
9. Call `task-consistency-manager`.
10. Call `design-doc-maintainer` when design impact exists.
11. If and only if the target repository explicitly requires TDD for the selected work, call `tdd-executor`. Otherwise record TDD as not applicable with the governing source and continue.
12. Call `codex-delegation-executor` to choose an executor and run implementation and verification under the shared implementation contract.
13. Call `review-enforcer`.
14. Call `progress-sync-manager`.
15. Call `git-workflow-manager`.
16. When an Issue or task reaches done, make an explicit parent-side decision: `no skill action needed`, `update an existing skill`, or `propose a new skill`.
17. When the chosen Skill action should be executed now, call `skill-authoring-wrapper`.
18. Call `feedback-points-manager` when reusable process feedback, Skillization state, or a follow-up Issue must be recorded.
19. Return to task confirmation.

## Core rules

- Work on one task at a time.
- Do not start implementation or resume flows from another standard entry point.
- Do not select a task while the run target remains ambiguous.
- Do not treat implementation as complete before required validation, review, progress synchronization, commit, and PR creation.
- Do not skip task reconciliation, design reflection, review, or progress updates.
- Do not enter the workflow on stale local Skills when a safe latest synchronization was available.
- Do not trust the workflow entry until `AGENTS.md` contains the required Skill-first constraints or the user has been explicitly notified.
- Do not skip parent-owned end-of-Issue Skill-gap reflection.
- Do not leave substantial local Skill changes without an explicit caller.
- Do not choose parent versus sub-agent implementation outside `codex-delegation-executor`.
- Do not dispatch implementation sub-agent work before the user-confirmed model is known.
- Treat design editing, test authoring, code authoring, documentation, configuration, and workflow editing as implementation work owned through the applicable executor.
- Do not call `tdd-executor` merely because code or tests may change. Call it only when the target repository explicitly requires TDD.
- CodexSkill repository maintenance is non-TDD unless the user explicitly changes that repository policy.
- When work is delegated, prefer making the sub-agent read the relevant Skill and shared contract files instead of relying only on a paraphrased prompt.
- Do not make delegated tasks re-enter this orchestration Skill unless orchestration analysis itself was delegated.
- Call `feedback-points-manager` for reusable process problems, repeated instructions, or workflow failures.
- Stop and re-plan when required work is missing from task tracking.

## Outputs

After this Skill runs, the workflow has:

- one explicitly selected task,
- the governing target-project development and testing policy,
- a concrete route through applicable child Skills,
- implementation and validation evidence or an explicit blocking condition,
- review, report, tracking, commit, and PR state.

## Completion condition

A task cycle is complete only when:

- accepted implementation is complete or explicitly blocked,
- target-project-required tests and validation are recorded,
- TDD was applied only when required and otherwise recorded as not applicable,
- review is complete,
- required reports exist,
- progress files are synchronized,
- commit and PR actions are complete,
- the end-of-Issue Skill decision is recorded,
- no merge was performed.

## What this Skill must not do

- Do not contain detailed TDD instructions.
- Do not contain detailed Git instructions.
- Do not contain detailed review criteria.
- Do not directly replace child Skills.
- Do not bypass `codex-delegation-executor` when executable work needs an owner decision.
