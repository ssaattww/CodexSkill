---
name: codex-delegation-executor
description: Delegate investigation, implementation, build, and test execution to Codex or sub-agents instead of performing those steps manually. Use for code investigation, implementation tasks, verification runs, review preparation, and evidence collection. This skill standardizes how work is delegated and how results are captured in reports.
---

# Codex Delegation Executor

Route executable work through Codex.

## Goal

Ensure investigation, implementation, build, and test verification are delegated consistently and leave evidence.

## Delegate these work types

Delegate:

- code investigation
- implementation
- build execution
- test execution
- environment verification
- focused review preparation

## Required delegation pattern

For each delegated task:

1. define the exact scope
2. define expected outputs
3. define validation commands or evidence
4. run the delegated work
5. capture results in `reports/`

## Rules

- Keep delegated tasks small and sequential.
- Prefer one focused sub-task over one large ambiguous request.
- Exclude noisy diffs and irrelevant generated files when preparing review inputs.
- Require concrete evidence instead of verbal assurance.

## Strong rule

Do not personally substitute for delegated investigation, review, or test execution when this workflow expects Codex to do it.

## Evidence rules

Record in `reports/`:

- what was delegated
- what was changed or checked
- what commands ran
- pass/fail outcome
- unresolved risks if any

## Cross-cutting rule

If recurring delegation failures or repeated workflow mistakes appear, call `feedback-points-manager`.