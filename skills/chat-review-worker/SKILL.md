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

All four must be installed. Do not replace them with repository-external shared files.

## Modes

- `initial review`
- `fix verification`
- `independent final review`

Use the same normal review chat for initial review and fix verification when available. Independent final review must use a fresh chat that did not implement, fix, or perform normal review.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve permissions before repository writes or PR comments.
- Validate reviewer continuity or independence before invoking `review-worker`.
- Persist the detailed review report under target-repository rules, or return it in full.
- Post the concise PR review comment when authorized, or return its complete body.
- Persist the handoff under target-repository rules, or return the complete packet.
- The user chooses the next chat and merge action.

## Boundaries

- Do not start another worker or sub-agent.
- Do not implement findings.
- Do not redefine review criteria locally when `review-worker` is unavailable; report the missing dependency.
- Do not exceed current-chat permissions.
- Do not reuse a verdict after HEAD changes.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context, review coverage, findings, verdict, report output, and a transportable handoff; authorized PR updates are complete; reviewer continuity or independence is explicit; and no merge was performed.
