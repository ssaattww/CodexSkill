---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, ownership, and mandatory report output. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, and report-backed.

## Run this skill

Run this skill whenever:

- a skill requires sub-agent execution
- `codex-delegation-executor` chooses a `sub-agent`
- independent review or verification is required
- a bounded implementation or investigation task is handed off

## Required flow

1. define the exact task type and why a `sub-agent` is being used
2. define the scope, non-goals, and expected outputs
3. define write ownership and file boundaries when edits are allowed
4. call `report-output-manager` and decide the report path before dispatch
5. create the report file before dispatch using the standard template
6. tell the `sub-agent` to fill in that exact report file
7. require commands run, changed files, outcome, and unresolved risks in the report
8. do not treat the delegated task as complete until the report exists and has been reviewed

Read the template from `report-output-manager` when creating the file:

- [../report-output-manager/references/sub-agent-report-template.md](../report-output-manager/references/sub-agent-report-template.md)

## Required prompt content

Every sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- validation commands or evidence expectations
- report path
- instruction to update the pre-created report file instead of inventing a new format
- required final output shape

For coding tasks also include:

- owned files or modules
- instruction not to revert unrelated changes
- instruction to list changed files in the final response

## Report rules

- Every sub-agent task must produce a file under `reports/`.
- The parent agent should create the report file before dispatch whenever feasible.
- The report must be created before the parent workflow treats the task as complete.
- The parent agent should pre-populate the standard headings so the `sub-agent` writes into a fixed structure.
- If the `sub-agent` cannot write the report directly, the parent agent must write it immediately from the returned evidence.
- Do not ask a sub-agent for ad hoc investigation, review, or implementation without a report path.

## Standard report sections

Use these sections in order:

- `# Sub-agent Execution Report`
- `## Task`
- `## Why Sub-agent`
- `## Scope`
- `## Non-goals`
- `## Commands`
- `## Files`
- `## Outcome`
- `## Risks`

## Minimum report contents

Include:

- task identifier or purpose
- why a `sub-agent` was used
- scope handled
- commands run
- files changed or checked
- outcome
- unresolved risks or follow-up items

## Rules

- Keep sub-agent tasks small and concrete.
- Prefer one bounded request over one broad speculative request.
- Reuse existing reports before dispatching duplicate work.
- Use `execution-cost-stabilizer` if the delegation plan risks wasteful reruns or excessive parallelism.
- Do not leave report structure up to the `sub-agent`.

## Cross-cutting rule

If recurring sub-agent dispatch failures or report omissions appear, call `feedback-points-manager`.
