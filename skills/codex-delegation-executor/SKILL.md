---
name: codex-delegation-executor
description: Delegate investigation, implementation, build, and test execution to Codex or sub-agents instead of performing those steps manually. Use for code investigation, implementation tasks, verification runs, review preparation, evidence collection, and multi-agent decomposition. This skill standardizes executor choice, delegation assessment, and report-backed results.
---

# Codex Delegation Executor

Route executable work through Codex or sub-agents.

## Goal

Ensure investigation, implementation, build, and verification work are delegated consistently, with executor choice and any multi-agent decomposition made explicitly and evidenced.

This Skill decides whether work stays with the main agent, goes to one sub-agent, or is split into independently bounded sub-agent tasks. `sub-agent-task-manager` owns the model tier, reasoning effort, fork policy, role/default-role planning, runtime-profile observability, and report-persistence handling for each bounded sub-agent task.

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
- uncertainty, expected change radius, criticality, repetition, observed decomposability, and context need
- `decomposition_policy: allowed | forbidden` when the caller owns an identity-sensitive execution constraint
- report persistence mode when the caller requires `normal_persistence` or `deferred_attestation`
- any pre-reserved report-path identity supplied by an upstream lifecycle owner
- explicit user or repository model, reasoning, budget, availability, fork, or agent-role constraints

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

Use `sub-agent-task-manager` for these categories.

Ordinary fixed-sub-agent work uses `normal_persistence` and must produce a report under `reports/`. Independent-final review is the explicit exception: when `review-enforcer` supplies `report_persistence_mode: deferred_attestation` and a pre-reserved report-path identity, the reviewer returns structured evidence to the parent and must not create or edit that reserved repository path before a passing verdict.

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
- `decomposition_policy`: `allowed` or `forbidden`
- `decomposition_disposition` when policy suppresses an otherwise-decomposable task
- `context_need`: `fresh`, `bounded_history`, or `full_history`
- source evidence for each non-obvious classification

`decomposability` is an observed work-structure signal. `decomposition_policy` is an execution constraint. Do not rewrite an observed `independent_workstreams` signal to `single` merely because a caller forbids decomposition.

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

Split work into multiple sub-agents only when `decomposition_policy: allowed` and all of the following hold:

- at least two workstreams can execute independently
- every workstream has explicit scope, non-goals, expected evidence, and report ownership
- write ownership is non-overlapping, or the work is read-only
- no blocking investigation result is required before another workstream can start
- the parent defines a synthesis and conflict-resolution step
- `execution-cost-stabilizer` confirms that parallel execution provides material value

Do not split work merely because it is large. Keep sequential dependencies sequential. When decomposition is forbidden, preserve truthful decomposability and record the policy disposition instead of changing the signal.

For every decomposed task:

- run a separate delegation assessment
- call `sub-agent-task-manager` separately
- allow different model tiers and reasoning efforts
- use a separate report path
- preserve one parent-owned integration decision

When one exceptionally difficult problem is intrinsically not separable, leave it as one task and allow the selector to consider Sol `max`. A caller prohibition on decomposition does not establish intrinsic non-decomposability and must not be used to justify `max`.

## Required delegation pattern

For each delegated task:

