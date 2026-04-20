# Skillization Policy

Open this only when deciding duplicate grouping, recurrence handling, or whether a point should become a skill.

## Duplicate grouping

When a new point appears:

1. detect whether equivalent intent already exists
2. append the FP to the same duplicate group
3. avoid isolated near-duplicate rows
4. keep traceability to all source FP IDs

Group by intent, not literal wording.

## Default skillization threshold

- first occurrence: record only
- second occurrence: set to `検討中` and prepare a skillization recommendation
- third occurrence or more: prefer implementation, usually by updating an existing skill, unless clearly one-off

Early skillization is allowed when all are true:

- cross-repository applicability is obvious
- recurrence cost is high
- omission risk is high if not automated by skill

Do not skillize:

- issue-specific design content
- one-time feature decisions
- externally constrained rules that are not reusable as workflow

## Actions after skillization

When a point is skillized:

1. set `skill化状態` to `skill化済み`
2. set `関連skill`
3. preserve links to source FP IDs
4. rewrite wording from incident-specific to reusable rule
5. if ongoing execution should be tracked as work, move the loop to an issue and stop using the active FP ledger as the execution queue

If an existing skill is close, prefer extending it over creating a near-duplicate skill.

## New skill vs existing skill update

Use these classes:

1. no skill change
2. existing skill update
3. new skill candidate

Prefer `existing skill update` when:

- an existing skill already owns most of the workflow
- the gap can be closed by adding rules, routing, references, or a small helper script
- creating another skill would fragment ownership or triggering

Choose `new skill candidate` only when:

- no existing skill has defensible ownership
- the workflow is reusable across repositories
- forcing it into an existing skill would make ownership unclear

## Approval boundary

New skill creation is high risk.

- do not implement a brand-new skill without first recommending it to the user
- the recommendation should explain the recurring gap, why existing skills are insufficient, and the proposed owner scope

Existing skill updates may proceed without extra approval when they stay within the current skill family and ownership.

If a skill/process improvement remains as follow-up work after commit timing, prefer issue creation over leaving it in the active FP ledger.

## Ownership and maintenance

The agent that discovers the recurring gap owns the next lifecycle action until one of these is true:

- the user received a new-skill recommendation
- an existing-skill update PR was created
- the point was explicitly recorded as non-skill work

Do not leave stale skill gaps unowned.

## Sub-agent rule

Use sub-agents for narrow, context-heavy work when available:

- duplicate clustering
- reusable-vs-noise classification
- comparison against existing skills
- focused review of a skill update diff

Keep the final skillization decision in the main agent.
