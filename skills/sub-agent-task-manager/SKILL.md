---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, adaptive model and reasoning selection, ownership, and mandatory report output. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, proportionately resourced, and report-backed.

This Skill owns per-task model-tier, reasoning-effort, and fork-policy selection for newly dispatched sub-agents. It does not decide whether the parent should delegate or how independent workstreams should be decomposed; `codex-delegation-executor` owns those decisions unless the caller explicitly locks a task to one agent. Existing reviewer continuity is preserved by `review-enforcer` and is not treated as a new spawn.

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
- whether the caller explicitly forbids decomposition and requires one agent
- report persistence mode: `normal_persistence` or `deferred_attestation`
- user-approval evidence when `Sol xhigh` or `Sol max` is under consideration

When a caller already supplied a complete delegation assessment, reuse it. Otherwise derive the missing selection inputs from the bounded task and record that derivation. Do not require routine user confirmation of automatically selected profiles below the expensive-profile approval gate.

If the caller owns an identity-sensitive lifecycle and explicitly sets `decomposition_policy: forbidden`, preserve `decomposability: single` and do not return that task for multi-agent decomposition.

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
2. define the scope, non-goals, expected outputs, write ownership, decomposition policy, and report persistence mode
3. classify the task signals required by [references/agent-profile-selection.md](references/agent-profile-selection.md)
4. select and record one ordinary `dispatch_profile`, return independently separable work to `codex-delegation-executor` only when decomposition is allowed, or create an approval-gated `proposed_profile`
5. if the proposed profile is `Sol xhigh` or `Sol max`, present the proposal and cost notice to the user and stop before dispatch unless explicit current-task approval already exists
6. after approval, promote the approved proposal to `requested`; after rejection, recompute with `Sol xhigh` and `Sol max` excluded
7. read [references/spawn-agent-model-overrides.md](references/spawn-agent-model-overrides.md) and prepare the runtime call plan from `requested`, model availability, and fork constraints; do not populate `applied` before runtime evidence exists
8. identify which skill files the `sub-agent` must read
9. call `report-output-manager` and determine report handling:
   - for `normal_persistence`, reserve the path and create the standard report file before dispatch
   - for `deferred_attestation`, reserve the exact path only; do not create, pre-populate, or edit the repository report file before or during review
10. for `normal_persistence`, pre-populate the fixed report structure and parent-owned `Dispatch profile` fields before dispatch
11. tell the `sub-agent` to read the specified skill files before executing
12. give the child the report instructions for the selected persistence mode
13. dispatch using the `requested` model and reasoning effort as actual tool-call arguments when an override is permitted; when full-history inheritance is required, omit the incompatible override as defined by the spawn reference
14. after the spawn call or fallback attempt, record `applied` and `application_status` from actual runtime evidence, inheritance, rejection, or fallback; never infer `applied` from `requested`
15. for `normal_persistence`, update the parent-owned `Dispatch profile` fields with the post-call runtime evidence and require the child or parent to complete the remaining report sections
16. for `deferred_attestation`, retain the reviewer output and dispatch-profile evidence as parent-owned lifecycle evidence without writing the reserved report path; only the caller's passing-verdict attestation flow may persist it later
17. do not treat the delegated task as complete until the applicable report/evidence contract, runtime application status, and parent adjudication are satisfied

Read the report template from `report-output-manager` when `normal_persistence` applies:

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
- honor a caller-owned `decomposition_policy: forbidden`; such a task stays one agent even when its review scope is broad

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

Record `proposed`, `requested`, and `applied` distinctly when the approval gate is relevant. `requested` is known before spawn; `applied` is a post-runtime fact. A full-history fork inherits the parent profile; runtime rejection or fallback is a capability state, not evidence that the requested override was applied.

## Required prompt content

Every new sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- explicit instruction not to run `codex exec`, nested Codex, or equivalent agent-spawning inside the sub-agent task
- explicit instruction not to re-enter `development-orchestrator` or any other parent-owned workflow unless the parent explicitly named that workflow as part of the delegated task
- an explicit fork policy
- explicit decomposition policy when the caller requires a single agent
- skill names and file paths that must be read first
- validation commands or evidence expectations
- report persistence mode
- required final output shape

The requested model and reasoning effort belong only in actual spawn parameters. Do not rely on model names written in the prompt to configure execution. The prompt may state task-local cost or quality constraints, but it must not claim an unapplied runtime profile.

