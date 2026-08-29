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
- `report-output-manager` owns normal report phases used before the terminal independent-review lifecycle. Independent-final reservation and attestation are invoked only by `review-enforcer`.
- `review-enforcer` is the Codex wrapper that invokes `review-worker` and owns the independent-final terminal lifecycle from report reservation through final exact-head CI.

If a required Skill is unavailable, stop with a missing dependency. Do not reproduce its rules locally and do not fall back to `shared/` files.

The target repository owns its development method and testing order. This orchestrator must not impose TDD when the target repository does not require it.

## Execution owner

Run this Skill as: `parent`.

- This Skill owns task selection, lifecycle routing, pre-freeze readiness, and final workflow decisions.
- `review-enforcer` exclusively owns independent-final report reservation, reviewed-HEAD freeze, independent reviewer lifecycle, report attestation, final publication, and exact-head merge-gate CI.
- End-of-Issue Skill-gap reflection is parent work, not sub-agent work.
- This Skill owns the start-of-workflow check that repository-local Skills are current enough to trust.
- Restart and handover flows re-enter through this Skill.

## Inputs

Before running this Skill, establish:

- current local Skill state under `/home/ibis/AI/CodexSkill`,
- repository-root `AGENTS.md` and its Skill-first constraints,
- the user's intended work when it is not already explicit,
- the target repository's development and testing policy,
- any explicit user or repository model, reasoning, budget, availability, fork, or agent-role override for delegated work,
- current `tasks-status.md` and `phases-status.md`,
- recent relevant `reports/`,
- active `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`,
- repository state needed to select one task.

When no explicit dispatch override exists, do not ask the user to choose an implementation sub-agent model routinely. `codex-delegation-executor` and `sub-agent-task-manager` derive a profile from the bounded task. The exception is an approval-gated Sol `xhigh` or Sol `max` proposal, including one produced by agent-role/default-role planning; those profiles require explicit current-task user approval before dispatch.

## Required flow

