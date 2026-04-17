---
name: execution-cost-stabilizer
description: Reduce unnecessary reruns, over-parallelization, unstable agent behavior, and avoidable Codex cost during delegated development workflows. Use before heavy Codex execution, when planning execution order, when choosing reasoning effort, or when repeated retries and parallel jobs threaten stability or efficiency.
---

# Execution Cost Stabilizer

Control cost and execution instability.

## Goal

Keep delegated development efficient, sequential, and stable.

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

## Output expectations

After this skill runs, the next delegated action should be scoped, justified, and unlikely to waste effort.

## Cross-cutting rule

If repeated cost or stability failures recur, call `feedback-points-manager`.