### Normal-persistence prompt additions

For `normal_persistence`, also include:

- report path
- instruction to read the pre-created report file first and preserve its heading order, spacing, and existing filled text
- instruction to fill only child-owned blank sections or placeholder values instead of rewriting the full report
- instruction not to modify parent-owned `Dispatch profile` values, especially `requested`, `applied`, `application status`, approval, and continuity evidence

The parent owns the complete `Dispatch profile` section because the child cannot observe hidden spawn arguments or runtime application evidence.

### Deferred-attestation prompt additions

For `deferred_attestation`, also include:

- the reserved report path as metadata only
- explicit instruction that the reserved repository report file does not yet exist and must not be created or edited by the reviewer
- instruction to return structured findings, coverage, commands/evidence, verdict, risks, and unexplored areas to the parent
- instruction that the parent will retain this output until the caller's report-attestation flow decides whether it may be persisted

For review tasks also include:

- the review mode and criticality signals used by the profile selector
- explicit instruction to perform a code review using the built-in review behavior
- instruction to return findings first, ordered by severity
- instruction to include file/line references when available
- instruction to say explicitly when no findings were found
- instruction to distinguish blocking normal-path problems, user-confirmation-required capability gaps, and non-blocking concerns that should only be recorded and held
- instruction to inspect the relevant workspace directly when surrounding code context is needed, instead of relying only on a parent-prepared diff summary

For normal-persistence review tasks, require direct editing of the child-owned report sections. For deferred-attestation independent review, prohibit repository report editing and require structured parent-returned evidence instead.

For investigation tasks also include:

- instruction to inspect the relevant workspace directly when the answer depends on surrounding code or configuration context
- instruction not to stop at the parent-prepared excerpt when additional repository files are needed to confirm the result
- instruction to record the checked files and concrete evidence in the report or returned structured evidence, according to persistence mode

For coding tasks also include:

- owned files or modules
- instruction not to revert unrelated changes
- instruction to list changed files in the final response

When a relevant skill exists, do not paraphrase it loosely as the only guidance. Tell the `sub-agent` to read the actual `SKILL.md` path and then restate only the most critical task-local constraints.

## Report rules

- Every dispatched ordinary sub-agent task must produce a file under `reports/` using `normal_persistence`.
- An independent-final reviewer using `deferred_attestation` is the intentional exception: reserve the report path before freeze, but do not create or edit that repository file until the caller has a passing verdict and enters report-attestation mode.
- The parent agent should create the normal-persistence report file before dispatch whenever feasible.
- An approval-gated proposal may be recorded before a child report exists because no child has been dispatched yet; record it in the parent-owned lifecycle evidence.
- The parent should pre-populate the standard headings and parent-owned `Dispatch profile` fields so the `sub-agent` edits a fixed structure instead of rewriting the document.
- The standard template includes a fixed `Dispatch profile` section, but that section is parent-owned. The child must not attest to hidden spawn arguments or runtime application state.
- If a normal-persistence `sub-agent` cannot write its child-owned report sections directly, the parent must write them immediately from the returned evidence.
- Do not ask an ordinary sub-agent for ad hoc investigation, review, or implementation without a report path.
- For normal review and fix verification, the built-in review result must be materialized into the report file before the task is considered complete.
- For deferred-attestation independent final review, retain the built-in result as parent-owned evidence and do not materialize it into the reserved repository path until the passing-verdict attestation step.
- For normal review tasks, direct report editing by the reviewer is the default path; parent-side transcription is fallback only when direct editing is not possible.
- For review tasks, a concern that does not break the intended normal path yet should still be recorded, but may be held instead of blocking release immediately.
- For review tasks, do not stop or replace an in-flight reviewer just because waiting took too long; keep waiting until completion unless the user explicitly says to stop.
- Report text should be written in Japanese unless the user explicitly requests another language.
- A normal-persistence `sub-agent` must preserve the existing report format: no heading renames, no section reordering, no blank-line cleanup, and no whole-file replacement.
- Existing non-empty parent text and all parent-owned `Dispatch profile` values are immutable to the child unless the parent explicitly marks them as editable.

## Standard report sections

For `normal_persistence`, use these sections in order:

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

The fixed `Dispatch profile` section is parent-owned and contains:

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

## Minimum evidence contents

For every dispatched task, retain:

