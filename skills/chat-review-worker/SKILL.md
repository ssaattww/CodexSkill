---
name: chat-review-worker
description: Coordinate review in one ChatGPT chat by invoking runtime-neutral Skills and adding ChatGPT-specific reviewer continuity, permissions, persistence, PR, and handoff behavior.
---

# Chat Review Wrapper

## Goal

Act as the ChatGPT runtime wrapper for review. The user is the parent. This Skill must not redefine review semantics.

## Required Skills

Invoke these Skills in order:

1. `work-context-manager`
2. `review-worker`
3. `report-writer`
4. `chat-handoff-manager`

All four must be installed. Do not replace them with repository-external shared files or locally reproduced core logic.

## Modes

- `initial review`
- `fix verification`
- `independent final review`

Use the same normal review chat for initial review and fix verification when available. Independent final review must use a fresh chat that did not implement, fix, or perform normal review.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve permissions before repository writes or PR comments.
- Validate reviewer continuity or independence before invoking `review-worker`.
- Resolve the exact reviewed implementation HEAD and use only matching validation and CI evidence.
- Persist the detailed review report under target-repository rules, or return it in full.
- Post the concise PR review comment when authorized, or return its complete body.
- Persist normal-review and fix-verification handoffs under target-repository rules, or return complete packets.
- The user chooses the next chat and merge action.

## Normal review flow

1. Invoke `work-context-manager` for the current committed review target, requirements, design, previous findings, reports, tracking, and matching evidence.
2. Invoke `review-worker` for initial review or fix verification.
3. Invoke `report-writer` and persist the detailed report before the branch is considered ready for independent final review.
4. Invoke `chat-handoff-manager` with the complete review output; do not omit findings, coverage, held, unexplored, or reviewed-HEAD evidence.
5. Required fixes return to the implementation chat. Before closure review,
   require the per-finding required-action / production-path / actual
   composition-fixture / focused-evidence matrix. After fixes, route-appropriate
   validation, report, tracking, and a review-target commit, reuse the same
   normal review chat when available. Do not require local-route CI waiting.

## Independent final review flow

Before starting the one fresh independent-final-review chat:

- all implementation, design, workflow, configuration, task-tracking, handoff, and non-final report changes must be committed; local route freezes the validated local committed HEAD without pre-review push, while remote-CI-only records authorized pre-review push and matching current-HEAD CI,
- the independent-final-review report path or paths must be reserved,
- the route-selected committed HEAD must be frozen as `reviewed_implementation_head`.

Then:

1. Invoke `work-context-manager` for the frozen implementation HEAD and matching evidence.
2. Validate that this chat is independent from implementation, review fixes, and normal review.
3. Invoke `review-worker` in `independent final review` mode.
4. If the verdict requires a fix, do not persist a passing attestation. Return to normal implementation and fix verification, then reuse this same independent chat only for finding/CI-delta closure against the updated reviewed HEAD; do not begin another exhaustive independent review.
5. When the verdict passes, invoke `report-writer` with the pre-reserved report path and the reviewed implementation HEAD.
6. Persist at most one report-attestation commit. Its first parent must be the reviewed implementation HEAD, and its diff may change only the reserved independent-final-review report path or paths.
7. Validate and record the attestation diff. Treat the completion identity as `reviewed implementation HEAD + report-attestation HEAD`.
8. Make the final authorized push, then create or update the PR with the current-chat GitHub connector for that exact HEAD. Wait once after publication for exact-head required `pull_request` CI. For `remote_ci_only`, matching current-HEAD CI can be formal route evidence; do not wait for an unrequired `push` run.
9. Post or update the concise PR comment after the attestation commit; PR comments and PR body changes do not change Git HEAD.
10. Invoke `chat-handoff-manager` and return the final packet inline or transport it outside the PR branch. Do not commit a handoff after the report-attestation head.

Any other post-review repository commit invalidates completion and requires normal fix verification followed by same-reviewer bounded finding/CI-delta closure.

## Boundaries

- Do not start another worker or sub-agent.
- Do not implement findings.
- Do not redefine review criteria locally when `review-worker` is unavailable; report the missing dependency.
- Do not exceed current-chat permissions.
- Do not reuse a verdict after the reviewed implementation HEAD changes.
- Do not commit tracking, design, Skill, workflow, configuration, implementation, or handoff changes after independent final review.
- Do not create more than one report-attestation commit.
- Do not merge.

## Outputs

Return or persist:

- review mode,
- reviewed implementation HEAD,
- reviewer continuity or independence evidence,
- full coverage dispositions, findings, held items, unexplored areas, validation assessment, and verdict,
- detailed report path or complete body,
- report-attestation head and validated allowlist evidence when applicable,
- PR comment reference or complete body,
- complete handoff packet or external transport reference,
- remaining risks and next action.

## Completion condition

Complete when the required Skills have produced context, complete review evidence, verdict, report output, and a lossless handoff; authorized PR updates are complete; reviewer continuity or independence is explicit; and either the reviewed implementation HEAD remains unchanged or exactly one validated report-attestation commit exists with no later repository commit. No merge is performed.