1. Check whether `/home/ibis/AI/CodexSkill` is current enough for this run.
2. Check `AGENTS.md` before trusting the workflow entry. If either required Skill-first instruction is missing, notify the user explicitly before selecting a task.
3. If the local Skill repository is clean and behind its intended source, update it before continuing.
4. If it is dirty, diverged, or unsafe to update automatically, stop and resolve that state explicitly before trusting the workflow.
5. For a resumed or restarted session, call `restart-handover-manager` to reconstruct the current position.
6. At the first applicable user confirmation, establish the intended work and any explicit dispatch override or budget constraint. When intended work is not explicit, read [start intake policy](references/start-intake-policy.md) and establish the work target. Do not request routine confirmation of an automatically selected implementation model.
7. Invoke `work-context-manager` to resolve authority, current state, scope candidates, policy, validation targets, and write boundaries.
8. Select exactly one next task from the resolved context.
9. Call `task-consistency-manager`.
10. Call `design-doc-maintainer` when design impact exists.
11. If and only if the target repository explicitly requires TDD for selected work, call `tdd-executor`. Otherwise record TDD as not applicable with governing source and continue.
12. Call `codex-delegation-executor` to classify the task, choose an executor, and decide whether independently bounded workstreams justify multi-agent decomposition when decomposition is allowed. For each sub-agent task, `sub-agent-task-manager` selects model/reasoning/fork, preserves truthful decomposability separately from decomposition policy, plans explicit/default agent-role effects, and records runtime profile observability. If initial or role-adjusted planning proposes Sol `xhigh`/`max`, present rationale/cost to the user and stop before dispatch until explicit approval. If role impact cannot be inspected sufficiently to enforce the gate, stop with capability gap rather than dispatch.
13. Route validation, commit, push, and CI waiting by `verification_capability`. For `local_execution_available`, reuse focused inner-loop evidence before review-target commits, keep normal review/fix loops local without CI waits, and keep broader validation distinct from full local equivalence gate. For `remote_ci_only`, use matching current-HEAD CI after authorized push as formal verification evidence.
14. Before review, create/update implementation and verification reports through `report-output-manager`, synchronize task/phase tracking, and create review-target commit. Do not require local-route review round to push or wait for CI.
15. Call `review-enforcer` for normal review cycle. Persist normal-review/fix-verification reports before selecting independent-final-review target. Required fixes return through `implementation-executor`, followed by route-appropriate validation, report/tracking synchronization, commit, and another normal fix-verification round. Any initial/role-adjusted Sol `xhigh`/`max` review proposal remains subject to explicit approval stop.
16. After normal cycle converges, make parent-owned end-of-Issue Skill-gap decision: `no skill action needed`, `update an existing skill`, or `propose a new skill`.
17. When chosen Skill action should execute in current scope, call `skill-authoring-wrapper`. Otherwise record follow-up before final-review freeze.
18. Call `feedback-points-manager` for reusable process feedback, Skillization state, or follow-up Issue. Persist any repository-backed normal handoff, feedback ledger, report, or tracking change now.
19. If steps 16 through 18 changed repository files, run route-appropriate validation, update reports/tracking, commit, and return to normal review/fix-verification cycle. Repeat until normal cycle converges with all end-of-Issue/feedback changes included.
20. Ensure every non-final repository change is committed. After normal convergence, run the repository-defined full local equivalence gate exactly once for the final publication candidate HEAD; record exact-HEAD identity, retain invalidated prior runs, and rerun only if a content delta changes the candidate. **Do not reserve an independent-final report path and do not freeze the reviewed implementation HEAD here.** Mark the lifecycle as `pre_freeze_ready` and pass the completed pre-freeze evidence to `review-enforcer`.
21. Continue the same `review-enforcer` lifecycle for independent final review. `review-enforcer` alone performs the exactly-once reservation-only phase, records `reservation_owner: review-enforcer` and the stable reservation identity, freezes `reviewed_implementation_head`, selects/dispatches the fresh independent reviewer, retains structured evidence, handles same-reviewer bounded closure, persists at most one report-attestation commit, validates the attestation diff, performs the final authorized push/PR publication, and waits once for exact-head required `pull_request` CI. If profile/role planning proposes Sol `xhigh`/`max`, surface the proposal and stop before dispatch until the user explicitly approves. If role-profile safety is unresolved, stop with capability gap.
22. If `review-enforcer` returns a required repository-change disposition, invalidate terminal readiness and execute only the requested implementation, validation, reporting, tracking, feedback, or Skill-action work. Commit the changes, complete normal fix verification, then return to the **same** `review-enforcer` independent lifecycle so it can reuse its reviewer/reservation evidence as defined by that Skill. Do not create a second reservation or a new terminal owner.
23. When `review-enforcer` returns a passing terminal result, consume its completion evidence: `reviewed_implementation_head`, reservation identity/path evidence, independent reviewer verdict/coverage, `report_attestation_head` or explicit absence, attestation allowlist validation, final push state, PR publication state, and exact-head CI state. **Do not call `report-output-manager` attestation-persistence phase, create another attestation commit, invoke `git-pr-submitter` again, push again, or wait for CI again.**
24. After terminal completion, allow only Git-HEAD-neutral caller work that is not already represented by the returned evidence, such as a concise PR comment, review request, external Issue update, or inline/branch-external handoff transport. Do not duplicate final publication or CI waiting already owned by `review-enforcer`.
25. Do not commit task, design, Skill, workflow, configuration, feedback, handoff, report, or implementation changes after the attestation head. Return final handoff inline/outside reviewed PR branch.
26. Return to task confirmation. Starting another task begins a new lifecycle and must not append commits to the completed attestation pair.

## Independent-final terminal ownership

The independent-final terminal lifecycle has exactly one owner: `review-enforcer`.

`development-orchestrator` owns only readiness before that boundary and consumption after it. It must not directly invoke any of these terminal operations:

