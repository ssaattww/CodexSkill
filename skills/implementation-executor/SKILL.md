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

## Verification-route execution

Use `verification_capability` resolved by `work-context-manager`.

- For `local_execution_available`, run relevant local validation before the
  review-target commit. Normal review and fix-verification loops use local
  fix, relevant local validation, commit, and review; do not wait for CI.
  Before a CI-triggering push, rerun validation relevant to the pushed change.
  Before the final push, require the repository-defined full local gate. After
  report attestation, wait once only for exact-head required `pull_request` CI
  as the merge gate; do not wait for an unrequired `push` run.
- For `remote_ci_only`, after an authorized push, obtain or wait for matching
  current-HEAD CI as formal verification evidence. Missing, incomplete, or
  failed CI remains explicit evidence, never local Green.

Commit, push, and CI wait are distinct states. Pass their evidence to the core
worker and report path without adding runtime-specific wait rules to
`implementation-worker`.

## Boundaries

- Do not re-plan the task.
- Do not decide TDD applicability here; the target repository and caller own it.
- Do not redefine implementation rules locally when a required Skill is unavailable.
- Do not let the executor review its own changes.
- Do not merge.

## Completion condition

Complete when the required Skills have produced current context and implementation evidence for the accepted scope, the parent has the evidence required for reporting and review, no self-review verdict was issued, and no merge was performed.
