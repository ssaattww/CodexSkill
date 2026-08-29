---
name: review-enforcer
description: Coordinate runtime-neutral review through Codex reviewer sub-agents, reviewer continuity, independent final review, report attestation, and completion gates.
---

# Codex Review Wrapper

## Goal

Act as the Codex runtime wrapper for review without redefining review semantics, and enforce a finite lifecycle between immutable reviewed implementation content and repository-persisted review evidence.

## Required Skills

Invoke:

1. `work-context-manager`
2. `sub-agent-task-manager`
3. `review-worker`
4. `report-writer`
5. `report-output-manager`

Use `report-writer` only in phases where report content is actually generated. Independent-final reservation uses `report-output-manager`'s reservation-only phase and must not invoke `report-writer` before review evidence exists.

Do not replace these Skills with `shared/` files or duplicate their semantics locally.

## Reviewer dispatch contract

Every newly created reviewer sub-agent must be dispatched through `sub-agent-task-manager` as one identity-bearing reviewer execution.

- `review-enforcer` owns reviewer identity, continuity, independence, review mode, one-reviewer execution policy, report persistence mode, and lifecycle state.
- `sub-agent-task-manager` owns per-task model, reasoning effort, fork policy, role/default-role planning, expensive-profile approval gating, runtime-profile evidence, and dispatch.
- Every new reviewer task created by this Skill must set `decomposition_policy: forbidden` and `parallelism_mode: single_agent`.
- `decomposability` remains a truthful observed signal. Do not force it to `single` merely because execution decomposition is forbidden.
- If the review scope contains independently executable review areas, record `decomposability: independent_workstreams` together with `decomposition_disposition: prohibited_by_review_lifecycle`.
- Reviewer breadth never authorizes multi-agent execution in the current lifecycle. Large reviews remain one reviewer because normal-review continuity and the independent one-exhaustive-pass guarantee are identity-sensitive execution contracts.
- If `sub-agent-task-manager` produces an unapproved Sol `xhigh` or Sol `max` `proposed_profile`, return that proposal to the parent and stop before spawning the reviewer.
- Role/default-role planning is subject to the same approval gate. A role must not raise the effective plan to Sol `xhigh`/`max` without current-task approval.
- Do not bypass the proposal or role-profile capability stop by directly spawning a reviewer from this Skill.
- A reviewer that already exists is reused directly for continuity; reuse is not a new profile selection or new spawn.

When an existing reviewer is reused, preserve its original runtime-profile evidence and observability state. Record `application_status: reused_existing_agent_profile`, reviewer identity, original exact/unverified profile evidence, and continued review mode. Do not claim a new default was applied to an already-running reviewer.

## Report persistence by review mode

Use two distinct report modes.

### Normal review and fix verification

Use `report_persistence_mode: normal_persistence`.

- `sub-agent-task-manager` may pre-create the normal-review report from the standard template
- the reviewer may fill child-owned report sections directly
- parent-owned dispatch-profile fields are completed from pre-spawn planning and post-runtime observability evidence
- persist and commit these reports before the independent-final-review target is frozen

### Independent final review and bounded independent closure

Use `report_persistence_mode: deferred_attestation`.

- call `report-output-manager` in reservation-only phase before freeze
- reserve the exact independent-final-review report path as metadata only
- do not invoke `report-writer` during reservation
- do not create, pre-populate, or edit the repository report path before/during independent review
- the independent reviewer returns structured review evidence to the parent instead of editing a report file
- the parent retains reviewer output and dispatch-profile evidence outside frozen repository content
- only after a passing verdict may `report-writer` and `report-output-manager` materialize that evidence into the reserved path as the single report-attestation commit

If the independent review finds required changes, keep its evidence as parent-owned lifecycle state, invalidate terminal state, return through implementation and normal fix verification, and later reuse the same independent reviewer for bounded closure without creating the reserved report file. Persist only after that independent lifecycle reaches a passing verdict.

## Codex reviewer lifecycle

### Normal review cycle

Use one dedicated reviewer sub-agent for initial review and fix verification while available. Create that reviewer through `sub-agent-task-manager` with decomposition forbidden and normal persistence. Preserve truthful decomposability, finding identity, reviewed HEAD, selected criteria, held/unexplored items, fix context, reviewer identity, and original runtime-profile/observability evidence.

