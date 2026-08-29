---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, adaptive model and reasoning selection, ownership, and mandatory report output. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, proportionately resourced, and report-backed.

This Skill owns per-task model-tier, reasoning-effort, and fork-policy selection for newly dispatched sub-agents. It does not decide whether the parent should delegate or how independent workstreams should be decomposed; `codex-delegation-executor` owns those decisions. Existing reviewer continuity is preserved by `review-enforcer` and is not treated as a new spawn.

## Execution owner

Run this skill as: `parent`

- This skill prepares and dispatches sub-agent work; it is not itself a sub-agent worker skill.

## Inputs

Before running this skill, identify:

- delegated task purpose
- exact scope and non-goals
- relevant skill files the `sub-agent` must read
- whether the `sub-agent` should inspect the repository directly beyond the parent-prepared diff or summary
- write boundaries and validation expectations
- task kind, work class, uncertainty, change radius, criticality, repetition, decomposability, and context need
- explicit user or repository model, reasoning, budget, availability, or fork constraints
- whether `codex-delegation-executor` considered multi-agent decomposition and its disposition
- user-approval evidence when `Sol xhigh` or `Sol max` is under consideration

When a caller already supplied a complete delegation assessment, reuse it. Otherwise derive the missing selection inputs from the bounded task and record that derivation. Do not require routine user confirmation of automatically selected profiles below the expensive-profile approval gate.

## Run this skill

Run this skill whenever:

- a skill requires a new sub-agent execution
- `codex-delegation-executor` chooses a new `sub-agent`
- `review-enforcer` needs a new normal, replacement, or independent reviewer
- independent verification is required through a new sub-agent
- a bounded implementation or investigation task is handed off

Do not create a new reviewer merely because an existing reviewer moves from initial review to fix verification or bounded closure. `review-enforcer` owns that reuse and preserves the original applied profile.

## Required flow

1. define the exact task type and why a new `sub-agent` is being used
2. define the scope, non-goals, expected outputs, and write ownership
3. classify the task signals required by [references/agent-profile-selection.md](references/agent-profile-selection.md)
4. select and record one ordinary `dispatch_profile`, return independently separable work to `codex-delegation-executor`, or create an approval-gated `proposed_profile`
5. if the proposed profile is `Sol xhigh` or `Sol max`, present the proposal and cost notice to the user and stop before dispatch unless explicit current-task approval already exists
6. after approval, promote the approved proposal to `requested`; after rejection, recompute with `Sol xhigh` and `Sol max` excluded
7. read [references/spawn-agent-model-overrides.md](references/spawn-agent-model-overrides.md) and resolve the approved requested profile into an applied runtime profile
8. identify which skill files the `sub-agent` must read
9. call `report-output-manager` and decide the report path before dispatch
10. create the report file before dispatch using the standard template
11. tell the `sub-agent` to read the specified skill files before executing
12. tell the `sub-agent` to read that exact report file first and fill only the intended blank sections or placeholder values
13. require commands run, changed files, outcome, unresolved risks, and every field in the fixed `Dispatch profile` section to be completed in the report
14. dispatch with the applied model and reasoning effort as actual tool-call arguments and the selected fork policy
15. do not treat the delegated task as complete until the report exists, the runtime application status is recorded, and the parent has reviewed the result

Read the report template from `report-output-manager` when creating the file:

- [../report-output-manager/references/sub-agent-report-template.md](../report-output-manager/references/sub-agent-report-template.md)

## Profile-selection contract

Select the model tier and reasoning effort independently.

- use Luna only for low-uncertainty, local, ordinary-criticality, deterministic work
- use Terra for ordinary bounded technical work
- use Sol for judgment-heavy, ambiguous, high-criticality, cross-system, design, difficult debugging, and review work
- use `max` only for one exceptionally difficult, non-decomposable problem
- treat multi-agent or article-described `Ultra` execution as a decomposition strategy owned by `codex-delegation-executor`, never as a `reasoning_effort` value
- choose the highest floor required by task kind, uncertainty, change radius, and criticality
- preserve explicit user and repository overrides according to the precedence in the reference

### Expensive Sol approval gate

`Sol xhigh` and `Sol max` are not automatic dispatch profiles.

When either becomes the calculated profile:

- keep it in `proposed_profile`, not `requested`
- explain why `Sol high` is insufficient
- tell the user that the higher reasoning effort increases execution cost
- ask for explicit approval to use the proposed profile
- stop the workflow before spawning that agent
- do not treat repository policy, a prior unrelated approval, silence, or inferred preference as approval

