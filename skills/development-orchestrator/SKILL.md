---
name: development-orchestrator
description: Orchestrate iterative development work from task selection through design update, project-defined implementation and validation, Codex delegation, review, progress reflection, commit, and PR creation. Use when resuming development, starting a new issue or task, or continuing implementation across multiple tasks and phases. This Skill acts as the parent coordinator and calls specialized child Skills rather than performing detailed work itself.
---

# Development Orchestrator

## Goal

Advance one task at a time through the target project's required development lifecycle until commit and PR creation.

This is the single standard entry point for implementation and resume flows.

## Required Skills

Use independent Skills rather than repository-external shared files:

- `work-context-manager` resolves authority, scope, target identity, policy, validation evidence, and write boundaries.
- `implementation-executor` is the Codex wrapper that invokes `implementation-worker`.
- `report-output-manager` is the Codex wrapper that invokes `report-writer`.
- `review-enforcer` is the Codex wrapper that invokes `review-worker`.

If a required Skill is unavailable, stop with a missing dependency. Do not reproduce its rules locally and do not fall back to `shared/` files.

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
- any explicit user or repository model, reasoning, budget, availability, or fork override for delegated work,
- current `tasks-status.md` and `phases-status.md`,
- recent relevant `reports/`,
- active `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`,
- repository state needed to select one task.

When no explicit dispatch override exists, do not ask the user to choose an implementation sub-agent model routinely. `codex-delegation-executor` and `sub-agent-task-manager` derive a profile from the bounded task.

## Required flow

1. Check whether `/home/ibis/AI/CodexSkill` is current enough for this run.
2. Check `AGENTS.md` before trusting the workflow entry. If either required Skill-first instruction is missing, notify the user explicitly before selecting a task.
3. If the local Skill repository is clean and behind its intended source, update it before continuing.
4. If it is dirty, diverged, or unsafe to update automatically, stop and resolve that state explicitly before trusting the workflow.
5. For a resumed or restarted session, call `restart-handover-manager` to reconstruct the current position.
6. At the first applicable user confirmation, establish the intended work and any explicit dispatch override or budget constraint. When the intended work is not explicit, also read [start intake policy](references/start-intake-policy.md) and establish the work target. Do not request routine confirmation of an automatically selected implementation model.
7. Invoke `work-context-manager` to resolve authority, current state, scope candidates, policy, validation targets, and write boundaries.
8. Select exactly one next task from the resolved context.
9. Call `task-consistency-manager`.
10. Call `design-doc-maintainer` when design impact exists.
11. If and only if the target repository explicitly requires TDD for the selected work, call `tdd-executor`. Otherwise record TDD as not applicable with the governing source and continue.
12. Call `codex-delegation-executor` to classify the task, choose an executor, and decide whether independently bounded workstreams justify multi-agent decomposition. For each selected sub-agent task, `sub-agent-task-manager` selects and applies the model, reasoning effort, and fork policy. The selected `implementation-executor` invokes `work-context-manager` and `implementation-worker` for implementation or review follow-up.
13. Route validation, commit, push, and CI waiting by `verification_capability`. For `local_execution_available`, reuse focused inner-loop evidence before review-target commits, keep normal review/fix loops local without CI waits, and keep broader validation distinct from the full local equivalence gate. For `remote_ci_only`, use matching current-HEAD CI after authorized push as formal verification evidence.
14. Before review, create or update implementation and verification reports through `report-output-manager`, synchronize task and phase tracking, and create the review-target commit. Do not require a local-route review round to push or wait for CI.
15. Call `review-enforcer` for the normal review cycle. Persist normal review and fix-verification reports before selecting the independent-final-review target. Required fixes return through `implementation-executor`, followed by route-appropriate validation, report and tracking synchronization, commit, and another normal fix-verification round.
16. After the normal cycle converges, make the parent-owned end-of-Issue Skill-gap decision: `no skill action needed`, `update an existing skill`, or `propose a new skill`.
17. When the chosen Skill action should be executed in the current scope, call `skill-authoring-wrapper` now. Otherwise record the action as follow-up work before the final-review freeze.
18. Call `feedback-points-manager` for reusable process feedback, Skillization state, or a follow-up Issue. Persist any repository-backed normal handoff, feedback ledger, report, or tracking change now.
19. If steps 16 through 18 changed any repository file, run route-appropriate validation, update reports and tracking, commit, and return to the normal review or fix-verification cycle. Repeat until the normal cycle converges with all end-of-Issue and feedback changes included.
20. Ensure every non-final repository change is committed. After normal convergence, run the repository-defined full local equivalence gate exactly once for the final publication candidate HEAD; record its exact-HEAD identity, retain invalidated prior runs, and rerun only if a content delta changes that candidate. Do not substitute inner-loop focused or broader validation. Reserve the independent-final-review report path, then freeze the current HEAD as the reviewed implementation HEAD.
21. Call `review-enforcer` with one fresh independent reviewer against that frozen HEAD for the single exhaustive pass.
22. If that review discovers required repository change, invalidate the terminal state and return to implementation, validation, reporting, tracking, feedback or Skill-action processing as applicable, followed by normal fix verification and the same independent reviewer's bounded finding/CI-delta closure against the updated reviewed HEAD.
23. When independent final review passes, persist its detailed report through `report-output-manager` as at most one report-attestation commit. The commit's first parent must be the reviewed implementation HEAD and its changed paths must be limited to the pre-reserved independent-final-review report path or paths.
24. Validate the report-attestation diff, make the final authorized push, then invoke `git-pr-submitter` or the authorized equivalent to create or update the PR for that exact HEAD. Wait once after publication for exact-head required `pull_request` CI as the merge gate. On `remote_ci_only`, matching current-HEAD CI may also be formal route evidence. Do not wait for an unrequired `push` run. Update the PR body, concise PR comment, review request, or external Issue only after the attestation commit because those operations do not change Git HEAD.
25. Do not commit task, design, Skill, workflow, configuration, feedback, handoff, report, or implementation changes after the attestation head. Return the final handoff inline or outside the reviewed PR branch.
26. Return to task confirmation. Starting another task begins a new lifecycle and must not append commits to the completed attestation pair.

