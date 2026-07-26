---
name: tdd-executor
description: Apply test-driven development only when the target repository explicitly requires test-first work for the selected task. Use after the development-orchestrator has identified a governing TDD policy and before implementation begins.
---

# TDD Executor

## Goal

Apply a target repository's explicit test-first policy without imposing TDD on repositories or tasks that do not require it.

## Shared contracts

Follow:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Implementation Contract](../../shared/workflow/implementation-contract.md)

The target project's instructions own whether TDD applies. This Skill owns only the Codex test-first execution adapter after applicability has been established.

## Execution owner

Run this Skill as: `parent`.

- Parent owns the applicability decision, test strategy, and stopping condition.
- Test authoring is implementation work and uses `implementation-executor` through `codex-delegation-executor`.
- Test execution used as Red or Green evidence remains mandatory sub-agent work through `sub-agent-task-manager` when that repository workflow requires delegated evidence.

## Inputs

Before running this Skill, establish:

- the exact repository instruction, Project Instruction, accepted design, or user instruction that requires TDD,
- current task scope and exit criteria,
- relevant existing tests and changed behavior,
- the contract or regression behavior to prove,
- allowed write boundary,
- required failure diagnostics.

## Applicability gate

Do not run the TDD flow unless an authoritative source explicitly requires it for the selected work.

When TDD is not required:

- do not create a Red test merely to satisfy this Skill,
- do not delay implementation for artificial Red/Green evidence,
- record `TDD: not applicable` and the governing source,
- return control to `development-orchestrator`.

CodexSkill repository maintenance is non-TDD unless the user explicitly changes that repository policy.

## Required flow

When the applicability gate passes:

1. Read the governing TDD policy, task, and exit criteria.
2. Identify the smallest testable behavior for the task.
3. Define happy-path, failure-path, boundary, and regression cases required by the accepted scope.
4. Use `codex-delegation-executor` and `implementation-executor` to add or update the smallest tests that expose the current gap.
5. Run the test and record actual failing evidence tied to the current pre-implementation HEAD or workspace state.
6. Only after valid Red evidence exists, return control for implementation.
7. After implementation, run the applicable tests again and record Green and broader validation evidence.
8. Preserve diagnostics and artifacts required by the target project.

## Rules

- Do not infer TDD applicability solely from the fact that code or tests will change.
- Do not claim Red or Green evidence unless the command was run and the result observed.
- Prefer the smallest failing test that proves the intended behavior.
- Add integration or end-to-end proof only when narrower tests cannot establish the contract.
- Keep tests tied to task exit criteria.
- Do not weaken existing tests to obtain Green.
- Do not merge.

## Outputs

When applicable, return:

- governing TDD source,
- named test targets,
- defined cases,
- Red command and evidence,
- Green command and evidence when implementation is complete,
- broader validation evidence,
- diagnostics, unknowns, and remaining risks.

When not applicable, return:

- `TDD: not applicable`,
- the governing repository or user instruction,
- confirmation that no artificial test-first changes were introduced.

## Completion condition

This Skill is complete when either:

- TDD is not applicable and that disposition is explicitly grounded, or
- the governing TDD policy is satisfied with real Red and Green evidence, required diagnostics are preserved, and the result is ready for the next implementation or review stage.

No merge is performed by this Skill.