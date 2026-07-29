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

Persist normal-review and fix-verification reports, synchronize tracking, and commit or push all resulting repository changes before selecting the independent-final-review target.

### Independent final review

After the normal cycle converges:

- finish every implementation, design, workflow, configuration, tracking, handoff, and non-final report change,
- reserve the independent-final-review report path or paths,
- commit and push those changes,
- freeze the current PR HEAD as `reviewed_implementation_head`,
- start a different fresh reviewer sub-agent.

The independent reviewer must differ from the implementation agent and normal reviewer, must not have implemented fixes, and should use `fork_turns: "none"` unless a bounded exception is justified.

## Required flow

1. Invoke `work-context-manager` for the current PR HEAD and matching evidence.
2. Run applicable Markdown and repository gates.
3. Dispatch a normal reviewer sub-agent that invokes `review-worker` in the selected mode.
4. Invoke `report-writer` and persist through `report-output-manager`.
5. Return required findings to the implementation flow.
6. Reuse the normal reviewer for fix verification when available.
7. After each fix, require validation, report and tracking synchronization, commit, push, and current-HEAD evidence before another review round.
8. After convergence, ensure all non-final repository changes are committed and pushed, reserve the independent-final-review report path, and freeze the implementation HEAD.
9. Dispatch a fresh independent final reviewer against that frozen implementation HEAD.
10. If the verdict requires a fix, return to implementation and normal fix verification; do not create a passing attestation.
11. When the verdict passes, invoke `report-writer` and `report-output-manager` in report-attestation mode.
12. Persist at most one report-attestation commit whose first parent is the reviewed implementation HEAD and whose changed paths are limited to the pre-reserved independent-final-review report path or paths.
13. Validate the attestation diff and record the pair `reviewed implementation HEAD + report-attestation HEAD`.
14. Update the PR body or concise PR comment only after the attestation commit; those operations do not change Git HEAD.
15. Do not commit any later handoff, tracking, design, Skill, workflow, configuration, report, or implementation change.

Any other post-review commit invalidates completion and requires normal fix verification followed by another fresh independent final review.

## Report-attestation gate

A report-attestation head is acceptable only when:

- exactly one commit follows the reviewed implementation HEAD,
- the commit's first parent is the reviewed implementation HEAD,
- only pre-reserved independent-final-review report paths changed,
- the report names the reviewed implementation HEAD and identifies the commit as administrative attestation,
- no executable, Skill, design, workflow, configuration, tracking, handoff, or product path changed,
- no later repository commit exists.

The technical verdict remains attached to the reviewed implementation HEAD. The attestation commit does not expand the reviewed implementation scope.

## Codex responsibilities

- Parent owns reviewer identity, sub-agent dispatch, report path reservation, lifecycle gating, attestation validation, and integration.
- Parent review cannot replace reviewer sub-agent work.
- Do not cancel a reviewer merely because it is slow.
- Reviewers do not implement findings.
- Do not reuse a verdict from an earlier implementation HEAD.
- Do not create more than one report-attestation commit.
- Do not merge.

## Outputs

Return:

- normal review and fix-verification evidence,
- independent-final-review evidence,
- reviewed implementation HEAD,
- report-attestation head or explicit absence,
- attestation allowlist validation,
- reviewer identity and independence evidence,
- full findings, coverage, held and unexplored items, validation assessment, verdict, remaining risks, and next action.

## Completion condition

Complete only when the required Skills have produced normal review and independent-final-review evidence, all non-final repository changes preceded the frozen reviewed implementation HEAD, no unresolved required finding or verdict-invalidating unexplored area remains, and either no report commit was required or exactly one validated report-attestation head exists with no later repository commit. No merge is performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager` before freezing the independent-final-review target or record it as follow-up work.
