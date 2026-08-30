# Spawn-agent model overrides

Use this reference after [agent-profile-selection.md](agent-profile-selection.md) has produced an approved or ordinary `requested` dispatch profile.

This reference owns runtime call planning, role/default-role impact analysis, runtime application evidence, and fallback. It does not choose the task profile.

## Core contract

- `requested` is a pre-spawn instruction selected by the parent.
- `role_plan` is a pre-spawn description of the explicit `agent_type` or effective default role and any model/reasoning changes that role can apply.
- `planned_runtime_profile` is a pre-spawn expectation after known role/default-role constraints. It is not runtime proof.
- `applied` is a post-runtime fact. Keep it unset unless the parent can observe a trustworthy final runtime snapshot or another exact application proof.
- A successful `spawn_agent` call alone is not proof that `requested` became the final model/reasoning profile.
- Current Codex MultiAgent V2 applies requested model/reasoning overrides before applying the selected/default agent role, so role configuration can replace those values before the child starts.
- Put the requested model and reasoning effort in the actual spawn call, not only in the task message.
- For the current GPT-5.6 family, resolve selector tiers to `gpt-5.6-luna`, `gpt-5.6-terra`, or `gpt-5.6-sol` when those models are available.
- Preserve the selector's exact supported effort value: `none`, `low`, `medium`, `high`, `xhigh`, or `max`.
- `Ultra` is not a `reasoning_effort` value. Multi-agent decomposition must already have been handled by `codex-delegation-executor` when decomposition is permitted.
- For a fresh specialist with an override, explicitly use `fork_turns: "none"`.
- An explicit positive partial fork may use an override when its context need is bounded.
- Do not use an override with `fork_turns: "all"` or omitted `fork_turns`: full-history forks use the runtime's inheritance path.

## Role/default-role planning

Treat agent role configuration as part of the call plan, not as an opaque post-call detail.

Before dispatch:

1. identify explicit `agent_type` when one will be passed
2. otherwise identify the effective default role that the current runtime will apply
3. inspect the authoritative role configuration when it is available
4. record whether the role leaves model/reasoning unchanged, changes them, locks them, or is unknown
5. derive `planned_runtime_profile` only from known role/config evidence
6. return the role-adjusted plan through [agent-profile-selection.md](agent-profile-selection.md) when it changes the model tier or reasoning effort

The expensive Sol approval gate applies to the role-adjusted plan as well as the original selector output. If a role/default role would produce Sol `xhigh` or Sol `max`, create or update the proposal and stop before spawn until the current-task user explicitly approves it.

If the applicable role/default-role configuration cannot be inspected well enough to determine whether it can change model or reasoning effort, the parent cannot guarantee the expensive-profile gate. Record a role-profile capability gap and stop before dispatch rather than assuming the requested profile will survive role application.

A role that forces a profile below the required automatic floor is also a capability/policy mismatch. Do not silently claim the lower role profile satisfies the task.

## Required application sequence

Use this order without collapsing the steps:

1. finish task classification and initial profile selection
2. obtain any required user approval for the initial profile
3. identify the explicit/default agent role and inspect its profile effect
4. derive the role-adjusted `planned_runtime_profile`
5. re-run floor and expensive-profile approval checks when the role changes or locks model/reasoning
6. record `requested`, `role_plan`, and `planned_runtime_profile`; keep `applied: null`
7. resolve remaining call constraints such as model availability and fork compatibility without writing `applied`
8. invoke `collaboration.spawn_agent` with the requested override and explicit role when applicable, or use the required inheritance path
9. inspect the returned tool evidence and any parent-observable final runtime/config snapshot
10. only when exact final profile evidence exists, record it in `applied`
11. if the spawn succeeds but final model/reasoning is not observable, keep `applied: null` and record `application_status: spawn_succeeded_profile_unverified`
12. if the call rejects the override, record the rejection before considering a parent-owned fallback
13. if fallback runs, record its profile as exact `applied` only when the fallback execution provides exact configuration evidence

Never use an `applied` value as the input to the spawn call that is supposed to establish that value.

## Call shape

```js
await collaboration.spawn_agent({
  task_name: "bounded_task",
  message: "Task-local instructions only.",
  fork_turns: "none",
  agent_type: "<explicit role when selected>",
  model: "<dispatch_profile.requested.model>",
  reasoning_effort: "<dispatch_profile.requested.reasoning_effort>",
});
```

Omit `agent_type` only when the call intentionally uses the runtime default role. An omitted role is not equivalent to "no role"; account for the effective default role in `role_plan`.

