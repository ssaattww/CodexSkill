---
name: tdd-executor
description: Enforce test-driven development by defining test cases first, creating failing tests before implementation, and using those tests as the execution target for the current task. Use when starting implementation work, adding a bug fix, introducing new behavior, or hardening regressions.
---

# TDD Executor

Make tests lead implementation.

## Goal

Define expected behavior before code changes and keep the current task anchored to executable proof.

## Required flow

1. Read the current task and exit criteria.
2. Identify the smallest testable behavior for the task.
3. Define test cases.
4. Add or update tests so they fail for the current gap.
5. Only then allow implementation work.

## Rules

- Prefer the smallest failing test that proves the intended behavior.
- Add regression tests for bug fixes.
- Add integration or E2E tests when unit tests are insufficient to prove the contract.
- Keep tests tied to task exit criteria.

## Do not do

- Do not start implementation before defining tests.
- Do not rely on vague “manual confirmation” instead of executable checks when tests are feasible.
- Do not leave important edge cases implicit if the task depends on them.

## Output expectations

After this skill runs, the current task should have:

- named test targets
- explicit happy-path and error-path expectations when relevant
- at least one failing or newly necessary test that drives implementation