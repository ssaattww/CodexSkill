---
name: chat-implementation-worker
description: Coordinate implementation in one ChatGPT chat by invoking runtime-neutral Skills and adding ChatGPT-specific permissions, persistence, PR, and handoff behavior.
---

# Chat Implementation Wrapper

## Goal

Act as the ChatGPT runtime wrapper for implementation. The user is the parent. This Skill must not redefine implementation semantics.

## Required Skills

Invoke these Skills in order:

1. `work-context-manager`
2. `implementation-worker`
3. `report-writer`
4. `chat-handoff-manager`

All four must be installed. Do not replace them with repository-external shared files.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve permissions before writes.
- Apply changes, commit, push, and create or update the PR only when authorized.
- Persist the detailed implementation report under target-repository rules, or return it in full when writing is unavailable.
- Post the concise PR comment when authorized, or return its complete body.
- Persist the handoff under target-repository rules, or return the complete packet for copy and paste.
- The user chooses the next chat and merge action.

## Modes

- `initial implementation`
- `review follow-up`

Pass the selected mode and resolved context to `implementation-worker`.

## Boundaries

- Do not start another worker or sub-agent.
- Do not implement rules locally when the required Skill is unavailable; report the missing dependency.
- Do not issue an independent review verdict.
- Do not exceed current-chat permissions.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context, implementation evidence, report output, and a transportable handoff; authorized repository and PR updates are complete; final HEAD and matching CI evidence or explicit absence are recorded; and no merge was performed.