- independent-final `report-output-manager` reservation-only phase,
- reviewed implementation HEAD freeze,
- independent reviewer identity/lifecycle management,
- report-attestation persistence,
- report-attestation commit creation or allowlist validation,
- final push,
- final PR creation/update,
- exact-head required `pull_request` CI wait.

A returned `review-enforcer` terminal result is authoritative lifecycle evidence. Repeating any terminal operation after that result risks a second reservation, a second attestation commit, duplicate publication, or duplicate CI gating and is prohibited.

## Dispatch-profile policy

The workflow must preserve the distinction between:

- executor choice and multi-agent decomposition, owned by `codex-delegation-executor`
- per-task model, reasoning effort, fork policy, truthful decomposability, decomposition policy, agent-role/default-role planning, expensive-profile proposal state, and runtime-profile observability, owned by `sub-agent-task-manager`
- explicit user/repository overrides, subject to mandatory user-approval gate for Sol `xhigh` and Sol `max`

The parent records delegation assessment, proposal/approval evidence, requested profile, role plan, planned runtime profile, runtime observability, exact applied profile when observable, and application status. It does not infer success from a model name in child prompt or from spawn success alone.

When final model/reasoning metadata is not parent-visible, preserve `applied: null` and an explicit state such as `spawn_succeeded_profile_unverified`; do not fabricate an exact applied profile. This unverified state is valid lifecycle evidence, not automatic success/failure of the delegated task itself.

Sol `xhigh` and Sol `max` are a user-confirmation boundary for cost optimization. If initial selection or role/default-role planning proposes either, parent must explain why Sol `high` is insufficient, disclose higher execution cost, and stop before dispatch. Repository policy cannot waive confirmation. Explicit current-task user instruction counts as approval; prior unrelated approval/silence does not.

A dispatch classification must be recomputed when investigation/implementation changes task kind, uncertainty, change radius, criticality, or known role-adjusted runtime plan. Failed deterministic verification becomes investigation. Independently separable work returns to `codex-delegation-executor` only when decomposition policy permits; identity-sensitive review may preserve `decomposability: independent_workstreams` while suppressing decomposition by policy. Full-history/role constraints remain explicit runtime planning evidence. If user rejects expensive-profile proposal, recompute with Sol `xhigh`/`max` excluded.

## Report-attestation terminal rule

`review-enforcer` owns application of this terminal rule. `development-orchestrator` consumes and checks the returned evidence but does not re-execute the rule.

An independent-final-review verdict remains attached to its reviewed implementation HEAD. A later Git HEAD may be accepted only as a report-attestation head when all conditions below hold:

- exactly one commit follows reviewed implementation HEAD,
- its first parent is reviewed implementation HEAD,
- only independent-final-review report path(s) reserved by the `review-enforcer` pre-freeze reservation identity are changed,
- report identifies reviewed implementation HEAD and states commit is administrative attestation rather than reviewed implementation,
- automated/explicit diff check confirms no executable, Skill, design, workflow, configuration, task-tracking, feedback, handoff, or product file changed,
- no later repository commit exists.

Completion identity is `reviewed implementation HEAD + validated report-attestation HEAD`. Any other post-review commit invalidates completion and requires normal fix verification followed by same independent reviewer's bounded finding/CI-delta closure under `review-enforcer`.

After terminal completion, only operations that do not change Git HEAD are permitted: PR body/comment updates not already performed, review requests, external Issue operations, and branch-external/inline transport. Discovery of required repository write invalidates terminal state and returns workflow to normal cycle through `review-enforcer`.

## Core rules

