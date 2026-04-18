---
name: codex-delegation-executor
description: Delegate investigation, implementation, build, and test execution to Codex or sub-agents instead of performing those steps manually. Use for code investigation, implementation tasks, verification runs, review preparation, and evidence collection. This skill standardizes how work is delegated and how results are captured in reports.
---

# Codex Delegation Executor

Route executable work through Codex or sub-agents.

## Goal

Ensure investigation, implementation, build, and verification work are delegated consistently, with executor choice made explicitly and evidenced.

## Delegate these work types

Delegate:

- code investigation
- implementation
- build execution
- test execution
- environment verification
- focused review preparation
- requirement or issue-intake verification
- other assumption-sensitive classification or confirmation work

## Fixed sub-agent categories

The following work must be executed by a `sub-agent` now, not merely preferred:

- review
- build execution used as verification evidence
- test execution used as verification evidence
- environment verification
- requirement or issue-intake verification
- standards detection or standards validation

Use `sub-agent-task-manager` for these categories and require a report in `reports/`.

## Executor selection

Decide the executor inside this skill before running the work:

- If the work matches a fixed sub-agent category, do not decide; use a `sub-agent`.
- For implementation work, decide `main agent` vs `sub-agent` here based on coupling, urgency, write-scope overlap, and whether parallelism helps.
- Keep the main agent responsible for scoping, integration, and final synthesis even when a sub-agent executes the task.

## Required delegation pattern

For each delegated task:

1. classify the work as fixed-sub-agent vs implementation-side delegation
2. if fixed-sub-agent, call `sub-agent-task-manager`
3. otherwise choose executor and record why that executor was chosen
4. define the exact scope
5. define expected outputs
6. define validation commands or evidence
7. run the delegated work
8. capture results in `reports/`

## Rules

- Keep delegated tasks small and sequential.
- Prefer one focused sub-task over one large ambiguous request.
- Do not pre-decide implementation ownership outside this skill unless the user explicitly requires it.
- Use the main agent for implementation only when the task is tightly coupled to current context, on the critical path, or risky to hand off.
- Use a sub-agent for implementation when the task is bounded, parallelizable, or benefits from isolation.
- Every sub-agent request must leave a report in `reports/`.
- Pre-create the report file before dispatch when using `sub-agent-task-manager`.
- Exclude noisy diffs and irrelevant generated files when preparing review inputs.
- Require concrete evidence instead of verbal assurance.

## Strong rule

Do not personally substitute for delegated investigation, review, intake verification, or test execution when this workflow expects an independent pass.

## Evidence rules

Record in `reports/`:

- executor chosen and why
- what was delegated
- what was changed or checked
- what commands ran
- pass/fail outcome
- unresolved risks if any

When creating a new report file, call `report-output-manager` for placement and filename rules.

## Cross-cutting rule

If recurring delegation failures or repeated workflow mistakes appear, call `feedback-points-manager`.
