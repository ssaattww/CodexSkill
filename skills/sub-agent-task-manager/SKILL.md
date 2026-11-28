---
name: sub-agent-task-manager
description: Create and dispatch bounded sub-agent tasks with explicit scope, adaptive model and reasoning selection, ownership, and mandatory report output. Use whenever investigation, implementation, review, verification, or evidence work is handed to a sub-agent, or an existing Astra agent receives more work.
---

# Sub-Agent Task Manager

Standardize how work is handed to a sub-agent.

## Goal

Make every sub-agent task bounded, auditable, proportionately resourced, and report-backed.

This Skill owns per-task model-tier, reasoning-effort, fork-policy selection, role/default-role call planning, and runtime-profile evidence for newly dispatched sub-agents. It also owns Astra eligibility and operation-level authorization for new and existing agents. It does not decide whether the parent should delegate or how independent workstreams should be decomposed; `codex-delegation-executor` owns those decisions unless the caller explicitly forbids decomposition. Existing reviewer continuity and independent-final report-path reservation are owned by `review-enforcer` and are not treated as new spawn-side decisions.

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
- task kind, work class, uncertainty, change radius, criticality, repetition, observed decomposability, and context need
- `decomposition_policy: allowed | forbidden` and its caller-owned reason
- explicit user or repository model, reasoning, budget, availability, fork, or agent-role constraints
- explicit `agent_type` when one is required, otherwise the effective default-role context
- authoritative role/default-role configuration evidence when that role can change model or reasoning
- whether `codex-delegation-executor` considered multi-agent decomposition and its disposition
- report persistence mode: `normal_persistence` or `deferred_attestation`
- for `deferred_attestation`, `pre_reserved_report_path`, `reservation_owner`, `reservation_identity`, and evidence that the reservation was created before the reviewed implementation HEAD was frozen without creating/editing the repository file
- user-approval evidence when `Sol xhigh` or `Sol max` is under consideration
- for possible Astra use, same-task prior-attempt/blocker evidence, stable task/scope identity, parent context, proposed operation, cost notice, and the complete `astra_authorization` record defined in [references/astra-escalation.md](references/astra-escalation.md)
- operation mode: `new_dispatch` or `authorization_only`; for the latter, the caller-owned existing agent identity and original profile/observability evidence

When a caller already supplied a complete delegation assessment, reuse it. Otherwise derive the missing selection inputs from the bounded task and record that derivation. Do not require routine user confirmation of automatically selected profiles below the expensive-profile approval gate.

`decomposability` is an observed task signal. `decomposition_policy` is an execution constraint. If the caller forbids decomposition, preserve the observed signal and record `decomposition_disposition: prohibited_by_caller_policy`; do not rewrite the signal to `single`.

For independent-final `deferred_attestation`, `review-enforcer` is the reservation owner. This Skill must receive and reuse its pre-freeze reservation. Missing, ambiguous, post-freeze, or already-materialized reservation evidence is a lifecycle blocker; do not create a second reservation to compensate.

## Run this skill

Run this skill whenever:

- a skill requires a new sub-agent execution
- `codex-delegation-executor` chooses a new `sub-agent`
- `review-enforcer` needs a new normal, replacement, or independent reviewer
- independent verification is required through a new sub-agent
- a bounded implementation or investigation task is handed off
- an existing Astra agent will receive more work, a retry, or a work-starting resume

Do not create a new reviewer merely because an existing reviewer moves from initial review to fix verification or bounded closure. `review-enforcer` owns that reuse and preserves the original profile/observability evidence. Astra reuse still requires operation-level authorization.

## Authorization-only mode

For an existing agent, run [references/astra-escalation.md](references/astra-escalation.md)'s parent-owned operation gate instead of the new-dispatch flow below.

- Resolve the existing profile and proposed operation without reselecting defaults or modifying original runtime evidence.
- For possible Astra work, validate eligibility, exact high profile, task/scope/agent binding, and a fresh `single_turn` grant or still-valid explicit `task_until_completion` grant.
- Return an operation-bound authorization result to the lifecycle owner. The owner must serialize check/consumption/submission as one parent-controlled sequence; a positive preflight result is not a reusable permission token.
- Do not spawn, replace an agent, create/reserve a report, or change reviewer identity.
- If authorization is missing, pending, consumed, revoked, expired, or mismatched, do not start work; return the appropriate approval stop or capability gap with evidence.
- Observational polling, waiting, and result retrieval are not new work and do not consume authorization.

