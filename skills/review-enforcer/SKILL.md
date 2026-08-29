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

Do not replace these Skills with `shared/` files or duplicate their semantics locally.

## Reviewer dispatch contract

Every newly created reviewer sub-agent must be dispatched through `sub-agent-task-manager` as one identity-bearing reviewer task.

- `review-enforcer` owns reviewer identity, continuity, independence, review mode, single-reviewer scope, report persistence mode, and lifecycle state.
- `sub-agent-task-manager` owns per-task model, reasoning effort, fork policy, expensive-profile approval gating, runtime application, and dispatch-profile evidence.
- Every reviewer task created by this Skill must set `decomposability: single`, `decomposition_policy: forbidden`, and `parallelism_mode: single_agent`.
- Reviewer breadth never authorizes multi-agent decomposition. Large reviews remain one reviewer because normal-review continuity and the independent one-exhaustive-pass guarantee are identity-sensitive lifecycle contracts.
- If `sub-agent-task-manager` produces an unapproved `Sol xhigh` or `Sol max` `proposed_profile`, return that proposal to the parent and stop before spawning the reviewer.
- Do not bypass the proposal stop by directly spawning a reviewer from this Skill.
- A reviewer that already exists is reused directly for continuity; reuse is not a new profile selection or new spawn.

When an existing reviewer is reused, preserve its originally applied execution profile. Record `application_status: reused_existing_agent_profile`, the original applied profile, the reviewer identity, and the review mode being continued. Do not claim that a new default such as Terra `high` was applied to an already-running Sol reviewer.

## Report persistence by review mode

Use two distinct report modes.

### Normal review and fix verification

Use `report_persistence_mode: normal_persistence`.

- `sub-agent-task-manager` may pre-create the normal-review report from the standard template.
- the reviewer may fill child-owned report sections directly
- parent-owned dispatch-profile fields are completed from actual spawn/runtime evidence
- persist and commit these reports before the independent-final-review target is frozen

### Independent final review and bounded independent closure

Use `report_persistence_mode: deferred_attestation`.

- reserve the exact independent-final-review report path before freeze through `report-output-manager`
- reservation is metadata only; do not create, pre-populate, or edit that repository path before or during independent review
- the independent reviewer returns structured review evidence to the parent instead of editing a report file
- the parent retains reviewer output and dispatch-profile evidence outside the frozen repository content
- only after a passing verdict may `report-writer` and `report-output-manager` materialize that evidence into the reserved path as the single report-attestation commit

If the independent review finds required changes, keep its evidence as parent-owned lifecycle state, invalidate the terminal state, return through implementation and normal fix verification, and later reuse the same independent reviewer for bounded closure without creating the reserved report file. Persist only after that independent lifecycle reaches a passing verdict.

## Codex reviewer lifecycle

### Normal review cycle

Use one dedicated reviewer sub-agent for initial review and fix verification while available. Create that reviewer through `sub-agent-task-manager` with decomposition forbidden and normal persistence. Preserve finding identity, reviewed HEAD, selected criteria, held and unexplored items, fix context, reviewer identity, and the originally applied reviewer profile.

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

The independent reviewer must differ from the implementation agent and normal reviewer, must not have implemented fixes, must remain a single reviewer for the entire independent lifecycle, and should use `fork_turns: "none"` unless a bounded exception is justified.

If independent-final-review profile selection proposes `Sol xhigh` or `Sol max`, stop before reviewer creation and return the proposal to the user. Continue only after explicit current-task approval. If the user rejects the proposal, let `sub-agent-task-manager` recompute the profile with the rejected expensive profiles excluded.

## Required flow