1. classify the work as fixed-sub-agent vs implementation-side delegation
2. record the delegation assessment, including truthful decomposability and any separate decomposition policy/disposition
3. if the work has independent workstreams and decomposition is allowed, decide whether multi-agent decomposition meets every gate above
4. if fixed-sub-agent, call `sub-agent-task-manager`
5. otherwise choose executor and record why that executor was chosen
6. when choosing a `sub-agent`, pass the bounded task, assessment, explicit overrides or constraints, decomposition disposition, report persistence mode, and any upstream pre-reserved report identity to `sub-agent-task-manager`
7. define the exact scope and non-goals
8. identify any skill files the executor must read
9. define expected outputs
10. define validation commands or evidence
11. run or dispatch the delegated work
12. capture results plus dispatch evidence: `requested`, `role_plan`, `planned_runtime_profile`, `profile_observability`, exact `applied` only when observable, otherwise the explicit unverified/inherited/fallback/capability-gap state, and synthesis evidence
13. for `normal_persistence`, materialize the evidence in `reports/`; for `deferred_attestation`, retain it as parent-owned lifecycle evidence until the passing-verdict attestation owner permits persistence

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
- Ordinary `normal_persistence` sub-agent work must leave a report in `reports/`.
- Pre-create the report file before dispatch only for `normal_persistence`.
- Independent-final `deferred_attestation` is reservation-only before review: do not create, edit, or require direct reviewer editing of the reserved report path.
- For `normal_persistence`, instruct the child to read the pre-created report and preserve its format, filling only child-owned blank sections or placeholders.
- For independent-final `deferred_attestation`, require structured reviewer output to the parent and preserve the pre-reserved report identity supplied by `review-enforcer`.
- Exclude noisy diffs and irrelevant generated files from the explicit focus, but do not block the `sub-agent` from reading broader workspace context when needed.
- Require concrete evidence instead of verbal assurance.
- Do not instruct a `sub-agent` to run `codex exec`, nested Codex, or equivalent agent-spawning workflows inside the delegated task.
- Do not instruct a `sub-agent` to re-enter `development-orchestrator` or any other parent-owned workflow unless that orchestration work is itself the explicit delegated task.
- For review tasks, instruct the `sub-agent` to use the built-in review behavior rather than a custom ad hoc review style.
- For normal review/fix verification, direct report editing may be used under `normal_persistence`; for independent-final deferred attestation, repository report editing is prohibited before passing verdict.
- For review tasks, instruct the reviewer to separate normal-path blockers, user-confirmation-required capability gaps, and non-blocking concerns that should only be recorded and held.
- For review and investigation tasks, prefer workspace-direct inspection over parent-written excerpts when repository access is available.
- Do not accept chat-only output for ordinary normal-persistence review. Deferred independent-final review is different: structured parent-returned review evidence is authoritative until attestation persistence is allowed.
- When a delegated task depends on an existing skill, instruct the executor to read that skill file explicitly.
- Do not encode model or reasoning selection only in a task prompt. Let `sub-agent-task-manager` select and plan the profile as actual spawn arguments.
- Do not infer exact `applied` from successful spawn. Accept `spawn_succeeded_profile_unverified` when the runtime hides the final profile and preserve `profile_observability`.
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
- for every sub-agent task: `requested`, `role_plan`, `planned_runtime_profile`, and `profile_observability`
- exact `applied` evidence when observable, otherwise an explicit `spawn_succeeded_profile_unverified`, inherited, fallback, or capability-gap state without inventing exact model/reasoning values
- synthesis evidence when multiple sub-agents were used
- report-backed evidence for `normal_persistence`, or retained parent-owned evidence plus a stable pre-reserved report identity for `deferred_attestation`

## Evidence rules

Record or retain, according to persistence mode:

- executor chosen and why
- delegation assessment and source evidence
- multi-agent decomposition policy/disposition
- what was delegated
- what was changed or checked
- what commands ran
- requested profile for every sub-agent
- role/default-role plan and its configuration evidence
- planned runtime profile
- runtime profile observability
- exact applied profile only when observable; otherwise the explicit unverified/inherited/fallback/capability-gap state
- report persistence mode and, for deferred attestation, the upstream reservation owner/identity
- pass/fail outcome
- synthesis result when applicable
- unresolved risks if any

When creating a new normal-persistence report file, call `report-output-manager` for placement and filename rules. Do not create or re-reserve an independent-final deferred-attestation report path here when `review-enforcer` already owns its pre-freeze reservation.

## Completion condition

This skill is complete for the current work item only when:

- executor choice has been made explicitly
- the delegation assessment is recorded without falsifying observed decomposability
- any multi-agent split satisfies every decomposition gate and caller policy
- delegated or assigned work scope is fixed
- required execution has run or been dispatched
- sub-agent dispatch evidence includes requested profile, role plan, planned runtime profile, and profile observability
- exact applied profile is recorded when observable; otherwise an explicit supported unverified/inherited/fallback/capability-gap state is recorded
- results/evidence are captured in the applicable normal report or retained deferred-attestation lifecycle evidence

## Cross-cutting rule

If recurring delegation failures, profile misclassification, runtime-observability gaps, report-lifecycle conflicts, or repeated workflow mistakes appear, call `feedback-points-manager`.