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
2. `task-consistency-manager`
3. `task-breakdown-planner` when tracking is missing, vague, or must be split
4. `implementation-worker`
5. `progress-sync-manager`
6. `report-writer`
7. `chat-handoff-manager`

All seven Skills must be installed. Do not replace any required Skill with repository-external shared files.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve permissions before writes.
- Use `work-context-manager` to resolve the canonical task tracking path and optional canonical phase tracking path from project/repository authority.
- Pass those resolved tracking paths unchanged to every task tracking Skill; never substitute guessed basenames.
- Confirm the accepted work is represented in canonical task tracking before significant implementation starts.
- Add or split task tracking through `task-breakdown-planner` when required, then re-run `task-consistency-manager`.
- Apply changes, commit, push, and create or update the PR only when authorized.
- Synchronize canonical task and phase state through `progress-sync-manager` after implementation progress, validation, review follow-up, PR/commit updates, or blocking state changes.
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
- Do not invoke optional sub-agent delegation described by a dependency Skill; this wrapper executes required task tracking operations in the current chat.
- Do not implement rules locally when a required Skill is unavailable; report the missing dependency.
- Do not edit canonical task tracking directly outside the task tracking Skills.
- Do not guess canonical tracking paths when `work-context-manager` cannot resolve them; report the missing path as blocked.
- Do not issue an independent review verdict.
- Do not exceed current-chat permissions.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context with explicit canonical tracking paths or explicit blocked/unknown state, consistent task tracking, implementation evidence, synchronized progress, report output, and a transportable handoff; authorized repository and PR updates are complete; final HEAD and matching CI evidence or explicit absence are recorded; and no merge was performed.