1. Invoke `work-context-manager` for the current committed HEAD and matching evidence.
2. Run applicable Markdown and repository gates.
3. Ask `sub-agent-task-manager` to select the profile for one new normal reviewer with `decomposability: single`, `decomposition_policy: forbidden`, `parallelism_mode: single_agent`, and `report_persistence_mode: normal_persistence`; dispatch that reviewer to invoke `review-worker` in the selected mode. If an expensive Sol proposal is awaiting approval, stop before spawn and return the proposal to the parent.
4. Invoke `report-writer` and persist normal-review evidence through `report-output-manager`.
5. Return required findings to the implementation flow.
6. Reuse the normal reviewer for fix verification when available. Reuse the existing agent and its original applied profile; do not create a new profile or claim that the focused-fix default replaced the running reviewer's profile. Record `application_status: reused_existing_agent_profile`.
7. Before requesting finding closure, require a finding-by-finding completeness matrix covering every required action, production path, actual composition fixture, and focused evidence. Do not dispatch closure review while any cell is incomplete.
8. After each fix, require route-appropriate validation, report and tracking synchronization, and a review-target commit before another normal-review round. On `local_execution_available`, do not wait for CI in this loop; on `remote_ci_only`, record matching current-HEAD CI evidence after authorized push when it is required for formal verification.
9. After convergence, verify that the parent has completed the end-of-Issue Skill-gap decision, any in-scope `skill-authoring-wrapper` work, feedback classification and ledger synchronization, normal handoff persistence, reports, and tracking.
10. If step 9 creates or discovers any repository change, require route-appropriate validation, commit, and another normal review or fix-verification round. Do not freeze the target yet.
11. Only after the normal cycle converges again with all pre-freeze work included, ensure every non-final repository change is committed. On the local route, require the repository-defined full local gate before final push. Reserve the independent-final-review report path as metadata only, and freeze the implementation HEAD.
12. Ask `sub-agent-task-manager` to select the profile for one fresh independent final reviewer with `decomposability: single`, `decomposition_policy: forbidden`, `parallelism_mode: single_agent`, and `report_persistence_mode: deferred_attestation`. If it returns an unapproved `Sol xhigh` or `Sol max` proposal, stop before spawn; after approval, dispatch that single reviewer through `sub-agent-task-manager` without creating the reserved report file.
13. Retain the independent reviewer's structured findings, coverage, commands/evidence, verdict, risks, unexplored areas, and post-runtime dispatch-profile evidence as parent-owned lifecycle evidence.
14. If the one exhaustive independent review finds required changes, invalidate the terminal state, return to implementation and normal fix verification, then reuse that same independent reviewer only for finding/CI-delta closure against the updated reviewed HEAD. Preserve the reviewer's original applied profile and record `application_status: reused_existing_agent_profile`; do not spawn another fresh exhaustive reviewer, decompose the review, add new review criteria, or create the reserved report file.
15. When the independent lifecycle reaches a passing verdict, invoke `report-writer` and `report-output-manager` in report-attestation mode using the retained reviewer evidence and pre-reserved path.
16. Persist at most one report-attestation commit whose first parent is the reviewed implementation HEAD and whose changed paths are limited to the pre-reserved independent-final-review report path or paths.
17. Validate the attestation diff, make the final authorized push, then invoke `git-pr-submitter` or the authorized equivalent to create or update the PR for that exact HEAD. Wait once after publication for exact-head required `pull_request` CI. Do not wait for an unrequired `push` run.
18. After the attestation commit, permit only operations that do not change Git HEAD: PR body or comment updates, review requests, external Issue operations, and inline or branch-external handoff transport.
19. Do not call any repository-writing Skill after attestation and do not commit any later handoff, tracking, design, Skill, workflow, configuration, feedback, report, or implementation change.

Any other post-review commit invalidates completion and requires normal fix verification followed by same-reviewer bounded finding/CI-delta closure.

## Pre-freeze gate

The independent-final-review target must not be frozen until all of the following are explicit and repository-stable:

- implementation, validation, design, workflow, configuration, normal reports, and tracking,
- normal review and fix-verification evidence,
- end-of-Issue Skill-gap decision,
- any selected in-scope Skill update,
- feedback classification and any feedback ledger write,
- repository-backed normal handoff,
- the independent-final-review report path reservation as metadata only, with no file created yet,
- current-HEAD validation evidence and verification-route disposition. For `remote_ci_only`, matching current-HEAD CI may be formal evidence; for the local route, do not require CI completion before attestation.

A newly discovered repository write after this gate invalidates the gate and returns the workflow to the normal cycle. Creating or editing the reserved independent-final-review report before a passing verdict also invalidates the gate.

## Report-attestation gate

A report-attestation head is acceptable only when:

- exactly one commit follows the reviewed implementation HEAD,
- the commit's first parent is the reviewed implementation HEAD,
- only pre-reserved independent-final-review report paths changed,
- those paths did not exist or change during the frozen independent review itself,
- the report names the reviewed implementation HEAD and identifies the commit as administrative attestation,
- no executable, Skill, design, workflow, configuration, tracking, feedback, handoff, or product path changed,
- no later repository commit exists.

The technical verdict remains attached to the reviewed implementation HEAD. The attestation commit does not expand the reviewed implementation scope.

## Codex responsibilities

- Parent owns reviewer identity, continuity, independence, single-reviewer enforcement, report path reservation, retained independent evidence, pre-freeze gating, lifecycle gating, attestation validation, and integration.
- `sub-agent-task-manager` owns every new reviewer spawn and its dispatch profile, but must honor the caller's no-decomposition and report-persistence constraints.
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
- independent-final-review evidence retained outside the frozen repository until attestation,
- reviewed implementation HEAD,
- report-attestation head or explicit absence,
- attestation allowlist validation,
- reviewer identity and independence evidence,
- reviewer dispatch-profile evidence, including any expensive-profile proposal and approval evidence,
- reviewer continuity evidence, including `reused_existing_agent_profile` when applicable,
- single-reviewer/decomposition-forbidden evidence for every review dispatch,
- full findings, coverage, held and unexplored items, validation assessment, verdict, remaining risks, and next action,
- finding completeness matrix and verification capability with separate commit, push, and CI-wait evidence.

## Completion condition

Complete only when the required Skills have produced normal review and independent-final-review evidence, every newly created reviewer went through `sub-agent-task-manager` as a single non-decomposable reviewer, any required `Sol xhigh` or `Sol max` approval preceded reviewer spawn, reused reviewers preserved their original applied profile, the independent reviewer did not write the reserved report path before passing, all non-final repository changes and mandatory end-of-Issue or feedback work preceded the frozen reviewed implementation HEAD, no unresolved required finding or verdict-invalidating unexplored area remains, and either no report commit was required or exactly one validated report-attestation head exists with no later repository commit or repository-writing Skill execution. No merge is performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager` and persist any resulting repository change before freezing the independent-final-review target. After freeze, record newly discovered feedback only through a non-Git external operation or invalidate the terminal state and return to the normal cycle.
