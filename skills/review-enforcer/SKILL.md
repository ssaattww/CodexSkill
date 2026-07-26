---
name: review-enforcer
description: Coordinate runtime-neutral review through Codex reviewer sub-agents, reviewer continuity, independent final review, and completion gates.
---

# Codex Review Wrapper

## Goal

Act as the Codex runtime wrapper for review without redefining review semantics.

## Required Skills

Invoke:

1. `work-context-manager`
2. `review-worker`
3. `report-writer`

Do not replace these Skills with `shared/` files.

## Codex reviewer lifecycle

### Normal review cycle

Use one dedicated reviewer sub-agent for initial review and fix verification while available. Preserve finding identity, reviewed HEAD, selected criteria, and fix context.

### Independent final review

After the normal cycle converges, start a different fresh reviewer sub-agent. It must differ from the implementation agent and normal reviewer, must not have implemented fixes, and should use `fork_turns: "none"` unless a bounded exception is justified.

## Required flow

1. Invoke `work-context-manager` for the current PR HEAD and matching evidence.
2. Run applicable Markdown gates.
3. Dispatch a reviewer sub-agent that invokes `review-worker` in the selected mode.
4. Invoke `report-writer` and persist through `report-output-manager`.
5. Return required findings to the implementation flow.
6. Reuse the normal reviewer for fix verification when available.
7. After convergence, dispatch a fresh independent final reviewer against the unchanged current HEAD.
8. If HEAD changes, repeat normal fix verification and independent final review.

## Codex responsibilities

- Parent owns reviewer identity, sub-agent dispatch, report path reservation, lifecycle gating, and integration.
- Parent review cannot replace reviewer sub-agent work.
- Do not cancel a reviewer merely because it is slow.
- Reviewers do not implement findings.
- Do not reuse a verdict from an earlier HEAD.
- Do not merge.

## Completion condition

Complete only when the required Skills have produced normal review and independent-final-review evidence for the unchanged current HEAD, required reports exist, reviewer independence is recorded, no unresolved blocking finding or verdict-invalidating unexplored area remains, and no merge was performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.
