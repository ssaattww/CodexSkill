---
name: codex-delegation-executor
description: Delegate investigation, implementation, build, and test execution to Codex or sub-agents instead of performing those steps manually. Use for code investigation, implementation tasks, verification runs, review preparation, evidence collection, and multi-agent decomposition. This skill standardizes executor choice, delegation assessment, and report-backed results.
---

# Codex Delegation Executor

Route executable work through Codex or sub-agents.

## Goal

Ensure investigation, implementation, build, and verification work are delegated consistently, with executor choice and any multi-agent decomposition made explicitly and evidenced.

This Skill decides whether work stays with the main agent, goes to one sub-agent, or is split into independently bounded sub-agent tasks. `sub-agent-task-manager` owns the model tier, reasoning effort, and fork policy for each bounded sub-agent task.

## Execution owner

Run this skill as: `parent`

- This skill is the policy owner for delegation, executor choice, and multi-agent decomposition.
- It may dispatch sub-agents through `sub-agent-task-manager`, but the parent keeps decision and synthesis authority.

## Inputs

Before running this skill, identify:

- the concrete work item to delegate or execute
- whether the work is implementation, review, verification, investigation, design, intake, standards, or environment work
- scope boundaries, target files, and non-goals when known
- validation or evidence expectations
- coupling, urgency, write-scope overlap, and whether parallelism helps
- uncertainty, expected change radius, criticality, repetition, and context need
- explicit user or repository model, reasoning, budget, availability, or fork constraints

Do not require a routine user-selected implementation model. Preserve an explicit override when the user or repository supplies one; otherwise let `sub-agent-task-manager` select the per-task profile from the delegation assessment.

## Delegate these work types

Delegate:

- code investigation
- implementation via `implementation-executor`
- design-document editing as implementation work via `design-executor`
- test authoring as implementation work via `implementation-executor`
- code authoring as implementation work via `implementation-executor`
- build execution
- test execution
- environment verification
- focused review preparation
- requirement or issue-intake verification
- standards detection or standards validation
- other assumption-sensitive classification or confirmation work

## Fixed sub-agent categories

The following work must be executed by a `sub-agent` now, not merely preferred:

- review
- build execution used as verification evidence
- test execution used as verification evidence
- environment verification
- requirement or issue-intake verification
- standards detection or standards validation

Use `sub-agent-task-manager` for these categories and require a report in `reports/`.

A fixed sub-agent category fixes the executor, not the model. Pass the task assessment and review or verification mode to `sub-agent-task-manager`, which applies [agent-profile-selection.md](../sub-agent-task-manager/references/agent-profile-selection.md).

## Delegation assessment

Before selecting or dispatching an executor, record:

- `task_kind`
- `work_class`: `mechanical`, `bounded_technical`, or `judgment_heavy`
- `uncertainty`: `low`, `medium`, or `high`
- `change_radius`: `local`, `cross_module`, or `cross_system`
- `criticality`: `ordinary` or `high`
- `repetition`: `single` or `high_volume`
- `decomposability`: `single`, `sequential_dependencies`, or `independent_workstreams`
- `context_need`: `fresh`, `bounded_history`, or `full_history`
- source evidence for each non-obvious classification

Estimate change radius by affected contracts and dependencies, not only by line or file count. A small security, compatibility, migration, concurrency, public-API, or release change is high-criticality even when its edit is local.

If evidence is insufficient, classify uncertainty upward rather than inventing certainty. A later discovery that changes the classification must trigger profile recomputation before another dispatch.

## Executor selection

Decide the executor inside this skill before running the work:

- If the work matches a fixed sub-agent category, do not decide between parent and child; use a `sub-agent`.
- For implementation work, decide `main agent` vs `sub-agent` here based on coupling, urgency, write-scope overlap, and whether isolation or parallelism helps.
- Treat design-document edits, test authoring, and code authoring as implementation work for this decision.
- When the work is design-document editing, make the executor read `design-executor`.
- When the work is code or test authoring, make the executor read `implementation-executor`.
- Keep the main agent responsible for scoping, integration, profile-adjudication evidence, and final synthesis even when a sub-agent executes the task.

Use these provisional thresholds as the default trigger for switchable implementation work:

- affected files are 4 or more
- affected modules or directories are 2 or more
- expected edit chunks are 4 or more
- the parent would otherwise need to read 5 or more implementation files before writing safely

Use the main agent by default below those thresholds unless isolation, independence, or parallelism is clearly more valuable.

The thresholds decide executor ownership only. They do not imply Luna, Terra, or Sol; per-task model selection uses the qualitative assessment above.

## Multi-agent decomposition

Treat article-described `Ultra` execution as a strategy, not a reasoning level.

Split work into multiple sub-agents only when all of the following hold:

- at least two workstreams can execute independently
- every workstream has explicit scope, non-goals, expected evidence, and report ownership
- write ownership is non-overlapping, or the work is read-only
- no blocking investigation result is required before another workstream can start
- the parent defines a synthesis and conflict-resolution step
- `execution-cost-stabilizer` confirms that parallel execution provides material value

Do not split work merely because it is large. Keep sequential dependencies sequential.

