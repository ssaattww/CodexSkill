---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, ownership, and mandatory report output. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, and report-backed.

## Execution owner

Run this skill as: `parent`

- This skill prepares and dispatches sub-agent work; it is not itself a sub-agent worker skill.

## Inputs

Before running this skill, identify:

- delegated task purpose
- exact scope and non-goals
- relevant skill files the `sub-agent` must read
- write boundaries and validation expectations

## Run this skill

Run this skill whenever:

- a skill requires sub-agent execution
- `codex-delegation-executor` chooses a `sub-agent`
- independent review or verification is required
- a bounded implementation or investigation task is handed off

## Required flow

1. define the exact task type and why a `sub-agent` is being used
2. define the scope, non-goals, and expected outputs
3. identify which skill files the `sub-agent` must read
4. define write ownership and file boundaries when edits are allowed
5. call `report-output-manager` and decide the report path before dispatch
6. create the report file before dispatch using the standard template
7. tell the `sub-agent` to read the specified skill files before executing
8. tell the `sub-agent` to fill in that exact report file
9. require commands run, changed files, outcome, and unresolved risks in the report
10. do not treat the delegated task as complete until the report exists and has been reviewed

Read the template from `report-output-manager` when creating the file:

- [../report-output-manager/references/sub-agent-report-template.md](../report-output-manager/references/sub-agent-report-template.md)

## Required prompt content

Every sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- skill names and file paths that must be read first
- validation commands or evidence expectations
- report path
- instruction to update the pre-created report file instead of inventing a new format
- required final output shape

For review tasks also include:

- explicit instruction to perform a code review using the built-in review behavior
- instruction to return findings first, ordered by severity
- instruction to include file/line references when available
- instruction to say explicitly when no findings were found
- instruction to write those findings into the pre-created report file, not only in the chat response

For coding tasks also include:

- owned files or modules
- instruction not to revert unrelated changes
- instruction to list changed files in the final response

When a relevant skill exists, do not paraphrase it loosely as the only guidance. Tell the `sub-agent` to read the actual `SKILL.md` path and then restate only the most critical task-local constraints.

## Report rules

- Every sub-agent task must produce a file under `reports/`.
- The parent agent should create the report file before dispatch whenever feasible.
- The report must be created before the parent workflow treats the task as complete.
- The parent agent should pre-populate the standard headings so the `sub-agent` writes into a fixed structure.
- If the `sub-agent` cannot write the report directly, the parent agent must write it immediately from the returned evidence.
- Do not ask a sub-agent for ad hoc investigation, review, or implementation without a report path.
- For review tasks, the built-in review result must be materialized into the report file before the task is considered complete.
- Report text should be written in Japanese unless the user explicitly requests another language.

## Standard report sections

Use these sections in order:

- `# Sub-agent実行レポート`
- `## タスク`
- `## sub-agentを使う理由`
- `## 対象範囲`
- `## 対象外`
- `## 実行コマンド`
- `## 対象ファイル`
- `## 指摘事項`
- `## 結果`
- `## リスク`

## Minimum report contents

Include:

- task identifier or purpose
- why a `sub-agent` was used
- scope handled
- commands run
- files changed or checked
- findings summary or explicit `no findings`
- outcome
- unresolved risks or follow-up items

## Outputs

After this skill runs, there should be:

- a dispatched sub-agent task with explicit scope
- a pre-created report path under `reports/`
- report-backed evidence for the delegated work

## Completion condition

This skill is complete only when:

- the sub-agent task has been dispatched with the required prompt content
- the report file exists in the expected location
- the parent has reviewed the resulting report

## Rules

- Keep sub-agent tasks small and concrete.
- Prefer one bounded request over one broad speculative request.
- Reuse existing reports before dispatching duplicate work.
- Use `execution-cost-stabilizer` if the delegation plan risks wasteful reruns or excessive parallelism.
- Do not leave report structure up to the `sub-agent`.
- For review tasks, prefer the model's native review behavior over inventing a custom review rubric in the prompt.
- When a task depends on an existing skill, prefer making the `sub-agent` read that skill over duplicating its workflow in the prompt.

## Cross-cutting rule

If recurring sub-agent dispatch failures or report omissions appear, call `feedback-points-manager`.
