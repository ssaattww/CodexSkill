# Agent profile selection

Use this reference before dispatching every bounded `sub-agent` task.

The selector chooses a model tier, reasoning effort, and fork policy separately. It may return decomposable work to `codex-delegation-executor` only when the caller permits decomposition. Identity-sensitive reviewer tasks from `review-enforcer` are caller-locked to one agent and must remain `decomposability: single`.

## Current model family

Use the following runtime model IDs when they are available:

| Tier | Runtime model | Intended use |
| --- | --- | --- |
| Luna | `gpt-5.6-luna` | deterministic, repetitive, cost-sensitive, high-volume work |
| Terra | `gpt-5.6-terra` | ordinary implementation and bounded technical work |
| Sol | `gpt-5.6-sol` | ambiguous, high-risk, cross-system, design, debugging, and review work |

Use only reasoning effort values supported by the selected runtime model. For the GPT-5.6 family, the normalized values are `none`, `low`, `medium`, `high`, `xhigh`, and `max`.

`Ultra` is not a `reasoning_effort` value. Treat it as a multi-agent execution strategy for independently separable workstreams. `codex-delegation-executor` owns that decomposition decision when decomposition is allowed; this reference selects the profile for each resulting bounded task.

Do not use pricing as the primary selector. Use task nature, uncertainty, change radius, and criticality first, then choose the least expensive profile that satisfies the resulting floor.

## Mandatory user-approval gate for expensive Sol profiles

`Sol xhigh` and `Sol max` are approval-gated profiles. They are never selected or dispatched automatically.

When automatic classification, repository policy, escalation, or another Skill concludes that either profile is appropriate:

1. classify it only as a `proposed_profile`
2. explain why `Sol high` is insufficient and what benefit the higher effort is expected to provide
3. state that `Sol xhigh` or `Sol max` has higher execution cost
4. present the proposed profile to the user
5. stop the dispatch flow before creating or invoking the sub-agent with that profile
6. wait for explicit user approval
7. only after approval, promote the proposal to `requested` and continue runtime application

An explicit user instruction in the current task that directly requests `Sol xhigh` or `Sol max` counts as approval. A repository policy, previous approval for another task, inferred preference, or silence does not count.

If the user rejects the proposal, recompute the profile with `Sol xhigh` and `Sol max` excluded. Normally the highest automatic fallback is `Sol high`, but classification must still be recomputed rather than silently copying the rejected proposal.

This gate has higher precedence than repository policy and automatic selection. It also applies to review and release-audit tasks.

## Selection inputs

Record these signals before choosing a profile:

- `task_kind`: implementation, design, investigation, review, verification, environment verification, intake verification, standards work, or other
- `work_class`: `mechanical`, `bounded_technical`, or `judgment_heavy`
- `uncertainty`: `low`, `medium`, or `high`
- `change_radius`: `local`, `cross_module`, or `cross_system`
- `criticality`: `ordinary` or `high`
- `repetition`: `single` or `high_volume`
- `decomposability`: `single`, `sequential_dependencies`, or `independent_workstreams`
- `decomposition_policy`: `allowed` or `forbidden`
- `context_need`: `fresh`, `bounded_history`, or `full_history`
- explicit user or repository model, effort, budget, and availability constraints
- approval state when `Sol xhigh` or `Sol max` is proposed
- existing agent identity and its applied profile when the caller requests continuity reuse

`criticality: high` includes security, authorization, privacy, destructive data handling, schema or data migration, concurrency, compatibility, public API, release, deployment, and other changes where an incorrect result has a large or difficult-to-reverse impact.

When `decomposition_policy: forbidden`, preserve `decomposability: single` even if the scope contains several review areas. This is required for `review-enforcer` reviewer identity and one-pass lifecycle guarantees.

## Model-tier rules

Choose the highest floor required by any applicable rule.

### Luna floor

Use Luna only when all of the following are true:

- the expected behavior and procedure are already decided
- uncertainty is low
- the change or evidence scope is local
- criticality is ordinary
- the task is mechanical, repetitive, or high-volume
- success can be checked with explicit deterministic evidence

Examples include exact formatting, generated-file updates, repetitive metadata edits, known-command execution, extraction, classification, and bounded evidence collection.

Do not use Luna for open-ended investigation, root-cause analysis, architecture, requirement interpretation, independent review, or failure diagnosis.

### Terra floor

Use Terra for ordinary bounded technical work, including:

- implementation from accepted requirements with a bounded change radius
- focused verification whose commands and expected evidence are known
- localized investigation with a concrete hypothesis
- a newly created reviewer dedicated only to focused fix verification when continuity reuse is unavailable
- cross-module work whose behavior is still well specified and whose risk is ordinary

Raise Terra from `medium` to `high` when the task spans modules, has several interacting conditions, or needs careful regression reasoning but does not require Sol.

