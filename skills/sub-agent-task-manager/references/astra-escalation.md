# Astra escalation and authorization

This reference is owned by `sub-agent-task-manager`. Read it before proposing, starting, continuing, resuming, retrying, or inheriting any execution that could use Astra. It extends [agent-profile-selection.md](agent-profile-selection.md) and [spawn-agent-model-overrides.md](spawn-agent-model-overrides.md); their ordinary Luna/Terra/Sol rules remain in force.

## Profile and scope invariants

- Astra is an escalation-only profile, not an automatic task default or ordinary higher-tier availability substitute.
- Resolve Astra to `gpt-6-astra`. This repository permits only `reasoning_effort: high` for Astra, even if the runtime supports other efforts.
- Astra authorization permits one scoped sub-agent's work, not changing the parent model or using parent-owned `codex exec` as an Astra fallback.
- Authorization does not grant filesystem, network, computer-use, destructive-action, nested-agent, or merge permission.
- Apply these rules to requested, role-adjusted, inherited, replacement, and reused profiles. A different entry path must not bypass the gate.
- Current-task profile overrides and repository policy do not manufacture eligibility, cost disclosure, or user approval. An instruction changing this policy must be explicit; merely requesting Astra does not waive its prerequisites.

## Eligibility before proposal

Require evidence of an actual attempt using an existing Luna/Terra/Sol model on the same accepted task, a problem encountered in that attempt, and the parent's concrete judgment that continuing the existing approach is unlikely to resolve it.

Record:

1. stable task ID, scope ID, scope description, and completion conditions;
2. prior attempt identity, work performed, requested model, observed applied model or explicit uncertainty, and actual result/blocker evidence;
3. why further work with the existing approach is insufficient, not just that an error occurred;
4. lower-cost investigation, scope reduction, and evidence-reuse options considered with `execution-cost-stabilizer`;
5. the task-specific expected benefit of Astra, such as understanding unfamiliar interaction rules or reconciling evidence that defeats the current hypothesis.

It is not necessary to exhaust every existing tier. Do not claim an unobserved model was applied, invent a failed attempt, or convert benchmark performance into a guarantee of solving this task. High difficulty, many files, computer use, review, and a first failing test do not by themselves establish eligibility. Authentication, unavailable tools, missing authority, network failure, or missing required user input must not be bypassed by model escalation when a model change cannot resolve the blocker.

Without this evidence, keep Astra unselected and return missing prerequisites or an ordinary-model plan. Eligibility is required even when Astra appears through role configuration or parent-profile inheritance.

## Proposal and explicit consent

Once eligible:

1. create `proposed_profile` with `model_tier: astra`, `model: gpt-6-astra`, and `reasoning_effort: high`;
2. keep the Astra candidate out of `requested` and do not invoke it;
3. present the prior attempt, blocker, expected benefit, exact bounded next work, model/effort, and cost notice;
4. offer `single_turn` as the default and `task_until_completion` only as an explicit option;
5. stop before Astra execution until the user explicitly approves the presented proposal and scope;
6. after approval, promote the proposal to `requested`, then perform role, availability, fork, and operation-boundary checks before consuming authorization.

Cost notice must identify the comparison baseline and evidence date, available pricing or usage evidence, and any unknown actual cost. Do not encode Issue #67's 2.4x estimate as a fixed price or total-work multiplier. Official API standard short-context prices checked on 2026-09-06 are Astra $10/$50 and Sol $4/$20 per million input/output tokens (2.5x unit prices); actual Codex cost/usage depends on the user's offering and execution. Recheck current applicable information when presenting a real proposal; disclose unavailable estimates instead of inventing them.

Silence, repository policy, approval of a different task/profile, an old report, and inferred preference are not consent. A direct affirmative answer to a clearly presented single-turn request can approve that request. A generic implementation or PR instruction does not. Ambiguous approval never becomes indefinite or task-wide approval.

On rejection, exclude Astra and recompute under the ordinary selector and existing Sol approval gates. Do not silently select Sol xhigh/max or keep asking the same rejected proposal without a user request to reconsider or materially new evidence.

## Authorization modes and turn boundary

