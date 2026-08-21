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
2. `review-worker`
3. `report-writer`
4. `report-output-manager`

Do not replace these Skills with `shared/` files or duplicate their semantics locally.

## Codex reviewer lifecycle

### Normal review cycle

Use one dedicated reviewer sub-agent for initial review and fix verification while available. Preserve finding identity, reviewed HEAD, selected criteria, held and unexplored items, and fix context.

Persist normal-review and fix-verification reports, synchronize tracking, and
commit all resulting repository changes before selecting the
independent-final-review target. Push and CI waiting remain separate,
verification-route-owned states.

### Independent final review

After the normal cycle converges:

- finish every implementation, design, workflow, configuration, tracking, feedback-ledger, normal handoff, and non-final report change,
- finish the parent-owned end-of-Issue Skill-gap decision and execute any in-scope Skill update,
- reserve the independent-final-review report path or paths,
- commit those changes,
- for `local_execution_available`, freeze the validated local committed HEAD without pre-review push; for `remote_ci_only`, complete authorized pre-review push and matching current-HEAD CI,
- freeze that HEAD as `reviewed_implementation_head`,
- start a different fresh reviewer sub-agent.

The independent reviewer must differ from the implementation agent and normal reviewer, must not have implemented fixes, and should use `fork_turns: "none"` unless a bounded exception is justified.

## Required flow

1. Invoke `work-context-manager` for the current committed HEAD and matching evidence.
2. Run applicable Markdown and repository gates.
3. Dispatch a normal reviewer sub-agent that invokes `review-worker` in the selected mode.
4. Invoke `report-writer` and persist through `report-output-manager`.
5. Return required findings to the implementation flow.
6. Reuse the normal reviewer for fix verification when available.
7. Before requesting finding closure, require a finding-by-finding completeness
   matrix covering every required action, production path, actual composition
   fixture, and focused evidence. Do not dispatch closure review while any cell
   is incomplete.
8. After each fix, require route-appropriate validation, report and tracking
   synchronization, and a review-target commit before another review round. On
   `local_execution_available`, do not wait for CI in this loop; on
   `remote_ci_only`, record matching current-HEAD CI evidence after authorized
   push when it is required for formal verification.
9. After convergence, verify that the parent has completed the end-of-Issue Skill-gap decision, any in-scope `skill-authoring-wrapper` work, feedback classification and ledger synchronization, normal handoff persistence, reports, and tracking.
10. If step 9 creates or discovers any repository change, require route-appropriate validation, commit, and another normal review or fix-verification round. Do not freeze the target yet.
11. Only after the normal cycle converges again with all pre-freeze work included, ensure every non-final repository change is committed. On the local route, require the repository-defined full local gate before final push. Reserve the independent-final-review report path, and freeze the implementation HEAD.
12. Dispatch a fresh independent final reviewer against that frozen implementation HEAD.
13. If the one exhaustive independent review finds required changes, invalidate the terminal state, return to implementation and normal fix verification, then reuse that same independent reviewer only for finding/CI-delta closure against the updated reviewed HEAD. Do not spawn another fresh exhaustive reviewer or add new review criteria.
14. When the verdict passes, invoke `report-writer` and `report-output-manager` in report-attestation mode.
15. Persist at most one report-attestation commit whose first parent is the reviewed implementation HEAD and whose changed paths are limited to the pre-reserved independent-final-review report path or paths.
16. Validate the attestation diff, make the final authorized push, then invoke `git-pr-submitter` or the authorized equivalent to create or update the PR for that exact HEAD. Wait once after publication for exact-head required `pull_request` CI. Do not wait for an unrequired `push` run.
17. After the attestation commit, permit only operations that do not change Git HEAD: PR body or comment updates, review requests, external Issue operations, and inline or branch-external handoff transport.
18. Do not call any repository-writing Skill after attestation and do not commit any later handoff, tracking, design, Skill, workflow, configuration, feedback, report, or implementation change.

Any other post-review commit invalidates completion and requires normal fix verification followed by same-reviewer bounded finding/CI-delta closure.

## Pre-freeze gate

The independent-final-review target must not be frozen until all of the following are explicit and repository-stable:

- implementation, validation, design, workflow, configuration, reports, and tracking,
- normal review and fix-verification evidence,
- end-of-Issue Skill-gap decision,
- any selected in-scope Skill update,
- feedback classification and any feedback ledger write,
- repository-backed normal handoff,
- current-HEAD validation evidence and verification-route disposition. For
  `remote_ci_only`, matching current-HEAD CI may be formal evidence; for the
  local route, do not require CI completion before attestation.

A newly discovered repository write after this gate invalidates the gate and returns the workflow to the normal cycle.

## Report-attestation gate

A report-attestation head is acceptable only when:

- exactly one commit follows the reviewed implementation HEAD,
- the commit's first parent is the reviewed implementation HEAD,
- only pre-reserved independent-final-review report paths changed,
- the report names the reviewed implementation HEAD and identifies the commit as administrative attestation,
- no executable, Skill, design, workflow, configuration, tracking, feedback, handoff, or product path changed,
- no later repository commit exists.

The technical verdict remains attached to the reviewed implementation HEAD. The attestation commit does not expand the reviewed implementation scope.

## Codex responsibilities

- Parent owns reviewer identity, sub-agent dispatch, report path reservation, pre-freeze gating, lifecycle gating, attestation validation, and integration.
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
- independent-final-review evidence,
- reviewed implementation HEAD,
- report-attestation head or explicit absence,
- attestation allowlist validation,
- reviewer identity and independence evidence,
- full findings, coverage, held and unexplored items, validation assessment, verdict, remaining risks, and next action.
- finding completeness matrix and verification capability with separate commit,
  push, and CI-wait evidence.

## Completion condition

Complete only when the required Skills have produced normal review and independent-final-review evidence, all non-final repository changes and mandatory end-of-Issue or feedback work preceded the frozen reviewed implementation HEAD, no unresolved required finding or verdict-invalidating unexplored area remains, and either no report commit was required or exactly one validated report-attestation head exists with no later repository commit or repository-writing Skill execution. No merge is performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager` and persist any resulting repository change before freezing the independent-final-review target. After freeze, record newly discovered feedback only through a non-Git external operation or invalidate the terminal state and return to the normal cycle.