- task identifier or purpose
- why a `sub-agent` was used
- scope handled
- commands run
- files changed or checked
- findings summary or explicit `no findings`
- outcome or verdict
- unresolved risks or follow-up items
- dispatch-profile requested and post-runtime applied evidence
- when applicable, `Sol xhigh` / `Sol max` proposal and explicit approval evidence
- when applicable, reviewer continuity evidence and `reused_existing_agent_profile`

For deferred attestation, these remain parent-owned lifecycle evidence until persistence is permitted.

## Outputs

After this skill runs for a normal-persistence dispatched task, there should be:

- a dispatched sub-agent task with explicit scope
- a pre-created report path under `reports/`
- a recorded delegation assessment and requested `dispatch_profile`
- post-runtime `applied` and `application_status` evidence
- report-backed evidence for the delegated work

For a deferred-attestation independent reviewer, there should be:

- one dispatched reviewer with explicit scope and reserved report path metadata
- no repository report file created or edited by the reviewer
- requested and post-runtime applied dispatch-profile evidence retained by the parent
- structured review evidence retained by the parent for later attestation or fix-loop handling

When the expensive Sol approval gate is pending, the output is instead:

- a recorded `proposed_profile`
- cost and justification notice
- `application_status: awaiting_user_approval`
- no dispatch using that profile

## Completion condition

This skill is complete for a normal-persistence dispatched task only when:

- the sub-agent task has been dispatched with the required prompt content
- any required `Sol xhigh` or `Sol max` approval was obtained before dispatch
- post-runtime `applied` or an explicit inherited, fallback, or capability-gap state is recorded
- the report file exists in the expected location
- the parent-owned `Dispatch profile` evidence and child-owned task evidence are complete
- the parent has reviewed the resulting report and underlying evidence

For a deferred-attestation independent reviewer, this Skill's dispatch work is complete when the reviewer returns, post-runtime profile evidence is recorded, the structured review evidence is retained by the parent, and the reserved path remains unwritten. Repository report persistence is completed later only through the caller's report-attestation flow after a passing verdict.

An approval-gated task is intentionally incomplete while awaiting user approval.

## Rules

- Keep sub-agent tasks small and concrete.
- Prefer one bounded request over one broad speculative request.
- Reuse existing reports before dispatching duplicate work.
- Honor `decomposition_policy: forbidden`; do not return caller-locked identity-sensitive tasks to multi-agent decomposition.
- Use `execution-cost-stabilizer` before proposing `max`, multi-agent decomposition, wasteful reruns, or excessive parallelism.
- Never dispatch `Sol xhigh` or `Sol max` without explicit current-task user approval.
- Do not silently downgrade an approval-gated proposal merely to avoid asking the user; present the proposal and stop first. After rejection, recompute the profile.
- Do not make a sub-agent run `codex exec`, nested Codex, or equivalent agent-spawning workflows inside the delegated task.
- Do not let a sub-agent re-run `development-orchestrator` or other parent-owned workflow entry skills just because they exist in the repo; the sub-agent should execute only the delegated task and the explicitly named supporting skills.
- Do not leave report structure up to the `sub-agent`.
- For review and investigation tasks, prefer letting the `sub-agent` read the relevant workspace directly instead of over-constraining it to parent-curated excerpts.
- For review tasks, prefer the model's native review behavior over inventing a custom review rubric in the prompt.
- Do not treat a model or reasoning mention in `message` as an override. Pass the `requested` values in the actual `spawn_agent` call, not post-call `applied` values.
- Do not combine a model or reasoning override with omitted `fork_turns` or `fork_turns: "all"`; full-history forks inherit the parent execution profile.
- Do not silently downgrade an explicit user or repository profile override, except that an unapproved repository request for `Sol xhigh` or `Sol max` remains a proposal until the user approves it.
- Do not keep a failed deterministic task on Luna after the work has become diagnosis or judgment.
- If runtime rejects a hidden override argument, keep fallback execution parent-owned as defined by the spawn reference. Do not ask the delegated sub-agent to run the fallback.
- If independently separable work would justify multi-agent execution and decomposition is allowed, return it to `codex-delegation-executor` before dispatch rather than overloading one sub-agent.
- Never create or edit an independent-final reserved report path before the caller enters passing-verdict report-attestation mode.

## Cross-cutting rule

If recurring sub-agent dispatch failures, profile misclassification, approval-gate bypasses, report omissions, or attestation-boundary violations appear, call `feedback-points-manager`.