Keep the task request focused on work, scope, evidence, and report rules. A model name written only in `message` does not configure the spawned agent.

## Pre-spawn evidence shape

Before the call:

```yaml
requested:
  model: <selected model>
  reasoning_effort: <selected effort>
  fork_turns: <selected fork policy>
role_plan:
  explicit_agent_type: <role or null>
  effective_role: <role name>
  role_config_evidence: <path/source or null>
  profile_effect: unchanged | changed | locked | unknown
planned_runtime_profile:
  model: <known planned model or null>
  reasoning_effort: <known planned effort or null>
applied: null
application_status: pending_runtime_result
profile_observability: pending
```

`planned_runtime_profile` is planning evidence only. Never rename it to `applied` before runtime proof.

## Post-spawn evidence

When a trustworthy parent-visible final snapshot exists:

```yaml
applied:
  model: <observed final model>
  reasoning_effort: <observed final effort>
  fork_turns: <observed/established fork policy>
application_status: applied_verified
profile_observability: verified_final_snapshot
```

When the tool call succeeds but the parent-visible output exposes only task identity/nickname or otherwise omits the final model/reasoning snapshot:

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
profile_observability: final_profile_hidden
observed_runtime_evidence:
  spawn_succeeded: true
  task_identity: <returned task identity>
```

Do not copy `requested` or `planned_runtime_profile` into `applied` merely because spawn succeeded.

## Full-history constraint

A full-history spawn can have different role behavior from a fresh/partial spawn. Treat the actual runtime path as authoritative.

When full history is mandatory:

1. preserve the selected specialization in `requested` as unapplied evidence
2. determine whether an explicit role will still be applied on that full-history path
3. omit incompatible model/reasoning overrides when the runtime requires inheritance
4. keep `applied` unset until exact final inheritance/role evidence is parent-observable
5. record `application_status: inherited_parent_profile` only when the final inherited profile is actually established
6. otherwise use `spawn_succeeded_profile_unverified` or a capability-gap state as appropriate
7. state which context requirement prevented fresh or partial-fork specialization

Prefer a fresh task-local prompt or bounded positive partial fork when specialization is more important than complete conversational history.

## Failure handling

The visible schema and backend acceptance can differ. Treat rejection as a capability state, not as successful application.

1. record the rejected requested model, effort, role, fork policy, and error
2. do not populate `applied` with the rejected request
3. do not silently downgrade an explicit user or repository override
4. when policy permits fallback, the parent may run the work through:

```bash
codex exec --model <model> -c model_reasoning_effort="<effort>"
```

5. keep that fallback parent-owned; a sub-agent must never run nested Codex
6. record `fallback_applied` only when exact fallback configuration evidence exists
7. when fallback starts but exact effective model/reasoning still cannot be observed, use an explicit unverified fallback state instead of inventing `applied`
8. when no compliant fallback exists, keep `applied` unset and record `application_status: capability_gap`

If the selected model is unavailable but the runtime exposes another model in the same or a higher selector tier, the parent may resolve the requested runtime identifier before spawn only when no explicit identifier was pinned. Record the resolution as a constraint and preserve the requested tier. This call-planning resolution still does not populate `applied` before runtime evidence exists.

## Escalation handling

Profile escalation must return through [agent-profile-selection.md](agent-profile-selection.md). Do not change only the spawn arguments without updating classification and approval evidence.

- raise reasoning effort when the problem remains the same but needs more careful analysis
- raise model tier when task nature, uncertainty, change radius, or criticality changed
- re-run the approval gate when role/default-role planning raises the effective plan to Sol `xhigh` or Sol `max`
- return independently separable work to `codex-delegation-executor` only when the caller permits decomposition

## Evidence limit

A delegated agent cannot attest to hidden spawn arguments or final parent-side runtime configuration. The parent owns `requested`, `role_plan`, `planned_runtime_profile`, runtime observability, `applied`, and fallback evidence.

Current Codex MultiAgent V2 can obtain an internal agent config snapshot for telemetry, but ordinary tool output may hide model/reasoning metadata and return only task identity. Internal telemetry availability is not parent-visible proof unless the runtime explicitly exposes that snapshot to the caller.

## References

- [Agent profile selection](agent-profile-selection.md)
- [Codex issue #32031](https://github.com/openai/codex/issues/32031)
- [Codex MultiAgent V2 spawn implementation](https://github.com/openai/codex/blob/6478a751fde8884b2fdc76486fe23175a8e795d4/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)
