---
name: implementation-executor
description: Coordinate runtime-neutral implementation through the Codex parent and sub-agent model without redefining implementation semantics.
---

# Codex Implementation Wrapper

## Goal

Act as the Codex runtime wrapper for implementation.

## Required Skills

Invoke:

1. `work-context-manager`
2. `implementation-worker`

The parent may delegate execution through `codex-delegation-executor`, but the delegated executor must use the runtime-neutral Skills above. Do not replace them with `shared/` files.

## Codex responsibilities

- The parent owns scope, write boundary, executor selection, commit integration, progress sync, reporting, PR updates, and handoff.
- Pass the resolved work context and selected mode to `implementation-worker`.
- Return all implementation evidence to the parent.
- Use `report-output-manager` for persistence after implementation evidence is available.

## Boundaries

- Do not re-plan the task.
- Do not decide TDD applicability here; the target repository and caller own it.
- Do not redefine implementation rules locally when a required Skill is unavailable.
- Do not let the executor review its own changes.
- Do not merge.

## Completion condition

Complete when the required Skills have produced current context and implementation evidence for the accepted scope, the parent has the evidence required for reporting and review, no self-review verdict was issued, and no merge was performed.