`single_turn` authorizes one operation for one agent and one task. A turn starts when the parent submits a bounded work request and ends when that agent returns a result, failure, interruption, or request for more input. Internal reasoning and tool calls within that bounded operation are not separate turns.

A new `send_input`, work-starting resume, retry, or other additional work request is a new turn, even within the same parent message or user turn. Require new single-turn approval before it. Status polling, waiting, reading existing output, and a resume that only restores access without starting work do not consume authorization.

`task_until_completion` authorizes later operations only within the explicitly approved task ID, scope, and completion conditions. Validate the grant before every operation, but do not repeatedly ask for approval while that grant remains valid. Task-wide approval does not authorize unlimited blind retries; return to cost stabilization when there is no progress.

For both modes:

- bind authorization to the current parent context, task ID, scope ID, exact profile, and one agent/dispatch slot;
- a new agent or decomposed/sibling task does not inherit the grant;
- ordinary corrective commits within unchanged scope do not alone change task identity; record the target HEAD for each operation;
- expire the grant on task completion, cancellation, scope/acceptance expansion, or a new lifecycle, including a reopened completed task;
- revoke on user withdrawal; do not start further work and use available safe interruption when needed, recording whether in-flight execution actually stopped;
- a handoff preserves evidence but does not transfer permission to a new parent session; re-establish current-user authority there;
- never broaden a task grant to the whole repository, Issue, PR, branch, or future tasks implicitly.

Each single-turn prompt must contain a bounded work unit, stop/return conditions, no nested agents, and no autonomous requeue after returning. Do not hide continued work inside an unbounded instruction to evade another approval.

## Parent-owned operation gate

Run this gate immediately before every operation that can start Astra work, including continuity reuse. The parent owns serialization; parallel requests must not race on a shared grant.

1. Resolve actual task/scope and current parent context. Verify eligibility evidence is present and still describes this task.
2. Resolve the exact requested or originally established profile and all role/default-role/inheritance effects. Verify the planned profile is Astra high, or determine the operation is non-Astra. Unknown potential Astra exposure is a capability gap, not permission to proceed.
3. Check the current grant's explicit approval evidence, profile, scope, mode, owner, agent/dispatch-slot binding, and completion/revocation/expiry state.
4. Identify a unique operation ID, whether it starts work, its bounded work unit, and target HEAD.
5. For `single_turn`, bind and mark the approved grant `consumed` immediately before submitting that one operation. For `task_until_completion`, record the operation under the still-valid grant.
6. Invoke only after these checks. Capture returned agent identity and bind a spawn's reserved dispatch slot to it.
7. Record operation outcome, runtime observability, and any failure. Preserve the immutable usage history.

An issued request consumes single-turn authorization even if it is rejected, times out, or its execution start is uncertain. Do not automatically retry with the same grant. Inspect existing operation state without starting work; a further invocation requires new approval. A preflight failure before submission does not consume a grant, but any changed scope/profile requires renewed consent.

Missing, pending, rejected, consumed, expired, revoked, or mismatched authorization means no work-starting call. Preserve `application_status: awaiting_user_approval` for pending approval and an explicit capability gap for an unresolved runtime constraint. Do not manufacture `reused_existing_agent_profile` execution evidence for a continuation that was not invoked; retain original evidence separately.

## Runtime and fallback safeguards

- New Astra spawns require both `requested` and the known `planned_runtime_profile` to resolve to `gpt-6-astra` / `high`. An alias is acceptable only with authoritative evidence that it resolves to that same model.
- Role/default-role changes to Astra must return through this reference even when the initial request was an ordinary model. A role fixing Astra to a different effort is incompatible; user consent to Astra high does not authorize it.
- Availability resolution to a same/higher tier must not automatically pick Astra. Resolve its eligibility and approval first; never overwrite an explicitly pinned identifier silently.
- For full-history inheritance, inspect the effective inherited model/effort and role path before dispatch. If Astra high and the approved scope cannot be guaranteed, re-plan fresh/partial context or stop. Omitting override arguments is not an approval bypass.
- Unknown relevant role, inherited profile, or existing-agent profile that might be Astra blocks new work until the cost gate can be enforced. Do not mark a known Sol reviewer unknown merely because unrelated metadata is hidden.
- Astra spawn rejection or unavailability does not authorize parent `codex exec`, parent model switching, another agent, nested Codex, or an unapproved higher-cost fallback. Record a capability gap and return a non-Astra plan or explicit user decision.
- A successful call without final profile evidence remains `applied: null` with the appropriate unverified observability state. Known safe preflight and explicit approval are still necessary.
- If an observed final profile differs from the approved Astra high profile, record the discrepancy, do not send more work, use safe interruption where available, and re-plan. Do not silently relabel the actual profile as approved.