An explicit current-task instruction from the user that directly requests `Sol xhigh` or `Sol max` satisfies the gate. If the user rejects the proposal, recompute a non-gated profile; normally the upper automatic fallback is `Sol high`.

This gate applies to all task kinds, including independent final review and release audit, and has priority over repository policy and automatic selection.

For newly created review agents, use these defaults:

- initial normal review: Sol with `high`
- focused fix verification when continuity reuse is unavailable: Terra with `high`
- independent final review or release audit: propose Sol with `xhigh`, then stop for explicit user approval before dispatch

When `review-enforcer` reuses an existing normal or independent reviewer, do not apply these new-agent defaults. Preserve the original applied profile and record `application_status: reused_existing_agent_profile` in the review evidence.

For investigation, do not use Luna for open-ended or root-cause work. A deterministic evidence-collection task may use Luna, but a failure or conflicting evidence must be reclassified before retrying.

Record `proposed`, `requested`, and `applied` distinctly when the approval gate is relevant. A full-history fork inherits the parent profile; runtime rejection or fallback is a capability state, not evidence that the requested override was applied.

## Required prompt content

Every new sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- explicit instruction not to run `codex exec`, nested Codex, or equivalent agent-spawning inside the sub-agent task
- explicit instruction not to re-enter `development-orchestrator` or any other parent-owned workflow unless the parent explicitly named that workflow as part of the delegated task
- an explicit fork policy
- skill names and file paths that must be read first
- validation commands or evidence expectations
- report path
- instruction to read the pre-created report file first and preserve its heading order, spacing, and existing filled text
- instruction to fill only blank sections or placeholder values instead of rewriting the full report
- instruction to complete the fixed `Dispatch profile` placeholders without adding, removing, or reordering report sections
- required final output shape

The selected model and reasoning effort belong only in actual spawn parameters. Do not rely on model names written in the prompt to configure execution. The prompt may state task-local cost or quality constraints, but it must not claim an unapplied runtime profile.

For review tasks also include:

- the review mode and criticality signals used by the profile selector
- explicit instruction to perform a code review using the built-in review behavior
- instruction to return findings first, ordered by severity
- instruction to include file/line references when available
- instruction to say explicitly when no findings were found
- instruction to treat the report template as immutable structure and fill only blank sections or placeholder values
- instruction to distinguish blocking normal-path problems, user-confirmation-required capability gaps, and non-blocking concerns that should only be recorded and held
- instruction to inspect the relevant workspace directly when surrounding code context is needed, instead of relying only on a parent-prepared diff summary
- explicit permission and requirement to write those findings into the pre-created report file without changing the report format

For investigation tasks also include:

- instruction to inspect the relevant workspace directly when the answer depends on surrounding code or configuration context
- instruction not to stop at the parent-prepared excerpt when additional repository files are needed to confirm the result
- instruction to record the checked files and concrete evidence in the report

For coding tasks also include:

- owned files or modules
- instruction not to revert unrelated changes
- instruction to list changed files in the final response

When a relevant skill exists, do not paraphrase it loosely as the only guidance. Tell the `sub-agent` to read the actual `SKILL.md` path and then restate only the most critical task-local constraints.

## Report rules

- Every dispatched sub-agent task must produce a file under `reports/`.
- The parent agent should create the report file before dispatch whenever feasible.
- The report must be created before the parent workflow treats a dispatched task as complete.
- An approval-gated proposal may be recorded before a child report exists because no child has been dispatched yet; record it in the parent-owned lifecycle evidence.
- The parent should pre-populate the standard headings and placeholders so the `sub-agent` edits a fixed structure instead of rewriting the document.
- The standard template includes a fixed `Dispatch profile` section. Do not require profile evidence outside that fixed structure.
- If the `sub-agent` cannot write the report directly, the parent must write it immediately from the returned evidence.
- Do not ask a sub-agent for ad hoc investigation, review, or implementation without a report path.
- For review tasks, the built-in review result must be materialized into the report file before the task is considered complete.
- For review tasks, direct report editing by the reviewer is the default path; parent-side transcription is fallback only when direct editing is not possible.
- For review tasks, a concern that does not break the intended normal path yet should still be written to the report, but may be held instead of blocking release immediately.
- For review tasks, do not stop or replace an in-flight reviewer just because waiting took too long; keep waiting until completion unless the user explicitly says to stop.
- Report text should be written in Japanese unless the user explicitly requests another language.
- The `sub-agent` must preserve the existing report format: no heading renames, no section reordering, no blank-line cleanup, and no whole-file replacement.
- Existing non-empty parent text in the report is immutable unless the parent explicitly marks it as editable.
- Record all profile-selection inputs, proposal and approval evidence when relevant, requested and applied profile, selection source, reasons, constraints, fork policy, application status, and any escalation or fallback in the fixed `Dispatch profile` section.

