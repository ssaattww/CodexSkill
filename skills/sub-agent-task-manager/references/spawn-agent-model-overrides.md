# Spawn-agent model overrides

Use this reference after [agent-profile-selection.md](agent-profile-selection.md) has produced a requested `dispatch_profile`.

This reference owns runtime application and fallback. It does not choose the task profile.

## Core contract

- `collaboration.spawn_agent` accepts the runtime arguments `model` and `reasoning_effort` even when they are absent from the visible tool schema.
- Put the selected model and reasoning effort in the actual spawn call, not only in the task message.
- For the current GPT-5.6 family, resolve the selector tiers to `gpt-5.6-luna`, `gpt-5.6-terra`, or `gpt-5.6-sol` when those models are available.
- Preserve the selector's exact supported effort value: `none`, `low`, `medium`, `high`, `xhigh`, or `max`.
- `Ultra` is not a `reasoning_effort` value. Multi-agent decomposition must already have been handled by `codex-delegation-executor` before this reference is used.
- Record the requested profile separately from the profile the runtime actually applied.
- For a fresh specialist with an override, explicitly use `fork_turns: "none"`.
- An explicit positive partial fork may use an override when its context need is bounded.
- Do not use an override with `fork_turns: "all"` or omitted `fork_turns`: full-history forks inherit the parent model and reasoning profile.

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

After the call, record:

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

1. omit the override and inherit the parent profile
2. record `application_status: inherited_parent_profile`
3. preserve the requested profile as unapplied evidence
4. state which context requirement prevented fresh or partial-fork specialization

Prefer a fresh task-local prompt or bounded positive partial fork when specialization is more important than complete conversational history.

## Failure handling

The visible schema and backend acceptance can differ. Treat rejection as a capability state, not as successful application.

1. record the rejected model, effort, fork policy, and error
2. do not silently downgrade an explicit user or repository override
3. when policy permits fallback, the parent may run the work through:

```bash
codex exec --model <model> -c model_reasoning_effort="<effort>"
```

4. keep that fallback parent-owned; a sub-agent must never run nested Codex
5. record the actual fallback profile and `application_status: fallback_applied`
6. when no compliant fallback exists, record `application_status: capability_gap` and return the blocker

If the selected model is unavailable but the runtime exposes another model in the same or a higher selector tier, the parent may resolve to that model only when no explicit identifier was pinned. Record the resolution as a constraint and preserve the requested tier.

## Escalation handling

Profile escalation must return through [agent-profile-selection.md](agent-profile-selection.md). Do not change only the spawn arguments without updating the classification evidence.

- raise reasoning effort when the problem remains the same but needs more careful analysis
- raise model tier when task nature, uncertainty, change radius, or criticality changed
- return independently separable work to `codex-delegation-executor` instead of treating multi-agent execution as an effort value

## Evidence limit

An agent cannot inspect its own live spawn call after dispatch. The parent must record the intended profile, actual call outcome, and any fallback in the parent-owned report. Never ask the child to attest to hidden arguments it cannot observe.

Background on the hidden-override constraint: [Codex issue #32031](https://github.com/openai/codex/issues/32031).