### Sol floor

Use Sol when any of the following applies:

- requirements or architecture must be decided
- uncertainty is high or the task is judgment-heavy
- root cause is unknown or spans layers
- change radius is cross-system
- criticality is high
- the task is an initial review, independent final review, release audit, security review, or compatibility review
- evidence conflicts and must be adjudicated
- the task requires synthesizing several technical domains

Do not downgrade a Sol-floor task merely because the expected edit is small. Change radius, uncertainty, and consequence take precedence over line count.

## Task defaults

Use these defaults after applying the floors above. A value marked `proposal` is not dispatchable until the user approves it. Defaults apply only when a new sub-agent is being created; continuity reuse preserves the existing agent profile instead of reselecting a default.

| Task | Default profile | Escalation |
| --- | --- | --- |
| exact repetitive transformation | Luna `low` | Luna `medium` when validation interpretation is needed |
| deterministic build or test execution | Luna `medium` | Reclassify failure diagnosis as investigation |
| ordinary bounded implementation | Terra `medium` | Terra `high` for cross-module or multi-factor work |
| localized debugging with a concrete hypothesis | Terra `high` | Sol `high` when the hypothesis fails or layers interact |
| design or requirement interpretation | Sol `high` | propose Sol `max`; stop for user approval |
| open-ended or cross-layer investigation | Sol `high` | propose Sol `max`; stop for user approval |
| initial normal review | Sol `high` | propose Sol `xhigh`; stop for user approval |
| focused fix verification, new reviewer only | Terra `high` | Sol `high` when the original finding or changed scope is high-criticality |
| independent final review or release audit | propose Sol `xhigh` | stop for user approval; propose Sol `max` only for one inseparable proof obligation |

Do not use `none` by default for delegated development work. It may be used only for an explicitly deterministic operation that requires no technical judgment and has a complete mechanical validator.

## Reviewer continuity rule

When `review-enforcer` requests reuse of an already-running normal reviewer or independent reviewer, continuity takes precedence over the task default table.

- do not spawn a replacement merely to apply the focused fix-verification default
- do not reselect Terra `high`, Sol `high`, `xhigh`, or `max` for the existing agent
- preserve the model, reasoning effort, and fork context that were actually applied when that reviewer was created
- record `application_status: reused_existing_agent_profile`
- record the reviewer identity and the original applied profile as continuity evidence
- record the continued review mode, such as `fix_verification` or `finding_ci_delta_closure`

Reusing an already-approved `Sol xhigh` or `Sol max` reviewer in the same review lifecycle does not create a new expensive-profile selection. The original approval evidence remains attached to that reviewer. A new reviewer, a replacement reviewer, or a new task lifecycle must pass profile selection and any applicable approval gate again.

If the original applied profile is unknown, do not invent it. Record the evidence gap and let `review-enforcer` decide whether continuity can be trusted or a replacement reviewer must be created through the normal selection path.

## Reasoning-effort rules

Choose reasoning effort independently from model tier:

- `low`: exact, low-risk transformations with explicit expected output
- `medium`: ordinary bounded implementation or deterministic evidence work
- `high`: multiple interacting conditions, careful debugging, design, or review
- `xhigh`: exhaustive or high-stakes review and audit with a bounded scope; when paired with Sol, user approval is mandatory
- `max`: one exceptionally difficult, non-decomposable problem where deeper reasoning is more useful than splitting the task; when paired with Sol, user approval is mandatory

Do not use `max` as a generic quality setting. Before proposing it, call `execution-cost-stabilizer` and record why Sol `high` or an independently decomposed plan is insufficient.

## Multi-agent decision

Return the task to `codex-delegation-executor` for decomposition only when `decomposition_policy: allowed` and all of the following hold:

- there are at least two independently executable workstreams
- each workstream can have explicit scope, non-goals, evidence, and report ownership
- write ownership does not overlap, or the tasks are read-only
- a parent synthesis step is defined
- parallel execution provides material value after applying `execution-cost-stabilizer`

Do not return a caller-locked task for decomposition. In particular, every reviewer task from `review-enforcer` has `decomposition_policy: forbidden` and remains one reviewer regardless of review breadth.

Each decomposed task receives its own profile. Do not assign one shared profile merely because the tasks run together.

## Override and availability precedence

Apply precedence in this order:

1. explicit current-task user instruction, including explicit approval for `Sol xhigh` or `Sol max`
2. mandatory user-approval gate for an unapproved `Sol xhigh` or `Sol max` proposal
3. reviewer continuity reuse of an existing agent and its actually applied profile
4. caller-owned decomposition prohibition
5. authoritative repository policy
6. runtime capability and model availability
7. automatic selection rules in this reference

An override may pin the model, effort, or both. Continue to classify the task and record when the override is below the automatically calculated floor. Do not silently replace an explicit override. Report the mismatch and follow the governing authority.