This mode is complete when the operation-specific authorization disposition and grant/usage evidence are returned. It does not by itself complete the delegated work or claim a continuation ran. Preserve original non-Astra Sol reviewer continuity rules.

## Required flow

Use this flow for `new_dispatch`.

1. define the exact task type and why a new `sub-agent` is being used
2. define scope, non-goals, expected outputs, write ownership, decomposition policy, report persistence mode, and applicable explicit/default agent role
3. classify truthful task signals required by [references/agent-profile-selection.md](references/agent-profile-selection.md), including observed `decomposability` separately from `decomposition_policy`
4. select and record one ordinary `dispatch_profile`, return independently separable work to `codex-delegation-executor` only when decomposition is allowed, or create an approval-gated `proposed_profile`; Astra requires the prior-attempt eligibility gate before proposal
5. for `Sol xhigh`, `Sol max`, or eligible Astra high, present the required proposal and cost notice and stop before dispatch unless the applicable explicit user approval exists; Astra uses the scoped approval modes in its reference
6. after approval, promote the approved proposal to `requested`; after rejection, exclude the rejected profile under its reference and recompute without automatically selecting another gated profile
7. read [references/spawn-agent-model-overrides.md](references/spawn-agent-model-overrides.md) and prepare the runtime call plan from `requested`, model availability, fork constraints, and explicit/default agent-role configuration
8. derive `role_plan` and `planned_runtime_profile`; if the role changes or locks model/reasoning, return the plan through the selector and re-run floor/approval checks before spawn, including Astra eligibility and high-only policy
9. if role/default-role or inheritance profile impact cannot be inspected well enough to guarantee the expensive-profile gate, record a role-profile capability gap and stop before dispatch
10. keep `applied: null` while planning; identify which skill files the `sub-agent` must read
11. resolve report handling without creating duplicate reservations:
    - for `normal_persistence`, call `report-output-manager` normal-persistence phase, reserve the path, and create the standard report file before dispatch
    - for independent-final `deferred_attestation`, do **not** call reservation-only phase here; validate and inherit the exact `pre_reserved_report_path` / `reservation_identity` supplied by `review-enforcer`, verify `reservation_owner: review-enforcer`, verify the path was reserved pre-freeze as metadata only, and verify the repository file still does not exist or has not changed
12. for `normal_persistence`, pre-populate the fixed report structure and parent-owned `Dispatch profile` fields available before spawn
13. tell the `sub-agent` to read the specified skill files before executing and give it the report instructions for the selected persistence mode; Astra receives a bounded work unit and stop/return conditions
14. immediately before Astra submission, run its operation gate and consume a single-turn grant or record use of a valid task-wide grant; then dispatch using the `requested` model/reasoning values and explicit `agent_type` when applicable; when using the runtime default role, omit `agent_type` but preserve that default role in `role_plan`; when full-history inheritance is required, follow the spawn reference without bypassing Astra authorization
15. after spawn/fallback, inspect parent-visible runtime evidence; record exact `applied` only when a trustworthy final profile snapshot or equivalent exact proof is observable; Astra rejection cannot fall back to parent `codex exec`
16. if spawn succeeds but final model/reasoning is hidden, keep `applied: null`, record `application_status: spawn_succeeded_profile_unverified`, and preserve `profile_observability: final_profile_hidden`
17. for `normal_persistence`, update parent-owned `Dispatch profile` fields with post-call evidence and any Astra grant usage, and require the child or parent to complete remaining report sections
18. for `deferred_attestation`, retain reviewer output, inherited reservation identity, and dispatch-profile/authorization evidence as parent-owned lifecycle evidence without writing the reserved report path; only `review-enforcer`'s passing-verdict attestation flow may persist it later
19. do not treat the delegated task as complete until the applicable report/evidence contract, runtime application/observability status, reservation identity, and parent adjudication are satisfied

Read the report template from `report-output-manager` only when `normal_persistence` applies:

