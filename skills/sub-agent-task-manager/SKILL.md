---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, ownership, execution profile, and one declared evidence mode. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent. Supports existing artifact-backed tasks and structured-result review tasks without forcing reviewers to edit report files.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, and explicit about whether its primary output is a structured result or a repository artifact.

## Execution owner

Run this skill as: `parent`

- This skill prepares and dispatches sub-agent work.
- It is not itself a worker skill.

## Inputs

Before dispatch, identify:

- delegated task purpose and type
- exact scope and non-goals
- relevant worker skill files
- repository context the worker may inspect directly
- write boundaries and validation expectations
- caller-selected model, reasoning effort, and fork policy
- confirmation source for an implementation model
- evidence mode
- required final output contract

## Evidence modes

Select one mode before dispatch.

### `artifact_backed`

Use when the worker is expected to create or update a repository report or another owned artifact as its primary evidence.

- This is the backward-compatible default when an existing caller does not explicitly provide a mode.
- Call `report-output-manager` with `reserve_artifact` before dispatch when a fixed report path is required.
- A pre-created generic report scaffold may be used.
- The worker may edit only its explicitly owned artifact fields.

### `structured_result`

Use when the worker must return a machine-readable result that another skill will render or persist.

- The caller must select this mode explicitly.
- Do not require a report path before dispatch.
- Do not require the worker to edit a Markdown file.
- Require the exact result contract and fixed values in the prompt.
- The parent validates the result before any renderer or artifact adapter is called.
- Review work dispatched by `review-enforcer` must use this mode and return `ReviewResult` from `review-core`.

The mode is part of the dispatch contract. Do not mix both as co-primary outputs.

## Required flow

1. Define the exact task type and why a sub-agent is used.
2. Define scope, non-goals, accessible context, and write boundaries.
3. Select the evidence mode; default only legacy or unspecified callers to `artifact_backed`.
4. Receive model, reasoning effort, and fork policy from the caller.
5. When an override is used, read [references/spawn-agent-model-overrides.md](references/spawn-agent-model-overrides.md).
6. Identify the worker skills and references that must be read.
7. Define the exact final output shape.
8. For `artifact_backed`, call `report-output-manager.reserve_artifact` and create the owned artifact before dispatch when required.
9. For `structured_result`, include the schema, enums, invariants, and validation owner; do not create a presentation artifact first.
10. Dispatch the worker with the selected execution profile in actual spawn arguments.
11. Keep waiting or re-polling until the task completes unless the user explicitly stops it.
12. Validate the returned artifact or structured result according to the selected mode.
13. Return the validated worker output to the caller.

## Required prompt content

Every sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- instruction not to run nested Codex, `codex exec`, or another agent-spawning workflow
- instruction not to re-enter `development-orchestrator` or another parent workflow unless explicitly delegated
- worker skill paths to read first
- available repository context and whether direct inspection is required
- validation expectations
- selected evidence mode or the explicit use of the backward-compatible artifact default
- required final output shape
- model and reasoning only through spawn arguments, not as prompt-only text
- explicit fork policy

For `artifact_backed`, also include:

- artifact path
- owned editable sections or file boundaries
- instruction to preserve non-owned content

For `structured_result`, also include:

- contract path and version
- fixed enum values
- required fields and invariants
- instruction to return the result to the caller instead of writing a presentation file

## Review dispatch

When `review-enforcer` dispatches review work:

- explicitly use `structured_result`
- require the worker to read:
  - `skills/review-core/SKILL.md`
  - `skills/review-core/references/review-contract.md`
  - `skills/review-policy/references/code-review-criteria.md`
- apply the reviewer profile selected by `review-enforcer`
- use the parent model and `high` reasoning unless the user overrides reasoning
- initial and fix verification use the same reviewer when available
- cold final uses `fork_turns: "none"` or another verified fresh-no-history context
- require findings first and severity order
- require file or contract locations when available
- require explicit no-findings output when applicable
- require one valid `ReviewResult`
- do not give the reviewer a report template
- do not ask the reviewer to choose a report path, write a report file, post a PR comment, or alter product code

## Implementation, investigation, and verification dispatch

- Existing artifact-backed flows continue to use the default mode unless their caller adopts a structured contract.
- A caller may explicitly adopt `structured_result` when a suitable contract exists.
- Coding tasks must state owned files or modules and prohibit reverting unrelated changes.
- Investigation tasks must allow direct context inspection when required.
- Verification tasks must identify exact commands and evidence expectations.

## Execution profile

- Apply model and reasoning overrides only through spawn arguments.
- A fresh specialist uses `fork_turns: "none"` unless an explicit bounded partial fork is required.
- Do not combine override values with `fork_turns: "all"` or omitted full-history behavior.
- If hidden override arguments are rejected, fallback execution remains parent-owned as documented in the spawn override reference.
- Never ask the delegated worker to execute the fallback itself.

## Rules

- Keep tasks bounded and concrete.
- Do not make report creation mandatory for a structured-result worker.
- Do not treat rendered prose as the source of machine workflow state.
- Do not allow a reviewer to edit product code or repository review artifacts.
- Do not let artifact rendering failure mutate a valid structured result.
- Do not infer an implementation model; use the user-confirmed value supplied by `development-orchestrator`.
- Prefer workers reading real skill files over copied paraphrases.
- Prefer direct repository inspection for review and investigation when context matters.
- Do not cancel an in-flight task only because one wait interval elapsed.
- Use `execution-cost-stabilizer` when the plan risks excessive retries or parallel work.

## Outputs

Return:

- dispatch task and execution profile
- selected evidence mode
- worker assignment
- validated structured result or artifact reference
- unresolved execution or validation failures

## Completion condition

This skill is complete only when:

- dispatch scope, profile, and evidence mode were explicit or the documented artifact default was applied
- the worker read the required skill contract
- the primary output satisfies the selected mode
- the caller received a validated output

## Cross-cutting rule

If recurring dispatch or evidence failures appear, call `feedback-points-manager`.
