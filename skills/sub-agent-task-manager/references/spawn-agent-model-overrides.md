# Spawn-agent model overrides

Use this reference when a parent selects a model or reasoning effort for a `sub-agent`.

## Core contract

- `collaboration.spawn_agent` accepts the runtime arguments `model` and `reasoning_effort` even when they are absent from the visible tool schema.
- Decide model, reasoning effort, and fork policy before dispatch. Put model and reasoning in the actual spawn call, not only in the task message.
- For review, `review-enforcer` selects the parent agent's current model and `high` reasoning effort by default; the user may override the reasoning effort. For implementation, use only the model that `development-orchestrator` confirmed with the user at workflow start.
- For a fresh specialist with an override, explicitly use `fork_turns: "none"`.
- An explicit positive partial fork may use an override when its context need is bounded. Do not use an override with `fork_turns: "all"` or omitted `fork_turns`: full-history forks inherit the parent model and reasoning profile.

## Call shape

```js
await collaboration.spawn_agent({
  task_name: "bounded_task",
  message: "Task-local instructions only.",
  fork_turns: "none",
  model: "<caller-selected-model>",
  reasoning_effort: "<caller-selected-effort>",
});
```

Keep the task request focused on work, scope, and report rules. A model name written only in `message` does not configure the spawned agent.

## Failure handling and limit

The visible schema and backend acceptance can differ. If the runtime rejects either override argument, the parent may run the work through `codex exec --model <model> -c model_reasoning_effort="<effort>"`; a sub-agent must never run that fallback or nested Codex.

An agent cannot inspect its own live spawn call after dispatch. Record the intended profile and call outcome in the parent-owned report, and treat backend rejection as a capability gap rather than claiming the override was applied. Background: [Codex issue #32031](https://github.com/openai/codex/issues/32031).