- [../report-output-manager/references/sub-agent-report-template.md](../report-output-manager/references/sub-agent-report-template.md)

## Profile-selection contract

Select model tier and reasoning effort independently, except Astra is fixed to `high`.

- use Luna only for low-uncertainty, local, ordinary-criticality, deterministic work
- use Terra for ordinary bounded technical work
- use Sol for judgment-heavy, ambiguous, high-criticality, cross-system, design, difficult debugging, and review work
- propose Astra high only through [references/astra-escalation.md](references/astra-escalation.md), never as an automatic default, floor, or availability fallback
- use `max` only for one exceptionally difficult, intrinsically non-decomposable problem; caller policy forbidding decomposition does not satisfy that condition
- treat multi-agent or article-described `Ultra` execution as a decomposition strategy owned by `codex-delegation-executor`, never as a `reasoning_effort` value
- choose the highest floor required by task kind, uncertainty, change radius, and criticality
- preserve explicit user and repository overrides according to the precedence in the reference
- honor `decomposition_policy: forbidden` without falsifying observed `decomposability`

### Expensive Sol approval gate

`Sol xhigh` and `Sol max` are not automatic dispatch profiles.

When either becomes the calculated initial or role-adjusted profile:

- keep it in `proposed_profile`, not `requested`
- explain why `Sol high` is insufficient
- tell the user that the higher reasoning effort increases execution cost
- ask for explicit current-task approval
- stop before spawning that agent
- do not treat repository policy, prior unrelated approval, silence, or inferred preference as approval

An explicit current-task instruction from the user that directly requests `Sol xhigh` or `Sol max` satisfies the gate. If the user rejects the proposal, recompute a non-gated profile; normally the upper automatic fallback is `Sol high`.

The same gate must be re-run when role/default-role planning raises a cheaper requested profile to Sol `xhigh` or Sol `max`.

For newly created review agents, use these defaults:

- initial normal review: Sol with `high`
- focused fix verification when continuity reuse is unavailable: Terra with `high`
- independent final review or release audit: propose Sol with `xhigh`, then stop for explicit user approval before dispatch

When `review-enforcer` reuses an existing normal or independent reviewer, do not apply these new-agent defaults. Preserve the original profile evidence and its observability state; record `application_status: reused_existing_agent_profile` for an invoked continuation. An Astra continuation additionally requires the authorization-only gate; original dispatch approval alone is not sufficient for another turn.

For investigation, do not use Luna for open-ended or root-cause work. A deterministic evidence-collection task may use Luna, but a failure or conflicting evidence must be reclassified before retrying.

`requested` and `planned_runtime_profile` are pre-spawn evidence. `applied` is a post-runtime fact and may remain unknown when the runtime hides final model/reasoning metadata.

## Required prompt content

Every new sub-agent request must include:

- task purpose
- exact scope
- explicit non-goals
- explicit instruction not to run `codex exec`, nested Codex, or equivalent agent-spawning inside the sub-agent task
- explicit instruction not to re-enter `development-orchestrator` or any other parent-owned workflow unless the parent explicitly named that workflow as part of the delegated task
- explicit fork policy
- decomposition policy when the caller constrains execution
- skill names and file paths that must be read first
- validation commands or evidence expectations
- report persistence mode
- required final output shape

For Astra also include the bounded authorized work unit and stop/return conditions. Do not give an unbounded autonomous continuation or requeue instruction that bypasses the next-turn approval gate.

The requested model/reasoning and agent role belong in actual spawn planning/tool arguments, not merely the message. Do not tell the child it is running an exact final profile when the parent cannot observe that fact.

### Normal-persistence prompt additions

For `normal_persistence`, also include:

- report path
- instruction to read the pre-created report file first and preserve heading order, spacing, and existing filled text
- instruction to fill only child-owned blank sections/placeholders instead of rewriting the full report
- instruction not to modify parent-owned `Dispatch profile` values

The parent owns the complete `Dispatch profile` section because the child cannot observe hidden spawn arguments, role application, or final runtime profile state. Astra approval and grant-consumption records are also parent-owned.

### Deferred-attestation prompt additions

For `deferred_attestation`, also include:

