---
name: execution-cost-stabilizer
description: Reduce unnecessary reruns, over-parallelization, unstable agent behavior, and avoidable Codex cost during delegated development workflows. Use before heavy Codex execution, when planning execution order, when choosing reasoning effort, or when repeated retries and parallel jobs threaten stability or efficiency.
---

# Execution Cost Stabilizer

Control cost and execution instability.

## Goal

Keep delegated development efficient, sequential, and stable.

## Execution owner

Run this skill as: `parent`

- This skill controls orchestration strategy and execution budget decisions.

## Inputs

Before running this skill, identify:

- planned delegated tasks
- current rerun or retry pressure
- parallelism candidates
- reasoning-effort choices under consideration

## Focus areas

Control:

- unnecessary reruns
- oversized delegated jobs
- too many parallel background tasks
- inappropriate reasoning effort
- repeated work caused by unclear scoping

## Rules

- Prefer sequential execution unless parallelism is clearly safe and useful.
- Prefer narrow scopes over large retries.
- Choose reasoning effort proportionate to task complexity.
- Reuse existing evidence and reports before rerunning expensive steps.

## Outputs

After this skill runs, the next delegated action should be scoped, justified, and unlikely to waste effort.

## Completion condition

This skill is complete only when the next execution plan is intentionally scoped and cost risks have been reduced as much as practical.

## Cross-cutting rule

If repeated cost or stability failures recur, call `feedback-points-manager`.