## Standard report sections

Use these sections in order:

- `# Sub-agent実行レポート`
- `## タスク`
- `## sub-agentを使う理由`
- `## 対象範囲`
- `## 対象外`
- `## Dispatch profile`
- `## 実行コマンド`
- `## 対象ファイル`
- `## 指摘事項`
- `## 結果`
- `## リスク`

The fixed `Dispatch profile` section contains placeholders for:

- selection inputs
- selection source
- proposed profile
- approval status / evidence
- requested profile
- applied profile
- application status
- reviewer continuity
- fork policy
- reasons / constraints

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
- dispatch-profile evidence and runtime application status
- when applicable, `Sol xhigh` / `Sol max` proposal and explicit approval evidence
- when applicable, reviewer continuity evidence and `reused_existing_agent_profile`

## Outputs

After this skill runs for a dispatched task, there should be:

- a dispatched sub-agent task with explicit scope
- a pre-created report path under `reports/`
- a recorded delegation assessment and selected `dispatch_profile`
- a requested and actually applied model, reasoning effort, and fork policy
- report-backed evidence for the delegated work

When the expensive Sol approval gate is pending, the output is instead:

- a recorded `proposed_profile`
- cost and justification notice
- `application_status: awaiting_user_approval`
- no dispatch using that profile

## Completion condition

This skill is complete for a dispatched task only when:

- the sub-agent task has been dispatched with the required prompt content
- any required `Sol xhigh` or `Sol max` approval was obtained before dispatch
- the requested profile has either been applied or recorded as an explicit inherited, fallback, or capability-gap state
- the report file exists in the expected location
- the report contains the fixed `Dispatch profile` evidence
- the parent has reviewed the resulting report and underlying evidence

An approval-gated task is intentionally incomplete while awaiting user approval.

## Rules

- Keep sub-agent tasks small and concrete.
- Prefer one bounded request over one broad speculative request.
- Reuse existing reports before dispatching duplicate work.
- Use `execution-cost-stabilizer` before proposing `max`, multi-agent decomposition, wasteful reruns, or excessive parallelism.
- Never dispatch `Sol xhigh` or `Sol max` without explicit current-task user approval.
- Do not silently downgrade an approval-gated proposal merely to avoid asking the user; present the proposal and stop first. After rejection, recompute the profile.
- Do not make a sub-agent run `codex exec`, nested Codex, or equivalent agent-spawning workflows inside the delegated task.
- Do not let a sub-agent re-run `development-orchestrator` or other parent-owned workflow entry skills just because they exist in the repo; the sub-agent should execute only the delegated task and the explicitly named supporting skills.
- Do not leave report structure up to the `sub-agent`.
- For review and investigation tasks, prefer letting the `sub-agent` read the relevant workspace directly instead of over-constraining it to parent-curated excerpts.
- For review tasks, prefer the model's native review behavior over inventing a custom review rubric in the prompt.
- For review tasks, prefer direct report editing by the reviewer and use parent-side transcription only as fallback.
- Do not treat a model or reasoning mention in `message` as an override. Pass the applied values in the actual `spawn_agent` call.
- Do not combine a model or reasoning override with omitted `fork_turns` or `fork_turns: "all"`; full-history forks inherit the parent execution profile.
- Do not silently downgrade an explicit user or repository profile override, except that an unapproved repository request for `Sol xhigh` or `Sol max` remains a proposal until the user approves it.
- Do not keep a failed deterministic task on Luna after the work has become diagnosis or judgment.
- If runtime rejects a hidden override argument, keep fallback execution parent-owned as defined by the spawn reference. Do not ask the delegated sub-agent to run the fallback.
- If independently separable work would justify multi-agent execution, return it to `codex-delegation-executor` before dispatch rather than overloading one sub-agent.

## Cross-cutting rule

If recurring sub-agent dispatch failures, profile misclassification, approval-gate bypasses, or report omissions appear, call `feedback-points-manager`.