Persist normal-review and fix-verification reports, synchronize tracking, and commit all resulting repository changes before selecting the independent-final-review target. Push and CI waiting remain separate, verification-route-owned states.

### Independent final review

After the normal cycle converges:

- finish every implementation, design, workflow, configuration, tracking, feedback-ledger, normal handoff, and non-final report change,
- finish the parent-owned end-of-Issue Skill-gap decision and execute any in-scope Skill update,
- reserve the independent-final-review report path or paths without creating those files,
- commit all other changes,
- for `local_execution_available`, freeze the validated local committed HEAD without pre-review push; for `remote_ci_only`, complete authorized pre-review push and matching current-HEAD CI,
- freeze that HEAD as `reviewed_implementation_head`,
- ask `sub-agent-task-manager` to prepare one different fresh reviewer sub-agent with decomposition forbidden and deferred attestation.

The independent reviewer must differ from the implementation agent and normal reviewer, must not have implemented fixes, must remain one reviewer for the entire independent lifecycle, and should use `fork_turns: "none"` unless a bounded exception is justified.

If independent-final-review profile or role planning proposes Sol `xhigh` or Sol `max`, stop before reviewer creation and return the proposal to the user. Continue only after explicit current-task approval. If role/default-role impact cannot be inspected sufficiently to enforce this gate, stop with a capability gap instead of dispatching.

## Required flow

1. Invoke `work-context-manager` for the current committed HEAD and matching evidence.
2. Run applicable Markdown and repository gates.
3. Classify the normal-review task truthfully, including observed `decomposability`; set `decomposition_policy: forbidden`, `parallelism_mode: single_agent`, and when relevant `decomposition_disposition: prohibited_by_review_lifecycle`.
4. Ask `sub-agent-task-manager` to select/plan/dispatch one new normal reviewer using `report_persistence_mode: normal_persistence`. If expensive-profile approval or role-profile safety is unresolved, stop before spawn.
5. Invoke `report-writer` and persist normal-review evidence through `report-output-manager`.
6. Return required findings to the implementation flow.
7. Reuse the normal reviewer for fix verification when available. Preserve original exact/unverified runtime-profile evidence; record `application_status: reused_existing_agent_profile`.
8. Before requesting finding closure, require a finding-by-finding completeness matrix covering every required action, production path, actual composition fixture, and focused evidence. Do not dispatch closure review while any cell is incomplete.
9. After each fix, require route-appropriate validation, report/tracking synchronization, and a review-target commit before another normal-review round. On `local_execution_available`, do not wait for CI in this loop; on `remote_ci_only`, record matching current-HEAD CI after authorized push when required for formal verification.
10. After convergence, verify that the parent completed end-of-Issue Skill-gap decision, any in-scope `skill-authoring-wrapper` work, feedback classification/ledger synchronization, normal handoff persistence, reports, and tracking.
11. If step 10 creates/discovers repository change, require route-appropriate validation, commit, and another normal review/fix-verification round. Do not freeze yet.
12. Only after normal convergence with all pre-freeze work included, ensure every non-final repository change is committed. On local route, require the repository-defined full local gate before final push. Call `report-output-manager` reservation-only phase to reserve independent-final-review report path as metadata, then freeze implementation HEAD.
13. Classify the independent-review task truthfully, including observed `decomposability`; set `decomposition_policy: forbidden`, `parallelism_mode: single_agent`, and relevant disposition.
14. Ask `sub-agent-task-manager` to select/plan one fresh independent final reviewer using `report_persistence_mode: deferred_attestation`. If expensive-profile approval or role-profile safety is unresolved, stop before spawn. After approval/safe planning, dispatch that one reviewer without creating the reserved report file.
15. Retain structured findings, coverage, commands/evidence, verdict, risks, unexplored areas, truthful decomposability/policy evidence, and runtime-profile observability evidence as parent-owned lifecycle evidence.
16. If the one exhaustive independent review finds required changes, invalidate terminal state, return to implementation and normal fix verification, then reuse the same independent reviewer only for finding/CI-delta closure against updated reviewed HEAD. Preserve original runtime-profile/observability evidence; do not spawn another fresh exhaustive reviewer, execute multi-agent review, add new review criteria, or create reserved report file.
17. When the independent lifecycle reaches a passing verdict, call `report-output-manager` attestation-persistence phase; only then invoke `report-writer` with retained complete evidence and the pre-reserved path.
18. Persist at most one report-attestation commit whose first parent is reviewed implementation HEAD and changed paths are limited to pre-reserved independent-final-review report paths.
19. Validate attestation diff, make final authorized push, then invoke `git-pr-submitter` or authorized equivalent for that exact HEAD. Wait once after publication for exact-head required `pull_request` CI. Do not wait for unrequired `push` run.
20. After attestation commit, permit only operations that do not change Git HEAD: PR body/comment updates, review requests, external Issue operations, and inline/branch-external handoff transport.
21. Do not call repository-writing Skills after attestation and do not commit later handoff/tracking/design/Skill/workflow/configuration/feedback/report/implementation changes.

