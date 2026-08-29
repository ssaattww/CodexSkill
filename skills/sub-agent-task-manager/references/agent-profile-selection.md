# Agent profile selection

Use this reference before dispatching every bounded `sub-agent` task.

The selector chooses a model tier, reasoning effort, and fork policy separately. It records task decomposability as an observed signal and execution decomposition policy as a separate caller constraint. It may return decomposable work to `codex-delegation-executor` only when decomposition is allowed.

## Current model family

Use the following runtime model IDs when they are available:

| Tier | Runtime model | Intended use |
| --- | --- | --- |
| Luna | `gpt-5.6-luna` | deterministic, repetitive, cost-sensitive, high-volume work |
| Terra | `gpt-5.6-terra` | ordinary implementation and bounded technical work |
| Sol | `gpt-5.6-sol` | ambiguous, high-risk, cross-system, design, debugging, and review work |

Use only reasoning effort values supported by the selected runtime model. For the GPT-5.6 family, the normalized values are `none`, `low`, `medium`, `high`, `xhigh`, and `max`.

`Ultra` is not a `reasoning_effort` value. Treat it as a multi-agent execution strategy for independently separable workstreams. `codex-delegation-executor` owns that decomposition decision when decomposition is allowed; this reference selects the profile for each resulting bounded task.

Do not use pricing as the primary selector. Use task nature, uncertainty, change radius, criticality, and observed decomposability first, then choose the least expensive profile that satisfies the resulting floor and caller constraints.

## Mandatory user-approval gate for expensive Sol profiles

`Sol xhigh` and `Sol max` are approval-gated profiles. They are never selected or dispatched automatically.

When automatic classification, repository policy, escalation, agent-role planning, or another Skill concludes that either profile is appropriate:

1. classify it only as a `proposed_profile`
2. explain why `Sol high` is insufficient and what benefit the higher effort is expected to provide
3. state that `Sol xhigh` or `Sol max` has higher execution cost
4. present the proposed profile to the user
5. stop the dispatch flow before creating or invoking the sub-agent with that profile
6. wait for explicit current-task user approval
7. only after approval, promote the proposal to `requested` and continue runtime application

An explicit user instruction in the current task that directly requests `Sol xhigh` or `Sol max` counts as approval. A repository policy, previous approval for another task, inferred preference, or silence does not count.

If the user rejects the proposal, recompute the profile with `Sol xhigh` and `Sol max` excluded. Normally the highest automatic fallback is `Sol high`, but classification must still be recomputed rather than silently copying the rejected proposal.

This gate has higher precedence than repository policy and automatic selection. It also applies to role/default-role profile changes, review, and release-audit tasks.

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
- explicit user or repository model, effort, budget, availability, fork, or agent-role constraints
- applicable explicit/default agent-role configuration evidence when runtime roles can change model or reasoning
- approval state when `Sol xhigh` or `Sol max` is proposed
- existing agent identity and original applied-profile evidence when the caller requests continuity reuse

`criticality: high` includes security, authorization, privacy, destructive data handling, schema or data migration, concurrency, compatibility, public API, release, deployment, and other changes where an incorrect result has a large or difficult-to-reverse impact.

## Decomposability versus decomposition policy

`decomposability` is an observation about the work. `decomposition_policy` is an execution constraint. Never rewrite the observed signal merely to satisfy the policy.

Examples:

- A large review can truthfully be `decomposability: independent_workstreams` while `decomposition_policy: forbidden` because reviewer identity and one-pass lifecycle semantics require one reviewer.
- A migration with strictly ordered steps can be `decomposability: sequential_dependencies` regardless of whether the caller allows parallel decomposition.
- A genuinely inseparable proof obligation is `decomposability: single`.

When decomposition is forbidden:

- preserve the observed `decomposability`
- set `decomposition_disposition: prohibited_by_caller_policy`
- execute with one agent as required
- do not use the policy prohibition as evidence that the underlying problem is intrinsically non-decomposable

This distinction matters for `max`: a caller policy that forbids splitting does not make an `independent_workstreams` problem qualify as a non-decomposable `max` problem.

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
| design or requirement interpretation | Sol `high` | propose Sol `max` only for an intrinsically inseparable problem |
| open-ended or cross-layer investigation | Sol `high` | propose Sol `max` only for an intrinsically inseparable root cause |
| initial normal review | Sol `high` | propose Sol `xhigh`; stop for user approval |
| focused fix verification, new reviewer only | Terra `high` | Sol `high` when the original finding or changed scope is high-criticality |
| independent final review or release audit | propose Sol `xhigh` | stop for user approval; propose Sol `max` only for one intrinsically inseparable proof obligation |

Do not use `none` by default for delegated development work. It may be used only for an explicitly deterministic operation that requires no technical judgment and has a complete mechanical validator.

## Reviewer continuity rule

When `review-enforcer` requests reuse of an already-running normal reviewer or independent reviewer, continuity takes precedence over the task default table.