- the inherited `pre_reserved_report_path`, `reservation_owner`, and `reservation_identity` as metadata only
- explicit instruction that the reserved repository report file does not yet exist and must not be created or edited by the reviewer
- instruction to return structured findings, coverage, commands/evidence, verdict, risks, and unexplored areas to the parent
- instruction that the parent will retain this output until `review-enforcer`'s passing-verdict attestation decides whether it may be persisted

For review tasks also include:

- review mode and criticality signals used by the profile selector
- explicit instruction to perform a code review using built-in review behavior
- instruction to return findings first, ordered by severity
- instruction to include file/line references when available
- instruction to say explicitly when no findings were found
- instruction to distinguish blocking normal-path problems, user-confirmation-required capability gaps, and non-blocking concerns that should only be recorded and held
- instruction to inspect the relevant workspace directly when surrounding context is needed

For normal-persistence review tasks, require direct editing of child-owned report sections. For deferred-attestation independent review, prohibit repository report editing and require structured parent-returned evidence instead.

For investigation tasks also include:

- instruction to inspect relevant workspace context directly
- instruction not to stop at a parent-prepared excerpt when more repository evidence is needed
- instruction to record checked files and concrete evidence in the report or returned structured evidence, according to persistence mode

For coding tasks also include:

- owned files/modules
- instruction not to revert unrelated changes
- instruction to list changed files in final output

When a relevant skill exists, tell the `sub-agent` to read the actual `SKILL.md` path; do not rely only on paraphrased guidance.

## Report rules

- Every dispatched ordinary sub-agent task must produce a file under `reports/` using `normal_persistence`.
- An independent-final reviewer using `deferred_attestation` is the intentional exception: `review-enforcer` reserves the path before freeze; this Skill reuses that exact reservation and does not create/edit/re-reserve the repository file until passing-verdict attestation.
- The parent should create the normal-persistence report file before dispatch whenever feasible.
- An approval-gated proposal or pre-dispatch capability gap may be recorded before a child report exists because no child was dispatched.
- The parent should pre-populate standard headings and parent-owned `Dispatch profile` fields.
- The fixed `Dispatch profile` section is parent-owned. The child must not attest to hidden spawn arguments, role application, final runtime profile, or user approval.
- If a normal-persistence child cannot write child-owned sections directly, the parent must write them immediately from returned evidence.
- For normal review/fix verification, built-in review results must be materialized before the task is complete.
- For deferred-attestation independent final review, retain the result and reservation identity as parent-owned evidence and do not materialize it until passing-verdict attestation.
- Do not stop/replace an in-flight reviewer merely because it is slow unless the user explicitly says to stop. Astra authorization withdrawal or an observed unapproved profile is handled through its reference's safe interruption rules, not as a performance timeout.
- Report text should be Japanese unless the user requests another language.
- Normal-persistence children must preserve report structure and existing parent text.

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

The fixed parent-owned `Dispatch profile` section contains:

- selection inputs, including observed decomposability and separate decomposition policy/disposition
- selection source
- proposed profile
- approval status/evidence
- for Astra, the complete versioned `astra_authorization` extension, including eligibility, cost notice, task/scope/agent binding, grant mode, per-operation usage, and invalidation
- requested profile
- explicit/default agent role plan and role-config evidence
- planned runtime profile
- applied profile, only when exactly observed
- application status
- runtime profile observability
- reviewer continuity
- fork policy
- reasons/constraints

## Minimum evidence contents

For every dispatched task, retain:

- task identifier/purpose
- why a sub-agent was used
- scope handled
- commands run
- files changed/checked
- findings summary or explicit `no findings`
- outcome/verdict
- unresolved risks/follow-up
- truthful decomposability plus decomposition policy/disposition
- requested and role-adjusted planning evidence
- exact applied profile when observable, otherwise explicit unverified state
- report persistence mode and reservation identity when deferred
- when applicable, Sol `xhigh` / Sol `max` proposal and approval evidence
- when applicable, Astra eligibility and complete grant/operation evidence; old records without this evidence do not authorize Astra
- when applicable, reviewer continuity evidence

For deferred attestation, these remain parent-owned lifecycle evidence until persistence is permitted.

