# Skillization Policy

Open this only when deciding duplicate grouping, recurrence handling, whether a point should become a skill, or whether repeated agent output should become an internal tool.

## Duplicate grouping

When a new point appears:

1. detect whether equivalent intent already exists
2. append the FP to the same duplicate group
3. avoid isolated near-duplicate rows
4. keep traceability to all source FP IDs

Group by intent, not literal wording.

## Recurrence and implementation priority

Occurrence count is evidence for priority and recurrence risk. It is not a hard gate that forbids a justified low-risk improvement.

Use this default interpretation:

- first occurrence: record the point and classify ownership; implement immediately only when the gap is clear, omission risk is meaningful, and the change is an internal, reversible update within an existing skill or helper
- second occurrence: raise priority, set to `検討中` when still unresolved, and prepare or execute the existing-skill/internal-tool change
- third occurrence or more: prefer implementation unless the point is clearly one-off, externally constrained, or already covered by stronger evidence

Early implementation is appropriate when any of the following makes delay costly:

- cross-repository applicability is obvious
- recurrence cost is high
- omission risk is high if not enforced by the task routine, skill, or tool
- the agent is repeatedly producing the same deterministic output manually
- an existing skill already owns the behavior and a small reversible change closes the gap

Do not skillize or toolize:

- issue-specific design content
- one-time feature decisions
- output that requires substantial case-by-case judgment and has no reusable deterministic core
- externally constrained rules that are not reusable as workflow

## Runtime trigger vs durable tracking

The task routine is the runtime source of truth for the current step, including mandatory skill and tool reflection.

Feedback points and GitHub Issues are the durable source of truth for:

- history
- duplicate grouping
- recurrence evidence
- follow-up work
- commit or PR references

Do not make issue lookup the only mechanism that reminds the agent what to do. Hooks and local task-routine state must surface or block missing steps even when GitHub has not been opened in the current turn.

## Actions after skillization or toolization

When a point is skillized:

1. set `skill化状態` to `skill化済み`
2. set `関連skill`
3. preserve links to source FP IDs
4. rewrite wording from incident-specific to reusable rule
5. if ongoing execution should be tracked as work, move the loop to an issue and stop using the active FP ledger as the execution queue

When a point becomes an internal tool or helper:

1. identify the owning existing skill
2. keep the helper under that skill's `scripts/`, `hooks/`, or equivalent internal directory
3. record the task-routine tool decision and evidence
4. add tests for deterministic behavior when practical
5. use a follow-up issue only when work remains after the current commit

If an existing skill is close, prefer extending it over creating a near-duplicate skill. If an internal helper can remove deterministic repeated output without creating a new public contract, prefer that over a standalone tool.

## New skill vs existing skill update

Use these classes:

1. no skill change
2. existing skill update
3. new skill candidate

Prefer `existing skill update` when:

- an existing skill already owns most of the workflow
- the gap can be closed by adding rules, routing, references, hooks, or a small helper script
- creating another skill would fragment ownership or triggering

Choose `new skill candidate` only when:

- no existing skill has defensible ownership
- the workflow is reusable across repositories
- forcing it into an existing skill would make ownership unclear

## Tool decision classes

Use these classes in the task routine:

1. `none`
2. `update-existing`
3. `create-internal`
4. `propose-external`

Prefer `update-existing` or `create-internal` when:

- the repeated output has a deterministic reusable core
- the helper remains within an existing skill's ownership
- the action is internal, reversible, and low risk
- no new external contract, credential, or organizational approval is introduced

Choose `propose-external` when:

- the tool would expose a new standalone interface
- it changes an external/public contract
- it performs destructive or irreversible operations
- it requires credentials, legal review, or organizational approval

## Approval boundary

New skill creation and standalone external tools are high risk.

- do not implement a brand-new skill without first recommending it to the user
- do not introduce a standalone external tool without first recommending it to the user
- the recommendation should explain the recurring gap, why existing skills/internal helpers are insufficient, and the proposed owner scope

Existing skill updates and internal helper creation may proceed without extra approval when they stay within current ownership and are internal, reversible, and low risk.

If a skill/process/tool improvement remains as follow-up work after commit timing, prefer issue creation over leaving it in the active FP ledger.

## Ownership and maintenance

The agent that discovers the gap owns the next lifecycle action until one of these is true:

- the user received a new-skill or external-tool recommendation
- an existing-skill/internal-tool update PR was created
- the point was explicitly recorded as no-change work

Do not leave stale skill or tool gaps unowned.

## Sub-agent rule

Use sub-agents for narrow, context-heavy work when available:

- duplicate clustering
- reusable-vs-noise classification
- comparison against existing skills and helpers
- focused review of a skill or internal-tool update diff

Keep the final skillization/toolization decision in the main agent and record it in the active task routine.