A repository policy that requests `Sol xhigh` or `Sol max` creates a proposal but cannot satisfy the approval gate.

## Dispatch profile schema

For an ordinary newly dispatched profile before the spawn call:

```yaml
dispatch_profile:
  schema_version: 3
  selection_source: automatic | user_override | repository_policy
  task_kind: review
  signals:
    work_class: judgment_heavy
    uncertainty: high
    change_radius: cross_module
    criticality: high
    repetition: single
    decomposability: single
    decomposition_policy: forbidden
    context_need: fresh
  requested:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
    parallelism_mode: single_agent
  applied: null
  application_status: pending_runtime_result
  approval:
    required: false
    status: not_required
  reasons: []
  constraints: []
  escalation_triggers: []
```

`requested` is the pre-spawn instruction. `applied` is not known yet.

After the call, fill `applied` and replace `pending_runtime_result` using actual runtime evidence:

```yaml
applied:
  model: <actual model or inherited parent model>
  reasoning_effort: <actual effort or inherited parent effort>
  fork_turns: <actual fork policy>
application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
```

Never copy `requested` into `applied` merely because the call was attempted.

For approval-gated profiles, keep the candidate out of `requested` until approval:

```yaml
dispatch_profile:
  schema_version: 3
  selection_source: automatic | repository_policy
  proposed_profile:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: xhigh | max
    fork_turns: none
    parallelism_mode: single_agent
  requested: null
  applied: null
  application_status: awaiting_user_approval
  approval:
    required: true
    status: pending | approved | rejected
    approved_by: null
    approval_evidence: null
  reasons:
    - why Sol high is insufficient
  cost_notice:
    - higher reasoning effort increases execution cost
```

For continuity reuse:

```yaml
dispatch_profile:
  schema_version: 3
  selection_source: continuity_reuse
  task_kind: review
  requested: null
  applied:
    model: <original applied model>
    reasoning_effort: <original applied effort>
    fork_turns: <original fork policy>
  application_status: reused_existing_agent_profile
  continuity:
    reviewer_identity: <existing reviewer>
    continued_mode: fix_verification | finding_ci_delta_closure
    original_profile_evidence: <report or spawn evidence>
  approval:
    required: false
    status: inherited_from_original_dispatch | not_required
```

After explicit approval, copy the approved proposal into `requested`, record approval evidence, and only then follow [spawn-agent-model-overrides.md](spawn-agent-model-overrides.md). Never claim the requested profile was applied without actual runtime evidence.

## Fork policy

- Use `fork_turns: "none"` for a fresh specialist when applying a model or reasoning override.
- Use an explicit positive partial fork only when the required history is bounded and identified.
- A full-history fork inherits the parent execution profile. Preserve the requested specialization as unapplied evidence and record `application_status: inherited_parent_profile` only from the actual inheritance path.
- Prefer fresh context plus explicit task-local inputs over a full-history fork when specialization matters.
- Continuity reuse keeps the existing agent context and is not represented as a new fork operation.

## Reclassification and escalation

Recompute the profile when new evidence changes uncertainty, change radius, criticality, or task kind and a new agent would be dispatched.

- A failed deterministic verification becomes investigation; do not keep retrying it as Luna work.
- A localized implementation that exposes architectural ambiguity becomes Sol work.
- A task that becomes cleanly separable returns to `codex-delegation-executor` only when decomposition is allowed.
- Raise reasoning effort when the problem is unchanged but needs more careful analysis.
- Raise model tier when the nature of the problem changes or the current model lacks the required judgment capability.
- If escalation reaches Sol `xhigh` or Sol `max`, convert it to a proposal and stop for user approval instead of dispatching.
- Do not recompute the profile merely because an existing reviewer moved from initial review to fix verification or bounded closure.

Avoid blind retry loops. Record the reason for every profile escalation or fallback and reuse existing evidence.

## Evidence requirement

Every dispatched task lifecycle must record:

- all selection inputs
- requested profile before spawn
- applied profile only after runtime evidence exists
- selection source and rationale
- fork policy
- runtime rejection, inheritance, or fallback, if any
- reclassification or escalation, if any
- whether multi-agent decomposition was allowed, considered, and used
- for `Sol xhigh` or `Sol max`, the proposal, cost notice, approval status, and explicit approval evidence
- for reviewer continuity, existing reviewer identity, original applied profile evidence, continued mode, and `application_status: reused_existing_agent_profile`

A proposal that is still awaiting approval is a stopped workflow state, not a dispatched task.

## References

- [Adaptive agent assignment design](../../../design/adaptive-agent-assignment-design.md)
- [Execution Cost Stabilizer](../../execution-cost-stabilizer/SKILL.md)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [OpenAI latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [参考記事: 役割分担で回すGPT-5.6 Luna / Terra / Sol](https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb)