- Work on one task at a time.
- Do not start implementation/resume flows from another standard entry point.
- Do not select a task while run target remains ambiguous.
- Do not treat implementation as complete before required validation, review, progress synchronization, commit, and PR creation.
- Do not skip task reconciliation, design reflection, review, or progress updates.
- Do not enter workflow on stale local Skills when safe latest synchronization was available.
- Do not trust workflow entry until `AGENTS.md` contains required Skill-first constraints or user has been explicitly notified.
- Do not skip parent-owned end-of-Issue Skill-gap reflection.
- Complete Skill action decisions, feedback classification/ledger synchronization, normal handoff persistence, reports, and tracking before independent-final terminal lifecycle begins.
- If any of those actions changes repository, require validation and normal review before entering terminal lifecycle again.
- Do not leave substantial local Skill changes without explicit caller.
- Do not choose parent versus sub-agent implementation outside `codex-delegation-executor`.
- Do not hardcode or routinely confirm implementation sub-agent model when no explicit override exists, except mandatory Sol `xhigh`/`max` gate.
- Never dispatch Sol `xhigh` or Sol `max` without explicit current-task user approval, including role-adjusted proposals.
- Do not bypass `sub-agent-task-manager` profile/role planning for delegated work.
- Do not falsify `decomposability` to enforce one-agent policy; record policy separately.
- Do not claim exact `applied` when final runtime profile is hidden.
- Treat design editing, test authoring, code authoring, documentation, configuration, and workflow editing as implementation work owned through applicable executor.
- Do not call `tdd-executor` merely because code/tests may change. Call it only when target repository explicitly requires TDD.
- CodexSkill repository maintenance is non-TDD unless user explicitly changes that policy.
- When work is delegated, make sub-agent read applicable wrapper/core Skill files instead of relying only on paraphrased prompt.
- Do not make delegated tasks re-enter this orchestration Skill unless orchestration analysis itself was delegated.
- Do not use deleted or repository-external `shared/` contracts as fallback.
- Stop/re-plan when required work is missing from task tracking.
- Do not reserve the independent-final report path or freeze the reviewed implementation HEAD outside `review-enforcer`.
- Do not call attestation persistence, create a second report-attestation commit, repeat final push/PR publication, or wait for final exact-head CI after `review-enforcer` has completed those operations.
- After report attestation, do not call any Skill that can write to reviewed repository branch.

## Outputs

After this Skill runs, workflow has:

- one explicitly selected task,
- structured context from `work-context-manager`,
- governing target-project development/testing policy,
- concrete route through applicable wrapper/core Skills,
- executor and decomposition decision/policy,
- delegation assessment plus proposal/approval evidence when applicable,
- requested profile, role/default-role plan, planned runtime profile, runtime observability, and exact applied profile when observable or explicit unverified/capability state for every dispatched sub-agent task,
- resolved `verification_capability` and separate commit/push/CI-wait evidence,
- implementation/validation evidence or explicit blocking condition,
- review/report/tracking/Skill-action/feedback state,
- `review-enforcer` terminal evidence including the single reservation identity, reviewed implementation HEAD, report-attestation head or explicit absence, attestation validation, final publication state, and exact-head CI state.

## Completion condition

A task cycle is complete only when:

- accepted implementation is complete or explicitly blocked,
- target-project-required tests/validation are recorded,
- TDD was applied only when required and otherwise recorded not applicable,
- normal review and independent final review are complete,
- delegated work records requested/role-plan evidence and either exact applied profile or an explicit unverified/inherited/fallback/capability state,
- any initial/role-adjusted Sol `xhigh`/`max` dispatch has explicit current-task approval evidence,
- required non-final reports/tracking/Skill decisions/feedback/normal handoffs were committed before independent-final terminal lifecycle,
- any repository change discovered during pre-freeze finalization returned through validation/normal review,
- `review-enforcer` created exactly one independent-final reservation identity and, when persistence was required, at most one validated report-attestation commit,
- this Skill did not repeat reservation, attestation persistence, final push, PR publication, or exact-head CI waiting after consuming `review-enforcer` completion,
- no repository-writing Skill ran after attestation head,
- terminal PR/CI evidence is complete or explicitly blocked,
- no merge was performed.

## What this Skill must not do

- Do not contain detailed agent profile selection matrix.
- Do not contain detailed TDD instructions.
- Do not contain detailed Git instructions beyond lifecycle boundary needed to keep review finite.
- Do not contain detailed review criteria.
- Do not directly replace child Skills.
- Do not bypass `codex-delegation-executor` when executable work needs an owner decision.