## Existing agents and reviewer continuity

The `authorization_only` mode of `sub-agent-task-manager` evaluates this gate for a caller-owned existing agent. It must not spawn, replace the reviewer, reselect task defaults, reserve/create a report, or mutate the original runtime-profile evidence.

`review-enforcer` remains the owner of reviewer identity and continuity. Before starting fix verification or bounded closure on an Astra reviewer, it obtains a positive authorization result for that operation. Reusing the same identity is not exemption from per-turn approval. A valid explicit `task_until_completion` grant can cover the same bounded review task until its recorded completion conditions, but not a different review lifecycle or a replacement reviewer.

Preserve the original rules for a known, already-approved Sol xhigh/max reviewer in the same lifecycle. Do not demand Astra-specific approval for that non-Astra continuation. Do not replace or reconfigure an existing reviewer merely to adopt Astra; use only already-permitted replacement procedures. If escalation conflicts with independent reviewer identity, single-reviewer policy, or one-exhaustive-pass semantics, return a lifecycle blocker rather than bypassing them.

## Evidence extension

Keep existing `dispatch_profile.schema_version: 4` fields and observability semantics. Add the following versioned extension for every Astra proposal or possible Astra operation. Ordinary non-Astra dispatch records need no fabricated Astra grant. Legacy records lacking this extension are not proof of Astra authorization.

```yaml
astra_authorization:
  schema_version: 1
  eligibility:
    task_id: task-identifier
    scope_id: accepted-scope-identifier
    completion_conditions: []
    prior_attempts:
      - identity: existing-model-attempt
        requested_model: gpt-5.6-sol
        applied_model: null
        profile_observability: final_profile_hidden
        result_evidence: report-or-operation-reference
    blocker_evidence: evidence-reference
    continuation_insufficient_reason: task-specific-reason
    lower_cost_options_considered: []
    expected_benefit: task-specific-benefit
  proposal:
    id: proposal-identifier
    model: gpt-6-astra
    reasoning_effort: high
    next_work_unit: bounded-work-description
    cost_notice:
      baseline: existing-profile
      evidence_date: null
      source: null
      estimate: unknown
      unknowns: []
  grant:
    id: null
    status: pending
    mode: single_turn
    parent_context_id: current-parent-context
    task_id: task-identifier
    scope_id: accepted-scope-identifier
    agent_identity_or_dispatch_slot: reserved-slot
    approved_by: null
    approval_evidence: null
    invalidation_reason: null
  usage: []
```

Grant status is `pending | approved | rejected | consumed | expired | revoked`. Grant mode is `single_turn | task_until_completion`. Bind the approval evidence to the presented proposal and mode; preserve superseded grants instead of replacing history. `approved_by` identifies the user, not a child agent or repository policy.

Each usage entry records `operation_id`, `operation_kind` (`spawn | continue | resume`), `agent_identity_or_dispatch_slot`, `task_id`, `scope_id`, `target_head`, `work_unit`, `grant_id`, `authorization_result`, `consumed_before_submission`, `outcome`, and an evidence reference. A retry is a new operation with new single-turn consent, not a second use of the original ID. Do not put sensitive message contents or credentials in authorization evidence.

For normal persistence, record this extension in the parent-owned `Dispatch profile` report section. For deferred attestation, retain it with the existing parent-owned lifecycle evidence without touching the reserved report path before the passing verdict. An approval stop before dispatch is evidence of no child execution, not a missing successful child report.

## References

- [Astra escalation design and acceptance cases](../../../design/astra-escalation-design.md)
- [Issue #67](https://github.com/ssaattww/CodexSkill/issues/67)
- [GPT-6 Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- [Codex subagents](https://developers.openai.com/codex/subagents)