Any other post-review commit invalidates completion and requires normal fix verification followed by same-reviewer bounded finding/CI-delta closure.

## Pre-freeze gate

The independent-final-review target must not be frozen until all of the following are explicit and repository-stable:

- implementation, validation, design, workflow, configuration, normal reports, and tracking,
- normal review and fix-verification evidence,
- end-of-Issue Skill-gap decision,
- any selected in-scope Skill update,
- feedback classification and any feedback ledger write,
- repository-backed normal handoff,
- independent-final-review report-path reservation as metadata only, with no file created yet,
- current-HEAD validation evidence and verification-route disposition.

For `remote_ci_only`, matching current-HEAD CI may be formal evidence; for local route, do not require CI completion before attestation.

A newly discovered repository write after this gate invalidates it and returns workflow to normal cycle. Creating/editing reserved independent-final-review report before passing verdict also invalidates the gate.

## Report-attestation gate

A report-attestation head is acceptable only when:

- exactly one commit follows reviewed implementation HEAD,
- commit first parent is reviewed implementation HEAD,
- only pre-reserved independent-final-review report paths changed,
- those paths did not exist/change during frozen independent review,
- report names reviewed implementation HEAD and identifies commit as administrative attestation,
- no executable, Skill, design, workflow, configuration, tracking, feedback, handoff, or product path changed,
- no later repository commit exists.

Technical verdict remains attached to reviewed implementation HEAD. Attestation commit does not expand reviewed implementation scope.

## Codex responsibilities

- Parent owns reviewer identity, continuity, independence, single-reviewer execution policy, truthful decomposability evidence, report-path reservation, retained independent evidence, pre-freeze gating, lifecycle gating, attestation validation, and integration.
- `sub-agent-task-manager` owns every new reviewer spawn/profile/role plan/runtime observability evidence and must honor no-decomposition/report-persistence constraints.
- Parent review cannot replace reviewer sub-agent work.
- Do not cancel a reviewer merely because it is slow.
- Reviewers do not implement findings.
- Do not reuse a verdict from an earlier implementation HEAD.
- Do not create more than one report-attestation commit.
- Do not permit a repository-writing Skill after attestation.
- Do not merge.

## Outputs

Return:

- normal review and fix-verification evidence,
- pre-freeze gate evidence,
- independent-final-review evidence retained outside frozen repository until attestation,
- reviewed implementation HEAD,
- report-attestation head or explicit absence,
- attestation allowlist validation,
- reviewer identity and independence evidence,
- reviewer dispatch-profile evidence including role plan, runtime observability, and any expensive-profile approval,
- reviewer continuity evidence including `reused_existing_agent_profile` when applicable,
- truthful `decomposability`, `decomposition_policy`, and decomposition disposition for every review dispatch,
- full findings, coverage, held/unexplored items, validation assessment, verdict, remaining risks, next action,
- finding completeness matrix and verification capability with separate commit/push/CI-wait evidence.

## Completion condition

Complete only when required Skills produced normal-review and independent-final-review evidence; every new reviewer went through `sub-agent-task-manager` under single-agent execution policy without falsifying decomposability; any required initial/role-adjusted Sol `xhigh`/`max` approval preceded reviewer spawn; runtime-profile observability uncertainty is preserved; reused reviewers preserved original profile evidence; independent reviewer did not write reserved report path before passing; all non-final repository changes and mandatory end-of-Issue/feedback work preceded frozen reviewed implementation HEAD; no unresolved required finding or verdict-invalidating unexplored area remains; and either no report commit was required or exactly one validated report-attestation head exists with no later repository commit/writing Skill. No merge is performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager` and persist any resulting repository change before freezing the independent-final-review target. After freeze, record newly discovered feedback only through a non-Git external operation or invalidate terminal state and return to normal cycle.