For every decomposed task:

- run a separate delegation assessment
- call `sub-agent-task-manager` separately
- allow different model tiers and reasoning efforts
- use a separate report path
- preserve one parent-owned integration decision

When one exceptionally difficult problem is not separable, leave it as one task and allow the selector to consider Sol `max`. Do not use `max` as a substitute for missing decomposition, and do not encode `ultra` in `reasoning_effort`.

## Required delegation pattern

For each delegated task:

1. classify the work as fixed-sub-agent vs implementation-side delegation
2. record the delegation assessment
3. if the work has independent workstreams, decide whether multi-agent decomposition meets every gate above
4. if fixed-sub-agent, call `sub-agent-task-manager`
5. otherwise choose executor and record why that executor was chosen
6. when choosing a `sub-agent`, pass the bounded task, assessment, explicit overrides or constraints, and decomposition disposition to `sub-agent-task-manager`
7. define the exact scope and non-goals
8. identify any skill files the executor must read
9. define expected outputs
10. define validation commands or evidence
11. run the delegated work
12. capture results, selected and applied dispatch profile, and synthesis evidence in `reports/`

## Rules

- Keep delegated tasks small and sequential unless the multi-agent gate is fully satisfied.
- Prefer one focused sub-task over one large ambiguous request.
- Do not pre-decide implementation ownership outside this skill unless the user explicitly requires it.
- Use the main agent for implementation only when the task is tightly coupled to current context, on the critical path, or risky to hand off.
- Use a sub-agent for implementation when the task is bounded, parallelizable, or benefits from isolation.
- Apply the same switchable implementation rule to design-document edits, test authoring, and code authoring.
- Do not use file count as the model selector. Pass qualitative task signals to `sub-agent-task-manager`.
- Do not hardcode model or reasoning defaults in this Skill; `sub-agent-task-manager` owns the central selection table.
- Do not require implementation model confirmation when no user or repository override exists.
- Do not leave concrete design-editing or code-editing workflow rules scattered across unrelated skills when `design-executor` or `implementation-executor` already covers them.
- Every sub-agent request must leave a report in `reports/`.
- Pre-create the report file before dispatch when using `sub-agent-task-manager`.
- Instruct the `sub-agent` to read the pre-created report and preserve its format, filling only blank sections or placeholders.
- Exclude noisy diffs and irrelevant generated files from the explicit focus, but do not block the `sub-agent` from reading broader workspace context when needed.
- Require concrete evidence instead of verbal assurance.
- Do not instruct a `sub-agent` to run `codex exec`, nested Codex, or equivalent agent-spawning workflows inside the delegated task.
- Do not instruct a `sub-agent` to re-enter `development-orchestrator` or any other parent-owned workflow unless that orchestration work is itself the explicit delegated task.
- For review tasks, instruct the `sub-agent` to use the built-in review behavior rather than a custom ad hoc review style.
- For review tasks, instruct the reviewer to edit the pre-created report directly and treat parent-side report transcription as fallback only.
- For review tasks, instruct the reviewer to separate normal-path blockers, user-confirmation-required capability gaps, and non-blocking concerns that should only be recorded and held.
- For review and investigation tasks, prefer workspace-direct inspection over parent-written excerpts when repository access is available.
- For review tasks, do not accept chat-only review output; require the findings to be written into the report file.
- When a delegated task depends on an existing skill, instruct the executor to read that skill file explicitly.
- Do not encode model or reasoning selection only in a task prompt. Let `sub-agent-task-manager` select and apply the profile as actual spawn arguments.
- Do not silently replace an explicit user or repository profile constraint.
- Do not dispatch a dependent implementation task while a blocking investigation remains unresolved.

## Strong rule

Do not personally substitute for delegated investigation, review, intake verification, or test execution when this workflow expects an independent pass.

Reviewer work is always `sub-agent` work.

## Outputs

After this skill runs, there should be:

- an explicit executor decision
- a recorded delegation assessment
- a bounded single task or an explicitly gated multi-agent decomposition
- a decomposition disposition explaining why multi-agent execution was or was not used
- a bounded delegated or locally executed work scope
- selected and applied dispatch-profile evidence for every sub-agent task
- synthesis evidence when multiple sub-agents were used
- evidence captured in `reports/` for the work performed

## Evidence rules

Record in `reports/`:

- executor chosen and why
- delegation assessment and source evidence
- multi-agent decomposition disposition
- what was delegated
- what was changed or checked
- what commands ran
- requested and applied dispatch profile for every sub-agent
- pass/fail outcome
- synthesis result when applicable
- unresolved risks if any

When creating a new report file, call `report-output-manager` for placement and filename rules.

## Completion condition

This skill is complete for the current work item only when:

- executor choice has been made explicitly
- the delegation assessment is recorded
- any multi-agent split satisfies every decomposition gate
- delegated or assigned work scope is fixed
- required execution has run or been dispatched
- selected and applied profiles are recorded for sub-agent work
- results and evidence are captured in `reports/`

## Cross-cutting rule

If recurring delegation failures, profile misclassification, or repeated workflow mistakes appear, call `feedback-points-manager`.
