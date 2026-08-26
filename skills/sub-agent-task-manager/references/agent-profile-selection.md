# Agent profile selection

Use this reference before dispatching every bounded `sub-agent` task.

The selector chooses a model tier, reasoning effort, and fork policy separately. It also decides whether the work should remain one bounded task or return to `codex-delegation-executor` for multi-agent decomposition.

## Current model family

Use the following runtime model IDs when they are available:

| Tier | Runtime model | Intended use |
| --- | --- | --- |
| Luna | `gpt-5.6-luna` | deterministic, repetitive, cost-sensitive, high-volume work |
| Terra | `gpt-5.6-terra` | ordinary implementation and bounded technical work |
| Sol | `gpt-5.6-sol` | ambiguous, high-risk, cross-system, design, debugging, and review work |

Use only reasoning effort values supported by the selected runtime model. For the GPT-5.6 family, the normalized values are `none`, `low`, `medium`, `high`, `xhigh`, and `max`.

`Ultra` is not a `reasoning_effort` value. Treat it as a multi-agent execution strategy for independently separable workstreams. `codex-delegation-executor` owns that decomposition decision; this reference selects the profile for each resulting bounded task.

Do not use pricing as the primary selector. Use task nature, uncertainty, change radius, and criticality first, then choose the least expensive profile that satisfies the resulting floor.

## Selection inputs

Record these signals before choosing a profile:

- `task_kind`: implementation, design, investigation, review, verification, environment verification, intake verification, standards work, or other
- `work_class`: `mechanical`, `bounded_technical`, or `judgment_heavy`
- `uncertainty`: `low`, `medium`, or `high`
- `change_radius`: `local`, `cross_module`, or `cross_system`
- `criticality`: `ordinary` or `high`
- `repetition`: `single` or `high_volume`
- `decomposability`: `single`, `sequential_dependencies`, or `independent_workstreams`
- `context_need`: `fresh`, `bounded_history`, or `full_history`
- explicit user or repository model, effort, budget, and availability constraints

`criticality: high` includes security, authorization, privacy, destructive data handling, schema or data migration, concurrency, compatibility, public API, release, deployment, and other changes where an incorrect result has a large or difficult-to-reverse impact.

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
- focused fix verification against already identified findings
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

Use these defaults after applying the floors above:

| Task | Default profile | Escalation |
| --- | --- | --- |
| exact repetitive transformation | Luna `low` | Luna `medium` when validation interpretation is needed |
| deterministic build or test execution | Luna `medium` | Reclassify failure diagnosis as investigation |
| ordinary bounded implementation | Terra `medium` | Terra `high` for cross-module or multi-factor work |
| localized debugging with a concrete hypothesis | Terra `high` | Sol `high` when the hypothesis fails or layers interact |
| design or requirement interpretation | Sol `high` | Sol `max` only for one exceptionally hard, inseparable decision |
| open-ended or cross-layer investigation | Sol `high` | Sol `max` for one exceptionally hard, inseparable root cause |
| initial normal review | Sol `high` | Sol `xhigh` for high-criticality scope |
| focused fix verification | Terra `high` | Sol `high` when the original finding or changed scope is high-criticality |
| independent final review or release audit | Sol `xhigh` | Sol `max` only when one inseparable proof obligation dominates |

Do not use `none` by default for delegated development work. It may be used only for an explicitly deterministic operation that requires no technical judgment and has a complete mechanical validator.

## Reasoning-effort rules

Choose reasoning effort independently from model tier:

- `low`: exact, low-risk transformations with explicit expected output
- `medium`: ordinary bounded implementation or deterministic evidence work
- `high`: multiple interacting conditions, careful debugging, design, or review
- `xhigh`: exhaustive or high-stakes review and audit with a bounded scope
- `max`: one exceptionally difficult, non-decomposable problem where deeper reasoning is more useful than splitting the task

Do not use `max` as a generic quality setting. Before selecting it, call `execution-cost-stabilizer` and record why Terra or Sol at `high` or `xhigh` is insufficient.

## Multi-agent decision

Return the task to `codex-delegation-executor` for decomposition instead of selecting a single `max` task when all of the following hold:

- there are at least two independently executable workstreams
- each workstream can have explicit scope, non-goals, evidence, and report ownership
- write ownership does not overlap, or the tasks are read-only
- a parent synthesis step is defined
- parallel execution provides material value after applying `execution-cost-stabilizer`

Each decomposed task receives its own profile. Do not assign one shared profile merely because the tasks run together.

## Override and availability precedence

Apply precedence in this order:

1. explicit user instruction
2. authoritative repository policy
3. runtime capability and model availability
4. automatic selection rules in this reference

An override may pin the model, effort, or both. Continue to classify the task and record when the override is below the automatically calculated floor. Do not silently replace an explicit override. Report the mismatch and follow the governing authority.

Separate the requested profile from the applied profile:

```yaml
dispatch_profile:
  schema_version: 1
  selection_source: automatic | user_override | repository_policy
  task_kind: review
  signals:
    work_class: judgment_heavy
    uncertainty: high
    change_radius: cross_module
    criticality: high
    repetition: single
    decomposability: single
    context_need: fresh
  requested:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: xhigh
    fork_turns: none
    parallelism_mode: single_agent
  applied:
    model: gpt-5.6-sol
    reasoning_effort: xhigh
    fork_turns: none
  application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
  reasons:
    - independent final review
    - high-criticality cross-module scope
  constraints: []
  escalation_triggers:
    - evidence conflict expands the review scope
```

When the selected model or effort is unavailable or rejected, follow [spawn-agent-model-overrides.md](spawn-agent-model-overrides.md). Never claim the requested profile was applied without actual runtime evidence.

## Fork policy

- Use `fork_turns: "none"` for a fresh specialist when applying a model or reasoning override.
- Use an explicit positive partial fork only when the required history is bounded and identified.
- A full-history fork inherits the parent execution profile. Record `application_status: inherited_parent_profile` and do not claim that a different requested model was applied.
- Prefer fresh context plus explicit task-local inputs over a full-history fork when specialization matters.

## Reclassification and escalation

Recompute the profile when new evidence changes uncertainty, change radius, criticality, or task kind.

- A failed deterministic verification becomes investigation; do not keep retrying it as Luna work.
- A localized implementation that exposes architectural ambiguity becomes Sol work.
- A task that becomes cleanly separable returns to `codex-delegation-executor` for decomposition.
- Raise reasoning effort when the problem is unchanged but needs more careful analysis.
- Raise model tier when the nature of the problem changes or the current model lacks the required judgment capability.

Avoid blind retry loops. Record the reason for every profile escalation or fallback and reuse existing evidence.

## Evidence requirement

Every dispatched task report must record:

- all selection inputs
- requested and applied profile
- selection source and rationale
- fork policy
- runtime rejection or fallback, if any
- reclassification or escalation, if any
- whether multi-agent decomposition was considered and why it was or was not used

## References

- [Adaptive agent assignment design](../../../design/adaptive-agent-assignment-design.md)
- [Execution Cost Stabilizer](../../execution-cost-stabilizer/SKILL.md)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [OpenAI latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [参考記事: 役割分担で回すGPT-5.6 Luna / Terra / Sol](https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb)