## Outputs

After this skill runs for a normal-persistence dispatched task, there should be:

- a dispatched sub-agent task with explicit scope
- a pre-created report path under `reports/`
- recorded delegation assessment, requested profile, role plan, and planned runtime profile
- post-runtime exact applied evidence or explicit unverified/inherited/fallback/capability-gap state
- report-backed task evidence

For a deferred-attestation independent reviewer, there should be:

- one dispatched reviewer with explicit scope
- one inherited pre-freeze report reservation owned by `review-enforcer`; no second reservation
- no repository report file created/edited by the reviewer
- requested/role-plan/runtime-observability evidence retained by the parent
- structured review evidence retained by the parent for later attestation/fix-loop handling

When a Sol or Astra approval gate is pending, output instead includes:

- recorded `proposed_profile`
- cost/justification notice and applicable task/turn approval scope
- `application_status: awaiting_user_approval`
- no dispatch or work-starting continuation using that profile

When role/default-role or inherited-profile impact cannot be resolved safely before dispatch, output instead includes:

- `application_status: capability_gap`
- role/default-role identity and missing evidence
- no dispatch

## Completion condition

A normal-persistence dispatched task completes only when:

- required prompt content was used
- any required initial or role-adjusted expensive-profile approval preceded dispatch
- every Astra work-starting operation passed its task/scope-bound authorization gate and consumption was recorded
- post-runtime exact applied evidence **or** an explicit unverified/inherited/fallback/capability-gap state is recorded
- report file exists in expected location
- parent-owned dispatch evidence and child-owned task evidence are complete
- parent reviewed the result/evidence

For a deferred-attestation independent reviewer, dispatch work completes when the inherited pre-freeze reservation identity is validated, no duplicate reservation was created, the reviewer returns, runtime profile observability state is recorded, structured review and applicable authorization evidence is retained by the parent, and the reserved path remains unwritten. Repository report persistence completes later only through `review-enforcer`'s passing-verdict report attestation.

An approval-gated or pre-dispatch role-capability-gap task is intentionally incomplete. Authorization-only completion is the operation-specific decision described above, not task completion.

## Rules

- Keep sub-agent tasks small and concrete.
- Prefer one bounded request over one broad speculative request.
- Reuse existing reports before dispatching duplicate work.
- Honor `decomposition_policy: forbidden` without rewriting observed `decomposability`.
- Never use a decomposition prohibition as evidence that a problem is intrinsically non-decomposable for `max` selection.
- Use `execution-cost-stabilizer` before proposing `max`, Astra escalation, multi-agent decomposition, wasteful reruns, or excessive parallelism.
- Never dispatch Sol `xhigh` or Sol `max` without explicit current-task user approval, including when an agent role/default role raises the planned runtime profile to those efforts.
- Never start or continue Astra work without the eligibility, high-only, and scoped authorization rules in its reference; do not share or replay a consumed grant.
- If role/default-role impact on model/reasoning is unknown, stop before dispatch rather than assuming the requested profile survives role application.
- Do not make a sub-agent run nested Codex or parent-owned orchestration workflows.
- Do not leave report structure up to the child.
- Do not treat a model/reasoning mention in `message` as an override.
- Pass pre-spawn `requested` values to spawn; never use post-runtime `applied` as call input.
- Do not claim exact `applied` merely because spawn succeeded. When final profile metadata is hidden, record `spawn_succeeded_profile_unverified` with `applied: null`.
- Full-history behavior, role application, rejection, and fallback must follow the spawn reference and must not bypass Astra authorization.
- If independently separable work would justify multi-agent execution and decomposition is allowed, return it to `codex-delegation-executor`; if decomposition is forbidden, preserve the decomposability observation and record the suppression.
- Never create/edit an independent-final reserved report path before passing-verdict attestation.
- Never create a second deferred-attestation reservation when `review-enforcer` already supplied the pre-freeze reservation; ambiguity is a blocker, not a reason to re-reserve.

## Cross-cutting rule

If recurring sub-agent dispatch failures, profile misclassification, approval-gate bypasses, role-profile uncertainty, report omissions, duplicate reservations, or attestation-boundary violations appear, call `feedback-points-manager`.