- do not spawn a replacement merely to apply the focused fix-verification default
- do not reselect Terra `high`, Sol `high`, `xhigh`, or `max` for the existing agent
- preserve the model, reasoning effort, and fork context that were actually established when that reviewer was created
- if exact original model/reasoning evidence was unavailable, preserve that uncertainty rather than inventing an exact profile
- record `application_status: reused_existing_agent_profile` only together with the original observability state
- record the reviewer identity and the original applied/unverified profile evidence as continuity evidence
- record the continued review mode, such as `fix_verification` or `finding_ci_delta_closure`

Reusing an already-approved `Sol xhigh` or `Sol max` reviewer in the same review lifecycle does not create a new expensive-profile selection. The original approval evidence remains attached to that reviewer. A new reviewer, a replacement reviewer, or a new task lifecycle must pass profile selection and any applicable approval gate again.

## Reasoning-effort rules

Choose reasoning effort independently from model tier:

- `low`: exact, low-risk transformations with explicit expected output
- `medium`: ordinary bounded implementation or deterministic evidence work
- `high`: multiple interacting conditions, careful debugging, design, or review
- `xhigh`: exhaustive or high-stakes review and audit with a bounded scope; when paired with Sol, user approval is mandatory
- `max`: one exceptionally difficult, intrinsically non-decomposable problem where deeper reasoning is more useful than splitting the task; when paired with Sol, user approval is mandatory

Do not use `max` as a generic quality setting. Before proposing it, call `execution-cost-stabilizer` and record why Sol `high`, Sol `xhigh`, or an independently decomposed plan is insufficient.

`decomposition_policy: forbidden` never satisfies the intrinsic non-decomposability requirement. If `decomposability: independent_workstreams`, do not justify `max` merely because the caller requires single-agent execution.

## Multi-agent decision

Return the task to `codex-delegation-executor` for decomposition only when `decomposition_policy: allowed` and all of the following hold:

- there are at least two independently executable workstreams
- each workstream can have explicit scope, non-goals, evidence, and report ownership
- write ownership does not overlap, or the tasks are read-only
- a parent synthesis step is defined
- parallel execution provides material value after applying `execution-cost-stabilizer`

When decomposition is forbidden but observed decomposability is `independent_workstreams`, record that decomposition was considered but suppressed by caller policy. Do not falsify the observed signal.

Each decomposed task receives its own profile. Do not assign one shared profile merely because the tasks run together.

## Agent-role/default-role re-evaluation

Current Codex MultiAgent V2 applies requested model/reasoning overrides before applying the explicit or default agent role. A role can therefore replace or lock model/reasoning after the selector creates `requested`.

Before spawn, require the runtime call planner to record:

```yaml
role_plan:
  explicit_agent_type: <role or null>
  effective_role: <role name>
  role_config_evidence: <path/source or null>
  profile_effect: unchanged | changed | locked | unknown
planned_runtime_profile:
  model: <known planned model or null>
  reasoning_effort: <known planned effort or null>
```

Rules:

- If the role/default role changes model tier or reasoning effort, re-evaluate floors and the expensive Sol approval gate against `planned_runtime_profile` before spawn.
- If the role/default role would produce Sol `xhigh` or Sol `max`, stop for current-task user approval even when the original `requested` profile was cheaper.
- If the role forces a profile below the required floor, record a policy/capability mismatch rather than silently accepting it.
- If applicable role configuration cannot be inspected well enough to determine whether it changes model/reasoning, stop before spawn with a role-profile capability gap. This is required to prevent an unobservable role from bypassing the expensive-profile gate.
- `planned_runtime_profile` is planning evidence, not `applied` evidence.

After spawn, exact `applied` may be recorded only when the parent can observe a trustworthy final runtime/config snapshot. If the call succeeds but final model/reasoning metadata is hidden, keep `applied: null` and use `application_status: spawn_succeeded_profile_unverified`.

## Override and availability precedence

Apply precedence in this order:

1. explicit current-task user instruction, including explicit approval for `Sol xhigh` or `Sol max`
2. mandatory user-approval gate for an unapproved initial or role-adjusted Sol `xhigh` / Sol `max` proposal
3. reviewer continuity reuse of an existing agent and its original observability state
4. caller-owned decomposition policy
5. authoritative repository policy
6. runtime role/default-role constraints and model availability
7. automatic selection rules in this reference

An override may pin the model, effort, or both. Continue to classify the task and record when the override is below the automatically calculated floor. Do not silently replace an explicit override. Report the mismatch and follow the governing authority.

A repository policy that requests Sol `xhigh` or Sol `max` creates a proposal but cannot satisfy the approval gate.

## Dispatch profile schema

For an ordinary newly dispatched profile before role/runtime planning:

```yaml
dispatch_profile:
  schema_version: 4
  selection_source: automatic | user_override | repository_policy
  task_kind: review
  signals:
    work_class: judgment_heavy
    uncertainty: high
    change_radius: cross_module
    criticality: high
    repetition: single
    decomposability: independent_workstreams
    decomposition_policy: forbidden
    decomposition_disposition: prohibited_by_caller_policy
    context_need: fresh
  requested:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
    parallelism_mode: single_agent
  role_plan:
    explicit_agent_type: null
    effective_role: default
    role_config_evidence: <source>
    profile_effect: unchanged
  planned_runtime_profile:
    model: gpt-5.6-sol
    reasoning_effort: high
  applied: null
  application_status: pending_runtime_result
  profile_observability: pending
  approval:
    required: false
    status: not_required
  reasons: []
  constraints: []
  escalation_triggers: []
```

`requested` and `planned_runtime_profile` are pre-spawn evidence. `applied` is not known yet.

When a trustworthy final snapshot is parent-visible:

```yaml
applied:
  model: <observed final model>
  reasoning_effort: <observed final effort>
  fork_turns: <established fork policy>
application_status: applied_verified
profile_observability: verified_final_snapshot
```

When spawn succeeds but final model/reasoning cannot be observed:

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
profile_observability: final_profile_hidden
```

Never copy `requested` or `planned_runtime_profile` into `applied` merely because the call succeeded.

For approval-gated profiles, keep the candidate out of `requested` until approval:

```yaml
dispatch_profile:
  schema_version: 4
  selection_source: automatic | repository_policy | role_adjustment
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
  schema_version: 4
  selection_source: continuity_reuse
  task_kind: review
  requested: null
  applied: <original exact profile or null when originally unverified>
  application_status: reused_existing_agent_profile
  profile_observability: <original observability state>
  continuity:
    reviewer_identity: <existing reviewer>
    continued_mode: fix_verification | finding_ci_delta_closure
    original_profile_evidence: <report or spawn evidence>
  approval:
    required: false
    status: inherited_from_original_dispatch | not_required
```

After explicit approval, copy the approved proposal into `requested`, record approval evidence, then run role/default-role planning and follow [spawn-agent-model-overrides.md](spawn-agent-model-overrides.md). A later role adjustment can require a second approval check if it raises the planned profile to Sol `xhigh` or Sol `max`.

## Fork policy

- Use `fork_turns: "none"` for a fresh specialist when applying a model or reasoning override.
- Use an explicit positive partial fork only when the required history is bounded and identified.
- A full-history fork follows the runtime inheritance/role path. Preserve requested specialization as unapplied evidence until final profile observability is established.
- Prefer fresh context plus explicit task-local inputs over a full-history fork when specialization matters.
- Continuity reuse keeps the existing agent context and is not represented as a new fork operation.

## Reclassification and escalation

Recompute the profile when new evidence changes uncertainty, change radius, criticality, task kind, or known role-adjusted runtime plan and a new agent would be dispatched.

- A failed deterministic verification becomes investigation; do not keep retrying it as Luna work.
- A localized implementation that exposes architectural ambiguity becomes Sol work.
- A task that becomes cleanly separable returns to `codex-delegation-executor` only when decomposition is allowed.
- Raise reasoning effort when the problem is unchanged but needs more careful analysis.
- Raise model tier when the nature of the problem changes or the current model lacks the required judgment capability.
- If escalation or role planning reaches Sol `xhigh` or Sol `max`, convert it to a proposal and stop for user approval instead of dispatching.
- Do not recompute the profile merely because an existing reviewer moved from initial review to fix verification or bounded closure.

Avoid blind retry loops. Record the reason for every profile escalation, role adjustment, observability gap, or fallback and reuse existing evidence.

## Evidence requirement

Every dispatched task lifecycle must record:

- all selection inputs, including truthful `decomposability` and separate `decomposition_policy`
- decomposition disposition when policy suppresses an otherwise possible split
- requested profile before spawn
- explicit/default agent-role plan and role-config evidence
- planned runtime profile after known role constraints
- whether role planning caused floor or approval re-evaluation
- applied profile only when exact final runtime evidence exists
- runtime profile observability state
- selection source and rationale
- fork policy
- runtime rejection, inheritance, role adjustment, or fallback, if any
- reclassification or escalation, if any
- whether multi-agent decomposition was allowed, considered, suppressed, or used
- for Sol `xhigh` or Sol `max`, the proposal, cost notice, approval status, and explicit approval evidence
- for reviewer continuity, existing reviewer identity, original profile/observability evidence, continued mode, and `application_status: reused_existing_agent_profile`

A proposal awaiting approval or an unresolved role-profile capability gap is a stopped workflow state, not a dispatched task.

## References

- [Adaptive agent assignment design](../../../design/adaptive-agent-assignment-design.md)
- [Spawn-agent model overrides](spawn-agent-model-overrides.md)
- [Execution Cost Stabilizer](../../execution-cost-stabilizer/SKILL.md)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [OpenAI latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [Codex MultiAgent V2 spawn implementation](https://github.com/openai/codex/blob/6478a751fde8884b2fdc76486fe23175a8e795d4/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)
- [参考記事: 役割分担で回すGPT-5.6 Luna / Terra / Sol](https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb)