## Dispatch-profile policy

The workflow must preserve the distinction between:

- executor choice and multi-agent decomposition, owned by `codex-delegation-executor`
- per-task model, reasoning effort, and fork policy, owned by `sub-agent-task-manager`
- explicit user or repository overrides, which take precedence over automatic selection

The parent records the delegation assessment, requested profile, applied profile, and runtime application status in the relevant report. It does not infer success from a model name written in the child prompt.

A dispatch classification must be recomputed when investigation or implementation changes the task kind, uncertainty, change radius, or criticality. A failed deterministic verification becomes investigation; independently separable work returns to `codex-delegation-executor`; a full-history fork that prevents an override is recorded as an inherited-parent-profile constraint.

## Report-attestation terminal rule

An independent-final-review verdict remains attached to its reviewed implementation HEAD. A later Git HEAD may be accepted only as a report-attestation head when all conditions below hold:

- exactly one commit follows the reviewed implementation HEAD,
- its first parent is the reviewed implementation HEAD,
- only the independent-final-review report path or paths reserved before review are changed,
- the report identifies the reviewed implementation HEAD and states that the commit is an administrative attestation rather than reviewed implementation,
- an automated or explicit diff check confirms that no executable, Skill, design, workflow, configuration, task-tracking, feedback, handoff, or product file changed,
- no later repository commit exists.

The completion identity is the pair `reviewed implementation HEAD + validated report-attestation HEAD`. Any other post-review commit invalidates completion and requires normal fix verification followed by the same independent reviewer's bounded finding/CI-delta closure.

After the freeze, only operations that do not change Git HEAD are permitted: PR body or comment updates, review requests, external Issue creation or update, and branch-external or inline transport. Discovery of a required repository write invalidates the terminal state and returns the workflow to the normal cycle.

## Core rules

- Work on one task at a time.
- Do not start implementation or resume flows from another standard entry point.
- Do not select a task while the run target remains ambiguous.
- Do not treat implementation as complete before required validation, review, progress synchronization, commit, and PR creation.
- Do not skip task reconciliation, design reflection, review, or progress updates.
- Do not enter the workflow on stale local Skills when a safe latest synchronization was available.
- Do not trust the workflow entry until `AGENTS.md` contains the required Skill-first constraints or the user has been explicitly notified.
- Do not skip parent-owned end-of-Issue Skill-gap reflection.
- Complete Skill action decisions, feedback classification, feedback-ledger synchronization, normal handoff persistence, reports, and tracking before freezing the independent-final-review target.
- If any of those actions changes the repository, require validation and normal review before freezing again.
- Do not leave substantial local Skill changes without an explicit caller.
- Do not choose parent versus sub-agent implementation outside `codex-delegation-executor`.
- Do not hardcode or require routine user confirmation of an implementation sub-agent model when no explicit override exists.
- Do not bypass `sub-agent-task-manager` profile selection for delegated work.
- Treat design editing, test authoring, code authoring, documentation, configuration, and workflow editing as implementation work owned through the applicable executor.
- Do not call `tdd-executor` merely because code or tests may change. Call it only when the target repository explicitly requires TDD.
- CodexSkill repository maintenance is non-TDD unless the user explicitly changes that repository policy.
- When work is delegated, make the sub-agent read the applicable wrapper and core Skill files instead of relying only on a paraphrased prompt.
- Do not make delegated tasks re-enter this orchestration Skill unless orchestration analysis itself was delegated.
- Do not use deleted or repository-external `shared/` contracts as a fallback.
- Stop and re-plan when required work is missing from task tracking.
- After report attestation, do not call any Skill that can write to the reviewed repository branch.

## Outputs

After this Skill runs, the workflow has:

- one explicitly selected task,
- a structured context from `work-context-manager`,
- the governing target-project development and testing policy,
- a concrete route through applicable wrapper and core Skills,
- an executor and multi-agent decomposition decision,
- a delegation assessment plus requested and applied dispatch profile for every sub-agent task,
- resolved `verification_capability` and separate commit, push, and CI-wait evidence,
- implementation and validation evidence or an explicit blocking condition,
- review, report, tracking, Skill-action, feedback, commit, and PR state,
- a reviewed implementation HEAD and, when repository persistence is required, a validated report-attestation head.

## Completion condition

A task cycle is complete only when:

- accepted implementation is complete or explicitly blocked,
- target-project-required tests and validation are recorded,
- TDD was applied only when required and otherwise recorded as not applicable,
- normal review and independent final review are complete,
- delegated work records the selected and actually applied dispatch profile,
- required non-final reports, tracking, Skill decisions, feedback classification, feedback-ledger updates, and normal handoffs were committed before independent final review,
- any repository change discovered during pre-freeze finalization returned through validation and normal review,
- any post-review repository write is exactly one validated report-attestation commit,
- no repository-writing Skill ran after the attestation head,
- commit and PR actions are complete,
- no merge was performed.

## What this Skill must not do

- Do not contain the detailed agent profile selection matrix.
- Do not contain detailed TDD instructions.
- Do not contain detailed Git instructions beyond the lifecycle boundary needed to keep review finite.
- Do not contain detailed review criteria.
- Do not directly replace child Skills.
- Do not bypass `codex-delegation-executor` when executable work needs an owner decision.
