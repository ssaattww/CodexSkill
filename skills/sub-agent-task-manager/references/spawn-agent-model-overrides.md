# Spawn-agent model overrides

Use this reference after [agent-profile-selection.md](agent-profile-selection.md) has produced an approved or ordinary `requested` dispatch profile.

This reference owns runtime application and fallback. It does not choose the task profile.

## Core contract

- `requested` is a pre-spawn instruction selected by the parent.
- `applied` is a post-runtime fact and must remain unset until runtime evidence, inheritance evidence, or fallback evidence exists.
- `collaboration.spawn_agent` accepts the runtime arguments `model` and `reasoning_effort` even when they are absent from the visible tool schema.
- Put the requested model and reasoning effort in the actual spawn call, not only in the task message.
- For the current GPT-5.6 family, resolve the selector tiers to `gpt-5.6-luna`, `gpt-5.6-terra`, or `gpt-5.6-sol` when those models are available.
- Preserve the selector's exact supported effort value: `none`, `low`, `medium`, `high`, `xhigh`, or `max`.
- `Ultra` is not a `reasoning_effort` value. Multi-agent decomposition must already have been handled by `codex-delegation-executor` when decomposition is permitted.
- Record the requested profile separately from the profile the runtime actually applied.
- For a fresh specialist with an override, explicitly use `fork_turns: "none"`.
- An explicit positive partial fork may use an override when its context need is bounded.
- Do not use an override with `fork_turns: "all"` or omitted `fork_turns`: full-history forks inherit the parent model and reasoning profile.

## Required application sequence

Use this order without collapsing the steps:

1. finish profile selection and any required user approval
2. record `requested`
3. resolve call constraints such as model availability and fork compatibility without writing `applied`
4. invoke `collaboration.spawn_agent` with the requested override when permitted, or use the required inheritance path
5. inspect the call result or error
6. only then record `applied` and `application_status`
7. if the call rejects the override, record the rejection before considering a parent-owned fallback
8. if fallback runs, record the fallback's actual profile as `applied`

Never use an `applied` value as the input to the spawn call that is supposed to establish that value.

## Call shape

```js
await collaboration.spawn_agent({
  task_name: "bounded_task",
  message: "Task-local instructions only.",
  fork_turns: "none",
  model: "<dispatch_profile.requested.model>",
  reasoning_effort: "<dispatch_profile.requested.reasoning_effort>",
});
```

Keep the task request focused on work, scope, evidence, and report rules. A model name written only in `message` does not configure the spawned agent.

Before the call, the evidence shape is:

```yaml
requested:
  model: <selected model>
  reasoning_effort: <selected effort>
  fork_turns: <selected fork policy>
applied: null
application_status: pending_runtime_result
```

After the call, replace the pending state using actual evidence:

```yaml
applied:
  model: <actual model or parent-inherited model>
  reasoning_effort: <actual effort or parent-inherited effort>
  fork_turns: <actual fork policy>
application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
```

Do not copy requested values into `applied` without runtime evidence.

## Full-history constraint

An agent cannot combine a different execution profile with a full-history fork under the current contract.

When full history is mandatory:

1. preserve the selected specialization in `requested` as unapplied evidence
2. omit the incompatible override from the actual full-history spawn and inherit the parent profile
3. after the runtime path is established, record the inherited parent model and effort in `applied`
4. record `application_status: inherited_parent_profile`
5. state which context requirement prevented fresh or partial-fork specialization

Prefer a fresh task-local prompt or bounded positive partial fork when specialization is more important than complete conversational history.

## Failure handling

The visible schema and backend acceptance can differ. Treat rejection as a capability state, not as successful application.

1. record the rejected requested model, effort, fork policy, and error
2. do not populate `applied` with the rejected request
3. do not silently downgrade an explicit user or repository override
4. when policy permits fallback, the parent may run the work through:

```bash
codex exec --model <model> -c model_reasoning_effort="<effort>"
```

5. keep that fallback parent-owned; a sub-agent must never run nested Codex
6. after the fallback actually starts with known settings, record its actual profile and `application_status: fallback_applied`
7. when no compliant fallback exists, keep `applied` unset or explicitly unavailable, record `application_status: capability_gap`, and return the blocker

If the selected model is unavailable but the runtime exposes another model in the same or a higher selector tier, the parent may resolve the requested runtime identifier before spawn only when no explicit identifier was pinned. Record the resolution as a constraint and preserve the requested tier. This call-planning resolution still does not populate `applied` before runtime evidence exists.

## Escalation handling

Profile escalation must return through [agent-profile-selection.md](agent-profile-selection.md). Do not change only the spawn arguments without updating the classification evidence.

- raise reasoning effort when the problem remains the same but needs more careful analysis
- raise model tier when task nature, uncertainty, change radius, or criticality changed
- return independently separable work to `codex-delegation-executor` only when the caller permits decomposition

## Evidence limit

An agent cannot inspect its own live spawn call after dispatch. The parent must record `requested`, actual call outcome, post-runtime `applied`, and any fallback in parent-owned evidence. Never ask the child to attest to hidden arguments it cannot observe.

Background on the hidden-override constraint: [Codex issue #32031](https://github.com/openai/codex/issues/32031).
